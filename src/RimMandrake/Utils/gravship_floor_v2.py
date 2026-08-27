#!/usr/bin/env python3
"""
gravship_floor_v2.py - Cargo Decks, blistered and rusted. Offline renders.

VERSION 2.0  (2026-08-27)   Project: D:/Luke/dev/Rimworld/src/RimMandrake/Utils/

What changed from v1 (`gravship_floor_designs.py`):

  * ONE layout scheme, derived from Cargo Decks, plus FOUR colour treatments.
  * All grate is IRON, and it no longer means "trim" - it means the deck plating
    is GONE. Blisters are grown from a seeded value-noise field, so they are
    organic and reproducible.
  * A blister over the eat-through threshold loses its SUBSTRATE as well: the
    foundation is removed and the cell is a hole. The rightmost appendage - the
    pod pointing down and right - is eaten worst.
  * Per-cell COLOUR. RimWorld 1.6 keeps a colour per terrain cell
    (`TerrainGrid.ColorAt`, read by `SectionLayer_Terrain` and handed to
    `GetMaterial`), and it is a MULTIPLY, so every treatment can only darken.
    Walls take the same field, shifted.
  * The thrusters move to the WEST flank facing east, so the ship flies right.

Every colour is a real ColorDef, so a treatment is implementable as-is.
"""

import argparse
import collections
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gravship_layout import Layout                       # noqa: E402

CONDUIT = {"PowerConduit", "HiddenConduit", "VGE_AstrofuelPipe"}
LITTER = {"SteamGeyser", "VHGE_GasGeyser"}

PALETTE = {
    "CONNECT": ("AG_RustedTile",                             "rusted biotech lab tile"),
    "PLATE":   ("guy762_FloorTiles_DoomgiverFoorMetal_dark", "metal plating (iron)"),
    "GRATE_I": ("guy762_FloorTiles_XGrate_iron",             "crossed grate (iron)"),
    "SCAFF":   ("UCScaffoldTile",                            "scaffold tile"),
    "DIVOT":   ("guy762_FloorTiles_DivotedTile_rust",        "divoted tile (rust)"),
    "HULL":    ("VQE_AncientHullTile",                       "ancient hull tile"),
    "GROUND":  (None,                                        "the map floor, seen through a hole"),
}

# Every ColorDef the treatments may use, with the RGB the game multiplies by.
COLORS = {
    "Structure_BrownFaded":  (86, 76, 57),
    "Structure_BrownSubtle": (101, 88, 67),
    "Structure_BrownDark":   (90, 69, 38),
    "Structure_BrownDirt":   (119, 91, 50),
    "Structure_UmberBurnt":  (90, 58, 32),
    "Structure_BrownWood":   (108, 78, 55),
    "ReddishBrown":          (132, 83, 47),
    "Structure_RedSubtle":   (132, 84, 72),
    "Structure_Auburn":      (138, 51, 36),
    "Structure_Burgundy":    (91, 41, 45),
    "Structure_Sandstone":   (126, 104, 94),
    "Structure_Granite":     (105, 95, 97),
    "Structure_GreyDark":    (81, 81, 81),
    "Structure_Slate":       (70, 70, 70),
    "Structure_Marble":      (132, 135, 132),
    "Structure_GrayLight":   (166, 166, 166),
    "Structure_BrownLight":  (131, 110, 78),
    "Structure_Limestone":   (158, 153, 135),
    "Structure_Cream":       (195, 192, 176),
    "Structure_White":       (184, 184, 184),
    "Structure_Mustard":     (163, 131, 49),
    "Structure_Orange":      (167, 96, 39),
    "guy762_StructureColor_212thOrange": (170, 70, 0),
    "guy762_StructureColor_BespinBeige": (175, 150, 120),
    "guy762_StructureColor_ImpArmySlate": (110, 120, 115),
    "guy762_StructureColor_HK47Rust":    (200, 100, 50),
    "guy762_StructureColor_CinnagarIron": (90, 70, 50),
    None: (255, 255, 255),
}

# 🔴 The colour grid MULTIPLIES, so a tint can only darken. AG_RustedTile and the
# iron plating already render near (60,60,58); anything below ~140 crushes them to
# mud. FLOOR ramps therefore stay light and let hue do the work. WALLS start at
# ~(152) light grey and have the headroom, which is why they carry the theme.
# ⚠️ Kept at >=155 deliberately. The crossed grate renders (35,29,22) against the
# plating's (57,53,49); crush the plating with a 0.5 multiply and the blisters stop
# reading at all. Hue, not value, is what a floor tint may spend here.
FLOOR_LIGHT = [None, "Structure_Cream", "Structure_White",
               "guy762_StructureColor_BespinBeige", "Structure_GrayLight",
               "Structure_Limestone", "Structure_Mustard",
               "guy762_StructureColor_HK47Rust", "Structure_Orange"]
WALL_RUST = ["Structure_BrownSubtle", "Structure_BrownWood", "guy762_StructureColor_CinnagarIron",
             "Structure_BrownDark", "ReddishBrown", "Structure_UmberBurnt",
             "guy762_StructureColor_HK47Rust", "Structure_Auburn",
             "guy762_StructureColor_212thOrange"]
WALL_COLD = ["Structure_GrayLight", "Structure_Marble", "guy762_StructureColor_ImpArmySlate",
             "Structure_Granite", "Structure_GreyDark", "Structure_Slate"]


# ------------------------------------------------------------------- noise

def value_noise(shape, cell, rng, octaves=3):
    """Seeded fractal value noise in [0,1], `cell` px per lattice step."""
    H, W = shape
    out = np.zeros(shape, dtype=float)
    amp, tot, c = 1.0, 0.0, float(cell)
    for _ in range(octaves):
        gh, gw = int(H / c) + 2, int(W / c) + 2
        g = rng.random((gh, gw))
        yi = np.clip(np.arange(H) / c, 0, gh - 1.001)
        xi = np.clip(np.arange(W) / c, 0, gw - 1.001)
        y0 = yi.astype(int); x0 = xi.astype(int)
        fy = (yi - y0)[:, None]; fx = (xi - x0)[None, :]
        fy = fy * fy * (3 - 2 * fy); fx = fx * fx * (3 - 2 * fx)
        a = g[np.ix_(y0, x0)]; b = g[np.ix_(y0, x0 + 1)]
        cc = g[np.ix_(y0 + 1, x0)]; d = g[np.ix_(y0 + 1, x0 + 1)]
        out += amp * ((a * (1 - fx) + b * fx) * (1 - fy) + (cc * (1 - fx) + d * fx) * fy)
        tot += amp
        amp *= 0.5
        c *= 0.5
    return out / tot


# ------------------------------------------------------------------- the ship

class Ship(object):
    def __init__(self, path, sizes, move_thrusters=True):
        lay = Layout.load(path)
        self.W, self.H = lay.width, lay.height
        self.deck, self.walls, self.doors = set(), set(), set()
        self.occ, self.thrusters = {}, []
        self.things = collections.defaultdict(list)
        self.sizes = sizes
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
                        self._place(t.defName, x, z, t.rot or 0)
        self._area = {d: max(1, sizes.get(d, [1, 1])[0] * sizes.get(d, [1, 1])[1])
                      for d in self.things}
        self._area["GravEngine"] = 9
        self.ex, self.ez = lay.gravEngineX, lay.gravEngineZ
        self._place("GravEngine", self.ex, self.ez, 0)
        if move_thrusters:
            self.move_thrusters_west()

    def _place(self, defn, x, z, rot):
        w, h = self.sizes.get(defn, [1, 1])[:2]
        if rot % 2:
            w, h = h, w
        for dx in range(w):
            for dz in range(h):
                self.occ[(x - (w - 1) // 2 + dx, z - (h - 1) // 2 + dz)] = defn

    def move_thrusters_west(self):
        """The ship flies EAST, so the thrusters vent WEST off the western flank.

        As built they sit in the OUTER WALL LINE of the east flank (x=85, rot 3,
        exhaust venting east) - i.e. the ship was built to fly west. The mirror
        of that line on the west flank is x=6, so the thrusters take those wall
        cells, facing east, and the wall they replaced on the east comes back.
        """
        east = [c for c in self.things.get("SmallThruster", [])]
        for (x, z) in east:
            for dx in (0, 1):
                self.occ.pop((x + dx, z), None)
            self.walls.add((x, z))                       # wall line restored
        rows = sorted(z for (_, z) in east)
        self.thrusters = []
        for z in rows:
            self.walls.discard((6, z))                   # vent opening
            self._place("SmallThruster", 6, z, 1)
            self.thrusters.append((6, z))
        self.things["SmallThruster"] = self.thrusters

    def footprint(self, cell):
        return self._area.get(self.occ.get(cell), 1)

    def dilate(self, cells, r):
        out = set()
        for (x, z) in cells:
            for dx in range(-r, r + 1):
                for dz in range(-r, r + 1):
                    if abs(dx) + abs(dz) <= r:
                        out.add((x + dx, z + dz))
        return out


# --------------------------------------------------------------- the blisters

def blisters(ship, seed=20260827, cover=0.17, eat_min=26):
    """Grow organic patches of missing plating; the big ones eat through.

    Returns (grate_cells, hole_cells, blob_id_by_cell).
    """
    rng = np.random.default_rng(seed)
    n = value_noise((ship.H, ship.W), 11, rng, octaves=4)
    fine = value_noise((ship.H, ship.W), 4, rng, octaves=2)
    field = 0.72 * n + 0.28 * fine

    deck = np.zeros((ship.H, ship.W), dtype=bool)
    for (x, z) in ship.deck:
        deck[z, x] = True
    # the pod pointing down and right is eaten worst - push its field up hard
    pod = np.zeros_like(field)
    for (x, z) in ship.deck:
        if x >= 64 and 18 <= z <= 42:
            pod[z, x] = 1.0
    field = field + 0.30 * pod

    vals = field[deck]
    thr = np.quantile(vals, 1.0 - cover)
    mask = deck & (field >= thr)

    # connected components -> blobs
    lab = -np.ones(mask.shape, dtype=int)
    blobs, nid = [], 0
    for z in range(ship.H):
        for x in range(ship.W):
            if not mask[z, x] or lab[z, x] >= 0:
                continue
            stack, comp = [(x, z)], []
            lab[z, x] = nid
            while stack:
                cx, cz = stack.pop()
                comp.append((cx, cz))
                for ax, az in ((cx + 1, cz), (cx - 1, cz), (cx, cz + 1), (cx, cz - 1)):
                    if 0 <= ax < ship.W and 0 <= az < ship.H and mask[az, ax] and lab[az, ax] < 0:
                        lab[az, ax] = nid
                        stack.append((ax, az))
            blobs.append(comp)
            nid += 1

    grate, holes = set(), set()
    for comp in blobs:
        cells = set(comp)
        grate |= cells
        if len(cells) < eat_min:
            continue
        # erode twice: what survives is eaten clean through
        core = cells
        for _ in range(2):
            core = {c for c in core
                    if all((c[0] + dx, c[1] + dz) in core
                           for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
        holes |= core
    grate -= holes
    return grate, holes, blobs


# ------------------------------------------------------------------ the layout

def assign_layout(ship, grate, holes):
    """Cargo Decks, refined: blocks below, rust above, blisters everywhere."""
    R = {}
    R["engine"] = {c for c in ship.deck if abs(c[0] - ship.ex) <= 6
                   and ship.ez - 7 <= c[1] <= ship.ez + 7}
    R["spine"] = {c for c in ship.deck if 41 <= c[0] <= 49 and c[1] > ship.ez + 7}
    R["lower"] = {c for c in ship.deck if c[1] < 54}
    R["pod"] = {c for c in ship.deck if c[0] >= 64 and 18 <= c[1] <= 42}
    R["nacelle"] = {c for c in ship.deck if (c[0] <= 16 or c[0] >= 70) and 84 <= c[1] <= 100}
    heavy = {c for c, d in ship.occ.items()
             if d not in CONDUIT and d != "GravEngine" and ship.footprint(c) >= 6} & ship.deck
    R["heavy"] = heavy
    R["bay"] = (ship.dilate(heavy, 2) & ship.deck) - heavy

    m = {c: "CONNECT" for c in ship.deck}
    for c in R["lower"] | R["pod"] | R["nacelle"]:
        m[c] = "PLATE"
    for c in R["bay"] | R["heavy"]:
        m[c] = "PLATE"
    for c in R["spine"]:
        m[c] = "DIVOT"
    for c in R["engine"]:
        m[c] = "SCAFF"
    for c in grate & ship.deck:
        m[c] = "GRATE_I"
    for c in holes & ship.deck:
        m[c] = "HOLE"
    return m, R


# --------------------------------------------------------------- the colours

def _pick(ramp, t):
    i = int(np.clip(t, 0, 0.9999) * len(ramp))
    return ramp[i]


def treat_bare_metal(ship, ctx):
    """The control: no colour anywhere. What the blistering alone does."""
    return {c: None for c in ship.deck}, {c: None for c in ship.walls}


def treat_oxide_bloom(ship, ctx):
    """One rate of corrosion, hull-wide. Floors kept pale; the walls carry the brown."""
    n, f = ctx["n_big"], ctx["n_fine"]
    floor = {c: _pick(FLOOR_LIGHT[:8], 0.35 + 0.55 * n[c[1], c[0]]) for c in ship.deck}
    wall = {c: _pick(WALL_RUST[:6], 0.2 + 0.7 * n[c[1], c[0]] * (0.7 + 0.3 * f[c[1], c[0]]))
            for c in ship.walls}
    return floor, wall


def treat_bleed_down(ship, ctx):
    """Weathering with a direction: streaks along the flight axis, dark at the stern."""
    n = ctx["n_streak"]
    floor, wall = {}, {}
    for c in ship.deck:
        x, z = c
        aft = 1.0 - (x - 1) / float(ship.W - 2)
        floor[c] = _pick(FLOOR_LIGHT, 0.25 + 0.55 * (0.5 * n[z, x] + 0.5 * aft))
    for c in ship.walls:
        x, z = c
        aft = 1.0 - (x - 1) / float(ship.W - 2)
        wall[c] = _pick(WALL_RUST, 0.1 + 0.85 * (0.45 * n[z, x] + 0.55 * aft))
    return floor, wall


def treat_corrosion_halo(ship, ctx):
    """Rust as a wound. Hot at every blister lip, cold grey where the plating is sound."""
    dist, f = ctx["dist_blister"], ctx["n_fine"]
    floor, wall = {}, {}
    for c in ship.deck:
        x, z = c
        near = max(0.0, 1.0 - dist[z, x] / 10.0)
        floor[c] = _pick(FLOOR_LIGHT[1:], 0.15 + 0.8 * (0.75 * near + 0.25 * f[z, x]))
    for c in ship.walls:
        x, z = c
        near = max(0.0, 1.0 - dist[z, x] / 10.0)
        if near < 0.2:
            wall[c] = _pick(WALL_COLD, f[z, x])
        else:
            wall[c] = _pick(WALL_RUST[3:], 0.1 + 0.85 * near)
    return floor, wall


def treat_two_tone(ship, ctx):
    """Graphic, not noisy: umber ring over a cold undercarriage, hot rust only at the holes."""
    dist, f = ctx["dist_blister"], ctx["n_fine"]
    floor, wall = {}, {}
    for c in ship.deck:
        x, z = c
        if dist[z, x] <= 2:
            floor[c] = _pick(["Structure_Orange", "guy762_StructureColor_HK47Rust"], f[z, x])
        elif z < 54:
            floor[c] = _pick(["Structure_White", "Structure_Limestone", "Structure_GrayLight"], f[z, x])
        else:
            floor[c] = _pick(["guy762_StructureColor_BespinBeige", "Structure_Mustard",
                              "Structure_Orange"], f[z, x])
    for c in ship.walls:
        x, z = c
        if dist[z, x] <= 2:
            wall[c] = "guy762_StructureColor_212thOrange"
        elif z < 54:
            wall[c] = _pick(WALL_COLD[1:4], f[z, x])
        else:
            wall[c] = _pick(["Structure_UmberBurnt", "guy762_StructureColor_CinnagarIron",
                             "Structure_BrownDark"], f[z, x])
    return floor, wall


TREATMENTS = [
    ("bare_metal", "Bare Metal (control)",
     "No colour tool at all - the same blistered layout in the tiles' own colours. Everything "
     "below is measured against this, and it is a real option: the ship is already dark and "
     "oxidised without spending a single ColorDef.", treat_bare_metal),
    ("oxide_bloom", "Oxide Bloom",
     "One rate of corrosion over the whole hull, in six browns, with no edges anywhere. "
     "The ship is uniformly ancient - nothing points at anything.", treat_oxide_bloom),
    ("bleed_down", "Bleed Down",
     "Weathering with a direction: streaks run along the flight axis and pool dark at the "
     "stern, where the thrusters are. The hull remembers which way it flew.", treat_bleed_down),
    ("corrosion_halo", "Corrosion Halo",
     "Rust as a wound. Hottest orange right at the lip of every blister, cooling through "
     "brown to cold grey where the plating is still sound. The holes are what you look at.",
     treat_corrosion_halo),
    ("two_tone", "Two Tone",
     "Graphic rather than noisy: a deep umber ring over a cold grey undercarriage, with hot "
     "rust only in the two cells around each hole. Reads at map zoom.", treat_two_tone),
]


# -------------------------------------------------------------------- render

def load_swatches(swdir, ppc):
    out = {}
    n = 4
    for key, (defname, label) in PALETTE.items():
        im = Image.open(os.path.join(swdir, "pal_%s.png" % key)).convert("RGB")
        out[key] = im.resize((int(round(n * ppc)),) * 2, Image.LANCZOS)
    return out


def tiled(sw, W, H):
    t = Image.new("RGB", (W, H))
    for y in range(0, H, sw.height):
        for x in range(0, W, sw.width):
            t.paste(sw, (x, y))
    return t


def render(ship, assign, tint, wtint, sw, ppc, ground=(112, 96, 73)):
    W, H = int(ship.W * ppc), int(ship.H * ppc)
    base = Image.new("RGB", (W, H), ground)
    layers = {k: np.asarray(tiled(v, W, H), dtype=np.float32) for k, v in sw.items()}
    out = np.asarray(base, dtype=np.float32).copy()

    p = int(round(ppc))
    for (x, z), key in assign.items():
        px, py = int(x * ppc), int((ship.H - 1 - z) * ppc)
        if key == "HOLE":
            out[py:py + p, px:px + p] = layers["GROUND"][py:py + p, px:px + p] * 0.82
            continue
        col = np.array(COLORS[tint.get((x, z))], dtype=np.float32) / 255.0
        out[py:py + p, px:px + p] = layers[key][py:py + p, px:px + p] * col

    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img, "RGBA")
    for (x, z), defn in ship.occ.items():
        if (x, z) not in ship.deck or assign.get((x, z)) == "HOLE":
            continue
        px, py = x * ppc, (ship.H - 1 - z) * ppc
        d.rectangle([px, py, px + ppc, py + ppc], fill=(18, 16, 14, 92))
    for (x, z) in ship.walls:
        px, py = x * ppc, (ship.H - 1 - z) * ppc
        # measured live: a single-thickness GravshipHull renders ~(152) light grey,
        # and an umber-painted one measured (55,33,17) - a straight multiply.
        c = np.array(COLORS[wtint.get((x, z))], dtype=float) / 255.0
        base_wall = np.array([152, 152, 155], dtype=float) * c
        d.rectangle([px, py, px + ppc, py + ppc],
                    fill=tuple(int(v) for v in np.clip(base_wall, 0, 255)) + (255,),
                    outline=(40, 34, 28, 255))
    for (x, z) in ship.doors:
        px, py = x * ppc, (ship.H - 1 - z) * ppc
        d.rectangle([px, py, px + ppc, py + ppc], fill=(150, 118, 58, 255))
    for (x, z) in ship.thrusters:
        px, py = x * ppc, (ship.H - 1 - z) * ppc
        d.rectangle([px, py, px + 2 * ppc, py + ppc], fill=(214, 118, 42, 255),
                    outline=(30, 26, 22, 255))
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--layout", required=True)
    ap.add_argument("--swatches", default=os.path.join(HERE, "..", "..", "..",
                                                       "world", "_ship", "tex"))
    ap.add_argument("--sizes", default=os.path.join(HERE, "..", "..", "..",
                                                    "observed", "def_sizes.json"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=20260827)
    ap.add_argument("--cover", type=float, default=0.17)
    ap.add_argument("--ppc", type=float, default=9.0)
    ap.add_argument("--detail-ppc", type=float, default=26.0)
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    sizes = json.load(open(os.path.normpath(args.sizes)))
    ship = Ship(args.layout, sizes)
    grate, holes, blobs = blisters(ship, args.seed, args.cover)
    grate &= ship.deck
    holes &= ship.deck
    assign, R = assign_layout(ship, grate, holes)
    big = sorted((len(b) for b in blobs), reverse=True)[:8]
    print("deck %d  blisters %d blobs, %d grate cells, %d eaten through"
          % (len(ship.deck), len(blobs), len(grate), len(holes)))
    print("biggest blobs: %s" % big)
    print("thrusters now at %s (west flank, facing east)" % ship.thrusters)

    # shared noise context
    rng = np.random.default_rng(args.seed ^ 0x5EED)
    all_cells = list(ship.deck) + list(ship.walls)
    ctx = {"all_cells": all_cells,
           "n_big": value_noise((ship.H, ship.W), 22, rng, 3),
           "n_fine": value_noise((ship.H, ship.W), 6, rng, 3),
           "n_streak": value_noise((ship.H, ship.W), 30, rng, 3)}
    # streaks: stretch along x by averaging a window
    ns = ctx["n_streak"]
    k = 9
    pad = np.pad(ns, ((0, 0), (k, k)), mode="edge")
    ctx["n_streak"] = np.mean([pad[:, i:i + ns.shape[1]] for i in range(2 * k + 1)], axis=0)

    # distance to the nearest blister cell, in cells (BFS over the whole grid)
    INF = 10 ** 6
    dist = np.full((ship.H, ship.W), INF, dtype=float)
    frontier = [(x, z) for (x, z) in (grate | holes)]
    for (x, z) in frontier:
        dist[z, x] = 0
    d = 0
    while frontier:
        d += 1
        nxt = []
        for (x, z) in frontier:
            for ax, az in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1)):
                if 0 <= ax < ship.W and 0 <= az < ship.H and dist[az, ax] > d:
                    dist[az, ax] = d
                    nxt.append((ax, az))
        frontier = nxt
        if d > 40:
            break
    dist[dist >= INF] = 40
    ctx["dist_blister"] = dist

    sw_full = load_swatches(os.path.normpath(args.swatches), args.ppc)
    sw_det = load_swatches(os.path.normpath(args.swatches), args.detail_ppc)
    DETAILS = [("pod", 60, 16, 28, 30), ("stern", 0, 80, 30, 26), ("north", 8, 108, 40, 26)]

    manifest = []
    for slug, title, blurb, fn in TREATMENTS:
        tint, wtint = fn(ship, ctx)
        img = render(ship, assign, tint, wtint, sw_full, args.ppc)
        img.save(os.path.join(args.out, "%s.png" % slug))
        used = collections.Counter(list(tint.values()) + list(wtint.values()))
        dets = []
        for dname, dx, dz, dw, dh in DETAILS:
            di = render(ship, assign, tint, wtint, sw_det, args.detail_ppc)
            box = (int(dx * args.detail_ppc), int((ship.H - dz - dh) * args.detail_ppc),
                   int((dx + dw) * args.detail_ppc), int((ship.H - dz) * args.detail_ppc))
            fnm = "%s_d_%s.png" % (slug, dname)
            di.crop(box).save(os.path.join(args.out, fnm))
            dets.append({"name": dname, "file": fnm})
        manifest.append({"slug": slug, "title": title, "blurb": blurb,
                         "file": "%s.png" % slug, "details": dets,
                         "colors": used.most_common()})
        print("%-16s colours: %s" % (slug, ", ".join("%s(%d)" % kv for kv in used.most_common(6))))

    tiles = collections.Counter(assign.values())
    json.dump({"treatments": manifest,
               "tiles": {("HOLE" if k == "HOLE" else PALETTE[k][0]): v
                         for k, v in tiles.items()},
               "blisters": {"blobs": len(blobs), "grate": len(grate),
                            "holes": len(holes), "biggest": big},
               "thrusters": ship.thrusters},
              open(os.path.join(args.out, "manifest.json"), "w"), indent=1)
    print("tiles: %s" % dict(tiles))
    return 0


if __name__ == "__main__":
    sys.exit(main())
