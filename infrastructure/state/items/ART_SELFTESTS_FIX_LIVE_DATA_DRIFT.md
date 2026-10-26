# ART_SELFTESTS_FIX_LIVE_DATA_DRIFT

Review wave 94 ran all 79 art selftests (`run_selftests.py --only src/RimMandrake/Utils/art/selftest_*.py`, 2026-10-26).
Two FAIL on live repo/queue data, not on their fixtures. Evidence: `w94/st_placeholder_detect.txt` and
`w94/st_texture_gap_lint.txt` in the FOUNDRY session scratchpad. Both reproduce with a plain `python3 <selftest>`.

The two CRASHes the same run found (selftest_enact_ws, selftest_enact_apply_whole_pick: fixtures lacked plan["decisions"]
after ea640a7247) are fixed in review w94, commit "selftest_enact_ws and selftest_enact_apply_whole_pick had CRASHED".

## spec
1. `src/RimMandrake/Utils/art/selftest_placeholder_detect.py`, check "150 real artpipe renders all classify REAL":
   `D:\ClaudeWork\rimmandrake\artpipe\_artsrc\kit_callingpyre_icon_v1\kit_callingpyre_icon_v1.png` does not classify REAL.
   Decide: the render really is placeholder-like (then the sample must exclude it, or the render is bad art to file),
   or placeholder_detect misreads an icon (then fix the detector with a test).
2. `src/RimMandrake/Utils/art/selftest_texture_gap_lint.py`, check "the real repo: every gap is listed and no entry is stale":
   `TEXTURE GAP: RimMandrake/FlowWorks/PipePole/{look}/PipeSpan (MISSING; src/RimMandrake/FlowWorks/Defs/Machinery/RM_PipePoles.xml)`.
   `{look}` is a template, not a texPath, and PipeSpan.png was installed 2026-10-22 (D5). So the lint likely reads a
   templated path from that def file as a literal one. Fix the lint to skip/expand templates, with a test; or list
   the entry. FlowWorks is BENCH's, so the def file itself is not to be edited from FOUNDRY.
