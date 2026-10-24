# HOSE_SHORT_SPAN_DECIDE_NO_CURVE

Found 2026-10-24 by HOSE_CURVE_REBUILD_SMOOTH_AS_PHYSICS step 4, by hand reasoning (not a proof).
Detail: `design/RimMandrake/flowworks_hose_geometry_g2_2026-10-23.md` §6 "Step 4" and §7.
Logs: `D:\ClaudeWork\rimmandrake\scratch\hose_geometry_20261023\h4_14.log`.

The hose stations short (4 rows), tankW (4), and mateA/mateB/splice (12) admit no G2 curve within the bend limit R=1.2.
The 2.2-cell lead-out (an owner card) and the 0.6-cell end straight leave too little free hose.
The Dubins re-route (step 4) and reel pay-out up to 3.2 cells do not help.

Owner decision needed:
- (a) refuse the lay with a reason the player sees;
- (b) shorten the lead-out on short spans, down to 0.6;
- (c) keep today's shaped fallback, which for tankW draws a kink at the flange.

Today's default is (c). `--hose-curves` fails these rows honestly.
