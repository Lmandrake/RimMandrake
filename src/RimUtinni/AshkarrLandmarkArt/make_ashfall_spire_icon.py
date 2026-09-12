#!/usr/bin/env python3
"""
make_ashfall_spire_icon.py — the world-map icon for RUT_AshfallSpire ("The Spire").

ASHFALL_SPIRE_LANDMARK_1 / design/Jawa/worldbuilding/ashfall_research_base.md SS3.
Owner's display register, verbatim: "a mysterious thin black needle of a building
with a disc landing near the top, visible only occasionally due to the atmospheric
turbulence over the Scald's mountains." Every element below is that sentence and
nothing else — needle, disc near the top, ash hiding it. No interior, no builders,
no plot: the dungeon shell and campaign function are out of this item's scope.

WHY PROCEDURAL, not generated. Same reasoning as make_slough_breach_icon.py and
make_complex_structures_icon.py in this folder: local image generation is PARKED
(owner ruling 2026-09-05) and the Codex $imagegen path pops an interactive Windows
UAC dialog that must not fire during unattended FOUNDRY/BELT work. This draws the
icon deterministically instead, matched to the house convention measured off the
existing sheets in Textures/World/Landmarks/Ashkarr/ (1024x1024 RGBA, 2x2 grid of
four 512x512 variants, near-black outline, flat-shaded fills).

The one place it departs from the house style on purpose: the outline weight. The
other sheets carry a chunky W=9 outline around blobby organic shapes. A 9px outline
on a shaft this thin would swallow the shaft entirely and the silhouette would read
as a fat post, not a needle. So the needle is drawn as its own near-black FILL (it
is a black needle — the outline colour IS the subject) with a cold rim-light down
one edge so it still separates from a dark world tile, and the chunky outline is
kept only where the house style needs it: the rock the Spire stands on.

Distinct from the other Ashkarr structure icons: RUT_ComplexStructures and the
vanilla AncientWarehouse/Ruins repaints all read as masonry footprints seen from
above; sw_Sarlacc and RUT_GapingDoom read as holes. This is the only one that is a
single vertical thing standing up, and the only one deliberately half-occluded.

Four variants differ in ridge profile, spire height, disc cant and — the point —
WHICH bands of ash are crossing it, so the four map cells read as four glimpses of
the same object at different moments of the turbulence rather than four objects.

Deterministic: every coordinate comes from a fixed table, never RNG, so a re-run
reproduces the same sheet byte-for-byte and there is no seed that could roll a
different one.

    python3 make_ashfall_spire_icon.py            # writes the PNG
"""
import os
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "Textures", "World", "Landmarks", "Ashkarr",
                   "RUT_AshfallSpire.png")

CELL = 512
CX = CELL // 2

OUTLINE = (12, 12, 16, 255)      # near-black, the house outline
NEEDLE = (20, 20, 26, 255)       # the black needle itself
RIMLIGHT = (86, 92, 104, 255)    # cold edge light so the silhouette separates
DISC = (28, 28, 36, 255)         # the disc, same black body
DISC_FACE = (132, 138, 150, 255) # the pale dish face catching what light there is
DISC_EDGE = (58, 62, 72, 255)
ROCK = (74, 64, 54, 255)         # ashfall ridge rock, warm dark
ROCK_LIT = (108, 96, 80, 255)    # sunward face of the ridge
ASH = (206, 194, 172)            # blowing ash — alpha applied per band
W = 9                            # house outline weight, rock only


# (ridge ridgeline y-offsets, spire base y, spire top y, half-width bottom,
#  half-width top, disc centre y, disc half-width, disc half-height, disc cant,
#  [(band y, band height, band alpha), ...])
VARIANTS = [
    # 1 — clearest glimpse: one thin band low across the rock only
    (( 24,  -8,  16,  -4,  20), 404, 58, 13, 5, 126, 64, 17, -7,
     [(356, 46, 74), (196, 22, 40)]),
    # 2 — mid-occlusion: a band cuts the shaft just under the disc
    ((  8,  22,  -6,  18,  -2), 410, 66, 14, 5, 138, 60, 16, 5,
     [(372, 52, 82), (168, 40, 122), (250, 18, 46)]),
    # 3 — mostly hidden: a wide band eats the middle third of the shaft
    (( 30,  -2,  26,   6,  14), 400, 54, 12, 4, 120, 68, 18, -3,
     [(348, 44, 70), (238, 92, 150), (140, 20, 54)]),
    # 4 — top-lit: ash sits low, the disc stands clear above it
    (( -4,  18,   4,  24,  -8), 414, 62, 14, 5, 130, 62, 17, 9,
     [(392, 58, 96), (308, 40, 120), (196, 16, 34)]),
]


RIDGE_X = (48, 122, 210, 300, 392, 464)
RIDGE_Y = (474, 406, 372, 390, 400, 470)
RIDGE_FOOT = 484          # kept well inside the cell: the closing bottom edge
                          # and its 9px outline must not touch the cell border,
                          # or the atlas renders a black bar under every icon.


def ridge(offs):
    """The impassable ridge the Spire stands on — a contained massif, not a
    full-width band, so the icon sits inside its world tile rather than running
    off the edges. offs jitters five fixed peak heights so no two variants share
    a profile."""
    pts = [(RIDGE_X[i], RIDGE_Y[i] + (offs[i - 1] if 0 < i <= len(offs) else 0))
           for i in range(len(RIDGE_X))]
    return pts + [(RIDGE_X[-1], RIDGE_FOOT), (RIDGE_X[0], RIDGE_FOOT)]


def draw_rock(d, ox, oy, offs):
    pts = [(x + ox, y + oy) for x, y in ridge(offs)]
    d.polygon(pts, fill=ROCK, outline=OUTLINE, width=W)
    # sunward face: the WHOLE flank left of the crest, cut at the crest itself.
    # Anything narrower leaves a vertical seam in the middle of the massif and
    # reads as a pale block set on the mountain rather than a lit slope.
    crest = 2
    flank = [(RIDGE_X[i] + ox, RIDGE_Y[i] + (offs[i - 1] if i > 0 else 0) + oy)
             for i in range(crest + 1)]
    d.polygon(flank + [(RIDGE_X[crest] + ox, RIDGE_FOOT - 5 + oy),
                       (RIDGE_X[0] + ox, RIDGE_FOOT - 5 + oy)], fill=ROCK_LIT)


def draw_spire(d, ox, oy, base_y, top_y, hw_b, hw_t):
    """A tapered black needle. Drawn as fill, not as an outlined shape — see the
    module docstring on why the house W=9 outline is wrong here."""
    shaft = [(CX - hw_b + ox, base_y + oy), (CX - hw_t + ox, top_y + oy),
             (CX + hw_t + ox, top_y + oy), (CX + hw_b + ox, base_y + oy)]
    d.polygon(shaft, fill=NEEDLE)
    # cold rim light down the left edge only, 2px, so it reads against dark tiles
    d.line([(CX - hw_b + ox, base_y + oy), (CX - hw_t + ox, top_y + oy)],
           fill=RIMLIGHT, width=3)
    # the mast above the disc, thinner still, tapering to a point
    d.line([(CX + ox, top_y + oy), (CX + ox, top_y - 26 + oy)],
           fill=NEEDLE, width=max(3, hw_t))
    # a shallow flare where the needle meets the rock, so it stands ON it
    d.polygon([(CX - hw_b - 9 + ox, base_y + 14 + oy),
               (CX - hw_b + ox, base_y - 18 + oy),
               (CX + hw_b + ox, base_y - 18 + oy),
               (CX + hw_b + 9 + ox, base_y + 14 + oy)], fill=NEEDLE)


def draw_disc(d, ox, oy, cy, rx, ry, cant):
    """The disc landing near the top: an ellipse canted a few degrees off level,
    faked by drawing it as a flattened polygon whose two ends sit at different
    heights — a real rotation would need a second layer and this reads the same
    at 128px, which is the size a world-map icon is actually seen at."""
    left = (CX - rx + ox, cy + cant + oy)
    right = (CX + rx + ox, cy - cant + oy)
    top = (CX + ox, cy - ry + oy)
    bot = (CX + ox, cy + ry + oy)
    # body (the dark underside), then the pale face as an inset upper crescent
    d.polygon([left, top, right, bot], fill=DISC, outline=DISC_EDGE, width=3)
    face = [(left[0] + rx * 0.22, left[1] - ry * 0.18),
            (top[0], top[1] + ry * 0.30),
            (right[0] - rx * 0.22, right[1] - ry * 0.18),
            (CX + ox, cy + oy)]
    d.polygon(face, fill=DISC_FACE)
    # the stub that joins the disc to the mast
    d.line([(CX + ox, cy + oy), (CX + ox, cy + ry + 10 + oy)],
           fill=DISC, width=7)


def ash_cell(bands):
    """Blowing ash drawn on its OWN transparent layer and composited, because
    PIL's ImageDraw replaces pixels rather than blending them — an RGBA fill with
    alpha<255 drawn straight onto the sheet would punch a hole in the spire
    instead of veiling it. Blurred so the band edges are weather, not stripes.

    Built at CELL size and pasted, never blurred across the full sheet: a
    GaussianBlur over the 2x2 atlas would smear each variant's ash into its
    neighbours' cells, and a texture atlas must not bleed between cells."""
    layer = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for (by, bh, ba) in bands:
        ld.rectangle([-4, by, CELL + 4, by + bh], fill=ASH + (ba,))
    return layer.filter(ImageFilter.GaussianBlur(11))


def main():
    img = Image.new("RGBA", (CELL * 2, CELL * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    ash = Image.new("RGBA", (CELL * 2, CELL * 2), (0, 0, 0, 0))
    for i, v in enumerate(VARIANTS):
        (offs, base_y, top_y, hw_b, hw_t, dcy, drx, dry, cant, bands) = v
        ox, oy = (i % 2) * CELL, (i // 2) * CELL
        draw_rock(d, ox, oy, offs)
        draw_spire(d, ox, oy, base_y, top_y, hw_b, hw_t)
        draw_disc(d, ox, oy, dcy, drx, dry, cant)
        ash.paste(ash_cell(bands), (ox, oy))
    # ash goes OVER everything — that is the whole "visible only occasionally"
    # reading.
    img = Image.alpha_composite(img, ash)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT)
    print("wrote %s  %s" % (OUT, img.size))


if __name__ == "__main__":
    main()
