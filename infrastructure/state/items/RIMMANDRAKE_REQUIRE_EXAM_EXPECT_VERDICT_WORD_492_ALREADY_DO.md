## spec
Found by the Codex full-file review of `src/RimMandrake/rimflow/designer_stage.py` during
`RIMMANDRAKE_RETAKE_ONLY_TOUCHED_EXAM_SCENARIOS_CARD_ASKED_TWICE` (finding 13, code that build did not touch):
`exam_errors` needs each scenario's `expect` only to be a non-empty string. Ten scenarios with `"expect": "maybe:
unspecified"` and a declared 10/10 pass the gate, though no scenario has a defined right answer. Every one of the 492
scenarios in the twelve exam.json files on disk already starts with `accept` or `reject` (measured 2026-11-18), so the
fix refuses nothing that exists. Smallest fix: refuse an expect whose text before the first `:` is not `accept` or
`reject` (case and spacing aside), naming both words in the error.

## verify
python3 src/RimMandrake/rimflow/selftest_designer_stage.py

## criteria
- exam_errors refuses a scenario whose expect carries no accept/reject verdict word, the error naming both words.
- Every exam.json on disk that passed before still passes.

## acceptance
Acceptance test (1 check), run from the repo root; it reuses the passing-exam fixture of
`src/RimMandrake/rimflow/selftest_exam_partial_retake.py`:

```
python3 - <<'PY'
import shutil, sys, tempfile
sys.path.insert(0, "src/RimMandrake/rimflow")
import designer_stage as DS, concept_tree as CT, selftest_exam_partial_retake as T
root = tempfile.mkdtemp()
try:
    rd, d = T.fixture(root, "X")
    ex = T.read(d, "exam.json")
    ex["scenarios"] = [dict(s, expect="maybe: unspecified") for s in ex["scenarios"]]
    ex["scenarios_hash"] = CT.sha(ex["scenarios"])
    errs = DS.exam_errors(ex, d, T.read(d, "stage.json"), rd)
    ok = any("accept" in e and "reject" in e for e in errs)
    print("PASS" if ok else "FAIL", errs[:2]); sys.exit(0 if ok else 1)
finally:
    shutil.rmtree(root, ignore_errors=True)
PY
```

Watched FAILING before filing (2026-11-18, on the build's tree: `FAIL []`, exit 1). Expected: 1 pass after the fix,
and `selftest_designer_stage.py` stays green.
