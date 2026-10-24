# HOSE_SPLICE_BUILD_MATES_BY_SLOPE

Owner walk 2026-10-23 (walk save e, screenshot Steam 20261023063832_1.jpg), verbatim: "(screenshot) two hoses joined end to
end do not mate, they just lay on top of each other. We need a universal joiner that understands slope/angles to ensure they
come together. I really felt like we already had this in the past... Please use boundary conditions that include the first and
second derivative as well (angle and max hose curvature)". In the screenshot a reel's hose comes down and runs ESE onto the
free end of a second hose that also points east; both open-end wraps sit on top of each other.

## history (what existed)

- No hose-to-hose join solver ever existed in git (searched `-S`/`--grep` for Hermite, clothoid, curvature, splice, joiner,
  end-to-end, MateEnds across FlowWorks, GimmeSomeSlack and _Shared); nothing was removed. What he likely recalls:
  - `8bab86bebd` (2026-10-07, MESSYCONDUIT_CABLE_PILE_LOOK_1 rule 3, his 10-04 words "They CAN look like sealed joiners from
    one cable length to another"): `HoseMath.Layer`/`FootprintOn` only EXEMPT two touching end fittings from the
    fitting-on-another-hose bar. Passive: no geometry moves, so two ends dropped together overlap.
  - Mid-hose rigid joiners (B9/B17, round 4): two couplings meshed at `JoinerMesh`, the hose straightened under them.
  - End aiming at C1 only, no curvature bound: relay `endInward` + `StraightenEnd` (round 7), port `EndOnPort` cubic Hermite
    (`f256450686`), lead-out `HoseMath.Dubins` (G1, radius >= R).
- Max curvature = 1 / `HoseShapeParams.MinBendRadius` (1.2 cells shipped, floor 0.45).

## spec (built)

- `HoseSpliceMath.Join` (Verse-free): a G2 curve, position + heading + curvature matched at BOTH ends, |k| <= kmax everywhere.
  Curvature is piecewise linear in arc length (a chain of clothoid pieces): end knots fixed to the end curvatures, inner knots
  and length solved by Gauss-Newton (minimum-norm steps, active-set clamp). The bound is exact (max |k| is at a knot). A
  sharpness tube (sigma = kmax^2/2, two radii from straight to tightest) holds each end's curvature instead of dropping it at
  once; a fairing pass smooths the winner. Seeds: every Dubins word at 1.15/1.5/2.2 x R. Gentlest wins: added length +
  R x integral(k^2) + 0.5 x displacement area from where the hose lay; a crossing or doubled-back candidate is never taken.
- `HoseSpliceMath.MateTail`: a drawn hose's end re-shaped to arrive at the coupling along the axis, its last
  `CouplingStraight` (JoinerHalf + 0.1) dead straight, joined G2 to the untouched hose at a cut-back of 1.5..8.5 cells.
- `HoseSpliceMath.MatePair`: the coupling axis is SOLVED, not assumed: A's arrival, B's arrival reversed and their bisector
  are tried, each end re-shaped, the least summed cost wins (the screenshot: B keeps its line, A loops round into it; at 90
  degrees both bend part way).
- `RM_MapComponent_Hoses`: two laid OPEN free ends (not on a relay/port, not carried/winding) on the same or 8-adjacent cells
  pair up (A = lower thing id, one partner each). Solved once per layout (key = both layKeys + stiffness + girth); each frame
  re-lands the cached seed (1 solve) and the mesh cache key carries the pair. Drawn as ONE joiner: each hose its half
  (coupling at JoinerMesh + wrap), no open-end wraps. `MateReport()` is the live state read.
- Not changed: flow (two mated hoses are not one hydraulic run; the item asked for the look).
- Cost: full pair search ~15 ms per layout change (selftest S4 bar 25 ms); per frame one re-land on a fill transition.

## criteria

- A1 L0: SelfTest HoseSpliceChecks S1-S5 green (C0/C1/C2 at both ends, |k| <= kmax, no curvature jump, no crossing or
  doubling back, clear of the partner, cached re-solve identical, cost < 25 ms); FlowWorks SelfTest otherwise as before.
- A2 L2: live, two hoses laid end to end (the walk-save-e screenshot case): `RM_MapComponent_Hoses.MateReport()` names the
  pair, and a zoomed capture shows ONE joiner at the coupling, both hoses running straight into it from opposite sides, no
  overlap (judged by a second agent).

## NEXT

Live check owed (A2): deploy the DLL, lay a hose onto another hose's open end, read MateReport and capture the joint.
