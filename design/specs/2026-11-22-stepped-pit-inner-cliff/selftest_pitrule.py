#!/usr/bin/env python3
"""Offline promises of the stepped-pit rule (pitrule.py), RIMMANDRAKE_REDRAW_STEPPED_PIT_INNER_CLIFF_STOPS_SHORT_OF_THE_RIM.

Each promise is checked on the new rule (must PASS) and on a twin of today's draw (model/pitdraw.py's sizes: a face sized by
the drop, a lip line from edge to edge; must FAIL where today is wrong), so the test is seen red for the reason he gave.

  P1 RISER_STOPS_AT_SIDE_WALL   an inner riser's lip line and face start at the side wall's line at the riser's top depth,
                                never at the ground rim, wherever the side wall beside it is shallower than the riser's top
  P2 SIDE_WALL_WIDER_WHEN_DEEPER a side wall shows wider beside a deeper floor, at every pair of depths (0.5 .. 20 m)
  P3 FACES_ADD_UP               down any column, the north faces add up to H(deepest): the inner riser is the part of the wall
                                between its two floors, never a second full-height wall
  P4 EVERY_DEPTH_APART          H, W and the depth value K strictly change over the whole dig range (no cap that makes two
                                depths alike, today's stop at 2.5 m)
  P5 SINGLE_DEPTH_SIDES_KEPT    a single-depth pit of 2.5 m or less keeps today's side strips exactly, and its north face is
                                today's at NORTH_SCALE (0.7: his L's 4 m north arm read as a lip, 2026-11-22)
  P6 LOCAL_3X3                  a square's plan reads only its 3x3 (changing a square two away changes nothing)
  P7 NORTH_SHELF_IN_VIEW        a one-square shelf along a north wall keeps at least 0.4 of a square of floor in view at
                                every depth to 8 m (his words, 2026-11-22: "the lower-right northern inner shelf is incredibly
                                narrow, that's a bit weird and incorrect"; it showed 0.26 at 4 m)

    python3 selftest_pitrule.py          exit 0 when every promise holds on the new rule and P1..P4 fail on today's twin
"""
import itertools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pitrule as R  # noqa: E402

DEPTHS = [0.5 * i for i in range(1, 41)]
TODAY_N = [0.0, 0.12, 0.23, 0.35, 0.50, 0.62]
TODAY_S = [0.0, 0.06, 0.11, 0.17, 0.23, 0.29]


def today_face(t, drop):
    return R._table(t, drop) if drop > 0 else 0.0


class Today:
    """Today's draw sizes (pitdraw.plan_cell): faces by the DROP to the neighbour, lip line full width."""
    @staticmethod
    def plan(grid, r, c):
        d = R._at(grid, r, c)
        n, w = R._at(grid, r - 1, c), R._at(grid, r, c - 1)
        return {"t": today_face(TODAY_N, d - n) if n < d else 0.0,
                "l": today_face(TODAY_S, d - w) if w < d else 0.0,
                "lip_n": (0.0, 1.0) if n < d else None}

    H = staticmethod(lambda z: today_face(TODAY_N, z))
    W = staticmethod(lambda z: today_face(TODAY_S, z))
    K = staticmethod(lambda z: 1.0 if z <= 0 else (0.61 if z <= 2 else 0.42 if z <= 4 else 0.35))


class New:
    plan = staticmethod(R.plan_cell)
    H, W, K = staticmethod(R.H), staticmethod(R.W), staticmethod(R.K)


def p1(M):
    """Pit two columns wide inside ground: the riser square at column 0 has ground (0) to its west."""
    for a, b in itertools.combinations([1, 2, 4, 6, 8, 12], 2):
        grid = [[a, a], [b, b]]
        p = M.plan(grid, 1, 0)
        if p["lip_n"] is None or p["lip_n"][0] < M.W(a) - 1e-9 or M.W(a) <= 0:
            return False, f"{a} m over {b} m: lip starts at {p['lip_n'] and round(p['lip_n'][0], 3)}, side wall line at {a} m is {round(M.W(a), 3)}"
    return True, "every riser starts at the side wall's line at its top depth"


def p2(M):
    for a, b in zip(DEPTHS, DEPTHS[1:]):
        if not M.W(b) > M.W(a):
            return False, f"W({b}) = {M.W(b):.3f} not wider than W({a}) = {M.W(a):.3f}"
    return True, "side wall wider at every deeper floor"


def p3(M):
    for col in ([2, 6], [1, 3, 6], [4, 8], [2, 4, 8, 16]):
        grid = [[z] for z in col]
        total = sum(M.plan(grid, r, 0)["t"] for r in range(len(col)))
        if abs(total - M.H(col[-1])) > 1e-6:
            return False, f"column {col}: faces add to {total:.3f}, H({col[-1]}) = {M.H(col[-1]):.3f}"
    return True, "faces down every column add up to H(deepest)"


def p4(M):
    for f, name in ((M.H, "H"), (M.W, "W"), (M.K, "K")):
        for a, b in zip(DEPTHS, DEPTHS[1:]):
            if f(a) == f(b):
                return False, f"{name}({a}) == {name}({b}) = {f(a):.3f}"
    return True, "H, W and K change at every half metre to 20 m"


def p5(M):
    scale = getattr(R, "NORTH_SCALE", 1.0)
    for z in DEPTHS:
        if z > 2.5:
            break
        if abs(M.H(z) - scale * today_face(TODAY_N, z)) > 1e-9 or abs(M.W(z) - today_face(TODAY_S, z)) > 1e-9:
            return False, f"{z} m differs from today's side strip or scaled north face"
    return True, "single-depth pits to 2.5 m keep today's side strips and today's north face at NORTH_SCALE"


def p7(M):
    for z in DEPTHS:
        if z > 8.0:
            break
        if 1.0 - M.H(z) < 0.4:
            return False, f"a 1-square north shelf at {z} m shows {1.0 - M.H(z):.2f} of a square"
    return True, "a 1-square north shelf keeps 0.4 of a square in view to 8 m"


def p6(M):
    import random
    rnd = random.Random(7)
    for _ in range(300):
        grid = [[rnd.choice([0, 1, 2, 4, 8]) for _ in range(5)] for _ in range(5)]
        base = M.plan(grid, 2, 2)
        g2 = [row[:] for row in grid]
        rr, cc = rnd.choice([(0, rnd.randrange(5)), (4, rnd.randrange(5)), (rnd.randrange(5), 0), (rnd.randrange(5), 4)])
        g2[rr][cc] = rnd.choice([0, 1, 2, 4, 8, 16])
        if M.plan(g2, 2, 2) != base:
            return False, f"changing ({rr},{cc}) changed square (2,2)"
    return True, "plans read only the 3x3"


PROMISES = [("P1 RISER_STOPS_AT_SIDE_WALL", p1, True), ("P2 SIDE_WALL_WIDER_WHEN_DEEPER", p2, True),
            ("P3 FACES_ADD_UP", p3, True), ("P4 EVERY_DEPTH_APART", p4, True),
            ("P5 SINGLE_DEPTH_SIDES_KEPT", p5, False), ("P6 LOCAL_3X3", p6, False),
            ("P7 NORTH_SHELF_IN_VIEW", p7, False)]


def main():
    ok = True
    for name, f, today_must_fail in PROMISES:
        good, why = f(New)
        print(f"{'PASS' if good else 'FAIL'}  new    {name}: {why}")
        ok &= good
        if today_must_fail:
            tg, twhy = f(Today)
            print(f"{'RED ' if not tg else 'GREEN?'}  today  {name}: {twhy}")
            ok &= not tg
    print("ALL PROMISES HOLD; today's twin is red on P1-P4" if ok else "SELFTEST FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
