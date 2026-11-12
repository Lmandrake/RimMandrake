# Broadening the testing — 2026-11-11 20:12 -08:00

Second model: GPT (`gpt_consult.py`, model gpt-6.1-sol, job consult-20261111-200654-2011159-a107dd), given the
selftest, `live_line.py` and STATEMENT.md.

## The question

> What would a real user (the nightly selftest sweep; the next person landing a squash; someone new; someone trying to
> break it; a messy real case) try that I have not? Name concrete failure modes where this guard would stay GREEN while
> hooks are really unwired, or go RED falsely. Max 12 bullets, ranked by how likely.

What I had tested when I asked: green on the working tree at HEAD and at `--rev` HEAD / 943a7a66da / 8fb9f7f2b6~1; red on
`--rev 8fb9f7f2b6` and on `--settings <that file saved to scratch>` (all 30 named with the items relying on them);
fixtures (dropped hook, deleted script, disableAllHooks, name-inside-name, unreadable JSON); one mutant per real hook.

## The answer (condensed, in its order)

1. Default mode reads the working tree: an uncommitted restoration or an untracked script hides a broken HEAD.
2. A hook moved to the wrong event, or behind a matcher that never fires, still reads as wired.
3. `--rev` judges an old commit against today's promises: new promises condemn old commits.
4. False RED: `python3 "${CLAUDE_PROJECT_DIR}"/.claude/hooks/foo.py` (quote before the slash) resolves to `/.claude/...`.
5. `disableAllHooks` in settings.local.json or a higher-precedence file is not read.
6. A no-op command naming the file (`true # .claude/hooks/foo.py`) reads as wired.
7. A malformed promise (`hook=foo.py extra=x`) is silently skipped, so its hook can be unwired unseen.
8. `python3 /missing/foo.py # .claude/hooks/foo.py`: any existing candidate path satisfies the check.
9. Basename-only retirement: retiring `hook=legacy/foo.py` also retires `.claude/hooks/foo.py`.
10. False RED: promise `hook=.claude/hooks/foo.py` run as `python3 .claude/hooks/foo.py` resolves to
    `.claude/hooks/.claude/hooks/foo.py`.
11. A dangling symlink or a folder at the script path passes the existence check (and `--rev` accepts any git object).
12. Show the real sweep discovers it and propagates the exit status.

## What I tried and what I found

- **4 and 10 were real false REDs in the shared checker** (`live_line._hook`, which the deadman and `rimflow close` use
  too). Reproduced both in fixtures, fixed `_hook` (quote-split paths are retried under the project; a name standing
  alone is resolved as itself, and a bare one also under `.claude/hooks/`). Both spellings, plus
  `"$CLAUDE_PROJECT_DIR/.claude/hooks/x"`, are now fixture rows. `selftest_live_gate.py` stayed green after a first
  version broke it (a bare `"wired_one.py"` token stopped resolving to `.claude/hooks/`; fixed).
- **7 was real**: unparseable hook lines are now returned and each is a FAIL, never skipped (fixture row `D`).
- **9 was real**: a bare `hook=x.py` retirement still covers every path spelling (what live_retired.txt holds today); a
  path-qualified retirement now covers that path only (fixture rows `G`/`H`).
- **11 was real**: the default existence test is `os.path.isfile` (a dangling link and a folder are red, fixture rows);
  `--rev` requires a regular blob (`git ls-tree` mode 100644/100755), not any object.
- **1 was real for the nightly**: by default the test now judges this clone's file AND HEAD's committed copy whenever
  the two differ. Shown with a pre-commit probe (temp copy of settings minus conductor_goodbye.py, real file untouched):
  the clone's copy red naming it, HEAD's committed copy green, exit 1
  (`evidence/dirty_tree_probe.txt`).
- **3 is by design** and shown, not hidden: `--rev` replays an instance against today's promises. The history sweep
  (`evidence/history_sweep.txt`) shows every settings commit from 6077899266 (2026-11-06) to HEAD green except the
  clobber (0 of 30); older commits are red only on hooks that were added later, never on one that existed then.
- **12**: `run_selftests.py --only selftest_live_hooks_wired` discovers and runs it (RESULT GREEN); it reads git state,
  so the known-results cache never answers for it and the nightly always runs it (`evidence/run_selftests_only.txt`).
- **Not acted on, and why**: 2 (event/matcher placement) is a different class: a `hook=` promise says a hook is wired,
  not where; `selftest_conductor_goodbye.py` still pins conductor_goodbye.py to UserPromptSubmit. 5 (settings.local.json,
  untracked, per-clone) is not committed state, so it is outside "the committed `.claude/settings.json`". 6 and 8 need
  someone deliberately writing a decoy command; the guard is for an accidental clobber, which drops whole entries.
