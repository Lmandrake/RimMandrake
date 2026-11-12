`PIT_TEMPERATURE_SOFTENING_1` (Pit temperature couples hard to ambient and wears down resistance; Exposed Prisoner thought) is built so every bullet in its STATEMENT.md is true in ordinary use, shown by fresh evidence.

The owner's words and what we owe the user are in `whittle/pit_temperature_softening_1/STATEMENT.md`. That is the only thing you may not change.
The owner's later rulings are in `whittle/pit_temperature_softening_1/NOTES.md`, newest first. Reread both before you claim done; when they and this
conversation disagree, the files win.

BE CREATIVE. Figure out the problems and solve them. Don't just work to a checklist. Use it the way a user would,
look at what they would actually see, work out what's really wrong, and fix it. Everything but that statement is
yours: code, assets, tests, harnesses. If a test is wrong or in your way, fix it or drop it.

How to see what the user sees: its proof script or a bridge session on your lane's game only (the lane file says which, and how to hold the bridge), screenshots through the bridge; the item's verify section says: Bridge: desert noon, unroofed pit vs roofed twin — the pit's temperature moves faster; an occupant's resistance falls faster in the pit than in a normal prison cell; a compassionate colonist gets the thought, a psychopath does not.. Save what you judge by in `whittle/pit_temperature_softening_1/evidence/`. Show ordinary
use, not a staged best case.

What you have, by name (agents tend to overlook what isn't named, so this list is meant to be complete):
- the item's verify section in `infrastructure/state/items/PIT_TEMPERATURE_SOFTENING_1.md`, and `python3 src/RimMandrake/Utils/run_selftests.py --only <tests>` as the fast check
- `rimflow show PIT_TEMPERATURE_SOFTENING_1` (runs, notes, evidence paths), and the run notes in NOTES.md
- the `chatgpt-consult` skill
What you may not touch: other lanes' games, the owner's mod list on his campaign, anything outside this item; and the Whittle machinery
itself: `whittle/pit_temperature_softening_1/STATEMENT.md`, `whittle/pit_temperature_softening_1/NOTES.md`, `whittle/pit_temperature_softening_1/STOP`, `whittle/pit_temperature_softening_1/JUDGE_PROMPT.md`, `whittle/pit_temperature_softening_1/JUDGE.md`, the
Stop hook and its settings. Those belong to the owner and the judge. Work lands on main through ./publish: commit what works, keep experiments in scratch.

How to work:
- Fix as many things as you can. Search before you build: don't assume something isn't there, and don't trust old
  notes without checking.
- Don't write placeholders or stand-ins. Build the real thing. Don't file tickets or leave a problem as a note when
  you can fix it now.
- Keep the wheel turning fast: the smallest setup that shows the problem. Send heavy reading to subagents so your
  context stays clear.
- If something truly needs the owner, write it in `whittle/pit_temperature_softening_1/BLOCKED.md` and stop; that is always allowed.

Before you claim done:
1. Ask a different model to broaden your testing: give it the statement, what you tested and how, and ask what a real
   user would try that you haven't (someone new, someone experienced, someone trying to break it, a messy real case).
   Try the one or two most revealing and look. Write the question, the answer and what you found in
   `whittle/pit_temperature_softening_1/BROADEN.md`.
2. Write `whittle/pit_temperature_softening_1/DONE.md` from its template: every statement line, your honest verdict, and fresh evidence files.
3. Spawn a fresh subagent judge (an ordinary subagent, not a fork, which would inherit this conversation) and give it
   `whittle/pit_temperature_softening_1/JUDGE_PROMPT.md` as its whole brief, plus the run command if it needs one. It writes `whittle/pit_temperature_softening_1/JUDGE.md`; you
   don't. If it would not show the work, keep going on what it found.

You're done when, in real use, you would be happy to show this to the owner. A hook will not let you stop before
then (it is a checklist: it refuses an incomplete or stale claim, not a weak one). When it refuses, read its reason and
do what it says. Don't write thin evidence to satisfy it; the judge and the owner read the files. The owner looks after
the judge.

## This loop's round (appended to the Whittle prompt by loop.sh)

Before anything else read `infrastructure/whittle_claude/common.md` (the project rules and the blockages) and
`infrastructure/whittle_claude/lane_archmagi.md` (what your lane may touch). The item is `PIT_TEMPERATURE_SOFTENING_1`; your Whittle
directory is `whittle/pit_temperature_softening_1`; its `MODE` file says `whittle` or `pilot`.

- Mode `whittle`: build until every STATEMENT bullet is true and shown by evidence, then let the judge pass it.
- Mode `pilot`: this is a Test Pilot sitting, not another code-and-retest round. Run `rimflow pilot PIT_TEMPERATURE_SOFTENING_1` and follow
  the brief it prints, with the `test-pilot-sitting` skill: experiments that discriminate between hypotheses, each
  recorded in NOTES.md, then the fix or the filed finding.
- Live evidence comes only from your lane's game, held through the bridge lock as your lane file says, and released
  before you stop. Record proof runs on the item the way its proof script does (modcheck, or `rimflow live`: read `--help`) so the ledger
  carries them.
- Commit and `./publish` your work as it lands (explicit paths). Do NOT close the item here: the wrap-up phase closes,
  parks or drops it after checking your DONE.md and the judge.
- If you cannot go on without the owner, write the question as common.md says, put one line in `whittle/pit_temperature_softening_1/BLOCKED.md`
  naming it, and stop.
