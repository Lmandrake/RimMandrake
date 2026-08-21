"""ashkarr_regrade_rivers.py - a river narrows as it dies. Grade each segment by ITS flow.

    python3 src/RimMandrake/Utils/ashkarr_regrade_rivers.py            # report only
    python3 src/RimMandrake/Utils/ashkarr_regrade_rivers.py --apply    # rewrite the def column

THE DEFECT, measured on the painted world 2026-08-21. A river's grade is fixed for its
whole length, so a stream LOSING water to evaporation still draws at maximum width all the
way to where it dries up. Worked example, system 2 in The Dune Sea: 30 tiles, graded
`HugeRiver` from tile 11347 at flow 26,193 down to tile 16727 at flow 6,968 - a quarter of
the water, the same river on screen - then it stops.

Planet-wide the hierarchy is inverted: **113 `HugeRiver` edges against 103 `Creek`**. Real
drainage is mostly small streams.

WHAT THIS FIXES AND WHAT IT DOES NOT.
✅ Fixes the constant width and the inverted hierarchy. A losing stream now steps
   HugeRiver -> LargeRiver -> River -> Creek as its flow falls, which is what a river doing
   that actually looks like.
⛔ Does NOT fix rivers that BEGIN from nothing. Six big chains start on dry land with no
   tributary above them because the channel head is wherever accumulation first crosses a
   threshold - the whole catchment feeding 28,936 units of flow exists in the field and is
   simply never drawn. That is inside `ashkarr_paint.py`, and re-running it moves biomes.
   Filed as RIVERS_BEGIN_FROM_NOTHING_1.

⛔ AND IT IS NOT A GENERATOR. One pass over the one map, no seed, no knobs.

WHAT IT TOUCHES: the `def` column of river rows in the links bundle. Road rows are not
read and the other columns are asserted byte-identical before anything is written.
"""
import argparse
import collections
import csv
import io
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
TILES = os.path.join(REPO, "world", "ASHKARR_WORLDMAP_tiles.csv")
LINKS = os.path.join(REPO, "world", "ASHKARR_WORLDMAP_links.csv")

# Flow at which a segment earns each grade. Chosen against the measured distribution
# (p5=21, p50=1657, p80=15063, p100=28930) so that the commonest grade is the smallest
# one, and so the Scald outflow visibly steps down twice on its way to drying up.
GRADES = [(20000.0, "HugeRiver"), (8000.0, "LargeRiver"), (1000.0, "River"), (0.0, "Creek")]


def grade(flow):
    for cut, name in GRADES:
        if flow >= cut:
            return name
    return "Creek"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    flow = {}
    with io.open(TILES, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            try:
                flow[int(r["tile"])] = float(r["river_flow"] or 0)
            except (TypeError, ValueError):
                flow[int(r["tile"])] = 0.0

    with io.open(LINKS, encoding="utf-8", newline="") as fh:
        rd = csv.DictReader(fh)
        cols = list(rd.fieldnames)
        rows = list(rd)
    before = [dict(r) for r in rows]

    was = collections.Counter(r["def"] for r in rows if r["kind"] == "river")
    moved = 0
    for r in rows:
        if r["kind"] != "river":
            continue
        # ⚠️ the MIN of the two endpoints, not the max. A segment is only as big as the
        # water actually crossing it, and taking the max would keep a dying river wide by
        # borrowing the flow of the tile upstream of it - which is the bug being fixed.
        f = min(flow.get(int(r["a"]), 0.0), flow.get(int(r["b"]), 0.0))
        g = grade(f)
        if g != r["def"]:
            r["def"] = g
            moved += 1
    now = collections.Counter(r["def"] for r in rows if r["kind"] == "river")

    print("%-12s %6s %6s" % ("def", "was", "now"))
    for d in ("Creek", "River", "LargeRiver", "HugeRiver"):
        print("%-12s %6d %6d" % (d, was.get(d, 0), now.get(d, 0)))
    print("\nsegments re-graded: %d of %d river edges" % (moved, sum(was.values())))
    print("road rows untouched: %d" % sum(1 for r in rows if r["kind"] != "river"))

    # 🔴 Only `def`, and only on river rows.
    for i, r in enumerate(rows):
        for c in cols:
            if c == "def" and r["kind"] == "river":
                continue
            if r[c] != before[i][c]:
                sys.exit("🔴 %s changed on row %d - refusing to write" % (c, i))
    print("verified: every other column, and every road row, byte-identical")

    if not a.apply:
        print("\nreport only. Pass --apply to write.")
        return 0
    with io.open(LINKS, "w", encoding="utf-8", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=cols)
        wr.writeheader()
        wr.writerows(rows)
    print("\nwrote %s" % LINKS)
    return 0


if __name__ == "__main__":
    sys.exit(main())
