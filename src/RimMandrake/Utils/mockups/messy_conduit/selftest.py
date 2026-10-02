#!/usr/bin/env python3
"""Selftest: renders small scenes in every style and checks they are non-empty,
correctly sized, deterministic, and that no strand vertex sits inside a blocked
(wall/machine/rock) cell that holds no conduit (risk register row 4)."""
import hashlib
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render  # noqa: E402
from scene import base_scene, break_scene  # noqa: E402
from styles import LEVEL_ORDER, STYLE_ORDER, STYLES, LEVELS  # noqa: E402


def main():
    fails = 0
    checks = 0
    sc = base_scene()
    for st in STYLE_ORDER:
        for lv in LEVEL_ORDER:
            net = render.Net(sc, 1)
            strands, ex = render.build_strands(net, STYLES[st], dict(LEVELS[lv]), {})
            checks += 1
            bad = 0
            for s in strands:
                for p in s["pts"]:
                    c = (int(math.floor(p[0])), int(math.floor(p[1])))
                    if net.blocked(c):
                        bad += 1
            if bad or not strands:
                fails += 1
                print(f"FAIL geometry {st}/{lv}: {bad} vertices in blocked cells, {len(strands)} strands")
    for st in STYLE_ORDER:
        a, info = render.render_scene(break_scene(), st, "default", cell_px=40, ss=1, seed=7)
        b, _ = render.render_scene(break_scene(), st, "default", cell_px=40, ss=1, seed=7)
        checks += 3
        if a.size != (9 * 40, 3 * 40):
            fails += 1
            print("FAIL size", st, a.size)
        arr = np.asarray(a, np.float32)
        if arr.std() < 5:
            fails += 1
            print("FAIL empty", st)
        if hashlib.sha1(a.tobytes()).digest() != hashlib.sha1(b.tobytes()).digest():
            fails += 1
            print("FAIL nondeterministic", st)
        if info["live_tips"] < 1:
            fails += 1
            checks += 1
            print("FAIL no live end", st)
    print(f"{checks - fails}/{checks} checks passed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
