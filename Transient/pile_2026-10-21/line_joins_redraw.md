# line_joins_redraw — BENCH helper progress (2026-10-21)
Items: PIPE_GIRTH_TUNE_HALF_AS_THICK, HOSE_GIRTH_TUNE_MUCH_THINNER (claimed), LINE_JOINS_JUDGE_GPT_SEES_FIRST (close when consumed)
## Wave 1 — no-art fixes
- [x] sprinkler drawOffset (0,0,0.31) on RM_SprinklerHead + 4 ThingStyleDefs (Defs/Sprinklers/RM_Sprinklers.xml)
- [x] HoseMath FlatVisible 0.38->0.09, PlumpExtra 0.085->0.025 (0.09 flat / 0.115 plump); thickness slider 0.5-1 -> 0.75-2 (default 1 = thin);
      LiquidJoinRule.ProposedHoseThickness (0.65) deleted; selftests HoseSelfTest.Widths + LiquidJoin_hose_thickness_scale re-pinned. SelfTest exe: hose 347/347, LiquidJoin 4/4 ok;
      14 unrelated FAILs are staged-build path misses (e.g. ClimbingGear_JawaFactions.xml not under D:\ClaudeWork build root) — not from this change.
- [x] pipe girth: it is the ATLAS TEXTURE (40 px of 176), no code/XML number -> art candidates, wave 2. Pipe centre-stubs sample the atlas, so they follow.
## Wave 1b — pipe girth (a NUMBER after all: art_source/pipe/build_pipe_atlas.py W_PIPE)
- [x] W_PIPE 40->18 px (0.30 -> 0.136 of the 132-px displayed cell; the review's "0.23" used the 176 tile, not the 132 shown), HUB 72->36.
      Rebuilt + installed all 4 looks' atlas + menu icon via the builder's --install (art ledger). check_pipe_atlas: 0 failures x4.
      Caps keep the old dome shape, scaled down with the bore (flat plates = redraw candidate).
- [x] damageData rect (0,0.35,1,0.3) -> (0,0.43,1,0.14) in RM_UniversalPipeStyles.xml (4) + RM_LiquidLogistics.xml
- [x] pole span RM_PipePoleMath.SpanWidthCells 0.22 -> 0.14 + RM_PipePoles.xml spanWidth; PipePoleChecks can-fail re-pinned 0.12-0.15
- selftest_hose_port.py P2 FAIL is pre-existing (GSS AerialSettings.cs string), not this change.
## Wave 2 — candidates
## Wave 3 — review sheet line_joins_redraw
## Live check owed
## Shas
