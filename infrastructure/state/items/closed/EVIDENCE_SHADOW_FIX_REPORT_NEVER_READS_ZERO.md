## spec
RIMFLOW_DELETE_CLOSE_GUARDS_ONE_PER_LANDING (WP-09c) may delete a guard only on a shadow reading of >=30 closes and 0
disagreements. `evidence_gate.py report` cannot give that reading, whatever happens from now on.

Measured 2026-11-06 about 21:45Z against `/home/mandrake/rm/relentless/store/evidence_shadow.jsonl`:

- `report`: 148 closes, 71 agree, 76 DISAGREE, 1 pre-record. `summary()` reads the whole log and has no window. The log
  began 13:47Z, and most rows before 18:00Z predate the working Marker writer (EVIDENCE_SHADOW_FIX_REJECTS_EVERY_CLOSE,
  8e3e8ef4a5 harvest). Those rows hold the count above 0 for good. Since 18:00Z: 68 closes, 5 disagree.
- `rescore --snapshot` on a copy of the store's state.json files, evidence/ and the log: exit 1, 158 rows, 11 unexplained.
- Of the 5 since 18:00Z:
  - 3 at 21:12Z are OWNER no-code or no-box closes of items the store holds as retired (WATER_SCENES_S5_JUDGE_THIRD_DRAFT,
    ALBINO_SWIM_NORTH_FIX_SHOWS_THE_FACE, ARTEVAL_JUDGE_LIVE_HEAD_TO_HEAD). `report` counts them as disagreements, and
    `rescore` files them under the `verdict_gone` cohort, though no verdict ever existed. The row does not record who
    closed. `RELENTLESS_WHY` exists but `shadow()` does not use it.
  - 1 is `run not green: newest box run is unrunnable` (OPS_CHURN_DIAGNOSE_RELENTLESS_BBZJ_VGUX@d908be8cbf): the gate
    accepted on the Marker's word, the predicate refused. Nobody has ruled which is right.
  - 1 is the pre_record cohort (DEPLOY_GUARD_FIX_EXCLUDE_DIR_MISMATCH).
- The 10 other unexplained rescore rows are `no run` closes, 9 of them RELENTLESS_* items, not yet classified.

Do not make the number smaller by widening a cohort until it passes. Each exclusion must name a true reason that a test
pins.

Done when:
1. `report` can state a declared window (rows at or after a named writer fix, or a named sha), and says plainly which
   rows it left out and why.
2. A row records whether the close was a Relentless close. An owner-authority close is out of the predicate's scope and
   is reported as its own line, neither agreement nor disagreement, and is no longer `verdict_gone` in `rescore`.
3. The unrunnable-run case is decided and pinned by a test, with its reason in the module doc.
4. The 10 unexplained rescore rows are each classified, or the reading keeps saying they are not.
5. selftest_evidence_gate covers all of this, and the corpus check still passes.
