## spec
designer_stage.py control_copy_errors checks the exam's control copy for the right leaf set and for no mention of the removed leaf, but never compares the RETAINED leaves with the tree, so a hand edit that reverses one ("Pawns must not climb" -> "Pawns must climb", one word deleted) passes and the control Reader's miss no longer proves the scenarios discriminate. Parent finding 5; attempt-2 review of the parent ran it. roles/designer_exam.md step 5 lets the Designer strip paraphrases of the removed rule by hand, so "retained leaves byte-equal to the generated copy" would forbid that strip, and "deletion only" does not stop a reversal. DECIDED 2026-11-18 (the DESIGN DECISION note on this item): nobody edits the control copy by hand. `exam-control <dir> --leaf <id> --strip "<phrase>"` strips a paraphrase in whole units (sheet line dropped, list entry dropped, any other string value becomes exactly "(removed)"; a phrase found in a retained leaf's id or experience is refused), copy.json records the phrases under "strip", and control_copy_errors regenerates the copy from the current tree plus that list and refuses any difference. The control copies already hand-stripped (Graffiti, GelatinousSlime, Stillsand) are not newly refused: a one-time allowlist of their tree.json and sheet.md content hashes.
Acceptance test: python3 src/RimMandrake/rimflow/acceptance/control_copy_retained_rules_accept.py (23 checks; on b28e0d697, watched: 14 run, 13 red, 1 green, the other 9 run only once `strip` exists). Covers: hand edits of a retained leaf, a sheet line, one word in a sheet line, a non-leaf value, a list entry; a program strip in each unit kind; a strip the record no longer names; refused phrases (retained experience, retained id, empty, blank, not text); a phrase found nowhere.

## refs
file: src/RimMandrake/rimflow/designer_stage.py
file: src/RimMandrake/rimflow/roles/designer_exam.md

## criteria
- The acceptance test passes (23 of 23); designer_exam.md step 5 and its last bullet say the phrase is named to the program and the copy is never edited by hand; control_copy_errors over the 8 real design/concepts/*/exam_control dirs returns the same before and after the build.

## verify
python3 src/RimMandrake/rimflow/acceptance/control_copy_retained_rules_accept.py
