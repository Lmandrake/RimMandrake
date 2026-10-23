# BRIDGE RUN 1 — every owed FlowWorks + GSS live check, one driver, one sitting

Written 2026-10-23 (BENCH takeover, area P) offline, from the merged ledger (`model.replay()`: **159 open FlowWorks/GSS items,
115 with owed criteria, 182 owed criteria**), the Wave-1 helpers' progress files
(`D:\ClaudeWork\rimmandrake\scratch\takeover_{A,B,D,E,F,H,P}_20261023.md`) and FOUNDRY's earlier sitting plan
(`Transient/flowworks_live_sitting_plan.md`, whose order this keeps and extends). Nothing here has run against this
sitting's DLL. Times: **M** measured on the 10-22 belt, **E** estimated.

**Rules for the driver.** One driver holds the bridge (`rimflow bridge take --for "BRIDGE_RUN_1"`; release at the end).
Every row is PASS / FAIL / UNMEASURED with MOD / SITE / HARNESS; **only a PASS or a MOD FAIL is a verify** (UNMEASURED never
is). Verify each row straight off its result JSON:

    rimflow verify <ITEM> --criterion <C> --result pass|fail|partial --config min-<N> --evidence <result.json>

`<N>` is the run's measured `len(env.running)` (B0 / `driver_stamp`), never a tier label. A row marked *partial* is
`--result partial`. A look (L1/L3 "live look", "capture") is never verified by the driver: the frame goes to a naive
Opus judge (`design/RimMandrake/art_judge_brief.md`, "Nothing reaches the owner unread") and the judge's verdict is the
verify, logged `--why "delegated: look"`. A prior-PASS-now-FAIL is a STOP (file it, then go on). Between steps:
`jawa/kill_hostiles`, `jawa/incident_queue_clear`, feed + quench colonists; the scripts below do this themselves.

All commands run from the **export root** (step 0.2) with `python.exe ... | tr -d '\r'` unless marked `python3` (WSL).

---

## 0. Before the load (≈10 min, game closed)

1. **Publish state.** `./publish` in `/home/mandrake/rm/bench`; note `git rev-parse --short HEAD` = **RUN_SHA**. Every
   FlowWorks / GSS commit from Wave 1 (areas A B D E F H P) must be on origin/main; a helper's uncommitted C# never deploys.
2. **Export** (assembly identity, python.exe cannot read WSL paths):
   `git -C /home/mandrake/rm/bench archive RUN_SHA src/RimMandrake/Utils src/RimMandrake/FlowWorks src/RimMandrake/GimmeSomeSlack src/RimMandrake/_Shared | tar -x -C /mnt/d/ClaudeWork/rimmandrake/scratch/bridge_run_1/`
   then `cd D:\ClaudeWork\rimmandrake\scratch\bridge_run_1`. Results land beside each script in the export; copy the
   result JSONs back to `Transient/flowworks_takeover_20261023/bridge_run_1/` before verifying.
3. **Deploy** (plan, then `--apply`): `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod FlowWorks`,
   `--mod GimmeSomeSlack`, `--mod LuminousPigment`; JawaBench via `bridgetools/build.py`. Then read the deployed DLL hash
   and compare with the export's `Assemblies/RimMandrakeFlowWorks.dll` (the PIPE_GIRTH trap: a commit that was never
   deployed). Owed-at-deploy items: PIT_SPIKES_REDRAW_SPOKES_NOT_LOGS, RAIL_LADDER_REDRAW_CLIMB_NOT_CRAWL (`needs deploy`),
   WORLD_PATHS_VERIFY_WATER_FINALLY_WET.
4. **Tier**: `python3 src/RimMandrake/Utils/modset_builder.py --tier fw_gss_sitting --apply` and add
   `mandrake.rm.luminouspigment` (glow-tank rows). All five DLC. **One cold load** (~70 s on this tier).
5. `rimflow bridge take --for "BRIDGE_RUN_1 FlowWorks+GSS owed checks"`.
6. Offline gate (WSL, seconds): `python3 src/RimMandrake/Utils/selftest_flowworks_stock.py`,
   `python3 src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py --offline-gate`. Any red refuses the live steps it covers.

---

## 1. Fresh quicktest maps, quiet rows (tier fw_gss_sitting) — E ≈ 50 min

Each step starts `--fresh-map` (or `test_site_saves.py load calm`, equivalent where `--fresh-map` is not named).

| # | command | time | rows → item criterion |
|---|---|---|---|
| 1.1 | `northstar/sitting_gaps_proof.py --fresh-map` | E 7 min | `RIVER_LAYER_REDRAWS_CLEAN` → FLOWWORKS_RIVERCOLOR_FIX_DICT_SELF_ENUM A1 · **`CONVERTER_BIG_RECIPE_RUNS` → FLOWWORKS_CONVERTER_FIX_BLOCKED_STARVES_REST A1 (NEW 7fce87f1ae: the re-scoped still; first live run)** · `RAILING_HAS_STUFF` → RAILING_MATERIAL_FIX_MADE_OF_NOTHING A1 · `FAUCET_TAB_PIPE_ONLY` → PIPE_FAUCET_BUILD_TAP_NAME_NOW_FREE A1 · `T30_pipe_faucet` → same A2 · `FAUCET_LOOKS_RESOLVE` / `FAUCET_TAKES_MODERN` (partial) → FAUCET_REDRAW_BORROWED_BLEED_WELL A2/A3 · `GUARDRAIL_ATLAS_RESOLVES` → GUARDRAIL_ART_RESKIN_BORROWED_FENCE A2 · `REEL_FACINGS_LAY_ALONG_AXIS` (partial) → HOSE_REEL_FIX_TURNS_WITH_THE_SHIP A1 · `S3_HOSES_ON_BARE_GROUND` → HOSE_PATHING_REPAIR_SCENIC_ROUTE_PLEASE A1 · `SETTINGS_SEARCH_FINDS_ROW` → SETTINGS_SEARCH_FIX_LABELS_NOT_FOUND A1 · `CANAL_LAKE_ONE_DEF` + its `shot` → CANAL_LAKE_COLOUR_UNIFY_TWO_BLUES A1 (L3: judge reads the frame). `REACTOR_NEXT_REACTION_RUNS` stays UNMEASURED/SITE by construction (no verify). |
| 1.2 | `northstar/pond_pump.py --drain --fresh-map` | E 5 min | POND_PUMP_FIX_LAST_DROP_COUNTS A2, A3 |
| 1.3 | `northstar/suspension_settings_live.py --fresh-map` | M 9 s | SUSPENSION_BUTTONS_DIAGNOSE_STILL_SHOWING A1 · SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS A7 |
| 1.4 | `northstar/glow_tank_live.py --fresh-map` | M 139 s | GLOWTANK_DRINK_DIAGNOSE_DRY_BESIDE_THE_SEA A1 · GLOW_TANK_LIQUID_FEED_1 A2 |
| 1.5 | `northstar/liquid_checks.py --only L5 --fresh-map` | M 48 s | SPILL_DIAGNOSE_TEN_THOUSAND_GONE_DRY A1 · LIQUID_LEDGER_BUILD_NO_UNIT_LOST A6 · its receipt → TESTENV_MEGAPEDE_HARDEN_GATECRASHER A1 (arrivals empty or logged, no hostile survives to a stop) |
| 1.6 | `northstar/walk_gaps_proof.py --fresh-map` | M 313 s | `PORTS_*` → FLOWWORKS_PUMP_PORTS_REBUILD_ONE_PER_SIDE A4 · `PONDS_HOSE_LEVEL` / `PONDS_DIFFERENT_LIQUIDS_NO_MIX` → PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL A4 / A5 · `PORTS_CORNER_REFUSED` → PROOF_REELS_FIX_STILL_STAGED_WEST A3 (half) |
| 1.7 | `northstar/pipe_levelling_perf_proof.py --rehearsal` (SAME map as 1.6, no new map) | E 5 min, capped by `--budget-s 480` | LEVEL_REHEARSAL_FIX_POURS_ON_FULL_PONDS A1 (0 levels lost, no conservation exception) · PROOF_REELS_FIX_STILL_STAGED_WEST A3 (other half: `layFailures` read) · **LEVEL_REHEARSAL_UNSTICK_WAITS_FOR_GODOT A1** (finishes inside the budget, both rows written, `res.calm` present). NEW d9a1934bd0: a dead probe channel / spent budget now writes UNMEASURED/HARNESS and exits; a mech raid the recovery cannot clear writes UNMEASURED/SITE. |
| 1.8 | `northstar/trench_crossing_live.py --fresh-map` | M 58 s | TRENCH_CROSSING_FIX_DOWN_ACROSS_AND_UP A3 |
| 1.9 | `northstar/drawbridge_proof.py --fresh-map` then the **cables capture** (§1a) on the same map | M 231 s + 3 min | DRAWBRIDGE_LOOKS_FIX_HIS_PICKS_OUTRANK A1 (rows) · DRAWBRIDGE_CABLES_FIX_STOP_SHORT A1, A2 (frames → judge) |
| 1.10 | `northstar/suspension_bridge_proof.py --fresh-map` | M 236 s | `LOOK_<Look>_RESOLVES` → SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS A8 (frames to the judge too) |
| 1.11 | `northstar/water_looks_proof.py --fresh-map` | E 4 min | WATER_ART_CANDIDATES_BUILD_WHAT_HE_APPROVED A1, A2, A3 |
| 1.12 | `northstar/legacy_fill_live.py --fresh-map` | E 3 min | EXCAVATION_LEGACY_MIGRATION_FLAG_1 A1, A2 |
| 1.13 | `northstar/deep_lake_proof.py --fresh-map` | E 6 min | DRAWDOWN_DIAGNOSE_THIRTEEN_BEFORE_TWELVE A1 |
| 1.14 | `northstar/deep_stone_live.py --fresh-map` | E 3 min | PIT_DEEPSTONE_BUILD_DIGGING_FINALLY_PAYS A2 |
| 1.15 | `northstar/ladder_wall_proof.py --fresh-map` | E 3 min | LADDER_PARITY_BUILD_NO_KEYS_REQUIRED A4 (four `LADDER_PARITY_*` wall rows) · **A7 `LADDER_PARITY_CLIMBER_CENSUS` (NEW 99deb7e783; first live run)** |
| 1.16 | `northstar/pit_rescue_live.py --fresh-map` | E 4 min | LADDER_PARITY A6 first half ("still green"); the prisoner-escape half has NO row (PIT_ESCAPE_PROVE_LADDER_LEFT_DOWN) |
| 1.17 | **Tank debug + pipe style menu**, god mode on a fresh map: build an `RM_LiquidTank` and a 3-cell `RM_UniversalPipe` run; `rimworld/list_gizmos` on the tank (expect `Dev: fill`, `Dev: empty`), press fill → `hp tank:x,z` reads capacity in the chosen liquid; press empty → 0. Select a pipe: the `Choose style` float menu lists exactly the four looks and restyles the whole run (`jawa/thing_graphic` on every run cell) | E 5 min | TANK_DEBUG_BUILD_FILL_AT_WILL A1 · PIPE_STYLE_PRUNE_WHOLE_RUN_ONLY A1 · HOSE_RULINGS_BUILD_THREE_REVERSALS_ONE_CARD A2 (the four-look menu survives blueprint → frame → built) — hand steps, no script row: record the reads in the run notes |
| 1.18 | GSS: `src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py --live` (loads `calm`) | E 15 min | its rows → GSS items; S12d → GSS_STYLE_RUN_PROVE_MIXED_LOOKS_SUSPECTED D4; B12/B13 (`GimmeSomeSlack/validation.py`) → GSS_HOOKUP_CABLE_PROBE_HIDDEN_CONDUIT. On fw_gss_sitting this is evidence, NOT a `modcheck record` (the GSS record wants its own tier). |

### 1a. Drawbridge cables capture (after 1.9, same map; DRAWBRIDGE_CABLES_FIX_STOP_SHORT)

drawbridge_proof leaves scene A (timber, plot `origin+(0..5,0)`, default origin 140,140) and scene B (steel, `(0..7,6)`) standing.
With `C = src/RimMandrake/Utils/rimbridge_client.py`:

    python.exe C --call jawa/static_call --json "{\"type\":\"RimMandrake.FlowWorks.Pits.RM_DrawbridgeProofs\",\"method\":\"ProofDevSet\",\"args\":\"142,140;lower;instant\"}"
    python.exe C --call jawa/static_call --json "{\"type\":\"RimMandrake.FlowWorks.Pits.RM_DrawbridgeProofs\",\"method\":\"ProofDevSet\",\"args\":\"143,146;lower;instant\"}"
    python.exe C --call rimworld/set_camera_zoom --json "{\"rootSize\":8}"
    python.exe C --call rimworld/frame_cell_rect --json "{\"x\":137,\"z\":138,\"width\":14,\"height\":11,\"paddingCells\":1}"
    python.exe C --call jawa/take_screenshot --json "{\"fileName\":\"br1_cables_lowered\"}"
    (then ProofDevSet ...;raise;instant on both, 10 ticks, the same frame -> br1_cables_raised)

A1: every bollard's two ropes run unbroken clamp → deck end on both banks, timber and steel (Scrapper look). A2: raised, the
ropes lie as slack loops on their bank, none over the pit; the raised leaf's top shows its hook eye. Judge both frames.

---

## 2. The river site (load `river`) — E ≈ 25 min

`python.exe src/RimMandrake/Utils/modcheck/test_site_saves.py load river` (read-back check included).

| # | command | rows → item criterion |
|---|---|---|
| 2.1 | `northstar/extension_proof.py --live --site river --out <river.json>` | `weir_captures_floating` → WEIR_CATCH_FIX_NO_FREE_FISH A3 (lifted=1 onDry=True created=0 unitsAfter=unitsBefore) · `river_flotsam_enters_and_leaves` → (area E's flotsam rows) · TAKEN_BY_LAND_SERVICE_1 A3 · FLOWWORKS_QUARRY_DIGGING_1 A3/A4 · RIVER_TOGGLE_PROOFS_BUILD_ELEVEN_UNCLAIMED A2/A5 where its components reach them · its receipt → TESTENV_FLOODS_HARDEN_SEASON_CRASHES_PARTY A1 (enableStoryteller=false, no Seasonal flooding letter) |
| 2.2 | `python.exe .../test_site_saves.py check river` then `jawa/quiet_site action=status` | TESTENV_HIVES_HARDEN_RIVER_MAP_SQUATTERS A1 (0 threat structures) · TESTENV_TOXIC_DIAGNOSE_RIVER_SITE_SNIFFLES (diagnose: record what sickens on the site) |
| 2.3 | `northstar/suspension_bridge_proof.py --river x1,z1,x2,z2` (a 10-square crossing of the site's river, read from the load's river cells) | SUSPENSION_WATERS_BUILD_MAY_BACKTRACK A1, A3 |
| 2.4 | the weir white-water capture: stage a weir (ProofWeirPool site, `extensions_rivers.py` weir component's cells) and frame its downstream cell; `src/RimMandrake/FlowWorks/art_source/.../whitewater_frames.py` names the frame set | WEIR_LOOK_REDESIGN_WHITEWATER_FROZEN_SOLID A3 (frames → art-eval run) |
| 2.5 | then `python3 northstar/extension_proof.py --merge <dry.json> <river.json>` with step 3.3's dry half | FLOWWORKS_CHECKOUT_SCOPE_1 A2 |

---

## 3. The walkthrough save e (maps C and R) — E ≈ 30 min, two loads

Back up the Saves folder first. `rimworld/load_game_ready` `RM_fw_walkthrough_20261023e`. In-memory changes are discarded
after (never save over e).

| # | command | rows / looks → item criterion |
|---|---|---|
| 3.1 | `northstar/joint_check.py --all-maps --crops Transient/joint_gate/<stamp>` | JOINT_GATE_HARDEN_TRUST_THE_DRAWN_BOX A2 · JOINT_CHECK_WIDEN_PIPE_STUBS_UNSEEN A2 · HOSE_CROSSING_FIX_FLAT_AS_A_PANCAKE A2 · HOSE_BUILDINGS_FIX_BATTERY_HIDE_AND_SEEK A2 · HOSE_JOINTS_REPAIR_ENDS_MISS_THE_NOZZLES A3 · CENTRE_CELLS_FIX_WALK_THROUGH_WALLS A2 |
| 3.2 | `northstar/scenarios_map.py --save` with the gate red (expect the refusal line), then green | JOINT_GATE_HARDEN_TRUST_THE_DRAWN_BOX A3 |
| 3.3 | `northstar/extension_proof.py --live --site dry --out <dry.json>` needs the golden site, not e: run it on `test_site_saves.py load calm` after `prep_site.py` + `preflight_flowworks.py` (E 6 min) | FLOWWORKS_CHECKOUT_SCOPE_1 A2 (dry half) · PIT_TEMPERATURE_SOFTENING_1 A2-A4 · FLOWWORKS_CONTAINER_MATERIALS_1 A2 · LIQUID_BOTTLE_LOOP_1 A1-A3 where its plots reach them |
| 3.4 | map C: **zoo check** `northstar/scenarios_map.py --build --only C5 --no-soak`, `jawa/list_pawns` census of every other plot before and after (equal) | SCENARIO_ONLY_FIX_SWEEPS_THE_WHOLE_ZOO A1 (NEW c4aefb25df) |
| 3.5 | map R: `northstar/scenarios_map.py --river --build` (map R current) then frame station R1 and capture | RIVER_MUFFALO_FIX_SHOWS_ITS_REAR A1 (offline half proved d356baa2a4: the build turns the Muffalo west, locked) · CORD_LOOP_UNTANGLE_LASSOED_A_PIPE A1 (map R C1 battery→pump cord at 36,72 after the fresh cord rebuild) |
| 3.6 | map C station looks, one zoomed frame each at 80-100 px/cell (`scenarios_map.py --goto <Cn>` then `jawa/take_screenshot`) | C12: LADDER_EW_FIX_LEANS_THE_WRONG_WAY A1 · both pumping stations: PUMPSTATION_COUPLER_MATCH_FIX_STEEL A1, COUPLER_ART_INSTALL_DRESSED_UP_AT_LAST A1 · the cord junction pump: CORD_PLUG_FIX_FINDS_THE_PIPE_SLOT A2 · the end-to-end hoses: HOSE_SPLICE_BUILD_MATES_BY_SLOPE A2 (read `RM_MapComponent_Hoses.MateReport()` by static_call) · reels: REEL_TAP_CAMERA_REDRAW_STILL_SIDE_ON A1 (L3) |

---

## 4. A disposable looks map (fresh quicktest; `review_map.py --build --fresh-map`) — E ≈ 30 min

`src/RimMandrake/FlowWorks/review_map.py --build --fresh-map`, then `--goto <station>` + `jawa/take_screenshot` per look,
zoomed to 80-100 px/cell. Stage the missing hoses by `hp lay:` where a station has none. Every frame goes to the judge.

| looks | → item criterion |
|---|---|
| a hose coupled on each side of each tank look (RM_LiquidTank, Tall, XTall, cargo tank upper W/E) and both pumping stations | TANK_LANE_FITTINGS_REDRAW_MODERN_ONLY A2 · TANK_NS_PORTS_REDRAW_COUPLE_THIN_AIR A2 · TANK_SOUTH_PORT_REDRAW_STUB_PEEKS_OUT A2 · UNDER_COUPLER_DECIDE_CORNER_CROWDING A2 · HOSE_SIDEPORT_FIX_AIMS_AT_OLD_MIDPOINT A1 (Tall south lane-0 port at 0.75) |
| a hose coupled to each pump look and to a tank | UNDERCOUPLER_GIRTH_TUNE_PEEKS_PAST_NECK A1 · PUMP_COUPLING_SHRINK_STILL_SIZED_FOR_GIANTS (its owed look) · PUMP_PORTS_REDRAW_SIZED_FOR_FAT_PIPES A1 · PUMP_ART_RESKIN_LESS_GARDEN_HOSE A2 (beside a colonist, true scale) |
| a chemfuel and a propane adapter on a pipe, hose coupled | PIPE_ADAPTER_REDRAW_FLANGE_FOR_A_WHALE A1 |
| pipe runs with tees, crosses, dead ends in each of the four looks; a pipe beside a tank / machine; a hose on a pipe | PIPE_FITTINGS_REDRAW_NO_MORE_LADDERS A1 · PIPE_TANK_JOIN_FIX_SLIPS_UNDER_SKID A1 · PIPE_ENDS_BUILD_MEET_IN_THE_MIDDLE A2 |
| a 2x2 reel facing N and S, stored and laid, four looks; a Modern reel stored N/S/W | REEL_FACINGS_REDRAW_NORTH_SOUTH_OWED A1 · MODERN_REEL_SHADOW_FIX_BOX_TOO_BIG B2 |
| a flowing vs an empty hose, every look | HOSE_PLUMP_FIX_SKINNIER_WHEN_FULL A2 |
| a depth-4 pawn on a pit south row; a muffalo at the lip | PIT_LIP_OCCLUDES_OUTSIDE_1 A1 |
| tar / propane / water channels with liquid looks toggled off/on 3 times (`ProofWaterLook set:`) | LIQUID_LOOK_MATERIAL_OWNERSHIP_1 A1 (state read + frame) |
| FlowWorks Mod Settings window: every screen; the search box; per-section reset | FLOWWORKS_RESET_BUILD_TWELVE_SCREENS_MISSING A1 (L4, owner) · SETTINGS_SCREEN_KIT_1 A5 (screenshot) |
| GSS + Pyrelands settings windows: master off shades dependents; Reset asks first, Cancel changes nothing | SETTINGS_KIT_BUILD_GREY_SWITCHES_AT_LAST A2, A3 |
| owner_review_stage on a vanilla-biome map, and on RM_TheRot with `--any-biome` | WATER_LOOK_DIAGNOSE_GREY_ON_THE_ROT A1, A2 (`northstar/owner_review_stage.py`) |
| the wall faces D1..D4, a superdeep cell, a spiked D4 cell | EXCAVATION_WALL_ART_1 A1 (state), A3, A4 (frames, L3 judge) · FLOWWORKS_VISUAL_PRINCIPLES_1 A2 (state rows), A3 (judge) |

---

## 5. The long session and the hostile rows (fresh maps, quiet first, hostile last) — E ≈ 85 min

| # | command | rows → item criterion |
|---|---|---|
| 5.1 | `northstar/live_session.py` (B0-B10 on one fresh 250 map; `--dry-run` prints the block table) | M ~57 min. B1 v2 `X8c_lid_walker_drawn_at_ground` → PIT_LID_FIX_VICKY_PEEKS_THROUGH A2 · B3 liquid_checks L2/L4/L5/L6 → LIQUID_LEDGER_BUILD_NO_UNIT_LOST A4/A6/A7 · proof_hose realflow → HOSE_RULINGS_BUILD_THREE_REVERSALS_ONE_CARD A5, HOSE_ROUTE_FIX_TUNNELS_UNDER_WALLS A3 · B4 → THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY T6 (`B4_dehydration_rate`, 0.30 ± 0.03), HW1, T8 · B4 `B4_rail_unrailed_control` → FALL_GUARDRAILS_BUILD_REAL_OBJECT A3 (stays owed if the control never steps off: his ruling) · `timing.parked` / `timing.bystanders` → SESSION_HURT_DIAGNOSE_BRUISED_AT_THE_BELL A1 · B8 raid_trench → PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH · B9 owner save (L4 eyes) |
| 5.2 | `northstar/raid_trench_proof.py --direct --depth 8 --fresh-map` | `RAID_FILL_CAUSEWAY` → CAUSEWAY_DIAGNOSE_WAITS_AT_THE_LIP A1 · RAIDERS_TRENCH_BUILD_BREACH_AND_JUMP A3 · LADDER_PARITY A3 (with `LADDER_PARITY_BREACH_SCAR_REPAIR`) |
| 5.3 | `northstar/raid_trench_proof.py --direct --colony-ladders --fresh-map` | LADDER_PARITY A1 |
| 5.4 | `northstar/raid_trench_proof.py --carriers --fresh-map` | LADDER_PARITY A2 |
| 5.5 | `northstar/raid_trench_proof.py --direct --depth 4 --trees 6 --fresh-map` | **LADDER_PARITY A5 `LADDER_PARITY_RAIDER_FELLS_TREE` (NEW 99deb7e783; first live run)** |
| 5.6 | `northstar/underpass_raid_live.py --fresh-map` | SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD A9 gate (rides PIT_CLIMB) |
| 5.7 | Titans (needs HugeThings on the tier: add `HugeThings` for this step only, or skip): stage a dug 1-wide and 2-wide 4 m trench; `RM_TrenchStride.ProofStride` | TITAN_TRENCHES_WIRE_MIND_THE_GAP A5 (one call); A1-A4 have no row yet |

## 6. The 325x325 perf map — E ≈ 12 min

Start a 325 map by hand (no tool makes one), then `northstar/pipe_levelling_perf_proof.py --budget-s 900` →
PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL A3.

## 7. GREEN-MIN (a second cold load, last) — E ≈ 25 min

`modset_builder.py --tier flowworks --apply`, cold load (~22 s minimal), then
`python.exe src/RimMandrake/Utils/modcheck/cli.py run FlowWorks` (it REWRITES ModsConfig: restore with
`modset_builder.py --restore --apply` after). Covers FLOWWORKS_NORTHSTAR_GREEN_MINIMAL_1, FLOWWORKS_NORTHSTAR_TRIAL_1 A1/A4,
PIT_TEMPERATURE_SOFTENING_1 A5, SURFACE_RIVER_WEIRS_1 A3. GREEN_FULL_1 is DROPPED (owner card 2026-10-21: small list is enough).

**Sitting total E ≈ 4 h 30 min** (two cold loads, ~25 fresh maps, three save loads). Steps 1-3 alone: E ≈ 1 h 45 min.
`rimflow bridge release` the moment it ends; commit `infrastructure/state/ledger/events/BENCH.jsonl` by explicit path.

---

## 8. Owner sitting (L4; staged here, judged by him later, every image through a naive judge first)

DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS A3 · CANAL_LAKE_COLOUR A2 · HOSE_REEL_FIX_TURNS_WITH_THE_SHIP A2 · HOSE_RULINGS A4 ·
LIQUID_LEDGER A9 · GLOW_TANK_LIQUID_FEED_1 H1 · FLOWWORKS_CONTAINER_MATERIALS_1 A3 · PIT_TEMPERATURE A6 · WATER_ART_CANDIDATES A4 ·
FLOWWORKS_VISUAL_PRINCIPLES_1 A4 · EXCAVATION_WALL_ART_1 A5 · SUSPENSION_UNDERPASS A8 (joint screenshot) · FALLEN_WIRE_SHOCK_1 H1 ·
PIPE_FAUCET A3 · PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS A5 · PIT_PAWN_FIX_CARRIES_A_SUNNY_SQUARE A2 (save e boar pit) ·
REEL_LINK_FIX_IGNORES_THE_OBVIOUS_PORT A2 · REEL_NOZZLE_FIX_COUPLER_HIDES_UNDERNEATH A2 · WEIR_CATCH A4 · WEIR_LOOK A4 ·
POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD A8 · FLOWWORKS_RESET_BUILD_TWELVE_SCREENS_MISSING A1 · FLOWWORKS_NORTHSTAR_TRIAL_1 A3 ·
FLOWWORKS_BARS_JUDGE_FIVE_IN_ONE_SITTING · WATER_DEPTH_RESKIN_HE_LOOKS_FIRST.
**Owner present only (flyer / joint):** RIVER_TOGGLE_PROOFS A7 (flyer over a river), GRAVSHIP_WIRES_SURVIVE_LAUNCH_1 A3 (joint
flight). LADDER_PARITY A8 is a judge-agent ruling (delegated: fact/taste), not a bridge step.

## 9. Owed live criteria with NO runnable row yet (not dischargeable in this run without new work)

| item | crit | what is missing |
|---|---|---|
| LADDER_PARITY_BUILD_NO_KEYS_REQUIRED | A6 (escape half) | prisoner-escape row: filed PIT_ESCAPE_PROVE_LADDER_LEFT_DOWN |
| TITAN_TRENCHES_WIRE_MIND_THE_GAP | A1-A4 | a titan spawn on a HugeThings tier; only A5 is one call |
| HEAT_BUDGET_PREFIX_MEND_LATE_CELLS_STARVE / NATURAL_HEAT_CACHE_PROVE_STALE_DAYS | A2 | a hot-pool room past the heat budget (RM_LiquidHeat.ProofHeat/ProofRescan) |
| FLUID_PALETTE_EXHAUSTION_MEND_KEY_ZERO, TAR_COOLING_GLASS_MEND_ENGINE_CELLS, HAZARD_TAR_TERRAIN_FROM_LIQUIDS_1 | A2 / A1 | selftest only; no live row |
| PIPE_POLE_SWITCH_DECIDE_HOSTAGE_TO_WIRES | A2, A3 | menu visibility needs a screenshot read (list_architect_designators' `visible` is not Designator.Visible) |
| MISSION_TANK_GOAL_REWIRE_TO_DEST | A2 | `player_missions.py` chain report, never run live |
| CORD_GRAPH_TOPOLOGY_REVISION_1 | A2 | SwayHash/RippleHash before/after read on a busy map: no script names it |
| ASH_FIELD_FIX_FORGETS_THE_WATER | A2 | ProbeCell watered across save/load: no row |
| LAVA_LIQUID_BUILD_PROMISED_BY_CARD | A4 | a Forge map census of RM_PumpingStation_Wrecked spawns |
| WORLDMAP_LIQUID_TAGS_1 | A1 | a landing quicktest of the canonical Ash'karr save (a different load) |
| PEN_ANIMALS_UNSTICK_STATUES_LEARN_TO_WALK | A1, A2 | Pyrelands keeper save + `human_review.py --release-pens` (a Pyrelands load) |
| SUSPENSION_GRATE_BUILD_LET_THE_FIRE_UP | A4 | slime-on-grate slip census: "no script row yet" |
| FALLEN_WIRE_SHOCK_1 | A5 | a live end in a chemfuel puddle / canal oil: GSS row not written |
| JAWA_DROWNING_PROVE_RAT_SIZED_IN_SHALLOWS, TANK_SHADOW_DIAGNOSE_DRIFTS_OFF_THE_SKID, RIVER_SCENES_BUILD_WALKTHROUGH_WITH_CAPTIONS, CANAL_OBJECTS_SHEET_BUILD_POSES_AND_STYLES, PIT_SUPERDEEP_COLLAPSE_1 | — | proposed/ready, no manifest yet: build work before a live check |
| HOSE_GIRTH_TUNE_MUCH_THINNER, PIPE_GIRTH_TUNE_HALF_AS_THICK | — | `doing game-up` under their owners: a look once deployed (fold into §4 if built by then) |

Also pending: SUSPENSION_BASE_REWIRE_COVERS_STEP_OUT A2 is a code review (`code_review_status.py check`), not a bridge step.
