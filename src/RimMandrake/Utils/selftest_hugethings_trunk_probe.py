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
txt = open(LIVE, encoding="utf-8").read() if os.path.exists(LIVE) else ""
check("live proof file runs trunk_live.py for A2", re.search(r"^live-proof A2: .*trunk_live\.py", txt, re.M) is not None)

print("%d/%d PASS" % (sum(results), len(results)))
sys.exit(0 if all(results) else 1)
