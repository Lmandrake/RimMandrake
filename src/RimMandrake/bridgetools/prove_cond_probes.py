"""CONDPROBES_WIRE_ENGINE_READS live proof (build_spec bridge_conditions_2026-11-06 §2 T2). Read-only except A1's one
staged FlowWorks cell (below); nothing is spawned or advanced. The game must be Playing a map and PAUSED: every comparison is refused unless all its reads carry the
same ticksGame, because a moving pawn or a turning sky would make two honest reads differ.

  python.exe src/RimMandrake/bridgetools/prove_cond_probes.py --clause A1   cond_eval values == the existing read tools
  python.exe src/RimMandrake/bridgetools/prove_cond_probes.py --clause A2   bad defName / OOB cell / bad pawn: named refusals
  python.exe src/RimMandrake/bridgetools/prove_cond_probes.py --clause A3   no FlowWorks: fw.* reads status unbound

A1 (a list WITH FlowWorks): for 12 cells (up to 8 FlowWorks cells that are dug, filled or a source, found with
    flowworks_excavation_rect onlyNonZero, the rest spread over the map; when the map has none, ONE cell near the centre
    is dug 2 and filled 1 with jawa/flowworks_excavation_drive first, the only write, printed as MUTATION) jawa/cond_eval's cell.glow and cell.roofed equal
    jawa/glow_at's groundGlow and roofed; cell.terrain equals jawa/get_terrain_layers top; fw.depth, fw.fill and fw.source
    equal flowworks_excavation_rect dEff, fEff and isSource (the DepthAt/FillAt/IsSourceCell getters); map.sky_glow and
    game.hour equal glow_at's skyGlow and hour; game.tick equals ticksGame; pawn.pos x/z equals jawa/pawn_get position
    for up to 6 spawned pawns (at least one). Every probe reads status ok.
    Blind guards: at least one compared cell has FlowWorks depth > 0 and fill > 0 and at least one has groundGlow > 0
    (an all-zero comparison proves nothing: UNMEASURED); glow_at's mapId equals the mapId cond_eval pinned.
A2: map.count of a def that does not exist is refused `bind` naming the def; a cell one past the map edge is refused
    `cell_oob`; an unknown pawn is refused `bind` naming it; a thing.field path with a call is refused `field_method`;
    and the same map.count over a def that does exist evaluates ok (the refusal is not blanket).
A3 (a list WITHOUT FlowWorks, tier `bridge`): fw.fill, fw.depth and fw.source at the map centre read status `unbound`
    with a detail naming FlowWorks, the tree's status is unbound (UNKNOWN, never false), and cell.glow in the same tree
    reads ok (the instrument can see).

Exit 0 holds, 1 does not, 2 UNMEASURED: <reason> (no map, not paused, nothing to compare, a tool absent, wrong list).
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(HERE, "..", "Utils")
for _p in (UTILS, os.path.join(UTILS, "modcheck")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

TOL = 1e-5
NOSUCH_DEF = "RM_CondProbe_NoSuchDef"
NOSUCH_PAWN = "CondProbeNoSuchPawn424242"


class Unmeasured(Exception):
    pass


class Bridge(object):
    def __init__(self):
        import rimbridge_client as rb
        h, p, t = rb.resolve_endpoint()
        self.c = rb.RimBridge(host=h, port=p, token=t, timeout=120)
        self.c.connect()
        self.ticks = set()

    def call(self, tool, **p):
        r = self.c.call(tool, p, check=False)
        r = r if isinstance(r, dict) else {}
        tg = r.get("ticksGame")
        if isinstance(tg, (int, float)) and tg >= 0:
            self.ticks.add(int(tg))
        return r


def _need(r, what):
    if not r.get("success"):
        raise Unmeasured("%s failed: %s" % (what, str(r)[:300]))
    return r


def _still(b, what):
    if len(b.ticks) > 1:
        raise Unmeasured("the game advanced during %s (ticksGame %s): pause it" % (what, sorted(b.ticks)))


def _map(b):
    mi = b.call("jawa/map_info")
    sx, sz = int(mi.get("sizeX") or 0), int(mi.get("sizeZ") or mi.get("sizeY") or 0)
    if sx <= 20 or sz <= 20:
        raise Unmeasured("no map (map_info %s)" % str(mi)[:200])
    return sx, sz


def _sentinel(p):
    """A cmp whose only job is to make the probe read: its pv is what we compare."""
    if p in ("cell.terrain",):
        return ["!=", "__cond_probe__"]
    if p in ("cell.is_water", "cell.roofed", "cell.fire", "fw.source"):
        return ["==", True]
    return [">=", -1e9]


def node(nid, probe):
    op, lit = _sentinel(probe["p"])
    return {"id": nid, "cmp": [probe, op, lit]}


def cond_eval(b, nodes):
    tree = {"any": nodes} if len(nodes) > 1 else nodes[0]
    r = b.call("jawa/cond_eval", tree=json.dumps(tree))
    if "refused" not in r and "values" not in r:
        raise Unmeasured("jawa/cond_eval absent or failed (companion older than this item?): %s" % str(r)[:300])
    return r


def by_id(r):
    return {v.get("id"): v for v in (r.get("values") or []) if isinstance(v, dict)}


def same(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return a is b or a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(float(a) - float(b)) <= TOL
    return a == b


# ------------------------------------------------------------------------------------------------ A1
CELL_PROBES = ("cell.glow", "cell.roofed", "cell.terrain", "cell.is_water", "fw.depth", "fw.fill", "fw.source",
               "cell.temp", "cell.fire")


def _fw_cells(b, sx, sz, want):
    found, step = [], 90
    for z0 in range(0, sz, step):
        for x0 in range(0, sx, step):
            w, h = min(step, sx - x0), min(step, sz - z0)
            r = b.call("jawa/flowworks_excavation_rect", x=x0, z=z0, w=w, h=h, onlyNonZero=True, includeTerrain=False)
            if not r.get("success"):
                raise Unmeasured("flowworks_excavation_rect failed (is FlowWorks on this list?): %s" % str(r)[:300])
            for row in r.get("rows") or []:
                if len(found) < want:
                    found.append((int(row["x"]), int(row["z"])))
            if len(found) >= want:
                return found
    return found


def _dug_filled(b, c):
    r = b.call("jawa/flowworks_excavation_rect", x=c[0], z=c[1], w=1, h=1, onlyNonZero=False, includeTerrain=False)
    row = (r.get("rows") or [{}])[0]
    return bool(row.get("dEff")) and bool(row.get("fEff"))


def clause_a1(b):
    sx, sz = _map(b)
    b.ticks.clear()
    fw = _fw_cells(b, sx, sz, 8)
    if not any(_dug_filled(b, c) for c in fw):
        sx0, sz0 = sx // 2 + 9, sz // 2 + 9
        d = b.call("jawa/flowworks_excavation_drive", x=sx0, z=sz0, deepenLevels=2, setBodyWaterM=0.5)
        print("MUTATION: flowworks_excavation_drive %d,%d deepenLevels=2 setBodyWaterM=0.5 -> %s" % (sx0, sz0, str(d)[:200]))
        if not d.get("success"):
            raise Unmeasured("no dug, filled FlowWorks cell on the map and staging one failed: %s" % str(d)[:300])
        fw = [(sx0, sz0)] + fw[:7]
    spread = [(sx // 2, sz // 2), (1, 1), (sx - 2, sz - 2), (sx // 3, 2 * sz // 3), (2 * sx // 3, sz // 3),
              (sx // 4, sz // 4), (3 * sx // 4, 3 * sz // 4), (sx // 2 + 5, sz // 2 - 5)]
    cells = list(dict.fromkeys(fw + spread))[:12]
    print("cells: %d FlowWorks non-zero + %d spread: %s" % (len(fw), len(cells) - len(fw), cells))
    fails = []
    reads = 0
    # cond_eval in batches of 6 cells (9 probes each + root, under the 64-node cap)
    cv = {}
    for i in range(0, len(cells), 6):
        nodes = []
        for (x, z) in cells[i:i + 6]:
            for p in CELL_PROBES:
                nodes.append(node("%s@%d,%d" % (p, x, z), {"p": p, "cell": [x, z]}))
        r = cond_eval(b, nodes)
        if r.get("refused"):
            fails.append("cond_eval refused a valid tree: %s" % str(r)[:300])
            continue
        cv.update(by_id(r))
    mnodes = [node("map.sky_glow", {"p": "map.sky_glow"}), node("game.hour", {"p": "game.hour"}),
              node("game.tick", {"p": "game.tick"})]
    rm = cond_eval(b, mnodes)
    cv.update(by_id(rm))
    for k, v in sorted(cv.items()):
        if k and v.get("status") != "ok":
            if k.startswith("fw.") and v.get("status") == "unbound":
                raise Unmeasured("fw.* reads unbound: FlowWorks is not on this list (%s)" % v.get("detail"))
            fails.append("%s status %s (%s)" % (k, v.get("status"), v.get("detail")))
    # the existing tools
    glow = _need(b.call("jawa/glow_at", cells=";".join("%d,%d" % c for c in cells)), "glow_at")
    gl = {(int(c["x"]), int(c["z"])): c for c in glow.get("cells") or []}
    terr = {}
    fwr = {}
    for (x, z) in cells:
        t = _need(b.call("jawa/get_terrain_layers", rect="%d,%d,1,1" % (x, z)), "get_terrain_layers")
        terr[(x, z)] = (t.get("cells") or [{}])[0].get("top")
        f = _need(b.call("jawa/flowworks_excavation_rect", x=x, z=z, w=1, h=1, onlyNonZero=False, includeTerrain=False),
                  "flowworks_excavation_rect")
        fwr[(x, z)] = (f.get("rows") or [{}])[0]

    def cmp(key, got, want, tool):
        nonlocal_reads[0] += 1
        if not same(got, want):
            fails.append("%s: cond_eval %r != %s %r" % (key, got, tool, want))

    nonlocal_reads = [0]
    for (x, z) in cells:
        k = lambda p: cv.get("%s@%d,%d" % (p, x, z), {}).get("pv")
        g = gl.get((x, z))
        if g is None:
            fails.append("glow_at returned no row for %d,%d" % (x, z))
        else:
            cmp("cell.glow@%d,%d" % (x, z), k("cell.glow"), g.get("groundGlow"), "glow_at.groundGlow")
            cmp("cell.roofed@%d,%d" % (x, z), k("cell.roofed"), g.get("roofed"), "glow_at.roofed")
        cmp("cell.terrain@%d,%d" % (x, z), k("cell.terrain"), terr.get((x, z)), "get_terrain_layers.top")
        row = fwr.get((x, z)) or {}
        cmp("fw.depth@%d,%d" % (x, z), k("fw.depth"), row.get("dEff"), "flowworks_excavation_rect.dEff")
        cmp("fw.fill@%d,%d" % (x, z), k("fw.fill"), row.get("fEff"), "flowworks_excavation_rect.fEff")
        cmp("fw.source@%d,%d" % (x, z), k("fw.source"), row.get("isSource"), "flowworks_excavation_rect.isSource")
    cmp("map.sky_glow", cv.get("map.sky_glow", {}).get("pv"), glow.get("skyGlow"), "glow_at.skyGlow")
    cmp("game.hour", cv.get("game.hour", {}).get("pv"), glow.get("hour"), "glow_at.hour")
    cmp("game.tick", cv.get("game.tick", {}).get("pv"), glow.get("ticksGame"), "glow_at.ticksGame")
    filled = sum(1 for c in cells if (fwr.get(c) or {}).get("dEff") and (fwr.get(c) or {}).get("fEff"))
    lit = sum(1 for c in cells if ((gl.get(c) or {}).get("groundGlow") or 0) > 0)
    roofed = sum(1 for c in cells if (gl.get(c) or {}).get("roofed"))
    print("compared cells: %d with FlowWorks depth and fill, %d with groundGlow > 0, %d roofed" % (filled, lit, roofed))
    if not filled:
        raise Unmeasured("no compared cell has FlowWorks depth > 0 and fill > 0: the fw comparison would be 0 == 0")
    if not lit:
        raise Unmeasured("every compared cell has groundGlow 0 (night, unlit?): the glow comparison would be 0 == 0")
    pinned = (rm.get("canonical") or {}).get("mapId")
    if pinned is None or glow.get("mapId") is None or int(pinned) != int(glow.get("mapId")):
        fails.append("cond_eval pinned mapId %r but glow_at read map %r" % (pinned, glow.get("mapId")))
    # pawns
    lst = _need(b.call("jawa/pawn_get"), "pawn_get listing")
    pawns = [p for p in (lst.get("pawns") or []) if p.get("thingId")][:6]
    if not pawns:
        raise Unmeasured("no spawned pawn to compare pawn.pos against")
    pnodes = []
    for p in pawns:
        for f in ("x", "z"):
            pnodes.append(node("pawn.pos.%s@%s" % (f, p["thingId"]), {"p": "pawn.pos", "pawn": p["thingId"], "f": f}))
    rp = cond_eval(b, pnodes)
    if rp.get("refused"):
        fails.append("cond_eval refused the pawn tree: %s" % str(rp)[:300])
    pv = by_id(rp)
    for p in pawns:
        one = _need(b.call("jawa/pawn_get", pawn=p["thingId"]), "pawn_get " + p["thingId"])
        snap = (one.get("pawns") or [{}])[0]
        pos = snap.get("position") or {}
        for f in ("x", "z"):
            rec = pv.get("pawn.pos.%s@%s" % (f, p["thingId"]), {})
            if rec.get("status") != "ok":
                fails.append("pawn.pos.%s@%s status %s (%s)" % (f, p["thingId"], rec.get("status"), rec.get("detail")))
            cmp("pawn.pos.%s@%s" % (f, p["thingId"]), rec.get("pv"), pos.get(f), "pawn_get.position")
    _still(b, "A1")
    print("A1: %d comparisons over %d cells, %d pawns, tick %s" % (nonlocal_reads[0], len(cells), len(pawns),
                                                                   sorted(b.ticks)))
    return fails


# ------------------------------------------------------------------------------------------------ A2
def clause_a2(b):
    sx, sz = _map(b)
    fails = []
    cases = [
        ("bad defName", {"cmp": [{"p": "map.count", "def": NOSUCH_DEF}, ">=", 0]}, "bind", NOSUCH_DEF),
        ("OOB cell", {"cmp": [{"p": "cell.glow", "cell": [sx, 0]}, ">=", 0]}, "cell_oob", "%d,0" % sx),
        ("bad pawn", {"cmp": [{"p": "pawn.pos", "pawn": NOSUCH_PAWN, "f": "x"}, ">=", 0]}, "bind", NOSUCH_PAWN),
        ("field method", {"cmp": [{"p": "thing.field", "thing": "x", "path": "GetHashCode()"}, "==", 1]},
         "field_method", "GetHashCode()"),
    ]
    for what, tree, name, needle in cases:
        r = cond_eval(b, [tree])
        print("%s: refused=%s at=%s detail=%s" % (what, r.get("refused"), r.get("at"), r.get("detail")))
        if r.get("refused") != name or needle not in str(r.get("detail")) or r.get("success") is not False:
            fails.append("%s: want refused %s naming %s, got %s" % (what, name, needle, str(r)[:300]))
    # the refusal is not blanket: a def that exists binds and reads ok
    things = b.call("jawa/list_things", rect="0,0,%d,%d" % (sx, sz), limit=1)
    rows = things.get("things") or things.get("rows") or []
    real = rows[0].get("def") if rows and isinstance(rows[0], dict) else None
    real = real or "Steel"
    r = cond_eval(b, [{"cmp": [{"p": "map.count", "def": real}, ">=", 0]}])
    print("real def %s: success=%s status=%s v=%s" % (real, r.get("success"), r.get("status"), r.get("v")))
    if r.get("refused") or r.get("status") != "ok":
        fails.append("map.count over existing def %s did not read ok: %s" % (real, str(r)[:300]))
    return fails


# ------------------------------------------------------------------------------------------------ A3
def clause_a3(b):
    sx, sz = _map(b)
    x, z = sx // 2, sz // 2
    nodes = [node(p, {"p": p, "cell": [x, z]}) for p in ("fw.fill", "fw.depth", "fw.source", "cell.glow")]
    r = cond_eval(b, [{"all": nodes}])
    if r.get("refused"):
        return ["cond_eval refused a valid tree: %s" % str(r)[:300]]
    v = by_id(r)
    print("A3 at %d,%d: tree status=%s v=%s; %s" % (x, z, r.get("status"), r.get("v"),
                                                    {k: (w.get("status"), w.get("detail")) for k, w in v.items() if k}))
    if any(v.get(p, {}).get("status") == "ok" for p in ("fw.fill", "fw.depth", "fw.source")):
        raise Unmeasured("fw.* read ok: FlowWorks IS on this list; A3 needs a list without it (tier bridge)")
    if v.get("cell.glow", {}).get("status") != "ok":
        raise Unmeasured("cell.glow did not read ok, so the instrument cannot see: %s" % v.get("cell.glow"))
    fails = []
    for p in ("fw.fill", "fw.depth", "fw.source"):
        w = v.get(p, {})
        if w.get("status") != "unbound" or "FlowWorks" not in str(w.get("detail")):
            fails.append("%s: want status unbound naming FlowWorks, got %s" % (p, w))
    if r.get("status") != "unbound" or r.get("v") is not None:
        fails.append("tree: want status unbound and v null (UNKNOWN), got status %s v %s" % (r.get("status"), r.get("v")))
    return fails


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--clause", required=True, choices=("A1", "A2", "A3"))
    a = ap.parse_args(argv)
    try:
        b = Bridge()
        fails = {"A1": clause_a1, "A2": clause_a2, "A3": clause_a3}[a.clause](b)
    except Unmeasured as e:
        print("UNMEASURED: %s" % e)
        return 2
    except Exception as e:  # a bridge that cannot be asked is not a verdict
        print("UNMEASURED: %s: %s" % (type(e).__name__, str(e)[:300]))
        return 2
    for f in fails:
        print("FAIL " + f)
    print("%s %s" % (a.clause, "HOLDS" if not fails else "DOES NOT HOLD (%d)" % len(fails)))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
