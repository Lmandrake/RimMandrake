#!/usr/bin/env python3
"""The live cut end swept over every cord the game hands the lay (RIMMANDRAKE_INVENT_SLACK_LIVE_END_GREEN_BY_THIN_MARGIN).

    python3 live_end_sweep.py replay CENSUS.jsonl OUT.jsonl [--jobs N] [--every K]
        Lays every "raw" cord of a census (selftest_gimmesomeslack.py --live-census: the cord as the builder hands it to the live-end lay,
        with the ground beside it) with live_end_lay.lay_live_end, reads the three bars with their own instruments, and writes one row a
        cord: what the lay did (kept / join / turn loop / service loop / none), every bar, and for each device whether a bare cord could
        have held (the emergency-only check).
    python3 live_end_sweep.py table OUT.jsonl
        The map: every region of the family, how it is closed.
    python3 live_end_sweep.py shots [--out DIR]
        The straight shot (a fitting right behind the conduit end) at every length: where a bare cord holds, where only a device does,
        where nothing does.
"""
import collections
import json
import math
import multiprocessing
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import live_end_lay as Y  # noqa: E402
import live_end_lib as L  # noqa: E402

SEEDS = (17, (2654435761 + 17) & L.M64, (5 * 2654435761 + 17) & L.M64)


def judge(P, pos, out, cnt, seeds=SEEDS, frames=90):
    """The three bars on a laid cord, by their own instruments (the pinch bar with the bend-wave whip) -> (bad letters, dict)."""
    b = L.read_bars(P, out, pos, cnt=cnt, frames=1)
    bad = "".join(ch for ch in b["bad"] if ch in "ST")
    minr = 99.0
    if cnt > 0:
        for s in seeds:
            minr = min(minr, Y.live_read_bend(P, cnt, seed=s, frames=frames)[0])
        if minr < L.MIN_BEND_R:
            bad += "P"
    return bad, dict(len=b["len"], tail=b["tail"], turn=b["turn"], arrive=b["arrive"], minr=minr)


def one(line):
    r = json.loads(line)
    if r.get("mode") != "raw":
        return None
    ground = Y.Ground(r.get("blocked", ()))
    ties = r["ties"] if isinstance(r.get("ties"), list) else ()
    fc = r.get("fartype") == "Terminal" or r["cord"].count("terminal:") == 2
    try:
        g = Y.lay_live_end(r["pts"], r["pos"], r["out"], ground, ties, far_cut=fc)
        bad, m = judge(g["pts"], r["pos"], r["out"], g["cnt"])
        o = dict(src=r["src"], scene=r["scene"], cord=r["cord"], far=r.get("fartype", ""), len0=r["len"], kind=g["kind"], why=g["why"], bad=bad,
                 raw_bad=r["bad"], **m)
        o["len"] = round(o["len"], 3)
        o["minr"] = round(min(o["minr"], 99), 4)
        kind = g["kind"].split()[0]
        if kind in ("turn", "service", "none"):
            # the emergency-only check, and the map's reading of the bare cord: with the margins, and with the bare bars
            bare = Y.lay_live_end(r["pts"], r["pos"], r["out"], ground, ties, allow_device=False, far_cut=fc)
            o["bare_margin"] = bare["kind"]
            knife = Y.lay_live_end(r["pts"], r["pos"], r["out"], ground, ties, allow_device=False, margin=False, far_cut=fc)
            kb = judge(knife["pts"], r["pos"], r["out"], knife["cnt"])[0] if knife["kind"] != "none" else "x"
            o["bare_knife"] = knife["kind"] if kb == "" else "none"
        if kind != "kept":
            o["grew"] = round(L.length(g["pts"]) - r["len"], 2)
        return json.dumps(o)
    except Exception as ex:  # a cord the lay cannot read is a finding, not a crash
        return json.dumps(dict(src=r["src"], scene=r["scene"], cord=r["cord"], kind="error", why=repr(ex), bad="E", len0=r["len"]))


def replay(src, dst, jobs, every):
    def lines():
        with open(src) as f:
            k = 0
            for line in f:
                if '"mode":"raw"' not in line:
                    continue
                k += 1
                if k % every == 0:
                    yield line
    n = 0
    with multiprocessing.Pool(jobs) as pool, open(dst, "w") as out:
        for res in pool.imap(one, lines(), chunksize=40):
            if res:
                out.write(res + "\n")
                n += 1
                if n % 5000 == 0:
                    print("replay:", n, flush=True)
    print("replay: %d cords -> %s" % (n, dst))


def region(o):
    """(setting, what the cord comes from, run length) of a family scene; the source's name otherwise."""
    if o["src"] != "family":
        return (o["src"], o.get("far", ""), "")
    w = o["scene"].split()
    return (w[7] if len(w) > 8 else "shipped", w[1], w[3])


def table(path):
    rows = [json.loads(x) for x in open(path)]
    kinds = collections.Counter()
    bad = collections.Counter()
    reg = collections.defaultdict(collections.Counter)
    worst = collections.defaultdict(lambda: 99.0)
    devices_needed = devices_not = 0
    for o in rows:
        k = o["kind"].split()[0]
        if k == "join":
            k = "join broad" if float(o["kind"].split()[1]) >= 0.66 else "join tight"
        kinds[k] += 1
        if o["bad"]:
            bad[o["bad"]] += 1
        rg = region(o)
        reg[rg][k] += 1
        if o["bad"]:
            reg[rg]["BAR FAILS"] += 1
        worst[rg] = min(worst[rg], o.get("minr", 99))
        if k in ("turn", "service"):
            if o.get("bare_margin") == "none":
                devices_needed += 1
            else:
                devices_not += 1
    print("cords: %d   lay: %s" % (len(rows), dict(kinds)))
    print("bars failing after the lay: %s" % (dict(bad) or "none"))
    print("handed cords failing a bar (the builder before the lay): %d" % sum(1 for o in rows if o.get("raw_bad")))
    print("devices: %d used, %d where the bare cord could not hold with margin, %d where it could (must be 0)" % (devices_needed + devices_not, devices_needed, devices_not))
    cols = ["kept", "join broad", "join tight", "turn", "still", "none", "error", "BAR FAILS"]
    print("%-10s %-10s %-6s " % ("setting", "from", "run") + " ".join("%10s" % c for c in cols) + "   tightest")
    for rg in sorted(reg):
        print("%-10s %-10s %-6s " % rg + " ".join("%10d" % reg[rg][c] for c in cols) + "   %.3f" % worst[rg])
    return rows


def shots(out_dir=None, quiet=False):
    """A fitting on the conduit's own line, its tip `a` cells behind the conduit end: the bare cord, the device, or nothing."""
    res = []
    a = 0.30
    while a <= 2.4001:
        n = max(2, int(a / Y.STEP))
        P = [(k * a / n, 0.0) for k in range(n + 1)]
        # the fitting: a box whose arm's tip is where the cord starts, its middle an arm behind
        box = lambda q: math.hypot(q[0] + ARM, q[1]) < KEEP_OFF  # noqa: E731
        full = Y.lay_live_end(P, (a, 0), (1, 0), on_far=box)
        bare = Y.lay_live_end(P, (a, 0), (1, 0), allow_device=False, on_far=box)
        knife = Y.lay_live_end(P, (a, 0), (1, 0), allow_device=False, margin=False, on_far=box)
        kb = judge(knife["pts"], (a, 0), (1, 0), knife["cnt"])[0] if knife["kind"] != "none" else "x"
        res.append((round(a, 2), bare["kind"], knife["kind"] if kb == "" else "none", full["kind"]))
        a += 0.05
    if not quiet:
        print("%6s  %-18s %-18s %-18s" % ("a", "bare, with margin", "bare, bars only", "with the devices"))
        for r in res:
            print("%6.2f  %-18s %-18s %-18s" % r)
    return res


def pose_cord(dist, bearing, phi):
    """The handed cord of an abstract pose: a fitting's tip `dist` cells from the conduit end (at the origin, the conduit running +x), at
    `bearing` degrees round it, the cord leaving the fitting heading `phi` degrees: the fitting's stiff bit, then a taut chord to the end."""
    b, h = math.radians(bearing), math.radians(phi)
    F = (dist * math.cos(b), dist * math.sin(b))
    P = [(F[0] + math.cos(h) * 0.05 * k, F[1] + math.sin(h) * 0.05 * k) for k in range(4)]
    a = P[-1]
    m = max(2, int(math.hypot(*a) / 0.05))
    return P + [(a[0] * (1 - k / m), a[1] * (1 - k / m)) for k in range(1, m + 1)]


#: how far a cord keeps off a fitting's body (CordBuilder.BoxKeepOff), and how far behind its tip a box's or plate's middle is (an arm)
KEEP_OFF, ARM = 0.55, 0.5


def pose_body(dist, bearing, phi):
    """The middle of the abstract fitting's body: an arm's length behind its tip."""
    b, h = math.radians(bearing), math.radians(phi)
    return (dist * math.cos(b) - ARM * math.cos(h), dist * math.sin(b) - ARM * math.sin(h))


def body_on_run(dist, bearing, phi):
    """Whether the fitting's body lies on the cut end's own straight run (the run is the segment y = 0, -LIVE_RUN <= x <= 0), and off its
    line (a body ON the line is the straight shot: the cord is kept, or lies still). No cord can be laid to such a fitting and whip."""
    c = pose_body(dist, bearing, phi)
    dx = max(-Y.LIVE_RUN - c[0], 0.0, c[0])
    return math.hypot(dx, c[1]) < KEEP_OFF and abs(c[1]) > 0.05


def run_dist(q):
    """How far a point is from the cut end's straight run (y = 0, -LIVE_RUN <= x <= 0)."""
    return math.hypot(max(-Y.LIVE_RUN - q[0], 0.0, q[0]), q[1])


def machine_body(dist, bearing, phi):
    """A machine's footprint as the abstract fitting's body: the unit cell behind its plug -> (inside(q), distance from the run)."""
    b, h = math.radians(bearing), math.radians(phi)
    tip, u = (dist * math.cos(b), dist * math.sin(b)), (math.cos(h), math.sin(h))

    def local(q):
        dx, dy = q[0] - tip[0], q[1] - tip[1]
        return -(dx * u[0] + dy * u[1]), -dx * u[1] + dy * u[0]      # depth behind the plug, offset across

    def inside(q):
        d, a = local(q)
        return 0.0 < d < 1.0 and abs(a) < 0.5

    near = 9.0
    for k in range(14):
        d, a = local((-Y.LIVE_RUN * k / 13.0, 0.0))
        near = min(near, math.hypot(max(-d, 0.0, d - 1.0), max(abs(a) - 0.5, 0.0)))
    return inside, near


def one_pose(args):
    dist, bearing, phi = args[:3]
    if len(args) > 3 and args[3] == "none":
        on_far, near, on_run = None, 9.0, False
    elif len(args) > 3 and args[3] == "machine":
        on_far, near = machine_body(dist, bearing, phi)
        on_run = near < 1e-9
    else:
        c = pose_body(dist, bearing, phi)
        on_far, near, on_run = (lambda q: math.hypot(q[0] - c[0], q[1] - c[1]) < KEEP_OFF), run_dist(c), body_on_run(dist, bearing, phi)
    g = Y.lay_live_end(pose_cord(dist, bearing, phi), (0, 0), (1, 0), on_far=on_far)
    bad, r = judge(g["pts"], (0, 0), (1, 0), g["cnt"])
    return dict(dist=dist, bearing=bearing, phi=phi, kind=g["kind"], bad=bad, on_run=on_run, near=round(near, 3), len=round(r["len"], 2), minr=round(min(r["minr"], 99), 3), why=g["why"][:80])


def poses(dst, jobs, dists=None, step=15, body="box", quiet=False):
    """Every fitting pose round a conduit end on open floor (the abstract family): where a bare cord holds, lies still, or finds no lay."""
    dists = dists or [round(0.3 + 0.1 * k, 1) for k in range(23)]
    grid = [(d, b, p, body) for d in dists for b in range(0, 360, step) for p in range(0, 360, step)]
    with multiprocessing.Pool(jobs) as pool:
        res = pool.map(one_pose, grid, chunksize=20)
    if dst:
        json.dump(res, open(dst, "w"))
    if quiet:
        return res
    by = collections.defaultdict(collections.Counter)
    for r in res:
        k = r["kind"].split()[0]
        by[r["dist"]][("BAR FAILS" if r["bad"] else k) + (", body on run" if r["on_run"] else "")] += 1
    unlaid = [r for r in res if r["bad"] or r["kind"].split()[0] == "none"]
    print("poses: %d (distance x bearing x heading, %d deg steps; the fitting's body a %s) -> %s" % (len(res), step, body, dst))
    print("unlaid: %d; the furthest any unlaid fitting's body is from the run: %.3f" % (len(unlaid), max([r["near"] for r in unlaid], default=0.0)))
    for d in sorted(by):
        print("  %.1f  %s" % (d, dict(by[d])))
    return res


def main(argv):
    if len(argv) >= 2 and argv[0] == "poses":
        poses(argv[1], int(argv[argv.index("--jobs") + 1]) if "--jobs" in argv else max(1, (os.cpu_count() or 2) - 2),
              body="machine" if "--machine" in argv else "none" if "--no-body" in argv else "box")
        return 0
    if len(argv) >= 3 and argv[0] == "replay":
        jobs = int(argv[argv.index("--jobs") + 1]) if "--jobs" in argv else max(1, (os.cpu_count() or 2) - 2)
        every = int(argv[argv.index("--every") + 1]) if "--every" in argv else 1
        replay(argv[1], argv[2], jobs, every)
        return 0
    if len(argv) >= 2 and argv[0] == "table":
        table(argv[1])
        return 0
    if argv and argv[0] == "shots":
        shots()
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
