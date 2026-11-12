# Notes (newest first)

## 2026-11-11 20:35 -08:00 — picked by CLAUDE_ARCHMAGI_OFFLINE1 (setup)
- Runs so far: none (nonpass tail 0). Mode whittle. Offline only: no game.
- Item filed 2026-11-07 by a Relentless worker while building AGENT_IMPROVE_HARDEN_CADENCE_EMPTY_KINDS (causal chain:
  BUILD_GENERALIZATION_CHECK -> HARDEN_NOISE_CALLED_OVERFIT -> TUNE_L2_GATE_SAMPLE_POWER -> HARDEN_GATE_EMPTY_SOURCE_KINDS
  -> HARDEN_CADENCE_EMPTY_KINDS -> this).
- Code: `src/RimMandrake/Utils/agent_improve.py`: `task_kind(p)` (~l.210) reads the intent word of the FIRST parsable item
  id in a piece's `text` (ITEM_TOKEN regex + `model.parse_name`), else None. `source_kinds(row, entry)` (~l.710) = set of
  task_kind over the row's cited pieces minus None. `general_gate` (~l.714) refuses empty kinds, but runs only when
  `LEVELS[pk_level]["need_general"]` (L2). `_prepare_record` (~l.790) writes `source_kinds` into
  `infrastructure/state/agent_improve/changes/<target>_v<N>.json` regardless.
- Also read `gather()` (~l.220): at L1 the recurrence bar wants pieces from 2+ task kinds, counted with the same task_kind,
  so an L1 change already needs kinded pieces in the WINDOW, but the CITED pieces may still be kindless.
- Design: `design/RimMandrake/daily_agent_improvement_2026-11-02.md` §4.3 (l.~120-150) already says a record naming no
  source kinds cannot be checked and is shown `unmeasured`; it does not say whether L0/L1 should be allowed to write one.
  §4.1 table: L1 runs the 4.3 check on every fifth change, L2 on every change.
- Measured at pick (not yet the evidence): both records on file, `rimworld-modding_v1.json` and `using-rimflow_v1.json`,
  have `source_kinds: []` and 1 cited piece each. 2 of 2: tiny sample, and both are L0 changes.
- Where kinds could come from instead (item's own suggestion): the piece's own item (does a piece carry an item/seat
  field besides text? read `collect()`), or the lesson's seat work. Check the piece schema before choosing.
- Selftests: `src/RimMandrake/Utils/selftest_agent_improve.py`, `_cadence.py`, `_general.py`, `_steps.py`.
- Relentless freeze applies: no new rule, layer or judging machinery. Fixing where kinds come from in existing code, or
  writing the by-design decision, is in scope; inventing a new gate is not.
- Blockages from the brief that apply: evidence proportional to the criteria (one measurement + one selftest/doc line).
