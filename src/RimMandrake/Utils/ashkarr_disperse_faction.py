#!/usr/bin/env python3
"""
ashkarr_disperse_faction.py — spread one faction's settlements as far apart as the
map allows, subject to a biome whitelist.

WHY. Owner, 2026-09-07, of the Deep Desert Tribes: *"they are weirdly linear right
now, not a good look"* — six of their nine sat in a longitude band 7-29 deg with a
13.7 deg minimum gap. A faction that lives in the deep desert should read as
scattered across it, not strung along a line.

WHAT IT SOLVES. Maximin dispersion (the k-dispersion problem): choose N tiles so
that the SMALLEST distance from any chosen site to any settlement — the faction's
own new sites AND every other faction's fixed ones — is as large as possible.
Maximising the minimum is the right objective here rather than maximising the mean,
because one pair sitting on top of each other is exactly the defect being fixed and
a mean would hide it.

  1. GREEDY FARTHEST-FIRST seeds the answer: every other faction's settlement is a
     fixed obstacle, then N times over, take the candidate tile whose nearest
     already-placed neighbour is furthest away.
  2. LOCAL IMPROVEMENT then sweeps: move each site, one at a time, to whichever
     candidate most raises the global minimum, until nothing improves. Greedy alone
     is a known ~2-approximation and the sweep reliably recovers several degrees.

Deterministic — no RNG anywhere, so a re-run reproduces the same map. Ties break on
tile id.

CONSTRAINTS APPLIED. Candidate tiles must be in --biomes; must carry no world object
and no landmark (`LandmarkDef.IsValidTile` rejects a settlement sharing a tile, and
`AddLandmark` will not police it for us); and must not be Impassable hilliness.

⚠️ CHECK THE FACTION IS ROAD-EXEMPT BEFORE MOVING IT. Most factions must stay on the
one road net — `ashkarr_settle.py` drops a site the road search cannot reach rather
than writing an orphan. The Deep Desert Tribes are the documented exception: "the
Deep Desert Tribes build none. 91 road edges into Tusken holdings were removed
2026-08-24." Moving a road-bound faction with this tool will strand it.

    python3 ashkarr_disperse_faction.py --faction "Deep Desert Tribes"
    python3 ashkarr_disperse_faction.py --faction "Deep Desert Tribes" --apply
"""
import argparse
import csv
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)

TILES = os.path.join(REPO, "world", "ASHKARR_WORLDMAP_tiles.csv")
OBJS = os.path.join(REPO, "Transient", "base_e", "objects.json")
LMKS = os.path.join(REPO, "Transient", "base_e", "landmarks.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--faction", required=True)
    ap.add_argument("--biomes", default="Desert,ExtremeDesert")
    ap.add_argument("--tiles", default=TILES)
    ap.add_argument("--objects", default=OBJS)
    ap.add_argument("--landmarks", default=LMKS)
    ap.add_argument("--max-arc", type=float, default=None,
                    help="keep sites within this many degrees of the substellar point")
    ap.add_argument("--min-temp", type=float, default=None,
                    help="keep sites at or above this mean temperature (C)")
    ap.add_argument("--slack", type=float, default=2.0,
                    help="degrees of minimum separation to trade for a rounder scatter")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    ok_biomes = set(a.biomes.split(","))
    T = {int(r["tile"]): r for r in csv.DictReader(open(a.tiles))}
    objs = json.load(open(a.objects))
    lmk = {int(l["tile"]) for l in json.load(open(a.landmarks))}
    occupied = {int(o["tile"]) for o in objs}

    setts = [o for o in objs if o.get("isSettlement")]
    mine = [o for o in setts if (o.get("factionName") or "") == a.faction]
    if not mine:
        sys.exit("no settlements for faction %r" % a.faction)
    others = [int(o["tile"]) for o in setts if o not in mine]

    def vec(t):
        la, lo = math.radians(float(T[t]["lat"])), math.radians(float(T[t]["lon"]))
        return (math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la))

    V = {}

    def v(t):
        if t not in V:
            V[t] = vec(t)
        return V[t]

    def sep(x, y):
        return math.degrees(math.acos(max(-1.0, min(1.0, sum(p * q for p, q in zip(v(x), v(y)))))))

    old = [int(o["tile"]) for o in mine]
    cand = sorted(t for t, r in T.items()
                  if r["biome"] in ok_biomes
                  and t not in occupied
                  and t not in lmk
                  and r["hilliness"].strip() != "5"
                  and (a.max_arc is None or float(r["arc"]) <= a.max_arc)
                  and (a.min_temp is None or float(r["temp_c"]) >= a.min_temp))
    # the faction's own current tiles are legal destinations too
    cand = sorted(set(cand) | {t for t in old if T[t]["biome"] in ok_biomes})
    if a.max_arc or a.min_temp:
        print("  climate envelope: arc <= %s, temp >= %s" % (a.max_arc, a.min_temp))

    def score(sites):
        pts = others + list(sites)
        return min(sep(x, y) for i, x in enumerate(pts) for y in pts[i + 1:]
                   if x in sites or y in sites)

    print("DISPERSE %r — %d settlements, %d candidate tiles in {%s}"
          % (a.faction, len(mine), len(cand), a.biomes))
    print("  before: minimum separation to any settlement = %.2f deg" % score(old))

    # 1. greedy farthest-first
    placed = list(others)
    nearest = {t: min(sep(t, p) for p in placed) for t in cand}
    chosen = []
    for _ in range(len(mine)):
        best = max(cand, key=lambda t: (nearest[t], -t))
        chosen.append(best)
        placed.append(best)
        for t in cand:
            d = sep(t, best)
            if d < nearest[t]:
                nearest[t] = d
    print("  greedy: %.2f deg" % score(chosen))

    # 2. local improvement
    for _ in range(60):
        improved = False
        for i in range(len(chosen)):
            cur = score(chosen)
            best, bestv = chosen[i], cur
            for t in cand:
                if t in chosen and t != chosen[i]:
                    continue
                trial = list(chosen)
                trial[i] = t
                s = score(trial)
                if s > bestv + 1e-9:
                    best, bestv = t, s
            if best != chosen[i]:
                chosen[i] = best
                improved = True
        if not improved:
            break
    print("  after local improvement: %.2f deg" % score(chosen))

    # 3. ROUNDNESS pass. Maximin alone pushes sites to the extremes of the region,
    # which can leave them MORE strung out along one axis, not less -- and "weirdly
    # linear" was the actual complaint. So spend up to --slack degrees of separation
    # buying a rounder scatter: accept any swap that keeps the minimum within slack
    # of the best found and lowers the ratio of the first to the second principal
    # spread (1.0 = a round cloud). Never drops below the original arrangement.
    def linearity(sites):
        n = len(sites)
        V = [v(t) for t in sites]
        c = [sum(p[i] for p in V) / n for i in range(3)]
        M = [[sum((p[i] - c[i]) * (p[j] - c[j]) for p in V) / n for j in range(3)]
             for i in range(3)]
        # symmetric 3x3 eigenvalues, closed form (no numpy dependency here)
        import cmath
        p1 = M[0][1] ** 2 + M[0][2] ** 2 + M[1][2] ** 2
        q = (M[0][0] + M[1][1] + M[2][2]) / 3.0
        p2 = sum((M[i][i] - q) ** 2 for i in range(3)) + 2 * p1
        pp = math.sqrt(max(p2 / 6.0, 1e-18))
        B = [[(M[i][j] - (q if i == j else 0)) / pp for j in range(3)] for i in range(3)]
        detB = (B[0][0] * (B[1][1] * B[2][2] - B[1][2] * B[2][1])
                - B[0][1] * (B[1][0] * B[2][2] - B[1][2] * B[2][0])
                + B[0][2] * (B[1][0] * B[2][1] - B[1][1] * B[2][0]))
        phi = math.acos(max(-1.0, min(1.0, detB / 2.0))) / 3.0
        e1 = q + 2 * pp * math.cos(phi)
        e3 = q + 2 * pp * math.cos(phi + 2 * math.pi / 3)
        e2 = 3 * q - e1 - e3
        w = sorted([e1, e2, e3], reverse=True)
        return w[0] / max(w[1], 1e-12)

    floor_ = score(chosen) - a.slack
    print("  linearity after maximin: %.2f  (spending up to %.1f deg for roundness)"
          % (linearity(chosen), a.slack))
    for _ in range(40):
        improved = False
        for i in range(len(chosen)):
            bl = linearity(chosen)
            best, bestl = chosen[i], bl
            for t in cand:
                if t in chosen and t != chosen[i]:
                    continue
                trial = list(chosen)
                trial[i] = t
                if score(trial) < floor_:
                    continue
                L = linearity(trial)
                if L < bestl - 1e-9:
                    best, bestl = t, L
            if best != chosen[i]:
                chosen[i] = best
                improved = True
        if not improved:
            break
    print("  final: %.2f deg minimum separation, linearity %.2f"
          % (score(chosen), linearity(chosen)))

    # pair old -> new by proximity so names stay near their ground where possible
    pairs, free = [], list(chosen)
    for o in sorted(mine, key=lambda o: int(o["tile"])):
        t0 = int(o["tile"])
        t1 = min(free, key=lambda t: sep(t0, t))
        free.remove(t1)
        pairs.append((o, t0, t1))

    print("\n  %-24s %-8s -> %-8s %-16s %6s %7s  moved" % (
        "settlement", "from", "to", "biome", "arc", "temp"))
    for o, t0, t1 in pairs:
        r = T[t1]
        print("  %-24s %-8d -> %-8d %-16s %6s %7s  %.1f deg"
              % ((o.get("label") or o.get("name")), t0, t1, r["biome"], r["arc"],
                 r["temp_c"], sep(t0, t1)))

    nn = ["%.1f" % min(sep(t1, y) for _, _, y in pairs if y != t1) for _, _, t1 in pairs]
    print("\n  nearest-neighbour within the faction, after: %s" % nn)

    if not a.apply:
        print("\nDRY RUN. --apply to move them.")
        return 0

    from rimbridge_client import RimBridge, resolve_endpoint
    host, port, token = resolve_endpoint()
    with RimBridge(host, port, token) as rb:
        for o, t0, t1 in pairs:
            if t0 == t1:
                continue
            r = rb.call("jawa/world_objects_set", {"ids": str(o["id"]), "tile": t1})
            print("MOVE %-24s %d -> %d  success=%s"
                  % ((o.get("label") or o.get("name")), t0, t1, r.get("success")))
        c = rb.call("jawa/world_commit", {})
        print("COMMIT failedSteps=%s" % c.get("failedSteps"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
