import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import {
  calculate,
  classifyMessage,
  classifyPlannedPrTitle,
  validateSquashMessage,
} from '../tools/release-calculation.mjs';

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
  ['docs: clarify release policy', 'v1.0.1'],
  ['docs(ai): update framework rules', 'v1.0.1'],
  ['test: cover release fixture', null],
  ['chore: maintain tooling', null],
  ['feature: alias excluded by ticket policy', null],
  ['revert: excluded by ticket policy', null],
  ['docs: explain !: marker in prose', 'v1.0.1'],
]) {
  test(`calculates ${expected ?? 'no release'} for ${message.split('\n')[0]}`, () => fixture((repo) => {
    const head = commit(repo, message);
    const result = calculate(repo, head);
    assert.equal(result.previousTag, 'v1.0.0');
    assert.equal(result.nextTag, expected);
    assert.equal(result.commitCount, 1);
  }));
}

test('highest bump covers the complete range and lower-priority additions do not increase it', () =>
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

test('message and PR input validation enforce GitHub-style planned squash input', () => fixture((repo) => {
  const message = [
    'feat(api)!: [issue-3] add tag mode - PR1 (#42)',
    '',
    '* feat(api): [issue-3][step-1] add tag selection',
    '',
    '* docs(api): [issue-3][step-2] explain tag migration',
  ].join('\n');
  const messagePath = join(repo, 'squash.txt');
  writeFileSync(messagePath, message);
  const script = new URL('../tools/release-calculation.mjs', import.meta.url).pathname;
  const valid = spawnSync('node', [script, 'validate-message', '--message-file', messagePath], {
    encoding: 'utf8', timeout: 10000,
  });
  assert.equal(valid.status, 0, valid.stderr);
  assert.deepEqual(JSON.parse(valid.stdout), {
    valid: true, bump: 'major', pullRequestNumber: 42, commitCount: 2,
  });
  const eventPath = join(repo, 'event.json');
  writeFileSync(eventPath, JSON.stringify({ pull_request: {
    title: 'docs(ai): [issue-3] title before edit - PR2', body: 'No breaking change',
  } }));
  const before = spawnSync('node', [script, 'validate-pr', '--event-file', eventPath], {
    encoding: 'utf8', timeout: 10000,
  });
  assert.equal(before.status, 0, before.stderr);
  assert.equal(JSON.parse(before.stdout).bump, 'patch');
  writeFileSync(eventPath, JSON.stringify({ pull_request: {
    title: 'feat!: edited title - PR1', body: 'Migration: clients must update.',
  } }));
  const after = spawnSync('node', [script, 'validate-pr', '--event-file', eventPath], {
    encoding: 'utf8', timeout: 10000,
  });
  assert.equal(after.status, 0, after.stderr);
  assert.equal(JSON.parse(after.stdout).bump, 'major');
  writeFileSync(eventPath, JSON.stringify({ pull_request: {
    title: 'feat: [issue-3] body-only breaking - PR1',
    body: 'BREAKING CHANGE: migrate clients',
  } }));
  const invalid = spawnSync('node', [script, 'validate-pr', '--event-file', eventPath], {
    encoding: 'utf8', timeout: 10000,
  });
  assert.equal(invalid.status, 1);
}));

test('planned PR title validation covers issue, ad hoc, step, suffix, and whole-purpose syntax', () => {
  assert.equal(
    classifyPlannedPrTitle(
      'chore(policy-search): [issue-235] quiesce Java consumers - PR4',
    ),
    null,
  );
  assert.equal(classifyPlannedPrTitle('fix!: replace compatibility contract - PR1'), 'major');
  for (const title of [
    'feat(ai): [issue-10][step-2] add release identity - PR1',
    'feat(ai): [issue-10][STEP-2] add release identity - PR1',
    'feat(ai): [STEP-2] add release identity - PR1',
    'feat(ai): [issue-0] add release identity - PR1',
    'feat(ai): [Issue-10] add release identity - PR1',
    'feat(ai): explain [issue-10] compatibility - PR1',
    'feat(ai): [issue-10] add release identity',
    'feat(ai): [issue-10] add release identity - PR0',
    'feat(ai): [issue-10] add release identity - PR999 (#44)',
  ]) {
    assert.throws(() => classifyPlannedPrTitle(title));
  }
});

test('proposed squash validation rejects missing suffixes and malformed commit lists', () => {
  const title = 'feat: [issue-3] add tag mode - PR1';
  const valid = `${title} (#42)\n\n* feat: first source commit\n\n* fix: second source commit`;
  assert.deepEqual(validateSquashMessage(valid), {
    bump: 'minor', pullRequestNumber: 42, commitCount: 2,
  });
  for (const message of [
    `${title}\n\n* feat: source commit`,
    `${title} (#0)\n\n* feat: source commit`,
    `${title} (#42)`,
    `${title} (#42)\n\nfeat: source commit`,
    `${title} (#42)\n\n* feat: source commit\n* fix: source commit`,
  ]) {
    assert.throws(() => validateSquashMessage(message));
  }
});

test('proposed squash validation matches title, PR number, and ordered source commits', () => {
  const title = 'fix(k8s): [issue-287] secure Dashboard deployment and signals - PR3';
  const subjects = [
    'fix(dashboard): [issue-287][step-10D] provision reader prerequisites',
    'fix(dashboard): [issue-287][step-10D] apply canonical Secret data',
  ];
  const message = `${title} (#306)\n\n${subjects.map((subject) => `* ${subject}`).join('\n\n')}`;
  const expected = { title, pullRequestNumber: 306, commitSubjects: subjects };
  assert.deepEqual(validateSquashMessage(message, expected), {
    bump: 'patch', pullRequestNumber: 306, commitCount: 2,
  });
  for (const invalidExpected of [
    { ...expected, title: `${title} revised` },
    { ...expected, pullRequestNumber: 307 },
    { ...expected, commitSubjects: [...subjects].reverse() },
    { ...expected, commitSubjects: subjects.slice(0, 1) },
    { ...expected, commitSubjects: [...subjects, 'docs: added commit'] },
    { ...expected, commitSubjects: [subjects[0], `${subjects[1]} revised`] },
  ]) {
    assert.throws(() => validateSquashMessage(message, invalidExpected));
  }
});

test('release calculation accepts GitHub-style squash bodies and historical breaking footers', () =>
  fixture((repo) => {
    const squash = [
      'feat: [issue-3] add tag mode - PR1 (#42)',
      '',
      '* feat: [issue-3][step-1] add tag selection',
      '',
      '* docs: [issue-3][step-2] explain tag selection',
    ].join('\n');
    assert.equal(calculate(repo, commit(repo, squash)).nextTag, 'v1.1.0');
    const head = commit(repo, 'chore: historical change\n\nBREAKING CHANGE: migrate the profile');
    assert.equal(calculate(repo, head).nextTag, 'v2.0.0');
  }));

test('malformed messages fail rather than becoming no-release', () => fixture((repo) => {
  for (const message of ['not conventional', 'feat: ', 'fix: valid\n\nBREAKING CHANGE:']) {
    assert.throws(() => classifyMessage(message));
  }
  assert.throws(() => calculate(repo, commit(repo, 'broken release-driving message')));
}));

test('a conventionally named merge is rejected with its commit identity', () => fixture((repo) => {
  const branch = git(repo, 'branch', '--show-current');
  git(repo, 'checkout', '-q', '-b', 'topic');
  commit(repo, 'feat: topic change');
  git(repo, 'checkout', '-q', branch);
  commit(repo, 'fix: main change');
  git(repo, 'merge', '--no-ff', '-m', 'feat: combine topic', 'topic');
  const head = git(repo, 'rev-parse', 'HEAD');
  const script = new URL('../tools/release-calculation.mjs', import.meta.url).pathname;
  const result = spawnSync('node', [script, 'calculate', '--repo', repo, '--head', head], {
    encoding: 'utf8', timeout: 10000,
  });
  assert.equal(result.status, 1);
  assert.match(result.stderr, /Release range contains a non-squash merge/u);
  assert.ok(result.stderr.includes(head));
  assert.equal(result.stdout, '');
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
