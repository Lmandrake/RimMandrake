The mineral matrix rebuild (item MINERAL_SHEET_REBUILD_FROM_PAINTED_MAP) is a generator anyone can rerun from the repo: one command turns committed inputs into the matrix CSVs for the 27 painted biomes plus the two marked extras, with real labels and no (Jawa) tag, and the sheet built from them carries a passing prereview record.

The owner's words and what we owe the user are in `whittle/mineral_sheet_rebuild_from_painted_map/STATEMENT.md`. That is the only thing you may not change.
The owner's later rulings are in `whittle/mineral_sheet_rebuild_from_painted_map/NOTES.md`, newest first. Reread both before you claim done; when they and this
conversation disagree, the files win.

BE CREATIVE. Figure out the problems and solve them. Don't just work to a checklist. Use it the way a user would,
look at what they would actually see, work out what's really wrong, and fix it. Everything but that statement is
yours: code, assets, tests, harnesses. If a test is wrong or in your way, fix it or drop it.

How to see what the user sees: run the restored generator in a fresh clone (`scratch_clone.py`, or a `git clone` under the round dir) and read its CSVs and stats.json; diff them against the 2026-10-30 build; open the sheet's page with the old playwright harness (`prereview/run.py`) and run `python3 src/RimMandrake/Utils/art/prereview.py check` on its record. Save what you judge by in `whittle/mineral_sheet_rebuild_from_painted_map/evidence/`. Show ordinary
use, not a staged best case.

What you have, by name (agents tend to overlook what isn't named, so this list is meant to be complete):
- The 2026-10-30 build on Archmagi, `ssh mandrake@archmagi-wsl`, in `/mnt/d/ClaudeWork/rimmandrake/mineral_matrix_2026-10-30/` (gen_matrix.py, gen.log, PROGRESS.md, page/, prereview/, build_xlsx.py) and its round-two inputs in `/mnt/d/ClaudeWork/rimmandrake/mineral_matrix_2026-10-28/`. The fast check: rerun gen and `diff` its CSVs against those.
- The authority for the row set: `design/RimMandrake/biome_name_provenance_audit_2026-10-28.md`. The BiomeDefs under `src/`. Ledger history: `python3 src/RimMandrake/rimflow/cli.py show MINERAL_SHEET_REBUILD_FROM_PAINTED_MAP`. Lessons in `infrastructure/state/lessons/`. Selftests: `python3 src/RimMandrake/Utils/run_selftests.py --only <test>`.
- A second model: `python3 src/RimMandrake/Utils/gpt_consult.py "q" -f <file>` (the `chatgpt-consult` skill).
What you may not touch: any game on any machine (offline lane: no deploy, no bridge, no start); any mod file or def (the D10 hold: nothing reaches the game before his review); the owner's labelled workbook `mineral_matrix_2026-10-30.xlsx` and the published artifact; Archmagi's ClaudeWork files (read them, never write them); other loops' items; and the Whittle machinery
itself: `whittle/mineral_sheet_rebuild_from_painted_map/STATEMENT.md`, `whittle/mineral_sheet_rebuild_from_painted_map/NOTES.md`, `whittle/mineral_sheet_rebuild_from_painted_map/STOP`, `whittle/mineral_sheet_rebuild_from_painted_map/JUDGE_PROMPT.md`, `whittle/mineral_sheet_rebuild_from_painted_map/JUDGE.md`, the
Stop hook and its settings. Those belong to the owner and the judge. Work lands on main
through ./publish: commit what works, keep experiments in scratch.

How to work:
- Fix as many things as you can. Search before you build: don't assume something isn't there, and don't trust old
  notes without checking.
- Don't write placeholders or stand-ins. Build the real thing. Don't file tickets or leave a problem as a note when
  you can fix it now.
- Keep the wheel turning fast: the smallest setup that shows the problem. Send heavy reading to subagents so your
  context stays clear.
- If something truly needs the owner, write it in `whittle/mineral_sheet_rebuild_from_painted_map/BLOCKED.md` and stop; that is always allowed.

Before you claim done:
1. Ask a different model to broaden your testing: give it the statement, what you tested and how, and ask what a real
   user would try that you haven't (someone new, someone experienced, someone trying to break it, a messy real case).
   Try the one or two most revealing and look. Write the question, the answer and what you found in
   `whittle/mineral_sheet_rebuild_from_painted_map/BROADEN.md`.
2. Write `whittle/mineral_sheet_rebuild_from_painted_map/DONE.md` from its template: every statement line, your honest verdict, and fresh evidence files.
3. Spawn a fresh subagent judge (an ordinary subagent, not a fork, which would inherit this conversation) and give it
   `whittle/mineral_sheet_rebuild_from_painted_map/JUDGE_PROMPT.md` as its whole brief, plus the run command if it needs one. It writes `whittle/mineral_sheet_rebuild_from_painted_map/JUDGE.md`; you
   don't. If it would not show the work, keep going on what it found.

You're done when, in real use, you would be happy to show this to the owner. A hook will not let you stop before
then (it is a checklist: it refuses an incomplete or stale claim, not a weak one). When it refuses, read its reason and
do what it says. Don't write thin evidence to satisfy it; the judge and the owner read the files. The owner looks after
the judge.

## This loop's round (appended to the Whittle prompt by loop.sh)

Before anything else read `infrastructure/whittle_claude/common.md` (the project rules and the blockages) and
`infrastructure/whittle_claude/lane_offline.md` (what your lane may touch). The item is `MINERAL_SHEET_REBUILD_FROM_PAINTED_MAP`; your Whittle
directory is `whittle/mineral_sheet_rebuild_from_painted_map`; its `MODE` file says `whittle` or `pilot`.

- Mode `whittle`: build until every STATEMENT bullet is true and shown by evidence, then let the judge pass it.
- Mode `pilot`: this is a Test Pilot sitting, not another code-and-retest round. Run `rimflow pilot MINERAL_SHEET_REBUILD_FROM_PAINTED_MAP` and follow
  the brief it prints, with the `test-pilot-sitting` skill: experiments that discriminate between hypotheses, each
  recorded in NOTES.md, then the fix or the filed finding.
- Live evidence comes only from your lane's game, held through the bridge lock as your lane file says, and released
  before you stop. Record proof runs on the item the way its proof script does (modcheck, or `rimflow live`: read `--help`) so the ledger
  carries them.
- Commit and `./publish` your work as it lands (explicit paths). Do NOT close the item here: the wrap-up phase closes,
  parks or drops it after checking your DONE.md and the judge.
- If you cannot go on without the owner, write the question as common.md says, put one line in `whittle/mineral_sheet_rebuild_from_painted_map/BLOCKED.md`
  naming it, and stop.
