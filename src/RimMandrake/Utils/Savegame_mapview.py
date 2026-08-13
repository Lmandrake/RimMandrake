#!/usr/bin/env python3
"""
Savegame_mapview.py  —  RimWorld 1.6 (.rws) map preview / research probe
=========================================================================

PURPOSE
-------
A first-pass utility to confirm that we can *read and understand* the in-play
map that lives inside a RimWorld savegame, and to render a quick visual
"Map Preview" from it. This is a research probe for the save-based
world-authoring pipeline (see ../save_authoring_pipeline.md and
../rimworld_file_lore.md).

WHAT IT DOES  (all verified against 03_Gravtasm__starting_save.rws, 1.6.4633)
--------------------------------------------------------------------------
  * Parses the .rws (plain XML) and locates the in-play map block under <maps>.
  * Reads map <size> = (W, 1, H).
  * Decodes the terrain grid: <terrainGrid><topGridDeflate> is base64 of a RAW
    DEFLATE stream (zlib.decompress(data, -15)) that unpacks to W*H little-endian
    uint16 values. Each uint16 is a RimWorld *shortHash* of a TerrainDef defName
    (NOT a 0..N legend index).
  * Decodes the roof grid: <roofGrid><roofsDeflate> (same encoding; 0 = no roof).
  * Scans placed things as <def>/<id>/<pos> triples and bins them by category
    (pawns / buildings / other) using position (x, 0, z).
  * Renders a PNG preview: one deterministic color per distinct terrain shortHash,
    a translucent overlay for roofed cells, and dots for pawns.
  * Emits a legend JSON/console table: distinct terrain hashes + cell counts,
    roof hashes + counts, thing-type counts, and pawn positions.

THE shortHash CAVEAT  (important, honest limitation)
----------------------------------------------------
The uint16 values are RimWorld `ShortHashGiver` hashes assigned at load time
(base StableStringHash, then per-DefType collision-adjusted across the ACTIVE
load order). They therefore CANNOT be reliably reversed to a defName from the
save text alone — you'd have to replay the exact mod list/load order to rebuild
the hash->name table. This tool:
  * always colors + counts by raw hash (works with zero assumptions), and
  * ADDITIONALLY attempts a best-effort match against vanilla TerrainDef names
    using the base StableStringHash. Any match is TENTATIVE (collisions may have
    bumped the real value) and is labeled as such. For authoritative names, use
    the live route (RimBridgeServer get_cell(s)_info) or an offline legend built
    by loading the campaign's exact mod set.

USAGE
-----
  python3 Savegame_mapview.py <path-to.rws> [--out DIR] [--scale N] [--no-image]

  Defaults: --out = alongside the save, --scale = 4 (px per cell).

Outputs (basename = save filename stem):
  <stem>_preview.png     terrain + roof + pawn render
  <stem>_legend.json     machine-readable legend + stats
  (console)              human-readable summary
"""

import sys
import os
import re
import json
import base64
import zlib
import struct
import argparse
import colorsys
from collections import Counter, defaultdict

# ---------------------------------------------------------------------------
# Vanilla TerrainDef defNames for best-effort (TENTATIVE) hash matching.
# Not exhaustive; extend as needed. Modded terrains will simply not match.
# ---------------------------------------------------------------------------
VANILLA_TERRAINS = [
    "Sand", "SoftSand", "Soil", "SoilRich", "MossyTerrain", "Gravel",
    "Mud", "Marsh", "MarshyTerrain", "Ice", "WaterDeep", "WaterShallow",
    "WaterMovingChestDeep", "WaterMovingShallow", "WaterOceanDeep",
    "WaterOceanShallow", "PackedDirt", "Concrete", "PavedTile", "Bridge",
    "Sandstone_Rough", "Sandstone_RoughHewn", "Sandstone_Smooth",
    "Granite_Rough", "Granite_RoughHewn", "Granite_Smooth",
    "Limestone_Rough", "Limestone_RoughHewn", "Limestone_Smooth",
    "Slate_Rough", "Slate_RoughHewn", "Slate_Smooth",
    "Marble_Rough", "Marble_RoughHewn", "Marble_Smooth",
    "MetalTile", "SilverTile", "GoldTile", "SterileTile", "WoodPlankFloor",
    "TileSandstone", "TileGranite", "TileLimestone", "TileSlate", "TileMarble",
    "CarpetRed", "CarpetDarkGreen", "BurnedWoodPlankFloor", "BrokenAsphalt",
    "AncientConcrete", "AncientTile", "FlagstoneSandstone", "FlagstoneGranite",
    "FlagstoneLimestone", "FlagstoneSlate", "FlagstoneMarble",
    # Odyssey / common extras (harmless if absent from the build):
    "Saltpan", "SaltFlats", "RoughStone", "SmoothStone",
]


def stable_string_hash(s: str) -> int:
    """Port of RimWorld Verse.GenText.StableStringHash."""
    if s is None:
        return 0
    num = 23
    for ch in s:
        num = (num * 31 + ord(ch)) & 0xFFFFFFFF
    # emulate C# int overflow (signed 32-bit)
    if num >= 0x80000000:
        num -= 0x100000000
    return num


def short_hash_candidates(defname: str):
    """Return plausible base shortHash values (pre collision-adjust)."""
    h = stable_string_hash(defname)
    cands = set()
    # ShortHashGiver: (ushort)(StableStringHash % 65535 + 1)
    cands.add((h % 65535) + 1)
    # alt formulations seen in the wild
    cands.add(h & 0xFFFF)
    cands.add(h % 65536)
    return {c & 0xFFFF for c in cands}


def build_vanilla_hash_map():
    m = defaultdict(list)
    for name in VANILLA_TERRAINS:
        for c in short_hash_candidates(name):
            m[c].append(name)
    return m


# ---------------------------------------------------------------------------
# .rws parsing helpers
# ---------------------------------------------------------------------------

def read_save(path: str) -> str:
    with open(path, "r", errors="replace") as fh:
        return fh.read()


def parse_map_size(text: str):
    """First <size>(W, 1, H)</size> inside <maps>."""
    seg = text
    mstart = text.find("<maps>")
    if mstart != -1:
        seg = text[mstart:]
    m = re.search(r"<size>\((\d+),\s*(\d+),\s*(\d+)\)</size>", seg)
    if not m:
        raise ValueError("Could not find map <size> under <maps>.")
    w, _, h = int(m.group(1)), int(m.group(2)), int(m.group(3))
    return w, h


def decode_deflate_grid(text: str, tag: str, expected_cells: int):
    """Decode a <tag>...base64 raw-deflate...</tag> block to a list of uint16."""
    m = re.search(r"<%s>(.*?)</%s>" % (tag, tag), text, re.S)
    if not m:
        return None
    blob = re.sub(r"\s", "", m.group(1))
    raw = zlib.decompress(base64.b64decode(blob), -15)
    if len(raw) % 2 != 0:
        raise ValueError("%s: decoded byte length %d not even (not uint16?)"
                         % (tag, len(raw)))
    vals = struct.unpack("<%dH" % (len(raw) // 2), raw)
    if len(vals) != expected_cells:
        # Not fatal — report and continue with what we have.
        print("  [warn] %s decoded %d cells, expected %d"
              % (tag, len(vals), expected_cells))
    return list(vals)


def parse_things(text: str):
    """Extract (def, id, x, z) triples for placed things (best-effort)."""
    things = []
    pat = re.compile(
        r"<def>([^<]+)</def>\s*<id>([^<]+)</id>.*?<pos>\((\d+),\s*\d+,\s*(\d+)\)</pos>",
        re.S,
    )
    for m in pat.finditer(text):
        things.append((m.group(1), m.group(2), int(m.group(3)), int(m.group(4))))
    return things


PAWN_DEFS = {"Human"}
PAWN_HINT = re.compile(r"(Human|Colonist|Mech|Animal|Pawn|Jawa)", re.I)


def categorize(defname: str) -> str:
    if defname in PAWN_DEFS or defname.startswith("Mech_"):
        return "pawn"
    if PAWN_HINT.search(defname):
        # crude; real pawns are Class-based, but Human covers the common case
        return "pawn" if defname == "Human" else "other"
    return "other"


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def color_for_index(i: int, n: int):
    """Deterministic distinct colors around the hue wheel."""
    h = (i / max(n, 1)) % 1.0
    s = 0.45 + 0.25 * ((i % 3) / 2.0)
    v = 0.55 + 0.30 * ((i % 2))
    r, g, b = colorsys.hsv_to_rgb(h, s, min(v, 1.0))
    return (int(r * 255), int(g * 255), int(b * 255))


def render_preview(size, terrain, roofs, things, out_png, scale,
                   hash_to_color):
    from PIL import Image, ImageDraw
    w, h = size
    # RimWorld origin (0,0) is bottom-left; image y grows downward -> flip z.
    img = Image.new("RGB", (w, h), (20, 20, 24))
    px = img.load()
    for idx, hv in enumerate(terrain):
        x = idx % w
        z = idx // w
        y = h - 1 - z
        px[x, y] = hash_to_color.get(hv, (60, 60, 60))
    # roof overlay (translucent dark)
    if roofs:
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        od = overlay.load()
        for idx, rv in enumerate(roofs):
            if rv != 0:
                x = idx % w
                z = idx // w
                y = h - 1 - z
                od[x, y] = (0, 0, 0, 70)
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    # upscale
    if scale != 1:
        img = img.resize((w * scale, h * scale), Image.NEAREST)
    # pawn dots
    draw = ImageDraw.Draw(img)
    for defname, _id, x, z in things:
        if categorize(defname) == "pawn":
            y = h - 1 - z
            cx, cy = x * scale + scale // 2, y * scale + scale // 2
            r = max(2, scale)
            draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                         fill=(255, 60, 60), outline=(255, 255, 255))
    img.save(out_png)
    return out_png


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="RimWorld .rws map preview probe")
    ap.add_argument("save", help="path to .rws savegame")
    ap.add_argument("--out", default=None, help="output directory")
    ap.add_argument("--scale", type=int, default=4, help="pixels per cell")
    ap.add_argument("--no-image", action="store_true",
                    help="skip PNG; only emit legend + stats")
    args = ap.parse_args()

    if not os.path.isfile(args.save):
        sys.exit("No such file: %s" % args.save)

    stem = os.path.splitext(os.path.basename(args.save))[0]
    out_dir = args.out or os.path.dirname(os.path.abspath(args.save))
    os.makedirs(out_dir, exist_ok=True)

    print("Reading %s ..." % args.save)
    text = read_save(args.save)

    w, h = parse_map_size(text)
    cells = w * h
    print("Map size: %d x %d  (%d cells)" % (w, h, cells))

    terrain = decode_deflate_grid(text, "topGridDeflate", cells)
    if terrain is None:
        sys.exit("Could not locate <topGridDeflate> terrain grid.")
    roofs = decode_deflate_grid(text, "roofsDeflate", cells)
    things = parse_things(text)

    # ---- terrain stats + best-effort names ----
    tcount = Counter(terrain)
    vhash = build_vanilla_hash_map()
    distinct = sorted(tcount.keys(), key=lambda k: -tcount[k])
    hash_to_color = {hv: color_for_index(i, len(distinct))
                     for i, hv in enumerate(distinct)}

    terrain_legend = []
    for hv in distinct:
        guesses = vhash.get(hv, [])
        terrain_legend.append({
            "shortHash": hv,
            "cells": tcount[hv],
            "pct": round(100.0 * tcount[hv] / cells, 2),
            "tentative_vanilla_name": guesses[0] if len(guesses) == 1 else
                (guesses if guesses else None),
            "color_rgb": hash_to_color[hv],
        })

    roof_legend = []
    if roofs:
        rc = Counter(roofs)
        for hv, n in rc.most_common():
            roof_legend.append({
                "shortHash": hv,
                "cells": n,
                "roofed": hv != 0,
            })

    thing_types = Counter(t[0] for t in things)
    pawns = [{"def": d, "id": i, "x": x, "z": z}
             for (d, i, x, z) in things if categorize(d) == "pawn"]

    legend = {
        "save": os.path.basename(args.save),
        "map_size": {"w": w, "h": h, "cells": cells},
        "terrain": {
            "distinct": len(distinct),
            "encoding": "topGridDeflate: base64 raw-DEFLATE -> LE uint16 "
                        "shortHash per cell (NOT a 0..N legend)",
            "name_caveat": "tentative_vanilla_name is a best-effort "
                           "StableStringHash match and may be wrong due to "
                           "ShortHashGiver collision-adjustment; authoritative "
                           "names require the live game or the exact load order.",
            "legend": terrain_legend,
        },
        "roofs": {"distinct": len(roof_legend), "legend": roof_legend},
        "things": {
            "total": len(things),
            "distinct_defs": len(thing_types),
            "top_types": thing_types.most_common(25),
            "pawn_count": len(pawns),
            "pawns": pawns[:200],
        },
    }

    legend_path = os.path.join(out_dir, "%s_legend.json" % stem)
    with open(legend_path, "w") as fh:
        json.dump(legend, fh, indent=2)

    # ---- console summary ----
    print("\n=== TERRAIN (%d distinct shortHashes) ===" % len(distinct))
    for row in terrain_legend[:30]:
        name = row["tentative_vanilla_name"]
        name = ("  ~%s?" % name) if isinstance(name, str) else ""
        print("  hash %-6d %7d cells (%5.1f%%)%s"
              % (row["shortHash"], row["cells"], row["pct"], name))
    if roof_legend:
        roofed = sum(r["cells"] for r in roof_legend if r["roofed"])
        print("\n=== ROOFS ===  roofed cells: %d (%.1f%%)"
              % (roofed, 100.0 * roofed / cells))
    print("\n=== THINGS ===  total %d, distinct defs %d, pawns %d"
          % (len(things), len(thing_types), len(pawns)))
    for d, n in thing_types.most_common(15):
        print("  %-30s %d" % (d, n))

    if not args.no_image:
        png_path = os.path.join(out_dir, "%s_preview.png" % stem)
        render_preview((w, h), terrain, roofs, things, png_path,
                       args.scale, hash_to_color)
        print("\nPreview image: %s" % png_path)
    print("Legend JSON:   %s" % legend_path)


if __name__ == "__main__":
    main()
