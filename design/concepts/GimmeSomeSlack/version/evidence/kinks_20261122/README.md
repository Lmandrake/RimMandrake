# Ground-cord kinks at station 3 (his walk of 2026-11-22): the geometry, solved offline first

Item: `RIMMANDRAKE_SMOOTH_SLACK_GROUND_CORD_KINKS_AT_STATION_THREE`. His words (2026-11-22, about 4:10 PM PST, save
GSS_011_VISIT2_WALK_20261121 on ArchBig): *"Station 3 has radical kinks in the swarm of blue cables to the left in this
image. I don't even see why, it didn't have to bend that radically."*

## The measure

A kink is a turn of 50 degrees or more within 0.12 cell of drawn cord: a radius under 0.14 cell, where the loose loops
lie at 0.45 and wider and the faired floor at 0.7 (`kink.py`; in C# `CordShapeAudit.Kinks`). It is excused (`classify.py`;
C# `CordShapeAudit.KinkWhy`) only when it lies under art (a wall, the machine the cord plugs into), inside a cut dead
end's own limp curl (within 1.0 cell of the cut), or within 0.3 cell of a wall, furniture or another machine. Every other
kink is VISIBLE (unforced).

## The cause

Every shaping pass (Fair, Polish, Unbend, and a pile's spline fallback) keeps the run at each end of a cord exactly as
laid (a plug, a strip socket, a pile port, a wall plate) and shapes only the cord between. Where the shaped cord left
that pinned run at an angle, the joint stayed a corner: nothing rounds across the pin's edge. The bend bar
(`CordShapeAudit.Why`) classes any turn within 0.75 cell of a fitting as "socket" (forced) however sharp, so neither the
edge redraws (`LayEdge`) nor the pile redraws ever tried another lay.

At station 3 (the live map dumped by the probe, `worlddump`, and laid offline by the production builder) the visible
kinks were the two pile cables' hooks at the power strips (129 and 114 degrees, 0.16 cell from the socket) and the switch
lead's kink at the wall plate (68 degrees). Over the sweep, every pile-cable kink was on a spline cable, the fallback when
no heap walk fits (259 kinks on 97 spline cables; 0 on 659 walked cables).

## The fix

`CordShape.Unkink`, the last pass on every laid ground strand (edge pieces, dived pieces, pile cables, and the twin shapes
the twin pass may swap in): each kink is replaced by a blend that leaves the cord before it in its own heading and joins
the cord after it in its own heading, no tighter than 0.2 cell (Dubins arc-straight-arc paths first, which can turn a
cable that doubles back off its port, then cubic curves), on the cord's own ground. The pinned end runs and tied loops
never move. And `LayFaults` counts each unforced kink, so a redraw that keeps one loses to one that does not.

## The sweep (the region round station 3)

`gen.py` writes station-3-like worlds: seeds x pile size (3x3, 4x3, 3x4, 4x4) x battery lead (1, 2, 4 cells) x lamp
place x wall on/off x pile look (strips, boxes) x slack scale (0.6, 1.0, 1.6) x cords per edge (1, 2). The SelfTest lays a
folder of them (`selftest_gimmesomeslack.py --lab DIR OUT`, `--no-unkink` for the builder before the fix);
`classify.py OUT DIR` counts the classes.

Measured 2026-11-22 on the final fix (Python classifier, `classify.py`, over the lab output):

| | parent (`--no-unkink`) | fix |
|---|---|---|
| full region, 5,184 worlds: VISIBLE (unforced) kinks | 12,813 | 294: 237 at 50-55 degrees (on the threshold, where the Python and C# measures differ), 36 at 55-70, 12 at 70-90, 9 at 90+ (one geometry, only with 2 cords per run, polish.md) |
| station 3 from the live map's dump (`worlddump`, ArchSmall, 2026-11-22) | 3 (pile hooks 129 and 114 degrees, wall-plate bump 68) | 0 |

The deciding check is the C# one, `Source/SelfTest/KinkChecks.cs` (T_NO_KINK_OFFLINE, `selftest_gimmesomeslack.py --no-export
--kinks-only`; T_CORE runs it on 2 seeds): stations 1-4 of the review map and a 384-world region (6 seeds). Parent: stations
3 + 3 + 3 + 0 unforced kinks, region 722: red. Fix: 0 and 0: green; the region's 2 S-jogs (a 0.04-cell notch where a lamp cord
meets a junction-box arm, on the parent too; polish.md) are reported as jogs (two opposite turns, the cord's way within 35 degrees
either side), never as kinks.

Live, ArchSmall, gimmesomeslack tier (all five DLC), the review map built by `human_review.py --build`, saved as
GSS_KINKS_ST3_BEFORE and reloaded after the fix was deployed: `gss_kinks_st3_before_after.png` (3 kinks to 0, counted by eye on
both captures) and `gss_lamp_before_after.png` (the switch light, green and red, at its old and its halved size).

What the run met on the way, each one a check that went red and was repaired before landing: a blend let into a battery's
unwalkable footprint (gap scene), the slide-under approach moved (CordSlideUnderChecks), stub joins 12.5 degrees off slope when
the stub's kept run was trimmed by two samples (StubJoinChecks, fuzz), a kink that kept the edge redraws going (the slice check's
re-lay Build 16-19 ms to 35 ms), blends that shortened a lead under the slack bar, and pile roundings that became bends (geometry
suite). Final: whole GSS selftest 5,661/5,661, geometry suite 12/12, slice re-lay 21.2 ms (bound 30).
