#!/usr/bin/env python3
"""render_terrain.py -- offline terrain grid renderer: 2-D grid -> PNG.

No game, no bridge, no mod set at runtime (beyond reading one static def
dump for name resolution). This is the iteration loop for the map
generator: render, LOOK, adjust -- see
infrastructure/state/items/TERRAIN_GRID_RENDERER_1.md.

Two input shapes render through the SAME colour-classification path so a
corpus save and a generated grid are comparable on one contact sheet:

INPUT A -- a corpus `.rws` save (see savemap.py's module docstring for the
grid codec). Decoded via savemap.SaveMap, using its "terrain" (topGrid)
grid and a shortHash->defName table loaded from a RimDefDump capture.
`savemap.load_hash_table(dump_dir, "TerrainDef")` expects
`<dump_dir>/defs/TerrainDef.json`, but the live DefDump folder nests that
one level deeper, per capture run: `<dump_dir>/captures/<ISO8601>/defs/
TerrainDef.json`. `_resolve_dump_dir()` below tries the literal layout
first, then falls back to the newest `captures/*` folder (ISO8601 names
sort chronologically as plain strings). If NEITHER resolves -- no
TerrainDef.json anywhere under dump_dir -- there is no name table at all;
cells are then decoded straight from the raw ushort grid (bypassing
SaveMap, which refuses to construct without a working hash table) and
rendered by a colour hashed deterministically from the raw shortHash, with
every cell counted unknown. This is a narrower, rarer fallback than the
ordinary case below: a save whose mod set includes terrain the *current*
dump does not know about (a genuinely gap-riddled but loaded table) still
renders those specific cells MAGENTA, same as any other unresolved name --
see the "unknown/unresolvable" rule below. The raw-hash colouring exists
only so a totally-absent dump doesn't masquerade as "zero unknown cells".

INPUT B -- a generated grid: a plain text file, one row per output row
(z), cells are defNames separated by commas:

    Sand,Sand,Soil,Gravel
    Sand,Rock,Rock,Gravel
    WaterDeep,WaterDeep,Rock,Rock

  - Every row must have the same cell count (grid width); a ragged file is
    a hard error.
  - Blank lines are skipped; whitespace around each cell is stripped.
  - defNames are matched case-insensitively by substring against PALETTE
    below; a defName matching no family renders MAGENTA and counts as an
    unknown cell (unknown_hashes is always 0 here -- there is no hash).

Palette: one fixed RGB colour per terrain FAMILY (below), chosen for VALUE
contrast over hue -- terrain has no UVs at thumbnail scale (see the
render-offline-from-live-captures memory). Unknown/unresolvable ->
MAGENTA (255, 0, 255), never grey, and always counted; the render prints
one stdout line: `unknown_cells=<n> unknown_hashes=<m>`.

CLI:

    render_terrain.py INPUT --out OUT.png [--px N] [--thumb]
                       [--dump-dir DIR]
    render_terrain.py --sheet A.rws B.txt ... --out SHEET.png [--px N]
                       [--dump-dir DIR]
    render_terrain.py --selftest

Uses Pillow when importable (confirmed present: PIL). Falls back to a
hand-rolled, stdlib-only PNG encoder (zlib + struct, no filtering beyond
None) when Pillow is absent -- see _write_png_manual().
"""
import argparse
import base64
import glob
import io
import os
import re
import struct
import sys
import tempfile
import zlib

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
import savemap

try:
    from PIL import Image, ImageDraw
    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False

DEFAULT_DUMP_DIR = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
                     "RimWorld by Ludeon Studios/DefDump")

MAGENTA = (255, 0, 255)

# One fixed colour per terrain family. Checked as a case-insensitive
# substring against the defName, IN THIS ORDER -- more specific families
# first so e.g. "MarshyTerrain" hits "marsh" before any broader term could
# claim it. Not exhaustive of every modded TerrainDef; anything that
# matches nothing here is an unknown cell (MAGENTA), which is the correct,
# visible behaviour for a modded corpus map.
PALETTE = [
    ("water",  (40,  80, 170)),
    ("marsh",  (95, 110,  80)),
    ("mud",    (101, 67,  33)),
    ("ice",    (205, 230, 240)),
    ("snow",   (240, 240, 245)),
    ("lava",   (200, 60,  20)),
    ("rock",   (95,  95, 100)),
    ("gravel", (150, 145, 135)),
    ("rough",  (140, 115, 90)),
    ("smooth", (190, 190, 185)),
    ("sand",   (225, 205, 150)),
    ("soil",   (120, 90,  60)),
    ("dirt",   (150, 120, 85)),   # PackedDirt: natural ground, not a floor
    ("floor",  (170, 170, 180)),
    ("tile",   (170, 170, 180)),   # built floors, same grey as "floor"
    ("flagstone", (170, 170, 180)),
    ("concrete",  (170, 170, 180)),
    ("metal",     (170, 170, 180)),
]


UNMATCHED = {}  # defName -> cell count, for every name that fell through PALETTE


def classify(defname):
    """defName -> family RGB, or None if it matches no family (=> MAGENTA).
    Every miss is tallied in UNMATCHED so the palette can be extended by name."""
    name = defname.lower()
    for substr, color in PALETTE:
        if substr in name:
            return color
    UNMATCHED[defname] = UNMATCHED.get(defname, 0) + 1
    return None


def _print_unmatched():
    """One stdout line naming the defNames that fell through PALETTE, most
    cells first (top 10) -- how the palette gets extended by name."""
    if UNMATCHED:
        top = sorted(UNMATCHED.items(), key=lambda kv: -kv[1])[:10]
        print("unmatched_names=" + ",".join("%s:%d" % kv for kv in top))


def hash_color(h):
    """Deterministic colour from a raw shortHash, used ONLY when no def
    dump at all could be resolved (see module docstring). Not part of the
    family palette -- just a stable, visually distinct fill so re-renders
    of the same unresolved corpus agree pixel-for-pixel. Still unknown.
    """
    r = (h * 2654435761) & 0xFFFFFF
    return ((r >> 16) & 0xFF, (r >> 8) & 0xFF, r & 0xFF)


def _resolve_dump_dir(dump_dir):
    """Find a directory savemap.load_hash_table() will actually accept.

    Tries <dump_dir>/defs/TerrainDef.json (the literal layout savemap.py
    expects) first, then the newest <dump_dir>/captures/*/defs/
    TerrainDef.json. Returns the effective dir to pass to savemap, or None
    if neither resolves.
    """
    if not dump_dir:
        return None
    direct = os.path.join(dump_dir, "defs", "TerrainDef.json")
    if os.path.isfile(direct):
        return dump_dir
    captures = sorted(glob.glob(os.path.join(dump_dir, "captures", "*")))
    for cand in reversed(captures):
        if os.path.isfile(os.path.join(cand, "defs", "TerrainDef.json")):
            return cand
    return None


def _raw_decode_terrain(path):
    """Decode topGridDeflate directly, bypassing SaveMap (which refuses to
    construct without a working hash table). Returns (w, h, [ushort, ...]).
    """
    text = io.open(path, encoding="utf-8", errors="replace").read()
    m = re.search(r"<mapSizeX>(\d+)</mapSizeX>.*?<mapSizeZ>(\d+)</mapSizeZ>",
                  text, re.S)
    w = int(m.group(1)) if m else 250
    h = int(m.group(2)) if m else 250
    m2 = re.search(r"<topGridDeflate>(.*?)</topGridDeflate>", text, re.S)
    if not m2:
        raise KeyError("no <topGridDeflate> in %s" % path)
    raw = zlib.decompress(base64.b64decode("".join(m2.group(1).split())), -15)
    arr = list(struct.unpack("<%dH" % (len(raw) // 2), raw[:len(raw) // 2 * 2]))
    return w, h, arr


def render_rws(path, dump_dir=DEFAULT_DUMP_DIR):
    """Corpus .rws -> (w, h, colors[row-major], unknown_cells, unknown_hashes)."""
    effective = _resolve_dump_dir(dump_dir)
    if effective:
        m = savemap.SaveMap(path, effective)
        w, h = m.w, m.h
        grid = m.grid("terrain")
        by_hash = m.by_hash
        colors = []
        unknown_cells = 0
        unknown_hashes = 0
        for hcode in grid:
            name = by_hash.get(hcode)
            if name is None:
                colors.append(MAGENTA)
                unknown_cells += 1
                unknown_hashes += 1
                continue
            c = classify(name)
            if c is None:
                colors.append(MAGENTA)
                unknown_cells += 1
            else:
                colors.append(c)
        return w, h, colors, unknown_cells, unknown_hashes
    else:
        w, h, grid = _raw_decode_terrain(path)
        colors = [hash_color(hc) for hc in grid]
        return w, h, colors, len(grid), len(grid)


def render_text_grid(path):
    """Generated defName grid (Input B) -> (w, h, colors, unknown_cells, 0)."""
    rows = []
    with io.open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\r\n")
            if not line.strip():
                continue
            rows.append([c.strip() for c in line.split(",")])
    if not rows:
        raise ValueError("empty grid file: %s" % path)
    w = len(rows[0])
    for i, r in enumerate(rows):
        if len(r) != w:
            raise ValueError("ragged grid in %s: row %d has %d cells, row 0 has %d"
                              % (path, i, len(r), w))
    h = len(rows)
    colors = []
    unknown_cells = 0
    for row in rows:
        for name in row:
            c = classify(name)
            if c is None:
                colors.append(MAGENTA)
                unknown_cells += 1
            else:
                colors.append(c)
    return w, h, colors, unknown_cells, 0


def render_grid(path, dump_dir=DEFAULT_DUMP_DIR):
    """Dispatch on extension: .rws -> render_rws, else -> render_text_grid."""
    if path.lower().endswith(".rws"):
        return render_rws(path, dump_dir)
    return render_text_grid(path)


# --------------------------------------------------------------- PNG output

def colors_to_image(w, h, colors, px):
    """Row-major RGB colours (w*h of them) -> a (w*px, h*px) image object.

    A Pillow Image when Pillow is present; otherwise a tiny stand-in with
    just enough surface (.size, .save) for the rest of this module.
    """
    if HAVE_PIL:
        img = Image.new("RGB", (w, h))
        img.putdata(colors)
        if px != 1:
            img = img.resize((w * px, h * px), Image.NEAREST)
        return img
    return _ManualImage(w, h, colors, px)


class _ManualImage(object):
    """Stand-in for a PIL Image when Pillow is unavailable."""

    def __init__(self, w, h, colors, px):
        self.w, self.h, self.colors, self.px = w, h, colors, px
        self.size = (w * px, h * px)
        self.width, self.height = self.size

    def save(self, path):
        _write_png_manual(path, self.w, self.h, self.colors, self.px)


def _write_png_manual(path, w, h, colors, px):
    """Hand-rolled PNG encoder: stdlib zlib + struct only, no filtering
    beyond "None" per scanline. Used only when Pillow cannot be imported.
    """
    W, H = w * px, h * px

    def scanline(y):
        cy = y // px
        row = bytearray([0])  # filter type 0 = None
        base = cy * w
        for x in range(W):
            r, g, b = colors[base + x // px]
            row += bytes((r, g, b))
        return bytes(row)

    raw = b"".join(scanline(y) for y in range(H))
    compressed = zlib.compress(raw, 9)

    def chunk(tag, data):
        body = tag + data
        return (struct.pack(">I", len(data)) + body
                + struct.pack(">I", zlib.crc32(body) & 0xffffffff))

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)  # 8-bit RGB
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", ihdr))
        f.write(chunk(b"IDAT", compressed))
        f.write(chunk(b"IEND", b""))


def _thumb_path(out_path):
    root, ext = os.path.splitext(out_path)
    return root + "_thumb" + (ext or ".png")


# ------------------------------------------------------------------- sheet

def build_sheet(inputs, dump_dir, px, out_path):
    """Several grids side by side on one contact sheet with a caption row.

    Captions are always printed to stdout too (the "caption legend"),
    since a corpus grid's unknown counts belong in the record either way.
    """
    entries = []
    for path in inputs:
        w, h, colors, uc, uh = render_grid(path, dump_dir)
        img = colors_to_image(w, h, colors, px)
        entries.append((os.path.basename(path), img, w, h, uc, uh))

    for name, img, w, h, uc, uh in entries:
        print("caption: %s size=%dx%d unknown_cells=%d unknown_hashes=%d"
              % (name, w, h, uc, uh))
    _print_unmatched()

    if not HAVE_PIL:
        raise SystemExit("sheet mode needs Pillow to compose one PNG "
                          "(not installed) -- captions printed above")

    pad, cap_h = 12, 20
    maxh = max(img.height for _, img, _, _, _, _ in entries)
    total_w = sum(img.width for _, img, _, _, _, _ in entries) + pad * (len(entries) + 1)
    sheet_h = maxh + cap_h + pad * 2
    sheet = Image.new("RGB", (total_w, sheet_h), (30, 30, 30))
    draw = ImageDraw.Draw(sheet)
    x = pad
    for name, img, w, h, uc, uh in entries:
        sheet.paste(img, (x, pad))
        caption = "%s %dx%d unk=%d/%d" % (name, w, h, uc, uh)
        draw.text((x, pad + maxh + 4), caption, fill=(255, 255, 255))
        x += img.width + pad
    sheet.save(out_path)
    return out_path


# ---------------------------------------------------------------- selftest

def run_selftest():
    passed = 0
    total = 2

    # (1) synthetic 20x20 grid: 3 known families (Sand/Soil/Gravel, 4 rows
    # each = 60 cells) + 2 unknown names (4 rows each = 80 cells).
    # Expected unknown_cells == 2 * 80 == 160.
    tmp = tempfile.mkdtemp(prefix="render_terrain_selftest_")
    try:
        families = (["Sand"] * 4 + ["Soil"] * 4 + ["Gravel"] * 4
                    + ["FooBarUnknown1"] * 4 + ["BazQuxUnknown2"] * 4)
        grid_path = os.path.join(tmp, "synthetic.txt")
        with io.open(grid_path, "w", encoding="utf-8") as f:
            f.write("\n".join(",".join([name] * 20) for name in families) + "\n")
        w, h, colors, uc, uh = render_text_grid(grid_path)
        px = 2
        img = colors_to_image(w, h, colors, px)
        ok = (w, h) == (20, 20) and img.size == (40, 40) and uc == 160 and uh == 0
        print("selftest 1 (synthetic grid): dims=%s unknown_cells=%d "
              "(expect 160) unknown_hashes=%d -> %s"
              % (img.size, uc, uh, "OK" if ok else "FAIL"))
        if ok:
            passed += 1
    except Exception as e:
        print("selftest 1 FAILED: %r" % (e,))

    # (2) one corpus map, if present on disk.
    corpus = ("/mnt/d/Luke/dev/Rimworld/research/RimMandrake/hand_authored_maps/"
              "World_45_In_Memory_of_Rain/InMemoryOfRain.rws")
    if os.path.isfile(corpus):
        try:
            w, h, colors, uc, uh = render_rws(corpus, DEFAULT_DUMP_DIR)
            px = 2
            img = colors_to_image(w, h, colors, px)
            ok = img.size == (w * px, h * px)
            print("selftest 2 (corpus %s): dims=%s mapSize=%dx%d "
                  "unknown_cells=%d unknown_hashes=%d -> %s"
                  % (os.path.basename(corpus), img.size, w, h, uc, uh,
                     "OK" if ok else "FAIL"))
            if ok:
                passed += 1
        except Exception as e:
            print("selftest 2 FAILED: %r" % (e,))
    else:
        print("selftest 2 SKIPPED: corpus not found at %s" % corpus)
        total -= 1

    result = "PASS" if passed == total else "FAIL"
    print("SELFTEST %s %d/%d" % (result, passed, total))
    return passed == total


# ----------------------------------------------------------------------- CLI

def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Offline terrain grid -> PNG renderer (see module docstring).")
    ap.add_argument("input", nargs="?", help="a .rws save or a defName-grid text file")
    ap.add_argument("--out", help="output PNG path")
    ap.add_argument("--px", type=int, default=2, help="pixels per cell (default 2)")
    ap.add_argument("--thumb", action="store_true", help="also write a 1px/cell copy")
    ap.add_argument("--dump-dir", default=DEFAULT_DUMP_DIR,
                     help="RimWorld DefDump folder for hash->defName resolution")
    ap.add_argument("--sheet", nargs="+", metavar="INPUT",
                     help="contact-sheet mode: several inputs -> one PNG (needs --out)")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return 0 if run_selftest() else 1

    if args.sheet:
        if not args.out:
            ap.error("--sheet requires --out")
        build_sheet(args.sheet, args.dump_dir, args.px, args.out)
        return 0

    if not args.input or not args.out:
        ap.error("INPUT and --out are required (or use --selftest / --sheet)")

    w, h, colors, uc, uh = render_grid(args.input, args.dump_dir)
    img = colors_to_image(w, h, colors, args.px)
    img.save(args.out)
    print("unknown_cells=%d unknown_hashes=%d" % (uc, uh))
    _print_unmatched()
    print("wrote %s (%dx%d px, %dx%d cells)" % (args.out, img.size[0], img.size[1], w, h))

    if args.thumb:
        timg = colors_to_image(w, h, colors, 1)
        tpath = _thumb_path(args.out)
        timg.save(tpath)
        print("wrote %s (thumb, %dx%d px)" % (tpath, timg.size[0], timg.size[1]))

    return 0


if __name__ == "__main__":
    sys.exit(main())
