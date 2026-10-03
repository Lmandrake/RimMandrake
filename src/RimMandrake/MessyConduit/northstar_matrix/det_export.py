#!/usr/bin/env python3
"""Export the matrix FLOOR scenes as STAGED worlds for the C# SelfTest's fresh-vs-incremental check.

    python3 src/RimMandrake/MessyConduit/northstar_matrix/det_export.py [--out <json>]

The live runner builds a board one def at a time (conduit, each transmitter def, each connector def, trees,
then the battery charge) and the map component rebuilds its cords between those calls, reusing its per-edge cache; the probe's
`fresh` command then lays the finished map with an EMPTY cache. A cord the cache carried across an op that
changed what the planner reads must come out the same as a fresh lay -- D2_fresh_builder_same, which was
RED on every ring board (2026-10-02). This writes each floor scene's cumulative world after every one of those calls,
in GAME coordinates at the isolation-run origin (12,12) (cords are seeded from absolute cells), to
Source/SelfTest/matrix_det_scenes.json; DeterminismChecks.cs replays the stages through ONE CordBuilder and
compares the last build with a fresh one, edge by edge.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MODDIR = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import design_spec as D  # noqa: E402
import scenes as S  # noqa: E402

OUT = os.path.join(MODDIR, "Source", "SelfTest", "matrix_det_scenes.json")
ORIGIN = (12, 12)
BUILD_ORDER = ("Battery", "WoodFiredGenerator", "PowerSwitch", "RM_AerialMast", "Heater", "ElectricSmelter", "StandingLamp")


def _g(sc, p, origin=ORIGIN):
    return [origin[0] + p[0], origin[1] + (sc["h"] - 1 - p[1])]


def _rect(sc, d, origin=ORIGIN):
    """Device footprint in game cells: x0, z0 (south-west), w, h (scene y is south)."""
    return [origin[0] + d["x"], origin[1] + (sc["h"] - 1 - (d["y"] + d["h"] - 1)), d["w"], d["h"]]


def staged(sc, origin=ORIGIN):
    conduit = [_g(sc, p, origin) for p in sc["conduit"]]
    cset = {tuple(c) for c in conduit}
    blocked = ([_g(sc, p, origin) + ["wall"] for p in sc["walls"]] + [_g(sc, p, origin) + ["rock"] for p in sc["rock"]] +
               [_g(sc, p, origin) + ["water"] for p in sc["water"] if tuple(_g(sc, p, origin)) not in cset])
    machines = []                                   # (def, machine) in spawn order
    charged = False
    for d in sorted(sc["devices"], key=lambda d: (not S.DEVICE_DEFS[d["role"]]["transmitter"], d["id"])):
        r = S.DEVICE_DEFS[d["role"]]
        x0, z0, w, h = _rect(sc, d, origin)
        if r["transmitter"]:
            hook = sorted({(x, z) for x in range(x0 - 1, x0 + w + 1) for z in range(z0 - 1, z0 + h + 1)
                           if ((x0 <= x < x0 + w) != (z0 <= z < z0 + h)) and (x, z) in cset})
            if hook:
                machines.append((r["def"], {"id": "t" + d["id"], "kind": r["type"], "x": x0, "z": z0, "w": w, "h": h,
                                            "hookups": [list(c) for c in hook]}))
            charged = charged or (d["role"] == "battery" and bool(d.get("charged")))
        elif d.get("hookup") is not None and tuple(_g(sc, d["hookup"], origin)) in cset:
            machines.append((r["def"], {"id": "c" + d["id"], "kind": "consumer", "x": x0, "z": z0, "w": w, "h": h,
                                        "hookups": [_g(sc, d["hookup"], origin)]}))
    trees = [_g(sc, p, origin) for p in sc["trees"]]
    out, cur = [], {"conduit": conduit, "blocked": blocked, "doors": [_g(sc, p, origin) for p in sc["doors"]],
                    "machines": [], "charged": False, "trees": []}
    out.append(dict(cur, stage="PowerConduit"))
    # run_live.py's order: one build_batch per def (TRANSMITTERS then CONNECTORS order), then trees, then charge
    for dn in BUILD_ORDER:
        ms = [m for d, m in machines if d == dn]
        if ms:
            cur = dict(cur, machines=cur["machines"] + ms)
            out.append(dict(cur, stage=dn))
    if trees:
        cur = dict(cur, trees=trees)
        out.append(dict(cur, stage="trees"))
    cur = dict(cur, charged=charged)
    out.append(dict(cur, stage="charge"))
    return out


def export():
    rows = D.floor_rows()
    scenes = []
    for k, r in enumerate(rows):
        spec, sc = D.floor_spec(r, k)
        scenes.append({"id": spec["id"], "topology": r["T"], "w": ORIGIN[0] + sc["w"] + 8, "h": ORIGIN[1] + sc["h"] + 8,
                       "settings": spec["settings"], "stages": staged(sc)})
    return {"generator": "src/RimMandrake/MessyConduit/northstar_matrix/det_export.py", "origin": list(ORIGIN),
            "build_order": list(BUILD_ORDER), "scenes": scenes}


def ring_split_scenes(data):
    """Ring scenes whose stages include a world where the heater has hooked the ring and the lamp has not yet:
    the state that makes the ring's two halves parallel edges, then splits one (the D2 ring defect)."""
    out = []
    for sc in data["scenes"]:
        if sc["topology"] != "ring":
            continue
        ids = [{m["id"] for m in st["machines"]} for st in sc["stages"]]
        if any("che" in i and "clamp" not in i for i in ids) and "clamp" in ids[-1]:
            out.append(sc["id"])
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args(argv)
    data = export()
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(data, f, sort_keys=True, separators=(",", ":"))
        f.write("\n")
    print("wrote %s (%d scenes)" % (a.out, len(data["scenes"])))


if __name__ == "__main__":
    main()
