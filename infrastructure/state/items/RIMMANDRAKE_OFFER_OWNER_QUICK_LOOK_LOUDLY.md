## spec
Owner fix E, his words: "If we can insert an owner quick-look to settle a difficult or several questions swiftly,
offer that loudly." He added that the Designer often runs on mods not yet written, so this applies when the mod has
enough working code that a staged scene could settle the hard questions.

Into roles/designer.md verbatim; enforced where a program can: a waiting_owner result (or a return to stage 2) on a
concept whose inventory has code present must carry a quick_look field (offer with what it settles and the scene, or
offer false with why not); the park summary puts the offer at the top.

Authority: owner ruling OWNER tsn=1794527688430451936 and card tsn=1794527885746395760 on RIMMANDRAKE_BIND_REFUSALS_TO_FIXES_NO_CEREMONY_LOOPS; Conductor brief 2026-11-12 (CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM). Already landed before this: 5e1fb090e736 (third-refusal stop), 40fde3bc437f (refusal_contract.py). Context: EK overnight loop, design/concepts/ExplosiveKnockback/stage.json; spec design/specs/2026-11-12-refusal-contract-for-judges-and-gates.md.

## Built (2026-11-12)
`designer_stage.quick_look_errors`, called by `result_errors` on a `waiting_owner` result and on a `return` that
proposes a `question`, when `code_present(record)` (an inventory entry with `impl: present`): refuses a missing or
malformed `quick_look`, an offer settling nothing or naming no scene, and a decline with no why. The loud half (QUICK
LOOK OFFERED on his queue line and park page) landed with B+C at e3c6fa76427b. His rule verbatim in
`roles/designer.md` (which also carries B's "Away, you park" bullet). Test: `selftest_designer_quick_look.py` (18 ok,
3 mutants caught: check disabled, return branch and waiting_owner branch unwired).
