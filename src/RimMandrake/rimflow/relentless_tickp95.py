"""Tick wall p50/p95 and the slow leaves over a window of supervisor ticks, and a check that every leaf over budget has
a detach item filed (RELENTLESS_REMEASURE_TICK_P95_DETACH_NEXT).

`report <since-iso> <journal.jsonl>...` reads the tick rows (do=tick with phases) of the Relentless store journal that
relentless_tickprof fills, and prints the report (the WP-10a prof.py format, plus a `budget` block).
`check <report.txt>` exits 0 only when the report covers >= MIN_TICKS ticks, names wall p50/p95 and the phases, and
every leaf in its budget block maps to an item with a `file` event in the ledger. A leaf the map does
not name, or whose item is missing, exits 1 and names it: file the detach, then add it to DETACH.
The checker's box holds the ledger as of the candidate's PARENT (relentless_wall tree_from_parent), so commit a new `file`
event at least one commit before the sha that `finish` names, or this check cannot see it there.

Budget: a py_leaf costing >= BUDGET_S seconds per tick on mean (~3% of a ~310 s tick) is over budget.
"""
import json
import os
import re
import statistics
import sys

MIN_TICKS = 100
BUDGET_S = 10.0
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
LEDGER = os.path.join(ROOT, "infrastructure", "state", "ledger", "events")

# leaf (the py_leaves "at" key) -> the item that detaches it from the tick
DETACH = {
    "relentless_wall:make_box < relentless:step [child]": "MAKEBOX_REWIRE_OFF_TICK_STILL_TOP_LEAF",
    "relentless_integrity:nul_or_empty < relentless_integrity:clone_damage": "NULSCAN_REWIRE_OFF_TICK_GREW_SINCE",
    "scratch_clone:own_bytes < scratch_clone:clone_bytes [child]": "CLONEBYTES_REWIRE_OFF_TICK_NEW_THIRD",
    "relentless:_detached_clone < relentless:clean_checkout [child]": "CLEANCHECKOUT_REWIRE_OFF_TICK_CLONE_INLINE",
    "relentless:prepare < relentless:_lease [child]": "LEASEPREP_REWIRE_OFF_TICK_SIX_MINUTES",
    "relentless:rimflow < relentless:ledger_close [child]": "LEDGERCLOSE_REWIRE_OFF_TICK_ONE_PROC_EACH",
    "relentless_showing:mods_fp < relentless_jobs:__call__": "MODSFP_REWIRE_OFF_TICK_MISS_WALKS_INLINE",
}


def pct(v, q):
    v = sorted(v)
    return v[min(len(v) - 1, int(q * len(v)))] if v else None


def rows(since, paths):
    out = []
    for p in paths:
        with open(p, encoding="utf-8", errors="replace") as f:
            for line in f:
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                if d.get("do") == "tick" and "phases" in d and d.get("at", "") >= since:
                    out.append(d)
    return out


def report(since, paths):
    rs = rows(since, paths)
    n = len(rs)
    L = ["n %d %s %s" % (n, rs[0]["at"] if rs else "", rs[-1]["at"] if rs else "")]
    w = [r["wall_s"] for r in rs]
    L.append("wall p50 %s p95 %s mean %.0f" % (pct(w, .5), pct(w, .95), statistics.mean(w) if w else 0))
    ph = {}
    for r in rs:
        for k, v in r["phases"].items():
            ph.setdefault(k, []).append(v)
    tot = sum(sum(v) for v in ph.values()) or 1
    for k, v in sorted(ph.items(), key=lambda a: -sum(a[1])):
        L.append("phase %-14s p50 %6.1f p95 %6.1f share %4.1f%%" % (k, pct(v, .5), pct(v, .95), 100 * sum(v) / tot))
    pr = {}
    for r in rs:
        for x in r.get("proc") or []:
            if isinstance(x, dict):
                k, s = x.get("cmd") or x.get("name") or "?", x.get("s", 0)
            else:
                k, s = str(x[0]), x[1]
            pr[k] = pr.get(k, 0) + s
    L.append("proc top:")
    L += ["  %-40s %7.0f s" % (k, v) for k, v in sorted(pr.items(), key=lambda a: -a[1])[:12]]
    ss = {}
    for r in rs:
        for x in r.get("slow_steps") or []:
            ss.setdefault(x["item"], []).append(x["s"])
    L.append("slow steps:")
    L += ["  %-50s n=%d sum=%.0f" % (k, len(v), sum(v)) for k, v in sorted(ss.items(), key=lambda a: -sum(a[1]))[:10]]
    pl = {}
    for r in rs:
        for x in r.get("py_leaves") or []:
            pl[x["at"]] = pl.get(x["at"], 0) + x["s"]
    L.append("py_leaves top:")
    L += ["  %-80s %d" % (k, v) for k, v in sorted(pl.items(), key=lambda a: -a[1])[:25]]
    L.append("budget %.1f s/tick over %d ticks:" % (BUDGET_S, n))
    for k, v in sorted(pl.items(), key=lambda a: -a[1]):
        if n and v / n >= BUDGET_S:
            L.append("  over %6.1f s/tick %s -> %s" % (v / n, k, DETACH.get(k, "UNFILED")))
    return "\n".join(L) + "\n"


def item_on_disk(i):
    """The item was filed: a `file` event for it in a ledger shard (its prose file is optional)."""
    import glob
    for p in glob.glob(os.path.join(LEDGER, "*.jsonl")):
        with open(p, encoding="utf-8", errors="replace") as f:
            for line in f:
                if i in line:
                    try:
                        d = json.loads(line)
                    except ValueError:
                        continue
                    if d.get("id") == i and d.get("event") == "file":
                        return True
    return False


def check(path):
    txt = open(path, encoding="utf-8").read()
    bad = []
    m = re.search(r"^n (\d+) ", txt, re.M)
    n = int(m.group(1)) if m else 0
    if n < MIN_TICKS:
        bad.append("covers %d ticks, needs >= %d" % (n, MIN_TICKS))
    if not re.search(r"^wall p50 \d+(\.\d+)? p95 \d+(\.\d+)?", txt, re.M):
        bad.append("no wall p50/p95 line")
    if not re.search(r"^phase \S+ +p50", txt, re.M):
        bad.append("no phase lines")
    if not re.search(r"^budget ", txt, re.M):
        bad.append("no budget block")
    over = re.findall(r"^  over +[\d.]+ s/tick (.+) -> (\S+)$", txt, re.M)
    for leaf, named in over:
        i = DETACH.get(leaf)
        if not i:
            bad.append("over budget, no detach mapped: %s" % leaf)
        elif named != i:
            bad.append("report says %s, the map says %s (stale report, write it again): %s" % (named, i, leaf))
        elif not item_on_disk(i):
            bad.append("over budget, item %s not on disk: %s" % (i, leaf))
    for b in bad:
        print("FAIL", b)
    if bad:
        return 1
    print("OK %d ticks; %d leaves over %.1f s/tick, each with a detach item: %s"
          % (n, len(over), BUDGET_S, ", ".join(DETACH[l] for l, _ in over) or "none"))
    return 0


def main(a):
    if len(a) >= 3 and a[0] == "report":
        sys.stdout.write(report(a[1], a[2:]))
        return 0
    if len(a) == 2 and a[0] == "check":
        return check(a[1])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
