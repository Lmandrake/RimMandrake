# FlowWorks live sitting plan — one bridge sitting, every owed FlowWorks live criterion

Written 2026-10-23 (FOUNDRY proof-coverage helper), offline, from the ledger (`rimflow queue FOUNDRY --acceptance`, filtered to
FlowWorks: **142 owed criteria on 90 built/validated items**: 37 L1, 79 L2, 2 L3, 17 L4, 7 GREEN). For the bridge driver.
Times marked **M** are measured from the scripts' last result JSONs (2026-10-22 belt); **E** are estimates. Nothing here has
run against this sitting's DLL.

## 0. Before the load (deploy)

1. Commit-state check: deploy only **committed** FlowWorks (`git show HEAD:src/RimMandrake/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll`
   exported, and `FW_REPO_DLL=<export>` set for `live_session.py` B0 / `validation_v2.py`: other helpers rebuild the DLL in the
   working tree). `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod FlowWorks` (plan) then `--apply`.
2. Also deployed: the JawaBench companion (`bridgetools/build.py`), Gimme Some Slack, `mandrake.rm.biomes` (for the tier),
   **LuminousPigment** (the glow-tank rows only).
3. Tier: **`fw_gss_sitting`** (Utils/modset_builder.py) **+ `mandrake.rm.luminouspigment`**. One cold load. All five DLC.
   If LuminousPigment cannot ride along, run step 3 on its own `luminouspigment` swap at the end (~70 s launch, M 44-70 s).
4. `rimflow bridge take --for "FlowWorks owed-criteria sitting"`; release the moment the sitting ends.
5. Every step below starts `--fresh-map` (a new quicktest map, main menu first) unless it says otherwise; the clean saved site
   (`Utils/modcheck/test_site_saves.py load calm`) is equivalent for steps that do not say `--fresh-map`.

Every row: PASS/FAIL/UNMEASURED with MOD/SITE/HARNESS. **Only a PASS or a MOD FAIL is a verify**; UNMEASURED is not.
Verify line (the config is B0's / the script's measured `min-N`, never a tier label):

    rimflow verify <ITEM> --criterion <C> --result pass|fail|partial --config min-<N> --evidence <result.json>

A row marked *partial* below discharges only part of its criterion: record `--result partial`, never `pass`.

## 1. The order (cheapest first; map-wide and hostile last)

| # | run (python.exe, repo root) | time | rows -> `--criterion` it verifies |
|---|---|---|---|
| 1 | `northstar/sitting_gaps_proof.py --fresh-map` (NEW 2026-10-23; selftest `selftest_sitting_gaps_proof.py`, 23 mutation faults) | E 6-8 min (~3,600 ticks; T30 waits up to 3,000) | `RIVER_LAYER_REDRAWS_CLEAN` -> FLOWWORKS_RIVERCOLOR_FIX_DICT_SELF_ENUM A1 · `RAILING_HAS_STUFF` -> RAILING_MATERIAL_FIX_MADE_OF_NOTHING A1 · `FAUCET_TAB_PIPE_ONLY` -> PIPE_FAUCET_BUILD_TAP_NAME_NOW_FREE A1 · `T30_pipe_faucet` -> PIPE_FAUCET_BUILD_TAP_NAME_NOW_FREE A2 · `FAUCET_LOOKS_RESOLVE` -> FAUCET_REDRAW_BORROWED_BLEED_WELL A2 · `FAUCET_TAKES_MODERN` -> FAUCET_REDRAW_BORROWED_BLEED_WELL A3 *partial* (clamp-on-axis is def data) · `GUARDRAIL_ATLAS_RESOLVES` -> GUARDRAIL_ART_RESKIN_BORROWED_FENCE A2 · `REEL_FACINGS_LAY_ALONG_AXIS` -> HOSE_REEL_FIX_TURNS_WITH_THE_SHIP A1 *partial* (no turning gravship) · `S3_HOSES_ON_BARE_GROUND` -> HOSE_PATHING_REPAIR_SCENIC_ROUTE_PLEASE A1 · `SETTINGS_SEARCH_FINDS_ROW` -> SETTINGS_SEARCH_FIX_LABELS_NOT_FOUND A1 · `CANAL_LAKE_ONE_DEF` -> CANAL_LAKE_COLOUR_UNIFY_TWO_BLUES A1 (L3: the row reads one terrain def; an Opus judge, not the driver, reads its frame `shot` and decides the verify) · `CONVERTER_BIG_RECIPE_RUNS`, `REACTOR_NEXT_REACTION_RUNS`: **UNMEASURED/SITE by construction** (see §3) — no verify |
| 1b | `northstar/pond_pump.py --drain --fresh-map` (another helper's rows, 67633f878) | E 5 min (M 513 s for the refill variant) | `POND_PUMP_drains_to_last_dl` -> POND_PUMP_FIX_LAST_DROP_COUNTS A2 · `POND_PUMP_dry_squares_stage` -> A3 |
| 2 | `northstar/suspension_settings_live.py --fresh-map` | M 9 s | `SB_settings_off_no_button` -> SUSPENSION_BUTTONS_DIAGNOSE_STILL_SHOWING A1 and SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS A7 (with `SB_settings_off_never_breaks`) |
| 3 | `northstar/glow_tank_live.py --fresh-map` (needs LuminousPigment) | M 139 s | `GLOWTANK_SALT_DRAWN_ONE_UNIT` -> GLOWTANK_DRINK_DIAGNOSE_DRY_BESIDE_THE_SEA A1 and GLOW_TANK_LIQUID_FEED_1 A2 |
| 4 | `northstar/liquid_checks.py --only L5 --fresh-map` | M 48 s | `L5_switched_off_hose_spills` -> SPILL_DIAGNOSE_TEN_THOUSAND_GONE_DRY A1 (and LIQUID_LEDGER_BUILD_NO_UNIT_LOST A6, also step 13) |
| 5 | `northstar/trench_crossing_live.py --fresh-map` | M 58 s | -> TRENCH_CROSSING_FIX_DOWN_ACROSS_AND_UP A3 |
| 6 | `northstar/walk_gaps_proof.py --fresh-map` | M 313 s | `PORTS_*` -> FLOWWORKS_PUMP_PORTS_REBUILD_ONE_PER_SIDE A4 · `PONDS_HOSE_LEVEL` -> PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL A4 · `PONDS_DIFFERENT_LIQUIDS_NO_MIX` -> A5 · `PORTS_CORNER_REFUSED` -> PROOF_REELS_FIX_STILL_STAGED_WEST A3 (half; the other half is step 7) |
| 7 | `northstar/pipe_levelling_perf_proof.py --rehearsal` (same map as 6, no new map) | E 5 min | -> LEVEL_REHEARSAL_FIX_POURS_ON_FULL_PONDS A1 · PROOF_REELS_FIX_STILL_STAGED_WEST A3 (other half) |
| 8 | `northstar/drawbridge_proof.py --fresh-map` | M 231 s | -> DRAWBRIDGE_LOOKS_FIX_HIS_PICKS_OUTRANK A1 |
| 9 | `northstar/suspension_bridge_proof.py --fresh-map` (+ `--river/--lake/--sea x1,z1,x2,z2` on a map that has them) | M 236 s | WAT_RIVER_CROSS -> SUSPENSION_WATERS_BUILD_MAY_BACKTRACK A1 · WAT_FLOOD_DAMAGE -> A3 · LOOK_<Look>_RESOLVES -> SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS A8 (eyes too) |
| 10 | `northstar/water_looks_proof.py --fresh-map` | E 4 min | -> WATER_ART_CANDIDATES_BUILD_WHAT_HE_APPROVED A1, A2, A3 |
| 11 | `northstar/legacy_fill_live.py --fresh-map` | E 3 min | -> EXCAVATION_LEGACY_MIGRATION_FLAG_1 A1, A2 |
| 12 | `northstar/deep_lake_proof.py --fresh-map` | E 6 min | `DL_shallow_dries_first`, `DL_colonist_free_in_bowl`, `DL_refill_restores_exact_shape` -> DRAWDOWN_DIAGNOSE_THIRTEEN_BEFORE_TWELVE A1 |
| 13 | `northstar/live_session.py` (full; B0-B10 on one fresh 250x250 map; its own `--dry-run` prints the block table) | E ~57 min (its catalog: 3,416 s + load) | its catalog (`--list`); for the owed list: B1 v2 `X8c_lid_walker_drawn_at_ground` -> PIT_LID_FIX_VICKY_PEEKS_THROUGH A2 · B3 liquid_checks L2/L4/L5/L6 -> LIQUID_LEDGER_BUILD_NO_UNIT_LOST A3/A5/A6/A7 · proof_hose realflow -> HOSE_RULINGS_BUILD_THREE_REVERSALS_ONE_CARD A5 · B4 `B4_rail_unrailed_control` FALL_GUARDRAILS A3 stays OWED (his ruling, §3) · B8 raid_trench_proof -> PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH raid · B9 owner save (L4 eyes only) · B10 thirst tail. SESSION_HURT_DIAGNOSE_BRUISED_AT_THE_BELL A1 reads its `timing.parked` / `timing.bystanders` and the logs' GovernorStops |
| 13b | `northstar/extension_proof.py --live --current-map` straight after 13's B1 (same map) | E 6 min | -> FLOWWORKS_CHECKOUT_SCOPE_1 A2 (both results recorded) · PIT_TEMPERATURE_SOFTENING_1 A2-A4 · FLOWWORKS_CONTAINER_MATERIALS_1 A2 · FLOWWORKS_QUARRY_DIGGING_1 A3/A4 (its plots; rows it cannot reach read UNMEASURED) |
| 14 | `northstar/raid_trench_proof.py --direct --depth 8 --fresh-map` (hostile: after every quiet row) | E 6 min | `RAID_FILL_CAUSEWAY` -> CAUSEWAY_DIAGNOSE_WAITS_AT_THE_LIP A1 and RAIDERS_TRENCH_BUILD_BREACH_AND_JUMP A3 |
| 15 | `northstar/pipe_levelling_perf_proof.py` on a **325x325** map (two 40,000-cell basins, 200 links) | E 10 min | -> PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL A3 |
| 16 | the walkthrough saves (maps C and R): `northstar/joint_check.py --all-maps --crops Transient/joint_gate/<stamp>`, then `northstar/scenarios_map.py --save` with the gate red and green | E 8 min (two loads) | -> JOINT_GATE_HARDEN_TRUST_THE_DRAWN_BOX A2, A3 · JOINT_CHECK_WIDEN_PIPE_STUBS_UNSEEN A2 · HOSE_CROSSING_FIX_FLAT_AS_A_PANCAKE A2 · HOSE_BUILDINGS_FIX_BATTERY_HIDE_AND_SEEK A2 · HOSE_JOINTS_REPAIR_ENDS_MISS_THE_NOZZLES A3 · CENTRE_CELLS_FIX_WALK_THROUGH_WALLS A2; the same load's map-C captures (zoomed, each judged before anyone else sees it) for HOSE_BEND_FIX_SHAVES_WALL_CORNERS A2, HOSE_LEADIN_FIX_STUB_IN_THE_CANAL A2 |

**Sitting total: E ~2 h 10 min** of bridge time (one cold load, ~13 fresh quicktest maps at 2-8 s each, two save loads), most
of it step 13. Steps 1-12 alone: E ~45 min and reach 35 criteria (2 of them partial).

Between steps: `jawa/kill_hostiles`, `jawa/incident_queue_clear`, feed + quench colonists (Food, Rest, **RM_Thirst**), and
keep the start colonists drafted off the site — `live_session.py` and `sitting_gaps_proof.py` now do this themselves
(SESSION_HURT_DIAGNOSE_BRUISED_AT_THE_BELL); the stand-alone scripts above draft their own. A GovernorStop naming a pawn the
row did not spawn is SITE, never a MOD verdict.

## 2. Owner eyes (L4) staged in the same sitting, judged later

live_session B9's owner save carries his looks; these L4 criteria are **not** verified by the driver: CANAL_LAKE_COLOUR A2,
GUARDRAIL_ART A4 (sheet), PIPE_FAUCET A3, HOSE_REEL A2, HOSE_RULINGS A4, LIQUID_LEDGER A9, GLOW_TANK_LIQUID_FEED H1,
FLOWWORKS_CONTAINER_MATERIALS A3, PIT_TEMPERATURE A6, WATER_ART A4, FLOWWORKS_VISUAL_PRINCIPLES A4,
SUSPENSION_UNDERPASS A8 (joint screenshot), RIVER_TOGGLE A7 (flyer: owner present only), FLOWWORKS_NORTHSTAR_TRIAL A3,
FLOWWORKS_RESET_BUILD_TWELVE_SCREENS_MISSING A1, CHILL_AIR_PUMP_1 H1. Every image goes through a naive judge first.

## 3. Findings this plan rests on (filed)

- **FLOWWORKS_CONVERTER_FIX_BLOCKED_STARVES_REST A1 and FLOWWORKS_REACTOR_FIX_STUCK_ENDS_SHIFT A1 cannot be staged from
  shipped content** (def census in `sitting_gaps_proof.def_census`, 2026-10-23): every shipped conversion makes
  RM_Liquid_FreshWater (tar refines to chemfuel alone), so no converter has a small recipe whose output can be full while a big
  recipe's has room; the only RM_LiquidReactionDef is RM_Reaction_TarAcid. Both fixes are proved offline (Gpt1016 selftest).
  The criteria need a re-scope or a test-only def (noted on both items).
- **FALL_GUARDRAILS_BUILD_REAL_OBJECT A3** waits on his ruling: the unrailed control never steps off a lip (live_session B4).
- **The four reworded depth bars are measured by rows that still stop at 2 m** (LADDER_ROWS_WIDEN_STILL_COUNT_TO_TWO).
- SETTINGS_SEARCH, faucet, river and the rest above had **no live row before 2026-10-23**; their rows are new and owed their
  first run: expect harness/site findings on the first pass and classify each.

## 4. Owed criteria with NO live row yet (not in this sitting)

| item | crit | why no row |
|---|---|---|
| TITAN_TRENCHES_WIRE_MIND_THE_GAP | A1-A5 | needs HugeThings on the tier and a titan spawn; RM_TrenchStride.ProofStride exists (A5 is a one-call row) |
| HEAT_BUDGET_PREFIX_MEND_LATE_CELLS_STARVE / NATURAL_HEAT_CACHE_PROVE_STALE_DAYS | A2 | a hot-pool room scene past the heat budget (RM_LiquidHeat.ProofHeat/ProofRescan); not written |
| LIQUID_LEDGER_BUILD_NO_UNIT_LOST | A4 | NS_intake_needs_pump has no live driver (live_session catalog) |
| PIPE_POLE_SWITCH_DECIDE_HOSTAGE_TO_WIRES | A2, A3 | architect-menu visibility: list_architect_designators' `visible` is not Designator.Visible (SUSPENSION_BUTTONS trap); needs a screenshot read |
| MISSION_TANK_GOAL_REWIRE_TO_DEST | A2 | player_missions.py chain report; not run live |
| LIQUID_LOOK_MATERIAL_OWNERSHIP_1 | A1 | looks toggle round trip; ProofWaterLook `set:` exists, no row |
| FLUID_PALETTE_EXHAUSTION_MEND_KEY_ZERO, TAR_COOLING_GLASS_MEND_ENGINE_CELLS | A2 | selftest only (call sites); no live row |
| GLOW_TANK_SEED_LIVE_SOW_1 | A2 | the WorkGiver sow route; no row |
| PIT_LIP_FIX_BOAR_HANGS_OUT A2, PIT_LIP_OCCLUDES_OUTSIDE_1 A1, HOSE_PLUMP A2, MODERN_REEL_SHADOW B2, TANK_LANE/TANK_NS/TANK_SOUTH/UNDER_COUPLER/CARGO_UPPER A2, PIPE_ENDS A2, PIPE_TANK_JOIN A1, PUMP_ART A2, RIVER_MUFFALO A1 | look | live LOOKS: a zoomed capture per station (review_map stations) + a naive judge; staged by `review_map.py`, not a row |
| RIVER_TOGGLE_PROOFS_BUILD_ELEVEN_UNCLAIMED | A1-A6 | a river map (river_site.py); validation.py river chains, a separate river-tile load |
| SURFACE_RIVER_WEIRS_1 A3, FLOWWORKS_NORTHSTAR_* (GREEN-MIN/FULL), PIT_TEMPERATURE A5 | GREEN | modcheck `run` / `record` on the minimal and full lists, after the bars are validated |
| SETTINGS_KIT_BUILD_GREY_SWITCHES_AT_LAST | A2, A3 | GSS/Pyrelands windows (not FlowWorks rows) |
| TESTENV_* (4) | A1 | test-environment receipts: read from the steps above (site_calm receipts), no row of their own |
