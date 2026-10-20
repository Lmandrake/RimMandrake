#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""world_layers_export.py - OFFLINE: the canonical save's world layers -> w9 stamp files.

Item WORLD_LAYERS_RESCUE_THE_SAVE_HAS_MORE (PLAN.md §5a "export the authoritative layers",
02_world_pipeline.md §3). The committed w9 stamp files (`world/ASHKARR_WORLDMAP_*.csv`) are
stale against the save; nothing wrote the save's layers back. This does, READ-ONLY:

    save (.rws) --worldmap.py/worldview.py decoders--> raw/     names exactly as the save holds them
                                                    -> ported/  names through the rename map, then
                                                                the retired-mutator port map
                                                    -> REPORT.md, diff.json

Layers (one file each, the shape w9_run.py stamps from; extra columns are appended, never reordered):
    ASHKARR_WORLDMAP_tiles.csv        biome/elev/temp/rain/hilliness/swampiness/region from the save;
                                      lat/lon/arc/bearing/water/river_flow carried from the record CSV
                                      by tile id (geometry is seed-independent; the save has no positions)
    ASHKARR_WORLDMAP_links.csv        kind,a,b,def - rivers first (record order for edges the record
                                      shares, then by river distance), then roads
    ASHKARR_WORLDMAP_mutators.csv     tile,mutators (every entry, save order, ';'-joined)
    ASHKARR_WORLDMAP_landmarks.csv    tile,landmark,why,name
    ASHKARR_WORLDMAP_settlements.csv  id,faction_def,faction,name,tile,lat,lon,arc,biome,why  (NPC only)
    ASHKARR_WORLDMAP_factions.csv     ref,loadID,def,name,primary_ideo,ideo_name,ideo_culture,hidden,relations
    ASHKARR_WORLDMAP_features.csv     uid,def,name,drawCenter,size,tiles
    ASHKARR_WORLDMAP_landforms.csv    tile,topology,topologyDirection,landforms,biomeVariants (GeologicalLandforms)
    world_info.json                   world info, preset, axial tilt, worldGenerationData, liquid worldTags

🔴 shortHash decode: the save's hashes are decoded against EVERY DefDump capture, ranked by how
much of the save's own <modIds> each capture loaded. A hash two captures name differently is a
reported CONFLICT (the best-ranked name is used); a hash no capture names is UNRESOLVED and, for
biomes only, inferred from the record tiles CSV when every tile carrying it agrees there.
⛔ Never writes a save; never generates a world (CLAUDE.md: no worldgen). Never overwrites the
committed stamp files: --out must not be world/ itself.

    python3 src/RimMandrake/Utils/world_layers_export.py --dry-run     decode + diff, write nothing
    python3 src/RimMandrake/Utils/world_layers_export.py               write to world/rescue_2026-10-19/
    python3 src/RimMandrake/Utils/selftest_world_layers_export.py      fixture selftest
"""
import argparse
import collections
import csv
import hashlib
import io
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

import worldmap                                                    # noqa: E402
from save_donor_rewrite import short_hash_raw                     # noqa: E402  Verse.ShortHashGiver raw hash

DEF_TYPES = ("BiomeDef", "TileMutatorDef", "LandmarkDef", "RoadDef", "RiverDef", "FactionDef",
             "FeatureDef", "WorldObjectDef")
RECORD_PREFIX = os.path.join(REPO, "world", "ASHKARR_WORLDMAP_")
DEFAULT_OUT = os.path.join(REPO, "world", "rescue_2026-10-19")
DEFAULT_PROFILE = os.path.join(REPO, "deployed", "config", "ModsConfig.CANDIDATE_2026-10-19.xml")
RENAME_MAP = os.path.join(REPO, "infrastructure", "state", "naming_rename_map.csv")
PORT_MAP = os.path.join(REPO, "design", "RimMandrake", "retired_mutators_port_map.json")
SAVE_NAME = "CANONICAL_ASHKARR_START_2026-09-12.rws"
BUMP = 16              # how far a ShortHashGiver collision bump is looked for (observed: +1)
# Renames the save outlived that naming_rename_map.csv does not carry (each cited). Their OLD names
# join the hash universe, so a save hash that only a retired name explains is still decoded.
HISTORICAL_RENAMES = {
    "BiomeDef": {
        "RUT_ForsakenCrags": ("RUT_Abyss", "a534284e4 ABYSS_FULL_RENAME_1"),
        "RUT_PoisonForest": ("RUT_Cauldron", "CAULDRON_FULL_RENAME_1, 2026-09-30 (biome_paint_list.md)"),
        "RM_FE_Pyrelands": ("RM_Pyrelands", "84d42c63b owner ruling 2026-09-21"),
    },
}
LAYERS = ("tiles", "links", "mutators", "landmarks", "settlements", "factions", "features", "landforms")


# =============================================================================
# def tables
# =============================================================================
def _capture_defs(cap_dir, def_type):
    p = os.path.join(cap_dir, "defs", def_type + ".json")
    if not os.path.exists(p):
        return []
    data = json.load(open(p, encoding="utf-8"))
    defs = data if isinstance(data, list) else data.get("defs", data)
    return [d for d in defs if isinstance(d, dict) and d.get("defName")]


class Captures(object):
    """Every DefDump capture, ranked by overlap with the save's own mod list."""

    def __init__(self, cap_root, save_mods, def_types=DEF_TYPES):
        self.ranked = []
        for n in sorted(os.listdir(cap_root)) if os.path.isdir(cap_root) else []:
            d = os.path.join(cap_root, n)
            try:
                man = json.load(open(os.path.join(d, "manifest.json"), encoding="utf-8-sig"))
            except (OSError, ValueError):
                continue
            mods = {m.get("packageId", "").lower() for m in man.get("mods", [])}
            share = len(mods & save_mods) / float(len(save_mods) or 1)
            self.ranked.append({"name": n, "dir": d, "mods": len(mods), "share": round(share, 4)})
        # best overlap first; ties -> newest first
        self.ranked.sort(key=lambda c: (-c["share"], [-ord(ch) for ch in c["name"]]))
        self.by_hash = {}      # type -> hash -> [(cap, name), ...] in rank order
        self.pkg = {}          # type -> name -> packageId (newest capture that has it)
        for t in def_types:
            hmap, pk = collections.defaultdict(list), {}
            for c in self.ranked:
                for d in _capture_defs(c["dir"], t):
                    if d.get("shortHash") is not None:
                        hmap[int(d["shortHash"])].append((c["name"], d["defName"]))
            for c in sorted(self.ranked, key=lambda c: c["name"], reverse=True):
                for d in _capture_defs(c["dir"], t):
                    pk.setdefault(d["defName"], d.get("packageId") or "")
            self.by_hash[t], self.pkg[t] = hmap, pk

    def name(self, def_type, h):
        """(name or None, conflict list or None)."""
        hits = self.by_hash.get(def_type, {}).get(h, [])
        if not hits:
            return None, None
        names = []
        for _, n in hits:
            if n not in names:
                names.append(n)
        return names[0], (hits if len(names) > 1 else None)


class TableFromDicts(object):
    """Fixture stand-in for Captures: {type: {hash: name}}, {type: {name: pkg}}."""

    def __init__(self, hashes, pkgs):
        self.ranked = [{"name": "fixture", "dir": "", "mods": 0, "share": 1.0}]
        self.by_hash = {t: {h: [("fixture", n)] for h, n in m.items()} for t, m in hashes.items()}
        self.pkg = pkgs

    def name(self, def_type, h):
        hit = self.by_hash.get(def_type, {}).get(h)
        return (hit[0][1], None) if hit else (None, None)


def src_def_index(src_root):
    """{defName: packageId} for every <defName> in our own mods under src/ (defs not yet captured)."""
    out = {}
    if not os.path.isdir(src_root):
        return out
    for root, dirs, files in os.walk(src_root):
        about = os.path.join(root, "About", "About.xml")
        if not os.path.exists(about):
            continue
        try:
            pid = (ET.parse(about).getroot().findtext("packageId") or "").strip().lower()
        except ET.ParseError:
            continue
        for r2, d2, f2 in os.walk(root):
            for f in f2:
                if f.endswith(".xml") and os.sep + "About" not in r2:
                    try:
                        txt = open(os.path.join(r2, f), encoding="utf-8", errors="replace").read()
                    except OSError:
                        continue
                    for n in re.findall(r"<defName>\s*([^<\s]+)\s*</defName>", txt):
                        out.setdefault(n, pid)
        dirs[:] = []            # a mod root's subtree was just walked
    return out


def read_profile(path):
    r = ET.parse(path).getroot().find("activeMods")
    return {li.text.strip().lower() for li in r if li.text}


def read_rename_map(path):
    m = {}
    if not os.path.exists(path):
        return m
    for row in csv.DictReader(open(path, encoding="utf-8")):
        if row.get("kind") == "def" and row.get("old") and row.get("new") and row["old"] != row["new"]:
            m[row["old"]] = row["new"]
    return m


def read_port_map(path):
    if not os.path.exists(path):
        return {}
    j = json.load(open(path, encoding="utf-8"))
    return {t: {o: r.get("new") for o, r in j.get(t, {}).items()} for t in ("TileMutatorDef", "LandmarkDef")}


def read_csv(path):
    if not os.path.exists(path):
        return None
    return list(csv.DictReader(open(path, encoding="utf-8", newline="")))


# =============================================================================
# decode
# =============================================================================
def decode(save_path, table, record, geom=None):
    """Every layer out of one save, names through `table`. Returns (layers, notes)."""
    import worldview
    notes = collections.defaultdict(list)
    grid = worldmap.WorldGrid.__new__(worldmap.WorldGrid)
    grid.save_path = save_path
    with open(save_path, encoding="utf-8", errors="surrogateescape") as fh:
        grid.text = fh.read()
    grid._locate_surface()
    grid.arrays = {}
    for name, width in worldmap.SCALARS.items():
        raw = grid._read_array(name)
        if raw is None:
            continue
        import struct
        fmt = "<%d%s" % (len(raw) // width, "H" if width == 2 else "B")
        grid.arrays[name] = list(struct.unpack(fmt, raw))
    grid.tiles = len(grid.arrays["tileBiome"])
    if geom is None:
        import worldgeom
        geom = worldgeom.Geometry(grid.tiles)
    grid.geom = geom
    objs = worldmap.WorldObjects.__new__(worldmap.WorldObjects)
    objs.save_path, objs.text = save_path, grid.text

    unresolved = collections.defaultdict(collections.Counter)
    conflicts = {}
    universe = collections.defaultdict(set)          # type -> every name any capture or the record knows
    for t, hm in table.by_hash.items():
        for hits in hm.values():
            universe[t].update(n for _, n in hits)
    for r in record.get("tiles") or []:
        universe["BiomeDef"].add(r["biome"])
    for r in record.get("mutators") or []:
        universe["TileMutatorDef"].update(m for m in r["mutators"].split(";") if m)
    for r in record.get("links") or []:
        universe["RiverDef" if r["kind"] == "river" else "RoadDef"].add(r["def"])
    for t, m in HISTORICAL_RENAMES.items():
        universe[t].update(m)
    raw_of = {t: {n: short_hash_raw(n) for n in ns} for t, ns in universe.items()}

    def candidates(t, h):
        """Names that could carry hash h in SOME mod set: raw hash h, or a raw hash just below h
        that a collision could have bumped up to h (Verse.ShortHashGiver bumps by +1)."""
        return sorted(n for n, r in raw_of.get(t, {}).items() if h - BUMP <= r <= h)

    def nm(t, h):
        n, c = table.name(t, h)
        if c:
            conflicts[(t, h)] = c
        if n is None:
            unresolved[t][h] += 1
            return "?%d" % h
        return n

    settled = []      # every name the record evidence changed, with why

    def settle(t, h, capture_name, evidence):
        """Decide one hash. `evidence` is a Counter of record names seen where this hash sits.
        Ambiguous = more than one candidate name, or the capture's name is not the sole raw-h name."""
        cands = candidates(t, h)
        sole_raw = [n for n in cands if raw_of[t][n] == h]
        unamb = (capture_name is not None and not capture_name.startswith("?")
                 and cands == [capture_name] and sole_raw == [capture_name])
        if unamb:
            return capture_name
        ev = {n: c for n, c in evidence.items() if n in cands}
        if (capture_name is None or capture_name.startswith("?")) and len(sole_raw) == 1 and not ev:
            settled.append({"type": t, "hash": h, "capture_name": capture_name, "record_name": sole_raw[0],
                            "candidates": cands, "evidence": dict(evidence.most_common(5)),
                            "how": "UNRESOLVED in every capture; the one name whose raw hash is exactly h "
                                   "(historical rename list); record evidence, if any, is not hash-consistent"})
            return sole_raw[0]
        if len(ev) == 1:
            pick = next(iter(ev))
            if pick != capture_name:
                settled.append({"type": t, "hash": h, "capture_name": capture_name, "record_name": pick,
                                "candidates": cands, "evidence": dict(evidence.most_common(5)),
                                "how": "record names exactly one hash-consistent candidate"})
            return pick
        if capture_name is None or capture_name.startswith("?"):
            if len(evidence) == 1:
                pick = next(iter(evidence))
                settled.append({"type": t, "hash": h, "capture_name": capture_name, "record_name": pick,
                                "candidates": cands, "evidence": dict(evidence),
                                "how": "UNRESOLVED hash; record unanimous but name NOT hash-consistent"})
                return pick
        if len(cands) > 1:
            notes["ambiguous_unsettled"].append({"type": t, "hash": h, "used": capture_name,
                                                 "candidates": cands, "evidence": dict(evidence.most_common(5))})
        return capture_name if capture_name is not None else "?%d" % h

    # ---- features (needed for tiles' region) ----
    feats = objs.features()
    feat_by_uid = {f["uid"]: f for f in feats}
    farr = grid.arrays.get("tileFeature", [0xFFFF] * grid.tiles)

    # ---- tiles ----
    rec_tiles = {int(r["tile"]): r for r in (record.get("tiles") or [])}
    bev = collections.defaultdict(collections.Counter)
    for i, h in enumerate(grid.arrays["tileBiome"]):
        if i in rec_tiles:
            bev[h][rec_tiles[i]["biome"]] += 1
    bname = {h: settle("BiomeDef", h, nm("BiomeDef", h), bev[h]) for h in set(grid.arrays["tileBiome"])}
    biome_names = [bname[h] for h in grid.arrays["tileBiome"]]
    tiles = []
    for i in range(grid.tiles):
        rr = rec_tiles.get(i, {})
        fu = farr[i]
        tiles.append({
            "tile": i,
            "lat": rr.get("lat", ""), "lon": rr.get("lon", ""), "arc": rr.get("arc", ""),
            "bearing": rr.get("bearing", ""),
            "elev_m": "%d" % (grid.arrays["tileElevation"][i] - 8192),
            "temp_c": "%.1f" % ((grid.arrays["tileTemperature"][i] - 3000) / 10.0),
            "rain_mm": "%d" % grid.arrays["tileRainfall"][i],
            "biome": biome_names[i],
            "water": rr.get("water", ""), "river_flow": rr.get("river_flow", ""),
            "region": (feat_by_uid[fu]["name"] if fu in feat_by_uid else ""),
            "hilliness": "%d" % grid.arrays["tileHilliness"][i],
            "swampiness": "%.2f" % (grid.arrays["tileSwampiness"][i] / 255.0),
        })
    if rec_tiles and len(rec_tiles) != grid.tiles:
        notes["warnings"].append("record tiles CSV has %d rows, save %d tiles - geometry columns blank where missing"
                                 % (len(rec_tiles), grid.tiles))

    # ---- links ----
    links = {}
    rec_edge = {}
    for r in record.get("links") or []:
        rec_edge[(r["kind"], frozenset((int(r["a"]), int(r["b"]))))] = r["def"]
    for kind, dtype in (("river", "RiverDef"), ("road", "RoadDef")):
        o_name, a_name, d_name, _ = worldview.LINKS[kind]
        ob, ab, db = grid._read_array(o_name), grid._read_array(a_name), grid._read_array(d_name)
        rows, broken = [], []
        if ob is not None and ab is not None and db is not None:
            import struct
            origins = struct.unpack("<%dI" % (len(ob) // 4), ob)
            hashes = struct.unpack("<%dH" % (len(db) // 2), db)
            for o, s, h in zip(origins, ab, hashes):
                ns = geom.neighbours(o)
                if s >= len(ns):
                    broken.append({"origin": o, "slot": s, "hash": h})
                    continue
                rows.append((o, ns[s], h))
        if broken:
            notes["links_broken"].extend(broken)
        ev = collections.defaultdict(collections.Counter)
        for a, b, h in rows:
            k = (kind, frozenset((a, b)))
            if k in rec_edge:
                ev[h][rec_edge[k]] += 1
        lname = {h: settle(dtype, h, nm(dtype, h), ev[h]) for h in {r[2] for r in rows}}
        links[kind] = [(a, b, lname[h]) for a, b, h in rows]
    rdist = worldview.read_river_distances(grid)
    links_rows = _order_links(links, record.get("links") or [], rdist)

    # ---- mutators ----
    per_tile = collections.OrderedDict()
    entries = grid.mutator_entries()
    rec_mut = {int(r["tile"]): set(m for m in r["mutators"].split(";") if m) for r in (record.get("mutators") or [])}
    mev = collections.defaultdict(collections.Counter)
    for t, h in entries:
        for n in rec_mut.get(t, ()):
            mev[h][n] += 1
    # evidence for a mutator hash = record names on the same tiles that are hash-consistent with h;
    # settle() keeps only candidates, so unrelated co-located mutators do not vote
    mname = {}
    for h in {h for _, h in entries}:
        cands = set(candidates("TileMutatorDef", h))
        cn = nm("TileMutatorDef", h)
        ev = collections.Counter({n: c for n, c in mev[h].items() if n in cands})
        mname[h] = settle("TileMutatorDef", h, cn, ev)
    for t, h in entries:
        per_tile.setdefault(t, []).append(mname[h])
    mutators = [{"tile": t, "mutators": ";".join(per_tile[t])} for t in sorted(per_tile)]

    # ---- landmarks ----
    rec_lm = {(int(r["tile"]), r["landmark"]): r.get("why", "") for r in (record.get("landmarks") or [])}
    landmarks = []
    for m in objs.landmarks():
        if m["layer"] != 0:
            notes["landmarks_off_surface"].append(m)
            continue
        landmarks.append({"tile": m["tile"], "landmark": m["def"],
                          "why": rec_lm.get((m["tile"], m["def"]), ""), "name": m["name"] or ""})
    landmarks.sort(key=lambda r: r["tile"])

    # ---- factions ----
    ideos = objs.ideos()
    factions = []
    fac_by_ref = {}
    for f in objs.factions():
        ide = ideos.get(f["primaryIdeo"] or "", {})
        row = {"ref": f["ref"], "loadID": f["loadID"], "def": f["def"], "name": f["name"] or "",
               "primary_ideo": f["primaryIdeo"] or "", "ideo_name": ide.get("name") or "",
               "ideo_culture": ide.get("culture") or "", "hidden": f["hidden"] or "",
               "relations": ";".join("%s:%s:%s" % r for r in f["relations"])}
        factions.append(row)
        fac_by_ref[f["ref"]] = row

    # ---- settlements ----
    rec_set = {(r["name"], r["faction_def"]): r.get("why", "") for r in (record.get("settlements") or [])}
    settlements, player = [], []
    for s in objs.settlements():
        fr = fac_by_ref.get(s["faction"])
        if fr is None:
            notes["settlement_faction_unknown"].append({"id": s["id"], "faction": s["faction"]})
            fr = {"def": "?" + (s["faction"] or ""), "name": ""}
        rr = rec_tiles.get(s["tile"], {})
        row = {"id": s["id"], "faction_def": fr["def"], "faction": fr["name"], "name": s["name"] or "",
               "tile": s["tile"], "lat": rr.get("lat", ""), "lon": rr.get("lon", ""), "arc": rr.get("arc", ""),
               "biome": biome_names[s["tile"]] if 0 <= s["tile"] < grid.tiles else "",
               "why": rec_set.get((s["name"], fr["def"]), "")}
        if s["layer"] != 0:
            notes["settlements_off_surface"].append(row)
            continue
        (player if fr["def"] == "PlayerColony" else settlements).append(row)
    notes["player_settlements"] = player

    # ---- features ----
    ftiles = collections.Counter(farr)
    features = [{"uid": f["uid"], "def": f["def"], "name": f["name"] or "", "drawCenter": f["drawCenter"] or "",
                 "size": f["size"] or "", "tiles": ftiles.get(f["uid"], 0)} for f in feats]

    # ---- landforms + world info ----
    landforms, info = _landforms_and_info(grid.text)

    layers = {"tiles": tiles, "links": links_rows, "mutators": mutators, "landmarks": landmarks,
              "settlements": settlements, "factions": factions, "features": features, "landforms": landforms}
    counts = {"tiles": grid.tiles, "river_entries": len(links["river"]), "road_entries": len(links["road"]),
              "mutator_entries": len(entries), "mutator_tiles": len(per_tile),
              "landmarks": len(landmarks), "settlements_npc": len(settlements),
              "settlements_player": len(player), "factions": len(factions), "features": len(features),
              "landforms": len(landforms)}
    notes["unresolved_in_captures"] = {t: dict(c) for t, c in unresolved.items() if c}
    notes["settled"] = settled
    notes["conflicts"] = [{"type": t, "hash": h, "hits": c} for (t, h), c in sorted(conflicts.items())]
    return layers, counts, info, notes


def _order_links(links, rec_links, rdist):
    """Rivers first then roads (w9 stage 2 contract: rivers mouth-first, in file order).
    An edge the record shares keeps the record's position and orientation; a new river edge
    follows, ordered by river distance of its nearer endpoint (low = nearer the mouth)."""
    out = []
    for kind in ("river", "road"):
        cur = {}
        for a, b, d in links[kind]:
            cur[frozenset((a, b))] = (a, b, d)
        done = set()
        for r in rec_links:
            if r.get("kind") != kind:
                continue
            a, b = int(r["a"]), int(r["b"])
            k = frozenset((a, b))
            if k in cur and k not in done:
                out.append({"kind": kind, "a": a, "b": b, "def": cur[k][2]})
                done.add(k)
        rest = [v for k, v in cur.items() if k not in done]
        if kind == "river" and rdist:
            rest.sort(key=lambda v: (min(rdist[v[0]], rdist[v[1]]), v[0], v[1]))
        else:
            rest.sort(key=lambda v: (v[0], v[1]))
        out.extend({"kind": kind, "a": a, "b": b, "def": d} for a, b, d in rest)
    return out


def _landforms_and_info(text):
    rows, info = [], {}
    a = text.find('<li Class="GeologicalLandforms.LandformData">')
    if a >= 0:
        b = text.find("</tileData>", a)
        blk = ET.fromstring(text[text.find("<tileData>", a):b + len("</tileData>")])
        keys = [k.text for k in blk.find("keys")]
        for k, v in zip(keys, blk.find("values")):
            lfs = v.find("landforms")
            bvs = v.find("biomeVariants")
            rows.append({"tile": int(k), "topology": v.findtext("topology") or "",
                         "topologyDirection": v.findtext("topologyDirection") or "",
                         "landforms": ";".join(x.text or "" for x in lfs) if lfs is not None else "",
                         "biomeVariants": ";".join(x.text or "" for x in bvs) if bvs is not None else ""})
        rows.sort(key=lambda r: r["tile"])

    w0 = text.find("<world>")
    sub = text[w0:] if w0 >= 0 else text
    for tag in ("info", "worldPresetName", "axialTilt", "worldGenerationData"):
        i = sub.find("<%s>" % tag)
        if i >= 0:
            info[tag] = simple_from(sub, tag)
    lt = re.search(r'<li Class="RimMandrake\.FlowWorks\.LiquidTypes\.RM_WorldComponent_LiquidTags"\s*(/>|>(.*?)</li>)',
                   text, re.S)
    info["liquid_worldTags"] = ("component absent" if not lt else
                                "component present, EMPTY (self-closing element)" if lt.group(1) == "/>" else
                                lt.group(2).strip()[:2000])
    return rows, info


def simple_from(text, tag):
    i = text.find("<%s>" % tag)
    j = text.find("</%s>" % tag, i)
    el = ET.fromstring(text[i:j + len(tag) + 3])
    if len(el) == 0:
        return el.text
    out = {}
    for c in el:
        if len(c) == 0:
            out[c.tag] = c.text
        else:
            out[c.tag] = [ET.tostring(x, encoding="unicode").strip() if len(x) else x.text for x in c]
    return out


# =============================================================================
# port (rename map, then retired-mutator port map) and resolution on the profile
# =============================================================================
NAME_FIELDS = {"tiles": [("biome", "BiomeDef")], "links": [("def", None)],
               "mutators": [("mutators", "TileMutatorDef")], "landmarks": [("landmark", "LandmarkDef")],
               "settlements": [("faction_def", "FactionDef"), ("biome", "BiomeDef")],
               "factions": [("def", "FactionDef")], "features": [("def", "FeatureDef")]}


def port(layers, rename, portmap):
    """Copy of layers with names mapped. Returns (ported, applied) where applied counts
    every (layer, step, old, new). new=None in the port map leaves the name in place (reported)."""
    applied = collections.Counter()
    out = {}
    for layer, rows in layers.items():
        fields = NAME_FIELDS.get(layer, [])
        new_rows = []
        for r in rows:
            r = dict(r)
            for f, dtype in fields:
                if layer == "links":
                    dtype = "RiverDef" if r["kind"] == "river" else "RoadDef"
                vals = r[f].split(";") if layer == "mutators" else [r[f]]
                res = []
                for v in vals:
                    n = v
                    hist = HISTORICAL_RENAMES.get(dtype, {})
                    if n in hist:
                        applied[(layer, "historical_rename", n, hist[n][0])] += 1
                        n = hist[n][0]
                    if n in rename:
                        applied[(layer, "rename_map", n, rename[n])] += 1
                        n = rename[n]
                    pm = portmap.get(dtype, {})
                    if n in pm:
                        if pm[n]:
                            applied[(layer, "port_map", n, pm[n])] += 1
                            n = pm[n]
                        else:
                            applied[(layer, "port_map_NOT_PORTED", n, "")] += 1
                    res.append(n)
                r[f] = ";".join(res) if layer == "mutators" else res[0]
            new_rows.append(r)
        out[layer] = new_rows
    return out, applied


def resolve_on_profile(layers, captures, src_idx, profile):
    """{(type, name): (count, packageId, status)} for every def name the ported files carry."""
    seen = collections.Counter()
    for layer, rows in layers.items():
        for f, dtype in NAME_FIELDS.get(layer, []):
            for r in rows:
                t = dtype or ("RiverDef" if r["kind"] == "river" else "RoadDef")
                for v in (r[f].split(";") if layer == "mutators" else [r[f]]):
                    if v:
                        seen[(t, v)] += 1
    out = {}
    for (t, n), c in seen.items():
        pid = captures.pkg.get(t, {}).get(n) or src_idx.get(n) or ""
        if n.startswith("?"):
            st = "UNRESOLVED_HASH"
        elif not pid:
            st = "NO_SOURCE"
        elif pid.lower() in profile:
            st = "OK"
        else:
            st = "MOD_NOT_ON_PROFILE"
        out[(t, n)] = (c, pid, st)
    return out


# =============================================================================
# identity diff
# =============================================================================
def identity_keys(layer, rows):
    """A multiset of identity tuples per layer - what 'the same world' means for that layer."""
    if rows is None:
        return None
    c = collections.Counter()
    for r in rows:
        if layer == "tiles":
            for col in ("biome", "elev_m", "temp_c", "rain_mm", "hilliness", "swampiness", "region"):
                c[(int(r["tile"]), col, str(r[col]))] += 1
        elif layer == "links":
            a, b = int(r["a"]), int(r["b"])
            c[(r["kind"], min(a, b), max(a, b), r["def"])] += 1
        elif layer == "mutators":
            for m in (r["mutators"] or "").split(";"):
                if m:
                    c[(int(r["tile"]), m)] += 1
        elif layer == "landmarks":
            c[(int(r["tile"]), r["landmark"])] += 1
        elif layer == "settlements":
            c[(int(r["tile"]), r["faction_def"], r["name"])] += 1
        elif layer == "factions":
            c[(r["def"], r["name"])] += 1
        elif layer == "features":
            c[(r["def"], r["name"])] += 1
        elif layer == "landforms":
            c[(int(r["tile"]), r["topology"], str(r["topologyDirection"]), r["landforms"], r["biomeVariants"])] += 1
    return c


def diff_layer(layer, new_rows, old_rows):
    n, o = identity_keys(layer, new_rows), identity_keys(layer, old_rows)
    if o is None:
        return {"record": "none", "new": sum(n.values())}
    add, lose = n - o, o - n
    d = {"new": sum(n.values()), "record": sum(o.values()),
         "adds": sum(add.values()), "losses": sum(lose.values()),
         "add_sample": [list(k) for k in list(add)[:8]], "loss_sample": [list(k) for k in list(lose)[:8]]}
    if layer == "tiles":
        by_col = collections.Counter(k[1] for k in add)
        d["tiles_changed_by_column"] = dict(by_col)
        tr = collections.Counter()
        old_b = {k[0]: k[2] for k in o if k[1] == "biome"}
        for k in add:
            if k[1] == "biome":
                tr[(old_b.get(k[0], ""), k[2])] += 1
        d["biome_transitions_top"] = [[a, b, c] for (a, b), c in tr.most_common(15)]
        d.pop("add_sample"); d.pop("loss_sample")
    if layer == "links":
        for kind in ("river", "road"):
            nk = {(k[1], k[2]) for k in n if k[0] == kind}
            ok = {(k[1], k[2]) for k in o if k[0] == kind}
            d[kind] = {"edges_save": len(nk), "edges_record": len(ok), "shared_topology": len(nk & ok),
                       "added_edges": len(nk - ok), "lost_edges": len(ok - nk),
                       "def_changed_on_shared": sum(1 for k in add if k[0] == kind and (k[1], k[2]) in ok)}
    if layer == "mutators":
        d["tiles_save"] = len({k[0] for k in n})
        d["tiles_record"] = len({k[0] for k in o})
    if layer in ("landmarks", "settlements"):
        if layer == "landmarks":
            nt = {k[0]: k[1] for k in n}
            ot = {k[0]: k[1] for k in o}
            d["retyped_same_tile"] = sum(1 for t in set(nt) & set(ot) if nt[t] != ot[t])
            d["tiles_only_in_save"] = len(set(nt) - set(ot))
            d["tiles_only_in_record"] = len(set(ot) - set(nt))
        else:
            nn = {(k[2], k[1]): k[0] for k in n}
            on = {(k[2], k[1]): k[0] for k in o}
            moved = [[k[0], k[1], on[k], nn[k]] for k in set(nn) & set(on) if nn[k] != on[k]]
            d["moved_same_name_faction"] = len(moved)
            d["moved_sample"] = moved[:8]
            d["names_only_in_save"] = len(set(nn) - set(on))
            d["names_only_in_record"] = len(set(on) - set(nn))
    return d


# =============================================================================
# write
# =============================================================================
HEADERS = {
    "tiles": ["tile", "lat", "lon", "arc", "bearing", "elev_m", "temp_c", "rain_mm", "biome", "water",
              "river_flow", "region", "hilliness", "swampiness"],
    "links": ["kind", "a", "b", "def"],
    "mutators": ["tile", "mutators"],
    "landmarks": ["tile", "landmark", "why", "name"],
    "settlements": ["id", "faction_def", "faction", "name", "tile", "lat", "lon", "arc", "biome", "why"],
    "factions": ["ref", "loadID", "def", "name", "primary_ideo", "ideo_name", "ideo_culture", "hidden", "relations"],
    "features": ["uid", "def", "name", "drawCenter", "size", "tiles"],
    "landforms": ["tile", "topology", "topologyDirection", "landforms", "biomeVariants"],
}


def csv_text(layer, rows):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=HEADERS[layer], lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k, "") for k in HEADERS[layer]})
    return buf.getvalue()


def write_set(out_dir, layers, info=None):
    os.makedirs(out_dir, exist_ok=True)
    for layer in LAYERS:
        with open(os.path.join(out_dir, "ASHKARR_WORLDMAP_%s.csv" % layer), "w", encoding="utf-8", newline="") as fh:
            fh.write(csv_text(layer, layers[layer]))
    if info is not None:
        with open(os.path.join(out_dir, "world_info.json"), "w", encoding="utf-8") as fh:
            json.dump(info, fh, indent=1, ensure_ascii=False)


def read_set(d):
    return {layer: read_csv(os.path.join(d, "ASHKARR_WORLDMAP_%s.csv" % layer)) for layer in LAYERS}


def roundtrip(layers, out_dir):
    """Re-read written files; every layer's identity multiset must equal the decode's."""
    back = read_set(out_dir)
    return {l: (identity_keys(l, layers[l]) == identity_keys(l, back[l])) for l in LAYERS}


# =============================================================================
# main
# =============================================================================
def save_mod_ids(path):
    with open(path, encoding="utf-8", errors="surrogateescape") as fh:
        head = fh.read(200000)
    a, b = head.find("<modIds>"), head.find("</modIds>")
    if a < 0 or b < a:
        raise SystemExit("REFUSING: no <modIds> block in the first 200000 chars of %s" % path)
    return {m.strip().lower() for m in re.findall(r"<li>(.*?)</li>", head[a:b])}


def sha16(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()[:16]


def run(save, out, profile_path, dry_run, cap_root=None, record_prefix=RECORD_PREFIX, src_root=None,
        table=None, geom=None, src_idx=None, quiet=False):
    if os.path.realpath(out) == os.path.realpath(os.path.dirname(record_prefix)):
        raise SystemExit("REFUSING: --out is the committed stamp-file folder; write to a NEW folder")
    record = {l: read_csv(record_prefix + l + ".csv") for l in LAYERS}
    save_mods = save_mod_ids(save)
    if table is None:
        if cap_root is None:
            from game_paths import CAPTURES
            cap_root = CAPTURES
        table = Captures(cap_root, save_mods)
    layers, counts, info, notes = decode(save, table, record, geom=geom)
    if src_idx is None:
        src_idx = src_def_index(src_root or os.path.join(REPO, "src"))
    known = set(src_idx)
    for m in table.pkg.values():
        known.update(m)
    rename_all, portmap = read_rename_map(RENAME_MAP), read_port_map(PORT_MAP)
    # a rename row is applied only when its NEW name exists (a capture or src/ defines it): the map
    # holds placeholders such as TBD_SPLIT, and writing a name nothing defines would lose the entry
    rename = {o: n for o, n in rename_all.items() if n in known}
    notes["rename_rows_skipped_new_unknown"] = sorted([o, n] for o, n in rename_all.items() if n not in known)
    ported, applied = port(layers, rename, portmap)
    profile = read_profile(profile_path) if profile_path and os.path.exists(profile_path) else set()
    res = resolve_on_profile(ported, table, src_idx, profile)
    diffs = {l: diff_layer(l, layers[l], record[l]) for l in LAYERS}
    info = dict(info)
    info["_provenance"] = {"save": save, "save_sha256_16": sha16(save), "save_modIds": len(save_mods),
                           "captures_ranked": table.ranked, "profile": profile_path,
                           "profile_mods": len(profile), "rename_map": RENAME_MAP, "port_map": PORT_MAP,
                           "tool": "src/RimMandrake/Utils/world_layers_export.py"}
    result = {"counts": counts, "diffs": diffs, "notes": {k: v for k, v in notes.items()},
              "applied": [[*k, v] for k, v in sorted(applied.items())],
              "profile_resolution": sorted([[t, n, c, p, s] for (t, n), (c, p, s) in res.items()],
                                           key=lambda r: (r[4] == "OK", r[0], -r[2]))}
    rt = None
    if not dry_run:
        write_set(os.path.join(out, "raw"), layers, info)
        write_set(os.path.join(out, "ported"), ported, info)
        rt = roundtrip(layers, os.path.join(out, "raw"))
        rt_ported = roundtrip(ported, os.path.join(out, "ported"))
        result["roundtrip_raw"], result["roundtrip_ported"] = rt, rt_ported
        with open(os.path.join(out, "diff.json"), "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=1, ensure_ascii=False, default=str)
        with open(os.path.join(out, "REPORT.md"), "w", encoding="utf-8") as fh:
            fh.write(report_md(result, info["_provenance"]))
    if not quiet:
        print(summary(result, dry_run))
    return result, layers, ported


def summary(r, dry):
    c = r["counts"]
    bad = [x for x in r["profile_resolution"] if x[4] != "OK"]
    s = ["%s tiles=%d rivers=%d roads=%d mutator_entries=%d (tiles %d) landmarks=%d settlements=%d npc + %d player "
         "factions=%d features=%d landforms=%d" % ("DRY-RUN" if dry else "WROTE", c["tiles"], c["river_entries"],
                                                  c["road_entries"], c["mutator_entries"], c["mutator_tiles"],
                                                  c["landmarks"], c["settlements_npc"], c["settlements_player"],
                                                  c["factions"], c["features"], c["landforms"]),
         "hashes no capture names: %s (settled: %d, ambiguous unsettled: %d) | conflicts: %d | names not OK on profile: %d (%d entries)"
         % ({t: len(v) for t, v in r["notes"]["unresolved_in_captures"].items()} or "none", len(r["notes"]["settled"]), len(r["notes"].get("ambiguous_unsettled", [])),
            len(r["notes"]["conflicts"]), len(bad), sum(x[2] for x in bad))]
    if "roundtrip_raw" in r:
        s.append("round trip raw=%s ported=%s" % (all(r["roundtrip_raw"].values()), all(r["roundtrip_ported"].values())))
    return "\n".join(s)


def report_md(r, prov):
    L = ["# World layers rescue: canonical save -> w9 stamp files", "",
         "Written by `src/RimMandrake/Utils/world_layers_export.py` (item `WORLD_LAYERS_RESCUE_THE_SAVE_HAS_MORE`).",
         "OFFLINE: the save was only read. Every number below is the tool's own count on this run.", "",
         "## Provenance", "",
         "- save: `%s` (sha256/16 `%s`, %d modIds in its header)" % (prov["save"], prov["save_sha256_16"], prov["save_modIds"]),
         "- decode captures, ranked by share of the save's modIds loaded:"]
    for c in prov["captures_ranked"]:
        L.append("  - `%s` %d mods, share %.3f" % (c["name"], c["mods"], c["share"]))
    L += ["- profile checked: `%s` (%d active mods)" % (prov["profile"], prov["profile_mods"]),
          "- `raw/` = names as the save holds them; `ported/` = the historical renames in the tool "
          "(`HISTORICAL_RENAMES`, each cited), then `naming_rename_map.csv` def rows whose new name exists, then "
          "`retired_mutators_port_map.json` (a separate, reported step)",
          "- shortHash decode: every capture, plus a collision check (Verse.ShortHashGiver raw hash, +%d bump "
          "window); an ambiguous hash is settled by the record CSV only when it names exactly one "
          "hash-consistent candidate (see Decode notes)" % BUMP, "",
          "## Counts (save)", "", "| layer | count |", "|---|---|"]
    for k, v in r["counts"].items():
        L.append("| %s | %d |" % (k, v))
    L += ["", "## Identity diff vs committed `world/ASHKARR_WORLDMAP_*.csv` (raw names)", ""]
    for l, d in r["diffs"].items():
        L.append("### %s" % l)
        L.append("```")
        L.append(json.dumps(d, ensure_ascii=False, default=str)[:3000])
        L.append("```")
    if "roundtrip_raw" in r:
        L += ["", "## Round trip (written files re-read vs decode, identity multisets)", "",
              "- raw: %s" % r["roundtrip_raw"], "- ported: %s" % r["roundtrip_ported"]]
    n = r["notes"]
    L += ["", "## Decode notes", "",
          "- hashes no capture names: `%s`" % json.dumps(n.get("unresolved_in_captures")),
          "- settled (decode differs from the best capture, or no capture names the hash) - %d:" % len(n.get("settled", []))]
    for x in n.get("settled", []):
        L.append("  - %s %s: capture `%s` -> **`%s`** (%s; candidates %s)" % (
            x["type"], x["hash"], x["capture_name"], x["record_name"], x["how"], x["candidates"]))
    L.append("- ambiguous, NOT settled (best capture's name used) - %d:" % len(n.get("ambiguous_unsettled", [])))
    for x in n.get("ambiguous_unsettled", []):
        L.append("  - %s %s: used `%s`; candidates %s; record evidence %s" % (
            x["type"], x["hash"], x["used"], x["candidates"], x["evidence"]))
    L += ["- rename-map rows skipped (new name defined nowhere): %d" % len(n.get("rename_rows_skipped_new_unknown", [])),
          "- hash conflicts between captures (%d):" % len(n.get("conflicts", []))]
    for c in n.get("conflicts", [])[:40]:
        L.append("  - %s %s: %s" % (c["type"], c["hash"], c["hits"]))
    L.append("- player settlements (excluded from the settlements file): `%s`"
             % json.dumps([(p["id"], p["name"], p["tile"]) for p in n.get("player_settlements", [])]))
    for k in ("settlement_faction_unknown", "links_broken", "landmarks_off_surface", "settlements_off_surface", "warnings"):
        if n.get(k):
            L.append("- %s: `%s`" % (k, json.dumps(n[k], default=str)[:1500]))
    L += ["", "## Port step (applied to `ported/`)", "", "| layer | step | old | new | entries |", "|---|---|---|---|---|"]
    for row in r["applied"]:
        L.append("| %s | %s | `%s` | `%s` | %d |" % tuple(row))
    bad = [x for x in r["profile_resolution"] if x[4] != "OK"]
    L += ["", "## Names in `ported/` NOT resolvable on the profile (%d names, %d entries)" % (len(bad), sum(x[2] for x in bad)),
          "", "Listed, not dropped. Status: MOD_NOT_ON_PROFILE (defining packageId known, not active), "
          "NO_SOURCE (no capture or src/ defines it), UNRESOLVED_HASH.", "",
          "| type | defName | entries | packageId | status |", "|---|---|---|---|---|"]
    for t, nme, c, p, s in bad:
        L.append("| %s | `%s` | %d | `%s` | %s |" % (t, nme, c, p, s))
    ok = [x for x in r["profile_resolution"] if x[4] == "OK"]
    L += ["", "%d names resolve on the profile (%d entries)." % (len(ok), sum(x[2] for x in ok)), ""]
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--save", help="default: Saves/%s" % SAVE_NAME)
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--profile", default=DEFAULT_PROFILE)
    ap.add_argument("--captures", help="DefDump captures root (default game_paths.CAPTURES)")
    ap.add_argument("--dry-run", action="store_true", help="decode and diff; write nothing")
    a = ap.parse_args(argv)
    save = a.save
    if not save:
        from game_paths import SAVES
        save = os.path.join(SAVES, SAVE_NAME)
    run(save, a.out, a.profile, a.dry_run, cap_root=a.captures)


if __name__ == "__main__":
    main()
