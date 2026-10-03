"""ORACLE: the expected node graph of a scene, computed with the existing Python nodal reducer.

    expect(sc, level="ropey")      -> what the live census should read (graph level only: no geometry)
    nodal_reference(sc)            -> nodal.reduce() on the scene with the mock-up's OWN liveness, for the
                                      cross-check that this wrapper does not change the reducer's answers

Two things the mock-up models differently from the game, corrected here (both read from
src/RimMandrake/MessyConduit/Source/CordWorldAdapter.cs):
  1. Transmitter buildings (battery, generator, switch) hook to EVERY cardinally adjacent conduit cell and join
     those cells into one power net. The mock-up has one hookup per machine and propagates power only along
     conduit, so each transmitter becomes one mock-up machine per hookup (merged back into one node here) and
     liveness is computed here by union over conduit adjacency + transmitter bridges, then handed to the reducer.
  2. A device footprint is buried (stub_device) only if the pathgrid is unwalkable there. Every device we place is
     PassThroughOnly/Standable, so its footprint is given to the reducer as zero-size (never blocks).
Lamps census as "consumer" in game (the adapter never emits Lamp): `node_types_live` applies that mapping.
"""
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
MOCK = os.path.join(REPO, "src", "RimMandrake", "Utils", "mockups", "messy_conduit")
if MOCK not in sys.path:
    sys.path.insert(0, MOCK)
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import nodal  # noqa: E402
import render  # noqa: E402
import scenes as S  # noqa: E402

# tangle level -> MessyConduitSettings fields (slider ranges from MessyConduitMod.cs: slack 0..1.8,
# sprawlCap 2..40, cordsPerConnection 1..3). `tangles` stays true at every level so the GRAPH is level-invariant.
LEVELS = {
    "tidy": {"slack": 0.2, "sprawlCap": 3.0, "cordsPerConnection": 1},
    "ropey": {"slack": 1.0, "sprawlCap": 16.0, "cordsPerConnection": 3},     # = shipped defaults
    "ratsnest": {"slack": 1.8, "sprawlCap": 40.0, "cordsPerConnection": 3},
}
TANGLE_STRAND_ALLOWANCE = 32      # per tangle node: UNVERIFIED upper allowance for tangle strands in `strands`


def _is_tx(d):
    return S.DEVICE_DEFS[d["role"]]["transmitter"]


def _active_devices(sc, with_aerial):
    out = []
    for d in sc["devices"]:
        if d["role"] == "switch" and not d.get("on", True):
            continue                          # a switch flicked off transmits nothing: no node, no bridge
        out.append(d)
    if with_aerial and sc.get("aerial"):
        dead = set(sc["aerial"].get("killed", []))
        for k, p in enumerate(sc["aerial"]["poles"]):
            if k in dead:
                continue                      # anchor destroyed: gone from the map
            out.append({"id": "pole%d" % k, "role": "pole", "x": p[0], "y": p[1], "w": 1, "h": 1, "hookup": None})
    return out


def _hookups(sc, d):
    if d["role"] == "pole" or _is_tx(d):
        return S.transmitter_hookups(sc, d)
    return [tuple(d["hookup"])] if d.get("hookup") is not None else []


def liveness(sc, with_aerial=False):
    """Union-find over conduit adjacency + transmitter bridges (+ uncut aerial spans). Returns
    (live conduit cells, {device id: live})."""
    cs = [tuple(p) for p in sc["conduit"]]
    parent = {}

    def f(a):
        parent.setdefault(a, a)
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def u(a, b):
        parent[f(a)] = f(b)
    cset = set(cs)
    for c in cs:
        f(("c", c))
        for q in S._nb4(c):
            if q in cset:
                u(("c", c), ("c", q))
    devs = _active_devices(sc, with_aerial)
    for d in devs:
        f(("d", d["id"]))
        if d["role"] == "pole" or _is_tx(d):
            for h in _hookups(sc, d):
                u(("d", d["id"]), ("c", h))
    if with_aerial and sc.get("aerial"):
        cut = set(sc["aerial"]["cut"])
        dead = set(sc["aerial"].get("killed", []))
        for k, (i, j) in enumerate(sc["aerial"]["spans"]):
            if k not in cut and i not in dead and j not in dead:
                u(("d", "pole%d" % i), ("d", "pole%d" % j))
    src = set()
    for d in devs:
        if (d["role"] == "battery" and d.get("charged")) or (d["role"] == "generator" and d.get("active")):
            src.add(f(("d", d["id"])))
    live = {c for c in cs if f(("c", c)) in src}
    dlive = {}
    for d in devs:
        if d["role"] == "pole" or _is_tx(d):
            dlive[d["id"]] = f(("d", d["id"])) in src
        else:
            hk = _hookups(sc, d)
            dlive[d["id"]] = bool(hk) and hk[0] in live
    return live, dlive


def to_nodal(sc, with_aerial=False, own_liveness=False, real_footprints=False):
    """The scene in the mock-up's dict format (scene.py). own_liveness: mark sources so the mock-up's Net computes
    liveness itself (used only by nodal_reference). real_footprints: keep device sizes (for the mock-up RENDERER,
    which draws machines; never for the graph, where it would wrongly bury conduit under walkable devices)."""
    machines, lamps = [], []
    for d in _active_devices(sc, with_aerial):
        hk = _hookups(sc, d)
        role = d["role"]
        kind = "battery" if role == "battery" else "lamp" if role == "lamp" else role
        src = own_liveness and ((role == "battery" and d.get("charged")) or (role == "generator" and d.get("active")))
        for k, h in enumerate(hk):
            machines.append({"id": "%s#%d" % (d["id"], k), "kind": kind, "x": d["x"], "y": d["y"], "w": d["w"] if real_footprints else 0,
                             "h": d["h"] if real_footprints else 0,
                             "hookup": tuple(h), "source": bool(src), "_dev": d["id"], "_role": role})
    return {"name": sc["name"], "w": sc["w"], "h": sc["h"], "indoor": [],
            "walls": [tuple(p) for p in sc["walls"]], "doors": [tuple(p) for p in sc["doors"]],
            "rock": [tuple(p) for p in sc["rock"]], "water": [tuple(p) for p in sc["water"]],
            "machines": machines, "lamps": lamps, "trees": [{"x": p[0], "y": p[1]} for p in sc["trees"]],
            "items": [], "conduit": [tuple(p) for p in sc["conduit"]]}


TYPE_OF_ROLE = {"battery": "battery", "generator": "source", "switch": "transmitter", "consumer": "consumer",
                "bench": "consumer", "lamp": "lamp", "pole": "transmitter"}


def _reduce(sc, with_aerial, own_liveness, tangle_min=None):
    """tangle_min: the C# BuildOptions threshold (CordBuilder: Tangles ? TangleMin : int.MaxValue). None = the
    shipped 9; a huge number = tangles OFF (dense fields then reduce to junction blobs)."""
    nsc = to_nodal(sc, with_aerial, own_liveness)
    net = render.Net(nsc, 1)
    if not own_liveness:
        net.live = liveness(sc, with_aerial)[0]
    old = nodal.TANGLE_MIN
    try:
        if tangle_min is not None:
            nodal.TANGLE_MIN = tangle_min
        return nodal.reduce(net)
    finally:
        nodal.TANGLE_MIN = old


def _summary(g, use_roles):
    def label(v):
        nd = g.nodes[v]
        if v[0] == "m":
            m = g.machine_of[v]
            t = TYPE_OF_ROLE[m["_role"]] if use_roles else nd["type"]
            return [t, "dev:" + m["_dev"]]
        return [nd["type"], int(nd["cell"][0]), int(nd["cell"][1])]
    types = Counter()
    seen_dev = set()
    for v, nd in g.nodes.items():
        if v[0] == "m":
            m = g.machine_of[v]
            if m["_dev"] in seen_dev:
                continue
            seen_dev.add(m["_dev"])
            types[TYPE_OF_ROLE[m["_role"]] if use_roles else nd["type"]] += 1
        else:
            types[nd["type"]] += 1
    ends = sorted(sorted([label(e["a"]), label(e["b"])], key=repr) for e in g.cord_edges())
    ends = sorted(ends, key=repr)
    return {
        "node_types": dict(sorted(types.items())),
        "cord_edges": len(g.cord_edges()),
        "hidden_edges": sum(e["kind"] == "hidden" for e in g.edges),
        "cord_ends": ends,
        "knots": sum(len(e["knots"]) for e in g.cord_edges()),
        "spurs": len(g.spur_knots),
        "terminals": sorted([[int(nd["cell"][0]), int(nd["cell"][1]), bool(nd["live"]), bool(nd.get("gap"))]
                             for nd in g.nodes.values() if nd["type"] == "terminal"]),
        "wall_terminals": sorted([[int(nd["cell"][0]), int(nd["cell"][1]), bool(nd["live"])]
                                  for nd in g.nodes.values() if nd.get("terminal")]),
        "tangles": sum(1 for nd in g.nodes.values() if nd["type"] == "tangle"),
    }


def expect(sc, level="ropey", with_aerial=False, tangle_min=None):
    g = _reduce(sc, with_aerial, own_liveness=False, tangle_min=tangle_min)
    out = _summary(g, use_roles=True)
    live, dlive = liveness(sc, with_aerial)
    out["node_types_live"] = dict(sorted(Counter(
        {("consumer" if k == "lamp" else k): 0 for k in out["node_types"]}).items()))
    for k, n in out["node_types"].items():
        out["node_types_live"]["consumer" if k == "lamp" else k] += n
    out["conduit_cells"] = len(sc["conduit"])
    out["live_cells"] = len(live)
    out["devices_live"] = dict(sorted(dlive.items()))
    cmax = LEVELS[level]["cordsPerConnection"]
    out["strands_bounds"] = [out["cord_edges"], cmax * out["cord_edges"] + TANGLE_STRAND_ALLOWANCE * out["tangles"]]
    out["cords_across_nets"] = 0           # M2: a cord only ever joins cells of one net
    return out


def nets(sc, with_aerial=False):
    """Number of power nets: components of conduit cells + transmitter devices (+ uncut spans)."""
    cs = {tuple(p) for p in sc["conduit"]}
    parent = {}

    def f(a):
        parent.setdefault(a, a)
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for c in cs:
        f(("c", c))
        for q in S._nb4(c):
            if q in cs:
                parent[f(("c", c))] = f(("c", q))
    for d in _active_devices(sc, with_aerial):
        if d["role"] == "pole" or _is_tx(d):
            f(("d", d["id"]))
            for h in _hookups(sc, d):
                parent[f(("d", d["id"]))] = f(("c", h))
    if with_aerial and sc.get("aerial"):
        cut = set(sc["aerial"]["cut"])
        dead = set(sc["aerial"].get("killed", []))
        for k, (i, j) in enumerate(sc["aerial"]["spans"]):
            if k not in cut and i not in dead and j not in dead:
                parent[f(("d", "pole%d" % i))] = f(("d", "pole%d" % j))
    return len({f(k) for k in list(parent)})


def aerial_expect(sc):
    if not sc.get("aerial"):
        return None
    _, dl = liveness(sc, with_aerial=True)
    a = sc["aerial"]
    cut = set(a["cut"])
    dangling = []
    for k in sorted(cut):
        i, j = a["spans"][k]
        dangling += [{"pole": i, "live": dl.get("pole%d" % i)}, {"pole": j, "live": dl.get("pole%d" % j)}]
    return {"status": "UNBUILT (RM_AerialMast not built; phase-2 design 2.3)", "poles": len(a["poles"]), "spans": len(a["spans"]),
            "cut_spans": len(cut), "pole_live": [dl.get("pole%d" % k) for k in range(len(a["poles"]))],
            "dangling_span_ends": dangling, "far_consumer_live": dl.get("h_air")}


def hose_expect(sc):
    if not sc.get("hose"):
        return None
    return {"cells": len(sc["hose"]["cells"]), "inflation": sc["hose"]["inflation"],
            "state": {"flat": "Flat", "plump": "Plump"}[sc["hose"]["inflation"]], "cord_edges_touching_hose": 0}


def full(sc, level="ropey"):
    """Everything the live runner compares, for one scene."""
    return {"graph": expect(sc, level), "graph_with_aerial": expect(sc, level, True) if sc.get("aerial") else None,
            "aerial": aerial_expect(sc), "hose": hose_expect(sc)}


def bridging_transmitters(sc):
    """Transmitter devices that join two otherwise-separate conduit components (the case where the mock-up's own
    liveness and the game's differ)."""
    cs = {tuple(p) for p in sc["conduit"]}
    comp = {}
    for c in sorted(cs):
        if c in comp:
            continue
        st = [c]
        comp[c] = c
        while st:
            q = st.pop()
            for n in S._nb4(q):
                if n in cs and n not in comp:
                    comp[n] = c
                    st.append(n)
    out = []
    for d in _active_devices(sc, False):
        if _is_tx(d) and len({comp[h] for h in S.transmitter_hookups(sc, d)}) > 1:
            out.append(d["id"])
    return out


def nodal_reference(sc):
    """nodal.reduce with the mock-up's own liveness (sources marked, Net._live): the reducer's unaided answer."""
    return _summary(_reduce(sc, False, own_liveness=True), use_roles=False)


def compare_with_reference(sc):
    """[] if this oracle agrees with the unaided reducer on every graph field (machine-node TYPE labels excepted:
    the reducer calls a charged battery 'source'). Only meaningful when no transmitter bridges two components."""
    if bridging_transmitters(sc):
        return None
    a = expect(sc)
    b = nodal_reference(sc)
    diffs = []
    for k in ("cord_edges", "hidden_edges", "knots", "spurs", "terminals", "wall_terminals", "tangles"):
        if a[k] != b[k]:
            diffs.append((k, a[k], b[k]))
    na = sum(v for k, v in a["node_types"].items() if k not in ("battery", "source", "consumer", "lamp", "transmitter"))
    nb = sum(v for k, v in b["node_types"].items() if k not in ("battery", "source", "consumer", "lamp", "transmitter"))
    if na != nb:
        diffs.append(("non-machine nodes", na, nb))

    def strip(ends):
        return sorted(sorted([e[0][1:] if e[0][1:2] and str(e[0][1]).startswith("dev:") else e[0],
                              e[1][1:] if e[1][1:2] and str(e[1][1]).startswith("dev:") else e[1]], key=repr)
                      for e in ends)
    if sorted(map(repr, strip(a["cord_ends"]))) != sorted(map(repr, strip(b["cord_ends"]))):
        diffs.append(("cord_ends", len(a["cord_ends"]), len(b["cord_ends"])))
    return diffs
