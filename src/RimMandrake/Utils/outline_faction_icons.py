#!/usr/bin/env python3
"""outline_faction_icons.py — put a black outline on a world-map faction icon.

WHY
===
🔴 Owner, 2026-08-23: the faction icons on the world map "are indeed quite hard to
see". They are white/grey silhouettes on a 128x128 canvas, and RimWorld draws them
over a planet surface whose colour we do not control.

🔑 THE OUTLINE SURVIVES THE TINT, AND THAT IS WHY BLACK IS THE RIGHT COLOUR.
`ExpandableWorldObjectsUtility.ExpandableWorldObjectsOnGUI` sets
`GUI.color = worldObject.ExpandingIconColor` and, for a settlement, that resolves to
the FACTION's colour (`WorldObject.ExpandingIconColor` -> `def.expandingIconColor ??
Material.color`). GUI.color MULTIPLIES, and it dims further at low zoom
(`expandingIconColor.r *= num2` at lines 157-159). Black multiplied by anything is
still black, so the outline reads identically for every faction at every zoom, while
the body of the icon keeps taking the faction's colour. ⛔ A white or grey outline
would be tinted along with the glyph and would vanish against a same-hued map.

⚠️ THE CANVAS IS FIXED AT 128x128, SO THE OUTLINE HAS TO BE PAID FOR.
Measured before the change: all thirteen icons had only 5-6 px of clear margin, so a
7 px ring drawn outward would have clipped on the canvas edge. Instead the GLYPH is
scaled down about its own bounding-box centre by exactly enough that
`glyph + 2 * outline` lands back inside the original bounding box.

⇒ **The silhouette the player sees is the same size it was before.** The icon does
not grow, does not move, and does not touch an edge it did not touch before — the
ring is carved out of the glyph, not added around it. That is what keeps
`validate_sprite.py`'s footprint, origin and canvas-contact checks meaningful; if the
ring were added outward, every icon would report an overrun and the checks would have
to be waived, which is how a real clipping bug would then get through.

⚠️ RESIZE IS PREMULTIPLIED. Averaging straight RGBA across a cutout edge pulls the
transparent pixels' RGB into the visible rim and leaves a dark halo — the same defect
the sprite skill warns about. Premultiplying before the resize and un-premultiplying
after is the fix, and it is why this does not just call `Image.resize`.

USAGE
=====
    python3 src/RimMandrake/Utils/outline_faction_icons.py            # plan only
    python3 src/RimMandrake/Utils/outline_faction_icons.py --apply
    python3 src/RimMandrake/Utils/outline_faction_icons.py --apply --width 9

⚠️ Writing the repo copy is not deploying it. The game reads
`C:\\Program Files (x86)\\Steam\\steamapps\\common\\RimWorld\\Mods`, and a TEXTURE is
read once at startup — a running game will not pick this up. Deploy with
`deploy_custom_mods.py --mod Jawa_Patches --apply`, then the icons change on the next
load.

🔑 RE-RUNNING THIS IS SAFE AND IS *NOT* IDEMPOTENT-BY-LUCK — it refuses. An icon that
already carries a ring would get a second ring carved out of the first, shrinking the
glyph again every run. `already_outlined()` detects the ring and skips, so the guard
is the tool's, not the operator's memory.
"""

import argparse
import os
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow is required:  python3 -m pip install --user Pillow")

ICON_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "..", "Jawa", "Jawa_Patches",
                        "Textures", "World", "JawaFactions")

# 7 px on a 128 px canvas is 5.5% of the icon's width. Expandable world objects draw
# at roughly a third of the source resolution at default zoom, so this lands near
# 2 px of visible black on screen - thick enough to separate the glyph from a biome
# fill, thin enough that the glyph is still the thing you read.
DEFAULT_WIDTH = 7

# Anything at or below this alpha is treated as absent. The sprite validator rejects a
# "faint fringe" of alpha 1-31 because those pixels are invisible but still corrupt
# every bounding-box and coverage measurement, so the same floor is used here.
ALPHA_FLOOR = 8


def load(path):
    return Image.open(path).convert("RGBA")


def mask_bbox(img, floor=ALPHA_FLOOR):
    """Bounding box of everything meaningfully opaque. None for an empty image."""
    a = img.getchannel("A").point(lambda v: 255 if v > floor else 0)
    return a.getbbox()


def resize_rgba(img, size):
    """Premultiplied LANCZOS resize. See the module docstring on the dark halo."""
    r, g, b, a = img.split()
    pr = Image.new("L", img.size)
    pg = Image.new("L", img.size)
    pb = Image.new("L", img.size)
    rp, gp, bp, ap = r.load(), g.load(), b.load(), a.load()
    orr, org, orb = pr.load(), pg.load(), pb.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            al = ap[x, y]
            orr[x, y] = rp[x, y] * al // 255
            org[x, y] = gp[x, y] * al // 255
            orb[x, y] = bp[x, y] * al // 255
    pre = Image.merge("RGBA", (pr, pg, pb, a)).resize(size, Image.LANCZOS)
    r2, g2, b2, a2 = pre.split()
    rl, gl, bl, al2 = r2.load(), g2.load(), b2.load(), a2.load()
    w2, h2 = size
    for y in range(h2):
        for x in range(w2):
            av = al2[x, y]
            if av == 0:
                rl[x, y] = gl[x, y] = bl[x, y] = 0
            else:
                rl[x, y] = min(255, rl[x, y] * 255 // av)
                gl[x, y] = min(255, gl[x, y] * 255 // av)
                bl[x, y] = min(255, bl[x, y] * 255 // av)
    return Image.merge("RGBA", (r2, g2, b2, a2))


def dilate_max(alpha, radius):
    """Disc dilation done as a true per-pixel max. Clear, and fast enough at 128px."""
    w, h = alpha.size
    src = alpha.load()
    out = Image.new("L", (w, h), 0)
    dst = out.load()
    offsets = [(dx, dy)
               for dy in range(-radius, radius + 1)
               for dx in range(-radius, radius + 1)
               if dx * dx + dy * dy <= radius * radius]
    for y in range(h):
        for x in range(w):
            best = 0
            for dx, dy in offsets:
                sx, sy = x + dx, y + dy
                if 0 <= sx < w and 0 <= sy < h:
                    v = src[sx, sy]
                    if v > best:
                        best = v
                        if best == 255:
                            break
            dst[x, y] = best
    return out


def already_outlined(img, width):
    """True if the outer `width` band of the silhouette is already near-black.

    🔑 This is the re-run guard, and it is measured rather than remembered: a second
    pass would carve a second ring out of the first and shrink the glyph again. It
    samples the ring the tool would REPLACE, so it cannot be fooled by an icon that
    merely happens to contain black somewhere.
    """
    if not mask_bbox(img):
        return False
    a = img.getchannel("A")
    # the band = solid pixels within `width` of the outside, found by dilating the
    # TRANSPARENT region inward and intersecting it with the solid region
    eroded = dilate_max(a.point(lambda v: 255 if v <= ALPHA_FLOOR else 0), width)
    px = img.load()
    ep = eroded.load()
    ap = a.load()
    band, dark = 0, 0
    w, h = img.size
    for y in range(h):
        for x in range(w):
            if ap[x, y] > 128 and ep[x, y] > 128:
                band += 1
                r, g, b, _ = px[x, y]
                if max(r, g, b) < 64:
                    dark += 1
    return band > 0 and dark * 100 // band >= 80


def outline(img, width):
    """Return a new RGBA with the glyph shrunk and a black ring in the space freed."""
    bb = mask_bbox(img)
    if not bb:
        return None, "empty alpha - nothing to outline"
    W, H = img.size
    x0, y0, x1, y1 = bb
    span_x, span_y = x1 - x0, y1 - y0

    # Shrink the glyph so glyph + 2*width lands back inside the ORIGINAL bbox. This
    # is what keeps the finished silhouette exactly the size it was.
    tx, ty = span_x - 2 * width, span_y - 2 * width
    if tx < 8 or ty < 8:
        return None, "glyph too small to carve a %d px ring out of" % width
    scale = min(tx / span_x, ty / span_y)
    nw, nh = max(1, round(span_x * scale)), max(1, round(span_y * scale))

    glyph = resize_rgba(img.crop(bb), (nw, nh))

    # Register on the ORIGINAL bbox centre so the icon does not drift.
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    ox, oy = int(round(cx - nw / 2.0)), int(round(cy - nh / 2.0))

    placed = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    placed.paste(glyph, (ox, oy))

    ring_alpha = dilate_max(placed.getchannel("A"), width)
    ring = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ring.putalpha(ring_alpha)          # pure black, ring_alpha coverage

    out = Image.alpha_composite(ring, placed)

    # Kill the invisible fringe the validator rejects: alpha 1..ALPHA_FLOOR is
    # unreadable on screen and poisons every later measurement of this file.
    a = out.getchannel("A").point(lambda v: 0 if v <= ALPHA_FLOOR else v)
    out.putalpha(a)
    return out, None


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", default=os.path.normpath(ICON_DIR))
    ap.add_argument("--width", type=int, default=DEFAULT_WIDTH,
                    help="ring thickness in source px on the 128 px canvas "
                         "(default %d)" % DEFAULT_WIDTH)
    ap.add_argument("--apply", action="store_true",
                    help="write the PNGs; without this it only prints the plan")
    ap.add_argument("--force", action="store_true",
                    help="outline again even if a ring is already detected. "
                         "⛔ This shrinks the glyph a second time - it is for a "
                         "deliberate width change after a `git checkout` of the "
                         "originals, never for a re-run.")
    ap.add_argument("--only", action="append", default=[],
                    help="basename without .png, repeatable")
    a = ap.parse_args()

    names = sorted(f for f in os.listdir(a.dir) if f.lower().endswith(".png"))
    if a.only:
        want = {n.lower() for n in a.only}
        names = [f for f in names if os.path.splitext(f)[0].lower() in want]
    if not names:
        sys.exit("no PNGs matched under %s" % a.dir)

    print("%-26s %-11s %-11s %s" % ("icon", "bbox span", "silhouette", "note"))
    print("-" * 78)
    wrote = skipped = failed = 0
    for f in names:
        p = os.path.join(a.dir, f)
        img = load(p)
        bb = mask_bbox(img)
        before = "%dx%d" % (bb[2] - bb[0], bb[3] - bb[1]) if bb else "-"
        if already_outlined(img, a.width) and not a.force:
            print("%-26s %-11s %-11s SKIP - already outlined" % (f, before, "-"))
            skipped += 1
            continue
        out, err = outline(img, a.width)
        if err:
            print("%-26s %-11s %-11s FAILED - %s" % (f, before, "-", err))
            failed += 1
            continue
        nb = mask_bbox(out)
        after = "%dx%d" % (nb[2] - nb[0], nb[3] - nb[1]) if nb else "-"
        grew = nb and bb and (nb[2] - nb[0] > bb[2] - bb[0] or
                              nb[3] - nb[1] > bb[3] - bb[1])
        note = "ring %d px" % a.width
        if grew:
            note += "  ⚠️ SILHOUETTE GREW - would clip"
        if a.apply:
            out.save(p)
            note += "  written"
            wrote += 1
        print("%-26s %-11s %-11s %s" % (f, before, after, note))

    print("-" * 78)
    if not a.apply:
        print("PLAN ONLY - nothing written. Re-run with --apply.")
    else:
        print("wrote %d, skipped %d, failed %d" % (wrote, skipped, failed))
        print("⚠️ The repo is not the game. Deploy, then it takes effect on the NEXT "
              "load:\n   python3 src/RimMandrake/Utils/deploy_custom_mods.py "
              "--mod Jawa_Patches --apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
