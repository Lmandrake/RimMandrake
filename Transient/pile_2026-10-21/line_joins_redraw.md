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
- artpipe find: no prior render at the new girth (old reel 'smaller_fairlead' jobs 2026-10-17 predate the thin hose); 0 sprinkler/tap/pipe hits.
- 18 jobs filed (fill_queue, list Transient/pile_2026-10-21/line_joins_redraw/artlist.json, ids *_lj_*): reel PumpHookup+Deployed x4 looks,
  sprinkler head x4 (riser foot at texture centre), tank x4 (neck+coupling on the pipe axis E/W), pump x1, tap x1 (pump/tap have one look).
- NOT made: pipe->hose metal reducer (needs RM_MapComponent_Hoses.DrawPortStub C# + new texture) — owed; flat pipe cap plates (need new raw/<look>_fittings.png) — owed.
## Wave 3 — review sheet line_joins_redraw
- art.py backfill artpipe first (lj2 + Modern PumpHookup were not in the ledger). art_sheet --subjects RM_HoseReel RM_SprinklerHead RM_LiquidTank
  RM_LiquidPump RM_LiquidTap --jobs <17 lj ids> --hide-sets <older families> --name line_joins_redraw: only new candidates + IN GAME show.
- scaled_review_gate PASS; game_art deliver OK; sheet_freshness verify exit 0; serve_gated -> http://localhost:34515/?t=hs9DuZkq2Pkss4x6GkvTDg (200)
- Native folder: \\wsl.localhost\Ubuntu\home\mandrake\rm\bench\Transient\biome_ffar\ (line_joins_redraw sheet, 2026-10-21)
- Candidate caveats: reels drew 2.1-2.4 cells wide (asked 1.6-1.8), still side-on; sprinkler feet sit ~20-35 px below centre (install sets
  drawOffset to match the pick); Industrial sprinkler v2 came out tiny (hidden); tap still side-on. RM_SprinklerHead_lj2_Scrapper still rendering.
## Install notes (when he picks)
- sprinkler: drawOffset (0,0,0.31) is for TODAY's art; a picked head needs drawOffset z = (foot_y_px - 128)/256 for its own foot.
- reel: re-run src/RimMandrake/Utils/mockups/messy_conduit/reel_intake_geometry.py (ReelIntakeGeometry.cs is generated from the art); shrink shadowData.
## Live check owed (live helper; nothing deployed by me)
- deploy FlowWorks (DLL + Defs + 4 pipe atlases/icons), then at 1 cell = 80-100 px: pipe run, bends, T/4-way, caps (4 looks) beside a conduit and
  a colonist; hose flat AND plump coupled to a pipe end, a pump and a tank; reel hose; sprinkler on a MID-run pipe cell (foot on the axis?);
  a pipe-pole span (0.14) beside a ground pipe; Mod Settings hose-thickness slider 0.75-2x.
## Shas
- a88b56db48 (hose + sprinkler offset) · 8d5b94b0e1 (pipe half girth) · 0c54100dfa (progress)
- 22:13 6/18 renders done (reels x4, Scrapper tank, Scrapper sprinkler), 0 failed; waiting on the daemon (5 at a time).
- 22:22 11/18 done
- 22:26 14/18 done; Scrapper PumpHookup timed out (worker 124) -> requeue_flakes
- 22:32 17/18; sprinkler v1 feet sit at y~175-200 not 128 and Modern is 24x35 px -> 4 sprinkler v2 jobs (*_lj2_*) with exact layout
