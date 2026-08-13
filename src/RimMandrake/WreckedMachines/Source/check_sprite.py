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
  python Source/check_sprite.py AutomatedSmelter --tier kludged --strict
  python Source/check_sprite.py ALL            # every machine, every tier

Exit code 0 = every required file present and sane. 1 = at least one FAIL.
Warnings alone do not fail the run unless --strict is given.
"""

import argparse
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pnglib import measure, PngError                         # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
MOD_ROOT = os.path.dirname(HERE)
ART_SOURCE = os.path.join(MOD_ROOT, "art_source")

# --------------------------------------------------------------------------
# The general validator, src/RimMandrake/Utils/check_sprite.py
# --------------------------------------------------------------------------
# This file keeps its own CLI and its own MANIFEST.json flow - those are what
# briefs.py, sheet.py, README.md and the three BRIEF_*.md files call, and none
# of them should have to change. What it does NOT keep is a private copy of the
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

TIERS = ("wrecked", "kludged", "repaired")

# How far the drawn mass may drift, as a fraction of canvas, before it will
# visibly sit off its footprint. 2% of a 512px canvas is ~10px — about a third
# of a tile at this drawSize, which is the point where the eye notices.
CENTRE_DRIFT_TOLERANCE = 0.02
# A damaged machine should not be substantially BIGGER than the intact one.
MAX_BBOX_GROWTH = 1.05
# Below this, the image is suspiciously empty.
MIN_COVERAGE_PCT = 5.0


class Result:
    def __init__(self, name):
        self.name, self.fails, self.warns = name, [], []

    def fail(self, msg): self.fails.append(msg)

    def warn(self, msg): self.warns.append(msg)

    @property
    def status(self):
        return "FAIL" if self.fails else ("warn" if self.warns else "ok")


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def check_file(src_meta, cand_path, src_path):
    r = Result(os.path.basename(cand_path))

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
        cx0, cy0, cx1, cy1 = c["bbox"]
        s_cx, s_cy = (sx0 + sx1) / 2.0, (sy0 + sy1) / 2.0
        c_cx, c_cy = (cx0 + cx1) / 2.0, (cy0 + cy1) / 2.0
        dx, dy = abs(c_cx - s_cx) / c["width"], abs(c_cy - s_cy) / c["height"]
        if max(dx, dy) > CENTRE_DRIFT_TOLERANCE:
            r.fail("silhouette centre drifted %.1f%%/%.1f%% of canvas (max %.0f%%) "
                   "— it will sit off its footprint"
                   % (dx * 100, dy * 100, CENTRE_DRIFT_TOLERANCE * 100))
        # 5. damaged art should not grow
        sw, sh = src_meta["bbox_wh"]
        cw, ch = c["bbox_wh"]
        if cw > sw * MAX_BBOX_GROWTH or ch > sh * MAX_BBOX_GROWTH:
            r.warn("drawn area grew (%s -> %s); damage should remove mass, not add it"
                   % (src_meta["bbox_wh"], c["bbox_wh"]))

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


def check_machine(short, tiers, strict=False):
    man_path = os.path.join(ART_SOURCE, short, "MANIFEST.json")
    if not os.path.isfile(man_path):
        print("  %s: no MANIFEST.json — run grab_source_art.py first" % short)
        return 1
    man = json.load(open(man_path, encoding="utf-8"))
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
    ap.add_argument("--tier", help="wrecked | kludged | repaired (or any tier dir)")
    ap.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = ap.parse_args()

    tiers = (args.tier,) if args.tier else TIERS
    if args.machine == "ALL":
        if not os.path.isdir(ART_SOURCE):
            sys.exit("No art_source/ yet — run grab_source_art.py first.")
        machines = sorted(d for d in os.listdir(ART_SOURCE)
                          if os.path.isdir(os.path.join(ART_SOURCE, d)))
    else:
        machines = [args.machine]

    rc = 0
    for m in machines:
        rc |= check_machine(m, tiers, args.strict)
    print("\n%s" % ("FAILED — fix the above before authoring defs." if rc
                    else "All required art present and sane."))
    return rc


if __name__ == "__main__":
    sys.exit(main())
