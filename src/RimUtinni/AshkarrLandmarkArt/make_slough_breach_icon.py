#!/usr/bin/env python3
"""
make_slough_breach_icon.py — the world-map icon for RUT_Slough_GelatinousBreach.

VAULT_DUNGEON_BUILD_1 / dungeons_arc_spec.md SS3.9 (owner ruling, 2026-09-01):
"V5 gets a NEW organic landmark ... V5 is the second type-2 vault and must read
as a breach, distinct from V4." V4 already reads as a place via the reused
AncientWarehouse landmark (masonry treatment); V5 has none yet and needs one
that says "torn open, something got out" rather than "abandoned building."

WHY PROCEDURAL, not generated. Same reasoning as make_complex_structures_icon.py
in this folder: local image generation is PARKED (owner ruling 2026-09-05) and
the Codex $imagegen path pops an interactive Windows UAC dialog that must not
fire during unattended FOUNDRY/BELT work. This draws the icon deterministically
instead, matched to the house style measured off the existing sheets in
Textures/World/Landmarks/Ashkarr/ (1024x1024 RGBA, 2x2 grid of four 512x512
variants, chunky near-black outline, flat-shaded fills) and to the "organic"
treatment already in the house palette (landmark_art.py's t_organic: dark
gullet centre blooming to a raw, wet rim) — but with its OWN silhouette and
colour key so it reads as a DIFFERENT place from VEE_FleshPits (pink, radial
folds, a living thing) and from RUT_GapingDoom (green sarlacc throat, a single
round maw). This is a RUPTURE: a ragged, torn-edged membrane patch with pooled
ooze breaking through it and smaller secondary tears nearby — the type-2
"breach" reading (dungeons_arc_spec.md SS3.3: "torn open from inside... the
thing that got out left a trail"), sickly yellow-green rather than FleshPits'
pink or the vault template's own AA_GreenGoo swatch.

Deterministic: layout comes from a fixed vertex table, never RNG, so a re-run
reproduces the same icon and there is no seed that could roll a different one.

    python3 make_slough_breach_icon.py            # writes the PNG
"""
import os
import math
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "Textures", "World", "Landmarks", "Ashkarr",
                    "RUT_Slough_GelatinousBreach.png")

CELL = 512
OUTLINE = (30, 34, 24, 255)          # near-black with a faint green cast
RIM = (150, 168, 60, 255)            # raw, bright rim where the tear is fresh
MID = (96, 118, 46, 255)             # sickly mid-green
DARK = (46, 54, 26, 255)             # deep pooled ooze
SHEEN = (188, 206, 120, 255)         # wet highlight fleck
GROUND = (110, 100, 78, 255)         # torn ground scab around the breach
W = 9                                # outline weight, matched to the sheets


def ring(cx, cy, r, n, jag, phase=0.0):
    """A closed ragged ring: n vertices at radius r, each nudged by a fixed
    per-vertex jitter table (jag), so the edge reads as TORN rather than round."""
    pts = []
    for i in range(n):
        a = phase + 2 * math.pi * i / n
        rr = r * (1.0 + jag[i % len(jag)])
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


# Fixed jitter tables (no RNG) — each a different "torn edge" fingerprint.
JAG_A = [0.18, -0.08, 0.22, -0.14, 0.05, -0.20, 0.16, -0.06, 0.24, -0.12, 0.02, -0.18]
JAG_B = [-0.10, 0.20, -0.16, 0.08, -0.22, 0.14, -0.04, 0.18, -0.14, 0.06, -0.20, 0.10]
JAG_C = [0.12, -0.18, 0.06, 0.20, -0.10, -0.04, 0.16, -0.22, 0.08, 0.02, -0.14, 0.18]

# Four variants: (main breach cx,cy,r,n,jag,phase), [secondary tears...]
VARIANTS = [
    ((256, 260, 150, 11, JAG_A, 0.3),
     [(120, 130, 34, 8, JAG_B, 1.1), (400, 360, 30, 9, JAG_C, 2.4),
      (380, 140, 22, 7, JAG_A, 0.7)]),
    ((260, 250, 140, 12, JAG_B, 0.9),
     [(400, 150, 36, 8, JAG_A, 0.4), (110, 360, 32, 9, JAG_C, 1.8),
      (150, 150, 20, 7, JAG_B, 2.9)]),
    ((250, 270, 155, 11, JAG_C, 1.6),
     [(400, 380, 30, 8, JAG_B, 0.2), (120, 150, 34, 9, JAG_A, 1.3),
      (390, 130, 22, 7, JAG_C, 3.0)]),
    ((262, 245, 145, 12, JAG_A, 2.2),
     [(130, 360, 36, 8, JAG_C, 0.6), (400, 160, 28, 9, JAG_B, 1.9),
      (140, 140, 24, 7, JAG_A, 2.6)]),
]


def draw_tear(d, cx, cy, r, n, jag, phase, ox, oy, big):
    pts = [(x + ox, y + oy) for x, y in ring(cx, cy, r, n, jag, phase)]
    # torn ground scab: a wider, lower-contrast halo the breach sits inside
    halo = [(x + ox, y + oy) for x, y in ring(cx, cy, r * 1.28, n, jag, phase)]
    d.polygon(halo, fill=GROUND, outline=OUTLINE, width=max(3, W // 2))
    d.polygon(pts, fill=MID, outline=OUTLINE, width=W if big else max(3, W // 2))
    # pooled ooze, offset slightly off-centre so it reads as SPILLING not centred
    pool = [(x + ox, y + oy) for x, y in
            ring(cx - r * 0.12, cy + r * 0.10, r * 0.55, max(6, n - 2), jag, phase + 0.4)]
    d.polygon(pool, fill=DARK)
    if big:
        rim_pts = [(x + ox, y + oy) for x, y in
                   ring(cx - r * 0.12, cy + r * 0.10, r * 0.60, max(6, n - 2),
                        jag, phase + 0.4)]
        d.line(rim_pts + [rim_pts[0]], fill=RIM, width=max(2, W // 3))
        # a few wet sheen flecks, fixed positions relative to the breach
        for fx, fy in ((-0.35, -0.25), (0.30, -0.10), (0.05, 0.35), (-0.10, 0.05)):
            px, py = cx + ox + r * fx, cy + oy + r * fy
            d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=SHEEN)


def draw_variant(d, ox, oy, main, tears):
    cx, cy, r, n, jag, phase = main
    draw_tear(d, cx, cy, r, n, jag, phase, ox, oy, big=True)
    for (tcx, tcy, tr, tn, tjag, tphase) in tears:
        draw_tear(d, tcx, tcy, tr, tn, tjag, tphase, ox, oy, big=False)


def main():
    img = Image.new("RGBA", (CELL * 2, CELL * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, (main, tears) in enumerate(VARIANTS):
        ox, oy = (i % 2) * CELL, (i // 2) * CELL
        draw_variant(d, ox, oy, main, tears)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT)
    print("wrote %s  %s" % (OUT, img.size))


if __name__ == "__main__":
    main()
