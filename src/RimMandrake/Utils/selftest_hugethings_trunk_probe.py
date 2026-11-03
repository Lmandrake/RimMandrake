"""selftest_hugethings_trunk_probe.py -- offline half of HUGETHINGS_TRUNK_ZERO_BLOCKERS_1 (criterion A1).

    python3 src/RimMandrake/Utils/selftest_hugethings_trunk_probe.py      -> "N/N PASS", exit 0

The live trunk check (a full-grown RM_Nogtyl staged on a quicktest map) read 0 blockers on 2026-10-08 with nothing to say why.
This pins the instrument that will say why, before any game load:
  * MapComponent_HugeFootprints.DebugPlantState is `public static string (Map, IntVec3)`, the only shape jawa/static_call can
    call with `current|x,z`, and its body mutates nothing (no Spawn/Despawn/Take/Open, no ledger/pending/realized/dirty write);
  * CompHugeFootprint.DebugDescribe exists and is what the probe prints for the comp;
  * the committed RM_HugeThings.dll carries both names and its .srchash MATCHes the sources (dll_source_stamp.py);
  * northstar/trunk_live.py reads the allowed blocker counts from the patch (the same numbers validation.py's giant_blockers
    reads, sanity: non-empty and every one > 0), and its judge passes a good reading and fails 0 blockers, a count outside the
    measured set, and any blocker south; an unreadable count is UNMEASURED; its settings gate refuses a non-default setting;
  * trunk_live.run(), driven by a fake bridge on a PASS and a 0-blocker FAIL reading, calls jawa/static_call
    DebugPlantState with 'current|x,z' at the staged site and prints its result in the row detail and stdout;
  * the live proof file names trunk_live.py for A2.
"""
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
MOD = os.path.join(ROOT, "src", "RimMandrake", "HugeThings")
SRC = os.path.join(MOD, "Source")
DLL = os.path.join(MOD, "Assemblies", "RM_HugeThings.dll")
LIVE = os.path.join(ROOT, "infrastructure", "state", "live_proofs", "HUGETHINGS_TRUNK_ZERO_BLOCKERS_1.txt")
sys.path.insert(0, os.path.join(MOD, "northstar"))
sys.path.insert(0, MOD)

results = []


def check(name, ok, detail=""):
    results.append(bool(ok))
    print("%s  %s%s" % ("PASS" if ok else "FAIL", name, ("  -- " + detail) if detail and not ok else ""))


def body(text, sig):
    i = text.find(sig)
    if i < 0:
        return None
    j = text.find("{", i)
    depth = 0
    for n in range(j, len(text)):
        if text[n] == "{":
            depth += 1
        elif text[n] == "}":
            depth -= 1
            if depth == 0:
                return text[j:n + 1]
    return None


mc = open(os.path.join(SRC, "MapComponent_HugeFootprints.cs"), encoding="utf-8").read()
SIG = "public static string DebugPlantState(Map map, IntVec3 cell)"
b = body(mc, SIG)
check("DebugPlantState is public static string (Map, IntVec3)", b is not None)
MUT = re.compile(r"\b(Spawn|Despawn|Take|TryTake|Open|RealizePending|RealizeOwner|MoveItems|RelabelOwners|Reconcile|MarkTaken)\s*\("
                 r"|\.(Add|Remove|Clear|Set)\s*\(\s*(?!.*\bList<)|realized\s*\[|\bmutating\s*=|ownershipChanged\s*=")
if b is not None:
    # local lists may Add; only the component's state may not change
    hits = [m.group(0) for m in MUT.finditer(b)]
    state_writes = [h for h in hits if not h.startswith(".Add")]
    adds = re.findall(r"\b(\w+)\.Add\s*\(", b)
    bad_adds = [a for a in adds if a in ("pending", "dirty", "realized", "comps", "lastMoveTick")]
    check("DebugPlantState changes no component state", not state_writes and not bad_adds, "%r %r" % (state_writes, bad_adds))
    check("DebugPlantState reports the planner's view of pending cells", "Planner.Plan" in b and "dryPlanAccepts" in b)
comp = open(os.path.join(SRC, "CompHugeFootprint.cs"), encoding="utf-8").read()
check("CompHugeFootprint.DebugDescribe exists and the probe prints it",
      "public string DebugDescribe()" in comp and b is not None and "DebugDescribe()" in b)

raw = open(DLL, "rb").read()
check("RM_HugeThings.dll carries DebugPlantState and DebugDescribe", b"DebugPlantState" in raw and b"DebugDescribe" in raw)
r = subprocess.run([sys.executable, os.path.join(ROOT, "src", "RimMandrake", "Utils", "dll_source_stamp.py"), "check"],
                   cwd=ROOT, capture_output=True, text=True, timeout=120)
line = [ln for ln in r.stdout.splitlines() if ln.endswith("HugeThings/Assemblies/RM_HugeThings.dll")]
check("RM_HugeThings.dll .srchash MATCHes its sources", line and line[0].startswith("MATCH"), str(line or r.stdout[-300:]))

import trunk_live as T  # noqa: E402
import validation as V  # noqa: E402

allowed = T.allowed_counts()
check("allowed counts read from the patch (sanity: non-empty, all > 0)", allowed and all(n > 0 for n in allowed), repr(allowed))
check("allowed counts agree with validation.py giant_blockers", allowed == sorted(set((V.giant_blockers() or {}).values())),
      "%r vs %r" % (allowed, V.giant_blockers()))
if allowed:
    a = allowed[0]
    out = max(allowed) + 1
    table = [((a, 0), "PASS"), ((0, 0), "FAIL"), ((out, 0), "FAIL"), ((a, 1), "FAIL"), ((None, 0), "UNMEASURED"),
             ((a, None), "UNMEASURED")]
    for (around, south), want in table:
        got = T.judge(around, south, allowed, "probe")[0]
        check("judge(around=%s, south=%s) -> %s" % (around, south, want), got == want, got)
    check("judge with no allowed counts is UNMEASURED", T.judge(a, 0, [], "p")[0] == "UNMEASURED")
check("settings gate passes the shipped defaults",
      not T.settings_ok({"giantPlantsEnabled": "True", "plantTrunkEnabled": "True", "plantTrunkScale": "1"}))
check("settings gate refuses trunk off / scale 0.75 / unreadable",
      T.settings_ok({"giantPlantsEnabled": "True", "plantTrunkEnabled": "False", "plantTrunkScale": "1"})
      and T.settings_ok({"giantPlantsEnabled": "True", "plantTrunkEnabled": "True", "plantTrunkScale": "0.75"})
      and T.settings_ok({}))
# the 2026-11-03 live run died UNMEASURED reading map_info's size as {"size": {x, z}}; the tool replies sizeX/sizeZ
MI_CS = os.path.join(ROOT, "src", "RimMandrake", "bridgetools", "JawaBench.BridgeTools", "JawaBenchMapInfoTools.cs")
mi_src = open(MI_CS, encoding="utf-8").read() if os.path.exists(MI_CS) else ""
check("jawa/map_info replies sizeX/sizeZ (JawaBenchMapInfoTools.cs)",
      "sizeX = map.Size.x" in mi_src and "sizeZ = map.Size.z" in mi_src)
check("map_centre reads the real map_info reply (250x250 -> 155,95)",
      T.map_centre({"success": True, "mapId": 0, "sizeX": 250, "sizeZ": 250, "cellCount": 62500}) == (155, 95))
check("map_centre on an unreadable reply is None",
      T.map_centre({"success": False}) is None and T.map_centre({"size": {"x": 250, "z": 250}}) is None)
# run() itself, driven by a fake bridge: the DebugPlantState read must be called at the staged site and printed beside the
# verdict on PASS and FAIL alike (blind check 2026-11-03: replacing probe(x, z) with a constant left every row green)
import json  # noqa: E402
import tempfile  # noqa: E402


class FakeRB:
    PROBE = "registered=True claimed=0 pending=13 dryPlanAccepts=0 MARK-7f3a"

    def __init__(self, blockers):
        self.blockers, self.calls, self.staged = blockers, [], False

    def call(self, tool, kw):
        self.calls.append((tool, dict(kw)))
        if tool == "jawa/mod_settings_field":
            return {"success": True, "value": {"plantTrunkScale": "1"}.get(kw["field"], "True")}
        if tool == "jawa/map_info":
            return {"success": True, "sizeX": 250, "sizeZ": 250}
        if tool == "jawa/artboard_stage":
            self.staged = True
            return {"success": True, "ops": [{"id": "g", "ok": True, "readBack": 1.0}]}
        if tool == "jawa/list_things":
            south = kw["rect"].endswith(",17,2")
            return {"success": True, "countMatched": 0 if (south or not self.staged) else self.blockers}
        if tool == "jawa/static_call":
            return {"success": True, "result": self.PROBE}
        return {"success": True}


for label, n, want_rc, want_status in (("PASS", allowed[0] if allowed else 10, 0, "PASS"), ("0-blocker FAIL", 0, 1, "FAIL")):
    fk = FakeRB(n)
    with tempfile.TemporaryDirectory() as td:
        outp = os.path.join(td, "rows.json")
        import io, contextlib  # noqa: E401,E402
        with contextlib.redirect_stdout(io.StringIO()) as so:
            rc = T.run(fk, "", outp)
        rows = json.load(open(outp, encoding="utf-8"))["rows"] if os.path.exists(outp) else []
    sc = [kw for tool, kw in fk.calls if tool == "jawa/static_call"]
    stage = [kw for tool, kw in fk.calls if tool == "jawa/artboard_stage"]
    m = re.search(r"\|x=(\d+)\|z=(\d+)\|", stage[0]["ops"]) if stage else None
    site = "%s,%s" % m.groups() if m else "?"
    check("run() %s: exit %d, row %s" % (label, want_rc, want_status),
          rc == want_rc and rows and rows[0]["status"] == want_status, "rc=%r rows=%r" % (rc, rows))
    check("run() %s calls jawa/static_call %s.DebugPlantState with 'current|%s' after staging" % (label, T.MC, site),
          any(kw.get("type") == T.MC and kw.get("method") == "DebugPlantState" and kw.get("args") == "current|" + site
              for kw in sc)
          and [t for t, _ in fk.calls].index("jawa/artboard_stage") < max(i for i, (t, _) in enumerate(fk.calls)
                                                                          if t == "jawa/static_call"),
          "static_calls=%r site=%s" % (sc, site))
    check("run() %s prints the probe's result in the row detail and stdout" % label,
          rows and FakeRB.PROBE in rows[0]["detail"] and FakeRB.PROBE in so.getvalue(), repr(rows)[:300])

txt = open(LIVE, encoding="utf-8").read() if os.path.exists(LIVE) else ""
check("live proof file runs trunk_live.py for A2", re.search(r"^live-proof A2: .*trunk_live\.py", txt, re.M) is not None)

print("%d/%d PASS" % (sum(results), len(results)))
sys.exit(0 if all(results) else 1)
