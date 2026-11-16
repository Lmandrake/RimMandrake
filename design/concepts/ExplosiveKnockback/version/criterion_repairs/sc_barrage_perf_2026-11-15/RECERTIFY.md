# Re-certify ExplosiveKnockback's tree with the barrage bar read as the p99 frame in the window

Item `RIMMANDRAKE_RECERTIFY_KNOCKBACK_TREE_BARRAGE_P99_HELD_AGAIN`, filed 2026-11-15 by the fixer of
`RIMMANDRAKE_REPAIR_BARRAGE_FRAME_CRITERION_BASELINE_FAILS_TOO`.

He agreed on 2026-11-15 (OWNER:1794799770273329641, *"1 agree."*) that `barrage_frame_budget` reads the 99th-percentile
frame inside the 0.9-8.25 s barrage-and-chain window at most 50 ms. The scene, decider, record and plan follow it
(`9c8c37aced`, re-pinned `6dbf3b7021`). The leaf's and the sheet's own words are held in `tree_sheet_rewording.patch`
(this folder): his coverage certificate is bound to the tree and sheet hashes, and at the time only an event of his on
the concept's item (`RIMMANDRAKE_DESIGN_KNOCKBACK_FIRST_TOUCH`) could re-sign it; his answer is on the repair item.

Done 2026-11-15 8:35 PM PST, with no card (the Conductor's evidence-for-ask call): `concept_tree.py certify` now takes his
words on an item caused by the concept's item or by one of its refusal records (this folder's `refusal.json` names
`RIMMANDRAKE_ROUTE_EXPLOSIVEKNOCKBACK_VISIT_TWO_FAILURES`, which caused the repair item), the "fix the rule" half of his
card OWNER:1794748823561950419. The patch is applied at `3aa7e5c15d` (the leaf's experience reordered to lead with "at
most 50 ms", the constraint shape lint asks; the patch as held failed lint), the tree re-certified on
OWNER:1794799770273329641 at `fab7999d8f`, and `designer_stage.py repin` re-pinned stages 2, 3 and 5; stage 4's exam
is void by repin's rule and is retaken under `RIMMANDRAKE_RETAKE_KNOCKBACK_EXAM_NO_SCENARIO_READS_LEAF`.

Acceptance test: `python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_barrage_p99.py | grep -c "PASS T1 .*(today's tree)"`
prints 1 (and the run ends ALL PASS), and `python3 src/RimMandrake/rimflow/designer_stage.py status design/concepts/ExplosiveKnockback`
shows coverage passed on the new OWNER event. Watched failing at `6dbf3b7021`: T1 reads "(held patch applied)", count 0.
