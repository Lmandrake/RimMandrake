# Live hose proof — hose walls + joints (BENCH helper, 2026-10-22 late)

Shas under test (deployed, FlowWorks 15 files VERIFIED): 849b1674ea (walls), 34559c60d9 / c750fe9056 / 7870b3b597 (joints),
41c06f6a2b (portable ladder art), fb34c9bc2d (Modern tank art). Mod list fw_gss_sitting (14, swap-active kept).
New save **RM_fw_walkthrough_20261022c** (map C only, see F2); save b untouched (save_guard VERIFIED, read-only loads).
⚠ 694e9d2ddc (Modern reel FA art) landed at 20:13 while this ran; it is NOT deployed in save c (see F1).

## Status
- [x] bridge taken; HEAD == origin/main at start; offline HO1-HO9 5/5, hose 380/380
- [x] deploy FlowWorks (15 files, VERIFIED), relaunch via Steam, main menu
- [x] map C build: 11/11 scenarios as staged (twice: second on a new world for map R)
- [ ] map R build: NOT founded (F2) — two worlds, 40 river tiles, all "no straight south bank for C1"
- [x] labels pinned (279); C12 sign spot-read (3 signs listed)
- [x] joint check (8b) map C: PASS, 24 joints on 18 reels, 0 gaps, 0 unmeasured (after fixing the checker, F3)
- [x] HW1 save c map C: PASS (12 laid); save b map C: PASS (13 laid), save b map R: PASS (2 laid)
- [x] reel o1 re-lay (minBendRadius 1.21 -> 1.2): save c len 25.97, through the wall gap (22,42), wallCross 0; save b o1 also through the gap
- [x] save c saved (ok=True, keepers VERIFIED)
- [x] zoomed captures + verdicts (below)
- [x] after.png
- [x] findings filed, rows recorded
- [x] bridge released; game up paused on save c

## Results
| check | result | evidence |
|---|---|---|
| joint_check --all-maps, save c | **PASS** (map C; map R absent) | `Transient/pile_2026-10-22/joint_check_rebuild.json` |
| joint_check --all-maps, save b | FAIL map 0: reel 41679 feed_nozzle_shared (West-staged o1, the SITE defect save c fixes); map 9 PASS | `live_hose_proof/joint_check_saveB.json` (shows the check can fail) |
| HW1 save c map C | **PASS** 12 laid | `live_hose_proof/hw1_saveC_mapC.json` |
| HW1 save b map C | **PASS** 13 laid (incl. o1 41679) | `live_hose_proof/hw1_saveB_mapC.json` |
| HW1 save b map R | **PASS** 2 laid | `live_hose_proof/hw1_saveB_mapR.json` |
| proof_hose offline gate | red: csharp_selftest (F1, not the deployed code); runs used --skip-offline | |

## Captures (per-capture verdicts) — save c, map C, closest zoom (114 px/cell)
Bars: hose meets nozzle/port with no gap; no hose through a wall; nothing unrecognizable.

| capture | what | verdict |
|---|---|---|
| o1_relay_gap | reel o1 (18,43) re-laid, faces east | PASS: through the wall gap, clear of battery and pump |
| r49818_reel / _end | o1 nozzle; free end at Hobb's pit | PASS: collar on nozzle; pipe from tank feeds the reel top (under-reel link); end lies free |
| r49819_reel | relay o2, stored | PASS |
| r49822..r49826 reel/end | C3 park, four looks (plump/filling/flat/wound) | PASS: every reel faces east, collar on nozzle, ends free; no U-turn |
| r49827 reel/end | C3 dropped carry | PASS |
| r49828/29/30 | turned reels N/E/S (stored) | PASS (art look is the owner's card) |
| r49838_reel | C4 stored reel + pump link | PASS: link from pump flange into the reel drum, no float |
| r49882 reel/end | C5 hose to THEIR tank | PASS: coupling seated on the tank flange (D8 gone) |
| r49943 / r49944 reel/end, C7_vertical_after | C7 one hose net: pipe links + laid hoses | PASS: pipe links meet both reels at the nozzle elbow, no loose cap; note: link and laid hose meet at the same elbow (reads as a T, joint check passes it as under-reel) |
| r50042 reel/end | C7 tower garden hose | PASS |
| r50093 reel/end | C10 hose into the pond | PASS |
| r50099 reel/end, z_r50099 | X tank-to-reel link + hose to tank | PASS: link rises to the nozzle elbow, end on the far tank flange; same T note as C7 |
| r*_path (12) | every laid hose path | PASS: no wall crossed, no U-turn, no hose under a building |
| ladder4_walls | portable ladder on all four pit walls (3 spawned after the save, discarded by reload) | PASS: auto-faces each wall; N/E/W read as ladders; S shows only its top above the rim (perspective) |
| ladderP_65_17 | staged ladder, west wall | PASS |
| tankM_C7z | Modern tanks: white poly short, green poly tall, IBC cargo | PASS: recognizable |
| tankM_C5bz | C5 cargo tanks + pipe risers | PASS |
| B_o1_gap (save b) | o1 on save b with the new DLL | PASS walls (through the gap); still loops west past the battery corner (save b's West staging) |

Phone image: `Transient/pile_2026-10-22/live_hose_proof/after.png` (1600 x 3118, 8 rows before | after) — looked at: all 8 rows PASS.

## Findings
- F1 `MODERN_REEL_FIX_ONE_JOINT_IN_AIR` (MOD): 694e9d2ddc turns the C# joints row red 255/256 (Modern rot0 stored side 0,1 runs through air). Not deployed in save c; save c shows the previous Modern reel art.
- F2 `MAP_R_BUILDER_FIX_FORTY_BANKS_REFUSED` (SITE/HARNESS): no map R on two worlds (15 + 25 tiles); same-world retry tries 0. Walk stops 8-11 cannot run on save c; save b keeps its map R.
- F3 `JOINT_CHECK_FIX_ALL_MAPS_SAW_ONE` (HARNESS, fixed this sitting): --all-maps read one map and crashed restoring it.
- Remaining defects by class: MOD 0 visible on the deployed code (F1 is offline-only, undeployed); SITE 1 (F2); HARNESS 0 open (F3 fixed). Minor look note: feed link and laid hose share the nozzle elbow on laid reels with a port beside them (C7 x2, X reel 237).
