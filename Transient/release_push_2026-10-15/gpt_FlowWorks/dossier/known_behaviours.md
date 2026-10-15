# FlowWorks known behaviours and past bugs (auto-extracted heads of ledger item files, 2026-10-15)

OPEN = live work (head of infrastructure/state/items/<ID>.md); CLOSED = done/dropped items kept for the bugs they record. Heads are truncated.


## OPEN EXCAVATION_LOAD_SANITY_REPAIR_1 — FL-3: Excavation grid sanity repair on load and palette compaction
## spec
Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` row FL-3 (belt hygiene pass 2026-10-09; items/ live+closed and src/ re-checked: not filed, not built). The row is the spec:
| FL-3 | Robustness: on load, check that the dig map makes sense. Depth must be 0–4, liquid must not exceed depth, and each liquid must be a known one. Repair anything wrong with one logged line instead of silently zeroing a wrong-sized grid. Also drop removed liquids from the per-map liquid list, so a long campaign never runs out of its 254 slots. | PostLoadInit pass in RM_MapComponent_Excavation, plus palette compaction and remap. Add selftest cases with a corrupted grid. | S | low | FlowWorks | `EnsureGrids` (RM_MapComponent_Excavation.cs:210) silently reallocates a wrong-sized grid. `PaletteKey` (:253) returns 0 once 254 is reached and never compacts. There is no clamp or repair on load (grep sanit/clamp/repair). Not in EXCAVATION_LEGACY_MIGRATION_FLAG_1, which only covers legacy rehydration. |
Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; PatchApplier for any Harmony.
## verify
- Offline: Selftest with corrupted grid passes: depth clamped 0-4

## OPEN EXCAVATION_WALL_ART_1 — Wall-face art for all four depths, spikes and ladder (Quarry perspective)
Part of the pit collapse (`PIT_SUPERDEEP_COLLAPSE_1` carries the rulings; `design/RimMandrake/flowworks_pits_unified_model_2026-10-02.md` is the one model). A pit is a canal cell dug to SUPERDEEP (D=4) and nothing else.
## spec
Rulings 19/33 + the depth ruling: every depth legible and different; depth read from the wall faces in Quarry's perspective; the camera angle must let some spike show. Shared rim + per-depth wall gradient (the cheap layered approach). Also: `RM_Spikes` art (D=4 only — owner Q2, 2026-10-02 — so no spike art at D 1-3) and `RM_Ladder` art; no `TrapSpikeArmed` anywhere. **Search artpipe state and review-sheet decisions first** (`artpipe_state.py find`) — art may already exist.
## verify
Offline contact sheet of D=1..4 dry + one fluid; owner review sheet; deployed textures resolve (no magenta).
## criteria
`pit_depth_ladder_legible`, `pit_reads_as_hole`, `spikes_read_distinct`, `never_reads_as_building` can pass.
## depends
Can start now (art), wires after `CANAL_BOTTOM_SPIKES_1` / `LADDER_PRISON_DOOR_1` exist.
## northstar
Frame-judged bars only; the state side is the texPath census in O1.

## OPEN FLOWWORKS_BUILD_PROGRAM_1 — one liquid mod, built on depth
Filed by BENCH 2026-09-16 from a full bench design session with the owner. **Read
`design/RimMandrake/flowworks_mod_definition.md` first** — it carries all 27 of his rulings from
that date, each traceable to his words, plus the measured facts about the existing code. This item is
the build order, not the design.
Supersedes `FLUIDITY_MOD_CONSOLIDATION_1`. Absorbs the scope of `FLUID_SOURCE_STOCK_MODEL_1`,
`CANAL_CONSTRAINED_SPREAD_1`, `LIQUID_SINK_DRAINAGE_1`, `CANAL_FILL_IN_DISPLACEMENT_1` and
`CANYON_FLOOD_ERASES_CANALS_1` as phases — those stay filed as the trackable units.
## The one-paragraph version
**FlowWorks** is one mod owning the whole liquid domain, built on a single primitive: an **excavated
cell with a depth**. Depth is the only Z-level in the game, and it is what makes liquid behaviour
possible. Every excavated cell carries `depth` D (0=surface, then shallow/mid/deep/SUPERDEEP) and
`fill` F, with `0 ≤ F ≤ D`. Crossing cost, capture, escape chance, capacity, drawn terrain and
climb-out all read from those two integers. Canals, pits, terraces and dig sites stop being types and
become *shapes*. Liquid moves by a **sort plus an overflow** at pulse boundaries — never a simulation.
## 🔴 Two laws that bound the s

## OPEN FLOWWORKS_CHECKOUT_SCOPE_1 — ordinary FlowWorks features sit outside the basic checkout
Found by the 2026-10-06 northstar review (`design/RimMandrake/northstar_review_2026-10-06.md` finding 7, GPT action 7),
CONFIRMED by reading the walk:
1. **Scope.** The walk's step 4 puts doors, spikes, ladders OFF, the superdeep prison room + capture down + lip service,
   the pump, bottle revert, wall faces, dig finds, bottles/tanks/drilling, shores, river steam and fire extinguishing in
   `extension_proof.py` "on request, never by the core proof". The owner's 2026-10-04 ruling (debug_process §6b) reserves
   "extended" for mod-mod compatibility, declared incompatibilities and removal — not ordinary Utinni-play features. So a
   green core proof (59/59 PASS, `validation_v2_result_20261005T232201.json`) says nothing about those features.
2. **Coverage arrows.** The walk's five `## must be true` lines carry no `→` arrow (§2.3). Proposed mapping, from the
   59 row ids of tonight's result — UNVERIFIED, check each against the row's predicate before writing it:
   - designation + colonist digs → `E8_player_dig`, `J_workgiver_selection`, `J_orders_accepted`
   - D=1..4 terrains → `S1_dig_ladder`, `S1n_superdeep_is_max`
   - channel-constrained spread, default on → `E2_dry_ring`, `E2_channels_fi

## OPEN FLOWWORKS_CONTAINER_MATERIALS_1 — bottles and barrels are made from a material the player picks
Filed by BENCH, 2026-10-06, on the owner's typed ruling (23:28), answering what to do
about the glass-bottle render that contradicted his patchwork-metal brief (386d51170):
> "Player can set what kinds of bottles they use (leather, glass(any stone), metal)
> depending on what they have in abundance and what crafting stations they have.
> Barrels are like this too: wooden, metal, plasteel"
## spec
Vanilla-native: the bottle and barrel families are **stuffable** (one def per state,
material carried as `Stuff`), and each material is its own RecipeDef at the stations
that material belongs to, so what a colony can make follows its benches:
| container | material (stuff) | recipe | stations |
|---|---|---|---|
| bottle | leather (Leathery) | `RM_Make_Bottle_Leather` | crafting spot, hand/electric tailoring bench |
| bottle | glass, from any stone block (Stony) | `RM_Make_Bottle_Glass` | stonecutter's table, electric smelter |
| bottle | metal (Metallic) | `RM_Make_Bottle_Metal` | fueled/electric smithy, machining table |
| barrel | wood (Woody) | `RM_Make_Barrel_Wood` | crafting spot |
| barrel | metal (Metallic, not plasteel) | `RM_Make_Barrel_Metal` | fueled/electric smithy |
| barrel |

## OPEN FLOWWORKS_LADDER_RAISE_LOWER_1
Owner, 2026-10-06 21:40, typed into a question card (verbatim):
> Ladders should be able to be raised and lowered (two states for the ladder). Someone needing to enter the pit from
> the top will descend the ladder and access the contents. The ladder should be clickable by the user: ladder up,
> ladder down. No need to have the colonists automatically move them up and down.
## spec
- `RM_Ladder` gets two states, raised and lowered, toggled by a player gizmo (ladder up / ladder down). Colonists never toggle it themselves.
- Lowered: pawns may path down into the pit and back out by it; haulers can fetch items lying on the pit floor (Explosive Knockback throws items and corpses into pits).
- Raised: nobody climbs it; a held pawn cannot escape by it (existing hold/ladder-release behaviour keyed to the lowered state).
- Each state needs its own art (art commission 2026-10-06 queued the ladder; add a raised variant).
- Runner scenes: toggle both ways via the gizmo; a hauler fetches an item from the pit floor only when lowered.

## OPEN FLOWWORKS_NORTHSTAR_GREEN_FULL_1
Parent: `FLOWWORKS_NORTHSTAR_TRIAL_1`. Plan: `design/RimMandrake/northstar_trials/FlowWorks_trial_plan.md` §4. Gated on GREEN_MINIMAL.
## acceptance
- Same suite, same preflight, on the owner's full list after a cold load (~15 min MEASURED 2026-09-07 on 599 mods).
- `modcheck status FlowWorks` = GREEN; his list restored byte-identical afterwards.

## OPEN FLOWWORKS_NORTHSTAR_GREEN_MINIMAL_1
Parent: `FLOWWORKS_NORTHSTAR_TRIAL_1`. Plan: `design/RimMandrake/northstar_trials/FlowWorks_trial_plan.md` §4.
Gated on: REVALIDATE, WIRE, SITE_PREP, BASELINE_RUN, plus the art and mechanics the validated bars need
(plan §1 ruled-vs-built table and §5). A RED run never closes this item.
## acceptance
- A passing run on the `flowworks` tier, preflight clean; `modcheck status FlowWorks` = GREEN.
- Owner reviewed the sheet once (`record_owner_review`).

## OPEN FLOWWORKS_NORTHSTAR_SHIP_1
Parent: `FLOWWORKS_NORTHSTAR_TRIAL_1`. Plan: `design/RimMandrake/northstar_trials/FlowWorks_trial_plan.md` §5.
## acceptance
- `code_review_status.py check` over `git ls-files src/RimMandrake/FlowWorks`: 0 DIRTY (12 DIRTY of 129 on 2026-09-30, listed in plan §1).
- Mod Settings superb per the 2026-09-12 ruling: grouped by phase, worldgen-affecting toggles labelled
  (`typedLiquidShoresEnabled`), defaults = shipped, an all-off component proving the mod still digs dry channels.
- Art for every visual bar; no def on `Things/Building/Security/TrapSpikeArmed`.
- `deploy_custom_mods.py --mod FlowWorks` in sync; DLL `.srchash` matches.
- `FLOWWORKS_DOOR_FAMILY_1` and `PIT_SUPERDEEP_COLLAPSE_1` closed, or their bars parked by his word.
## offline audit (FOUNDRY flowworksA, 2026-10-05) — state, not a verdict
- **Code review:** `code_review_status.py check` over tracked FlowWorks files (150, excluding .png/.dll/.srchash/bin/obj): **88 DIRTY, 62 CLEAN** — 38 `.cs`, 23 `.xml`, 10 `.py`, 14 `northstar/validation_v2_result_*.json` run captures (derived output; review cannot make them meaningful — candidates to untrack rather than review), 3 other. Includes today's Phase 6 / fluid-identity / fill-effects files (never marked). Acceptance (0 DIRTY) is far off; needs f

## OPEN FLOWWORKS_NORTHSTAR_TRIAL_1
Parent of the FlowWorks north-star trial. Plan (authority for every child): `design/RimMandrake/northstar_trials/FlowWorks_trial_plan.md` — bars and bindings
(§2), site preparation and preflight (§3), run sequence (§4), SHIPPED gaps (§5), driver requirements
(§6), proposed bar text (§7), GPT review (§9; prompt/answer in `Transient/northstar_trials_gpt/`).
Owner, 2026-09-30 (typed): *"Write out comprehensive northatar plans for all three and ticket them out
as trials for full completion. Use gpt reviews for their validation plan especially site preparation
that's often overlooked before a proper test setup. I'd like this to go very well. Then use ultra fast
python to drive the bridge to validate. Make it happen!"*
## children (ladder order)
1. `FLOWWORKS_NORTHSTAR_REVALIDATE_1` — VALIDATED again, with the pit bars folded in (BENCH, owner sitting).
2. `FLOWWORKS_NORTHSTAR_WIRE_1` — WIRED.
3. `FLOWWORKS_NORTHSTAR_SITE_PREP_1` — golden site + preflight.
4. `FLOWWORKS_NORTHSTAR_BASELINE_RUN_1` — first live run (RED expected).
5. `FLOWWORKS_NORTHSTAR_GREEN_MINIMAL_1` → 6. `FLOWWORKS_NORTHSTAR_GREEN_FULL_1` → 7. `FLOWWORKS_NORTHSTAR_SHIP_1`.
Depends on the shared driver at `src/RimMandrake/Utils/northstar_driver/` (another agent builds it; §6 lists the call

## OPEN FLOWWORKS_PLAYTEST_CAMPAIGN_1 — find and fix FlowWorks bugs with the new test methods; learn which method fits which bug
## direction (owner, 2026-10-06, typed in BENCH chat)
*"This is now your #1 priority. See how far you can get on FlowWorks. You may also go back and experiment on Gimme Some Slack as another interesting trial of the different methods. It almost feels like we need all three approaches (plus Northstar still perhaps?) as four different methods for four diferent classes of bug/testing. But that is not my ruling, it is my question. I would love to gather data to inform that question and find the right ways forward. Please don't go down deep rabbit holes chasing very time-expensive statistics, however. It's much more important to make progress finding and fixing bugs, revealing actual gameplay functionality, and building out the mods to their fully functional state. Please also include concepts for SOME art review. Pre-working some art review before the human's check is pretty important. And there it feels like taking very rich screenshots that can test MANY items at once and be segmented down into individual checks MIGHT be a way forward. That's a whole new thrust for you to explore for efficiency and problem discovery. I authorize thinking/planning/designing/impl

## OPEN FLOWWORKS_REVIEW_LOOKS_ROUND_1
Owner's review of the fresh FlowWorks review map (`RM_fw_review_20261006b`), 2026-10-06 ~19:00, typed mid-turn
(verbatim):
> Reviewing FlowWorks sheet: Dirty Oil looks EXCELLENT in the pit. Dirty slime as well. Scorched dirt and stone
> doesn't look like anything at all, it needs blast marks and blackened bits. The Stone Tar looks oddly blue. It
> should not be blue, it should be dark grey no matter what. Not transparent. Dirt tar should look the same as stone
> tar. I'm seeing strange words in the description like flooded channel and excavation pit. We should just list the
> water by depth, just like it does for riverbanks and shores. Deep, shallow, etc. Need many more of the fluids online
> here. Blood. Chemfuel. Astrofuel. White slime. Red Slime.
## Work
1. KEEP: dirty oil and dirty slime pit looks (approved).
2. Scorched dirt / scorched stone: add visible blast marks and blackened patches.
3. Tar: dark grey, never blue, opaque — on stone AND dirt alike (supersedes the 2026-10-06 mid-grey tint 0.58,0.56,0.60 where it reads blue/transparent).
4. Inspect/label text: drop "flooded channel" / "excavation pit" wording; name water by depth the way vanilla riverbanks and shores do (Deep / Shallow …).
5. More fluids online on the review map and in the

## OPEN FLOWWORKS_SETTINGS_WIRE_AFTER_TANKS
Filed by BENCH 2026-10-14 from SETTINGS_KIT_BUILD_GREY_SWITCHES_AT_LAST (kit built at e21f179c3c, GSS and Pyrelands wired).
FlowWorks C# was being edited by another agent, so its wiring was written down instead of done.
## spec
Follow `infrastructure/state/items/SETTINGS_KIT_BUILD_GREY_SWITCHES_AT_LAST.md` section "FlowWorks wiring owed" (steps 1-5:
csproj links, Masters/Get/Set/Dependent helpers, Reset all, candidate masters to confirm at their read sites).
## criteria
- A1 L0: settings_audit.py shows FlowWorks masters "declared"; selftest_settings_screens.py all ok; FlowWorks DLL stamp MATCH.
- A2 L1: in the FlowWorks settings window a master off shades its dependents and keeps their values; Reset all asks first.

## OPEN FLOWWORKS_VISUAL_PRINCIPLES_1 — the owner's five visual rules for pits and liquids
Owner, 2026-10-05 (verbatim): *"Principle 1: The canals, when dug deep enough to hold a man, should have the
same perspective appearance as the walls do when viewed from above (tall enough to stop a man). The deeper
canals should be even more extended in appearance. 2: the walls should look like either dirt or stone,
depending on the terrain beside them. 3: When filled with water it should move and act like water (ripples,
V waves, etc.) not just be solid coloration. 4) Tar should not simply be solid black, because that just looks
like the burned surface after a fire. It should look like black liquid. 5) The burned pit must look like an
empty pit that is scorched, not just a black surface or a normal pit."*
## spec
Drawing only — no flow, fire or pit mechanic changes. Every feature has a Mod Setting; off = the flat look.
1. **Depth perspective** — `RM_WallFaceMath.NorthByDrop` D1 0.10 / D2 0.18 / D3 0.30 / D4 0.50 cells,
   side faces 0.04/0.07/0.12/0.18; lit face + dark rim + contact shadow (`SectionLayer_RMExcavationWalls`).
   Near-lip occluder `RM_PitLipOcclusion` hides the part of a sunk pawn below the near bank.
2. **Material** — `RM_FaceMaterial`: the face is the neighbour ground's own ter

## OPEN GLOW_TANK_LIQUID_FEED_1 — the GlowTank drinks from the pipe network
Source: `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` row LP-2 (owner card 2026-10-08: queue all batches).
Spec: `design/RimMandrake/deepfire_luminous_pigment_spec.md` §2.5 (Q5 2026-09-25: salt or boiling water only).
## what
Built at `041c0142b`. Checked first: the tank header and `Building_GlowTank.cs` said the water gate was not built,
and the reason ("no way to carry a liquid") no longer holds — FlowWorks ships `RM_LiquidNet.TanksFor` and
`Building_LiquidTank`.
- With FlowWorks loaded and "Tank needs ocean water" on, the tank draws one unit of `RM_Liquid_SaltWater` or
  `RM_Liquid_BoilingWater` from a liquid tank adjacent to it or on a hose run touching it, by reflection
  (`FlowWorksWaterBridge`, soft-hook convention: no assembly reference, no modDependency).
- `RM_GlowTankWater` kernel: a reserve of up to two units, drained while running, refilled at half a unit. Fuzzed
  (`LuminousPigmentFuzz` family `water`).
- Dry: the crop's growth pauses (Harmony postfix on `Plant.GrowthRate`, cultured crowncarpet in a GlowTank only).
  Nothing dies of thirst. The inspect string says dry / hours in reserve / "not needed (FlowWorks not loaded)".
- Mod Settings: toggle + units per day (0.5–20). Without Flo

## OPEN HAZARD_TAR_TERRAIN_FROM_LIQUIDS_1 — EH-5: hazard code reads tar terrains from FlowWorks liquid defs, not literals
## spec
Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` (remaining rows, helper pass 2026-10-09; owner 'Queue all' card 2026-10-08). Row EH-5 there is the spec; its 'Checked' column says what was read to confirm it is unbuilt. Re-check src before building.
| EH-5 | **Generic hazard code stops hard-coding campaign terrain (hygiene).** The tar beast, the tar-pit belch and the Sump living map name `"RM_TarDeep"`/`"RM_TarShallow"` as literal strings. Read the tar terrains from FlowWorks' `RM_Liquid_Tar` entry, or from a def field, so a second tar liquid or a renamed terrain cannot silently break them. | small refactor | S | low | EnvironmentalHazards, FlowWorks (read-only) | `RM_CompTarBeast.cs:140`, `RUT_IncidentWorker_TarPitBelch.cs:98`, `RM_MapComponent_SumpLivingMap.cs:96`; `FlowWorks/Defs/LiquidTypes/LiquidDefs/RM_LiquidDefRegistry.xml:324` already maps tar to `RM_TarShallow` |
Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; names follow the three-tier scheme.
## verify
- Offline: build clean; RM_MapComponent_SumpLivingMap.TarShallow/TarDeep resolve from LiquidDef RM_Liquid_Tar.terrainSuite (fallback to the name

## OPEN HOSE_RULINGS_BUILD_THREE_REVERSALS_ONE_CARD
Rulings #1, #2, #3, #8 of `design/RimMandrake/gss_flowworks_rulings_2026-10-11.md`.
## state
- **#1/#8 rigid pipe, looks half — built 830f2c8d0.** `RM_UniversalPipe` (defName kept; old `RM_LiquidHose` saves alias
  to it) is the rigid pipe; the flexible line is the hose reel's hose and keeps the name "hose". Four looks
  (Scrapper/Industrial/Modern/Futuristic) through the shared `_Shared/StylePicker/StylePickerCore.cs` (FlowWorks instance
  `Source/Machinery/PipeLook.cs`), `RM_UniversalPipe_<Look>` Basic-linked ThingStyleDefs, "Choose style" for one pipe or
  its run, `pipeDefaultLook` setting. Owned atlas art: art subagent, `RimMandrake/FlowWorks/Pipe/<Look>/` (placeholder =
  tinted vanilla conduit atlas). Absorbs the duplicate RIGID_PIPE_BUILD_WIRE_STYLE_PICKER.
- **#3 text half — built.** A hose end in water reads "lying in <water> (no intake: filling a tank takes a pump)"; the
  reel's inspect names its free end and the faction of a coupled tank; the dev flow gizmo no longer says "no pump yet".
  Audit: no free intake path into any tank exists (every TryAddLiquid caller is a pump, machine output, adapter, hand
  pour, ruin stock or the ruled tank->hose feed). Nozzle intake (hose-port step 9) stays unbuilt.
- **Flow half built und

## OPEN HUTT_SLAVE_PIT_TEST_SITE_1 — the Hutt slave pit, at a small stand-alone test site
## spec
Authority: `design/RimMandrake/ship_cargo_hoist_design_2026-10-01.md` §3a and §5 row 3 (RULED). A small stand-alone Hutt site (not Gorga's Palace) with a `RUT_` cast
and a fixed `RM_HoistFrame` over the pit.
- **Sell for silver:** slaves, unenslaved prisoners, and knocked-out beasts, tame or not. The player's own pawns
  walk them to the hoist and lower them. Silver comes up. Price multiplier in Mod Settings.
- **The oubliette:** a sealed map feature holding slaves. Nobody enters it. **Only the ship's hoist can lift them
  out, and only after the site is attacked and taken** (owner, verbatim in the doc §1b).
- **Arena offstage:** hinted at only in pit prices and letters. A visitable arena is a later, separate build.
## criteria
- A peaceful landing, a sale of each of the three cargo kinds, and silver received.
- The oubliette is unreachable while the Hutts hold the site, and liftable by the ship's hoist after conquest.
## Watch out
- This site's **oubliette** is a sealed map feature, not the pit "oubliette fitting" the owner CUT on 2026-09-17
  (`PIT_SUPERDEEP_COLLAPSE_1`). With FlowWorks it is simply an enclosed superdeep (D=4) room with no ladder:
  nobody climbs out by rule (`design/Rim

## OPEN LIQUID_BOTTLE_LOOP_1 — bottles as real items: fill, use, dirty, wash + special behaviors
Filed by BENCH, 2026-09-13 (`design/RimMandrake/liquids_framework_design.md`
§4 "Bottles are real items" + "Special behaviors").
## spec
Bottle chain: `RM_BottleEmpty` → fill job (terrain edge or tank) →
`RM_Bottle<Liquid>` (generator-emitted per row) → use → `RM_BottleDirty` →
wash job (consumes water) → empty. Buckets = larger bottle, same chain.
BARRELS too (owner-ruled 2026-09-13, "very scavenger"): ~25-unit big sibling,
same chain plus fill/empty bills at a tank; barrels are the vanilla-native
bulk trade route — every trader buys/sells them with zero patches.
Dirty stage behind a Mod Settings toggle, default ON in the campaign; off =
use returns a clean empty. Special behaviors as row data, no per-liquid C#:
revert timer (bottled boiling/icy → fresh), rot (bottled blood via
CompRottable; household recipe → hemopack before spoil). Bottles carry
cuisineTags ThingCategories so the future RSW cuisine mod cooks against tags,
never defNames. Blood is item-only in v1 — no blood terrain.
## verify
Quicktest: full loop observed (fill from a shore, drink, dirty appears, wash
returns empty). Timer checks: a boiling bottle becomes fresh; a blood bottle
rots on schedule and the hemopack recipe beat

## OPEN LIQUID_LEDGER_BUILD_NO_UNIT_LOST
Spec: `design/RimMandrake/liquid_network_semantics_design_2026-10-11.md` rev 2 (2dafd0502), §6 L1-L11; owner cards Q1-Q5
ruled 2026-10-11 (Q1 "Hose ends + tank jobs", Q2 real held volume + cleanable spill, Q3 pump pour = fast drain for Dump
tanks, Q4 theft priced like power theft).
## built (offline, all pushed; SelfTest 267/267, hose 342/342, 16/16 python selftests)
L1 7432ac095a transfer service · L2 12f1b314c7 components per revision · L3 9d727a3b22 fill/draw order · L4 25d272ff93
tank jobs + settle (tanksFeedHoses -> tankModesEnabled) · L5 9163cd3d76 free-end roles · L6 fe13508b7a pump as world mover ·
L7 5b9a704357 outflow ends + Dump drain · L8 8ec0dbef2a held volume + spill · L9 e329b72036 liquid theft · L10 5ce7f4aae3
adapter modes · L11 a341da28fa perf fixture (0.00016 ms mean, 0.11 ms worst offline).
## criteria
- A1 L0: C# SelfTest 267/267 + hose 342/342 + 16/16 FlowWorks python selftests at a341da28fa.
- A2 L2: lake -> pump -> hose Outflow -> disconnected canal fills with no tank (NS_canal_from_lake_no_tank).
- A3 L2: a Dump tank drains out an Outflow end with no pump (NS_dump_tank_drains_without_pump); a pump on Pour drains it fast.
- A4 L2: an Intake end in a pond moves nothing without a pump (NS_intake_needs_pump); pond round trip

## OPEN PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP
Spec: `design/RimMandrake/relative_depth_climb_design_2026-10-12.md` §8.1-8.3, §8.5 steps 1, 4, 6-9, §8.6 (build item 1 of
three in §8.7). Owner rulings: §10 there, 2026-10-12. Unblocks `POND_BED_BUILD_HOLLOW_KEEPS_ITS_SHAPE` step 2.
## state (BENCH, 2026-10-13) — built OFFLINE, live climb proof owed
Nothing was deployed and the bridge was not touched (a live driver held the game).
**Built (FlowWorks, behind the new Mod Setting `pitRelativeClimbEnabled`, default ON; OFF = the old absolute D 4 rule,
whose code paths are kept verbatim):**
- Math, selftested (`RM_PitTrapMath`): `ClimbLimit` (band edges on body size 0.75 / 1.65 / 3.0 → K 1/2/3/4, scaled by
  `pitClimbAbilityMultiplier`, + `RM_ClimbAbility` extra levels), `StepAllowed`, `DiagonalAllowed`, `StepCost` (slow climb
  at s = K ≥ 2, ramp 0, ladder per level; NOT yet wired into `RM_Patch_PitStepCost`, that is item 2), `ArrivalDropsTooFar`,
  `FallDropScale`, `HeldRelative`.
- Pocket grid: `RM_PocketGridMath` (pure labeller, no cell cap) + `Superdeep/RM_PocketGrid.cs` (per map, bands 1..3; K ≥ 4
  needs no grid). Depth-only (walls never stale it; vanilla reachability is ANDed). Covers read as ground. Generation
  `RM_MapComponent_Excavation.ClimbGeneration` moves on Deepen, FillIn, co

## OPEN PIT_RAMP_BUILD_STAIRS_BEAT_LADDERS
Spec: `design/RimMandrake/relative_depth_climb_design_2026-10-12.md` §8.2 (player text, modifiers), §8.4 (ramps, ladders)
— build item 3 of three in §8.7. Builds on `PIT_CLIFF_MASK_BUILD_ASTAR_LEARNS_WALLS` (masks, ladder joins).
## state (BENCH, 2026-10-14) — built OFFLINE, live checks owed; ART OWED (placeholder in place)
Nothing deployed; the bridge was not touched.
**Built (FlowWorks):**
- `RM_PitRamp` ThingDef (Structure menu, 25 wood/stone blocks, work 900, not an edifice, rotatable; rotation = uphill) with
  `RM_Building_PitRamp` (spawn/despawn bump the climb generation; inspect line says what it joins) and
  `PlaceWorker_PitRamp` (dug square or dry pond bed; must face a square 1..span shallower; never on a ladder; ghost marks
  the facing square). `RM_PitRamp.Joins` feeds the cliff masks, the step floor, the step cost (flat walk) and the pocket
  grid (`RM_PitRamp.Pairs` → `RM_PocketGridMath.Label`'s ramp joins) — structural, every band, enemies too.
- Ladders: join their square to ANY shallower N/S/E/W neighbour (item 2), each level costing "Ladder slowness" normal
  climbs. Placement now needs a wall (a shallower cardinal neighbour) and refuses a ramp square; a dry pond bed counts as dug.
- Mod Settings (Pits section): "Ramps" (`pitR

## OPEN PIT_SUPERDEEP_COLLAPSE_1
A pit is not a building. It is a SUPERDEEP excavated cell — depth 4 on the D/F
primitive that rulings 18 and 19 already established, and that ruling 19 already
called "the trapping level". This item carries the pit code and defs onto it.
## the ruling  (OWNER'S WORDS — verbatim, 2026-09-17)
Asked how to close the gap between rulings 18/19/24 and a pit that is still
`Building_OpenPit : Building, IThingHolderWithDrawnPawn` with its own parallel
depth ladder, he chose "rule it now" and said:
> *"If you're in a superdeep pit, you can't climb out. Period. Welcome to your
> pit. This defines a "room" if it's enclosed that you can use for prisoner
> storage. Should be a button to "jump into pit" and if you do, you are stuck
> there too. A ladder nearby can be pulled up or lowered to allow people out
> (like opening a prison door). Should work just like a prison cell mechanic.
> There is a reference prisoner mod we are subscribed to for inspiration here.
> Covering the pit allows people to fall into it involuntarily (or if they are
> somehow pushed or blasted into it, something that would move them normally
> against their will like weapon blowback). Most of the pit mod detail is no
> longer needed here unless it's just to install certain hardware in tine
> pit

## OPEN PIT_TEMPERATURE_SOFTENING_1 — Pit temperature couples hard to ambient and wears down resistance; Exposed Prisoner thought
Part of the pit collapse (`PIT_SUPERDEEP_COLLAPSE_1` carries the rulings; `design/RimMandrake/flowworks_pits_unified_model_2026-10-02.md` is the one model). A pit is a canal cell dug to SUPERDEEP (D=4) and nothing else.
## spec
- An unroofed superdeep room tracks outdoor temperature faster than a roofed room (multiplier at the seam measured in `SUPERDEEP_SEAM_MEASURE_1` item 5).
- Vanilla Heatstroke/Hypothermia do the harm; `RM_PitExposure` accumulates while exposed and lowers resistance (recruitment first) — two independent dials ([H]).
- **Exposed Prisoner** thought: compassionate pawns feel it; psychopaths and hard-morality cultures do not — copy the beggar-rejection structure, no new moral axis ([A-item]). Numbers and the exact def shape go to the owner with a proposal; never invent them as his.
- Mod Settings: on/off, coupling multiplier, resistance-loss rate.
## verify
Bridge: desert noon, unroofed pit vs roofed twin — the pit's temperature moves faster; an occupant's resistance falls faster in the pit than in a normal prison cell; a compassionate colonist gets the thought, a psychopath does not.
## criteria
"Letting them roast" measurably shortens cap

## OPEN RIVER_STEAM_ANIMATION_1 — animated steam rising from Pyrelands rivers
Owner, verbatim (2026-09-02): *"could we add animated steam rising from the
river? That is an amazing idea, file a ticket on that alone!"*
Thin item — FOUNDRY decision on spec/verify/criteria, 2026-09-02.
## spec
Pure ambience feature, no gameplay effect, no new art. `mandrake.rut.riversteam`
(RimUtinni tier — this names Ash'karr's Pyrelands specifically, per
`NAMING_SCHEME_PLAN.md`'s tier test).
`MapComponent_RiverSteam` (`src/RimUtinni/RiverSteam/Source/RiverSteamHook.cs`):
- MapComponent subclasses are auto-instantiated per map by `Map.FillComponents()`
  (`Verse/Map.cs:710`) — no Harmony patch or XML registration needed, confirmed
  by reading the real vanilla source, not assumed.
- Gates on `map.Biome.defName == "ZBiome_Grasslands"` — the Pyrelands' actual
  BiomeDef, per `ASHKARR_WORLD_DEFINITION.md`'s biome table ("stormy savanna").
  Every other biome's rivers stay silent.
  ⚠️ **Superseded, this original 2026-09-02 framing** — `PYRELANDS_WRONG_BIOME_DEF_1`
  (closed 2026-09-20) found the intended Pyrelands def is `RM_FE_Pyrelands`, not
  `ZBiome_Grasslands`, and which one carries the live tiles is UNRECONCILED
  against `world/ASHKARR_WORLDMAP_tiles.csv`. The engine is no longer hardcoded
  on this s

## OPEN SCALD_MECHANICS_1 — the Scald C# kit
## spec — the C# kit
Per `design/Jawa/worldbuilding/biomes/the_scald.md` (FROZEN,
`BIOME_FREEZE_FABLE_REVIEW_1`): steam-catch industry · margin fishing + bath
recreation · bubble-sailor and bottom-walker set-pieces · geyser fields ·
boiling-lift integration (R-B spec ruled, terrains shipped) · burning-shallows
wreck salvage.
**The engine mapping is drafted**:
`design/Jawa/worldbuilding/biomes/kits/scald_kit_spec.md` (2026-09-11) — 6
mechanics (S1 boil layer/steam sky, S2 steam-catch, S3 margin fishing + baths,
S4 geyser fields, S5 sail/walker set-pieces, S6 wreck salvage), heavy reuse
(ruled `RM_GameCondition_EnvironmentalWeather`, the miasma kit's
scatterer/anchor generics, vanilla 1.6 fishing/swimming/geysers), only 3 new
classes, hard-ban compliance table for the sheet's six 🔴 bans, build order,
and 2 open owner cards (the third — Scald salinity/fishing bucket — is
already open at `design/RimMandrake/RM_liquid_types_mod.md` §9 CARD-1 and is
consumed, not duplicated).
Governing rules from the sheet: the Scald is **never potable** (only its
distilled breath); **no boiling-immune traversal for free** (the shipped
burn values stand); **no macro-life in the boil itself** (walkers surface as
a set-piece, sails ride the carve-out); **no drained,

## OPEN SETTINGS_KIT_BUILD_GREY_SWITCHES_AT_LAST
Filed by BENCH 2026-10-14. Source: `Transient/experiment_2026-10-14/gss_review.md` §5 (GSS review found the shared
Mod Settings kit could not grey sub-settings under an off master switch, and had no reset-everything button).
Working notes: `Transient/experiment_2026-10-14/settings_kit.md`.
## spec
1. Kit: a way to declare a setting's master switch(es); dependents draw greyed and non-interactive while a master
   is off, values preserved.
2. Kit: a "Reset all to defaults" button that asks for confirmation.
3. Additive: a mod that does not opt in is unchanged (its DLL and .srchash too).
4. Wired into GimmeSomeSlack (both tabs) and Pyrelands. FlowWorks NOT edited (another agent is in it): wiring below.
5. Selftests: a dependent without a declared master, on a mod that declares masters, is flagged.
## built (2026-10-14)
- `src/RimMandrake/_Shared/SettingsKit/SettingsKitMasters.cs` (pure, selftested): `SettingDependencies`
  (`Declare(master, dependents...)`, `Independent(...)`, `Name(key, label)`, chains, several masters per dependent,
  cycles refused), `SettingsKitMasters.IsOn`, `ScopeGreyed`, `ResetAll`, `ResetAllLabel`, `ResetAllConfirmText`.
- `src/RimMandrake/_Shared/SettingsKit/SettingsKitMastersDrawer.cs` (Verse): `ResetAllButton(lis

## OPEN SETTINGS_SCREEN_KIT_1 — X-12: Shared settings-screen kit: collapsible sections, search box, per-section reset, and a "now / new maps only" tag per control
## spec
Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` row X-12 (belt hygiene pass 2 2026-10-09; items/ live+closed and src/ re-checked: not filed, not built). Scope: Build ONE helper under src/RimMandrake/_Shared/SettingsKit (linked <Compile Include>, like HarmonyResilience) that a mod calls from DoWindowContents. Adopt it first in FlowWorks, replacing the reflection-based DrawSectionReset added by FLOWWORKS_SETTINGS_SCOPE_RESET_1. Per-mod adoption is its own item each (CREATURE_BEHAVIORS_SETTINGS_SCREEN_1, ENVHAZARDS_SETTINGS_SCREEN_1). Do not rewrite any mod screen here beyond FlowWorks.
The row:
| X-12 | **One settings-screen kit for every mod**: collapsible sections, a search box, a reset per section, and a small "now / new maps only" tag on each control. CreatureBehaviors (~106 controls) and EnvironmentalHazards (~75) need it most. | shared UI helper, adopted mod by mod | M (kit) + S per mod | low | all; CB-5, EH-3, FL-5, LP-5 are the per-mod rows | MOD_OPTIONS_RETROFIT_1 asks for the scope wording but no shared kit, search or reset |
Every invented number is PROVISIONAL. Every feature gets a Mod

## OPEN STILLSAND_CAVE_AS_PLACE_1 — the cave's preservation, its drip, its glass walls and its mark
Split from `STILLSAND_PRECIOUS_CAVES_1` (spec 2, "the cavern as a place", and two table rows).
The chamber itself is built: a thick-roofed, permanently shaded floor of the rock's own rough stone,
and the brine seep, which reuses FlowWorks' shipped `RM_WaterBrineShallow`. These parts are still owed:
## spec
1. **The mummified preservation register:** nothing rots inside the cave, and desiccated remains stay.
   This needs C#. Read `CompRottable` first, then gate rotting on a roofed `RM_Stillsand` cave cell.
2. **The drip:** the cave's drip is the one water sound in the biome. It needs a SoundDef and an
   audio file, played as an ambient sustainer near the seep.
3. **The lens grotto's grown-biosilica walls:** a mineable natural-rock ThingDef that yields
   `RM_Biosilica`, with its own art (do a dedup check, then `fill_queue.py`). Then replace the
   floor stacks in `RM_PreciousCave_LensGrotto` with a ring of this wall.
4. **The taken cave's tribal mark:** a proper tribal glyph. Today the row soft-references the
   Graffiti mod's `RM_Graffiti_Vandal` scrawl.
## criteria
- A corpse left in a Stillsand cave does not rot.
- A lens grotto shows biosilica walls that can be mined for `RM_Biosili

## OPEN STILLSAND_SOLAR_STILL_1 — the solar still and the wringing still
From `STILLSAND_GLASS_LENS_CHAIN_1` §5, which that pass did not build. Read the parent's §5 for
the full ruling.
## spec
A glazed, black-bottomed lens condenser. It distils water from brine (cave seeps) and from wet
organics (fresh kills, eggs, duumma sacs). As the **wringing still** (lore IN) it also distils
**the dead**: a corpse gives water, outsiders take a mood penalty, and Sun-Debt believers call it
*drawing* (Utinni thoughts, RUT tier).
- Output goes into FlowWorks' water liquid or DBH water, whichever is live. Check which before
  building.
- The rate scales with sun elevation. A pearl lens (`RM_PearlLens`, already built) doubles it.
- Every litre counts on the Debt (`STILLSAND_RETURN_RITUAL_1`).
- It is distinct from the moisture vaporator.
Reuse: `RM_CompProperties_SunPowered` and `RM_SunPower.FactorAt` in
`src/RimMandrake/Stillsand/Source/RM_SunPowered.cs` already provide the sun gate: roof, shade
grid, pinned-sun elevation, and the gale matched by name. Glazing is `RM_SunGlass`; the
condensers are `RM_PrecisionLens`. Art: artpipe job `RM_SolarStill` is registered. Settings: a
toggle and a still-rate slider in `RM_GlassChainSettings` (parent §12).
## criteria
- A still completes one cycle in full sun an

## OPEN SUMP_TAR_FIRE_NETWORK_1 — network fire with gate firebreaks, and wiring the belch to glass-front cooling
Split out of `SUMP_TAR_HYDROLOGY_1` (FOUNDRY, 2026-09-26) — two of that
item's six sub-mechanisms that need either unbuilt hardware, a live burn
test, or an edit to a contended assembly, none of which fit that pass's
offline-only, uncontended-folders scope.
## what this item owns
1. **Network fire with gate firebreaks** (`SUMP_TAR_HYDROLOGY_1` ruling 5):
   "Lit tar propagates along connected liquid — a lit canal burns to its
   gate, a lit pool to its edges. Gate placement is life-and-death craft; a
   belch during a moat-burn is a genuine catastrophe."
   - `LiquidIgnitionMapComponent` (`Source/LiquidTypes/LiquidIgnition.cs`,
     `mandrake.rm.flowworks`) is a real, compiling PROTOTYPE — off by
     default, and its own header says outright "has never ticked inside a
     running game." It only proves the trigger-gated shape (adjacent real
     `Fire` Thing -> `FireUtility.TryStartFireIn`), not propagation-along-a-
     network or a stop-at-a-gate rule.
   - Tar is NOT flagged flammable in the registry today
     (`RM_Liquid_Tar`/`RM_LiquidProperties` on `RM_TarShallow`/`RM_TarDeep`
     carry no `flammable`/`igniteTemp`). Wiring it needs the SAME careful
     calibration

## OPEN SUMP_TAR_LIVING_SYSTEMS_1 — living-map responders, and tar rain (mod vs scenario)
Split out of `SUMP_TAR_HYDROLOGY_1` (FOUNDRY, 2026-09-26) — the two remaining
sub-mechanisms of that six-piece item, both needing iterative live tuning or
an explicit design decision this pass could not respons­ibly guess at.
## what this item owns
1. **The living map** (`SUMP_TAR_HYDROLOGY_1` ruling 8): "slow responders
   after every rewrite — soffeth rings grow at new seeps, mouse-lines
   re-route, flora margins migrate to new edges over days. The literacy game
   stays true after every belch." This is a multi-day simulation with no
   numbers named anywhere (growth rate, re-route delay, migration speed).
   Owner ruling 2026-10-03 (by question card): FOUNDRY picks first-guess
   pacing numbers, marks them PROVISIONAL in this item and in the def
   comment / settings tooltip, and they are tuned live later. Depends on the belch (or a
   canal release) actually rewriting the map first, which after
   `SUMP_TAR_FIRE_NETWORK_1`'s item 2 (belch -> real flood release) will be
   true; today the belch only splashes filth, so there is no real "after
   every rewrite" trigger yet to hang a responder off.
   **Part 1 BUILT (2026-10-03, round 36)** as `RM_MapComponent_SumpLivingMap`
   (`mandrake.rm.envi

## OPEN SUMP_TAR_NASTINESS_1 — the Sump is nasty, and the tar gets on everything
Owner ruling 2026-09-24 (typed in chat, quoted in full on
`BIOME_NUISANCE_NORMALIZATION_1`): the Sump must be many kinds of nasty — stinky,
sticky, messy, little way to keep clean. This item is the Sump-NOW slice of that
principle; the planet-wide normalization is gated to the end
(`BIOME_NUISANCE_NORMALIZATION_1`).
## spec
Four mechanics, all RM-tier (`RM_TheSump` / its kit), feature-gated per the Mod
Settings law:
1. **Sticky tar onto any terrain surface** — an overlay/coating a source can apply
   to arbitrary terrain (belch events, beast surfacing, tracking). 🔑 Check what is
   already built before writing anything: the Fever Wood's `RM_ToxinSealant`
   (item + terrain, `RM_MapComponent_LivingRegrowth` gating on it) is the shipped
   terrain-coating precedent; also weigh filth-based vs TerrainDef-swap approaches
   against `RM_CompTimedTerrainBurn` (Sump kit) and the FlowWorks/liquids layer.
   `SUMP_TAR_BELCH_EVENT_1` consumes this mechanism — build them coherently.
2. **Tarred-pawn hediffs** — tar on yourself: move/work penalties, mood, hygiene-
   flavored stink, spreads filth, maybe flammability. Severity from exposure;
   removal is not free.
3. **Solvents** — cleaning items that remove tar from p

## OPEN SWALE_CANAL_ART_REFERENCE_1 — Swale art from a live FlowWorks canal
Owner-typed on the Cracked Lands art sheet, 2026-09-29 (verbatim in
`Transient/bedazzle_art_sheets_2026-09-28/cracked_lands/sheet.decisions.json`,
row RM_Swale): screenshots of real canals are needed before this art can be
generated; the current render stands as PLACEHOLDER until then.
## spec
1. Build a real FlowWorks canal on a live map (quicktest fine; bridge work —
   `rimworld-live-review` staging rules apply).
2. Screenshot it clean at review zoom, several water states if cheap.
3. Spec the RM_Swale art against the shots (what a swale IS visually: the
   Cracked Lands' FlowWorks-normal channel per CRACKEDLANDS_MECHANICS_BUILD_1),
   then queue the regen with the shots as the visual target described in
   style_notes — ⛔ not as `reference=` (that triggers reskin-validate).
## criteria
- Shots committed (Transient/ ok), art spec written, regen job queued, and the
  placeholder note removed from the sheet manifest when the new art passes.

## OPEN spec
Owner answered 'Queue all' on a question card 2026-10-08 (decision taken by question card) for the remaining work of `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md`. Row X-10 there is the spec:
| X-10 | **"Taken by the land, comes back later" becomes one service.** The gale carry and FlowWorks' swept-away are the same mechanism built twice: a hold, a letter, a return. The spot where a pawn was taken gets a ground trace, so no one vanishes without a readable sign. | shared record + return + letter; a Traces prop when EVENT_TRACE_PROPS_LIBRARY_1 lands | M | low | Stillsand, FlowWorks, Traces | `RM_WorldComponent_SweptAway`, `RM_DuneGale`. Traces is still a spike |
Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; names follow the three-tier scheme.
## verify
Record each owed criterion with `rimflow verify TAKEN_BY_LAND_SERVICE_1 --criterion <ID> --result pass|fail|partial --config <list> --evidence <path>`:
- A2 (L1): taken_by_land.service_has_river_policy_and_trace_setting reads river policy registered and the trace setting;
- A3 (L2): a pawn swept off the river edge and a pawn carried off by a gale each get a letter, a drag mark where they sto
Evidence is the Player.log line or bridge state read the criterion names.
### Exact chec

## OPEN spec
Owner 2026-10-13: "Make tall tanks too that double the storage."
Capacity lives in C# (`Building_LiquidTank.Capacity` = footprint area x 20 x 2 if `RM_LiquidTankExtension.tall`), not in defs.
## done
- `RM_LiquidTankTall` (2x2, tall=true => 160; RM_LiquidTank is 80). Cost 285 steel + 5 components (1.9x / 1.7x), WorkToBuild 5800 (1.8x), HP 320, skill 5: a second drum roughly doubles material with a small frame saving. Same VCHE_PipeNetworks category, same thingClass so every workgiver/bill keyed on Building_LiquidTank covers it (no defName checks in non-selftest C#). The tank-capacity Mod Setting scales all tanks, so it already covers it.
- Art: PLACEHOLDER derivative (short-tank drum stacked twice, 512x768, drawSize (2,3), drawOffset z+0.5) via `art_source/TankTall/mk_tall.py` + artledger install. OWED: a real painted tall tank.
## owed
- The cargo tank `RM_UniversalCargoTank` is ALREADY tall (160). An extra-tall 320 version needs `RM_LiquidTankExtension` to carry a capacity factor (C#: extension, RM_Volume.TankCapacity, Mod Settings label, selftests). Owner picked it by card; waits on the pit-pocket-grid builder's uncommitted FlowWorks C#.
## done 2 (320 cargo)
`RM_UniversalCargoTankXTall` (2x2, `capacityFactor` 4 => 320). `RM_LiquidTankExtension.capacityFactor` (0 = uns

## OPEN WORLDMAP_LIQUID_TAGS_1 — typed liquid bodies on the frozen world drive landing mapgen
Filed by BENCH, 2026-09-13 (owner ruling: typed tiles drive mapgen —
`design/RimMandrake/liquids_framework_design.md` §4 "Typed worldmap → mapgen").
## spec
Two halves. (1) AUTHORING: the planet's water tiles and named bodies carry a
liquid TAG — which `LiquidDef` row that body's water is — covering
`LIQUID_BIOMES_MAP_1`'s four authored bodies (boiling ocean, two brine seas,
propane lake); read through a WorldComponent keyed by tile ID. No worldgen, no
re-render. (2) MAPGEN: a GenStep reads the landing tile's tag and REPAINTS the
vanilla-generated shores/lakes to that row's terrain suite — paint-over of
generated terrain, untyped tiles untouched.
🔴 **The tags are DATA that ships in the mod, not a live write onto the frozen
world.** This replaces the filing's original "one bridge pass writes worldTag
onto the tiles, committed with `world_commit`", which two measurements ruled
out on 2026-09-19:
- **`jawa/world_tile_set` writes exactly seven vanilla scalars** — biome,
  elevation, hilliness, temperature, rainfall, swampiness, pollution. A world
  tile has no free metadata field, so "write a tag onto the tile" could only
  have been done by overwriting one of the seven hand-authored values on a

## CLOSED BOILING_ICY_CANAL_FLUIDS_1 — boiling and icy water as canal fluids
Follow-up to `LIQUID_HEAT_PUSH_1` (FL-1 / X-8). Today `RM_Liquid_BoilingWater` and `RM_Liquid_IcyWater` have
`canalFluid` null, so `RM_FluidIdentity` maps their ponds to nothing and a channel or pit dug from a boiling pond
fills with plain `RM_Fluid_Water`. A pit can therefore never be flooded with boiling water, and
PIT_TEMPERATURE_SOFTENING_1's "boiling pit is a heat cell" case is unreachable even though the heat path is wired
(`FluidDef.hot/col

## CLOSED CANAL_BOTTOM_SPIKES_1 — Spikes as per-cell hardware on a superdeep canal bottom (RM_Spikes)
Part of the pit collapse (`PIT_SUPERDEEP_COLLAPSE_1` carries the rulings; `design/RimMandrake/flowworks_pits_unified_model_2026-10-02.md` is the one model). A pit is a canal cell dug to SUPERDEEP (D=4) and nothing else.
## spec
- `RM_Spikes` ThingDef + `PlaceWorker_SpikesOnExcavation` + `RM_SpikeUtility.HasSpikes(map, cell)`, mirroring the ladder's shape. Placement: **D=4 only** — owner Q2, 2026-10-02 (by card): spikes onl

## CLOSED CANAL_FILL_FRONT_TRACE_MOUTH_STAYS_DRY
Class: HARNESS (traced 2026-10-12, offline-MEASURED). Not a leak, not a dead feed: water races, so a dead-end D=1 channel fills
from its FAR END back and the mouth is wet only once the run is full. See "Root cause (2026-10-12)" below. extension_proof dry half, chain `plot_C` row `canal_fill_front`, has FAILed in all three
2026-10-11 runs (extension_result_20261011T141116.json, ...T170309.json, BENCH Transient/bench_live_20261011/ext_dry.json):
the source is stocked 300/300 a

## CLOSED RM_LiquidDrill: impassable, player-buildable, and shootable over
## measured
Live 620-mod cold load, 2026-09-19. Diffing the distinct config-error lines of
this load against the immediately preceding session's log, this is one of
exactly three new lines:
```
Config error in RM_LiquidDrill: impassable, player-buildable building that can
be shot/seen over.
```
`RM_LiquidTap` does **not** produce it, so it is the drill's own def, not the
shared `RM_LiquidDrillExtension` or the C# class.
## what it means
RimWorld's o

## CLOSED FLOODEDCANYON_RM_MOD_BUILD_1 — build RM_FloodedCanyon as its own RimMandrake mod
**the Cracked Lands - twin pair, mod EXISTS; RUT_CrackedLands merges in**
Phase A row 8 of `design/RimMandrake/biome_mod_architecture.md`. Parent:
`BIOME_MOD_SPLIT_EXECUTION_1`. Governed by `BIOME_PAINT_ONCE_AT_THE_END_1`.
## spec
🔑 **`biome_mod_architecture.md` §5 Phase A is the authority — read it, do not re-derive
it from here.** Steps 1–6, restated only far enough to start:
1. **Scaffold** `About/About.xml` with `mandrake.rm.floo

## CLOSED FLOOD_ENGINE_CORRECTIONS_1 — fix the FluidCanals flood defects, then a clean live pass
Filed by BENCH, 2026-09-13, out of the liquids-framework design sitting
(`design/RimMandrake/liquids_framework_design.md` §4, §7 phase ①). This is the
gate item: nothing else in the framework builds on the flood engine until it
lands.
## spec
Fix the three defects `FLUID_CANAL_FLOOD_TUNING_GAPS_1` recorded (read that
item's findings first — this item exists because it said "needs a design pass,
not a quick fix"):
1. Floods are

## CLOSED FLOOD_SWITCH_OFF_PROVE_SPILLS_GO_NOWHERE
Found by the independent P4-P8 review: `Transient/flowworks_review_P4_P8_20261011.md` (P6a section).
## What is true now (origin/main 9272c1344)
- P6a (57b4b4120) made an excavated cell HandsOff for a FlowWorks spill when `legacyFloodViaEngineEnabled`
  ("Spilled liquid fills channels properly") is OFF. That fix is right for the race: vanilla's queued temp-terrain
  removal strips whatever temp terrain is there (`TempTerrainManager.Tick` -> `RemoveTempTerrain`), engine fil

## CLOSED FLOWWORKS_BOTTLED_LIQUID_TYPE_MISSING_1 — RM_BottledLiquidExtension type not found
Filed 2026-09-18 (BENCH). Queue description: "RM_BottledLiquidExtension type not
found: RM_LiquidBottles_Base.xml discards + drives ~82 defs / 420 crossrefs on
the full load."
## 2026-09-18 (FOUNDRY, offline/BELT) — root cause was already fixed; independently verified, closing
**Root cause was a DEPLOY GAP, not a missing/uncompiled/misnamed class** — same
family as `ENVHAZARDS_DLL_REBUILD_OWED_1`, and already root-caused and
redepl

## CLOSED FLOWWORKS_DONOR_AFFORDANCE_GAP_1
## Thin item — no spec existed
Queue title was the entire brief. No `## spec`/`## verify` section, no prose
file, before this one. Picked up per FOUNDRY doctrine for thin items: decided
the approach myself, recorded the reasoning below rather than blocking.
## What was measured (re-measured, not trusted from the title)
`mandrake.rm.flowworks` (`src/RimMandrake/FlowWorks/`) generates its liquid
TerrainDefs from a table in `Tools/generate_liquid_suite.py`, which unions
`<affordances

## CLOSED FLOWWORKS_DOOR_FAMILY_1
Two stuffable doors for FlowWorks: a **Sluice** and a **SecurityGrateDoor**. Both
pass liquid without being opened; the grate also holds a real prisoner. Commissioned
by the owner 2026-09-17, in the middle of ruling on the pit collapse
(`PIT_SUPERDEEP_COLLAPSE_1`), which is why it is a separate item — it is new content,
not part of that collapse.
## the commission  (OWNER'S WORDS — verbatim, 2026-09-17)
Asked how a trapped mechanoid should resolve, he chose "killable from the lip" and
then

## CLOSED FLOWWORKS_FORCED_PIT_FALL_ROW_1 - FlowWorks forced-entry pit fall row
Filed 2026-10-07 from the GREEN-MIN / L2 sweeps (Transient/*_20261007.md).
## spec
FlowWorks validation_v2 row P3 (walk into a pit, held, one descent, fall damage) now asserts the REFUSAL, because FLOWWORKS_PIT_FALL_ONLY_FORCED_1 (owner 2026-10-06) forbids careless pathing into a pit (path veto 790fd4e8d, RM_PitTrapMath.cs:244-269). The forced-entry half is therefore unmeasured: add a row where a pawn is forced in (flyer landing counted by RM_P

## CLOSED FLOWWORKS_LIQUID_FACES_1 — every liquid, every face
Owner ticket, 2026-09-24, typed at the Sump flow round, verbatim:
> "Add a ticket item for Flowworks to consider floods, rain, rivers, lakes, and
> oceans of every supported kind of fuel and liquid in the mod."
## what this is
The generalization of the Sump's tar hydrology (`SUMP_TAR_HYDROLOGY_1`) to the
whole LiquidDef registry: for EVERY supported liquid and fuel row
(`liquids_framework_design.md` §2's roster — water grades, tar, the slime trio,
chemfuel, prop

## CLOSED FLOWWORKS_NORTHSTAR_BASELINE_RUN_1
Parent: `FLOWWORKS_NORTHSTAR_TRIAL_1`. Plan: `design/RimMandrake/northstar_trials/FlowWorks_trial_plan.md` §4. Needs: WIRE + SITE_PREP + the shared driver.
The first live execution is a BASELINE, not GREEN: most visual bars are expected NO today (Gravel channel
art, no pit art, no depth draw offset — plan §1). Its value is (a) the first live proof the visual floor
catches a mod whose state passes, and (b) real timings.
## acceptance
- Preflight clean; full run on the `flowworks`

## CLOSED FLOWWORKS_NORTHSTAR_REVALIDATE_1
Parent: `FLOWWORKS_NORTHSTAR_TRIAL_1`. Plan: `design/RimMandrake/northstar_trials/FlowWorks_trial_plan.md` §2.4 and §7.
FlowWorks' `## north star` is VALIDATED (13 must + 3 cannot, hash matches, MEASURED 2026-09-30) but has
**zero pit bars**; Pits.md's 11+1 bind nothing (`modcheck run FlowWorks` reads only FlowWorks.md — the
`feature:` key is read by `doctor` alone). `PIT_SUPERDEEP_COLLAPSE_1` (authority over the spec) forbids
moving them as they stand and records his third-card-r

## CLOSED FLOWWORKS_NORTHSTAR_SITE_PREP_1
Parent: `FLOWWORKS_NORTHSTAR_TRIAL_1`. Plan: `design/RimMandrake/northstar_trials/FlowWorks_trial_plan.md` §3 (the whole section; GPT-reviewed, §9).
## acceptance
- `modset_builder.py` tier `flowworks` (bridge + FlowWorks + JawaBench, all five DLCs), asserting `mandrake.rm.pits` absent.
- `prep_site.py` builds the golden trial site: plots + buffers per manifest, reservoirs painted paused,
  classification forced and recorded, plants/pawns/animals cleared, summer, golden save read-o

## CLOSED FLOWWORKS_NORTHSTAR_WIRE_1
Parent: `FLOWWORKS_NORTHSTAR_TRIAL_1`. Plan: `design/RimMandrake/northstar_trials/FlowWorks_trial_plan.md` §2.
`src/RimMandrake/FlowWorks/validation.py` is the OLD Pits suite moved in unchanged (`Suite("Pits")`,
four PitsSettings toggles, building-pit chains) — MEASURED 2026-09-30. No canal/depth/stock/superdeep
component exists. FlowWorks ships 27 boolean toggles (MEASURED).
## acceptance
- `validation.py` rewritten: `Suite("FlowWorks")`, `suite.toggles` = all 27 toggles, one component

## CLOSED FLOWWORKS_PIT_FALL_ONLY_FORCED_1 — who falls into a pit, and when
## ruling (owner, 2026-10-06, typed on a question card)
*"You can't fall in by careless colonist pathing. Only if they get blown/forced in do they fall. Enemies can fall if the pit is concealed or they are forced/blown in."*
## what
- Colonists never path into a pit by accident; they fall (with fall damage) only when blown or forced in.
- Enemies fall when the pit is concealed, or when blown or forced in.
Code today: fall damage is gated on `RM_Sup

## CLOSED FLOWWORKS_PIT_OCCUPANT_LIP_CUT_1 — near lip must not hide an occupant
Owner ruling by question card 2026-10-09: cut the near-lip see-through around an occupied pit cell so the occupant is visible. Current rule lives in `FLOWWORKS_VISUAL_PRINCIPLES_1` (A2: "the near lip hides 85% (a ghost stays so a D4 pawn can be found)"). Evidence shot: `Transient/fw_ovn_shots/pitG_x3.png`.
## criteria
- [ ] Near-lip draw skips/cuts out the occupied cell (and what the occupant needs to read) at every depth incl. D4.
- [ ] Unoccu

## CLOSED FLOWWORKS_SETTINGS_SCOPE_RESET_1 — FL-5: FlowWorks settings say when each takes effect plus per-section reset
## spec
Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` row FL-5 (belt hygiene pass 2026-10-09; items/ live+closed and src/ re-checked: not filed, not built). The row is the spec:
| FL-5 | The settings screen says when each setting takes effect: "now", "next pulse", "new ponds only" or "new maps only". Each section gets its own reset-to-default button. Some text already does this ("d

## CLOSED FLOWWORKS_SLUICE_TWO_DOORS_1 — a sealed sluice gate and a liquid-passing grate gate
## ruling (owner, 2026-10-06, typed on a question card)
*"There are sealed sluice gates (standard) and the ones made of metal grates that always allow liquid (this is just a gate, not a sluice gate then). Yes, both, two kinds of door."*
## what
- **Sluice gate (standard):** sealed. Shut holds liquid; open lets it through.
- **Grate gate:** metal grate, always passes liquid; it is just a gate (pawn barrier), not a sluice.
Today the

## CLOSED FLOWWORKS_TABS_RECONCILE_PIPES_WITH_PIPES
Owner ruling 2026-10-11 #4: *"Our tanks should go where other storage tanks go. Our pipes/hoses/wires/conduit should go
where those normally go. Only ask me this if there is ambiguity."*
## evidence (workshop defs read 2026-10-11)
- Vanilla: no liquid pipes or tanks.
- Vanilla Chemfuel Expanded (2792917473), Vanilla Helixien Gas Expanded (2877699803), Vanilla Nutrient Paste Expanded
  (2920385763): pipes, valves AND tanks (PS_ChemfuelTank, VNPE_NutrientPasteVat) all in `V

## CLOSED FLUID_CANAL_MECHANIC_1 — general canal/fluid-flow mechanic, RimMandrake tier
> 🔴 **Ruled 2026-09-13** (owner, liquids-framework bench sitting): FlowWorks
> is the framework's FLOW ENGINE (`design/RimMandrake/liquids_framework_design.md`
> §4) — pulsed spread only, plus two new asks: natural-source auto-prime and
> one-shot spills. Gate first: `FLOOD_ENGINE_CORRECTIONS_1` (the
> FLUID_CANAL_FLOOD_TUNING_GAPS_1 defects) before anything builds on the engine.
> The six-fluid roster this item names now comes from the

## CLOSED LADDER_PRISON_DOOR_1 — Ladder raise/lower works like a prison door; ladder art
Part of the pit collapse (`PIT_SUPERDEEP_COLLAPSE_1` carries the rulings; `design/RimMandrake/flowworks_pits_unified_model_2026-10-02.md` is the one model). A pit is a canal cell dug to SUPERDEEP (D=4) and nothing else.
## spec
- `RM_Ladder` gains a raised/lowered state, toggled from the lip (outside), never from inside a D=4 cell.
- Who may climb a lowered ladder: **like a prison door** — owner Q1, 2026-10-02 (by card). Your colonists

## CLOSED LIQUID_BODY_FLUID_IDENTITY_1 — Fluid identity per liquid body (retire per-map ActiveFluid); the merge rule
Part of the pit collapse (`PIT_SUPERDEEP_COLLAPSE_1` carries the rulings; `design/RimMandrake/flowworks_pits_unified_model_2026-10-02.md` is the one model). A pit is a canal cell dug to SUPERDEEP (D=4) and nothing else.
## spec
[F] + owner Q3 (2026-10-02, typed: *"If (1) is easiest, it's also the best for now."*): **fluids never mix** — chosen because it is the cheapest of the three by reading the code (unif

## CLOSED LIQUID_HEAT_PUSH_1 — hot and icy liquid move the air through vanilla heat
Source: `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` rows FL-1 / X-8. Closes the heat push that
closed `BOILING_WATER_BURNS_1` §3 specified and never landed.
## what
Built at `f90610cd5` (FlowWorks + one TerminalBiomes patch). Every 250 ticks, on its own timer (the depth engine
being off does not stop it), each wet hot or icy cell pushes vanilla heat into its ROOM — the same
`Room.Temperature` a heater writes, so vanilla Heats

## CLOSED LIQUID_REGISTRY_CORE_1 — the LiquidDef registry skeleton, adopting existing terrains
Filed by BENCH, 2026-09-13. Owner-ruled architecture: core registry + client
mods (`design/RimMandrake/liquids_framework_design.md` §2–3 — the spec lives
there, not here).
## spec
In LiquidTypes (growing into `RimMandrake: Liquids`): the new top-level def
type `RimMandrake.LiquidTypes.LiquidDef` with the property block and nullable
form slots per design §2; v1 rows per design §3 including the brine/propane
minimal rows forced by

## CLOSED LIQUID_SINK_DRAINAGE_1 — map-edge sinks drain a canal, live-proven
Owner, 2026-09-16: "I suppose we should add Sinks too at the edge of the map that simply
provide drainage from empty canals" — the inverse of a limitless source: liquid leaving is
transferred off-map, not destroyed, and overflow stays the only other conservation
exception. Filed as new work, but three earlier FOUNDRY passes this wave (history above)
found the mechanism was **already built** under `FLOWWORKS_BUILD_PROGRAM_1` Phase 4
(`8bb7c29d2`) t

## CLOSED LIQUID_THEFT_FIX_TANK_HIDES_ITSELF
Found live by BENCH 2026-10-11 (flowworks tier, 11 mods, export of c4bd7af75a, FlowWorks DLL addf7fd7 deployed). Class: MOD.
## finding
`RM_LiquidTheft.Witness` (src/RimMandrake/FlowWorks/Source/Machinery/RM_LiquidTheft.cs) asks
`GenSight.LineOfSight(p.Position, tank.Position, map)`. That 3-arg overload ends only at the single `Position` cell
(`CellRect.SingleCell(end)`), and `RM_LiquidTank` is 2x2 with `fillPercent` 1.0, so its other three cells block sight.
A witness whose lin

## CLOSED LIQUID_TYPES_MOD_1 — one liquid system, many liquids
> 🔴 **Ruled 2026-09-13** (owner, liquids-framework bench sitting): this mod's
> shape is now specified by `design/RimMandrake/liquids_framework_design.md` —
> LiquidTypes grows into the CORE REGISTRY (`LiquidDef` + form slots), and the
> roster below is superseded by that design's §3 (brine/propane minimal rows in,
> ammonia/coolant/etc. terrains stay shipped without rows). Concrete first slice:
> `LIQUID_REGISTRY_CORE_1`. Read the design before continuing this

## CLOSED LIQUID_TYPES_SPIKES_1 — the five spikes, run
Runs `design/RimMandrake/RM_liquid_types_mod.md` §8 against the three cards
ruled 2026-09-12 (Scald FRESHWATER + rivers flow OUT, coolant `Other` bucket,
films IN v1 — none re-litigated here). Sizing followed §8's own line: *"prove
on ONE def, measure, report."* All five spikes closed offline; a live/
quicktest pass on the built mod is owed before the mod ships (noted per
spike, not blocking this item).
New mod: `src/RimMandrake/LiquidTypes/` (`mandrake.rm.liquidtypes`

## CLOSED LIQUID_UNIT_CONTRACT_ROUNDTRIP_1 — FL-6/X-14: FlowWorks: one liquid-unit contract and an offline round-trip selftest (pond, canal, pump, tank, container, pour back)
## spec
Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` row FL-6/X-14 (belt hygiene pass 2 2026-10-09; items/ live+closed and src/ re-checked: not filed, not built). Scope: Selftest chaining RM_PumpMath.TankUnitsPerLevel, LiquidDef unitsPerBucket/Barrel/Bottle and RM_ContainerMaterials.UnitsIn proves nothing appears or vanishes w

## CLOSED NORTH_STAR_PIT_PILOT_1 — the pit proves the design, or the design is wrong
Filed by BENCH 2026-09-15. Successor to `MOD_VALIDATION_PIT_PILOT_1`, which is
closed `done` having "run it green" — that green is the defect this item exists
to overturn. Design: `design/RimMandrake/north_star_validation_spec.md`.
## Where this stands
- The pit's bars live in FlowWorks' walk (`design/validation_walks/RimMandrake/FlowWorks.md`,
  groups **Depth**, **The pit**, **The cover**, **The built half**), VALIDATED 2026-10-01
  afte

## CLOSED PITS_STALE_DEPLOY_COLLISION_1
MEASURED 2026-09-30 (read-only): the live `ModsConfig.xml` (612 active) contains BOTH
`mandrake.rm.flowworks` and `mandrake.rm.pits`. The game folder `Mods/Pits/` (About.xml dated
2026-08-30, `Assemblies/RimMandrakePits.dll`) is the pre-merge Pits mod. **All 22 of its defNames collide
with FlowWorks' defs** (`RM_OpenPit_Bare`, `RM_OpenPit_Spiked`, `RM_PinnedInPit`, `RM_DigPitDeeper`, …).
Pits merged into FlowWorks at `cade628c1`; the source folder holds only `__pycache__`.
Effect: du

## CLOSED PIT_CLIFF_MASK_BUILD_ASTAR_LEARNS_WALLS
Spec: `design/RimMandrake/relative_depth_climb_design_2026-10-12.md` §8.5 steps 2-3, 5 (build item 2 of three in §8.7).
Builds on `PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP` (ae8d38f27c) and the pond-bed hollow (acfae20df4): the masks read the
same depth as the pocket grid (`RM_PocketGrid.EffectiveDepth` = `ClimbDepthAt`, so a dry bed's 2/4 counts; covers read 0).
## state (BENCH, 2026-10-14) — built OFFLINE, live checks owed
Nothing deployed; the bridge was not touched.
**Bu

## CLOSED PIT_COVER_FALL_REWIRE_1 — Pit cover rehoused: multi-cell terrain-mimic cover that drops pawns into a superdeep cell
Part of the pit collapse (`PIT_SUPERDEEP_COLLAPSE_1` carries the rulings; `design/RimMandrake/flowworks_pits_unified_model_2026-10-02.md` is the one model). A pit is a canal cell dug to SUPERDEEP (D=4) and nothing else.
## spec
- A cover Thing over one or more D=4 cells, drawn with `TerrainMimicPrinter` (kept), with `CompPitCoverTrigger` summing mass over **the cover's cells** every 30 ticks.
- On t

## CLOSED PIT_DEPTH_DRAW_OFFSET_1 — Pawns visibly sink and rise with canal depth; superdeep walls 20% above the head
Part of the pit collapse (`PIT_SUPERDEEP_COLLAPSE_1` carries the rulings; `design/RimMandrake/flowworks_pits_unified_model_2026-10-02.md` is the one model). A pit is a canal cell dug to SUPERDEEP (D=4) and nothing else.
## spec
His ruling: *"The pawn should visibly rise up and lower down as they move over the depths… the walls are higher than their head by 20%"*. A pawn's vertical draw offset varies with the

## CLOSED PIT_FILL_EFFECTS_1 — What a fluid does to a pit occupant: drowning at D=4, poison keyed to fill, burning oil with an occupant
Part of the pit collapse (`PIT_SUPERDEEP_COLLAPSE_1` carries the rulings; `design/RimMandrake/flowworks_pits_unified_model_2026-10-02.md` is the one model). A pit is a canal cell dug to SUPERDEEP (D=4) and nothing else.
## spec
- `RM_PitDrowning` keyed to F>0 at D=4 for non-swimmers (swimming-graphic test, never an "aquatic" substring).
- Poison FluidDef: toxin keyed to fill, not a comp.
-

## CLOSED PIT_LEGACY_CODE_RETIRE_1 — Delete the old Pits building model from FlowWorks (21 pit defs, dig chain, PitsMod, escape, fittings)
Part of the pit collapse (`PIT_SUPERDEEP_COLLAPSE_1` carries the rulings; `design/RimMandrake/flowworks_pits_unified_model_2026-10-02.md` is the one model). A pit is a canal cell dug to SUPERDEEP (D=4) and nothing else.
## spec
The table in §4 of the unified model is the list. In short:
- RETIRE `Defs/Pits/ThingDefs/*` (18 concrete + 3 abstract — the last `TrapSpikeArmed` texPaths in th

## CLOSED PIT_TRAP_VISUAL_REDESIGN_1 — four-depth legibility, after the FlowWorks merge
**Re-scoped 2026-09-16.** This was a design sitting to decide what a pit looks
like in the covered, sprung and occupied states. Two of the owner's own rulings
that day changed what is left of it:
- **The specification half is DELIVERED.** The Pits validation walk's `## must
  show` list is VALIDATED and binds at hash
  `145a6b5d90729cb4647c73762c1685886164f5ef612d2495fdc6338755402991` — twelve
  lines covering covered (`pit_covered_invi

## CLOSED POND_BED_BUILD_HOLLOW_KEEPS_ITS_SHAPE
Spec: `design/RimMandrake/natural_bodies_as_canals_design_2026-10-11.md` §4 Option B, rulings 2-7; §9 for depth > 4
(that part is `POND_ELEVATION_BUILD_LAKES_RUN_DEEP`).
## state (BENCH night helper, 2026-10-13)
Prerequisites built: `POND_VOLUME_UNIFY_DEEP_NOTCH_YARDSTICK` (a9ecaad78dcb) and `POND_RETURN_LEG_BUILD_WATER_GOES_HOME`
(cd10284be668) — the return leg already takes water into a dry bed square and credits the pond, and a dug bed square
already leaves its pond and co

## CLOSED POND_RETURN_LEG_BUILD_WATER_GOES_HOME
Spec: `design/RimMandrake/natural_bodies_as_canals_design_2026-10-11.md` §4 Option A, §7 net change; owner rulings
5 and 6 (2026-10-12, same file, "Owner rulings").
## built (BENCH night helper, 2026-10-13, offline)
- **Return leg (G1, GPT #5/#6).** `RM_MapComponent_Excavation.CanReturnLevels / TryReturnLevels`: a natural pond square
  or its dried bed square (never a dug one) takes whole levels back into the pond's stock, all or nothing, up to
  capacity, through `RM_LiquidS

## CLOSED POND_VOLUME_UNIFY_DEEP_NOTCH_YARDSTICK
Spec: `design/RimMandrake/natural_bodies_as_canals_design_2026-10-11.md` §8, §8.5, §9.6. Owner 2026-10-12: *"1 tank
square, 1 deep water square/pond, 1 deep canal square should all be the same volume."*
## built (BENCH night helper, 2026-10-13, offline)
- `Source/RM_Volume.cs` (Verse-free, in SelfTest): `LevelsPerSquare 4`, `UnitsPerLevel 5`, `UnitsPerSquare 20`,
  `ShallowBedLevels 2`, `BedLevels(impassable, pathCost)` (deep = Impassable or pathCost >= 40: WaterDeep, OceanD

## CLOSED PUMP_POUR_TUNE_NO_FASTER_THAN_GRAVITY
Found live by BENCH 2026-10-11 (flowworks tier, 11 mods, export of c4bd7af75a, FlowWorks DLL addf7fd7). Class: MOD (tuning).
## finding
Owner ruling Q3 (liquid_network_semantics_design_2026-10-11.md): *"Keep it as faster draining"* -- a pump on Pour drains a
Dump tank FAST, against the Dump tank's slow gravity rate. Live, the basic `RM_LiquidPump` pours a Dump tank no faster
than gravity:
| scene | drained per 1000 ticks |
|---|---|
| L2a Dump tank, Outflow hose end, no pump

## CLOSED spec
No design doc — this is an engine/tooling investigation, not a content build.
Discovered as a side effect of `FISH_BESTIARY_BUILD_1`'s live verification
pass (2026-09-18): every attempt to generate a fresh map at a world tile that
carries a river or a lake-type `TileMutatorDef` produced a map with **zero**
water-family terrain anywhere on it, across every biome tried.
## what was measured
Method: `jawa/colony_found` (Player faction, some runs) or bare
`jawa/world_tile_map_generate` (other runs, no differenc

## CLOSED RIGID_PIPE_BUILD_WIRE_STYLE_PICKER
Owner rulings 2026-10-11 #1 and #8 (`design/RimMandrake/gss_flowworks_rulings_2026-10-11.md`).
## spec
- The rigid universal pipe is `RM_UniversalPipe` (defName kept; old `RM_LiquidHose` saves alias to it). The flexible line
  is the hose reel's hose and keeps the name "hose". Reading of ruling #1: the pipe the Q1 default produced IS the rigid
  pipe the owner asked for; what changes is its art (styled looks) and its interop. Card question owed if he meant a
  third, separate pa

## CLOSED spec
Full specs, both ruled by the owner 2026-08-30: `design/Jawa/covered_pit_traps_spec.md`
(the pit mechanics themselves) and `design/Jawa/trap_renaissance_spec.md` §4b (the
audit item this grew out of; its §2 trap-sense ruling — "Option C, gene + Ishko
layer" — is campaign-layer content, not in scope for this core-framework build).
Risk spikes proving the three hardest API shapes already compiled clean before
this item was filed: `src/RimMandrake/Spikes/` (Spike1 terrain-mimic print,
Spike2 holding-platform p

## CLOSED RIVER_SITE_FIX_FISHLESS_ROT_RIVER (presumed SITE, FlowWorks river proof)
**Measured (BENCH 2026-10-12b, harness 9905d543b3, FlowWorks a9c8e76b, 23-mod ratchet_pilot+patches tier):**
`river_site.py` took **tile 9980 RM_TheRot** (current 3,910, fast 1,127). The 2026-10-12 world's tile 825 (TemperateForest) was not
in this quicktest world (70 river tiles among 2,371 flat temperate candidates, against 176 last time). `extension_proof --live
--site river` read 9 PASS / 0 FAIL / 11 UNMEASURED (`Transient/bench_live_202

## CLOSED RIVER_SITE_FIX_GEYSER_ON_EVERY_TILE
Found live by BENCH 2026-10-11 (flowworks tier, 11 mods). Class: HARNESS (site finder).
`src/RimMandrake/FlowWorks/northstar/river_site.py` rejects any tile with a `BW.NATURAL_SCENERY` thing (SteamGeyser) anywhere
in the 130x130 central rect (61,61,130,130). On a vanilla quicktest world that is nearly every river tile: two attempts
(10 tries, then 30 after BENCH raised the cap to 40) rejected every river tile that had a current, so the river half of
extension_proof never got it

## CLOSED SCALD_DIVING_MOD_1 — Deep Diving (RimMandrake tier)
Owner ruling (2026-09-12, `scald_kit_spec.md` open card 3, verbatim): "Diving
interaction, and make the diving mod v1 content now!!" Ban 4 in
`the_scald.md` ("no macro-life in the boil itself") is superseded exactly
this far: a DEEP interaction exists; the boiling SURFACE stays no-swim.
## What shipped
`src/RimMandrake/DivingInteraction/` — packageId `mandrake.rm.divinginteraction`,
namespace `RimMandrake.DivingInteraction`, defName prefix `RM_` (naming_lint:
0

## CLOSED STILLSAND_GLASS_LENS_CHAIN_1 — sand to glass to lens: stills, ovens, the sun lance and fulgurites
From `STILLSAND_BEDAZZLE_SITTING_1` (closed 2026-09-30). Design source:
`design/Jawa/worldbuilding/biomes/stillsand_turn3_development_2026-09-30.md` §2.4 and §4 #5, #11,
#12, with the turn-4 rulings in `stillsand_bedazzle_cast_2026-09-30.md` §0. Owner, typed, volley
turn 2: *"the very fine sand of this region is extremely high quality and can be smelted into a fine
glass fit for lenses. The lenses can be made into hi

## CLOSED Live check that the Stillsand native crash is gone. On tier acc_20261009b a 100x100 Stillsand map crashed the game natively 4 of 4 times once ticks ran (crash dumps `Crash_2026-10-09_075221959`, `_075708322`; same native frame in `_073219564` and `_074917192`): a Burst frame (`lib_burst_generated`) on a WORKER thread, no managed exception. Paused spawns, generation and `clear_area` survived; a 75x75 map survived.
Never-observed mechanism (why this is live): the ShadeGrid sun-cost path customizer's NativeArray lifet

## CLOSED STILLSAND_RM_MOD_BUILD_1 — build RM_Stillsand as its own RimMandrake mod
**the Stillsand (extreme desert; campaign label "the Dune Sea" stays a Utinni patch)**
Phase A row 1 of `design/RimMandrake/biome_mod_architecture.md`. Parent:
`BIOME_MOD_SPLIT_EXECUTION_1`. Governed by `BIOME_PAINT_ONCE_AT_THE_END_1`.
## 🔑 STATE — MEASURED 2026-09-23
Not a twin (§4 doesn't apply — row 1 is "PROPOSED — owner-named standalone", no existing
`RM_Stillsand` folder). `src/RimMandrake/Stillsand` does not exist (checked, `ls` → no

## CLOSED STILLSAND_SAND_SWIM_KIT_1 — things swim under the sand: the kit, the Listening, sand fishing, the thumper
From `STILLSAND_BEDAZZLE_SITTING_1` (closed 2026-09-30). Design source:
`design/Jawa/worldbuilding/biomes/stillsand_turn3_development_2026-09-30.md` §2.0, §2.1 and §4
#1, #9, #15, with the turn-4 rulings in the cast bible `stillsand_bedazzle_cast_2026-09-30.md` §0.
Owner, volley turn 2, typed: *"The listening should focus on wind and sand Noises and then ominous
rumbling as things swim through the sand or bur

## CLOSED SUMP_TAR_HYDROLOGY_1 — how the tar flows: the Sump on FlowWorks
Eight owner rulings, 2026-09-24, post-sitting flow round (his framing, typed:
consider *"how the flow works on the rest of this biome since making tar
[moats] was one of the original inspirations of that particular mod and all the
places that the tar liquid might go in terms of an entire ecosystem if oceans
and rivers were made of tar"* — *"as well as even things like tar rain"*).
Engine ground: FlowWorks pulsed spread (sort+overflow depth grid, no p

## CLOSED SUPERDEEP_HOLDER_RETIRE_1 — Retire the hidden RM_SuperdeepPit holder; a D=4 cell traps a SPAWNED pawn by grid rule
Part of the pit collapse (`PIT_SUPERDEEP_COLLAPSE_1` carries the rulings; `design/RimMandrake/flowworks_pits_unified_model_2026-10-02.md` is the one model). A pit is a canal cell dug to SUPERDEEP (D=4) and nothing else.
## spec
Today `RM_SuperdeepCapture.EnsureHolder` spawns a `Building_SuperdeepPit : Building_OpenPit` on every D=4 cell and despawns captured pawns into its container. Owner, 2026-10-0

## CLOSED SUPERDEEP_PRISON_ROOM_1 — An enclosed superdeep area is a room; a prisoner bed makes it a prison; capture down / convert down from the lip
Part of the pit collapse (`PIT_SUPERDEEP_COLLAPSE_1` carries the rulings; `design/RimMandrake/flowworks_pits_unified_model_2026-10-02.md` is the one model). A pit is a canal cell dug to SUPERDEEP (D=4) and nothing else.
## spec
- LAW 2 exception [D]: depth may bound a room. Implement at the seam `SUPERDEEP_SEAM_MEASURE_1` found (likely a Harmony patch on region building if reg

## CLOSED SUPERDEEP_SEAM_MEASURE_1 — Measure the engine seams the pit collapse needs (Desktop, RimSage)
Part of the pit collapse (`PIT_SUPERDEEP_COLLAPSE_1` carries the rulings; `design/RimMandrake/flowworks_pits_unified_model_2026-10-02.md` is the one model). A pit is a canal cell dug to SUPERDEEP (D=4) and nothing else.
## spec
Desktop only (RimSage). Read, do not build. Record each answer with the decompiled member cited, in a `## measured` section here.
1. `Verse.AI.PathFinder.FindPath` / `Pawn_PathFollower.TryEnterNex

## CLOSED TESTENV_RIVERSITE_HARDEN_RIVER_ENDS_AT_SEA
Filed by BENCH 2026-10-15 (live round 7, HEAD 0207ac8fc2). Evidence in `Transient/bench_live_20261015_r7/live/`:
`river/river_site.log`, `river/ext_swept_site1_{1,2,3}.json` and `.log`, `probes/edge_probe.py`, `probes/maps_probe.py`.
Class SITE/HARNESS. Both defects are in `src/RimMandrake/FlowWorks/northstar/river_site.py`, and the swept row consumes them.
## 1. The swept row was staged on a river that has no downstream map edge
`river_site.py` (run on the r6 Pyrelands

## CLOSED TESTENV_SWEPT_BRUISE_HARDEN_OWN_HAZARD
Filed by BENCH 2026-10-15 (r6). Evidence: `Transient/bench_live_20261015_r6/live/river/ext_river.log` (the GOVERNOR_STOP
line) and `ext_river_swept2.log`.
What happened:
- FlowWorks' river extension row `swept/returns_home` stages throwaway colonists on moving water at the map edge and waits
  for the current to carry one off.
- The current bruised the swept colonist: Fitz went from health 1 to 0.95, Bruise/Torso, from
  `RM_MapComponent_RiverCurrent.ApplyHazards` with `brui

## CLOSED spec
Owner answered 'Queue all' on a question card 2026-10-08 (decision taken by question card) for the remaining work of `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md`. Row FL-2 there is the spec:
| FL-2 | Thick liquids visibly creep. Today, liquid that reaches a cell can pass straight on to the next cell within the same pulse, so on a long canal tar can race almost as fast as water. Cap how far a fill front moves in one pulse, so tar, slime and blood crawl at their stated speed. | Kernel: a recipi

## CLOSED WEIR_BREACH_FIX_CATCH_STRANDS_AT_HOME (MOD, FlowWorks rivers)
**Row:** `extension_proof --live --site river` `breach_wash` (toggle `breachWashesCatch`), and the 6 rows it gates
(silt_richen_and_revert, ferry_rope, ferry_rope_undrafted, levee_engine_fact, levee_holds_and_gap_leaks, breach_cascade_order).
**Measured live 2026-10-12c** (23-mod tier, FlowWorks a9c8e76b, river_site tile 60145 TemperateForest, map 8):
`Transient/bench_live_20261012c/ext_river.json`: `BREACH heldBefore=3 heldAfter=3 breaching=True arres

## CLOSED WEIR_POOL_DIAGNOSE_DAMMED_AT_THE_EDGE (FlowWorks rivers; presumed SITE, untraced)
BENCH 2026-10-12, extension_proof `--live --site river` on river_site.py's tile 825 (TemperateForest, riverCount 2, current 3,582
cells), 23-mod pilot tier, export e8a4060321: `works.weir_arrest_and_pool` FAIL —
`RM_RiverWorksProofs.ProofWeirPool` returned `POOL cells=0 dropped=0 arrestedWet=True at=(108, 0, 12)`; the 8 later `works`
components were UNMEASURED (upstream failed). Evidence: `Transient/bench_live_20261012/ext_river.jso