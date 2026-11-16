# ExplosiveKnockback road back after visit 2 — live holder run run-1794816087 (2026-11-16 PST)

Archmagi, RimWorld 1.6.4871, ExplosiveKnockback PROOF build from source 6624908423 (deployed DLL md5 8753d17373e353be5878f971edb04644),
FlowWorks deployed from the same main.

## sc_barrage_perf (RIMMANDRAKE_REPAIR_BARRAGE_FRAME_CRITERION_BASELINE_FAILS_TOO)
Full list (316 mods, ModsConfig = FULL), quicktest AridShrubland 250x250 (live_site.py --biome AridShrubland, 3 colonists, site_checked).
Command: `python.exe src\RimMandrake\ExplosiveKnockback\knockback_runner.py --scenes frame_probe_selfcheck,barrage_perf_off,barrage_perf --ticks 0 --real-seconds 25`
| run | control windowP99Ms | barrage windowP99Ms | verdict |
|---|---|---|---|
| 1 | 30.9 | 32.1 | PASS |
| 2 | 21.1 | 20.3 | PASS |
| 3 | 20.0 | 20.4 | PASS |
Evidence: sc_barrage_perf_run{1,2,3}.txt and the runner's run_*.jsonl beside this file.

## sc_pit_fetch (RIMMANDRAKE_FIX_DRY_PIT_HAULER_DESCENT_SWIMS_HID_IT)
Minimal list (34 mods, visit 2's env_minimal4.json exactly), quicktest AridShrubland, FlowWorks deployed from main.
Cause, read live with `RM_KnockbackProof.PitProbe` (proof build only) and the hauler's own job log (`sc_pit_fetch_hauler_joblog_before.txt`):
with the pits dry every gate was open (haul job offered, CanReach true, FlowWorks' RelativeVeto false, path found, portable ladder
lowered). The hauler climbed down and picked the stack up; vanilla's `Toils_Haul.CheckForGetOpportunityDuplicate` (a same-def stack
within 8 cells, found by `GenClosest.ClosestThingReachable`, a region search FlowWorks' reach veto never sees) then retargeted the
job at the CONTROL pit's stack 6 cells away. That pit's ladder is raised: `ErroredPather` at toil GotoThing, the carried stack dropped
on the ladder cell, the same job again, all day. With the control stack destroyed the stack and corpse were fetched
(`sc_pit_fetch_control_destroyed.txt`). Visit 1's rain-filled pits made the control pit swimmable, which hid it.
Scene fixes (RM_KnockbackProof.cs pit_goods_fetch; offline guard selftest_explosiveknockback_pit_fetch.py, red on the old layout):
the control pit sits in the scene's far corner (13+ cells); the main pit is 5 wide so the corpse lies inside it, not on an edge row
the rim touches; the corpse is un-forbidden (vanilla forbids a corpse dying outside the home area); the hauler is regenerated until it
can haul and the map's other colonists do not haul during the scene.
Acceptance `python.exe src\RimMandrake\ExplosiveKnockback\knockback_runner.py --scenes pit_goods_fetch --ticks 60000` after the fix:
run 1 FAIL (corpse out=False; first scene on a fresh map, cause not read), runs 2-5 PASS (`sc_pit_fetch_after_fix_run*.txt`).
The FlowWorks defect itself (duplicate pickup across a sealed pit) is filed for FlowWorks.

## sc_walk_raid (RIMMANDRAKE_FIX_WALK_RAID_SIX_FAILED_ROWS_AFTER_CRASHES)
Full list, `--save EK_WALK_RAID_BASE_20261115T173148` (the staged base). Run 3: cover rows FAIL with 0 descents; a fresh load showed
the rider falls (`sc_walk_raid_cover_rider.txt`), and stepping the order showed the FIRST storeroom shell breaks the cover and drops
the rider before the grenade (`sc_walk_raid_cover_steps.txt`). Harness: the grenade now goes first in each order and the cover is read
before it (W15/W16). Run 5: cover rows PASS in both orders; reload row read SAVE_DROPS_STATE from two leavings born after the save,
re-numbered by the load (+1000): the census keys such things by def and cell (W17). Gas rows FAIL in both orders: drifted gas relit
under a burned cell's fire burst again 30-60 ticks later; Explosive Knockback now bursts a cell at most once per 600 ticks (model
test with drift, selftest_explosiveknockback_gas_clumps.py). Runs 3-5 here predate the gas gate and the census fix in the game.
