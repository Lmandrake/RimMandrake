# FLOWWORKS_NORTHSTAR_SHIP_1

Parent: `FLOWWORKS_NORTHSTAR_TRIAL_1`. Plan: `design/RimMandrake/northstar_trials/FlowWorks_trial_plan.md` §5.

## acceptance
- `code_review_status.py check` over `git ls-files src/RimMandrake/FlowWorks`: 0 DIRTY (12 DIRTY of 129 on 2026-09-30, listed in plan §1).
- Mod Settings superb per the 2026-09-12 ruling: grouped by phase, worldgen-affecting toggles labelled
  (`typedLiquidShoresEnabled`), defaults = shipped, an all-off component proving the mod still digs dry channels.
- Art for every visual bar; no def on `Things/Building/Security/TrapSpikeArmed`.
- `deploy_custom_mods.py --mod FlowWorks` in sync; DLL `.srchash` matches.
- `FLOWWORKS_DOOR_FAMILY_1` and `PIT_SUPERDEEP_COLLAPSE_1` closed, or their bars parked by his word.

## offline audit (FOUNDRY flowworksA, 2026-10-05) — state, not a verdict
- **Code review:** `code_review_status.py check` over tracked FlowWorks files (150, excluding .png/.dll/.srchash/bin/obj): **88 DIRTY, 62 CLEAN** — 38 `.cs`, 23 `.xml`, 10 `.py`, 14 `northstar/validation_v2_result_*.json` run captures (derived output; review cannot make them meaningful — candidates to untrack rather than review), 3 other. Includes today's Phase 6 / fluid-identity / fill-effects files (never marked). Acceptance (0 DIRTY) is far off; needs full-file review passes by a reviewer other than the author.
- **Settings:** grouped by section (excavation/flow, unproven, stock, burning liquid, pits, containers, tanks, drilling, shores, swale); the one worldgen-affecting toggle is labelled ("affects newly generated maps"); defaults = shipped. **All-off component ADDED**: validation.py chain `all_off_still_digs` (every FW + pit toggle off, a D=1 run beside a pond stays D=1 and dry). Not run live.
- **Art:** 3 of 100 def texture references are FlowWorks' own art; 97 borrow vanilla/foreign paths — the fill ladders (water ramps tinted, 71 refs), channels (`Gravel`), pit covers (`Soil`), sluice/grate (`DoorSimple_Mover`), drill/tap (`DeepDrill`), flame (`Fire`), swale (`GraveEmpty`), spikes (`Skullspike`), deep sand (`SoftSand`). **`RM_Ladder` is still on `Things/Building/Security/TrapSpikeArmed`** (the bar this item names); candidates `Transient/flowworks_art_2026-09-16/buildings/RUT_Ladder_A/B.png` await his pick — owner decision, not wired.
- **Deploy sync:** not checked (this pass does not touch deploy). DLL `.srchash` matches committed source by `DLL_SOURCE_STAMP_GUARD_1` at every push.
