# Offline worklist, ratchet pilot (Pyrelands + FlowWorks + GimmeSomeSlack) - 2026-10-14

Open items that are build/fix work. CONFLICT = touches FlowWorks C# (`src/RimMandrake/FlowWorks/Source`), where a builder is editing now (TANK_TALL, POND_BED, PIT_POCKET_GRID). Sequence behind them or take only the non-C# slice.
Do not touch (another agent is on them): POND_BED_BUILD_HOLLOW_KEEPS_ITS_SHAPE, RATCHET_PILOT_PROVE_THREE_MODS_ONE_LOOP, PYRE_BURROWERS_DIAGNOSE_FLEE_BEFORE_DIVE, SAFE_ADVANCE_MENU_DIAGNOSE_LUCKY_NULLREF, TANK_TALL_BUILD_TWICE_THE_DRINK, TESTENV_HIVES/FLOODS/MEGAPEDE/TRIALSITE, PYRELANDS_SHIP_READINESS_1.

## Highest value first
| ID | Scope (one line) | Files | FlowWorks C# conflict |
|----|------------------|-------|-----------------------|
| `PIT_CLIFF_MASK_BUILD_ASTAR_LEARNS_WALLS` | per-band connectivity masks with per-request swap, slow-climb step cost, retire AvoidPits/StayInPit/PlanRoute (design `relative_depth_climb_design_2026-10-12.md` s8.5 steps 2-3,5) | FlowWorks/Source pit pathing + selftests | YES, and blocked behind PIT_POCKET_GRID (BENCH, doing) |
| `PIT_RAMP_BUILD_STAIRS_BEAT_LADDERS` | RM_PitRamp building + ladder spans any depth slowly + settings + size table (design s8.2, 8.4) | FlowWorks/Defs, Source, Textures (art ledger), Languages | YES (after pocket grid) |
| `POND_ELEVATION_BUILD_LAKES_RUN_DEEP` | deep elevation for natural bodies (>4), water-height flow, lift 4000-cell cap, cap sink at 4 (design natural_bodies s9) | FlowWorks/Source body/flow code | YES; wait for POND_BED |
| `FLOOD_SWITCH_OFF_PROVE_SPILLS_GO_NOWHERE` | with legacy-flood setting OFF a spill places nothing and the settings text understates it: fix text or define behaviour, add selftest | Flood_FlowWorks.cs CanFloodInto, Languages (item file has the analysis) | YES (C#); the Languages text slice is safe |
| `HOSE_REEL_MIGRATE_TO_FLOWWORKS_AT_LAST` | ledger says proposed but steps 0-8 landed (6b031841a..ef888b271); needs an `implemented` record or a list of what remains, then close; GSS becomes cables/conduits only | ledger only first; GimmeSomeSlack/ leftover reel code check | no (read-only audit) |
| `LIQUID_KIT_COMMENTS_CORRECT_GHOST_PATCHES` | correct two comments citing nonexistent patches (RM_FluidResidue.cs header, RM_LiquidKits.xml) | FlowWorks/Source/RM_FluidResidue.cs, Patches/Kits xml | comment-only C# edit: YES, tiny, do after the builder |
| `PYRELANDS_GRASS_SATURATION_1` | ground cover: grass everywhere, ash where burned, no bare dirt; def side done, residual is clear Bush/Pincushion instances and a look | Pyrelands biome defs under src/RimMandrake | no |
| `PYRELANDS_STRUCK_GLASS_RITE_BUILD_1` | Struck Glass rite (ring of fulgurite, lightning-storm strike), spec in item file | mandrake.rut.rites mod, Pyrelands defs, art list job RM_StruckGlassRing | no |
| `FW_RIVER_SITE_DIAGNOSE_NOBODY_SWEPT_AWAY` | build a river site where a pawn is swept and the pan draws stock (unblocks live items 4-6); harness/site, not mod | FlowWorks/northstar river site builder, extensions_rivers.py | no (python harness) |
| `FLOWWORKS_NORTHSTAR_SHIP_1` | SHIPPED rung: settings superb, art complete, code review CLEAN, deployed | FlowWorks Settings, code_review_status over FlowWorks files | possible review marks only |
| `TESTENV_BURROW_HEAT_HARDEN_COLONISTS_COOKED` / `TESTENV_BURROW_COLD_PROVE_RELOAD_PER_TRIAL` | cap trials per map or reload fixture per trial; heat repeats killed colonists | Pyrelands validation.py / burrow diag harness | no (needs bridge to prove) |
| `VITALS_OVERHEAD_MEASURE_FULL_LIST_TOLL` | game-up measurement of vitals overhead (not offline; keep for a game-up window) | JawaBench vitals | no |

## Process/ledger-only (no code)
`FLOWWORKS_PLAYTEST_CAMPAIGN_1` (direction item from 2026-10-06; the pilot is its successor; recommend drop or supersede by RATCHET_PILOT after owner nod), `FLOWWORKS_REVIEW_LOOKS_ROUND_1` (scorch and tar approved 2026-10-07; items 1, 4, 5 never recorded as done: audit then close), `FLOWWORKS_NORTHSTAR_GREEN_MINIMAL_1` (needs a verify record, see v2 61/61), `NORTHSTAR_FAST_DRIVER_1` (core built, live proof owed; may be moot), `GIMMESOMESLACK_NORTHSTAR_VALIDATE_1` (owner conditionally accepted 2026-10-06; GSS proof_all now 106/106, ask owner to validate), `PYRELANDS_NORTHSTAR_TRIAL_1` (parent), `FLOODS/FLOOD_WITNESS_EVENT_1` is Cracked Lands, not in scope.

## Done this triage
Superseded `FLOWWORKS_PIT_OCCUPANT_HIDDEN_BY_LIP_1` by `PIT_LIP_OCCLUDES_OUTSIDE_1` (same defect, a100d8e2e).
Uncertain, left: everything else; no item had unrecorded proof beyond what the 2026-10-13 closer already noted.
