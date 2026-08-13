#!/usr/bin/env python3
"""
animal_contact_sheet.py — every animal's sprite on one wall of paper.

VERSION 1.0  (2026-08-10)   Project: D:/Luke/dev/Rimworld/src/RimMandrake/Utils/
Docs/manifest: src/RimMandrake/Utils/README.md  ("animal_contact_sheet.py" section)
Python 3.8+ stdlib **plus Pillow** — the same single third-party dependency
Savegame_mapview.py already carries. Nothing else. Keep it that way.

CHANGELOG
  1.0  first cut. Layer-2 projection over def_inventory.py, exactly like
       animal_inventory.py: it owns no load-set resolution, no XML parsing and
       no <ParentName> machinery. What it owns is "where does an animal's
       picture live on disk, and how do you lay 1,243 of them out so a human
       can review the roster in one sitting".

WHY THIS EXISTS
===============
animals.csv answers every question about an animal except the one you actually
ask first: *what does it look like?* Deciding which of 1,243 animals to keep,
cut, or re-skin for a Star Wars campaign is a visual judgement, and it cannot be
made from a spreadsheet. This renders the roster as paginated contact sheets in
EXACTLY animals.csv's row order — which is grouped by mod — so the sheet reads
as "here is what Alpha Animals contributes, here is what Beasts of the Rim
contributes", and a decision about a whole mod is one glance rather than 60
wiki lookups.

The output is deliberately a PAIR: the sheets, and an index CSV that maps every
cell back to (defName, mod, texPath, file on disk). A picture you cannot act on
is decoration. "Cell 3,7 looks wrong" has to become a defName and a file path,
or the tool has failed.

WHERE THE PICTURE ACTUALLY LIVES (the non-obvious part)
=======================================================
An animal's sprite is NOT on its ThingDef. `ThingDef.graphicData` is null for
every animal in the game — pawns are rendered from their PawnKindDef, because
different kinds of the same race (Bear_Grizzly vs Bear_Polar, worker vs queen)
can look different. So the path is:

    animals.csv row  ->  ThingDef defName
                     ->  PawnKindDef whose <race> is that defName
                     ->  lifeStages[LAST].bodyGraphicData.texPath
                     ->  a .png somewhere under some mod's Textures/

Four traps live in those four arrows, and each one silently costs coverage
rather than raising an error:

  1. lifeStages is ordered juvenile -> adult, so lifeStages[0] is the BABY.
     Taking the first entry gives you a sheet of puppies and chicks. We take
     the LAST entry, and the run confirms zero animals have a texPath on an
     earlier stage but not the last one, so nothing is lost by that rule.
  2. Several PawnKindDefs can share one race. We prefer the one whose defName
     equals the race defName (Muffalo -> Muffalo), else the first in load
     order, and RECORD which was used in the index CSV — because for a
     multi-kind race the choice is a real editorial decision, not a detail.
  3. texPath is extension-less and side-less. `Things/Pawn/Animal/Bear/Bear`
     is a family of files; the game appends `_south` / `_east` / `_north`
     itself. We try `_south` first (the front-facing view, which is what you
     want to look at), then the bare name, then the other sides. Matching is
     case-insensitive because mod authors are not consistent and NTFS does not
     punish them for it.
  4. Textures are indexed per mod from its LOADED content dirs *and* its root,
     not just the root — the same trap rimworld_loadset.py documents for Defs/.
     A mod with a LoadFolders.xml keeps its art under 1.6/Textures/, and
     indexing only <mod>/Textures/ finds nothing for it. Indexing happens in
     LOAD ORDER so a later mod retexturing an earlier one's path wins, which
     is what the game does.

WHAT THIS CANNOT SHOW — read this before reading the numbers
============================================================
**Roughly 40% of animals have no previewable sprite, and that is correct
behaviour, not a bug.** Vanilla and DLC art (Core, Odyssey, Anomaly, Ideology)
ships packed inside Unity asset bundles, not as loose PNGs, and several large
mods do the same — Star Wars Animal Collection ships exactly ONE loose PNG for
its whole roster; Jurassic Rimworld and JDS Separatist likewise. Extracting
Unity bundles is out of scope and stays out of scope: it needs a bundle
unpacker, it is version-fragile, and the payoff is a picture we could also get
by looking at the animal in game.

So the sheets cover the MODDED long tail, which is precisely the population the
keep/cut/re-skin decision is about — the vanilla animals are the ones you
already know by sight. `animal_textures_missing.csv` is therefore a deliverable
in its own right: it is the list of animals that can only be reviewed in game,
and (grouped by mod) the list of mods that bundle their art.

Three further blind spots, inherited from layer 1 and worth naming:
  * PatchOperations have not run. A mod that retextures an animal by patching
    its PawnKindDef's texPath is invisible here; we render the base XML's path.
  * MayRequire gating is not evaluated, so a lifeStages list inherited from an
    abstract base may include entries a real load would drop.
  * We render ONE still frame of ONE life stage from ONE side. Colour variation
    (`colorGenerator`), gender variants, body-size scaling by life stage and
    every mask/shader the game applies at draw time are all absent. The sheet
    tells you what the art asset is, not what the pawn looks like on the map.

DESIGN DECISIONS YOU MAY WANT TO OVERRULE (all are CLI flags)
=============================================================
  * BACKGROUND IS A CHECKERBOARD, not a flat colour. These are alpha PNGs and
    the roster contains both near-black silhouettes (Alpha Animals' void
    creatures) and near-white ones (arctic fauna). Any single flat background
    makes one of those two groups invisible, which would defeat the entire
    purpose of the sheet. A two-tone mid-grey check keeps both readable and
    also makes it obvious where the sprite's transparent bounds are.
    `--flat-bg RRGGBB` if you disagree.
  * SPRITES ARE TRIMMED to their alpha bounding box by default (`--no-trim`).
    RimWorld art carries a lot of empty margin, and untrimmed the sheet is
    mostly background. The cost is that relative animal SIZE is no longer
    readable off the sheet — a chinchilla and a thrumbo fill the same cell. If
    you are eyeballing scale rather than design, pass --no-trim.
  * MISSING ANIMALS ARE OMITTED from the sheets (`--include-missing` draws a
    placeholder cell instead). At ~40% missing, placeholders would waste four
    pages in ten. The missing CSV is the better instrument for that question.
  * Duplicate defNames are NOT deduplicated. animals.csv has 1,243 rows for
    1,197 distinct defNames because mods redefine each other; those rows are
    kept, so a doubled cell means "two mods claim this animal" — which is
    exactly the kind of thing this review should catch. The index CSV carries
    the source row's `duplicateDefName` so a doubled cell is explicable.
  * Upscaling is capped (`--max-upscale`, default 2.0) and uses NEAREST, so a
    64px sprite is shown at 128px sharp rather than at 152px blurred. Honest
    about resolution; a suspiciously small cell means a suspiciously small art
    asset.

OUTPUTS (to --out)
==================
  animal_sheet_NN.png          the paginated sheets
  animal_sheet_index.csv       one row per PLACED cell: page/row/col ->
                               defName, mod, pawnkind, life stage, texPath,
                               resolved file, pixel size. The actionable half.
  animal_textures_missing.csv  one row per animal with no previewable sprite,
                               with a machine-readable `reason`.

USAGE
=====
  python animal_contact_sheet.py --csv ..\\mods\\inventory\\animals.csv --out .\\out
  python animal_contact_sheet.py --cols 12 --rows 8 --cell 200 --out .\\out
  python animal_contact_sheet.py --limit 60 --out .\\smoke     # fast smoke test

PERFORMANCE
===========
Run natively on Windows. Indexing ~43,500 loose PNGs is a directory walk with
no file opens (~1 s); only the ~700 files actually PLACED are ever decoded.
Whole run is a few seconds. If it becomes minutes you are on the device bridge
— see the note in animal_inventory.py.
"""

import argparse
import colorsys
import csv
import os
import random
import sys
import time
from collections import defaultdict

# Layer 1. Load-set resolution, the single parse of every def file, and
# <ParentName> merging all live there. This file asks for exactly two things:
# the resolved PawnKindDef elements, and ds.mods (for the texture index, which
# must use the same contentDirs the def scan used or the two disagree about
# which mod folders are live).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from def_inventory import build, txt, D_CONFIG, D_WORKSHOP, D_LOCAL, D_DATA  # noqa: E402

VERSION = "1.0"

# Only PawnKindDef is needed. This narrows how many DefRecords get allocated;
# it does NOT narrow the parse or the global Name index (see def_inventory).
WANT_TYPES = ("PawnKindDef",)

# Repo-relative default for the ordering CSV, resolved against this file's
# location so the tool works from any cwd.
DEFAULT_CSV = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "observed", "2026-08-13_pre-restructure", "inventory", "animals.csv"))

# Side suffixes, in the order we want them. `_south` is the front view and is
# what a human recognises an animal by; the bare name covers mods that ship a
# single omnidirectional texture; the rest are last-resort so that "we have SOME
# picture" beats "we have none".
TEX_SUFFIXES = ("_south", "", "_east", "_north", "_side")

# ------------------------------------------------------------------ palette
BG_PAGE = (26, 27, 31)          # page paper: darker than any cell, so the gaps
                                # between cells read as separators for free
BG_HEADER = (18, 19, 22)
BG_CAPTION = (34, 35, 40)
FG_TITLE = (236, 238, 242)
FG_SUB = (150, 154, 162)
FG_NAME = (240, 242, 246)
FG_MOD = (146, 150, 158)
GRID = (58, 60, 66)
CHECK_A = (108, 110, 116)       # mid-grey pair. Deliberately NOT far apart and
CHECK_B = (128, 130, 136)       # deliberately mid-luminance: dark sprites read
                                # against it, light sprites read against it.
BG_PLACEHOLDER = (46, 40, 40)
FG_PLACEHOLDER = (120, 96, 96)


# ------------------------------------------------------------------ fonts
def load_font(size, bold=False):
    """
    A TrueType font at `size`, or the bitmap fallback.

    Pillow's bundled DejaVu is not guaranteed to be present in every build, and
    ImageFont.load_default() ignores size on older Pillow, so we walk a list of
    real Windows faces first. Font choice is cosmetic — never let it abort a run.
    """
    from PIL import ImageFont
    names = (["segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"] if bold
             else ["segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"])
    for n in names:
        for base in (r"C:\Windows\Fonts", ""):
            try:
                return ImageFont.truetype(os.path.join(base, n) if base else n, size)
            except Exception:
                continue
    try:
        return ImageFont.load_default(size=size)     # Pillow >= 10
    except Exception:
        return ImageFont.load_default()


def text_w(draw, s, font):
    try:
        return int(draw.textlength(s, font=font))
    except Exception:                                # very old Pillow
        return draw.textsize(s, font=font)[0]


def fit_text(draw, s, font, max_w):
    """Truncate with an ellipsis so a long defName cannot bleed into its neighbour."""
    if not s:
        return ""
    if text_w(draw, s, font) <= max_w:
        return s
    ell = "\u2026"
    lo, hi = 0, len(s)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if text_w(draw, s[:mid] + ell, font) <= max_w:
            lo = mid
        else:
            hi = mid - 1
    return s[:lo] + ell if lo else ""


def mod_color(name):
    """
    Deterministic accent colour per mod name.

    Same trick as Savegame_mapview.color_for_index, but keyed on the NAME rather
    than an index so a mod keeps its colour across runs and across pages even
    when the roster changes. Saturation is kept low and value high so the strip
    reads as a grouping cue, not as data.
    """
    h = (hash(name) & 0xFFFF) / 65535.0
    r, g, b = colorsys.hsv_to_rgb(h, 0.45, 0.78)
    return (int(r * 255), int(g * 255), int(b * 255))


# ------------------------------------------------------------------ textures
def build_texture_index(mods):
    """
    {lowercased path relative to a Textures/ root -> absolute file} over every
    loose PNG in the load set.

    Two things make this correct rather than nearly correct:

      * every LOADED content dir is searched, plus the mod root. A mod with a
        LoadFolders.xml puts its art under 1.6/Textures/ and has nothing at
        <mod>/Textures/; a mod without one may use either or both. Same trap
        rimworld_loadset.py documents for Defs/, same fix.
      * iteration is in LOAD ORDER and later writes overwrite earlier ones, so
        a retexture mod beats the mod it retextures — which is the game's rule.

    No file is opened here. This is a pure directory walk over ~43,500 files and
    costs about a second; decoding happens only for the ~700 we actually place.
    """
    index = {}
    files_seen = 0
    dirs_seen = 0
    for m in mods:
        roots = []
        for base in list(m.get("contentDirs") or []) + [m["folder"]]:
            p = os.path.join(base, "Textures")
            if os.path.isdir(p) and p not in roots:
                roots.append(p)
        dirs_seen += len(roots)
        for tex_root in roots:
            for dirpath, _, files in os.walk(tex_root):
                rel_dir = os.path.relpath(dirpath, tex_root)
                for fn in files:
                    if not fn.lower().endswith(".png"):
                        continue
                    files_seen += 1
                    rel = fn if rel_dir == "." else os.path.join(rel_dir, fn)
                    index[rel.replace("\\", "/").lower()] = os.path.join(dirpath, fn)
    return index, files_seen, dirs_seen


def resolve_texture(tex_path, index):
    """(absolute file, suffix used) for a def's texPath, or (None, None)."""
    if not tex_path:
        return None, None
    base = tex_path.replace("\\", "/").strip("/").lower()
    for suf in TEX_SUFFIXES:
        hit = index.get(base + suf + ".png")
        if hit:
            return hit, (suf or "<bare>")
    return None, None


# ------------------------------------------------------------------ pawnkinds
def build_pawnkind_map(ds):
    """
    {race defName -> [pawnkind info, ...]} in load order.

    Read off `.element`, i.e. AFTER <ParentName> merging, and that matters here
    in a way it does not in animal_inventory.py: a large number of modded
    PawnKindDefs declare nothing but <defName>/<race> and inherit their whole
    lifeStages block (and therefore their texPath) from an abstract base. Read
    unmerged, those animals have no picture at all.

    (animal_inventory.py v1.5 deliberately still reads pawnkinds from `.own`,
    for behaviour-neutrality with v1.4. That hold does not apply to a new tool,
    and the two files' pawnkind-derived columns are not compared anywhere.)
    """
    by_race = defaultdict(list)
    for rec in ds.of_type("PawnKindDef"):
        el = rec.element
        race = txt(el, "race")
        if not race:
            continue
        stages = el.findall("lifeStages/li")
        # LAST stage = adult. See trap 1 in the module docstring.
        tex = txt(stages[-1], "bodyGraphicData/texPath") if stages else ""
        by_race[race].append({
            "defName": rec.defName, "modName": rec.modName,
            "stageCount": len(stages), "stageIndex": (len(stages) - 1) if stages else -1,
            "texPath": tex,
        })
        rec.release()                                # do not hold 1,700 merged trees
    return by_race


def pick_pawnkind(race, kinds):
    """
    Which PawnKindDef speaks for this race.

    Preference order: the kind whose defName IS the race defName (the canonical
    one — Muffalo/Muffalo), then the first kind in load order that actually has
    a texPath, then the first kind at all. The choice is recorded per cell in
    the index CSV because for a multi-kind race it is an editorial call, and a
    reviewer looking at a Megascarab has a right to know they are looking at the
    worker rather than the queen.
    """
    if not kinds:
        return None
    for k in kinds:
        if k["defName"] == race:
            return k
    for k in kinds:
        if k["texPath"]:
            return k
    return kinds[0]


# ------------------------------------------------------------------ csv input
def read_animals_csv(path):
    """
    animals.csv rows, IN FILE ORDER. Order is the whole point — it is grouped by
    mod, which is what makes the sheet reviewable a mod at a time.

    utf-8-sig because animal_inventory.py writes a BOM (Excel wants it); reading
    it as plain utf-8 corrupts the first column name and silently loses defName.
    """
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


# ------------------------------------------------------------------ planning
def plan_cells(rows, by_race, tex_index):
    """
    Walk animals.csv in order and split it into (placed, missing).

    Nothing is decoded here; this is pure bookkeeping, so the expensive image
    work below runs over a known-length list and the page count is known before
    the first pixel is drawn.

    `reason` on a missing row is the deliverable. Four distinct causes, and they
    mean genuinely different things:
      no_defName    the csv row is an abstract base (no defName), not an animal
      no_pawnkind   no PawnKindDef anywhere references this race
      no_texPath    a pawnkind exists but declares no bodyGraphicData/texPath
      no_loose_png  a texPath exists and no loose PNG matches it — the asset
                    bundle case, i.e. "exists, but not previewable offline"
    """
    placed, missing = [], []
    for i, row in enumerate(rows, 1):
        dn = (row.get("defName") or "").strip()
        base = {
            "csvRow": i, "defName": dn, "label": row.get("label", ""),
            "modName": row.get("modName", ""), "packageId": row.get("packageId", ""),
            "loadOrder": row.get("loadOrder", ""),
            "duplicateDefName": row.get("duplicateDefName", ""),
        }
        if not dn:
            missing.append(dict(base, reason="no_defName", texPath="",
                                pawnKindDefName="",
                                detail=row.get("abstractName", "")))
            continue
        kinds = by_race.get(dn) or []
        kind = pick_pawnkind(dn, kinds)
        if kind is None:
            missing.append(dict(base, reason="no_pawnkind", texPath="",
                                pawnKindDefName="", detail=""))
            continue
        common = dict(base, pawnKindDefName=kind["defName"],
                      pawnKindCount=len(kinds), pawnKindMod=kind["modName"],
                      lifeStageIndex=kind["stageIndex"],
                      lifeStageCount=kind["stageCount"],
                      texPath=kind["texPath"])
        if not kind["texPath"]:
            missing.append(dict(common, reason="no_texPath", detail=""))
            continue
        path, suf = resolve_texture(kind["texPath"], tex_index)
        if not path:
            missing.append(dict(common, reason="no_loose_png", detail=""))
            continue
        placed.append(dict(common, textureFile=path, texSuffix=suf))
    return placed, missing


# ------------------------------------------------------------------ sprites
def load_sprite(path, trim):
    """
    One sprite as RGBA, optionally trimmed to its alpha bounding box.

    Returns (image, note) or (None, reason). NEVER raises: some fraction of
    43,500 mod PNGs are truncated, mis-declared, or 0x0, and one bad file must
    cost one cell, not the run. Failure reasons are written to the missing CSV
    so a corrupt asset is reported rather than silently absent.
    """
    from PIL import Image
    try:
        im = Image.open(path)
        im.load()                                    # force decode HERE, inside
                                                     # the try: Image.open() is
                                                     # lazy and a truncated file
                                                     # only blows up on access
    except Exception as exc:
        return None, "unreadable_png:%s" % type(exc).__name__
    try:
        if im.mode != "RGBA":
            im = im.convert("RGBA")
        if trim:
            bbox = im.getchannel("A").getbbox()
            if bbox is None:
                # Fully transparent. Real, and worth naming: a placeholder asset
                # or a mod shipping an empty file. Cropping it would throw.
                return None, "blank_png"
            im = im.crop(bbox)
        if im.width < 1 or im.height < 1:
            return None, "zero_size_png"
        return im, ""
    except Exception as exc:
        return None, "decode_failed:%s" % type(exc).__name__


def fit_sprite(im, box_w, box_h, max_upscale):
    """
    Scale to fit the box, aspect preserved, never blurring a small sprite.

    Downscale with LANCZOS (mod art is photographic-ish, not pixel art, and
    LANCZOS keeps thin limbs and antennae legible at 1/4 size). Upscale with
    NEAREST and only up to max_upscale, because a 3x bicubic enlargement of a
    48px asset looks like a smudge and lies about the asset's quality.
    """
    from PIL import Image
    scale = min(box_w / float(im.width), box_h / float(im.height))
    if scale >= 1.0:
        scale = min(scale, max(1.0, max_upscale))
        resample = Image.NEAREST
    else:
        resample = Image.LANCZOS
    w = max(1, int(round(im.width * scale)))
    h = max(1, int(round(im.height * scale)))
    if (w, h) != (im.width, im.height):
        im = im.resize((w, h), resample)
    return im


def checker_tile(w, h, size, ca, cb):
    """One reusable checkerboard the size of a sprite well. Built once per run."""
    from PIL import Image
    tile = Image.new("RGB", (w, h), ca)
    px = tile.load()
    for y in range(h):
        yodd = (y // size) & 1
        for x in range(w):
            if ((x // size) & 1) ^ yodd:
                px[x, y] = cb
    return tile


# Packed-earth palette, sampled to sit in the same mid-luminance band a
# checkerboard occupied. That band is the whole point: it is what keeps Alpha
# Animals' near-black silhouettes AND arctic mods' near-white ones readable
# against the same background.
EARTH_DARK = (74, 58, 42)
EARTH_LITE = (152, 120, 88)


def earth_tile(w, h, seed=1701):
    """
    A packed-earth ground tile, in the spirit of RimWorld's soil terrain.

    Generated rather than sampled from the game: vanilla terrain art is packed
    into Unity asset bundles and is not on disk as PNGs (the same reason 40% of
    this sheet's animals cannot be previewed), so there is nothing to copy.
    Generating it also keeps the result deterministic and lets us pin the
    contrast where sprites stay legible.

    Three octaves of value noise — coarse blotches, medium mottling, fine grain
    — then a scatter of pebbles. Built ONCE per run and reused for every cell,
    so the per-pixel Python loops here cost nothing at sheet scale.
    """
    from PIL import Image, ImageDraw, ImageFilter
    rnd = random.Random(seed)

    def octave(div, lo, hi, resample):
        ow, oh = max(2, w // div), max(2, h // div)
        layer = Image.new("L", (ow, oh))
        layer.putdata([rnd.randint(lo, hi) for _ in range(ow * oh)])
        return layer.resize((w, h), resample)

    coarse = octave(9, 70, 185, Image.BICUBIC)
    medium = octave(4, 100, 155, Image.BILINEAR)
    fine = octave(1, 116, 140, Image.NEAREST)

    v = Image.blend(coarse, medium, 0.45)
    v = Image.blend(v, fine, 0.22)
    v = v.filter(ImageFilter.SMOOTH)

    # Map the single value channel onto the brown ramp.
    out = Image.new("RGB", (w, h))
    src, dst = v.load(), out.load()
    dr = EARTH_LITE[0] - EARTH_DARK[0]
    dg = EARTH_LITE[1] - EARTH_DARK[1]
    db = EARTH_LITE[2] - EARTH_DARK[2]
    for y in range(h):
        for x in range(w):
            t = src[x, y] / 255.0
            dst[x, y] = (EARTH_DARK[0] + int(dr * t),
                         EARTH_DARK[1] + int(dg * t),
                         EARTH_DARK[2] + int(db * t))

    # Pebbles and grit. Sparse on purpose — this is a backdrop, and anything
    # busier competes with the sprite it exists to show off.
    d = ImageDraw.Draw(out)
    for _ in range(max(6, (w * h) // 700)):
        px_, py_ = rnd.randrange(w), rnd.randrange(h)
        rad = rnd.choice((1, 1, 1, 2))
        shade = rnd.randint(-26, 22)
        base = dst[px_, py_]
        d.ellipse([px_ - rad, py_ - rad, px_ + rad, py_ + rad],
                  fill=tuple(max(0, min(255, ch + shade)) for ch in base))
    return out


def ground_shadow(sprite, blur=3, opacity=110, squash=0.34):
    """
    A soft elliptical shadow to sit the sprite ON the ground rather than float
    it over a texture.

    Earned its place: a mottled background is busier than a flat checkerboard,
    so sprite edges lose separation without it. Derived from the sprite's own
    alpha, so it follows the actual silhouette instead of being a generic blob.
    """
    from PIL import Image, ImageFilter
    alpha = sprite.getchannel("A")
    sw, sh = alpha.size
    fh = max(3, int(sh * squash))
    squashed = alpha.resize((sw, fh), Image.BILINEAR)

    pad = blur * 3
    layer = Image.new("L", (sw + pad * 2, fh + pad * 2), 0)
    layer.paste(squashed, (pad, pad))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    layer = layer.point(lambda v: int(v * opacity / 255))

    shadow = Image.new("RGBA", layer.size, (18, 12, 8, 0))
    shadow.putalpha(layer)
    return shadow, pad


# ------------------------------------------------------------------ rendering
ACCENT_H = 4                    # per-mod colour strip at the top of every cell
TAG_H = 15                      # mod-name tag, drawn on the first cell of a run
MARGIN = 22
GAP = 3                         # page background showing through == separator
HEADER_H = 58


def render_page(cells, page_no, page_count, args, fonts, tile, stamp):
    """
    One sheet. `cells` is up to cols*rows entries, in order.

    Entries flagged `_ph` (placeholders, only present under --include-missing)
    are SKIPPED here but still consume their grid position, so the placeholder
    pass can draw them at the same coordinates. There is exactly one place where
    a cell's (x, y) is computed from its index, and getting that wrong is the
    obvious way to produce overlapping cells.

    Layout per cell:
        [ accent strip           ]  4px, colour == mod, so a run of one mod's
        [                        ]      animals reads as a continuous band
        [   sprite on checker    ]  the well; first cell of a mod run also
        [                        ]      carries a small mod-name tag
        [ defName / modName      ]  caption, two lines, dim second line
    """
    from PIL import Image, ImageDraw

    cw, ch = args.cell, args.cell + args.caption
    well_h = args.cell - ACCENT_H
    page_w = MARGIN * 2 + args.cols * cw + (args.cols - 1) * GAP
    page_h = MARGIN * 2 + HEADER_H + args.rows * ch + (args.rows - 1) * GAP

    img = Image.new("RGB", (page_w, page_h), BG_PAGE)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, page_w, HEADER_H + MARGIN // 2], fill=BG_HEADER)

    mods_here = []
    for c in cells:
        if not mods_here or mods_here[-1] != c["modName"]:
            mods_here.append(c["modName"])
    span = mods_here[0] if len(mods_here) == 1 else "%s \u2192 %s" % (
        mods_here[0], mods_here[-1])
    n_draw = sum(1 for c in cells if not c.get("_ph"))

    draw.text((MARGIN, 14), "RimWorld animal contact sheet \u2014 page %d of %d"
              % (page_no, page_count), font=fonts["title"], fill=FG_TITLE)
    draw.text((MARGIN, 38), fit_text(
        draw, "%d sprites  \u00b7  %d mods: %s  \u00b7  %s"
        % (n_draw, len(mods_here), span, stamp),
        fonts["sub"], page_w - 2 * MARGIN), font=fonts["sub"], fill=FG_SUB)

    placed_rows = []
    prev_mod = None
    for i, c in enumerate(cells):
        if c.get("_ph"):
            # Position consumed, drawing deferred. prev_mod is deliberately NOT
            # updated: a placeholder must not suppress the next real cell's tag.
            continue
        r, col = divmod(i, args.cols)
        x0 = MARGIN + col * (cw + GAP)
        y0 = MARGIN + HEADER_H + r * (ch + GAP)
        accent = mod_color(c["modName"])

        draw.rectangle([x0, y0, x0 + cw - 1, y0 + ch - 1], fill=BG_CAPTION,
                       outline=GRID)
        draw.rectangle([x0, y0, x0 + cw - 1, y0 + ACCENT_H - 1], fill=accent)
        wy = y0 + ACCENT_H
        img.paste(tile, (x0, wy))

        sprite, note = load_sprite(c["textureFile"], not args.no_trim)
        if sprite is None:
            # A cell we planned but could not decode. Kept visible on purpose —
            # a red X in the grid is a finding, and it is carried out to the
            # missing CSV by the caller via c["renderError"].
            c["renderError"] = note
            draw.line([x0 + 8, wy + 8, x0 + cw - 8, wy + well_h - 8],
                      fill=(190, 80, 80), width=2)
            draw.line([x0 + cw - 8, wy + 8, x0 + 8, wy + well_h - 8],
                      fill=(190, 80, 80), width=2)
            c["imageW"] = c["imageH"] = ""
        else:
            c["imageW"], c["imageH"] = sprite.width, sprite.height
            fitted = fit_sprite(sprite, cw - 8, well_h - 8 - TAG_H, args.max_upscale)
            px = x0 + (cw - fitted.width) // 2
            py = wy + TAG_H + (well_h - TAG_H - fitted.height) // 2

            # Shadow first, so the sprite lands on top of it.
            if not args.no_shadow:
                shadow, pad = ground_shadow(fitted)
                sx = px - pad
                sy = py + fitted.height - shadow.height + pad // 2
                img.paste(shadow, (sx, sy), shadow)

            img.paste(fitted, (px, py), fitted)      # alpha over the ground
            sprite.close()

        # Mod-name tag only where the mod CHANGES. Repeating it on every cell
        # would be visual noise; the accent strip already carries continuity.
        if c["modName"] != prev_mod:
            label = fit_text(draw, c["modName"], fonts["tag"], cw - 8)
            tw = text_w(draw, label, fonts["tag"])
            draw.rectangle([x0, wy, x0 + tw + 8, wy + TAG_H - 1], fill=accent)
            draw.text((x0 + 4, wy + 1), label, font=fonts["tag"], fill=(16, 16, 18))
            prev_mod = c["modName"]

        cy = y0 + args.cell
        draw.text((x0 + 4, cy + 2),
                  fit_text(draw, c["defName"], fonts["name"], cw - 8),
                  font=fonts["name"], fill=FG_NAME)
        draw.text((x0 + 4, cy + 16),
                  fit_text(draw, c["modName"], fonts["mod"], cw - 8),
                  font=fonts["mod"], fill=FG_MOD)

        c["page"], c["row"], c["col"] = page_no, r, col
        placed_rows.append(c)

    return img, placed_rows


# ------------------------------------------------------------------ output
INDEX_COLS = ["page", "row", "col", "csvRow", "defName", "label", "modName",
              "packageId", "loadOrder", "duplicateDefName", "pawnKindDefName",
              "pawnKindMod", "pawnKindCount", "lifeStageIndex", "lifeStageCount",
              "texPath", "texSuffix", "textureFile", "imageW", "imageH",
              "renderError"]

MISSING_COLS = ["csvRow", "defName", "label", "modName", "packageId", "loadOrder",
                "reason", "texPath", "pawnKindDefName", "pawnKindCount",
                "lifeStageIndex", "lifeStageCount", "textureFile", "detail"]


def write_csv(path, cols, rows):
    # utf-8-sig to match every other CSV this project emits (Excel needs the BOM).
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:
        wr = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        wr.writeheader()
        wr.writerows(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Paginated contact sheet of every animal's sprite, in "
                    "animals.csv order.")
    ap.add_argument("--csv", default=DEFAULT_CSV,
                    help="animals.csv — supplies BOTH the row order and the labels")
    ap.add_argument("--out", default="./out")
    ap.add_argument("--config", default=D_CONFIG)
    ap.add_argument("--workshop", default=D_WORKSHOP)
    ap.add_argument("--local", default=D_LOCAL)
    ap.add_argument("--data", default=D_DATA)
    ap.add_argument("--cell", type=int, default=160, help="cell size in px")
    ap.add_argument("--caption", type=int, default=32, help="caption strip height in px")
    ap.add_argument("--cols", type=int, default=14)
    ap.add_argument("--rows", type=int, default=9)
    ap.add_argument("--bg", choices=("earth", "checker"), default="earth",
                    help="cell background: generated packed earth (default) or checkerboard")
    ap.add_argument("--check", type=int, default=10, help="checkerboard square px")
    ap.add_argument("--flat-bg", default="", metavar="RRGGBB",
                    help="flat cell background; overrides --bg")
    ap.add_argument("--no-shadow", action="store_true",
                    help="omit the soft ground shadow under each sprite")
    ap.add_argument("--no-trim", action="store_true",
                    help="do NOT crop sprites to their alpha bbox (keeps relative scale)")
    ap.add_argument("--max-upscale", type=float, default=2.0)
    ap.add_argument("--include-missing", action="store_true",
                    help="draw placeholder cells for animals with no sprite")
    ap.add_argument("--limit", type=int, default=0, help="stop after N csv rows (smoke test)")
    ap.add_argument("--no-image", action="store_true", help="CSVs only, write no PNGs")
    a = ap.parse_args(argv)

    t0 = time.perf_counter()
    os.makedirs(a.out, exist_ok=True)

    if not os.path.isfile(a.csv):
        sys.exit("no animals.csv at %s (run animal_inventory.py first)" % a.csv)
    rows = read_animals_csv(a.csv)
    if a.limit:
        rows = rows[:a.limit]

    ds = build(a.config, a.workshop, a.local, a.data, types=WANT_TYPES, quiet=True)
    t_scan = time.perf_counter() - t0
    print("load set: version %s, %d active mods -> %d content folders"
          % (ds.gameVersion, len(ds.mods),
             sum(len(m["contentDirs"]) for m in ds.mods)))

    t = time.perf_counter()
    tex_index, n_png, n_texdirs = build_texture_index(ds.mods)
    t_index = time.perf_counter() - t
    print("textures: %d loose PNGs in %d Textures/ roots -> %d distinct paths"
          % (n_png, n_texdirs, len(tex_index)))

    by_race = build_pawnkind_map(ds)
    placed, missing = plan_cells(rows, by_race, tex_index)
    print("animals.csv rows: %d   resolvable sprites: %d   missing: %d"
          % (len(rows), len(placed), len(missing)))

    if a.include_missing:
        # Re-interleave so placeholders keep their true position in csv order.
        merged = sorted([dict(p, _ph=False) for p in placed]
                        + [dict(m, _ph=True) for m in missing],
                        key=lambda r: r["csvRow"])
    else:
        merged = [dict(p, _ph=False) for p in placed]

    per_page = a.cols * a.rows
    pages = (len(merged) + per_page - 1) // per_page if merged else 0

    index_rows, page_files = [], []
    t = time.perf_counter()
    if not a.no_image and merged:
        from PIL import Image
        fonts = {"title": load_font(19, bold=True), "sub": load_font(13),
                 "tag": load_font(11, bold=True), "name": load_font(13, bold=True),
                 "mod": load_font(11)}
        if a.flat_bg:
            rgb = tuple(int(a.flat_bg.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
            tile = Image.new("RGB", (a.cell, a.cell - ACCENT_H), rgb)
        elif a.bg == "checker":
            tile = checker_tile(a.cell, a.cell - ACCENT_H, a.check, CHECK_A, CHECK_B)
        else:
            tile = earth_tile(a.cell, a.cell - ACCENT_H)
        stamp = time.strftime("%Y-%m-%d %H:%M")
        for p in range(pages):
            chunk = merged[p * per_page:(p + 1) * per_page]
            img, done = render_page(chunk, p + 1, pages, a, fonts, tile, stamp)
            if a.include_missing:
                _draw_placeholders(img, chunk, a, fonts)
            name = "animal_sheet_%02d.png" % (p + 1)
            img.save(os.path.join(a.out, name))
            page_files.append(name)
            index_rows.extend(done)
            img.close()
    t_render = time.perf_counter() - t

    # A cell we planned but whose PNG would not decode stays in the index (it
    # occupies a grid position and you must be able to look up the red X) AND is
    # also reported as missing, because it has no previewable sprite. Those are
    # the only rows that appear in both files, and `renderError` marks them.
    broken = [r for r in index_rows if r.get("renderError")]
    for r in broken:
        missing.append(dict(r, reason=r["renderError"], detail="planned but undecodable"))

    write_csv(os.path.join(a.out, "animal_sheet_index.csv"), INDEX_COLS, index_rows)
    missing.sort(key=lambda r: r["csvRow"])
    write_csv(os.path.join(a.out, "animal_textures_missing.csv"), MISSING_COLS, missing)

    # ---- console summary --------------------------------------------------
    by_reason = defaultdict(int)
    for m in missing:
        by_reason[m["reason"]] += 1
    total = sum(os.path.getsize(os.path.join(a.out, f)) for f in page_files)
    print("\nplaced %d cells over %d pages (%d per page: %dx%d @ %dpx)"
          % (len(index_rows), len(page_files), per_page, a.cols, a.rows, a.cell))
    print("missing %d  " % len(missing)
          + "  ".join("%s=%d" % kv for kv in sorted(by_reason.items())))
    if broken:
        print("undecodable PNGs (drawn as a red X, listed in the missing CSV): %d"
              % len(broken))
    print("sheets on disk: %.1f MB   timings: scan=%.1fs texindex=%.1fs "
          "render=%.1fs total=%.1fs"
          % (total / 1048576.0, t_scan, t_index, t_render,
             time.perf_counter() - t0))
    print("wrote %d PNG + 2 CSV to %s" % (len(page_files), os.path.abspath(a.out)))
    return 0


def _draw_placeholders(img, chunk, a, fonts):
    """Grey stub cells for --include-missing. Same grid maths as render_page."""
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    cw, ch = a.cell, a.cell + a.caption
    for i, c in enumerate(chunk):
        if not c["_ph"]:
            continue
        r, col = divmod(i, a.cols)
        x0 = MARGIN + col * (cw + GAP)
        y0 = MARGIN + HEADER_H + r * (ch + GAP)
        draw.rectangle([x0, y0, x0 + cw - 1, y0 + ch - 1],
                       fill=BG_PLACEHOLDER, outline=GRID)
        draw.text((x0 + 6, y0 + a.cell // 2 - 8),
                  fit_text(draw, c.get("reason", "?"), fonts["mod"], cw - 12),
                  font=fonts["mod"], fill=FG_PLACEHOLDER)
        draw.text((x0 + 4, y0 + a.cell + 2),
                  fit_text(draw, c["defName"] or "(abstract)", fonts["name"], cw - 8),
                  font=fonts["name"], fill=FG_PLACEHOLDER)


if __name__ == "__main__":
    sys.exit(main())
