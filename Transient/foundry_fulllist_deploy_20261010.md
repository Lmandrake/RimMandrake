# 551 FULL.LATEST deploy + launch + live proofs (FOUNDRY, 2026-10-10)

## Progress
- 13:29 bridge taken; started

## Preflight waivers
Final offline preflight (20:36Z, --all --deep): O09 companion now PASS; O02 PASS after fix 2bba7a406. Remaining FAILs waived:
- O07 known_wedgers (RealFoW): wedge is on bland_world's second-map ruin destroy; this is a cold load + quicktest, not a bland-world suite run. Waived.
- O06 ship_coverage (38 absent / 14 installed): owner ruling, added only after a clean 551 load. Waived.
- O04 modsconfig_intent 550 vs 551 and O05 list_sane: vlvop.tormentmaster.expansion not installed (About.xml sweep of Mods + workshop/294100, 1377 About files, probe 553 ludeon deps; D:\SteamLibrary has no 294100). Dropped from the LIVE copy only; FULL.LATEST untouched. Waived.
- O14 effective_def_lint: 0 crash findings; residual = 3 failed_ops (patches matching nothing, filed RAKATA_PATCHES_PROBE_THREE_OPS_MATCH_NOTHING). Non-fatal. Waived.
- O13 deploy_match: FlowWorks 14 / WreckedMachines 3 files are game-only leftovers (northstar jsons, retired textures), no load effect. UtinniPatches' game-only FlameStatuary_HolyAct.xml (removed in repo 30c1ae50b, moved to ShkaarIdol_HolyAct.xml => duplicate patch) PRUNED. Waived for the rest.
- O10 dependency_fp UNMEASURED: baseline to be recorded after the green load.

## Load

## Live proofs

## Owed
- 13:31 preflight O02 bug fixed (HELD token) + clone synced to origin, pushed f34b77501. Offline FAILs: O07 RealFoW, O06 38 absent, O04 67 live, O09 companion, O05 tormentmaster, O14 6 crash (Armoury undeployed), O13 6 mods drift
- 13:36 companion built+deployed (gm, f34b77501ea0), profile=test file written; ModsConfig -> FULL.LATEST (551) then tormentmaster dropped from live copy (550; absent in both roots + D:\SteamLibrary)
- 13:36 deployed FlowWorks WreckedMachines Armoury(67153b072+27edb8a0e) SWBestiary UtinniPatches + biomes compose (CreatureBehaviors dll)
- 13:39 launching via launch_and_wait.sh
- 13:39 RimWorldWin64 PID 1568 up (launch_ready.py; launch_and_wait.sh was mode 644 -> fixed 504a3c795)
- 13:40 health_observer.py started (python.exe --for 10800, announced here; not the C1 config)
- 13:46 loading (log 115 KB, 0 exceptions)
- 13:51 defs phase; 2 exceptions so far = Worldbuilder IsMemeAllowedFor postfix NRE inside ConfigErrors (donor, non-fatal)
- 13:55 post-defs; exceptions 4: Worldbuilder x2 (ConfigErrors), VBE RimThemes key, Quarry BuildStoneDict dup key 'Sandstone' (possible label collision; check later)
- 14:00 READY: pid 1568, 550 mods, 1241 s (20.7 min) from launch; receipt D:\Luke\dev\_rmscratch\launch_receipts\launch_20261010T140006.json; first exception = Worldbuilder ConfigErrors NRE (donor); launch_ready audit: no MODS_RESET/CORE_ONLY
- 14:00 preflight --live: only O04/L04 (tormentmaster, waived). handshake: sha 96e05a9e.. compile gm, profile test, gate complete installMs 2466, all hook coverage ok, argGuard installed -> Transient/foundry_fulllist_handshake_menu_20261010.json. dependency baseline recorded (12 entries). Starting quicktest.
- 14:03 quicktest started (start_debug_game_ready, reply lost at 25s, reconciled as applied)
- 14:05 quicktest Playing (epoch 1, map 0). experiment manifest TPS_ATTR_AB_INSESSION_20261010/C0 recorded; A/B running (Normal/Superfast/Ultrafast x ABBA x 40 s)
- 14:07 Armoury fix confirmed live: 0 lines naming OuterRim_Durasteel in Player.log (literal search, MEASURE_ALLOW_SCAN=1). Quarry dup key 'Sandstone' (post-long-event, non-fatal) unresolved; L03: 29 config errors, first is ours: MenuShell defName 'Utinni Shellmandrake.rut.menushell' has a space
- 14:10 FINDING: quicktest map runs ~8 TPS at Normal (ratio ~0.13, ~120 ms sim per tick, top tl:Normal ~83%, fps ~6) on the 550 list. Attribution A/B at Normal: on 119.0 vs off 123.1 ms/tick (-3.3%, inside block spread 114-129) = no measurable overhead; profEstMs ~0.13 ms per window
- 14:16 A/B done (ABBA x3 speeds, 40 s blocks): sim ms/tick on vs off Normal 119.0/123.1, Superfast 96.0/112.1, Ultrafast 97.7/101.1 -> ON never slower; overhead below the block-to-block noise (~5-15%) at ~8-10 TPS. Result Transient/foundry_tps_ab_result_20261010.json
- 14:18 awareness live: receipts PASS (3/3 kinds match), pawn_origin spawn chain PASS, journal RaidEnemy row PASS (first raid swallowed by RaidProtectionFee modal: journal honest, 0 pawns), Mechanoid raid drop-pod chain PASS 1/1 ourInvolvement ours; Infestation fired (not a worker-false case; unproven)
- 14:18 hive from the Infestation destroyed; abort_proof (live_queue) started for CLEAN/DISRUPTED
- 14:20 health_observer sampling OK (537 rows; game main thread 0.99 cores = saturated, private 30.6 GB, ws 18.3 GB, system avail 3.8 GB)
- 14:23 abort_proof run1 10/11: only control_quiet failed, on 9 Spelopedes from MY pass-1 Infestation (hostile_pawns SURPRISE correctly raised). hostile_raid recorded+removed CLEAN PASS, predator DISRUPTED abort PASS. Rerunning on the now-bland map.
- 14:31 abort_proof run2 10/11: control_quiet aborted on a REAL hazard (RM_ChokingSpores toxic spores damaged colonist Aaron; quicktest map is not bland) -> detector honest, control not a defect. hostile_raid CLEAN + predator abort PASS both runs.
- 14:33 pass4: in-game handshake epoch 1 map 0, coverage ok x7; disarm -> ResourcePodCrash journaled, no AWARE row; no wildlife left (bland prep) so PAWN_ORIGIN A2 unmeasured.
- 14:35 DEFECT found+fixed d0c8ace23 (built, NOT deployed): awareness meters for incident-journal / origin-generation timed the wrapped original (means 438 ms / 43 ms) while labelled "hook body only".
- 14:40 rimflow verify recorded: VISITOR A3 pass, A2 partial; INCIDENT A2 pass, A5 pass; PAWN_ORIGIN A3 pass, A6 fail; PREFLIGHT A1 pass, A2 partial; COMPANION_HANDSHAKE A1 pass (-> done); COMPANION_PROFILE A3 pass; BRIDGE_TPS_REVIEW2 C4 partial.

## Live proofs
Evidence: Transient/foundry_awareness_live_20261010.json, Transient/modcheck/live_queue_results.jsonl (abort_proof runs 14:18, 14:26),
Transient/foundry_tps_ab_result_20261010.json (+ schedule), Transient/foundry_fulllist_handshake_menu_20261010.json, Transient/foundry_fulllist_preflight_live_20261010.txt.
- PASS: spawn receipts 3/3; spawn origin chain; forced-raid journal; drop-pod chain (Mechanoid raid); armed/disarmed disk rows; hostile_raid CLEAN; predator abort; handshake keys+sha; gate complete; preflight --live L01-L07.
- Honest negatives: first RaidEnemy was swallowed by Leo.RaidProtectionFee's Dialog_NodeTree (fire_incident said so; journal says returned true, 0 pawns). Infestation is not a worker-false case (fired, hive spawned, cleaned up).
- TPS: autostart on the full list with no bridge call; attribution overhead not measurable in-session.

## Owed
- INCIDENT A3 (worker-false incident), A4 (queued incident chain); VISITOR A2 substituted case, A4 manhunter+joiner scene report; PAWN_ORIGIN A2 (needs install.generation-early + fresh map), A4 caravan/gravship, A5 save/load epoch, A6 after deploying d0c8ace23.
- COMPANION_PROFILE A1 (no profile file) and A2 campaignSaves; handshake §5 items 3-5 (epoch guard refusals, wild-spawner block release, 10-min coverage).
- MUST 17: C0-C5 / 3-restart overhead protocol and overnight reconstruction.
- LOW TPS FINDING: quicktest map on the 550 list runs ~8-10 TPS (ratio ~0.13), tl:Normal ~83%, main thread 0.99 cores, private 30.6 GB; needs its own diagnosis.
- Quarry BuildStoneDict duplicate 'Sandstone' key; MenuShell config error (defName with a space); 29 config errors overall.
- The 14 installed missing mods: separate follow-up now that the 550 load is clean (owner ruling).
