#!/usr/bin/env python3
"""Contact sheet: 6 generic mark candidates vs the shipping graffiti art."""
from PIL import Image, ImageDraw, ImageFont

REPO = "/mnt/d/Luke/dev/Rimworld/"
D = REPO + "Transient/art_review_generic_marks/"

CANDS = [
    ("tally", "tally count", "13 strokes, soot black"),
    ("arrow", "direction arrow", "burnt ochre, drips"),
    ("hazard", "warning glyph", "dried-clay red"),
    ("sun", "sun mark", "ochre disc + 8 rays"),
    ("handprint", "handprint", "pressed ochre palm"),
    ("spiral", "spiral", "black over red echo"),
]
EXIST = [
    (REPO + "src/RimMandrake/SacredGraffiti/Textures/Things/Filth/SacredMark/SacredMark_Ishko.png",
     "SacredMark_Ishko", "campaign mark (shipping)"),
    (REPO + "src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Vandal/vandal_2.png",
     "RM_Graffiti_Vandal 2", "donor vandal tile (shipping)"),
    (REPO + "src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Vandal/vandal_5.png",
     "RM_Graffiti_Vandal 5", "donor vandal tile (shipping)"),
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

ncols = 6
col_w = BIG + PAD
sheet_w = PAD + ncols * col_w
row_big_h = BIG + 52
row_small_h = SMALL + 46
sheet_h = (74                      # title
           + 30 + row_big_h        # candidates, big
           + 30 + row_small_h      # candidates, sprite size
           + 34 + row_big_h        # existing art, big
           + 30 + row_small_h      # existing art, sprite size
           + PAD)

sheet = Image.new("RGB", (sheet_w, sheet_h), BG)
d = ImageDraw.Draw(sheet)

d.text((PAD, 20), "RM Graffiti - generic default mark candidates", font=f_title, fill=INK)
d.text((PAD, 52), "GRAFFITI_GENERIC_MARKS_1  -  candidates for the owner's eye, not shipped content"
                  "   |   640x640 RGBA, Graphic_Single, subject inside a 512px box with 64px margin",
       font=f_sub, fill=DIM)

y = 74 + 30
d.text((PAD, y - 26), "CANDIDATES", font=f_head, fill=ACCENT)
for i, (n, label, note) in enumerate(CANDS):
    x = PAD + i * col_w
    sheet.paste(tile(D + "final/RM_Mark_%s.png" % n, BIG), (x, y))
    d.text((x, y + BIG + 6), label, font=f_lab, fill=INK)
    d.text((x, y + BIG + 27), note, font=f_sub, fill=DIM)

y += row_big_h + 30
d.text((PAD, y - 26), "CANDIDATES AT SPRITE SIZE (96px - does it still read?)", font=f_head, fill=ACCENT)
for i, (n, label, note) in enumerate(CANDS):
    x = PAD + i * col_w
    sheet.paste(tile(D + "final/RM_Mark_%s.png" % n, SMALL), (x, y))
    d.text((x, y + SMALL + 6), label, font=f_sub, fill=DIM)

y += row_small_h + 34
d.text((PAD, y - 26), "EXISTING SHIPPING ART, FOR STYLE COMPARISON", font=f_head, fill=ACCENT)
for i, (p, label, note) in enumerate(EXIST):
    x = PAD + i * col_w
    sheet.paste(tile(p, BIG), (x, y))
    d.text((x, y + BIG + 6), label, font=f_lab, fill=INK)
    d.text((x, y + BIG + 27), note, font=f_sub, fill=DIM)

y += row_big_h + 30
d.text((PAD, y - 26), "EXISTING ART AT SPRITE SIZE", font=f_head, fill=ACCENT)
for i, (p, label, note) in enumerate(EXIST):
    x = PAD + i * col_w
    sheet.paste(tile(p, SMALL), (x, y))
    d.text((x, y + SMALL + 6), label, font=f_sub, fill=DIM)

out = D + "generic_marks_contact_sheet.png"
sheet.save(out)
print("wrote", out, sheet.size)
