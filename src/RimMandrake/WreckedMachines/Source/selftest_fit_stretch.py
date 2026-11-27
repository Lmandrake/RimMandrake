#!/usr/bin/env python3
"""selftest_fit_stretch.py: fit_sprite.py corrects a picture drawn a few per cent too wide (choose_stretch).

    python3 Source/selftest_fit_stretch.py [--fitter PATH] [--before PATH]

Run from src/RimMandrake/WreckedMachines/. Dev tooling, not shipped. Exit 0 pass, 1 fail.

The donor is the smelter's approved Wrecked south picture (Textures/.../AutomatedSmelter/Wrecked/), with the smelter's
MANIFEST (art_source/AutomatedSmelter/). Each case is a copy of it, scaled up about 2.2 times onto a larger transparent
or opaque black canvas (the way the image model returns a picture), fitted with --inside (the briefs' fit command) in a
temp root:
  plain     the copy at the donor's proportions: the overlap the fitter reaches when nothing is wrong;
  wide6     the copy 6% wider (the fault of 2026-11-27): must fill the donor within FILL_TOLERANCE_PT of `plain`;
  wide6blk  the same on an opaque black canvas (the keyed path);
  wide15    the copy 15% wider, over the stretch limit: must be fitted with one factor and say so;
  nostretch `plain` again with --no-stretch: its bytes must equal `plain`'s (a picture with no skew is not changed),
            and with --before PATH (an older fit_sprite.py) the older fitter's bytes too.
--fitter PATH tests another copy of fit_sprite.py (an older one must FAIL wide6).
"""
import argparse
import contextlib
import hashlib
import importlib.util
import io
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
DONOR = os.path.join(MOD, "Textures", "WreckedMachines", "Factories", "AutomatedSmelter", "Wrecked",
                     "AutomatedSmelter_south.png")
MANIFEST = os.path.join(MOD, "art_source", "AutomatedSmelter", "MANIFEST.json")
SHORT, FILE = "AutomatedSmelter", "AutomatedSmelter_south.png"
UPSCALE = 2.2          # the model returns about 1408 px on the long edge; the smelter canvas is 640 (2.2 times)
CANVAS = 1.3           # the copy sits on a canvas this much larger than itself, as a model picture does
# A point of fill (the check's share of the donor's drawn pixels) is the brief's bar for "fills the donor as well as
# the unstretched copy does".
FILL_TOLERANCE_PT = 1.0


def load(path, tmp):
    """A fit_sprite.py by path, beside a pnglib.py and check_sprite.py from this folder (an older copy kept in scratch
    has neither next to it)."""
    d = os.path.join(tmp, "fitter")
    os.makedirs(d, exist_ok=True)
    shutil.copy(path, os.path.join(d, "fit_sprite.py"))
    for f in ("pnglib.py", "check_sprite.py"):
        shutil.copy(os.path.join(HERE, f), os.path.join(d, f))
    spec = importlib.util.spec_from_file_location("fit_under_test_%d" % len(os.listdir(tmp)),
                                                  os.path.join(d, "fit_sprite.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, d)
    spec.loader.exec_module(mod)
    sys.path.remove(d)
    return mod


def make_copy(dst, sx, opaque):
    """The donor's drawing, cropped to its silhouette, scaled UPSCALE (times sx across), centred on a larger canvas."""
    from PIL import Image
    im = Image.open(DONOR).convert("RGBA")
    im = im.crop(im.getchannel("A").point(lambda a: 255 if a > 32 else 0).getbbox())
    w, h = im.size
    im = im.resize((round(w * UPSCALE * sx), round(h * UPSCALE)), Image.LANCZOS)
    W, H = round(im.size[0] * CANVAS / sx * 1.06), round(im.size[1] * CANVAS)   # same canvas for every sx up to 6%
    W = max(W, im.size[0] + 40)
    bg = Image.new("RGBA", (W, H), (0, 0, 0, 255 if opaque else 0))
    bg.alpha_composite(im, ((W - im.size[0]) // 2, (H - im.size[1]) // 2))
    if opaque:
        bg = bg.convert("RGB").convert("RGBA")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    bg.save(dst)


def fit(F, root, tier, sx, opaque, no_stretch=False):
    cand = os.path.join(root, SHORT, tier, FILE)
    make_copy(cand, sx, opaque)
    F.ART_SOURCE = root
    buf = io.StringIO()
    if no_stretch:
        F.STRETCH_ON = False
    with contextlib.redirect_stdout(buf):
        try:
            r = F.fit_one(SHORT, tier, FILE, True, inside=True)
        finally:
            if no_stretch:
                F.STRETCH_ON = True
    out = buf.getvalue()
    bar = F._check_bar()
    src = os.path.join(root, SHORT, "restored", FILE)
    return {"fill": bar.donor_fill_pct(cand, src), "outside": bar.outside_outline_pct(cand, src),
            "aspect": r.get("aspect", 1.0), "out": out,
            "sha": hashlib.sha256(open(cand, "rb").read()).hexdigest(), "limit_out": bar.OUTSIDE_LIMIT_PCT}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fitter", default=os.path.join(HERE, "fit_sprite.py"))
    ap.add_argument("--before", help="an older fit_sprite.py whose bytes the no-skew case must equal")
    a = ap.parse_args()
    tmp = tempfile.mkdtemp(prefix="fitstretch_")
    fails = 0
    try:
        root = os.path.join(tmp, "root")
        os.makedirs(os.path.join(root, SHORT, "restored"))
        shutil.copy(MANIFEST, os.path.join(root, SHORT, "MANIFEST.json"))
        shutil.copy(DONOR, os.path.join(root, SHORT, "restored", FILE))
        F = load(a.fitter, tmp)
        print("fitter %s; donor %s" % (a.fitter, os.path.relpath(DONOR, MOD)))

        def line(ok, name, text):
            nonlocal fails
            fails += 0 if ok else 1
            print("%s  %-10s %s" % ("PASS" if ok else "FAIL", name, text))

        plain = fit(F, root, "plain", 1.0, False)
        line(plain["aspect"] == 1.0 and plain["outside"] <= plain["limit_out"], "plain",
             "fill %.2f%%, outside %.2f%% (limit %.2f%%), stretch ratio %.4f (must be 1)"
             % (plain["fill"], plain["outside"], plain["limit_out"], plain["aspect"]))
        for name, opaque in (("wide6", False), ("wide6blk", True)):
            r = fit(F, root, name, 1.06, opaque)
            ok = r["fill"] >= plain["fill"] - FILL_TOLERANCE_PT and r["outside"] <= r["limit_out"]
            line(ok, name, "fill %.2f%% vs plain %.2f%% (must be within %.1f pt: worst allowed %.2f%%), outside "
                 "%.2f%% (limit %.2f%%), stretch ratio %.4f"
                 % (r["fill"], plain["fill"], FILL_TOLERANCE_PT, plain["fill"] - FILL_TOLERANCE_PT,
                    r["outside"], r["limit_out"], r["aspect"]))
        r = fit(F, root, "wide15", 1.15, False)
        said = "over the limit" in r["out"]
        line(r["aspect"] == 1.0 and said, "wide15",
             "stretch ratio %.4f (must be 1), output says it is over the limit: %s (limit %s)"
             % (r["aspect"], said, "%.1f%%" % ((F.STRETCH_MAX_SKEW - 1) * 100)
                if hasattr(F, "STRETCH_MAX_SKEW") else "none"))
        if hasattr(F, "STRETCH_ON"):
            r = fit(F, root, "nostretch", 1.0, False, no_stretch=True)
            line(r["sha"] == plain["sha"], "nostretch",
                 "bytes with --no-stretch %s plain's (%s vs %s)"
                 % ("equal" if r["sha"] == plain["sha"] else "DIFFER from", r["sha"][:12], plain["sha"][:12]))
        else:
            line(False, "nostretch", "this fitter has no --no-stretch")
        if a.before:
            B = load(a.before, tmp)
            r = fit(B, root, "before", 1.0, False)
            line(r["sha"] == plain["sha"], "before",
                 "no-skew bytes of the older fitter %s this one's (%s vs %s)"
                 % ("equal" if r["sha"] == plain["sha"] else "DIFFER from", r["sha"][:12], plain["sha"][:12]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%s: %d failed check(s); read 1 donor, %d fitted cases"
          % ("FAIL" if fails else "PASS", fails, 5 + (1 if a.before else 0)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
