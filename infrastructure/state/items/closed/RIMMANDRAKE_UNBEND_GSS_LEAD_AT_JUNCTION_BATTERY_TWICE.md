## spec
found-by: BENCH detached helper on RIMMANDRAKE_PROVE_GSS_SWITCHBOARD_DENSE, 2026-11-12, reading the two speed_20261112 GSS proof_all runs
on SteveDesktop (tier gimmesomeslack; evidence `D:\ClaudeWork\rimmandrake\conductor\carryover_20261112\gss\steve\gss_before.json`
and `gss_after.json`, row M2c_no_sharp_bends).

**MOD.** Both runs, same build, report the same single unforced bend (owner's never_taut_straight_cord bar, 2026-11-07: no turn
tighter than 90 degrees within one cell that no wall, building, door or socket forces; CordShapeAudit.Bends):

    piece junction:163,153|battery:153,153  at (156.63, 152.78)  turn 235.62 deg over arc 2.3 cells  sharp 43.27  fromEnd 6.24
    tally: strands 4, bends 6, why {hidden 1, loop 4, unforced 1}

Deterministic (identical coordinates both runs), so it is the planner's route on the core site, not noise. The two ends share z=153, 10 cells apart, and the
bend is 6 cells from an end; what stands near it was not checked. Either the
planner kinks the lead (a MOD fix in CordBuilder/CordPlanner) or CordShapeAudit misnames a broad loop (then the audit is wrong,
and its own LabWorld selftest should carry the case). Decide which from the strand's points.

**Next:** dump the strand's points (`bends` probe rows carry them, or a `rect:` probe on 150,148,16,10), plot, and fix the side
that is wrong.

Acceptance test: live only. `proof_all.py --live --no-shots` on SteveDesktop (testq, tier gimmesomeslack): M2c_no_sharp_bends
PASS with `unforced` 0, and the same site's piece junction:163,153|battery:153,153 absent from `where`. Fails on 4ff9d1df8b
(seen twice, 2026-11-12).
