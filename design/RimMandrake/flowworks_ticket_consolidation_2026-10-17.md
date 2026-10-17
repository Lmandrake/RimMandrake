# FlowWorks ticket consolidation (2026-10-17)

Owner, 2026-10-17: *"please now consolidate all FlowWorks tickets to respect the new 'let's rebuild it all to work once
and for all' ruling I just gave and re-issue them sensibly."* Epic: `FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG`; plan:
`design/RimMandrake/flowworks_one_rebuild_plan_2026-10-17.md` (rulings R1-R9, packages P1-P10). Executed through rimflow
(supersede / file / needs / note); every supersede cites his words above, every filing `--per-ruling` the epic. No item
was closed as passed: every owed live check moved into a successor's `## verify`.

**Census.** `model.replay()` at this commit, open states plus built/validated, selected by id family (FLOWWORKS_, WATER_,
PIT_, LIQUID_, HOSE_, DEPTH_, RIVER, CANAL, SLUICE, LAKE, DIG_ …), FlowWorks words in the title, or an item file citing
`flowworks_*.md`; then a second sweep over water/depth/liquid/hose/pump/tank words. 122 first-sweep hits and every second-sweep hit were read; the
FlowWorks-related ones are below. Sanity probe: the epic and all its filed children appear. Hits judged NOT FlowWorks
(other mods that merely mention water, pits or tanks: GSS_*, Stillsand, Sarlacc, Bacta, Twilight Sea, sea passes,
Rust Cathedral, …) are left out.

**Verdicts.** RE-SCOPE (package) = a rebuild package re-issued with criteria rewritten in the shared language (the
epic's item file: decilitre stock, one surface per connected body within 1 cm, hole depth and water depth with litres,
the under-25 cm look, 8 m dig default settable 2-20 m, the four relative rules), each with the live proofs it owes.
ABSORBED = superseded into a package. SUPERSEDED = replaced by a new item. RE-SCOPE (note) = stays, part of it moves
or waits on a decision. KEPT = still valid and unaffected. DEAD = obsolete under five / notches / 2 m pit /
whole-square recession / z-levels: **none of the open items was purely that**; the dead parts lived inside items that
were absorbed (whole-unit surface rule, receding-source run) or carry a correction note (the rewire item's "pit stays
2 m"). `WATER_SURFACE_REPAIR_LEVEL_OR_BUST` was already superseded by P3 earlier the same day.

**Counts:** 11 re-scoped packages (P1-P10, P9 is two items) · 4 re-scoped by note · 5 absorbed · 1 superseded ·
0 dead · 7 new · 76 kept.

**Dependency order** (needs in brackets): `WATER_SCENES_WALK_MEND_TRIPS_AFTER_S4` [offline] → P1 [deploy];
P2 [bridge] any time, gates shipping P5; P3 + P4 [offline, one pass] → P5 + P6 [offline] → P7 [offline] → P8 [offline]
→ P10 [deploy + bridge + his look]; P9 [offline, then his look] any time. Owner items: the two cards any time; S5 third
draft and the bars after P10.

## For him to decide (I was not sure)
1. `FLOWWORKS_BUILD_PROGRAM_1` (validated, the 2026-09-16 program) absorbed into the epic: right, or keep it open beside it?
2. `DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL`: do digging machines/droids still exist now colonists dig to 8 m (20 m max)?
   Kept open with a note; drop it if not.
3. `POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD` (BENCH, doing): its pond stages may be wholly replaced by the solver; waits on
   `WATER_NATURAL_DECIDE_ONE_SURFACE`.
4. `RM_WaterThin` (already provisionally installed) may already BE the under-25 cm look of
   `VERY_SHALLOW_WATER_RESKIN_HE_SEES_FIRST`; the item says to check before generating more.
5. `LIQUID_LITRES_MIGRATE_DRUMS_ARE_DRUMS` (built, owner-held, live check never run) absorbed into P4 rather than proved
   first on its own.
6. `CANAL_LAKE_COLOUR_UNIFY_TWO_BLUES` was filed from a relayed review observation; no measurement of the two colours yet.

## North star
`design/validation_walks/RimMandrake/FlowWorks.md` `## north star` gained `still_water_one_surface_height` (R9; no other
bar touched; state stays DRAFT). Measuring script stub: `src/RimMandrake/FlowWorks/northstar/level_surface_bar.py`,
wired as chain `water_level_surface` in `src/RimMandrake/FlowWorks/validation.py` (UNMEASURED until P3's diagnostic).
He re-validates in one sitting (`FLOWWORKS_BARS_JUDGE_FIVE_IN_ONE_SITTING`): the new bar, `fill_tier_legible`,
`depth_and_fill_jointly_legible`, `pit_depth_ladder_legible`, `pawn_height_ladder_legible`.

## The table
| id | state | what | verdict | reason (ruling) |
|---|---|---|---|---|
| `DEPTH_READOUT_BUILD_TWO_NUMBERS_NOT_ONE` | proposed | In-game readout shows hole/canal depth and water depth as two separate figures, water with volume in parent... | RE-SCOPE (package P8) | needs bridge -> offline (building is offline; its live row is in P10); readout per R4 on the solver's numbers |
| `DIG_COST_TUNE_DEEP_IS_A_MEGAPROJECT` | proposed | Plan P6: dig cost by depth keeps today's curve (3,200 x the notch being cut; one 7 m square ~5.5 digger-day... | RE-SCOPE (package P6) | criteria rewritten in the shared language (decilitres, one surface, two-figure readout, under-25 cm look, 8 m dig 2-20 m, relative rules) with the live proofs it owes; R6 one big rebuild |
| `FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG` | proposed | One big FlowWorks depth rebuild: exactly-level water (decilitres, one surface per body), metres/litres rewi... | RE-SCOPE (package P10) | criteria rewritten in the shared language (decilitres, one surface, two-figure readout, under-25 cm look, 8 m dig 2-20 m, relative rules) with the live proofs it owes; R6 one big rebuild |
| `LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD` | proposed | FlowWorks code/defs/settings to the ruled depth spec §7.2: RM_Volume SquareAreaM2+MetresPerNotch, FillTier ... | RE-SCOPE (package P4) | criteria rewritten in the shared language (decilitres, one surface, two-figure readout, under-25 cm look, 8 m dig 2-20 m, relative rules) with the live proofs it owes; R6 one big rebuild |
| `PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH` | proposed | Plan P2: owed live proofs of the built climb work (pocket grid, cliff masks, ramp, ladder: PIT_POCKET_GRID_... | RE-SCOPE (package P2) | criteria rewritten in the shared language (decilitres, one surface, two-figure readout, under-25 cm look, 8 m dig 2-20 m, relative rules) with the live proofs it owes; R6 one big rebuild |
| `PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT` | proposed | Plan P5 (T1): dig cap from 2 m to a Mod Setting, default 8 m (16 notches), range 2-20 m; split Superdeep (4... | RE-SCOPE (package P5) | criteria rewritten in the shared language (decilitres, one surface, two-figure readout, under-25 cm look, 8 m dig 2-20 m, relative rules) with the live proofs it owes; R6 one big rebuild |
| `PIT_RULES_REWIRE_RELATIVE_NOT_ABSOLUTE` | proposed | Plan P7: the four 2 m-keyed rules relative to the height difference (owner R7): drowning by water over the ... | RE-SCOPE (package P7) | criteria rewritten in the shared language (decilitres, one surface, two-figure readout, under-25 cm look, 8 m dig 2-20 m, relative rules) with the live proofs it owes; R6 one big rebuild |
| `VERY_SHALLOW_WATER_RESKIN_HE_SEES_FIRST` | proposed | Plan P9: new water look for water under 25 cm deep (every liquid's first band), keyed by water depth; cosme... | RE-SCOPE (package P9) | criteria rewritten in the shared language (decilitres, one surface, two-figure readout, under-25 cm look, 8 m dig 2-20 m, relative rules) with the live proofs it owes; R6 one big rebuild |
| `WATER_DEPTH_RESKIN_HE_LOOKS_FIRST` | proposed | New art per ruled depth spec §4: wall-edge depth band overlay on wet canals (gap between water and lip) and... | RE-SCOPE (package P9) | criteria rewritten in the shared language (decilitres, one surface, two-figure readout, under-25 cm look, 8 m dig 2-20 m, relative rules) with the live proofs it owes; R6 one big rebuild |
| `WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES` | proposed | Plan P3: level-surface solver (flowworks_level_surface_2026-10-17.md Option 1): each connected body holds e... | RE-SCOPE (package P3) | criteria rewritten in the shared language (decilitres, one surface, two-figure readout, under-25 cm look, 8 m dig 2-20 m, relative rules) with the live proofs it owes; R6 one big rebuild |
| `WATER_SCENES_PROVE_AFTER_THE_CREEP_FIX` | proposed | Plan P1: deploy the fe309aefe FlowWorks DLL (dry-front creep fix; game down), rerun S2, S5 and S6 of norths... | RE-SCOPE (package P1) | criteria rewritten in the shared language (decilitres, one surface, two-figure readout, under-25 cm look, 8 m dig 2-20 m, relative rules) with the live proofs it owes; R6 one big rebuild |
| `CANAL_LAKE_COLOUR_UNIFY_TWO_BLUES` | proposed | Water in a dug canal and the lake it joins are drawn in different colours (seen in the 2026-10-17 water-sce... | NEW | canal water vs the lake it joins drawn in different colours; child of WATER_DEPTH_RESKIN_HE_LOOKS_FIRST |
| `DEPTH_DEFAULTS_ASK_ELEVEN_VETOES` | proposed | One question card: keep or veto the rebuild's defaulted choices, V1-V8 of the plan (dig cost curve, drownin... | NEW | one card: V1-V8 + D3/D4/D6 defaulted choices |
| `DEPTH_QUESTIONS_ASK_RAIDERS_FIRST` | proposed | The rebuild's unasked cards, raiders first: raiders facing a trench they cannot cross (play Q7: scaling lad... | NEW | the unasked cards Q7 (raiders vs trench) first, then Q6, Q2, Q11, Q12, Q9 |
| `FLOWWORKS_BARS_JUDGE_FIVE_IN_ONE_SITTING` | proposed | Owner re-validates the FlowWorks north-star section in one sitting: the new bar still_water_one_surface_hei... | NEW | his re-validation of the north-star section: the new level bar + four reworded bars |
| `WATER_NATURAL_DECIDE_ONE_SURFACE` | proposed | Placeholder for the natural-water review (flowworks_natural_water_engine/play_2026-10-17.md, in flight): th... | NEW | placeholder for the natural-water review's owner decisions (helpers writing flowworks_natural_water_engine/play_2026-10-17.md) |
| `WATER_SCENES_S5_JUDGE_THIRD_DRAFT` | proposed | Owner: approve scene S5 redrawn a third time with exactly-level numbers (plan P10; one surface per body, li... | NEW | his approval of S5 redrawn with level numbers (replaces WATER_SCENES_JUDGE_S5_REDRAWN) |
| `WATER_SCENES_WALK_MEND_TRIPS_AFTER_S4` | proposed | northstar/water_scenes_walk.py raises a Python traceback after S4.c (S4.d never reported) and again in S5 (... | NEW | S4 crash: water_scenes_walk.py tracebacks after S4.c and in S5; blocks P1 |
| `FLOWWORKS_BUILD_PROGRAM_1` | superseded | FlowWorks - the phased build program for one liquid mod built on excavation depth as the primitive, carryin... | ABSORBED -> the epic | old phased program; its owed rows (receding-source terraced run, wall art judged, his acceptance) are carried by the epic verify and FLOWWORKS_NORTHSTAR_TRIAL_1; whole-square recession dead under R1 |
| `KERNEL_SELFTEST_WIRE_SHIPPED_TUPLE_NEVER` | superseded | No FlowWorks SelfTest case runs RM_FlowKernel at the full shipped flag combination (V&V pilot 1 lint) | ABSORBED -> P3 | the solver's selftests at the shipped flag combination are now a P3 verify line; R6 |
| `LAKE_FLOOR_TUNE_TEN_TO_FIFTY_METRES` | superseded | Natural lake/pond floor cap: default 20 m (was 10 m), setting up to 125 m; very large lakes and oceans may ... | ABSORBED -> P4 | same bed code and settings (plan P4); its 20/125/50 m criteria copied into P4 verify; R5 keeps lake floors |
| `LIQUID_LITRES_MIGRATE_DRUMS_ARE_DRUMS` | superseded | Re-base all FlowWorks liquid accounting to litres (deep square ~4,300 L; barrel 208 L, bucket 15 L, bottle ... | ABSORBED -> P4 `LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD` | litres/dL base (built cf4f24213) is P4's foundation; its never-run live checks moved to P4/P8 verify, not passed; R1+R6 |
| `WATER_SURFACE_REWIRE_PUDDLES_LEFT_BEHIND` | superseded | FlowWorks: water flows from higher water surface to lower (fill-depth), gap >=2 units, so flat channels lev... | ABSORBED -> P3 `WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES` | whole-unit 'gap >= 2' surface rule (built, never deployed; live walk 0/deep/0) is replaced by the exactly-level solver; R1 (notches dead) |
| `WATER_SCENES_JUDGE_S5_REDRAWN` | superseded | Owner: re-approve redrawn scene S5 (gravity limits A/B, 2 m canal F, pump G; scenes file re-sealed 1e0a16af... | SUPERSEDED -> `WATER_SCENES_S5_JUDGE_THIRD_DRAFT` | S5's whole-notch gravity limits are wrong under level water; R3 redraw in P10; its bar and veto asks moved to the bars and vetoes items |
| `DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL` | proposed | Digging deeper than 4: a digging machine, a self-digging digger droid, and droids that can operate the mach... | RE-SCOPE (note; owner decides) | premise 'digging deeper than 4' is gone (colonists dig to 8 m, 2-20 m); whether machines/droids dig at all is unruled; R5 |
| `FLOWWORKS_REVIEW_LOOKS_ROUND_1` | proposed | FlowWorks review-map round 2026-10-06: scorch marks, stone/dirt tar dark grey opaque, depth-only water labe... | RE-SCOPE (note) | its item 4 (water named by depth words) is replaced by the two-figure readout P8; rest stands; R4 |
| `PIT_TEMPERATURE_SOFTENING_1` | validated | Pit temperature couples hard to ambient and wears down resistance; Exposed Prisoner thought | RE-SCOPE (note) | its pit-room test 'room >=50% D=4' is the 2 m pit; P7 re-points it to the person-band pocket (V6); owed live rows run after P7; R7 |
| `POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD` | doing | Natural water cells (ponds, marsh, vanilla water terrain) get partial depth like dug cells: a drying pond s... | RE-SCOPE (note; owner/helpers decide) | integer head rule and 's levels below the brim' replaced by the solver; natural water waits on `WATER_NATURAL_DECIDE_ONE_SURFACE`; R1 |
| `CRACKEDLANDS_MECHANICS_BUILD_1` | doing | Build the Cracked Lands mechanics: the Swale (FlowWorks-normal, Utinni-locked biome discovery), survey+cist... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `CRACKEDLANDS_SWALE_CAMPAIGN_LOCK_1` | ready | Utinni lock for RM_Swale: locked in the campaign until discovered in the Cracked Lands (first completed sur... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `DIG_ROCK_TUNE_STONE_FIGHTS_BACK` | doing | Canal digging: through rock yields rock chunks at the vanilla rock-wall mining rate and takes much more wor... | KEPT | rock factor multiplies the P6 curve (noted) |
| `EXCAVATION_LEGACY_MIGRATION_FLAG_1` | built | FlowWorks: Legacy rehydration: schema flag and a restoration policy for cells with no original terrain | KEPT | legacy terrain rehydration; independent of P3's body migration |
| `EXCAVATION_WALL_ART_1` | validated | Wall-face art for all four depths, spikes and ladder (Quarry perspective) | KEPT | D1..D4 wall faces stay valid; faces past 2 m are P5/P9 |
| `FLOOD_SOAK_MARKERS_BUILD_AIMED_AT_CANALS` | doing | Dev map controls (Baroque Biomes): flood trigger aimed at a canal (fixes FW review station 11) and soak zon... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `FLOOD_STATION_REWIRE_DRY_CANAL_STAYS_DRY` | proposed | FW review station 11: forced canyon flood is torn down next tick on a non-canyon map (Active false: feature... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `FLOWWORKS_CHECKOUT_SCOPE_1` | built | FlowWorks: ordinary features only in the on-request extension proof; walk lines lack coverage arrows | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `FLOWWORKS_CONTAINER_MATERIALS_1` | validated | Bottles and barrels are made from a material the player picks (stuffable + per-material recipes at matching... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `FLOWWORKS_CONVERTER_FIX_BLOCKED_STARVES_REST` | built | FlowWorks: first blocked recipe truncates shared budget (CompLiquidConverter.cs:~265) | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `FLOWWORKS_CONVERTER_FIX_CAP_EATS_CHANGE` | proposed | FlowWorks: budget cap drops earned remainder (RM_ConversionMath.cs:76) | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `FLOWWORKS_HOSE_FIX_PAUSE_REMESH_EVERY_FRAME` | proposed | FlowWorks: hose mesh rebuilt every frame while paused mid-transition (RM_MapComponent_Hoses.cs:584) | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `FLOWWORKS_LADDER_RAISE_LOWER_1` | validated | Pit ladder has two player-toggled states (raised/lowered); entering a pit from the top descends a lowered l... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `FLOWWORKS_NORTHSTAR_GREEN_FULL_1` | built | FlowWorks north star GREEN on the full mod list | KEPT | child of the trial; runs after the epic |
| `FLOWWORKS_NORTHSTAR_GREEN_MINIMAL_1` | proposed | FlowWorks north star GREEN on the minimal tier | KEPT | child of the trial; runs after the epic |
| `FLOWWORKS_NORTHSTAR_SHIP_1` | proposed | FlowWorks SHIPPED: settings superb, art complete, code review CLEAN, deployed | KEPT | child of the trial; runs after the epic |
| `FLOWWORKS_NORTHSTAR_TRIAL_1` | built | FlowWorks north-star trial: VALIDATED -> WIRED -> GREEN-minimal -> GREEN-full -> SHIPPED | KEPT | GREEN/SHIP chain now follows the epic; section needs his re-validation first (noted) |
| `FLOWWORKS_PITCOVER_FIX_BURNS_PAWN_UNHARMED` | proposed | FlowWorks: destroyed pit cover gives occupants no fall (Building_PitCover.cs:161) | KEPT | cover-destroyed fall; independent bug; fall size comes from P7 |
| `FLOWWORKS_PITFALL_FIX_HISTORY_NOT_SAVED` | proposed | FlowWorks: lastCell not scribed, last-tick fall lost across save (RM_SuperdeepTrap.cs:512,606) | KEPT | save bug in RM_SuperdeepTrap; independent, but P7 edits the same file |
| `FLOWWORKS_PLAYTEST_CAMPAIGN_1` | proposed | FlowWorks bugs via new test methods + rich-screenshot art pre-review; method-per-bug-class data | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `FLOWWORKS_QUARRY_DIGGING_1` | validated | Design pass: extend FlowWorks with the quarry concept - digging a canal can uncover local materials (local ... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `FLOWWORKS_REACTOR_FIX_STUCK_ENDS_SHIFT` | built | FlowWorks: return where continue intended, later reactions never run (RM_LiquidReaction.cs:187-191) | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `FLOWWORKS_RIVERCOLOR_FIX_DICT_SELF_ENUM` | built | FlowWorks: path compression writes parent[] while enumerating parent.Keys (RM_RiverColors.cs:160) | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `FLOWWORKS_VISUAL_PRINCIPLES_1` | validated | FlowWorks look: owner's five visual rules (deep cuts as walls, dirt/stone faces, moving water, tar as liqui... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `FLOW_CONTROLS_BUILD_EIGHT_QUIET_PEBBLES` | doing | Dev map controls (FlowWorks): flow meter, level holder, timer switch, map-edge setter, current painter, liq... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `FLOW_ORDER_EXTERNAL_INPUT_1` | built | FlowWorks: Flow order for sourceless (pump/drill/rain-fed) channels and >6000-cell networks | KEPT | owed rows stand but re-run after P3 replaces the still-water kernel path (noted) |
| `FLOW_SOURCE_SINK_BUILD_TAPS_FOR_MAPMAKERS` | doing | FlowWorks dev-placed Source and Sink objects (any liquid, set rate; minimal look; not buildable) for map ma... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `FLUID_PALETTE_EXHAUSTION_MEND_KEY_ZERO` | validated | FlowWorks P7 (GPT G3.6): an exhausted fluid palette returns key 0, so a cell's fluid identity silently chan... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `FORGE_CYCLE_MECHANICS_1` | doing | Build the Forge fire-and-water grand cycle: gas-wash ignition, boiling rain + FlowWorks flooding, steam plu... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `GLOW_TANK_LIQUID_FEED_1` | validated | LP-2: glow tank drinks salt or boiling water from a FlowWorks pipe network; settings toggle 'tank needs water' | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `HAZARD_TAR_TERRAIN_FROM_LIQUIDS_1` | built | EH-5: hazard code reads tar terrains from FlowWorks liquid defs, not literals | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `HEAT_BUDGET_PREFIX_MEND_LATE_CELLS_STARVE` | validated | FlowWorks P9a (GPT G3.8): the liquid heat budget is spent from the start of the list every interval, starvi... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `HOSE_JOINTS_REDESIGN_PUMP_TOO_PUNY` | doing | Liquid connection visuals: pump heftier than the hose, hose diameter a bit thinner, visible connectors wher... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `HOSE_LAY_POLISH_CENTRE_VS_MOUTH` | proposed | FlowWorks: hose lay edge cases (centre vs mouth range, refused feeder, bend radius) | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `HOSE_PATHING_REPAIR_SCENIC_ROUTE_PLEASE` | proposed | Hose routing should prefer bare ground around a hose reel over passing through it (water-scene S3: pond los... | KEPT | water-scene S3 hose-reel path loss; independent bug |
| `HOSE_RULINGS_BUILD_THREE_REVERSALS_ONE_CARD` | validated | FlowWorks: enact the 2026-10-11 hose-port reversals - rigid universal pipe with wire-style art picker (#1, ... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `HUTT_SLAVE_PIT_TEST_SITE_1` | built | Hutt slave pit at a small stand-alone test site: sell slaves, prisoners and downed beasts for silver; seale... | KEPT | its D=4 oubliette is Superdeep, which stays a constant |
| `LAVA_LIQUID_BUILD_PROMISED_BY_CARD` | validated | FlowWorks: add the lava liquid the owner promoted by card 2026-09-24 (missing from the liquid registry); se... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `LIQUID_BOTTLE_LOOP_1` | built | Bottles as real items: fill/use/dirty/wash loop (dirty behind a toggle, default ON), revert-on-bottle for b... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `LIQUID_CONTAINERS_REDRAW_NO_MANA_POTIONS` | doing | Bottles, buckets, barrels: four tech styles each (Junker oddly shaped, Industrial generic water bottle, Mod... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `LIQUID_INDUSTRY_SETPIECES_1` | validated | Found industrial liquid works via the shared scatterer: desal, detox, tar refinery, pumping station — wreck... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `LIQUID_LEDGER_BUILD_NO_UNIT_LOST` | validated | FlowWorks liquid networks L1-L3 (design/RimMandrake/liquid_network_semantics_design_2026-10-11.md §6): one ... | KEPT | conservation service; P3 keeps it (now decilitres) |
| `LIQUID_LOOK_MATERIAL_OWNERSHIP_1` | built | FlowWorks: Liquid looks own their materials | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `LIQUID_THIRST_CHAIN_1` | built | Water cleaning chain crude/household/industrial wired to DBH thirst (DBHThirst MEASURED in frozen dump); gr... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `MISSION_TANK_GOAL_REWIRE_TO_DEST` | built | FlowWorks P14 (GPT G6.5): the machinery player mission's goal accepts ANY filled tank (northstar/player_mis... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `MODCHECK_SETUP_UNMEASURED_FIX_READS_AS_FAIL` | proposed | modcheck runner.py ~529-538 records any chain-SETUP ExpectationFailed as FAIL + finding, ignoring an 'UNMEA... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `NATURAL_HEAT_CACHE_PROVE_STALE_DAYS` | validated | FlowWorks P9b (GPT G3.9, hook unverified): the natural-heat cache trusts terrain for 15,000 ticks after it ... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `PIT_LADDER_REDRAW_HUNG_ON_THE_WALL` | doing | Pit ladder mounts on a pit wall like a door (placed on the edge, faces into the pit), with a slid-up state ... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `PIT_LIP_FIX_BOAR_HANGS_OUT` | built | Pit near-lip occlusion: a pawn lying (asleep/downed) in a pit's southern cell draws over the south lip inst... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `PIT_LIP_OCCLUDES_OUTSIDE_1` | built | Pit-lip occlusion quad paints ground over a pawn standing OUTSIDE the pit (Muffalo south of pit, owner-spot... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP` | doing | Relative climbing core: climb-limit bands, StepAllowed math + selftests, cached per-band pocket grid replac... | KEPT | built offline; P2 discharges its live climb proof |
| `PIT_SPIKES_SHRINK_HALF_A_MAN` | doing | RM_Spikes art fills the whole pit cell vertically; redraw: spikes about half a man tall, mostly pointing up... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `PIT_SUPERDEEP_COLLAPSE_1` | doing | Collapse the pit onto the D/F primitive: a superdeep cell you cannot climb out of, a room for prisoner stor... | KEPT | stays open; P2 discharges its live proof; Superdeep (4) stays a constant separate from the dig cap (P5) |
| `PROPANE_CANAL_WIRE_STILL_NO_FLUID` | proposed | Propane has no canal FluidDef, so a propane tank cannot fill a cut | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `RIVERCOLORS_MERGE_RAINBOW_JOINS_THE_FLOW` | proposed | Merge RiverColors (mandrake.rut.rivercolors) into FlowWorks as part of adding liquids to the world; retire ... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `RIVER_STEAM_ANIMATION_1` | built | Animated steam rising from the rivers (Pyrelands weather visual) | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `RIVER_TOGGLE_PROOFS_BUILD_ELEVEN_UNCLAIMED` | built | FlowWorks rivers: prove the 11 river settings toggles owed in validation.py, and the 10 untested river-walk... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS` | proposed | Zoom in on river-works art (weir, stakes, silt trap, ferry, fords) and hose connections (tank, pump, reel s... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `SETTINGS_KIT_BUILD_GREY_SWITCHES_AT_LAST` | built | Settings kit: master-switch greying of dependents + Reset-all-to-defaults (confirmed); wire GSS + Pyrelands... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `SLIME_CROSSING_BUILD_SLIPPERY_SLOPE` | doing | FlowWorks slime: nearly uncrossable and slow to climb out of (owner: 'so slippery it is nearly uncrossable'... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `SLUICE_GATE_REWIRE_TURNS_LIKE_A_DOOR` | doing | Sluice gate and every canal water-blocking structure auto-rotate after placement like vanilla doors (orient... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `SPRINKLER_HEADS_BUILD_PUMP_REQUIRED` | doing | Build sprinklers per design/RimMandrake/sprinklers_design_2026-10-16.md (ruled): native pipe head + VFE ada... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `STATION_REACH_CENTRE_RETHINK_FOOTPRINT` | validated | FlowWorks P11 (GPT G1.22, note): a pumping station's reach is measured from its position, not its footprint... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `SURFACE_RIVER_WEIRS_1` | validated | Port the weir / bank-works / breach system to ordinary surface river tiles (owner-typed 2026-09-26): weir, ... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `SWALE_CANAL_ART_REFERENCE_1` | doing | Swale art from live reference: build a real FlowWorks canal in game, screenshot it, spec the RM_Swale art f... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `TANK_LOOKS_WIRE_FOUR_STYLE_SWITCH` | doing | FlowWorks tanks (liquid tank, universal cargo tank, etc.) get the four-look style switch like hose reels an... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `TANK_TALL_BUILD_TWICE_THE_DRINK` | doing | Tall variants of RM_LiquidTank and RM_UniversalCargoTank: same footprint, double the storage (160 / 320 uni... | KEPT | tank sizes; read 'units' as litres after P4 |
| `TAR_COOLING_GLASS_MEND_ENGINE_CELLS` | validated | FlowWorks P6b (GPT G3.5): tar cooling writes glass onto cells the depth engine owns (Flood_FlowWorks.cs ~37... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `TAR_LOOK_TUNE_THICK_AND_SLOW` | doing | Tar surface: water ripple plus a thick, slow, glossy look, tuned live with the owner; needs a live look-tun... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `TESTENV_FLOODS_HARDEN_SEASON_CRASHES_PARTY` | built | 'Seasonal flooding' ThreatSmall letter on the FlowWorks river site map during extension_proof (04:29Z): sto... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `TESTENV_HIVES_HARDEN_RIVER_MAP_SQUATTERS` | built | FlowWorks river_site map carried a dormant insect Hive + GlowPod (vitals threat_structure, 04:28Z) during e... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `TESTENV_MEGAPEDE_HARDEN_GATECRASHER` | built | Test environment: a VFEI2_Megapede + 3 Spelopede (Insect) arrived on the FlowWorks golden site mid liquid_h... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `TESTENV_TRIALSITE_DIAGNOSE_NOBODY_HOME` | built | Test environment: NS_FlowWorks_TrialSite_v1 on ratchet_pilot+patches loads with NO living colonist on the c... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY` | doing | FlowWorks gets its own drinking bottles and its own thirst need (design first); when Dubs Bad Hygiene Lite ... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `THIRST_DESIGN_SLIME_IS_THE_LAST_RESORT` | proposed | 3x3 deep design pass: thirst, every fluid type, gathering/storage/access, health, jobs, crop watering, mach... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
| `THIRST_RULES_BUILD_SALT_OFF_THE_MENU` | proposed | Build the ruled thirst/fluid rules: first fix today's two rule breaks (auto-fill gathers any liquid; thirst... | KEPT | independent of depth and water level; no 2026-10-17 ruling touches it |
