The work is a class guard for CLOSEOUT_TRAP_FIX_HELPERS_ALWAYS_ALIVE: a selftest that goes red whenever a hook named by
a `hook=` promise is missing from the repo's `.claude/settings.json` (as it was after the Pyrelands landing,
8fb9f7f2b6), green on today's file, recorded with `rimflow guard`, then the item closed with its hook promise.

The owner's words and what we owe the user are in `whittle/closeout_trap_fix_helpers_always_alive/STATEMENT.md`. That
is the only thing you may not change. The owner's later rulings are in
`whittle/closeout_trap_fix_helpers_always_alive/NOTES.md`, newest first. Reread both before you claim done; when they
and this conversation disagree, the files win.

BE CREATIVE. Figure out the problems and solve them. Don't just work to a checklist. Use it the way a user would,
look at what they would actually see, work out what's really wrong, and fix it. Everything but that statement is
yours: code, assets, tests, harnesses. If a test is wrong or in your way, fix it or drop it.

How to see what the user sees: run the selftest on the real settings file and on the instance
(`git show 8fb9f7f2b6:.claude/settings.json > <round dir>/settings_8fb9f7f2b6.json`, passed with `--settings`), and
read `rimflow show CLOSEOUT_TRAP_FIX_HELPERS_ALWAYS_ALIVE` for the guard and close events. Save what you judge by in
`whittle/closeout_trap_fix_helpers_always_alive/evidence/`. Show ordinary use, not a staged best case.

What you have, by name (agents tend to overlook what isn't named, so this list is meant to be complete):
- The run: `python3 <your selftest>` and `python3 <your selftest> --settings <path>`; it takes seconds.
  `python3 src/RimMandrake/Utils/run_selftests.py --only <name>` before a commit.
- The deadman's own check: `src/RimMandrake/rimflow/live_line.py` (`_hook(name, settings)`), the promise list in
  `src/RimMandrake/Utils/deadman_check.py`, the retired list `src/RimMandrake/rimflow/live_retired.txt`, the baseline
  `src/RimMandrake/rimflow/live_baseline.txt`, the last sweep `D:\ClaudeWork\rimmandrake\ops_watch\live_sweep.json`.
- A precedent guard: `src/RimMandrake/Utils/selftest_live_retired.py`. The guard gate: `src/RimMandrake/rimflow/repeat_guard.py`.
- The ledger history of the outage: `rimflow show CLOSEOUT_TRAP_FIX_HELPERS_ALWAYS_ALIVE`; commits 8fb9f7f2b6 and 943a7a66da.
- A second model: the `chatgpt-consult` skill (`python3 src/RimMandrake/Utils/gpt_consult.py "q" -f <file>`).
What you may not touch: any game on any machine, the bridge, systemd units, `~/.claude/settings.json`, the dispatch
tree `/home/mandrake/rm/dispatch`, other seats' items (CONDUCTOR_CLOSEOUT_BUILD_LEDGER_CHECK included), anything
outside the item; and the Whittle machinery itself: `whittle/closeout_trap_fix_helpers_always_alive/STATEMENT.md`,
`whittle/closeout_trap_fix_helpers_always_alive/NOTES.md`, `whittle/closeout_trap_fix_helpers_always_alive/STOP`,
`whittle/closeout_trap_fix_helpers_always_alive/JUDGE_PROMPT.md`, `whittle/closeout_trap_fix_helpers_always_alive/JUDGE.md`,
the Stop hook and its settings. Those belong to the owner and the judge. Work lands on main through ./publish: commit
what works, keep experiments in scratch.

How to work:
- Fix as many things as you can. Search before you build: don't assume something isn't there, and don't trust old
  notes without checking.
- Don't write placeholders or stand-ins. Build the real thing. Don't file tickets or leave a problem as a note when
  you can fix it now.
- Keep the wheel turning fast: the smallest setup that shows the problem. Send heavy reading to subagents so your
  context stays clear.
- If something truly needs the owner, write it in `whittle/closeout_trap_fix_helpers_always_alive/BLOCKED.md` and stop;
  that is always allowed.

Before you claim done:
1. Ask a different model to broaden your testing: give it the statement, what you tested and how, and ask what a real
   user would try that you haven't (someone new, someone experienced, someone trying to break it, a messy real case).
   Try the one or two most revealing and look. Write the question, the answer and what you found in
   `whittle/closeout_trap_fix_helpers_always_alive/BROADEN.md`.
2. Write `whittle/closeout_trap_fix_helpers_always_alive/DONE.md` from its template: every statement line, your honest
   verdict, and fresh evidence files.
3. Spawn a fresh subagent judge (an ordinary subagent, not a fork, which would inherit this conversation) and give it
   `whittle/closeout_trap_fix_helpers_always_alive/JUDGE_PROMPT.md` as its whole brief, plus the run command if it needs
   one. It writes `whittle/closeout_trap_fix_helpers_always_alive/JUDGE.md`; you don't. If it would not show the work,
   keep going on what it found.

You're done when, in real use, you would be happy to show this to the owner. A hook will not let you stop before
then (it is a checklist: it refuses an incomplete or stale claim, not a weak one). When it refuses, read its reason and
do what it says. Don't write thin evidence to satisfy it; the judge and the owner read the files. The owner looks after
the judge.
