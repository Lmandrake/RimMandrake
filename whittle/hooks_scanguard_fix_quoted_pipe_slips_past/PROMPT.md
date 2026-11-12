The work is closing HOOKS_SCANGUARD_FIX_QUOTED_PIPE_SLIPS_PAST for good: `.claude/hooks/block_blind_scan.py` refuses a
scan whose quoted argument holds a separator (already fixed at a2bac49a9a), and the way the fix "died" (its `hook=`
running-promise read "not wired" on Archmagi's `~/rm/dispatch` clone) is caught by a class guard test before it can
happen again, so the item closes and stays closed.

The owner's words and what we owe the user are in `whittle/hooks_scanguard_fix_quoted_pipe_slips_past/STATEMENT.md`.
That is the only thing you may not change. The owner's later rulings are in
`whittle/hooks_scanguard_fix_quoted_pipe_slips_past/NOTES.md`, newest first. Reread both before you claim done; when
they and this conversation disagree, the files win.

BE CREATIVE. Figure out the problems and solve them. Don't just work to a checklist. Use it the way a user would,
look at what they would actually see, work out what's really wrong, and fix it. Everything but that statement is
yours: code, assets, tests, harnesses. If a test is wrong or in your way, fix it or drop it.

How to see what the user sees: pipe a Bash PreToolUse payload into the hook
(`echo '{"tool_name":"Bash","tool_input":{"command":"grep -c \"a;b\" Player.log"}}' | python3 .claude/hooks/block_blind_scan.py; echo $?`)
and read its refusal; run `python3 -c "import sys; sys.path.insert(0,'src/RimMandrake/rimflow'); import live_line as L; print(L.check('hook=block_blind_scan.py'))"`
for the running-promise check (None = passes); `rimflow show HOOKS_SCANGUARD_FIX_QUOTED_PIPE_SLIPS_PAST` for what the
ledger owes. Save what you judge by in `whittle/hooks_scanguard_fix_quoted_pipe_slips_past/evidence/`. Show ordinary
use, not a staged best case.

What you have, by name (agents tend to overlook what isn't named, so this list is meant to be complete):
- `python3 .claude/hooks/selftest_block_blind_scan.py` (seconds; 30/30 at setup); `python3
  src/RimMandrake/Utils/run_selftests.py --only <tests>` before a commit.
- `src/RimMandrake/rimflow/live_line.py` (`_hook`, `settings_paths`, `check`), the existing
  `src/RimMandrake/rimflow/selftest_live_*.py`, `rimflow guard --help` and its code in `src/RimMandrake/rimflow/cli.py`,
  the item's history and runs (`rimflow show`), the deadman (`deadman_check.py`) that reopened it, and the three items
  reopened by the same sweep (named in NOTES.md).
- A second model: the `chatgpt-consult` skill (`python3 src/RimMandrake/Utils/gpt_consult.py "q" -f <file>`).
What you may not touch: any running RimWorld or the bridge on any machine, other seats' clones (`~/rm/bench`,
`~/rm/runner`, Archmagi's `~/rm/dispatch`), the user-level `~/.claude/settings.json`, other items; and the Whittle
machinery itself: `whittle/hooks_scanguard_fix_quoted_pipe_slips_past/STATEMENT.md`,
`whittle/hooks_scanguard_fix_quoted_pipe_slips_past/NOTES.md`, `whittle/hooks_scanguard_fix_quoted_pipe_slips_past/STOP`,
`whittle/hooks_scanguard_fix_quoted_pipe_slips_past/JUDGE_PROMPT.md`, `whittle/hooks_scanguard_fix_quoted_pipe_slips_past/JUDGE.md`,
the Stop hook and its settings. Those belong to the owner and the judge. Work lands on main through ./publish: commit
what works, keep experiments in scratch.

How to work:
- Fix as many things as you can. Search before you build: don't assume something isn't there, and don't trust old
  notes without checking.
- Don't write placeholders or stand-ins. Build the real thing. Don't file tickets or leave a problem as a note when
  you can fix it now.
- Keep the wheel turning fast: the smallest setup that shows the problem. Send heavy reading to subagents so your
  context stays clear.
- If something truly needs the owner, write it in `whittle/hooks_scanguard_fix_quoted_pipe_slips_past/BLOCKED.md` and
  stop; that is always allowed.

Before you claim done:
1. Ask a different model to broaden your testing: give it the statement, what you tested and how, and ask what a real
   user would try that you haven't (someone new, someone experienced, someone trying to break it, a messy real case).
   Try the one or two most revealing and look. Write the question, the answer and what you found in
   `whittle/hooks_scanguard_fix_quoted_pipe_slips_past/BROADEN.md`.
2. Write `whittle/hooks_scanguard_fix_quoted_pipe_slips_past/DONE.md` from its template: every statement line, your
   honest verdict, and fresh evidence files.
3. Spawn a fresh subagent judge (an ordinary subagent, not a fork, which would inherit this conversation) and give it
   `whittle/hooks_scanguard_fix_quoted_pipe_slips_past/JUDGE_PROMPT.md` as its whole brief, plus the run command if it
   needs one. It writes `whittle/hooks_scanguard_fix_quoted_pipe_slips_past/JUDGE.md`; you don't. If it would not show
   the work, keep going on what it found.

You're done when, in real use, you would be happy to show this to the owner. A hook will not let you stop before
then (it is a checklist: it refuses an incomplete or stale claim, not a weak one). When it refuses, read its reason and
do what it says. Don't write thin evidence to satisfy it; the judge and the owner read the files. The owner looks after
the judge.
