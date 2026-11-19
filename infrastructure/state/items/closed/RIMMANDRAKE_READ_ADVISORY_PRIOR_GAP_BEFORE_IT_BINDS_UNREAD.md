# RIMMANDRAKE_READ_ADVISORY_PRIOR_GAP_BEFORE_IT_BINDS_UNREAD

## spec
A coverage refusal stored ADVISORY because no second reader graded its criterion (llm_reader returned nothing: `unread`) binds unread on the retry. Found by Codex's third look at src/RimMandrake/rimflow/coverage_judge.py on RIMMANDRAKE_FIX_COVERAGE_JUDGE_TEN_FINDINGS_FIFTH_COUNT_CLEAN, 2026-11-18; reproduced by the filer [measured]: look 1 refuses g1 with the reader returning None (advisory); look 2 (brief CALIBRATED) answers g1 still open with no new gap. rejudge_slots carries g1 as `carried`; reader_items excludes carried gaps ("checked when written"), so second_read has nothing to read, `unread` is None, and RC.submit counts the refusal: contract counted True, advisory False, and it is the second not_covered, so judging STOPS on a refusal whose criterion no reader ever graded.

Where: coverage_judge.py reader_items (excludes every carried gap), contract_verdict (leaves carried gaps out of refusals), rejudge_slots/delta_merge (carry the advisory prior's gaps as trusted).

Smallest fix (suggested, not binding): a carried gap whose `criterion_by` is not `second_reader` (it was never graded: `judge (no second read)`) is shown to the second reader on the look that carries it, and binds only on its grade; if the reader again returns nothing, the look stays advisory as look 1 did. A gap the reader graded stays out of the read (control).

## verify
Acceptance test: `python3 design/specs/2026-11-17-judge-flaws-not-polish/tickets/case_advisory_prior_gap_gets_its_read.py` — 3 cases, exit 0 when right; watched failing on 19d3e29026 plus the ten-findings fix (1 wrong: the carried gap is never shown to a reader and the look is not advisory). Note: coverage_judge.py is in the coverage_judge calibration brief (UNTESTED now); recalibration is RIMMANDRAKE_RECALIBRATE_JUDGE_THEN_RESTAMP_PYRELANDS_ONCE.

## criteria
- The case file exits 0: a never-graded carried gap is read before it binds (or the look stays advisory); a graded one is not re-read.

## refs
file: src/RimMandrake/rimflow/coverage_judge.py
file: design/specs/2026-11-17-judge-flaws-not-polish/tickets/case_advisory_prior_gap_gets_its_read.py
