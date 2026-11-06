#!/usr/bin/env python3
"""selftest_cond_probes.py - offline half of CONDPROBES_WIRE_ENGINE_READS (bridge_conditions build_spec §2 T2).

The Verse probe source (JawaBench.BridgeTools/JawaBenchCondProbes.cs) cannot run without the game, so this checks what
can be checked without it, and prove_cond_probes.py carries the live clauses (A1 values, A2 refusals, A3 unbound):

  1. every v1 probe the core declares (JawaBenchCondCore.Probes) has its own Verse read (`case "<name>":` in Bind),
     except ring.count, which is refused at bind naming RINGPROBES_WIRE_EVENT_CURSORS;
  2. IProbeSource hands the source the compiled Probe (so a probe is pinned to its MapId; the key holds no map), and
     the Verse source reads Find.CurrentMap only in CurrentMap() (the default at compile), never per read;
  3. the source is read-only: no RNG, no spawn/destroy/set, no Invoke or SetValue;
  4. its non-ok statuses are the named set gone|oob|unbound|error, and FlowWorks absence is `unbound`;
  5. jawa/cond_eval is declared and is in northstar_driver/tool_schemas.json (lint_calls needs it);
  6. prove_cond_probes.py, against a fake bridge, holds on a consistent world and does NOT hold (or says UNMEASURED)
     on a world where one tool disagrees, FlowWorks is absent from A1's list, or FlowWorks is present on A3's.

Exit 0 all pass, 1 a failure.
"""
import contextlib
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "JawaBench.BridgeTools")
CORE = os.path.join(SRC, "JawaBenchCondCore.cs")
PROBES = os.path.join(SRC, "JawaBenchCondProbes.cs")
SCHEMAS = os.path.join(HERE, "..", "Utils", "northstar_driver", "tool_schemas.json")
sys.path.insert(0, HERE)

FAILS = []


def check(ok, what, detail=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", what, (": " + detail) if (detail and not ok) else ""))
    if not ok:
        FAILS.append(what)


def strip_comments(s):
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    return re.sub(r"//[^\n]*", "", s)


def static_checks():
    core = open(CORE, encoding="utf-8").read()
    src = open(PROBES, encoding="utf-8").read()
    code = strip_comments(src)
    block = core[core.index("Dictionary<string, ProbeInfo> Probes"):]
    block = block[:block.index("};")]
    names = re.findall(r'\{\s*"([a-z_.]+)",\s*new ProbeInfo', block)
    check(len(names) >= 20, "core declares the v1 probe set", "found %d: %s" % (len(names), names))
    cases = set(re.findall(r'case "([a-z_.]+)":', code))
    missing = [n for n in names if n not in cases]
    check(not missing, "every core probe has a Verse read case", "missing %s" % missing)
    ring = re.search(r'case "ring\.count":\s*why = "([^"]*)";\s*return null;', code)
    check(bool(ring) and "RINGPROBES_WIRE_EVENT_CURSORS" in ring.group(1), "ring.count is refused at bind, naming its item")
    check("pawn.flight" not in code and "pawn.anim" not in code, "no flight/anim probe in the Verse source")

    iface = core[core.index("internal interface IProbeSource"):]
    iface = iface[:iface.index("}")]
    check("string Refuse(string key, JawaBenchCondCore.Probe p);" in iface
          and "CondRead Read(string key, JawaBenchCondCore.Probe p, int x, int z);" in iface,
          "IProbeSource passes the compiled Probe (map pinning)")
    check("public string Refuse(string key, JawaBenchCondCore.Probe p)" in code
          and "public CondRead Read(string key, JawaBenchCondCore.Probe p, int x, int z)" in code,
          "VerseProbeSource implements the pinned interface")
    cm = [m.start() for m in re.finditer(r"Find\.CurrentMap", code)]
    cur = code.index("public int CurrentMap()")
    check(len(cm) == 1 and cur < cm[0] < cur + 200, "Find.CurrentMap only in CurrentMap()", "at %s" % cm)
    check(code.count("p.MapId") >= 1 and "MapById(mapId)" in code, "reads resolve the probe's own MapId")

    banned = [r"\bRand\.", r"\.SetValue\(", r"\.Invoke\(", r"GenSpawn", r"\.Destroy\(", r"DeSpawn\(", r"SetTerrain",
              r"\.DoSingleTick", r"TickManager\.(CurTimeSpeed|Pause|Toggle)", r"\.SetRoof", r"Notify_"]
    hits = [b for b in banned if re.search(b, code)]
    check(not hits, "the Verse source is read-only", "uses %s" % hits)
    sts = set(re.findall(r'St\("([a-z_]+)"', code))
    check(sts and sts <= {"gone", "oob", "unbound", "error"}, "non-ok statuses are the named set", str(sorted(sts)))
    fw = code[code.index("static FwReads FwFor"):]
    check('"FlowWorks is not loaded' in fw and 'St("unbound", err)' in code, "FlowWorks absent reads unbound, naming it")
    check(re.search(r'\[Tool\(\s*"jawa/cond_eval"', src) is not None, "jawa/cond_eval is declared")
    check("JawaBenchCondCore.CondEval(spec, NewProbeSource())" in code, "cond_eval runs the core over the Verse source")
    try:
        t = json.load(open(SCHEMAS, encoding="utf-8"))["tools"].get("jawa/cond_eval") or {}
    except (OSError, ValueError) as e:
        t = {"err": str(e)}
    check(sorted(t.get("parameters") or []) == ["mapId", "tree"], "tool_schemas.json lists jawa/cond_eval(tree, mapId)",
          str(t))


# ------------------------------------------------------------------------------------------------ fake bridge
class World(object):
    def __init__(self, fw=True, glow_skew=0.0, blank_fw=False, dark=False, moving=False):
        self.sx = self.sz = 100
        self.fw = fw
        self.glow_skew = glow_skew
        self.blank_fw = blank_fw
        self.dark = dark
        self.moving = moving
        self.staged = {}
        self.tick = 1000

    def glow(self, x, z):
        return 0.0 if self.dark else round(((x * 7 + z * 3) % 10) / 10.0, 3)

    def roofed(self, x, z):
        return (x + z) % 5 == 0

    def terrain(self, x, z):
        return "WaterShallow" if x == 50 else "Sand"

    def fwrow(self, x, z):
        if (x, z) in self.staged:
            d, f = self.staged[(x, z)]
        else:
            d = 2 if (x, z) == (10, 10) and not self.blank_fw else 0
            f = 1 if d else 0
        src = (x, z) == (20, 20) and not self.blank_fw
        return {"x": x, "z": z, "d": d, "f": f, "dEff": d, "fEff": f, "isSource": src}

    def probe(self, p):
        n, c = p["p"], p.get("cell")
        if n.startswith("fw.") and not self.fw:
            return None, "unbound", "FlowWorks is not loaded (RimMandrake.FlowWorks.RM_MapComponent_Excavation does not resolve)"
        if c:
            x, z = c
            row = self.fwrow(x, z)
            v = {"cell.glow": self.glow(x, z), "cell.roofed": self.roofed(x, z), "cell.terrain": self.terrain(x, z),
                 "cell.is_water": self.terrain(x, z).startswith("Water"), "fw.depth": float(row["dEff"]),
                 "fw.fill": float(row["fEff"]), "fw.source": row["isSource"], "cell.temp": 21.5, "cell.fire": False}[n]
            return v, "ok", ""
        if n == "map.sky_glow":
            return 0.8, "ok", ""
        if n == "game.hour":
            return 9.25, "ok", ""
        if n == "game.tick":
            return float(self.tick), "ok", ""
        if n == "map.count":
            return 3.0, "ok", ""
        if n == "pawn.pos":
            i = int(p["pawn"][5:])
            return float(i if p["f"] == "x" else i + 1), "ok", ""
        return None, "error", "fake has no " + n


class FakeBridge(object):
    def __init__(self, w):
        self.w = w
        self.ticks = set()

    def call(self, tool, **p):
        w = self.w
        if w.moving:
            w.tick += 1
        self.ticks.add(w.tick)
        if tool == "jawa/map_info":
            return {"sizeX": w.sx, "sizeZ": w.sz}
        if tool == "jawa/flowworks_excavation_rect":
            if not w.fw:
                return {"success": False, "message": "FlowWorks is not loaded"}
            rows = []
            for z in range(p["z"], p["z"] + p["h"]):
                for x in range(p["x"], p["x"] + p["w"]):
                    r = w.fwrow(x, z)
                    if not p.get("onlyNonZero") or r["d"] or r["isSource"]:
                        rows.append(r)
            return {"success": True, "rows": rows, "ticksGame": w.tick}
        if tool == "jawa/flowworks_excavation_drive":
            w.staged[(p["x"], p["z"])] = (p["deepenLevels"], min(p["setFill"], p["deepenLevels"]))
            return {"success": True, "ticksGame": w.tick}
        if tool == "jawa/glow_at":
            cells = [tuple(int(v) for v in c.split(",")) for c in p["cells"].split(";")]
            return {"success": True, "skyGlow": 0.8, "hour": 9.25, "ticksGame": w.tick, "mapId": 0,
                    "cells": [{"x": x, "z": z, "groundGlow": w.glow(x, z) + w.glow_skew, "roofed": w.roofed(x, z)}
                              for x, z in cells]}
        if tool == "jawa/get_terrain_layers":
            x, z = (int(v) for v in p["rect"].split(",")[:2])
            return {"success": True, "cells": [{"x": x, "z": z, "top": w.terrain(x, z)}]}
        if tool == "jawa/pawn_get":
            if not p.get("pawn"):
                return {"success": True, "pawns": [{"thingId": "Human%d" % i} for i in (30, 40)], "ticksGame": w.tick}
            i = int(p["pawn"][5:])
            return {"success": True, "pawns": [{"position": {"x": i, "z": i + 1}}]}
        if tool == "jawa/list_things":
            return {"success": True, "things": [{"def": "Steel"}]}
        if tool == "jawa/cond_eval":
            return self.cond_eval(json.loads(p["tree"]))
        return {"success": False, "message": "fake has no " + tool}

    def cond_eval(self, tree):
        w = self.w
        nodes = tree["any"] if "any" in tree else tree["all"] if "all" in tree else [tree]
        if len(nodes) == 1 and ("all" in nodes[0] or "any" in nodes[0]):
            nodes = nodes[0].get("all") or nodes[0].get("any")
        vals, worst = [], "ok"
        for n in nodes:
            pr = n["cmp"][0]
            if pr["p"] == "map.count" and pr["def"] != "Steel":
                return {"success": False, "refused": "bind", "at": "$.tree", "detail": "no ThingDef named '%s'" % pr["def"]}
            if pr["p"] == "pawn.pos" and not pr["pawn"].startswith("Human"):
                return {"success": False, "refused": "bind", "at": "$.tree", "detail": "no pawn '%s'" % pr["pawn"]}
            if pr["p"] == "thing.field" and "(" in pr["path"]:
                return {"success": False, "refused": "field_method", "at": "$.tree.cmp[0].path",
                        "detail": "fields and properties only: " + pr["path"]}
            c = pr.get("cell")
            if c and not (0 <= c[0] < w.sx and 0 <= c[1] < w.sz):
                return {"success": False, "refused": "cell_oob", "at": "$.tree.cmp[0].cell",
                        "detail": "%d,%d outside %dx%d" % (c[0], c[1], w.sx, w.sz)}
            v, st, de = w.probe(pr)
            rec = {"id": n.get("id"), "pv": v, "status": st, "v": True if st == "ok" else None}
            if st != "ok":
                rec["detail"] = de
                worst = st
            vals.append(rec)
        return {"success": True, "status": worst, "v": None if worst != "ok" else True, "values": vals,
                "canonical": {"mapId": 0.0, "tree": tree},
                "ticksGame": w.tick}


def run_clause(clause, world):
    import prove_cond_probes as pc
    real = pc.Bridge
    pc.Bridge = lambda: FakeBridge(world)
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            rc = pc.main(["--clause", clause])
    finally:
        pc.Bridge = real
    return rc, buf.getvalue()


def fake_checks():
    for clause, world, want, what in [
        ("A1", World(), 0, "A1 holds on a consistent world"),
        ("A1", World(glow_skew=0.01), 1, "A1 does not hold when glow_at disagrees"),
        ("A1", World(fw=False), 2, "A1 is UNMEASURED without FlowWorks"),
        ("A1", World(blank_fw=True), 0, "A1 stages a dug, filled cell when the map has none, then holds"),
        ("A1", World(dark=True), 2, "A1 is UNMEASURED when every compared cell is dark (0 == 0 proves nothing)"),
        ("A1", World(moving=True), 2, "A1 is UNMEASURED when the clock moves between reads"),
        ("A2", World(), 0, "A2 holds: bad def, OOB, bad pawn, field method refused by name"),
        ("A3", World(fw=False), 0, "A3 holds: fw.* unbound naming FlowWorks"),
        ("A3", World(fw=True), 2, "A3 is UNMEASURED when FlowWorks is loaded"),
    ]:
        rc, out = run_clause(clause, world)
        check(rc == want, what, "rc %s, want %s; tail %r" % (rc, want, out[-400:]))


def main():
    static_checks()
    fake_checks()
    print("cond probes selftest: %s" % ("all checks passed" if not FAILS else "%d FAILED" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
