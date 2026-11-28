# Polish beside design/specs/2026-11-24-wait-lane-job/boundary.md

## (fresh read, WB-pipeline-read-utils-20261128-092119, 2026-11-28)
- not handled (for the page's DOES NOT SURVIVE): `src/RimMandrake/Utils/testq/testq.py` `wait_for` returns hung at `silent >= HUNG_S` (9000 s) before a caller's longer deadline when the tick has been dead for 2.5 h.
