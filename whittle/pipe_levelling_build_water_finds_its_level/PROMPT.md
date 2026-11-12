`PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL` (Connected bodies of water level out slowly through pipes by gravity (extending tanks' slow gravity emptying), owner: 'Let's see if we can do this'. Feasibility first. Spec: design/RimMandrake/flowwork) is built so every bullet in its STATEMENT.md is true in ordinary use, shown by fresh evidence.

The owner's words and what we owe the user are in `whittle/pipe_levelling_build_water_finds_its_level/STATEMENT.md`. That is the only thing you may not change.
The owner's later rulings are in `whittle/pipe_levelling_build_water_finds_its_level/NOTES.md`, newest first. Reread both before you claim done; when they and this
conversation disagree, the files win.

BE CREATIVE. Figure out the problems and solve them. Don't just work to a checklist. Use it the way a user would,
look at what they would actually see, work out what's really wrong, and fix it. Everything but that statement is
yours: code, assets, tests, harnesses. If a test is wrong or in your way, fix it or drop it.

How to see what the user sees: its proof script or a bridge session on your lane's game only (the lane file says which, and how to hold the bridge), in-game screenshots through the bridge that you then Read (lane file: how, and modal dialogs); the item's verify section says: - L0: feasibility note — which solver call gives a body's surface and accepts a bounded transfer. - L1: selftests — 1-cell vs 100-cell basin at different floors converge to one surface, volume conserved; ten parallel links; same-body loop moves nothing; crest siphon flows; exposed intake stops; wate. Save what you judge by in `whittle/pipe_levelling_build_water_finds_its_level/evidence/`. Show ordinary
use, not a staged best case.

What you have, by name (agents tend to overlook what isn't named, so this list is meant to be complete):
- the item's verify section in `infrastructure/state/items/PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL.md`, and `python3 src/RimMandrake/Utils/run_selftests.py --only <tests>` as the fast check
- `rimflow show PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL` (runs, notes, evidence paths), and the run notes in NOTES.md
- the `chatgpt-consult` skill
What you may not touch: other lanes' games, the owner's mod list on his campaign, anything outside this item; and the Whittle machinery
itself: `whittle/pipe_levelling_build_water_finds_its_level/STATEMENT.md`, `whittle/pipe_levelling_build_water_finds_its_level/NOTES.md`, `whittle/pipe_levelling_build_water_finds_its_level/STOP`, `whittle/pipe_levelling_build_water_finds_its_level/JUDGE_PROMPT.md`, `whittle/pipe_levelling_build_water_finds_its_level/JUDGE.md`, the
Stop hook and its settings. Those belong to the owner and the judge. Work lands on main through ./publish: commit what works, keep experiments in scratch.

How to work:
- Fix as many things as you can. Search before you build: don't assume something isn't there, and don't trust old
  notes without checking.
- Don't write placeholders or stand-ins. Build the real thing. Don't file tickets or leave a problem as a note when
  you can fix it now.
- Keep the wheel turning fast: the smallest setup that shows the problem. Send heavy reading to subagents so your
  context stays clear.
- If something truly needs the owner, write it in `whittle/pipe_levelling_build_water_finds_its_level/BLOCKED.md` and stop; that is always allowed.

Before you claim done:
1. Ask a different model to broaden your testing: give it the statement, what you tested and how, and ask what a real
   user would try that you haven't (someone new, someone experienced, someone trying to break it, a messy real case).
   Try the one or two most revealing and look. Write the question, the answer and what you found in
   `whittle/pipe_levelling_build_water_finds_its_level/BROADEN.md`.
2. Write `whittle/pipe_levelling_build_water_finds_its_level/DONE.md` from its template: every statement line, your honest verdict, and fresh evidence files.
3. Spawn a fresh subagent judge (an ordinary subagent, not a fork, which would inherit this conversation) and give it
   `whittle/pipe_levelling_build_water_finds_its_level/JUDGE_PROMPT.md` as its whole brief, plus the run command if it needs one. It writes `whittle/pipe_levelling_build_water_finds_its_level/JUDGE.md`; you
   don't. If it would not show the work, keep going on what it found.

You're done when, in real use, you would be happy to show this to the owner. A hook will not let you stop before
then (it is a checklist: it refuses an incomplete or stale claim, not a weak one). When it refuses, read its reason and
do what it says. Don't write thin evidence to satisfy it; the judge and the owner read the files. The owner looks after
the judge.
