#!/usr/bin/env python3
# selftest-timeout: 300
"""RIMMANDRAKE_INVENT_SLACK_LIVE_END_GREEN_BY_THIN_MARGIN: the live cut end's mathematics, swept offline, as a permanent check.

The Python original of Core/CordLiveEnd.cs and CordMotion.Whip (src/RimMandrake/Utils/mockups/messy_conduit/live_end_lay.py) is swept
over the abstract input space, so the live end cannot slide back into constant tuning without this going red:

  whip        the bend-wave whip never bends a dead straight cord under twice the pinch bar, at either end of the whip bar, over
              30 seeds x 20 s; and the instrument can fail: the old sideways whip folds a 0.7 tail under the bar
  shot        a fitting on the conduit's own line: from 0.85 cells behind the end a bare cord holds every bar and the whole pigtail
              whips; nearer, the cord lies still (the owner, 2026-11-16: "a2, and where it does not apply then c")
  poses       a fitting anywhere from 0.3 to 2.5 cells round the conduit end, facing any way (13,248 poses): the lay alone lays every
              one with a bare cord; with the fitting's own body there, it fails only where that body crowds the end's run
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

#: where the lay may fail: a box-like fitting's middle this near the cut end's run (measured 0.749; the C# suite holds the grid's nearest,
#: 0.835, above LiveEndSweepChecks.BoxSepMin 0.80), a machine's footprint this near (measured 0.219)
BOX_CROWD, MACHINE_CROWD = 0.75, 0.22

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

    # ---- every fitting pose round a conduit end: distance 0.3 to 2.5 cells x bearing x heading, 15 degrees apart (13,248 poses), the handed
    # cord a taut chord from the fitting's stiff bit. RIMMANDRAKE_LAY_SLACK_CLOSE_FITTINGS_TWENTY_ONE_UNLAID: 21 of 288 such poses once found
    # no lay, by three rules of the lay's own (a second length cap, "never across its own run", a join's heading at a corner vertex)
    jobs = max(1, (os.cpu_count() or 2) - 2)
    free = S.poses(None, jobs, body="none", quiet=True)
    kinds = {}
    for r in free:
        kinds[r["kind"].split()[0]] = kinds.get(r["kind"].split()[0], 0) + 1
    unlaid = [r for r in free if r["bad"] or r["kind"].split()[0] not in ("kept", "join")]
    worst = min(r["minr"] for r in free)
    check(not unlaid and worst >= 1.5 * L.MIN_BEND_R, "poses: %d fitting poses 0.3-2.5 cells round the end (the lay alone, no fitting body): every one a bare cord holding the three "
          "bars (%s); tightest bend %.3f; unlaid %s" % (len(free), kinds, worst, [(r["dist"], r["bearing"], r["phi"], r["kind"], r["bad"]) for r in unlaid[:3]]))
    check(kinds.get("turn", 0) == 0, "poses: the tied loop is used on none of them (%d)" % kinds.get("turn", 0))

    # ---- the same poses with the fitting's own body there (a join never comes back over the fitting it left): the lay fails only where that
    # body crowds the end's own run. The C# suite proves the grid puts no fitting there (LiveEndSweepChecks: BoxSepMin 0.80, no machine on a run)
    box = S.poses(None, jobs, body="box", quiet=True)
    bu = [r for r in box if r["bad"] or r["kind"].split()[0] == "none"]
    far = max([r["near"] for r in bu], default=0.0)
    check(far <= BOX_CROWD, "poses, the fitting a box, plate or strip: %d of %d unlaid, every one with the fitting's middle within %.3f cell of the end's run "
          "(limit %.2f; the grid's nearest is 0.835)" % (len(bu), len(box), far, BOX_CROWD))
    mach = S.poses(None, jobs, body="machine", quiet=True)
    mu = [r for r in mach if r["bad"] or r["kind"].split()[0] == "none"]
    farm = max([r["near"] for r in mu], default=0.0)
    on = sum(1 for r in mu if r["on_run"])
    check(farm <= MACHINE_CROWD, "poses, the fitting a machine's plug: %d of %d unlaid, %d with the machine's footprint ON the end's run, the rest within %.3f cell of it "
          "(limit %.2f)" % (len(mu), len(mach), on, farm, MACHINE_CROWD))

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
