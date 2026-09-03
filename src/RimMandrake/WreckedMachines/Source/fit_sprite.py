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
     silhouette, preserving aspect. Never stretches.
  6. **Register** — searches scale and offset to maximise mask overlap (IoU)
     with the reference. This is the part a naive centre-and-scale gets wrong:
     damaged art is *missing chunks*, so its bounding box is not its centre of
     mass, and bbox-centring alone drifts the machine off its footprint.
  7. **Compose** onto the reference's exact canvas with premultiplied,
     area-averaged resampling, so the downscale stays sharp and no dark fringe
     appears at the cut edge.

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
ART_SOURCE = os.path.join(MOD_ROOT, "art_source")

ALPHA_THRESHOLD = 32        # what counts as "drawn" when measuring a silhouette
KEY_TOLERANCE = 28          # luminance at/below which an edge pixel reads as background
SPECK_FRACTION = 0.02       # islands smaller than this fraction of the biggest are noise
REG_LONG_EDGE = 128         # registration works on a mask this big; full res is far too slow
REG_SCALES = [0.88 + 0.02 * i for i in range(13)]   # 0.88 .. 1.12
REG_SHIFT = 10              # +/- this many low-res pixels
MAX_ASPECT_SKEW = 1.35      # refuse beyond this ratio; the shape is simply wrong
CLOSE_RADIUS = 6            # seal background channels narrower than this after keying
TIERS = ("wrecked", "kludged", "repaired")   # the three states we author art for


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


def register(cand_rgba, cw, ch, src_mask, sw, sh, src_box):
    """Find the (scale, dx, dy) placing the candidate best over the reference.

    Returns a rectangle in reference-canvas coordinates plus the achieved IoU.
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
    for s in REG_SCALES:
        # candidate silhouette scaled to `s` of the reference silhouette box
        fit = min(tgt_w / float(cw), tgt_h / float(ch)) * s
        nw, nh = max(1, int(round(cw * fit * k))), max(1, int(round(ch * fit * k)))
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
    out_w = max(1, int(round(cw * fit)))
    out_h = max(1, int(round(ch * fit)))
    out_x = int(round((bx - pad + dx) / k))
    out_y = int(round((by - pad + dy) / k))
    return {"iou": iou, "scale_of_fit": s, "rect": (out_x, out_y, out_w, out_h)}


# ------------------------------------------------------------------------ main
def fit_one(short, tier, filename, apply_changes, close_radius=CLOSE_RADIUS):
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

    # 2/3. mask, despeckle, trim
    cmask = build_mask(cw, ch, c_rgba)
    cmask, dropped = despeckle(cmask, cw, ch)
    if dropped:
        notes.append("despeckled %d stray px" % dropped)
        print("     specks   dropped %d stray px" % dropped)
    cx0, cy0, cx1, cy1 = mask_bbox(cmask, cw, ch)
    tw, th = cx1 - cx0 + 1, cy1 - cy0 + 1

    smask = build_mask(sw, sh, s_rgba)
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

    # 4/5. register
    reg = register(crop, tw, th, smask, sw, sh, (sx0, sy0, sx1, sy1))
    ox, oy, nw, nh = reg["rect"]
    print("     register IoU %.3f at scale %.2f, placed %dx%d at (%d,%d)"
          % (reg["iou"], reg["scale_of_fit"], nw, nh, ox, oy))
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

    if not apply_changes:
        print("     (dry run — pass --apply to write)")
        return {"file": filename, "tier": tier, "iou": reg["iou"], "notes": notes,
                "applied": False}

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
            "applied": True}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("machine")
    ap.add_argument("--tier", help="wrecked | kludged | repaired (or any tier dir)")
    ap.add_argument("--all-tiers", action="store_true")
    ap.add_argument("--facing", help="just one facing, e.g. east")
    ap.add_argument("--apply", action="store_true", help="write (default is a dry run)")
    ap.add_argument("--close", type=int, default=CLOSE_RADIUS,
                    help="morphological seal radius after keying (default %d)" % CLOSE_RADIUS)
    args = ap.parse_args()

    if not args.tier and not args.all_tiers:
        ap.error("choose --tier or --all-tiers")
    tiers = TIERS if args.all_tiers else (args.tier,)

    man_path = os.path.join(ART_SOURCE, args.machine, "MANIFEST.json")
    if not os.path.isfile(man_path):
        sys.exit("No MANIFEST.json for %s — run grab_source_art.py first." % args.machine)
    man = json.load(open(man_path, encoding="utf-8"))
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
                r = fit_one(args.machine, tier, fn, args.apply, args.close)
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
