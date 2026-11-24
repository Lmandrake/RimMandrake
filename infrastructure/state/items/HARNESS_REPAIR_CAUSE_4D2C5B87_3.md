# HARNESS_REPAIR_CAUSE_4D2C5B87_3

Filed by testq ingest.repair() (TESTQ_REPAIR_FIX_TICKETS_NAME_THEIR_PASS). A harness fault: the run measured nothing for what it held, so no verdict was recorded.

## spec

- cause signature: `surprise: surprise: safe_advance stopped after # of # tick(s): hurt: health # -> #; newest`
- job `J20261124T075639Z-b97376`, attempt `J20261124T075639Z-b97376.a1`, mod FlowWorks, host stevedesktop, outcome DONE/None
- chains held without a verdict: `swept`
- runner note: modcheck exit 1; {'PASS': 40, 'UNMEASURED': 12}
- read the sighting: `python3 src/RimMandrake/Utils/testq/testq.py show J20261124T075639Z-b97376`
- later sightings land as `seen again in testq <attempt>` notes on this item: re-run those jobs too.

## classify

Decide the class FIRST, from the sighting, before changing any code. Prior from the cause kind `surprise`: SITE.
- ENVIRONMENT (the host: SIMD fault, reboot, disk) was checked at filing: 57 known fault window(s) in fault_windows.json, none overlaps the run (2026-11-24T08:00:15Z .. 2026-11-24T08:49:09Z). If the host still did it, drop this item with that evidence; never change the harness for a host fault.
- MOD: the mod under test stopped the harness reading it. File a finding or item on the mod and supersede this one; the harness is not changed.
- SITE: the test site (map, fixture, quiet hold, a surprise event) did it. Fix the staging, not the check.
- HARNESS: the harness's own code. Fix it here.

## verify

Pass = the SAME job re-run yields a verdict. After the fix is published, queue it again:

    python3 src/RimMandrake/Utils/testq/testq.py submit FlowWorks --chains swept,thirst,fuel_moat_astrofuel,liquid_heat --purpose guard --by BENCH --sha <the fix's published sha> --profile targeted

and when it finishes: `python3 src/RimMandrake/Utils/testq/retest.py passed <new job id> HARNESS_REPAIR_CAUSE_4D2C5B87_3` exits 0 (the run is DONE, rows carry PASS/FAIL/SKIP, and none carries this cause). A FAIL verdict passes this item: a real FAIL is a verdict.

## negative control

`python3 src/RimMandrake/Utils/testq/retest.py passed J20261124T075639Z-b97376 HARNESS_REPAIR_CAUSE_4D2C5B87_3` must exit 1 both before and after the fix: the original sighting still carries the cause. If it exits 0, the fix silenced the detector.

## forbidden

- heal: no retry, auto-restart or self-repair that turns the fault into a pass without removing its cause.
- tolerance: no widened timeout, threshold or budget that lets the same fault through unseen.
- drop the check: no removed row, chain, `retest.CAUSES` pattern or validity test; no row re-labelled to escape it.

## criteria

- the class is recorded on this item (note) with its evidence before the fix;
- `retest.py passed <re-run job> HARNESS_REPAIR_CAUSE_4D2C5B87_3` exits 0 on a job run at the fix's sha;
- the negative control above exits 1.
