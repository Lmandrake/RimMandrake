# HARNESS_REPAIR_CAUSE_C1B99C19_2

Filed by testq ingest.repair() (TESTQ_REPAIR_FIX_TICKETS_NAME_THEIR_PASS). A harness fault: the run measured nothing for what it held, so no verdict was recorded.

## spec

- cause signature: `driver_undelivered: UNMEASURED: no proof_hose result at the current mod hash: run `python.exe <path>`
- job `J20261123T034430Z-894ebb`, attempt `J20261123T034430Z-894ebb.a1`, mod FlowWorks, host stevedesktop, outcome DONE/None
- chains held without a verdict: `hose_live_rows`
- runner note: modcheck exit 1; {'PASS': 111, 'FAIL': 5, 'UNMEASURED': 46}
- read the sighting: `python3 src/RimMandrake/Utils/testq/testq.py show J20261123T034430Z-894ebb`
- later sightings land as `seen again in testq <attempt>` notes on this item: re-run those jobs too.

## classify

Decide the class FIRST, from the sighting, before changing any code. Prior from the cause kind `driver_undelivered`: HARNESS.
- ENVIRONMENT (the host: SIMD fault, reboot, disk) was checked at filing: 57 known fault window(s) in fault_windows.json, none overlaps the run (2026-11-23T03:46:17Z .. 2026-11-23T04:55:09Z). If the host still did it, drop this item with that evidence; never change the harness for a host fault.
- MOD: the mod under test stopped the harness reading it. File a finding or item on the mod and supersede this one; the harness is not changed.
- SITE: the test site (map, fixture, quiet hold, a surprise event) did it. Fix the staging, not the check.
- HARNESS: the harness's own code. Fix it here.

## verify

Pass = the SAME job re-run yields a verdict. After the fix is published, queue it again:

    python3 src/RimMandrake/Utils/testq/testq.py submit FlowWorks --chains thirst,hose_live_rows,sprinklers,core_live_rows --purpose fix --by BENCH --sha <the fix's published sha> --row-item core_live_rows=KNOWN_GOOD_AUDIT_MEASURE_SWEEP_MISSES --row-item hose_live_rows=KNOWN_GOOD_AUDIT_MEASURE_SWEEP_MISSES --row-item sprinklers=KNOWN_GOOD_AUDIT_MEASURE_SWEEP_MISSES --row-item thirst=THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY --profile targeted

and when it finishes: `python3 src/RimMandrake/Utils/testq/retest.py passed <new job id> HARNESS_REPAIR_CAUSE_C1B99C19_2` exits 0 (the run is DONE, rows carry PASS/FAIL/SKIP, and none carries this cause). A FAIL verdict passes this item: a real FAIL is a verdict.

## negative control

`python3 src/RimMandrake/Utils/testq/retest.py passed J20261123T034430Z-894ebb HARNESS_REPAIR_CAUSE_C1B99C19_2` must exit 1 both before and after the fix: the original sighting still carries the cause. If it exits 0, the fix silenced the detector.

## forbidden

- heal: no retry, auto-restart or self-repair that turns the fault into a pass without removing its cause.
- tolerance: no widened timeout, threshold or budget that lets the same fault through unseen.
- drop the check: no removed row, chain, `retest.CAUSES` pattern or validity test; no row re-labelled to escape it.

## criteria

- the class is recorded on this item (note) with its evidence before the fix;
- `retest.py passed <re-run job> HARNESS_REPAIR_CAUSE_C1B99C19_2` exits 0 on a job run at the fix's sha;
- the negative control above exits 1.
