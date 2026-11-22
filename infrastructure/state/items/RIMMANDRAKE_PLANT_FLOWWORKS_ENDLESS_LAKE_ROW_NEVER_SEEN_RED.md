# RIMMANDRAKE_PLANT_FLOWWORKS_ENDLESS_LAKE_ROW_NEVER_SEEN_RED

## spec
FlowWorks sc_source_pays, row SRC_lake_reads_endless. Visit 4 (2026-11-21) repaired the scene so the lake row runs on the river
site (9da1303401): on the real build it reads PASS (stock of limitless body 1 = 11790 before and after a 10-square moat took
200000 dL). The repair was NOT seen red: a mutant DLL whose RM_LiquidStock.TryDebit debits limitless bodies
(D:\ClaudeWork\rimmandrake\scratch\v4_mutant_limitless\LIMITLESS_BODY_DEBITED.patch) also read PASS with the same stock.
Either the kernel's draw from an edge body never goes through TryDebit (the plant is off the path), or the row's criterion
(body stock from flowworks_pulse includeBodies) cannot see a lake that drops. Find which; if the stock is blind, judge the
lake's own water (the probe cells' dL before and after the draw) instead.
## verify
Live, fw_gss_sitting tier, game a or b: a planted fault on the real edge-refill path (the lake loses what the moat takes)
reads SRC_lake_reads_endless FAIL; the real build reads PASS; both readings beside the row.
## criteria
Acceptance test: python.exe src\RimMandrake\FlowWorks\northstar\concept_scenes.py --scene scene_source_pays --out <json>
on the mutant: exit 1 with SRC_lake_reads_endless FAIL (today: exit 0, PASS = red for this item); on the real build: exit 0.
Offline: python3 src/RimMandrake/FlowWorks/northstar/selftest_source_pays_scene.py stays ok (0 failed).
## refs
file: src/RimMandrake/FlowWorks/northstar/concept_scenes.py
file: src/RimMandrake/FlowWorks/Source/RM_LiquidStock.cs
file: design/concepts/FlowWorks/version/in_game/visit_4/evidence/plant/sc_source_pays_MUTANT_limitless_debited.json

## outcome (visit 4, 2026-11-21 ~5:00 PM PST)
Answered in the same sitting: the first plant (TryDebit) was off the path; the exact kernel reads a body through
RM_LiquidStock.LevelBodyOf. The plant LIMITLESS_BODY_RUNS_DOWN (LevelBodyOf returns a limitless body's id) reads
SRC_lake_reads_endless FAIL (stock 11790 -> 11784.415), the real build PASS (11790 -> 11790). The row's stock criterion is not blind.
