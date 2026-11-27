#!/usr/bin/env python3
"""selftest_donor_specks.py: small detached pieces of a donor picture are not part of the reference.

    python3 Source/selftest_donor_specks.py [--before-check PATH] [--before-fit PATH]

Run from src/RimMandrake/WreckedMachines/. Dev tooling, not shipped. Exit 0 pass, 1 fail. One line per check, with
its value and its limit.

The fault (2026-11-27): the Medicine Granulator's donor east picture has 158 stray pixels at its bottom edge, 63 px
below the machine. check_sprite.py took the donor's bounding box with them, read a centre drift of 4.9% (limit 2%),
and failed every east picture of the granulator, however well it was drawn.

The donor here is the smelter's Repaired east picture (Textures/.../AutomatedSmelter/Repaired/; the donor's art as
shipped). `specks` is that picture with a stripe of SPECK_W x SPECK_H px added at the bottom edge of the canvas, like
the granulator's. Its MANIFEST measurements are pnglib.measure() of that file, as grab_source_art.py wrote them before
the rule (so the check must find the body in the file, not trust the MANIFEST's box).
  rule      check_sprite.donor_body drops exactly the stripe;
  keep      a detached block of KEEP_SHARE_PCT of the body (a real separate part) is kept;
  faithful  the plain picture checked against `specks`: no FAIL, drift within the check's limit;
  shift-y   the picture moved 5% of the canvas down; shift-x the same across: both must FAIL on drift;
  nostray   the plain donor (no stripe): the body is the whole picture, byte for byte;
  side      `side`: the same stripe stood upright at the LEFT canvas edge (it widens the donor's box, which sets
            the fitter's one-factor scale; the bottom stripe lies inside the body's width and does not): the plain
            picture checked against it has no FAIL;
  fit       a fitted copy (the picture scaled up 2.2 times on a larger canvas, fitted --inside) has the same bytes
            and the same fitter output (reference box, stretch decision, registration) against `specks` and against
            `side` as against the plain donor;
--before-check / --before-fit PATH: an older check_sprite.py / fit_sprite.py; its check lines and fit bytes against
the plain donor must equal this one's (a donor with no strays is checked and fitted as before).
"""
import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
SHORT, FILE = "AutomatedSmelter", "AutomatedSmelter_east.png"
DONOR = os.path.join(MOD, "Textures", "WreckedMachines", "Factories", SHORT, "Repaired", FILE)
MANIFEST = os.path.join(MOD, "art_source", SHORT, "MANIFEST.json")
# The granulator's stripe was 66 x 3 px (158 drawn), 63 px below the body. The smelter's body ends at y 446 of 512,
# so a stripe on the last three rows sits 63 px below it, the same gap.
SPECK_W, SPECK_H, SPECK_X = 66, 3, 280
SHIFT = 0.05           # the brief's "really shifted" picture: 5% of the canvas
KEEP_SHARE_PCT = 1.0   # a real separate part this big (share of the body) must stay in the reference
UPSCALE, CANVAS = 2.2, 1.3   # as selftest_fit_stretch.py: the size and canvas of a model picture

sys.path.insert(0, HERE)
from pnglib import read_png, write_rgba, measure      # noqa: E402


def load(path, name, tmp):
    """A tool by path, beside a pnglib.py and check_sprite.py from this folder."""
    d = os.path.join(tmp, name)
    os.makedirs(d, exist_ok=True)
    for f in ("pnglib.py", "check_sprite.py"):
        shutil.copy(os.path.join(HERE, f), os.path.join(d, f))
    dst = os.path.join(d, "fit_sprite.py" if name.startswith("fit") or name == "before_fit" else "check_sprite.py")
    shutil.copy(path, dst)
    spec = importlib.util.spec_from_file_location("under_test_%s" % name, dst)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, d)
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.path.remove(d)
    return mod


def shifted(w, h, rgba, dx, dy):
    out = bytearray(w * h * 4)
    for y in range(h):
        for x in range(w):
            sx, sy = x - dx, y - dy
            if 0 <= sx < w and 0 <= sy < h:
                out[(y * w + x) * 4:(y * w + x) * 4 + 4] = rgba[(sy * w + sx) * 4:(sy * w + sx) * 4 + 4]
    return out


def add_block(w, h, rgba, x0, y0, bw, bh):
    out = bytearray(rgba)
    for y in range(y0, y0 + bh):
        for x in range(x0, x0 + bw):
            out[(y * w + x) * 4:(y * w + x) * 4 + 4] = bytes((90, 90, 96, 255))
    return out


def make_root(root, donor_path):
    os.makedirs(os.path.join(root, SHORT, "restored"), exist_ok=True)
    man = json.load(open(MANIFEST, encoding="utf-8"))
    m = measure(donor_path)
    m["file"] = FILE
    man["measurements"] = {FILE: m}
    json.dump(man, open(os.path.join(root, SHORT, "MANIFEST.json"), "w"), indent=1)
    shutil.copy(donor_path, os.path.join(root, SHORT, "restored", FILE))
    return m


def check_lines(C, meta, cand, src):
    r = C.check_file(meta, cand, src)
    return r, ["%s %s" % (r.status, r.name)] + ["x " + f for f in r.fails] + ["! " + w for w in r.warns]


def model_copy(dst):
    """The donor's drawing cropped to its silhouette, scaled UPSCALE, centred on a larger transparent canvas."""
    from PIL import Image
    im = Image.open(DONOR).convert("RGBA")
    im = im.crop(im.getchannel("A").point(lambda a: 255 if a > 32 else 0).getbbox())
    im = im.resize((round(im.size[0] * UPSCALE), round(im.size[1] * UPSCALE)), Image.LANCZOS)
    bg = Image.new("RGBA", (round(im.size[0] * CANVAS), round(im.size[1] * CANVAS)), (0, 0, 0, 0))
    bg.alpha_composite(im, ((bg.size[0] - im.size[0]) // 2, (bg.size[1] - im.size[1]) // 2))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    bg.save(dst)


def fit_bytes(F, root, tier):
    cand = os.path.join(root, SHORT, tier, FILE)
    model_copy(cand)
    F.ART_SOURCE = root
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        F.fit_one(SHORT, tier, FILE, True, inside=True)
    return hashlib.sha256(open(cand, "rb").read()).hexdigest(), buf.getvalue()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", default=os.path.join(HERE, "check_sprite.py"))
    ap.add_argument("--fitter", default=os.path.join(HERE, "fit_sprite.py"))
    ap.add_argument("--before-check", help="an older check_sprite.py whose lines on a stray-free donor must equal")
    ap.add_argument("--before-fit", help="an older fit_sprite.py whose bytes on a stray-free donor must equal")
    ap.add_argument("--skip-fit", action="store_true", help="the check cases only (fast)")
    a = ap.parse_args()
    tmp = tempfile.mkdtemp(prefix="donorspecks_")
    fails = 0
    n = 0

    def line(ok, name, text):
        nonlocal fails, n
        n += 1
        fails += 0 if ok else 1
        print("%s  %-9s %s" % ("PASS" if ok else "FAIL", name, text))

    try:
        C = load(a.check, "check", tmp)
        w, h, plain = read_png(DONOR)
        body_px = sum(1 for i in range(w * h) if plain[i * 4 + 3])
        sp = add_block(w, h, plain, SPECK_X, h - SPECK_H, SPECK_W, SPECK_H)
        stripe_px = SPECK_W * SPECK_H
        specks_path = os.path.join(tmp, "specks_" + FILE)
        write_rgba(specks_path, w, h, sp)
        print("check %s; donor %s %dx%d, body %d px; stripe %d px (%.3f%% of the body) at y %d-%d"
              % (a.check, os.path.relpath(DONOR, MOD), w, h, body_px, stripe_px, 100.0 * stripe_px / body_px,
                 h - SPECK_H, h - 1))

        # rule / keep
        db = getattr(C, "donor_body", None)
        if db is None:
            line(False, "rule", "this check_sprite.py has no donor_body (the donor's body rule)")
            line(False, "keep", "this check_sprite.py has no donor_body")
        else:
            _, dropped = db(w, h, sp)
            line(dropped == stripe_px, "rule", "dropped %d px of the stripe's %d (limit: a piece under %.2f%% of "
                 "the body)" % (dropped, stripe_px, C.DONOR_SPECK_SHARE_PCT))
            side = int((body_px * KEEP_SHARE_PCT / 100.0) ** 0.5) + 1
            kb = add_block(w, h, plain, 2, 2, side, side)    # top-left corner, clear of the smelter (bbox from x 54)
            _, kd = db(w, h, kb)
            line(kd == 0, "keep", "a detached %dx%d block (%.2f%% of the body) dropped %d px (must be 0)"
                 % (side, side, 100.0 * side * side / body_px, kd))

        # faithful / shift
        root_s = os.path.join(tmp, "specks")
        meta_s = make_root(root_s, specks_path)
        src_s = os.path.join(root_s, SHORT, "restored", FILE)
        lim = C.CENTRE_DRIFT_TOLERANCE * 100
        r, ls = check_lines(C, meta_s, DONOR, src_s)
        line(r.status != "FAIL" and r.drift is not None and r.drift <= lim, "faithful",
             "status %s, drift %.2f%% (limit %.0f%%), outside %s, fill %s%s"
             % (r.status, r.drift if r.drift is not None else -1, lim,
                "%.2f%%" % r.outside if r.outside is not None else "-",
                "%.2f%%" % r.fill if r.fill is not None else "-",
                "" if r.status != "FAIL" else "; " + "; ".join(r.fails)))
        for name, dx, dy in (("shift-y", 0, int(round(SHIFT * h))), ("shift-x", int(round(SHIFT * w)), 0)):
            p = os.path.join(tmp, name + ".png")
            write_rgba(p, w, h, shifted(w, h, plain, dx, dy))
            r, _ = check_lines(C, meta_s, p, src_s)
            line(r.status == "FAIL" and r.drift is not None and r.drift > lim, name,
                 "moved %d,%d px: status %s, drift %.2f%% (limit %.0f%%; must FAIL)"
                 % (dx, dy, r.status, r.drift if r.drift is not None else -1, lim))

        side_path = os.path.join(tmp, "side_" + FILE)
        write_rgba(side_path, w, h, add_block(w, h, plain, 0, (h - SPECK_W) // 2, SPECK_H, SPECK_W))
        root_d = os.path.join(tmp, "side")
        meta_d = make_root(root_d, side_path)
        r, _ = check_lines(C, meta_d, DONOR, os.path.join(root_d, SHORT, "restored", FILE))
        line(r.status != "FAIL" and r.drift is not None and r.drift <= lim, "side",
             "status %s, drift %.2f%% (limit %.0f%%)%s" % (r.status, r.drift if r.drift is not None else -1, lim,
                                                         "" if r.status != "FAIL" else "; " + "; ".join(r.fails)))

        # nostray
        root_p = os.path.join(tmp, "plain")
        meta_p = make_root(root_p, DONOR)
        src_p = os.path.join(root_p, SHORT, "restored", FILE)
        cand_p = os.path.join(MOD, "Textures", "WreckedMachines", "Factories", SHORT, "Wrecked", FILE)
        if db is not None:
            same, dropped = db(w, h, plain)
            line(dropped == 0 and bytes(same) == bytes(plain), "nostray",
                 "plain donor: dropped %d px (must be 0), body %s the picture"
                 % (dropped, "equals" if bytes(same) == bytes(plain) else "DIFFERS from"))
        else:
            line(False, "nostray", "this check_sprite.py has no donor_body")
        _, now = check_lines(C, meta_p, cand_p, src_p)
        if a.before_check:
            B = load(a.before_check, "before_check", tmp)
            _, old = check_lines(B, meta_p, cand_p, src_p)
            line(now == old, "nostray", "Wrecked east vs plain donor: %d check line(s) %s the older check's"
                 % (len(now), "equal" if now == old else "DIFFER from"))

        # fit
        if not a.skip_fit:
            F = load(a.fitter, "fit", tmp)
            sha_p, out_p = fit_bytes(F, root_p, "fitted")
            ref_p = [x.strip() for x in out_p.splitlines() if "vs reference" in x]
            for name, root_x in (("fit", root_s), ("fit-side", root_d)):
                sha_x, out_x = fit_bytes(F, root_x, "fitted")
                ref_x = [x.strip() for x in out_x.splitlines() if "vs reference" in x]
                diff = [x for x in out_x.splitlines() if x not in out_p.splitlines()]
                line(sha_x == sha_p and out_x == out_p, name,
                     "fitted copy against the %s donor: bytes %s, %d output line(s) differ from the plain donor's "
                     "(must be 0); reference line %s"
                     % ("bottom-stripe" if name == "fit" else "side-stripe",
                        "equal" if sha_x == sha_p else "DIFFER (%s vs %s)" % (sha_x[:12], sha_p[:12]), len(diff),
                        "equal" if ref_x == ref_p else "%r vs %r" % (ref_x[:1], ref_p[:1])))
            if a.before_fit:
                Bf = load(a.before_fit, "before_fit", tmp)
                sha_b, _ = fit_bytes(Bf, root_p, "fitted_before")
                line(sha_b == sha_p, "fit", "plain donor: this fitter's bytes %s the older fitter's (%s vs %s)"
                     % ("equal" if sha_b == sha_p else "DIFFER from", sha_p[:12], sha_b[:12]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%s: %d failed check(s) of %d" % ("FAIL" if fails else "PASS", fails, n))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
