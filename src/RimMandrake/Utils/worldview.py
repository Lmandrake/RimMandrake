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
# 🔴 READABILITY IS THE POINT. Owner, 2026-08-18: "I'm having a very hard time
# reading this colorbar uniquely, there's too much of similar by-eye coloration."
# So the palette is chosen for SEPARATION first and mimicry second: the deserts are a
# pale-to-tan ramp, but everything else is pulled to a hue no desert occupies.
BIOME_COLOR = {
    # --- water
    "Ocean": "#1b3f66", "Lake": "#2f7fb5", "SeaIce": "#cfe4ee",
    # --- the dayside waste: a light ramp, cream -> tan -> olive
    "ExtremeDesert": "#f4e6bd", "Desert": "#dcbc74", "AridShrubland": "#b4a049",
    "ZBiome_Badlands": "#b0603a", "Wasteland": "#8e8d85",
    "AB_GallatrossGraveyard": "#d8c58a",
    # --- the Pyrelands
    "ZBiome_Grasslands": "#9dbb35", "Savanna": "#8faa30",
    # --- green, only on water
    "AB_FeraliskInfestedJungle": "#12703a", "ZBiome_DesertOasis": "#59cd8c",
    "AB_MiasmicMangrove": "#1f6b60", "COMIGO_GreaterSwamp_Tropical": "#2f8f70",
    # --- fire, one province
    "AB_PyroclasticConflagration": "#f4762a", "LavaField": "#d6431a",
    "Volcano": "#8c2a14", "Scarlands": "#bb2f4c", "AB_TarPits": "#211c1f",
    # --- the terminator's rot
    "PoisonForest": "#5d7a26", "AB_GelatinousSuperorganism": "#e04fb0",
    "HorrorWastes": "#7c0f31", "AB_MycoticJungle": "#a558da",
    "BMT_FungalForest": "#6a4fd8", "AB_OcularForest": "#7a2b93",
    # --- the dark
    "AB_RockyCrags": "#3a3a52", "AB_PropaneLakes": "#1f7d8c",
    "Glowforest": "#3fe0c2", "BMT_CrystalCaverns": "#a6dcff",
    "BMT_EarthenDepths": "#4a3a2a",
    # --- one-offs
    "AB_MechanoidIntrusion": "#9a9ab8", "IronScruff_PrimordialGeysers": "#46cfe0",
}

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


class BundlePlanet(object):
    """The planet read from the DATA BUNDLE rather than from a savegame.

    🔴 Owner, 2026-08-18: nothing writes to a .rws any more, so the renderer must be
    able to draw the map from `world/ashkarr_*.csv` alone. Same surface as
    PlanetView, so every layer, projection and legend works unchanged."""

    def __init__(self, stem):
        import csv as _csv
        import json as _json
        rows = list(_csv.DictReader(open(stem + "_tiles.csv", encoding="utf-8")))
        self.n = len(rows)
        self.path = stem + "_tiles.csv"
        self.geom = worldgeom.Geometry(self.n)
        g = self.geom
        self.biome = [r["biome"] for r in rows]
        self.elev = np.array([float(r["elev_m"]) for r in rows])
        self.temp = np.array([float(r["temp_c"]) for r in rows])
        self.rain = np.array([float(r["rain_mm"]) for r in rows])
        self.arc = np.array([float(r["arc"]) for r in rows])
        self.is_water = np.array([r["water"] == "1" for r in rows])
        self.grid = type("G", (), {"arrays": {"tilePollution": [0] * self.n}})()
        # 🔑 Hilliness and swampiness are DESIGN, so they come from the bundle. They
        # used to be derived here, which put a decision about the planet inside the
        # renderer - and this renderer is supposed to know nothing about Ash'karr.
        # The fallback below exists only for older bundles that predate the columns.
        if "hilliness" in rows[0]:
            self.hilly = np.array([int(r["hilliness"]) for r in rows], np.uint8)
            self.swamp = np.array([float(r["swampiness"]) for r in rows])
        else:
            self.swamp = np.zeros(self.n)
            self.hilly = np.ones(self.n, np.uint8)
            for t in range(self.n):
                if self.is_water[t]:
                    continue
                vals = [self.elev[t]] + [self.elev[u] for u in g.neighbours(t)]
                rel = max(vals) - min(vals)
                self.hilly[t] = (4 if rel > 780 else 3 if rel > 430 else
                                 2 if rel > 190 else 1)
        names, idx = [], {}
        self.feature_idx = np.full(self.n, 0xFFFF, np.uint16)
        for t, r in enumerate(rows):
            nm = r["region"]
            if not nm:
                continue
            if nm not in idx:
                idx[nm] = len(names)
                names.append(nm)
            self.feature_idx[t] = idx[nm]
        self.features = [{"index": i, "name": nm, "def": "Region"}
                         for i, nm in enumerate(names)]
        meta = _json.load(open(stem + "_meta.json", encoding="utf-8"))
        self.meta = meta
        self.info = {"name": meta.get("planet"), "seedString": "hand-authored",
                     "startingTile": meta.get("startingTile"),
                     "gameVersion": None, "mods": None,
                     "subdivisions": None, "planetCoverage": None,
                     "overallRainfall": None, "overallTemperature": None,
                     "radius": None, "pollution": None}
        self.settlements, self.factions = [], {}
        for r in _csv.DictReader(open(stem + "_settlements.csv", encoding="utf-8")):
            key = r["faction_def"]
            if key not in self.factions:
                self.factions[key] = {"name": r["faction"], "def": key,
                                      "index": len(self.factions)}
            self.settlements.append({"id": int(r["id"]), "tile": int(r["tile"]),
                                     "name": r["name"], "faction": key,
                                     "why": r["why"]})
        self.rivers, self.roads = [], []
        for r in _csv.DictReader(open(stem + "_links.csv", encoding="utf-8")):
            (self.rivers if r["kind"] == "river" else self.roads).append(
                (int(r["a"]), int(r["b"]), r["def"], 0))
        self.landmarks, self.unresolved = [], []
        self.water_biome_set = {"Ocean", "Lake", "SeaIce"}
        self.rivers_broken = self.roads_broken = []
        self.river_dist = None
        self.other_objects = {}

    def feature_name(self, i):
        return None if i == 0xFFFF or i >= len(self.features) else self.features[i]["name"]

    def coast_edges(self):
        out = []
        for t in range(self.n):
            ns = self.geom.neighbours(t)
            for k, u in enumerate(ns):
                if u > t and self.is_water[t] != self.is_water[u]:
                    out.append((t, k))
        return out

    def components(self, mask):
        return PlanetView.components(self, mask)

    def link_components(self, links):
        return PlanetView.link_components(self, links)


# 🔴 Owner 2026-08-19: "Please use icon shape + color to identify factions cleanly."
# Colour alone fails at 4 px on a 2400 px map and fails again for anyone who reads
# colour poorly. Shape carries the identity; colour reinforces it.
FACTION_MARKS = [
    ("circle", "#ffd45e"), ("square", "#ff7a4d"), ("triangle", "#5fe08f"),
    ("diamond", "#7fb6ff"), ("star", "#ff6fd0"), ("hex", "#c3ff6e"),
    ("cross", "#ffffff"), ("down", "#ff5e5e"), ("plus", "#b58bff"),
    ("bowtie", "#5ee0e0"), ("pent", "#ffb347"), ("ring", "#9fe8c8"),
]


def marker(shape, x, y, r, fill, stroke="#0d0f14", sw=1.2, extra=""):
    """One faction icon. Every shape is drawn to the same visual weight."""
    a = 'fill="%s" stroke="%s" stroke-width="%.2f"%s' % (fill, stroke, sw, extra)
    if shape == "circle":
        return '<circle cx="%.1f" cy="%.1f" r="%.1f" %s/>' % (x, y, r, a)
    if shape == "ring":
        return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
                'stroke-width="%.1f"/>' % (x, y, r, fill, sw * 2.2))
    if shape == "square":
        return '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" %s/>' % (
            x - r * .88, y - r * .88, r * 1.76, r * 1.76, a)
    pts = {
        "triangle": [(0, -1.15), (1.0, .72), (-1.0, .72)],
        "down":     [(0, 1.15), (1.0, -.72), (-1.0, -.72)],
        "diamond":  [(0, -1.25), (1.05, 0), (0, 1.25), (-1.05, 0)],
        "bowtie":   [(-1.1, -1.0), (1.1, -1.0), (-1.1, 1.0), (1.1, 1.0)],
        "cross":    [(-.38, -1.1), (.38, -1.1), (.38, -.38), (1.1, -.38),
                     (1.1, .38), (.38, .38), (.38, 1.1), (-.38, 1.1),
                     (-.38, .38), (-1.1, .38), (-1.1, -.38), (-.38, -.38)],
    }
    if shape == "plus":
        pts["plus"] = pts["cross"]
    if shape in ("hex", "pent", "star"):
        k = {"hex": 6, "pent": 5, "star": 5}[shape]
        out = []
        for i in range(k * (2 if shape == "star" else 1)):
            ang = math.pi * 2 * i / (k * (2 if shape == "star" else 1)) - math.pi / 2
            rad = 1.15 if (shape != "star" or i % 2 == 0) else 0.5
            out.append((math.cos(ang) * rad, math.sin(ang) * rad))
        pts[shape] = out
    q = pts.get(shape) or pts["triangle"]
    return '<polygon points="%s" %s/>' % (
        " ".join("%.1f,%.1f" % (x + dx * r, y + dy * r) for dx, dy in q), a)


def hillshade(pv):
    """Per-tile shading from the local elevation gradient, sun from the north-west.

    🔴 Owner: "We need to see mountain ranges too, critically." A flat biome fill
    cannot show a range - two Desert tiles 2 km apart in height look identical. This
    multiplies every fill by the slope, so the ranges read THROUGH the biome colour
    instead of needing their own layer."""
    g, n = pv.geom, pv.n
    sh = np.ones(n)
    east = np.zeros((n, 3))
    for t in range(n):
        c = g.vec[t]
        up = np.array([0.0, 1.0, 0.0])
        e = np.cross(up, c)
        e = e / (np.linalg.norm(e) + 1e-12)
        nn = np.cross(c, e)
        gx = gy = 0.0
        for u in g.neighbours(t):
            d = g.vec[u] - c
            dh = pv.elev[u] - pv.elev[t]
            gx += float(d.dot(e)) * dh
            gy += float(d.dot(nn)) * dh
        # light from the upper left, and a touch of ambient so nothing goes black
        lam = (-0.62 * gx + 0.62 * gy) / 380.0
        sh[t] = 1.0 + np.clip(lam, -0.62, 0.62)
    return sh


def shade_hex(col, k):
    r, g, b = _hex(col)
    return "#%02x%02x%02x" % (min(255, max(0, int(r * k))),
                              min(255, max(0, int(g * k))),
                              min(255, max(0, int(b * k))))


def _small_circle(sub_lat, sub_lon, arc_deg, steps=361):
    """Unit vectors on the circle `arc_deg` from a point. arc 90 IS the terminator."""
    a, b = math.radians(sub_lat), math.radians(sub_lon)
    c = np.array([math.cos(a) * math.cos(b), math.sin(a), math.cos(a) * math.sin(b)])
    up = np.array([0.0, 1.0, 0.0])
    e = np.cross(up, c)
    e = e / (np.linalg.norm(e) + 1e-12)
    nn = np.cross(c, e)
    th = math.radians(arc_deg)
    out = []
    for k in range(steps):
        p = math.radians(k * 360.0 / (steps - 1))
        out.append(c * math.cos(th) + (e * math.cos(p) + nn * math.sin(p)) * math.sin(th))
    return np.array(out)


def draw_panel(svg, pv, proj, y0, layer, show, tooltips, corners, shade):
    """One map into one band of the sheet."""
    g = pv.geom
    svg.add('<g transform="translate(0,%d)">' % y0)
    svg.add('<g shape-rendering="crispEdges">')
    merged = defaultdict(list)
    for t in range(pv.n):
        xy, vis = proj.project(corners[t], ref=g.vec[t])
        if not vis:
            continue
        v = tile_value(pv, layer, t)
        col = biome_color(v) if layer == "biome" else ramp_color(RAMPS[layer], float(v))
        if shade is not None:
            col = shade_hex(col, shade[t])
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

    sc = proj.w / 2400.0

    def seg(a, b, ref):
        xy, vis = proj.project(np.stack([g.vec[a], g.vec[b]]), ref=ref)
        if not vis or abs(xy[0][0] - xy[1][0]) > proj.w * 0.5:
            return []
        out = ["M%.1f %.1f L%.1f %.1f" % (xy[0][0], xy[0][1], xy[1][0], xy[1][1])]
        for dx in proj.wrap_copies(xy):
            out.append("M%.1f %.1f L%.1f %.1f"
                       % (xy[0][0] + dx, xy[0][1], xy[1][0] + dx, xy[1][1]))
        return out

    # ⭐ THE RANGES, drawn as themselves. Owner: "We need to see mountain ranges
    # too, critically." Hillshade alone is not enough at this tile size, so every
    # Mountainous / Impassable tile also gets an outline.
    if "mountains" in show:
        d = []
        for t in range(pv.n):
            if pv.hilly[t] < 4:
                continue
            xy, vis = proj.project(corners[t], ref=g.vec[t])
            if not vis or (xy[:, 0].max() - xy[:, 0].min()) > proj.w * 0.4:
                continue
            d.append("M" + " ".join("%.1f %.1f" % (x, y) for x, y in xy) + "Z")
        svg.add('<path d="%s" fill="none" stroke="#2a1c10" stroke-width="%.1f" '
                'opacity="0.55"/>' % (" ".join(d), 1.6 * sc))

    if "coast" in show:
        d = []
        for t, k in pv.coast_edges():
            cs = corners[t]
            e = np.stack([cs[(k - 1) % len(cs)], cs[k]])
            xy, vis = proj.project(e, ref=g.vec[t])
            if not vis or abs(xy[0][0] - xy[1][0]) > proj.w * 0.5:
                continue
            d.append("M%.1f %.1f L%.1f %.1f" % (xy[0][0], xy[0][1], xy[1][0], xy[1][1]))
        svg.add('<path d="%s" stroke="#0a1520" stroke-width="%.1f" fill="none" '
                'opacity="0.85"/>' % (" ".join(d), 1.1 * sc))

    if "roads" in show and pv.roads:
        by = defaultdict(list)
        for o, t, dn, _ in pv.roads:
            by[dn].extend(seg(o, t, g.vec[o]))
        for dn, ds in by.items():
            col, wd, dash = ROAD_STYLE.get(dn, ("#a08a6a", 1.5, None))
            svg.add('<path d="%s" stroke="%s" stroke-width="%.2f" fill="none"%s/>'
                    % (" ".join(ds), col, wd * sc,
                       ' stroke-dasharray="%s"' % dash if dash else ""))
    if "rivers" in show and pv.rivers:
        by = defaultdict(list)
        for o, t, dn, _ in pv.rivers:
            by[dn].extend(seg(o, t, g.vec[o]))
        for dn, ds in by.items():
            svg.add('<path d="%s" stroke="#57c8ff" stroke-width="%.2f" fill="none" '
                    'opacity="0.95"/>' % (" ".join(ds), RIVER_WIDTH.get(dn, 1.5) * sc))

    # ⭐ THE TERMINATOR. Owner: "I need to see where the terminator is on this map."
    if "grid" in show:
        for arc, style, lab in ((90, None, "TERMINATOR"),):
            pts = _small_circle(0, 0, arc)
            xy, _ = proj.project(pts)
            d, run = [], []
            for k in range(len(xy)):
                if run and abs(xy[k][0] - run[-1][0]) > proj.w * 0.45:
                    d.append("M" + " L".join("%.1f %.1f" % (a, b) for a, b in run))
                    run = []
                run.append(xy[k])
            if run:
                d.append("M" + " L".join("%.1f %.1f" % (a, b) for a, b in run))
            svg.add('<path d="%s" fill="none" stroke="#ffffff" stroke-width="%.1f" '
                    'opacity="%.2f"%s/>'
                    % (" ".join(d), (2.4 if arc == 90 else 1.2) * sc,
                       0.85 if arc == 90 else 0.35,
                       ' stroke-dasharray="%s"' % style if style else ""))
        for lat, lon, mark, txt in ((0, 0, "#ffd45e", "SUBSTELLAR"),
                                    (0, 180, "#7fb0ff", "ANTISTELLAR")):
            a, b = math.radians(lat), math.radians(lon)
            v = np.array([math.cos(a) * math.cos(b), math.sin(a), math.cos(a) * math.sin(b)])
            xy, vis = proj.project(v[None, :], ref=v)
            if not vis:
                continue
            svg.add('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
                    'stroke-width="%.1f"/>' % (xy[0][0], xy[0][1], 7 * sc, mark, 2.2 * sc))
            svg.add('<text x="%.1f" y="%.1f" font-size="%.1f" fill="%s" '
                    'text-anchor="middle" font-family="DejaVu Sans, sans-serif" '
                    'stroke="#000" stroke-width="%.1f" paint-order="stroke">%s</text>'
                    % (xy[0][0], xy[0][1] - 11 * sc, 13 * sc, mark, 2.0 * sc, txt))

    if "settlements" in show and pv.settlements:
        # the dots always draw; the NAMES declutter, because 72 holdings crowd the
        # terminator band into an unreadable smear
        placed_px = []
        for st in pv.settlements:
            t = st["tile"]
            if t >= pv.n:
                continue
            xy, vis = proj.project(g.vec[t][None, :], ref=g.vec[t])
            if not vis:
                continue
            f = pv.factions.get(st["faction"], {})
            shape, col = FACTION_MARKS[f.get("index", 0) % len(FACTION_MARKS)]
            svg.add(marker(shape, xy[0][0], xy[0][1], 5.0 * sc, col, sw=1.3 * sc,
                           extra=""). replace("/>", "><title>%s — %s</title></%s>"
                    % (esc(st["name"]), esc(f.get("name") or st["faction"]),
                       "circle" if shape in ("circle", "ring") else
                       "rect" if shape == "square" else "polygon"), 1))
            if "labels" in show:
                px, py = float(xy[0][0]), float(xy[0][1])
                if any(abs(px - a) < 62 * sc and abs(py - b) < 13 * sc
                       for a, b in placed_px):
                    continue
                placed_px.append((px, py))
                svg.add('<text x="%.1f" y="%.1f" font-size="%.1f" fill="#f0f0f0" '
                        'font-family="DejaVu Sans, sans-serif" stroke="#101014" '
                        'stroke-width="%.1f" paint-order="stroke">%s</text>'
                        % (px + 6 * sc, py - 5 * sc, 13 * sc, 2.5 * sc,
                           esc(st["name"] or "")))
        stt = pv.info.get("startingTile")
        if stt is not None and stt < pv.n:
            xy, vis = proj.project(g.vec[stt][None, :], ref=g.vec[stt])
            if vis:
                svg.add('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" '
                        'stroke="#ff3b3b" stroke-width="%.1f"/>'
                        % (xy[0][0], xy[0][1], 9 * sc, 2.2 * sc))

    if "labels" in show and pv.features:
        svg.add('<g font-family="DejaVu Sans, sans-serif" fill="#f2ead2" '
                'opacity="0.88" text-anchor="middle">')
        # 🔴 Labels crowd, and the anchor is not what collides - the TEXT is.
        # An 11 deg separation between anchors let "The Dew Horn", "The Scald" and
        # "The Dew Belt" print on top of each other, because a 20-word-wide italic
        # is far wider than 11 deg of sphere. So: keep the anchor rule only to stop
        # two names for one place, then test the PROJECTED PIXEL BOX, and walk a
        # short ladder of vertical offsets before giving a name up entirely.
        MIN_SEP = 6.0
        drawn = []
        placed = []      # (x0, y0, x1, y1) pixel boxes already taken
        for f in pv.features:
            idx = np.where(pv.feature_idx == f["index"])[0]
            if len(idx) < 8:
                continue
            v = g.vec[idx].mean(axis=0)
            v = v / np.linalg.norm(v)
            if any(math.degrees(math.acos(max(-1.0, min(1.0, float(v.dot(d)))))) < MIN_SEP
                   for d in drawn):
                continue
            drawn.append(v)
            xy, vis = proj.project(v[None, :], ref=v)
            if not vis:
                continue
            size = max(11.0, min(28.0, 5.6 * math.sqrt(len(idx)))) * sc
            name = f["name"] or f["def"]
            # DejaVu Sans Oblique averages ~0.52 em per character over mixed case.
            half_w = 0.26 * size * len(name) + 3.0 * sc
            x0, y0 = float(xy[0][0]), float(xy[0][1])
            for step in (0.0, -1.25, 1.25, -2.5, 2.5, -3.75, 3.75, -5.0, 5.0):
                cy = y0 + step * size
                box = (x0 - half_w, cy - 0.80 * size, x0 + half_w, cy + 0.28 * size)
                if any(box[0] < q[2] and q[0] < box[2] and box[1] < q[3] and q[1] < box[3]
                       for q in placed):
                    continue
                placed.append(box)
                svg.add('<text x="%.1f" y="%.1f" font-size="%.1f" font-style="italic" '
                        'stroke="#101014" stroke-width="%.1f" paint-order="stroke">%s</text>'
                        % (x0, cy, size, 2.2 * sc, esc(name)))
                break
        svg.add("</g>")
    svg.add("</g>")


def render(pv, layer="biome", projection="equirect", width=2400, center=(0.0, 0.0),
           tooltips=True, show=("rivers", "roads", "settlements", "coast", "labels",
                                "grid", "mountains"),
           out_path=None, sheet=True, relief=True):
    """The review sheet: rectangular map on top, legend, equal-area map beneath.

    Owner, 2026-08-18: "I think I might need a Mollweide map beneath the rectangular
    depiction & legend to better visualize." The rectangular map is the one you can
    point at; the Mollweide is the one whose AREAS are true."""
    g = pv.geom
    corners = g.all_corners()
    shade = hillshade(pv) if relief else None
    main = worldgeom.make_projection(projection, width, center)
    second = (worldgeom.Mollweide(width, center[1])
              if sheet and projection == "equirect" else None)
    legend_h = 300 if not getattr(pv, 'settlements', None) else 520
    total = main.h + legend_h + (second.h + 30 if second else 0)
    svg = SVG(main.w, total)

    draw_panel(svg, pv, main, 0, layer, set(show), tooltips, corners, shade)
    y0 = main.h

    svg.add('<g font-family="DejaVu Sans, sans-serif" fill="#e8e8e8">')
    svg.add('<rect x="0" y="%d" width="%d" height="%d" fill="#101218"/>'
            % (y0, main.w, legend_h))
    svg.add('<text x="14" y="%d" font-size="23" font-weight="bold">%s — %s</text>'
            % (y0 + 26, esc(pv.info.get("name") or os.path.basename(pv.path)), esc(layer)))
    svg.add('<text x="14" y="%d" font-size="14" opacity="0.85">%d tiles · %d settlements'
            ' · %d river edges · %d road edges · %.1f%% water · substellar (0,0), '
            'terminator = the solid white circle</text>'
            % (y0 + 48, pv.n, len(pv.settlements), len(pv.rivers), len(pv.roads),
               100.0 * float(pv.is_water.sum()) / pv.n))
    if layer == "biome":
        cen = Counter(pv.biome).most_common(30)
        for i, (b, c) in enumerate(cen):
            col, row = i // 10, i % 10
            x, y = 14 + col * 290, y0 + 72 + row * 27
            svg.add('<rect x="%d" y="%d" width="20" height="20" fill="%s" '
                    'stroke="#000"/>' % (x, y, biome_color(b)))
            svg.add('<text x="%d" y="%d" font-size="13">%s  <tspan opacity="0.6">%.1f%%'
                    '</tspan></text>' % (x + 26, y + 15, esc(b), 100.0 * c / pv.n))
    else:
        stops = RAMPS[layer]
        lo, hi = stops[0][0], stops[-1][0]
        for i in range(360):
            v = lo + (hi - lo) * i / 359.0
            svg.add('<rect x="%d" y="%d" width="2" height="26" fill="%s"/>'
                    % (14 + i * 2, y0 + 80, ramp_color(stops, v)))
        last = -1e9
        for a, _ in stops:
            x = 14 + 720 * (a - lo) / (hi - lo)
            if x - last < 34:
                continue
            last = x
            svg.add('<text x="%.0f" y="%d" font-size="13" text-anchor="middle" '
                    'opacity="0.8">%g</text>' % (x, y0 + 124, a))
    # ⭐ WHO LIVES WHERE, as an actual legend box. Owner 2026-08-19: "The legend
    # needs text too, as in an actual legend box like you have for biomes."
    if getattr(pv, "settlements", None):
        by = defaultdict(list)
        for st in pv.settlements:
            by[st["faction"]].append(st["name"])
        order = sorted(by, key=lambda k: -len(by[k]))
        bx, bw = 880, main.w - 900
        svg.add('<rect x="%d" y="%d" width="%d" height="%d" fill="#161a22" '
                'stroke="#39415a" stroke-width="1.5" rx="4"/>'
                % (bx, y0 + 60, bw, legend_h - 74))
        svg.add('<text x="%d" y="%d" font-size="15" font-weight="bold" '
                'letter-spacing="1.5" fill="#c8d2e8">FACTIONS AND THEIR '
                'SETTLEMENTS</text>' % (bx + 14, y0 + 82))
        x, y = bx + 16, y0 + 108
        colw = (bw - 32) // 2
        for j, k in enumerate(order):
            f = pv.factions.get(k, {})
            shape, col = FACTION_MARKS[f.get("index", 0) % len(FACTION_MARKS)]
            svg.add(marker(shape, x + 9, y - 5, 7.5, col, sw=1.2))
            svg.add('<text x="%d" y="%d" font-size="15" font-weight="bold" '
                    'fill="#f0f4ff">%s <tspan font-weight="normal" opacity="0.6">'
                    '(%d)</tspan></text>' % (x + 24, y, esc(f.get("name", k)), len(by[k])))
            line, lines = "", []
            for nm in by[k]:
                if len(line) + len(nm) > 54:
                    lines.append(line)
                    line = ""
                line += (" · " if line else "") + nm
            lines.append(line)
            for ln in lines:
                y += 17
                svg.add('<text x="%d" y="%d" font-size="13" fill="#aeb8cc">%s</text>'
                        % (x + 24, y, esc(ln)))
            y += 20
            if y > y0 + legend_h - 46 and x < bx + colw:
                x, y = bx + 16 + colw, y0 + 108

        # and a key for everything that is not a settlement
        kx = 14
        ky = y0 + legend_h - 26
        svg.add('<text x="%d" y="%d" font-size="13" fill="#aeb8cc">KEY&#160;&#160;'
                '<tspan fill="#57c8ff">river</tspan> &#160;'
                '<tspan fill="#b0a08a">road</tspan> &#160;'
                '<tspan fill="#ffffff">terminator (arc 90)</tspan> &#160;'
                '<tspan fill="#8e8d85">Wasteland = dead salt plain</tspan> &#160;'
                '<tspan fill="#2f7fb5">Lake = hypersaline pool / the Scald</tspan> &#160;'
                'outlined hexes = mountainous</text>' % (kx, ky))

    svg.add("</g>")

    if second:
        svg.add('<rect x="0" y="%d" width="%d" height="%d" fill="#0b0d12"/>'
                % (y0 + legend_h, main.w, second.h + 30))
        draw_panel(svg, pv, second, y0 + legend_h + 15, layer, set(show) - {"labels"},
                   False, corners, shade)
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
    ap.add_argument("save", help="a .rws savegame, or a bundle stem like world/ashkarr")
    ap.add_argument("--out", default=os.path.join(REPO, "world", "view"))
    ap.add_argument("--dump", default=DEFAULT_DUMP, help="def dump for the SAME mod set")
    ap.add_argument("--layer", default="biome",
                    choices=["biome", "elevation", "temperature", "rainfall",
                             "swampiness", "hilliness", "pollution"])
    ap.add_argument("--projection", default="equirect", choices=["equirect", "ortho", "mollweide"])
    ap.add_argument("--no-sheet", action="store_true", help="one map only, no Mollweide panel")
    ap.add_argument("--no-relief", action="store_true", help="flat fills, no hillshade")
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

    if a.save.endswith(".rws"):
        pv = PlanetView(a.save, a.dump, a.water_biome, a.not_water_biome)
    else:
        pv = BundlePlanet(a.save)
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
    stem = os.path.splitext(os.path.basename(a.save))[0] or "ashkarr"
    jpath = os.path.join(a.out, "%s.report.json" % stem)
    with open(jpath, "w", encoding="utf-8") as fh:
        json.dump(rep, fh, indent=1, ensure_ascii=False)
    print("\nreport  %s" % jpath)

    if not a.report_only:
        show = {"rivers", "roads", "settlements", "coast", "labels", "grid", "mountains"}
        show -= {s.strip() for s in a.hide.split(",") if s.strip()}
        lat, lon = (float(x) for x in a.center.split(","))
        svg = os.path.join(a.out, "%s.%s.%s.svg" % (stem, a.layer, a.projection))
        render(pv, a.layer, a.projection, a.width, (lat, lon),
               not a.no_tooltips, show, svg, not a.no_sheet, not a.no_relief)
        print("map     %s  (%.1f MB)" % (svg, os.path.getsize(svg) / 1e6))
        if a.png:
            png = rasterise(svg, a.width)
            print("png     %s" % (png or "no Chrome found - open the svg in a browser"))


if __name__ == "__main__":
    main()
