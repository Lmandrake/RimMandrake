## spec
found-by: BENCH detached helper RIMMANDRAKE_CHALLENGE_GSS_BLIND_RESTS_ON_ONE_TEST (blind challenge of Gimme Some Slack 0.1.0, Stages 4 and 5, cycle 1, 2026-11-15). Class Problem, bar no_hose_in_gss (and inventory no_hose).

Criterion: oracle: offline scan finds no ThingDef, texture or class for hoses or reels under src/RimMandrake/GimmeSomeSlack; false pass named by the leaf: 'the scan matching only def names, missing a texture folder'

Evidence:
- T_NO_HOSE is the only decider of both proves_at 4-5 bars (test_table.json bars no_hose, no_hose_in_gss: decides [T_NO_HOSE])
- planted PF_HOSE_TEXTURE_FOLDER (Textures/Things/Hose/Segment_south.png) and PF_HOSE_COMP_CLASS_ATTR (<li Class="CompProperties_HoseReel" />) both left T_NO_HOSE green: design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_1/lane2/planted_results.jsonl
- the scanner matched texture FILE names only and element text only, never a folder or a Class attribute
- today's tree ships no hose either way: the widened scan reads T1 green (reruns_after_fix.jsonl T_NO_HOSE PASS)

Would pass: T_NO_HOSE goes red by name on a hose texture inside a Hose/ folder and on a comp or worker named only by its Class attribute, and stays green on the shipped tree

Smallest fix: scan the texture path under Textures/ (not just the file name) and every Class attribute in Defs/ and Patches/; add the two as mutants M5, M6

Verdict on the criterion: sound: the leaf itself names the texture-folder false pass

Status at filing: FIXED 6d2aeb9c3f. Record: `design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_1/lane2/faults.json` (this id).

Acceptance test: `python3 src/RimMandrake/GimmeSomeSlack/northstar/selftest_gss_no_hose.py` exits 0 with M5 and M6 PASS. Watched fail (rc 1) against the parent's scanner.
