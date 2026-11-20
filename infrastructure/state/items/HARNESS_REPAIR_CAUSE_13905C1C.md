# HARNESS_REPAIR_CAUSE_13905C1C

Filed by testq ingest.repair() (TESTQ_REPAIR_FIX_TICKETS_NAME_THEIR_PASS). A harness fault: the run measured nothing for what it held, so no verdict was recorded.

## spec

- cause signature: `GAME: native_crash_in_load`
- job `J20261115T135012Z-7ecbdd`, attempt `J20261115T135012Z-7ecbdd.a1`, mod FlowWorks, host stevedesktop, outcome INVALID/LOAD
- chains held without a verdict: the whole job (no sheet)
- runner note: 4FBEE (mono-2.0-bdwgc) mono_profiler_init_etw 0x00007FFDF1A67374 (KERNEL32) BaseThreadInitThunk 0x00007FFDF20FCC91 (ntdll) RtlUserThreadStart  ========== END OF STACKTRACE ===========  A crash has been intercepted by the crash handler. For call stack and other details, see the latest crash report ge
- read the sighting: `python3 src/RimMandrake/Utils/testq/testq.py show J20261115T135012Z-7ecbdd`
- later sightings land as `seen again in testq <attempt>` notes on this item: re-run those jobs too.

## classify

Decide the class FIRST, from the sighting, before changing any code. Prior from the cause kind `GAME`: ENVIRONMENT.
- ENVIRONMENT (the host: SIMD fault, reboot, disk) was checked at filing: 41 known fault window(s) in fault_windows.json, none overlaps the run (2026-11-15T13:54:05Z .. 2026-11-15T13:58:08Z). If the host still did it, drop this item with that evidence; never change the harness for a host fault.
- MOD: the mod under test stopped the harness reading it. File a finding or item on the mod and supersede this one; the harness is not changed.
- SITE: the test site (map, fixture, quiet hold, a surprise event) did it. Fix the staging, not the check.
- HARNESS: the harness's own code. Fix it here.

## verify

Pass = the SAME job re-run yields a verdict. After the fix is published, queue it again:

    python3 src/RimMandrake/Utils/testq/testq.py submit FlowWorks --chains plot_H_depth_ladder --purpose guard --by BENCH --sha <the fix's published sha> --for-item RIMMANDRAKE_AUTHOR_TESTQ_BLOCKS_STEVE_SITS_IDLE_BY_RULE --profile targeted

and when it finishes: `python3 src/RimMandrake/Utils/testq/retest.py passed <new job id> HARNESS_REPAIR_CAUSE_13905C1C` exits 0 (the run is DONE, rows carry PASS/FAIL/SKIP, and none carries this cause). A FAIL verdict passes this item: a real FAIL is a verdict.

## negative control

`python3 src/RimMandrake/Utils/testq/retest.py passed J20261115T135012Z-7ecbdd HARNESS_REPAIR_CAUSE_13905C1C` must exit 1 both before and after the fix: the original sighting still carries the cause. If it exits 0, the fix silenced the detector.

## forbidden

- heal: no retry, auto-restart or self-repair that turns the fault into a pass without removing its cause.
- tolerance: no widened timeout, threshold or budget that lets the same fault through unseen.
- drop the check: no removed row, chain, `retest.CAUSES` pattern or validity test; no row re-labelled to escape it.

## criteria

- the class is recorded on this item (note) with its evidence before the fix;
- `retest.py passed <re-run job> HARNESS_REPAIR_CAUSE_13905C1C` exits 0 on a job run at the fix's sha;
- the negative control above exits 1.
