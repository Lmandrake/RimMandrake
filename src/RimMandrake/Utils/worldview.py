#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""worldview.py - READ a RimWorld savegame and portray its PLANET.

The planet map, not the local tilemap: the hex grid, the biomes painted on it, the
rivers and roads threaded between tiles, the bodies of water, and the settlements
standing on them. Read-only - nothing in this file ever writes a save.

    python3 src/RimMandrake/Utils/worldview.py world/WORLDMAP_sub7b_source.rws
    ... --layer elevation --projection ortho --center 0,0
    ... --tile 4711 --tile 8003        # everything known about single tiles

It writes three things next to each other in `world/view/`:

    <save>.<layer>.<proj>.svg   the map - zoomable, every hex hoverable for its
                                tile id, biome, elevation, temperature, rainfall
    <save>.report.json          the same characterisation as data
    stdout                      the characterisation as prose

🔑 WHERE EACH THING COMES FROM, because they are four different storage shapes:

  biome/elevation/temp/rain/hilliness/swampiness   per-tile deflate arrays, via
        worldmap.WorldGrid, with ITS calibrated encodings (temp = (raw-3000)/10 and
        so on). Never re-derive those here.
  rivers and roads   NOT graphs and NOT per-tile: parallel per-ENTRY arrays of
        (origin tile int32, adjacency byte, def shortHash). One undirected edge
        stored ONCE, owned by the lower-index tile; the adjacency byte is that
        tile's index into the ENGINE's own neighbour order. Decoded and proved
        2026-08-18 (origin < target on 1.000 of 648 entries, reciprocity exactly
        0.000). worldgeom holds that ordering.
  settlements, landmarks, features   plain XML, via worldmap.WorldObjects.
  tile POSITIONS   are in neither - the engine rebuilds them from <subdivisions>.
        worldgeom reads them from a CSV dumped out of the live game.

⚠️ The biome shortHash table must come from a def dump of the SAME mod set as the
save, or a hash resolves to a DIFFERENT biome rather than failing. The report
prints `unresolved` - a non-empty list means the picture is lying to you.
"""
import argparse
import base64
import json
import math
import os
import re
import struct
import sys
import zlib
from collections import Counter, defaultdict, deque

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)

import worldgeom
from worldmap import WorldGrid, WorldObjects, DECODE, load_hash_table, DEFAULT_DUMP


# ==========================================================================
# 1. the link arrays - rivers and roads
# ==========================================================================
LINKS = {
    "river": ("tileRiverOrigins", "tileRiverAdjacency", "tileRiverDef", "RiverDef"),
    "road":  ("tileRoadOrigins",  "tileRoadAdjacency",  "tileRoadDef",  "RoadDef"),
}


def _inflate(b64):
    return zlib.decompress(base64.b64decode("".join(b64.split())), -15)


def read_links(grid, kind, dump_dir=DEFAULT_DUMP):
    """[(origin, target, defName, slot), ...] for rivers or roads.

    The adjacency byte is a slot into the origin tile's ENGINE neighbour order, so
    the target cannot be recovered without worldgeom. A slot pointing past the end
    of a pentagon's neighbour list is reported as a broken entry rather than
    silently wrapped."""
    o_name, a_name, d_name, def_type = LINKS[kind]
    text, lo, hi = grid.text, grid.surf_lo, grid.surf_hi

    def blob(name):
        tag = "<%sDeflate>" % name
        a = text.find(tag, lo, hi)
        if a < 0:
            return None
        b = text.find("</%sDeflate>" % name, a)
        return _inflate(text[a + len(tag):b])

    ob, ab, db = blob(o_name), blob(a_name), blob(d_name)
    if ob is None or ab is None or db is None:
        return [], []
    origins = list(struct.unpack("<%dI" % (len(ob) // 4), ob))
    slots = list(ab)
    hashes = list(struct.unpack("<%dH" % (len(db) // 2), db))
    names, _ = load_hash_table(def_type, dump_dir)

    geom = grid.geom
    good, broken = [], []
    for o, s, h in zip(origins, slots, hashes):
        ns = geom.neighbours(o)
        if s >= len(ns):
            broken.append({"origin": o, "slot": s, "def": names.get(h, "?%d" % h)})
            continue
        good.append((o, ns[s], names.get(h, "?%d" % h), s))
    return good, broken


def read_river_distances(grid):
    tag = "<tileRiverDistancesDeflate>"
    a = grid.text.find(tag, grid.surf_lo, grid.surf_hi)
    if a < 0:
        return None
    b = grid.text.find("</tileRiverDistancesDeflate>", a)
    return list(_inflate(grid.text[a + len(tag):b]))


# ==========================================================================
# 2. what counts as water
# ==========================================================================
def water_biomes(dump_dir=DEFAULT_DUMP):
    """Biome defNames the game itself treats as open water: impassable, and drawn
    with a water texture. Read off the defs so a modded ocean is included, plus the
    two named cases the rule alone would miss."""
    out = {"Ocean", "Lake", "SeaIce"}
    path = os.path.join(dump_dir, "BiomeDef.json")
    try:
        data = json.load(open(path, encoding="utf-8"))
    except Exception:
        return out
    defs = data if isinstance(data, list) else data.get("defs", data)
    for d in defs:
        f = d.get("fields") or {}
        tex = str(f.get("texture", ""))
        if f.get("impassable") and ("Water" in tex or "Ocean" in tex):
            out.add(d["defName"])
    return out


# ==========================================================================
# 3. the whole planet, read once
# ==========================================================================
class PlanetView(object):
    def __init__(self, save_path, dump_dir=DEFAULT_DUMP, extra_water=(), no_water=()):
        self.path = save_path
        self.grid = WorldGrid(save_path, dump_dir)
        self.grid.geom = worldgeom.Geometry(self.grid.tiles)
        self.geom = self.grid.geom
        self.objs = WorldObjects(save_path)
        self.n = self.grid.tiles

        self.biome = self.grid.biome_names()
        self.unresolved = self.grid.unresolved()
        self.elev = np.array([DECODE["tileElevation"][0](v)
                              for v in self.grid.arrays["tileElevation"]])
        self.temp = np.array([DECODE["tileTemperature"][0](v)
                              for v in self.grid.arrays["tileTemperature"]])
        self.rain = np.array([float(v) for v in self.grid.arrays["tileRainfall"]])
        self.hilly = np.array(self.grid.arrays.get("tileHilliness", [0] * self.n))
        self.swamp = np.array(self.grid.arrays.get("tileSwampiness", [0] * self.n)) / 255.0
        self.feature_idx = np.array(self.grid.arrays.get("tileFeature", [0xFFFF] * self.n))

        wb = (water_biomes(dump_dir) | set(extra_water)) - set(no_water)
        self.water_biome_set = wb
        self.is_water = np.array([b in wb for b in self.biome])

        self.rivers, self.rivers_broken = read_links(self.grid, "river", dump_dir)
        self.roads, self.roads_broken = read_links(self.grid, "road", dump_dir)
        self.river_dist = read_river_distances(self.grid)

        self.settlements = self.objs.settlements()
        self.landmarks = self.objs.landmarks()
        self.features = self.objs.features()
        self.factions = self._factions()
        self.info = self._info()
        self.other_objects = Counter(
            re.findall(r'<li Class="([^"]+)"', self._world_objects_text()))

    # -- header bits -------------------------------------------------------
    def _world_objects_text(self):
        t = self.objs.text
        i = t.find("<worldObjects>")
        return t[i:t.find("</worldObjects>", i)] if i >= 0 else ""

    def _info(self):
        # 🔴 The game's OWN <info> block comes first in the file and is a different
        # thing (play time, starting pawns). Anchor on <world> or every field
        # silently reads None.
        t = self.objs.text
        w = t.find("<world>")
        i = t.find("<info>", w if w >= 0 else 0)
        seg = t[i:t.find("</info>", i)] if i >= 0 else ""
        start = re.search(r"<startingTile>(-?\d+),", t)
        g = lambda tag, s=seg: (re.search(r"<%s>(.*?)</%s>" % (tag, tag), s, re.S)
                                or [None, None])[1]
        surf = self.grid.text[self.grid.surf_lo:self.grid.surf_hi]
        return {
            "name": g("name"),
            "seedString": g("seedString"),
            "planetCoverage": g("planetCoverage"),
            "overallRainfall": g("overallRainfall"),
            "overallTemperature": g("overallTemperature"),
            "pollution": g("pollution"),
            "gameVersion": g("gameVersion", t[:t.find("</meta>")]),
            "subdivisions": g("subdivisions", surf),
            "radius": g("radius", surf),
            "mods": len(re.findall(r"<li>", t[t.find("<modIds>"):t.find("</modIds>")])),
            "startingTile": int(start.group(1)) if start else None,
        }

    def _factions(self):
        """Index -> {def, name}. The Nth record IS Faction_N - the records carry no
        loadID, and the highest reference in the file matches the record count."""
        t = self.objs.text
        i = t.find("<allFactions>")
        if i < 0:
            return {}
        seg = t[i:t.find("</allFactions>", i)]
        out = {}
        for k, m in enumerate(re.finditer(r"<li>\s*<leader>.*?<def>(.*?)</def>\s*"
                                          r"<name>(.*?)</name>", seg, re.S)):
            out["Faction_%d" % k] = {"def": m.group(1), "name": m.group(2), "index": k}
        return out

    # -- derived ------------------------------------------------------------
    def components(self, mask):
        """Connected runs of True in mask, over the tile adjacency graph."""
        seen = np.zeros(self.n, dtype=bool)
        out = []
        for s in range(self.n):
            if seen[s] or not mask[s]:
                continue
            q, comp = deque([s]), []
            seen[s] = True
            while q:
                t = q.popleft()
                comp.append(t)
                for u in self.geom.neighbours(t):
                    if mask[u] and not seen[u]:
                        seen[u] = True
                        q.append(u)
            out.append(comp)
        out.sort(key=len, reverse=True)
        return out

    def link_components(self, links):
        """Connected networks of river or road edges -> [[(o,t,def), ...], ...]."""
        adj = defaultdict(list)
        for o, t, d, _ in links:
            adj[o].append((t, d))
            adj[t].append((o, d))
        seen, out = set(), []
        for s in adj:
            if s in seen:
                continue
            q, tiles, edges = deque([s]), [], set()
            seen.add(s)
            while q:
                a = q.popleft()
                tiles.append(a)
                for b, d in adj[a]:
                    edges.add((min(a, b), max(a, b), d))
                    if b not in seen:
                        seen.add(b)
                        q.append(b)
            out.append({"tiles": tiles, "edges": sorted(edges)})
        out.sort(key=lambda c: len(c["edges"]), reverse=True)
        return out

    def feature_name(self, idx):
        if idx == 0xFFFF or idx >= len(self.features):
            return None
        return self.features[idx]["name"]

    def coast_edges(self):
        """Shared hex edges where water meets land - the coastline, exactly."""
        out = []
        for t in range(self.n):
            ns = self.geom.neighbours(t)
            for k, u in enumerate(ns):
                if u > t and self.is_water[t] != self.is_water[u]:
                    out.append((t, k))
        return out


# ==========================================================================
# 4. the characterisation
# ==========================================================================
HILLINESS = {0: "Undefined", 1: "Flat", 2: "SmallHills", 3: "LargeHills",
             4: "Mountainous", 5: "Impassable"}


def characterise(pv):
    g, n = pv.geom, pv.n
    land = ~pv.is_water
    deg = Counter(len(g.neighbours(t)) for t in range(n))

    biome_cen = Counter(pv.biome)
    water_bodies = pv.components(pv.is_water)
    landmasses = pv.components(land)

    def body(comp, kind):
        feats = Counter(pv.feature_name(pv.feature_idx[t]) for t in comp)
        feats.pop(None, None)
        lat = float(np.mean([g.lat[t] for t in comp]))
        lon = float(np.degrees(np.arctan2(
            np.mean(np.sin(np.radians([g.lon[t] for t in comp]))),
            np.mean(np.cos(np.radians([g.lon[t] for t in comp]))))))
        return {"kind": kind, "tiles": len(comp), "pct": round(100.0 * len(comp) / n, 3),
                "centroid": [round(lat, 2), round(lon, 2)],
                "named": [k for k, _ in feats.most_common(3)],
                "biomes": dict(Counter(pv.biome[t] for t in comp).most_common(4))}

    rnets = pv.link_components(pv.rivers)
    dnets = pv.link_components(pv.roads)

    river_tiles = {t for o, u, _, _ in pv.rivers for t in (o, u)}
    mouths = sorted(t for t in river_tiles
                    if any(pv.is_water[u] for u in g.neighbours(t)))

    setl = []
    for s in pv.settlements:
        t = s["tile"]
        f = pv.factions.get(s["faction"], {})
        setl.append({
            "id": s["id"], "tile": t, "name": s["name"],
            "faction": f.get("name") or s["faction"], "factionDef": f.get("def"),
            "biome": pv.biome[t] if t < n else "?",
            "lat": round(float(g.lat[t]), 2), "lon": round(float(g.lon[t]), 2),
            "elevation_m": round(float(pv.elev[t]), 1),
            "temp_c": round(float(pv.temp[t]), 1),
            "rain_mm": round(float(pv.rain[t])),
            "hilliness": HILLINESS.get(int(pv.hilly[t]), str(pv.hilly[t])),
            "coastal": bool(any(pv.is_water[u] for u in g.neighbours(t))),
            "on_river": t in river_tiles,
            "on_road": t in {x for o, u, _, _ in pv.roads for x in (o, u)},
            "region": pv.feature_name(pv.feature_idx[t]),
        })
    setl.sort(key=lambda s: (s["faction"] or "", s["name"] or ""))

    stat = lambda a: {"min": round(float(a.min()), 1), "mean": round(float(a.mean()), 1),
                      "max": round(float(a.max()), 1)} if len(a) else None

    return {
        "save": os.path.basename(pv.path),
        "planet": dict(pv.info, tiles=n),
        "hexgrid": {
            "tiles": n,
            "degree_histogram": {str(k): v for k, v in sorted(deg.items())},
            "pentagons": deg.get(5, 0),
            "mean_tile_arc_deg": round(g.mean_tile_arc(), 4),
            "edges": len(g.edges()),
            "lat_range": [round(float(g.lat.min()), 2), round(float(g.lat.max()), 2)],
            "geometry_verified": deg.get(5, 0) == 12 and set(deg) <= {5, 6},
        },
        "biomes": {
            "unresolved_hashes": pv.unresolved,
            "distinct": len(biome_cen),
            "census": [{"biome": b, "tiles": c, "pct": round(100.0 * c / n, 3),
                        "water": b in pv.water_biome_set,
                        "temp_c": round(float(np.mean(pv.temp[[i for i in range(n)
                                                              if pv.biome[i] == b]])), 1)}
                       for b, c in biome_cen.most_common()],
        },
        "water": {
            "definition": "biome in %s" % sorted(pv.water_biome_set),
            "water_tiles": int(pv.is_water.sum()),
            "water_pct": round(100.0 * float(pv.is_water.sum()) / n, 2),
            "below_sea_level_tiles": int((pv.elev < 0).sum()),
            "coastline_edges": len(pv.coast_edges()),
            "bodies": [body(c, "water") for c in water_bodies[:12]],
            "body_count": len(water_bodies),
            "landmasses": [body(c, "land") for c in landmasses[:12]],
            "landmass_count": len(landmasses),
        },
        "terrain": {
            "elevation_m": stat(pv.elev), "elevation_land_m": stat(pv.elev[land]),
            "temperature_c": stat(pv.temp), "rainfall_mm": stat(pv.rain),
            "hilliness": {HILLINESS.get(int(k), str(k)): v
                          for k, v in sorted(Counter(pv.hilly.tolist()).items())},
            "swampiness_mean": round(float(pv.swamp.mean()), 3),
        },
        "rivers": {
            "edges": len(pv.rivers), "broken_entries": pv.rivers_broken,
            "by_def": dict(Counter(d for _, _, d, _ in pv.rivers).most_common()),
            "tiles_touched": len(river_tiles),
            "networks": len(rnets),
            "largest": [{"edges": len(c["edges"]), "tiles": len(c["tiles"]),
                         "defs": dict(Counter(d for _, _, d in c["edges"])),
                         "head": max(c["tiles"], key=lambda t: pv.elev[t]),
                         "head_elev_m": round(float(max(pv.elev[t] for t in c["tiles"])), 1),
                         "reaches_sea": any(t in mouths for t in c["tiles"])}
                        for c in rnets[:8]],
            "mouths": len(mouths),
        },
        "roads": {
            "edges": len(pv.roads), "broken_entries": pv.roads_broken,
            "by_def": dict(Counter(d for _, _, d, _ in pv.roads).most_common()),
            "tiles_touched": len({t for o, u, _, _ in pv.roads for t in (o, u)}),
            "networks": len(dnets),
            "largest": [{"edges": len(c["edges"]), "tiles": len(c["tiles"]),
                         "defs": dict(Counter(d for _, _, d in c["edges"])),
                         "settlements": sum(1 for s in pv.settlements
                                            if s["tile"] in set(c["tiles"]))}
                        for c in dnets[:8]],
        },
        "settlements": {
            "count": len(setl),
            "by_faction": dict(Counter(s["faction"] for s in setl).most_common()),
            "by_biome": dict(Counter(s["biome"] for s in setl).most_common()),
            "coastal": sum(1 for s in setl if s["coastal"]),
            "on_river": sum(1 for s in setl if s["on_river"]),
            "on_road": sum(1 for s in setl if s["on_road"]),
            "list": setl,
        },
        "landmarks": {"count": len(pv.landmarks),
                      "by_def": dict(Counter(m["def"] for m in pv.landmarks).most_common(20))},
        "regions": {"count": len(pv.features),
                    "by_def": dict(Counter(f["def"] for f in pv.features).most_common()),
                    "named": [{"name": f["name"], "def": f["def"],
                               "tiles": int((pv.feature_idx == f["index"]).sum())}
                              for f in pv.features]},
        "other_world_objects": dict(pv.other_objects),
    }


def print_report(r):
    p, w = r["planet"], r["water"]
    say = lambda s="": sys.stdout.write(s + "\n")
    say("=" * 74)
    say("PLANET  %s     seed %s     coverage %s" % (p.get("name"), p.get("seedString"),
                                                    p.get("planetCoverage")))
    say("        RimWorld %s · %s mods · subdivisions %s · rainfall x%s temp %s"
        % (p.get("gameVersion"), p.get("mods"), p.get("subdivisions"),
           p.get("overallRainfall"), p.get("overallTemperature")))
    h = r["hexgrid"]
    say("HEXGRID %d tiles, %d edges, %d pentagons, mean tile arc %.3f deg  [%s]"
        % (h["tiles"], h["edges"], h["pentagons"], h["mean_tile_arc_deg"],
           "geometry verified" if h["geometry_verified"] else "🔴 GEOMETRY SUSPECT"))
    say()
    b = r["biomes"]
    say("BIOMES  %d distinct%s" % (b["distinct"], "" if not b["unresolved_hashes"]
        else "   🔴 UNRESOLVED HASHES %s - the def dump does not match this save"
             % b["unresolved_hashes"][:8]))
    for row in b["census"][:18]:
        say("   %-34s %6d  %5.2f%%  %6.1fC %s"
            % (row["biome"], row["tiles"], row["pct"], row["temp_c"],
               "~water~" if row["water"] else ""))
    if len(b["census"]) > 18:
        say("   ... %d more" % (len(b["census"]) - 18))
    say()
    say("WATER   %d tiles (%.1f%%), %d bodies, %d coastline edges, %d tiles below 0 m"
        % (w["water_tiles"], w["water_pct"], w["body_count"], w["coastline_edges"],
           w["below_sea_level_tiles"]))
    for c in w["bodies"][:6]:
        say("   sea/lake  %6d tiles  centroid %7.2f,%8.2f  %s"
            % (c["tiles"], c["centroid"][0], c["centroid"][1],
               ", ".join(c["named"]) or "unnamed"))
    say("LAND    %d masses; largest:" % w["landmass_count"])
    for c in w["landmasses"][:5]:
        say("   land      %6d tiles  centroid %7.2f,%8.2f  %s"
            % (c["tiles"], c["centroid"][0], c["centroid"][1],
               ", ".join(c["named"]) or "unnamed"))
    say()
    t = r["terrain"]
    say("TERRAIN elevation %s m (land %s) · temp %s C · rain %s mm"
        % (t["elevation_m"], t["elevation_land_m"], t["temperature_c"], t["rainfall_mm"]))
    say("        hilliness %s" % t["hilliness"])
    say()
    rv = r["rivers"]
    say("RIVERS  %d edges over %d tiles in %d networks, %d reach the sea   %s"
        % (rv["edges"], rv["tiles_touched"], rv["networks"], rv["mouths"], rv["by_def"]))
    for c in rv["largest"][:5]:
        say("   network %3d edges  head tile %5d at %6.0f m  %s  %s"
            % (c["edges"], c["head"], c["head_elev_m"], c["defs"],
               "reaches sea" if c["reaches_sea"] else "endorheic"))
    rd = r["roads"]
    say("ROADS   %d edges over %d tiles in %d networks   %s"
        % (rd["edges"], rd["tiles_touched"], rd["networks"], rd["by_def"]))
    for c in rd["largest"][:5]:
        say("   network %3d edges  %2d settlements  %s"
            % (c["edges"], c["settlements"], c["defs"]))
    for kind in ("rivers", "roads"):
        if r[kind]["broken_entries"]:
            say("   🔴 %d %s entries point at a slot the tile has no neighbour in"
                % (len(r[kind]["broken_entries"]), kind))
    say()
    s = r["settlements"]
    say("SETTLE  %d settlements · %d coastal · %d on a river · %d on a road"
        % (s["count"], s["coastal"], s["on_river"], s["on_road"]))
    for row in s["list"]:
        say("   %-28s %-26s tile %-6d %-22s %6.0f m %5.1fC %5.0f mm %s%s%s"
            % (row["name"] or "-", row["faction"], row["tile"], row["biome"],
               row["elevation_m"], row["temp_c"], row["rain_mm"],
               "coast " if row["coastal"] else "", "river " if row["on_river"] else "",
               "road" if row["on_road"] else ""))
    say()
    say("REGIONS %d named world features · LANDMARKS %d"
        % (r["regions"]["count"], r["landmarks"]["count"]))
    if r["other_world_objects"]:
        say("OTHER   %s" % r["other_world_objects"])
    say("=" * 74)


# ==========================================================================
# 5. the picture
# ==========================================================================
BIOME_COLOR = {
    "Ocean": "#20496e", "Lake": "#2b6ea3", "SeaIce": "#bcd3de",
    "IceSheet": "#e6eef2", "Tundra": "#8f9a86", "GlacialPlain": "#cfe0e6",
    "BorealForest": "#3f6b46", "TemperateForest": "#4a7c3a", "TropicalRainforest": "#1f6b32",
    "TemperateSwamp": "#4e6b39", "TropicalSwamp": "#3d6b3a", "ColdBog": "#5c6f5c",
    "Wetland": "#4c7a5e", "Grasslands": "#7d9b4e", "AridShrubland": "#a89a5c",
    "Desert": "#c8ab6a", "ExtremeDesert": "#ded0a0", "Wasteland": "#8c7f6b",
    "LavaField": "#5d3320", "Volcano": "#6b3a2a", "Scarlands": "#8f5a4a",
    "PoisonForest": "#5b7a4a", "Glowforest": "#4a7a72", "Undercave": "#3a3540",
    "Underground": "#2f2b34", "Labyrinth": "#4a3f55", "MetalHell": "#6a2530",
    "Space": "#0a0a12", "Orbit": "#0a0a12",
}
BIOME_COLOR["Savanna"] = "#a59a52"

RAMPS = {
    "elevation": [(-500, "#0d1f3d"), (-1, "#3a6ea8"), (0, "#7fb3d8"), (1, "#d8c89a"),
                  (400, "#b99a63"), (1200, "#96754e"), (2200, "#8a8078"), (3500, "#e8e6e4")],
    "temperature": [(-60, "#2b1f6b"), (-30, "#3a6ea8"), (-10, "#7fc4e0"), (0, "#d8e8e0"),
                    (12, "#7fc46a"), (25, "#e0c04a"), (38, "#d8622a"), (60, "#7a1010")],
    "rainfall": [(0, "#d8c89a"), (200, "#c8b060"), (600, "#8ab04a"), (1200, "#3f8f5a"),
                 (2200, "#1f5f7a"), (4000, "#14304f")],
    "swampiness": [(0, "#d8c89a"), (0.5, "#7f8f4a"), (1.0, "#33502f")],
    "hilliness": [(0, "#cfd6cf"), (1, "#b8c8a8"), (2, "#a0a878"), (3, "#8f8560"),
                  (4, "#7a6a55"), (5, "#4a4038")],
    "pollution": [(0, "#cfd6cf"), (1, "#6a4a7a")],
}
ROAD_STYLE = {
    "DirtPath": ("#8a6a44", 0.9, "2 3"), "DirtRoad": ("#9a7040", 1.5, None),
    "StoneRoad": ("#b0a08a", 2.0, None), "AncientAsphaltRoad": ("#4a4a52", 2.4, None),
    "AncientAsphaltHighway": ("#33333a", 3.4, None),
}
RIVER_WIDTH = {"Creek": 1.0, "River": 1.8, "LargeRiver": 2.8, "HugeRiver": 4.0}


def _hex(c):
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


def ramp_color(stops, v):
    if v <= stops[0][0]:
        return stops[0][1]
    for (a, ca), (b, cb) in zip(stops[:-1], stops[1:]):
        if v <= b:
            f = 0.0 if b == a else (v - a) / (b - a)
            ra, rb = _hex(ca), _hex(cb)
            return "#%02x%02x%02x" % tuple(int(ra[k] + f * (rb[k] - ra[k])) for k in range(3))
    return stops[-1][1]


def biome_color(name):
    if name in BIOME_COLOR:
        return BIOME_COLOR[name]
    # deterministic, muted, and stable between runs so two maps stay comparable
    h = zlib.crc32(name.encode()) & 0xFFFFFFFF
    hue = (h % 360) / 360.0
    sat, val = 0.30 + ((h >> 9) % 25) / 100.0, 0.42 + ((h >> 17) % 30) / 100.0
    i = int(hue * 6) % 6
    f = hue * 6 - int(hue * 6)
    p, q, t = val * (1 - sat), val * (1 - f * sat), val * (1 - (1 - f) * sat)
    rgb = [(val, t, p), (q, val, p), (p, val, t),
           (p, q, val), (t, p, val), (val, p, q)][i]
    return "#%02x%02x%02x" % tuple(int(255 * c) for c in rgb)


class SVG(object):
    def __init__(self, w, h, bg="#0b0d12"):
        self.w, self.h = w, h
        self.parts = ['<svg xmlns="http://www.w3.org/2000/svg" '
                      'viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h),
                      '<rect width="%d" height="%d" fill="%s"/>' % (w, h, bg)]

    def add(self, s):
        self.parts.append(s)

    def write(self, path):
        self.parts.append("</svg>")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(self.parts))
        return path


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def tile_value(pv, layer, t):
    return {"biome": pv.biome[t], "elevation": pv.elev[t], "temperature": pv.temp[t],
            "rainfall": pv.rain[t], "swampiness": pv.swamp[t],
            "hilliness": pv.hilly[t],
            "pollution": pv.grid.arrays.get("tilePollution", [0] * pv.n)[t] / 65535.0
            }[layer]


def render(pv, layer="biome", projection="equirect", width=2400, center=(0.0, 0.0),
           tooltips=True, show=("rivers", "roads", "settlements", "coast", "labels"),
           out_path=None):
    g = pv.geom
    proj = worldgeom.make_projection(projection, width, center)
    legend_h = 260
    svg = SVG(proj.w, proj.h + legend_h)
    corners = g.all_corners()

    def poly(t):
        xy, vis = proj.project(corners[t], ref=g.vec[t])
        return (xy, vis)

    # -- tiles -----------------------------------------------------------
    svg.add('<g id="tiles" shape-rendering="crispEdges">')
    merged = defaultdict(list)
    for t in range(pv.n):
        xy, vis = poly(t)
        if not vis:
            continue
        v = tile_value(pv, layer, t)
        col = biome_color(v) if layer == "biome" else ramp_color(RAMPS[layer], float(v))
        d = "M" + " ".join("%.1f %.1f" % (x, y) for x, y in xy) + "Z"
        for dx in proj.wrap_copies(xy):
            d += " M" + " ".join("%.1f %.1f" % (x + dx, y) for x, y in xy) + "Z"
        if tooltips:
            svg.add('<path d="%s" fill="%s"><title>tile %d · %s · %.0f m · %.1f C · '
                    '%.0f mm · %s%s</title></path>'
                    % (d, col, t, esc(pv.biome[t]), pv.elev[t], pv.temp[t], pv.rain[t],
                       HILLINESS.get(int(pv.hilly[t]), ""),
                       (" · " + esc(pv.feature_name(pv.feature_idx[t])))
                       if pv.feature_name(pv.feature_idx[t]) else ""))
        else:
            merged[col].append(d)
    for col, ds in merged.items():
        svg.add('<path d="%s" fill="%s"/>' % (" ".join(ds), col))
    svg.add("</g>")

    def seg(a, b, ref):
        """One tile-centre to tile-centre segment, wrapped like the hexes."""
        xy, vis = proj.project(np.stack([g.vec[a], g.vec[b]]), ref=ref)
        if not vis or abs(xy[0][0] - xy[1][0]) > proj.w * 0.5:
            return []
        out = ["M%.1f %.1f L%.1f %.1f" % (xy[0][0], xy[0][1], xy[1][0], xy[1][1])]
        for dx in proj.wrap_copies(xy):
            out.append("M%.1f %.1f L%.1f %.1f"
                       % (xy[0][0] + dx, xy[0][1], xy[1][0] + dx, xy[1][1]))
        return out

    # -- coastline -------------------------------------------------------
    if "coast" in show:
        d = []
        for t, k in pv.coast_edges():
            cs = corners[t]
            e = np.stack([cs[(k - 1) % len(cs)], cs[k]])
            xy, vis = proj.project(e, ref=g.vec[t])
            if not vis or abs(xy[0][0] - xy[1][0]) > proj.w * 0.5:
                continue
            d.append("M%.1f %.1f L%.1f %.1f" % (xy[0][0], xy[0][1], xy[1][0], xy[1][1]))
        svg.add('<g id="coast"><path d="%s" stroke="#0a1520" stroke-width="1.1" '
                'fill="none" opacity="0.8"/></g>' % " ".join(d))

    # -- roads then rivers (rivers on top; they are the rarer signal) ------
    if "roads" in show and pv.roads:
        svg.add('<g id="roads" fill="none" stroke-linecap="round">')
        by_def = defaultdict(list)
        for o, t, dn, _ in pv.roads:
            by_def[dn].extend(seg(o, t, g.vec[o]))
        for dn, ds in by_def.items():
            col, wd, dash = ROAD_STYLE.get(dn, ("#a08a6a", 1.5, None))
            sc = proj.w / 2400.0
            svg.add('<path d="%s" stroke="%s" stroke-width="%.2f"%s><title>%s</title></path>'
                    % (" ".join(ds), col, wd * sc,
                       ' stroke-dasharray="%s"' % dash if dash else "", esc(dn)))
        svg.add("</g>")
    if "rivers" in show and pv.rivers:
        svg.add('<g id="rivers" fill="none" stroke-linecap="round">')
        by_def = defaultdict(list)
        for o, t, dn, _ in pv.rivers:
            by_def[dn].extend(seg(o, t, g.vec[o]))
        for dn, ds in by_def.items():
            sc = proj.w / 2400.0
            svg.add('<path d="%s" stroke="#4fa3d8" stroke-width="%.2f" opacity="0.95">'
                    '<title>%s</title></path>'
                    % (" ".join(ds), RIVER_WIDTH.get(dn, 1.5) * sc, esc(dn)))
        svg.add("</g>")

    # -- settlements ------------------------------------------------------
    if "settlements" in show and pv.settlements:
        pal = ["#ffd45e", "#ff8a5e", "#6ee0a0", "#8ab6ff", "#ff7bd0", "#c3ff6e",
               "#ffffff", "#ff5e5e", "#9d7bff", "#5ee0e0"]
        svg.add('<g id="settlements" font-family="DejaVu Sans, sans-serif">')
        sc = proj.w / 2400.0
        for s in pv.settlements:
            t = s["tile"]
            if t >= pv.n:
                continue
            xy, vis = proj.project(g.vec[t][None, :], ref=g.vec[t])
            if not vis:
                continue
            x, y = xy[0]
            f = pv.factions.get(s["faction"], {})
            col = pal[f.get("index", 0) % len(pal)]
            svg.add('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="#101014" '
                    'stroke-width="%.1f"><title>%s · %s · tile %d · %s</title></circle>'
                    % (x, y, 4.0 * sc, col, 1.2 * sc, esc(s["name"]),
                       esc(f.get("name") or s["faction"]), t, esc(pv.biome[t])))
            if "labels" in show:
                svg.add('<text x="%.1f" y="%.1f" font-size="%.1f" fill="#f0f0f0" '
                        'stroke="#101014" stroke-width="%.1f" paint-order="stroke">%s</text>'
                        % (x + 6 * sc, y - 5 * sc, 13 * sc, 2.5 * sc, esc(s["name"] or "")))
        st = pv.info.get("startingTile")
        if st is not None and st < pv.n:
            xy, vis = proj.project(g.vec[st][None, :], ref=g.vec[st])
            if vis:
                svg.add('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" '
                        'stroke="#ff3b3b" stroke-width="%.1f"><title>starting tile %d'
                        '</title></circle>' % (xy[0][0], xy[0][1], 9 * sc, 2.2 * sc, st))
        svg.add("</g>")

    # -- region labels ----------------------------------------------------
    if "labels" in show and pv.features:
        sc = proj.w / 2400.0
        svg.add('<g id="regions" font-family="DejaVu Sans, sans-serif" '
                'fill="#e8e0c8" opacity="0.75" text-anchor="middle">')
        for f in pv.features:
            idx = np.where(pv.feature_idx == f["index"])[0]
            if len(idx) < 8:
                continue
            v = g.vec[idx].mean(axis=0)
            v = v / np.linalg.norm(v)
            xy, vis = proj.project(v[None, :], ref=v)
            if not vis:
                continue
            size = max(11.0, min(30.0, 6.0 * math.sqrt(len(idx)))) * sc
            svg.add('<text x="%.1f" y="%.1f" font-size="%.1f" font-style="italic" '
                    'stroke="#101014" stroke-width="%.1f" paint-order="stroke">%s</text>'
                    % (xy[0][0], xy[0][1], size, 2.0 * sc, esc(f["name"] or f["def"])))
        svg.add("</g>")

    # -- legend -----------------------------------------------------------
    y0 = proj.h + 8
    svg.add('<g id="legend" font-family="DejaVu Sans, sans-serif" fill="#e8e8e8">')
    svg.add('<rect x="0" y="%d" width="%d" height="%d" fill="#101218"/>'
            % (proj.h, proj.w, legend_h))
    svg.add('<text x="14" y="%d" font-size="22" font-weight="bold">%s — %s, %s</text>'
            % (y0 + 22, esc(pv.info.get("name") or os.path.basename(pv.path)),
               esc(layer), esc(projection)))
    svg.add('<text x="14" y="%d" font-size="14" opacity="0.8">%d tiles · seed %s · '
            '%d settlements · %d river edges · %d road edges · %.1f%% water</text>'
            % (y0 + 44, pv.n, esc(pv.info.get("seedString")), len(pv.settlements),
               len(pv.rivers), len(pv.roads),
               100.0 * float(pv.is_water.sum()) / pv.n))
    if layer == "biome":
        cen = Counter(pv.biome).most_common(30)
        for i, (b, c) in enumerate(cen):
            col, row = i // 5, i % 5
            x, y = 14 + col * 400, y0 + 70 + row * 26
            svg.add('<rect x="%d" y="%d" width="18" height="18" fill="%s" '
                    'stroke="#000"/>' % (x, y, biome_color(b)))
            svg.add('<text x="%d" y="%d" font-size="14">%s  <tspan opacity="0.6">%d '
                    '(%.1f%%)</tspan></text>'
                    % (x + 24, y + 14, esc(b), c, 100.0 * c / pv.n))
    else:
        stops = RAMPS[layer]
        lo, hi = stops[0][0], stops[-1][0]
        for i in range(360):
            v = lo + (hi - lo) * i / 359.0
            svg.add('<rect x="%d" y="%d" width="2" height="26" fill="%s"/>'
                    % (14 + i * 2, y0 + 74, ramp_color(stops, v)))
        last = -1e9
        for a, _ in stops:
            x = 14 + 720 * (a - lo) / (hi - lo)
            if x - last < 34:          # ramps have crowded stops at the low end
                continue
            last = x
            svg.add('<text x="%.0f" y="%d" font-size="13" text-anchor="middle" '
                    'opacity="0.8">%g</text>' % (x, y0 + 118, a))
    svg.add("</g>")
    return svg.write(out_path)


CHROME = ["/mnt/c/Program Files/Google/Chrome/Application/chrome.exe",
          "/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"]


def rasterise(svg_path, width=None):
    """SVG -> PNG. No PIL and no matplotlib on this machine, but Chrome is here and
    it is the renderer the file was written for anyway. The window size comes from
    the file's own viewBox - guessing it crops the globe."""
    import subprocess
    exe = next((c for c in CHROME if os.path.exists(c)), None)
    if not exe:
        return None
    png = os.path.splitext(svg_path)[0] + ".png"
    with open(svg_path, encoding="utf-8") as fh:
        head = fh.read(400)
    vb = re.search(r'viewBox="0 0 (\d+) (\d+)"', head)
    win = "%s,%s" % (vb.group(1), vb.group(2)) if vb else "%d,%d" % (width, width)
    def win_path(p):
        p = os.path.abspath(p)
        return p[5].upper() + ":" + p[6:] if p.startswith("/mnt/") else p
    subprocess.run([exe, "--headless", "--disable-gpu", "--hide-scrollbars",
                    "--window-size=" + win, "--screenshot=" + win_path(png).replace("/", "\\"),
                    "file:///" + win_path(svg_path).replace("\\", "/")],
                   capture_output=True, timeout=300)
    return png if os.path.exists(png) else None


# ==========================================================================
def main():
    ap = argparse.ArgumentParser(description="Portray the planet inside a RimWorld save.")
    ap.add_argument("save")
    ap.add_argument("--out", default=os.path.join(REPO, "world", "view"))
    ap.add_argument("--dump", default=DEFAULT_DUMP, help="def dump for the SAME mod set")
    ap.add_argument("--layer", default="biome",
                    choices=["biome", "elevation", "temperature", "rainfall",
                             "swampiness", "hilliness", "pollution"])
    ap.add_argument("--projection", default="equirect", choices=["equirect", "ortho"])
    ap.add_argument("--center", default="0,0", help="lat,lon for --projection ortho")
    ap.add_argument("--width", type=int, default=2400)
    ap.add_argument("--no-tooltips", action="store_true",
                    help="merge hexes by colour: much smaller file, no hover")
    ap.add_argument("--hide", default="", help="comma list of rivers,roads,settlements,coast,labels")
    ap.add_argument("--water-biome", action="append", default=[],
                    help="treat this biome as water too (repeatable)")
    ap.add_argument("--not-water-biome", action="append", default=[])
    ap.add_argument("--tile", action="append", type=int, default=[],
                    help="print everything known about this tile (repeatable)")
    ap.add_argument("--png", action="store_true",
                    help="also rasterise the svg with headless Chrome, if installed")
    ap.add_argument("--report-only", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    pv = PlanetView(a.save, a.dump, a.water_biome, a.not_water_biome)
    rep = characterise(pv)
    if not a.quiet:
        print_report(rep)

    for t in a.tile:
        g = pv.geom
        ns = g.neighbours(t)
        print("\nTILE %d  lat %.3f lon %.3f" % (t, g.lat[t], g.lon[t]))
        print("  biome %s · elevation %.0f m · temp %.1f C · rain %.0f mm · %s · swamp %.2f"
              % (pv.biome[t], pv.elev[t], pv.temp[t], pv.rain[t],
                 HILLINESS.get(int(pv.hilly[t]), "?"), pv.swamp[t]))
        print("  region %s · landmark %s"
              % (pv.feature_name(pv.feature_idx[t]),
                 next((m["def"] for m in pv.landmarks if m["tile"] == t), None)))
        print("  neighbours (engine slot order) %s" % ns)
        print("  rivers %s" % [(o, u, d) for o, u, d, _ in pv.rivers if t in (o, u)])
        print("  roads  %s" % [(o, u, d) for o, u, d, _ in pv.roads if t in (o, u)])
        print("  settlement %s"
              % next((s["name"] for s in pv.settlements if s["tile"] == t), None))

    os.makedirs(a.out, exist_ok=True)
    stem = os.path.splitext(os.path.basename(a.save))[0]
    jpath = os.path.join(a.out, "%s.report.json" % stem)
    with open(jpath, "w", encoding="utf-8") as fh:
        json.dump(rep, fh, indent=1, ensure_ascii=False)
    print("\nreport  %s" % jpath)

    if not a.report_only:
        show = {"rivers", "roads", "settlements", "coast", "labels"}
        show -= {s.strip() for s in a.hide.split(",") if s.strip()}
        lat, lon = (float(x) for x in a.center.split(","))
        svg = os.path.join(a.out, "%s.%s.%s.svg" % (stem, a.layer, a.projection))
        render(pv, a.layer, a.projection, a.width, (lat, lon),
               not a.no_tooltips, show, svg)
        print("map     %s  (%.1f MB)" % (svg, os.path.getsize(svg) / 1e6))
        if a.png:
            png = rasterise(svg, a.width)
            print("png     %s" % (png or "no Chrome found - open the svg in a browser"))


if __name__ == "__main__":
    main()
