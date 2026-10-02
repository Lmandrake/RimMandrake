#!/usr/bin/env python3
"""Owner excursions mock-up (design §8.11): 'cap 0.38' (the phase-0 routing) against the owner's
big walkability-aware slack loops, on a scene with real open floor.

    python3 sprawl.py --out <dir> [--seed 1] [--ss 2] [--cell 64]
"""
import argparse
import os
import sys
import time

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render  # noqa: E402
from scene import SPRAWL_KEY, sprawl_scene  # noqa: E402
from styles import STYLES  # noqa: E402

OWNER = {"slack": 0.9, "cap": 2.6, "loops": 0.16, "heap_p": 0.35, "iters": 70}


def render_pair(style, level, seed, ss, cell, sprawl_prm=None):
    sc = sprawl_scene()
    out = []
    t0 = time.time()
    a, _ = render.render_scene(sc, style, level, cell, ss, seed, 0, {})
    t1 = time.time()
    b, info = render.render_scene(sc, style, level, cell, ss, seed, 0,
                                  {"sprawl": sprawl_prm or OWNER, "level_over": {"loop_p": 0.0, "coil_p": 0.0}})
    t2 = time.time()
    key = "   ".join(f"{k}: {v}" for k, v in SPRAWL_KEY[:3])
    key2 = "   ".join(f"{k}: {v}" for k, v in SPRAWL_KEY[3:])
    out.append(render.frame_scene(a, sc, "BEFORE  -  phase-0 routing, sprawl capped at 0.38 cell",
                                  f"{STYLES[style]['title']}, level {level}; render {t1 - t0:.1f} s", cell, key))
    out.append(render.frame_scene(
        b, sc, "AFTER  -  owner excursions: slack 0.9 (cable 1.9x the run), loops/figure-8s/heaps up to 2.6 cells",
        f"relaxed-rope settle: inextensible, bend-smoothed, pushed OUT of unwalkable cells (piles against walls/rock); "
        f"render {t2 - t1:.1f} s", cell, key2))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--ss", type=int, default=2)
    ap.add_argument("--cell", type=int, default=64)
    ap.add_argument("--only", default="")
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    written = []
    for style, level, tag in (("jawa", "default", "jawa"), ("extcord", "tidy", "extcord")):
        if a.only and tag not in a.only.split(","):
            continue
        pan = render_pair(style, level, a.seed, a.ss, a.cell)
        body = render.grid(pan, 1)
        img = render.titled(body, f"06 sprawl: cap 0.38 vs owner excursions  -  {STYLES[style]['title']}",
                            "Owner, 2026-10-02: 'much larger excursions that avoid unwalkable areas or even pile up "
                            "against them' (reference: 00_owner_reference_orange_cord.png)")
        p = os.path.join(a.out, f"06_sprawl_{tag}.png")
        img.save(p, optimize=True)
        written.append(p)
        print("wrote", p, flush=True)
    return written


if __name__ == "__main__":
    main()
