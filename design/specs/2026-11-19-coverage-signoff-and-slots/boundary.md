# BOUNDARY: what a coverage sign-off resets, and what closes a repaired slot, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/coverage_judge.py` (`since_signoff`, `counting_window`, `stop_reason`, `_caps`,
`_slots`, `delta_plan`) and the counts `pipe show` prints for them (`src/RimMandrake/rimflow/pipeline_control.py`,
`_cov_since`). Items: `RIMMANDRAKE_RESET_COVERAGE_STRIKES_AFTER_SIGNOFF_OLD_TWO_COUNTED` (Graffiti, 2026-11-17: rounds
not_covered, not_covered, covered, not_covered stopped judging on its first refusal after passing) and
`RIMMANDRAKE_REQUIRE_PASSING_ROW_TO_CLOSE_REPAIRED_SLOT` (Codex review of coverage_judge.py, 2026-11-18, round 2
finding 1: a slot answered `repaired` closed with no checklist row on its ids, and coverage could sign). Written
2026-11-19 for `RIMMANDRAKE_READY_PIPELINE_FOR_WRECKED_MACHINES_HE_HOLDS_GO`. Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_coverage_signoff.py`. This page covers only these two rules; the rest of
`coverage_judge.py` has no page yet.

## ACCEPTS (the only inputs this is built for)

- **a-stage-json.** A concept's `stage.json` as a dict: `coverage_rounds` (oldest first, each with `verdict`
  `covered`, `not_covered`, `malformed` or none), and optionally `coverage_releases`.
- **a-delta-answer.** A delta judge's record (`checklist` rows with `parts`, `gaps`) and its `repairs` answer, merged
  against the plan `delta_plan` made from the prior `not_covered` verdict.

## DOES NOT SURVIVE (not promised)

- **a-slot-with-no-ids.** A slot whose gap names no checklist id closes on its `repaired` answer alone: there is no
  row to require.
- **rounds-out-of-order.** The window is read by position in `rounds()`, oldest first; a hand-edited stage.json with
  rounds out of time order is read as written.
- **system-faults.** The count of judge rounds that died of a system cause (JUDGE_FAULT_LIMIT) is not reset by a
  sign-off: a system fault is no look and stays counted from the release, as before.

## PROMISES (each one is owed a test of the same name)

- **strikes-count-from-the-last-sign-off.** A `not_covered` verdict before the last `covered` verdict counts nothing
  toward the strike limit: rounds not_covered, not_covered, covered, not_covered do not stop judging.
- **runs-and-spend-count-from-the-last-sign-off.** The run cap and the spend cap count only rounds after the last
  `covered` verdict, so judge runs that ended in a sign-off do not stop the next episode.
- **the-strike-limit-still-binds-without-a-sign-off.** With no `covered` verdict since the release (or ever), the
  strike, run and spend limits bind exactly as before; strikes after a sign-off still stop at the limit.
- **a-sign-off-after-a-release-ends-the-release.** A `covered` verdict after a release ends that release's one-look
  account: a later refusal is the first strike of a new episode, not the release's spent look.
- **malformed-verdicts-are-not-reset-by-a-sign-off.** Malformed verdicts are the brief failing its refusal contract,
  not a look at the design: a sign-off does not reset their count.
- **pipe-show-counts-the-window-the-stop-reads.** `pipe show`'s cov-nc, cov-runs and look counts are taken over the
  same window `stop_reason` reads.
- **a-repaired-slot-closes-only-with-a-passing-row-per-id.** A slot closes only when every one of its ids has a
  checklist row this look and every such row is all ok, whatever its `repairs` answer says.
- **a-claimed-slot-is-owed-its-rows.** The delta plan asks the judge for a row on every id of every slot the
  Designer claims fixed, so a claimed repair always has its way to close. A carried slot nobody claims is not owed
  its rows (the delta stays scoped to claimed and changed rows) and closes only if the judge writes them.
- **an-unchecked-repair-never-signs.** The Codex scenario (a prior failed row on a slot's id, a sheet-only change, no
  fix claim, `repaired: true`, an empty checklist and no gaps) merges to `not_covered` with the slot still open.

Later lists beside this page: `polish.md` and `next_version.md` (none yet).
