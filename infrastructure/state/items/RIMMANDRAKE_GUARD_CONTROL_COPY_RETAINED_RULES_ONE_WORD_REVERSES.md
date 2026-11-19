## spec
designer_stage.py control_copy_errors checks the exam's control copy for the right leaf set and for no mention of the removed leaf, but never compares the RETAINED leaves with the tree, so a hand edit that reverses one ("Pawns must not climb" -> "Pawns must climb", one word deleted) passes and the control Reader's miss no longer proves the scenarios discriminate. Parent finding 5; attempt-2 review of the parent ran it. roles/designer_exam.md step 5 lets the Designer strip paraphrases of the removed rule by hand, so "retained leaves byte-equal to the generated copy" would forbid that strip, and "deletion only" does not stop a reversal. Open design question: what may a hand strip change in a retained leaf (nothing, with paraphrases stripped only in sheet.md; whole sentences replaced by "(removed)" each named in copy.json; or an independent reviewer approving each edit)?
Acceptance test: python3 src/RimMandrake/rimflow/acceptance/control_copy_retained_rules_accept.py (1 case red on 25d20f71e0 and on 8992cdc87e, watched; the generated copy passes). Pins only what any answer must hold.

## refs
file: src/RimMandrake/rimflow/designer_stage.py
file: src/RimMandrake/rimflow/roles/designer_exam.md

## criteria
- The acceptance test passes; the designer_exam.md step 5 text says what a hand strip may change.

## verify
python3 src/RimMandrake/rimflow/acceptance/control_copy_retained_rules_accept.py
