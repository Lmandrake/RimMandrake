# RIMMANDRAKE_RECERTIFY_KNOCKBACK_TREE_AFTER_HIS_OWN_REWORDING

Found 2026-11-15 by the detached helper RIMMANDRAKE_CHALLENGE_KNOCKBACK_BLIND_TWO_FIRST_EXIT_MISSED (reconcile of blind cycle 2).

**Problem.** The owner ruled by card on 2026-11-14 ~9:47 PM PST (OWNER:1794721689897638306, item
RIMMANDRAKE_BUILD_KNOCKBACK_STAGE_THREE_ELEVEN_BARS_UNRUN): *"Throw it, as built; the locked bar's wording changes by his
word from 'slides one cell' to 'thrown a short way', and the test follows"*. The tests followed (scenes.json
sc_closed_containers, sc_settings_sweep, sc_storeroom_bomb_pit; RM_KnockbackProof_StageThree.cs; record.json decision
dc_container_thrown_short_way). The bar's own words in `tree.json` (closed_container_holds, settings_scale_and_switch) and
`sheet.md` did **not** land: ExplosiveKnockback's coverage stamp is his certificate (`signed_by: owner`,
OWNER:1794608649743135329) and is bound to `tree_hash` and `sheet_hash`. With the rewording applied,
`concept_tree.py gate design/concepts/ExplosiveKnockback` goes from `gate: PASS` (at df9c1b6adf) to `REFUSED (1) - the
signature is on another tree hash` [measured]. Certifying is his (delegation_policy.md §2); an agent re-stamping it, or
reading his wording card as a certificate, would forge his pass.

The rewording is held as a patch: `design/concepts/ExplosiveKnockback/version/criterion_repairs/closed_containers_thrown_2026-11-15/tree_sheet_rewording.patch`
(8 edits in tree.json, 2 in sheet.md; `git apply --check` passes on 2026-11-15).

## spec (his choice, by card)
1. Re-certify the reworded tree (one card: "Certify ExplosiveKnockback's tree with the container now thrown a short way?"),
   then an agent applies the patch, re-stamps from his card with `concept_tree.py certify`, runs
   `designer_stage.py repin --source OWNER:1794721689897638306@<commit>`, and re-pins tree/sheet in `version/bars.md`.
2. Or: a Divergent change to the certificate rule (an owner-card change to a locked tree carries his certificate the way
   `designer_stage.py repin` carries stage pins) — filed for the next version, his call.

## verify
Acceptance test: `git apply design/concepts/ExplosiveKnockback/version/criterion_repairs/closed_containers_thrown_2026-11-15/tree_sheet_rewording.patch && python3 src/RimMandrake/rimflow/concept_tree.py gate design/concepts/ExplosiveKnockback | tail -1`
prints `gate: PASS`, and `grep -c "slides one cell" design/concepts/ExplosiveKnockback/tree.json design/concepts/ExplosiveKnockback/sheet.md` reads 0 for both.
Expected: 2 checks pass. Watched on the base 2026-11-15: with the patch applied the gate prints `gate: REFUSED (1)` (the
signature is on another tree hash); without it, the grep reads 1 and 1.
