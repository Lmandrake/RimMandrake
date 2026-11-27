#!/usr/bin/env python3
"""selftest_terrain_wrap.py - terrain_wrap.py on synthetic textures and a synthetic manifest (no repo art read).

  1. tileable noise passes `check`;
  2. the same noise with a 1-px dark frame fails (the grid line our renders drew at every repeat);
  3. a texture whose content does not wrap (a ramp) fails;
  4. `heal` makes 2 and 3 pass, keeps size and mode, and changes no pixel of an already clean file's centre much;
  5. `manifest` passes a row whose bytes match, fails on changed bytes, on a REDO and on a framed terrain row,
     and passes a held row (bytes match, repair named by store sha) without measuring it.
"""
import hashlib
import json
import os
import sys
import tempfile

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import terrain_wrap as TW  # noqa: E402


def tileable(n=256, seed=1):
    rng = np.random.default_rng(seed)
    f = np.fft.fft2(rng.normal(size=(n, n)))
    k = np.hypot(*np.meshgrid(np.fft.fftfreq(n), np.fft.fftfreq(n)))
    img = np.real(np.fft.ifft2(f * np.exp(-(k * 40) ** 2)))     # periodic by construction
    img = (img - img.min()) / (img.max() - img.min()) * 120 + 60
    return np.stack([img, img * 0.9, img * 0.7], -1).astype(np.uint8)


def save(a, d, name, mode="RGB"):
    p = os.path.join(d, name)
    Image.fromarray(a, mode).save(p)
    return p


def main():
    fails = []

    def ok(cond, what):
        print(("PASS " if cond else "FAIL ") + what)
        if not cond:
            fails.append(what)

    with tempfile.TemporaryDirectory() as d:
        clean = tileable()
        p_clean = save(clean, d, "clean.png")
        ok(TW.problems(p_clean) == [], "tileable noise passes: %s" % TW.problems(p_clean))
        framed = clean.copy()
        framed[0] = framed[-1] = (framed[0] * 0.8).astype(np.uint8)
        framed[:, 0] = framed[:, -1] = (framed[:, 0] * 0.8).astype(np.uint8)
        p_framed = save(framed, d, "framed.png")
        ok(any("frame" in x for x in TW.problems(p_framed)), "1-px dark frame fails: %s" % TW.problems(p_framed))
        ramp = clean.astype(float)
        ramp += np.linspace(0, 40, ramp.shape[1])[None, :, None]
        p_ramp = save(np.clip(ramp, 0, 255).astype(np.uint8), d, "ramp.png")
        ok(any("wrap" in x for x in TW.problems(p_ramp)), "content that does not wrap fails: %s" % TW.problems(p_ramp))
        rgba = np.dstack([framed, np.full(framed.shape[:2], 255, np.uint8)])
        p_rgba = save(rgba, d, "framed_rgba.png", "RGBA")
        for src in (p_framed, p_ramp, p_rgba):
            out = src[:-4] + "_healed.png"
            TW.heal(src, out)
            a, b = Image.open(src), Image.open(out)
            ok(TW.problems(out) == [] and a.size == b.size and a.mode == b.mode,
               "heal repairs %s, same size and mode: %s" % (os.path.basename(src), TW.problems(out)))
        out = os.path.join(d, "clean_healed.png")
        TW.heal(p_clean, out)
        c = np.asarray(Image.open(out)).astype(float)[64:-64, 64:-64]
        ok(abs(c - clean.astype(float)[64:-64, 64:-64]).mean() < 25, "heal keeps a clean file's look (centre close)")

        def sha(p):
            return hashlib.sha256(open(p, "rb").read()).hexdigest()
        rows = [{"path": p_clean, "sha256": sha(p_clean), "verdict": "KEEP", "terrain": True}]
        man = os.path.join(d, "m.json")

        def run(rows):
            json.dump({"rows": rows}, open(man, "w"))
            return TW.check_manifest(man, root="/")
        ok(run(rows) == [], "manifest: matching KEEP terrain row passes")
        ok(run([dict(rows[0], sha256="0" * 64)]) != [], "manifest: changed bytes fail")
        ok(run([dict(rows[0], verdict="REDO")]) != [], "manifest: a REDO fails")
        ok(run([{"path": p_framed, "sha256": sha(p_framed), "verdict": "KEEP", "terrain": True}]) != [],
           "manifest: a framed terrain fails")
        ok(run([{"path": p_framed, "sha256": sha(p_framed), "verdict": "KEEP", "terrain": True,
                 "held": "Contagion", "repair_store_sha": "ab" * 32}]) == [],
           "manifest: a held row with its stored repair passes unmeasured")
        ok(run([{"path": p_framed, "sha256": sha(p_framed), "verdict": "KEEP", "terrain": True, "held": "X"}]) != [],
           "manifest: a held row without a stored repair fails")
        try:
            run([dict(rows[0], path=os.path.join(d, "gone.png"))])
            ok(False, "manifest: an unreadable picture raises Unreadable (exit 2), never a verdict")
        except TW.Unreadable:
            ok(True, "manifest: an unreadable picture raises Unreadable (exit 2), never a verdict")
        ok(TW.main(["manifest", os.path.join(d, "none.json")]) == 1, "manifest: a missing manifest exits 1 (need unmet)")
    print("%d failed" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
