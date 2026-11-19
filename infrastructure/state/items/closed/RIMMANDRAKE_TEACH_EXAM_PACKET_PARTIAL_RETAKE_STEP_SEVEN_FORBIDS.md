## spec
Caused by `RIMMANDRAKE_RETAKE_ONLY_TOUCHED_EXAM_SCENARIOS_CARD_ASKED_TWICE` (his card 2026-11-18 4:29 PM PST, "Retake
only what changed"). That build added `src/RimMandrake/rimflow/exam_retake.py` (record / plan / carry), records the
read map at every stage-4 close, makes `designer_stage.exam_errors` re-check every carried answer, and names the plan in
the two steward briefs (`maturation_autonomy.RETAKE_STEP`). Its brief forbade an edit to the exam prompt (a judge-prompt
edit binds only after recalibration), so the Designer's stage-4 packet `src/RimMandrake/rimflow/roles/designer_exam.md`
was not edited. Consequence: the main path (stage 5 refusal -> stage 3 repair -> stage 4 Designer run) still follows the
packet, which says nothing of the plan, and step 7 says "Never re-score the same scenarios against an edited tree
without refreezing", which a carry could be read to break. So a Designer-run retake still re-runs every scenario.

What is owed: a decision that this packet is not a calibrated judge prompt (no calibration record names it: grep of
`calibrat` in roles/designer*.md finds none for designer_exam.md, measured 2026-11-18), then a short "Retake after a
coverage repair" step: run `exam_retake.py plan <dir>`; PARTIAL re-runs only the named scenarios through two fresh
Readers plus a control Reader on a fresh exam-control copy, then `exam_retake.py carry <dir> --fresh <file>` (the fresh
file holds readers, reader_verdicts with a leaf per answer, inputs {tree, sheet}, scenarios_hash, control,
accept_where_reject_core); NONE_TOUCHED stands; CANNOT_RUN fixes the input and re-plans; WHOLE is steps 1-6 in full.
Step 4 should also require `reader_verdicts` keyed by each Reader's agent id with a leaf per answer (without it no map
is recorded and every later retake is whole). Step 7 amended to allow a carry.

## verify
grep -q "exam_retake.py plan" src/RimMandrake/rimflow/roles/designer_exam.md && grep -q "exam_retake.py carry" src/RimMandrake/rimflow/roles/designer_exam.md

## criteria
- The stage-4 packet tells the Designer to run the plan before a retake and to carry what it carries.
- Step 7 no longer forbids a carry made by exam_retake.py.
- Step 4 asks for reader_verdicts keyed by agent id with a leaf per answer.

## acceptance
Acceptance test: the `## verify` line. Watched failing on the build's tree before filing (exit 1: the packet names
neither command). Expected: exit 0 after the edit. It proves only that the packet names the commands; the first real
Designer-run partial retake is the live test, UNRUN until a mod's coverage look refuses.
