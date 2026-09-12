#!/usr/bin/env python3
"""make_utinni_worldicon.py — the world-map sprite for the Utinni in flight.

UTINNI_WORLDMAP_FLIGHT_ICON_1. Vanilla's WorldObjectDef Gravship draws
World/WorldObjects/Expanding/Gravship (a pale grav-engine dome) when zoomed out
and World/WorldObjects/Caravan when not. Both are replaced with OUR ship.

WHERE THE SILHOUETTE COMES FROM — this is the point of the script. It is NOT
drawn from imagination: it is the ACTUAL footprint of the current ship, read
straight out of the authored layout

    design/Jawa/worldbuilding/ship_build/exported/Gravship_v2_ring_2026-09-12.xml

(ShipLayoutDefV2, 88 rows x 94 cols). A cell counts as hull when it carries a
foundationDef. Re-export the ship and re-run this and the icon follows the ship;
there is no hand-traced outline to drift out of date.

WHY PROCEDURAL, not generated. Same reasoning as
src/RimUtinni/AshkarrLandmarkArt/make_slough_breach_icon.py: local image
generation is PARKED (owner ruling 2026-09-05) and the Codex $imagegen path pops
an interactive Windows UAC dialog that must not fire during unattended work. A
generator could not have drawn the real footprint anyway.

COLOUR IS A VALUE PROBLEM HERE, NOT A HUE PROBLEM. Gravship.ExpandingIconColor
is a C# override — `base.Faction?.Color ?? Color.white` (RimWorld/Planet/
Gravship.cs:146) — so the XML expandingIconColor field is ignored and the sprite
is MULTIPLIED by the player faction's colour (the "pale blue" the owner sees
today is that tint, not the art). Multiplication preserves value ordering and
destroys hue, so this palette is near-neutral and carries all its reading in
value: near-black keel line, dark hull, a top-lit gradient, a bright hub plate
and a brighter engine core. Under any faction tint the ring and hub still read.

SIZE. 64x64, matched to vanilla's own measured PNGs (both
ludeon.rimworld.odyssey .../expanding/gravship.png and ludeon.rimworld.core
Caravan.png are 64x64 — measured from the extracted bundle cache, not guessed).
The engine scales the expanding icon itself via expandingIconDrawSize 1.35, so
one size is all that is needed. Drawn at 16x supersample and area-downsampled
premultiplied, because plain averaging on a cutout drags transparent black into
the rim.

Deterministic: no RNG anywhere. A re-run reproduces the same two PNGs.

    python3 Source/make_utinni_worldicon.py
"""
import os
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
REPO = os.path.normpath(os.path.join(MOD, "..", "..", ".."))

SHIP_XML = os.path.join(
    REPO, "design", "Jawa", "worldbuilding", "ship_build", "exported",
    "Gravship_v2_ring_2026-09-12.xml")

OUT_EXPANDING = os.path.join(
    MOD, "Textures", "World", "WorldObjects", "Expanding", "RUT_Utinni.png")
OUT_CARAVAN = os.path.join(
    MOD, "Textures", "World", "WorldObjects", "RUT_UtinniCaravan.png")

FINAL = 64          # vanilla's own canvas for both textures (measured)
SS = 16             # supersample factor
BIG = FINAL * SS
MARGIN = 2 * SS     # keep the silhouette off the canvas edge

# Near-neutral, value-led. Every one of these survives a multiplicative tint.
#
# ⚠️ The values are deliberately MID, not the "dark hull" of the design note
# taken literally, and vanilla shows why: its own Expanding/Gravship is a
# near-WHITE hull inside a black keel precisely because the faction tint can
# only ever darken. Author the hull dark and the tint takes it to mud on a
# bright globe. Authored mid, a typical faction colour lands it dark and the
# ship still reads. The dark-hulk character comes from the heavy black keel and
# the warm neutral cast, not from low overall luminance.
KEEL = (18, 16, 14, 255)         # outline / keel line, near-black
HULL_TOP = (178, 166, 146, 255)  # top-lit hull
HULL_BOT = (104, 95, 82, 255)    # shadowed hull
HUB_PLATE = (222, 212, 190, 255)
HUB_EDGE = (26, 23, 20, 255)
CORE = (252, 246, 228, 255)

HUB_CX, HUB_CZ = 42, 45   # hub centre in layout cells (the grav engine block)
HUB_R = 12
OUTLINE_CELLS = 3         # keel thickness, in layout cells


def load_mask(path):
    """(mask, nrows, ncols) — True where the ship has a foundation."""
    rows = ET.parse(path).getroot().find("rows")
    mask = []
    for row in rows:
        line = []
        for cell in row:
            if cell.get("IsNull") == "True":
                line.append(False)
            else:
                fd = cell.find("foundationDef")
                line.append(fd is not None and bool(fd.text))
        mask.append(line)
    return mask, len(mask), len(mask[0])


def erode(mask, n):
    """4-connected erosion by n steps. Cells outside the grid count as empty."""
    h, w = len(mask), len(mask[0])
    cur = mask
    for _ in range(n):
        nxt = [[False] * w for _ in range(h)]
        for r in range(h):
            for c in range(w):
                if not cur[r][c]:
                    continue
                if (r > 0 and cur[r - 1][c] and r < h - 1 and cur[r + 1][c]
                        and c > 0 and cur[r][c - 1] and c < w - 1 and cur[r][c + 1]):
                    nxt[r][c] = True
        cur = nxt
    return cur


def bbox(mask):
    h, w = len(mask), len(mask[0])
    rs = [r for r in range(h) if any(mask[r])]
    cs = [c for c in range(w) if any(mask[r][c] for r in range(h))]
    return rs[0], rs[-1], cs[0], cs[-1]


def cells_to_canvas(mask):
    """Scale + offset mapping layout cells onto the supersampled canvas."""
    r0, r1, c0, c1 = bbox(mask)
    gw, gh = (c1 - c0 + 1), (r1 - r0 + 1)
    avail = BIG - 2 * MARGIN
    scale = min(avail / gw, avail / gh)
    ox = MARGIN + (avail - gw * scale) / 2.0 - c0 * scale
    oy = MARGIN + (avail - gh * scale) / 2.0 - r0 * scale
    return scale, ox, oy


def paint(img, mask, scale, ox, oy, colour_at):
    """Fill every masked cell as a rectangle; colour_at(r, c) picks the colour."""
    d = ImageDraw.Draw(img)
    h, w = len(mask), len(mask[0])
    for r in range(h):
        for c in range(w):
            if not mask[r][c]:
                continue
            col = colour_at(r, c)
            if col is None:
                continue
            x0 = ox + c * scale
            y0 = oy + r * scale
            # +1 so neighbouring cells share an edge instead of leaving a seam
            d.rectangle([x0, y0, x0 + scale + 1, y0 + scale + 1], fill=col)


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(4))


def build(mask):
    r0, r1, _, _ = bbox(mask)
    span = max(1, r1 - r0)
    inner = erode(mask, OUTLINE_CELLS)
    scale, ox, oy = cells_to_canvas(mask)

    img = Image.new("RGBA", (BIG, BIG), (0, 0, 0, 0))

    # 1. whole silhouette in the keel colour — everything else is drawn inside it
    paint(img, mask, scale, ox, oy, lambda r, c: KEEL)

    # 2. hull, top-lit: a vertical value gradient across the ship's own height
    def hull(r, c):
        return lerp(HULL_TOP, HULL_BOT, (r - r0) / span)
    paint(img, inner, scale, ox, oy, hull)

    # 3. hub plate — the visible centre that makes this read as a RING with a
    #    hub rather than as a blank washer at 64 px
    hub = [[mask[r][c] and (c - HUB_CX) ** 2 + (r - HUB_CZ) ** 2 <= HUB_R ** 2
            for c in range(len(mask[0]))] for r in range(len(mask))]
    hub_in = erode(hub, 1)
    paint(img, hub, scale, ox, oy, lambda r, c: HUB_EDGE)
    paint(img, hub_in, scale, ox, oy, lambda r, c: HUB_PLATE)

    # 4. engine core — the one bright note, ~4 cells across
    d = ImageDraw.Draw(img)
    cx = ox + (HUB_CX + 0.5) * scale
    cy = oy + (HUB_CZ + 0.5) * scale
    rr = 2.2 * scale
    d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=CORE, outline=HUB_EDGE,
              width=max(1, int(scale * 0.6)))
    return img


def downsample(img):
    """Premultiplied area downsample — plain averaging bleeds transparent black
    into the rim and leaves a dark fringe on a cutout."""
    r, g, b, a = img.split()
    af = a.convert("F")
    pm = [Image.composite(ch, Image.new("L", img.size, 0), a) for ch in (r, g, b)]
    pm = [ch.convert("F") for ch in pm]
    small_a = af.resize((FINAL, FINAL), Image.LANCZOS)
    small = [ch.resize((FINAL, FINAL), Image.LANCZOS) for ch in pm]
    out = Image.new("RGBA", (FINAL, FINAL))
    px_a = small_a.load()
    px = [ch.load() for ch in small]
    op = out.load()
    for y in range(FINAL):
        for x in range(FINAL):
            av = max(0.0, min(255.0, px_a[x, y]))
            if av <= 0.5:
                op[x, y] = (0, 0, 0, 0)
                continue
            k = 255.0 / av
            op[x, y] = tuple(
                [max(0, min(255, int(round(px[i][x, y] * k)))) for i in range(3)]
                + [int(round(av))])
    return out


def main():
    mask, h, w = load_mask(SHIP_XML)
    big = build(mask)
    # a touch of blur before the downsample kills the stair-stepping that a
    # cell-rectangle raster leaves on the ring's diagonals. Keep it small —
    # past ~0.2 cells the keel stops reading as a hard line and the whole thing
    # goes soft, which at 64 px is the difference between a ship and a smudge.
    big = big.filter(ImageFilter.GaussianBlur(SS * 0.18))
    icon = downsample(big)
    for out in (OUT_EXPANDING, OUT_CARAVAN):
        os.makedirs(os.path.dirname(out), exist_ok=True)
        icon.save(out)
        print("wrote %s  %s" % (out, icon.size))


if __name__ == "__main__":
    main()
