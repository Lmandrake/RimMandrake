## spec
WP-09c (RIMFLOW_DELETE_CLOSE_GUARDS_ONE_PER_LANDING) deletes four old close guards "each after its predicate shows 0
disagreements". Read literally today, that would remove protection, even with a perfect reading:

1. **Nothing enforces.** `evidence_gate.py` is shadow only: `shadow()` "never refuses", and the module has no enforce
   mode. Deleting a guard leaves that check undone, not done by the record. A flip to enforce has to land first, and no
   work package in redesign_final.md section 5 names it.
2. **The predicate is silent outside the store.** `judge()` returns None for an item the Relentless store does not hold.
   `_close_gate` and `model._fold_close_gate` also protect hand closes and closes from a clone behind the gate. On the
   ledger since 13:47Z, 2 of 145 closes never reached the shadow (sanity: 143 did, against the log's 148 by item+sha).
3. **It does not check what `_close_gate` checks.**
   - `close_refusals`: owed criteria, a level-tagged pass on this sha, a newest failing run, `guard_owed`.
   - `_sha_refusals`, `_guard_refusals`, `marker_lock`, the fold gate.
   - `NOT_JUDGED = {"guard"}` says so for guards. Redesign section 3.4 also keeps the lease fence, literal sha,
     `unlanded_owed`, provenance flags, diagnose/warrant and close_audit.
   - Agreement cannot show equivalence: the gate refused 3 of 148 closes, and the predicate rejected those for its own
     reasons (no marker, no run), not the gate's.
4. **Two named guards have no predicate at all.**
   - `src/RimMandrake/rimflow/live_proof_lint.py` (the item's `Utils/live_proof_lint.py` does not exist) and its hook
     `.claude/hooks/warn_close_live_proof_owed.py` warn about debt named only in a commit message. The predicate never
     reads a commit message, so no shadow reading says anything about them. The item says only "the .claude/settings.json
     hook"; that this is the one meant is my inference, and this design must name it.
   - `relentless_wall.py` GAP parsing narrows a GAP:OTHER WEAK to PASS. The predicate treats every WEAK as not closing,
     so deleting the narrowing changes behaviour: every GAP:OTHER WEAK then holds. That is a decision, not a cleanup.

Done when: a design note under `design/RimMandrake/` gives, for each of the four guards and each `_close_gate` check,
what replaces it (a named evidence-record entry and test, or "kept"), which reading licenses its deletion, and the order,
with the enforce flip first and its revert named. RIMFLOW_DELETE_CLOSE_GUARDS_ONE_PER_LANDING's spec is corrected to
match. Depends on EVIDENCE_SHADOW_FIX_REPORT_NEVER_READS_ZERO for the reading.
