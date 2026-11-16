# RIMMANDRAKE_SEE_GSS_DLL_HOSE_NAMES_HIDDEN_IN_TAILS

## spec
found-by: BENCH detached helper RIMMANDRAKE_JUDGE_GIMMESOMESLACK_BLIND_CYCLE_SIX_TESTS_FIRST (blind challenge of Gimme Some Slack 0.1.0, Stages 4 and 5, cycle 6, judge-1794822790, 2026-11-16, code c991553a4f). Class Polish, bar no_hose.
Criterion: T_NO_HOSE sees every hose-named member the shipped DLL carries
Evidence:
- lane1/lane1_rows.jsonl K_DLL_NO_HOSE_TYPES FAIL: the shipped DLL's metadata holds LayParams::Hose, CordKind.Hose and the DrawOrder hose altitudes, compiled from _Shared/SlackGeometry (CordLayer.cs:75, :87; DrawOrder.cs)
- T_NO_HOSE's assembly scan reads raw ASCII runs; 'Hose' is stored as the tail of 'LayerHose' in the #Strings heap, so LayParams.Hose and CordKind.Hose never appear as their own run and the scan stays green (its docstring names only the DrawOrder table)
- lane2/planted_results.jsonl P09_CORDS_LAID_WITH_HOSE_PRESET: GSS's CordBuilder laying its cords with LayParams.Hose() stays green under T_NO_HOSE (LANE1 S_CS_NO_HOSE_REEL_IDENTIFIER catches it)
- today no GSS source names a Hose identifier (lane 1 S_CS_NO_HOSE_REEL_IDENTIFIER PASS, 102556 tokens) and the cords draw cord art: no hose is drawn
Would pass: python3 design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_6/lane2/acceptance_polish.py hose_preset exits 0
Smallest fix: selftest_gss_no_hose.py scan(): for Source/**/*.cs outside SelfTest, strip comments and strings and hit any identifier matching HOSE_PART ('identifier: <name>'); name LayParams.Hose and CordKind.Hose in the docstring as shared code GSS never calls
Verdict on the criterion: criterion sound; the instrument is blind to tail-shared names and to identifiers, but nothing hose-shaped is used by GSS today; Polish

## verify
Acceptance test: `python3 design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_6/lane2/acceptance_polish.py hose_preset` exits 0 (1 check).
Watched fail on c991553a4f: rc 1 (T_NO_HOSE stays green with the plant). It restores the planted file byte for byte; `git diff --quiet -- src/RimMandrake/GimmeSomeSlack` after.
