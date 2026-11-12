# Broaden: a second model on what a real user would try

Asked 2026-11-11 20:04 -08:00, GPT through `src/RimMandrake/Utils/gpt_consult.py` (gpt-6.1-sol, job
consult-20261111-200353-1996850-e04470). It was given STATEMENT.md, the guard test, the history replay and the green
run.

## The question

I built a class-guard selftest (attached: the statement it must satisfy, the test, and its runs). What it guards: a landing
(8fb9f7f2b6, a branch squash) replaced the repo's .claude/settings.json with a 1-hook version, silently unwiring ~40
Claude Code safety hooks for 8 hours. The test reads every `hook=<file>` promise from the ledger and live_baseline.txt
(minus retired ones) and checks each with the deadman's own wiring check against the repo's .claude/settings.json.

What I tested and how: (1) today's file: green 28/28; (2) the 8fb9f7f2b6 copy via --settings: red, names all 28 hooks;
(3) replay on settings at 5 commits around the outage: green/red/red/green/green exactly matching the window; (4) the
dispatch tree's settings: green; (5) fixtures inside the test: real settings minus one hook reports exactly that hook;
a lookalike x_<name> does not count; a ledger-only promise dropped is reported; disableAllHooks reports all; a wired
hook whose file is missing is reported.

Question: what would a real user try that I have not -- someone new, someone experienced, someone trying to break it, a
messy real case? Rank the 5 most revealing concrete experiments (input -> what a false green or false red would look
like). Be concrete about JSON shapes and git scenarios. Under 400 words.

## The answer (verbatim)

1. **Check whether `--settings` is independent of the default file.** Save known-good settings, replace the repo’s settings with `{"hooks":{}}`, then run with `--settings <good-copy>`. A false red reports failure despite the selected file satisfying every promise. The shown code predicts this outcome because `sanity()` builds fixtures from the default settings and subtracts its existing failures.

2. **Keep the hook’s name while making its command inert.** Replace its sole entry with this shape, preserving other hooks.

   ```json
   {"hooks":{"PreToolUse":[{"matcher":"Bash","hooks":[{"type":"command","command":"echo block_agent_over_slots.py"}]}]}}
   ```

   A false green accepts a command that prints the filename. Separately retain the real command but change its matcher to `__never_a_tool__`. Green would expose a trigger-coverage gap despite apparent wiring.

3. **Replay a squash that also loses its promise.** On main, add and wire a ledger-only `hook=fixture_guard.py`. Land a stale branch squash that removes both that ledger row and its settings entry, preserving the existing target promise and other hooks. A false green passes because the missing obligation disappeared from the guard’s inputs. Your historical replay retained today’s promises, so it doesn’t exercise this failure.

4. **Run from conflicting worktrees and working directories.** Create worktrees A and B. Give B a unique ledger-only promise, its hook file, and settings missing that hook. Run B’s script while the shell’s working directory is A, then reverse the arrangement. A false green reads A’s promises while checking B. A false red requires hooks promised solely in A. This probes source discovery beyond passing another tree’s settings through `--settings`.

5. **Exercise path collisions and partial retirement.** Promise both `hook=.claude/hooks/a/check.py` and `hook=.claude/hooks/b/check.py`. Create both files, but wire only `"command":"python3 .claude/hooks/a/check.py"`. Require red identifying B’s missing wiring. Then retire only A’s subject and rerun. A false green treats the shared basename as sufficient or lets A’s retirement erase B’s obligation. For the complementary false-red check, wire both paths and require green.

## What I tried and found

- **(1) `--settings` and the default file are tangled. Tried it, and it was real.** The first version cut its sanity fixtures from the
  repo's own settings and subtracted that file's failures. On a clobbered clone (the very case the guard is for), the
  sanity rows went red as well, reading as if the instrument had gone blind ("got []"). A fresh Opus reviewer found the
  same thing, plus crash paths: a top-level `[]`, an event holding a dict, and a bare `--settings`. `rimflow guard` would
  have read those as a crash, not a red. **Fixed:** the instrument rows now run on synthetic settings and a project
  root of their own. A malformed settings file is a red row, never a traceback. On the 8fb9f7f2b6 copy, only the
  main rows go red and every instrument row stays green (`evidence/guard_instance_8fb9f7f2b6.txt`).
- **(3) A squash that rolls back the promise along with the wiring. Tried it, and it was real.** A landing that also restores an older
  `live_baseline.txt` takes the baseline promise out of the guard's inputs, so the main row passes. Added a row: every
  `hook=` line ever added to live_baseline.txt (from its git history) must still be there or be retired in
  live_retired.txt. Replayed by removing `hook=bench_mode.py` from both the baseline and the settings: the main row
  reads 27 of 27, and the history row goes red naming `hook=bench_mode.py`
  (`evidence/guard_baseline_rollback.txt`; the baseline was put back afterwards). A rollback of ledger events is
  outside this guard: the ledger is append-only and `block_ledger_lint.py` refuses a push that is not an append.
- **(2) An inert command that names the hook (`echo block_agent_over_slots.py`), or a matcher that never fires. Not
  pursued.** The class is a landing that replaces the file. Writing a decoy command on purpose is a different defect,
  and judging which matcher is "right" for each hook is a design question per hook, not a wiring census. One related
  hole is now closed: a hook name that appears only outside any `command` (in a matcher, say) is reported, because the
  guard walks hooks.<Event>[].hooks[].command itself (fixture row "named only in a matcher").
- **(4) Worktrees and a mismatched cwd.** Worktrees are off in this project (`block_worktrees.py`). The test resolves
  everything from its own file path, never from the cwd. Its ledger read is the deadman's own reader (the bench
  clone plus this clone), so another clone adds promises; it cannot swap them. Not run.
- **(5) Two hooks sharing a basename in different folders.** Read, not run. Each spelling is checked as written, and
  the first that fails reports the group, so `b/check.py` missing is still named. Retirement matches the literal
  subject, as the deadman does.
