#!/usr/bin/env python3
"""
thing_contact_sheet.py — contact sheets for everything that is NOT a pawn.

VERSION 1.0  (2026-08-15)   Project: D:/Luke/dev/Rimworld/src/RimMandrake/Utils/
Python 3.8+ stdlib **plus Pillow**. Nothing else. Keep it that way.

CHANGELOG
  1.0  first cut. Generalises animal_contact_sheet.py v1.0 off animals and onto
       weapons / apparel / buildings / items / plants. Everything below the
       planning layer is IMPORTED from animal_contact_sheet, not reimplemented:
       the texture index, the texPath resolver, the sprite loader, the fitter,
       the earth/checker backgrounds, the shadow, the fonts and the CSV writer
       are the same code, verified by the animal run. Only "which defs, and
       where is their picture" is new.

WHY THIS EXISTS
===============
Contact sheets of the ACTUAL SPRITES turned an impossible list-based decision
into a fast visual one: six sheets of 1,243 animals let a 584-mod stack be
cherrypicked in minutes instead of weeks. Animals were only the first asset
type. This is the same instrument pointed at weapons, apparel, buildings, items
and plants, which together are the rest of the graphical surface of the stack.

WHERE THE PICTURE LIVES — and why this file is SIMPLER than the animal one
==========================================================================
An animal's sprite is NOT on its ThingDef (`graphicData` is null for every
animal), which is why animal_contact_sheet.py has to hop
ThingDef -> PawnKindDef -> lifeStages[LAST].bodyGraphicData.texPath.

**Weapons, apparel, buildings, items and plants carry `graphicData.texPath`
DIRECTLY on the ThingDef.** So generalising REMOVES a hop. `plan_cells()` is the
only function that had to change.

    ThingDef (inheritance resolved)
      -> graphicData/texPath          extension-less, side-less
      -> a .png somewhere under some mod's Textures/

TWO EXTRA GRAPHIC SHAPES THE ANIMAL TOOL NEVER MET
==================================================
`graphicData.graphicClass` decides what texPath MEANS, and two classes make it
a folder rather than a file stem:

  * Graphic_Single      texPath is the file stem.  Bear.png
  * Graphic_Multi       texPath is the stem of a SIDE FAMILY. Bear_south.png,
                        Bear_east.png, Bear_north.png. Common on buildings.
                        Handled by the same suffix ladder animals use; we show
                        _south, i.e. the front elevation.
  * Graphic_Random      🔴 texPath is a FOLDER. The game loads every PNG under
                        it and picks one per thing. There is no file at the
                        texPath itself, so the suffix ladder finds NOTHING and
                        the cell renders blank unless you look inside.
  * Graphic_StackCount  same shape as Random — a folder of _a/_b/_c variants.
  * Graphic_Appearances / _Indexed / _Mote  also folder-shaped in practice.

So resolution is a two-stage ladder: the suffix ladder first (which is exact),
then a DIRECTORY lookup that takes the first PNG under texPath/ in sorted
order. The index CSV records which stage fired (`texSuffix` = a suffix, the
literal `<bare>`, or `<dir:name.png>`) so a reviewer can tell "this is the
asset" from "this is one of N variants I picked for you".

WHAT THIS CANNOT SHOW — read before reading the numbers
=======================================================
**A large blank fraction is CORRECT, not a bug.** Vanilla and DLC art ships
inside Unity AssetBundles, not as loose PNGs, and extracting them is out of
scope (version-fragile, and the payoff is a picture of something you already
know by sight). Every Core building, Core weapon and Core apparel item is
therefore un-previewable offline. The sheets cover the MODDED long tail, which
is exactly the population a cherrypicking pass is about, and
`<cat>_textures_missing.csv` is the list of things reviewable only in game.

Inherited blind spots, all from layer 1 and all real:
  * PatchOperations have NOT run. A mod that retextures something by patching
    its texPath is invisible; we render the donor's art.
  * MayRequire is not evaluated.
  * We draw ONE still frame from ONE side, with no stuff colour, no quality, no
    shader and no mask. The sheet tells you what the art ASSET is, not what the
    thing looks like built out of plasteel.

DO NOT DEDUPLICATE
==================
Two mods shipping the same defName is a FINDING, not noise — it is how zebra,
black bear and mandrill were caught shipping twice in the animal pass. Every
row is kept and `duplicateDefName` names every mod that declared the key.

CATEGORIES
==========
  weapons    equipmentType == Primary, OR a non-empty weaponTags
  apparel    has an <apparel> block
  buildings  has a <building> block          (~8.7k — paginates, see --cols/--rows)
  items      category Item (or has thingCategories) with graphicData, and none
             of the above
  plants     has a <plant> block
  all        every set above, one run, one def scan, one texture index

OUTPUTS (per category, under --out/sheets_<category>/)
======================================================
  <cat>_sheet_NN.png            the decision surface
  <cat>_sheet_index.csv         one row per PLACED cell: page/row/col ->
                                defName, label, mod, packageId, texPath, file on
                                disk. **The actionable half — a picture you
                                cannot act on is decoration.**
  <cat>_textures_missing.csv    one row per thing with no previewable sprite,
                                with a machine-readable reason. A deliverable in
                                its own right.

USAGE
=====
  🔴 Pillow is NOT installed for WSL python3 (PEP 668). Use Windows python.exe;
     relative paths work from the repo root.

  python.exe src/RimMandrake/Utils/thing_contact_sheet.py --category weapons
  python.exe src/RimMandrake/Utils/thing_contact_sheet.py --category all
  python.exe src/RimMandrake/Utils/thing_contact_sheet.py --category buildings --cols 18 --rows 12
  python.exe src/RimMandrake/Utils/thing_contact_sheet.py --category items --limit 200 --out ./smoke
"""

import argparse
import os
import sys
import time
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from def_inventory import build, txt, D_CONFIG, D_WORKSHOP, D_LOCAL, D_DATA  # noqa: E402

# Everything below the planning layer is the animal tool's, unchanged. Importing
# rather than copying is deliberate: these functions are the ones that carry the
# measured traps (LoadFolders content dirs, the suffix ladder, never-raise sprite
# decoding), and two copies would drift.
from animal_contact_sheet import (  # noqa: E402
    build_texture_index, resolve_texture, load_bundle_index,
    DEFAULT_BUNDLE_DIR, load_sprite, fit_sprite,
    checker_tile, earth_tile, ground_shadow,
    load_font, text_w, fit_text, mod_color, write_csv,
    BG_PAGE, BG_HEADER, BG_CAPTION, FG_TITLE, FG_SUB, FG_NAME, FG_MOD, GRID,
    CHECK_A, CHECK_B, BG_PLACEHOLDER, FG_PLACEHOLDER,
    ACCENT_H, TAG_H, MARGIN, GAP, HEADER_H,
)

VERSION = "1.0"

WANT_TYPES = ("ThingDef",)

REPO_ROOT = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
DEFAULT_OUT = os.path.join(REPO_ROOT, "observed", "inventory")

CATEGORIES = ("weapons", "apparel", "buildings", "items", "plants")

# graphicClasses whose texPath names a FOLDER of variants rather than a file
# stem. Membership here only changes the ORDER we try things in — the directory
# fallback runs for anything the suffix ladder misses — but naming them makes
# the common case one lookup instead of six.
DIR_GRAPHIC_CLASSES = ("Graphic_Random", "Graphic_StackCount",
                       "Graphic_Appearances", "Graphic_Indexed")


# ------------------------------------------------------------------ selection
def _has(el, path):
    return el.find(path) is not None


def _nonempty_list(el, path):
    node = el.find(path)
    return node is not None and len(node) > 0


def is_weapon(el):
    """equipmentType Primary, or any weaponTags. Either alone is enough."""
    if txt(el, "equipmentType") == "Primary":
        return True
    return _nonempty_list(el, "weaponTags")


def is_apparel(el):
    return _has(el, "apparel")


def is_building(el):
    return _has(el, "building")


def is_plant(el):
    return _has(el, "plant")


def is_item(el):
    """
    A resource/item with art, and none of the above.

    `<category>Item</category>` is the authoritative discriminator; a def with
    <thingCategories> is included too, because a fair number of modded items
    inherit their category from a base this tool cannot see the C# default of.
    """
    if is_weapon(el) or is_apparel(el) or is_building(el) or is_plant(el):
        return False
    if not _has(el, "graphicData"):
        return False
    return txt(el, "category") == "Item" or _nonempty_list(el, "thingCategories")


SELECTORS = {
    "weapons": is_weapon,
    "apparel": is_apparel,
    "buildings": is_building,
    "items": is_item,
    "plants": is_plant,
}


# ------------------------------------------------------------------ rows
def collect_rows(ds, category):
    """
    Every matching ThingDef, in a row order GROUPED BY MOD.

    Row order is the design, not taste: sorted by (modName, defName) so one
    mod's whole contribution is one glance — "this is what Vanilla Weapons
    Expanded adds, this is what Star Wars adds" — instead of sixty lookups.

    Abstract defs and defs with no defName are dropped: they are inheritance
    scaffolding, never a thing on the map.

    Read off `rec.element`, i.e. AFTER <ParentName> merging, and that is
    load-bearing here: the overwhelming majority of modded weapons declare
    nothing but a label, a texPath and some stats, inheriting <equipmentType>,
    <thingClass> and half of graphicData from a base. Read unmerged, the weapon
    selector matches almost nothing.
    """
    want = SELECTORS[category]
    rows = []
    for rec in ds.of_type("ThingDef"):
        if not rec.defName or rec.isAbstract:
            continue
        el = rec.element
        try:
            if not want(el):
                continue
            rows.append({
                "defName": rec.defName,
                "label": txt(el, "label"),
                "modName": rec.modName,
                "packageId": rec.packageId,
                "loadOrder": rec.loadOrder,
                "sourceFile": rec.sourceFile.replace("\\", "/"),
                "thingCategory": txt(el, "category"),
                "graphicClass": txt(el, "graphicData/graphicClass"),
                "texPath": txt(el, "graphicData/texPath"),
                "duplicateOwners": rec.duplicateOwners,
            })
        finally:
            rec.release()          # do not hold 35k merged ThingDef trees

    # Duplicates are RECORDED, never removed. A doubled cell means two mods ship
    # the same thing, and cutting one copy would leave the other on the map.
    owners = defaultdict(set)
    for r in rows:
        owners[r["defName"]].add(r["modName"])
    for r in rows:
        o = owners[r["defName"]] | set(r.pop("duplicateOwners") or [])
        r["duplicateDefName"] = " | ".join(sorted(o)) if len(o) > 1 else ""

    rows.sort(key=lambda r: (r["modName"].lower(), r["defName"].lower()))
    for i, r in enumerate(rows, 1):
        r["srcRow"] = i
    return rows


# ------------------------------------------------------------------ textures
def build_dir_index(tex_index):
    """
    {lowercased directory -> sorted [file keys]} derived from the flat texture
    index, so a Graphic_Random texPath (which names a FOLDER) can be resolved to
    a representative PNG.

    Derived rather than collected during the walk on purpose: build_texture_index
    is the animal tool's, verified, and imported unchanged. This is one cheap
    pass over its output.
    """
    dirs = defaultdict(list)
    for key in tex_index:
        d, _, fn = key.rpartition("/")
        dirs[d].append(fn)
    for v in dirs.values():
        v.sort()
    return dirs


def resolve_thing_texture(tex_path, graphic_class, tex_index, dir_index,
                          bundle_index=None):
    """
    (absolute file, how it was found) for a ThingDef's texPath, or (None, None).

    Two stages, tried in the order that is most likely to be exact for the
    declared graphicClass:

      suffix ladder  _south / bare / _east / _north / _side  — the animal tool's
                     resolve_texture, imported. Exact: this IS the asset.
      directory      first PNG under texPath/ in sorted order — for
                     Graphic_Random and friends, where texPath is a folder and
                     the suffix ladder can never hit. Reported as
                     `<dir:filename.png>` so the reviewer knows they are looking
                     at ONE of several variants.
    """
    if not tex_path:
        return None, None
    base = tex_path.replace("\\", "/").strip("/").lower()

    def by_dir():
        files = dir_index.get(base)
        if files:
            return tex_index[base + "/" + files[0]], "<dir:%s>" % files[0]
        return None, None

    if graphic_class in DIR_GRAPHIC_CLASSES:
        hit, how = by_dir()
        if hit:
            return hit, how
    hit, how = resolve_texture(tex_path, tex_index)
    if hit:
        return hit, how
    hit, how = by_dir()
    if hit:
        return hit, how
    # Last: the AssetBundle cache, matched on the LAST segment of texPath
    # against the object's m_Name. Reported as `<bundle...>`. Tried after the
    # directory fallback because a loose variant of the right thing beats an
    # exact-named texture from a mod that merely shares the name.
    return resolve_texture(tex_path, {}, bundle_index)


# ------------------------------------------------------------------ planning
def plan_cells(rows, tex_index, dir_index, bundle_index=None):
    """
    Split the rows into (placed, missing). This is the ONLY function that had to
    change to generalise off animals — everything else on the path is imported.

    Nothing is decoded here; it is pure bookkeeping, so the page count is known
    before the first pixel is drawn.

    `reason` on a missing row is the deliverable. Three causes, three different
    meanings:
      no_graphicData  the def declares no <graphicData> at all — usually an
                      abstract-ish or purely mechanical thing
      no_texPath      graphicData exists but names no texture
      no_loose_png    a texPath exists and no loose PNG matches it. **This is
                      the AssetBundle case** — the thing exists and is fine, it
                      just cannot be previewed offline. Expect a lot of these.
    """
    placed, missing = [], []
    for row in rows:
        tex = row.get("texPath") or ""
        if not tex:
            reason = "no_texPath" if row.get("graphicClass") else "no_graphicData"
            missing.append(dict(row, reason=reason))
            continue
        path, how = resolve_thing_texture(tex, row.get("graphicClass"),
                                          tex_index, dir_index, bundle_index)
        if not path:
            # Reason literal deliberately unchanged — the owner's review page and
            # its recorded decisions filter on it. It now means "no loose PNG
            # *and* no bundled texture of that name".
            missing.append(dict(row, reason="no_loose_png"))
            continue
        placed.append(dict(row, textureFile=path, texSuffix=how,
                           texSource="bundle" if how.startswith("<bundle")
                                     else "loose"))
    return placed, missing


# ------------------------------------------------------------------ rendering
def render_page(cells, page_no, page_count, category, args, fonts, tile, stamp):
    """
    One sheet. Same grid maths as animal_contact_sheet.render_page — there is
    exactly one place a cell's (x, y) is computed from its index, and getting it
    wrong is the obvious way to produce overlapping cells.

    Caption differs from the animal sheet: LABEL first (the human name — "plasma
    repeater", not "OR_PlasmaRepeater"), defName second and dim. The mod is on
    the accent strip and on the tag that is drawn wherever the mod CHANGES, so
    the mod boundary is visible without spending a caption line on it. `prev_mod`
    starts as None on every page, so the first cell of every page is always
    tagged even when a mod's run spans a page break.
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

    draw.text((MARGIN, 14), "RimWorld %s contact sheet \u2014 page %d of %d"
              % (category, page_no, page_count), font=fonts["title"], fill=FG_TITLE)
    draw.text((MARGIN, 38), fit_text(
        draw, "%d sprites  \u00b7  %d mods: %s  \u00b7  %s"
        % (len(cells), len(mods_here), span, stamp),
        fonts["sub"], page_w - 2 * MARGIN), font=fonts["sub"], fill=FG_SUB)

    placed_rows = []
    prev_mod = None
    for i, c in enumerate(cells):
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
            # Planned but undecodable. Kept VISIBLE as a red X on purpose: a
            # corrupt asset is a finding, and it is carried out to the missing
            # CSV by the caller via c["renderError"].
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
            if not args.no_shadow:
                shadow, pad = ground_shadow(fitted)
                img.paste(shadow, (px - pad,
                                   py + fitted.height - shadow.height + pad // 2),
                          shadow)
            img.paste(fitted, (px, py), fitted)
            sprite.close()

        if c["modName"] != prev_mod:
            tag = fit_text(draw, c["modName"], fonts["tag"], cw - 8)
            tw = text_w(draw, tag, fonts["tag"])
            draw.rectangle([x0, wy, x0 + tw + 8, wy + TAG_H - 1], fill=accent)
            draw.text((x0 + 4, wy + 1), tag, font=fonts["tag"], fill=(16, 16, 18))
            prev_mod = c["modName"]

        cy = y0 + args.cell
        draw.text((x0 + 4, cy + 2),
                  fit_text(draw, c["label"] or c["defName"], fonts["name"], cw - 8),
                  font=fonts["name"], fill=FG_NAME)
        draw.text((x0 + 4, cy + 16),
                  fit_text(draw, c["defName"], fonts["mod"], cw - 8),
                  font=fonts["mod"], fill=FG_MOD)

        c["page"], c["row"], c["col"] = page_no, r, col
        placed_rows.append(c)

    return img, placed_rows


# ------------------------------------------------------------------ output
INDEX_COLS = ["page", "row", "col", "srcRow", "defName", "label", "modName",
              "packageId", "loadOrder", "duplicateDefName", "thingCategory",
              "graphicClass", "texPath", "texSuffix", "textureFile",
              "imageW", "imageH", "sourceFile", "renderError",
              # APPENDED, never inserted: the owner is mid-review against a
              # fixed column order. loose | bundle — which store this cell's
              # sprite came out of.
              "texSource"]

MISSING_COLS = ["srcRow", "defName", "label", "modName", "packageId", "loadOrder",
                "duplicateDefName", "reason", "thingCategory", "graphicClass",
                "texPath", "sourceFile"]


def run_category(ds, category, tex_index, dir_index, a, bundle_index=None):
    """One category end to end: rows -> plan -> sheets + two CSVs. Returns stats."""
    out_dir = os.path.join(a.out, "sheets_%s" % category)
    os.makedirs(out_dir, exist_ok=True)

    rows = collect_rows(ds, category)
    if a.limit:
        rows = rows[:a.limit]
    placed, missing = plan_cells(rows, tex_index, dir_index, bundle_index)

    per_page = a.cols * a.rows
    pages = (len(placed) + per_page - 1) // per_page if placed else 0

    index_rows, page_files = [], []
    t = time.perf_counter()
    if not a.no_image and placed:
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
            chunk = placed[p * per_page:(p + 1) * per_page]
            img, done = render_page(chunk, p + 1, pages, category, a, fonts,
                                    tile, stamp)
            name = "%s_sheet_%02d.png" % (category, p + 1)
            img.save(os.path.join(out_dir, name))
            page_files.append(name)
            index_rows.extend(done)
            img.close()
    t_render = time.perf_counter() - t

    # A planned cell whose PNG would not decode stays in the INDEX (it occupies a
    # grid position, and you must be able to look up the red X) AND is reported
    # as missing, because it has no previewable sprite. `renderError` marks the
    # only rows that appear in both files.
    broken = [r for r in index_rows if r.get("renderError")]
    for r in broken:
        missing.append(dict(r, reason=r["renderError"]))

    write_csv(os.path.join(out_dir, "%s_sheet_index.csv" % category),
              INDEX_COLS, index_rows)
    missing.sort(key=lambda r: r["srcRow"])
    write_csv(os.path.join(out_dir, "%s_textures_missing.csv" % category),
              MISSING_COLS, missing)

    by_reason = defaultdict(int)
    for m in missing:
        by_reason[m["reason"]] += 1
    size = sum(os.path.getsize(os.path.join(out_dir, f)) for f in page_files)
    blank = (len(missing) / float(len(rows))) if rows else 0.0

    print("\n== %s ==" % category)
    print("  defs: %d   placed: %d over %d pages   missing: %d (%.1f%% blank)"
          % (len(rows), len(index_rows), len(page_files), len(missing),
             blank * 100.0))
    print("  missing by reason: "
          + "  ".join("%s=%d" % kv for kv in sorted(by_reason.items())))
    if broken:
        print("  undecodable PNGs (red X, also in the missing CSV): %d" % len(broken))
    print("  %.1f MB of PNG   render=%.1fs   -> %s"
          % (size / 1048576.0, t_render, os.path.abspath(out_dir)))
    return {"category": category, "defs": len(rows), "placed": len(index_rows),
            "pages": len(page_files), "missing": len(missing), "blank": blank,
            "bytes": size, "dir": out_dir}


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Paginated contact sheets of weapons / apparel / buildings "
                    "/ items / plants, grouped by mod, straight from the defs.")
    ap.add_argument("--category", default="weapons",
                    choices=CATEGORIES + ("all",))
    ap.add_argument("--out", default=DEFAULT_OUT,
                    help="parent dir; each category writes sheets_<category>/ under it")
    ap.add_argument("--config", default=D_CONFIG)
    ap.add_argument("--workshop", default=D_WORKSHOP)
    ap.add_argument("--local", default=D_LOCAL)
    ap.add_argument("--data", default=D_DATA)
    ap.add_argument("--cell", type=int, default=160, help="cell size in px")
    ap.add_argument("--caption", type=int, default=32)
    ap.add_argument("--cols", type=int, default=14)
    ap.add_argument("--rows", type=int, default=9)
    ap.add_argument("--bg", choices=("earth", "checker"), default="earth")
    ap.add_argument("--check", type=int, default=10)
    ap.add_argument("--flat-bg", default="", metavar="RRGGBB")
    ap.add_argument("--no-shadow", action="store_true")
    ap.add_argument("--no-trim", action="store_true",
                    help="do NOT crop to the alpha bbox (keeps relative scale)")
    ap.add_argument("--max-upscale", type=float, default=2.0)
    ap.add_argument("--limit", type=int, default=0, help="stop after N defs (smoke test)")
    ap.add_argument("--no-image", action="store_true", help="CSVs only")
    ap.add_argument("--bundles", default=DEFAULT_BUNDLE_DIR,
                    help="extract_bundle_textures.py cache dir")
    ap.add_argument("--no-bundles", action="store_true",
                    help="loose PNGs only — the pre-bundle baseline")
    a = ap.parse_args(argv)

    t0 = time.perf_counter()
    os.makedirs(a.out, exist_ok=True)

    ds = build(a.config, a.workshop, a.local, a.data, types=WANT_TYPES, quiet=True)
    print("load set: version %s, %d active mods -> %d content folders, %d ThingDefs"
          % (ds.gameVersion, len(ds.mods),
             sum(len(m["contentDirs"]) for m in ds.mods),
             len(ds.of_type("ThingDef"))))

    tex_index, n_png, n_texdirs = build_texture_index(ds.mods)
    dir_index = build_dir_index(tex_index)
    print("textures: %d loose PNGs in %d Textures/ roots -> %d distinct paths, "
          "%d dirs" % (n_png, n_texdirs, len(tex_index), len(dir_index)))

    bundle_index, n_bundle = ({}, 0) if a.no_bundles else load_bundle_index(a.bundles)
    print("bundles: %d extracted textures -> %d distinct names%s"
          % (n_bundle, len(bundle_index),
             "" if n_bundle else "  (run extract_bundle_textures.py under python.exe)"))

    cats = CATEGORIES if a.category == "all" else (a.category,)
    stats = [run_category(ds, c, tex_index, dir_index, a, bundle_index)
             for c in cats]

    print("\n%-11s %7s %7s %6s %8s %8s %8s"
          % ("category", "defs", "placed", "pages", "missing", "blank%", "MB"))
    for s in stats:
        print("%-11s %7d %7d %6d %8d %7.1f%% %8.1f"
              % (s["category"], s["defs"], s["placed"], s["pages"], s["missing"],
                 s["blank"] * 100.0, s["bytes"] / 1048576.0))
    print("total %.1f MB   %.1fs" % (sum(s["bytes"] for s in stats) / 1048576.0,
                                     time.perf_counter() - t0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
