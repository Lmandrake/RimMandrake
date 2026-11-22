# RIMMANDRAKE_FIX_FLOWWORKS_REVIEW_MAP_SPRINKLER_LOOKS_NEVER_CHOSEN

## spec
The FlowWorks review map (owner_review_stage.py, the walk savegame) has two stations that show something other than their
label, seen on visits 3 and 4 (2026-11-21, his full list, calm site):
- sprinklers 24-27 ("Futuristic / Industrial / Modern / Scrapper"): objects_sheet.choose_look returns None for all four pipe
  runs ("pipe look for net N: asked <Look>, game reads None"), so the four stations do not show four looks; and the row
  capture row_sprinklers is framed on one corner (a tank and a reel), not on the four stations.
- bars_trench 40-41: ProofTrenchCover refuses "shooter has no ranged verb": the shooter colonist is spawned unarmed.
Both are scene faults of the review map (no bar reads them: sc_trench_cover and the sprinkler checks decide those bars).
## verify
python3 src/RimMandrake/Utils/save_guard.py run --current-slot none -- python.exe src/RimMandrake/FlowWorks/northstar/owner_review_stage.py --only sprinklers,bars_trench --no-save
on a calm site (flowworks tier): today the notes hold 4 "pipe look ... reads None" lines and 2 "no ranged verb" lines (red).
## criteria
Acceptance test: the command above prints no "reads None" and no "no ranged verb" note, ProofTrenchCover answers for both
stations, and row_sprinklers.png shows all four stations (expected: 0 such notes; 4 stations in frame).
## refs
file: src/RimMandrake/FlowWorks/northstar/owner_review_stage.py
file: src/RimMandrake/FlowWorks/northstar/objects_sheet.py
