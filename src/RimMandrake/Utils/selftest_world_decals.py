#!/usr/bin/env python3
"""Offline check for the biome decals (RM_WorldDecals.cs, WORLD_DECALS_BUILD_ATLAS_PIPELINE_ONCE, world look 4a).

1. SOURCE: the worldBiomeDecals setting is a Scribed static whose initialiser equals its Scribe default, is reset by
   ResetWorldLook, drawn on the settings screen and part of the redraw key; the csproj compiles RM_WorldDecals.cs;
   RM_WorldLook.Wrap builds decals behind the setting; the fade is a postfix on the WorldDrawLayerBase.Alpha getter that
   only writes material colours (no mesh rebuild, no redraw); the queue sits strictly between the swirls/blend and the
   hills (3505 < q < 3510) and the lift strictly between the swirls (+0.004) and the hills (+0.005); a missing atlas is
   looked up with ContentFinder.Get(..., false) (no error); only flat land tiles get glyphs; no world data is written.
2. ARITHMETIC, mirrored from the C# (constants are read from the source, so a changed default is checked as shipped):
   hash, glyph count, cell pick, slot, atlas grid side, cell UVs and the altitude fade, swept over 200,000 tile ids and
   the whole altitude range.
3. GENERATOR: world_decal_atlas.py writes every row of world_decal_rows.json as an atlas that passes its own contract
   check, and the check refuses planted bad atlases.
Then plants one defect per source/arithmetic check and requires each to be caught.

    python3 src/RimMandrake/Utils/selftest_world_decals.py
"""
import math
import os
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(ROOT))
SHELL = os.path.join(ROOT, "BiomesShell", "Source")
sys.path.insert(0, os.path.join(ROOT, "Utils", "art"))
M32 = 0xFFFFFFFF
WORLD_WRITES = re.compile(r"\.hilliness\s*=[^=]|\.biome\s*=[^=]|PrimaryBiome\s*=[^=]|SetAllLayersDirty|world_commit\(")


def const(src, name, _kind=None):
    m = re.search(r"public (?:static|const) \w+ %s\s*=\s*([^;]+);" % name, src)
    if not m:
        raise KeyError(name)
    return float(m.group(1).strip().rstrip("f"))


# the C# lines the Python mirror copies; a change to any of them must change the mirror too
MIRRORED = [
    "uint h = (uint)tileId * 0x9E3779B1u + salt * 0x85EBCA77u;",
    "h ^= h >> 16; h *= 0x85EBCA6Bu;",
    "h ^= h >> 13; h *= 0xC2B2AE35u;\n                h ^= h >> 16;\n                return h;",
    "public static int GlyphCount(int tileId) => 2 + (int)(Hash(tileId, 0) % 2u);",
    "int c = (int)(Hash(tileId, 11u + (uint)k) % (uint)cells);",
    "if (k > 0 && c == Cell(tileId, k - 1, cells)) c = (c + 1) % cells;",
    "float turn = (Hash(tileId, 1) % 3600u) / 3600f;",
    "float angle = (turn + (float)k / count) * 2f * Mathf.PI;",
    "float jitter = ((Hash(tileId, 21u + (uint)k) % 1000u) / 999f) * decalJitter;",
    "return new Vector2(angle, decalSpread + jitter);",
    "return g == 1 || g == 2 || g == 4 ? g : 0;",
    "float inset = 1f / (side * CellPx);",
    "float v1 = 1f - (float)row / side, v0 = 1f - (float)(row + 1) / side;",
    "return 1f - Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(fullAt, goneAt, altitude));",
]


# ------------------------------------------------------------------ the C# arithmetic, line for line
class Decals:
    def __init__(self, src):
        self.CellPx = int(const(src, "CellPx", "int"))
        self.spread = const(src, "decalSpread", "float")
        self.jitter = const(src, "decalJitter", "float")
        self.size = const(src, "decalSize", "float")
        self.full = const(src, "decalFullAlt", "float")
        self.gone = const(src, "decalGoneAlt", "float")
        self.src = src

    @staticmethod
    def hash(tile, salt):
        h = (tile * 0x9E3779B1 + salt * 0x85EBCA77) & M32
        h ^= h >> 16; h = (h * 0x85EBCA6B) & M32
        h ^= h >> 13; h = (h * 0xC2B2AE35) & M32
        h ^= h >> 16
        return h

    def count(self, t):
        return 2 + self.hash(t, 0) % 2

    def cell(self, t, k, cells):
        if cells <= 1:
            return 0
        c = self.hash(t, 11 + k) % cells
        if k > 0 and c == self.cell(t, k - 1, cells):
            c = (c + 1) % cells
        return c

    def slot(self, t, k, n):
        turn = (self.hash(t, 1) % 3600) / 3600.0
        ang = (turn + k / n) * 2 * math.pi
        jit = ((self.hash(t, 21 + k) % 1000) / 999.0) * self.jitter
        return ang, self.spread + jit

    def grid(self, w, h):
        if w != h or w < self.CellPx or w % self.CellPx:
            return 0
        g = w // self.CellPx
        return g if g in (1, 2, 4) else 0

    def uv(self, cell, side):
        inset = 1.0 / (side * self.CellPx)
        col, row = cell % side, cell // side
        return (col / side + inset, 1 - (row + 1) / side + inset, (col + 1) / side - inset, 1 - row / side - inset)

    def fade(self, alt, full=None, gone=None):
        full = self.full if full is None else full
        gone = self.gone if gone is None else gone
        if gone <= full:
            return 1.0 if alt <= full else 0.0
        t = min(1.0, max(0.0, (alt - full) / (gone - full)))
        return 1.0 - t * t * (3 - 2 * t)      # Mathf.SmoothStep(0,1,t)


def check_source(mod, look, dec, proj):
    errs = []
    s = "worldBiomeDecals"
    init = re.search(r"public static bool " + s + r"\s*=\s*([^;]+);", mod)
    scribe = re.search(r'Scribe_Values\.Look\(ref ' + s + r', "' + s + r'", ([^)]+)\)', mod)
    if not init or not scribe:
        errs.append(s + ": not a Scribed static field")
    elif init.group(1).strip() != scribe.group(1).strip():
        errs.append(s + ": initialiser != Scribe default")
    reset = mod.split("void ResetWorldLook", 1)[-1].split("}", 1)[0]
    if s + " = " + (init.group(1).strip() if init else "true") not in reset:
        errs.append(s + ": not reset by ResetWorldLook")
    if "RM_BiomesSettings." + s not in mod.split("DoSettingsWindowContents", 1)[-1]:
        errs.append(s + ": not drawn on the settings screen")
    if '"/" + RM_BiomesSettings.' + s not in mod or mod.count("WorldLookKey()") < 3:
        errs.append(s + ": not part of the world-look redraw key")
    if '<Compile Include="RM_WorldDecals.cs" />' not in proj:
        errs.append("csproj does not compile RM_WorldDecals.cs")
    wrap = look.split("static IEnumerable Wrap", 1)[-1].split("static List<LayerSubMesh> SubMeshes", 1)[0]
    if not re.search(r"if \(RM_BiomesSettings\.worldBiomeDecals\)[^;]*RM_WorldDecals\.Build\(layer, mine\)", wrap):
        errs.append("RM_WorldLook.Wrap does not build decals behind the setting")
    if not re.search(r'PropertyGetter\(typeof\(WorldDrawLayerBase\), "Alpha"\)', dec):
        errs.append("no fade patch on the WorldDrawLayerBase.Alpha getter")
    post = dec.split("static void AlphaPostfix", 1)[-1].split("// ----", 1)[0]
    if "is WorldDrawLayer_Terrain" not in post or ".color = " not in post or "altitude" not in post:
        errs.append("fade postfix does not set material colour from the camera altitude on the terrain layer")
    if re.search(r"FinalizeMesh|SetAllLayersDirty|SetDirty|Regenerate|__result\s*=", post):
        errs.append("fade postfix rebuilds meshes or changes the layer alpha (must only write material colours)")
    q = const(dec, "decalQueue", "int"); sq = const(look, "swirlQueue", "int"); bq = const(look, "blendQueue", "int")
    if not (max(sq, bq) < q < 3510):
        errs.append("decalQueue %g not strictly between the swirls/blend (%g) and the hills (3510)" % (q, max(sq, bq)))
    lift = const(dec, "decalLift", "float"); sl = const(look, "swirlLift", "float")
    if not (sl < lift < 0.005):
        errs.append("decalLift %g not strictly between the swirls (%g) and the hills (0.005)" % (lift, sl))
    if not re.search(r'ContentFinder<Texture2D>\.Get\("World/Decals/" \+ b\.defName, false\)', dec):
        errs.append("atlas not looked up as World/Decals/<defName> with reportFailure=false")
    if "t.hilliness != Hilliness.Flat" not in dec or "b.isWaterBiome" not in dec:
        errs.append("glyphs not limited to flat land tiles")
    for line in MIRRORED:
        if line not in dec:
            errs.append("C# drifted from the Python mirror: %r" % line[:60])
    if "TilesCount));" in dec.split("public static string Build", 1)[-1] or "tileSpacing = 1.612f * circ / verts.Count;" not in dec:
        errs.append("glyph size not taken from the tile's own geometry (4 pi r^2 / TilesCount is wrong on a partial planet)")
    if WORLD_WRITES.search(dec):
        errs.append("writes world data or forces a redraw (must be look-only)")
    return errs


def check_math(d):
    errs = []
    N = 200000
    counts = {2: 0, 3: 0}
    cells4 = [0] * 16
    min_sep = 9.0
    for t in range(N):
        n = d.count(t)
        if n not in counts:
            errs.append("tile %d: %d glyphs (must be 2 or 3)" % (t, n)); break
        counts[n] += 1
        prev = None
        pts = []
        for k in range(n):
            c = d.cell(t, k, 16)
            if not 0 <= c < 16:
                errs.append("tile %d glyph %d: cell %d out of range" % (t, k, c)); break
            if c == prev:
                errs.append("tile %d: glyph %d repeats the cell of the one before" % (t, k)); break
            prev = c
            cells4[c] += 1
            if d.cell(t, k, 4) >= 4 or d.cell(t, k, 1) != 0:
                errs.append("tile %d: cell out of range on a 2x2 or 1x1 atlas" % t); break
            a, r = d.slot(t, k, n)
            if not (d.spread - 1e-9 <= r <= d.spread + d.jitter + 1e-9):
                errs.append("tile %d: slot radius %g outside spread..spread+jitter" % (t, r)); break
            pts.append((r * math.cos(a), r * math.sin(a)))
        if errs:
            break
        # outer reach: glyph corner must stay inside the hex's inscribed circle (apothem ~0.537 tile spacings for an
        # equal-area hex), so a glyph never hangs over a neighbouring tile's land
        reach = max(math.hypot(x, y) for x, y in pts) + d.size * 0.5 * math.sqrt(2)
        if reach > 0.62:
            errs.append("tile %d: a glyph reaches %.3f tile spacings from the centre (> 0.62)" % (t, reach)); break
        for i in range(n):
            for j in range(i + 1, n):
                sep = max(abs(pts[i][0] - pts[j][0]), abs(pts[i][1] - pts[j][1]))
                min_sep = min(min_sep, sep)
    if not errs:
        share = counts[3] / N
        if not 0.45 < share < 0.55:
            errs.append("3-glyph share %.3f (hash not mixing)" % share)
        mean = sum(cells4) / 16
        if max(abs(c - mean) / mean for c in cells4) > 0.05:
            errs.append("cell use uneven on a 4x4 atlas: %s" % cells4)
        # the drawn glyph sits in the inner 86% of its cell less the margin: overlapping squares are fine only if the
        # drawn parts do not meet
        if min_sep < d.size * 0.86:
            errs.append("two glyphs on one tile can overlap (min axis separation %.3f < %.3f)" % (min_sep, d.size * 0.86))
    if d.hash(12345, 0) != Decals.hash(12345, 0) or d.hash(0, 0) != 0:
        errs.append("hash not deterministic")
    # atlas grid
    for (w, h), want in {(256, 256): 1, (512, 512): 2, (1024, 1024): 4, (768, 768): 0, (512, 256): 0, (128, 128): 0,
                         (2048, 2048): 0, (500, 500): 0}.items():
        if d.grid(w, h) != want:
            errs.append("grid(%d,%d) = %d, want %d" % (w, h, d.grid(w, h), want))
    for side in (1, 2, 4):
        boxes = [d.uv(c, side) for c in range(side * side)]
        for c, (u0, v0, u1, v1) in enumerate(boxes):
            if not (0 < u0 < u1 < 1 and 0 < v0 < v1 < 1):
                errs.append("side %d cell %d: uv %s outside (0,1)" % (side, c, (u0, v0, u1, v1)))
        if side == 2 and not (boxes[0][1] > 0.5 and boxes[0][0] < 0.5):
            errs.append("cell 0 is not the TOP-left cell (Unity v runs bottom up)")
        for a in range(len(boxes)):
            for b in range(a + 1, len(boxes)):
                A, B = boxes[a], boxes[b]
                if A[0] < B[2] and B[0] < A[2] and A[1] < B[3] and B[1] < A[3]:
                    errs.append("side %d: cells %d and %d overlap in uv" % (side, a, b))
    # fade
    if not d.full < d.gone:
        errs.append("decalFullAlt %g not below decalGoneAlt %g" % (d.full, d.gone))
    prev = 2.0
    for alt in range(100, 1101):
        f = d.fade(alt)
        if not 0.0 <= f <= 1.0 or f > prev + 1e-9:
            errs.append("fade not monotone in [0,1] at altitude %d" % alt); break
        prev = f
    if d.fade(125) != 1.0 or d.fade(d.full) != 1.0:
        errs.append("not full strength at close zoom")
    if d.fade(d.gone) != 0.0 or d.fade(1100) != 0.0:
        errs.append("not gone past mid zoom")
    # the owner-look altitudes (studio method): close-ups at 320 show decals, the 900 grid does not
    if d.fade(320) != 1.0 or d.fade(900) != 0.0:
        errs.append("altitude 320 must draw full, 900 nothing")
    if not (300 <= d.gone <= 700):
        errs.append("decalGoneAlt %g is not 'mid zoom' (the camera runs 125..1100)" % d.gone)
    return errs


def check_generator():
    import world_decal_atlas as W
    import numpy as np
    from PIL import Image
    errs = []
    rows = W.load_rows()
    if not rows:
        return ["world_decal_rows.json has no rows"]
    with tempfile.TemporaryDirectory() as tmp:
        for name, row in rows.items():
            for key in ("mod", "sheet", "grid", "palette", "glyphs"):
                if key not in row:
                    errs.append("%s: row lacks %s" % (name, key))
            if errs:
                continue
            sheet = row["sheet"].split(" ")[0]
            if not os.path.exists(os.path.join(REPO, sheet)):
                errs.append("%s: palette source %s does not exist" % (name, sheet))
            p = os.path.join(tmp, name + ".png")
            W.atlas(row, name).save(p)
            e = W.check_atlas(p)
            if e:
                errs.append("%s: generated atlas fails the contract: %s" % (name, "; ".join(e)))
            im = np.asarray(Image.open(p))
            # lit from the upper left: in every cell the opaque pixels' upper-left half is brighter than the lower-right
            side = row["grid"]
            for k in range(side * side):
                c = im[(k // side) * W.CELL:(k // side + 1) * W.CELL, (k % side) * W.CELL:(k % side + 1) * W.CELL].astype(float)
                lum, a = c[..., :3].mean(axis=2), c[..., 3]
                yy, xx = np.mgrid[0:W.CELL, 0:W.CELL]
                body = a > 250
                if body.sum() < 50:
                    errs.append("%s cell %d: no opaque body" % (name, k)); continue
                cy, cx = yy[body].mean(), xx[body].mean()
                ul = body & ((xx - cx) + (yy - cy) < 0)
                lr = body & ((xx - cx) + (yy - cy) > 0)
                if not lum[ul].mean() > lum[lr].mean():
                    errs.append("%s cell %d: not lit from the upper left" % (name, k))
                near = a > 128                       # the glyph and its antialiased rim, grown by 3 px
                for _ in range(3):
                    near = near | np.roll(near, 1, 0) | np.roll(near, -1, 0) | np.roll(near, 1, 1) | np.roll(near, -1, 1)
                sh = (a > 8) & ~near                 # what is left is the baked shadow
                if sh.sum() == 0 or not (xx[sh].mean() > cx and yy[sh].mean() > cy):
                    errs.append("%s cell %d: no soft shadow down-right" % (name, k))
        # planted bad atlases must be refused
        bad = {"rect": Image.new("RGBA", (512, 256), (0, 0, 0, 0)), "rgb": Image.new("RGB", (512, 512)),
               "bleed": Image.new("RGBA", (512, 512), (255, 255, 255, 255)), "empty": Image.new("RGBA", (512, 512), (0, 0, 0, 0))}
        for n, im in bad.items():
            p = os.path.join(tmp, "bad_%s.png" % n)
            im.save(p)
            if not W.check_atlas(p):
                errs.append("contract check accepted a bad atlas (%s)" % n)
    return errs


def main():
    mod = open(os.path.join(SHELL, "RM_BiomesMod.cs"), encoding="utf-8").read()
    look = open(os.path.join(SHELL, "RM_WorldLook.cs"), encoding="utf-8").read()
    dec = open(os.path.join(SHELL, "RM_WorldDecals.cs"), encoding="utf-8").read()
    proj = open(os.path.join(SHELL, "RM_Biomes.csproj"), encoding="utf-8").read()
    fails = 0

    def report(label, errs):
        nonlocal fails
        print(("ok  " if not errs else "FAIL") + " " + label + ("" if not errs else ": " + "; ".join(errs[:6])))
        fails += bool(errs)

    report("source", check_source(mod, look, dec, proj))
    report("arithmetic (200,000 tiles, altitudes 100..1100)", check_math(Decals(dec)))
    report("generator + contract check", check_generator())

    plants = [
        ("default drift", lambda: check_source(mod.replace('"worldBiomeDecals", true', '"worldBiomeDecals", false'), look, dec, proj)),
        ("not reset", lambda: check_source(mod.replace("            worldBiomeDecals = true;\n", ""), look, dec, proj)),
        ("undrawn", lambda: check_source(mod.replace("ref RM_BiomesSettings.worldBiomeDecals", "ref dummy"), look, dec, proj)),
        ("csproj missing", lambda: check_source(mod, look, dec, proj.replace('<Compile Include="RM_WorldDecals.cs" />', ""))),
        ("not built", lambda: check_source(mod, look.replace("RM_WorldDecals.Build(layer, mine)", "\"\""), dec, proj)),
        ("no fade patch", lambda: check_source(mod, look, dec.replace('PropertyGetter(typeof(WorldDrawLayerBase), "Alpha")', 'Method(typeof(X), "Y")'), proj)),
        ("fade rebuilds", lambda: check_source(mod, look, dec.replace("lastAlpha = a;", "lastAlpha = a; Find.World.renderer.SetAllLayersDirty();"), proj)),
        ("over the hills", lambda: check_source(mod, look, dec.replace("decalQueue = 3507", "decalQueue = 3510"), proj)),
        ("lift over hills", lambda: check_source(mod, look, dec.replace("decalLift = 0.0045f", "decalLift = 0.006f"), proj)),
        ("missing atlas errors", lambda: check_source(mod, look, dec.replace('b.defName, false)', 'b.defName, true)'), proj)),
        ("hills get glyphs", lambda: check_source(mod, look, dec.replace("t.hilliness != Hilliness.Flat", "false"), proj)),
        ("mirror drift", lambda: check_source(mod, look, dec.replace("% 2u);", "% 3u);"), proj)),
        ("hash tail dropped", lambda: check_source(mod, look, dec.replace("h *= 0xC2B2AE35u;\n                h ^= h >> 16;", "h *= 0xC2B2AE35u;"), proj)),
        ("decals not in redraw key", lambda: check_source(mod.replace('+ "/" + RM_BiomesSettings.worldBiomeDecals', ""), look, dec, proj)),
        ("spacing from tile count", lambda: check_source(mod, look, dec.replace("tileSpacing = 1.612f * circ / verts.Count;", "tileSpacing = Mathf.Sqrt(4f * Mathf.PI / Mathf.Max(1, pl.TilesCount));"), proj)),
        ("fade never ends", lambda: check_math(Decals(dec.replace("decalGoneAlt = 620f", "decalGoneAlt = 1200f")))),
        ("glyphs too big", lambda: check_math(Decals(dec.replace("decalSize = 0.30f", "decalSize = 0.55f")))),
    ]
    caught = 0
    for name, run in plants:
        e = run()
        caught += bool(e)
        print(("ok  " if e else "FAIL") + " plant '%s' %s" % (name, "caught" if e else "NOT caught"))
    # a mirror that drifted from the C# must also fail: a broken count rule
    bad = Decals(dec); bad.count = lambda t: 2 + Decals.hash(t, 0) % 3
    e = check_math(bad); caught += bool(e)
    print(("ok  " if e else "FAIL") + " plant '4 glyphs' %s" % ("caught" if e else "NOT caught"))
    import world_decal_atlas as W
    for name, attr, val in (("no shadow", "SHADOW_ALPHA", 0.0), ("lit from the lower right", "LIGHT", (1.0, 1.0))):
        keep = getattr(W, attr); setattr(W, attr, val)
        try:
            e = check_generator()
        finally:
            setattr(W, attr, keep)
        caught += bool(e)
        print(("ok  " if e else "FAIL") + " plant '%s' %s" % (name, "caught" if e else "NOT caught"))
    total = len(plants) + 3
    fails += total - caught
    print("RESULT %s: %d checks, %d plants caught of %d" % ("PASS" if not fails else "FAIL", 3, caught, total))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
