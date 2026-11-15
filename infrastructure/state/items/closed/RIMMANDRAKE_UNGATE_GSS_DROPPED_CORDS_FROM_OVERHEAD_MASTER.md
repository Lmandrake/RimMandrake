## spec
found-by: BENCH detached helper RIMMANDRAKE_CHALLENGE_GSS_BLIND_RESTS_ON_ONE_TEST (blind challenge of Gimme Some Slack 0.1.0, Stages 4 and 5, cycle 1, 2026-11-15). Class Problem, bar shock_reach_setting; settings_switch_cleanly.

Criterion: shock_reach_setting: under Only downed lines and All the live cord a collapsed FlowWorks bridge deck dropped bites (sheet, delegated: 'Only downed lines keeps FlowWorks' dropped bridge-deck cords biting'); settings_switch_cleanly: flipping a feature switch changes just that feature

Evidence:
- RM_FallenWireShock.RebuildContacts returned on !AerialSettings.enabled BEFORE ExternalContacts (the FlowWorks dropped-cord source), and CheckPawns returned on the same switch (source at 67ddc758e5, lines 65 and 148)
- so with the overhead-lines master off, a dropped deck cord neither shocked nor lit fuel, whatever shockReach said: a power-lines switch silencing another mod's floor hazard
- red: selftest_gss_dropped_cords_ignore_aerial_master.py rc 1 on the parent (C1..C4 FAIL); green rc 0 after the fix; planted PF_GAME_DROPPED_CORD_MASTER_GATE (the old gate put back) caught: design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_1/lane2/planted_after_fix.jsonl
- game-side code: no offline test could reach it before; the live proof is the sc_shock_reach scene (Stage 6), UNRUN here

Would pass: with AerialSettings.enabled false and shockReach OnlyDownedLines or All, a pawn on a FlowWorks dropped-cord contact is shocked; our own fallen-span contacts are not

Smallest fix: gate only the aerial-strand loop of RebuildContacts on the master; let ExternalContacts run; in CheckPawns skip only DownedSpan contacts while the master is off

Verdict on the criterion: sound

Status at filing: FIXED 6d2aeb9c3f. Record: `design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_1/lane2/faults.json` (this id).

Acceptance test: `python3 src/RimMandrake/GimmeSomeSlack/selftest_gss_dropped_cords_ignore_aerial_master.py` exits 0 (6 rows). Watched fail (rc 1) on 67ddc758e5.
