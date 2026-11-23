# HARNESS_REPAIR_CAUSE_01DAD227_2

Filed by testq ingest.repair() (TESTQ_REPAIR_FIX_TICKETS_NAME_THEIR_PASS). A harness fault: the run measured nothing for what it held, so no verdict was recorded.

## spec

- cause signature: `site_hold: could not hold the site quiet -- not a verdict on the mod: site hold raised Help`
- job `J20261123T053152Z-7fe791`, attempt `J20261123T053152Z-7fe791.a1`, mod Pyrelands, host stevedesktop, outcome DONE/None
- chains held without a verdict: `rite_hook_alone`
- runner note: modcheck exit 1; {'UNMEASURED': 2, 'NOT_RUN': 6}
- read the sighting: `python3 src/RimMandrake/Utils/testq/testq.py show J20261123T053152Z-7fe791`
- later sightings land as `seen again in testq <attempt>` notes on this item: re-run those jobs too.

## classify

Decide the class FIRST, from the sighting, before changing any code. Prior from the cause kind `site_hold`: SITE.
- ENVIRONMENT (the host: SIMD fault, reboot, disk) was checked at filing: 57 known fault window(s) in fault_windows.json, none overlaps the run (2026-11-23T05:33:42Z .. 2026-11-23T05:55:15Z). If the host still did it, drop this item with that evidence; never change the harness for a host fault.
- MOD: the mod under test stopped the harness reading it. File a finding or item on the mod and supersede this one; the harness is not changed.
- SITE: the test site (map, fixture, quiet hold, a surprise event) did it. Fix the staging, not the check.
- HARNESS: the harness's own code. Fix it here.

## verify

Pass = the SAME job re-run yields a verdict. After the fix is published, queue it again:

    python3 src/RimMandrake/Utils/testq/testq.py submit Pyrelands --chains burn_line,rite_hook_alone --purpose fix --by BENCH --sha <the fix's published sha> --row-item burn_line=RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_VISIT_TWO_RUN_TWO --profile targeted

and when it finishes: `python3 src/RimMandrake/Utils/testq/retest.py passed <new job id> HARNESS_REPAIR_CAUSE_01DAD227_2` exits 0 (the run is DONE, rows carry PASS/FAIL/SKIP, and none carries this cause). A FAIL verdict passes this item: a real FAIL is a verdict.

## negative control

`python3 src/RimMandrake/Utils/testq/retest.py passed J20261123T053152Z-7fe791 HARNESS_REPAIR_CAUSE_01DAD227_2` must exit 1 both before and after the fix: the original sighting still carries the cause. If it exits 0, the fix silenced the detector.

## forbidden

- heal: no retry, auto-restart or self-repair that turns the fault into a pass without removing its cause.
- tolerance: no widened timeout, threshold or budget that lets the same fault through unseen.
- drop the check: no removed row, chain, `retest.CAUSES` pattern or validity test; no row re-labelled to escape it.

## criteria

- the class is recorded on this item (note) with its evidence before the fix;
- `retest.py passed <re-run job> HARNESS_REPAIR_CAUSE_01DAD227_2` exits 0 on a job run at the fix's sha;
- the negative control above exits 1.
