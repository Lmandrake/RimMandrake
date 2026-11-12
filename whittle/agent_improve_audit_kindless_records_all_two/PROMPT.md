The daily agent-improvement loop (`src/RimMandrake/Utils/agent_improve.py`) is where an applied change records its source task kinds; today a change applied at L0 or L1 can record none, and then the generalization check (design §4.3) can never read it. The work: make such changes record kinds from a sound source, or write in §4.3 why they stay uncheckable by design, and measure how many records on file have none.

The owner's words and what we owe the user are in `whittle/agent_improve_audit_kindless_records_all_two/STATEMENT.md`. That is the only thing you may not change.
The owner's later rulings are in `whittle/agent_improve_audit_kindless_records_all_two/NOTES.md`, newest first. Reread both before you claim done; when they and this
conversation disagree, the files win.

BE CREATIVE. Figure out the problems and solve them. Don't just work to a checklist. Use it the way a user would,
look at what they would actually see, work out what's really wrong, and fix it. Everything but that statement is
yours: code, assets, tests, harnesses. If a test is wrong or in your way, fix it or drop it.

How to see what the user sees: the user is the cadence and the Conductor reading change records. Read the records in `infrastructure/state/agent_improve/changes/*.json` (`source_kinds`), run `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_agent_improve,selftest_agent_improve_cadence,selftest_agent_improve_general` and read its output, and read §4.3 of `design/RimMandrake/daily_agent_improvement_2026-11-02.md` as a stranger would. Save what you judge by in `whittle/agent_improve_audit_kindless_records_all_two/evidence/`. Show ordinary
use, not a staged best case.

What you have, by name (agents tend to overlook what isn't named, so this list is meant to be complete):
- Fast check: `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_agent_improve` (add `_cadence`, `_general`, `_steps` for what you touch); measurement: a few lines of python over `infrastructure/state/agent_improve/changes/*.json`.
- History: the item chain in `rimflow show AGENT_IMPROVE_HARDEN_CADENCE_EMPTY_KINDS` and its ancestors (`infrastructure/state/items/closed/`); piece sources read by `collect()` in agent_improve.py; verdicts in `infrastructure/state/delegated/`; `whittle/agent_improve_audit_kindless_records_all_two/NOTES.md` has the code map.
- Second model: `python3 src/RimMandrake/Utils/gpt_consult.py "q" -f <file>...` (the `chatgpt-consult` skill).
What you may not touch: any running game or the bridge (offline lane), the live agent_improve state under `D:\ClaudeWork\rimmandrake\agent_improve\`, existing change records' history (records are append-only evidence), anything outside this item; the Relentless freeze bars any new rule, layer or judging machinery; and the Whittle machinery
itself: `whittle/agent_improve_audit_kindless_records_all_two/STATEMENT.md`, `whittle/agent_improve_audit_kindless_records_all_two/NOTES.md`, `whittle/agent_improve_audit_kindless_records_all_two/STOP`, `whittle/agent_improve_audit_kindless_records_all_two/JUDGE_PROMPT.md`, `whittle/agent_improve_audit_kindless_records_all_two/JUDGE.md`, the
Stop hook and its settings. Those belong to the owner and the judge. Work lands on main through ./publish: commit what works, keep experiments in scratch.

How to work:
- Fix as many things as you can. Search before you build: don't assume something isn't there, and don't trust old
  notes without checking.
- Don't write placeholders or stand-ins. Build the real thing. Don't file tickets or leave a problem as a note when
  you can fix it now.
- Keep the wheel turning fast: the smallest setup that shows the problem. Send heavy reading to subagents so your
  context stays clear.
- If something truly needs the owner, write it in `whittle/agent_improve_audit_kindless_records_all_two/BLOCKED.md` and stop; that is always allowed.

Before you claim done:
1. Ask a different model to broaden your testing: give it the statement, what you tested and how, and ask what a real
   user would try that you haven't (someone new, someone experienced, someone trying to break it, a messy real case).
   Try the one or two most revealing and look. Write the question, the answer and what you found in
   `whittle/agent_improve_audit_kindless_records_all_two/BROADEN.md`.
2. Write `whittle/agent_improve_audit_kindless_records_all_two/DONE.md` from its template: every statement line, your honest verdict, and fresh evidence files.
3. Spawn a fresh subagent judge (an ordinary subagent, not a fork, which would inherit this conversation) and give it
   `whittle/agent_improve_audit_kindless_records_all_two/JUDGE_PROMPT.md` as its whole brief, plus the run command if it needs one. It writes `whittle/agent_improve_audit_kindless_records_all_two/JUDGE.md`; you
   don't. If it would not show the work, keep going on what it found.

You're done when, in real use, you would be happy to show this to the owner. A hook will not let you stop before
then (it is a checklist: it refuses an incomplete or stale claim, not a weak one). When it refuses, read its reason and
do what it says. Don't write thin evidence to satisfy it; the judge and the owner read the files. The owner looks after
the judge.
