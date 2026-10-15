# PIT_REACH_VERIFY_FLYERS_AND_GIANTS

FlowWorks: pawnless reach uses person band (flyers, K3+), too-wide pawns walled in

Source: FlowWorks pre-release GPT consult, BENCH 2026-10-15 — `Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md` (full rows) and the `answer_<slice>.md` named by each finding id.

## findings

- **C3-F4** PLAUSIBLE HIGH — Pawnless reachability uses the person band with no flyer exemption: flyers and K3+ pawns may be refused valid routes. RelativeVeto (Superdeep/RM_SuperdeepTrap.cs: 'int k = p == null ? PersonBand') and the CanFly exemption needs p != null; vanilla StartPath runs a pawnless CanReach (the fixed ladder bug). Live: flyer ordered from surface onto a ladderless D4 floor; K3 animal up a sheer D3 step; read PatherFailed / job result.
- **C3-F5** PLAUSIBLE MEDIUM — A pawn too wide for its hole reads 'not held' but the cliff masks still wall it in. IsHeldAtRelative honours WideAt; RM_CliffMask bands select by K only (Superdeep/RM_CliffMask.cs). Live: force a K2 width-2 pawn into a 1-cell D4 hole, read IsHeld + a path to the surface.

## criteria

- Each CONFIRMED finding: a SelfTest/python case (or a live state read where the row says so) that goes red on today's code, then green with the fix.
- Each PLAUSIBLE finding: run the check written in its row first; close it as not-a-bug with the evidence if it stays green.
