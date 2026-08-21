#!/usr/bin/env python3
"""Composite a generated beast pair into an Alpha Vehicles Neolithic draught vehicle.

Generalises build_eopie_sled_south.py, which is DogSled-only and stays as it is --
it carries sled-specific rigging (trace stubs drawn onto a hitch) that none of the
other four vehicles need, because their reins are already drawn ABOVE the animal
band and survive the erase untouched.

WHAT IT DOES
  1. animal = opaque(art) AND black(mask). The shipped mask is the authority on
     which pixels are draught animal: (255,0,0) tints with the vehicle colour,
     (0,0,0) does not, and only the animals are untinted.
  2. Erase those pixels, but ONLY on rows inside the band. Rows above the band are
     copied verbatim, so the cart, its wheels and its reins register against the new
     art by construction rather than by eye.
  3. Fit the generated pair to the band and composite it in UNDER the surviving art,
     so the donor's own bodywork occludes the beast exactly as it occluded the animal
     it replaces.
  4. Rebuild the mask so the new beast is untinted and everything else is unchanged.

WHY THE BAND IS A TABLE AND NOT COMPUTED
  It was measured per vehicle in Source/GEOMETRY.md section 3, and no single rule
  reproduces all four -- proven 2026-08-21 by trying:
    * a >=18-px-per-row filter gets Chariot and OxCart right and cuts the heads off
      WarChariot, whose necks are thinner than 18 px;
    * a connected-blob filter gets WarChariot and CoveredCarriage right and leaves
      the Chariot's rein attached, overstating its band by 141 rows.
  GEOMETRY.md says "do not re-measure" and it is right. These are its numbers.

WHY STRETCH AND NOT PAD
  A pad preserves the drawing and loses span. An 84%-width pad came out 17% narrow
  and validate_sprite.py rejected it: a variant may lose area but must still span
  its footprint. An 18% stretch on a top-down animal is invisible.
"""

import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

DONOR = ("/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/"
         "3028675048/Textures/Things/Vehicles/Land/Tier0")
HERE = os.path.dirname(os.path.abspath(__file__))

# x0, x1, y0, y1 inclusive -- Source/GEOMETRY.md section 3.
BANDS = {
    ("Chariot", "south"):         (210, 301, 287, 468),
    ("WarChariot", "south"):      (165, 347, 200, 457),
    ("OxCart", "south"):          (155, 356, 282, 430),
    ("CoveredCarriage", "south"): (176, 335, 268, 484),
    ("Chariot", "north"):         (209, 302, 32, 267),
    ("WarChariot", "north"):      (151, 361, 44, 276),
    ("OxCart", "north"):          (154, 357, 32, 220),
    ("CoveredCarriage", "north"): (175, 336, 36, 198),
    # ⛔ EAST IS MEASURED AND WIRED AND THE ART IS NOT SHIPPABLE. Attempted 2026-08-21
    # with the south pair turned 90 degrees CCW and it is plainly wrong, so the east
    # bands stay here as measurement, not as a build that anyone should run:
    #   * The donor's east animals are drawn in SIDE elevation -- flank, profile head,
    #     legs under the body. The south pair is a plan view of the animal's BACK. Turning
    #     a plan view does not produce an elevation, and at sprite size it reads as two
    #     beasts lying on their sides rather than one team pulling.
    #   * The donor also STAGGERS the pair front-to-back (GEOMETRY section 3: OxCart east
    #     merges over x 400-474; CoveredCarriage's trunk gap is 5-7 px; WarChariot's is
    #     2-7 px). A turned south pair stacks them flat and square, with no overlap.
    #   * OxCart is the arithmetic proof as well as the visual one: its band is 224x180
    #     (aspect 1.244) and the turned bantha pair is 0.732, so a fill costs +69.9% and a
    #     contain fit spans only 66% of the band's width.
    # ⇒ East needs purpose-generated SIDE-view pairs, one per species, exactly as the
    # DogSled needed `art/eopie_pair_gen_east.png`. It is a missing asset, not a fit bug.
    ("Chariot", "east"):          (254, 486, 191, 342),
    ("WarChariot", "east"):       (212, 494, 148, 336),
    ("OxCart", "east"):           (282, 505, 158, 337),
    ("CoveredCarriage", "east"):  (280, 506, 155, 324),
}

# Which side of the band the vehicle is on. The beast must stay welded to the hitch,
# so any slack left by an aspect fit is taken off the FAR end, never off the hitch.
HITCH = {"south": "top", "north": "bottom", "east": "left"}
FAR = {"south": "bottom", "north": "top", "east": "right"}

# How the pair is fitted to the band.
#   fill    -- stretch both axes to the band exactly. Only correct where the band's
#              aspect already matches the pair's, which is true of south and only south.
#   south   -- take the SIZE from this vehicle's SOUTH band, anchor it at the far end
#              of the north band, and let the donor's own bodywork occlude the rest.
#              The beast is then the same animal at the same scale in both facings,
#              which is the thing a player actually notices when a cart turns.
#   contain -- scale by the binding axis, keep aspect, then allow the short axis to
#              stretch by at most MAX_STRETCH to recover span. Kept for east.
#
# 🔴 WHY NORTH CANNOT USE `fill`, measured 2026-08-21. The north band is the donor's
# north BLACK REGION, and it is not the south region turned round: the donor redraws
# the animals from behind and the cart occludes them differently. Band aspects go
# south -> north as 1.356 -> 1.079 (OxCart), 0.737 -> 0.994 (CoveredCarriage),
# 0.709 -> 0.906 (WarChariot). Filling those with the south pair costs -20.9%, +40.3%
# and +42.2% of width. The item allows ~18% on a top-down animal; 40% is a different
# animal. Contain-fit costs 0% distortion and buys it back in span.
# animal. Contain-fit costs 0% distortion and buys it back in span.
#
# 🔑 AND CONTAIN IS NOT THE ANSWER EITHER, measured the same day. The north band is
# SHORTER than the south one on CoveredCarriage (163 vs 217) and WarChariot (233 vs
# 258) because the donor's own wagon and chariot are drawn OVER the animals' hindquarters
# -- the band is what is left VISIBLE, not how long the horse is. Contain-fitting to it
# shrinks the whole beast to 80% of its south width, so the vehicle's team changes size
# when it turns. Taking the size from the SOUTH band and anchoring it at the far end
# reproduces the donor's own construction: same animal, drawn at one scale, partly hidden
# by the cart. That is what `south` does, and it is why UNDER matters.
FIT = {"south": "fill", "north": "south", "east": "contain"}

# 🔴 PER-VEHICLE, AND IT CANNOT BE DERIVED FROM THE BANDS. Measured 2026-08-21.
# `north: south` is right when the north band UNDERSTATES the animal — OxCart's ox horns
# reach to y27, five rows ABOVE its black band, so filling that band shrinks the team and
# returns three REJECTs. The Chariot is the opposite: the donor genuinely draws its horse
# LONGER facing north (236 rows against south's 182), nothing occludes it, and holding it
# to the south size starves the band by 14% — all of which collects at the hitch and
# reads as the beast floating free of the cart.
# ⛔ Do NOT try to tell those apart by comparing band sizes. Both vehicles have a north
# band ~1.3x their south band's length (OxCart 189/149, Chariot 236/182); the ratio is
# almost identical and the correct answers are opposite. Tried it, it re-broke OxCart to
# -20.9%. The discriminator is whether the ANIMAL overruns its band, which only a look at
# the donor art answers — so it is written down per vehicle rather than computed.
FIT_OVERRIDE = {("Chariot", "north"): "fill"}

# The most a contain fit may stretch its short axis to recover span. 18% is the item's
# stated invisibility limit for a top-down animal; sit under it, not on it.
MAX_STRETCH = 1.12

# Facings where the donor draws bodywork OVER the animal (GEOMETRY section 2: no
# isolated hitch exists on any north, and east stacks the pair under the shafts).
UNDER = {"north": True, "east": True, "south": False}

# 🔴 NORTH MUST BE AUTHORED. It cannot be derived, and that is measured, not assumed:
# `Vehicles.Graphic_Rgb.GetTextures` does set `drawRotatedExtraAngleOffset = 180f` when
# `_north` is missing, but the vehicle BODY never reads it --
# `Graphic_Rgb.ParallelGetPreRenderResults` builds its quaternion from
# `orientation.AsRotationAngle + rotation` alone, and `AdjustAngle`'s North case is
# empty. The only readers are `CompDrawLayer.AngleFromRot` / `CompDrawLayerTurret`,
# which draw add-on layers rather than the body, and both sit behind
# `ShouldDrawRotated`. ⇒ A vehicle with no `_north` draws the SOUTH sprite UNROTATED,
# rear end pointing north, with no error and no magenta. The donor mod agrees: it ships
# `_north`, `_east`, `_south` and NO `_west` -- west is the one facing that derives.
#
# ✅ But north needs no NEW beast art. Rotating the south pair 180 degrees and dropping
# it into the donor's own north band gives the animals seen from behind, which is what
# north wants. Graded against the DogSled's hand-authored north on
# `art/review/derived_facings.png`, that read as near-indistinguishable at sprite size.
ROTATE = {"north": 180, "south": 0, "east": 90}   # east: bottom -> right

# DECIDE's ruling from measured baseBodySize. The ladder is the point; do not swap
# one beast for another without redoing the whole ladder.
BEASTS = {
    "Chariot":         ("dewback", 1),
    "WarChariot":      ("dewback", 2),
    "OxCart":          ("bantha", 2),
    "CoveredCarriage": ("ronto", 2),
}


def opaque_black(art, mask):
    """The draught animals, and nothing else."""
    return (art[..., 3] > 0) & (mask[..., 0] < 32) & (mask[..., 1] < 32) & (mask[..., 2] < 32)


# GEOMETRY.md section 1: the black region is the animal's INTERIOR fill. Its 4-6 px
# keyline is tagged RED, so erasing only the black leaves a white outline of the DONOR
# animal standing on top of ours -- an ox-shaped halo round a bantha. Measured depth to
# majority black reaches 8 px on WarChariot, so 8 px covers every facing.
DILATE = 8

# GEOMETRY.md section 1: CoveredCarriage tags its WHEEL RIMS black -- 4 blobs north,
# 6 south, 3 east, 62-364 px each. A blanket erase deletes wheel detail.
MIN_BLOB = 600


def keep_big_blobs(m, minpx=MIN_BLOB):
    """Drop connected components smaller than minpx. 4-connected, no scipy here."""
    h, w = m.shape
    lab = np.zeros((h, w), np.int32)
    out = np.zeros_like(m)
    ys, xs = np.nonzero(m)
    nxt = 0
    for sy, sx in zip(ys.tolist(), xs.tolist()):
        if lab[sy, sx]:
            continue
        nxt += 1
        stack = [(sy, sx)]
        lab[sy, sx] = nxt
        cells = []
        while stack:
            cy, cx = stack.pop()
            cells.append((cy, cx))
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < h and 0 <= nx < w and m[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = nxt
                    stack.append((ny, nx))
        if len(cells) >= minpx:
            for cy, cx in cells:
                out[cy, cx] = True
    return out


def dilate(m, r=DILATE):
    im = Image.fromarray((m * 255).astype(np.uint8), "L")
    return np.array(im.filter(ImageFilter.MaxFilter(2 * r + 1))) > 127


def trim(im):
    bb = im.getbbox()
    return im.crop(bb) if bb else im


def build(vehicle, facing, pair_path, out_path, out_mask_path):
    band = BANDS.get((vehicle, facing))
    if band is None:
        sys.exit("no band measured for %s %s -- see GEOMETRY.md section 3" % (vehicle, facing))
    x0, x1, y0, y1 = band
    bw, bh = x1 - x0 + 1, y1 - y0 + 1

    src = os.path.join(DONOR, vehicle, "AV_%s_%s.png" % (vehicle, facing))
    srcm = os.path.join(DONOR, vehicle, "AV_%s_%sm.png" % (vehicle, facing))
    art = Image.open(src).convert("RGBA")
    mask = Image.open(srcm).convert("RGBA")
    A, M = np.array(art), np.array(mask)
    H, W = A.shape[:2]

    animal = keep_big_blobs(opaque_black(A, M))

    # The erase region is the band grown by DILATE on its three FREE sides and by
    # nothing at all on the hitch side. Growing it is what takes the keyline: the band
    # is the black bbox, the keyline sits OUTSIDE it, and clipping the dilation back to
    # the band leaves a rim of donor animal standing above the new one -- visible as
    # black flecks over the bantha horns before this was fixed. Not growing it at the
    # hitch is what keeps the yoke, the traces and the shaft, which are the only things
    # holding the beast to the cart.
    hitch = HITCH[facing]
    gx0 = x0 - (0 if hitch == "left" else DILATE)
    gx1 = x1 + DILATE
    gy0 = y0 - (0 if hitch == "top" else DILATE)
    gy1 = y1 + (0 if hitch == "bottom" else DILATE)
    clip = np.zeros_like(animal)
    clip[max(gy0, 0):gy1 + 1, max(gx0, 0):gx1 + 1] = True

    erase = dilate(animal & clip) & clip
    kept_above = int((animal & ~clip).sum())

    A[erase] = (0, 0, 0, 0)

    pair = Image.open(pair_path).convert("RGBA")
    turn = ROTATE.get(facing, 0)
    if turn:
        pair = pair.rotate(turn, expand=True)
    pair = trim(pair)
    pw, ph = pair.size

    mode = FIT_OVERRIDE.get((vehicle, facing)) or FIT.get(facing, "fill")
    if mode == "fill":
        tw, th = bw, bh
    elif mode == "south":
        sx0, sx1, sy0, sy1 = BANDS[(vehicle, "south")]
        tw, th = sx1 - sx0 + 1, sy1 - sy0 + 1
        if turn in (90, 270):
            tw, th = th, tw
        # If the south beast is SHORTER than the band ALONG THE DIRECTION OF TRAVEL,
        # stretch it toward the band -- bounded by MAX_STRETCH -- rather than leaving the
        # gap at the hitch. ⚠️ Only that axis. Stretching the perpendicular one too took
        # WarChariot north from +11.4% to +24.7% and bought nothing: the far-end anchor
        # opens no lateral gap, so a wider beast is distortion with no defect to fix.
        if facing in ("north", "south"):
            if th < bh:
                th = min(bh, int(round(th * MAX_STRETCH)))
        elif tw < bw:
            tw = min(bw, int(round(tw * MAX_STRETCH)))
    else:
        s = min(bw / pw, bh / ph)                      # contain: aspect preserved
        tw, th = int(round(pw * s)), int(round(ph * s))
        tw = min(bw, int(round(tw * MAX_STRETCH)))     # buy span back, bounded
        th = min(bh, int(round(th * MAX_STRETCH)))
    # Distortion actually applied: how far the two axis scales diverge. 0% means the
    # drawing is untouched; the item's limit for an invisible one is ~18%.
    stretch = (tw / pw) / (th / ph)

    beast = pair.resize((tw, th), Image.LANCZOS)
    B = np.array(beast)

    # Slack goes to the far end. The hitch edge is load-bearing: the reins and the
    # yoke were copied verbatim and they have to meet something.
    # `south`-mode anchors at the FAR end when the beast is LONGER than the band, because
    # then the band is short precisely because the cart covers the near end -- anchor far
    # and the overhang lands under the bodywork. When the beast is SHORTER than the band
    # (OxCart north: the donor simply draws its oxen 40 px longer from behind, nothing
    # covers them) anchoring far would open a gap at the yoke, so anchor at the hitch and
    # spend the slack on the heads, where no art is lost.
    # 🔴 ALWAYS anchor `south`-mode at the FAR end, even when that opens a gap at the
    # yoke. Measured 2026-08-21: OxCart north is the one facing where the ANIMAL sets the
    # sprite's outer extent -- the donor's ox horns reach y27, five rows ABOVE the black
    # band -- so anchoring at the hitch cost 45 px of span and validate_sprite.py returned
    # three REJECTs (height -10%, aspect squashed, origin y=72 against 27). The far end is
    # what the validator measures. The gap is closed by MAX_STRETCH above, not by moving
    # the beast off the extent it has to reach.
    anchor = FAR[facing] if mode == "south" else hitch
    if anchor == "left":
        ox, oy = x0, y0 + (bh - th) // 2
    elif anchor == "right":
        ox, oy = x1 + 1 - tw, y0 + (bh - th) // 2
    elif anchor == "top":
        ox, oy = x0 + (bw - tw) // 2, y0
    else:                                              # bottom
        ox, oy = x0 + (bw - tw) // 2, y1 + 1 - th
    ox, oy = max(ox, 0), max(oy, 0)

    canvas = np.zeros((H, W, 4), np.uint8)
    ch, cw = min(th, H - oy), min(tw, W - ox)
    canvas[oy:oy + ch, ox:ox + cw] = B[:ch, :cw]
    new = (canvas[..., 3] > 0)

    if UNDER.get(facing, False):
        # North and east put cart over animal -- the carriage canvas sits on the
        # horses' rumps, the chariot pole is painted across the back. Paste only into
        # what is now transparent and the donor's own bodywork occludes the beast for
        # free, which is why those three facings have no isolated hitch at all.
        new = new & (A[..., 3] == 0)
    A[new] = canvas[new]

    # Faint fringe corrupts every later measurement. The validator rejects on it.
    faint = (A[..., 3] > 0) & (A[..., 3] < 32)
    A[faint] = (0, 0, 0, 0)

    M[new] = (0, 0, 0, 255)                    # the new beast does not tint
    M[erase & ~new] = (255, 0, 0, 255)         # anything we emptied tints if refilled

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    Image.fromarray(A).save(out_path)
    Image.fromarray(M).save(out_mask_path)

    ys, xs = np.nonzero(A[..., 3] > 0)
    print("  %s %s" % (vehicle, facing))
    print("    band       %dx%d at (%d,%d)" % (bw, bh, x0, y0))
    print("    erased     %6d px of donor animal   kept outside clip: %d" % (int(erase.sum()), kept_above))
    print("    pair       %dx%d -> %dx%d at (%d,%d)   distortion %+.1f%%   band span %d%%x%d%%"
          % (pw, ph, tw, th, ox, oy, (stretch - 1) * 100,
             round(100 * tw / bw), round(100 * th / bh)))
    print("    faint      %6d px cleared (alpha 1-31)" % int(faint.sum()))
    print("    subject    bbox (%d,%d,%d,%d)" % (xs.min(), ys.min(), xs.max(), ys.max()))
    print("    wrote      %s" % os.path.normpath(out_path))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("vehicle", choices=sorted(BEASTS))
    p.add_argument("--facing", default="south")
    p.add_argument("--pair")
    p.add_argument("--out")
    a = p.parse_args()

    beast, _n = BEASTS[a.vehicle]
    pair = a.pair or os.path.join(HERE, "art", "%s_pair_gen_south.png" % beast)
    out = a.out or os.path.join(
        HERE, "..", "Textures", "Things", "Vehicles", "Land", "Tier0",
        a.vehicle, "AV_%s_%s.png" % (a.vehicle, a.facing))
    build(a.vehicle, a.facing, pair, out, out.replace(".png", "m.png"))


if __name__ == "__main__":
    main()
