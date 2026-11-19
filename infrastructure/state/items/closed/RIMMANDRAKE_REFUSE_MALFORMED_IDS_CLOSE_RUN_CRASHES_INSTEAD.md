## spec
Codex full-file review of designer_stage.py (2026-11-18, round 4, finding 3): a malformed identifier crashes close_run instead of producing a rejection. At stage 3, a scene with `"requirement": [{"id": "L1"}]` reaches `scene_errors`, where membership in the leaf set raises TypeError (a dict is unhashable); a waiting-owner ask with `"about": [{}]` crashes at `inv.get(a)` in `ask_errors`. Both raise before close_run clears and writes `running`, so the run stays open and a later open_run charges its reservation as a retry.
Fix: validate requirement, feature and about entries as string identifiers before any dict or set use; a non-string is a validation error in the rejection.

## verify
Acceptance test: drafted, NOT yet watched failing: two cases in `src/RimMandrake/rimflow/selftest_designer_stage.py`, each closing a run whose result carries one of the shapes above, expecting `close_run` to return (False, [an error naming the bad id shape]) with `running` cleared; expected 2 new checks PASS after the fix.

## criteria
close_run never raises on a result.json shape; every malformed id is a rejection reason.

## refs
file: src/RimMandrake/rimflow/designer_stage.py
