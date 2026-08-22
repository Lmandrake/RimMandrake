#!/usr/bin/env python3
"""selftest_river_link_order.py - prove ashkarr_paint.river_link_rows emits mouth-first.

🔴 WHY THIS IS NOT JUST "RE-RUN THE PAINTER". `world/ASHKARR_WORLDMAP_tiles.csv` is
frozen and the map was accepted for v1 (`canon.yml: accepted_for_v1: true`). Re-running
`ashkarr_paint.py` to check a row ordering would repaint an accepted planet, which
RIVER_LINKS_EMITTED_BACKWARDS_1 names as an outright FAIL condition.

⇒ Instead, RECONSTRUCT the emitter's four inputs from the artifacts we already have -
the accepted links CSV gives the drainage edges, the tiles CSV gives sea and
accumulation - then run the real `river_link_rows` on them and compare row for row
against the accepted file. Nothing is regenerated and nothing is written.

What this proves, and what it does not:
  ✅ the emitter's ORDER and ORIENTATION now match the accepted, corrected file
  ✅ the link SET is unchanged - same rows, same `def` column, no row lost or invented
  ⛔ it does NOT re-derive the drainage from the elevation field. If the painter's
     hydrology changed, this test would still pass. It is a test of the EMITTER.
"""
from __future__ import annotations
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
from ashkarr_paint import river_link_rows  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
LINKS = ROOT / "world" / "ASHKARR_WORLDMAP_links.csv"
TILES = ROOT / "world" / "ASHKARR_WORLDMAP_tiles.csv"


def main() -> int:
    accepted = [r for r in csv.DictReader(LINKS.open(encoding="utf-8"))
                if r["kind"] == "river"]
    tiles = list(csv.DictReader(TILES.open(encoding="utf-8")))
    n = len(tiles)

    sea = np.zeros(n, dtype=bool)
    for t in tiles:
        sea[int(t["tile"])] = bool(int(t["water"]))

    # 🔴 `acc` IS RECONSTRUCTED FROM THE ACCEPTED DEFS, NOT FROM tiles.csv, AND THAT IS
    # NOT A SHORTCUT. Measured 2026-08-21: `f(river_flow)` reproduces the accepted `def`
    # column on only 135 of 237 non-sea rows. The two files are not two views of one
    # run - `world/ASHKARR_WORLDMAP_tiles.csv` is the HAND-AUTHORED map (owner: "ONE
    # planetary map... iterate by LOOKING"), and its `river_flow` column has been edited
    # since the links were emitted. Feeding it here would test the owner's edits, not
    # the emitter.
    # ⇒ Give the emitter an `acc` that reproduces the accepted `def` exactly, so the
    # only thing under test is what actually changed: ORDER and ORIENTATION. Each tile
    # is the upstream end of at most one row (`down` is single-valued), so there is no
    # conflict to resolve.
    BAND = {"Creek": 100.0, "River": 500.0, "LargeRiver": 2000.0, "HugeRiver": 5000.0}
    acc = np.zeros(n, dtype=float)
    for r in accepted:
        acc[int(r["b"])] = BAND[r["def"]]

    # a = downstream, b = upstream in the accepted file, so down[b] = a.
    down = np.full(n, -1, dtype=int)
    A, B = set(), set()
    for r in accepted:
        a, b = int(r["a"]), int(r["b"])
        down[b] = a
        A.add(a)
        B.add(b)
    # `chan` is every tile with an outgoing river edge, plus any downstream endpoint
    # that is not sea - a terminal playa is a channel tile with nothing below it.
    chan = np.zeros(n, dtype=bool)
    for t in B:
        chan[t] = True
    for t in A:
        if not sea[t]:
            chan[t] = True

    produced = river_link_rows(chan, down, acc, sea)

    fails = []
    if len(produced) != len(accepted):
        fails.append("row count %d produced vs %d accepted" % (len(produced), len(accepted)))

    def key(row):
        a, b = int(row[1]), int(row[2])
        return (min(a, b), max(a, b), row[0], row[3])

    ps = sorted(key(r) for r in produced)
    as_ = sorted(key(["river", r["a"], r["b"], r["def"]]) for r in accepted)
    if ps != as_:
        extra = [x for x in ps if x not in set(as_)][:5]
        missing = [x for x in as_ if x not in set(ps)][:5]
        fails.append("link SET differs. produced-only %s | accepted-only %s" % (extra, missing))

    for i, (p, a) in enumerate(zip(produced, accepted)):
        if (int(p[1]), int(p[2]), p[3]) != (int(a["a"]), int(a["b"]), a["def"]):
            fails.append("row %d: produced %s vs accepted %s"
                         % (i, p[1:], [a["a"], a["b"], a["def"]]))
            if len(fails) > 6:
                break

    elev = {int(t["tile"]): float(t["elev_m"]) for t in tiles}
    uphill = sum(1 for r in produced if elev[int(r[1])] < elev[int(r[2])])
    print("river links     : %d produced, %d accepted" % (len(produced), len(accepted)))
    print("link set        : %s" % ("IDENTICAL" if ps == as_ else "DIFFERS"))
    print("order+orientation: %s" % ("IDENTICAL, row for row" if not any(
        f.startswith("row ") for f in fails) else "DIFFERS"))
    print("a-end lower than b-end, i.e. row runs uphill as mouth-first wants: "
          "%d / %d" % (uphill, len(produced)))

    if fails:
        print("\nFAIL")
        for f in fails[:8]:
            print("  " + f)
        return 1
    print("\nPASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
