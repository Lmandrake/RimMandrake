## Spec
`src/RimMandrake/rimflow/showcase_rules.json` holds two first-guess numbers (max_overlap 0.25, min_new_after_first 3),
status UNMEASURED. Owed by DESIGNER_SHOWCASES_WIDEN_ORTHOGONAL_SET.

## Verify
When the first two concepts under design/concepts/ reach Designer stage 3 (FlowWorks first), run
`python3 src/RimMandrake/rimflow/designer_stage.py showcases design/concepts/<Mod>` on each, judge whether the
numbers refused anything they should not (or passed a showcase that repeats earlier functionality), adjust, and
replace the `status` field with what was measured and why. Waits on concepts: none at stage 3 on 2026-11-05.
