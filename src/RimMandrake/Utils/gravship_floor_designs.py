#!/usr/bin/env python3
"""
gravship_floor_designs.py - render candidate FLOOR PLANS for a gravship layout, offline.

VERSION 1.0  (2026-08-27)   Project: D:/Luke/dev/Rimworld/src/RimMandrake/Utils/

Reads a ShipLayoutDefV2, assigns a TerrainDef to every deck cell under several
named design schemes, and renders each as a PNG using SWATCHES CUT FROM REAL
IN-GAME SCREENSHOTS - so the colour, the tiling frequency and the shading are the
game's, not an artist's impression of it.

WHY SWATCHES AND NOT THE SOURCE PNG
-----------------------------------
RimWorld terrain meshes carry NO UVs (`SectionLayer_Terrain.Regenerate` sets
verts, colors and tris only), so the terrain shader samples in WORLD space and
the on-screen repeat is a property of the shader, not of the 1024x1024 file.
Measured by autocorrelation on live captures: every palette terrain repeats on a
1-cell lattice with a 4-cell super-period. A 4-cell swatch therefore tiles
seamlessly and looks exactly like the game.

USAGE
    python3 gravship_floor_designs.py --layout <xml> --swatches <dir> --out <dir>
"""

import argparse
import collections
import json
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gravship_layout import Layout                       # noqa: E402

PPC_SRC = 30.1667          # measured px/cell in the source captures
SWATCH_CELLS = 4

CONDUIT = {"PowerConduit", "HiddenConduit", "VGE_AstrofuelPipe"}
LITTER = {"SteamGeyser", "VHGE_GasGeyser"}

# palette key -> (patch id the swatch came from, TerrainDef, human label)
PALETTE = {
    "CONNECT": ("B1", "AG_RustedTile",                              "rusted biotech lab tile"),
    "PLATE":   ("C2", "guy762_FloorTiles_DoomgiverFoorMetal_dark",  "metal plating (iron)"),
    "GRATE_I": ("C3", "guy762_FloorTiles_XGrate_iron",              "crossed grate (iron)"),
    "GRATE_Y": ("B4", "guy762_FloorTiles_XGrate_yellow",            "crossed grate (worn yellow)"),
    "SCAFF":   ("B2", "UCScaffoldTile",                             "scaffold tile"),
    "HULL":    ("D2", "VQE_AncientHullTile",                        "ancient hull tile"),
    "DIVOT":   ("A1", "guy762_FloorTiles_DivotedTile_rust",         "divoted tile (rust)"),
}


# ----------------------------------------------------------------- layout model

class Ship(object):
    def __init__(self, path, sizes):
        lay = Layout.load(path)
        self.lay = lay
        self.W, self.H = lay.width, lay.height
        self.deck, self.walls, self.doors = set(), set(), set()
        self.occ = {}
        self.things = collections.defaultdict(list)
        for z in range(lay.height):
            for x in range(lay.width):
                c = lay.cell(x, z)
                if c is None or c.empty():
                    continue
                if c.foundationDef:
                    self.deck.add((x, z))
                for t in c.things:
                    if t.defName in LITTER:
                        continue
                    self.things[t.defName].append((x, z))
                    if t.defName == "GravshipHull":
                        self.walls.add((x, z))
                    elif t.defName == "Door":
                        self.doors.add((x, z))
                    elif t.defName in CONDUIT:
                        pass
                    else:
                        w, h = sizes.get(t.defName, [1, 1])[:2]
                        if (t.rot or 0) % 2:
                            w, h = h, w
                        for dx in range(w):
                            for dz in range(h):
                                self.occ[(x - (w - 1) // 2 + dx,
                                          z - (h - 1) // 2 + dz)] = t.defName
        self._area = {d: max(1, sizes.get(d, [1, 1])[0] * sizes.get(d, [1, 1])[1])
                      for d in self.things}
        self._area["GravEngine"] = 9
        self.ex, self.ez = lay.gravEngineX, lay.gravEngineZ
        # a GravEngine is 3x3 and the export never contains one
        for dx in range(-1, 2):
            for dz in range(-1, 2):
                self.occ[(self.ex + dx, self.ez + dz)] = "GravEngine"

    def footprint(self, cell):
        """Area of the thing occupying `cell`, in cells."""
        return self._area.get(self.occ.get(cell), 1)

    def dilate(self, cells, r):
        out = set()
        for (x, z) in cells:
            for dx in range(-r, r + 1):
                for dz in range(-r, r + 1):
                    if abs(dx) + abs(dz) <= r:
                        out.add((x + dx, z + dz))
        return out & self.deck


# ------------------------------------------------------------------ the regions

def regions(s):
    """Every region is a set of deck cells. Later keys win in the designs."""
    r = {}
    r["engine"] = {c for c in s.deck if abs(c[0] - s.ex) <= 6 and s.ez - 7 <= c[1] <= s.ez + 7}
    r["spine"] = {c for c in s.deck if 41 <= c[0] <= 49 and c[1] > s.ez + 7}
    r["pads"] = {c for c in s.deck if c[1] <= 15}
    r["legs"] = {c for c in s.deck if 15 < c[1] < 54}
    r["pod"] = {c for c in s.deck if c[0] >= 64 and 18 <= c[1] <= 42}
    r["nacelle"] = {c for c in s.deck if c[0] >= 70 and 84 <= c[1] <= 100}
    used = set().union(*r.values())
    r["ring"] = s.deck - used
    machines = {c for c, d in s.occ.items()
                if d not in CONDUIT and d != "GravEngine"} & s.deck
    r["machine"] = machines
    # only a thing with a real footprint earns a BAY. A 1x1 grav field extender
    # or factory hopper given its own plated island reads as decoration, not
    # as heavy industry -- it was the first thing wrong with the render.
    heavy = {c for c in machines if s.footprint(c) >= 6}
    r["heavy"] = heavy
    r["bay"] = s.dilate(heavy, 2) - heavy
    r["baytrim"] = s.dilate(heavy, 3) - s.dilate(heavy, 2)
    r["threshold"] = s.dilate(s.doors, 2) & s.deck
    # the perimeter of every landing pad, and the mouth where a leg meets the ring
    pads = r["pads"]
    r["padedge"] = {c for c in pads
                    if any((c[0] + dx, c[1] + dz) not in pads
                           for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
    r["legmouth"] = {c for c in s.deck if 52 <= c[1] <= 54 and 28 <= c[0] <= 59}
    return r


# ------------------------------------------------------------------ the designs

def _base(s, R, m=None):
    m = m or {}
    for c in s.deck:
        m[c] = "CONNECT"
    return m


def _bays(s, R, m, trim="GRATE_I"):
    for c in R["baytrim"]:
        m[c] = trim
    for c in R["bay"] | R["heavy"]:
        m[c] = "PLATE"


def _core(s, R, m):
    for c in R["engine"]:
        m[c] = "SCAFF"
    for c in R["threshold"]:
        m[c] = "GRATE_Y"


def design_service_rings(s, R):
    """Rust everywhere; each heavy machine an iron-plate island ringed in iron grate."""
    m = _base(s, R)
    for c in R["pod"] | R["nacelle"]:
        m[c] = "PLATE"
    for c in R["pads"]:
        m[c] = "PLATE"
    for c in R["padedge"]:
        m[c] = "GRATE_Y"
    _bays(s, R, m)
    _core(s, R, m)
    return m


def design_hazard_lanes(s, R):
    """Marked walking routes: worn-yellow grate lanes down the spine and both legs."""
    m = _base(s, R)
    for c in R["pod"] | R["nacelle"]:
        m[c] = "PLATE"
    for c in R["pads"]:
        m[c] = "PLATE"
    _bays(s, R, m)
    lane = set()
    for (x, z) in s.deck:
        if 44 <= x <= 45 and z >= 54:
            lane.add((x, z))
        if z < 54 and x in (36, 37, 50, 51):
            lane.add((x, z))
    for c in lane:
        m[c] = "GRATE_Y"
    for c in R["legmouth"] | R["padedge"]:
        m[c] = "GRATE_Y"
    _core(s, R, m)
    return m


def design_cargo_decks(s, R):
    """Big blocks: the lower ship is all dock plating; the spine is the one processional axis."""
    m = _base(s, R)
    for c in R["legs"] | R["pads"] | R["pod"] | R["nacelle"]:
        m[c] = "PLATE"
    _bays(s, R, m)
    for c in R["spine"]:
        m[c] = "DIVOT"
    for c in R["legmouth"] | R["padedge"]:
        m[c] = "GRATE_Y"
    _core(s, R, m)
    return m


def design_stratified_hull(s, R):
    """Rust worn through to bare ancient hull; the legs never had rust at all."""
    m = _base(s, R)
    for c in R["ring"] | R["spine"]:
        x, z = c
        v = (x * 7 + z * 13) % 29
        if v < 7:
            m[c] = "HULL"
    for c in R["legs"]:
        m[c] = "HULL"
    for c in R["pod"] | R["nacelle"]:
        m[c] = "PLATE"
    for c in R["pads"]:
        m[c] = "PLATE"
    _bays(s, R, m)
    for c in R["legmouth"] | R["padedge"]:
        m[c] = "GRATE_Y"
    _core(s, R, m)
    return m


DESIGNS = [
    ("service_rings", "Service Rings",
     "Rust is the connective tissue and it reaches everywhere. Every heavy machine stands on "
     "an iron-plate island edged in iron grate; the landing pads are plate with a worn-yellow "
     "lip. Reads as one system somebody maintained bay by bay for a very long time.",
     design_service_rings),
    ("hazard_lanes", "Hazard Lanes",
     "The same bays, plus worn-yellow grate lanes running the full spine and both legs, and "
     "yellow at every leg mouth and pad lip. Reads as a working plant whose crew had marked "
     "routes and somewhere to be.", design_hazard_lanes),
    ("cargo_decks", "Cargo Decks",
     "Big blocks instead of islands: the whole lower ship - legs and pads - is dock plating, "
     "and the spine is divoted rust, the one thing used nowhere else. Reads as a hauler whose "
     "spine was the important part.", design_cargo_decks),
    ("stratified_hull", "Stratified Hull",
     "Rust worn through to bare ancient hull in patches across the ring and spine; the legs "
     "are hull and never had rust. Reads as older than its own fittings - the rust is a later "
     "layer over something that outlasted it.", design_stratified_hull),
]


# -------------------------------------------------------------------- rendering

def load_swatches(swdir, ppc):
    """One period-sized tile per palette key, resampled to `ppc` px/cell."""
    out = {}
    n = SWATCH_CELLS
    for key, (patch, defname, label) in PALETTE.items():
        im = Image.open(os.path.join(swdir, "pal_%s.png" % key)).convert("RGB")
        out[key] = im.resize((int(round(n * ppc)), int(round(n * ppc))), Image.LANCZOS)
    return out


def tiled(sw, W, H):
    t = Image.new("RGB", (W, H))
    for y in range(0, H, sw.height):
        for x in range(0, W, sw.width):
            t.paste(sw, (x, y))
    return t


def render(ship, assign, sw, ppc, bg=(58, 47, 36)):
    W = int(ship.W * ppc)
    H = int(ship.H * ppc)
    img = Image.new("RGB", (W, H), bg)
    layers = {k: tiled(v, W, H) for k, v in sw.items()}
    masks = {k: Image.new("L", (W, H), 0) for k in sw}
    drs = {k: ImageDraw.Draw(m) for k, m in masks.items()}
    for (x, z), key in assign.items():
        px = x * ppc
        py = (ship.H - 1 - z) * ppc
        drs[key].rectangle([px, py, px + ppc, py + ppc], fill=255)
    for k in sw:
        img.paste(layers[k], (0, 0), masks[k])
    d = ImageDraw.Draw(img, "RGBA")
    # machinery: a translucent slab so the floor under it still reads
    for (x, z), defn in ship.occ.items():
        if (x, z) not in ship.deck:
            continue
        px = x * ppc
        py = (ship.H - 1 - z) * ppc
        d.rectangle([px, py, px + ppc, py + ppc], fill=(20, 22, 26, 95))
    for (x, z) in ship.walls:
        px = x * ppc
        py = (ship.H - 1 - z) * ppc
        d.rectangle([px, py, px + ppc, py + ppc], fill=(112, 112, 118, 255),
                    outline=(74, 74, 80, 255))
    for (x, z) in ship.doors:
        px = x * ppc
        py = (ship.H - 1 - z) * ppc
        d.rectangle([px, py, px + ppc, py + ppc], fill=(196, 172, 96, 255))
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--layout", required=True)
    ap.add_argument("--swatches", default=os.path.join(HERE, "..", "..", "..",
                                                       "world", "_ship", "tex"))
    ap.add_argument("--sizes", default=os.path.join(HERE, "..", "..", "..",
                                                    "observed", "def_sizes.json"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--ppc", type=float, default=9.0)
    ap.add_argument("--detail-ppc", type=float, default=26.0)
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    sizes = json.load(open(os.path.normpath(args.sizes)))
    ship = Ship(args.layout, sizes)
    R = regions(ship)
    print("deck %d  walls %d  doors %d" % (len(ship.deck), len(ship.walls), len(ship.doors)))
    print("regions: " + ", ".join("%s=%d" % (k, len(v)) for k, v in sorted(R.items())))

    sw_full = load_swatches(os.path.normpath(args.swatches), args.ppc)
    sw_det = load_swatches(os.path.normpath(args.swatches), args.detail_ppc)
    # detail windows, in layout-local cells: (name, x, z, w, h)
    DETAILS = [("engine bay", 33, 82, 26, 20),
               ("north machine deck", 8, 112, 40, 22),
               ("leg + landing pad", 28, 0, 32, 20)]

    manifest = []
    for slug, title, blurb, fn in DESIGNS:
        assign = fn(ship, R)
        hist = collections.Counter(assign.values())
        img = render(ship, assign, sw_full, args.ppc)
        img.save(os.path.join(args.out, "%s.png" % slug))
        dets = []
        for dname, dx, dz, dw, dh in DETAILS:
            di = render(ship, assign, sw_det, args.detail_ppc)
            box = (int(dx * args.detail_ppc),
                   int((ship.H - dz - dh) * args.detail_ppc),
                   int((dx + dw) * args.detail_ppc),
                   int((ship.H - dz) * args.detail_ppc))
            crop = di.crop(box)
            fnm = "%s_detail_%s.png" % (slug, dname.split()[0])
            crop.save(os.path.join(args.out, fnm))
            dets.append({"name": dname, "file": fnm})
        manifest.append({"slug": slug, "title": title, "blurb": blurb,
                         "file": "%s.png" % slug, "details": dets,
                         "cells": {PALETTE[k][1]: n for k, n in hist.most_common()},
                         "labels": {PALETTE[k][1]: PALETTE[k][2] for k in hist}})
        print("%-16s %s" % (slug, dict(hist)))
    json.dump({"palette": {k: {"def": v[1], "label": v[2]} for k, v in PALETTE.items()},
               "designs": manifest},
              open(os.path.join(args.out, "manifest.json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
