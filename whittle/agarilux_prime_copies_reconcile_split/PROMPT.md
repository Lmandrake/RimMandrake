The work is to make RM_AgariluxPrime (the grath elder, a Rot giant) ship ONE texture: decide whether TheRot or UtinniPatches owns it from what the game really loads, delete the other copy, fix every inbound reference, and re-judge only if the survivor is the copy art-eval marked REGEN. Small, offline, done in hours.

The owner's words and what we owe the user are in `whittle/agarilux_prime_copies_reconcile_split/STATEMENT.md`. That is the only thing you may not change.
The owner's later rulings are in `whittle/agarilux_prime_copies_reconcile_split/NOTES.md`, newest first. Reread both before you claim done; when they and this
conversation disagree, the files win.

BE CREATIVE. Figure out the problems and solve them. Don't just work to a checklist. Use it the way a user would,
look at what they would actually see, work out what's really wrong, and fix it. Everything but that statement is
yours: code, assets, tests, harnesses. If a test is wrong or in your way, fix it or drop it.

How to see what the user sees: the player sees whichever PNG the def's final texPath resolves to after patches and load order. Show it with a resolved-def read (base def `src/RimMandrake/TheRot/Defs/ThingDefs_Plants/RM_TheRot_DonorPorts.xml` + the repoint in `src/RimMandrake/TheRot/Patches/RotSpecies_NamesAndSizes.xml`; the offline def dump via `python3 src/RimMandrake/Utils/refresh.py` / `measure` if needed) and a repo-wide search for the losing path after the change. Save what you judge by in `whittle/agarilux_prime_copies_reconcile_split/evidence/`. Show ordinary
use, not a staged best case.

What you have, by name (agents tend to overlook what isn't named, so this list is meant to be complete):
- Fast checks: `grep -rn` for the texture stems across `src/`, `infrastructure/state/art*`, `design/`; `python3 skills/rimworld-modding/scripts/validate_patch.py <patch> --defs ...`; `python3 src/RimMandrake/Utils/run_selftests.py --only <tests for touched files>`.
- Records: `infrastructure/state/art_eval/runs/gptredo_03/decisions.jsonl` (both subjects' verdicts), `D:\ClaudeWork\rimmandrake\art_eval\gptredo\` (the images), the art ledger (`art install` only; `artpipe_state.py find`), `whittle/agarilux_prime_copies_reconcile_split/NOTES.md`.
- A second model: the `chatgpt-consult` skill (`python3 src/RimMandrake/Utils/gpt_consult.py "q" -f <file>`).
What you may not touch: any running game on any machine (no deploy, no bridge, no ./game), the owner's mod list, other items' files and other Rot textures not in this split; and the Whittle machinery
itself: `whittle/agarilux_prime_copies_reconcile_split/STATEMENT.md`, `whittle/agarilux_prime_copies_reconcile_split/NOTES.md`, `whittle/agarilux_prime_copies_reconcile_split/STOP`, `whittle/agarilux_prime_copies_reconcile_split/JUDGE_PROMPT.md`, `whittle/agarilux_prime_copies_reconcile_split/JUDGE.md`, the
Stop hook and its settings. Those belong to the owner and the judge. Work lands on main
branch; a bad result is thrown away, so try things.

How to work:
- Fix as many things as you can. Search before you build: don't assume something isn't there, and don't trust old
  notes without checking.
- Don't write placeholders or stand-ins. Build the real thing. Don't file tickets or leave a problem as a note when
  you can fix it now.
- Keep the wheel turning fast: the smallest setup that shows the problem. Send heavy reading to subagents so your
  context stays clear.
- If something truly needs the owner, write it in `whittle/agarilux_prime_copies_reconcile_split/BLOCKED.md` and stop; that is always allowed.

Before you claim done:
1. Ask a different model to broaden your testing: give it the statement, what you tested and how, and ask what a real
   user would try that you haven't (someone new, someone experienced, someone trying to break it, a messy real case).
   Try the one or two most revealing and look. Write the question, the answer and what you found in
   `whittle/agarilux_prime_copies_reconcile_split/BROADEN.md`.
2. Write `whittle/agarilux_prime_copies_reconcile_split/DONE.md` from its template: every statement line, your honest verdict, and fresh evidence files.
3. Spawn a fresh subagent judge (an ordinary subagent, not a fork, which would inherit this conversation) and give it
   `whittle/agarilux_prime_copies_reconcile_split/JUDGE_PROMPT.md` as its whole brief, plus the run command if it needs one. It writes `whittle/agarilux_prime_copies_reconcile_split/JUDGE.md`; you
   don't. If it would not show the work, keep going on what it found.

You're done when, in real use, you would be happy to show this to the owner. A hook will not let you stop before
then (it is a checklist: it refuses an incomplete or stale claim, not a weak one). When it refuses, read its reason and
do what it says. Don't write thin evidence to satisfy it; the judge and the owner read the files. The owner looks after
the judge.
