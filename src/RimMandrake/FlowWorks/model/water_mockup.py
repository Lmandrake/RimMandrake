#!/usr/bin/env python3
"""Offline mockups of FlowWorks water by depth, on real ground, for the owner to pick a written target from.

Item RIMMANDRAKE_MOCK_FLOWWORKS_WATER_BY_DEPTH_ON_REAL_GROUND (owner by card 2026-11-20: "Colour and clarity now", with his
write-in "(1) and it needs to be on representative terrain (put some different textures on the ground as well as
furniture, bodies, etc)").

What one tile shows: a 5x3-cell pit dug into one bank ground, brim-full of fresh water at one depth (0.2 m sits in a
0.5 m pit), drawn top-down at 64 px a cell. In the pit: a standing colonist (1.75 m, RM_RelativeRulesMath.HeightByBand
band 2), a lying body (0.3 m, RM_UnderLiquid.CorpseMetres), a 2x2 table (fill 0.4 -> 0.8 m, BuildingMetres), a steel
stack (0.3 m, ItemMetres) and a ladder hung on the north wall (floor to rim). On the bank: a dry colonist for scale and
colour reference and a chair. The pit is drawn the way the mod draws it now: the floor is Gravel at
RM_PitReliefMath.FloorBrightness(depth notches); the north and side faces are the bank ground with the wall-face light
(RM_WallFaceMath, LightAlpha) at the RM_UnderLiquid face heights; a dark outline.

Water: every pixel under the line is passed through one candidate law `apply(rgb, metres_over)`: the floor at the full
depth, a wall face from the rim (0 under) to its foot, a thing from its foot (the full depth) up to its top. Candidate
SHIPPED is the law shipped until 2026-11-20 (approved 11-13; model/underliquid.py seen_approved_1113, Body); it reproduces the 2026-11-12 capture
BP3 (2 m of water over a 4 m pit floor) to within 0.012 per channel (`--calibrate`).

Not drawn (the same in every candidate, so they do not decide a pick): waves and ripples (0.2.0), floor shadows, the
pawn's sink offset, labels, lighting by time of day.

    python3 water_mockup.py --out <dir>          tiles and one sheet per ground, plus candidates.json
    python3 water_mockup.py --calibrate          the SHIPPED law against the measured capture colours
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import underliquid as ul  # noqa: E402  the shipped law

MOD = HERE.parent
PX = 64                                   # px per cell (vanilla sprites are 128 px for a 1.5-cell pawn: 85 px a cell)
COLS, ROWS = 8, 5                         # tile in cells: a 5x3 pit, a one-cell bank round it, two on the east
PIT = (1, 1, 6, 4)                        # x0, z0, x1, z1 cells (image rows: z0 is the north row)
DEPTHS = [0.0, 0.2, 0.5, 1.0, 1.5, 2.0, 5.0, 8.0]
HUMAN_M = 1.75
CORPSE_M = 0.3
TABLE_M = 0.8
ITEM_M = 0.3

# measured: BP3_2m.png (2026-11-12 capture, D:\ClaudeWork\rimmandrake\conductor\afk_20261112_night\live\captures)
CAPTURE = {"soil bank": (0.383, 0.298, 0.224), "water 2 m over a 4 m pit floor": (0.100, 0.157, 0.251)}


def vanilla_dir() -> Path:
    root = subprocess.run([sys.executable, str(Path.home() / "dev/Lodestar/bin/lib/agent_storage.py")],
                          capture_output=True, text=True, check=True).stdout.strip()
    d = Path(root) / "rimmandrake/scratch/vanilla_tex/ludeon.rimworld.core"
    if not d.is_dir():
        raise SystemExit(f"water_mockup: vanilla texture extract missing: {d}")
    return d


def load(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGBA")).astype(np.float32) / 255.0


# ── the candidate laws ─────────────────────────────────────────────────────────────────────────────────────────────
# Each maps (rgb[..., 3], metres_over[...]) -> rgb. metres_over <= 0 is dry (unchanged).

def _lerp(a, b, t):
    return a + (b - a) * t


BODY_SHIPPED = np.array(ul.body(ul.WATER_COLOUR), np.float32)


def law_shipped(rgb, m):
    s = np.vectorize(lambda x: ul.seen_approved_1113(ul.REFERENCE_CLARITY, float(x)))(m).astype(np.float32)[..., None]
    return _lerp(BODY_SHIPPED, rgb, s)


def rise_v(x):
    x = np.clip(x, 0.0, 1.0)
    return 1.0 - (1.0 - x) ** ul.CURVE_POWER


def law_firm(rgb, m):
    """SHIPPED's colour and deep end, with a firm start: 35% at the first centimetre, 90% at 4 m. Picked 2026-11-20 as the
    written target (design/concepts/FlowWorks/version/water_by_depth_target.json); RM_UnderLiquid.Seen now draws it."""
    a = (0.35 + 0.55 * rise_v(m / 4.0))[..., None]
    return _lerp(rgb, BODY_SHIPPED, a)


SHALLOW_TINT = np.array((0.30, 0.62, 0.74), np.float32)   # clear aqua
DEEP_TINT = np.array((0.06, 0.14, 0.31), np.float32)      # navy, a little darker than SHIPPED's body


def law_aqua(rgb, m):
    """A colour that walks from clear aqua (shallow) to navy (deep), 45% at the first centimetre to 95% at 4 m."""
    r = rise_v(m / 4.0)[..., None]
    c = _lerp(SHALLOW_TINT, DEEP_TINT, r)
    a = 0.45 + 0.50 * r
    return _lerp(rgb, c, a)


def law_aqua_soft(rgb, m):
    """AQUA's colour walk at FIRM's strength: 38% at 0.2 m to 90% at 4 m."""
    r = rise_v(m / 4.0)[..., None]
    c = _lerp(SHALLOW_TINT, DEEP_TINT, r)
    a = 0.35 + 0.55 * r
    return _lerp(rgb, c, a)


ABSORB = np.array((1.6, 0.55, 0.22), np.float32)          # per metre: red goes first, blue last (fresh water's order)
SCATTER = np.array((0.03, 0.17, 0.30), np.float32)
SHEEN = np.array((0.60, 0.82, 0.92), np.float32)


def law_clear(rgb, m):
    """Clear water: what lies under keeps its texture but loses red, then green, with depth (per-colour absorption),
    and the lost light is replaced by the water's own deep blue; a faint pale sheen marks the surface at any depth.
    Over the dark deep floor this is darkest near 2 m: past it the water's own blue outshines the floor."""
    t = np.exp(-ABSORB * m[..., None])
    out = rgb * t + SCATTER * (1.0 - t)
    return _lerp(out, SHEEN, 0.10)


def dry_above_line(law):
    """Every law leaves a point at or above the line (metres under <= 0) as it is, like RM_UnderLiquid.Seen."""
    def f(rgb, m):
        out = law(rgb, np.maximum(m, 0.0))
        return np.where((m > 0)[..., None], out, rgb)
    f.__doc__ = law.__doc__
    return f


law_firm, law_aqua, law_aqua_soft, law_clear = map(dry_above_line, (law_firm, law_aqua, law_aqua_soft, law_clear))

CANDIDATES = [
    ("SHIPPED", "Ships now (approved 11-13)", law_shipped,
     "Today's law, unchanged since his 11-13 approval: one dark blue sheet that thickens with depth."),
    ("FIRM", "Same blue, firm from the first step", law_firm,
     "Today's colour and deep end, but any water at all hides at least 35% of what lies under it."),
    ("AQUA", "Aqua shallows, navy deeps", law_aqua,
     "The colour changes with depth: clear aqua at the edge, navy by 4 m, and stronger than today at every depth."),
    ("AQUA_SOFT", "Aqua shallows, navy deeps, at FIRM's strength", law_aqua_soft,
     "AQUA's colours with FIRM's strength, so colour and strength can be judged apart."),
    ("CLEAR", "Clear water that loses red", law_clear,
     "Like real clear water: what lies under keeps its texture but loses its red, then its green, with depth, and a faint pale sheen marks the surface. Over the dark pit floor it is darkest (a dark teal) near 2 m; deeper, only the water's own blue shows, clearly bluer and brighter. Things standing in it (colonist, body, table) get the nearest cover the game can draw on them: one colour at one strength."),
    # second pass (RIMMANDRAKE_RESEARCH_FLOWWORKS_WATER_LOOK_FIRM_ALREADY_PICKED, owner card 2026-11-20 evening: "Maybe dry
    # and wet have different colors too ... Maybe more aggressive distortions on the surface will make it look more like
    # water"): FIRM's sheet, plus the ground and surface effects in FX below. Research:
    # design/concepts/FlowWorks/version/water_look_research.md
    ("WET", "FIRM, with wet ground and a waterline", law_firm,
     "FIRM's water, but the ground it covers is wet: the pit floor and walls under the water are darker and a little more saturated than the dry pit, a dark wet band runs along the bank just above the water, and a thin pale line marks where the water meets the wall."),
    ("RIPPLE", "FIRM, with a moving, distorted bottom", law_firm,
     "FIRM's water, but what lies on the bottom is visibly rippled: the floor and walls under the water are displaced by moving waves (more with depth), and pale ripple-light lines cross the floor in the shallows. Animated: three frames."),
    ("BLEND", "FIRM, wet ground plus a gentle moving bottom", law_firm,
     "The research's combination: WET's wet ground, wet band and waterline, with a gentler version of RIPPLE's moving bottom and ripple-light. Animated: three frames."),
]

# ── ground and surface effects (second pass) ───────────────────────────────────────────────────────────────────────
# Each candidate's effects; a candidate not named here draws its law alone (the first five). Numbers are mine, made for
# these pictures (px at 64 px a cell).
#   wet:       submerged ground (floor and walls under the line) x WET_VALUE in value and x WET_SAT in saturation, and a
#              wet band WET_BAND_PX wide above the line (on the walls; on the bank when the water is at the rim)
#   waterline: a pale meniscus line WATERLINE_PX wide where the water meets a wall or the rim, alpha WATERLINE_ALPHA
#   warp:      peak displacement (px) of the floor and walls under the line; grows with depth as 1 - exp(-m / 0.5)
#   ripple:    peak brightness of the ripple-light lines on the floor; fades with depth as exp(-m / 0.7)
#   frames:    animation frames drawn (1 = still)
FX = {
    "WET": {"wet": True, "waterline": True, "warp": 0.0, "ripple": 0.0, "frames": 1},
    "RIPPLE": {"wet": False, "waterline": False, "warp": 6.0, "ripple": 0.30, "frames": 3},
    "BLEND": {"wet": True, "waterline": True, "warp": 3.0, "ripple": 0.16, "frames": 3},
}
NO_FX = {"wet": False, "waterline": False, "warp": 0.0, "ripple": 0.0, "frames": 1}
WET_VALUE, WET_SAT = 0.70, 1.30
WET_BAND_PX = 10
WATERLINE_PX, WATERLINE_ALPHA = 2, 0.45
WATERLINE_COLOUR = np.array((0.80, 0.88, 0.92), np.float32)
RIPPLE_COLOUR = np.array((0.78, 0.90, 0.96), np.float32)

# How the mod would draw each effect, and what it cannot do (the card: "Each candidate must be something the game can
# draw"). Shown on the pick page and given to the judge.
MECHANISM = {
    "SHIPPED": "Drawn today: RM_ExcavationWalls.SeeThrough lays one sheet (RM_FaceMaterial.SheetMat, the body colour at "
               "alpha 1 - Seen) over the opaque floor and walls; things get RM_SubmergeDraw's cover (one colour at one "
               "alpha). Nothing moves.",
    "FIRM": "Built (6c668b36a8): the same sheet and cover with ShallowOpacity 0.35 in RM_UnderLiquid.Seen. Nothing moves.",
    "AQUA": "The same sheet with a body colour that changes with depth (one more input to SheetTint). Nothing moves.",
    "AQUA_SOFT": "As AQUA.",
    "CLEAR": "The floor and walls: a per-colour multiply would need a tint quad per band (TintMat, VertexColor shader). "
             "Things: only the one-colour cover (as drawn), never the per-colour loss.",
    "WET": "Wet ground: the floor and drowned-wall quads in SeeThrough get a TintMat quad of the ground's own darker, "
           "more saturated colour (VertexColor shader, already used for the floor shade). Wet band: one more TintMat "
           "strip, soft-edged by vertex alpha, above the waterline (on the bank at the rim). Waterline: a ShadeMat strip "
           "WATERLINE_PX wide at the line, like the walls' light. All static, one redraw per level change. Cannot: wet "
           "pawns, items or the ladder (vanilla draws them; only the cover reaches them).",
    "RIPPLE": "Moving bottom: the floor and drowned-wall quads drawn with vanilla's Map/TerrainLavaShallow distortion "
              "shader (its _DistortionAmplitude/_DistortionFrequency/_DistortionSpeed, already set by RM_LiquidLooks for "
              "tar), one material per depth band so the amplitude grows with depth [guess ~60% that the shader draws a "
              "plain ground texture without its own glow: needs a live look]. Ripple light: RM_LiquidSurface's overlay "
              "(MoteGlow, additive, drifting by material offset) with a ripple-line texture, on pit water cells, alpha "
              "by depth. Cannot: displace pawns, items, the body, the table or the ladder (vanilla draws them; no "
              "grab-pass shader in the mod), so they stay sharp on a wavy floor, as in these pictures.",
    "BLEND": "WET's static quads plus RIPPLE's distortion shader and overlay at lower amplitude and strength. Same "
             "limits: nothing standing in the water is displaced or wetted; only the floor, the walls and the bank.",
}


def fx_of(key):
    return FX.get(key, NO_FX)


def wetten(rgb):
    """Wet ground: darker and a little more saturated (rough, porous ground darkens when wet: Jensen et al. 1999)."""
    v = rgb * WET_VALUE
    mean = v.mean(-1, keepdims=True)
    return np.clip(mean + (v - mean) * WET_SAT, 0.0, 1.0)


def warp_amp(peak, m):
    return peak * (1.0 - np.exp(-np.maximum(m, 0.0) / 0.5))


def ripple_amp(peak, m):
    return peak * np.exp(-np.maximum(m, 0.0) / 0.7)


def wave_field(h, w, t, ox=0, oy=0):
    """Two crossing travelling waves (unit amplitude), t in [0, 1) one loop; world-anchored by ox, oy."""
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    x, y = x + ox, y + oy
    tau = 2 * math.pi
    dx = 0.65 * np.sin(tau * (y / 46.0 + x / 150.0 + t)) + 0.35 * np.sin(tau * (y / 21.0 - x / 67.0 + 2 * t))
    dy = 0.65 * np.sin(tau * (x / 52.0 - y / 170.0 + t)) + 0.35 * np.sin(tau * (x / 25.0 + y / 59.0 - 2 * t))
    return dx, dy


def ripple_lines(h, w, t, ox=0, oy=0, cell=40.0, width=2.2):
    """Caustic light: a net of thin bright lines on the borders of irregular cells about `cell` px across (Worley
    F2 - F1, the usual stand-in for caustics), 0..1. Each cell's point circles its jittered home once per loop, t in
    [0, 1); world-anchored by ox, oy (so neighbouring pits share one net)."""
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    x, y = (x + ox) / cell, (y + oy) / cell
    tau = 2 * math.pi
    x, y = (x + 0.22 * np.sin(tau * (y / 1.7 + t)) + 0.12 * np.sin(tau * (y / 0.6 - x / 1.1)),
            y + 0.22 * np.sin(tau * (x / 1.9 - t)) + 0.12 * np.sin(tau * (x / 0.7 + y / 1.3)))   # curved, never straight
    gx, gy = np.floor(x).astype(int), np.floor(y).astype(int)
    f1 = np.full(x.shape, 9.0, np.float32)
    f2 = np.full(x.shape, 9.0, np.float32)
    tau = 2 * math.pi
    for jy in (-1, 0, 1):
        for jx in (-1, 0, 1):
            cx, cy = gx + jx, gy + jy
            hsh = (cx * 374761393 + cy * 668265263) & 0xFFFFFF
            r1 = (hsh % 997) / 997.0
            r2 = ((hsh // 997) % 991) / 991.0
            r3 = ((hsh // 7) % 983) / 983.0
            px = cx + 0.5 + 0.35 * np.cos(tau * r1) + 0.12 * np.cos(tau * (t + r3))
            py = cy + 0.5 + 0.35 * np.sin(tau * r2) + 0.12 * np.sin(tau * (t + r3))
            d = np.sqrt((x - px) ** 2 + (y - py) ** 2)
            f2 = np.where(d < f1, f1, np.minimum(f2, d))
            f1 = np.minimum(f1, d)
    along = 0.55 + 0.45 * np.sin(tau * (x / 2.3 + y / 3.1 + t))                        # brighter and fainter runs
    return np.exp(-(f2 - f1) * cell / width) * along


def displace(region, dx, dy):
    """Bilinear sample of region at (x + dx, y + dy), clamped inside it."""
    h, w = region.shape[:2]
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    sx = np.clip(x + dx, 0, w - 1.001)
    sy = np.clip(y + dy, 0, h - 1.001)
    x0, y0 = sx.astype(int), sy.astype(int)
    fx, fy = (sx - x0)[..., None], (sy - y0)[..., None]
    a = region[y0, x0] * (1 - fx) + region[y0, x0 + 1] * fx
    b = region[y0 + 1, x0] * (1 - fx) + region[y0 + 1, x0 + 1] * fx
    return a * (1 - fy) + b * fy


def hides(fn, d):
    """How much of what lies under the water a law hides at depth d (0..1): one minus the contrast between black and
    white that survives it, averaged over red, green and blue. For a plain sheet this is its opacity."""
    bw = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]], np.float32)
    out = fn(bw, np.array([d, d], np.float32))
    return float(1.0 - np.mean(out[1] - out[0]))


def colour_at(fn, d, under=(0.5, 0.5, 0.5)):
    return [round(float(v), 3) for v in fn(np.array([under], np.float32), np.array([d], np.float32))[0]]


def hides_line(fn):
    return ", ".join(f"{hides(fn, d) * 100:.0f}% at {d:g} m" for d in DEPTHS[1:])


# ── the scene ──────────────────────────────────────────────────────────────────────────────────────────────────────

GROUNDS = [
    # key, label, texture, tint (stone textures are grey and tinted by the stone; [guess] at granite's colour)
    ("sand", "Sand (pale arid ground)", "Sand.png", (1.0, 1.0, 1.0)),
    ("soil", "Soil", "Soil.png", (1.0, 1.0, 1.0)),
    ("granite", "Rough granite", "RoughStone.png", (0.62, 0.58, 0.56)),
    ("mud", "Mud (dark ground)", "Mud.png", (1.0, 1.0, 1.0)),
]


def ground_patch(tex: np.ndarray, tint, w, h, seed):
    """A world-space crop of a ground texture: 1024 texture px span 8 cells [guess at the game's tiling]."""
    small = np.asarray(Image.fromarray((tex[..., :3] * 255).astype(np.uint8)).resize((512, 512), Image.LANCZOS)
                       ).astype(np.float32) / 255.0
    tiled = np.tile(small, (math.ceil(h / 512) + 1, math.ceil(w / 512) + 1, 1))
    oy, ox = (seed * 97) % 512, (seed * 211) % 512
    return tiled[oy:oy + h, ox:ox + w] * np.array(tint, np.float32)


def floor_brightness(d):
    tc = [1.0, 1.0, 0.78, 0.58, 0.38]
    bs = [1.0, 0.80, 0.66, 0.52, 0.38]
    if d <= 0:
        return 1.0
    if d <= 4:
        return bs[d]
    r = 1.0 - 0.22 * (math.log(d / 4.0) / math.log(2.0))
    return tc[4] * max(0.25, r)


def light_alpha(mult):
    g = 0.30
    return min(1.0, max(0.0, (g * mult - g) / (1.0 - g)))


CREAM = np.array((1.0, 248 / 255, 232 / 255), np.float32)


BODY_QUAD = (48, 176)        # rows of the composed pawn canvas that hold the body's 1.5-cell drawn quad (head above it)


class Sprites:
    def __init__(self, vd: Path):
        self.vd = vd
        self.pawn = self.compose_pawn((0.93, 0.76, 0.62), (0.35, 0.45, 0.70), (0.25, 0.17, 0.10))
        self.pawn2 = self.compose_pawn((0.62, 0.45, 0.33), (0.70, 0.30, 0.25), (0.12, 0.10, 0.09))
        self.corpse = np.rot90(self.pawn2, 1).copy()
        self.table = stuff(load(vd / "Table2x2_north.png"), WOOD)
        self.chair = stuff(load(vd / "DiningChair_south.png"), WOOD)
        self.steel = load(vd / "Steel_b.png")
        self.ladder = load(MOD / "Textures/Things/Building/FlowWorks/Canals/RM_Ladder_north.png")

    def compose_pawn(self, skin, shirt, hair):
        vd = self.vd

        def tinted(name, c):
            a = load(vd / name)
            a[..., :3] *= np.array(c, np.float32)
            return a

        body = tinted("Naked_Male_south.png", skin)
        shirt_l = tinted("ShirtBasic_Male_south.png", shirt)
        head = tinted("Male_Average_Normal_south.png", skin)
        hair_l = tinted("Mop_south.png", hair)
        canvas = np.zeros((176, 128, 4), np.float32)          # head sits 0.34 cell above the body (vanilla's offset)
        over(canvas, body, 0, 48)
        over(canvas, shirt_l, 0, 48)
        over(canvas, head, 0, 0 + 26)
        over(canvas, hair_l, 0, 0 + 26)
        return canvas                                          # the body's drawn quad is rows BODY_QUAD


WOOD = (0.52, 0.38, 0.26)   # [guess ~70%] vanilla WoodLog stuff colour (133, 97, 67)


def stuff(a, c):
    """Furniture textures are grey and tinted by what they are made of."""
    a = a.copy()
    a[..., :3] *= np.array(c, np.float32)
    return a


def over(dst, src, x, y):
    """Alpha-composite src (RGBA) onto dst (RGBA or RGB) at x, y, clipped."""
    h, w = src.shape[:2]
    H, W = dst.shape[:2]
    x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
    if x0 >= x1 or y0 >= y1:
        return
    s = src[y0 - y:y1 - y, x0 - x:x1 - x]
    a = s[..., 3:4]
    d = dst[y0:y1, x0:x1]
    d[..., :3] = s[..., :3] * a + d[..., :3] * (1 - a)
    if dst.shape[2] == 4:
        d[..., 3:4] = a + d[..., 3:4] * (1 - a)


def scale(sprite, w_px):
    h = round(sprite.shape[0] * w_px / sprite.shape[1])
    return np.asarray(Image.fromarray((sprite * 255).astype(np.uint8), "RGBA").resize((w_px, h), Image.LANCZOS)
                      ).astype(np.float32) / 255.0


def as_cover(law):
    """What the game can draw over a thing (a pawn, an item, a building): one colour at one alpha (RM_SubmergeDraw's
    silhouette cover), never a per-colour multiply. The cover that moves black and white as the law does on average:
    out = C x a + rgb x (1 - a), a = 1 - mean(law(white) - law(black)), C = law(black) / a. Equal to the law for a plain
    sheet; for CLEAR, the buildable stand-in."""
    def f(rgb, m):
        n = m.shape[0]
        lo = law(np.zeros((n, 3), np.float32), m)
        hi = law(np.ones((n, 3), np.float32), m)
        a = np.clip(1.0 - (hi - lo).mean(-1, keepdims=True), 1e-6, 1.0)
        return lo + rgb * (1.0 - a)
    return f


def drown_sprite(sprite, law, foot_m_over, height_m, quad=None, uniform=False):
    """Cut a thing's picture the way the game does (RM_UnderLiquid.Share, from its foot): its drawn quad's rows
    quad = (top, bottom), transparent margin included, span height_m; rows above the quad (a pawn's head) are higher
    still. A drowned row lies (foot - its height) under, or, with uniform (a pawn: RM_SubmergeDraw.DrawCutNode tints its
    whole drowned part as at the full depth), foot_m_over under."""
    out = sprite.copy()
    h = sprite.shape[0]
    if foot_m_over <= 0:
        return out
    top, bot = quad if quad else (0, h)
    frac = np.maximum(0.0, (bot - 0.5 - np.arange(h)) / max(1, bot - top))   # 0 at the foot, 1 at the quad's top
    m = foot_m_over - frac * height_m                           # metres under at each row
    if uniform:
        m = np.where(m > 0, foot_m_over, m)
    m2 = np.repeat(m[:, None], sprite.shape[1], 1).astype(np.float32)
    wet = (m2 > 0) & (sprite[..., 3] > 0)
    if wet.any():
        out[..., :3][wet] = law(sprite[..., :3][wet], m2[wet])
    return out


def tile(ground_key, sprites, grounds, law, water_m, seed=1, fx=None, frame=0):
    W, H = COLS * PX, ROWS * PX
    gtex, tint = grounds[ground_key]
    img = ground_patch(gtex, tint, W, H, seed).copy()
    x0, z0, x1, z1 = (v * PX for v in PIT)
    pit_m = 0.0 if water_m == 0 else max(0.5, math.ceil(water_m / ul.NOTCH - 1e-6) * ul.NOTCH)
    if water_m == 0:
        pit_m = 1.0                                             # the dry reference: an empty 1 m pit
    d = round(pit_m / ul.NOTCH)
    level = water_m
    # floor
    gravel = grounds["_gravel"][0]
    floor = ground_patch(gravel, (1, 1, 1), x1 - x0, z1 - z0, seed + 5) * floor_brightness(d)
    img[z0:z1, x0:x1] = floor
    # faces: the bank ground, lit
    drop_i = min(d, len(ul.NORTH_BY_DROP) - 1)
    hn = int(round(ul.NORTH_BY_DROP[drop_i] * PX))
    ws = int(round(ul.SIDE_BY_DROP[drop_i] * PX))
    bank = ground_patch(gtex, tint, W, H, seed + 11)
    if hn > 0:
        img[z0:z0 + hn, x0:x1] = _lerp(bank[z0:z0 + hn, x0:x1], CREAM, light_alpha(1.85))
    if ws > 0:
        for xa in (x0, x1 - ws):
            img[z0 + hn:z1, xa:xa + ws] = _lerp(bank[z0 + hn:z1, xa:xa + ws], CREAM, light_alpha(1.29))
    # metres under for every pit pixel: floor at the level; the north face from the rim (level - pit) to its foot
    mo = np.full((z1 - z0, x1 - x0), level, np.float32)
    if hn > 0:
        f = (np.arange(hn) / max(1, hn - 1)).astype(np.float32)   # 0 at the rim, 1 at the foot
        mo[:hn, :] = ((level - pit_m) + f * pit_m)[:, None]
    if ws > 0:
        f = (np.arange(ws) / max(1, ws - 1)).astype(np.float32)
        mo[hn:, :ws] = np.minimum(mo[hn:, :ws], ((level - pit_m) + f * pit_m)[None, :])
        mo[hn:, -ws:] = np.minimum(mo[hn:, -ws:], ((level - pit_m) + f[::-1] * pit_m)[None, :])
    region = img[z0:z1, x0:x1]
    wet = mo > 0
    fx = fx or NO_FX
    t = frame / max(1, fx["frames"])
    face = np.zeros_like(wet)
    face[:hn, :] = True
    if ws > 0:
        face[:, :ws] = face[:, -ws:] = True
    if wet.any() and fx["wet"]:
        region[wet] = wetten(region[wet])
        m_per_px = pit_m / max(1, hn)
        band = face & ~wet & (mo > -WET_BAND_PX * m_per_px)
        if band.any():
            k = np.clip(1.0 + mo[band] / (WET_BAND_PX * m_per_px), 0.0, 1.0)[:, None]
            region[band] = _lerp(region[band], wetten(region[band]), k)
        if level >= pit_m - 1e-6:                                # at the rim: the band lies on the bank round the pit
            yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
            ddx = np.maximum(np.maximum(x0 - xx, xx - (x1 - 1)), 0.0)
            ddz = np.maximum(np.maximum(z0 - yy, yy - (z1 - 1)), 0.0)
            dist = np.sqrt(ddx ** 2 + ddz ** 2)
            jag = 3.0 * np.sin(xx / 7.0 + 1.3 * np.sin(yy / 11.0)) * np.sin(yy / 9.0 + 0.7 * np.sin(xx / 5.0))
            k = np.clip((WET_BAND_PX - dist - jag) / 3.0, 0.0, 1.0)      # a crisp, ragged edge (3 px feather)
            k[z0:z1, x0:x1] = 0.0
            sel = k > 0
            img[sel] = _lerp(img[sel], wetten(img[sel]), k[sel][:, None])
    if wet.any() and fx["warp"] > 0:
        dx, dy = wave_field(z1 - z0, x1 - x0, t, x0, z0)
        a = warp_amp(fx["warp"], mo)
        moved = displace(region.copy(), dx * a, dy * a)
        region[wet] = moved[wet]
    if wet.any():
        region[wet] = law(region[wet], mo[wet])
    if wet.any() and fx["ripple"] > 0:
        light = ripple_lines(z1 - z0, x1 - x0, t, x0, z0) * ripple_amp(fx["ripple"], mo)
        region[wet] = np.clip(region[wet] + RIPPLE_COLOUR * light[wet][:, None], 0.0, 1.0)
    if wet.any() and fx["waterline"]:
        inner = wet.copy()
        inner[:2, :] = inner[-2:, :] = inner[:, :2] = inner[:, -2:] = False   # the outline's 2 px
        dry_p = np.pad(~inner, 1, constant_values=True)
        near = np.zeros_like(dry_p)
        for sy in range(-WATERLINE_PX, WATERLINE_PX + 1):
            for sx in range(-WATERLINE_PX, WATERLINE_PX + 1):
                near |= np.roll(np.roll(dry_p, sy, 0), sx, 1)
        line = inner & near[1:-1, 1:-1]
        region[line] = _lerp(region[line], WATERLINE_COLOUR, WATERLINE_ALPHA)
    # outline
    img[z0:z0 + 2, x0:x1] = img[z1 - 2:z1, x0:x1] = 0.10
    img[z0:z1, x0:x0 + 2] = img[z0:z1, x1 - 2:x1] = 0.10
    rgba = np.concatenate([img, np.ones((H, W, 1), np.float32)], 2)
    # things in the pit (cells relative to the pit's north-west corner)
    def put(sprite, cx, cz, w_cells, height_m, uniform=False):
        """cx, cz: the cell the thing stands on (its drawn quad centred there, as the game draws a thing)."""
        k = int(w_cells * PX) / sprite.shape[1]
        s = scale(sprite, int(w_cells * PX))
        quad = None
        if sprite is sprites.pawn:
            quad = (int(BODY_QUAD[0] * k), int(BODY_QUAD[1] * k))
        if level > 0:
            s = drown_sprite(s, as_cover(law), level, height_m, quad=quad, uniform=uniform)
        qt, qb = quad if quad else (0, s.shape[0])
        x = x0 + int((cx + 0.5) * PX - s.shape[1] / 2)
        y = z0 + int((cz + 0.5) * PX - (qt + qb) / 2)
        over(rgba, s, x, y)

    # the ladder hung on the north wall: floor to rim, a cell wide, its foot a third of a cell onto the floor
    rows_l = np.where(sprites.ladder[..., 3].max(1) > 0.05)[0]
    cols_l = np.where(sprites.ladder[..., 3].max(0) > 0.05)[0]
    lad = sprites.ladder[rows_l.min():rows_l.max() + 1, cols_l.min():cols_l.max() + 1]
    lad_h = hn + PX // 3 + PX // 4
    lad = np.asarray(Image.fromarray((lad * 255).astype(np.uint8), "RGBA").resize((int(PX * 0.7), lad_h), Image.LANCZOS)
                     ).astype(np.float32) / 255.0
    lad = drown_sprite(lad, as_cover(law), level, pit_m) if level > 0 else lad
    over(rgba, lad, x0 + int(PX * 0.15), z0)
    put(sprites.table, 3.5, 0.5, 2.0, TABLE_M)                  # a 2x2 table on cells 3-4, rows 0-1
    put(sprites.steel, 0.0, 2.0, 0.75, ITEM_M)
    put(sprites.corpse, 2.0, 2.0, 1.5, CORPSE_M, uniform=True)  # lying: covered whole as at the full depth
    put(sprites.pawn, 1.0, 1.0, 1.5, HUMAN_M, uniform=True)
    # on the bank: a dry colonist and a chair, for scale and for the dry colours
    dry = scale(sprites.pawn, int(1.5 * PX))
    over(rgba, dry, int(7.0 * PX - dry.shape[1] / 2), int(2.5 * PX - dry.shape[0] * (BODY_QUAD[0] + BODY_QUAD[1]) / 352))
    ch = scale(sprites.chair, PX)
    over(rgba, ch, int(6.5 * PX), int(3.8 * PX))
    return rgba[..., :3], pit_m


def label(im: Image.Image, text, xy, size=18):
    dr = ImageDraw.Draw(im)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except OSError:
        font = ImageFont.load_default()
    x, y = xy
    bb = dr.textbbox((x, y), text, font=font)
    dr.rectangle((bb[0] - 4, bb[1] - 3, bb[2] + 4, bb[3] + 3), fill=(20, 24, 32))
    dr.text((x, y), text, fill=(235, 235, 235), font=font)


def build(out: Path):
    vd = vanilla_dir()
    grounds = {k: (load(vd / f), t) for k, _l, f, t in GROUNDS}
    grounds["_gravel"] = (load(vd / "Gravel.png"), (1, 1, 1))
    sprites = Sprites(vd)
    out.mkdir(parents=True, exist_ok=True)
    manifest = {"cell_px": PX, "depths_m": DEPTHS, "grounds": [], "candidates": []}
    for key, name, fn, desc in CANDIDATES:
        manifest["candidates"].append({"key": key, "name": name, "what": desc, "hides_line": hides_line(fn),
                                       "hides_by_depth": {str(d): round(hides(fn, d), 4) for d in DEPTHS[1:]},
                                       "mid_grey_becomes": {str(d): colour_at(fn, d) for d in DEPTHS[1:]},
                                       "fx": fx_of(key), "mechanism": MECHANISM[key]})
    for gi, (gkey, glabel, _f, _t) in enumerate(GROUNDS):
        rows = []
        for key, name, fn, _d in CANDIDATES:
            row, frames = [], []
            fx = fx_of(key)
            for fr in range(fx["frames"]):
                names = []
                for d in DEPTHS:
                    rgb, pit_m = tile(gkey, sprites, grounds, fn, d, seed=gi + 3, fx=fx, frame=fr)
                    im = Image.fromarray((np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")
                    txt = "dry pit, 1 m" if d == 0 else f"{d:g} m of water"
                    label(im, txt + (f"  (frame {fr + 1}/{fx['frames']})" if fx["frames"] > 1 and d > 0 else ""), (8, 6))
                    stem = f"{gkey}_{key}_{str(d).replace('.', 'p')}m" + (f"_f{fr}" if fr else "")
                    im.save(out / f"{stem}.png")
                    names.append(f"{stem}.png")
                frames.append(names)
            row = frames[0]
            rows.append({"candidate": key, "tiles": row, "frames": frames})
        manifest["grounds"].append({"key": gkey, "label": glabel, "rows": rows, "sheet": contact(out, gkey, glabel, rows)})
    (out / "candidates.json").write_text(json.dumps(manifest, indent=1))
    return manifest


def contact(out: Path, gkey, glabel, rows, gap=6, head=40, left=230):
    """One sheet per ground: a row per candidate, a column per depth, true scale (64 px a cell)."""
    tw, th = COLS * PX, ROWS * PX
    W = left + len(DEPTHS) * (tw + gap)
    H = head + len(rows) * (th + gap)
    sheet = Image.new("RGB", (W, H), (28, 30, 36))
    label(sheet, f"{glabel}: fresh water by depth, one row per candidate (64 px a cell, the colonist is 1.75 m)",
          (8, 8), 20)
    names = {k: n for k, n, _f, _d in CANDIDATES}
    for ri, r in enumerate(rows):
        y = head + ri * (th + gap)
        label(sheet, r["candidate"], (8, y + 8), 22)
        words, line, ly = names[r["candidate"]].split(), "", y + 44
        for w_ in words:
            if len(line + " " + w_) > 18:
                label(sheet, line.strip(), (8, ly), 16)
                line, ly = "", ly + 26
            line += " " + w_
        if line.strip():
            label(sheet, line.strip(), (8, ly), 16)
        for ci, name in enumerate(r["tiles"]):
            sheet.paste(Image.open(out / name), (left + ci * (tw + gap), y))
    p = out / f"sheet_{gkey}.png"
    sheet.save(p)
    return p.name


REPO = MOD.parents[2]
SHEET_ID = "flowworks_water_look_second_pass"   # the first pass's page was flowworks_water_by_depth
SHEET_DIR = REPO / "Transient" / SHEET_ID
TEMPLATE = Path.home() / ".claude/skills/review-sheets/assets/sheet_template.html"


def candidate_image(out: Path, manifest, key, dest: Path, gap=6, left=190):
    """One picture per candidate: a strip of every depth for each ground, stacked."""
    tw, th = COLS * PX, ROWS * PX
    gs = manifest["grounds"]
    W = left + len(DEPTHS) * (tw + gap)
    H = len(gs) * (th + gap)
    im = Image.new("RGB", (W, H), (28, 30, 36))
    for gi, g in enumerate(gs):
        row = next(r for r in g["rows"] if r["candidate"] == key)
        y = gi * (th + gap)
        words, line, ly = g["label"].split(), "", y + 10
        for w_ in words:
            if len(line + " " + w_) > 14:
                label(im, line.strip(), (8, ly), 18)
                line, ly = "", ly + 30
            line += " " + w_
        if line.strip():
            label(im, line.strip(), (8, ly), 18)
        for ci, name in enumerate(row["tiles"]):
            im.paste(Image.open(out / name), (left + ci * (tw + gap), y))
    im.save(dest, quality=92)


def frames_image(out: Path, manifest, key, dest: Path, ground="sand", gap=6, left=190):
    """An animated candidate's frames on one ground: a row per frame, a column per depth."""
    tw, th = COLS * PX, ROWS * PX
    g = next(g for g in manifest["grounds"] if g["key"] == ground)
    row = next(r for r in g["rows"] if r["candidate"] == key)
    W = left + len(DEPTHS) * (tw + gap)
    im = Image.new("RGB", (W, len(row["frames"]) * (th + gap)), (28, 30, 36))
    for fi, names in enumerate(row["frames"]):
        y = fi * (th + gap)
        label(im, f"frame {fi + 1}", (8, y + 10), 18)
        for ci, name in enumerate(names):
            im.paste(Image.open(out / name), (left + ci * (tw + gap), y))
    im.save(dest, quality=92)


def zoom_image(out: Path, manifest, ground, dest: Path, factor=2, gap=4, left=120):
    """Every candidate on one ground at play zoom (64 / factor px a cell): a row per candidate."""
    tw, th = COLS * PX // factor, ROWS * PX // factor
    g = next(g for g in manifest["grounds"] if g["key"] == ground)
    W = left + len(DEPTHS) * (tw + gap)
    im = Image.new("RGB", (W, 30 + len(g["rows"]) * (th + gap)), (28, 30, 36))
    label(im, f"{g['label']} at {PX // factor} px a cell (play zoom); columns: dry, "
          + ", ".join(f"{d:g}" for d in DEPTHS[1:]) + " m", (6, 4), 14)
    for ri, r in enumerate(g["rows"]):
        y = 30 + ri * (th + gap)
        label(im, r["candidate"], (6, y + 6), 14)
        for ci, name in enumerate(r["tiles"]):
            t = Image.open(out / name)
            im.paste(t.resize((tw, th), Image.LANCZOS), (left + ci * (tw + gap), y))
    im.save(dest, quality=92)


def replace_block(html, block_id, payload):
    open_tag = f'<script id="{block_id}" type="application/json">'
    i = html.index(open_tag) + len(open_tag)
    j = html.index("</script>", i)
    return html[:i] + "\n" + payload + "\n" + html[j:]


def build_sheet(tiles: Path, manifest):
    img = SHEET_DIR / "img"
    img.mkdir(parents=True, exist_ok=True)
    items = []
    for c in manifest["candidates"]:
        dest = img / f"cand_{c['key']}.jpg"
        candidate_image(tiles, manifest, c["key"], dest)
        meta = {"made by": "water_mockup.py, offline", "how the game would draw it": c["mechanism"],
                "pass": "second (2026-11-21)" if c["key"] in FX else "first (2026-11-20)"}
        if c["fx"]["frames"] > 1:
            fdest = img / f"frames_{c['key']}.jpg"
            frames_image(tiles, manifest, c["key"], fdest)
            meta["frames"] = f"img/{fdest.name} (sand, every depth, {c['fx']['frames']} frames of the loop)"
        items.append({
            "id": c["key"], "label": f"{c['key']}: {c['name']}", "group": "water look (pick one)",
            "thumb": f"img/{dest.name}",
            "effect": f"{c['what']} Hides what lies under it: {c['hides_line']}.",
            "meta": meta,
            "trueSize": {"none": "each picture is a whole scene at 64 px a cell, with a 1.75 m colonist in and beside "
                                 "the pit for scale"},
        })
    ground_links = []
    for g in manifest["grounds"]:
        dest = img / f"ground_{g['key']}.jpg"
        Image.open(tiles / g["sheet"]).save(dest, quality=92)
        ground_links.append(f'<a href="img/{dest.name}" target="_blank">{g["label"]}</a>')
        zoom_image(tiles, manifest, g["key"], img / f"zoom_{g['key']}.jpg")
    zoom_links = " · ".join(f'<a href="img/zoom_{g["key"]}.jpg" target="_blank">{g["label"]}</a>'
                            for g in manifest["grounds"])
    html_path = SHEET_DIR / f"{SHEET_ID}.html"
    dec_path = SHEET_DIR / f"{SHEET_ID}.decisions.json"
    brief = (
        "<p><b>Second pass on FlowWorks water.</b> A judge picked FIRM on 2026-11-20 and it is built. Your card notes of "
        "that evening asked for more: \"Maybe dry and wet have different colors too ... Maybe more aggressive "
        "distortions on the surface will make it look more like water.\" Three new looks sit beside the first five: "
        "<b>WET</b> (wet ground, a wet band and a waterline), <b>RIPPLE</b> (a moving, distorted bottom with ripple "
        "light) and <b>BLEND</b> (both, gentler). All three keep FIRM's water colour and strength; only the ground and "
        "the surface change. Research behind them: design/concepts/FlowWorks/version/water_look_research.md.</p>"
        "<p>Each row is one candidate. Its picture has four grounds (sand, soil, rough granite, mud) and eight "
        "columns: a dry 1 m pit, then 0.2, 0.5, 1, 1.5, 2, 5 and 8 m of fresh water. In every pit: a standing "
        "colonist (1.75 m), a body lying on the floor, a wooden table (0.8 m), a steel stack and a ladder on the north "
        "wall. On the bank: a dry colonist and a chair, for scale and the dry colours. RIPPLE and BLEND move: their "
        "row shows frame 1, and a frames picture (in the row's details) shows three frames of the loop. "
        "Each row also says how the game would draw it and what it cannot do (nothing standing in the water is "
        "rippled or wetted: the game draws pawns and items itself).</p>"
        "<p>To compare all eight on one ground at true scale, open a ground sheet: " + " · ".join(ground_links) + ". "
        "At play zoom (32 px a cell): " + zoom_links + ".</p>"
        "<p>A fresh Opus judge picks one tonight (your card's \"Judge picks tonight\"); you can overrule it in game. "
        "Not drawn, the same in every row: floor shadows, a pawn's sink offset, labels, time-of-day light, vanilla's "
        "own sky reflection.</p>")
    config = {
        "sheetId": SHEET_ID,
        "title": "FlowWorks water look, second pass: wet ground and a moving bottom",
        "subtitle": "eight looks; the judge's pick becomes the 0.1.0 target",
        "briefHtml": brief,
        "criterion": "Rows are in order from today's look to the most changed. The order does not rank them.",
        "invented": [
            "The non-shipped looks (AQUA, AQUA_SOFT, CLEAR, WET, RIPPLE, BLEND) and all their numbers are mine, made "
            "for these sheets. FIRM is in the game since 6c668b36a8; none of the others is.",
            "The ripple light (a curved cell net) and the waves are drawn by formulas of mine; in the game they would "
            "be a texture drifting over the water and a distortion shader, so the exact shapes will differ.",
            "\"Hides\" is one number per depth: one minus the black-to-white contrast that survives the water. "
            "For a plain sheet of colour it equals the sheet's opacity.",
            "The ground texture scale (8 cells per texture), granite's grey tint and the wood colour of the table "
            "and chair are my estimates, not read from the game.",
        ],
        "posture": {"mode": "whitelist",
                    "explain": "Nothing is the target until you mark one row \"Make this the target\". A row you leave "
                               "alone is not picked."},
        "options": [
            {"key": "target", "label": "Make this the target", "hotkey": "1", "color": "#5ac37f", "counts": "in"},
            {"key": "no", "label": "Not this one", "hotkey": "2", "color": "#e06c6c", "counts": "out"},
        ],
        "groupLabel": "group",
        "media": False,
        "trueSize": "optional",
        "collect": "independent",       # his pick is the target; a pre-filled guess would anchor it
        "decisionsFile": dec_path.name,
        "decisionsPath": str(dec_path),
        "sheetPath": str(html_path),
    }
    html = TEMPLATE.read_text(encoding="utf-8")
    html = replace_block(html, "CONFIG", json.dumps(config, indent=1))
    html = replace_block(html, "ITEMS", json.dumps(items, indent=1))
    html = html.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="sheet-kind" content="non-art">', 1)
    html_path.write_text(html, encoding="utf-8")
    if dec_path.exists() and json.loads(dec_path.read_text()).get("decisions"):
        print(f"water_mockup: {dec_path} already holds decisions; left as it is")
    else:
        dec_path.write_text(json.dumps({
            "sheetId": SHEET_ID, "posture": "whitelist", "decidedCount": 0, "decisions": {}, "frozen": False,
            "reviewStatus": {"state": "prefill", "by": "water_mockup.py",
                             "evidence": "built offline; no row pre-filled, the pick is the owner's"},
        }, indent=2), encoding="utf-8")
    (SHEET_DIR / "candidates.json").write_text(json.dumps(manifest["candidates"], indent=1), encoding="utf-8")
    return html_path, dec_path


def calibrate():
    floor =np.array((0.358, 0.289, 0.225), np.float32) * floor_brightness(8)   # gravel mean, 4 m pit floor
    got = law_shipped(floor[None, :], np.array([2.0], np.float32))[0]
    want = np.array(CAPTURE["water 2 m over a 4 m pit floor"], np.float32)
    err = float(np.abs(got - want).max())
    print(f"SHIPPED at 2 m over a 4 m pit floor: model {got.round(3).tolist()} capture {want.tolist()} worst {err:.3f} "
          f"limit 0.02 cases 1")
    return 0 if err <= 0.02 else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path)
    ap.add_argument("--calibrate", action="store_true")
    ap.add_argument("--sheet", action="store_true", help=f"also write the review page in Transient/{SHEET_ID}/")
    a = ap.parse_args(argv)
    if a.calibrate:
        return calibrate()
    if not a.out:
        ap.error("--out or --calibrate")
    m = build(a.out)
    n = sum(len(r["tiles"]) for g in m["grounds"] for r in g["rows"])
    print(f"water_mockup: {n} tiles, {len(m['grounds'])} grounds x {len(m['candidates'])} candidates x {len(DEPTHS)} depths -> {a.out}")
    if a.sheet:
        h, d = build_sheet(a.out, m)
        print(f"water_mockup: sheet {h}\nwater_mockup: decisions {d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
