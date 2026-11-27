#!/usr/bin/env python3
"""
check_sprite.py — art intake validator. Refuse bad sprites before they reach a
def, and long before they reach a ~25-minute game load.

THE POINT
=========
Generated art fails in a small number of boring, mechanical ways, and every one
of them is invisible until a pawn is standing next to the thing in game:

  * wrong canvas size            -> the machine renders at the wrong scale
  * no alpha (opaque rectangle)  -> a white box sits on your factory floor
  * shifted silhouette           -> the machine floats off its own footprint
  * blank / near-empty image     -> an invisible building
  * colour drift to greyscale    -> looks like a different mod's asset
  * "damaged" version identical  -> the tier does nothing, and nobody notices

Each is decidable offline in milliseconds from the numbers `grab_source_art.py`
already measured. That is the whole justification for this file: a reload is the
scarcest resource in this project, so no reload should ever be spent
discovering that a PNG was the wrong size.

THE ALIGNMENT CHECK IS THE IMPORTANT ONE
========================================
RimWorld draws a building from its texture's centre at `drawSize`. Two images of
identical canvas size still misalign if the drawn mass sits in a different place
within that canvas. So we compare the **alpha bounding box** of the candidate
against the source's, and fail when its centre has drifted more than a tolerance
of the canvas. Damaged art is *expected* to shrink — chunks are missing — so the
test is on centre drift and on gross size change, not on an exact match.

USAGE
  python Source/check_sprite.py AutomatedSmelter --tier wrecked
  python Source/check_sprite.py Autoloom --tier kludged --strict --root /mnt/d/ClaudeWork/rimmandrake/art/wreckedmachines
  python Source/check_sprite.py ALL            # every machine, every tier in its MANIFEST

`--root DIR` (or env WM_ART_ROOT) picks the work folder; default art_source/.
The last line prints the worst value of each measured bar, its limit and how
many files were read.

Exit code 0 = every required file present and sane. 1 = at least one FAIL.
Warnings alone do not fail the run unless --strict is given.
"""

import argparse
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pnglib import measure, read_png, PngError               # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
MOD_ROOT = os.path.dirname(HERE)
ART_SOURCE = os.environ.get("WM_ART_ROOT") or os.path.join(MOD_ROOT, "art_source")

# --------------------------------------------------------------------------
# The general validator, src/RimMandrake/Utils/check_sprite.py
# --------------------------------------------------------------------------
# This file keeps its own CLI and its own MANIFEST.json flow - those are what
# grab_source_art.py, briefs.py and the per-facing briefs call. What it does NOT keep is a private copy of the
# checks: saturation, value distribution and the fully-transparent-pixel test
# live in the general tool, and are imported so both callers move together.
#
# STRICTLY OPTIONAL. If the import fails this file behaves exactly as it did
# before, minus the three extra findings, and says so once rather than dying -
# an art pipeline that refuses to run because a sibling module moved is worse
# than one that reports slightly less.
# Loaded by explicit PATH, not by name: this file is also called check_sprite.py
# and sits on sys.path, so a plain `import check_sprite` is ambiguous and would
# resolve to whichever entry happens to come first.
_GENERAL_PATH = os.path.join(os.path.dirname(MOD_ROOT), "Utils", "check_sprite.py")
try:
    import importlib.util as _ilu                            # noqa: E402
    _spec = _ilu.spec_from_file_location("rimmandrake_check_sprite", _GENERAL_PATH)
    GENERAL = _ilu.module_from_spec(_spec)
    _spec.loader.exec_module(GENERAL)
    HAVE_GENERAL = bool(getattr(GENERAL, "HAVE_VS", False))
except Exception:                                            # pragma: no cover
    GENERAL = None
    HAVE_GENERAL = False

TIERS = ("wrecked", "kludged")      # default when a MANIFEST names no tiers

# How far the drawn mass may drift, as a fraction of canvas, before it will
# visibly sit off its footprint. 2% of a 512px canvas is ~10px — about a third
# of a tile at this drawSize, which is the point where the eye notices.
CENTRE_DRIFT_TOLERANCE = 0.02
# A damaged machine should not be substantially BIGGER than the intact one.
MAX_BBOX_GROWTH = 1.05
# Below this, the image is suspiciously empty.
MIN_COVERAGE_PCT = 5.0
# Bar (owner): damage is subtractive and nothing projects past the donor's
# outline. Measured as the share of the picture's drawn pixels (alpha >= 32)
# that fall outside the donor's drawn pixels grown by OUTLINE_GROW_PX. Measured
# 2026-11-27 on the 12 approved smelter pictures (Wrecked, Kludged, Repaired):
# worst 0.08% at a 2 px grow (Kludged west). The limit is three times that.
OUTLINE_GROW_PX = 2
OUTSIDE_APPROVED_PCT = 0.08   # the measured worst of the 12 approved pictures
OUTSIDE_LIMIT_PCT = 0.25
ALPHA_DRAWN = 32
# The share of the donor's drawn pixels that the picture also draws. A picture
# placed small (fit_sprite --inside, or a model that drew the machine small)
# leaves a band of the donor's footprint empty. Measured 2026-11-27 on the 12
# approved smelter pictures: 95.89% (Wrecked north) to 99.32%. Below the
# lowest approved value is a warn: it asks for a look at true size.
FILL_WARN_PCT = 95.8
# THE DONOR'S BODY. The donor picture is the reference for the bounding box (centre drift), the outline and
# the fill. A detached piece of a few pixels is not part of the machine and must not move those references:
# the Medicine Granulator's donor east picture has one of 158 px at its bottom edge (a 66 x 3 stripe, 63 px below
# the body), which moved the reference centre 4.9% and failed both of its east pictures however well drawn.
# donor_body() leaves out every 8-connected piece of drawn pixels (alpha > 0, as pnglib.measure counts) that is
# smaller than DONOR_SPECK_SHARE_PCT of the largest piece. Measured 2026-11-27 over all 73 donor files under
# $W/*/restored/ (specks/pieces.txt, measure_pieces.py): exactly one has a second piece, the granulator's east,
# 159 px = 0.064% of its 248,723 px body; the other 72 are one piece, so no donor has a real separate part and
# nothing real is dropped at any limit. 0.5% is about eight times the stray (room for a stray twice or
# three times as big) and half the 1% share that selftest_donor_specks.py proves is kept (a real part).
# A donor whose strays are dropped reads from the body; one with none is read exactly as before.
DONOR_SPECK_SHARE_PCT = 0.5


class Result:
    def __init__(self, name):
        self.name, self.fails, self.warns = name, [], []

    def fail(self, msg): self.fails.append(msg)

    def warn(self, msg): self.warns.append(msg)

    @property
    def status(self):
        return "FAIL" if self.fails else ("warn" if self.warns else "ok")


def _grow(mask, w, h, r):
    """Square dilation of a boolean mask by r px (separable)."""
    if r <= 0:
        return mask
    a = [False] * (w * h)
    for y in range(h):
        row = mask[y * w:(y + 1) * w]
        run = [i for i, v in enumerate(row) if v]
        for x in run:
            for xx in range(max(0, x - r), min(w, x + r + 1)):
                a[y * w + xx] = True
    b = [False] * (w * h)
    for x in range(w):
        col = a[x::w]
        for y in [i for i, v in enumerate(col) if v]:
            for yy in range(max(0, y - r), min(h, y + r + 1)):
                b[yy * w + x] = True
    return b


def donor_body(w, h, rgba):
    """(rgba, dropped): the donor's body. Pieces of drawn pixels (alpha > 0, 8-connected) smaller than
    DONOR_SPECK_SHARE_PCT of the largest piece get alpha 0 in a copy; `dropped` counts those pixels. With no
    such piece the input is returned itself and dropped is 0."""
    n = w * h
    solid = bytes(rgba[3::4]).translate(_SOLID)
    seen = bytearray(n)
    pieces = []
    for start in range(n):
        if not solid[start] or seen[start]:
            continue
        seen[start] = 1
        stack, px = [start], []
        while stack:
            i = stack.pop()
            px.append(i)
            x = i % w
            for dy in (-w, 0, w):
                for dx in (-1, 0, 1):
                    j = i + dy + dx
                    if (dy or dx) and 0 <= j < n and not seen[j] and solid[j] \
                            and 0 <= x + dx < w:
                        seen[j] = 1
                        stack.append(j)
        pieces.append(px)
    if len(pieces) < 2:
        return rgba, 0
    limit = max(len(p) for p in pieces) * DONOR_SPECK_SHARE_PCT / 100.0
    small = [p for p in pieces if len(p) < limit]
    if not small:
        return rgba, 0
    out = bytearray(rgba)
    for p in small:
        for i in p:
            out[i * 4 + 3] = 0
    return out, sum(len(p) for p in small)


_SOLID = bytes([0] + [1] * 255)
_BODY = {}


def read_donor(path):
    """(w, h, rgba, dropped): the donor file with donor_body() applied. Cached per file version."""
    st = os.stat(path)
    key = (os.path.abspath(path), st.st_mtime_ns, st.st_size, DONOR_SPECK_SHARE_PCT)
    if key not in _BODY:
        w, h, rgba = read_png(path)
        body, dropped = donor_body(w, h, rgba)
        _BODY.clear()                      # one donor at a time: the batch goes picture by picture
        _BODY[key] = (w, h, body, dropped)
    return _BODY[key]


def body_bbox(w, h, rgba):
    """[x0, y0, x1, y1] (inclusive) of the pixels with alpha > 0, as pnglib.measure gives bbox."""
    xs0, ys0, xs1, ys1 = w, h, -1, -1
    for y in range(h):
        row = rgba[y * w * 4 + 3:(y + 1) * w * 4:4]
        if any(row):
            xs = [i for i, v in enumerate(row) if v]
            xs0, xs1 = min(xs0, xs[0]), max(xs1, xs[-1])
            ys0, ys1 = min(ys0, y), max(ys1, y)
    return [xs0, ys0, xs1, ys1] if xs1 >= 0 else None


def outside_outline_pct(cand_path, src_path, grow=OUTLINE_GROW_PX):
    """Share (%) of the picture's drawn pixels outside the donor's grown outline (the donor's body)."""
    sw, sh, s, _ = read_donor(src_path)
    cw, ch, c = read_png(cand_path)
    if (sw, sh) != (cw, ch):
        return None
    m = _grow([s[i * 4 + 3] >= ALPHA_DRAWN for i in range(sw * sh)], sw, sh, grow)
    tot = out = 0
    for i in range(cw * ch):
        if c[i * 4 + 3] >= ALPHA_DRAWN:
            tot += 1
            if not m[i]:
                out += 1
    return 100.0 * out / tot if tot else 0.0


def donor_fill_pct(cand_path, src_path):
    """Share (%) of the donor's drawn pixels (its body) that the picture also draws."""
    sw, sh, s, _ = read_donor(src_path)
    cw, ch, c = read_png(cand_path)
    if (sw, sh) != (cw, ch):
        return None
    tot = hit = 0
    for i in range(sw * sh):
        if s[i * 4 + 3] >= ALPHA_DRAWN:
            tot += 1
            if c[i * 4 + 3] >= ALPHA_DRAWN:
                hit += 1
    return 100.0 * hit / tot if tot else None


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def check_file(src_meta, cand_path, src_path):
    r = Result(os.path.basename(cand_path))
    r.drift = r.outside = r.fill = None

    if not os.path.isfile(cand_path):
        r.fail("missing")
        return r
    try:
        c = measure(cand_path)
    except PngError as e:
        r.fail("unreadable: %s" % e)
        return r
    except Exception as e:                       # noqa: BLE001 - report, never crash the batch
        r.fail("could not decode: %s" % e)
        return r

    if "error" in src_meta:
        r.warn("source measurement unavailable; only self-consistency checked")
        return r

    # 1. canvas size must match exactly
    if (c["width"], c["height"]) != (src_meta["width"], src_meta["height"]):
        r.fail("canvas %dx%d, expected %dx%d"
               % (c["width"], c["height"], src_meta["width"], src_meta["height"]))

    # 2. real alpha
    if not c["has_real_alpha"]:
        r.fail("no transparency — every pixel is opaque (a rectangle will render)")

    # 3. not blank
    if c["coverage_pct"] < MIN_COVERAGE_PCT:
        r.fail("only %.1f%% of the canvas is drawn; near-invisible" % c["coverage_pct"])

    # 4. alignment: centre drift of the drawn mass
    if (c["width"], c["height"]) == (src_meta["width"], src_meta["height"]):
        sx0, sy0, sx1, sy1 = src_meta["bbox"]
        sw, sh = src_meta["bbox_wh"]
        if os.path.isfile(src_path):             # the donor's body, not its strays
            dw, dh, drgba, dropped = read_donor(src_path)
            if dropped and (dw, dh) == (src_meta["width"], src_meta["height"]):
                sx0, sy0, sx1, sy1 = body_bbox(dw, dh, drgba)
                sw, sh = sx1 - sx0 + 1, sy1 - sy0 + 1
        elif src_meta.get("body_bbox"):          # grab_source_art.py's own reading of the body
            sx0, sy0, sx1, sy1 = src_meta["body_bbox"]
            sw, sh = src_meta["body_bbox_wh"]
        cx0, cy0, cx1, cy1 = c["bbox"]
        s_cx, s_cy = (sx0 + sx1) / 2.0, (sy0 + sy1) / 2.0
        c_cx, c_cy = (cx0 + cx1) / 2.0, (cy0 + cy1) / 2.0
        dx, dy = abs(c_cx - s_cx) / c["width"], abs(c_cy - s_cy) / c["height"]
        r.drift = max(dx, dy) * 100
        if max(dx, dy) > CENTRE_DRIFT_TOLERANCE:
            r.fail("silhouette centre drifted %.1f%%/%.1f%% of canvas (max %.0f%%) "
                   "— it will sit off its footprint"
                   % (dx * 100, dy * 100, CENTRE_DRIFT_TOLERANCE * 100))
        # 5. damaged art should not grow
        cw, ch = c["bbox_wh"]
        if cw > sw * MAX_BBOX_GROWTH or ch > sh * MAX_BBOX_GROWTH:
            r.warn("drawn area grew (%s -> %s); damage should remove mass, not add it"
                   % (src_meta["bbox_wh"], c["bbox_wh"]))

        # 5b. nothing past the donor's outline (the subtractive-damage bar)
        if os.path.isfile(src_path):
            r.outside = outside_outline_pct(cand_path, src_path)
            if r.outside is not None and r.outside > OUTSIDE_LIMIT_PCT:
                r.fail("%.2f%% of the drawn pixels lie outside the donor's outline "
                       "(+%d px; limit %.2f%%) - something projects past the machine"
                       % (r.outside, OUTLINE_GROW_PX, OUTSIDE_LIMIT_PCT))
            r.fill = donor_fill_pct(cand_path, src_path)
            if r.fill is not None and r.fill < FILL_WARN_PCT:
                r.warn("fills %.2f%% of the donor's drawn pixels (the approved smelter "
                       "pictures fill at least %.1f%%) - placed small or drawn small"
                       % (r.fill, FILL_WARN_PCT))

    # 6. colour mode consistency
    if c["is_greyscale"] != src_meta["is_greyscale"]:
        r.fail("source is %s but this is %s"
               % ("greyscale" if src_meta["is_greyscale"] else "colour",
                  "greyscale" if c["is_greyscale"] else "colour"))

    # 7. did anything actually change?
    if os.path.isfile(src_path) and sha(cand_path) == sha(src_path):
        r.fail("byte-identical to the restored source — this tier is not damaged")

    # 8-10. saturation, value distribution and the fully-transparent-pixel test,
    # from the general validator. Check 2 above ("real alpha") uses pnglib's
    # has_real_alpha, which asks whether ANY pixel is not fully opaque; the
    # general check asks whether any pixel is fully CLEAR, which is the property
    # that decides whether a silhouette or a block renders.
    if HAVE_GENERAL:
        for level, msg in GENERAL.extra_for_path(cand_path, src_path):
            (r.fail if level == GENERAL.REJECT else r.warn)(msg)

    return r


STATS = {"files": 0, "drift": (0.0, ""), "outside": (0.0, ""), "fill": (101.0, "")}


def _note(key, val, where):
    if val is not None and val >= STATS[key][0]:
        STATS[key] = (val, where)


def check_machine(short, tiers=None, strict=False):
    man_path = os.path.join(ART_SOURCE, short, "MANIFEST.json")
    if not os.path.isfile(man_path):
        print("  %s: no MANIFEST.json — run grab_source_art.py first" % short)
        return 1
    man = json.load(open(man_path, encoding="utf-8"))
    tiers = tiers or tuple(man.get("tiers") or TIERS)
    worst = 0
    for tier in tiers:
        tier_dir = os.path.join(ART_SOURCE, short, tier)
        print("\n%s / %s" % (short, tier))
        print("  " + "-" * 66)
        n_ok = n_warn = n_fail = 0
        for fn in man["expected_files"]:
            src_meta = man["measurements"].get(fn, {"error": "not measured"})
            r = check_file(src_meta,
                           os.path.join(tier_dir, fn),
                           os.path.join(ART_SOURCE, short, "restored", fn))
            STATS["files"] += 1
            _note("drift", r.drift, "%s/%s/%s" % (short, tier, fn))
            _note("outside", r.outside, "%s/%s/%s" % (short, tier, fn))
            if r.fill is not None and r.fill < STATS["fill"][0]:
                STATS["fill"] = (r.fill, "%s/%s/%s" % (short, tier, fn))
            mark = {"ok": "  ok  ", "warn": " warn ", "FAIL": " FAIL "}[r.status]
            print("  [%s] %s" % (mark, r.name))
            for m in r.fails:
                print("           x %s" % m)
            for m in r.warns:
                print("           ! %s" % m)
            n_ok += r.status == "ok"
            n_warn += r.status == "warn"
            n_fail += r.status == "FAIL"
        print("  %d ok, %d warn, %d FAIL" % (n_ok, n_warn, n_fail))
        if n_fail or (strict and n_warn):
            worst = 1
    return worst


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("machine", help="short name (e.g. AutomatedSmelter), or ALL")
    ap.add_argument("--tier", help="wrecked | kludged | icon (default: the MANIFEST's tiers)")
    ap.add_argument("--strict", action="store_true", help="treat warnings as failures")
    ap.add_argument("--root", help="work folder (default art_source/, or env WM_ART_ROOT)")
    args = ap.parse_args()
    global ART_SOURCE
    if args.root:
        ART_SOURCE = os.path.abspath(args.root)

    tiers = (args.tier,) if args.tier else None
    if args.machine == "ALL":
        if not os.path.isdir(ART_SOURCE):
            sys.exit("No art_source/ yet — run grab_source_art.py first.")
        machines = sorted(d for d in os.listdir(ART_SOURCE)
                          if os.path.isfile(os.path.join(ART_SOURCE, d, "MANIFEST.json")))
    else:
        machines = [args.machine]

    rc = 0
    for m in machines:
        rc |= check_machine(m, tiers, args.strict)
    print("\nread %d file(s); worst centre drift %.2f%% (limit %.0f%%) at %s; "
          "worst outside-outline %.2f%% (limit %.2f%%) at %s; "
          "lowest donor fill %s (warn below %.1f%%) at %s"
          % (STATS["files"], STATS["drift"][0], CENTRE_DRIFT_TOLERANCE * 100,
             STATS["drift"][1] or "-", STATS["outside"][0], OUTSIDE_LIMIT_PCT,
             STATS["outside"][1] or "-",
             ("%.2f%%" % STATS["fill"][0]) if STATS["fill"][1] else "-",
             FILL_WARN_PCT, STATS["fill"][1] or "-"))
    print("\n%s" % ("FAILED — fix the above before authoring defs." if rc
                    else "All required art present and sane."))
    return rc


if __name__ == "__main__":
    sys.exit(main())
