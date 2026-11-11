# TITAN_WALL_CRUSH_DIAGNOSE_WOOD_WALL_SHRUGS

## spec
The 2026-11-03 RoofWallProbe observation (T2 thin roof removed, wood wall HP 195->195) is expected with the default walls-and-slots rule enabled. TitanicWakeProcessor.ProcessCrushable deliberately leaves walls and doors to the separate clearing system in that mode. RoofWallProbe assigns Thing.Position directly; it neither requests a path nor starts a clearing job. Its old Python checker incorrectly required legacy wall damage under the default mode.

The repaired R4 diagnostic measures both modes with the same T2 and forced-out control at one pinned cell. Default: T2 removes the thin roof and preserves the wall. Legacy wake with wallsSlotsEnabled=False: T2 removes the roof and damages the wall. Both controls preserve roof and wall. Every mode field is read before and after each call; settings restoration is part of the verdict. The historical row ID remains for compatibility, with explicit L1 Position-setter wording.

## criteria
A1: row t2_holes_thin_roofs_and_crushes_walls of src/RimMandrake/HugeThings/northstar/titan_test_races_live.py reads PASS live, or the probe is shown wrong and fixed.

## proof — 2026-11-11
The incorrect-checker alternative is proved at L1. SteveDesktop all-DLC 14-mod disposable saved-scene run: default T2 wall 195->195, legacy T2 wall 195->135, roof removed in both; both forced-out controls retain RoofConstructed and wall 195->195. All calls use cell 103,103, settings remain stable, and no simulation ticks elapse. Planted roof/wall fingerprint controls pass. Scene-begin rectangle and touched settings restore exactly; game DOWN and own host lease FREE.

Raw accepted proof: whittle/ht-wall-probe/evidence/live_run_2/live.json. The first failed attempt is retained: expected legacy rubble tripped the new residue gate; the functional runner now records and removes only measured T2 rubble and rejects other residue. Regression: 195/195 detailed checks, focused run_selftests GREEN. Fresh independent Codex judgment: whittle/ht-wall-probe/JUDGE.md. Actual Whittle validator rc0.

Scope: loaded-method diagnostic integration only. Natural wall clearing, walked crossings, the R5 route test and flight are not accepted by this work. No C# or gameplay behavior changed.
