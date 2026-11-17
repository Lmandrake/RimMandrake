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
        full = Y.lay_live_end(P, (a, 0), (1, 0))
        bare = Y.lay_live_end(P, (a, 0), (1, 0), allow_device=False)
        knife = Y.lay_live_end(P, (a, 0), (1, 0), allow_device=False, margin=False)
        kb = judge(knife["pts"], (a, 0), (1, 0), knife["cnt"])[0] if knife["kind"] != "none" else "x"
        res.append((round(a, 2), bare["kind"], knife["kind"] if kb == "" else "none", full["kind"]))
        a += 0.05
    if not quiet:
        print("%6s  %-18s %-18s %-18s" % ("a", "bare, with margin", "bare, bars only", "with the devices"))
        for r in res:
            print("%6.2f  %-18s %-18s %-18s" % r)
    return res


def main(argv):
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
