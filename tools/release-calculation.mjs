#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import { CommitParser } from 'conventional-commits-parser';
import createPreset from 'conventional-changelog-conventionalcommits';
import semver from 'semver';

const parser = new CommitParser(createPreset().parser);
const releaseTag = /^v(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)$/u;
const headerPattern = /^[a-z][a-z0-9-]*(?:\([a-z0-9-]+\))?!?: \S.*$/u;
const fullSha = /^[0-9a-f]{40}(?:[0-9a-f]{24})?$/u;

function git(repo, ...args) {
  const result = spawnSync('git', ['-C', repo, ...args], {
    encoding: 'utf8', timeout: 15000, maxBuffer: 16 * 1024 * 1024,
  });
  if (result.error || result.status !== 0) {
    throw new Error(`Git ${args[0]} failed; release history is unavailable or invalid`);
  }
  return result.stdout.trimEnd();
}

function isAncestor(repo, ancestor, head) {
  const result = spawnSync('git', ['-C', repo, 'merge-base', '--is-ancestor', ancestor, head], {
    timeout: 15000,
  });
  if (result.error || ![0, 1].includes(result.status)) {
    throw new Error('Git ancestry check failed; release history is unavailable');
  }
  return result.status === 0;
}

export function classifyMessage(message) {
  const parsed = parser.parse(message);
  if (!parsed.header || !headerPattern.test(parsed.header) || !parsed.type || !parsed.subject) {
    throw new Error('Malformed Conventional Commit header');
  }
  const footerPresent = /^BREAKING(?: CHANGE|-CHANGE):/mu.test(message);
  const breakingNotes = parsed.notes.filter((note) =>
    (note.title === 'BREAKING CHANGE' || note.title === 'BREAKING-CHANGE') && note.text.trim(),
  );
  if (footerPresent && breakingNotes.length === 0) {
    throw new Error('Malformed breaking-change footer');
  }
  if (/^[a-z][a-z0-9-]*(?:\([a-z0-9-]+\))?!:/u.test(parsed.header) || breakingNotes.length > 0) {
    return 'major';
  }
  if (parsed.type === 'feat') return 'minor';
  if (parsed.type === 'fix' || parsed.type === 'perf' || parsed.type === 'docs') return 'patch';
  return null;
}

export function calculate(repo, head) {
  if (!fullSha.test(head)) throw new Error('Expected a full validated commit SHA');
  if (git(repo, 'rev-parse', '--is-shallow-repository') !== 'false') {
    throw new Error('Complete Git history is required');
  }
  const actualHead = git(repo, 'rev-parse', '--verify', `${head}^{commit}`);
  if (actualHead !== head) throw new Error('Validated SHA does not name a commit');
  const tags = git(repo, 'for-each-ref', '--format=%(refname:short)', 'refs/tags')
    .split('\n').filter((tag) => releaseTag.test(tag) && semver.valid(tag.slice(1)));
  if (!tags.includes('v1.0.0')) throw new Error('Required v1.0.0 baseline tag is missing');
  const baseline = git(repo, 'rev-parse', '--verify', 'refs/tags/v1.0.0^{commit}');
  if (!isAncestor(repo, baseline, head)) throw new Error('v1.0.0 is not reachable from the validated SHA');
  const reachable = tags.filter((tag) => {
    const commit = git(repo, 'rev-parse', '--verify', `refs/tags/${tag}^{commit}`);
    return isAncestor(repo, commit, head);
  });
  if (reachable.length === 0) throw new Error('No reachable release tag');
  reachable.sort((a, b) => semver.rcompare(a.slice(1), b.slice(1)));
  const previousTag = reachable[0];
  const previousCommit = git(repo, 'rev-parse', '--verify', `refs/tags/${previousTag}^{commit}`);
  const hashes = git(repo, 'rev-list', '--reverse', `${previousCommit}..${head}`)
    .split('\n').filter(Boolean);
  const priority = { patch: 1, minor: 2, major: 3 };
  let bump = null;
  for (const hash of hashes) {
    const parents = git(repo, 'show', '-s', '--format=%P', hash).split(' ').filter(Boolean);
    if (parents.length !== 1) {
      throw new Error(`Release range contains a non-squash merge [commit ${hash}]`);
    }
    const message = git(repo, 'show', '-s', '--format=%B', hash);
    let current;
    try {
      current = classifyMessage(message);
    } catch (error) {
      throw new Error(`${error.message} [commit ${hash}]`, { cause: error });
    }
    if ((priority[current] || 0) > (priority[bump] || 0)) bump = current;
  }
  return {
    previousTag, previousCommit, head, commitCount: hashes.length, bump,
    nextTag: bump ? `v${semver.inc(previousTag.slice(1), bump)}` : null,
  };
}

function option(args, name) {
  const index = args.indexOf(name);
  if (index < 0 || index + 1 >= args.length) throw new Error(`Missing ${name}`);
  return args[index + 1];
}

function main(args) {
  const mode = args[0];
  if (mode === 'calculate') {
    if (args.length !== 5) throw new Error('Usage: calculate --repo PATH --head FULL_SHA');
    return calculate(option(args, '--repo'), option(args, '--head'));
  }
  if (mode === 'validate-message') {
    if (args.length !== 3) throw new Error('Usage: validate-message --message-file PATH');
    const bump = classifyMessage(readFileSync(option(args, '--message-file'), 'utf8'));
    return { valid: true, bump };
  }
  if (mode === 'validate-pr') {
    if (args.length !== 3) throw new Error('Usage: validate-pr --event-file PATH');
    const event = JSON.parse(readFileSync(option(args, '--event-file'), 'utf8'));
    const title = event.pull_request?.title;
    const body = event.pull_request?.body ?? '';
    if (typeof title !== 'string' || typeof body !== 'string') {
      throw new Error('Pull request title/body unavailable');
    }
    return { valid: true, bump: classifyMessage(`${title}\n\n${body}`) };
  }
  throw new Error('Usage: calculate|validate-message|validate-pr');
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    console.log(JSON.stringify(main(process.argv.slice(2))));
  } catch (error) {
    console.error(`Release calculation: ${error.message}`);
    process.exitCode = 1;
  }
}
