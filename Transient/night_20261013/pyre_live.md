# Pyrelands short live checks - BENCH night helper, 2026-10-13

Tier ratchet_pilot (22) + mandrake.rm.patches = 23 mods (`Transient/bench_live_20261013c/ModsConfig.ratchet_pilot_plus_patches.xml`). Code from the
git archive at `D:\Luke\dev\_rmscratch\night_fw_20261013` (095517fafa; Pyrelands/Utils unchanged to HEAD), game pid 40844 killed by PID.
Owner ModsConfig md5 ee01dae9e30d121c78d88e474dacd8e8 before; `modset_builder --restore` verified the same after. Game down, bridge released.
Evidence and scripts: `D:\Luke\dev\RimMandrake` mirror path `Transient\night_20261013\pyre_live\` (census3.py, burrow_diag_chain.py, *.json, summ.py, Player.night_pyre.log).

## 1 PYRE_ANIMALS_DIAGNOSE_TEN_IS_NOT_TWELVE -> VARIANCE (close)
Three fresh Pyrelands site maps (`northstar_site.build_site`, fresh quicktest world each, 250x250, wild animals = faction None + Animal + not dead, read at tick 0 before save, then again after the fixture reload):
| site | tick-0 total | kinds | after reload |
|---|---|---|---|
| A (tile 5) | 17 | 4 (Gizka 10, Nuna 3, Sytheclaw 2, Flamefang 2) | 16 |
| B (tile 3) | 25 | 7 | 25 |
| C (tile 3) | 23 | 6 | 22 |
Lowest 16 >= 12 either way. With the 10 offline censuses (10,14,14,15,16,16,16,16,18,22) that is 1 of 13 under 12 (the p8a roll of 9 Gizka + 1 Flamefang). Variance; bar unchanged. Standing recommendation stays: the count is a weak instrument (points-based herds of tiny Gizka); a floor of ~8 or distinct-kinds would not flap.

## 2 PYRE_BURROWERS_DIAGNOSE_FLEE_BEFORE_DIVE -> Flee-before-dive NOT confirmed; real cause is a delayed first think pass
Probe = the real `burrowers` chain rewritten in a scratch copy of validation.py (`burrow_diag_chain.py`, NOT in the repo): Ashwallow at x+5 (near) or x+16 (control, 13-14 cells from the fire), fire 6x6, job sampled every 10 ticks via jawa/site_state.
- 25 trials total (6 cold, 19 warm; 3 of the warm ones are 13-14 cell controls). Flee was never seen BEFORE a dive. Control (13-14 cells) dove in 10 ticks every time.
- WARM trials (2nd+ trial on the same map) dive in 10-20 ticks: after the first burn the map stays in the standing-burn window (BURN_QUIET_TICKS 120000), so AnyBurn is already true. Not representative.
- COLD trials (first fire on a fresh map; 6 of them: run1 t0, run2 t0, run3 t0, cold_1..3 after a fixture reload): dive at 220, never within 300 (GotoWander x29, hediff not up), 270, 270, 380, 120 ticks. In every one the grazer sat in a `GotoWander` job for 11..35 samples, then `Wait_MaintainPosture`, then `RM_Burrow`. So: the burrow giver (Animal_PreWander, only consulted at a job boundary) is not asked while a long wander runs, and its first ask before the BurnLine measure says no.
- One Flee, AFTER a dive (cold_2): GotoWander x35, Wait_MaintainPosture, RM_Burrow x15 (380..520), then Flee x8 from 530 and RM_Burrowed gone: AnimalFlee preempted/ended the burrow job once the fire reached the grazer. Flee is a real interruption of the dive, but it follows it.
- So the repo chain's "never RM_Burrowed over 1500 ticks" is not explained by Flee-first in these 25 trials; the cold delay (up to >300 ticks) is real. The earlier failing samples (Flee x5, Wait x8) were not reproduced.
- C# fix direction (NOT built tonight, not a one-liner): on the BurnLine AnyBurn false->true edge (MapComponent_BurnLine.Measure), for each burrower-extension pawn inside detectionRadius of a fire call `pawn.jobs.CheckForJobOverride()` (or EndCurrentJob for wander jobs) so the PreWander giver runs now; and in RM_JobDriver_Burrow keep the dive alive against AnimalFlee (Harmony prefix JobGiver_AnimalFlee.TryGiveJob -> null when RM_Burrowed and burrow allowed). Alternative: accept ~400 ticks of latency and widen the row's sampling to 10 ticks over 600 ticks.

## Threats met (each -> TESTENV_* item)
| threat | where | action | item |
|---|---|---|---|
| two of three colonists died of the 52 C site heat (damage to the test) during an 11-trial, ~8000-tick burrow diag | run 3 | row restarted via a fixture reload per cold trial (colonists back to 3, no damage) | TESTENV_BURROW_HEAT_HARDEN_COLONISTS_COOKED |
| the chain aborted "safe_advance stopped: downed (health 0.26)" when the tracked grazer was burnt in the fire pad | run 2 | trials 0-8 kept; later runs sized to what fits | same item |
| bridge concurrency guard refused go_to_main_menu 37 s after my own previous python.exe sequel (stale pid of a finished run) | census run 2 | RM_ALLOW_CONCURRENT_BRIDGE=1 (I held the bridge) | TESTENV_GUARD_UNSTICK_BLOCKS_ITS_OWN_SEQUEL |
| `build_site` died PermissionError copying into saves_backup_<k> when the same site index k is reused (read-only copy of last backup) | census run 2 | used distinct k (12, 13) | TESTENV_SITE_BACKUP_REPAIR_READONLY_REUSE |
| repeated trials on one map are warm (standing-burn window) and dive in 10 ticks, hiding the cold delay | burrow diag | one trial per reloaded fixture | TESTENV_BURROW_COLD_PROVE_RELOAD_PER_TRIAL |

## Teardown
Game killed by PID 40844; 3 throwaway nightc* fixtures deleted from Saves; `modset_builder --restore` verified md5 ee01dae9e30d121c78d88e474dacd8e8; `./game --why "night Pyrelands checks done" down`; `rimflow bridge release`.
