#!/usr/bin/env python3
"""Bank stake + silt-trap art build (RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS fixes 8 and 10; owner 2026-10-17 by card:
"Commission REVIEW.md items 3,4,6,7,8,9,10 in four styles; judged in game").

raw/<Look>_{post,ridge_h,ridge_v,baffle}.png and raw/silt_wedge.png (codex $imagegen, generate.sh)  ->  out/
  <Look>/RM_BankStake          128x128  the lamp post on its earth footing (drawn 0.8 cell)
  <Look>/RM_BankStakeRidge_h   128x48   levee span between two stakes side by side (one period of the raw, seamless E-W)
  <Look>/RM_BankStakeRidge_v   64x128   levee span between two stakes one above the other (seamless N-S)
  <Look>/RM_SiltTrap           128x128  the baffle with its wet waterline (drawn 1.2 cells, as before)
  RM_SiltWedge                 128x128  look-free silt deposit, broad edge at the bottom, tip up (code turns the tip upstream)
Usage: build.py [Look ...]"""
import importlib.util
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("weirbuild", HERE.parent / "Weir" / "build.py")
W = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(W)
LOOKS = W.LOOKS
CELL = 128


def bbox_crop(im, floor=40):
    a = np.array(im)[..., 3] > floor
    ys, xs = np.nonzero(a)
    return im.crop((int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1))


def fit(src, box, canvas):
    crop = bbox_crop(src)
    cw, ch = crop.size
    s = min(box[0] / cw, box[1] / ch)
    crop = W.resize(crop, (max(1, round(cw * s)), max(1, round(ch * s))))
    out = Image.new("RGBA", canvas, (0, 0, 0, 0))
    out.alpha_composite(crop, ((canvas[0] - crop.size[0]) // 2, (canvas[1] - crop.size[1]) // 2))
    return out


def one_period_h(src, h):
    """The raw ridge spans two crib periods across its full width: take the left half (one period), make it seamless
    at CELL wide, and centre it vertically in an h-tall canvas."""
    band = bbox_crop(src)
    bw, bh = band.size
    half = band.crop((0, 0, bw // 2, bh))
    strip = W.seamless_h(half, CELL, round(bh * CELL / (bw // 2)))
    out = Image.new("RGBA", (CELL, h), (0, 0, 0, 0))
    out.alpha_composite(strip, (0, max(0, (h - strip.size[1]) // 2)))
    return out


def one_period_v(src, w):
    band = bbox_crop(src)
    bw, bh = band.size
    half = band.crop((0, 0, bw, bh // 2))
    strip = W.seamless_v(half, round(bw * CELL / (bh // 2)), CELL)
    out = Image.new("RGBA", (w, CELL), (0, 0, 0, 0))
    out.alpha_composite(strip, (max(0, (w - strip.size[0]) // 2), 0))
    return out


def build(look):
    raw = HERE / "raw"
    out = HERE / "out" / look
    out.mkdir(parents=True, exist_ok=True)
    op = lambda n: Image.open(raw / f"{look}_{n}.png").convert("RGBA")
    W.clean_alpha(fit(op("post"), (120, 120), (CELL, CELL))).save(out / "RM_BankStake.png")
    W.clean_alpha(one_period_h(op("ridge_h"), 48)).save(out / "RM_BankStakeRidge_h.png")
    W.clean_alpha(one_period_v(op("ridge_v"), 64)).save(out / "RM_BankStakeRidge_v.png")
    W.clean_alpha(fit(op("baffle"), (124, 124), (CELL, CELL))).save(out / "RM_SiltTrap.png")
    print(look, "ok")


def build_wedge():
    src = Image.open(HERE / "raw" / "silt_wedge.png").convert("RGBA")
    im = fit(src, (CELL, CELL), (CELL, CELL))
    a = np.array(im).astype(np.float32)
    a[..., 3] *= 0.92          # a deposit on the ground, a touch see-through so the bank texture reads through its edge
    Image.fromarray(a.astype(np.uint8)).save(HERE / "out" / "RM_SiltWedge.png")


if __name__ == "__main__":
    (HERE / "out").mkdir(exist_ok=True)
    for lk in (sys.argv[1:] or LOOKS):
        build(lk)
    build_wedge()
