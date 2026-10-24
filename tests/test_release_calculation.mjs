import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import { calculate, classifyMessage } from '../tools/release-calculation.mjs';

function git(repo, ...args) {
  const result = spawnSync('git', ['-C', repo, ...args], { encoding: 'utf8', timeout: 10000 });
  assert.equal(result.status, 0, result.stderr);
  return result.stdout.trim();
}

function fixture(fn) {
  const repo = mkdtempSync(join(tmpdir(), 'framework-release-'));
  try {
    git(repo, 'init', '-q');
    git(repo, 'config', 'user.name', 'Release fixture');
    git(repo, 'config', 'user.email', 'fixture@example.invalid');
    writeFileSync(join(repo, 'source.txt'), 'baseline');
    git(repo, 'add', 'source.txt');
    git(repo, 'commit', '-q', '-m', 'chore: baseline');
    git(repo, 'tag', 'v1.0.0');
    return fn(repo);
  } finally {
    rmSync(repo, { recursive: true, force: true });
  }
}

function commit(repo, message) {
  git(repo, 'commit', '--allow-empty', '-q', '-m', message);
  return git(repo, 'rev-parse', 'HEAD');
}

for (const [message, expected] of [
  ['fix: repair source', 'v1.0.1'],
  ['perf(core): speed up scan', 'v1.0.1'],
  ['feat(api): [issue-3] support selection', 'v1.1.0'],
  ['feat(api)!: replace contract', 'v2.0.0'],
  ['chore: change contract\n\nBREAKING CHANGE: consumers must upgrade', 'v2.0.0'],
  ['docs: clarify release policy', null],
  ['test: cover release fixture', null],
  ['chore: maintain tooling', null],
  ['feature: alias excluded by ticket policy', null],
  ['revert: excluded by ticket policy', null],
  ['docs: explain !: marker in prose', null],
]) {
  test(`calculates ${expected ?? 'no release'} for ${message.split('\n')[0]}`, () => fixture((repo) => {
    const head = commit(repo, message);
    const result = calculate(repo, head);
    assert.equal(result.previousTag, 'v1.0.0');
    assert.equal(result.nextTag, expected);
    assert.equal(result.commitCount, 1);
  }));
}

test('highest bump covers the complete range and nonreleasing additions do not increase it', () =>
  fixture((repo) => {
    commit(repo, 'fix: first squash');
    commit(repo, 'docs: intervening squash');
    const minor = calculate(repo, commit(repo, 'feat(ui): second releasing squash'));
    assert.equal(minor.nextTag, 'v1.1.0');
    assert.equal(minor.commitCount, 3);
    const unchanged = calculate(repo, commit(repo, 'test: more nonreleasing coverage'));
    assert.equal(unchanged.nextTag, 'v1.1.0');
    const major = calculate(repo, commit(repo, 'refactor!: breaking later squash'));
    assert.equal(major.nextTag, 'v2.0.0');
    assert.equal(major.commitCount, 5);
  }));

test('new release tag advances baseline without a 1.x ceiling', () => fixture((repo) => {
  commit(repo, 'feat: first release');
  git(repo, 'tag', '-a', 'v1.9.9', '-m', 'release v1.9.9');
  const head = commit(repo, 'fix!: incompatible repair');
  const result = calculate(repo, head);
  assert.equal(result.previousTag, 'v1.9.9');
  assert.equal(result.nextTag, 'v2.0.0');
}));

test('framework version ignores the private package version', () => fixture((repo) => {
  writeFileSync(join(repo, 'package.json'), '{"version":"99.99.99"}\n');
  git(repo, 'add', 'package.json');
  const head = commit(repo, 'fix: patch behavior');
  assert.equal(calculate(repo, head).nextTag, 'v1.0.1');
}));

test('message and PR input validation detect edited title and breaking footer', () => fixture((repo) => {
  const message = 'feat(api): [issue-3] add tag mode\n\nBREAKING CHANGE: migrate the profile';
  const messagePath = join(repo, 'squash.txt');
  writeFileSync(messagePath, message);
  const script = new URL('../tools/release-calculation.mjs', import.meta.url).pathname;
  const valid = spawnSync('node', [script, 'validate-message', '--message-file', messagePath], {
    encoding: 'utf8', timeout: 10000,
  });
  assert.equal(valid.status, 0, valid.stderr);
  assert.equal(JSON.parse(valid.stdout).bump, 'major');
  const eventPath = join(repo, 'event.json');
  writeFileSync(eventPath, JSON.stringify({ pull_request: {
    title: 'docs: title before edit', body: 'No breaking change',
  } }));
  const before = spawnSync('node', [script, 'validate-pr', '--event-file', eventPath], {
    encoding: 'utf8', timeout: 10000,
  });
  assert.equal(JSON.parse(before.stdout).bump, null);
  writeFileSync(eventPath, JSON.stringify({ pull_request: {
    title: 'feat!: edited title', body: 'BREAKING CHANGE: migrate clients',
  } }));
  const after = spawnSync('node', [script, 'validate-pr', '--event-file', eventPath], {
    encoding: 'utf8', timeout: 10000,
  });
  assert.equal(after.status, 0, after.stderr);
  assert.equal(JSON.parse(after.stdout).bump, 'major');
  writeFileSync(eventPath, JSON.stringify({ pull_request: { title: 'invalid title', body: '' } }));
  const invalid = spawnSync('node', [script, 'validate-pr', '--event-file', eventPath], {
    encoding: 'utf8', timeout: 10000,
  });
  assert.equal(invalid.status, 1);
}));

test('malformed messages fail rather than becoming no-release', () => fixture((repo) => {
  for (const message of ['not conventional', 'feat: ', 'fix: valid\n\nBREAKING CHANGE:']) {
    assert.throws(() => classifyMessage(message));
  }
  assert.throws(() => calculate(repo, commit(repo, 'broken release-driving message')));
}));

test('missing baseline, unrelated baseline, and shallow history fail closed', () => fixture((repo) => {
  const head = commit(repo, 'fix: repair');
  assert.throws(() => calculate(repo, '0'.repeat(40)));
  git(repo, 'tag', '-d', 'v1.0.0');
  assert.throws(() => calculate(repo, head), /baseline tag is missing/u);
  git(repo, 'tag', 'v1.0.0', git(repo, 'rev-list', '--max-parents=0', 'HEAD'));
  git(repo, 'checkout', '-q', '--orphan', 'unrelated');
  git(repo, 'rm', '-q', '-rf', '.');
  git(repo, 'commit', '--allow-empty', '-q', '-m', 'fix: unrelated');
  assert.throws(() => calculate(repo, git(repo, 'rev-parse', 'HEAD')), /not reachable/u);
}));

test('shallow checkout rejects an otherwise visible release tag', () => fixture((repo) => {
  const head = commit(repo, 'fix: repair');
  const clone = mkdtempSync(join(tmpdir(), 'framework-shallow-'));
  try {
    const result = spawnSync('git', ['clone', '-q', '--depth=1', `file://${repo}`, clone], {
      encoding: 'utf8', timeout: 10000,
    });
    assert.equal(result.status, 0, result.stderr);
    git(clone, 'tag', 'v1.0.0');
    assert.throws(() => calculate(clone, head), /Complete Git history/u);
  } finally {
    rmSync(clone, { recursive: true, force: true });
  }
}));
