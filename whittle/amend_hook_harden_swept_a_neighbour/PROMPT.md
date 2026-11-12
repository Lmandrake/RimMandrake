The work: re-close AMEND_HOOK_HARDEN_SWEPT_A_NEIGHBOUR. The amend refusal in `.claude/hooks/block_blanket_git_stage.py`
must still hold as registered. A class guard must also be added, so that a landing which clobbers
`.claude/settings.json` (as 8fb9f7f2b6 did) fails a selftest instead of silently unwiring every safety hook.

The owner's words and what we owe the user are in `whittle/amend_hook_harden_swept_a_neighbour/STATEMENT.md`. That is the only thing you may not change.
The owner's later rulings are in `whittle/amend_hook_harden_swept_a_neighbour/NOTES.md`, newest first. Reread both before you claim done; when they and this
conversation disagree, the files win.

BE CREATIVE. Figure out the problems and solve them. Don't just work to a checklist. Use it the way a user would,
look at what they would actually see, work out what's really wrong, and fix it. Everything but that statement is
yours: code, assets, tests, harnesses. If a test is wrong or in your way, fix it or drop it.

How to see what the user sees: an agent that runs `git commit --amend` in this clone gets refused. Feed the REGISTERED
command line from `.claude/settings.json` a PreToolUse JSON payload on stdin and read its decision. Run the guard
selftest against main's settings, and against `git show 8fb9f7f2b6:.claude/settings.json` written to scratch. Save what you
judge by in `whittle/amend_hook_harden_swept_a_neighbour/evidence/`. Show ordinary use, not a staged best case.

What you have, by name (agents tend to overlook what isn't named, so this list is meant to be complete):
- `python3 .claude/hooks/selftest_block_blanket_git_stage.py` (seconds); `python3 src/RimMandrake/Utils/run_selftests.py --only <t>`
- `src/RimMandrake/rimflow/live_line.py` (`_hook`, `settings_paths`), `src/RimMandrake/rimflow/live_baseline.txt`,
  the RUNNER `live` events in `infrastructure/state/ledger/events/RUNNER.jsonl`, and commits 8fb9f7f2b6 and 943a7a66da
- `rimflow guard --help`, `rimflow close --help` (the running-promise flag with `hook=block_blanket_git_stage.py`),
  `python3 src/RimMandrake/Utils/code_review_status.py check <path>`
- the lane gate `infrastructure/whittle_claude/gate.py` refuses Bash text containing the close's promise flag: see NOTES.md
- a second model: the `chatgpt-consult` skill, or `python3 src/RimMandrake/Utils/gpt_consult.py "q" -f <file>`
What you may not touch: any RimWorld game or the bridge, on any machine; other loops' clones; other items (cite the
guard on them later, but do not close them here); and the Whittle machinery itself: `whittle/amend_hook_harden_swept_a_neighbour/STATEMENT.md`,
`whittle/amend_hook_harden_swept_a_neighbour/NOTES.md`, `whittle/amend_hook_harden_swept_a_neighbour/STOP`, `whittle/amend_hook_harden_swept_a_neighbour/JUDGE_PROMPT.md`,
`whittle/amend_hook_harden_swept_a_neighbour/JUDGE.md`, the Stop hook and its settings. Those belong to the owner and the judge.
Work lands on main through ./publish: commit what works, keep experiments in scratch.

How to work:
- Fix as many things as you can. Search before you build: don't assume something isn't there, and don't trust old
  notes without checking.
- Don't write placeholders or stand-ins. Build the real thing. Don't file tickets or leave a problem as a note when
  you can fix it now.
- Keep the wheel turning fast: the smallest setup that shows the problem. Send heavy reading to subagents so your
  context stays clear.
- If something truly needs the owner, write it in `whittle/amend_hook_harden_swept_a_neighbour/BLOCKED.md` and stop; that is always allowed.

Before you claim done:
1. Ask a different model to broaden your testing: give it the statement, what you tested and how, and ask what a real
   user would try that you haven't (someone new, someone experienced, someone trying to break it, a messy real case).
   Try the one or two most revealing and look. Write the question, the answer and what you found in
   `whittle/amend_hook_harden_swept_a_neighbour/BROADEN.md`.
2. Write `whittle/amend_hook_harden_swept_a_neighbour/DONE.md` from its template: every statement line, your honest verdict, and fresh evidence files.
3. Spawn a fresh subagent judge (an ordinary subagent, not a fork, which would inherit this conversation) and give it
   `whittle/amend_hook_harden_swept_a_neighbour/JUDGE_PROMPT.md` as its whole brief, plus the run command if it needs one. It writes
   `whittle/amend_hook_harden_swept_a_neighbour/JUDGE.md`; you don't. If it would not show the work, keep going on what it found.

You're done when, in real use, you would be happy to show this to the owner. A hook will not let you stop before
then (it is a checklist: it refuses an incomplete or stale claim, not a weak one). When it refuses, read its reason and
do what it says. Don't write thin evidence to satisfy it; the judge and the owner read the files. The owner looks after
the judge.
