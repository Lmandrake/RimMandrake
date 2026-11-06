# HARNESS_REPAIR_CAUSE_4F477502

Filed by testq ingest.repair() (TESTQ_REPAIR_FIX_TICKETS_NAME_THEIR_PASS). A harness fault: the run measured nothing for what it held, so no verdict was recorded.

## spec

- cause signature: `LOAD: CFBEE (mono-#-bdwgc) mono_profiler_init_etw # (KERNEL#) BaseThreadInitThunk # (n`
- job `J20261106T122857Z-88bde4`, attempt `J20261106T122857Z-88bde4.a1`, mod Graffiti, host stevedesktop, outcome INVALID/LOAD
- chains held without a verdict: the whole job (no sheet)
- runner note: CFBEE (mono-2.0-bdwgc) mono_profiler_init_etw 0x00007FFFFB157374 (KERNEL32) BaseThreadInitThunk 0x00007FFFFB2FCC91 (ntdll) RtlUserThreadStart  ========== END OF STACKTRACE ===========  A crash has been intercepted by the crash handler. For call stack and other details, see the latest crash report ge
- read the sighting: `python3 src/RimMandrake/Utils/testq/testq.py show J20261106T122857Z-88bde4`
- later sightings land as `seen again in testq <attempt>` notes on this item: re-run those jobs too.

## classify

Decide the class FIRST, from the sighting, before changing any code. Prior from the cause kind `LOAD`: HARNESS.
- ENVIRONMENT (the host: SIMD fault, reboot, disk) was checked at filing: 22 known fault window(s) in fault_windows.json, none overlaps the run (2026-11-06T12:30:09Z .. 2026-11-06T12:32:31Z). If the host still did it, drop this item with that evidence; never change the harness for a host fault.
- MOD: the mod under test stopped the harness reading it. File a finding or item on the mod and supersede this one; the harness is not changed.
- SITE: the test site (map, fixture, quiet hold, a surprise event) did it. Fix the staging, not the check.
- HARNESS: the harness's own code. Fix it here.

## verify

Pass = the SAME job re-run yields a verdict. After the fix is published, queue it again:

    python3 src/RimMandrake/Utils/testq/testq.py submit Graffiti --chains forced_paint_job,mental_break_spree,spree_wall --purpose guard --by BENCH --sha <the fix's published sha> --for-item STEVE_LANE_UNSTICK_BRAKED_UNOWNED_5CB3 --profile targeted

and when it finishes: `python3 src/RimMandrake/Utils/testq/retest.py passed <new job id> HARNESS_REPAIR_CAUSE_4F477502` exits 0 (the run is DONE, rows carry PASS/FAIL/SKIP, and none carries this cause). A FAIL verdict passes this item: a real FAIL is a verdict.

## negative control

`python3 src/RimMandrake/Utils/testq/retest.py passed J20261106T122857Z-88bde4 HARNESS_REPAIR_CAUSE_4F477502` must exit 1 both before and after the fix: the original sighting still carries the cause. If it exits 0, the fix silenced the detector.

## forbidden

- heal: no retry, auto-restart or self-repair that turns the fault into a pass without removing its cause.
- tolerance: no widened timeout, threshold or budget that lets the same fault through unseen.
- drop the check: no removed row, chain, `retest.CAUSES` pattern or validity test; no row re-labelled to escape it.

## criteria

- the class is recorded on this item (note) with its evidence before the fix;
- `retest.py passed <re-run job> HARNESS_REPAIR_CAUSE_4F477502` exits 0 on a job run at the fix's sha;
- the negative control above exits 1.
