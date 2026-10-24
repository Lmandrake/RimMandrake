# FLIER_LINE_CHECK_FIX_SIDEWAYS_UNSEEN

Source: /mnt/d/ClaudeWork/rimmandrake/scratch/gpt_flier/gpt_answer.md section A3 (D:\ClaudeWork\rimmandrake\scratch\gpt_flier\gpt_answer.md), GPT opinion 2026-10-20. The P0 findings from that review were already fixed (commit 02931e44f4: templateMask ECC, UNMEASURED on estimator failure, coverage). This is the P1 remainder, verified in src/RimMandrake/Utils/art/flier_body_stabilize.py `line_check`: verdict gates only `dy_px` (midpoint vertical) and `ddeg`.

## spec
GPT quotes:
- "P1: The line test misses horizontal drift and expansion. line_check gates midpoint vertical movement and angle change. It does not gate: horizontal movement, endpoint displacement, line length, distance between head and shoulder anchors. Both eyes can slide horizontally together and pass. They can move apart along a horizontal line and pass. Keep the owner's overlays, but gate each endpoint in two dimensions, and report line length and head-to-root distances."
- "P1: Several 'anatomical' points are constructed proxies (east: eye plus a snout point on the eye's row; north: head edges substituted for hidden eyes; multi-wing creatures: first two hinges used) ... their meaning must be explicit ... A north-facing head-reference line is legitimate; calling it an eye measurement is not."

Build: in line_check gate each endpoint's (dx, dy) against the reference with LINE_TOL_PX, report line length change and eye-to-shoulder distance change; label proxy points in the output `label` field honestly. Owner overlays stay.

## verify
- Selftest: synthetic frames with both eye points shifted +3 px horizontally -> MOVING (today LEVEL); points moved apart along the line -> MOVING; identical frames -> LEVEL.
- Existing six rebuilt sets still read LEVEL or are re-reported with the reason.
- Run: python3 src/RimMandrake/Utils/run_selftests.py --only <flier stabilizer test>.
