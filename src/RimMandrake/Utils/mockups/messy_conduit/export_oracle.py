#!/usr/bin/env python3
"""Export the nodal-model test scenes and the Python oracle's answers for the C# SelfTest.

    python3 export_oracle.py [--out <json>]

Default out: src/RimMandrake/GimmeSomeSlack/Source/SelfTest/oracle_scenes.json

The C# port (src/RimMandrake/GimmeSomeSlack/Source/Core/) must reproduce, for every scene, the
GRAPH-level answers of nodal.reduce(): node-type census, cord/hidden edge counts, the endpoint
pairs of every cord edge (by node type and cell), knot and pruned-spur counts, terminals with their
live flag, and wall terminals. Laid geometry is NOT compared point-for-point: phase 1a lays slack
with canned shapes instead of the PBD settle (design §8.10), so the C# side asserts geometric
PROPERTIES instead (no vertex in an unwalkable cell, determinism, unrelated-edit stability).
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nodal  # noqa: E402
import render  # noqa: E402
import rope  # noqa: E402
import tricky  # noqa: E402
from scene import gap_scene, nodal_scene  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
DEFAULT_OUT = os.path.join(REPO, "src", "RimMandrake", "MessyConduit", "Source", "SelfTest", "oracle_scenes.json")


def scene_json(sc):
    net = render.Net(sc, 1)
    blocked = []
    for y in range(sc["h"]):
        for x in range(sc["w"]):
            c = (x, y)
            if rope.unwalkable(net, c):
                kind = "rock" if c in net.rock else "water" if c in net.water else \
                    "device" if c in net.machine_cells else "wall"
                blocked.append([x, y, kind])
    machines = [{"id": m["id"], "kind": "source" if m.get("source") else
                 ("battery" if m["kind"] == "battery" else "consumer"),
                 "x": m["x"], "y": m["y"], "w": m["w"], "h": m["h"], "hookup": list(m["hookup"])}
                for m in sc["machines"]]
    machines += [{"id": f"lamp{k}", "kind": "lamp", "x": lp["x"], "y": lp["y"], "w": 1, "h": 1,
                  "hookup": list(lp["hookup"])} for k, lp in enumerate(sc["lamps"])]
    return {"name": sc["name"], "w": sc["w"], "h": sc["h"], "conduit": [list(c) for c in sorted(net.cells)],
            "blocked": blocked, "doors": [list(d) for d in sc["doors"]],
            "trees": [[t["x"], t["y"]] for t in sc["trees"]], "machines": machines,
            "sources": [list(m["hookup"]) for m in sc["machines"] if m.get("source")] if not sc.get("power_off") else []}


def expect(sc):
    net = render.Net(sc, 1)
    g = nodal.reduce(net)

    def cellof(v):
        return list(g.nodes[v]["cell"])
    ends = []
    for e in g.cord_edges():
        a = [g.nodes[e["a"]]["type"], *cellof(e["a"])]
        b = [g.nodes[e["b"]]["type"], *cellof(e["b"])]
        ends.append(sorted([a, b]))
    ends.sort()
    return {
        "types": sorted(nd["type"] for nd in g.nodes.values()),
        "cord_edges": len(g.cord_edges()),
        "hidden_edges": sum(e["kind"] == "hidden" for e in g.edges),
        "cord_ends": ends,
        "knots": sum(len(e["knots"]) for e in g.cord_edges()),
        "spurs": len(g.spur_knots),
        "terminals": sorted([[*nd["cell"], bool(nd["live"])] for nd in g.nodes.values() if nd["type"] == "terminal"]),
        "wall_terminals": sorted([[*nd["cell"], bool(nd["live"])] for nd in g.nodes.values() if nd.get("terminal")]),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=DEFAULT_OUT)
    a = ap.parse_args(argv)
    scenes = [nodal_scene(), gap_scene(), tricky.downed_scene(), tricky.under_scene(), tricky.needless_scene(),
              tricky.tangle_scene(), tricky.tangle_scene(power_off=True)]
    scenes[-1]["name"] = "tangle_off"
    out = [{"scene": scene_json(sc), "expect": expect(sc)} for sc in scenes]
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as f:
        json.dump({"generator": "src/RimMandrake/Utils/mockups/messy_conduit/export_oracle.py", "scenes": out}, f,
                  indent=1)
    print(f"wrote {a.out}: {len(out)} scenes")


if __name__ == "__main__":
    main()
