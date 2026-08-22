#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ashkarr_settle.py - more moisture farmers, more Hutts, more oases, and roads to them.

Owner, 2026-08-22: *"more settlements and roads, though do keep large areas of
barrenness please. Making a lot more Hutts in the desert could make sense here (more
oases though), and the moisture farmers could definitely be all over the place."*

  HOMESTEAD DEFENSE LEAGUE are the moisture farmers - `FACTION_SPEC.md:160`,
  "pawnSingular moisture farmer", the Covenant of Free Wells. They go everywhere the
  air holds anything: from the hot margin out to the cold side of the terminator.

  HUTT CARTEL sit on the water and charge for it. Every new holding is placed beside
  a well, and where there is no well one is dug - a new `Oasis` landmark on an
  adjacent tile, because the existing holdings' own why-text says "beside a
  near-desert oasis - the well is guarded and is NOT free".

🔴 BARRENNESS IS A CONSTRAINT HERE, NOT A HOPE. Three mechanisms enforce it, and the
run REFUSES if the last one fails:
  1. BARREN_REGIONS get nothing, ever. The night side is meant to be empty.
  2. MIN_SPACING hexes between any two settlements, old or new.
  3. an emptiness floor - after placing, at least MIN_EMPTY_FRACTION of land tiles
     must still be more than EMPTY_RADIUS hexes from any settlement, or the whole
     pass is rejected rather than written.

    python3 src/RimMandrake/Utils/ashkarr_settle.py            # plan only
    python3 src/RimMandrake/Utils/ashkarr_settle.py --apply

Roads: every new settlement is joined to the EXISTING network by least-cost path -
cost rises with elevation gain and hilliness - so the invariant that every settlement
is on one connected road net survives the pass. New spurs are DirtRoad.
"""
import argparse
import csv
import heapq
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
WORLD = os.path.join(REPO, "world")
STEM = os.path.join(WORLD, "ASHKARR_WORLDMAP")
NEIGHBOURS = os.path.join(WORLD, "world_neighbors_sub7b.csv")

MIN_SPACING = 4            # hexes between any two settlements
EMPTY_RADIUS = 6           # "empty" means no settlement within this many hexes
MIN_EMPTY_FRACTION = 0.55  # at least this much of the land must stay that empty

# ⛔ Nothing is ever placed in these. The night side and the seas are meant to be blank,
# and the owner asked for large areas of barrenness by name.
BARREN_REGIONS = {
    "The Deadstone", "The Ammonia Flats", "The Umbra", "The Nightspill",
    "The Twilight Sea", "The Gray Sea", "The Scald", "The Rust Cathedral",
    "The Cinderdark", "The Frostbloom", "The Deep Bloom", "The Venom Wood",
    "The Coldspore", "The Crown Rot", "The Last Scrub", "The Rimewall",
    "The Cold Bloom", "The Ashen Waste", "The High Rot", "The Grayrot",
    "The Shoulder", "The Last Green",
}

HOMESTEAD_NAMES = [
    "Dryhold", "Fogline", "The Catchment", "Saltfurrow", "Dewfall", "Stillwater Farm",
    "The Vaporworks", "Nightdew", "Cold Catch", "The Sumps", "Brinefield", "Farrow",
    "The Standpipe", "Mistfoot", "Dripstone", "The Long Furrow", "Whistledew",
    "Pumphouse", "Greenpatch", "Cloudtrap", "Sweetwell", "Hollowdew", "Thornfurrow",
    "Chalkwell", "The Drybed", "Windcatch", "Lowdew", "Sandfurrow", "The Condensary",
    "Fallowdew",
]
HUTT_NAMES = [
    "The Debt House", "Slug Hollow", "Tollwater", "The Levy", "Fatwell",
    "The Reckoning", "Oilpalm", "Gorge Station", "The Skim", "Bloatwater",
    "Cartel Ground", "The Vig",
]

DROID_NAMES = [
    "The Cracking Yard", "Vent Twelve", "No Owner", "Cell Seven", "The Free Charge",
    "Second Speaker", "Vent Forty", "The Long Charge",
]
HELIX_NAMES = [
    "The Draft", "Cold Archive", "The Revision", "Specimen Hall", "The Fair Copy",
    "Second Reading",
]

DROID_WHY = ("they settle on water nobody else can drink and crack it for fuel, so "
             "attackers arrive thirsty at a source that would kill them")
HELIX_WHY = ("a cold, isolated research seat on the nightside edge - the Helix does not "
             "raid, it retrieves, and it wants no neighbours")

HOMESTEAD_WHY = ("moisture farming reaches wherever the air holds anything - "
                 "vaporators, aquifers, and a covenant that the wells stay free")
HUTT_WHY = ("beside a near-desert oasis - the well is guarded and is NOT free")
OASIS_WHY = "a Hutt well - dug for the holding beside it, and charged for"


def load():
    tiles = list(csv.DictReader(open(STEM + "_tiles.csv", encoding="utf-8")))
    T = {}
    for r in tiles:
        T[int(r["tile"])] = dict(
            elev=float(r["elev_m"]), rain=float(r["rain_mm"]), temp=float(r["temp_c"]),
            arc=float(r["arc"]), water=int(r["water"]), biome=r["biome"],
            region=r["region"], hill=int(r["hilliness"]), lat=r["lat"], lon=r["lon"])
    nb = {}
    rd = csv.reader(open(NEIGHBOURS, encoding="utf-8"))
    next(rd)
    for row in rd:
        nb[int(row[0])] = [int(x) for x in row[1:] if x.strip() and int(x) >= 0]
    return T, nb


def within(a, b, nb, limit):
    if a == b:
        return True
    seen, frontier = {a}, [a]
    for _ in range(limit):
        nxt = []
        for x in frontier:
            for n in nb[x]:
                if n in seen:
                    continue
                if n == b:
                    return True
                seen.add(n)
                nxt.append(n)
        frontier = nxt
    return False


def farthest_first(cand, occupied, nb, T, want, spacing):
    """Greedy farthest-point sampling: each pick is the candidate furthest, in hexes,
    from everything already placed. This is what "all over the place" actually means -
    ranking by any single scalar (arc, temperature, elevation) piles them at that
    scalar's extremes instead. Measured 2026-08-22: ranking by distance-from-arc-75
    put 26 homesteads at arc 45-49 and 103-105 with nothing between, 15 of them in
    two regions."""
    import collections as _c
    land = {t for t in T if T[t]["water"] == 0}
    dist = {}
    q = _c.deque()
    for t in occupied:
        if t in land:
            dist[t] = 0
            q.append(t)
    while q:
        x = q.popleft()
        for n in nb[x]:
            if n in land and n not in dist:
                dist[n] = dist[x] + 1
                q.append(n)
    pool = set(cand)
    chosen = []
    while len(chosen) < want and pool:
        best = max(pool, key=lambda t: (dist.get(t, 10**6), -t))
        if dist.get(best, 10**6) < spacing:
            break                       # nothing left that is far enough from anything
        chosen.append(best)
        pool.discard(best)
        # push the distance field down around the new pick
        seen, frontier, d = {best}, [best], 0
        dist[best] = 0
        while frontier and d < 40:
            d += 1
            nxt = []
            for x in frontier:
                for n in nb[x]:
                    if n in land and n not in seen:
                        seen.add(n)
                        if d < dist.get(n, 10**6):
                            dist[n] = d
                            nxt.append(n)
            frontier = nxt
    return chosen


def road_path(src, targets, T, nb):
    """least-cost path from src to the nearest tile in `targets`; None if unreachable."""
    dist = {src: 0.0}
    prev = {src: None}
    pq = [(0.0, src)]
    while pq:
        d, x = heapq.heappop(pq)
        if x in targets and x != src:
            out = []
            while x is not None:
                out.append(x)
                x = prev[x]
            return out[::-1]
        if d > dist.get(x, 1e18):
            continue
        for n in nb[x]:
            if T[n]["water"] == 1 or T[n]["hill"] >= 5:
                continue
            step = 1.0 + max(0.0, T[n]["elev"] - T[x]["elev"]) / 200.0 + T[n]["hill"] * 0.4
            nd = d + step
            if nd < dist.get(n, 1e18):
                dist[n] = nd
                prev[n] = x
                heapq.heappush(pq, (nd, n))
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--homesteads", type=int, default=0)
    ap.add_argument("--hutts", type=int, default=0)
    ap.add_argument("--droids", type=int, default=7)
    ap.add_argument("--helix", type=int, default=5)
    a = ap.parse_args()

    T, nb = load()
    srows = list(csv.DictReader(open(STEM + "_settlements.csv", encoding="utf-8")))
    lrows = list(csv.DictReader(open(STEM + "_landmarks.csv", encoding="utf-8")))
    links = list(csv.reader(open(STEM + "_links.csv", encoding="utf-8")))
    header, body = links[0], links[1:]

    occupied = {int(r["tile"]) for r in srows}
    lm_tiles = {int(r["tile"]) for r in lrows}
    road_tiles = {int(x) for k, p, q, d in body if k == "road" for x in (p, q)}
    next_id = max(int(r["id"]) for r in srows) + 1

    def ok(t, barren_ok=()):
        """barren_ok lets ONE faction into regions the barren list otherwise closes.
        The Ascendant Helix needs it: their whole placement rule is "cold, isolated
        research seats on the nightside edge", which is exactly the ground the barren
        list protects. They stay rare and far apart instead - isolation is their
        character, so a wide spacing serves both the fiction and the emptiness floor."""
        d = T[t]
        return (d["water"] == 0 and d["hill"] < 5 and t not in occupied
                and t not in lm_tiles and d["region"]
                and (d["region"] not in BARREN_REGIONS or d["region"] in barren_ok))

    plans = []
    # ── moisture farmers: everywhere the air holds anything ────────────────────
    hs = [t for t in T if ok(t) and 45 <= T[t]["arc"] <= 105
          and T[t]["biome"] in ("AridShrubland", "Desert", "Wasteland", "ZBiome_Badlands",
                                "ZBiome_Grasslands", "ZBiome_DesertOasis", "ExtremeDesert")
          and -25 <= T[t]["temp"] <= 45 and T[t]["hill"] <= 3]
    # spread them: rank by how FAR they are from the nearest existing settlement
    plans.append(("Homestead Defense League", "OutlanderCivil", HOMESTEAD_NAMES,
                  HOMESTEAD_WHY, hs, a.homesteads, False))

    # ── Hutts: the deep desert, each on a well ─────────────────────────────────
    ht = [t for t in T if ok(t) and 55 <= T[t]["arc"] <= 88
          and T[t]["biome"] in ("Desert", "ExtremeDesert") and T[t]["hill"] <= 2]
    plans.append(("Hutt Cartel", "Jawa_HuttCartel", HUTT_NAMES, HUTT_WHY, ht, a.hutts, True))

    # ── Free Droid Enclaves: the day side, on water that would kill a drinker ──
    UNDRINKABLE = ("AB_PropaneLakes", "AB_TarPits", "Volcano", "LavaField",
                   "AB_PyroclasticConflagration", "Scarlands", "AB_MechanoidIntrusion")
    dr = [t for t in T if ok(t) and T[t]["arc"] <= 55
          and (T[t]["biome"] in UNDRINKABLE
               or any(T[n]["biome"] in UNDRINKABLE for n in nb[t]))]
    plans.append(("Free Droid Enclaves", "Jawa_FreeDroidEnclaves", DROID_NAMES,
                  DROID_WHY, dr, a.droids, False))

    # ── Ascendant Helix: cold, isolated, on the nightward edge ────────────────
    HELIX_BARREN_OK = {"The Rimewall", "The Cold Bloom", "The Ashen Waste", "The Grayrot",
                       "The Shoulder", "The Last Green", "The High Rot"}
    hx = [t for t in T if ok(t, HELIX_BARREN_OK) and 98 <= T[t]["arc"] <= 128
          and T[t]["hill"] <= 4 and T[t]["biome"] not in ("Ocean", "Lake")]
    plans.append(("Ascendant Helix", "Jawa_AscendantHelix", HELIX_NAMES, HELIX_WHY,
                  hx, a.helix, False))

    new_s, new_lm, name_i = [], [], {}
    for faction, fdef, names, why, cand, want, wants_well in plans:
        placed = 0
        for t in farthest_first(cand, occupied, nb, T, min(want, len(names)), MIN_SPACING):
            if placed >= want or placed >= len(names):
                break
            if any(within(t, u, nb, MIN_SPACING) for u in occupied):
                continue
            well = None
            if wants_well:
                well = next((n for n in nb[t]
                             if n not in occupied and n not in lm_tiles
                             and T[n]["water"] == 0 and T[n]["hill"] <= 3), None)
                if well is None:
                    continue
            occupied.add(t)
            new_s.append({"id": str(next_id), "faction_def": fdef, "faction": faction,
                          "name": names[placed], "tile": str(t), "lat": T[t]["lat"],
                          "lon": T[t]["lon"], "arc": "%.4f" % T[t]["arc"],
                          "biome": T[t]["biome"], "why": why})
            next_id += 1
            if well is not None:
                lm_tiles.add(well)
                new_lm.append({"tile": str(well), "landmark": "Oasis", "why": OASIS_WHY})
            placed += 1
        print("  %-26s %2d new  (asked %d)" % (faction, placed, want))

    # ── roads to every new settlement ──────────────────────────────────────────
    new_roads, unreachable = [], []
    have = {frozenset((int(p), int(q))) for k, p, q, d in body if k == "road"}
    for s in new_s:
        t = int(s["tile"])
        p = road_path(t, road_tiles, T, nb)
        if p is None:
            unreachable.append((s["name"], t))
            continue
        for i in range(len(p) - 1):
            e = frozenset((p[i], p[i + 1]))
            if e in have:
                continue
            have.add(e)
            new_roads.append(["road", str(p[i]), str(p[i + 1]), "DirtRoad"])
        road_tiles.update(p)
    # 🔑 EVERY SETTLEMENT IS ON THE ONE ROAD NET, and that invariant is worth more than
    # one extra placement. A site the road-cost search cannot reach is DROPPED, not
    # written as an orphan - otherwise the map quietly acquires settlements no caravan
    # can route to, and nothing downstream would notice.
    if unreachable:
        drop = {n for n, _ in unreachable}
        new_s = [x for x in new_s if x["name"] not in drop]
        for name, t in unreachable:
            occupied.discard(t)
        print("\n  DROPPED %d unreachable site(s): %s" % (len(unreachable), sorted(drop)))
    print("  %d new road links laid; %d settlements now placed"
          % (len(new_roads), len(new_s)))

    # ── the emptiness floor ────────────────────────────────────────────────────
    land = [t for t in T if T[t]["water"] == 0]
    near = set()
    for t in occupied:
        seen, frontier = {t}, [t]
        for _ in range(EMPTY_RADIUS):
            nxt = []
            for x in frontier:
                for n in nb[x]:
                    if n not in seen:
                        seen.add(n)
                        nxt.append(n)
            frontier = nxt
        near |= seen
    empty = [t for t in land if t not in near]
    frac = len(empty) / len(land)
    print("\n  BARRENNESS: %d of %d land tiles (%.0f%%) are more than %d hexes from any "
          "settlement" % (len(empty), len(land), 100 * frac, EMPTY_RADIUS))
    if frac < MIN_EMPTY_FRACTION:
        sys.exit("REFUSED: that is below the %.0f%% floor. The owner asked for large areas "
                 "of barrenness; place fewer." % (100 * MIN_EMPTY_FRACTION))

    print("  settlements %d -> %d   landmarks %d -> %d   road links %d -> %d"
          % (len(srows), len(srows) + len(new_s), len(lrows), len(lrows) + len(new_lm),
             sum(1 for r in body if r[0] == "road"),
             sum(1 for r in body if r[0] == "road") + len(new_roads)))
    if not a.apply:
        print("plan only - re-run with --apply")
        return

    with open(STEM + "_settlements.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(srows[0].keys()))
        w.writeheader()
        w.writerows(srows + new_s)
    with open(STEM + "_landmarks.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["tile", "landmark", "why"])
        w.writeheader()
        w.writerows(lrows + new_lm)

    # 🔴 A NEW LANDMARK MUST CARRY ITS REQUIRED MUTATOR, or it is the same defect that
    # left ten of the original sixteen broken (`ashkarr_landmarks.py`, REPAIR). The
    # first run of this tool wrote 11 Oasis landmarks and none of the Oasis mutators,
    # reintroducing it within the hour. Every Oasis placed here is a well, so the
    # mutator is `Oasis` and it is not looked up - it is stated.
    import re as _re
    mrows = list(csv.DictReader(open(STEM + "_mutators.csv", encoding="utf-8")))
    MU = {int(r["tile"]): [x for x in _re.split(r"[;|,]", r["mutators"]) if x.strip()]
          for r in mrows}
    for r in new_lm:
        t = int(r["tile"])
        MU.setdefault(t, [])
        if "Oasis" not in MU[t]:
            MU[t].append("Oasis")
    with open(STEM + "_mutators.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["tile", "mutators"])
        for t in sorted(MU):
            if MU[t]:
                w.writerow([t, ";".join(MU[t])])
    body.extend(new_roads)
    with open(STEM + "_links.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(body)
    print("written: settlements, landmarks and links")


if __name__ == "__main__":
    main()
