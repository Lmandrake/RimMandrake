# RIMMANDRAKE_DECIDE_COVERAGE_LOOK_BEFORE_EXAM_SIX_EXAMS_RETAKEN

## spec
A decision for the Conductor, from `design/specs/2026-11-15-cheap-guards-at-every-door.md` (section 7). Not a build.
The Designer takes its exam (stage 4) before the coverage judge looks (stage 5); a coverage refusal returns the concept
to stage 3 and the exam is then taken again. Measured from the Designer run records and each stage.json, 2026-11-04 to
11-15: 13 of 16 exam runs passed (Gimme Some Slack failed one, PyrelandsMechanics' control failed twice); 3 of 14
coverage looks signed. Six exam retakes followed a coverage refusal: Gimme Some Slack USD 2.61, 2.54, 5.06; Pyrelands
2.67, 2.80; Graffiti 3.11; USD 18.79 in all.
The question: should the coverage judge look before the exam, with the exam taken once on the tree the judge signs (and
again only if the exam itself changes the tree)? For: the check that usually refuses runs first. Against, unmeasured:
whether the judge's reading leans on an exam-passed tree (`maturation_autonomy.exam_gate` makes the judge skip when the
exam does not pass, which says someone wanted that order), and his card of 2026-11-14 kept both as gates before a lock
without ruling on their order.
If yes: file the build with its acceptance test (the stage machine's order, `exam_gate`, the locked-change chain).
If no: close this with the reason, so it is not found again.

The builder does not edit the acceptance test; a clause believed wrong goes to the Conductor with the evidence.
A guard that cannot run says "did not run" and lets the work through; every refusal carries evidence, would_pass and
smallest_fix (standing_rulings.md, A refusal carries its path to pass).

## refs
file: design/specs/2026-11-15-cheap-guards-at-every-door.md
file: src/RimMandrake/rimflow/maturation_autonomy.py
file: src/RimMandrake/rimflow/designer_stage.py

## verify
none (a decision)

## criteria
- A1: closed with the decision and its reason in the close note.

## acceptance
Acceptance test: none, a stage-order decision; a build that follows from it is filed with its own test.
