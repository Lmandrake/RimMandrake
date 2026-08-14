#!/usr/bin/env python3
"""
mapkit.py  —  shared terrain palette + semantic map model + renderer
====================================================================

Foundation for the map-improver practice agent (see map_agent.py). This is
the "screenshot-level" layer: we work with a SEMANTIC terrain grid — each cell
holds a real RimWorld terrain *name* we assign — NOT the load-order shortHashes
of a live save. That is deliberate: the exercise is creative worldcraft on
player-style maps, so a named grid we can reason about and color sensibly is the
right substrate (see rimworld_file_lore.md §2b for why raw-save hashes are the
wrong input for this).

The terrain vocabulary + roles are grounded in the campaign's verified
`biome_terrain_palette.md` (Table B) so anything the agent proposes uses
authentic terrain that will pass a sniff test:
  vanilla:  Sand SoftSand Soil SoilRich Gravel Mud Marsh
            WaterShallow WaterDeep WaterMovingShallow WaterMovingChestDeep
            WaterOceanShallow WaterOceanDeep
  AlphaBiomes: AB_SolidifiedLava AB_LiquidLava AB_Obsidian AB_VolcanicGravel
               AB_FineSand AB_CompactedSand AB_ForsakenRock AB_CrackedMud
  Gunk(alien): GU_RedWaterShallow GU_RedWaterDeep GU_AlienSand
  crafted:  AB_AsphaltFloor  (refinery/wreck flooring)  MetalTile (droid/mech)

Everything here is pure-stdlib + Pillow. No live game, no save mutation.
"""

import json
import colorsys

# --------------------------------------------------------------------------
# TERRAIN PALETTE
# Each terrain: sensible display color (RGB) + coarse properties used by the
# analyzer/improver. Colors chosen to read like a RimWorld map at a glance.
# props: passable, buildable, fertility(0..1.4), water(none/fresh/saline),
#        movecost(1.0 = normal; >1 slow), family (grouping for stats).
# --------------------------------------------------------------------------
TERRAIN = {
    # ---- arid / desert floors ----
    "Sand":            {"rgb": (222, 202, 150), "family": "sand",  "passable": True,  "buildable": True,  "fertility": 0.00, "water": "none",  "move": 1.15},
    "SoftSand":        {"rgb": (231, 213, 165), "family": "sand",  "passable": True,  "buildable": True,  "fertility": 0.00, "water": "none",  "move": 1.6},
    "GU_AlienSand":    {"rgb": (206, 168, 133), "family": "sand",  "passable": True,  "buildable": True,  "fertility": 0.00, "water": "none",  "move": 1.2},
    "Gravel":          {"rgb": (150, 141, 123), "family": "rock",  "passable": True,  "buildable": True,  "fertility": 0.05, "water": "none",  "move": 1.0},
    "AB_ForsakenRock": {"rgb": (128, 116, 110), "family": "rock",  "passable": True,  "buildable": True,  "fertility": 0.00, "water": "none",  "move": 1.0},
    # ---- soils (farmable) ----
    "Soil":            {"rgb": (124,  98,  66), "family": "soil",  "passable": True,  "buildable": True,  "fertility": 1.00, "water": "none",  "move": 1.0},
    "SoilRich":        {"rgb": ( 92,  70,  44), "family": "soil",  "passable": True,  "buildable": True,  "fertility": 1.40, "water": "none",  "move": 1.0},
    "MossyTerrain":    {"rgb": ( 96, 104,  60), "family": "soil",  "passable": True,  "buildable": True,  "fertility": 0.72, "water": "none",  "move": 1.0},
    # ---- wet / mud ----
    "Mud":             {"rgb": ( 82,  68,  50), "family": "mud",   "passable": True,  "buildable": False, "fertility": 0.00, "water": "fresh", "move": 1.8},
    "Marsh":           {"rgb": ( 78,  86,  58), "family": "mud",   "passable": True,  "buildable": False, "fertility": 1.10, "water": "fresh", "move": 2.0},
    "AB_CrackedMud":   {"rgb": (120, 100,  74), "family": "mud",   "passable": True,  "buildable": True,  "fertility": 0.10, "water": "none",  "move": 1.1},
    # ---- fresh water ----
    "WaterShallow":         {"rgb": ( 96, 150, 176), "family": "water", "passable": True,  "buildable": False, "fertility": 0.0, "water": "fresh",  "move": 2.6},
    "WaterDeep":            {"rgb": ( 46,  92, 130), "family": "water", "passable": False, "buildable": False, "fertility": 0.0, "water": "fresh",  "move": 99},
    "WaterMovingShallow":   {"rgb": (108, 162, 184), "family": "water", "passable": True,  "buildable": False, "fertility": 0.0, "water": "fresh",  "move": 2.6},
    "WaterMovingChestDeep": {"rgb": ( 54, 104, 142), "family": "water", "passable": False, "buildable": False, "fertility": 0.0, "water": "fresh",  "move": 99},
    # ---- saline water ----
    "WaterOceanShallow": {"rgb": ( 80, 138, 150), "family": "water", "passable": True,  "buildable": False, "fertility": 0.0, "water": "saline", "move": 2.6},
    "WaterOceanDeep":    {"rgb": ( 38,  82, 104), "family": "water", "passable": False, "buildable": False, "fertility": 0.0, "water": "saline", "move": 99},
    # ---- alien red-water (Gunk) ----
    "GU_RedWaterShallow":{"rgb": (168,  86,  84), "family": "water", "passable": True,  "buildable": False, "fertility": 0.0, "water": "fresh",  "move": 2.6},
    "GU_RedWaterDeep":   {"rgb": (120,  52,  54), "family": "water", "passable": False, "buildable": False, "fertility": 0.0, "water": "fresh",  "move": 99},
    # ---- volcanic ----
    "AB_SolidifiedLava": {"rgb": ( 58,  52,  56), "family": "volcanic", "passable": True,  "buildable": True,  "fertility": 0.0, "water": "none", "move": 1.1},
    "AB_Obsidian":       {"rgb": ( 34,  30,  40), "family": "volcanic", "passable": True,  "buildable": True,  "fertility": 0.0, "water": "none", "move": 1.0},
    "AB_VolcanicGravel": {"rgb": ( 74,  64,  60), "family": "volcanic", "passable": True,  "buildable": True,  "fertility": 0.0, "water": "none", "move": 1.05},
    "AB_LiquidLava":     {"rgb": (206,  86,  32), "family": "volcanic", "passable": False, "buildable": False, "fertility": 0.0, "water": "none", "move": 99},
    # ---- natural stone (mountain / cavern rock) ----
    "RockFace":          {"rgb": ( 62,  58,  54), "family": "mountain", "passable": False, "buildable": False, "fertility": 0.0, "water": "none", "move": 99},
    "RockRubble":        {"rgb": (110, 104,  96), "family": "rock",     "passable": True,  "buildable": True,  "fertility": 0.0, "water": "none", "move": 1.2},
    "CaveFloor":         {"rgb": ( 84,  80,  86), "family": "cave",     "passable": True,  "buildable": True,  "fertility": 0.10, "water": "none", "move": 1.0},
    # ---- crafted / exotic set-piece floors ----
    "AB_AsphaltFloor":   {"rgb": ( 70,  70,  74), "family": "crafted",  "passable": True,  "buildable": True,  "fertility": 0.0, "water": "none", "move": 0.9},
    "MetalTile":         {"rgb": (120, 122, 128), "family": "crafted",  "passable": True,  "buildable": True,  "fertility": 0.0, "water": "none", "move": 0.9},
    "AncientConcrete":   {"rgb": (138, 134, 126), "family": "crafted",  "passable": True,  "buildable": True,  "fertility": 0.0, "water": "none", "move": 0.9},
    "AB_TileObsidian":   {"rgb": ( 44,  40,  50), "family": "crafted",  "passable": True,  "buildable": True,  "fertility": 0.0, "water": "none", "move": 0.9},
}

# fallback color for any terrain name we don't know (bright magenta = "unknown")
UNKNOWN_RGB = (255, 0, 255)


def tcolor(name):
    t = TERRAIN.get(name)
    return t["rgb"] if t else UNKNOWN_RGB


def tprop(name, key, default=None):
    t = TERRAIN.get(name)
    return t.get(key, default) if t else default


# --------------------------------------------------------------------------
# THING / FEATURE markers — overlaid dots+labels for the pawn/item/set-piece
# notes the agent attaches (it does NOT paint them into terrain).
# --------------------------------------------------------------------------
FEATURE_STYLE = {
    "structure": {"rgb": (40, 40, 40),   "r": 2},   # existing built walls, etc.
    "wreck":     {"rgb": (200, 60, 40),  "r": 3},   # crashed-ship debris
    "mine":      {"rgb": (60, 40, 90),   "r": 3},   # abandoned mine entrance
    "refinery":  {"rgb": (150, 110, 30), "r": 3},   # oil/chem refinery
    "droid":     {"rgb": (30, 120, 160), "r": 3},   # dead droid / crater
    "relic":     {"rgb": (200, 170, 40), "r": 3},   # loot / artifact
    "cave":      {"rgb": (150, 90, 200), "r": 2},   # cavern mouth
    "hazard":    {"rgb": (200, 40, 120), "r": 3},   # hostile flora / spore
    "pawn":      {"rgb": (220, 30, 30),  "r": 2},   # creature to add
}


class GameMap:
    """A semantic RimWorld map: W×H grid of terrain NAMES + feature markers."""

    def __init__(self, w, h, fill="Sand", name="map"):
        self.w = w
        self.h = h
        self.name = name
        # grid[z][x] -> terrain name ; origin bottom-left like RimWorld
        self.grid = [[fill for _ in range(w)] for _ in range(h)]
        self.features = []   # list of dicts: {kind,x,z,label,note}
        self.meta = {}

    # ---- cell access ----
    def get(self, x, z):
        return self.grid[z][x]

    def set(self, x, z, name):
        if 0 <= x < self.w and 0 <= z < self.h:
            self.grid[z][x] = name

    def in_bounds(self, x, z):
        return 0 <= x < self.w and 0 <= z < self.h

    def add_feature(self, kind, x, z, label="", note=""):
        self.features.append({"kind": kind, "x": x, "z": z,
                              "label": label, "note": note})

    # ---- persistence (our own compact JSON map format) ----
    def to_dict(self):
        return {"name": self.name, "w": self.w, "h": self.h,
                "grid": self.grid, "features": self.features,
                "meta": self.meta}

    def save_json(self, path):
        with open(path, "w") as fh:
            json.dump(self.to_dict(), fh)

    @classmethod
    def from_dict(cls, d):
        m = cls(d["w"], d["h"], name=d.get("name", "map"))
        m.grid = d["grid"]
        m.features = d.get("features", [])
        m.meta = d.get("meta", {})
        return m

    @classmethod
    def load_json(cls, path):
        with open(path) as fh:
            return cls.from_dict(json.load(fh))

    def copy(self):
        return GameMap.from_dict(json.loads(json.dumps(self.to_dict())))

    # ---- stats ----
    def terrain_histogram(self):
        from collections import Counter
        c = Counter()
        for row in self.grid:
            for name in row:
                c[name] += 1
        return c


# --------------------------------------------------------------------------
# RENDERER
# --------------------------------------------------------------------------
def render(gm, path, scale=4, show_features=True, title=None,
           grid_lines=False):
    """Render a GameMap to a PNG. Origin bottom-left -> flip z for rows."""
    from PIL import Image, ImageDraw, ImageFont
    W, H = gm.w, gm.h
    margin_top = 28 if title else 0
    img = Image.new("RGB", (W * scale, H * scale + margin_top), (245, 244, 240))
    px = img.load()
    for z in range(H):
        row = gm.grid[z]
        img_z = (H - 1 - z)               # flip: RimWorld z=0 at bottom
        for x in range(W):
            r, g, b = tcolor(row[x])
            for dy in range(scale):
                yy = img_z * scale + dy + margin_top
                for dx in range(scale):
                    px[x * scale + dx, yy] = (r, g, b)

    draw = ImageDraw.Draw(img, "RGBA")
    if title:
        try:
            font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        except Exception:
            font = ImageFont.load_default()
        draw.rectangle([0, 0, W * scale, margin_top], fill=(30, 30, 34))
        draw.text((6, 5), title, fill=(240, 240, 240), font=font)

    if show_features:
        for f in gm.features:
            st = FEATURE_STYLE.get(f["kind"], {"rgb": (0, 0, 0), "r": 2})
            cx = f["x"] * scale + scale // 2
            cz = (H - 1 - f["z"]) * scale + scale // 2 + margin_top
            r = max(2, st["r"] * max(1, scale // 3))
            col = st["rgb"]
            draw.ellipse([cx - r, cz - r, cx + r, cz + r],
                         fill=col + (255,), outline=(255, 255, 255, 220))
    if hasattr(path, "write"):        # file-like buffer (render_to_image)
        img.save(path, format="PNG")
    else:
        img.save(path)
    return path


def render_to_image(gm, scale=4, show_features=True, title=None):
    """Render a GameMap and return the in-memory PIL.Image (no file written)."""
    import io
    from PIL import Image
    buf = io.BytesIO()
    render(gm, buf, scale=scale, show_features=show_features, title=title)
    buf.seek(0)
    return Image.open(buf).copy()


def render_pair(before, after, path, scale=4, titles=("BEFORE", "AFTER")):
    """Render two maps side by side into one PNG for easy comparison.

    Composited entirely in memory so no temp files need to be deleted (the
    workspace mount blocks unlink)."""
    from PIL import Image
    a = render_to_image(before, scale=scale, title=titles[0])
    b = render_to_image(after, scale=scale, title=titles[1], show_features=True)
    gap = 16
    out = Image.new("RGB", (a.width + b.width + gap, max(a.height, b.height)),
                    (255, 255, 255))
    out.paste(a, (0, 0))
    out.paste(b, (a.width + gap, 0))
    out.save(path)
    return path


def legend_swatches(path, names=None, scale=1):
    """Emit a small PNG legend of terrain name -> color actually in use."""
    from PIL import Image, ImageDraw, ImageFont
    names = names or list(TERRAIN.keys())
    rowh = 22
    W = 260
    img = Image.new("RGB", (W, rowh * len(names) + 8), (250, 250, 250))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    except Exception:
        font = ImageFont.load_default()
    for i, nm in enumerate(names):
        y = 4 + i * rowh
        draw.rectangle([6, y + 2, 26, y + 18], fill=tcolor(nm),
                       outline=(0, 0, 0))
        draw.text((32, y + 4), nm, fill=(20, 20, 20), font=font)
    img.save(path)
    return path
