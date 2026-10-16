# FlowWorks closeout run-sheet (2026-10-16, BENCH helper; offline only, nothing closed, game/bridge untouched)

Mod `D:\Luke\dev\RimMandrake\src\RimMandrake\FlowWorks` (packageId `mandrake.rm.flowworks`). Sources: the queue projections
(`infrastructure/state/queue/{BENCH,FOUNDRY}.md`), `rimflow show`, and the ledger `implemented` / `verify` events (open criteria
were computed by diffing each item's `implemented` criteria against its `verify ... result=pass` events, L0 excluded).
Companion run-sheet: `Transient/ratchet_live_runsheet_2026-10-16.md` section 5. Handoff: `infrastructure/state/handoffs/BENCH_REBOOT_HANDOFF_202610161625.md`.
Today's FW builds are UNDEPLOYED until BENCH deploys FlowWorks (`deploy_custom_mods.py --mod FlowWorks --apply`, game down) plus the companion DLL
(`bridgetools/build.py --gm --apply`, needed for the litres playtest scene). Every B/C row below assumes that happened.

## A. Closeable NOW offline (3) - BENCH closes; proof listed

| item | proof | how |
|---|---|---|
| `PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP` | state `doing`, needs offline, no open criteria. Verify event 2026-10-15T16:55Z: `climb_proof.py` origin 120,120 on calm save at FlowWorks b5c8547e8b, 12 MEASURED PASS incl. CLIMB_step_cost_slow_at_K. Commits ae8d38f27, 4e03b77dd are the pending reconcile | `rimflow reconcile ... --verdict partial --sha ae8d38f27 4e03b77dd --remaining "3 climb_proof rows UNMEASURED (raider, hauler, save-reload)"`, or complete if BENCH accepts them as owed to items 2-3 of design sec 8.7 |
| `HOSE_LAY_POLISH_CENTRE_VS_MOUTH` | note 2026-10-15T16:30Z: C8a-F4 FIXED 79902641c6 (test GptA_hose_install_range_from_the_mouth); C8a-F5 NOT A BUG (documented last-resort fallback). Only C7a-F2 left, "visual only, fix only if the owner wants it" | close; file C7a-F2 as a separate owner-call item if wanted |
| `FLOWWORKS_REVIEW_LOOKS_ROUND_1` | owner note 2026-10-07T03:48Z: scorch round 4 (5c1644814, save RM_fw_review_20261006g) approved; tar dark grey and see-through water checked live by BENCH. Tar look is now carried by `TAR_LOOK_TUNE_THICK_AND_SLOW` (station 3) | close, pointer to TAR_LOOK_TUNE |

Near-misses deliberately NOT in A: `RAID_DETECTOR_REPAIR_FLOOD_NOT_A_RAID` (flood half PASS at ce40347df6, real-raid half still owed -> B7).
`FLOWWORKS_QUARRY_DIGGING_1` (A1/A2 pass 2026-10-15, A3-A5 open -> B). `FLOWWORKS_PLAYTEST_CAMPAIGN_1` (owner-set campaign, no close criteria -> D).

## B. Needs a live bridge check by an agent (bridge held, `flowworks` tier running)

Order: B1 first (the suites double as the base for most rows), then the rest in any order.

### B1. The two suites
```
python.exe src/RimMandrake/FlowWorks/northstar/validation_v2.py --live          # loads the calm site RM_TestSite_calm_v1
python.exe src/RimMandrake/FlowWorks/northstar/extension_proof.py --live --site river --out <river.json>   # loads the clean saved river site
```
Pass: validation_v2 baseline 61/61 PASS on calm (0 FAIL). The litres migration (cf4f24213) and level-by-surface (4177d0631c) may change the row
count or the oracle rows; a FAIL on an old row after litres is a finding, not a pass. extension_proof river baseline 20 PASS / 0 FAIL / 1 UNMEASURED
(the UNMEASURED is `first_find_sends_letter`: a rock chunk sends no letter by design). Read the result JSON `rows`, do not trust the exit code.
Closes on pass (record per-criterion with `rimflow verify`): `FLOWWORKS_BUILD_PROGRAM_1` A1 (+A2/A3 already pass), `FLOWWORKS_CHECKOUT_SCOPE_1` A2 (both suites run back to back, results recorded),
`FLOWWORKS_QUARRY_DIGGING_1` A3/A4/A5 only if the chain rows named placer/panning/dig_finds show PASS on the river or dry half, `TESTENV_HIVES_HARDEN_RIVER_MAP_SQUATTERS` A1 and `TESTENV_FLOODS_HARDEN_SEASON_CRASHES_PARTY` A1 (the river run itself: receipt `enableStoryteller=false`, `jawa/quiet_site` status 0 threat structures, no "Seasonal flooding" letter).

### B2. Rows that need their own call (item -> check -> pass criterion)
| item | check | pass |
|---|---|---|
| `WATER_SURFACE_REWIRE_PUDDLES_LEFT_BEHIND` | review map stations 1, 2 (see C): bridge side, `validation_v2 --live` flow rows A/B/C/R with `levelBySurfaceEnabled` on | draining canal empties with no deep patches; oracle==kernel at every pulse |
| `LIQUID_LITRES_MIGRATE_DRUMS_ARE_DRUMS` | mouseover readout over canal/pond; load an OLD save with tanks/hoses (loads x2000); fill a barrel | barrel = 208 L, bucket 15 L, bottle 1.5 L, old tank units x2000, no conservation warning |
| `LIQUID_LEDGER_BUILD_NO_UNIT_LOST` A3-A7 | `python.exe src/RimMandrake/FlowWorks/northstar/liquid_checks.py --fresh-map --only L2,L4,L5,L6 --theft-day` (the Transient fw_live_checks.py copy stages pre-litres units; its L2/L4/L5/L6 now refuse) | A3 Dump tank drains with no pump; A4 Intake in pond moves nothing without pump, round trip conserves; A5 ship tank Fill/Empty over hose; A6 switched-off hose spills at open end and colonists clean it; A7 hose into another faction's tank spotted within 12 cells, 2 goodwill/day |
| `HOSE_RULINGS_BUILD_THREE_REVERSALS_ONE_CARD` A2, A5 | same harness: pipe build button opens the four-look menu, a picked look survives blueprint -> frame -> built; A5 = ledger A2-A8 above | menu has four looks, look kept; A5 follows ledger rows |
| `FLOW_SOURCE_SINK_BUILD_TAPS_FOR_MAPMAKERS` | `jawa/static_call RM_MapControls.PlaceSource` / `PlaceSink` on a dug channel | level moves, L0 ledger `flowSources/flowSinks` present, no conservation warning, survives save/reload |
| `FLOW_CONTROLS_BUILD_EIGHT_QUIET_PEBBLES` | `validation.py` chain `flow_map_controls_six` live | all component rows PASS |
| `SLUICE_GATE_REWIRE_TURNS_LIKE_A_DOOR` | `validation.py` chain `flow_door_facing` live: sluice and grate, blueprint and built, N-S / E-W / superdeep canal | drawn across the channel, neighbouring doors vanilla |
| `SLIME_CROSSING_BUILD_SLIPPERY_SLOPE` | `extension_proof.py --live --chains slime_slip` (build station 12 first, see C) | `slime_slips_the_wader`, `natural_slime_slips`, `slime_slip_off` PASS; owner look closes it (C) |
| `FLOOD_SOAK_MARKERS_BUILD_AIMED_AT_CANALS` + `FLOOD_STATION_REWIRE_DRY_CANAL_STAYS_DRY` | build station 11, select the trigger, press Flood now, Report | `reach == raisedFillCells`, `activeFloodCells=0`, flood survives the next tick (the item records the old failure: torn down because featureInOtherBiomes is off) |
| `TANK_LOOKS_WIRE_FOUR_STYLE_SWITCH` | `validation.py` row `pipe_looks.tank_choose_style_live` at review station `tank_styles` | Choose style gizmo on a BUILT tank changes this/every selected tank |
| `LIQUID_CONTAINERS_REDRAW_NO_MANA_POTIONS` | station 51 state read (see C): Style button on a container bill, style kept through fill/drink/wash, no cross-style stacking | all four styles resolve, stack never mixes looks |
| `FLOWWORKS_CONTAINER_MATERIALS_1` A2 | material survives fill, wash, pour into a tank; metal/wood refuse acid, plasteel holds | as stated |
| `LACQUER_PRESS_REWIRE_BILL_PLUS_RIGHT_CLICK` | lacquer_bill validation chain; right-click the press with a colonist selected; unpower the press | bill returns the same item +1 coat; right-click lists options; unpowered shows a disabled reason (the item leaves `doing` on this) |
| `REVIEW_MAP_LABELS_FIX_ORPHANS_ADOPTED` | `python.exe src/RimMandrake/FlowWorks/review_map.py --labels \| tr -d '\r'` | labels `8:` and `9:` appear (also covered by C station 8, 9) |
| `PIT_LIP_FIX_BOAR_HANGS_OUT` A2 | pawn asleep/downed on a pit south-row cell, then a standing occupant | no body over the south rim; standing upper half still visible |
| `PIT_LIP_OCCLUDES_OUTSIDE_1` A1 | depth-4 pawn on a pit south row | stays inside the opening, muffalo lip cover spans the sprite |
| `GIANT_MUSHROOM_DRAW_FIX_SOUTH_GOES_FRONT` | live look on the review map V block (f89a991bed) | a more-southern tall plant draws in front |
| `PIT_TEMPERATURE_SOFTENING_1` A2-A4 | desert noon: unroofed vs roofed pit temperature; occupant resistance; compassionate vs psychopath thought | A2 faster, A3 resistance falls faster than a cell, A4 RM_ExposedPrisoner only on the compassionate |
| `RIVER_TOGGLE_PROOFS_BUILD_ELEVEN_UNCLAIMED` A1-A6 | covered by the river extension_proof run (B1), plus ProofGrid flood spawn, weir catch, stake-line | A1 each of 11 toggles off removes its effect; A2 SeasonalFlood turns the surge on; A5 driftRolls; A6 continuous stake-line holds a spring flood, a gap leaks |
| `FLUID_PALETTE_EXHAUSTION..._A2`, `HEAT_BUDGET_PREFIX..._A2`, `NATURAL_HEAT_CACHE..._A2`, `STATION_REACH..._A2`, `TAR_COOLING_GLASS..._A2` | one L2 row each (P-series, `Transient/flowworks_p_series_AG_20261011.md`) | write into a dry cut never re-stamps an unkeyable liquid; room over a late hot cell warms; draining a roofed hot pool stops warming within 250 ticks; station draws 4 off its long side not 5; tar release leaves base depth terrain intact |
| `EXCAVATION_LEGACY_MIGRATION_FLAG_1` A1/A2, `EXCAVATION_LOAD_SANITY_REPAIR_1` A1 | load a save of fully filled channels; fill a channel with no recorded original terrain | no cells re-read as excavations; surrounding ground handed back; no "excavation load repair" warning |
| `FLOW_ORDER_EXTERNAL_INPUT_1` A3/A4 | settings has `maxNetworkCells` slider and `networkSeamsMoveEnabled`; a >6000-cell net wets end to end, pulse cost timed | as stated |
| `LIQUID_LOOK_MATERIAL_OWNERSHIP_1` A1, `HAZARD_TAR_TERRAIN_FROM_LIQUIDS_1` A1 | tar/propane/water keep own colours, toggle looks off/on; hazard code reads tar terrains | no colour bleed; restores vanilla water |
| `MISSION_TANK_GOAL_REWIRE_TO_DEST` A2 | chain mission report | destination tank read by ThingID (boundBy thingId) |
| `GLOW_TANK_LIQUID_FEED_1` A2, `FALLEN_WIRE_SHOCK_1` A5 | salt-water tank drawn down one unit at a time, crop grows; live end in chemfuel puddle starts a fire | as stated (needs seeded glow tank; GSS DLL for the wire) |
| `LAVA_LIQUID_BUILD_PROMISED_BY_CARD` A4 | forge map: RM_PumpingStation_Wrecked | never spawns with lava as its only liquid within 10 cells |
| `FLOWWORKS_SETTINGS_WIRE_AFTER_TANKS` A2, `SETTINGS_KIT_BUILD_GREY_SWITCHES_AT_LAST` A2/A3, `SETTINGS_SCREEN_KIT_1` A5 | open the FlowWorks settings window, `system_screenshot.py` | master off greys dependents and keeps values; Reset all asks (Cancel no-op); collapsible sections plus search box |
| `TESTENV_MEGAPEDE_HARDEN_GATECRASHER` A1, `TESTENV_TRIALSITE_DIAGNOSE_NOBODY_HOME` A1 | liquid_checks golden-site run; load `NS_FlowWorks_TrialSite_v1`, `quiet_site.ensure_colonists(3)`, advance 600 ticks | receipt arrivals empty/logged, no hostile survives; no colony_loss |
| `RAID_DETECTOR_REPAIR_FLOOD_NOT_A_RAID` (B7) | one governed chain with `jawa/fire_raid dryRun false` | raid_arrived still recorded |
| `LIQUID_INDUSTRY_SETPIECES_1` A2-A4, `SUMP_TAR_NASTINESS_1` A2-A6, `SURFACE_RIVER_WEIRS_1` A3, `SUMP_TAR_FIRE_NETWORK_1`, `PIT_SUPERDEEP_COLLAPSE_1` | adjacent (Sump/RiverWorks/umbrella), only if time remains | per item `## verify` |

## C. Needs the OWNER's eyes in game (review map `src/RimMandrake/FlowWorks/northstar/review/map/KEYSHEET.md`, driver `review_map.py --goto N`)

Build once: `python.exe src/RimMandrake/FlowWorks/review_map.py --build --fresh-map | tr -d '\r'`, then `--goto N`. Ratchet note: owner said FlowWorks is NOT signed off.

| station | what he judges | closes |
|---|---|---|
| 1 Canal off the map edge drains | lower canal stays empty, upper holds | `WATER_SURFACE_REWIRE_PUDDLES_LEFT_BEHIND` |
| 2 Liquid spreads along the canal | three branches fill in steady pulses, no liquid outside the cut, levelling is flat with no deep patches | same |
| 3 Tar crawls, water runs (also 46) | tar thick, slow, glossy dark grey, creeps a few cells while water runs; tuned live | `TAR_LOOK_TUNE_THICK_AND_SLOW` (needs the live look-tuning tool) |
| 8, 9 | notice lines carry the numbers 8: and 9:; refill waits for the muffalo; fill-in sends water home | `REVIEW_MAP_LABELS_FIX_ORPHANS_ADOPTED` |
| 11 Canyon floods run through canals | Flood now at the trigger: water enters at the west end and runs the whole canal, nowhere else, survives next tick | `FLOOD_STATION_REWIRE...`, `FLOOD_SOAK_MARKERS...` |
| 12 Slime is nearly uncrossable | bank colonist walks round, slip text over wader, climb-out slides back, natural pool slips but never slides back, setting OFF wades | `SLIME_CROSSING_BUILD_SLIPPERY_SLOPE` (closes on his look) |
| 45 Spikes, ladder, gates own drawings | all four own art, open vs shut readable; spikes should be half a man tall, ladder wall-mounted | `PIT_SPIKES_SHRINK_HALF_A_MAN`, `PIT_LADDER_REDRAW_HUNG_ON_THE_WALL`, `FLOWWORKS_LADDER_RAISE_LOWER_1` A2 |
| 51 Containers in the four looks | four styles, liquid window takes the colour, body untinted, Style button on the bill, no two looks in one stack | `LIQUID_CONTAINERS_REDRAW_NO_MANA_POTIONS`, `FLOWWORKS_CONTAINER_MATERIALS_1` A3 |

Also owner-gated, if he has time (ordered cheapest first): station 36 raised ladder, 62 spills (`LIQUID_LEDGER` A9), 60 four pipe looks (`HOSE_RULINGS` A4), station V pits (`FLOWWORKS_VISUAL_PRINCIPLES_1` A4), 38 sun-and-cold (`PIT_TEMPERATURE_SOFTENING_1` A6), `MESSYCONDUIT_CABLE_PILE_LOOK_1` A4 (junction pile, Modern strip pile, crossing hoses), the hose/pump connection sheet `http://localhost:35259/?t=5cQKurOK_hGH7Dhxi9E70Q` (`HOSE_JOINTS_REDESIGN_PUMP_TOO_PUNY`), pit ladder art sheet `http://localhost:36179/?t=kxi6u8T-d6C9Cgjf1-kkQg`.
Owner calls flagged in the litres handoff: chemfuel/astrofuel item stays 200 L, machine rates kept at old balance.

## D. Not closeable this session (needs build work or a gate that is not this session)

- `TANK_TALL_BUILD_TWICE_THE_DRINK`: owner rejected the tall-tank art 2026-10-15 (wrong perspective); redo owed.
- `PROPANE_CANAL_WIRE_STILL_NO_FLUID`: FlowWorks_Fluids.xml has no propane FluidDef (only water, tar, four slimes); build.
- `SPILL_FILTH_FIX_SOIL_SAYS_NO`: RM_Filth_LiquidSpill still `placementMask Natural` only; def/comment fix plus live proof owed.
- `MODCHECK_SETUP_UNMEASURED_FIX_READS_AS_FAIL`: `Utils/modcheck/runner.py` ~592 still records chain-setup ExpectationFailed as FAIL regardless of an UNMEASURED prefix.
- `VALIDATION_V2_IDENTITY_WIRE_READS_ZERO`: no run_identity in FlowWorks northstar code.
- `FLOWWORKS_NORTHSTAR_GREEN_MINIMAL_1`, `_GREEN_FULL_1` (full-list cold load ~15 min), `_TRIAL_1`, `_SHIP_1`, `FULL_LOAD_RESIDUE_TRIAGE_1`: gated on the full-list run, code review CLEAN (88/150 DIRTY at last count), owner word.
- `WATER_SURFACE_REWIRE...`, `SLIME_CROSSING`, `SLUICE_GATE`, `FLOW_*`, `TANK_LOOKS`, `LITRES`: code files still DIRTY for review (`code_review_status.py check`), so `FLOWWORKS_NORTHSTAR_SHIP_1` stays open even after the live pass.
- `DIG_ROCK_TUNE_STONE_FIGHTS_BACK`, `HOSE_JOINTS_REDESIGN_PUMP_TOO_PUNY` (owner rules sheet first), `PIT_LADDER_REDRAW`, `PIT_SPIKES_SHRINK` (art redraw), `PIT_SUPERDEEP_COLLAPSE_1` (umbrella), `DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL` (design owed), `VEXXITH_USES_1` (no work started), `FLOWWORKS_PLAYTEST_CAMPAIGN_1` (standing campaign), `TESTENV_TOXIC_DIAGNOSE_RIVER_SITE_SNIFFLES` (open diagnosis).
- Blocked FW-adjacent: `CRACKEDLANDS_MECHANICS_BUILD_1`, `FORGE_CYCLE_MECHANICS_1`, `SWALE_CANAL_ART_REFERENCE_1`, `CAULDRON_MECHANICS_BUILD_1`, `LIQUID_BOTTLE_LOOP_1` (fill job never produces a filled bottle, 4 tries), `LIQUID_THIRST_CHAIN_1` (depends on the bottle loop), `BAZAAR_BROKER_TAB_1`.

## CHANGELOG step (do last, after the walk items settle)

`src/RimMandrake/FlowWorks/CHANGELOG.md` 1.0.0 (dated 2026-10-15) is stale: the DLL has changed many times since (litres, level-by-surface, slime slip, door facing, map controls, tank styles, hose joints). After the final deploy, add the packaged DLL hash line the way GSS 1.0.0 does (GSS names `5e523c88...` in its "repackage" line): take the md5/sha from `python3 src/RimMandrake/Utils/dll_source_stamp.py check | grep FlowWorks` (expect MATCH), list the new player-facing features, and keep the version equal to `<modVersion>` in `About/About.xml`.

## Recommended order

1. Deploy FW + companion DLL (game down; BENCH).  2. Startup Player.log first-exception read.  3. B1 both suites.  4. Quick B2 rows that need no owner (litres, ledger harness, door facing, map controls, lacquer, labels).  5. Build review map, owner walks C in order 1, 2, 3, 8/9, 11, 12, 45, 51 (water first, since rows 1-2 verify the biggest change).  6. Record `rimflow verify` per criterion, close A and the passed items.  7. CHANGELOG hash.
