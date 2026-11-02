"""Proof of DEEP_LAYER_BELT_HARNESS_1: the LanternDeeps Deep-only proofs get a real Lantern Deep pocket map.

    python3 src/RimMandrake/LanternDeeps/prove_deep_harness.py --offline
    python.exe "$(wslpath -w src/RimMandrake/LanternDeeps/prove_deep_harness.py)" --clause A1 < /dev/null
    python.exe "$(wslpath -w src/RimMandrake/LanternDeeps/prove_deep_harness.py)" --clause A2 < /dev/null

Exit 0 = the clause holds, 1 = it does not, 2 = unmeasured (no game, no map).

--offline  the wiring: the mineshaft is a MapPortal whose generator carries the Creep/Aurora/Collapse components;
           RM_DeepHarness.cs is compiled into the shipped DLL; every validation.py chain that reads a Deep-only
           answer opens a Deep first (_enter_deep) and leaves it in a finally (_leave_deep).
A1 (live)  on the current map (a quicktest map is started if none plays), RM_DeepHarness.EnterDeep generates a
           pocket map of biome RM_LanternDeeps carrying Creep, Aurora and Collapse and makes it current; LeaveDeep
           returns to the source map and the Deep is gone.
A2 (live)  inside that Deep (furnished: battery + torch) every Deep-only proof answers past its prerequisite: no
           "only on a Deep" and no "no colony battery". The proofs' own pass/fail is the LanternDeeps suite's
           business; this clause proves the harness gives them a Deep.
The live clauses clean up after themselves (LeaveDeep destroys the Deep and the harness's portal).
"""
import ast
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(os.path.dirname(HERE), "Utils")
HARNESS = "RimMandrake.LanternDeeps.RM_DeepHarness"
DEEP_COMPS = ("RM_MapComponent_Creep", "RM_MapComponent_DeepAurora", "RM_MapComponent_DeepCollapse")
NEEDS = ("only on a Deep", "no colony battery")
PROOFS = [("RM_CreepCleaversProof", "ProofCreep", "10"), ("RM_CreepCleaversProof", "ProofCleave", "go"),
          ("RM_AuroraCollapseProof", "ProofAurora", "go"), ("RM_AuroraCollapseProof", "ProofCollapse", "go"),
          ("RM_HydrocarbonWave2Proof", "ProofSlick", "go"), ("RM_HydrocarbonWave2Proof", "ProofKnocker", "go"),
          ("RM_HydrocarbonWave3Proof", "ProofHush", "go"), ("RM_HydrocarbonWave3Proof", "ProofSipper", "go"),
          ("RM_HydrocarbonWave3Proof", "ProofTapper", "go"), ("RM_HydrocarbonWave3Proof", "ProofPooler", "go")]


def _read(rel):
    with open(os.path.join(HERE, rel), encoding="utf-8") as fh:
        return fh.read()


def offline():
    bad = []
    shaft = re.sub(r"<!--.*?-->", "", _read("Defs/ThingDefs_Buildings/RM_LanternDeepMineshaft.xml"), flags=re.S)
    if "<thingClass>MapPortal</thingClass>" not in shaft or \
            "<pocketMapGenerator>RM_LanternDeepGenerator</pocketMapGenerator>" not in shaft:
        bad.append("RM_LanternDeepMineshaft is not a MapPortal onto RM_LanternDeepGenerator")
    gen = re.sub(r"<!--.*?-->", "", _read("Defs/MapGeneration/RM_LanternDeepGenerator.xml"), flags=re.S)
    m = re.search(r"<customMapComponents>(.*?)</customMapComponents>", gen, re.S)
    comps = re.findall(r"<li>\s*RimMandrake\.LanternDeeps\.(\w+)\s*</li>", m.group(1)) if m else []
    for c in DEEP_COMPS:
        if c not in comps:
            bad.append("RM_LanternDeepGenerator.customMapComponents lacks " + c)
    if '<Compile Include="RM_DeepHarness.cs" />' not in _read("Source/RM_LanternDeeps.csproj"):
        bad.append("RM_DeepHarness.cs is not compiled")
    with open(os.path.join(HERE, "Assemblies", "RimMandrake.LanternDeeps.dll"), "rb") as fh:
        dll = fh.read()
    for name in (b"RM_DeepHarness", b"EnterDeep", b"LeaveDeep"):
        if name not in dll:
            bad.append("shipped DLL lacks %s (rebuild with winbuild.py LanternDeeps)" % name.decode())
    tree = ast.parse(_read("validation.py"))
    deep_chains = 0
    for fn in tree.body:
        if not isinstance(fn, ast.FunctionDef) or fn.name.startswith("_"):
            continue
        calls = [n.func.id for n in ast.walk(fn) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)]
        if "_deep_prereq_missing" not in calls:
            continue
        deep_chains += 1
        enters = [s for s in fn.body if isinstance(s, ast.If) and "_enter_deep" in ast.dump(s.test)]
        tries = [s for s in fn.body if isinstance(s, ast.Try)]
        if not enters or not tries or "_leave_deep" not in ast.dump(ast.Module(body=tries[-1].finalbody, type_ignores=[])):
            bad.append("chain %s reads a Deep-only answer without _enter_deep / finally _leave_deep" % fn.name)
        elif fn.body.index(enters[0]) > fn.body.index(tries[-1]):
            bad.append("chain %s enters the Deep after its proofs" % fn.name)
    if deep_chains < 4:
        bad.append("only %d Deep-only chains found in validation.py (expected creep_cleavers, aurora_collapse, "
                   "hydrocarbon_wave2, hydrocarbon_wave3)" % deep_chains)
    for b in bad:
        print("FAIL " + b)
    print("OFFLINE %s: %d Deep-only chains wired, portal->generator->%s" % ("PASS" if not bad else "FAIL",
                                                                          deep_chains, ",".join(DEEP_COMPS)))
    return 0 if not bad else 1


class Session(object):
    def __init__(self):
        sys.path.insert(0, UTILS)
        import rimbridge_client as rb   # noqa: E402
        host, port, token = rb.resolve_endpoint()
        self.b = rb.RimBridge(host=host, port=port, token=token, timeout=600.0)
        self.b.connect()

    def call(self, tool, **p):
        r = self.b.call(tool, p) or {}
        if isinstance(r, dict) and r.get("content"):
            try:
                r = json.loads(r["content"][0]["text"])
            except Exception:
                pass
        return r

    def static(self, typ, method, args):
        r = self.call("jawa/static_call", type=typ, method=method, args=args)
        return str((r or {}).get("result", "")) or "no result: %r" % (r,)


def playing(s):
    if s.call("rimworld/get_ui_state").get("programState") != "Playing":
        s.call("rimworld/start_debug_game_ready", timeoutMs=280000, readiness="mapData", pauseIfNeeded=True)
        for _ in range(120):
            if s.call("rimworld/get_ui_state").get("programState") == "Playing":
                break
            time.sleep(1)
    info = s.call("jawa/map_info")
    return info if info.get("sizeX") is not None else None


def live(clause):
    s = Session()
    if playing(s) is None:
        print("UNMEASURED: no playing map")
        return 2
    s.static(HARNESS, "LeaveDeep", "go")   # a Deep left current by an earlier run
    entered = s.static(HARNESS, "EnterDeep", "furnish" if clause == "A2" else "")
    print("EnterDeep: " + entered)
    ok = True
    try:
        if clause == "A1":
            info = s.call("jawa/map_info")
            print("map_info: " + json.dumps({k: info.get(k) for k in ("biome", "mapBiome", "sizeX", "mapIndex", "tile")}))
            ok = (entered.startswith("entered ") and "biome=RM_LanternDeeps" in entered and "pocket=True" in entered
                  and all(c in entered for c in ("Creep", "Aurora", "Collapse")))
        else:
            if not entered.startswith("entered "):
                print("FAIL no Deep opened")
                return 1
            for typ, method, arg in PROOFS:
                res = s.static("RimMandrake.LanternDeeps." + typ, method, arg)
                hit = [n for n in NEEDS if n in res]
                print("%s %s: %s" % ("FAIL" if hit else "ok  ", method, res[:200]))
                ok = ok and not hit
    finally:
        left = s.static(HARNESS, "LeaveDeep", "go")
        print("LeaveDeep: " + left)
    if clause == "A1":
        ok = ok and left.startswith("left ") and "stillListed=False" in left
    print("%s %s" % ("PASS" if ok else "FAIL", clause))
    return 0 if ok else 1


def main(argv):
    if "--offline" in argv:
        return offline()
    if "--clause" in argv and argv[argv.index("--clause") + 1] in ("A1", "A2"):
        return live(argv[argv.index("--clause") + 1])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
