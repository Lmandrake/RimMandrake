"""verify_u4_riverdist.py - prove a world save carries the canonical (U4) river flow.

WORLD_RIVERS_REPAIR_DOWNHILL_AT_LAST: the importer laid rivers in export order, which
flattened riverDist (every head <= 5). The fix re-laid them mouth-first live and saved.
This reads the save's tileRiverDistancesDeflate and river links and checks, against
world/ASHKARR_PARITY_U4_riverdist_2026-10-20_plan.json and its links CSV:

  1. the save's river edge set and defs equal the plan's river rows (same geometry);
  2. riverDist equals the plan's `after` (the canonical values) on every plan tile;
  3. the maximum riverDist on a river tile is the canonical maximum (50, not 5).

Usage: python3 world/verify_u4_riverdist.py <save.rws>    exit 0 all hold, 1 any fails.
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src", "RimMandrake", "Utils"))
import worldview  # noqa: E402

PLAN = os.path.join(HERE, "ASHKARR_PARITY_U4_riverdist_2026-10-20_plan.json")


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    plan = json.load(open(PLAN, encoding="utf-8"))
    after = {int(k): int(v) for k, v in plan["after"].items()}
    rows = [r for r in csv.DictReader(open(os.path.join(HERE, plan["linksCsv"]), encoding="utf-8"))
            if r["kind"] == "river"]
    want_edges = {tuple(sorted((int(r["a"]), int(r["b"])))): r["def"] for r in rows}

    try:
        pv = worldview.PlanetView(argv[1])
        dist = worldview.read_river_distances(pv.grid)
    except Exception as e:  # a corrupt or partial block: decoding failed, so the save cannot pass
        print("FAIL: could not decode the save: %r" % e)
        return 1
    if dist is None:
        print("FAIL: save has no tileRiverDistancesDeflate block")
        return 1
    got_edges = {tuple(sorted((o, n))): dfn for o, n, dfn, _ in pv.rivers}

    fails = 0
    # the save stores each river link once; a duplicate, a link off the grid or an
    # unresolved def hash would be hidden by the edge dict below, so refuse them here
    if len(pv.rivers) != len(got_edges) or pv.rivers_broken or pv.rivers_unresolved:
        print("FAIL 0: %d raw river links for %d edges, %d broken, unresolved hashes %s"
              % (len(pv.rivers), len(got_edges), len(pv.rivers_broken), pv.rivers_unresolved))
        fails += 1
    # read_links zips the three parallel arrays, which drops unmatched trailing entries:
    # decode them here and require one origin, one slot and one def per link
    g = pv.grid
    lens = []
    for name, width in zip(worldview.LINKS["river"][:3], (4, 1, 2)):
        tag = "<%sDeflate>" % name
        a = g.text.find(tag, g.surf_lo, g.surf_hi)
        if a < 0:
            lens.append(0)
            continue
        b = g.text.find("</%sDeflate>" % name, a)
        lens.append(len(worldview._inflate(g.text[a + len(tag):b])) // width)
    if len(set(lens)) != 1 or lens[0] != len(pv.rivers):
        print("FAIL 0: river link arrays origins/slots/defs = %s entries, %d links read" % (lens, len(pv.rivers)))
        fails += 1
    if len(dist) != pv.n:
        print("FAIL: riverDist grid has %d entries, the planet has %d tiles" % (len(dist), pv.n))
        return 1
    top = max(list(after) + [t for e in got_edges for t in e])
    if top >= len(dist):
        print("FAIL: tile %d is referenced, the planet has %d tiles" % (top, len(dist)))
        return 1
    # sanity: the instrument sees rivers at all (a blind read would give 0 edges / all zeros)
    print("save: %d river edges, %d tiles in riverDist grid; plan: %d edges, %d river tiles"
          % (len(got_edges), len(dist), len(want_edges), len(after)))
    if got_edges != want_edges:
        miss = set(want_edges) - set(got_edges)
        extra = set(got_edges) - set(want_edges)
        wrongdef = [e for e in set(want_edges) & set(got_edges) if want_edges[e] != got_edges[e]]
        print("FAIL 1: edge set differs: %d missing, %d extra, %d wrong def (e.g. %s)"
              % (len(miss), len(extra), len(wrongdef), sorted(miss | extra)[:5] or wrongdef[:5]))
        fails += 1
    else:
        print("PASS 1: river edges and defs equal the plan (%d)" % len(got_edges))

    bad = [(t, dist[t], v) for t, v in sorted(after.items()) if dist[t] != v]
    if bad:
        print("FAIL 2: riverDist differs from canon on %d/%d tiles, e.g. (tile, save, canon) %s"
              % (len(bad), len(after), bad[:8]))
        fails += 1
    else:
        print("PASS 2: riverDist equals canon on %d/%d river tiles" % (len(after), len(after)))

    rtiles = {t for e in got_edges for t in e}
    mx_save = max(dist[t] for t in rtiles) if rtiles else 0
    mx_canon = max(after.values())
    if mx_save != mx_canon:
        print("FAIL 3: max riverDist on river tiles %d, canon %d" % (mx_save, mx_canon))
        fails += 1
    else:
        print("PASS 3: max riverDist on river tiles %d == canon %d" % (mx_save, mx_canon))
    print("RESULT:", "PASS" if not fails else "FAIL")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
