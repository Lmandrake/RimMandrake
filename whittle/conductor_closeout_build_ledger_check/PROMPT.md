The work is a class guard for CONDUCTOR_CLOSEOUT_BUILD_LEDGER_CHECK: the goodbye hook's live promise died because a
squash landing replaced `.claude/settings.json` and unwired every hook. The guard is a selftest that goes red whenever a
hook any live promise relies on is missing from the committed settings, shown failing on that landing's settings, green
at HEAD, then the item closes again.

The owner's words and what we owe the user are in `whittle/conductor_closeout_build_ledger_check/STATEMENT.md`. That is
the only thing you may not change. The owner's later rulings are in `whittle/conductor_closeout_build_ledger_check/NOTES.md`,
newest first. Reread both before you claim done; when they and this conversation disagree, the files win.

BE CREATIVE. Figure out the problems and solve them. Don't just work to a checklist. Use it the way a user would,
look at what they would actually see, work out what's really wrong, and fix it. Everything but that statement is
yours: code, assets, tests, harnesses. If a test is wrong or in your way, fix it or drop it.

How to see what the user sees: the "user" is the nightly sweep and the next landing. Run the guard on HEAD's settings
(green) and on `git show 8fb9f7f2b6:.claude/settings.json` saved to scratch (red, naming conductor_goodbye.py and the
other dropped hooks); then `rimflow guard CONDUCTOR_CLOSEOUT_BUILD_LEDGER_CHECK --test <test> --instance "<args>"`.
Save the outputs in `whittle/conductor_closeout_build_ledger_check/evidence/`. Show ordinary use, not a staged best case.

What you have, by name (agents tend to overlook what isn't named, so this list is meant to be complete):
- Run: `python3 src/RimMandrake/Utils/run_selftests.py --only <test>`; fast check: `python3 <test> [--settings <path>]`.
- Wiring checker: `src/RimMandrake/rimflow/live_line.py` (`_hook`, `check`); promise sources: the ledger through
  `src/RimMandrake/rimflow/model.py` `read()`/`replay()`, and `src/RimMandrake/rimflow/live_baseline.txt`; the deadman
  `src/RimMandrake/Utils/deadman_check.py` and its last pass `/mnt/d/ClaudeWork/rimmandrake/ops_watch/live_sweep.json`.
- Existing tests to extend rather than duplicate: `.claude/hooks/selftest_conductor_goodbye.py`,
  `src/RimMandrake/rimflow/selftest_live_gate.py`, `src/RimMandrake/rimflow/selftest_conductor_closeout.py`.
- History: commits 8fb9f7f2b6 (the clobber) and 943a7a66da (the restore); `rimflow show CONDUCTOR_CLOSEOUT_BUILD_LEDGER_CHECK`.
- A second model: the `chatgpt-consult` skill (`python3 src/RimMandrake/Utils/gpt_consult.py "q" -f <file>`).
What you may not touch: any game, the bridge, any systemd timer (the owner stopped the pipeline), `~/.claude/settings.json`,
`/home/mandrake/rm/dispatch`, other seats' clones, anything outside this item; and the Whittle machinery itself:
`whittle/conductor_closeout_build_ledger_check/STATEMENT.md`, `whittle/conductor_closeout_build_ledger_check/NOTES.md`,
`whittle/conductor_closeout_build_ledger_check/STOP`, `whittle/conductor_closeout_build_ledger_check/JUDGE_PROMPT.md`,
`whittle/conductor_closeout_build_ledger_check/JUDGE.md`, the Stop hook and its settings. Those belong to the owner and the
judge. Work lands on main through ./publish: commit what works, keep experiments in scratch.

How to work:
- Fix as many things as you can. Search before you build: don't assume something isn't there, and don't trust old
  notes without checking.
- Don't write placeholders or stand-ins. Build the real thing. Don't file tickets or leave a problem as a note when
  you can fix it now.
- Keep the wheel turning fast: the smallest setup that shows the problem. Send heavy reading to subagents so your
  context stays clear.
- If something truly needs the owner, write it in `whittle/conductor_closeout_build_ledger_check/BLOCKED.md` and stop;
  that is always allowed.

Before you claim done:
1. Ask a different model to broaden your testing: give it the statement, what you tested and how, and ask what a real
   user would try that you haven't (someone new, someone experienced, someone trying to break it, a messy real case).
   Try the one or two most revealing and look. Write the question, the answer and what you found in
   `whittle/conductor_closeout_build_ledger_check/BROADEN.md`.
2. Write `whittle/conductor_closeout_build_ledger_check/DONE.md` from its template: every statement line, your honest
   verdict, and fresh evidence files.
3. Spawn a fresh subagent judge (an ordinary subagent, not a fork, which would inherit this conversation) and give it
   `whittle/conductor_closeout_build_ledger_check/JUDGE_PROMPT.md` as its whole brief, plus the run command if it needs
   one. It writes `whittle/conductor_closeout_build_ledger_check/JUDGE.md`; you don't. If it would not show the work, keep
   going on what it found.

You're done when, in real use, you would be happy to show this to the owner. A hook will not let you stop before
then (it is a checklist: it refuses an incomplete or stale claim, not a weak one). When it refuses, read its reason and
do what it says. Don't write thin evidence to satisfy it; the judge and the owner read the files. The owner looks after
the judge.

## This loop's round (appended to the Whittle prompt by loop.sh)

Before anything else read `infrastructure/whittle_claude/common.md` (the project rules and the blockages) and
`infrastructure/whittle_claude/lane_offline.md` (what your lane may touch). The item is `CONDUCTOR_CLOSEOUT_BUILD_LEDGER_CHECK`; your Whittle
directory is `whittle/conductor_closeout_build_ledger_check`; its `MODE` file says `whittle` or `pilot`.

- Mode `whittle`: build until every STATEMENT bullet is true and shown by evidence, then let the judge pass it.
- Mode `pilot`: this is a Test Pilot sitting, not another code-and-retest round. Run `rimflow pilot CONDUCTOR_CLOSEOUT_BUILD_LEDGER_CHECK` and follow
  the brief it prints, with the `test-pilot-sitting` skill: experiments that discriminate between hypotheses, each
  recorded in NOTES.md, then the fix or the filed finding.
- Live evidence comes only from your lane's game, held through the bridge lock as your lane file says, and released
  before you stop. Record proof runs on the item the way its proof script does (modcheck, or `rimflow live`: read `--help`) so the ledger
  carries them.
- Commit and `./publish` your work as it lands (explicit paths). Do NOT close the item here: the wrap-up phase closes,
  parks or drops it after checking your DONE.md and the judge.
- If you cannot go on without the owner, write the question as common.md says, put one line in `whittle/conductor_closeout_build_ledger_check/BLOCKED.md`
  naming it, and stop.
