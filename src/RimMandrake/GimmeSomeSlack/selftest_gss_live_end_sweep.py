#!/usr/bin/env python3
# selftest-timeout: 300
"""RIMMANDRAKE_INVENT_SLACK_LIVE_END_GREEN_BY_THIN_MARGIN: the live cut end's mathematics, swept offline, as a permanent check.

The Python original of Core/CordLiveEnd.cs and CordMotion.Whip (src/RimMandrake/Utils/mockups/messy_conduit/live_end_lay.py) is swept
over the abstract input space, so the live end cannot slide back into constant tuning without this going red:

  whip        the bend-wave whip never bends a dead straight cord under twice the pinch bar, at either end of the whip bar, over
              30 seeds x 20 s; and the instrument can fail: the old sideways whip folds a 0.7 tail under the bar
  shot        a fitting on the conduit's own line: from 0.85 cells behind the end a bare cord holds every bar and the whole pigtail
              whips; nearer, the cord lies still (the owner, 2026-11-16: "a2, and where it does not apply then c")
  poses       a fitting anywhere from 2 to 4 cells round the conduit end, facing any way, on open floor: a bare join holds every bar
              with margin for every pose; no tied loop is used
  can fail    a hooked cord (a 0.05-radius corner behind the run) is refused by the margin bars and repaired by the lay

The game's own cords are swept by the C# suite (SelfTest/LiveEndSweepChecks.cs, in selftest_gimmesomeslack.py). Exit 0 PASS, 1 FAIL.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils", "mockups", "messy_conduit"))
import live_end_lay as Y  # noqa: E402
import live_end_lib as L  # noqa: E402
import live_end_sweep as S  # noqa: E402

fails = 0
checks = 0


def check(ok, msg):
    global fails, checks
    checks += 1
    if not ok:
        fails += 1
    print(("PASS " if ok else "FAIL ") + msg)


def straight(tail):
    n = int(round((tail + 0.5) / 0.05))
    return [(i * 0.05, 0.0) for i in range(n + 1)], int(round(tail / 0.05)) + 1


def main():
    # ---- whip
    new = {}
    old = {}
    for tail in (0.7, 0.95):
        P, cnt = straight(tail)
        seeds = [(s * 2654435761 + 17) & L.M64 for s in range(30)]
        new[tail] = min(Y.live_read_bend(P, cnt, seed=s, frames=600)[0] for s in seeds)
        old[tail] = min(L.live_read(P, cnt, seed=s, frames=600)[0] for s in seeds)
    check(min(new.values()) >= Y.LIVE_BEND_R, "whip: the bend wave never bends a straight cord under %.2f (tail 0.7: %.3f, tail 0.95: %.3f; 30 seeds x 20 s)"
          % (Y.LIVE_BEND_R, new[0.7], new[0.95]))
    check(old[0.7] < L.MIN_BEND_R, "whip can fail: the old sideways whip folds a straight 0.7 tail to %.3f, under the bar's %.2f (0.95: %.3f)"
          % (old[0.7], L.MIN_BEND_R, old[0.95]))

    # ---- the straight shot
    res = S.shots(quiet=True)
    still = [a for a, bare, knife, full in res if full == "still"]
    whips = [a for a, bare, knife, full in res if full == "kept"]
    other = [(a, full) for a, bare, knife, full in res if full not in ("still", "kept")]
    check(not other and max(still) < 0.85 <= min(whips), "shot: a fitting under 0.85 behind the end lies still, from 0.85 the whole pigtail whips on a bare cord "
          "(still up to %.2f, whipping from %.2f, other outcomes %s)" % (max(still), min(whips), other))

    # ---- poses on open floor
    kinds = {}
    bad = []
    worst = 99.0
    n = 0
    for dist in (2.0, 2.5, 3.0, 4.0):
        for bearing in range(0, 360, 30):
            for phi in range(0, 360, 45):
                b, h = math.radians(bearing), math.radians(phi)
                F = (dist * math.cos(b), dist * math.sin(b))
                # the handed cord: the fitting's stiff bit, then a straight chord to the conduit end at the origin (the conduit runs +x)
                P = [(F[0] + math.cos(h) * 0.05 * k, F[1] + math.sin(h) * 0.05 * k) for k in range(4)]
                a = P[-1]
                m = max(2, int(math.hypot(*a) / 0.05))
                P += [(a[0] * (1 - k / m), a[1] * (1 - k / m)) for k in range(1, m + 1)]
                g = Y.lay_live_end(P, (0, 0), (1, 0))
                k = g["kind"].split()[0]
                kinds[k] = kinds.get(k, 0) + 1
                badl, r = S.judge(g["pts"], (0, 0), (1, 0), g["cnt"])
                n += 1
                if g["cnt"]:
                    worst = min(worst, r["minr"])
                if badl or k not in ("kept", "join"):
                    bad.append((dist, bearing, phi, g["kind"], badl))
    check(not bad and worst >= 1.5 * L.MIN_BEND_R, "poses: %d fitting poses 2-4 cells round the end, every one a bare cord holding the three bars (%s); tightest bend %.3f; refused %s"
          % (n, kinds, worst, bad[:3]))
    check(kinds.get("turn", 0) == 0, "poses: the tied loop is used on none of them (%d)" % kinds.get("turn", 0))

    # ---- can fail: a hook behind the run
    r = 0.05
    P = [(-2.0 + 0.05 * k, -0.9) for k in range(24)]
    P += [(-0.85 + r * math.sin(t), -0.9 + r - r * math.cos(t)) for t in (math.pi / 8 * k for k in range(1, 5))]
    P += [(-0.8, -0.85 + 0.05 * k) for k in range(1, 17)]
    P += [(-0.8 + r - r * math.cos(t), -0.05 + r * math.sin(t)) for t in (math.pi / 8 * k for k in range(1, 5))]
    P += [(-0.75 + 0.05 * k, 0.0) for k in range(1, 16)]
    P2, cnt = Y.set_joint(P)
    before = Y.bars_with_margin(P2, (0, 0), (1, 0), cnt)
    g = Y.lay_live_end(P, (0, 0), (1, 0))
    after, rr = S.judge(g["pts"], (0, 0), (1, 0), g["cnt"])
    check("P" in before and g["kind"].startswith("join") and after == "" and rr["minr"] >= Y.LIVE_BEND_R * 0.98,
          "can fail: a hooked cord (0.05 corners) is refused (%s) and laid again (%s, tightest bend %.3f)" % (before, g["kind"], rr["minr"]))

    print("%d/%d live end sweep checks pass" % (checks - fails, checks))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
