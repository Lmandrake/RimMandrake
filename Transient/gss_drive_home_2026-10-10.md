# GimmeSomeSlack — drive home (2026-10-10)

**Status:** DONE on the test tier. Full `proof_all.py --live` (shots ON) = **151 PASS / 0 FAIL**:
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
