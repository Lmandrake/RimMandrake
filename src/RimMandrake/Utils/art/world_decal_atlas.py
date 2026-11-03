#!/usr/bin/env python3
"""Biome decal atlases for the planet (WORLD_DECALS_BUILD_ATLAS_PIPELINE_ONCE, world look 4a). Procedural, no donor bytes.

The CONTRACT (what RM_WorldDecals.cs reads and what this script must write) is
design/Jawa/worldbuilding/world_decal_atlas_contract.md. In short: World/Decals/<BiomeDef defName>.png, square RGBA, cells
of 256 px (512 px = 2x2, 1024 px = 4x4), cells read left to right, top row first; every cell one upright glyph lit from
the upper left with a soft shadow down-right baked in; zero alpha on a margin round every cell so nothing bleeds.

Each biome is one ROW of design/Jawa/worldbuilding/world_decal_rows.json: its mod, grid side, palette (taken from the
biome's own sheet, which the row cites) and glyph list (names from GLYPHS below). The Baroque redo is "edit the row,
re-run gen, re-judge, install": no code changes.

usage:
  python3 world_decal_atlas.py gen     [--biome DEF ...] [--out DIR]   write <DEF>.png (+ a contact sheet) to DIR
  python3 world_decal_atlas.py check   PNG ...                          contract check of atlases on disk
  python3 world_decal_atlas.py install --biome DEF [--dry-run] [--out DIR]   art-ledger install (art.py install)
DIR defaults to <agent storage>/rimmandrake/scratch/world_decals/tex.
"""
import argparse, json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../.."))
ROWS = os.path.join(REPO, "design/Jawa/worldbuilding/world_decal_rows.json")
REL = "World/Decals/{}.png"
CELL = 256              # px per cell (RM_WorldDecals.CellPx)
SIDES = (1, 2, 4)       # grid sides the C# accepts (RM_WorldDecals.GridSide)
MARGIN = 8              # px of zero alpha round every cell
SS = 2                  # supersampling for antialiased edges
LIGHT = (-1.0, -1.0)    # light comes FROM the upper left (image x right, y down)
SHADOW_OFFSET = 7       # px, down-right
SHADOW_BLUR = 5         # px
SHADOW_ALPHA = 0.45


def storage_root():
    out = subprocess.run([sys.executable, os.path.expanduser("~/dev/Lodestar/bin/lib/agent_storage.py")],
                         capture_output=True, text=True)
    if out.returncode != 0 or not out.stdout.strip():
        sys.exit("agent storage root unknown: " + out.stderr.strip())
    return out.stdout.strip()


def default_out():
    return os.path.join(storage_root(), "rimmandrake", "scratch", "world_decals", "tex")


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ------------------------------------------------------------------ glyph bank: each draws a white mask on an L image
def _poly(d, pts, w=None):
    d.polygon(pts, fill=255) if w is None else d.line(pts, fill=255, width=w, joint="curve")


def g_rock(d, s, r):
    c, n = s / 2, r.integers(7, 11)
    pts = []
    for k in range(n):
        a = 2 * math.pi * k / n + r.uniform(-0.2, 0.2)
        rad = s * r.uniform(0.22, 0.32)
        pts.append((c + rad * math.cos(a), c + rad * 0.8 * math.sin(a) + s * 0.04))
    _poly(d, pts)


def g_dune(d, s, r):
    w, h = s * r.uniform(0.62, 0.72), s * r.uniform(0.26, 0.32)
    x0, y0 = (s - w) / 2, s * 0.5 - h / 2
    d.ellipse([x0, y0, x0 + w, y0 + h * 2], fill=255)
    d.ellipse([x0 + w * 0.12, y0 + h * 0.55, x0 + w * 1.05, y0 + h * 2.6], fill=0)


def g_shrub(d, s, r):
    for _ in range(r.integers(6, 10)):
        rad = s * r.uniform(0.08, 0.13)
        x, y = s / 2 + s * r.uniform(-0.16, 0.16), s * 0.5 + s * r.uniform(-0.14, 0.1)
        d.ellipse([x - rad, y - rad, x + rad, y + rad], fill=255)


def g_tuft(d, s, r):
    bx, by = s / 2, s * 0.72
    for k in range(r.integers(5, 8)):
        a = math.radians(-90 + r.uniform(-50, 50))
        ln = s * r.uniform(0.28, 0.42)
        tx, ty = bx + ln * math.cos(a), by + ln * math.sin(a)
        nx, ny = -math.sin(a) * s * 0.025, math.cos(a) * s * 0.025
        _poly(d, [(bx - nx, by - ny), (tx, ty), (bx + nx, by + ny)])


def g_crater(d, s, r):
    rad = s * r.uniform(0.28, 0.33)
    c = s / 2
    d.ellipse([c - rad, c - rad * 0.8, c + rad, c + rad * 0.8], fill=255)
    ir = rad * r.uniform(0.6, 0.7)
    d.ellipse([c - ir, c - ir * 0.8 + s * 0.02, c + ir, c + ir * 0.8 + s * 0.02], fill=0)


def g_spire(d, s, r):
    for _ in range(r.integers(1, 4)):
        x = s / 2 + s * r.uniform(-0.15, 0.15)
        w, h = s * r.uniform(0.08, 0.14), s * r.uniform(0.4, 0.6)
        base = s * 0.78
        _poly(d, [(x - w, base), (x + s * r.uniform(-0.03, 0.03), base - h), (x + w, base)])


def g_crystal(d, s, r):
    c = s / 2
    for k in range(r.integers(3, 5)):
        a = math.radians(-90 + r.uniform(-40, 40))
        ln, w = s * r.uniform(0.22, 0.36), s * r.uniform(0.04, 0.07)
        bx, by = c + s * r.uniform(-0.06, 0.06), s * 0.68
        tx, ty = bx + ln * math.cos(a), by + ln * math.sin(a)
        mx, my = (bx + tx) / 2, (by + ty) / 2
        nx, ny = -math.sin(a) * w, math.cos(a) * w
        _poly(d, [(bx, by), (mx + nx, my + ny), (tx, ty), (mx - nx, my - ny)])


def g_crack(d, s, r):
    pts, x, y = [], s * 0.2, s * 0.5
    while x < s * 0.8:
        pts.append((x, y))
        x += s * r.uniform(0.07, 0.12)
        y = s * 0.5 + s * r.uniform(-0.12, 0.12)
    _poly(d, pts, w=max(4, int(s * 0.035)))


def g_frond(d, s, r):
    bx, by, tx, ty = s / 2, s * 0.8, s / 2 + s * r.uniform(-0.08, 0.08), s * 0.2
    _poly(d, [(bx, by), (tx, ty)], w=max(3, int(s * 0.02)))
    for k in range(1, 8):
        t = k / 8
        x, y = bx + (tx - bx) * t, by + (ty - by) * t
        ln = s * 0.2 * (1 - t * 0.7)
        for side in (-1, 1):
            d.ellipse([x + side * ln * 0.5 - ln * 0.5, y - ln * 0.18, x + side * ln * 0.5 + ln * 0.5, y + ln * 0.18], fill=255)


def g_puff(d, s, r):
    c, cy = s / 2, s * 0.42
    _poly(d, [(c, s * 0.82), (c, cy)], w=max(3, int(s * 0.018)))
    for k in range(14):
        a = 2 * math.pi * k / 14
        rad, dot = s * 0.16, s * 0.035
        x, y = c + rad * math.cos(a), cy + rad * math.sin(a)
        d.ellipse([x - dot, y - dot, x + dot, y + dot], fill=255)
    d.ellipse([c - s * 0.05, cy - s * 0.05, c + s * 0.05, cy + s * 0.05], fill=255)


GLYPHS = {"rock": g_rock, "dune": g_dune, "shrub": g_shrub, "tuft": g_tuft, "crater": g_crater, "spire": g_spire,
          "crystal": g_crystal, "crack": g_crack, "frond": g_frond, "puff": g_puff}


# ------------------------------------------------------------------ one cell
def cell_image(glyph, palette, seed):
    """RGBA CELLxCELL: glyph shaded light->dark from the upper left, soft shadow down-right, zero-alpha margin."""
    if glyph not in GLYPHS:
        raise SystemExit("unknown glyph %r (bank: %s)" % (glyph, ", ".join(sorted(GLYPHS))))
    s = CELL * SS
    m = Image.new("L", (s, s), 0)
    inner = int(s * 0.86)                       # draw in an inner box, so the shadow and blur stay off the margin
    mi = Image.new("L", (inner, inner), 0)
    GLYPHS[glyph](ImageDraw.Draw(mi), inner, np.random.default_rng(seed))
    off = (s - inner) // 2 - SHADOW_OFFSET * SS // 2
    m.paste(mi, (off, off))
    m = m.resize((CELL, CELL), Image.LANCZOS)
    mask = np.asarray(m, dtype=np.float32) / 255.0

    # side light: emboss of the blurred mask against the light direction
    blur = np.asarray(m.filter(ImageFilter.GaussianBlur(3)), dtype=np.float32) / 255.0
    lx, ly = LIGHT
    sh = np.roll(np.roll(blur, int(-3 * ly), axis=0), int(-3 * lx), axis=1)   # sample toward the light
    relief = np.clip(0.5 + 2.2 * (blur - sh), 0.0, 1.0)
    dark, mid, light = (np.array(hex_rgb(c), dtype=np.float32) for c in palette["body"])
    t = relief[..., None]
    body = np.where(t < 0.5, dark + (mid - dark) * (t / 0.5), mid + (light - mid) * ((t - 0.5) / 0.5))

    # shadow: the mask moved down-right and blurred
    shadow = Image.fromarray((mask * 255).astype(np.uint8)).transform(
        (CELL, CELL), Image.AFFINE, (1, 0, -SHADOW_OFFSET, 0, 1, -SHADOW_OFFSET))
    shadow = np.asarray(shadow.filter(ImageFilter.GaussianBlur(SHADOW_BLUR)), dtype=np.float32) / 255.0 * SHADOW_ALPHA
    scol = np.array(hex_rgb(palette["shadow"]), dtype=np.float32)

    a_body = mask
    a_out = a_body + shadow * (1 - a_body)
    rgb = (body * a_body[..., None] + scol * (shadow * (1 - a_body))[..., None]) / np.maximum(a_out, 1e-6)[..., None]
    a_out[:MARGIN, :] = a_out[-MARGIN:, :] = 0
    a_out[:, :MARGIN] = a_out[:, -MARGIN:] = 0
    out = np.dstack([np.clip(rgb, 0, 255), np.clip(a_out * 255, 0, 255)]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def atlas(row, name):
    side = row["grid"]
    if side not in SIDES:
        raise SystemExit("%s: grid %r not in %s" % (name, side, SIDES))
    glyphs = row["glyphs"]
    img = Image.new("RGBA", (CELL * side, CELL * side), (0, 0, 0, 0))
    for k in range(side * side):
        g = glyphs[k % len(glyphs)]
        seed = sum(map(ord, name)) * 1009 + k * 7919   # stable across runs (Python's hash() is salted per process)
        img.paste(cell_image(g, row["palette"], seed), ((k % side) * CELL, (k // side) * CELL))
    return img


# ------------------------------------------------------------------ contract check
def check_atlas(path):
    """Return a list of contract violations for one PNG (empty = passes)."""
    errs = []
    im = Image.open(path)
    if im.mode != "RGBA":
        errs.append("mode %s, not RGBA" % im.mode)
        im = im.convert("RGBA")
    w, h = im.size
    if w != h or w % CELL or (w // CELL) not in SIDES:
        return errs + ["%dx%d is not a square %s atlas of %d px cells" % (w, h, "/".join(str(CELL * s) for s in SIDES), CELL)]
    side = w // CELL
    a = np.asarray(im)[..., 3]
    for k in range(side * side):
        c = a[(k // side) * CELL:(k // side + 1) * CELL, (k % side) * CELL:(k % side + 1) * CELL]
        rim = np.concatenate([c[:MARGIN].ravel(), c[-MARGIN:].ravel(), c[:, :MARGIN].ravel(), c[:, -MARGIN:].ravel()])
        if rim.max() > 0:
            errs.append("cell %d: alpha %d on its %d px margin (bleeds into the next cell)" % (k, rim.max(), MARGIN))
        cover = (c > 32).mean()
        if cover < 0.04:
            errs.append("cell %d: empty (%.1f%% covered)" % (k, cover * 100))
        if cover > 0.75:
            errs.append("cell %d: a block, not a glyph (%.1f%% covered)" % (k, cover * 100))
        if c.max() < 200:
            errs.append("cell %d: never opaque (max alpha %d)" % (k, c.max()))
    return errs


def load_rows():
    data = json.load(open(ROWS, encoding="utf-8"))
    return {k: v for k, v in data.items() if not k.startswith("_")}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gen"); g.add_argument("--biome", nargs="*"); g.add_argument("--out")
    c = sub.add_parser("check"); c.add_argument("png", nargs="+")
    i = sub.add_parser("install"); i.add_argument("--biome", required=True); i.add_argument("--out"); i.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.cmd == "check":
        bad = 0
        for p in args.png:
            errs = check_atlas(p)
            print(("ok   " if not errs else "FAIL ") + p + ("" if not errs else ": " + "; ".join(errs)))
            bad += bool(errs)
        return 1 if bad else 0
    rows = load_rows()
    out = args.out or default_out()
    os.makedirs(out, exist_ok=True)
    if args.cmd == "gen":
        names = args.biome or sorted(rows)
        for n in names:
            if n not in rows:
                sys.exit("no row for %s in %s" % (n, ROWS))
            p = os.path.join(out, n + ".png")
            atlas(rows[n], n).save(p)
            errs = check_atlas(p)
            print(("wrote " if not errs else "FAIL  ") + p + ("" if not errs else ": " + "; ".join(errs)))
            if errs:
                return 1
        return 0
    if args.cmd == "install":
        n = args.biome
        row = rows[n]
        src = os.path.join(out, n + ".png")
        if not os.path.exists(src) or check_atlas(src):
            sys.exit("run gen first; %s missing or failing the contract" % src)
        stage = os.path.join(REPO, "Transient", "world_decals_stage", n + ".png")   # art.py wants a file inside the clone
        os.makedirs(os.path.dirname(stage), exist_ok=True)
        Image.open(src).save(stage)
        cmd = [sys.executable, os.path.join(REPO, "src/RimMandrake/Utils/art/art.py"), "install", row["mod"], REL.format(n),
               "--file", os.path.relpath(stage, REPO), "--reason", "script:src/RimMandrake/Utils/art/world_decal_atlas.py"]
        if args.dry_run:
            cmd.append("--dry-run")
        return subprocess.run(cmd, cwd=REPO).returncode


if __name__ == "__main__":
    sys.exit(main())
