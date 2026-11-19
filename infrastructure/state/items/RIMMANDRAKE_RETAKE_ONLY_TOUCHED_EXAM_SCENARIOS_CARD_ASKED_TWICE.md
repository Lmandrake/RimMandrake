## spec
The owner's ruling on the order of the Designer exam and the coverage judge, by card 2026-11-18 4:29 PM PST
(ledger note on `RIMMANDRAKE_REORDER_COVERAGE_BEFORE_EXAM_SIX_RETAKES_PAID`, tsn 1795048533407382294), picked
option **Retake only what changed**, its description verbatim:

> Why: remove the waste without moving the gates. Keeps exam first; after a judge refusal, only the exam scenarios the
> repair touched are re-run. Buys most of the saving at a small build. Costs: needs a reliable map from a repair to the
> scenarios it touches. Recommended as the smallest change.

The same question was put to him again on a card at 7:05 PM PST the same day. His answer (2026-11-18, about 7:15 PM
PST): *"Actually I have ruled on this multiple times. I'm not sure why you keep losing the ruling. ... Please look back
at those rulings I already gave you, and the evidence they were based on, and come to a consensus recommendation. Then
implement it now and don't return to me with this item, ok?"*

**The Conductor's ruling, made on that word (final; this question does not go back to him):**
1. The order stays: the Designer exam (stage 4, Cold Reader) runs first, the coverage judge looks after it.
2. After a coverage-judge refusal is repaired, only the exam scenarios the repair touched are re-run. The other
   scenarios keep their earlier answers.
3. When the map from a repair to the scenarios it touches cannot tell (a file with no mapping, an unreadable map, a
   change to something every scenario reads, such as the bars sheet), the whole exam is retaken. A partial retake is
   never guessed.

**The evidence the ruling rests on.**
- Measured 2026-11-04 to 2026-11-15 from the Designer run records and each `stage.json`: 13 of 16 exam runs passed;
  3 of 14 coverage looks signed; six exam retakes followed a coverage refusal.
- Measured on origin/main c6f9f55a7e (lane verdict note of 2026-11-18T21:21:23Z on the superseded item): the coverage
  judge depends on an exam-passed tree. `coverage_judge.py` tells the judge to read `exam.json` and lists it as refusal
  evidence; it hashes `exam.json` into the delta plan; `designer_lock.md` defines the lock's frozen files as "those
  stage 3 wrote and stage 4 examined"; `coverage_judge.py` and `maturation_autonomy.exam_gate` skip the look on a
  failing exam on purpose. So "judge first" is a rebuild of the stage machine and a judge-prompt edit that binds only
  after recalibration, where "retake only what changed" moves no gate.
- His earlier cards: 2026-11-14 kept both the exam and the coverage judge as gates before a lock; 2026-11-17 chose one
  whole-mod check in place of both for a CLEANSED design. This build changes neither: it only narrows what a retake
  re-runs wherever the exam and the coverage judge both run.

**What to build.**
- A map from a changed design file (or changed section) to the exam scenarios that read it, built from what each
  scenario actually read when it was answered (recorded at exam time), never from a hand-kept list.
- The retake after a coverage repair: re-run the scenarios the map names, carry the other answers forward, and record
  in `exam.json` which answers are carried and from which exam, so a reader can tell a carried answer from a fresh one.
- The four outcomes stay distinct: retaken, carried forward, whole exam retaken because the map could not tell, and
  the retake could not run.

## the map (DESIGN DECISION 2026-11-18, the Conductor's delegate; it binds the builder like the acceptance section)
The map's unit is the LEAF, not the file. Every Reader is handed the whole `tree.json` and `sheet.md`
(roles/designer_exam.md step 4), so a file-level read record would say every repair touches every scenario. Where the
text above says "file", read "leaf".
- **Recorded at exam time:** `exam.json` gains `reads`: `{scenario id: [leaf ids its Readers said they relied on]}`,
  written when the exam is scored (step 4 already asks each Reader for "the leaf it relied on"). A scenario's
  `expect_source` leaf always counts as read too.
- **A leaf is touched** when `concept_tree.leaf_hash` differs between the tree the exam was taken on and the repaired
  tree, or a `sheet.md` line tagged `[leaf:<id>]` was added, removed or changed.
- **A scenario is retaken** when it read a touched leaf, or its own text is new or changed. Every other answer is
  carried, marked with the exam it came from.
- **The whole exam is retaken, never a guess,** when: a leaf was added or removed; tree content outside `leaves`
  (and outside `coverage`) changed; a sheet line with no leaf tag changed; `reads` is missing, lacks a scenario or
  names a leaf the exam's tree lacks; a tree, sheet or exam cannot be read; the exam was taken on another tree.
  Every exam that exists today has no `reads`, so its first retake is whole; partial retakes start with the next exam.
- **Not inputs:** files a Reader never sees (`scenes.json`, `record.json`, the floor). A repair to those alone is
  "looked, none touched".
- **The control run** is carried when its broken leaf is untouched and none of its `missed_ids` is retaken; otherwise
  it is made again with `exam-control` and re-run.
- One pure function carries all of it: `designer_stage.exam_retake_plan(old_tree, new_tree, old_sheet, new_sheet,
  exam, scenarios=None)` -> `{"mode": "none"|"partial"|"whole", "retake", "carry", "touched_leaves", "why"}`.
Measured over the git history of eight concepts' `tree.json` (2026-11-18): 30 of 45 tree edits changed leaves only,
with a median of 8% of the leaves changed; 13 added or removed a leaf; 2 changed tree content outside the leaves.

Acceptance test for the map: `python3 src/RimMandrake/rimflow/acceptance/exam_retake_map_accept.py` (33 checks; on
b4c47bd15 in a throwaway `git clone --shared`, watched: 32 red, 1 green). It stands beside `selftest_exam_partial_retake.py`
(A1 to A6 through the stage machine), which the building run still writes first.

## refs
file: src/RimMandrake/rimflow/designer_stage.py
file: src/RimMandrake/rimflow/maturation_autonomy.py
file: src/RimMandrake/rimflow/coverage_judge.py

## verify
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_designer_stage selftest_maturation_autonomy selftest_exam_partial_retake
python3 src/RimMandrake/rimflow/acceptance/exam_retake_map_accept.py

## criteria
- A1: a repair that touches files read by 2 of 10 scenarios re-runs exactly those 2; the other 8 answers are carried
  forward and marked as carried, with the exam they came from.
- A2: a repair that touches a file no scenario's read record covers, or a file every scenario reads, retakes the whole
  exam.
- A3: a missing or unreadable map retakes the whole exam and says why; it is never read as "nothing touched".
- A4: a repair that touches nothing a scenario read re-runs zero scenarios, and that result is recorded as "looked,
  none touched", distinct from A3.
- A5: a carried answer whose scenario text itself changed is not carried: that scenario is re-run.
- A6: the order of the gates is unchanged: the coverage judge still does not look at a tree whose exam has not passed.

## acceptance
Acceptance test: a new selftest `selftest_exam_partial_retake.py` driving the retake through A1 to A6 with fixed stage
dicts and fixed read records (no model call), registered in the pipeline test table. It is watched FAILING on the base
commit before the build (A1, A4 and A5 fail by construction: today a retake re-runs every scenario), with the failing
output quoted in the commit message. Expected: 6 cases, 6 pass after the build. Not yet watched failing at filing: the
selftest does not exist; the building run writes it first and records the red run.

The builder does not edit this acceptance section; a clause believed wrong goes to the Conductor with the evidence.
