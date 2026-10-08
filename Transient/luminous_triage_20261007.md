# LuminousPigment live-L2 triage, 2026-10-07

Only file edited: `src/RimMandrake/LuminousPigment/validation.py` plus the mock in `selftest_luminouspigment.py`. No C# changed, no DLL rebuilt, nothing committed. Offline selftest: ALL OK (the mock had encoded the wrong -2.5 unit and now carries an `orders_patch` mutant). `lint_calls.py` is clean.
The fixes below are inferred from the raw sweep JSON and the source, not yet run live.

## patches_applied: HARNESS
- `get_defs` serialises `List<Type>` as the string `RuntimeType`, so `Orders.specialDesignatorClasses` can never name a class.
- `DeepfireOrdersPatch.xml` itself is fine.
- Fix: read the resolved Orders toolbar via `list_architect_categories` then `list_architect_designators`. The check looks for the labels "Apply deepfire" and "Remove deepfire" (`Designator_Deepfire.cs:20`, `:103`). A vanilla "Hunt" row is a sanity probe, and its absence is UNMEASURED.
- Re-check: `defs_load/patches_applied` PASS.

## mat_alive_control: FIXTURE (cause not proven)
- Evidence: after 600 ticks neither fresh nor dead stack existed in the 13x13 rect. The pad lies in the quicktest rock (`destroy_batch` removed 169 Sandstone).
- The comp (`CompMatVitality.cs`) cannot destroy a stack silently with chill -100 and life 1 day. `BecomeDead` always places a dead stack.
- Most likely a colonist hauled the loose stack out of the rect. Not proven.
- Fix: stage the stack in a sealed doorless `_room`, in both the control arm and the chill arm. If both are still empty, a new `_gone_or_moved` helper searches the whole map. A stack found elsewhere is UNMEASURED ("hauled"). A stack found nowhere is a FAIL, which points at the MOD.
- Re-check: `mat_vitality` three components. If the helper reports "gone from the whole map", open a MOD DEFECT against `CompMatVitality.BecomeDead`.

## unlocked_after_sighting: FIXTURE (pad terrain; also LIST ARTIFACT-adjacent)
- `set_plants` rejects RM_Crowncarpet ("terrain or conditions cannot support") because the pad is rock with no Light affordance.
- The plant ignores fertility (`RM_Crowncarpet.xml` completelyIgnoreFertility) and its wild-bed tag is irrelevant to a hand-placed plant.
- Fix: `set_terrain Soil` on the 1x1 cell first. A refused plant is now UNMEASURED; before, the unmeasured branch was dead code behind `_ok`.
- Re-check: `research_gate/unlocked_after_sighting`. Needs 2100 ticks and an unfogged cell within 20 of the pawn.
- If set_plants still rejects on Soil, the reason is temperature or light, not terrain. Read `rejectionReasons`.

## press_is_a_powered_bench: HARNESS (unit error)
- `power_net` reports watt-days per tick (`WattsToWattDaysPerTick` = 1/60000). 150 W reads -0.0025, which is exactly what the sweep measured.
- The check wanted -2.5 (its own wrong arithmetic). The press IS powered, and the mod applies `pressPower` via `LuminousPigmentMod.cs:480`.
- Fix: expect `-PRESS_WATTS/60000` with tolerance 0.0002, which still separates 100 W and 200 W.
- Re-check: `press_refine/press_is_a_powered_bench`. Downstream powered/unpowered press arms were UNMEASURED only because of this.

## wall_beauty_bonus_exact_and_not_doubled: HARNESS
- The debug action logs `thing.thingIDNumber` (92242). `thing_stats` resolves the engine string id ("Wall92242"), so the call answered NoSuchThingId. The same failure appeared in the prev run with 58072.
- Fix: look the wall up with `list_things Wall` on its 1x1 cell and pass its `id`.
- Re-check: `first_coat/wall_beauty_bonus_exact_and_not_doubled`. This is the first time the StatPart patch ("Deepfire" in statParts) and the +3 + 25% arithmetic actually get measured.

## light_follows_the_walker: FIXTURE (rock on the walk strip)
- The walker's job stayed "Wait" at the same cell for all 80 samples. `Goto` was ordered but ended at once because the 30-cell strip east is in rock.
- Fix: `destroy_batch categories=Building` over the strip (x-3, z-4, 40x9) before the roof step in `coated_walker_carries_a_light`.
- Re-check: `worn_glow/light_follows_the_walker`. If the walker still does not move after the strip is cleared, next suspects are drafted-pawn movement or the Goto job. Read `job` in the report lines.

## styling_station_lacquers_a_parka: FIXTURE (map-wide count) plus rock
- `deepfireOnMap` is map-wide (`StylingStationLacquer.AvailableDeepfire`). It read 25 because earlier chains leave stacks around, and the check demanded exactly 3 (`STYLE_COST`). The check was wrong whatever the job did.
- Fix: the setup check is now `>= STYLE_COST`, and consumption is checked as a delta (`left0 - STYLE_COST`). The styling pad is cleared of buildings first so the styler can reach the deepfire and station.
- Re-check: `styling_lacquer/styling_station_lacquers_a_parka`. The job is queued (`job RM_LacquerWornItem`), so reaching coats=1 within 40x250 ticks is the real test.

## titled_pawn_in_two_coats: FIXTURE (cross-chain leak)
- `RM_SawCommonerInDeepfire` is map-wide (`ThoughtWorkers_Sumptuary.cs`, `ThoughtWorker_SawCommonerInDeepfire`). The failed `worn_glow` chain left its 3-coat walker alive, and that walker counts as an offending commoner.
- It PASSed in the prev run, when worn_glow got further. The mod behaved as designed.
- Fix: the status chain now runs the "WornGlow: cleanup test pawns" action before spawning its pair.
- Re-check: `status/titled_pawn_in_two_coats` and its four dependants.
- Mod-design note, not a defect: the offence is map-wide by design.

## a_gods_own_idol_moves_it_by_fifteen: LIST ARTIFACT
- `StatueGodOf` returns null unless `NinefoldDeltaBridge.IsGod` is true, which needs Ninefold loaded. The action reported `ninefold:false`, so `statueGod` was ''.
- Fix: UNMEASURED when `ninefold` is false, matching the sibling arms. The statueGod check itself is unchanged and still runs when Ninefold is present.
- Re-check: run the gods chain on a tier carrying `mandrake.rm.ninefold`. All 6 gods components are blocked until then.

## Not triaged
`press_buildable_finishes_research` is UNMEASURED because `research_availability` reports no finished flag. That is a bridge gap, not in the scope given.
