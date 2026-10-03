# NORTHSTAR_PHASE_LADDER_1 — the standard rung sequence every north-star mod follows

DRAFT -> VALIDATED -> WIRED -> GREEN (minimal list) -> GREEN (full list) -> SHIPPED. One ledger item per rung,
per mod, named `<MOD>_NORTHSTAR_<RUNG>_1`.

1. DRAFT — walk has a `## north star` section (state: DRAFT).
2. VALIDATED — the owner's word, recorded with `modcheck/cli.py validate <Mod> --owner-said "..."`
   (hash-bound; prose corrected later means re-validate in the same sitting).
3. WIRED — every must-show/cannot-show bar has a component claiming it via `shows=` in validation.py
   (`modcheck floor <Mod>` shows no uncovered/orphan ids). MEASURED 2026-10-03: 3 of 110 validation.py files carry `shows=`.
4. GREEN minimal list — `northstar_driver` run on the minimal mod list + the mod: preflight OK, every
   expected bar PASS (UNMEASURED is not green). Results JSON in Transient/northstar/.
5. GREEN full list — same on the full canonical list (all five DLCs; see CLAUDE.md).
6. SHIPPED — deployed (deployed copy == repo), Mod Settings screen complete, art complete, code-review CLEAN
   for every file (`code_review_status.py check`).

Rules: a rung is closed only against evidence (results JSON path / commit), never against a prose claim; a
rung that regresses reopens as a finding, not a silent edit. Driver: NORTHSTAR_FAST_DRIVER_1.
