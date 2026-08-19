#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ashkarr_settle.py - who lives where on Ash'karr, and the roads between them.

🔴 PLACEMENT IS LORE, NOT HABITABILITY. Siting settlements by "where is it nicest"
puts all forty on the terminator ring, because that is where the water is - the
2026-08-17 run did exactly that and contradicted the faction plan. So every holding
below is placed by a ZONE that encodes WHY that faction is there, and habitability
only chooses between tiles inside the zone.

🔑 SMALL ZONES ARE FILLED FIRST. Filling in size order starved the Geonosians and the
Ascendant Helix to zero settlements on 2026-08-17. The PLAN is ordered, and the order
is priority.

Positions are (arc, bearing): arc = degrees from the substellar point, bearing 0 =
the GRAY flank (downwind), 180 = the TWILIGHT flank.
"""
import heapq
import math
import os
import sys
from collections import defaultdict, deque

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

MIN_SPACING = 3          # tiles between any two holdings


# ===========================================================================
# THE PLAN. Counts and reasons come from tidally_locked_world.md's arc-aware
# faction table (which explicitly SUPERSEDES faction_world_spec.md section 4 -
# that file is still written in latitude bands and was never rewritten).
# Order is PRIORITY: the small, story-critical zones are filled first, because
# filling in size order starved the Geonosians and the Ascendant Helix to zero
# on 2026-08-17.
# ===========================================================================
def PLAN(s):
    """[(factionDef, display name, boolean tile mask, why it is there), ...]"""
    A, off = s.arc, s.off
    B = s.biome
    isB = lambda names: np.array([b in names for b in B])
    P = []

    def add(fac, names, mask, why):
        for nm in names:
            P.append((fac, nm, mask, why))

    # --- 3 Empire. "Dead centre of the dayside. No water, volcanoes, mountains."
    # Owner 2026-08-18: "The Empire's few outposts locking down major areas."
    # Nothing in the record says "lock down"; the docs say roads, STRATEGIC PASSES
    # and the spaceport - so each seat is put on a choke point.
    add("Empire", ["Sunspire"], (A > 8) & (A < 26) & (s.slope > 120),
        "the planetary seat and spaceport, on the substellar plateau's rim")
    add("Empire", ["Oxalate Watch"], (s.d_scald > 12) & (s.d_scald < 20) & (off(185) < 40),
        "the Scald Gate - the one breach in the Spine, so the crater is held")
    add("Empire", ["Ashgarrison"], (A > 30) & (A < 56) & (off(0) < 22) & (s.slope > 150),
        "the Fall Line pass, the road off the plateau onto the Gray flank")

    # --- 5 Geonosian Foundry Hive, in TWO clusters (FACTION_SPEC.md ruling)
    add("Jawa_GeonosianFoundryHive", ["The Unfinished Work", "Oxide Deep"],
        (A > 40) & (A < 64) & (off(350) < 26) & isB(("Wasteland", "ZBiome_Badlands",
                                                     "Desert", "AB_GallatrossGraveyard")),
        "the ore seams - the collapsed silicax oxalate holdings the Jawas robbed")
    add("Jawa_GeonosianFoundryHive", ["The Godmouth", "Founder's Kiln", "Hollow Nave"],
        (A < 24) & isB(("ExtremeDesert", "Scarlands", "AB_MechanoidIntrusion")),
        "subterranean dayside rock, beside the Rust Cathedral they worship")

    # --- 3 Free Droid Enclaves: volcanic springs, plus the ruled plateau presence
    add("Jawa_FreeDroidEnclaves", ["The Trade Socket", "Vent Nine"],
        (A > 16) & (A < 44) & (s.volcanic | (s.slope > 260)) & (off(185) < 80),
        "low mountains with poisonous volcanic springs - water nobody else can drink")
    add("Jawa_FreeDroidEnclaves", ["No Master"],
        (A < 20) & isB(("AB_MechanoidIntrusion", "Scarlands", "ExtremeDesert")),
        "the Rust Cathedral is sacred to them; they keep a seat beside it")

    # --- 3 Ascendant Helix. "Isolated, cold - nightside edge." Near the strange
    #     biomes, not near the people (hydrology_and_fire_ecology R-H8).
    add("Jawa_AscendantHelix", ["Helix Landing", "The Coil", "Quiet Lab"],
        (A > 104) & (A < 138) & ~isB(("AB_PropaneLakes",)),
        "cold, isolated research seats on the nightside edge, next to what is strange")

    # --- 4 Blackstar Company. "Everywhere; they follow the money."
    add("AM_EnemyPirate", ["Blackstar Field", "The Contract Camp", "Toll Rock",
                           "Hardpan Yard"],
        (A > 24) & (A < 96) & isB(("Desert", "ZBiome_Badlands", "AridShrubland",
                                   "Wasteland")),
        "road junctions, ruins and rough outposts - wherever the traffic is")

    # --- 4 Wildsteam Clan. "The rivers - the wild jungles and poisonous marshes."
    add("Jawa_WildsteamClan", ["Steamreach", "Rego"],
        s.river & (s.d_scald < 44),
        "the Scald's rivers, where the only true jungle on the planet grows")
    add("Jawa_WildsteamClan", ["Marrowmarsh", "Sporefall"],
        (A > 80) & (A < 106) & isB(("AB_MycoticJungle", "PoisonForest",
                                    "AB_MiasmicMangrove", "BMT_FungalForest")),
        "the meridian's poison marshes - the other kind of wet, and nobody else wants it")

    # --- 5 Deepwater Compact. "The seas of the twilight band."
    #     CHECK.md: at least TWO on the Scald despite the Empire.
    add("Jawa_DeepwaterCompact", ["Butora", "Anchor Deep"],
        s.coast & (s.d_scald < 22),
        "the Scald shore - fresh water in the hottest place, held against the Empire")
    add("Jawa_DeepwaterCompact", ["Deepwater Hold", "Coldquay"],
        s.coast & (s.d_twilight < 26),
        "the Twilight Sea, the largest standing water on Ash'karr")
    add("Jawa_DeepwaterCompact", ["Tidewatch"], s.coast & (s.d_gray < 26),
        "the Grey Sea, salt-encrusted and shrinking - they hold it anyway")

    # --- 8 Hutt Cartel. BESIDE an oasis, never on it.
    add("Jawa_HuttCartel",
        ["Spicehead", "Sarlacc Ground", "Itunt", "The Yards", "Wellsong",
         "The Tollgate", "Bantha Cross", "Greasepalm"],
        s.by_oasis & (A > 34) & (A < 86),
        "beside a near-desert oasis - the well is guarded and is NOT the town tile")

    # --- 8 Junkers. 🔴 Owner's ruling 2026-08-18, and it is NOT in the record:
    #     the terminator bending into the dark where the air is still warm, plus the
    #     old mining and scavenging fields. The docs only ever said "wreck fields,
    #     wherever things fell."
    add("Jawa_Junkers",
        ["The Fuel Works", "Cryohaul", "Ammonia Landing", "Warmside Camp",
         "Bonepick Station"],
        (A > 96) & (A < 132) & (off(0) < 62),
        "past the terminator on the warm downwind flank, scavenging the cold swirl")
    add("Jawa_Junkers", ["Tailings End", "The Slagfield", "The Claim Jump"],
        (A > 38) & (A < 70) & (off(350) < 40) & isB(("Wasteland", "ZBiome_Badlands",
                                                     "AB_GallatrossGraveyard", "Desert")),
        "squatting the worked-out mining fields the Geonosians did not finish")

    # --- 7 Jawa Trade Moot. Circuits, not a blob. One node on the old mine.
    add("Jawa_IndigenousTribes", ["The Ore Moot"],
        (A > 42) & (A < 62) & (off(350) < 30),
        "the crawler circuit's anchor: the mine the sandcrawlers were stolen from")
    add("Jawa_IndigenousTribes",
        ["Crawler Ground", "Ridge Cache", "Wreck Circuit", "Sandmoot",
         "The Bartering Rock", "Tin Camp"],
        (A > 34) & (A < 82) & isB(("Desert", "ZBiome_Badlands", "ExtremeDesert",
                                   "AridShrubland", "Wasteland")),
        "canyon fortresses and crawler circuit nodes across the near-desert")

    # --- 9 Deep Desert Tribes. Canyons, caves, ridges. NEVER water tiles.
    add("TribeCivil",
        ["Duneward", "Stone Moot", "Redscarp", "The Dry Moot", "Barno",
         "The Long Camp", "Ashfoot", "Knife Canyon", "The Blind Wells"],
        (A > 28) & (A < 80) & ~s.river & ~s.coast
        & isB(("Desert", "ExtremeDesert", "ZBiome_Badlands", "ZBiome_Grasslands")),
        "the near-desert: canyons, caves and isolated ridges, and never a water tile")

    # --- 13 Homestead Defense League. The arable margin of the terminator.
    add("OutlanderCivil",
        ["Dewhome", "Condenser Flats", "Bell Cistern", "Mistcatch", "Stillmarket",
         "Rainshadow", "Vaporfall", "Longfurrow", "Cistern Hill", "Greenline",
         "The Dripworks", "Marrowfield", "Aquifer Station"],
        (A > 64) & (A < 102) & isB(("AridShrubland", "ZBiome_DesertOasis",
                                    "ZBiome_Grasslands", "Desert", "Wasteland")),
        "the arable margin of the terminator - vaporators, aquifers, and no source")
    return P


class Site(object):
    """The world as a settler sees it: the fields a zone predicate may test."""

    def __init__(self, w):
        self.w = w
        n = w["n"]
        self.arc, self.bear = w["arc"], w["bear"]
        self.elev, self.sea, self.biome = w["elev"], w["sea"], w["biome"]
        self.acc, self.chan, self.nbl = w["acc"], w["chan"], w["nbl"]
        self.coast = np.array([(not w["sea"][t]) and any(w["sea"][u] for u in w["nbl"][t])
                               for t in range(n)])
        self.river = np.array([w["riparian"][t] <= 1 for t in range(n)])
        self.oasis = np.array([b in ("ZBiome_DesertOasis", "AB_FeraliskInfestedJungle",
                                     "AB_MiasmicMangrove") for b in w["biome"]])
        # "beside an oasis, never on it" - the Hutt rule, made a field
        self.by_oasis = np.zeros(n, bool)
        for t in np.nonzero(self.oasis)[0]:
            for u in w["nbl"][t]:
                if not self.oasis[u] and not w["sea"][u]:
                    self.by_oasis[u] = True
        self.slope = np.array([max((abs(self.elev[t] - self.elev[u])
                                    for u in w["nbl"][t]), default=0.0)
                               for t in range(n)])
        self.volcanic = np.array([b in ("Volcano", "LavaField",
                                        "AB_PyroclasticConflagration", "Scarlands")
                                  for b in w["biome"]])
        self.ruinfield = np.array([b in ("AB_MechanoidIntrusion", "Wasteland",
                                         "AB_GallatrossGraveyard") for b in w["biome"]])
        self.d_scald = w["d_scald"]
        self.d_twilight = w["d_twilight"]
        self.d_gray = w["d_gray"]

    def off(self, b0):
        return np.abs((self.bear - b0 + 180) % 360 - 180)

    def livable(self):
        """Nothing is sited in the sea, in lava, or where a colony cannot stand."""
        bad = ("Ocean", "LavaField", "AB_PyroclasticConflagration",
               "AB_GelatinousSuperorganism", "AB_PropaneLakes")
        return np.array([(not self.sea[t]) and self.biome[t] not in bad
                         and self.elev[t] < 2600 for t in range(len(self.arc))])


def place(w, plan, comfort_c=(6.0, 40.0)):
    """Run the PLAN. Returns [{faction, name, tile, zone}, ...].

    Each entry is (factionDef, display name, zone predicate, why). One holding per
    entry, so the order of the list IS the priority and a starved zone is visible.
    """
    s = Site(w)
    n = w["n"]
    ok = s.livable()
    taken = []
    out = []
    temp = np.interp(s.arc, [0, 30, 60, 90, 120, 150, 180],
                     [70, 58, 38, 14, -22, -58, -80]) - np.clip(s.elev, 0, None) / 1000 * 5.5
    lo, hi = comfort_c
    comfort = np.exp(-((temp - (lo + hi) / 2.0) / ((hi - lo) / 1.6)) ** 2)

    for fac, name, zone, why in plan:
        m = (zone if isinstance(zone, np.ndarray) else zone(s)) & ok
        if not m.any():
            out.append({"faction": fac, "name": name, "tile": None, "why": why})
            continue
        cand = np.nonzero(m)[0]
        if taken:
            keep = []
            for t in cand:
                if min(_hops(w, int(t), taken, MIN_SPACING)) >= MIN_SPACING:
                    keep.append(t)
            if keep:
                cand = np.array(keep)
        score = comfort[cand] + 0.30 * s.river[cand] + 0.22 * s.coast[cand]
        t = int(cand[int(np.argmax(score))])
        taken.append(t)
        out.append({"faction": fac, "name": name, "tile": t, "why": why})
    return out


def _hops(w, t, others, cap):
    """Graph distance from t to each of `others`, capped - cheap because cap is 4."""
    d = {t: 0}
    q = deque([t])
    while q:
        x = q.popleft()
        if d[x] >= cap:
            continue
        for u in w["nbl"][x]:
            if u not in d:
                d[u] = d[x] + 1
                q.append(u)
    return [d.get(o, cap) for o in others] or [cap]


# --------------------------------------------------------------------------
def roads(w, sites, road_hash):
    """Roads that serve the settlements, not a spider.

    A minimum spanning tree over the holdings, then shortcuts wherever the tree
    detour is more than 1.9x the direct cost - a pure MST leaves caravans crossing
    the planet to reach a neighbour. Cost is real terrain: mountains, the deep waste
    and the dark all cost, so a road bends the way a road does.
    """
    n, nbl, geo = w["n"], w["nbl"], w["geo"]
    live = [x["tile"] for x in sites if x["tile"] is not None]
    cost = (1.0 + np.clip(w["elev"], 0, None) / 700.0
            + 2.4 * (w["riparian"] <= 1)
            + np.clip((w["arc"] - 96.0) / 10.0, 0, 8)          # nobody builds into the dark
            + 1.6 * np.clip((34.0 - w["arc"]) / 20.0, 0, 3))   # nor across the Anvil
    cost[w["sea"]] = 1e6

    def dijkstra(src):
        dist = np.full(n, np.inf)
        prev = np.full(n, -1, np.int32)
        dist[src] = 0.0
        pq = [(0.0, src)]
        while pq:
            dd, t = heapq.heappop(pq)
            if dd > dist[t]:
                continue
            for u in nbl[t]:
                nd = dd + cost[u]
                if nd < dist[u]:
                    dist[u] = nd
                    prev[u] = t
                    heapq.heappush(pq, (nd, u))
        return dist, prev

    tables = {t: dijkstra(t) for t in live}
    pairs = []
    for i, a in enumerate(live):
        for b in live[i + 1:]:
            d = tables[a][0][b]
            if np.isfinite(d):
                pairs.append((float(d), a, b))
    pairs.sort()

    parent = {t: t for t in live}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    chosen, tree_cost = [], {}
    for d, a, b in pairs:                      # Kruskal
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
            chosen.append((a, b, d))
    for a, b, d in chosen:
        tree_cost[(min(a, b), max(a, b))] = d
    # shortcuts: a link the tree makes absurdly long
    adj = defaultdict(list)
    for a, b, d in chosen:
        adj[a].append((b, d))
        adj[b].append((a, d))
    for d, a, b in pairs:
        if (min(a, b), max(a, b)) in tree_cost:
            continue
        along = _tree_dist(adj, a, b)
        if along > 1.9 * d and d < np.median([p[0] for p in pairs]):
            chosen.append((a, b, d))
            tree_cost[(min(a, b), max(a, b))] = d
            adj[a].append((b, d))
            adj[b].append((a, d))

    edges = []
    for a, b, d in chosen:
        dist, prev = tables[a]
        if not np.isfinite(dist[b]):
            continue
        path, t = [], b
        while t != a and t >= 0:
            path.append(t)
            t = prev[t]
        path.append(a)
        grade = "StoneRoad" if len(path) <= 16 else "DirtRoad"
        for x, y in zip(path[:-1], path[1:]):
            edges.append((int(x), int(y), road_hash[grade]))
    return edges, len(chosen)


def _tree_dist(adj, a, b):
    dist = {a: 0.0}
    pq = [(0.0, a)]
    while pq:
        d, t = heapq.heappop(pq)
        if t == b:
            return d
        if d > dist.get(t, 1e18):
            continue
        for u, w_ in adj[t]:
            nd = d + w_
            if nd < dist.get(u, 1e18):
                dist[u] = nd
                heapq.heappush(pq, (nd, u))
    return 1e18
