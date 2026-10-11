# GimmeSomeSlack — drive home (2026-10-10)

**Status:** PHASE 2 — full run on the 550-mod list in progress after check fixes 4c6e5cbb8. Phase 1 (test tier) DONE. Full `proof_all.py --live` (shots ON) = **151 PASS / 0 FAIL**:
`src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261010T185049.json` (flowworks tier: 11 mods, GSS + FlowWorks so P1 is
measured instead of SKIP; wall 400 s). Offline gate green (red=[]; O3 836/836). `run_selftests.py` GREEN (316 PASS / 0 FAIL / 67 SKIP).
Fix commits: df359078c, 4afb43d46 (pushed). Game: owner's 550-mod list restored (md5 ee01dae9…, matches the pre-swap snapshot), relaunched via Steam.

## Per-FAIL table

| id | root cause | fix sha | verified-live |
|---|---|---|---|
| M1, M2, M3b, M5 | Test SITE vs the owner's 2026-10-06 straight-lead-out ruling (question card): a 2x2 reel's hose leaves its WEST nozzle straight (OutletLead 4.0, never under the 1.2 min bend) or is refused. The maze reel sat 3 cells from the west wall in a 3-row chamber: the short route needed a 2.5-wide U-turn, the spiral a 1.26-radius turn into a 1-cell corridor. Unlayable by rule; 10-05 PASS predated the ruling. Offline maze (1x1 reel, no outlet) could not see it. | df359078c (maze redrawn: both options leave west; spiral ~2x short; C# HoseSelfTest.MazeRows kept identical) | yes, 8/8 maze |
| P1_reel_couples_to_tank | CHECK read feedDraws from M1's census, 4 game ticks after the tank was built; CompHoseReel.Port() caches its port 60 ticks (documented). First run ever with FlowWorks loaded (was SKIP). | df359078c (census taken at P1 time; M1 value kept as feedDrawsAtM1) | yes |
| RL3 (RL6, RL8 downstream) | Same ruling: relay A's hose U-turns out of its west nozzle (+~12 cells). (a) Site prepared only 2 cells west of A; (b) at 32 cells A->B the laid hose was ~44 > 40 and refused "route too long (lead-out included)" while `check:` said it fit. (b) is a real MOD defect: HoseMath.CheckInstall ignores the lead-out, so a player order was accepted and the hose never drew. | df359078c (site 8 cells west), 4afb43d46 (C#: RM_MapComponent_Hoses.CheckInstall runs a trial planned lay; test B at +24, C at +56, span still > one hose) | yes, 8/8 relay |
| B3, B4d, R2 | Did NOT reproduce on the 11-mod list (PASS twice). The 10-10 run was on 550 mods (proof_all only checks GSS is present). Draw counters read a frame after a setting/camera move; environment-specific on the full list — not diagnosed. | none | PASS on test tier |
| S9d | Same: PASS on the test tier (unprinted strands on the 550 list only). | none | PASS on test tier |
| SL3, SL4 | Same: PASS on the test tier (hose geometry hash moved across load; CR5 resume empty on the 550 list only). | none | PASS on test tier |
| Z_log_budget | The NREs ("Exception from long event") and the precept/RimFridge errors appear only on the 550 list; 0 errors on the test tier. | none | PASS on test tier |

## Phase 2 — the 550-mod list (owner's game)

| id | root cause (full list) | fix sha | verified-live |
|---|---|---|---|
| B4d | CHECK timing/geometry: frame_cell_rect keeps the zoom; on this list root size 24 = a 149-cell view, so framed on the stub the scene's ends ~80 cells away were on screen (liveEndsOnScreen 2). Camera arrives instantly (measured, Transient/gss_drive_home/cam_probe.py) -- not easing. | 4c6e5cbb8 (zoom to sizeRange.min before framing, view width recorded) | pending full run |
| CR2/CR3/CR5 (new), SL4 | CHECK timing: "Out of Combat ReBoost" walks colonists ~2 ticks/cell (measured: 24 cells in ~45 ticks, Transient/gss_drive_home/speed_probe.py) while MoveSpeed reads 4.6 c/s; fixed 60-tick steps finished the walk before the "mid-walk" draft. | 4c6e5cbb8 (_walk_a_little: step 2 ticks until the trail grew 2 cells) | pending |
| SL2/SL3 (in --only runs) | partial-run artefact: no plump hose without the hose block. Not a defect. | - | pending full run |
| Z_log_budget | Foreign errors on ANY save/load of this list: NRE in ReGrowthCore.Map_FinalizeInit_Patch.RecolorMineables (map init and every load; the bridge copy is a BetterStackTraces '[Ref DF9ACD49] Duplicate' that the old 'Map_FinalizeInit' exclusion could not match), NRE in RimFridge.RimFridgeComponent.StartedOrLoadedGame (on LoadedGame, PerformanceOptimizer transpiler on it), RimFridge missing ResearchProjectDef, 'Could not get load ID ... /sourcePrecept' (colonists' apparel), 'forgetTimers', disabled-stat MedicalSurgerySuccessChance on quicktest colonist Diver (no stack logged). None names GSS. | 4c6e5cbb8 (preflight takes a GSS-free control save/load + 600 ticks; Z excludes only errors in that set that do not name GSS; anything new is still charged, with its thrower) | pending |
| R2 | CHECK/harness: frame_cell_rect keeps the zoom; this list's camera sat at root 11 = a 12x6-cell view, so the 46x20 aerial site showed 2 of 4 masts (topDraws 2). Measured r2_probe.py: root 11 -> top 2, root 15/24 -> top 4. | 19ba7aff3 (validation.frame_fit: zoom out until the view holds the site) | pending |
| B4d (2nd) | the closest zoom on this list is an 11-cell view that holds neither scene end (root->width 11->11, 15->53, 20->107, 24->149, zoom_probe.py). | 19ba7aff3 (search the zoom for a >=40-cell view) | pending |
| M4 (new on full list) | MOD defect, seed-dependent: the 4 shortest lead-out joins all sat before the jog where the outlet run meets the first cell centre; the bend window read it ~0.7 < R=1.2, so a route that fits was refused "no room for the straight lead-out" (the re-lay before M4). New selftest maze 6 sweeps 300 seeds: 85 refused before, 0 after. | 19ba7aff3 (HoseMath.LayOnce tries up to 24 farther joins before refusing) | pending |
| P2 / L2 (UNMEASURED) | harness: chatty mods push the startup out of the bridge's last 500 entries; the [RimBridge] sanity line is never seen. | 2b329d934, 19ba7aff3 (fall back to Player.log) | pending |
| SL3 (harness) | rimworld/load_game answers "queued"; the old map stays Playing 3-8 s, so _wait_playing returned at once (loadSeconds 1-4) and after-load reads could come off the old map. Likely the 10-10 SL3 hash difference. | 78a3d7ecf (wait for the state to leave Playing first) | pending |
| S9a-d (run 5) | harness/environment: "CanDesignateCell refused ...: Can't place in undiscovered area" on SITE2 cells though jawa/set_fog unfogged them -- the list's fog (Real Fog of War) needs a colonist's sight; flaky by map. fog_probe.py: a far row refused, placeable after a 30-tick colonist visit. | 0e960f32f (validation.reveal in prepare_site and S9) | pending |
| R3 style_hose (run 6) | site margin: the first reel's west lead-out ran onto unprepared map ground (same class as the relay site). | 0e960f32f (SITE 8 cells west) | pending |
| Z (run 6) | foreign: NRE in BetterInfestations.CompSpawnerPawns.CompTick on a map-gen BI_Hive at (147,204), far from every site; not in the control because it fires on the hive's spawn timer. | 0e960f32f (P3 destroys non-player-faction buildings, as it already destroyed non-colonist pawns) | pending |
| B7, B7b (run 6) | harness: core framed its site at the kept zoom; the map started at root 11 (12x6 view), so lifted strands were off screen (swayDraws 0). | 54b2234b1 (frame_fit for every core SITE framing) | pending |
| SL2 (run 6) | CHECK: an idle colonist legitimately took the Dropped reel's kept Deploy order via the WorkGiver before the save, so 2 pawns had our carry driver deep-saved (design section 11's accepted case); the cap counted only the staged carrier. | 54b2234b1 (cap = colonists on RM_CarryHoseEnd/RM_RetractHose at the save) | pending |
| Z (run 6) | RimFridge StartedOrLoadedGame NRE + its missing ResearchProjectDef fired outside the control window. | 54b2234b1 (an error whose first frame is another mod's namespace, or whose text says [Source: other mod], is listed as that mod's; vanilla frames, stackless unknowns and anything naming GSS stay charged; selftest 6.x) | pending |
| H9 (run 7) | site margin: minBendRadius 2 makes the lead-out 5.6 + a 4-wide turn; the hose site had 4 cells west. | 9536a39f7 (hose SITE 10 cells west) | pending |
| SL4 (run 7) | harness: an idle colonist resumed reel 1's kept order (staged Dropped, saved Laid) / p2 busy, reel 2 never Carrying. | 9536a39f7 (others drafted during staging and carry rows), 963c8f7ab (all colonists drafted at preflight) | pending |
| MX_H02 (run 7) | 1 unwalkable hose point once; 0 in 15 reruns on another map. Not diagnosed: the census now reports unwalkableAt (cell, block kind, things, terrain). | 9536a39f7 (diagnostic) | pending |
| audit (fresh Opus reviewer, read-only) | 8 more fragile spots: fixed save sleeps, carry site margin, S9/B3/B6b on-screen reads after camera moves, B7 calm-map guard, wandering colonists, reveal visitor. | 963c8f7ab | pending |
| Z (run 8) | vanilla Log.ErrorOnce "Faction leader for <campaign faction> is null." (Faction.FactionTick, RimSage) fired once between P2 and the control. | 96491e5ef (control window opens at P2's log base) | pending |
| CR6, SL2/SL3 (run 9) | environment: a predator (wild animals respawn after P3's sweep) stabbed two colonists down; the carrier dropped the retract, the save staging broke. | e5809c0f4 (non-colonist pawns destroyed before every block) | pending |
| SL3 (run 10) | harness/world drift: the legacy hose (site corner) showed a lay before the save that the world no longer gave; reload is deterministic (3 loads, same hash, reload_probe.py). | 08b772a08 (251 ticks = one corridor-check cycle before the staging; site 6 cells past the lay) | pending |
| B3 | PASS in every full-list run since (not reproduced). | - | pending |

## Checks changed and why
- validation_hose.py MAZE / FILLER / MAZE_LEN comment (+ HoseSelfTest.MazeRows): old geometry was impossible under the owner's lead-out ruling; same two-option walk, same rows, same thresholds.
- SITE_R 6 cells wider west; RB/RC moved (24/56): same as the 10-09 hose-matrix soil-margin cure; RL2/RL8 premise (A-C beyond one hose) kept.
- P1 reads feedDraws from a census at P1 time: the old read sat inside a documented 60-tick port cache.
No threshold was loosened.

## Lessons (filed in infrastructure/state/lessons/, commit 8df8e14b1)
1. Tier label ≠ mod list: P2/L1 only check presence; read len(env.running) before comparing runs. -> rimworld-load-round
2. A ruling that REFUSES a behaviour invalidates live sites built before it; 1x1 offline models hide it. -> rimworld-debug-testing
3. Tick-keyed mod caches hold stale answers across many bridge calls (game stepped a few ticks). -> rimbridge
4. Polling Player.log for "Bridge token:" after relaunch matches the OLD log; also require a small line count. -> rimworld-load-round
5. list_logs limit 500 on an hours-old game misses the startup [RimBridge] line -> P2 UNMEASURED. -> rimbridge
6. A precheck on a simplified model accepted orders the real op refused; gate on a trial run. -> rimworld-modding

## Open questions
- None for the owner. Follow-up (BENCH's call): the 7 full-list-only reds (B3, B4d, R2, S9d, SL3, SL4, Z) need a proof run on the 550-mod list
  (~15 min load + ~15 min run) to tell harness timing on a slow frame rate from a real cross-mod interaction.
