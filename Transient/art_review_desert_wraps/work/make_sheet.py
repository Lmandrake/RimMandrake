#!/usr/bin/env python3
"""Contact sheet: DESERT_WRAPS_ART_COMMISSION_1 candidates, style-pick stage.

Convention matches Transient/art_review_generic_marks/make_sheet.py: dark
warm-brown ground, checker tile behind each RGBA candidate, big + sprite-size
rows, plus a style-anchor row showing OUR OWN absorbed Sovereign-Tusken art
(never the unsubscribed donor mod's own files) for comparison.
"""
from PIL import Image, ImageDraw, ImageFont

REPO = "/mnt/d/Luke/dev/Rimworld/"
D = REPO + "Transient/art_review_desert_wraps/"

WRAPS = [
    ("wrap_A_bound", "A - bound bucket", "1 mass, 3 spiral seams, minimal"),
    ("wrap_B_coil", "B - tight coil", "11-12 parallel bandage bands, stocky barrel"),
    ("wrap_C_cowl", "C - mantle + cowl", "2-layer: shoulder mantle over underwrap"),
    ("wrap_D_weathered", "D - weathered", "ragged torn hem, loose strip, patch/stitch"),
]
HEADS = [
    ("head_H1_pot", "H1 - flat pot", "square flat crown, straight sides, abrupt jaw"),
    ("head_H2_browridge", "H2 - brow ridge", "low sloped cranium, heavy bone brow, wide jaw"),
]
ANCHOR = [
    (REPO + "src/RimStarWars/Armoury/Textures/SWApparel/Sovereign_Tuskens/Wraps.png",
     "SovereignTusken Wraps", "our own absorbed asset (KotorCore wave)"),
    (REPO + "src/RimStarWars/Armoury/Textures/SWApparel/Sovereign_Tuskens/SandHead.png",
     "SovereignTusken SandHead", "our own absorbed mask/hood asset"),
    (REPO + "src/RimStarWars/StarWarsRaces/Textures/RimMandrakeSW/SWX/Pawn/HeadType/Sov_tusken/HeadSandM_south.png",
     "Sov_tusken HeadSandM", "our own absorbed devolved-head art (Sov.Sith wave)"),
]

BIG, SMALL, PAD = 300, 96, 18
BG = (26, 22, 19)
INK = (233, 224, 210)
DIM = (156, 141, 124)
ACCENT = (214, 149, 72)


def checker(size, a=(58, 50, 44), b=(44, 38, 33), step=12):
    im = Image.new("RGB", (size, size), a)
    d = ImageDraw.Draw(im)
    for y in range(0, size, step):
        for x in range(0, size, step):
            if ((x // step) + (y // step)) % 2:
                d.rectangle([x, y, x + step - 1, y + step - 1], fill=b)
    return im


def tile(path, size):
    base = checker(size)
    art = Image.open(path).convert("RGBA").resize((size, size), Image.LANCZOS)
    base.paste(art, (0, 0), art)
    return base


def font(sz, bold=False):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else ""),
              "/mnt/c/Windows/Fonts/%s.ttf" % ("arialbd" if bold else "arial")):
        try:
            return ImageFont.truetype(p, sz)
        except OSError:
            continue
    return ImageFont.load_default()


f_title = font(30, True)
f_head = font(19, True)
f_lab = font(17, True)
f_sub = font(14)

ncols = 4
col_w = BIG + PAD
sheet_w = PAD + ncols * col_w
row_big_h = BIG + 52
row_small_h = SMALL + 46
sheet_h = (74
           + 30 + row_big_h        # wraps, big
           + 30 + row_small_h      # wraps, sprite size
           + 34 + row_big_h        # heads, big (2 of 4 cols used)
           + 30 + row_small_h      # heads, sprite size
           + 34 + row_big_h        # style anchor, big (3 of 4 cols used)
           + PAD)

sheet = Image.new("RGB", (sheet_w, sheet_h), BG)
d = ImageDraw.Draw(sheet)

d.text((PAD, 20), "Desert wraps + devolved head - style candidates", font=f_title, fill=INK)
d.text((PAD, 52),
       "DESERT_WRAPS_ART_COMMISSION_1  -  candidates for the owner's eye, not shipped content  |  "
       "original art, prompted from design/Jawa/desert_wraps_design_capture.md - no donor PNG used as input",
       font=f_sub, fill=DIM)

y = 74 + 30
d.text((PAD, y - 26), "WRAP STYLE CANDIDATES (achromatic - Stuff-colored at craft time, like the source family)",
       font=f_head, fill=ACCENT)
for i, (n, label, note) in enumerate(WRAPS):
    x = PAD + i * col_w
    sheet.paste(tile(D + f"final/{n}.png", BIG), (x, y))
    d.text((x, y + BIG + 6), label, font=f_lab, fill=INK)
    d.text((x, y + BIG + 27), note, font=f_sub, fill=DIM)

y += row_big_h + 30
d.text((PAD, y - 26), "WRAPS AT SPRITE SIZE (96px - does the silhouette still read?)", font=f_head, fill=ACCENT)
for i, (n, label, note) in enumerate(WRAPS):
    x = PAD + i * col_w
    sheet.paste(tile(D + f"final/{n}.png", SMALL), (x, y))
    d.text((x, y + SMALL + 6), label, font=f_sub, fill=DIM)

y += row_small_h + 34
d.text((PAD, y - 26), "DEVOLVED HEAD-SHAPE CANDIDATES (front-facing; south/north/east are engine-appended per HeadTypeDef)",
       font=f_head, fill=ACCENT)
for i, (n, label, note) in enumerate(HEADS):
    x = PAD + i * col_w
    sheet.paste(tile(D + f"final/{n}.png", BIG), (x, y))
    d.text((x, y + BIG + 6), label, font=f_lab, fill=INK)
    d.text((x, y + BIG + 27), note, font=f_sub, fill=DIM)

y += row_big_h + 30
d.text((PAD, y - 26), "HEADS AT SPRITE SIZE", font=f_head, fill=ACCENT)
for i, (n, label, note) in enumerate(HEADS):
    x = PAD + i * col_w
    sheet.paste(tile(D + f"final/{n}.png", SMALL), (x, y))
    d.text((x, y + SMALL + 6), label, font=f_sub, fill=DIM)

y += row_small_h + 34
d.text((PAD, y - 26), "STYLE ANCHOR - OUR OWN ABSORBED SOVEREIGN-TUSKEN ART (shipping, not the unsubscribed mod)",
       font=f_head, fill=ACCENT)
for i, (p, label, note) in enumerate(ANCHOR):
    x = PAD + i * col_w
    sheet.paste(tile(p, BIG), (x, y))
    d.text((x, y + BIG + 6), label, font=f_lab, fill=INK)
    d.text((x, y + BIG + 27), note, font=f_sub, fill=DIM)

out = D + "desert_wraps_contact_sheet_2026-09-09.png"
sheet.save(out)
print("wrote", out, sheet.size)
