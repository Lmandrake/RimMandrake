## spec
`evidence_gate._record_for` picks the wrong record when the supervisor closes at the work sha under a bookkeeping
candidate, so the shadow rejects good closes. Measured 2026-11-06 against `/home/mandrake/rm/relentless/store`:

- RELENTLESS_VET_FULL_FILE_BEFORE_CLEAN closed at 88360b38. That sha's own record holds an old red run, and it is taken
  first. The candidate 0a0e109a holds a green run and the Marker's PASS. Reported: run not green, no marker.
- RELENTLESS_CORE_FIX_CODEX_FOUND_SEVEN closed at e8c7158e. The candidate 0a387e4e holds a green run and a PASS, but
  `_same_work` says no: the only overlap between the paths that differ and the paths this item's commits touched is
  `src/RimMandrake/rimflow/relentless.py`. Reported: no record. A work commit in a busy file can therefore never read green.

The reading stays above 0 until this is fixed, and under enforce each case would cost an attempt (`close_refused`).

Keep the protection `_same_work` exists for: A broken, B fixed and passed, closing at A is not B's pass. Do not widen a
cohort to make these two disappear.

Done when: `selftest_evidence_gate.py` holds both cases built from these shapes and they accept, the A-broken-B-fixed
case still rejects, and `evidence_gate.py corpus check` passes.
