# Done claim (partial: parked, see BLOCKED.md)

- true: the class is recorded on this item (note) with its evidence before the fix; | evidence: `whittle/harness_repair_cause_17704c88/evidence/sighting_record.json` `whittle/harness_repair_cause_17704c88/evidence/deploy_closure_head.txt`
- unseen: `retest.py passed <re-run job> HARNESS_REPAIR_CAUSE_17704C88` exits 0 on a job run at the fix's sha; | evidence: `whittle/harness_repair_cause_17704c88/evidence/rerun_job_pending.txt`
- true: the negative control above exits 1. | evidence: `whittle/harness_repair_cause_17704c88/evidence/negative_control.txt`

The class note is BENCH's 2026-11-06T21:05 HARNESS note (`rimflow show`), timestamped before the fix's ledger close; the fix (73760d1e3d) is published and its closure output at HEAD is in deploy_closure_head.txt. Selftests at HEAD: `evidence/selftests_head.txt` (3/3 green).

## What I'm least sure about
Whether the re-run, when the lane resumes, hits a different fault first. The only post-fix Pyrelands job (J20261106T105123Z-665f3a) died REFUSED/SYNC on a dirty runner clone, so no game has yet loaded Pyrelands with WeatherSuite through testq.

## What I did not test
The live run itself: the lane is paused by owner order until 2026-11-19. The ssh fetch in retest.py was exercised against the real Archmagi queue (negative control) and a fake ssh in the selftest; the "ssh down" branch is untested.
