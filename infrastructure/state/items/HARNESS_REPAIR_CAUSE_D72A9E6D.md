# HARNESS_REPAIR_CAUSE_D72A9E6D

Filed by testq ingest.repair() (TESTQ_REPAIR_FIX_TICKETS_NAME_THEIR_PASS). A harness fault: the run measured nothing for what it held, so no verdict was recorded.

## spec

- cause signature: `HANG: modcheck hung past #s twice (one clean restart between)`
- job `J20261124T190317Z-6b7bd8`, attempt `J20261124T190317Z-6b7bd8.a1`, mod Pyrelands, host stevedesktop, outcome INVALID/HANG
- chains held without a verdict: the whole job (no sheet)
- runner note: modcheck hung past 2700s twice (one clean restart between)
- read the sighting: `python3 src/RimMandrake/Utils/testq/testq.py show J20261124T190317Z-6b7bd8`
- later sightings land as `seen again in testq <attempt>` notes on this item: re-run those jobs too.

## classify

Decide the class FIRST, from the sighting, before changing any code. Prior from the cause kind `HANG`: HARNESS.
- ENVIRONMENT (the host: SIMD fault, reboot, disk) was checked at filing: 57 known fault window(s) in fault_windows.json, none overlaps the run (2026-11-24T19:11:51Z .. 2026-11-24T21:06:23Z). If the host still did it, drop this item with that evidence; never change the harness for a host fault.
- MOD: the mod under test stopped the harness reading it. File a finding or item on the mod and supersede this one; the harness is not changed.
- SITE: the test site (map, fixture, quiet hold, a surprise event) did it. Fix the staging, not the check.
- HARNESS: the harness's own code. Fix it here.

## verify

Pass = the SAME job re-run yields a verdict. After the fix is published, queue it again:

    python3 src/RimMandrake/Utils/testq/testq.py submit Pyrelands --chains burn_line,ash_fertility_watered,fresh_burn_bonus --purpose fix --by BENCH --sha <the fix's published sha> --for-item RIMMANDRAKE_RELOAD_SITE_AFTER_A_CHAIN_KILLS_ITS_COLONIST --profile targeted

and when it finishes: `python3 src/RimMandrake/Utils/testq/retest.py passed <new job id> HARNESS_REPAIR_CAUSE_D72A9E6D` exits 0 (the run is DONE, rows carry PASS/FAIL/SKIP, and none carries this cause). A FAIL verdict passes this item: a real FAIL is a verdict.

## negative control

`python3 src/RimMandrake/Utils/testq/retest.py passed J20261124T190317Z-6b7bd8 HARNESS_REPAIR_CAUSE_D72A9E6D` must exit 1 both before and after the fix: the original sighting still carries the cause. If it exits 0, the fix silenced the detector.

## forbidden

- heal: no retry, auto-restart or self-repair that turns the fault into a pass without removing its cause.
- tolerance: no widened timeout, threshold or budget that lets the same fault through unseen.
- drop the check: no removed row, chain, `retest.CAUSES` pattern or validity test; no row re-labelled to escape it.

## criteria

- the class is recorded on this item (note) with its evidence before the fix;
- `retest.py passed <re-run job> HARNESS_REPAIR_CAUSE_D72A9E6D` exits 0 on a job run at the fix's sha;
- the negative control above exits 1.
