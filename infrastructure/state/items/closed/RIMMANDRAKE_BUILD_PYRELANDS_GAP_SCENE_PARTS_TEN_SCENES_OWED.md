# RIMMANDRAKE_BUILD_PYRELANDS_GAP_SCENE_PARTS_TEN_SCENES_OWED

## spec

Pyrelands 0.1.0 locked change (owner card 2026-11-15, "Fix all 12 in 0.1.0", OWNER:1794748469904049550): the coverage
judge's Problem gaps (design/concepts/Pyrelands/version/evidence/coverage_judge_refusal_2026-11-14.json) were fixed in
design/concepts/Pyrelands/scenes.json by RIMMANDRAKE_APPLY_PYRELANDS_JUDGE_EDITS_ALL_TWENTY_ATTAINABLE. Ten scenes (twelve since the round-5 look, rm-coverage-judge-1794749968; its gaps g1-g5 in
design/concepts/Pyrelands/version/evidence/coverage_judge_refusal_2026-11-15.json) now
carry `owed_parts_item` = this item: their start, action, expect or control asks for reads that
src/RimMandrake/Pyrelands/validation.py does not make yet. Build them (script only; no gameplay change), offline and
live, per the project rule that the test is built with the item.

| scene | entry point | owed parts | gap |
|---|---|---|---|
| sc_foreign_arrivals | validation.py::foreign_arrivals (NEW chain) | whole scene: herd migration, manhunter pack, each disallowed fixed-species incident; vanilla arid control map | g1 |
| sc_populations | plant_census | fire-hawk >= 2 and ashwallow >= 8 counts; a donor plant in the wild-plant pass for a day, wildPlantAllowlistEnabled on vs off; a same-seed map with PyrelandsMechanicsGate off (other wild kinds' counts equal), hawks = max(2, its count) | g1, g6; round-5 g5 |
| sc_walk | walk_season | roster toggle (PyrelandsMechanicsGate) off a day then on: front, ProbeAsh, bed fires; roofed room on grass withers; fire-cast thirst and one-at-a-time water visits; no colonist burned in fire or starved at fire duty | g1, g7 |
| sc_ash_ground | ground_deep_ash | save at noon (ashground_noon), clear-weather run over the same clock hours, light and ProbeAsh compared hour by hour; shore ring read | g1, g10 |
| sc_three_skies | cinderfall | each sky from a reload of skies_noon, capture hour asserted 10h-14h; second ash patch under clear sky, black-rain depth loss >= 2x clear | g5, g11 |
| sc_grass_regreens | embergrass_regrow | sown dry (burned > 7 days ago) and watered ember-grass patches plus a vanilla grass on dry ash; daily growth, burst count | g2 |
| sc_furnace_bed | furnace_sleep | beast A health before and after its bed fire; a muffalo in a like bed fire takes burns; per poll, a Fire on A's own cell (and the muffalo's) while it lies there | g3; round-5 g4 |
| sc_flamefang_venom | flamefang_venom | tended vs untended venom severity over six hours, tended below untended at every read; immunity read until the hediff goes | g4; round-5 g1 |
| sc_fire_sense | validation.py::fire_sense (NEW chain) | whole scene: P beside a test-lit Fire takes RM_PyreStepAwayFromFire and ends >= 3 cells clear; urgently hungry H eats (Ingest) before BeatFire; PyrelandsMechanicsGate off control | round-5 g2 |
| sc_ash_watered | ash_fertility_watered | cell temperature above the crop's maxOptimalGrowthTemperature asserted; Plant.GrowthRateFactor_Temperature on both strips daily | round-5 g3 |
| sc_firehawk | firehawk | a second hawk > 54 cells from a visible burn takes RM_FireHawkSeekBurn and closes; fireHawkSpreadEnabled off control | g1 |
| sc_ruins | ruins | RM_FE_Charred paint on ruin walls, absent on the vanilla control | g1 |

When a scene's parts are built and run, set its `live_run` from UNRUN to the run's evidence and drop `owed_parts_item`
(a designer stage-3 edit; under the lock it needs a repin citing the card above).

Acceptance test (offline part; watched FAIL on base 2df259b129, 2026-11-15, AssertionError): every owed chain is
registered in validation.py:

    python3 -c "import re;t=open('src/RimMandrake/Pyrelands/validation.py').read();assert re.search(r'@suite.chain\(\"foreign_arrivals\"\)',t)"

Expected: exit 0 (1 assertion). The live part is each scene's `live_command` in scenes.json
(`modcheck run Pyrelands --chains <chain>`), UNRUN as of filing: the game was held by the Pyrelands in-game visit.

## refs
file: src/RimMandrake/Pyrelands/validation.py
new: src/RimMandrake/Pyrelands/selftest_pyrelands_ten_scenes_parts.py

## verify
- Offline: `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_pyrelands_ten_scenes_parts` passes (watched FAIL on base first), and the acceptance one-liner above exits 0.
- Live (not part of the offline build): each scene's `live_command` in design/concepts/Pyrelands/scenes.json, UNRUN until a bridge seat runs it.

## criteria
- A1 L0: every entry point in the table is a registered `@suite.chain` in validation.py (foreign_arrivals and fire_sense new)
- A2 L0: each chain body makes the owed reads named in its table row (static selftest selftest_pyrelands_ten_scenes_parts); a read with no bridge tool is recorded UNMEASURED with a reason, not invented
- A3 L2: each scene's `live_command` run on a bridge seat (owed; live_run stays UNRUN here)
