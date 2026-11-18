## spec
`maturation_autonomy._route` writes the locked-change chain brief with "retake the Cold Reader exam on the new tree ...
in full" whatever the change touched. Graffiti 2026-11-18T17:58:16Z: the change moved only scenes.json (6c7d175b52; the
re-pin re-pinned stages 3 and 4 for scenes), tree e6507f3b and sheet 26a15750 were unchanged and `exam_errors` read []
(the 2026-11-17 exam, 122/122, passes its gate). The exam's Readers see only sheet.md, tree.json and the scenario text, so a
retake would have re-asked identical inputs (run one of this chain spent 1,254,186 weighted tokens, Opus, on its retake
and look). Fix: the chain reads the exam gate (`exam_gate`, the same one coverage_judge.plan reads); when it passes at a
known tree hash the brief says the exam stands at that tree and orders no retake; a failing or unreadable gate keeps the
full-retake text.
## criteria
- A chain whose exam passes its gate at a known tree hash orders no retake and names the tree.
- A failing gate, or a gate with no tree hash, keeps the full-retake brief.
## verify
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_maturation_autonomy.py` prints ALL PASS; on the base
(f2de22337d) it printed 1 FAIL ("exam gate: a chain whose exam still passes its gate ... keeps it, no retake").
## refs
file: src/RimMandrake/rimflow/maturation_autonomy.py
file: src/RimMandrake/rimflow/selftest_maturation_autonomy.py
