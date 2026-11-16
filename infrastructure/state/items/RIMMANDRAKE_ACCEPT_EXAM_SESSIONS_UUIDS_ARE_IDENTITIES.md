# Designer exam must recognize fresh Claude CLI session UUID identities

## spec

Recognize the exact UUID session_id returned by a fresh Claude CLI exam helper as an agent identity, alongside existing helper and role-run identities. Preserve duplicate and author/examiner/challenger Reader rejection, including mixed annotated strings.

## verify

Run `python3 src/RimMandrake/rimflow/selftest_designer_stage.py`. The new regression failed on the base in two assertions. The updated run passes every assertion. Base and fixed outputs are retained in `design/concepts/LeaningScrub/exam_runs/uuid_regression_before.txt` and `uuid_regression_after.txt`. Run the real LeaningScrub Stage 4 check with fresh helper session UUIDs.

## criteria

All stage selftests pass. UUID identities are retained exactly. Fresh independent Readers pass identity validation. Duplicate, self-read, mixed legacy/UUID and malformed identities preserve their expected rejections.

## Watch out

Identity parsing also serves duplicate detection, role-label removal and comparison against the open run. Exam scoring and freshness requirements retain their existing checks.
