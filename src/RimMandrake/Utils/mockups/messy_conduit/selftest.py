#!/usr/bin/env python3
"""Selftest: renders small scenes in every style and checks they are non-empty,
correctly sized, deterministic, and that no strand vertex sits inside a blocked
(wall/machine/rock) cell that holds no conduit (risk register row 4). Then the nodal
cord model (§8.2, §8.7): node-reduction census, cords only between connected nodes,
never across a gap, no vertex in an unwalkable cell, determinism under unrelated
edits, and the tricky-configuration rules (tangle, needless spurs, wall terminals,
under rock/water/machines)."""
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
    # owner excursions (§8.6): big loops still never put a vertex in an unwalkable cell
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
    # nodal cord model (§8.2, §8.7)
    c2, f2 = nodal_checks()
    checks += c2
    fails += f2
    print(f"{checks - fails}/{checks} checks passed")
    return 1 if fails else 0


def nodal_checks():
    import nodal
    import tricky
    from scene import gap_scene, nodal_scene
    checks = fails = 0

    def check(ok, msg):
        nonlocal checks, fails
        checks += 1
        if not ok:
            fails += 1
            print("FAIL", msg)

    def conduit_components(net):
        comp, k = {}, 0
        for c in sorted(net.cells):
            if c in comp:
                continue
            stack = [c]
            comp[c] = k
            while stack:
                q = stack.pop()
                for n in net.nb[q]:
                    if n not in comp:
                        comp[n] = k
                        stack.append(n)
            k += 1
        return comp

    def cell_of_node(g, v):
        nd = g.nodes[v]
        return nd["cell"]
    # 1. node reduction on the main scene: exact census of node types and edge kinds
    net = render.Net(nodal_scene(), 1)
    g = nodal.reduce(net)
    types = sorted(nd["type"] for nd in g.nodes.values())
    want = sorted(["junction"] * 4 + ["terminal"] * 2 + ["battery", "source", "lamp"] + ["consumer"] * 3 +
                  ["stub_wall"] * 4 + ["stub_rock", "hidden_offmap"])
    check(types == want, f"nodal reduction census {types}")
    check(len(g.cord_edges()) == 13 and sum(e["kind"] == "hidden" for e in g.edges) == 3,
          f"edge census {len(g.cord_edges())} cord / {sum(e['kind'] == 'hidden' for e in g.edges)} hidden")
    # 2. cords only between truly connected nodes; never across the gap
    comp = conduit_components(net)
    bad = [e for e in g.cord_edges() if comp[cell_of_node(g, e["a"])] != comp[cell_of_node(g, e["b"])]]
    check(not bad, f"{len(bad)} cord edges join different conduit components")
    gaps = {frozenset([(12, 13), (14, 13)])}
    across = [e for e in g.edges if frozenset([cell_of_node(g, e["a"]), cell_of_node(g, e["b"])]) in gaps]
    check(not across, "a cord crosses the N13 gap")
    term = {nd["cell"]: nd for nd in g.nodes.values() if nd["type"] == "terminal"}
    check(set(term) == {(12, 13), (14, 13)} and term[(12, 13)]["live"] and not term[(14, 13)]["live"],
          "gap should give a live terminal at M13 and a dead one at O13")
    # 3. the small gap bed: two components -> two terminals, cords never span them
    gnet = render.Net(gap_scene(), 1)
    gg = nodal.reduce(gnet)
    gc = conduit_components(gnet)
    check(all(gc[cell_of_node(gg, e["a"])] == gc[cell_of_node(gg, e["b"])] for e in gg.cord_edges()),
          "gap bed: cord between unconnected nodes")
    check(sum(nd["type"] == "terminal" for nd in gg.nodes.values()) == 2, "gap bed: expected 2 terminals")
    # 4. laid geometry: no cord vertex inside an unwalkable cell (walls, rock, machines, water), any scene
    for sc in (nodal_scene(), tricky.downed_scene(), tricky.under_scene(), tricky.needless_scene()):
        n2 = render.Net(sc, 1)
        strands, ex = nodal.build_nodal(n2, STYLES["jawa"], dict(LEVELS["default"]), {})
        bad = sum(1 for s_ in strands for p in s_["pts"] if n2.blocked((int(math.floor(p[0])), int(math.floor(p[1]))))
                  and (int(math.floor(p[0])), int(math.floor(p[1]))) not in n2.cells)
        bad += sum(1 for s_ in strands for p in s_["pts"]
                   if (int(math.floor(p[0])), int(math.floor(p[1]))) in (n2.walls | n2.rock | n2.water))
        check(bad == 0, f"nodal geometry {sc['name']}: {bad} vertices in unwalkable cells")
    # 5. determinism, and an unrelated edit far away does not reshuffle a cord
    def cords(sc):
        n3 = render.Net(sc, 1)
        st, _ = nodal.build_nodal(n3, STYLES["jawa"], dict(LEVELS["default"]), {})
        return {round(float(s_["pts"][0][0]), 3): s_["pts"] for s_ in st}
    a1, a2 = cords(nodal_scene()), cords(nodal_scene())
    check(all(np.array_equal(a1[k], a2[k]) for k in a1), "nodal laying is not deterministic")
    sc_far = nodal_scene()
    sc_far["machines"] = sc_far["machines"] + [{"id": "far", "kind": "heater", "x": 24, "y": 0, "w": 1, "h": 1,
                                                "hookup": (25, 0)}]
    b1 = cords(sc_far)
    lamp_k = [k for k in a1 if abs(k - 5.5) < 0.6]
    check(bool(lamp_k) and all(k in b1 and np.array_equal(a1[k], b1[k]) for k in lamp_k),
          "an unrelated far-away edit reshuffled the lamp cords")
    # 6. tricky rules (§8.7)
    tg = nodal.reduce(render.Net(tricky.tangle_scene(), 1))
    check(sum(nd["type"] == "tangle" for nd in tg.nodes.values()) == 1 and len(tg.cord_edges()) == 4,
          f"lattice should be ONE tangle with 4 exit cords, got {len(tg.cord_edges())} cords")
    ng = nodal.reduce(render.Net(tricky.needless_scene(), 1))
    knots = sum(len(e["knots"]) for e in ng.cord_edges())
    check(knots == 3 and len(ng.spur_knots) == 2, f"needless conduit: {knots} knots, {len(ng.spur_knots)} spurs")
    check(sum(nd["type"] == "terminal" for nd in ng.nodes.values()) == 1, "the 4-cell spur must stay a terminal")
    dg = nodal.reduce(render.Net(tricky.downed_scene(), 1))
    wt = [nd for nd in dg.nodes.values() if nd.get("terminal")]
    check(len(wt) == 2 and sorted(nd["live"] for nd in wt) == [False, True], "downed: one live + one dead wall terminal")
    ug = nodal.reduce(render.Net(tricky.under_scene(), 1))
    ut = sorted(nd["type"] for nd in ug.nodes.values() if nd["type"].startswith("stub"))
    check(ut == ["stub_device"] * 2 + ["stub_rock"] * 2 + ["stub_water"] * 2, f"under: stubs {ut}")
    return checks, fails


if __name__ == "__main__":
    sys.exit(main())
