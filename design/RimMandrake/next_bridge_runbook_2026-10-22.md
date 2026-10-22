# Next bridge sitting: one runbook (written 2026-10-22, offline)

FOUNDRY helper, offline only. I ran nothing live. Every expectation below is pre-registered, so a reading
that differs is a finding. Sources: `rimflow next --acceptance --seat FOUNDRY`, `rimflow show <ID>` per item,
`infrastructure/state/handoffs/FOUNDRY_HANDOFF_202610221110.md`, `design/RimMandrake/gss_ship_path_2026-10-22.md`,
and the scripts' own usage blocks. Each criterion's text is cut short in `next`. **At the sitting, re-read the
full A-line with `rimflow show <ID>`: the ledger line is the bar, not this file.**

**Shape: three loads.** Load 1 (`fw_gss_sitting`, 14 mods) covers FlowWorks and GSS. Load 2 (`desertplants`,
16 mods) covers Webwork, The Rot and the wound link. Load 3, the full list, is the restore of his list, and the
GREEN-FULL harvest rides on it for free. Loads 1 and 2 are minimal lists: a boot to the bridge token takes
about 1 to 2 minutes, plus about 80 s for each quicktest. Load 3 is a cold load of about 15 minutes, and on a
first launch after a reboot it can take 25.

Load 2 exists only because `ROT_WOUNDLINK_FIX_DROPPED_AT_THE_DOOR` A2 needs `mandrake.rsw.swbestiary`, which
`fw_gss_sitting` does not carry. Webwork and The Rot are composed into `mandrake.rm.biomes`, so they would ride
Load 1 too. I moved them to Load 2 to keep Load 1's records on the tier that BENCH's FlowWorks/GSS records
already name. If Load 2 has to be dropped, run the Webwork and Rot rows on Load 1 and leave WOUNDLINK A2/A3 owed.

## Already clear (do not schedule)

| item | state | why |
|---|---|---|
| `WALL_REACH_TUNE_REBUILDS_TENFOLD` (REACH_THROTTLE_HOLDS) | done, closed at ee9fa61fbc | BENCH belt: `reach_map_proof --fresh-map` 6/6 PASS incl. REACH_THROTTLE_HOLDS, and a residual soak of ~98 builds per 1000 ticks (`src/RimMandrake/FlowWorks/northstar/reach_map_proof_result_20261022T1220_belt.json`). The pocket-grid follow-up 67dec5bec is an ancestor of the verified sha. |
| `FISH_ROLL_MEND_PONDS_BORN_BARREN` | done, closed at ee9fa61fbc | `live_session --only B0,B4,B7`: B4_reservoir_fish_rolled PASS on a temperate map. |
| `LADDER_HOSE_DIAGNOSE_SIPS_NOTHING` | done | lines_proof 11/11 PASS on c5c0f047ca. |
| `PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE` A4-A10 | verified L2 | lines_proof rows all PASS. A1-A3 are left; see P6. |

## 0. Prerequisites

### Offline, before the sitting (no bridge needed)

| # | what | why | est |
|---|---|---|---|
| P1 | **DONE 2026-10-22** (de881ea04). `src/RimMandrake/Webwork/northstar_plan.py` and `src/RimMandrake/TheRot/northstar_plan.py` exist (`USE_SUITE`, `EXPECT_MODS = ("mandrake.rm.biomes",)`); both mock-run through `northstar_driver/cli.py run --mock ... --mock-skip-site` and `--chains`. The generic driver mock reads NOT GREEN (it answers every tool alike, as for CrackedLands/Greentide); the per-chain proof is each `validation.py --mock` (below). | Without a plan the only live route to their chains was `modcheck run`, which **rewrites the live ModsConfig.xml**. | done |
| P2 | **DONE 2026-10-22 offline** (source 051b1d0b8, DLL 195c2fe9b, script b5a090cdc). Static `ProofWaterLook "x,z"` in FlowWorks, plus `src/RimMandrake/FlowWorks/northstar/water_looks_proof.py` rows A1-A3 (pits staged through `ProofStageBasin`), with `--mock`/`--offline-gate` and `selftest_water_looks_proof.py`: all 9 rows go red against their planted defects, and A3 records stale=True/False as data. **Owed in the deploy window:** deploy the rebuilt FlowWorks DLL. | `WATER_ART_CANDIDATES_BUILD_WHAT_HE_APPROVED` A1-A3 | done (deploy owed) |
| P3 | **DONE 2026-10-22, no new tool needed.** `jawa/pawn_flight action=report` already exists (read-only, `JawaBenchFlightTools.cs`, f707e69f1). `TheRot/validation.py` dustveil/`flight_tracker_state_read` now pauses, proves the clock is still (two `ticksGame` reads), spawns `RM_Dustveil` plus a non-flier control `RM_Chittik`, reads both, vanishes both (`pawn_force_incapacitate action=vanish`; `destroy_batch` never removes pawns) and voids the read if a tick moved. `python3 src/RimMandrake/TheRot/validation.py --mock` proves it FAILs on a grounded moth and reads UNMEASURED on a flying control or a running clock. UNMEASURED: whether the deployed JawaBench DLL carries `pawn_flight` (BlueDesert's chain calls it; check `jawa/pawn_flight` answers at 2.0). | `DUSTVEIL_FLIGHT_BUILD_A_MOTH_THAT_WALKED` A2 | done |
| P4 | **DONE 2026-10-22 offline** (aae39486d). Cause: a tank is a network member, not a conductor, so each reel was its own component with one open end and never linked (`linked: False`). The PONDS rig now joins the reels on a pipe run (x12, z2..5), the geometry is checked offline, and the coupling is read back live before the levelling window. In `selftest_walk_gaps_proof.py`, the old tank layout and a cut pipe read SITE/UNMEASURED and the fixed rig links. **Still broken:** `pipe_levelling_perf_proof.py` uses the same tank layout (row 1.11/P5). | `PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL` A4/A5 | done |
| P5 | Find or make a 325x325 fixture. `pipe_levelling_perf_proof.py` says no bridge tool makes one. Look for a 325 save first (UNMEASURED whether one exists; none in the Saves folder carries "325" or "levell" in its name). | `PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL` A3 | 15 min to look |
| P6 | `PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE` A1-A3 are **C# SelfTest cases** (LineCrossing, HoseBand_P2_pit_cover_carries_no_hose, LineReadout_P9, PipePoleGravship_P8), filed at L1. FlowWorks has no in-game SelfTest entry point. Run the SelfTest from the repo's `bin/Release/net8.0`: the staged build folder shows 14 false FAILs (lesson). It is BENCH's item, so ask BENCH whether A1-A3 can be re-levelled to L0. Do not invent a live route. | no bridge needed | 10 min |
| P7 | Pre-flight greens: `python3 src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py --offline-gate`, `python3 src/RimMandrake/FlowWorks/northstar/proof_hose.py --offline-gate`, `--mock` for `sheet_overflow_proof.py`, `walk_gaps_proof.py`, `pipe_levelling_perf_proof.py` and `water_looks_proof.py`, and STATIC plus `--mock` for `TheRot/validation.py` and `Webwork/validation.py` (all four PASS 2026-10-22; the mocks plant one defect per row and require it to read FAIL, or UNMEASURED when it blinds the instrument). | A red offline gate refuses `--live`. | 5 min |
| P8 | `python3 src/RimMandrake/Utils/modcheck/required_checks.py`, run alone (it hung once under a helper). | Handoff: the `script_sha` entries are stale for the touched validation.py files. | 5 min |

### Game down, bridge held (the deploy window)

1. `rimflow bridge take --for "next-bridge runbook 2026-10-22: deploy + loads 1-3"`. Then
   `./game --why "deploy window for the 2026-10-22 runbook" down`. DLLs cannot be written while the game runs.
2. Run each deploy as a **dry run first** and read the plan: refuse any `-` line, and refuse another seat's
   files (`rimworld-deploy` skill). Then run the same command with `--apply`, one mod at a time:
   ```
   python3 src/RimMandrake/Utils/deploy_custom_mods.py --compose biomes          # Biomes composite: Webwork, TheRot, CreatureBehaviors, EnvironmentalHazards, Pyrelands ... ; Wave-1 renames (SleepingIce, Wastes)
   python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod FlowWorks           # water looks DLL c5bbf3239 + later, sheet overflow, P2 hook
   python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod GimmeSomeSlack      # pipe-pole switch e1cebd84d; dry run said "in sync" 2026-10-22
   python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod UtinniPatches
   python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod Ninefold
   python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod Armoury
   python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod SWBestiary          # src/RimStarWars/SWBestiary; WOUNDLINK patches Durrok/Mullgoth if they live there
   ```
   If `Pyrelands` still deploys on its own, rather than composed, the dry run says so: deploy it on its own.
   The handoff also asks for the old Wasteland and NightsideIce game folders to be removed after the Wave-1
   rename. Check that in the plan: it will show them as orphans. Removing them is a deliberate step, never a
   `-` line taken without reading it.
3. P3's JawaBench companion: `build.py` and its deploy guard (`rimbridge-companion` skill).
4. Check every committed DLL: the `.srchash` must match the deployed file (`deploy_custom_mods.py` reports it).

Estimate: 15 to 20 min.

## 1. Load 1: `fw_gss_sitting` (14 mods), FlowWorks + GSS

Boot: `python3 src/RimMandrake/Utils/modset_builder.py --tier fw_gss_sitting --apply`, then launch through Steam
(`src/RimMandrake/bridgetools/launch_and_wait.sh`; it succeeds only on a current-process receipt). Then
`./game --why "load 1 fw_gss_sitting" up`.

Run `python3 src/RimMandrake/Utils/belt_watchdog.py --watch 300` under a Monitor for the whole sitting. Every
python.exe proof runs from the repo root, piped through `tr -d '\r'`.

Order: cheapest first. Anything that ruins a map runs after the rows that need that map clean.

| # | item / criterion | command | expected state read | est |
|---|---|---|---|---|
| 1.0 | tier truth | `jawa/running_mods` count, and the FlowWorks/GSS assembly sha | 14 mods; the sha equals the deployed `.srchash` | 1 min |
| 1.1 | GSS fresh proof (gss_ship_path) | `timeout 1200 python.exe src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py --live --no-shots` (loads the calm site save itself) | S12a, B12, B13, A8 and S12c PASS. S12d PASS, with `csavenow.pendingAtSave` truthy and `afterLoad.staged == afterLoad.ctrl`, both of length 1. Z PASS across both loads. If S12d reads UNMEASURED ("D4 save/load did not complete"), that is HARNESS: fix it, do not record. | 7 min |
| 1.2 | record GSS | `python3 -m modcheck.cli record GimmeSomeSlack --result src/RimMandrake/GimmeSomeSlack/northstar/proof_all_<stamp>.json --tier fw_gss_sitting` (run from `src/RimMandrake/Utils`) | PENDING-OWNER-REVIEW or GREEN | 1 min |
| 1.3 | `PIPE_POLE_SWITCH_DECIDE_HOSTAGE_TO_WIRES` A2, A3 (L1) | Same calm map. Place two `RM_PipePole` within range (dev spawn), then flip `AerialSettings.enabled` and the FlowWorks pipe-pole switch with `jawa/mod_settings_field`. Read: the Architect tab screenshot (does the designator show), the span drawn (screenshot), a new pole auto-links (`CompAerialAnchor` link count). | A2, with the power master OFF and poles ON: the pole is in the menu, spans draw, a new pole links. A3, with poles OFF and the master ON: the pole leaves the menu and its spans stop drawing. Restore both defaults and read them back. | 5 min |
| 1.4 | fresh quicktest | `rimworld/go_to_main_menu`, then `rimworld/start_debug_game_ready` (late reply: do not retry; poll `jawa/list_pawns`) | a Playing map | 2 min |
| 1.5 | `LIQUID_LEDGER_BUILD_NO_UNIT_LOST` A4/A6/A7, carrying `HOSE_RULINGS_BUILD_THREE_REVERSALS_ONE_CARD` A5 | `python.exe src/RimMandrake/FlowWorks/northstar/proof_hose.py --live --only realflow,hose` | Pre-register first. NS_intake_needs_pump: an Intake end moves nothing without a pump. NS_hose_carries_real_units: the round trip conserves. A switched-off hose spills at its open end. A hose into another faction's tank is spotted within 12 cells, at 2 goodwill/day. The 2026-10-19 min-11 run FAILed on realflow: classify each FAIL as MOD, SITE or HARNESS before any re-run. | 8 min |
| 1.6 | `HOSE_PLUMP_FIX_SKINNIER_WHEN_FULL` A2 (L2) | The same run's `H6_plump_within_transition`, then `python.exe src/RimMandrake/FlowWorks/northstar/owner_review_stage.py --only hoses --no-save`. Read the wide/close shots (`Transient/fw_hoses_walk/…`). | In every look a plump hose is at least as wide as an empty one (measure the pixel band in the image; never infer it from the exit code) | 4 min |
| 1.7 | `HOSE_RULINGS_BUILD_THREE_REVERSALS_ONE_CARD` A2 (L2, was partial) | Click the pipe build button with `python3 src/RimMandrake/Utils/system_click.py <x> <y>` (no bridge verb reaches `PipeLook.Pick`). Pick a look. Read the ThingStyle at the blueprint, the frame, the building, and after a save/load. Then "whole connected run". | A four-look float menu. The picked look survives all four stages. An unstyled pipe draws the default look. The run restyles. | 6 min |
| 1.8 | `PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL` A4, A5 (L2) | `python.exe src/RimMandrake/FlowWorks/northstar/walk_gaps_proof.py --fresh-map --only PONDS_HOSE_LEVEL,PONDS_DIFFERENT_LIQUIDS_NO_MIX --level-ticks 6000` (after P4). 🔴 Do **not** run the TRAVEL_*FLYER* rows. Flyers are not this runbook's business. | A4: `linked: True`, `levelMoves > 0`, surfaces within 1 cm, the hose reads "Levelling: flowing" then "level". A5: water and oil exchange nothing, and the readout says "different liquids never mix". `linked: False` again means HARNESS or SITE, never a pass. | 8 min |
| 1.9 | `WATER_ART_CANDIDATES_BUILD_WHAT_HE_APPROVED` A1, A2, A3 (L1) | `python.exe src/RimMandrake/FlowWorks/northstar/water_looks_proof.py --fresh-map` (after P2). Fallback without P2: `owner_review_stage.py --only shallows --no-save` plus a 10 m pit, read from screenshots, which leaves A3 owed. | A1: 5 m and deeper reads navy, 10 m and deeper darker; terrain is still WaterDeep; the setting OFF hides it. A2: below-lip water shows a N/W band that widens with the gap; brim-full shows none; OFF hides it. A3: draw down across 5 m and 10 m with no terrain write. **Record whether the tint goes stale** (that is the question A3 asks; either answer is data, and "stale" files a bug). | 12 min |
| 1.10 | `CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED` stage-4 rows (BENCH's build, through `OVERFLOW_DIAGNOSE_FIRST_WET_RUN`) | `python.exe src/RimMandrake/FlowWorks/northstar/sheet_overflow_proof.py --fresh-map` (it has the 9640e958cc rain fix) | RAIN_FULL_CANAL_SPILLS_SHEET, SHEET_RETURNS_TO_PIT and the ledger balance now PASS. The 5 that passed earlier stay PASS. 🔴 Afterwards read `sheetOverflowEnabled == False`: the 2026-10-22 run left the shipped-OFF switch ON when the perf call went INDETERMINATE. Skip this row if BENCH already ran it at a newer sha (`rimflow show OVERFLOW_DIAGNOSE_FIRST_WET_RUN`). | 12 min |
| 1.11 | `PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL` A3 (L1 perf) | `python.exe src/RimMandrake/FlowWorks/northstar/pipe_levelling_perf_proof.py --rigs 200 --calls 20` on the 325x325 map from P5. On a smaller map every row reads UNMEASURED/SITE. `--rehearsal` proves the harness only and is never the measurement. | `RM_Levelling.Tick` time and managed-heap delta are recorded for 200 links over two 40,000-cell basins (no bar number is set: it is a measurement) | 10 min + map |
| 1.12 | Owner keeper save (no owner needed now) | `python3 src/RimMandrake/Utils/save_guard.py run --current-slot none -- python.exe src/RimMandrake/FlowWorks/northstar/owner_review_stage.py --only shallows,hoses --save-name FW_owner_look_<date>` plus a 10 m pit | One named save for rows 3.1 to 3.3, kept until he says delete. Back up the Saves folder first. | 6 min |

Load 1 total: about 75 to 90 min of driving after a boot of about 2 min. Before leaving the load, check the
settings defaults are restored: pipe poles, the power master, sheet overflow and water looks.

## 2. Load 2: `desertplants` (16 mods), Webwork, The Rot, wound link

Boot: `python3 src/RimMandrake/Utils/modset_builder.py --tier desertplants --apply` (the plan dry-ran clean
offline 2026-10-22: 16 mods, biomes + rut.patches + swbestiary + proximityhatch + weathersuite). Launch, then
`./game --why "load 2 desertplants" up`, then a quicktest.

Chains run through the P1 plans, so no ModsConfig is rewritten:
`python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod <Mod> --plan src/RimMandrake/<Mod>/northstar_plan.py --chains <a,b>`.

| # | item / criterion | command | expected state read | est |
|---|---|---|---|---|
| 2.0 | tier truth | `jawa/running_mods` | 16 mods; the Biomes and SWBestiary hashes are the deployed ones | 1 min |
| 2.1 | `ROT_WOUNDLINK_FIX_DROPPED_AT_THE_DOOR` A2 (L1) | `--mod TheRot --chains wound_link` (scripted 2026-10-22). Rows `chittik_carries_wound_link` and `bestiary_kin_carry_wound_link`: a SHALLOW `jawa/get_defs` of `ThingDef/RM_Chittik;RM_Durrok;RM_Mullgoth` + `ThingDef/ZZ_NoSuchDef_Probe` (shallow because deep renders comps as field dicts with no class name). | All three carry `CompProperties_WoundLink`. The probe reads notFound, or the row is UNMEASURED. Durrok/Mullgoth absent reads UNMEASURED (swbestiary not on the tier), never PASS. | 2 min |
| 2.2 | `ROT_WOUNDLINK…` A3 (L2) | same run: rows `wound_shared_with_kin_when_on` and `no_share_when_off`. Two wild `RM_Chittik` 2 cells apart, a `Cut` 14 (AP 1) on A's `RM_CarapaceTheRot` (over the 8 gate, never the brain), both health rows read. The live switch is `RM_CreatureBehaviorsSettings.woundLinkEnabled`: TheRot's `healthSharing` strips comps at startup only. The chain restores the switch and vanishes its pawns. | ON: B carries a Cut on its carapace. OFF: B carries none. A victim with no Cut reads UNMEASURED. | 5 min |
| 2.3 | `WEB_SIEGE_DESIGN_SPIDERS_BRING_SHADE` A1 (L1), `THRIXWEAVE_RESELL_BUILD_DEARLY_SOLD` A1 (L1) | `--mod Webwork --chains defs_resolve,settings_roundtrip,thrixweave_and_front`, plus a Player.log grep for red lines naming `RM_WebworkSiege`, `RM_Webwork_Siege*`, `RM_WebSiege*` or `RM_WebworkSiegeDoorPatch` (read the whole log; never grep -c a missing file) | defs_resolve PASS with its control reading notFound. `rare_trader_resale_line` PASS (Orbital_Exotic carries `StockGenerator_ThrixweaveResale`). Zero siege red lines. | 4 min |
| 2.4 | `WEBWORK_DEAD_GIANT_BUILD_1` A2 (L2) | `--chains urraveth_remains` (ProofSite / ProofRead / ProofLoad) | Every `RM_Urraveth_*` piece spawns wrapped. A read sets `wrapped=false` and adds one chapter plus a thrixweave stack. A loaded rib creaks with the configured window. Removing the load clears it; leaving it collapses the piece and starts its neighbour creaking. | 6 min |
| 2.5 | `WEBWORK_TRACTION_LANCE_BUILD_1` A3 (L2; the earlier acc_biomes run was partial) | `--chains traction_lance` | A manned thrixweave lance reels a raider (`roped=True`, `cellsMoved >= 1`, endDist < startDist). An unmanned lance does nothing. A wall blocks with reason "wall". Cloth has a higher snap chance than thrixweave. An ollathrix is pulled to a cell whose ShadeAt is below the scald threshold. | 6 min |
| 2.6 | `WEB_SIEGE…` A2 (L2) | `--chains siege` on the quicktest map | setting_off_refuses, unshaded_or_unbordered_map_refuses, fires_and_spawns_awake_ollathrix and the rest PASS. `spider_spins_a_web_on_an_unexposed_cell` may read UNMEASURED here: it needs shade, so it moves to row 2.10. | 6 min |
| 2.7 | `ROT_WARM_MAT_BUILD_WORKS_FOR_FOOD` A1 (L1) | `--mod TheRot --chains defs_resolve,settings_roundtrip` | `RM_LivingMatRoot` resolves with both comps and no config error. The group "Ship: the portable warm mat" round-trips. | 3 min |
| 2.8 | `ROT_WARM_MAT…` A2 (L2) | `--chains living_mat_root` on the non-Rot quicktest map | fed_root_spreads_and_eats (5 cells), mat_room_warms_to_cap (toward min(outdoor+18, 21 °C), **never above 21**) and starved_root_dies_back all PASS. rot_root_eats_nothing reads UNMEASURED here; it runs in row 2.11. | 6 min |
| 2.9 | `DUSTVEIL_FLIGHT_BUILD_A_MOTH_THAT_WALKED` A1 (L1) and A2 (L2, after P3) | `--chains dustveil`. A2 is the scripted row `flight_tracker_state_read` (P3): paused, clock proven still, moth + non-flier control read through `jawa/pawn_flight action=report`, both vanished before any tick. | A1: `MaxFlightTime > 0` live, and `RM_MothSilk` and `RM_Dustveil` resolve. A2: `CanEverFly == true`. 🔴 **Owner ruling: never live-test flight without him present and never capture images of flight.** This row is a state read only: no ticks with the moth spawned, no screenshot, no forced flight. | 4 min |
| 2.10 | Webwork map (scratch world tile, never the campaign planet) | `jawa/world_tile_set tiles=<a quicktest-world tile> biome=RM_Webwork` + `jawa/world_commit`, then `jawa/world_tile_map_generate`. Restore the tile afterwards. | A shaded Webwork map. Rerun `--chains siege` for A3: `spider_spins_a_web_on_an_unexposed_cell` PASS (the spider's own spin job leaves one tagged siege web). | 6 min |
| 2.11 | Rot map, same route with `biome=RM_TheRot` | then `--mod TheRot --chains living_mat_root` | A3: `rot_root_eats_nothing`. The food count does not move over `ProofSweeps "5|fed"` and the mat still spreads. | 6 min |
| 2.12 | Owner keeper save | `save_guard.py` wrapper. Save `Webwork_Rot_owner_look_<date>` with an exotic trader in orbit (dev: orbital trader arrival, Orbital_Exotic), a minified living mat root and a staged siege. | One save for rows 3.4 to 3.6 | 5 min |

Load 2 total: about 65 min.

## 3. Owner-present rows (L4 and joint sessions)

He looks at **saves**, not at an agent driving: "Save user review options as save games". None of these blocks
Loads 1 and 2.

| # | item / criterion | what he does | save / tier |
|---|---|---|---|
| 3.1 | `WATER_ART_CANDIDATES…` A4 | looks at the navy tints and the shadow band against the mocks `deep_T2_navy` and `wall_1_shadow_band` | `FW_owner_look_<date>`, Load 1 tier |
| 3.2 | `FLOWWORKS_RESET_BUILD_TWELVE_SCREENS_MISSING` A1 | opens FlowWorks Mod Settings and checks Reset on every screen: Kit, Quarry, Sprinkler, Thirst, Drawbridge, Suspension, WallClimb, RaiderTrench, Swim, MapControl, Rivers x2. Zero ticks; any map, or the main menu. | Load 1 tier |
| 3.3 | `HOSE_RULINGS…` A4, `LIQUID_LEDGER…` A9 | judges the four pipe atlases, the spill art and the "Fitting:" relabel | `FW_owner_look_<date>` |
| 3.4 | `THRIXWEAVE_RESELL…` A2 | sees thrixweave at a steep price at the exotic trader | `Webwork_Rot_owner_look_<date>`, Load 2 tier |
| 3.5 | `WEB_SIEGE…` A4 | a natural siege on a shaded map bordering the Webwork reads as he ordered | a play session; it may need the full list and a campaign-adjacent map |
| 3.6 | `ROT_WARM_MAT…` A5 | plays a cold stop with the root: does it "help a lot" without trivialising? He also answers the spec's open questions 1 to 4. | a play session |
| 3.7 | `ROT_WARM_MAT…` A4 (L2, a gravship flight) | a minified root on the substructure flies and lands with its mat floor (UNMEASURED whether Odyssey carries top-layer floor over substructure). Pair it with `GRAVSHIP_WIRES_SURVIVE_LAUNCH_1` A3, which is already a joint flight with him watching: one launch serves both. | Load 2 tier, joint |
| 3.8 | `DUSTVEIL…` A3 (review sheet, offline) and A4 (live) | A3: judge the 15 artpipe frames `Dustveil_Flying_{1..5}_{east,south,north}` on a review sheet (no bridge; `rimworld-review-sheets` skill; at true scale). A4: watch the wings-only cycle and the landing back on the grounded look, **live, with him present**. | A4: Load 2 tier, joint, never solo |

## 4. Load 3: the full list (restore), GREEN-FULL harvest

1. `python3 src/RimMandrake/Utils/modmanifest.py check` (intended vs next-load vs loaded), then
   `python3 src/RimMandrake/Utils/modset_builder.py --restore-full` (FULL.LATEST, which carries the Wave 4 /
   Alien Worlds SHIP edit 1f6930706). `live_session.py` never restores the list, so this step is owed whatever
   else happens. Parse `activeMods` for the count; never cite one from a doc. 🔴 **Never quicktest on this list.**
2. Cold load (~15 min, up to 25). `./game --why "load 3 full list restore" loading`, then `up`. On UP, harvest
   the whole Player.log and refresh the dumps (`python3 src/RimMandrake/Utils/refresh.py`) before anything else.
3. The harvest itself serves `CUT_FALLOUT_GENERATED_DATA_1` A1 (patch-failure count down against the earlier
   harvest), `FULL_LOAD_RESIDUE_TRIAGE_1` A1 (zero patch failures, fewer config errors) and the Wave-1 rename
   check (zero `Could not resolve cross-reference` naming RM_NightsideIce / RM_Wasteland / RM_PoisonForest; a
   Scribe `Could not load reference to` naming one means a SAVE holds the dead name, so stop and read the
   `rimworld-savegame` skill). Read the FIRST exception, not the loudest.
4. Rows that need a scratch save on the full list (`PYRELANDS_GREEN_FULL_1` fresh mapgen, `ARMOURY_PROJECTILE_DAMAGE_TOOL_1`
   ranged ladder, `FLOWWORKS_NORTHSTAR_GREEN_FULL_1`) wait for GREEN-MIN first. They are not promised by this sitting.
5. `rimflow bridge release`. Leave the game up on his list.

Load 3: about 15 to 25 min to boot, plus about 10 min of harvest.

## Totals and owner time

- Agent-only: prerequisites about 4 h offline. The sitting: deploy about 20 min, Load 1 about 90 min, Load 2
  about 65 min, Load 3 about 35 min. That is about 3.5 h of bridge time, with two minimal boots and one cold
  boot.
- Owner: rows 3.1 to 3.4 take about 20 min on two saves. Rows 3.5 and 3.6 are play. Rows 3.7 and 3.8 A4 are one
  joint live session of about 15 min on the Load 2 tier.
- Verify each row as it lands: `rimflow verify <ID> --criterion <A#> --result pass|fail --config fw_gss_sitting-14|desertplants-16|full-<n> --evidence <path>`.
  Record evidence paths under `Transient/` and pin anything cited (`transient_pin.py add`).
