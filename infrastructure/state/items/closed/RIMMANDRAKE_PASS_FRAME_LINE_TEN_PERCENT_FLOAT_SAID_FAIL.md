## spec
ExplosiveKnockback `validation.py` `_Walk.frame_row` judged FRAME_BUDGET (bar walk_storeroom_raid) with
`over = on / off - 1.0`. For a mod-on p99 exactly 10% over mod-off (110 ms against 100 ms) that reads
0.10000000000000009, so the row FAILed while printing "+10.0% over mod off ... PASS at most +10%". His card
(2026-11-16, "Compare to mod-off") says "Pass if mod-on is within 10% of the same colony's mod-off run": the line
passes. 9a437178d8's offline selftest enshrined the float artefact as case FB_AT_BUDGET_LINE_10PCT expecting FAIL.
Found by the Codex review of 9a437178d8 in RIMMANDRAKE_VERIFY_REMOTE_LANDINGS_FOUR_SKIPPED_THE_DOOR, reproduced here.
Fix: the excess is taken as `(on - off) / off`, exact at the line; the case expects PASS. The bar, FRAME_OVER_OFF
and the line the planted mutant PF_V_FRAME_ROW_ALWAYS_PASS rewrites are unchanged.

## verify
python3 src/RimMandrake/ExplosiveKnockback/validation.py --selftest     # exits 0, "PASS (8 case(s), 0 failed)"
Watched failing at a907fc6756 with the corrected case: rc 1, "FB_AT_BUDGET_LINE_10PCT want PASS got FAIL".
Both planted mutants (design/concepts/ExplosiveKnockback/version/blind_challenge/cycle_5/lane2/planted_faults.json,
PF_V_FRAME_OVER_LOOSE and PF_V_FRAME_ROW_ALWAYS_PASS) still turn it red (rc 1 each), and
selftest_explosiveknockback_walk_raid.py stays GREEN (W25 +3.6% PASS, W26 +10.1% FAIL). Expected: 1 pass.

## criteria
- A mod-on p99 exactly 10% over the mod-off arm reads PASS; +11% still FAILs; both named mutants still killed.
