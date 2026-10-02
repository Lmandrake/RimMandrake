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
    # load-proportional bundles (§8.10)
    import load
    for state in ("day", "day_off", "night"):
        lsc = load.load_scene(state)
        net = render.Net(lsc, 1, load=True)
        inj, dev = load.injections(net)
        fk = load.solve_kirchhoff(net, inj)
        checks += 1
        worst = max(abs(sum(fk.get((c, q), 0) for q in net.nb[c] if q in net.live) - inj.get(c, 0))
                    for c in net.live)
        if worst > 1e-6:
            fails += 1
            print(f"FAIL kirchhoff conservation {state}: {worst}")
        model = load.make_model(lsc, 250)(net, STYLES["jawa"], 1)
        checks += 1
        if not all(1 <= n <= 10 for n in model["n"]):
            fails += 1
            print("FAIL strand range", state, model["n"])
        # every junction: matched pairs never join two strands flowing the same way
        checks += 1
        for J, (sl, pairs, loose) in model["plan"].items():
            if any(sl[a]["io"] == sl[b]["io"] for a, b in pairs):
                fails += 1
                print("FAIL junction matching", state, J)
                break
    # a tree net: Kirchhoff == spanning tree
    tsc = load.load_scene("day")
    tsc["conduit"] = [c for c in tsc["conduit"] if c not in [(7, 6), (8, 6), (7, 7)]]
    tsc["lamps"] = []
    tnet = render.Net(tsc, 1, load=True)
    ti, _ = load.injections(tnet)
    a_, b_ = load.solve_kirchhoff(tnet, ti), load.solve_tree(tnet, ti)
    checks += 1
    if max(abs(a_[k] - b_.get(k, 0)) for k in a_) > 1e-6:
        fails += 1
        print("FAIL tree: kirchhoff != subtree sums")
    checks += 1
    seq, prev = [], None
    for w in [740, 755, 748, 752, 745, 760, 700, 610]:
        prev = load.strands_hyst(w, prev, 250)
        seq.append(prev)
    if seq != [3, 4, 4, 4, 4, 4, 3, 3]:
        fails += 1
        print("FAIL hysteresis", seq)
    # owner excursions (§8.11): big loops still never put a vertex in an unwalkable cell
    from scene import sprawl_scene
    ssc = sprawl_scene()
    for st in ("jawa", "extcord"):
        net = render.Net(ssc, 1)
        strands, ex = render.build_strands(net, STYLES[st], dict(LEVELS["default"], loop_p=0, coil_p=0),
                                           {"sprawl": {"slack": 0.9, "cap": 2.6, "loops": 0.16, "heap_p": 0.35,
                                                       "iters": 70}})
        checks += 1
        bad = 0
        for s_ in strands:
            for p in s_["pts"]:
                c = (int(math.floor(p[0])), int(math.floor(p[1])))
                if net.blocked(c):
                    bad += 1
        if bad:
            fails += 1
            print(f"FAIL sprawl geometry {st}: {bad} vertices in unwalkable cells")
    print(f"{checks - fails}/{checks} checks passed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
