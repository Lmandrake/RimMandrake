# ENACT_MISSING_SNAPSHOT_HARDEN_NAMED_REFUSAL

Found in the ENACT_KEYED_FIX_UNREVIEWED review (FOUNDRY, 2026-10-24). Low severity.

## Defect
`build_plan` (around enact.py:994) reads `Path(doc["snapshot"])` without a guard:
- a missing snapshot file raises a raw FileNotFoundError;
- a decisions file with `snapshot` None or "" becomes `Path("")`, resolves to REPO_ROOT, and raises IsADirectoryError.

`ruling_status` propagates both. `enact()` is safe only because `I.ingest` refuses prefill first.
art_sheet.py:2788 wraps `ruling_status` in try/except, which hides the failure as a generic error.
Old and new code crash identically on 3 real files (see DECISIONS_ORPHANS_PRUNE_NO_SNAPSHOT).

## Failing-test sketch
Write a decisions doc with `snapshot: ""`, and a second one naming a non-existent snapshot path.
Expect `build_plan`/`ruling_status` to return a named refusal ("snapshot missing: <path>" / "not a decisions doc"),
not to raise. Also check that `""` never maps to the repo root.

## Evidence
/home/mandrake/.seat-tmp/FOUNDRY/enact_vet4/realdiff.txt (crash list)
