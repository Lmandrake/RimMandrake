# line_joins_redraw — BENCH helper progress (2026-10-21)
Items: PIPE_GIRTH_TUNE_HALF_AS_THICK, HOSE_GIRTH_TUNE_MUCH_THINNER (claimed), LINE_JOINS_JUDGE_GPT_SEES_FIRST (close when consumed)
## Wave 1 — no-art fixes
- [x] sprinkler drawOffset (0,0,0.31) on RM_SprinklerHead + 4 ThingStyleDefs (Defs/Sprinklers/RM_Sprinklers.xml)
- [x] HoseMath FlatVisible 0.38->0.09, PlumpExtra 0.085->0.025 (0.09 flat / 0.115 plump); thickness slider 0.5-1 -> 0.75-2 (default 1 = thin);
      LiquidJoinRule.ProposedHoseThickness (0.65) deleted; selftests HoseSelfTest.Widths + LiquidJoin_hose_thickness_scale re-pinned. SelfTest exe: hose 347/347, LiquidJoin 4/4 ok;
      14 unrelated FAILs are staged-build path misses (e.g. ClimbingGear_JawaFactions.xml not under D:\ClaudeWork build root) — not from this change.
- [x] pipe girth: it is the ATLAS TEXTURE (40 px of 176), no code/XML number -> art candidates, wave 2. Pipe centre-stubs sample the atlas, so they follow.
## Wave 2 — candidates
## Wave 3 — review sheet line_joins_redraw
## Live check owed
## Shas
