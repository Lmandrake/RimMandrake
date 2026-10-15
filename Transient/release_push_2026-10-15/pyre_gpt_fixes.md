# Pyrelands GPT-hunt fixes — BENCH, 2026-10-15

Source: `Transient/release_push_2026-10-15/gpt_Pyrelands/TRIAGE.md`. Owner, 2026-10-15: "No withheld functionality.
Build it all, test it all, get it all working." Offline only: no deploy, no bridge, no live flight.
Every CONFIRMED item is `rimflow implemented` (L0 passed, L2 live proof owed; criteria carry the command).

## CONFIRMED (fix + offline test or script row)
| # | item | fix | offline proof | sha |
|---|---|---|---|---|
| 1 | ASH_TERRAIN_FIX_NO_MEDIUM_GROUND | deep ash + scorchable ground carry vanilla Soil's affordances (Walkable/Light/Medium/Heavy/GrowSoil/Diggable; sand without GrowSoil) | lint `pyrelands-affordance` + 2 planted defects | 0ead3a5a0d |
| 2 | FIREHAWK_EMBER_FIX_WALKS_ITS_TWIG | JobDef tryStartFlying + ifFlyingKeepFlying + overrideFlyChance 1 | lint `pyrelands-flight` + planted defect; firehawk row reads `ProbeFlight` (state only) | 27593d1659 |
| 3 | FIRE_CLOCK_FIX_RAIDS_IGNORE_THE_SWITCH | fire raid + flame harvest gate on `RM_BurnKernel.TribesIncidentSwitchesOn(..., fireClockEnabled)` | fuzz 16-row table; lint wiring check | 331f33be07 |
| 4 | FURNACE_AURA_FIX_WARMS_THROUGH_WALLS | aura only in the open (none in an enclosed room, none without line of sight); vanilla heat pusher obeys the thermal switch | selftest `AuraReaches`; furnace_warmth row unroofs its pen + roofed arm expects 0 | e69fc18e80 |
| 5 | RITE_HARVEST_FIX_PICKS_PAST_FULL | full harvester stops; range measured from the rite origin (duty focus) | fuzz RiteHarvestWanted / RiteHarvestInRange (3-3 route: script row) | 0f3ad0f1dc |
| 6 | FURNACE_WARMTH_FIX_NO_SIGN_TO_READ | owner by card "Add a small sign": inspect line "Warmed by furnace-beast (+N C)" (keyed RM_FurnaceWarmedBy) | selftest `ShowsSign`; furnace_warmth row reads `WarmthSign` | ccdceb2702 |
| 7 | FIRE_RITE_FIX_DEFENDERS_MISS_THE_WAR | arrival timeout + turned-hostile exit source from every travel-subgraph toil | lint wiring check | f35fa336ce |
| 8 | SCORCH_FRUIT_FIX_LANDS_ON_FIREBREAK | pods land only on Pyrelands ground; once-per-fire roll set saved with the map (pruned to live fires) | fuzz FruitLandingLegal / RolledStillBurning | 59092408271 |
| 9 | BURN_HISTORY_FIX_ANCHOR_NEVER_AGES | history pruned on read too | fuzz PruneHistory | 874e177ccb |
| 10 | ASH_FIELD_FIX_FORGETS_THE_WATER | (3) watered grid saved (6) Black Rain hours 0 dries at once (7) overlay redrawn wet-to-dry (8) For() cache drops removed maps; (9) PLAUSIBLE: row only | fuzz BlackRainWaters / WateredExpiredWithin | 56cc1bdcdc |
| — | FlowWorksIrrigationRead (no item) | liquid accepted PER CELL (fluidGrid + palette, unrecorded -> ActiveFluid); ExplosiveGrowth + Pyrelands DLLs rebuilt | `_Shared/FlowWorksIrrigation/FlowWorksIrrigationKernel.cs` in the Pyrelands fuzz | 603ce41fbe |

## PLAUSIBLE (live check in `src/RimMandrake/Pyrelands/validation.py`, chain `gpt_hunt_plausible`, ce8b4f1799)
| # | item | row | state |
|---|---|---|---|
| 11 | FURNACE_SEED_DIAGNOSE_SHIPPED_SAVE_HERDLESS | save_furnace_herds_seeded (`diag/save_world_check.py`) | offline read of CANONICAL_ASHKARR_START_2026-09-12.rws: no seeder component (Pyrelands not in its list), 0 herds -> nothing latched yet; re-read the freeze candidate |
| 12 | FIRE_ECOLOGY_DIAGNOSE_FOREST_FIRES_FRUIT | vanilla_soil_fire_grows_no_fruit | live row |
| 13 | FURNACE_HERD_DIAGNOSE_ARRIVES_NEVER_LEAVES | world_herd_rejoins_circuit | UNMEASURED + procedure (design call) |
| 14 | FURNACE_CARAVAN_DIAGNOSE_HEARTH_GOES_COLD | none | owner reversed caravan warmth; item already dropped |
| 15 | FIREFOAM_DIAGNOSE_CANNOT_AIM_AT_FIRE | firefoam_can_aim_at_fire | def read: no targetParams (vanilla defaults false) -> row will FAIL; fix not built (scope freeze) |
| 16 | SAND_SHOVEL_DIAGNOSE_DIGS_UNDER_WALLS | shovel_refuses_under_wall (probe `RM_TerrainDigProof.ProofShovelUnderWall`) | live row |
| 17 | FIRE_SCAN_DIAGNOSE_BIG_BURN_COST | big_burn_tick_cost | UNMEASURED + procedure (CALIBRATING) |
| 18 | ALLOWLIST_DIAGNOSE_BARE_MIXED_PATCHES | allowlist_mixed_patch_keeps_grass | UNMEASURED + procedure (needs the final paint) |
| 19 | TRIBES_LOOKUP_DIAGNOSE_FIRST_ONE_FALLS | tribes_lookup_one_faction | start save: 1 TribeCivil -> moot |
| 5/3-3 | rite route through fire | rite_harvest_route_avoids_fire | UNMEASURED + procedure |
| 10/9 | ash field `active` latch | ash_field_activates_after_init | UNMEASURED + procedure |

## Notes
- Code review: 18 changed files marked CLEAN after full-file review. Still DIRTY (edited, not fully re-reviewed this pass):
  validation.py, PyrelandsFuzz.cs, FireEcologyHook.cs, PyrelandsAshField.cs, MapComponent_BurnLine.cs, RM_BurnKernel.cs,
  RM_FireEcoKernel.cs, lint_pyrelands_defs.py, RM_TerrainDig.cs (hard-coded English designator label/desc is a finding).
- `infrastructure/state/CANONICAL_SAVE.md` names `CANONICAL_ASHKARR_2026-09-09.rws`, which is not in the Saves folder.
- Pushes twice blocked by another agent's FlowWorks DLL/srchash mismatch (DLL_SOURCE_STAMP_GUARD_1); both cleared by them.
