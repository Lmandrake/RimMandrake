# canon_check v2 prototype — 2026-10-09 (BENCH helper; running notes)

## Built
- `src/RimMandrake/Utils/artpipe/canon_check.py`: `grade(..., mode="v2")` / CLI `--mode v2` (default v1; daemon untouched; v2 never writes the manifest).
  v2 = call A (describe canon images first, then render, no checklist) -> call B (v1 prompt + both descriptions + 2 GATE lines: body plan, colour layout; canon jobs only).
- `canon_check_labelset.py` (owner-label join), `canon_check_validate.py` (plan/run/table, resumable; results in `Transient/canon_check_v2/`).

## Label-set finding (changes the leniency report's number)
Report's 23 owner-rejected renders reproduce, BUT 16 of the 23 shas also carry a sheet `keep` ruling (before or after the reject) -> marked `conflicted`.
Only 7 are clean (no keep event). Reported as separate strata. 3 more keep-ruled shas whose reject says only "regenerate the description to match the appearance" are NOT art rejects and are excluded.
Split by subject: tune = eopie, iriaz, worrt, skennet (11 rejects); held-out = the other 12. Keeps split by md5(subject)%2.
v1 numbers = verdicts already stored in manifests (not re-spent).

Meter at start: primary_used_percent 62 (latest manifest meter_after); stop >80.

## Tune half (21 items; no prompt wording changed after seeing it — pipeline check only)
v1 rejects caught 0/11, keeps failed 1/10; v2 caught 5/11, keeps failed 3/10 (2 of those 3 are gorg/longtailgorg renders — subjects with owner rejects elsewhere).
Skennet (owner-note, no canon image) 0/3: the gate lines are canon-only, so owner-note jobs are structurally uncaught.

## Results (61 renders: 23 owner rejects + 8 v1-FAIL keeps + 22 random v1-PASS keeps, 1 subject-stratified per kind)
Rejects: 16 are `conflicted` (also keep-ruled in a sheet), all canon-kind; 7 clean, all owner-note kind (no canon image).

| split | grader | rejects caught | v1-PASS keeps false-failed | v1-FAIL keeps (old false fails) still failed |
|---|---|---|---|---|
| tune (11 rej, 9+1 keeps) | v1 | 0/11 | 0/9 | 1/1 |
| tune | v2 | 5/11 | 3/9 | 0/1 |
| HELD-OUT (12 rej, 13+7 keeps) | v1 | 0/12 | 0/13 | 7/7 |
| HELD-OUT | v2 | 6/12 | 6/13 | 3/7 |
| all | v2 | 11/23 | 9/22 | 3/8 |
No prompt wording was changed after seeing results (tune half used only as a pipeline check), so the held-out number is not fitted.

By stratum (all): canon-kind conflicted rejects 11/16 caught; owner-note clean rejects 0/7 (gates are canon-only; owner notes carry no canon image).
Only 1 of 23 v2 FAILs came from gate lines alone; the rest also fail a Must-show line, i.e. the descriptions make the per-line grading stricter.
Honest read: v2 catches ~2/3 of canon-kind rejects but fails ~41% of random previously-passing keeps (v1: 0%); v1 on the full 551 keeps had 1.5% false fail.
v2 does not clearly beat v1: it trades catch rate for a false-fail rate that would requeue ~40% of good renders. Caveat: some "keeps" that v2 failed are subjects with owner rejects (gorg, longtailgorg, hawkbat), so v2 may be partly right, and the 16 conflicted labels are noisy. N is small.
v1 numbers are the manifest-stored verdicts, not re-run. Cost: 61 items x 2 calls = ~122 codex gpt-6.1-sol/high vision calls (+2 pilot items). Codex meter: not measurable from my runs (latest manifest meter_after = 62.0% pre-run; never above 80 by that reading, but it does not include these calls).
Raw: `Transient/canon_check_v2/set.json`, `results_v2.jsonl`.

## Selftest
selftest_canon_check.py passes (new test_v2_mode, mocked). run_selftests: 4 fails, 3 unrelated pre-existing (selftest_tool_metadata DLL surface, selftest_items_glob_live drift, selftest_utinnipatches_dump missing RUT_JawaReturnTow), 1 was mine and fixed.
