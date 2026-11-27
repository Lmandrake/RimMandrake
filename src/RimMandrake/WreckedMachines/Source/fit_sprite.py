#!/usr/bin/env python3
"""
fit_sprite.py — conform generated art to a reference sprite's canvas and pose.

THE PROBLEM
===========
Image models do not respect a canvas spec. Ask for 640x512 and you get
1536x1024; ask for transparency and you get a black background. But the *art*
is often fine — on the Automated Smelter pilot the generated machines came back
with silhouette aspect ratios of 1.329 and 1.333 against the source's 1.328,
i.e. correct to a quarter of a percent. Only the packaging was wrong.

Packaging is arithmetic. This tool does the arithmetic, so the art director
never has to fight a text prompt about pixel dimensions again.

WHAT IT DOES, IN ORDER
======================
  1. **Restore alpha** if the image is fully opaque. Flood-fills inward from the
     canvas edge over background-coloured pixels, at a tolerance derived from
     the border itself rather than a guess, so interior darks survive. On the
     pilot's wrecked smelter that auto-tolerance came out at 3 and removed
     32.4% of the canvas.
  2. **Seal.** Morphologically close what the flood leaked through. Necessary,
     not optional: that smelter's own crevices are true black and physically
     connected to a true-black background, so no threshold can separate them —
     sealing reclaimed 4,103 px the flood had wrongly eaten.
  3. **Despeckle.** Drops islands far smaller than the main subject, because a
     single stray pixel of halo ruins every bounding-box measurement.
  4. **Trim** to the true silhouette.
  5. **Coarse fit** — scale so the silhouette matches the reference's measured
     silhouette, preserving aspect. One exception (choose_stretch): when the
     silhouette's aspect is 5% to 12% off the donor's AND the two-factor fit
     raises the registration overlap by at least 0.03 IoU, x and y are scaled
     by different factors so width and height both match. That case is the
     model drawing the whole machine in the wrong proportions; outside it the
     fit is one factor, as before, and the output says why.
  6. **Register** — searches scale and offset to maximise mask overlap (IoU)
     with the reference. This is the part a naive centre-and-scale gets wrong:
     damaged art is *missing chunks*, so its bounding box is not its centre of
     mass, and bbox-centring alone drifts the machine off its footprint.
  7. **Compose** onto the reference's exact canvas with premultiplied,
     area-averaged resampling, so the downscale stays sharp and no dark fringe
     appears at the cut edge.
  8. **Rim.** Every donor measured is drawn with a dark rim (edge luminance
     median 0). When step 1 keyed a black background it took that rim too, so
     registration compares the candidate with the donor keyed the same way,
     and the rim is then given back from the donor, only inside the donor's
     outline. On a thin-limbed sprite (the emanator) this is the difference
     between a fit 10% too large that spills out of its outline and a pass.

It refuses rather than guesses. Every failure names the measured number that
caused it.

USAGE
  python Source/fit_sprite.py AutomatedSmelter --tier wrecked            # dry run
  python Source/fit_sprite.py AutomatedSmelter --tier wrecked --apply
  python Source/fit_sprite.py AutomatedSmelter --all-tiers --apply
  python Source/fit_sprite.py AutomatedSmelter --tier kludged --facing east --apply

Originals are never destroyed: `--apply` moves the incoming file to
`<tier>/_raw/` and writes the conformed sprite in its place, so
`check_sprite.py` validates the conformed one and the raw stays recoverable.
"""

import argparse
import json
import os
import shutil
import sys
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pnglib import read_png, write_rgba, resize_rgba, PngError      # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
MOD_ROOT = os.path.dirname(HERE)
ART_SOURCE = os.environ.get("WM_ART_ROOT") or os.path.join(MOD_ROOT, "art_source")

ALPHA_THRESHOLD = 32        # what counts as "drawn" when measuring a silhouette
KEY_TOLERANCE = 28          # luminance at/below which an edge pixel reads as background
SPECK_FRACTION = 0.02       # islands smaller than this fraction of the biggest are noise
REG_LONG_EDGE = 128         # registration works on a mask this big; full res is far too slow
REG_SCALES = [0.88 + 0.02 * i for i in range(13)]   # 0.88 .. 1.12
REG_SHIFT = 10              # +/- this many low-res pixels
MAX_ASPECT_SKEW = 1.35      # refuse beyond this ratio; the shape is simply wrong
CLOSE_RADIUS = 6            # seal background channels narrower than this after keying
# Stretch (choose_stretch). Measured 2026-11-27 over 135 raws in the work folder (bbox skew as this file sees it,
# coarse IoU at one factor and at the full stretch):
#  - the two pictures that failed for proportions: refinery kludged south +7.35%, oven kludged south -9.52% (their
#    other tries +7.88/+8.62% and -8.60%); IoU gain from the stretch +0.043 .. +0.087.
#  - judged pictures in place: largest |skew| AmmoPress wrecked N -6.28% (gain +0.038), Cannery wrecked N -5.31%
#    (+0.040), refinery kludged E +5.46% (+0.018, top pipe torn off), refinery wrecked E +4.64% (+0.013, same);
#    below 4% the gain is at noise level (128 vs 256 px registration differ by up to 0.015).
STRETCH_MIN_SKEW = 1.05     # under 5% the box differences are damage and noise, not proportion
STRETCH_MAX_SKEW = 1.12     # the worst failure reads 10.53% in this file's own --inside line (9.52% above, measured
                            # without --inside); a larger stretch deforms round tanks visibly
STRETCH_MIN_GAIN = 0.03     # part differences gained <= 0.018, proportion errors >= 0.036
STRETCH_ON = True           # --no-stretch: one factor always, to reproduce a picture fitted before 2026-11-27
TIERS = ("wrecked", "kludged")   # default when a MANIFEST names no tiers


class FitError(Exception):
    """Raised with a precise, measured reason. Never a vague failure."""


# ----------------------------------------------------------------- mask helpers
def build_mask(w, h, rgba, thr=ALPHA_THRESHOLD):
    return bytearray(1 if rgba[i * 4 + 3] > thr else 0 for i in range(w * h))


def mask_bbox(mask, w, h):
    x0 = y0 = 1 << 30
    x1 = y1 = -1
    for y in range(h):
        row = y * w
        for x in range(w):
            if mask[row + x]:
                if x < x0: x0 = x
                if x > x1: x1 = x
                if y < y0: y0 = y
                if y > y1: y1 = y
    if x1 < 0:
        raise FitError("image has no drawn pixels above alpha %d" % ALPHA_THRESHOLD)
    return x0, y0, x1, y1


def border_stats(w, h, rgba):
    """Luminance distribution around the canvas edge — used to size the key."""
    lum = lambda i: (rgba[i * 4] * 299 + rgba[i * 4 + 1] * 587 + rgba[i * 4 + 2] * 114) // 1000
    vals = []
    for x in range(w):
        for y in (0, h - 1):
            vals.append(lum(y * w + x))
    for y in range(h):
        for x in (0, w - 1):
            vals.append(lum(y * w + x))
    vals.sort()
    n = len(vals)
    return {"median": vals[n // 2], "p95": vals[int(n * 0.95)],
            "p99": vals[int(n * 0.99)], "max": vals[-1]}


def key_background(w, h, rgba, tol=None):
    """Flood transparent inward from the canvas edge over background pixels.

    Connectivity is half the trick. A plain "make dark pixels transparent"
    threshold punches holes through every shadow inside the machine; flooding
    from the border only removes darkness actually *connected to the outside*,
    which is what "background" means.

    Choosing the threshold is the other half, and a fixed one is wrong. The
    pilot's wrecked smelter sits on pure black — 524k pixels at luminance 0,
    border median 0, p95 of 1 — while the machine's own rust ramps smoothly up
    from 1 with ~13k pixels at every level. A hardcoded tolerance of 28 was
    fourteen times too generous: the flood walked up that ramp, through the
    crevices and into the machine, and came out the far side. The result passed
    every numeric check and was visibly full of holes.

    So the tolerance is derived from the border itself: whatever the frame is
    made of, plus a small margin. If the border is not uniform, that is a
    different problem and it says so instead of guessing.
    """
    lum = lambda i: (rgba[i * 4] * 299 + rgba[i * 4 + 1] * 587 + rgba[i * 4 + 2] * 114) // 1000
    stats = border_stats(w, h, rgba)
    if tol is None:
        if stats["p99"] > 90:
            raise FitError("the canvas border is not a flat background "
                           "(edge luminance median %d, p99 %d, max %d) — there is "
                           "no background to key out. Re-generate with a "
                           "transparent or flat black background."
                           % (stats["median"], stats["p99"], stats["max"]))
        tol = min(40, max(2, stats["p95"] + 2))
    seen = bytearray(w * h)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            i = y * w + x
            if not seen[i] and lum(i) <= tol:
                seen[i] = 1; q.append(i)
    for y in range(h):
        for x in (0, w - 1):
            i = y * w + x
            if not seen[i] and lum(i) <= tol:
                seen[i] = 1; q.append(i)
    removed = 0
    while q:
        i = q.popleft()
        removed += 1
        x, y = i % w, i // w
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < w and 0 <= ny < h:
                j = ny * w + nx
                if not seen[j] and lum(j) <= tol:
                    seen[j] = 1; q.append(j)
    out = bytearray(rgba)
    for i in range(w * h):
        if seen[i]:
            out[i * 4 + 3] = 0
    return out, removed, tol, stats


def _bits_from_mask(mask, w, h, pad_w, pad):
    v = 0
    for y in range(h):
        row = mask[y * w:(y + 1) * w]
        if not any(row):
            continue
        r = 0
        for x in range(w - 1, -1, -1):
            r = (r << 1) | row[x]
        v |= r << ((pad + y) * pad_w + pad)
    return v


def _dilate(bits, pad_w, r):
    out = bits
    for k in range(1, r + 1):                       # horizontal
        out |= (bits << k) | (bits >> k)
    h_out = out
    for k in range(1, r + 1):                       # vertical
        out |= (h_out << (k * pad_w)) | (h_out >> (k * pad_w))
    return out


def close_alpha(w, h, rgba, radius):
    """Morphologically close the opaque mask, then restore what it seals.

    THE PROBLEM THIS SOLVES, WHICH NO THRESHOLD CAN
    ===============================================
    The pilot's wrecked smelter has true-black crevices *inside* the machine
    that touch the true-black background through gaps a few pixels wide. Those
    pixels are not merely similar to the background — they are the identical
    value, luminance 0, and connected to it. Every flood fill therefore leaks
    through them by construction, and lowering the tolerance cannot help
    because there is no tolerance below zero.

    Closing (dilate, then erode) seals channels narrower than the radius while
    leaving the outer silhouette where it was. Anything the closed mask
    reclaims gets its original colour back.

    Done with big-integer bitmasks: a dilation is a handful of shifts and ORs
    over the whole image at once, where a per-pixel neighbourhood scan at this
    radius would be a quarter of a billion operations in pure Python.
    """
    pad = radius + 2
    pad_w = w + 2 * pad
    pad_h = h + 2 * pad
    opaque = bytearray(1 if rgba[i * 4 + 3] > 0 else 0 for i in range(w * h))
    bits = _bits_from_mask(opaque, w, h, pad_w, pad)
    universe = _bits_from_mask(bytearray(b"\x01" * (w * h)), w, h, pad_w, pad)

    dil = _dilate(bits, pad_w, radius)
    # erode(X) == complement(dilate(complement(X))), restricted to the universe
    ero = universe & ~_dilate(universe & ~dil, pad_w, radius)
    closed = ero | bits                              # never lose original coverage

    reclaimed = 0
    out = bytearray(rgba)
    for y in range(h):
        base = (pad + y) * pad_w + pad
        for x in range(w):
            i = y * w + x
            if not opaque[i] and (closed >> (base + x)) & 1:
                out[i * 4 + 3] = 255
                reclaimed += 1
    return out, reclaimed


def donor_rim(w, h, rgba, tol):
    """How deep the donor's dark rim is, in donor pixels, and its typical alpha.

    Every donor measured so far is drawn with a dark rim: its edge pixels have
    median luminance 0 (emanator, power cell, component icon, crematorium; see
    MACHINES.md). When the model returns an opaque black background, keying
    cannot tell that rim from the background (both are luminance 0) and eats
    it. On a thin-limbed sprite the rim is a large share of the drawing (13% of
    the emanator), the eaten silhouette is too thin, and registration scales
    it up 10% to compensate, so the fitted picture spills out of its outline.

    The depth is read along every row and column: from each end, how many
    drawn pixels in a row are dark (luminance <= tol). The median of those
    runs is the rim depth. Returns (depth, median alpha of the rim pixels).
    """
    lum = lambda i: (rgba[i * 4] * 299 + rgba[i * 4 + 1] * 587 + rgba[i * 4 + 2] * 114) // 1000
    drawn = lambda i: rgba[i * 4 + 3] >= ALPHA_THRESHOLD
    runs, alphas = [], []

    def walk(idx):
        k = 0
        while k < len(idx) and not drawn(idx[k]):
            k += 1
        if k == len(idx):
            return                                  # nothing drawn on this line
        n = 0
        while k < len(idx) and drawn(idx[k]) and lum(idx[k]) <= tol:
            alphas.append(rgba[idx[k] * 4 + 3])
            n += 1; k += 1
        runs.append(n)
    for y in range(h):
        row = [y * w + x for x in range(w)]
        walk(row); walk(row[::-1])
    for x in range(w):
        col = [y * w + x for y in range(h)]
        walk(col); walk(col[::-1])
    if not runs:
        return 0, 255
    runs.sort(); alphas.sort()
    return runs[len(runs) // 2], (alphas[len(alphas) // 2] if alphas else 255)


def restore_rim(w, h, out, donor, depth, tol):
    """Give back the dark rim that keying took, in place, at donor resolution.

    A pixel is given back only when the DONOR has a dark (luminance <= tol)
    drawn pixel there, the fitted picture has nothing there, and it lies within
    `depth` px of the fitted picture. So the rim returns along the machine's
    edge and along any break, and nothing is ever drawn outside the donor's
    outline. The pixel takes the donor's own colour and alpha."""
    if depth <= 0:
        return 0
    lum = lambda a, i: (a[i * 4] * 299 + a[i * 4 + 1] * 587 + a[i * 4 + 2] * 114) // 1000
    pad = depth + 2
    pad_w = w + 2 * pad
    drawn = bytearray(1 if out[i * 4 + 3] >= ALPHA_THRESHOLD else 0 for i in range(w * h))
    near = _dilate(_bits_from_mask(drawn, w, h, pad_w, pad), pad_w, depth)
    added = 0
    for y in range(h):
        base = (pad + y) * pad_w + pad
        for x in range(w):
            i = y * w + x
            if (not drawn[i] and donor[i * 4 + 3] >= ALPHA_THRESHOLD
                    and lum(donor, i) <= tol and (near >> (base + x)) & 1):
                out[i * 4:i * 4 + 4] = donor[i * 4:i * 4 + 4]
                added += 1
    return added


def core_span(mask, w, h, frac=0.90):
    """Bounding box holding the central `frac` of drawn mass.

    The plain bounding box is dominated by whatever sticks out furthest, so a
    single trailing cable makes a machine measure as if it were that wide. This
    ignores thin appendages and reports the body.
    """
    cols = [0] * w
    rows = [0] * h
    tot = 0
    for y in range(h):
        base = y * w
        for x in range(w):
            if mask[base + x]:
                cols[x] += 1; rows[y] += 1; tot += 1
    if not tot:
        raise FitError("no drawn pixels")
    cut = tot * (1 - frac) / 2.0

    def span(v):
        acc = 0; lo = 0; hi = len(v) - 1
        for i, n in enumerate(v):
            acc += n
            if acc >= cut:
                lo = i; break
        acc = 0
        for i in range(len(v) - 1, -1, -1):
            acc += v[i]
            if acc >= cut:
                hi = i; break
        return lo, hi
    x0, x1 = span(cols); y0, y1 = span(rows)
    return x1 - x0 + 1, y1 - y0 + 1, tot


def appendage_load(mask, w, h):
    """How much of the drawing is thin stuff outside the body, as a fraction.

    RimWorld buildings own a fixed block of tiles. Anything drawn beyond the
    body overlaps the neighbours' tiles — and because this tool scales art to
    the reference footprint, every projecting cable also shrinks the machine
    itself to make room. On the pilot's first wrecked smelter that cost the
    core body 7% of its height.
    """
    bw, bh, tot = core_span(mask, w, h)
    inside = 0
    # count mass within the core box
    cols = [0] * w
    x0 = y0 = None
    # recompute the box corners the same way core_span did
    colsum = [0] * w; rowsum = [0] * h; t = 0
    for y in range(h):
        base = y * w
        for x in range(w):
            if mask[base + x]:
                colsum[x] += 1; rowsum[y] += 1; t += 1
    cut = t * 0.05

    def span(v):
        acc = 0; lo = 0; hi = len(v) - 1
        for i, n in enumerate(v):
            acc += n
            if acc >= cut:
                lo = i; break
        acc = 0
        for i in range(len(v) - 1, -1, -1):
            acc += v[i]
            if acc >= cut:
                hi = i; break
        return lo, hi
    cx0, cx1 = span(colsum); cy0, cy1 = span(rowsum)
    for y in range(cy0, cy1 + 1):
        base = y * w
        for x in range(cx0, cx1 + 1):
            if mask[base + x]:
                inside += 1
    return (bw, bh), 1.0 - inside / float(tot)


def despeckle(mask, w, h, frac=SPECK_FRACTION):
    """Keep only islands >= frac of the largest. Halo dust destroys bboxes."""
    label = [0] * (w * h)
    sizes = [0]
    cur = 0
    for start in range(w * h):
        if not mask[start] or label[start]:
            continue
        cur += 1
        n = 0
        q = deque([start]); label[start] = cur
        while q:
            i = q.popleft(); n += 1
            x, y = i % w, i // w
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if 0 <= nx < w and 0 <= ny < h:
                    j = ny * w + nx
                    if mask[j] and not label[j]:
                        label[j] = cur; q.append(j)
        sizes.append(n)
    if cur <= 1:
        return mask, 0
    biggest = max(sizes)
    keep = {i for i, s in enumerate(sizes) if i and s >= biggest * frac}
    dropped = 0
    out = bytearray(mask)
    for i in range(w * h):
        if mask[i] and label[i] not in keep:
            out[i] = 0; dropped += 1
    return out, dropped


# ------------------------------------------------------------------ registration
def mask_to_bits(mask, w, h, pad_w, ox, oy):
    """Pack a mask into one big int, positioned at (ox, oy) in a padded grid.

    Using a Python int as the bitmap makes translation a shift and overlap a
    single AND + `bit_count()`. That is what makes an exhaustive scale/offset
    search affordable in pure Python — thousands of candidate poses evaluate in
    well under a second, where a nested-loop pixel compare would take minutes.
    """
    v = 0
    for y in range(h):
        row = mask[y * w:(y + 1) * w]
        if not any(row):
            continue
        r = 0
        for x in range(w - 1, -1, -1):
            r = (r << 1) | row[x]
        v |= r << ((oy + y) * pad_w + ox)
    return v


def axis_fits(tgt_w, tgt_h, cw, ch, aspect):
    """The (x, y) scale factors that fit a cw x ch silhouette into the donor's
    tgt_w x tgt_h box, the x factor being `aspect` times the y factor. Aspect
    1.0 is the one-factor fit (the long axis fits, the other comes out short);
    aspect (tgt_w/tgt_h)/(cw/ch) makes both axes fit (see choose_stretch). At
    aspect 1.0 both values are exactly the old min(tgt_w/cw, tgt_h/ch)."""
    fy = min(tgt_w / (cw * aspect), tgt_h / float(ch))
    return fy * aspect, fy


def register(cand_rgba, cw, ch, src_mask, sw, sh, src_box, scales=None, aspect=1.0):
    """Find the (scale, dx, dy) placing the candidate best over the reference.

    Returns a rectangle in reference-canvas coordinates plus the achieved IoU.
    `aspect` is the x-to-y factor ratio (1.0: one factor for both axes).
    """
    # Work small. Registration accuracy beyond a pixel at this size is noise.
    k = REG_LONG_EDGE / float(max(sw, sh))
    lw, lh = max(1, int(sw * k)), max(1, int(sh * k))
    pad = REG_SHIFT + 4
    pad_w = lw + 2 * pad

    low_src = bytearray(lw * lh)
    for y in range(lh):
        sy = min(sh - 1, int(y / k))
        for x in range(lw):
            low_src[y * lw + x] = src_mask[sy * sw + min(sw - 1, int(x / k))]
    src_bits = mask_to_bits(low_src, lw, lh, pad_w, pad, pad)
    src_pop = src_bits.bit_count()

    sx0, sy0, sx1, sy1 = src_box
    tgt_w, tgt_h = sx1 - sx0 + 1, sy1 - sy0 + 1

    best = None
    fx0, fy0 = axis_fits(tgt_w, tgt_h, cw, ch, aspect)
    for s in (scales or REG_SCALES):
        # candidate silhouette scaled to `s` of the reference silhouette box
        fit = (fx0 * s, fy0 * s)
        nw, nh = max(1, int(round(cw * fit[0] * k))), max(1, int(round(ch * fit[1] * k)))
        if nw > lw + 2 * pad or nh > lh + 2 * pad:
            continue
        low_c = bytearray(nw * nh)
        for y in range(nh):
            sy = min(ch - 1, y * ch // nh)
            for x in range(nw):
                low_c[y * nw + x] = 1 if cand_rgba[(sy * cw + min(cw - 1, x * cw // nw)) * 4 + 3] > ALPHA_THRESHOLD else 0
        # base position: centre the candidate on the reference silhouette centre
        bx = int(round((sx0 + sx1) / 2.0 * k - nw / 2.0)) + pad
        by = int(round((sy0 + sy1) / 2.0 * k - nh / 2.0)) + pad
        if bx < 0 or by < 0:
            continue
        cand_bits = mask_to_bits(low_c, nw, nh, pad_w, bx, by)
        cand_pop = cand_bits.bit_count()
        if not cand_pop:
            continue
        for dy in range(-REG_SHIFT, REG_SHIFT + 1):
            shift = dy * pad_w
            for dx in range(-REG_SHIFT, REG_SHIFT + 1):
                t = shift + dx
                moved = cand_bits << t if t >= 0 else cand_bits >> -t
                inter = (moved & src_bits).bit_count()
                if not inter:
                    continue
                iou = inter / float(src_pop + cand_pop - inter)
                if best is None or iou > best[0]:
                    best = (iou, s, fit, dx, dy, nw, nh, bx, by)
    if best is None:
        raise FitError("could not overlap the reference silhouette at any tested "
                       "scale or offset — the shapes are unrelated")
    iou, s, fit, dx, dy, nw, nh, bx, by = best
    # translate the low-res solution back to full reference-canvas pixels
    out_w = max(1, int(round(cw * fit[0])))
    out_h = max(1, int(round(ch * fit[1])))
    out_x = int(round((bx - pad + dx) / k))
    out_y = int(round((by - pad + dy) / k))
    return {"iou": iou, "scale_of_fit": s, "rect": (out_x, out_y, out_w, out_h)}


def _check_bar():
    """check_sprite.py's outline bar, loaded by path (a plain import could
    find the general Utils/check_sprite.py first), so the fitter and the check
    can never disagree about it."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "wm_check_sprite", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "check_sprite.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def placed_outside_pct(crop, tw, th, rect, grown, sw, sh):
    """Share (%) of the candidate's drawn px that land outside `grown` (the
    donor's drawn px grown by the check's OUTLINE_GROW_PX) when placed at rect."""
    ox, oy, ow, oh = rect
    drawn = out = 0
    for y in range(oh):
        sy = y * th // oh
        Y = oy + y
        for x in range(ow):
            if crop[(sy * tw + x * tw // ow) * 4 + 3] > ALPHA_THRESHOLD:
                drawn += 1
                X = ox + x
                if not (0 <= X < sw and 0 <= Y < sh and grown[Y * sw + X]):
                    out += 1
    return 100.0 * out / drawn if drawn else 0.0


def register_inside(crop, tw, th, smask, sw, sh, box, donor_mask, aspect=1.0):
    """--inside: the best-overlap placement that keeps the picture inside the
    donor's outline (check_sprite's bar). Used when the model drew a part (a
    belt end, an intake) jutting a few per cent further than the donor: the
    plain best overlap then scales the body to match and pushes that part past
    the outline (the Autoloom south, 2026-11-27: best overlap at scale 1.04 put
    2.59% outside; scale 1.00 put 0.00%). The cost is a slightly smaller body,
    which check_sprite reports as the share of the donor the picture fills."""
    bar = _check_bar()
    grown = bar._grow(list(donor_mask), sw, sh, bar.OUTLINE_GROW_PX)
    rows = []
    for s in REG_SCALES:
        r = register(crop, tw, th, smask, sw, sh, box, scales=[s], aspect=aspect)
        rows.append((r["iou"], s, placed_outside_pct(crop, tw, th, r["rect"], grown, sw, sh), r))
    free = max(rows, key=lambda t: t[0])
    ok = [t for t in rows if t[2] <= bar.OUTSIDE_LIMIT_PCT]
    print("     inside   best overlap: scale %.2f IoU %.3f, %.2f%% outside (limit %.2f%%); "
          "read %d scales" % (free[1], free[0], free[2], bar.OUTSIDE_LIMIT_PCT, len(rows)))
    if not ok:
        raise FitError("no tested scale keeps the picture inside the donor's outline "
                       "(least outside %.2f%%) - re-generate" % min(t[2] for t in rows))
    best = max(ok, key=lambda t: t[0])
    print("     inside   coarse: scale %.2f IoU %.3f, %.2f%% outside"
          % (best[1], best[0], best[2]))
    # The refine aims at the approved pictures' measured worst, not at the
    # check's limit: aiming at the limit would make every fitted picture pass
    # it by a hair (the Autoloom south refined to 0.22% against 0.25%).
    return refine_inside(crop, tw, th, smask, grown, sw, sh, box, best[1], best[3]["rect"],
                         min(bar.OUTSIDE_APPROVED_PCT, bar.OUTSIDE_LIMIT_PCT),
                         bar.OUTSIDE_LIMIT_PCT, aspect)


# The coarse search steps 2% in scale and REG_LONG_EDGE-sized pixels in offset
# (6 full-res px on a 768 px canvas), so under the outline bar it can stop a
# whole step short (the Autoloom east, 2026-11-27: coarse best inside the bar
# IoU 0.934 at scale 0.98; scale 1.00 put 0.28% outside on the coarse grid).
# refine_inside searches one coarse step either side of the chosen scale, at
# full resolution, in 1 px offsets.
REFINE_SCALE_STEP = 0.0025     # an eighth of the coarse step
REFINE_SHIFT = 8               # full-res px each way: more than one coarse step


def refine_inside(crop, tw, th, smask, grown, sw, sh, box, s0, rect0, target, limit, aspect=1.0):
    """Full-res search around the coarse inside placement: scales s0-0.02 ..
    s0+0.02 in REFINE_SCALE_STEP, offsets +/-REFINE_SHIFT px. Keeps the best IoU
    against the registration mask among placements whose share outside `grown`
    is at most `target`; when none is (the model drew a part a little past the
    outline everywhere), the best among those at most `limit`, the check's bar.
    Scale s0 at offset 0 is the coarse placement, which is within `limit`, so
    the second tier is never empty (the Kludged Autoloom south, 2026-11-27:
    coarse 0.19%, nothing at or under 0.08%)."""
    P = REFINE_SHIFT + 64
    pw = sw + 2 * P
    src_bits = mask_to_bits(smask, sw, sh, pw, P, P)
    src_pop = src_bits.bit_count()
    ok_bits = mask_to_bits(bytearray(1 if g else 0 for g in grown), sw, sh, pw, P, P)
    sx0, sy0, sx1, sy1 = box
    base_fx, base_fy = axis_fits(sx1 - sx0 + 1, sy1 - sy0 + 1, tw, th, aspect)
    cx = rect0[0] + rect0[2] / 2.0
    cy = rect0[1] + rect0[3] / 2.0
    best = None          # best IoU with outside <= target
    best_lim = None      # best IoU with outside <= limit
    n = 0
    steps = int(round(0.02 / REFINE_SCALE_STEP))
    for i in range(-steps, steps + 1):
        s = s0 + i * REFINE_SCALE_STEP
        ow = max(1, int(round(tw * base_fx * s)))
        oh = max(1, int(round(th * base_fy * s)))
        m = bytearray(ow * oh)
        for y in range(oh):
            row = (y * th // oh) * tw
            for x in range(ow):
                if crop[(row + x * tw // ow) * 4 + 3] > ALPHA_THRESHOLD:
                    m[y * ow + x] = 1
        bx = int(round(cx - ow / 2.0))
        by = int(round(cy - oh / 2.0))
        if bx + P - REFINE_SHIFT < 0 or by + P - REFINE_SHIFT < 0 \
                or bx + ow + REFINE_SHIFT > sw + P or by + oh + REFINE_SHIFT > sh + P:
            continue
        cb = mask_to_bits(m, ow, oh, pw, bx + P, by + P)
        cpop = cb.bit_count()
        if not cpop:
            continue
        for dy in range(-REFINE_SHIFT, REFINE_SHIFT + 1):
            for dx in range(-REFINE_SHIFT, REFINE_SHIFT + 1):
                t = dy * pw + dx
                mv = cb << t if t >= 0 else cb >> -t
                n += 1
                outside = 100.0 * (cpop - (mv & ok_bits).bit_count()) / cpop
                if outside > limit:
                    continue
                inter = (mv & src_bits).bit_count()
                iou = inter / float(src_pop + cpop - inter)
                row = (iou, s, outside, (bx + dx, by + dy, ow, oh))
                if best_lim is None or iou > best_lim[0]:
                    best_lim = row
                if outside <= target and (best is None or iou > best[0]):
                    best = row
    if best is None:
        if best_lim is None:
            raise FitError("refine found no placement inside the outline - re-generate")
        print("     inside   no placement at or under the approved %.2f%%; using the "
              "best under the check's %.2f%%" % (target, limit))
        best = best_lim
    print("     inside   refined: scale %.4f IoU %.3f, %.2f%% outside (aim %.2f%%, "
          "limit %.2f%%); read %d placements" % (best[1], best[0], best[2], target, limit, n))
    return {"iou": best[0], "scale_of_fit": best[1], "rect": best[3]}


def choose_stretch(crop, tw, th, smask, sw, sh, box, skew):
    """The x-to-y factor ratio to fit with: 1.0 (one factor, as before) or the
    ratio that makes the silhouette's width AND height match the donor's.

    The image model sometimes draws the whole machine a few per cent too wide
    or too tall (the Kludged refinery south's tanks drawn fatter, the Kludged
    oven south drawn too tall; 2026-11-27). One factor then fits the long axis
    and leaves the other short, and the body reads small. A prompt sentence did
    not change the model's proportions in three calls either time.

    The skew alone cannot tell a proportion error from a shape change: a
    Wrecked picture with a part torn off (the refinery east's top pipe) has a
    shorter box for the right reason, and stretching it would draw the body
    taller than the donor's. So the stretch is used only when it also improves
    the registration overlap by at least STRETCH_MIN_GAIN; a torn-off part does
    not, a picture drawn in the wrong proportions does."""
    sx0, sy0, sx1, sy1 = box
    full = ((sx1 - sx0 + 1) / float(sy1 - sy0 + 1)) / (tw / float(th))
    pct = (skew - 1) * 100
    if not STRETCH_ON:
        print("     stretch  off (--no-stretch): skew %.2f%%, one factor" % pct)
        return 1.0
    if skew < STRETCH_MIN_SKEW:
        print("     stretch  none: skew %.2f%% is under the minimum %.1f%% (one factor, as before)"
              % (pct, (STRETCH_MIN_SKEW - 1) * 100))
        return 1.0
    if skew > STRETCH_MAX_SKEW:
        print("     stretch  NOT DONE: skew %.2f%% is over the limit %.1f%% (a larger stretch "
              "deforms round parts visibly); fitted with one factor, as before"
              % (pct, (STRETCH_MAX_SKEW - 1) * 100))
        return 1.0
    one = register(crop, tw, th, smask, sw, sh, box)
    two = register(crop, tw, th, smask, sw, sh, box, aspect=full)
    fx, fy = axis_fits(sx1 - sx0 + 1, sy1 - sy0 + 1, tw, th, full)
    if two["iou"] - one["iou"] < STRETCH_MIN_GAIN:
        print("     stretch  NOT DONE: the stretch x %.4f y %.4f would correct skew %.2f%% but "
              "moves the overlap only from IoU %.3f to %.3f (needs +%.3f): the box differs "
              "by a part, not by proportion; one factor, as before"
              % (fx, fy, pct, one["iou"], two["iou"], STRETCH_MIN_GAIN))
        return 1.0
    print("     stretch  corrects skew %.2f%% (minimum %.1f%%, limit %.1f%%): x %.4f y %.4f "
          "(ratio %.4f), overlap IoU %.3f -> %.3f"
          % (pct, (STRETCH_MIN_SKEW - 1) * 100, (STRETCH_MAX_SKEW - 1) * 100,
             fx, fy, full, one["iou"], two["iou"]))
    return full


# ------------------------------------------------------------------------ main
def fit_one(short, tier, filename, apply_changes, close_radius=CLOSE_RADIUS, inside=False):
    machine_dir = os.path.join(ART_SOURCE, short)
    man = json.load(open(os.path.join(machine_dir, "MANIFEST.json"), encoding="utf-8"))
    src_path = os.path.join(machine_dir, "restored", filename)
    cand_path = os.path.join(machine_dir, tier, filename)

    if not os.path.isfile(src_path):
        raise FitError("no reference art at restored/%s — run grab_source_art.py" % filename)
    if not os.path.isfile(cand_path):
        return None                                   # nothing supplied for this facing yet

    print("  %s / %s" % (tier, filename))
    sw, sh, s_rgba = read_png(src_path)
    cw, ch, c_rgba = read_png(cand_path)
    print("     canvas   %dx%d  ->  %dx%d" % (cw, ch, sw, sh))

    notes = []
    keyed_tol = None

    # 1. alpha
    opaque = all(c_rgba[i * 4 + 3] == 255 for i in range(0, cw * ch, 97))   # cheap sample
    if opaque:
        c_rgba, removed, tol, bstats = key_background(cw, ch, c_rgba)
        pct = 100.0 * removed / (cw * ch)
        if pct < 2:
            raise FitError("image is opaque and edge-keying removed only %.1f%% — "
                           "the background is not a flat dark colour, so alpha "
                           "cannot be recovered automatically. Re-generate with a "
                           "transparent or flat black background." % pct)
        if pct > 95:
            raise FitError("edge-keying removed %.1f%% of the image — it ate the "
                           "subject. The machine is too close in tone to its "
                           "background." % pct)
        c_rgba, reclaimed = close_alpha(cw, ch, c_rgba, close_radius)
        if reclaimed:
            print("     seal     closed %d px of background that had leaked into "
                  "the subject (radius %d)" % (reclaimed, close_radius))
            notes.append("sealed %d leaked px" % reclaimed)
        notes.append("restored alpha by edge-keying (%.1f%% removed)" % pct)
        print("     alpha    none -> keyed %.1f%% as background "
              "(auto tolerance %d; border median %d p95 %d p99 %d)"
              % (pct, tol, bstats["median"], bstats["p95"], bstats["p99"]))

        keyed_tol = tol

    # 2/3. mask, despeckle, trim
    cmask = build_mask(cw, ch, c_rgba)
    cmask, dropped = despeckle(cmask, cw, ch)
    if dropped:
        notes.append("despeckled %d stray px" % dropped)
        print("     specks   dropped %d stray px" % dropped)
    cx0, cy0, cx1, cy1 = mask_bbox(cmask, cw, ch)
    tw, th = cx1 - cx0 + 1, cy1 - cy0 + 1

    smask = build_mask(sw, sh, s_rgba)
    donor_mask = smask
    if keyed_tol is not None:
        # The candidate lost every background-dark pixel joined to its edge,
        # including the donor's dark rim (every donor measured has one, edge
        # luminance median 0). Put the donor through the same keying so the
        # two silhouettes are compared like with like. Without this a
        # thin-limbed sprite (the emanator: rim = 13% of its pixels) registers
        # 10% too large and spills out of its outline.
        flat = bytearray(s_rgba)
        for i in range(sw * sh):
            a = flat[i * 4 + 3]
            for c in range(3):
                flat[i * 4 + c] = flat[i * 4 + c] * a // 255
            flat[i * 4 + 3] = 255
        d_keyed = key_background(sw, sh, flat, tol=keyed_tol)[0]
        kmask = build_mask(sw, sh, d_keyed)
        if any(kmask):
            print("     like     donor keyed the same way for registration "
                  "(%d of %d drawn px kept)" % (sum(kmask), sum(smask)))
            smask = kmask
    sx0, sy0, sx1, sy1 = mask_bbox(smask, sw, sh)
    src_ar = (sx1 - sx0 + 1) / float(sy1 - sy0 + 1)
    cand_ar = tw / float(th)
    skew = max(cand_ar / src_ar, src_ar / cand_ar)
    print("     silhouette %dx%d (AR %.3f) vs reference %dx%d (AR %.3f) — skew %.1f%%"
          % (tw, th, cand_ar, sx1 - sx0 + 1, sy1 - sy0 + 1, src_ar, (skew - 1) * 100))
    # appendage diagnostic — projecting cables cost the machine its own size
    try:
        (cb_w, cb_h), load = appendage_load(cmask, cw, ch)
        (sb_w, sb_h), s_load = appendage_load(smask, sw, sh)
        rel_w = (cb_w / float(tw)) / (sb_w / float(sx1 - sx0 + 1))
        rel_h = (cb_h / float(th)) / (sb_h / float(sy1 - sy0 + 1))
        print("     body     core fills %.0f%% x %.0f%% of the reference body"
              % (rel_w * 100, rel_h * 100))
        if min(rel_w, rel_h) < 0.92:
            notes.append("body only %.0f%%x%.0f%% of reference" % (rel_w * 100, rel_h * 100))
            print("     ! the machine reads SMALLER than the original. Usually means "
                  "cables/hoses/plumes project past the body: the fit scales the whole "
                  "drawing into the footprint, so anything sticking out shrinks the "
                  "machine itself. Re-generate with everything inside the outline.")
    except FitError:
        pass

    if skew > MAX_ASPECT_SKEW:
        raise FitError("silhouette aspect %.3f vs reference %.3f (%.0f%% off, limit "
                       "%.0f%%). Fitting would either distort the machine or leave "
                       "it floating in empty canvas. Re-generate at the reference's "
                       "proportions." % (cand_ar, src_ar, (skew - 1) * 100,
                                         (MAX_ASPECT_SKEW - 1) * 100))

    # crop candidate to its silhouette before registering
    crop = bytearray(tw * th * 4)
    for y in range(th):
        src_off = ((cy0 + y) * cw + cx0) * 4
        crop[y * tw * 4:(y + 1) * tw * 4] = c_rgba[src_off:src_off + tw * 4]

    # 4/5. stretch, register
    aspect = choose_stretch(crop, tw, th, smask, sw, sh, (sx0, sy0, sx1, sy1), skew)
    if aspect != 1.0:
        notes.append("stretched x/y %.4f to correct skew %.1f%%" % (aspect, (skew - 1) * 100))
    if inside:
        reg = register_inside(crop, tw, th, smask, sw, sh, (sx0, sy0, sx1, sy1), donor_mask,
                              aspect)
    else:
        reg = register(crop, tw, th, smask, sw, sh, (sx0, sy0, sx1, sy1), aspect=aspect)
    ox, oy, nw, nh = reg["rect"]
    print("     register IoU %.3f at scale %.2f, placed %dx%d at (%d,%d)%s"
          % (reg["iou"], reg["scale_of_fit"], nw, nh, ox, oy,
             "" if aspect == 1.0 else "; scale x %.4f y %.4f" % (nw / float(tw), nh / float(th))))
    if reg["iou"] < 0.55:
        notes.append("LOW overlap %.2f — check the result by eye" % reg["iou"])
        print("     ! low overlap; the damaged shape differs a lot from the original")

    # 6. compose at full resolution
    scaled = resize_rgba(tw, th, crop, nw, nh)
    out = bytearray(sw * sh * 4)
    for y in range(nh):
        ty = oy + y
        if not (0 <= ty < sh):
            continue
        for x in range(nw):
            tx = ox + x
            if not (0 <= tx < sw):
                continue
            si = (y * nw + x) * 4
            if scaled[si + 3]:
                di = (ty * sw + tx) * 4
                out[di:di + 4] = scaled[si:si + 4]

    if keyed_tol is not None:
        depth, _ = donor_rim(sw, sh, s_rgba, keyed_tol)
        added = restore_rim(sw, sh, out, s_rgba, depth, keyed_tol)
        if added:
            print("     rim      gave back %d px of the donor's dark rim (depth %d), "
                  "inside the donor outline only" % (added, depth))
            notes.append("restored %d rim px" % added)

    if not apply_changes:
        print("     (dry run — pass --apply to write)")
        return {"file": filename, "tier": tier, "iou": reg["iou"], "notes": notes,
                "applied": False, "aspect": aspect}

    raw_dir = os.path.join(machine_dir, tier, "_raw")
    os.makedirs(raw_dir, exist_ok=True)
    raw_path = os.path.join(raw_dir, filename)
    if os.path.exists(raw_path):
        raise FitError("refusing to move %s over the existing raw copy at %s — "
                       "this file was very likely already fitted once (the "
                       "candidate at %s is probably the CONFORMED sprite, not "
                       "a fresh original). Re-running --apply would silently "
                       "destroy the true original. Move or remove the existing "
                       "_raw/ file first if you really mean to re-fit."
                       % (cand_path, raw_path, cand_path))
    shutil.move(cand_path, raw_path)
    write_rgba(cand_path, sw, sh, out)
    print("     WROTE    %s   (original preserved in %s/_raw/)" % (filename, tier))
    return {"file": filename, "tier": tier, "iou": reg["iou"], "notes": notes,
            "applied": True, "aspect": aspect}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("machine")
    ap.add_argument("--tier", help="wrecked | kludged | icon (or any tier dir)")
    ap.add_argument("--all-tiers", action="store_true")
    ap.add_argument("--facing", help="just one facing, e.g. east")
    ap.add_argument("--apply", action="store_true", help="write (default is a dry run)")
    ap.add_argument("--close", type=int, default=CLOSE_RADIUS,
                    help="morphological seal radius after keying (default %d)" % CLOSE_RADIUS)
    ap.add_argument("--root", help="work folder (default art_source/, or env WM_ART_ROOT)")
    ap.add_argument("--inside", action="store_true",
                    help="place at the best overlap that keeps the picture inside the "
                         "donor's outline (see register_inside)")
    ap.add_argument("--no-stretch", action="store_true",
                    help="one scale factor always (reproduces a fit made before the stretch)")
    args = ap.parse_args()
    global ART_SOURCE, STRETCH_ON
    if args.no_stretch:
        STRETCH_ON = False
    if args.root:
        ART_SOURCE = os.path.abspath(args.root)

    if not args.tier and not args.all_tiers:
        ap.error("choose --tier or --all-tiers")

    man_path = os.path.join(ART_SOURCE, args.machine, "MANIFEST.json")
    if not os.path.isfile(man_path):
        sys.exit("No MANIFEST.json for %s — run grab_source_art.py first." % args.machine)
    man = json.load(open(man_path, encoding="utf-8"))
    tiers = tuple(man.get("tiers") or TIERS) if args.all_tiers else (args.tier,)
    files = man["expected_files"]
    if args.facing:
        files = [f for f in files if f.lower().endswith("_%s.png" % args.facing.lower())]
        if not files:
            sys.exit("No expected file for facing %r." % args.facing)

    print("%s" % args.machine)
    done = fails = skipped = 0
    for tier in tiers:
        for fn in files:
            try:
                r = fit_one(args.machine, tier, fn, args.apply, args.close, args.inside)
                if r is None:
                    skipped += 1
                else:
                    done += 1
            except (FitError, PngError) as e:
                fails += 1
                print("  %s / %s" % (tier, fn))
                print("     REFUSED  %s" % e)
    print("\n%d fitted, %d refused, %d not supplied yet." % (done, fails, skipped))
    if done and not args.apply:
        print("Dry run only. Re-run with --apply to write.")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
