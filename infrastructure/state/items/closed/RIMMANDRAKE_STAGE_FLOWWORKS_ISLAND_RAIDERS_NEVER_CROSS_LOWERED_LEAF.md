## spec
found-by: FlowWorks in-game visit 3, game a, flowworks tier, calm site, 2026-11-21 5:51 AM PST.
sc_islands row ISL_raiders_escape FAIL twice on the same build (evidence/sc_islands_20261121T055111.json: both winches lost, both
leaves lowered; evidence/exp/sc_islands_rerun1.json: the east leaf lowered): the six sappers stayed on the steel span (x 65-77) for
all 50 polls (6,000 ticks). On game b at 03:55 PST the same scene passed in 2 polls (visit_2/evidence/exp/sc_islands_20261121T0355_gameb_hold.json).
RULED OUT, MOD "a lowered leaf carries no walker": probe_islands_leaf.py (evidence/exp/islands_leaf_probe.json) staged the scene,
destroyed both winches, and a colonist on the span walked across leaf A to the west bank (canReach True, arrived).
Class SITE, presumed [guess ~60%]: the raiders have no motive in the staging to cross a lowered leaf (their lord does not re-path);
whether they cross is AI chance, so the row cannot decide the bar. Unrepaired: no planted state shows a repair both ways in the sitting.

## verify
- sc_islands live: ISL_raiders_escape decides the bar on every run (PASS when a leaf falls), and a control that holds both winches stays trapped.

Acceptance test: `python.exe src\RimMandrake\FlowWorks\northstar\concept_scenes.py --scene scene_islands --out <json>` exits 0 in two
runs in a row on game a's calm site; red now (2 of 2 runs FAIL at visit 3).

## refs
file: src/RimMandrake/FlowWorks/northstar/concept_scenes.py
