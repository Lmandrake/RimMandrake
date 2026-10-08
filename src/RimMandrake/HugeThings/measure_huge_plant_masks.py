"""measure_huge_plant_masks.py -- measure each huge plant's drawn picture and ground contact FROM ITS ART.

    python3 src/RimMandrake/HugeThings/measure_huge_plant_masks.py                 # rewrite the Rot patch
    python3 src/RimMandrake/HugeThings/measure_huge_plant_masks.py --check         # exit 1 if the patch is stale
    python3 src/RimMandrake/HugeThings/measure_huge_plant_masks.py --preview DIR   # also write overlay PNGs

Owner decisions HUGE_THINGS_FOOTPRINT_1 (decision taken by question card 2026-10-07 20:05 PDT):
  1. the selection rect wraps the WHOLE drawn picture at its current growth, where the engine draws it;
  2. pawns are blocked wherever the art touches the ground (stem / roots / body base), never under an
     overhanging cap.

So the per-species data is MEASURED here, never hand-tuned. A new giant is one run of this tool: every Rot
plant drawn >= GIANT_MIN_WIDTH cells wide (the same rule selftest_hugethings_footprint.py sweeps) is
measured and written into TheRot/Patches/RotGiants_HugeFootprint.xml.

THE DRAW TRANSFORM (decompiled 1.6, read via RimSage 2026-10-07; Source/FootprintMath.cs cites the same):
  Plant.Print, maxMeshCount == 1:
    size   = graphicData.drawSize.x * visualSizeRange.LerpThroughRange(growth)   -- a SQUARE quad
    centre = Position + (0.5, 0.5) + Gen.RandomHorizontalVector(0.05)            -- GenThing.TrueCenter
    if centre.z - visual/2 < Position.z: centre.z = Position.z + visual/2        -- bottom-anchored
    flipUv = Rand.Bool (mirror in x); Graphic_Random variant = Rand.Range(0, SubGraphicsCount)
  Graphic_Collection.Init: variants = files in the texPath folder, minus *_m masks and facing files, by name.
  With drawSize.x == 1 (every giant here) the quad's bottom edge is the root cell's south edge and its
  centre column is the root cell's centre column. That is the frame the cells below are measured in.

WHAT IS MEASURED, per texture variant, unflipped, at full growth (size S = drawSize.x * visualMax):
  * opaqueMin/opaqueMax -- the bounding box of the visible pixels (alpha >= ALPHA_CUTOFF, the CutoutPlant
    discard) in normalized quad coordinates, u left->right, v bottom->top. The selection rect is this box
    placed where the engine draws the quad.
  * contact -- the cells, relative to the root cell, that the art touches the ground in. "Touches the
    ground" = visible pixels in the BASE BAND: from the silhouette's lowest visible row up a depth of
    BAND_DEPTH x the base's width (a round footprint seen at RimWorld's 3/4 angle), and only between the
    base's own left and right edges (so a cap overhanging wider than the base is never counted). The base
    is the silhouette's lowest BASE_ROWS share of rows. A cell is contact when the band covers at least
    CELL_COVER of it after a DILATE_CELLS closing (so a tangle of roots reads as solid, a lone tendril not).
    A cell whose centre falls outside the visible-pixel box (less JITTER_MARGIN in x) is never contact either: the
    kernel refuses to block outside the drawn picture at any growth or setting, so the data must agree with it.
    The root cell itself is never contact: a plant cannot share its cell with an impassable edifice
    (GenSpawn.SpawningWipes -> BlocksPlanting would wipe the plant).
"""
import argparse
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
RM = os.path.normpath(os.path.join(HERE, ".."))
ROT = os.path.join(RM, "TheRot")
PATCH = os.path.join(ROT, "Patches", "RotGiants_HugeFootprint.xml")
SIZES_PATCH = os.path.join(ROT, "Patches", "RotSpecies_NamesAndSizes.xml")
WORKSHOP = "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100"
DONORS = [os.path.join(WORKSHOP, "1841354677")]          # Alpha Biomes: the AB_ giants' own defs
GIANT_MIN_WIDTH = 6.0

ALPHA_CUTOFF = 0.5     # CutoutPlant discards below this; what is not drawn is not picture
BASE_ROWS = 0.10       # share of the silhouette's height that defines its base
BAND_DEPTH = 0.5       # contact band depth, as a share of the base width
CELL_COVER = 0.25      # share of a cell the band must cover for the cell to block
DILATE_CELLS = 0.15    # closing radius, in cells, before measuring cover
JITTER_MARGIN = 0.06   # cells: Plant.Print's x jitter is +-0.05, the kernel keeps a cell only if its centre is in the picture
WORK_PX = 1024         # textures are measured at this side (alpha box-resampled)

TOOL_CMD = "python3 src/RimMandrake/HugeThings/measure_huge_plant_masks.py"


# ---- defs ---------------------------------------------------------------------------------------------------
def _def_sources():
    for p in glob.glob(os.path.join(ROT, "Defs", "**", "*.xml"), recursive=True):
        yield p
    for d in DONORS:
        for p in glob.glob(os.path.join(d, "1.6", "Defs", "**", "*.xml"), recursive=True):
            yield p


def load_defs():
    """{defName: element} and {Name: element} over TheRot's own defs and the donor's."""
    named, abstract = {}, {}
    for p in _def_sources():
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        for el in root:
            if not isinstance(el.tag, str) or el.tag != "ThingDef":
                continue
            if el.get("Name"):
                abstract[el.get("Name")] = el
            dn = el.findtext("defName")
            if dn:
                named[dn.strip()] = el
    return named, abstract


def _inherited(el, abstract, path):
    while el is not None:
        v = el.findtext(path)
        if v is not None and v.strip():
            return v.strip()
        el = abstract.get(el.get("ParentName"))
    return None


def _patched(defname, field):
    """The value a TheRot PatchOperationReplace sets on ThingDef[defName]/<field>, if any."""
    src = open(SIZES_PATCH, encoding="utf-8").read()
    tag = field.split("/")[-1]
    m = re.search(r'defName="%s"\]/%s</xpath>\s*<value><%s>([^<]+)</%s>' % (re.escape(defname), re.escape(field), tag, tag), src)
    return m.group(1).strip() if m else None


def resolve(defname, named, abstract):
    el = named[defname]
    tex = _patched(defname, "graphicData/texPath") or _inherited(el, abstract, "graphicData/texPath")
    cls = _inherited(el, abstract, "graphicData/graphicClass") or "Graphic_Random"   # Core PlantBaseNonEdible
    ds = _inherited(el, abstract, "graphicData/drawSize") or "(1,1)"
    vr = _patched(defname, "plant/visualSizeRange") or _inherited(el, abstract, "plant/visualSizeRange")
    mesh = _inherited(el, abstract, "plant/maxMeshCount") or "1"
    dsx = float(ds.strip("()").split(",")[0])
    vmin, vmax = (float(x) for x in vr.split("~"))
    return {"def": defname, "texPath": tex, "graphicClass": cls, "drawSizeX": dsx, "visual": (vmin, vmax),
            "maxMeshCount": int(mesh), "label": _patched(defname, "label") or el.findtext("label")}


def rot_plants():
    """Every Rot plant: TheRot's own defs plus the donor defs NamesAndSizes resizes."""
    named, abstract = load_defs()
    own = set()
    for p in glob.glob(os.path.join(ROT, "Defs", "**", "*.xml"), recursive=True):
        try:
            for el in ET.parse(p).getroot():
                if isinstance(el.tag, str) and el.findtext("defName") and el.find("plant") is not None:
                    own.add(el.findtext("defName").strip())
        except ET.ParseError:
            pass
    donor = set(re.findall(r'defName="(\w+)"\]/plant/visualSizeRange</xpath>', open(SIZES_PATCH, encoding="utf-8").read()))
    out = []
    for dn in sorted(own | donor):
        if dn in named and _inherited(named[dn], abstract, "plant/visualSizeRange"):
            out.append(resolve(dn, named, abstract))
    return out


# ---- textures -----------------------------------------------------------------------------------------------
def texture_roots():
    roots = sorted(glob.glob(os.path.join(RM, "*", "Textures")))
    roots += sorted(glob.glob(os.path.join(RM, "..", "RimStarWars", "*", "Textures")))
    for d in DONORS:
        roots += [os.path.join(d, "1.6", "Textures"), os.path.join(d, "Textures")]
    return [r for r in roots if os.path.isdir(r)]


def variant_files(texPath, graphicClass):
    """[(variantName, file)] as Graphic_Collection.Init would load them. Refuses an ambiguous path."""
    hits = []
    for r in texture_roots():
        base = os.path.join(r, texPath)
        if graphicClass == "Graphic_Single":
            if os.path.isfile(base + ".png"):
                hits.append([(os.path.basename(texPath), base + ".png")])
        elif os.path.isdir(base):
            fs = []
            for f in sorted(os.listdir(base)):
                stem, ext = os.path.splitext(f)
                if ext.lower() != ".png" or stem.endswith("_m"):
                    continue
                if any(s in stem for s in ("_east", "_north", "_west", "_south")):
                    continue
                fs.append((stem, os.path.join(base, f)))
            if fs:
                hits.append(fs)
    if not hits:
        raise SystemExit("no texture for %s (%s) under %d roots" % (texPath, graphicClass, len(texture_roots())))
    if len(hits) > 1:
        raise SystemExit("ambiguous texture %s: %d roots carry it -- decide which loads last" % (texPath, len(hits)))
    return hits[0]


def alpha_of(path):
    im = Image.open(path).convert("RGBA")
    a = im.getchannel("A")
    if a.size != (WORK_PX, WORK_PX):
        a = a.resize((WORK_PX, WORK_PX), Image.BOX)    # PrintPlane stretches any aspect onto the square quad
    return np.asarray(a, dtype=np.float32) / 255.0     # [row from TOP, col]


# ---- the measurement ----------------------------------------------------------------------------------------
def measure_variant(alpha, size):
    """-> (opaqueMin(u,v), opaqueMax(u,v), contact [(dx,dz)], band bool array). v from the bottom."""
    n = alpha.shape[0]
    vis = alpha >= ALPHA_CUTOFF
    rows = np.where(vis.any(axis=1))[0]
    cols = np.where(vis.any(axis=0))[0]
    if rows.size == 0:
        raise SystemExit("texture has no visible pixels")
    top, bot = int(rows[0]), int(rows[-1])            # image rows (top = 0)
    omin = (cols[0] / n, (n - 1 - bot) / n)
    omax = ((cols[-1] + 1) / n, (n - top) / n)

    sil_h = bot - top + 1
    base_rows = max(1, int(round(BASE_ROWS * sil_h)))
    base = vis[bot - base_rows + 1:bot + 1]
    bcols = np.where(base.any(axis=0))[0]
    bl, br = int(bcols[0]), int(bcols[-1])
    depth = max(1, int(round(BAND_DEPTH * (br - bl + 1))))
    band = np.zeros_like(vis)
    band[max(0, bot - depth + 1):bot + 1, bl:br + 1] = vis[max(0, bot - depth + 1):bot + 1, bl:br + 1]

    px_per_cell = n / size
    k = int(round(DILATE_CELLS * px_per_cell)) * 2 + 1
    if k >= 3:
        img = Image.fromarray((band * 255).astype(np.uint8))
        img = img.filter(ImageFilter.MaxFilter(k)).filter(ImageFilter.MinFilter(k))
        closed = (np.asarray(img) > 127) & (np.arange(n)[:, None] <= bot)   # never grow below the base
    else:
        closed = band

    contact = []
    # cell (dx, dz) relative to the root cell covers quad-x [dx, dx+1) - (0.5 - size/2) ... in pixels:
    # quad x of a cell's west edge = (dx + 0.5 - (0.5 - size/2)) ... simpler: quad-left world x = 0.5 - size/2
    left = 0.5 - size / 2.0
    for dz in range(0, int(np.ceil(size))):
        for dx in range(int(np.floor(left)) - 1, int(np.ceil(left + size)) + 1):
            x0, x1 = (dx - left) * px_per_cell, (dx + 1 - left) * px_per_cell
            z0, z1 = dz * px_per_cell, (dz + 1) * px_per_cell          # from the quad bottom
            c0, c1 = max(0, int(np.floor(x0))), min(n, int(np.ceil(x1)))
            r0, r1 = max(0, n - int(np.ceil(z1))), min(n, n - int(np.floor(z0)))
            if c1 <= c0 or r1 <= r0:
                continue
            cu, cv = (dx + 0.5 - left) / size, (dz + 0.5) / size
            if not (omin[0] + JITTER_MARGIN / size <= cu <= omax[0] - JITTER_MARGIN / size and omin[1] <= cv <= omax[1]):
                continue   # the kernel never blocks a cell whose centre is outside the drawn picture
            cover = closed[r0:r1, c0:c1].mean()
            if cover >= CELL_COVER and (dx, dz) != (0, 0):
                contact.append((dx, dz))
    return omin, omax, contact, closed


def measure(plant):
    if plant["maxMeshCount"] != 1:
        raise SystemExit("%s: maxMeshCount %d -- Plant.Print's multi-mesh branch is not measured" % (plant["def"], plant["maxMeshCount"]))
    if plant["drawSizeX"] != 1.0:
        # Plant.Print anchors with visual/2 but draws drawSize.x * visual: the quad's bottom then sits off the root's south
        # edge by a growth-dependent amount, and the measurement frame below assumes it sits on it (GPT review #7).
        raise SystemExit("%s: drawSize.x %s != 1 -- the measurement frame is not defined for it" % (plant["def"], plant["drawSizeX"]))
    size = plant["drawSizeX"] * plant["visual"][1]
    out = []
    for name, f in variant_files(plant["texPath"], plant["graphicClass"]):
        omin, omax, contact, band = measure_variant(alpha_of(f), size)
        out.append({"texture": name, "file": f, "opaqueMin": omin, "opaqueMax": omax, "contact": contact, "band": band})
    return size, out


# ---- writing ------------------------------------------------------------------------------------------------
def _fmt(v):
    return ("%.4f" % v).rstrip("0").rstrip(".") if v % 1 else "%d" % v


def render_patch(results):
    L = ['<?xml version="1.0" encoding="utf-8"?>', "<Patch>",
         "  <!-- GENERATED by `%s`. Do not hand-edit; rerun it. -->" % TOOL_CMD,
         "  <!-- HUGE_THINGS_FOOTPRINT_1 (decision taken by question card 2026-10-07 20:05 PDT): the selection rect wraps",
         "       the whole drawn picture; pawns are blocked only where the art touches the ground. Every Rot plant drawn",
         "       %s+ cells wide is measured from its own art by the tool above (method in its docstring)." % _fmt(GIANT_MIN_WIDTH),
         "",
         "       measuredSize = drawSize.x * visualMax: the full-growth quad the cells were measured in. Per variant",
         "       (Graphic_Random sub-texture, matched by name at runtime): opaqueMin/opaqueMax = visible-pixel box in",
         "       quad coordinates (u left->right, v bottom->top); contact = full-growth ground-contact cells (dx,dz)",
         "       relative to the root cell, unflipped. Runtime mirrors them with the engine's own flipUv and scales",
         "       them with growth (Source/FootprintMath.cs).",
         "",
         "       Gated per def by PatchOperationConditional on its own xpath (absent donor = no-op); the extension <li>",
         "       carries MayRequire=\"mandrake.rm.hugethings\", which the def loader honours on a list element.",
         "       (MayRequire on an Operation would be inert; it is not used there.) -->", ""]
    for plant, size, variants in results:
        L.append("  <!-- %s, %s (%s wide): %s -->" % (plant["def"], plant["label"], _fmt(size),
                 ", ".join("%s %d contact cells" % (v["texture"], len(v["contact"])) for v in variants)))
        L += ['  <Operation Class="PatchOperationConditional">',
              '    <xpath>/Defs/ThingDef[defName="%s"]</xpath>' % plant["def"],
              '    <match Class="PatchOperationAddModExtension">',
              '      <xpath>/Defs/ThingDef[defName="%s"]</xpath>' % plant["def"],
              "      <value>",
              '        <li Class="RimMandrake.HugeThings.RM_HugePlantExtension" MayRequire="mandrake.rm.hugethings">',
              "          <measuredSize>%s</measuredSize>" % _fmt(size),
              "          <variants>"]
        for v in variants:
            L += ["            <li>",
                  "              <texture>%s</texture>" % v["texture"],
                  "              <opaqueMin>(%s,%s)</opaqueMin>" % tuple(_fmt(round(x, 4)) for x in v["opaqueMin"]),
                  "              <opaqueMax>(%s,%s)</opaqueMax>" % tuple(_fmt(round(x, 4)) for x in v["opaqueMax"]),
                  "              <contact>"]
            rows = {}
            for dx, dz in v["contact"]:
                rows.setdefault(dz, []).append(dx)
            for dz in sorted(rows):
                L.append("                " + "".join("<li>(%d,%d)</li>" % (dx, dz) for dx in sorted(rows[dz])))
            L += ["              </contact>", "            </li>"]
        L += ["          </variants>", "        </li>", "      </value>", "    </match>", "  </Operation>", ""]
    L.append("</Patch>")
    body = "\n".join(L)
    assert "--" not in body.replace("<!--", "").replace("-->", ""), "an XML comment may not contain a double hyphen"
    return "\n".join(L) + "\n"


def preview(results, outdir):
    os.makedirs(outdir, exist_ok=True)
    tiles = []
    for plant, size, variants in results:
        for v in variants:
            T = 512
            im = Image.open(v["file"]).convert("RGBA").resize((T, T))
            bg = Image.new("RGBA", (T, T), (70, 70, 70, 255))
            bg.alpha_composite(im)
            ov = Image.new("RGBA", (T, T), (0, 0, 0, 0))
            d = ImageDraw.Draw(ov)
            c = T / size
            left = 0.5 - size / 2.0
            for dx, dz in v["contact"]:
                x0 = (dx - left) * c
                y1 = T - dz * c
                d.rectangle([x0, y1 - c, x0 + c, y1], fill=(255, 0, 0, 80), outline=(255, 0, 0, 200))
            x0 = (0 - left) * c
            d.rectangle([x0, T - c, x0 + c, T], outline=(255, 255, 0, 255), width=2)
            u0, v0 = v["opaqueMin"]
            u1, v1 = v["opaqueMax"]
            d.rectangle([u0 * T, T - v1 * T, u1 * T, T - v0 * T], outline=(0, 255, 255, 255), width=2)
            bg.alpha_composite(ov)
            d = ImageDraw.Draw(bg)
            d.text((4, 4), "%s %s  %d cells" % (plant["def"], v["texture"], len(v["contact"])), fill=(255, 255, 0, 255))
            bg.convert("RGB").save(os.path.join(outdir, "mask_%s_%s.png" % (plant["def"], v["texture"])))
            tiles.append(bg.convert("RGB"))
    if tiles:
        cols = 4
        sheet = Image.new("RGB", (512 * cols, 512 * ((len(tiles) + cols - 1) // cols)), (0, 0, 0))
        for i, t in enumerate(tiles):
            sheet.paste(t, ((i % cols) * 512, (i // cols) * 512))
        sheet.save(os.path.join(outdir, "mask_sheet.png"))


def giants():
    return [p for p in rot_plants() if p["drawSizeX"] * p["visual"][1] >= GIANT_MIN_WIDTH]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="exit 1 if the patch differs from a fresh measurement")
    ap.add_argument("--preview", metavar="DIR", help="write overlay PNGs (red contact, cyan picture box, yellow root)")
    a = ap.parse_args(argv)
    gs = giants()
    probe = {"AB_AgariluxPrime", "RM_Nogtyl", "AB_DribblingCap"} - {p["def"] for p in gs}
    if probe:
        raise SystemExit("sanity probe: cannot see known giants %r among %d plants" % (sorted(probe), len(gs)))
    results = []
    for p in sorted(gs, key=lambda p: -p["drawSizeX"] * p["visual"][1]):
        size, variants = measure(p)
        results.append((p, size, variants))
        print("%-26s %5s wide  %s" % (p["def"], _fmt(size),
              "  ".join("%s:%d" % (v["texture"], len(v["contact"])) for v in variants)))
    text = render_patch(results)
    if a.preview:
        preview(results, a.preview)
    if a.check:
        cur = open(PATCH, encoding="utf-8").read()
        if cur != text:
            print("STALE: %s differs from a fresh measurement; rerun `%s`" % (PATCH, TOOL_CMD))
            return 1
        print("CURRENT: %s" % PATCH)
        return 0
    with open(PATCH, "w", encoding="utf-8") as fh:
        fh.write(text)
    print("wrote %s (%d giants)" % (PATCH, len(results)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
