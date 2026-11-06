## spec
Step 1 of `design/RimMandrake/evidence_gate_enforce_before_deletes_2026-11-06.md`. That note holds the site, scope, fail
direction and reading; follow it.

The flip adds a refusal, so it does not land before RELENTLESS_MEASURE_THREE_DAY_CHECK_NOV9 is read (owner card
2026-11-06, `design/RimMandrake/standing_rulings.md`). If that read says no flip, drop this item.

Preconditions: EVIDENCE_SHADOW_FIX_REPORT_NEVER_READS_ZERO and EVIDENCE_GATE_FIX_WORK_SHA_HIDES_CANDIDATE are closed.

Done when:
1. `green()` reads the word the supervisor acted on, recorded in the Marker entry from `relentless_wall.read_as`, with
   tests that a GAP:OTHER WEAK accepts and a GAP:DIFF or untagged WEAK rejects. Corpus rows that read PASS leave the
   false class, named in that commit.
2. `evidence_gate.py report` on a window opening after those fixes shows at least 30 supervisor closes and 0
   gate-accept/record-reject disagreements, and `corpus check` passes.
3. `evidence_gate.ENFORCE = True` lands as one commit that cites that reading, scoped to `--why` exactly
   `relentless: blind check passed`, with tests in `selftest_evidence_gate.py` for a refused close, a hand close left
   alone, and a None row refusing in scope. No key is added to `relentless_rules.json`.

Revert: `git revert <flip sha>`, then `./publish`, on the first `close_refused` whose candidate record holds a green run
and the Marker's PASS.
