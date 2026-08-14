#!/usr/bin/env python3
"""Prove the tint claim offline: how much "old, rusty, terrible" costs zero pixels.

Same method as src/Jawa/DesertVehicleReskin/Source/preview_tint.py — do the
multiply Unity would do, and put a true-in-game-size strip on the sheet, because
768 px of hull is not the decision and 64 px of wall is.

TWO MECHANISMS, one sheet each. They are different and the difference is the
whole proposal:

  sheet 1 (masked / CutoutComplex)   art x color where the mask is RED,
                                     art x colorTwo where the mask is GREEN,
                                     art untouched where the mask is BLACK.
                                     Selective. Two paintable regions.

  sheet 2 (unmasked / plain Cutout)  art x color over the WHOLE sprite.
                                     RimWorld honours graphicData/color on the
                                     default Cutout shader — Ludeon ships
                                     AncientFortifiedWall (127,135,127) and
                                     OrbitalAncientFortifiedWall (132,140,140)
                                     as two defs over ONE atlas, differing only
                                     by that node. No mask required.

⚠️ <color> MULTIPLIES. It can only ever darken. A light, desaturated source
takes a tint beautifully; an already-dark source just goes muddy. So the script
measures each source's mean luminance and SOLVES for the colour that lands the
requested rendered target, rather than pasting a palette in and hoping. If the
solved colour clips past 255 the source is too dark to tint to that target and
the script says so — that is the honest boundary of the free route.

Run: /home/mandrake/.venvs/art/bin/python design/Jawa/art/preview_gravship_rust.py
     (Pillow is not on the system python here.)
"""

import os
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
WS = "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100"
# Only ACTIVE mods are used here. Checked against ModsConfig.xml by packageId on
# 2026-08-13: guy762.MM.KotORCore ACTIVE, Arcjc007.GravshipCrashes ACTIVE, VGE
# ACTIVE (its VGE_* defs are present in the live DefDump). Okagrim.NecroTexGrav
# ([Odyssey] Necrotic Gravship Retextured) is INACTIVE and is deliberately NOT
# used — a preview built on art the game is not loading would prove nothing.
KOTOR = os.path.join(WS, "3254370945/Textures")          # SW KotOR Resources and Materials
VGE = os.path.join(WS, "3609835606/Textures")            # Vanilla Gravship Expanded - Ch.1
CRASH = os.path.join(WS, "3578515873/Textures")          # Gravship Crashes

# RimWorld draws one map cell at 64 px when the camera is fully zoomed in. A def's
# drawSize is in cells, so true-in-game px = drawSize * 64. That is the generous
# end; ordinary play zoom is roughly a third of it, so the strip is drawn twice.
PX_PER_CELL_MAX = 64
PX_PER_CELL_PLAY = 22

# What we want ON SCREEN, not what we type into the def. The def value is solved.
TARGET_PLATE = (118, 74, 45)     # rusted iron, the hull body
TARGET_TRIM = (132, 116, 87)     # sun-bleached sand, the trim and lettering

# For the UNMASKED sprites the solve-to-a-target trick does not apply, and that
# is the finding, not a bug. Measured 2026-08-13: the ship's own structural art
# is already dark — GravshipStructuralBeam_Atlas means (54,53,54), GravEngine
# (113,130,135). Multiply can only DARKEN, so no <color> can lift them to a mid
# rust brown; solving for one just clips to (255,255,255) and does nothing.
# What multiply CAN do to a dark source is bleed the blue-grey out of it and
# leave rust. So the unmasked panel applies a WASH whose max channel is 255 —
# the hue shift is real, the luminance is roughly preserved, nothing is crushed.
RUST_WASH = (255, 150, 96)       # bleeds cold grey to warm oxide
RUST_DEEP = (208, 112, 62)       # same hue, one stop down: neglected and filthy

# Nearest shipped ColorDefs, for the floor-paint half of the proposal. Values read
# from Data/Core/Defs/ColorDefs/ColorDefs.xml on 2026-08-13.
SHIPPED_RUST_COLORDEFS = [
    ("Structure_UmberBurnt", (90, 58, 32)),
    ("Structure_BrownDark", (90, 69, 38)),
    ("Structure_BrownDirt", (119, 91, 50)),
    ("Structure_Orange", (167, 96, 39)),
    ("Structure_Sandstone", (126, 104, 94)),
]


def load(path, mode="RGBA"):
    im = Image.open(path)
    return im.convert(mode)      # KotOR masks are Adam7-interlaced 8-bit palette


def classify(mp, x, y):
    """Which channel of the mask owns this pixel: 'r', 'g', 'b' or None."""
    mr, mg, mb = mp[x, y][:3]
    if mr > 128 and mg <= 128 and mb <= 128:
        return "r"
    if mg > 128 and mr <= 128 and mb <= 128:
        return "g"
    if mb > 128 and mr <= 128 and mg <= 128:
        return "b"
    return None


def mean_luma(art, mask, channel):
    """Mean per-channel value of the art under one mask region (or all of it)."""
    ap = art.load()
    mp = mask.load() if mask else None
    w, h = art.size
    tot = [0, 0, 0]
    n = 0
    for y in range(0, h, 2):                     # every other pixel: 4x faster, same mean
        for x in range(0, w, 2):
            r, g, b, a = ap[x, y]
            if a < 64:
                continue
            if mp is not None and classify(mp, x, y) != channel:
                continue
            tot[0] += r
            tot[1] += g
            tot[2] += b
            n += 1
    if not n:
        return None, 0
    return tuple(t / n for t in tot), n


def solve(src_mean, target):
    """The <color> that lands `target` on screen, given a source of `src_mean`.

    Unity multiplies: out = src * (color/255). So color = 255 * target / src.
    Returns (colour, clipped) — clipped is True when the source is too dark and
    the target is unreachable by multiply alone.
    """
    out = []
    clipped = False
    for s, t in zip(src_mean, target):
        if s <= 1:
            out.append(255)
            clipped = True
            continue
        v = 255.0 * t / s
        if v > 255:
            clipped = True
            v = 255
        out.append(int(round(v)))
    return tuple(out), clipped


def tint(art, mask, color, color_two=None, color_three=None):
    """Do what the shader does. mask=None means plain Cutout: multiply everything."""
    out = Image.new("RGBA", art.size, (0, 0, 0, 0))
    ap, op = art.load(), out.load()
    mp = mask.load() if mask else None
    w, h = art.size
    f = {"r": [c / 255.0 for c in color]}
    if color_two:
        f["g"] = [c / 255.0 for c in color_two]
    if color_three:
        f["b"] = [c / 255.0 for c in color_three]
    for y in range(h):
        for x in range(w):
            r, g, b, a = ap[x, y]
            if a == 0:
                continue
            if mp is None:
                k = f["r"]
            else:
                ch = classify(mp, x, y)
                k = f.get(ch)
                if k is None:
                    op[x, y] = (r, g, b, a)          # black mask / unlisted: untinted
                    continue
            op[x, y] = (min(255, int(r * k[0])),
                        min(255, int(g * k[1])),
                        min(255, int(b * k[2])), a)
    return out


# ---------------------------------------------------------------- sheet builder

CHECK_A, CHECK_B = (96, 96, 96), (120, 120, 120)


def checker(size, step=16):
    im = Image.new("RGBA", size, CHECK_A)
    d = ImageDraw.Draw(im)
    for y in range(0, size[1], step):
        for x in range(0, size[0], step):
            if (x // step + y // step) % 2:
                d.rectangle([x, y, x + step - 1, y + step - 1], fill=CHECK_B)
    return im


def paste_on_check(sheet, img, xy):
    bg = checker(img.size)
    bg.alpha_composite(img)
    sheet.paste(bg, xy)


def build_sheet(out_path, title, notes, panels, big=384):
    """panels = list of dicts: label, before(Image), after(Image), cells(float), sub"""
    pad, head, capt = 18, 96, 34
    n = len(panels)
    col_w = big * 2 + pad
    sheet_w = pad + n * (col_w + pad)
    # The true-size strip is clamped to the panel width. A 32-cell hull overlay is
    # 2048 px at max zoom — bigger than anything this sheet can show — and that
    # itself is the point: hull overlays are never downsampled, so trap #45 (art
    # correct at source, broken at render) cannot bite them. A 1-cell wall at
    # 64 px from a 640 px source is downsampled 10x and absolutely can.
    strip_h = min(int(PX_PER_CELL_MAX * max(p["cells"] for p in panels)), big) + 46
    sheet_h = head + capt + big + pad + strip_h + 60
    sheet = Image.new("RGBA", (sheet_w, sheet_h), (34, 34, 38, 255))
    d = ImageDraw.Draw(sheet)
    d.text((pad, 12), title, fill=(255, 235, 200, 255))
    for i, line in enumerate(notes):
        d.text((pad, 34 + i * 14), line, fill=(200, 200, 205, 255))

    x = pad
    for p in panels:
        d.text((x, head), p["label"], fill=(255, 255, 255, 255))
        d.text((x, head + 13), p["sub"], fill=(180, 180, 190, 255))
        for j, (tag, img) in enumerate((("SHIPPED", p["before"]), ("RUSTED", p["after"]))):
            bx = x + j * (big + pad)
            fit = img.copy()
            fit.thumbnail((big, big), Image.LANCZOS)
            d.text((bx, head + capt - 12), tag,
                   fill=(255, 210, 150, 255) if j else (170, 200, 255, 255))
            paste_on_check(sheet, fit, (bx, head + capt))
            # true in-game size, both zooms, drawn directly under its own panel,
            # clamped so a 32-cell sprite cannot run over its neighbour's column
            ty = head + capt + big + pad
            d.text((bx, ty - 14), "TRUE IN-GAME SIZE:", fill=(255, 200, 140, 255))
            tx = bx
            for zoom, plabel in ((PX_PER_CELL_MAX, "max zoom"),
                                 (PX_PER_CELL_PLAY, "play zoom")):
                s = max(4, int(round(p["cells"] * zoom)))
                shown = min(s, big // 2 - 8)
                small = img.resize((shown, shown), Image.LANCZOS)
                paste_on_check(sheet, small, (tx, ty + 16))
                cap = plabel if shown == s else f"{plabel} = {s}px, shown clipped"
                d.text((tx, ty + 16 + shown + 2), cap, fill=(150, 150, 160, 255))
                tx += shown + 16
        x += col_w + pad
    sheet.save(out_path)
    print("wrote", out_path, sheet.size)


# ------------------------------------------------------------------- the panels

def masked_sheet():
    """CutoutComplex: two independently paintable regions, zero new pixels."""
    specs = [
        dict(label="guy762_SWGravshipOverlay_KT400Freighter",
             sub="KT-400 freighter hull overlay | CutoutComplex | drawSize 32x32",
             art=os.path.join(KOTOR, "Gravships/KT400/KT400.png"),
             mask=os.path.join(KOTOR, "Gravships/KT400/KT400_m.png"),
             color=(215, 240, 255), color_two=(255, 240, 125), cells=32),
        dict(label="guy762_SWGravshipOverlay_DynamicFreighter",
             sub="Dynamic-class freighter hull | CutoutComplex | drawSize 32x32",
             art=os.path.join(KOTOR, "Gravships/Dynamic/Dynamic.png"),
             mask=os.path.join(KOTOR, "Gravships/Dynamic/Dynamic_m.png"),
             color=(135, 90, 50), color_two=(225, 225, 225), cells=32),
        dict(label="guy762_PoweredWall_DreadnaughtA",
             sub="durasteel ship wall | CutoutComplex | 1 cell",
             art=os.path.join(KOTOR, "Buildings/Walls/DreadnaughtWallA.png"),
             mask=os.path.join(KOTOR, "Buildings/Walls/DreadnaughtWallA_m.png"),
             color=(140, 65, 65), color_two=(165, 165, 180), cells=1),
    ]
    panels = []
    for s in specs:
        art, mask = load(s["art"]), load(s["mask"])
        if art.size != mask.size:
            mask = mask.resize(art.size, Image.NEAREST)
        mr, nr = mean_luma(art, mask, "r")
        mg, ng = mean_luma(art, mask, "g")
        c1, clip1 = solve(mr, TARGET_PLATE) if mr else ((255, 255, 255), False)
        c2, clip2 = solve(mg, TARGET_TRIM) if mg else (None, False)
        print(f"  {s['label']}")
        print(f"    RED  region {nr:>7} px  mean {tuple(round(v) for v in mr)}"
              f"  -> <color>{c1}</color>{'  CLIPPED' if clip1 else ''}")
        if mg:
            print(f"    GREEN region {ng:>7} px  mean {tuple(round(v) for v in mg)}"
                  f"  -> <colorTwo>{c2}</colorTwo>{'  CLIPPED' if clip2 else ''}")
        else:
            print("    GREEN region      0 px  (single-region mask)")
        panels.append(dict(
            label=s["label"], sub=s["sub"], cells=s["cells"],
            before=tint(art, mask, s["color"], s["color_two"]),
            after=tint(art, mask, c1, c2 or s["color_two"])))
    build_sheet(
        os.path.join(HERE, "REVIEW_gravship_rust_masked.png"),
        "MASKED (CutoutComplex) — two paintable regions, ZERO new pixels. "
        "LEFT of each pair: the colours shipped today. RIGHT: solved rust.",
        ["Mechanism: art x <color> where the mask is RED, art x <colorTwo> where it is GREEN, "
         "art untouched where it is BLACK.",
         "Every RIGHT image is a def patch of two RGB triples. Not one pixel of art was "
         "authored, edited or redrawn.",
         "Solved, not guessed: <color> = 255 * target / source-mean, so the sprite LANDS on "
         "rust instead of merely being multiplied toward it."],
        panels)


def unmasked_sheet():
    """Plain Cutout: one global multiply. This is the majority of the ship."""
    specs = [
        dict(label="GravEngine  (art: VGE retexture)",
             sub="the gravship core | plain Cutout, NO mask | drawSize 3x3",
             art=os.path.join(VGE, "Things/Structures/GravEngines/GravEngine/GravEngine.png"),
             cells=3),
        dict(label="VGE_GravshipStructuralBeam",
             sub="linked structural beam atlas | plain Cutout, NO mask | 1 cell",
             art=os.path.join(VGE, "Things/Structures/Linked/GravshipStructuralBeam_Atlas.png"),
             cells=1),
        dict(label="BrokenSubstructure  (TerrainDef, the deck)",
             sub="ruptured deck plate | isPaintable true | 1 cell",
             art=os.path.join(CRASH, "Terrain/Surfaces/Substructure/BrokenSubstructure.png"),
             cells=1),
    ]
    panels = []
    for s in specs:
        art = load(s["art"])
        m, n = mean_luma(art, None, None)
        after = tint(art, None, RUST_WASH)
        am, _ = mean_luma(after, None, None)
        print(f"  {s['label']}")
        print(f"    whole sprite {n:>7} px  source mean {tuple(round(v) for v in m)}"
              f"  x <color>{RUST_WASH}</color>  -> rendered mean "
              f"{tuple(round(v) for v in am)}")
        panels.append(dict(
            label=s["label"], sub=s["sub"], cells=s["cells"],
            before=art, after=after))
    build_sheet(
        os.path.join(HERE, "REVIEW_gravship_rust_unmasked.png"),
        "UNMASKED (plain Cutout) — one global multiply, ZERO new pixels. "
        f"LEFT: untinted, as it renders today. RIGHT: one <color>{RUST_WASH}</color> node.",
        ["No mask is required. RimWorld honours graphicData/color on the DEFAULT Cutout "
         "shader — the trick Ludeon itself uses:",
         "AncientFortifiedWall (127,135,127) and OrbitalAncientFortifiedWall (132,140,140) are "
         "two defs over ONE atlas, differing only by that node.",
         "THE LIMIT, measured: <color> MULTIPLIES, so it can only DARKEN. This art is already "
         "dark (beam atlas means 54,53,54), so no <color> can",
         "lift it to a mid rust-brown. What the wash does instead is bleed the cold blue-grey "
         "out and leave oxide. Rusting is free; brightening is not."],
        panels)


def main():
    print("=== sheet 1: masked (CutoutComplex) ===")
    masked_sheet()
    print("\n=== sheet 2: unmasked (plain Cutout) ===")
    unmasked_sheet()
    print("\nnearest SHIPPED ColorDefs for the paintable deck (Data/Core/.../ColorDefs.xml):")
    for name, rgb in SHIPPED_RUST_COLORDEFS:
        print(f"    {name:<24} {rgb}")


if __name__ == "__main__":
    main()
