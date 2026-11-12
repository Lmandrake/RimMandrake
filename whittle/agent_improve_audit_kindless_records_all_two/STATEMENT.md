# AGENT_IMPROVE_AUDIT_KINDLESS_RECORDS_ALL_TWO — done statement

Item: changes applied below L2 can record no source kinds, so the generalization check (design 4.3) can never read them.
Criteria copied from `infrastructure/state/items/AGENT_IMPROVE_AUDIT_KINDLESS_RECORDS_ALL_TWO.md`; no new scope.

- **A change applied below L2 either records source kinds, or the decision to let it stay uncheckable is written in
  design 4.3 with its reason.** Evidence: either (a) `src/RimMandrake/Utils/agent_improve.py` `apply_change` at L0/L1
  writes a change record whose `source_kinds` is non-empty for a change whose cited pieces name no item (kinds taken from
  a ruled other source), shown by a selftest in `selftest_agent_improve*.py` that fails on the old code and passes on the
  new; or (b) a dated paragraph in `design/RimMandrake/daily_agent_improvement_2026-11-02.md` §4.3 stating that L0/L1
  changes with no source kinds stay uncheckable by design, and why. Whichever is chosen, the doc and code agree.
- **The share of change records with no source kinds is measured from `infrastructure/state/agent_improve/changes/` and
  stated.** Evidence: a measurement (command and its output saved in `whittle/agent_improve_audit_kindless_records_all_two/evidence/`)
  of how many records on file have `source_kinds == []` out of how many, with a sanity probe showing the reader can see a
  non-empty list, stated on the item (note or close reason) and, if (b), in §4.3.
