# Bridge run 1 — 2026-10-23 (BENCH, owner card 08:25 "Now; I'll step away")

Driver: BENCH bridge subagent. Bridge taken 08:36 PDT.

## Deploy
- 08:37 game closed (owner walk Player.log kept: Player_prev_owner_walk.log); FlowWorks DLL rebuilt from a sparse HEAD clone at d945b7bb5e (bench tree has uncommitted drawbridge edits, excluded); committed 02c29c45a4.
- Deployed whole-mod from that clone: FlowWorks (70 files incl. 4 pruned deleted Weir water PNGs), GimmeSomeSlack (DLL+srchash). JawaBench companion build.py --apply --gm (game copy was 10-20 build).
- Deployed DLL sha256: FlowWorks ce4f7375ad87cc43...; GSS f5cfd5a64c5dde4f...; JawaBench md5 d0fed28e50cb.
- 08:39 Steam relaunch, 14-mod list; save e loaded 08:4x compatible 14/14; 621 jawa/ names listed.

## Mechanical checks
| item | verdict | evidence |
|---|---|---|
| REEL_LINK_FIX_IGNORES_THE_OBVIOUS_PORT A2 (L4) | captures/br1_reel_link_47-14_to_43-13.png, br1_reel_link_on_nozzle_43-13.png — lay:47,14->43,13 relays, endPoint (44.957,12.786) vs 43,13 nozzleTip (44.974,12.773): ends on the brass nozzle. lay:39,13->43,13 REFUSED 'no room for the straight lead-out from the nozzle' (39,13 faces north, wall ~3 cells north) |
| REEL_NOZZLE_FIX_COUPLER_HIDES_UNDERNEATH A2 (L4) | captures/br1_reel_nozzle_south_47-14.png — south Scrapper reel, brass coupling over the outlet bore |
| PIT_PAWN_FIX_CARRIES_A_SUNNY_SQUARE A2 (L4) | captures/br1_pit_boar_zoom.png, br1_pit_boar_wide.png, br1_pit_boar_f0..f3 — LOOKS BROKEN: boar standing at 39,23 (in the 2x2 superdeep pit) is drawn ~3 cells south ON the room's south wall with soil squares replacing the wall cells either side. Filed PIT_BOAR_FIX_SUNBATHES_ON_THE_WALL |
| LADDER_EW_FIX_LEANS_THE_WRONG_WAY A1 (L3) | captures/br1_c12_ladders_ew.png — C12 portable ladders 65-67,16-18: E and W ladders are drawn upright like the N/S ones, slanted, mid-cell, not touching their walls; judge owed |
| DRAWBRIDGE_CABLES_FIX_STOP_SHORT A1/A2 | captures/br1_db_timber_lowered.png, br1_db_timber_raised.png, br1_db_steel_lowered.png, br1_db_steel_raised.png, br1_drawbridges_asis.png (save e DB station, 62-92,172-180). Lowered: ropes run clamp->deck end on both banks, no gap seen; raised: slack loops on the bank, none over the pit |
| CORD_PLUG_FIX_FINDS_THE_PIPE_SLOT A2 | captures/br1_pumpport_modern_north_17-146.png (C7 pump: cord beside the south flange, under the body), br1_cord_plug_mapR_pump_175-120.png (map R pump: cord in at a slant between N and W flanges, under the body) |
| UNDERCOUPLER_GIRTH / PUMP_COUPLING_SHRINK / PUMP_PORTS_REDRAW / HOSE_SIDEPORT | captures/br1_pumpport_modern_north_17-146.png (Modern hose laid onto the C7 pump north flange: coupling ~flange width, no collar peeking), br1_pumpport_industrial_25-78.png, br1_tankport_liquidtank/tall/cargo/xtall_116-*.png, br1_tankport_scrapper_230-117.png. NOTE lay onto the pump's own cell (17,146) left the end lying on top of the pump uncoupled (probe path) |
| HOSE_SPLICE (look) | captures/br1_hose_splice_43-13_onto_24-13.png, br1_hose_splice_zoom.png |
| TANK_DEBUG_BUILD_FILL_AT_WILL A1 | PARTIAL (verify partial) | 'Tanks: empty ALL' debug action emptied 26/26; picker order FreshWater first of 23; FlowWorksTankDebug.Fill filled 26/26 to capacity. UNMEASURED: the FillAll/FillOne FloatMenu vanishes when driven headless (mouse distant), click route not exercised; tank_debug_out.txt |
| HOSE_SPLICE_BUILD_MATES_BY_SLOPE A2 | PASS -> done | lay:43,13 -> 36,13 onto reel 24,13's free end: mateOf 49829+49827, mateSolves 1, joiner halves 2; captures/br1_hose_splice_zoom.png shows one continuous slope-matched hose |
| BLEED_WELL_BUILD_SWITCH_AND_SAY_WHY A2 (L4) | UNMEASURED (owner) | switch = 'Designate toggle power' gizmo present; inspect names the reason ('Not running: this map has no subsurface liquid to bleed.'). The 'Give this map a subsurface yield...' Dialog_DebugOptionListLister could not be driven (click_ui_target closed it, no yield set: hasYield False). NOTE save e has NO subsurface yield, so all 5 walk bleed wells sit idle |
| PIPE_STYLE_PRUNE_WHOLE_RUN_ONLY A1 | PASS -> done | menu exactly 4 looks; 2-pipe and 6-pipe runs restyled whole, neighbours untouched, restored; pipe_style_out.txt |

## Visual captures (not closed — art pipeline)
| item | capture |
|---|---|

## Modern-style candidate capture
- Scene staged in save e area F (map C, 109-128 x 112-125): Modern pump 114,118 + Modern tanks 112,118 (pump-tank coupler) and 124,118 (pipe elbow up to its flange), a Modern pipe run with tee/cross/elbow/end caps, a second 4-pipe tee run (117,113), sprinkler on 117,118, faucet on 122,118, two Modern reels: 110,123 hose to the pump/tank junction, 126,122 hose onto the pipe end 119,121 (saddle). Pipe span between poles NOT staged. Saved as RM_br1_modern_scene_20261023 (owner saves stat-checked unchanged).
- BEFORE (deployed originals) frames: captures/br1_modern_BEFORE_{overview,pump_tank_coupler,sprinkler_tee,faucet_tankflange,saddle_hose_on_pipe,pipe_endcaps,reel_hose_coupling}.png
- 08:55 game closed; the 13 cand_r3 PNGs copied over the DEPLOYED Mods/FlowWorks/Textures Modern paths only (repo untouched); originals backed up to D:\ClaudeWork\rimmandrake\backups\br1_modern_deployed_20261023 (MANIFEST.txt, 13 paths). No texture hot-reload exists (hot_reload_defs retired), so a restart on the 14-mod list is the cheapest correct route.
- 08:57 CANDIDATE frames (same scene, RM_br1_modern_scene_20261023 loaded on the swapped textures): captures/br1_modern_CAND_{overview,pump_tank_coupler,sprinkler_tee,faucet_tankflange,saddle_hose_on_pipe,pipe_endcaps,reel_hose_coupling}.png. Reels stay the kept red fire reel (not a candidate).
- 08:58 RESTORED: game closed, deploy_custom_mods --mod FlowWorks --apply from the HEAD clone rewrote exactly those 13 files; re-plan 'Everything in sync'. Relaunched.

## New bugs filed

## End state
- (pending)
- 09:27 driver 2 (BENCH bridge subagent) resumed; prior driver's sitting_gaps (1.1), walk_gaps (1.6) verified in ledger, rehearsal (1.7) UNMEASURED (mech raid RM_LivingBolt at tick 14134 -> 480 s budget spent), zoo C5 (3.4) PASS.
- 09:28 DEPLOY 2: HEAD fed77f423a (committed DLLs MATCH srchash; FlowWorks DLL 86b7fbaf53 sha256 5b463e4e667058b4 deployed==repo; LuminousPigment DLL+About; GSS in sync) from sparse clean clone; Steam relaunch, 14-mod list. Rows from here run on fed77f423a.
- 09:33 filed TANKS_ROW_FIX_LEVELS_WHAT_RULING_FORBADE (TANKS_JOINED_ONE_LEVEL is HARNESS: Store tanks never level by GSS ruling 3) and SITTING_GAPS_FIX_READS_BLANK_GRAPHIC_PATHS (1.1's 3 UNMEASURED rows). Starting 1.2.
- 09:30 1.2 pond_pump --drain: 4/4 PASS -> POND_PUMP_FIX_LAST_DROP_COUNTS A2,A3 verified, done
- 09:32 1.3 suspension_settings_live: first run SB_settings_off_no_button UNMEASURED/HARNESS (empty static_call arg); export-only patch -> 2/2 PASS; SUSPENSION_BUTTONS A1 done, SUSPENSION_BRIDGE A7 verified; filed SUSPENSION_PROOF_FIX_EMPTY_ARG_NO_METHOD
- 09:35 1.4 glow_tank_live: SALT_DRAWN PASS, SETTING_OFF PASS, CROP_GROWS UNMEASURED/SITE (out of season, growth null) -> GLOWTANK_DRINK A1 verified done-path; GLOW_TANK_LIQUID_FEED_1 A2 left owed; filed GLOWTANK_CROP_FIX_FROZEN_FRESH_MAP
- 09:37 1.5 liquid_checks L5: 3/3 PASS -> SPILL_DIAGNOSE A1, LIQUID_LEDGER A6, TESTENV_MEGAPEDE A1 verified
- 09:51 1.6 rerun walk_gaps2 (fed77f423a): 14 PASS incl COVER_DECON_DROPS_RIDER now PASS (item already done); TANKS_JOINED FAIL again (HARNESS, filed); PONDS_HOSE_LEVEL UNMEASURED/SITE (coupling [null,[0,1]], A4 already verified earlier). 1.7 rehearsal2 killed by my 530 s timeout (rc 124)
- 09:52 1.7: LEVEL_REHEARSAL_UNSTICK A1 verified FAIL (both runs over budget, 1/2 rows); note filed. Clearing hostiles.
- 09:58 1.8 trench_crossing 2/2 PASS -> TRENCH_CROSSING A3 verified. Rehearsal kill left hose maxLength=80 + an indeterminate call: reconciled, maxLength restored 40 (read back). 5 conservation exceptions seen in Player.log after walk_gaps2 map (note on LEVEL_REHEARSAL_FIX_POURS_ON_FULL_PONDS, A1 owed). Note: game was very slow (13-29 s per call) on the rehearsal map.
- 10:05 1.9 drawbridge_proof 12/12 PASS (no row reads the look textures, so DRAWBRIDGE_LOOKS A1 stays owed -> judge via frames); §1a cables: proof scenes are torn down now, so staged own timber(2-leaf)+steel at 175-182,150/156 -> captures/br1b_cables_lowered.png, br1b_cables_raised.png (upright-bollard build 0fa86c8e83) for the art-eval judge (DRAWBRIDGE_CABLES item already owes nothing)
- 10:11 1.10 suspension_bridge_proof: 24 PASS, 1 FAIL, 9 UNMEASURED (owed/no --river/--lake/--sea by design). FAIL GRATE_fire_burns_people_above = PRIOR PASS NOW FAIL (15v3 on 41fb948b5e -> 5v6): STOP filed GRATE_FIRE_FIX_SOLID_DECK_BURNS_TOO, SUSPENSION_GRATE A1 verified fail. LOOK_*_resolves 4/4 PASS (A8 is a look: judge owed, no frames taken)
- 10:12 1.11 water_looks: in-script gate red from D: export (filed WATER_LOOKS_GATE_FIX_WSL_CALL_EMPTY); gate green in WSL; live --skip-offline 9/9 PASS -> WATER_ART_CANDIDATES A1,A2,A3 verified (L1)
- 10:14 1.12 legacy_fill 3/3 PASS -> EXCAVATION_LEGACY_MIGRATION_FLAG_1 A1,A2 verified
- 10:16 1.13 deep_lake x2: painted lake read as wild limitless body (1894 / 4000 truncated) -> 3+2 FAIL scored MOD, classed SITE presumed; filed DEEP_LAKE_FIX_PAINTED_LAKE_JOINS_WILD; DRAWDOWN A1 left owed
- 10:19 1.14 deep_stone: map row PASS, cut row UNMEASURED/SITE (nobody took the dig job) -> filed DEEP_STONE_FIX_NOBODY_PICKS_UP_SHOVEL; A2 owed
- 10:20 1.15 ladder_wall: PLACED PASS, DOUBLE_WALL_REFUSED PASS, CENSUS PASS (A7 verified L1), OVER_WALL FAIL with after=null (HARNESS: id mismatch, filed LADDER_WALL_FIX_LOSES_CLIMBER_BY_ID), ONE_WAY UNMEASURED; A4 owed
- 10:27 1.16 pit_rescue x2: QUEUED+BUILT PASS, COLONIST_OUT FAIL both runs = PRIOR PASS NOW FAIL (STOP) -> filed PIT_RESCUE_FIX_LADDER_UP_NOBODY_COMES, LADDER_PARITY A6 verified fail
- 16:35 driver 3 (BENCH bridge subagent): bridge taken. DEPLOY 3 plan: HEAD 1f37da7100 export -> D:\ClaudeWork\rimmandrake\scratch\bridge_run_1c; dll_source_stamp MATCH FlowWorks/GSS/LuminousPigment (committed DLLs current, no rebuild). Next: close, deploy, relaunch, C3 boar + C12 ladders recapture, then 1.17, 1.18.
- 16:38 DEPLOY 3: game closed cleanly; from export 1f37da7100: FlowWorks 147 files (DLL + .srchash + RM_LadderPortable_east/west.png + review/northstar JSON), GSS 29 files (northstar/review only; DLL already in sync); LuminousPigment in sync. Re-plan: no +/~ lines. Deployed FlowWorks DLL sha256 7d63311b00e1986b == export. ModsConfig 14 mods. Steam relaunch.
- 16:42 save e loaded compatible 14/14. C3 boar (stepped 38,22->39,23 paused, then +1/+60/+300): boar drawn on pit south lip (headline fixed) but soil strip over south wall top + soil square outside rim persist -> PIT_BOAR_FIX_SUNBATHES_ON_THE_WALL A2 verify PARTIAL, filed PIT_SINK_FIX_SOIL_STRIP_OVER_WALL (captures/br1d3_c3_boar_{zoom,wide,s1,s60,s300}.png). C12 ladders: E/W against their own walls -> LADDER_EW_FIX_LEANS_THE_WRONG_WAY A1 PASS -> done (captures/br1d3_c12_ladders_ew{,_wide}.png). PIT_PAWN A2 stays L4 owner. Next: 1.17 then 1.18.
- 16:46 companion test profile had expired 18:30Z (static_call REFUSED campaign profile); extended expiresUtc -> 2026-10-24T08:00Z (precedent 2026-10-22 run; campaignSaves untouched; backup D:\ClaudeWork\rimmandrake\backups\br1_driver3_20261023\companion_profile.json.bak). Rows before this used only non-debug-invoke tools.
- 23:49Z 1.17 HR A2: real-UI route found (Architect tab > Pipe networks button > Universal pipe gizmo button via click_ui_target) opens 4-look menu [Scrapper (current), Industrial, Modern, Futuristic]; running s117b.py (log s117b.log)
- 23:54Z 1.17 HR A2 s117b/s117c: four_looks PASS, blueprint Industrial PASS, frame Industrial PASS, built 3x Industrial (current) PASS (logs s117b.log, s117c.log). Next: verifies, then 1.18
- 23:55Z 1.17 done: HR A2 verify PASS; TD A1 verify PARTIAL; filed BRIDGE_FLOATMENU_FIX_DEBUG_PICKER_UNREADABLE (HARNESS). Next 1.18 proof_all --live
- 23:55Z 1.18 plan: proof_all exceeds a 540s call, so chunked: A --only matrix (loads calm), B --only core,aerial,style --no-fresh-map, C --only save_load,d4_save --no-fresh-map; out D:\ClaudeWorkimmandrake\scratchr1_gss; logs Transient/bridge_run_1_20261023/gss_[ABC].log
- 00:00Z 1.18 chunk A matrix: 35 PASS 1 FAIL (MX_F60_T15_S0 regression, filed GSS_WATER_STUB_FIX_PASSED_LAST_WEEK); running chunk B
- 00:04Z 1.18 chunk B core/aerial/style: 83 PASS, 1 UNMEASURED (S12d placeholder in style; d4_save block measures it); running chunk C
- 00:05Z 1.18 chunk C save_load/d4_save: 8 PASS incl S12d_D4 PASS. Next: B12/B13 validation.py, verifies

### Driver 3 final table (1.16 recapture + 1.17 + 1.18), HEAD 1f37da7100 deployed, FlowWorks DLL 7d63311b00e1986b
| row | verdict | item / evidence |
|---|---|---|
| C3 boar on lip (PIT_BOAR A2) | FAIL (partial) | soil strip over wall -> filed PIT_SINK_FIX_SOIL_STRIP_OVER_WALL; captures/br1d3_c3_boar_*.png |
| C12 E/W ladders (LADDER_EW A1) | PASS | LADDER_EW_FIX_LEANS_THE_WRONG_WAY -> done; captures/br1d3_c12_ladders_ew*.png |
| 1.17 TD gizmos / fill pick Brine 16/16 / water first / empty | PASS x4 | TANK_DEBUG A1 partial verify; s117.log |
| 1.17 TD fill-ALL debug-action picker | UNMEASURED (HARNESS) | filed BRIDGE_FLOATMENU_FIX_DEBUG_PICKER_UNREADABLE; fillall_probe.log |
| 1.17 HR four-look menu (real UI click) / blueprint / frame / built keep Industrial | PASS x5 | HOSE_RULINGS A2 verify pass; s117b.log, s117c.log |
| 1.18 GSS proof_all A matrix | 35 PASS, 1 FAIL | MX_F60_T15_S0 prior PASS now FAIL -> filed GSS_WATER_STUB_FIX_PASSED_LAST_WEEK; gss_A.log/json |
| 1.18 GSS proof_all B core/aerial/style | 83 PASS, 1 UNMEASURED | S12d placeholder (by design; measured in C); B12+B13 PASS -> GSS_HOOKUP_CABLE_PROBE_HIDDEN_CONDUIT closed; gss_B.log/json |
| 1.18 GSS proof_all C save_load/d4_save | 8 PASS | S12d_D4 PASS -> GSS_STYLE_RUN_PROVE_MIXED_LOOKS_SUSPECTED closed; gss_C.log/json |
Totals: PASS 136, FAIL 2, UNMEASURED 2; MEASURED 138/140. proof_all ran in 3 --only chunks (a full run exceeds one 540 s call).
Game left Playing/paused on site calm, Player.log 75 KB / 12 load-time error lines (no storm); bridge HELD by BENCH. Section 1 done; section 2 is for a fresh helper.
- 00:08Z committed 5af0f36e3a (ledger + 3 item files), published ce66f83e92. Driver 3 STOPPED; bridge held; section 2 is for a fresh helper. Owed: TANK_DEBUG A1 debug-action route (blocked by BRIDGE_FLOATMENU harness item); PIT_PAWN A2 L4 owner look.
- 00:10Z driver 4 (BENCH, §1 harness re-runs + §2): bridge taken. DEPLOY 4 plan: HEAD 39ec8aac5e export -> D:\ClaudeWorkimmandrake\scratchridge_run_1d; FlowWorks 23 changes (DLL, srchash, RM_SuspensionBridges.xml, 12 anchor PNGs, northstar); GSS in sync. Next: close, apply, relaunch, then §1 re-runs.
- 00:21Z DEPLOY 4 done: game closed (taskkill graceful), deploy_custom_mods --mod FlowWorks --apply from export 39ec8aac5e: 15 files, re-plan no +/~; deployed FlowWorks DLL sha256 d50cfe8feaffc96e == export (dll_source_stamp MATCH); GSS in sync; ModsConfig 14 mods; Steam relaunch, bridge UP at menu. Next: §1 re-runs from the D: export.
- 00:21Z 2.a ladder_wall3: PLACED PASS, OVER_WALL FAIL (order taken byLadder=True, after 900t colonist at 117,110 = 11W/15S of foot; undrafted pawn beside a 7-cell wall it can walk round -> HARNESS suspect, to file), ONE_WAY UNMEASURED, DOUBLE_WALL PASS, CENSUS PASS. ladder_wall3.log/json. Next water_looks.
- 00:22Z 2.b water_looks3 from D: export: offlineGate red=[] (selftest exit 0), 9/9 PASS. Next deep_lake.
- 00:23Z 2.c deep_lake3: body ONE 5184-cell limited, truncated=False (harness fix WORKS) but deepest=4 with deepBedsEnabled/scale 2/max 20 -> DL_lake_over_4000 FAIL + gradual_hollow FAIL (deepestDry 4, abyss 0) = MOD presumed, to file; shallow_dries PASS, refill_exact PASS, colonist rows UNMEASURED, save_reload OWED. Next deep_stone.
- 00:24Z 2.d deep_stone3: DS_map_has_deep_stone PASS; superdeep cut UNMEASURED: job gate reads no workGiver block because deep_stone_live.py:149 passes pawn= but jawa/flowworks_job_probe takes pawnId= (JawaBenchFlowWorksJobProbeTools.cs:67); ordered_job itself accepted=True. HARNESS, to file. Next pit_rescue x2.
- 00:25Z 2.e pit_rescue3: QUEUED/BUILT/COLONIST_OUT PASS (queued 250, built 1250, out 2500). Run 2 next.
- 00:26Z 2.e pit_rescue4: 3/3 PASS again (out 2500); beds medical both runs (Bed9749/9769, Bed38862/38878). Next walk_gaps TANKS_JOINED_STORE_HOLD.
- 00:28Z 2.f walk_gaps3 --only tanks: TANKS_APART_HOLD PASS, TANKS_JOINED_STORE_HOLD PASS (0.1/0.4/0.8 held, 400000 conserved, netReach 2 others). Note: no Dump/pump can-fail control was added; the netReach require is the only blindness guard. §1 re-runs done; next §2 river.
- 00:28Z §2 start: 2.1 extension_proof --live --site river (from D: export).
- 00:29Z §2 2.1 BLOCKED: RM_TestSite_river_v1 (built 10-15 on the full list) loads NOT CLEAN on the 14-mod list (FinalizeLoading NRE ListerFilthInHomeArea, apparel sort NRE, 201 pawn register exceptions, missing AA_/VFEI2_/RUT_/AB_/RSW_ defs). Player_s2_river_load.log. All §2 rows UNMEASURED/SITE (2.5 also needs §3.3 dry half). Map R not staged -> RIVER_MUFFALO left. Next: file items, ledger, restore healthy game.
- 00:30Z river load left the game in an Update() NRE storm (owner: game died). Game closed (graceful), storm log Player_s2_river_storm.log; first exception VFEInsectoids.GameComponent_Insectoids missing -> abstract GameComponent. §2 OWED (needs full-list load or rebuilt river site, RIVER_SITE_REBUILD_FOR_FOURTEEN_MODS). Relaunched; next §3 save e per parent.
- 00:33Z §3 start (parent redirect): save e backed up to /mnt/d/ClaudeWork/rimmandrake/backups/br1d4_saves_20261023T1733 (e only + LISTING; folder 7.2 GB). Loading e; 3.1 joint_check next.
- 00:39Z 3.1 joint_check --all-maps on e: map 0 FAIL 75 joints, only gap the known staged C7 pipe stub [25,130]; map 51 PASS 14 joints incl 1 hose_crossing lifts over. Verifies: JOINT_CHECK_WIDEN A2 pass; JOINT_GATE A2, HOSE_CROSSING A2, HOSE_BUILDINGS A2, HOSE_JOINTS A3 partial; CENTRE_CELLS A2 UNMEASURED (needs its wall scene). s3_joint.log/json, crops D:\ClaudeWorkimmandrake\scratchridge_run_1d\joint_gate. Next 3.2.
- 00:43Z 3.2 scenarios_map --save --name RM_br1d4_gate_red_probe on e: JOINT GATE FAIL -> refusal line printed, rc=1, nothing written, e md5 e7fb0659f23a unchanged. Red half PASS; green half UNMEASURED (known C7 stub keeps gate red). JOINT_GATE A3 partial. s3_save_red.log. Next 3.5 map R.
- 00:45Z 3.5 map R: --river --goto R1 then --river --build (in place, no --fresh-map) -> C1 depth_wrong 1, C11 0 of 8 stations ('no free crossing'), swept 1 non-colonist (R1 Muffalo gone, goto lists R1..R0). HARNESS -> filed RIVER_BUILD_FIX_IN_PLACE_SWEEPS_STATIONS. e map R predates d356baa2a4, so RIVER_MUFFALO A1 + CORD_LOOP A1 UNMEASURED/OWED (fresh map R build). In-memory only: e reloaded, md5 unchanged; export map_r_placed.json restored. s35_*.log. Next 3.6 remaining looks.
- 00:48Z 3.6 looks on e map C: CORD_PLUG A2 PASS (cords at 25,78 + 17,146 slant in beside south flange, end under body) -> closed against 0959a81688; PUMPSTATION_COUPLER A1 UNMEASURED (only station def on map C is RM_PumpingStation_Wrecked 48,99; styled pumps show no distinct under-coupler, 17,146 has no hose; note filed); COUPLER_ART A1 / REEL_TAP A1 (L3 owner look) not judged. Side note: the 17,146 cord detours in a wide loop east before reaching the pump. captures/br1d4_pump_*. Next 3.3 dry on calm.
- 00:53Z 3.3 dry extension: UNMEASURED/SITE. calm+prep_site (refused step 8, golden exists)+preflight: DIRTY 5F/3U (sidecar tile mismatch etc.); golden NS_FlowWorks_TrialSite_v1 loaded (missing Pyrelands classes, no storm): preflight DIRTY 6F (pond capacity 2/cell vs sidecar 5, tier, VEF modal). Filed TRIAL_SITE_REBUILD_FOR_FOURTEEN_MODS. extension_proof dry not run. Game reloaded to calm (CLEAN), Playing/paused. s33_*.log.

## Driver 4 final (2026-10-24 ~00:55Z; deployed HEAD 39ec8aac5e, FlowWorks DLL sha256 d50cfe8feaffc96e)
| section | PASS | FAIL | UNMEASURED |
|---|---|---|---|
| §1 re-runs (ladder_wall3, water_looks3, deep_lake3, deep_stone3, pit_rescue3+4, walk_gaps3) | 23 | 2 (deep beds stop at 4: lake_over_4000, gradual_hollow) | 6 (OVER_WALL harness, ONE_WAY, 2 DL colonist, DL save_reload, DS cut harness) |
| §2 river (2.1-2.5) | 0 | 0 | 5, OWED: river_v1 not loadable on 14 mods (RIVER_SITE_REBUILD_FOR_FOURTEEN_MODS) |
| §3 (3.1 joint, 3.2 refusal, 3.3 dry, 3.5 map R, 3.6 looks; 3.4 done earlier) | 3 (joint map 51, save refusal red half, CORD_PLUG A2) | 1 (joint map 0, only the known staged C7 stub) | 8 (3.2 green half, 3.3 dry site, 3.5 Muffalo + cord, 3.6 coupler/coupler-art/reel-tap) |
| total | 26 | 3 | 19, MEASURED 29/48 |
Closed: LADDER_WALL_FIX_LOSES_CLIMBER_BY_ID, WATER_LOOKS_GATE_FIX_WSL_CALL_EMPTY, DEEP_LAKE_FIX_PAINTED_LAKE_JOINS_WILD, PIT_RESCUE_FIX_LADDER_UP_NOBODY_COMES, CORD_PLUG_FIX_FINDS_THE_PIPE_SLOT.
Filed: LADDER_WALL_FIX_CLIMBER_WALKS_ROUND_WALL (H), DEEP_BEDS_FIX_FLOOR_STOPS_AT_FOUR (MOD), DEEP_STONE_FIX_PROBE_NEVER_NAMES_PAWN (H), RIVER_SITE_REBUILD_FOR_FOURTEEN_MODS (SITE), RIVER_BUILD_FIX_IN_PLACE_SWEEPS_STATIONS (H), TRIAL_SITE_REBUILD_FOR_FOURTEEN_MODS (SITE).
Game left Playing/paused on calm (CLEAN), no storm; save e untouched (md5 e7fb0659f23a); bridge HELD by BENCH. OWED: §2, 3.3, 3.5 (fresh map R build), 3.6 coupler looks.
- 00:56Z committed afa9cccde8 (ledger + 6 items + 4 closed proses). ./publish REFUSED twice: first another helper's uncommitted regen_rounds.json, then the replay of 65a7b24b76 (art eval regen round, not this driver) conflicts with origin in infrastructure/state/art_eval/regen_rounds.json. afa9cccde8 is local only and needs that merge, then ./publish. Driver 4 STOPPED; bridge HELD; game on calm.

## Driver 5 (BENCH, 2026-10-24 UTC; deploy ae73abbbb8 DLL + §3 remainder + owed looks)
- PLAN: export ae73abbbb8 -> scratch/bridge_run_1e; close game; ./game down; deploy FlowWorks --apply; hash check; Steam relaunch; load calm; §3: 3.2 green, 3.5 fresh map R (Muffalo, cord), 3.6 coupler looks; 3.3 stays SITE unless trial site rebuilt; owed looks (hose join bore, Scrapper pipe v2, Heavy anchors, sprinkler flange bands, SLACK_LOOP/ANCHOR_BASE).
- 03:09Z DEPLOY 5: game closed (taskkill graceful); FlowWorks DLL deployed sha256 010d63f729b56823 == repo ae73abbbb8 (VERIFIED in sync); GSS DLL+srchash also drifted (GSS_WATER_STUB fix 744197d480) -> deployed, sha 1e2b945e13ae == repo; LuminousPigment in sync; ModsConfig 14. Steam relaunch, bridge up 57 s; calm loaded CLEAN (s5_load_calm.log). Export scratch/bridge_run_1e.
- 03:10Z 3.5 start: --river --build --fresh-map on calm (founds map R as 2nd map, in memory)
- 03:13Z 3.5 DONE on fresh map R (map 5, tile 5169): R1 Muffalo side-on facing west (captures/br1e_R1_muffalo*.png) PASS; C1 cord battery 63,196 -> pump 64,200: no loop/heap, one S-bend crosses pipe cell 64,199 (br1e_C1_cord*) PASS w/ note. COORDINATOR ADD: after §3+looks run ladder_wall_proof.py <out> --fresh-map (fc095befc0) for LADDER_WALL_FIX_CLIMBER_WALKS_ROUND_WALL; OVER_WALL+ONE_WAY expected PASS; drafted full-wall never crosses = MOD refile.
- 03:14Z COORDINATOR ADD 2: rerun deep_stone_live.py <out> --fresh-map (14a3d41401) for DEEP_STONE_FIX_PROBE_NEVER_NAMES_PAWN: expect workGiver+pawn blocks, dig accepted, depth 3->4.
- 03:14Z 3.2 green: scenarios_map --save --name RM_br1e_gate_green_probe on calm+fresh map R (sweeps map 0 outside C rects in memory; calm reload after)
- 03:15Z 3.2 green PASS: gate map0 0 joints, map5 14 joints/2 reels 0 gaps -> saved RM_br1e_gate_green_probe.rws (new only, changed=[] gone=[]); s5_save_green.log. JOINT_GATE A3 = red (s3_save_red.log) + green -> pass. Reloading calm for looks.

### Driver 5: owed looks (calm map 0, stage5.py = base defs + set_thing_props style; s5_stage.log, s5_cap.log)
Captures are in D:\ClaudeWork\rimmandrake\scratch\br1e_caps\ (s5_*_v/_zoom/_full.png). Driver notes only; the L1 judge is owed.
- HOSE_JOIN south joins (pump S port, laid from a rot0 reel). Scrapper, Modern and Futuristic laid; Industrial lay "target blocked". In s5_join_scrap_zoom.png and s5_join_mf_zoom.png the coupler is side-on, with no dark bore disc. Only these 3 of 4 looks are shown.
- Scrapper pipe v2 (s5_pipe_spr_wide.png): run, end cap, tee N@145, cross@150 and elbow@160 all read aligned.
- Sprinkler heads x4 (same frame): no dark flange bands beside the heads. The dark smudges at x~148 are off-pipe ground stains, not touching any head.
- ANCHOR_BASE A1 (s5_anch_base_full.png): base Rope, Timber, Steel and Heavy are upright in rot 0-3. A2 (s5_anch_heavy_full.png): styled Heavy in Scrapper, Industrial, Modern and Futuristic, upright in rot 0-3. Scrapper Heavy reads close to the base Heavy.
- SLACK_LOOP: not staged (needs the save-e drawbridge station). Owed.
NEXT: 3.6 stations, then the export at origin/main and the ladder_wall and deep_stone reruns.

### Driver 5: 3.6 + SLACK on save e (loaded from menu in 11 s; only the known Scribe load warnings, no tick storm; s5_loade.log)
- Save e holds NO Kludged or Repaired pumping station on map 0 or map R (map 51); its only station is Wrecked at 48,99. stage36.py staged both stations in area F (Kludged at 112,118 and Repaired at 124,118), each laid from a reel to its S side and its E side.
- PUMPSTATION_COUPLER A1 / COUPLER_ART A1 (L1, judge owed): s5_st_kludged_v.png and s5_st_repaired_v.png. On the S side a steel neck is coupled to the hose's brass coupling. The E lay reports layOk, but its hose end lies loose about 1 cell off the east flange, with an open bore. The station likely has no E port, so this is not filed.
- SLACK_LOOP A1/A2 (L1, judge owed): s5_db_west_v.png and s5_db_east_v.png. On timber and steel raised, the ropes lie as flat coils at the bollard feet with nothing standing up. On lowered, the ropes reach the deck and the bollards stand upright. Only the E-W bridge rotation exists at this station.
- REEL_TAP A1 L3 (owner look): s5_reels_13-16_v.png shows the laid reels side-on (red, black, scrapper).
NEXT: export at origin/main (reruns are python-only, so no redeploy), load calm, run ladder_wall_proof --fresh-map, then deep_stone_live --fresh-map.

### Driver 5: coordinator reruns (export scratch/bridge_run_1f = origin/main 5a439387f2, python only; deployed DLL still ae73abbbb8)
- ladder_wall_proof --fresh-map (D:\ClaudeWork\rimmandrake\scratch\bridge_run_1f\ladder_wall_s5.json, s5_ladder_wall.log): PLACED, OVER_WALL, DOUBLE_WALL_REFUSED and CLIMBER_CENSUS PASS. OVER_WALL: the drafted climber's job is RM_ClimbOverWall and it first crosses at tick 60, at x 129 = wallX+1. LADDER_WALL_FIX_CLIMBER_WALKS_ROUND_WALL A1 verified (min-14) -> validated.
- ONE_WAY FAIL, HARNESS: the 21-cell wall leaves a walk-round path, so TryBestCrossing from the far side resolves from=(127) on the ladder side (RM_WallClimb.cs:130 accepts any reachable foot). Filed LADDER_ONEWAY_FIX_WALK_ROUND_COUNTED.
- deep_stone_live --fresh-map (bridge_run_1f\deep_stone_s5.json, s5_deep_stone.log): the job_probe reply now carries workGiver and pawn blocks, and the dig order is accepted. Depth stayed at 3 over 6000 ticks: UNMEASURED SITE (the fresh map gained 7 Filth_Blood and 7 RM_ChokingSpores near the plot). Not verified; notes added to DEEP_STONE_FIX_PROBE_NEVER_NAMES_PAWN and DEEP_STONE_FIX_NOBODY_PICKS_UP_SHOVEL.

### Driver 5 tally
| section | PASS | FAIL | UNMEASURED |
|---|---|---|---|
| §3 (3.1 and 3.4 from driver 4; 3.2 green; 3.3; 3.5 R1/C1; 3.6 looks) | 3 (3.2 green -> JOINT_GATE A3, 3.5 Muffalo, 3.5 cord) | 0 new | 1 SITE (3.3 dry, TRIAL_SITE_REBUILD_FOR_FOURTEEN_MODS) + 3.6 coupler/art/reel captures (L1/L3 judge owed) |
| owed looks | 0 (L1, never verified by the driver) | 0 | 6 captured, judge owed |
| reruns | 4 ladder rows | 1 ONE_WAY (HARNESS, filed) | 1 deep_stone depth (SITE) |
Verified: RIVER_MUFFALO A1 and CORD_LOOP A1 (done), JOINT_GATE A3 and LADDER_WALL A1 (validated). L1 notes with capture paths: HOSE_JOIN, SCRAPPER_PIPE, ANCHOR_BASE, SLACK_LOOP, PUMPSTATION_COUPLER, COUPLER_ART, REEL_TAP.

### Driver 5: MODERN_FITTINGS recipe (calm map 0, x138-153 z138-146; s5_mf_stage*.log, s5_mf_cap*.log)
- Pipe styled Modern 15/15 first, then faucet and sprinkler built by spawn; both draw red Modern, not rusty. Two Modern poles 10 apart: spans=1 MEASURED (ProofLinkPoles Ok, inspect "Pipe spans: 1/3"). StyleDef and texPath UNMEASURED HARNESS: no reader, filed STYLE_READBACK_PROBE_ANY_BUILT_THING. Capture br1e_caps\s5_mf_panel2.png (plants cleared). L1 judge owed; candidate art not swapped in.
- End: calm map 0 paused (scene staged in memory, not saved); bridge HELD by BENCH.

## Driver 6: §4 looks map (export scratch/bridge_run_1g at eeac5c18f0; fresh RM_TheRot 250 quicktest tile 23300, then a vanilla TemperateForest 325 map tile 79933, then save e for the pit shadow)
Captures: `D:\ClaudeWork\rimmandrake\scratch\br1f_caps\` (all), with the cited evidence copied to `captures\br1f\` (untracked).
- Build: `review_map.py --build --fresh-map` gave visuals 39/39 and gallery 87/87 (`captures\br1f\fw_review_map_verify.json`). Stations 63/66/67 hose lays were refused ("no room for the straight lead-out"), and stations 35/36 'Ladder' never read 'Ladder up'. Filed REVIEW_MAP_FIX_STATIONS_NO_LEAD_OUT.
- Tanks (batches A and B): 32/32 + 32/32 hoses coupled, with brass couplings and stubs drawn (s6_A_sheet.png, s6_B_sheet.png). L1, judge owed (TANK_LANE/TANK_NS/TANK_SOUTH/UNDER_COUPLER A2, HOSE_SIDEPORT A1). The tall tank's N hose passes behind the tank top (judge).
- Pumps (batch C, s6_C_sheet.png): W and S couple. The E/N lays aimed 2 cells off, which is HARNESS staging. Judge owed (UNDERCOUPLER_GIRTH A1, PUMP_COUPLING, PUMP_PORTS A1, PUMP_ART A2).
- PIPE_ADAPTER A1: UNMEASURED, SITE (RM_PipeAdapter_Chemfuel needs VCE, which is absent on this list; the pad is empty).
- Pipes (s7_ph_sheet.png): tee/cross/elbow/dead end read in all four looks. The tank group pipe jogs up into the tank's W flange with an elbow (s7z_tank_group_close_v.png). Judge owed: PIPE_FITTINGS A1, PIPE_TANK_JOIN A1, PIPE_ENDS A2.
- Reels (s7_reels_sheet.png, s7n_sheet.png): N back and S front are distinct in each look. The Modern E/W reel shadow is small (s7n_EW_Modern_v.png). Judge owed: REEL_FACINGS A1, MODERN_REEL_SHADOW B2.
- HOSE_PLUMP A2: the flowing hose is at least as wide as the empty one in every look (s7_ph_sheet.png). Judge owed.
- PIT_LIP A1 (s8_pitlip_close_v.png): the upper halves of the pawns show in the opening, and the lower halves sit under a translucent lip with a ghost showing. Ambiguous, so judge owed.
- LIQUID_LOOK A1 (L2): PASS, verified (`captures\br1f\liq.json`, liq_sheet.png). Run 1's off1 miss was HARNESS: ApplyChangedSettings snapshots lazily on the first window draw (FlowWorksMod.cs:2043).
- FlowWorks settings (`captures\br1f\fws\fws_fw_00..34.png`): every section has 'Reset this section', and p00 has Reset all and the search box. Quarry was not found by name. The separate Water effects window has no reset or search. FLOWWORKS_RESET A1 is L4 (owner, noted); SETTINGS_SCREEN_KIT A5 is judge owed.
- SETTINGS_KIT A2/A3 (skit.json, skit_sheet.png): on GSS Cables and Pyrelands, master off greys the dependents; clicking a dependent is a no-op; master on restores; Reset asks Confirm/Go back; Go back is a no-op; Confirm resets. Config was restored. get_ui_layout has no 'disabled' key, so that is UNMEASURED (instrument; lesson filed). The GSS Overhead tab is not clickable, so that is UNMEASURED (HARNESS). Judge owed.
- WATER_LOOK A1 (L2): PASS, verified. On TemperateForest 325 all 12 rows and the overview are whole, and the swatch reads as water (ors_van_sheet.png).
- WATER_LOOK A2 (L2): FAIL, verified. A fresh RM_TheRot swatch reads as water (RGB 87,99,103; ors_rot_sum.txt), so grey is not reproduced and the biome alone is not the cause.
- owner_review_stage itself has three HARNESS gaps:
  - The bars_* rows land off a 250 map.
  - The held-open sluice and grate read open=False (gate_probe.json). By hand, Hold open plus a walk-in opens the sluice and keeps it open (gate_diag4.json), so the mod is fine.
  - The trench shooter is unarmed.
  Filed REVIEW_STAGE_FIX_SMALL_MAPS_HELD_GATES.
- Wall faces D1..D4 (st_V0..V3): captured, judge owed (EXCAVATION_WALL_ART A1/A3/A4, VISUAL_PRINCIPLES A2/A3).
- Owed deep_lake_proof --fresh-map (deep_lake.json):
  - DEEP_BEDS A1: PASS, verified (body = draw = 5 > 4).
  - DEEP_BEDS A2: partial, SITE. Abyss needs a bed of at least 8 notches and the draw's deepest is 5; the colonist rows pass.
  - DRAWDOWN A1: PASS, verified (shallow_dries 5<=5, colonist_free, refill hash equal).
- Owed PIT_COVER A2 (save e C3 boar pit; pit2.json): hour 15.2 and noon, step 120/+420, contrast-boosted crops pit2_*_cb.png. Driver read: no obvious bright box; the boar's ghost patch sits in the shadow band. Judge owed (noted).

### Driver 6 tally
| section | PASS | FAIL | UNMEASURED | judge/owner owed |
|---|---|---|---|---|
| §4 looks | 2 verified (LIQUID A1, WATER_LOOK A1) | 1 verified (WATER_LOOK A2) | 3 (PIPE_ADAPTER A1 SITE; 'disabled' key instrument; GSS Overhead tab HARNESS) | tanks, pumps, pipes, reels, plump, pit lip, wall faces, settings kit/screens (L1/L3); FLOWWORKS_RESET A1 (L4) |
| owed deep_lake | 2 verified (DEEP_BEDS A1, DRAWDOWN A1) | 0 | 1 partial SITE (DEEP_BEDS A2) | - |
| owed pit shadow | - | - | - | PIT_COVER A2 captured |
Filed: REVIEW_STAGE_FIX_SMALL_MAPS_HELD_GATES, REVIEW_MAP_FIX_STATIONS_NO_LEAD_OUT (both HARNESS); lesson ui-layout-no-disabled-key. End: save e loaded, paused; bridge HELD by BENCH.

## Driver 7: §5 long session and hostile rows (export scratch/bridge_run_1h at 5516b15f25, FlowWorks DLL 9b07f8c09557 = deployed; 14-mod list)
Captures: `D:\ClaudeWork\rimmandrake\scratch\br1g_caps\` (ls_c*/session.json + verify_lines.txt per chunk, r52..r56.json/.log, file7.log, ver7.log, note7.log).
Deviations from the sheet, both HARNESS:
- 5.1 ran as `live_session --only B0,<block>` chunks (c1c..c9): a whole session cannot finish inside a 540 s foreground call. Chunking voids rows that need session length (T6 ride <2000 ticks; B7 has no pit registry). Filed LIVE_SESSION_FIX_OUTRUNS_FOREGROUND_WINDOW.
- 5.2-5.6 ran on a fresh map I made first (fm.py), then the guardian purge, then the script WITHOUT its own `--fresh-map` (raidrow.sh), so spores could be purged before the row.
Test environment: on RM_TheRot maps the guardian-grove plants (RM_AgelessCap, RM_AgariluxPrime, RM_Skulltop) emit RM_ChokingSpores. Parked colonists collected dozens of Scratch + ToxicBuildup and went down, which GovernorStopped sprinkler/proof_hose three times (c2b, c2d, c2e). The export's recalm.py now destroys them and ends RM_SheenExposureLock. Filed QUIET_SITE_FIX_SPORE_GUARDIANS_STILL_BITE.
- B1 (c1c, after c1/c1b ABORTs on a used map; HARNESS, filed LIVE_SESSION_FIX_B1_NEEDS_PRISTINE_MAP): validation_v2 all PASS, X8c_lid_walker_drawn_at_ground PASS -> PIT_LID A2 verified. B2 dialogs/readouts all PASS (TANK_TALL verified; seven FOUNDRY items noted VERIFY OWED).
- B3 liquid (c2b): L2 PASS. L4 SITE/partial. **L5_switched_off_hose_spills FAIL, STOP (PASS earlier today)**: 10000 units spilled, filth thickness in rect 6->8 vs 3 pieces expected. The rect held 6 before, so presumed SITE, unproven; not verified. Filed SPILL_FILTH_DIAGNOSE_TWO_OF_THREE. L6 not run (UNMEASURED). LIQUID A4/A7 stay owed.
- proof_hose realflow (c2e): 17 PASS, NS_external_pipe + SL4 UNMEASURED SITE -> HOSE_RULINGS A5 partial, not verified. No wall row in realflow -> HOSE_ROUTE A3 UNMEASURED.
- sprinkler (c2f, after purge): 8/10 PASS incl. T22_no_brine_spray; it then crashed. SESSION_HURT A1 FAIL again: Vikinger parked and drafted at 126,126, ended at 160,95 with Bruise + Crack. Presumed HARNESS; noted.
- B4 (c3): 13 PASS / 1 FAIL / 4 UNMEASURED. **B4_grenade_no_blast_cover (TRENCH_COVER A4) FAIL, STOP**: trench 13.33 vs open 20; PASS 10-22 (6 trials). n=1, not verified. Filed GRENADE_COVER_DIAGNOSE_TRENCH_LEAKS_BLAST.
  - B4_dehydration_rate UNMEASURED: chunk ride too short; the 1000-tick hint is 0.27/60k vs the 0.30 bar, so THIRST T6 stays owed.
  - B4_rail_unrailed_control UNMEASURED (the control never stepped off), so FALL_GUARDRAILS A3 stays owed per his ruling.
  - No HW1/T8 rows were read (owed). The fish rows are SITE: the Rot biome has no fish.
- B5 (c4) 4/4 PASS. B6 (c5) PASS. B7 reload PASS but VACUOUS (pairs {}), so treated as UNMEASURED; filed PROOF_ROWS_FIX_PASS_ON_EMPTY_SAMPLE.
- B8 (c7, Rot map): RAID_island_sealed FAIL (pocket=False), outcome MILL_FAR, LADDER_BREACH/MASKSWAP UNMEASURED. The same check PASSED on all five r52..r56 maps, so presumed SITE; not verified.
- B9 (c9, AridShrubland; owner_review_stage refuses RM_TheRot with exit 3): stage exit 0, save `FLOWWORKS_OWNER_REVIEW_20261023_2228.rws` written. 8 rows OWED to his eyes.
- B10 thirst (c8, map had 0 colonists after r56): T3/T4/T5/T9/T10 PASS. T2 FAIL is vacuous (perColonist {}), HARNESS, in PROOF_ROWS_FIX_PASS_ON_EMPTY_SAMPLE. T1/T7 UNMEASURED (no --log in chunk mode).
- 5.2 (r52, depth 8): **RAID_FILL_CAUSEWAY FAIL**. Six raiders, three came near; outcome LEFT/STALL/SHOT_ACROSS; no square filled. Verified fail: CAUSEWAY A1, RAIDERS_TRENCH A3, LADDER_PARITY A3 (bar "still PASS"). BREACH_SCAR_REPAIR UNMEASURED (nothing filled). island_sealed + MASKSWAP PASS.
- 5.3 (r53): LADDER_PARITY_RAIDERS_USE_COLONY_LADDERS PASS -> A1 verified. MASKSWAP FAIL is masked by the legal colony ladders (HARNESS, not counted).
- 5.4 (r54): LADDER_PARITY_RAID_BRINGS_SOME_LADDERS PASS -> A2 verified (raid milled far; MASKSWAP/LADDER_BREACH UNMEASURED).
- 5.5 (r55, depth 4, 6 trees): LADDER_PARITY_RAIDER_FELLS_TREE PASS is VACUOUS: 6/6 oaks standing, no stump, PASS on chopSeen alone. Not verified; A5 stays owed. Filed in PROOF_ROWS_FIX_PASS_ON_EMPTY_SAMPLE (a MOD "chop never fells" is presumed too). RAID_LADDER_BREACH FAIL: one raider ladder on one wall, no fill. Same no-fill as r52; noted on CAUSEWAY.
- 5.6 (r56): UND_raiders_walk_under_moat PASS -> SUSPENSION_UNDERPASS A9 verified.
- 5.7 Titans: UNMEASURED SITE (tier). HugeThings is not on the 14-mod active list (ModsConfig parsed), and adding it was out of scope for this driver.
- Re-confirmations (PASS, criterion already passed, no verify recorded): FALL_GUARDRAILS A2, TRENCH_COVER A2, LIQUID A3, PIT_ACCESS A1-A4, SUSPENSION_BASE A3, POND_DEPTH A5/A6, SALT_BOTTLE T5, FLOWWORKS_ENDLESS_LABEL A1. These show no regression on those rows.
- VERIFY OWED by FOUNDRY (BENCH refused on seat; a note with the evidence is on each): BEACH_RING A1, DEPTH_READOUT A2, FALL_DAMAGE A1, LIQUID_DEPTH A2, PIT_ALERT A1, PIT_ROOM A1, VALIDATION_V2 (item), DIG_COST A2, PIT_DEPTH A2.

### Driver 7 tally
| section | PASS | FAIL | UNMEASURED | judge/owner owed |
|---|---|---|---|---|
| 5.1 live_session (chunked) | 4 verified (PIT_LID A2, TANK_TALL); 9 FOUNDRY verifies owed as notes; 11 re-confirmed | 2 STOP regressions filed, unverified (L5 spill, grenade A4); SESSION_HURT A1 presumed HARNESS; B8 island presumed SITE | T6, T1, T7, HW1, T8, L6, LIQUID A4/A7, HOSE_ROUTE A3, HOSE_RULINGS A5 (partial), rail A3, B7 (vacuous), T2 (vacuous) | B9 8 rows (save written) |
| 5.2 depth 8 | island, MASKSWAP | 3 verified MOD (CAUSEWAY A1, RAIDERS_TRENCH A3, LADDER_PARITY A3) | BREACH_SCAR_REPAIR | - |
| 5.3 / 5.4 | LADDER_PARITY A1, A2 verified | - | 5.4 MASKSWAP/LADDER_BREACH | - |
| 5.5 trees | - | RAID_LADDER_BREACH (same no-fill, noted) | LADDER_PARITY A5 (vacuous PASS) | - |
| 5.6 underpass | SUSPENSION_UNDERPASS A9 verified | - | - | - |
| 5.7 titans | - | - | TITAN A5 (SITE: tier) | - |
Filed: SPILL_FILTH_DIAGNOSE_TWO_OF_THREE, GRENADE_COVER_DIAGNOSE_TRENCH_LEAKS_BLAST (STOPs); QUIET_SITE_FIX_SPORE_GUARDIANS_STILL_BITE (test env); LIVE_SESSION_FIX_B1_NEEDS_PRISTINE_MAP, LIVE_SESSION_FIX_OUTRUNS_FOREGROUND_WINDOW, PROOF_ROWS_FIX_PASS_ON_EMPTY_SAMPLE (HARNESS). Notes: SESSION_HURT, CAUSEWAY. End: fresh AridShrubland map after B9, paused; bridge HELD by BENCH.
