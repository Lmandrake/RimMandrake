# Re-certify ExplosiveKnockback's tree with the barrage bar read as the p99 frame in the window

Item `RIMMANDRAKE_RECERTIFY_KNOCKBACK_TREE_BARRAGE_P99_HELD_AGAIN`, filed 2026-11-15 by the fixer of
`RIMMANDRAKE_REPAIR_BARRAGE_FRAME_CRITERION_BASELINE_FAILS_TOO`.

He agreed on 2026-11-15 (OWNER:1794799770273329641, *"1 agree."*) that `barrage_frame_budget` reads the 99th-percentile
frame inside the 0.9-8.25 s barrage-and-chain window at most 50 ms. The scene, decider, record and plan follow it
(`9c8c37aced`, re-pinned `6dbf3b7021`). The leaf's and the sheet's own words are held in `tree_sheet_rewording.patch`
(this folder): his coverage certificate is bound to the tree and sheet hashes, and only an event of his on the
concept's item (`RIMMANDRAKE_DESIGN_KNOCKBACK_FIRST_TOUCH`) can re-sign it. His answer is on the repair item instead.

1. The Conductor asks one card on `RIMMANDRAKE_DESIGN_KNOCKBACK_FIRST_TOUCH`: "Do you certify ExplosiveKnockback's tree
   with the barrage bar now read as the 99th-percentile frame in the barrage window, at most 50 ms?"
2. On yes: `git apply` the patch, commit, `concept_tree.py certify design/concepts/ExplosiveKnockback --owner-event
   OWNER:<tsn>`, `designer_stage.py repin ... --source OWNER:<tsn>@<commit>`, re-pin tree/sheet in `version/bars.md`.
   The second half of his earlier card ("fix the rule", a card change carrying his certificate) would make this card
   unnecessary; it is filed for the next version.

Acceptance test: `python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_barrage_p99.py | grep -c "PASS T1 .*(today's tree)"`
prints 1 (and the run ends ALL PASS), and `python3 src/RimMandrake/rimflow/designer_stage.py status design/concepts/ExplosiveKnockback`
shows coverage passed on the new OWNER event. Watched failing at `6dbf3b7021`: T1 reads "(held patch applied)", count 0.
