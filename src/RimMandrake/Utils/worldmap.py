#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""worldmap.py - READ the planet inside a RimWorld savegame. Writing is retired.

Both write() methods refuse (2026-08-18/19 rulings): nothing writes a painted world
into a .rws, and the map now reaches the game over the live bridge. Every DECODER
below is correct and still in use - worldview.py, worldmap_review.py, ashkarr_paint.py.

The world grid lives at savegame/game/world/grid/layers, as a list of PlanetLayers.
Only the SurfaceLayer carries real tile data; the two OrbitLayers are stubs. Each
per-tile property is its own parallel array, base64 + **raw DEFLATE**, indexed by
tile id:

    tileBiomeDeflate        2 bytes/tile   BiomeDef shortHash
    tileElevationDeflate    2 bytes/tile   signed metres
    tileTemperatureDeflate  2 bytes/tile
    tileRainfallDeflate     2 bytes/tile
    tileFeatureDeflate      2 bytes/tile   0xFFFF = none
    tilePollutionDeflate    2 bytes/tile
    tileHillinessDeflate    1 byte/tile    enum
    tileSwampinessDeflate   1 byte/tile

Those eight are PURE VALUE DATA - no ids, no back-references - which is why they are
safe to rewrite offline. Roads, rivers and mutators are graphs and are deliberately
NOT touched here.

    🔴 The shortHash table MUST come from a def dump of the SAME mod set as the save.
    A hash decoded against a different set resolves to a DIFFERENT biome rather than
    failing, so a wrong table produces a plausible, silently wrong planet.

Verified round-trip and live edit on 2026-08-15, see `worldmap.py --selftest`.
"""
import base64
import json
import os
import re
import shutil
import struct
import sys
import zlib

# --- the arrays we understand, and their element width in bytes -----------
SCALARS = {
    "tileBiome": 2,
    "tileElevation": 2,
    "tileTemperature": 2,
    "tileRainfall": 2,
    "tileFeature": 2,
    "tilePollution": 2,
    "tileHilliness": 1,
    "tileSwampiness": 1,
}
# which of them are def references, and against which def type
HASHED = {"tileBiome": "BiomeDef"}

# 🔑 ENCODINGS, calibrated against the running engine 2026-08-15.
# Every array is little-endian UNSIGNED; the physical value comes out of a
# bias/scale, which is why a naive read gives nonsense like "ocean elevation 7842".
#
#   temperature   (raw - 3000) / 10  -> degrees C     ✅ VERIFIED
#         Colony tile 1318 read raw 3067; the game's own `Outputs\Temperature Data`
#         printed "Tile avg: 6.7C"; (3067-3000)/10 = 6.70 exactly. Biome means then
#         land where they should: Tundra -1.1, BorealForest 0.4, TemperateForest 6.1.
#   rainfall      raw                -> mm/year       ✅ no transform
#         Land spans 233..2584, mean 1197 - already mm. 40 is hyper-arid desert.
#   elevation     raw - 8192         -> metres        ✅ VERIFIED 2026-08-18
#         Was "strongly supported, not proven". Now proven: jawa/world_tile_export
#         dumped the ENGINE's own elevation for all 21,872 tiles and (raw - live) is
#         the constant 8192 on every single one - min 8192.0, max 8192.0.
#   pollution     raw / 65535        -> 0..1 fraction ⚠️ HYPOTHESIS (only 0 and 3277
#         observed; 3277/65535 = 0.05). Still unproven - world_tile_export does not
#         carry pollution, so the 2026-08-18 calibration could not reach it.
#   hilliness     raw                -> enum byte     (0..5)
#   swampiness    raw                -> 0..1 fraction ⚠️ unconfirmed scale
#   feature       raw                -> index into world/features, 0xFFFF = none
#
# ⛔ Do NOT write a scalar whose encoding is marked unconfirmed. Biome, temperature,
# rainfall, elevation and swampiness are all now VERIFIED against the live engine via
# jawa/world_tile_export; pollution alone is still a hypothesis.
#
# 🔑 THE CALIBRATION RECIPE, for the next unknown field: jawa/world_tile_export dumps
# the ENGINE's own value per tile to CSV; read the raw array out of the same save and
# regress one against the other. It settled three encodings in one call and needed no
# game restart. Never guess a scale that a running game will simply tell you.
DECODE = {
    "tileTemperature": (lambda v: (v - 3000) / 10.0, lambda c: int(round(c * 10)) + 3000),
    "tileRainfall":    (lambda v: float(v),          lambda mm: int(round(mm))),
    "tileElevation":   (lambda v: float(v - 8192),   lambda m: int(round(m)) + 8192),
}

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from game_paths import DEF_DUMP                                   # noqa: E402

DEFAULT_DUMP = os.path.join(DEF_DUMP, "defs")


def load_hash_table(def_type, dump_dir=DEFAULT_DUMP):
    """shortHash -> defName for one def type, straight out of the offline dump.

    The dump carries `shortHash` on every def, so we never have to reimplement
    RimWorld's ShortHashGiver - which would be its own silent-failure surface.
    """
    # ⭐ db first — one indexed query instead of `json.load` of a whole type
    # file (TerrainDef is small, but ThingDef.json is 316 MB and this function
    # is called with whatever type the grid needs).
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from dump_manifest import hash_table
        hit = hash_table(def_type, os.path.dirname(dump_dir.rstrip("/\\")))
        if hit is not None:
            return hit
    except Exception:
        pass                      # fall through to the JSON read

    path = os.path.join(dump_dir, def_type + ".json")
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    defs = data if isinstance(data, list) else data.get("defs", data)
    fwd, rev = {}, {}
    for d in defs:
        if not isinstance(d, dict):
            continue
        h, n = d.get("shortHash"), d.get("defName")
        if h is None or n is None:
            continue
        fwd[int(h)] = n
        rev[n] = int(h)
    return fwd, rev


def _decode(b64_text):
    return zlib.decompress(base64.b64decode("".join(b64_text.split())), -15)


def _encode(raw):
    # level 9 to match what the game writes closely enough; RimWorld does not care
    # about the exact stream, only that it inflates back to the same bytes.
    c = zlib.compressobj(9, zlib.DEFLATED, -15)
    return base64.b64encode(c.compress(raw) + c.flush()).decode("ascii")


class WorldGrid(object):
    """The surface layer of one savegame's planet, decoded into python lists."""

    def __init__(self, save_path, dump_dir=DEFAULT_DUMP):
        self.save_path = save_path
        self.dump_dir = dump_dir
        with open(save_path, encoding="utf-8", errors="surrogateescape") as fh:
            self.text = fh.read()
        self._locate_surface()
        self.arrays = {}
        for name, width in SCALARS.items():
            raw = self._read_array(name)
            if raw is None:
                continue
            fmt = "<%d%s" % (len(raw) // width, "H" if width == 2 else "B")
            self.arrays[name] = list(struct.unpack(fmt, raw))
        self.tiles = len(self.arrays["tileBiome"])
        self.biome_by_hash, self.hash_by_biome = load_hash_table("BiomeDef", dump_dir)

    # -- locating ---------------------------------------------------------
    def _locate_surface(self):
        """Find the SurfaceLayer block. Orbit layers carry the SAME element names,
        so a naive search for tileBiomeDeflate finds an orbit stub and silently
        edits 488 tiles instead of the planet."""
        i = self.text.find('<li Class="SurfaceLayer">')
        if i < 0:
            raise RuntimeError("no SurfaceLayer in %s" % self.save_path)
        j = self.text.find('<li Class=', i + 10)
        if j < 0:
            j = self.text.find("</layers>", i)
        self.surf_lo, self.surf_hi = i, j

    def _span(self, name):
        tag = "<%sDeflate>" % name
        a = self.text.find(tag, self.surf_lo, self.surf_hi)
        if a < 0:
            return None
        b = self.text.find("</%sDeflate>" % name, a)
        return a + len(tag), b

    def _read_array(self, name):
        sp = self._span(name)
        return None if sp is None else _decode(self.text[sp[0]:sp[1]])

    # -- reading ----------------------------------------------------------
    def biome_names(self):
        return [self.biome_by_hash.get(h, "?%d" % h) for h in self.arrays["tileBiome"]]

    def census(self):
        out = {}
        for n in self.biome_names():
            out[n] = out.get(n, 0) + 1
        return dict(sorted(out.items(), key=lambda kv: -kv[1]))

    def unresolved(self):
        """Hashes with no def in the dump. Non-empty means the table and the save
        disagree - stop and fix that before writing anything."""
        return sorted({h for h in self.arrays["tileBiome"] if h not in self.biome_by_hash})

    # -- writing ----------------------------------------------------------
    def set_biome(self, tile_ids, biome_defname):
        if biome_defname not in self.hash_by_biome:
            raise KeyError("no BiomeDef %r in the dump" % biome_defname)
        h = self.hash_by_biome[biome_defname]
        arr = self.arrays["tileBiome"]
        for t in tile_ids:
            arr[t] = h
        return len(tile_ids)

    # -- typed access, using the calibrated encodings above ---------------
    def get(self, name, tile_id):
        """Physical value for one tile - degrees C, mm, metres - not the raw short."""
        raw = self.arrays[name][tile_id]
        return DECODE[name][0](raw) if name in DECODE else raw

    def set(self, name, tile_ids, value):
        """Set a PHYSICAL value (degrees C, mm, metres). Encodes for you."""
        if name not in DECODE:
            raise KeyError("%r has no calibrated encoding - use set_scalar() and "
                           "know what you are doing" % name)
        enc = DECODE[name][1](value)
        for t in tile_ids:
            self.arrays[name][t] = enc
        return {"array": name, "tiles": len(tile_ids), "value": value, "raw": enc}

    def set_scalar(self, name, tile_ids, value):
        if name not in self.arrays:
            raise KeyError("no array %r" % name)
        arr = self.arrays[name]
        for t in tile_ids:
            arr[t] = value
        return len(tile_ids)

    def write(self, out_path):
        raise SystemExit(
            "worldmap.write() is RETIRED. Owner's ruling 2026-08-18: nothing writes a\n"
            "painted world into a .rws - two attempts, two dead loads, every invariant\n"
            "check passed and the game still died. Owner's ruling 2026-08-19: the map\n"
            "reaches the game through the LIVE BRIDGE, not a file.\n"
            "This module stays because its DECODERS are correct and still used by\n"
            "worldview.py, worldmap_review.py and ashkarr_paint.py. Reading is fine.\n"
            "See ASHKARR_WORLD_DEFINITION.md 12 and queue/CHECK.md\n"
            "worldpaint-live-bridge-route-9d41c7.")


def _selftest(save_path, dump_dir=DEFAULT_DUMP):
    g = WorldGrid(save_path, dump_dir)
    print("tiles         %d" % g.tiles)
    print("arrays        %s" % ", ".join(sorted(g.arrays)))
    bad = g.unresolved()
    print("unresolved    %s" % (bad if bad else "none - table matches the save"))
    cen = g.census()
    for k, v in list(cen.items())[:8]:
        print("   %-26s %d" % (k, v))
    # round-trip: re-encode untouched and confirm every array survives
    tmp = save_path + ".roundtrip"
    g.write(tmp)
    h = WorldGrid(tmp, dump_dir)
    same = all(h.arrays[k] == g.arrays[k] for k in g.arrays)
    print("round-trip    %s" % ("IDENTICAL" if same else "🔴 MISMATCH"))
    os.remove(tmp)
    return same


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        p = [a for a in sys.argv[1:] if not a.startswith("--")]
        sys.exit(0 if _selftest(p[0]) else 1)
    print(__doc__)


# ---------------------------------------------------------------------------
# World OBJECTS and LANDMARKS live in plain XML, not in the deflate blobs.
# They are edited as text. Both are safe because we only ever change a TILE
# INDEX or a DEF NAME - never a loadID, never a Faction_N reference. That is
# the whole reason moving things inside one save is safe while transplanting a
# world between saves is not.
# ---------------------------------------------------------------------------

_SETTLEMENT_RE = re.compile(
    r'(<li Class="Settlement">.*?</li>)', re.S)


class WorldObjects(object):
    """Settlements and landmarks in one save, addressed by tile."""

    def __init__(self, save_path):
        self.save_path = save_path
        with open(save_path, encoding="utf-8", errors="surrogateescape") as fh:
            self.text = fh.read()

    # -- settlements ------------------------------------------------------
    def settlements(self):
        out = []
        for m in _SETTLEMENT_RE.finditer(self.text):
            blk = m.group(1)
            tile = re.search(r"<tile>(-?\d+),(\d+)</tile>", blk)
            name = re.search(r"<nameInt>(.*?)</nameInt>", blk, re.S)
            fac = re.search(r"<faction>(.*?)</faction>", blk)
            ident = re.search(r"<ID>(\d+)</ID>", blk)
            if not tile:
                continue
            out.append({
                "id": int(ident.group(1)) if ident else None,
                "tile": int(tile.group(1)),
                "layer": int(tile.group(2)),
                "name": name.group(1) if name else None,
                "faction": fac.group(1) if fac else None,
                "span": m.span(1),
            })
        return out

    def move_settlement(self, settlement_id, new_tile):
        """Retarget one settlement. Only <tile> changes - ID, faction and name
        are untouched, so nothing that references this object breaks."""
        for s in self.settlements():
            if s["id"] != settlement_id:
                continue
            a, b = s["span"]
            blk = self.text[a:b]
            new = re.sub(r"<tile>-?\d+,\d+</tile>",
                         "<tile>%d,%d</tile>" % (new_tile, s["layer"]), blk, count=1)
            self.text = self.text[:a] + new + self.text[b:]
            return {"id": settlement_id, "from": s["tile"], "to": new_tile}
        raise KeyError("no settlement with ID %r" % settlement_id)

    # -- landmarks --------------------------------------------------------
    def _landmark_spans(self):
        lo = self.text.find("<landmarks>")
        lo = self.text.find("<landmarks>", lo + 1)   # the inner dict
        hi = self.text.find("</landmarks>", lo)
        ks = self.text.find("<keys>", lo), self.text.find("</keys>", lo)
        vs = self.text.find("<values>", lo), self.text.find("</values>", lo)
        return lo, hi, ks, vs

    def landmarks(self):
        lo, hi, ks, vs = self._landmark_spans()
        keys = re.findall(r"<li>(-?\d+),(\d+)</li>", self.text[ks[0]:ks[1]])
        vals = re.findall(r"<li>\s*<def>(.*?)</def>\s*<name>(.*?)</name>\s*</li>",
                          self.text[vs[0]:vs[1]], re.S)
        return [{"tile": int(t), "layer": int(l), "def": d, "name": n}
                for (t, l), (d, n) in zip(keys, vals)]

    def move_landmark(self, old_tile, new_tile):
        lo, hi, ks, vs = self._landmark_spans()
        seg = self.text[ks[0]:ks[1]]
        if "<li>%d," % old_tile not in seg:
            raise KeyError("no landmark on tile %d" % old_tile)
        seg2 = re.sub(r"<li>%d,(\d+)</li>" % old_tile,
                      lambda m: "<li>%d,%s</li>" % (new_tile, m.group(1)), seg, count=1)
        self.text = self.text[:ks[0]] + seg2 + self.text[ks[1]:]
        return {"from": old_tile, "to": new_tile}

    def retype_landmark(self, tile, new_defname):
        """Change WHAT a landmark is, in place. ⚠️ The runtime AddLandmark() also
        rolls LandmarkDef.mutatorChances; editing the def here does NOT, so the
        landmark changes and its terrain features do not follow."""
        marks = self.landmarks()
        idx = next((i for i, m in enumerate(marks) if m["tile"] == tile), None)
        if idx is None:
            raise KeyError("no landmark on tile %d" % tile)
        lo, hi, ks, vs = self._landmark_spans()
        seg = self.text[vs[0]:vs[1]]
        n = -1

        def sub(m):
            nonlocal n
            n += 1
            return m.group(0) if n != idx else m.group(0).replace(
                "<def>%s</def>" % marks[idx]["def"], "<def>%s</def>" % new_defname, 1)

        seg2 = re.sub(r"<li>\s*<def>.*?</def>\s*<name>.*?</name>\s*</li>", sub, seg, flags=re.S)
        self.text = self.text[:vs[0]] + seg2 + self.text[vs[1]:]
        return {"tile": tile, "was": marks[idx]["def"], "now": new_defname}

    def write(self, out_path):
        raise SystemExit(
            "worldmap.write() is RETIRED. Owner's ruling 2026-08-18: nothing writes a\n"
            "painted world into a .rws - two attempts, two dead loads, every invariant\n"
            "check passed and the game still died. Owner's ruling 2026-08-19: the map\n"
            "reaches the game through the LIVE BRIDGE, not a file.\n"
            "This module stays because its DECODERS are correct and still used by\n"
            "worldview.py, worldmap_review.py and ashkarr_paint.py. Reading is fine.\n"
            "See ASHKARR_WORLD_DEFINITION.md 12 and queue/CHECK.md\n"
            "worldpaint-live-bridge-route-9d41c7.")

    # -- world FEATURES: the named regions drawn across the planet ---------
    # <li><def>Island</def><name>Caxigo Island</name>
    #     <drawCenter>(x, y, z)</drawCenter>          position on the globe
    #     <maxDrawSizeInTiles>2.4</maxDrawSizeInTiles> label size
    #     <layer>PlanetLayer_0</layer></li>
    # Which TILES belong to a feature is the separate `tileFeature` array in
    # WorldGrid (2 bytes/tile, index into this list, 0xFFFF = none).
    def _features_span(self):
        a = self.text.find("<features>")
        return a, self.text.find("</features>", a)

    def features(self):
        lo, hi = self._features_span()
        out = []
        for i, m in enumerate(re.finditer(r"<li>(.*?)</li>", self.text[lo:hi], re.S)):
            blk = m.group(1)
            g = lambda tag: (re.search(r"<%s>(.*?)</%s>" % (tag, tag), blk, re.S) or [None, None])[1]
            out.append({
                "index": i, "def": g("def"), "name": g("name"),
                "drawCenter": g("drawCenter"), "size": g("maxDrawSizeInTiles"),
                "span": (lo + m.start(1), lo + m.end(1)),
            })
        return out

    def rename_feature(self, index, new_name):
        """Rename a region. Pure cosmetics in the save, but it is what the player
        reads across the world map, so it is how a planet gets its voice."""
        f = self.features()[index]
        a, b = f["span"]
        blk = re.sub(r"<name>.*?</name>", "<name>%s</name>" % new_name,
                     self.text[a:b], count=1, flags=re.S)
        self.text = self.text[:a] + blk + self.text[b:]
        return {"index": index, "was": f["name"], "now": new_name}

    def resize_feature(self, index, size):
        f = self.features()[index]
        a, b = f["span"]
        blk = re.sub(r"<maxDrawSizeInTiles>.*?</maxDrawSizeInTiles>",
                     "<maxDrawSizeInTiles>%s</maxDrawSizeInTiles>" % size,
                     self.text[a:b], count=1, flags=re.S)
        self.text = self.text[:a] + blk + self.text[b:]
        return {"index": index, "size": size}
