"""Offline selftest for BATCHREADS_BUILD_ROUND_TRIP_CUT (tickburst_2026-11-06/final.md L-d). No game, no bridge.

Proves: (1) the three new batch read tools (things in rects, pawn state, power nets) are declared in the companion
source, each building its rows with the SAME helper its single-call tool uses (so a batch row and a single read cannot
disagree field by field), and each carries a name the client's read-only heuristic accepts; the fourth, fluid cells,
already existed (flowworks_excavation_rect, JawaBenchFlowWorksPulseTools.cs) and is the one the proof below adopts;
(2) tool_schemas.json knows all four, so lint_calls accepts a call to them;
(3) on one existing proof -- the FlowWorks northstar extension chain `plot_C_limitless_canal`, whose canal_fill_front bar
reads every channel cell's exact water once per pulse -- the batch path returns the SAME verdicts as the per-cell path
and the round trips it saves are counted; (4) the batch reply is never trusted when it cannot be: a companion without
the tool, a short row list, a misplaced row, a row without the getter values or an integer dl, or a refused rect all fall back to the per-cell tools
(each planted, each must still give the per-cell verdict and pay the per-cell calls).
The live half (each batch tool reads the same cells/things/pawns/nets as its single-call tool on a loaded map) is
infrastructure/state/live_proofs/BATCHREADS_BUILD_ROUND_TRIP_CUT.txt.
"""
import atexit as _st_atexit, os as _st_os, shutil as _st_shutil, tempfile as _st_tempfile  # noqa: E401
_st_tempfile.tempdir = _st_os.environ["TMPDIR"] = _st_tempfile.mkdtemp(prefix="st_selftest_batch_reads_")
_st_atexit.register(_st_shutil.rmtree, _st_tempfile.tempdir, True)
import json
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(MOD)))
UTILS = os.path.join(ROOT, "src", "RimMandrake", "Utils")
for _p in (HERE, UTILS, os.path.join(UTILS, "modcheck")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

CS = os.path.join(ROOT, "src", "RimMandrake", "bridgetools", "JawaBench.BridgeTools")
SCHEMAS = os.path.join(UTILS, "northstar_driver", "tool_schemas.json")

# batch tool -> (its single-call twin, the shared row helper both must call, the method names)
TOOLS = {
    "jawa/list_things_batch": ("jawa/list_things", "ThingListRow", "ListThingsBatch", "ListThings"),
    "jawa/get_pawns_batch": ("jawa/pawn_get", "PawnSnapshot", "PawnGetBatch", "PawnGet"),
    "jawa/get_power_nets_batch": ("jawa/power_net", "PowerNetBlock", "PowerNetBatch", "PowerNetTool"),
}
FLUID_BATCH = "jawa/flowworks_excavation_rect"      # pre-existing; read-only by its own Description
READ_ONLY_PREFIXES = ("list_", "get_")      # rimbridge_client.READ_ONLY_PREFIXES (checked against it below)


def _sources():
    out = {}
    for fn in sorted(os.listdir(CS)):
        if fn.endswith(".cs"):
            with open(os.path.join(CS, fn), encoding="utf-8") as f:
                out[fn] = f.read()
    return out


def _method_body(src_all, name):
    """The text of `public static async Task<object> <name>(` up to the next [Tool( or end of file."""
    for src in src_all.values():
        m = re.search(r"public static async Task<object> %s\(" % re.escape(name), src)
        if m:
            nxt = src.find("[Tool(", m.end())
            return src[m.start(): nxt if nxt > 0 else len(src)]
    return None


def check_source(probs):
    src = _sources()
    blob = "\n".join(src.values())
    for tool, (single, helper, batch_m, single_m) in TOOLS.items():
        if blob.count('"%s"' % tool) != 1:
            probs.append("%s: declared %d times in the companion source, want exactly 1" % (tool, blob.count('"%s"' % tool)))
        if not tool.split("/", 1)[1].startswith(READ_ONLY_PREFIXES):
            probs.append("%s: name fails the client's read-only prefixes %s" % (tool, READ_ONLY_PREFIXES))
        for m in (batch_m, single_m):
            body = _method_body(src, m)
            if body is None:
                probs.append("%s: method %s not found" % (tool, m))
            elif helper + "(" not in body:
                probs.append("%s: %s does not call the shared row helper %s" % (tool, m, helper))
        if not re.search(r"private static \w+ %s\(" % helper, blob):
            probs.append("%s: shared helper %s is not defined" % (tool, helper))
    # the batch tools only read: no PowerOn write, no setter, no Destroy in the batch file
    batch_file = src.get("JawaBenchBatchReadTools.cs", "")
    for bad in ("PowerOn =", ".Destroy(", "SetTerrain", "forcePowerOn"):
        if bad in batch_file:
            probs.append("JawaBenchBatchReadTools.cs contains %r: a batch READ tool must not write" % bad)
    # rule 9 of the companion skill: no 'jawa/' literal in prose (build.py would register a phantom tool)
    for lit in re.findall(r'"(jawa/[a-z_0-9]*)', batch_file):
        if lit not in TOOLS:
            probs.append("JawaBenchBatchReadTools.cs names %r in a string: build.py reads it as a tool" % lit)
    try:
        import rimbridge_client as rb
        for p in READ_ONLY_PREFIXES:
            if p not in rb.READ_ONLY_PREFIXES:
                probs.append("rimbridge_client.READ_ONLY_PREFIXES lost %r" % p)
        # every read the live proof makes must pass the client's read-only guard (power_net is read-only only without
        # forcePowerOn, so the heuristic rightly calls it mutating; the proof never passes that flag)
        probe = rb.RimBridge.__new__(rb.RimBridge)
        probe.static_reads = True
        for tool, params in ([(t, {}) for t in TOOLS] + [(FLUID_BATCH, {}), ("jawa/pawn_get", {}),
                             ("jawa/flowworks_excavation_report", {}), ("jawa/list_things", {}), ("jawa/list_pawns", {}),
                             ("jawa/static_call", {"type": "RimMandrake.FlowWorks.Machinery.RM_LineProofs",
                                                   "method": "ProofPitWater"})]):
            if not probe.looks_read_only(tool, params):
                probs.append("rimbridge_client calls %s %s mutating" % (tool, params.get("method", "")))
        if probe.looks_read_only("jawa/static_call", {"type": "RimMandrake.FlowWorks.Machinery.RM_LineProofs",
                                                      "method": "ProofFillWithFluid"}):
            probs.append("rimbridge_client calls ProofFillWithFluid read-only: the guard went blind")
    except Exception as e:      # the import is the instrument; a failure is a finding, not a pass
        probs.append("rimbridge_client import failed: %r" % (e,))
    with open(SCHEMAS, encoding="utf-8") as f:
        tools = json.load(f)["tools"]
    if 'Read-only: FlowWorks depth/water state for EVERY cell of a rect' not in blob:
        probs.append("%s: its read-only Description changed; re-read it before trusting it as the fluid batch" % FLUID_BATCH)
    for tool in list(TOOLS) + [FLUID_BATCH]:
        if tool not in tools:
            probs.append("tool_schemas.json lacks %s (run tool_schemas.py --supplement-only)" % tool)


# ------------------------------------------------------------------ the existing proof, two ways
def _canal_game(dl_front=7414):
    """The plot_C_limitless_canal fake game of selftest_extensions.canal(): a 3-cell wet front of `dl_front` decilitres
    behind the mouth, the source paying 3 x 0.74 levels. Per-cell tools only, as the companion had before this item."""
    st = {}

    def per_cell(tl, p):
        if tl == "jawa/flowworks_body_report":
            stock = 287.6 if p.get("classify") else 287.6 - 0.7414 * 3
            return {"success": True, "isSourceCell": True, "body": {"id": 1, "stock": stock, "limitless": False}}
        if tl == "jawa/flowworks_engine_state":
            st["e"] = st.get("e", 1000) + 750
            return {"success": True, "depthEngineEnabled": True, "nextPulseTick": st["e"], "pulseIntervalTicks": 250}
        if tl == "jawa/flowworks_excavation_report":
            return {"success": True, "depth": 1, "waterDl": 0, "waterM": 0.0, "isSourceCell": False, "isSinkCell": False,
                    "sinkTransferredTotal": 0.0}
        if tl == "jawa/static_call" and p.get("method") == "ProofPitWater":
            x = int(str(p.get("args")).split(",")[0])
            i = x - st.setdefault("x0", x)
            return {"result": "PITWATER dl=%d wet=1 cells=1" % (dl_front if 0 <= i < 3 else 0)}
        if tl == "jawa/static_call" and p.get("method") == "ProofResetRect":
            return {"result": "RESET x left=0"}
        if tl == "jawa/static_call" and p.get("method") == "ProofFillWithFluid":
            return {"result": "FILLED"}
        if tl == "jawa/flowworks_excavation_drive":
            return {"success": True, "depth": 4, "waterM": 0.0, "waterDl": 0}
        if tl == "jawa/spawn_pawn":
            return {"pawns": [{"id": "P1"}]}
        return {"success": True}
    return per_cell


def _batched(per_cell, plant=None):
    """Add jawa/flowworks_excavation_rect (its REAL row shape, JawaBenchFlowWorksPulseTools.cs) to a per-cell fake,
    answering each cell of the rect, row by row, from the SAME per-cell answers (so the only difference between the
    two runs is the number of round trips). `plant` corrupts the reply to prove the caller refuses it."""
    def h(tl, p):
        if tl != FLUID_BATCH:
            return per_cell(tl, p)
        rows = []
        for dz in range(int(p["h"])):
            for dx in range(int(p["w"])):
                x, z = int(p["x"]) + dx, int(p["z"]) + dz
                rep = per_cell("jawa/flowworks_excavation_report", {"x": x, "z": z})
                pw = per_cell("jawa/static_call", {"type": "x", "method": "ProofPitWater", "args": "%d,%d,1,1" % (x, z)})
                dl = int(re.match(r"PITWATER dl=(-?\d+)", pw["result"]).group(1))
                rows.append({"x": x, "z": z, "d": rep["depth"], "dEff": rep["depth"], "dl": dl, "fluid": None, "isExcavated": rep["depth"] > 0,
                             "isSource": rep["isSourceCell"], "isSink": rep["isSinkCell"], "terrain": None})
        r = {"success": True, "mapId": 0, "rect": {k: p[k] for k in "xzwh"}, "cellCount": len(rows),
             "cellsScanned": len(rows), "rows": rows, "sinkTransferredTotal": 0.0, "overflowDestroyedTotal": 0.0}
        return plant(r) if plant else r
    return h


def _counting(h, counter):
    def c(tl, p):
        key = tl if tl != "jawa/static_call" else "static_call:%s" % p.get("method")
        counter[key] += 1
        return h(tl, p)
    return c


FLUID_READS = ("jawa/flowworks_excavation_report", "static_call:ProofPitWater", FLUID_BATCH)


def check_round_trips(probs, report):
    import selftest_extensions as SE
    import extensions as EXT
    chain = "plot_C_limitless_canal"
    runs = {}
    for label, game in (("per_cell", _canal_game()), ("batch", _batched(_canal_game()))):
        n = Counter()
        got = SE._ext_run(EXT, chain, _counting(game, n))
        runs[label] = (got, n)
    (v1, n1), (v2, n2) = runs["per_cell"], runs["batch"]
    if v1 != v2:
        probs.append("%s: batch verdicts %s differ from per-cell %s" % (chain, v2, v1))
    if v1.get("canal_fill_front") != "PASS":
        probs.append("%s: canal_fill_front %s on the wet-front fake, want PASS (the fixture went blind)"
                     % (chain, v1.get("canal_fill_front")))
    fluid1 = sum(n1[k] for k in FLUID_READS)
    fluid2 = sum(n2[k] for k in FLUID_READS)
    total1, total2 = sum(n1.values()), sum(n2.values())
    if n2["jawa/flowworks_excavation_report"] or n2["static_call:ProofPitWater"]:
        probs.append("%s: the batch run still paid per-cell fluid reads %s" % (chain, {k: n2[k] for k in FLUID_READS}))
    if not (n2[FLUID_BATCH] > 0 and fluid2 < fluid1):
        probs.append("%s: no round trips saved: per-cell %d fluid calls, batch %d" % (chain, fluid1, fluid2))
    report.update({"proof": "FlowWorks northstar extensions.py chain %s (offline fake game; per_cell includes the one probe of the absent batch tool)" % chain,
                   "verdicts": v1, "per_cell": {"fluid_calls": fluid1, "all_calls": total1,
                                                "by_tool": {k: n1[k] for k in FLUID_READS}},
                   "batch": {"fluid_calls": fluid2, "all_calls": total2, "by_tool": {k: n2[k] for k in FLUID_READS}},
                   "round_trips_saved": total1 - total2, "ms_saved_at_53ms": (total1 - total2) * 53})
    if total1 - total2 != fluid1 - fluid2:
        probs.append("%s: non-fluid calls changed between runs (%d vs %d)" % (chain, total1 - fluid1, total2 - fluid2))

    # (4) every untrustworthy batch reply falls back to the per-cell tools, verdict unchanged
    def short(r):
        r["rows"] = r["rows"][:-1]
        return r

    def moved(r):
        r["rows"][0]["x"] -= 1
        return r

    def nogetter(r):
        r["rows"][-1]["dEff"] = None
        return r

    def booldl(r):
        r["rows"][0]["dl"] = True
        return r

    def nulldl(r):
        r["rows"][0]["dl"] = None
        return r

    def refused(r):
        return {"success": False, "message": "rect is not inside map 0. Nothing was read."}
    for plant in (short, moved, nogetter, booldl, nulldl, refused):
        n = Counter()
        got = SE._ext_run(EXT, chain, _counting(_batched(_canal_game(), plant), n))
        if got != v1:
            probs.append("plant %s: verdicts %s, want the per-cell %s" % (plant.__name__, got, v1))
        if n["static_call:ProofPitWater"] != n1["static_call:ProofPitWater"]:
            probs.append("plant %s: %d ProofPitWater reads, want the per-cell %d (the bad batch reply was trusted)"
                         % (plant.__name__, n["static_call:ProofPitWater"], n1["static_call:ProofPitWater"]))
    # an absent tool is probed ONCE per run, then never again
    n = Counter()
    SE._ext_run(EXT, chain, _counting(_canal_game(), n))
    if n[FLUID_BATCH] != 1:
        probs.append("absent batch tool probed %d times in one run, want 1" % n[FLUID_BATCH])
    # the wet front must still be SEEN through the batch: a dry batch reading FAILs like a dry per-cell one
    for dl, want in ((0, "FAIL"),):
        got = SE._ext_run(EXT, chain, _batched(_canal_game(dl))).get("canal_fill_front")
        if got != want:
            probs.append("batch dl=%d: canal_fill_front %s, want %s" % (dl, got, want))


# ------------------------------------------------------------------ the live script, drilled offline
class _FakeLive(object):
    """A paused map for prove_batch_reads.py's clauses: things, pawns, two powered buildings on one net and one
    unpowered wall, and a dry FlowWorks line. `lie` makes one batch tool disagree with its single-call twin."""

    def __init__(self, lie=None, ticks=500):
        self.lie, self.tick, self.calls, self.secs, self.ticks = lie, ticks, 0, 0.0, set()
        self.things = [dict(id="Steel%d" % i, def_="Steel", x=10 + 3 * i, z=12, hp=100) for i in range(5)] + \
            [dict(id="Battery1", def_="Battery", x=40, z=40, hp=100), dict(id="Solar1", def_="SolarGenerator", x=44, z=40, hp=100),
             dict(id="Wall1", def_="Wall", x=50, z=50, hp=300)]
        self.pawns = {"Human1": {"name": "Ann", "x": 20, "z": 20}, "Human2": {"name": "Bo", "x": 22, "z": 21}}

    def _row(self, t):
        return {"id": t["id"], "def": t["def_"], "x": t["x"], "z": t["z"], "hitPoints": t["hp"]}

    def _in(self, t, r):
        x, z, w, h = r
        return x <= t["x"] < x + w and z <= t["z"] < z + h

    def _power(self, tid):
        if tid not in ("Battery1", "Solar1"):
            return None
        return {"thing": {"id": tid, "defName": tid[:-1]}, "connected": True,
                "net": {"currentStoredEnergy": 10.0, "powerCompsCount": 2}, "isPowerTrader": tid == "Solar1",
                "powerOn": True if tid == "Solar1" else None, "energyOutputPerTick": 1.5 if tid == "Solar1" else None}

    def call(self, tool, **p):
        self.calls += 1
        self.ticks.add(self.tick)
        ok = {"success": True, "ticksGame": self.tick}
        if tool == "jawa/map_info":
            return dict(ok, sizeX=100, sizeZ=100)
        if tool == "jawa/list_things":
            pool = [t for t in self.things if p.get("group") != "BuildingArtificial" or t["def_"] != "Steel"]
            if p.get("group") == "PowerTrader":
                pool = [t for t in self.things if t["def_"] == "SolarGenerator"]
            pool = pool[:int(p.get("limit") or 200)]
            if p.get("rect"):
                r = tuple(int(v) for v in p["rect"].split(","))
                pool = [t for t in pool if self._in(t, r)]
            return dict(ok, things=[self._row(t) for t in pool], countMatched=len(pool))
        if tool == "jawa/list_things_batch":
            res = []
            for tok in p["rects"].split(";"):
                r = tuple(int(v) for v in tok.split(","))
                rows = [self._row(t) for t in self.things if self._in(t, r)]
                if self.lie == "things" and rows:
                    rows[0]["hitPoints"] -= 1
                res.append({"things": rows, "countMatched": len(rows)})
            return dict(ok, results=res)
        if tool == "jawa/list_pawns":
            return dict(ok, pawns=[{"id": k} for k in self.pawns])
        if tool == "jawa/pawn_get":
            if p["pawn"] not in self.pawns:
                return {"success": False, "message": "No pawn"}
            return dict(ok, pawns=[dict(self.pawns[p["pawn"]])])
        if tool == "jawa/get_pawns_batch":
            rows = []
            for q in p["pawns"].split(","):
                if q in self.pawns:
                    snap = dict(self.pawns[q])
                    if self.lie == "pawns":
                        snap["x"] += 1
                    rows.append({"query": q, "ok": True, "pawn": snap})
                else:
                    rows.append({"query": q, "ok": False, "error": "No pawn"})
            return dict(ok, rows=rows)
        if tool == "jawa/power_net":
            w = self._power(p["thing"])
            if w is None:
                return {"success": False, "message": "has no CompPower."}
            out = dict(ok, **{k: v for k, v in w.items() if k != "powerOn"})
            out.update(powerOnBefore=w["powerOn"], powerOnAfter=w["powerOn"])
            return out
        if tool == "jawa/get_power_nets_batch":
            rows = []
            for q in p["things"].split(","):
                w = self._power(q)
                if w is None:
                    rows.append({"query": q, "ok": False, "error": "has no CompPower."})
                    continue
                w = dict(w, query=q, ok=True, netIndex=0)
                if self.lie == "power" and q == "Solar1":
                    w["powerOn"] = False
                rows.append(w)
            return dict(ok, rows=rows, netCount=1)
        if tool == "jawa/flowworks_excavation_report":
            return dict(ok, depth=0, waterDl=0, isSinkCell=False)
        if tool == "jawa/static_call" and p.get("method") == "ProofPitWater":
            return dict(ok, result="PITWATER dl=0 wet=0 cells=1")
        if tool == "jawa/flowworks_excavation_rect":
            rows = [{"x": p["x"] + dx, "z": p["z"] + dz, "dEff": 1 if self.lie == "fluid" else 0, "dl": 0,
                     "isSink": False} for dz in range(p["h"]) for dx in range(p["w"])]
            return dict(ok, rows=rows, sinkTransferredTotal=0.0)
        return {"success": False, "message": "fake: unknown tool %s" % tool}


def check_live_script(probs):
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "prove_batch_reads", os.path.join(ROOT, "src", "RimMandrake", "bridgetools", "prove_batch_reads.py"))
    PB = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(PB)
    fns = {"A1": PB.clause_a1, "A2": PB.clause_a2}
    for clause, fn in fns.items():
        code, why = fn(_FakeLive())
        if code != 0:
            probs.append("live script %s on an agreeing fake: %s %s, want 0" % (clause, code, why))
    for lie, clause in (("things", "A1"), ("pawns", "A1"), ("fluid", "A2"), ("power", "A1")):
        code, why = fns[clause](_FakeLive(lie=lie))
        if code != 1:
            probs.append("live script %s with a lying %s batch: %s %s, want 1" % (clause, lie, code, why))
    # a moving game is no verdict (UNMEASURED), never a pass or a fail
    moving = _FakeLive()
    real = moving.call

    def tick(tool, **p):
        moving.tick += 1
        return real(tool, **p)
    moving.call = tick
    try:
        fns["A1"](moving)
        probs.append("live script A1 on an unpaused game did not refuse")
    except PB.Unmeasured:
        pass
    # a map with no CompPower building is no verdict for A1, never a pass on things and pawns alone
    bare = _FakeLive()
    bare.things = [t for t in bare.things if t["def_"] not in ("Battery", "SolarGenerator")]
    try:
        got = fns["A1"](bare)
        probs.append("live script A1 with no powered building gave %s, want UNMEASURED" % (got,))
    except PB.Unmeasured:
        pass
    # 300 ruin walls ahead of the one powered building (GAMEENV_FIX_PROOFSITE_28883863_ITEMS_WAIT): the cap must not hide it
    walled = _FakeLive()
    walled.things = [dict(id="Ruin%d" % i, def_="Wall", x=1 + i % 90, z=1 + i // 90, hp=300) for i in range(300)] + \
        [t for t in walled.things if t["def_"] != "Battery"]
    got = PB.clause_power(walled)
    if got[0] != 0:
        probs.append("live script power clause behind 300 walls gave %s, want 0" % (got,))
    a2 = PB.clause_a2(_FakeLive())[1]
    if "round trips saved" not in a2:
        probs.append("live script A2 prints no round-trip count: %s" % a2)


def main():
    probs, report = [], {}
    check_source(probs)
    import io
    import contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        check_round_trips(probs, report)
        check_live_script(probs)
    print(json.dumps(report, indent=1, sort_keys=True))
    for p in probs:
        print("FAIL:", p)
    print("selftest_batch_reads: %s (%d problem(s))" % ("PASS" if not probs else "FAIL", len(probs)))
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main())
