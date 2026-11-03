"""Proof of DEEP_LAYER_BELT_HARNESS_1: the LanternDeeps Deep-only proofs get a real Lantern Deep pocket map.

    python3 src/RimMandrake/LanternDeeps/prove_deep_harness.py --offline
    python.exe "$(wslpath -w src/RimMandrake/LanternDeeps/prove_deep_harness.py)" --clause A1 < /dev/null
    python.exe "$(wslpath -w src/RimMandrake/LanternDeeps/prove_deep_harness.py)" --clause A2 < /dev/null

Exit 0 = the clause holds, 1 = it does not, 2 = unmeasured (no game, no map).

--offline  the wiring: the mineshaft is a MapPortal whose generator carries the Creep/Aurora/Collapse components;
           RM_DeepHarness.cs is compiled into the shipped DLL; every validation.py chain that reads a Deep-only
           answer opens a Deep first (_enter_deep) and leaves it in a finally (_leave_deep); and, run against a
           recording fake bridge (modcheck stubbed), each Deep-only chain's first call is RM_DeepHarness.EnterDeep,
           its last LeaveDeep, and it makes no Proof* call when EnterDeep opens nothing; EnterDeep's args carry
           'furnish' (the fake refuses sipper/tapper with "no colony battery" otherwise) and all ten proofs are
           reached. The item's Nightside half too: SleepingIce validation.py's shivven chain, run the same way, builds
           a Soil room, stands a player-faction heat source inside it, runs >250 ticks and reads the dial before
           ProofSeek, and never reaches ProofSeek when the dial reads "heaters 0.0".
A1 (live)  on the current map (a quicktest map is started if none plays), RM_DeepHarness.EnterDeep generates a
           pocket map of biome RM_LanternDeeps carrying Creep, Aurora and Collapse and makes it current; LeaveDeep
           returns to the source map and the Deep is gone; map_info's mapBiome reads RM_LanternDeeps meanwhile.
A2 (live)  inside the Deep the suite itself opens (EnterDeep with validation.py's own args: battery + torch) every Deep-only proof answers past its prerequisite: no
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


ENTER_ARGS = set()   # the EnterDeep args the real validation.py chains pass (filled by _probe_chains)
DEEP_CHAINS = ("creep_cleavers", "aurora_collapse", "hydrocarbon_wave2", "hydrocarbon_wave3")
OPENED = "entered biome=RM_LanternDeeps pocket=True comps=Creep,Aurora,Collapse"


# a passing answer per Proof*, shaped to each chain's own assertion, so a chain runs to its last proof
PASS_ANSWERS = {"ProofCreep": "before=9.0 after=1.0 engulf=0.5", "ProofCleave": "before=1 after=4",
                "ProofAurora": "active=True glow=0.1->0.9", "ProofCollapse": "heldForWarning=True",
                "ProofSlick": "moved=3 fuelCells=2", "ProofKnocker": "heard=2",
                "ProofHush": "hidden=True second=lunge", "ProofSipper": "before=9.0 after=1.0",
                "ProofTapper": "before=9.0 after=1.0", "ProofPooler": "fireLeft=False flameHurt=False"}


class _FakeT(object):
    """A modcheck test object whose bridge only records: EnterDeep answers `enter`, a def read answers found, and
    every Proof* answers a plausible pass string, so a chain runs end to end without a game."""
    def __init__(self, enter):
        self.enter, self.calls, self.args, self.furnished = enter, [], [], False
        self.upstream_failed, self.upstream_reason = False, None

    def _guard(self):
        return True

    def component(self, *a, **k):
        import contextlib
        return contextlib.nullcontext()

    def set_setting(self, *a, **k):
        return True

    def screenshot(self, *a, **k):
        return None

    def _record(self, *a, **k):
        return None

    def bridge_call(self, tool, **kw):
        self.calls.append((tool, kw.get("type"), kw.get("method")))
        self.args.append(kw.get("args"))
        if tool == "jawa/static_call" and kw.get("method") == "EnterDeep":
            self.furnished = "furnish" in str(kw.get("args") or "")
            return {"result": self.enter}
        if tool == "jawa/static_call" and kw.get("method") in ("ProofSipper", "ProofTapper") and not self.furnished:
            return {"result": "REFUSED: no colony battery on this map"}   # RM_DeepHarness furnishes only on 'furnish'
        if tool == "jawa/static_call" and kw.get("method") == "LeaveDeep":
            return {"result": "left stillListed=False"}
        if tool == "jawa/get_defs":
            return {"success": True, "foundCount": 1}
        return {"result": PASS_ANSWERS.get(kw.get("method"), "ok")}


def _probe_chains():
    """Run the four Deep-only chains of the REAL validation.py against _FakeT (modcheck stubbed): with a Deep that
    opens, the first bridge call must be jawa/static_call RM_DeepHarness.EnterDeep and the last LeaveDeep; with one
    that does not, the chain must make no Proof* call at all and mark itself upstream-failed."""
    import types
    bad, chains = [], {}

    class _Suite(object):
        def __init__(self, *a, **k):
            pass

        def chain(self, name, *a, **k):
            def deco(fn):
                chains[name] = fn
                return fn
            return deco

        def __getattr__(self, name):
            return lambda *a, **k: (lambda fn: fn)

    class _Fail(Exception):
        pass
    saved = sys.modules.get("modcheck")
    sys.modules["modcheck"] = types.SimpleNamespace(Suite=_Suite, ExpectationFailed=_Fail)
    try:
        ns = {"__name__": "lanterndeeps_validation_probe"}
        exec(compile(_read("validation.py"), os.path.join(HERE, "validation.py"), "exec"), ns)
    finally:
        if saved is None:
            sys.modules.pop("modcheck", None)
        else:
            sys.modules["modcheck"] = saved
    if ns.get("DEEP_HARNESS") != HARNESS:
        bad.append("validation.py DEEP_HARNESS is %r, not %s" % (ns.get("DEEP_HARNESS"), HARNESS))
    reached = set()
    enter = (("jawa/static_call", HARNESS, "EnterDeep"))
    leave = (("jawa/static_call", HARNESS, "LeaveDeep"))
    for name in DEEP_CHAINS:
        fn = chains.get(name)
        if fn is None:
            bad.append("validation.py registers no chain %s" % name)
            continue
        t = _FakeT(OPENED)
        try:
            fn(t)
        except _Fail as ex:
            bad.append("chain %s failed on passing fake answers inside an opened Deep: %s" % (name, ex))
        proofs = [c for c in t.calls if c[0] == "jawa/static_call" and (c[2] or "").startswith("Proof")]
        if not t.calls or t.calls[0] != enter:
            bad.append("chain %s: first bridge call is %r, not RM_DeepHarness.EnterDeep" % (name, t.calls[:1]))
        if not t.calls or t.calls[-1] != leave:
            bad.append("chain %s: last bridge call is %r, not RM_DeepHarness.LeaveDeep" % (name, t.calls[-1:]))
        if not proofs:
            bad.append("chain %s ran no Proof* call inside an opened Deep" % name)
        reached.update(c[2] for c in proofs)
        enter_args = [a for c, a in zip(t.calls, t.args) if c == enter]
        if not enter_args or "furnish" not in str(enter_args[0] or ""):
            bad.append("chain %s calls EnterDeep with args %r, not 'furnish' (an unfurnished Deep has no colony "
                       "battery for the sipper/tapper)" % (name, enter_args[:1]))
        else:
            ENTER_ARGS.add(str(enter_args[0]))
        if t.upstream_failed:
            bad.append("chain %s gave up inside an opened Deep: %s" % (name, t.upstream_reason))
        t = _FakeT("no map")
        try:
            fn(t)
        except _Fail:
            pass
        proofs = [c for c in t.calls if c[0] == "jawa/static_call" and (c[2] or "").startswith("Proof")]
        if proofs or not t.upstream_failed:
            bad.append("chain %s ran %d Proof* call(s) / upstream_failed=%s when EnterDeep opened no Deep"
                       % (name, len(proofs), t.upstream_failed))
    missing = [m for _, m, _ in PROOFS if m not in reached]
    if missing:
        bad.append("inside an opened, furnished Deep the chains never reached %s" % ",".join(missing))
    return bad


SLEEPINGICE = os.path.join(os.path.dirname(HERE), "SleepingIce", "validation.py")
HEAT_SOURCES = ("Heater", "Campfire")   # a heat pusher RM_HeatDial.IsWorkingHeater counts once it pushes heat


class _IceT(object):
    """A modcheck test object for SleepingIce's shivven chain. Like the real one, bridge_call does nothing once the
    chain is upstream-failed; `dial` is what RM_HeatDial.ProofDial answers."""
    def __init__(self, dial):
        self.dial, self.calls = dial, []
        self.session = object()
        self.upstream_failed, self.upstream_reason = False, None

    def _guard(self):
        return not self.upstream_failed

    def component(self, *a, **k):
        import contextlib
        return contextlib.nullcontext()

    def bridge_call(self, tool, **kw):
        if not self._guard():
            return None
        self.calls.append((tool, kw))
        if tool == "jawa/map_info":
            return {"sizeX": 250, "sizeZ": 250}
        method = kw.get("method")
        if method == "ProofDial":
            return {"result": self.dial}
        if method in ("ProofSeek", "ProofState"):
            return {"result": "state=seeking terrain=Ice source=Heater dist=9"}
        return {"success": True}


def _probe_shivven():
    """NIGHTSIDE half of the item: run the REAL SleepingIce validation.py shivven chain against _IceT (modcheck
    stubbed). Before ProofSeek (which refuses with no working player heater) the chain must: build a room floored
    with natural Soil (ProofSeek lays ice only on non-layerable ground), stand a heat source INSIDE that room as
    faction player (a factionless heater is never counted; an outdoor one never pushes heat), run the clock past the
    250-tick HottestSource cache, and read the dial. A dial reading 'heaters 0.0' must stop ProofSeek ever reaching
    the bridge."""
    import types
    bad, chains = [], {}

    class _Suite(object):
        def __init__(self, *a, **k):
            pass

        def chain(self, name, *a, **k):
            def deco(fn):
                chains[name] = fn
                return fn
            return deco

        def __getattr__(self, name):
            return lambda *a, **k: (lambda fn: fn)

    class _Fail(Exception):
        pass
    saved = sys.modules.get("modcheck")
    sys.modules["modcheck"] = types.SimpleNamespace(Suite=_Suite, ExpectationFailed=_Fail)
    try:
        with open(SLEEPINGICE, encoding="utf-8") as fh:
            src = fh.read()
        exec(compile(src, SLEEPINGICE, "exec"), {"__name__": "sleepingice_validation_probe", "__file__": SLEEPINGICE})
    finally:
        if saved is None:
            sys.modules.pop("modcheck", None)
        else:
            sys.modules["modcheck"] = saved
    fn = chains.get("shivven")
    if fn is None:
        return ["SleepingIce validation.py registers no shivven chain"]
    t = _IceT("DIAL 0.62 heaters 70.0 fires 0.0 power 0.0 rooms 1.0")
    try:
        fn(t)
    except _Fail as ex:
        bad.append("shivven chain failed on passing fake answers: %s" % ex)
    seek = [i for i, (tool, kw) in enumerate(t.calls) if kw.get("method") == "ProofSeek"]
    if not seek:
        return bad + ["shivven chain never calls RM_ShivvenProof.ProofSeek"]
    before = t.calls[:seek[0]]
    rooms, heat, ticks_after, dial_after = [], [], 0, False
    for tool, kw in before:
        if tool == "jawa/make_empty_room":
            m = re.match(r"\s*(\d+),(\d+),(\d+),(\d+)\s*$", str(kw.get("rect", "")))
            if m and kw.get("floorDef") == "Soil":
                rooms.append(tuple(int(g) for g in m.groups()))
        elif tool == "jawa/build_batch":
            for op in str(kw.get("ops", "")).split(";"):
                m = re.match(r"\s*(\w+):(\d+),(\d+)", op)
                if m and m.group(1) in HEAT_SOURCES and kw.get("faction") == "player":
                    x, z = int(m.group(2)), int(m.group(3))
                    if any(rx < x < rx + rw - 1 and rz < z < rz + rh - 1 for rx, rz, rw, rh in rooms):
                        heat.append((m.group(1), x, z))
                        ticks_after, dial_after = 0, False
        elif tool == "rimworld/step_game_ticks" and heat:
            ticks_after += int(kw.get("ticks", 0))
        elif kw.get("method") == "ProofDial" and heat:
            dial_after = ticks_after > 250
    if not rooms:
        bad.append("shivven chain builds no Soil-floored room before ProofSeek")
    if not heat:
        bad.append("shivven chain stands no player-faction %s inside its Soil room before ProofSeek"
                   % "/".join(HEAT_SOURCES))
    elif not dial_after:
        bad.append("shivven chain does not run >250 ticks and read RM_HeatDial.ProofDial between the heater and "
                   "ProofSeek (ticks after heater: %d)" % ticks_after)
    t = _IceT("DIAL 0.00 heaters 0.0 fires 0.0 power 0.0 rooms 0.0")
    try:
        fn(t)
    except _Fail:
        pass
    if any(kw.get("method") == "ProofSeek" for _, kw in t.calls) or not t.upstream_failed:
        bad.append("shivven chain still reaches ProofSeek (or stays measured) when the dial reads heaters 0.0")
    return bad


def offline():
    bad = []
    harness_cs = _read("Source/RM_DeepHarness.cs")
    if 'arg.Contains("furnish")' not in harness_cs or '"Battery"' not in harness_cs:
        bad.append("RM_DeepHarness.cs no longer stands a Battery on arg 'furnish'")
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
    bad += _probe_chains()
    shiv = _probe_shivven()
    bad += shiv
    for b in bad:
        print("FAIL " + b)
    print("OFFLINE %s: %d Deep-only chains wired, portal->generator->%s; shivven chain sites a heater: %s"
          % ("PASS" if not bad else "FAIL", deep_chains, ",".join(DEEP_COMPS), "yes" if not shiv else "NO"))
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
    if clause == "A2":
        # the Deep the SUITE opens, not one this script furnishes itself: use validation.py's own EnterDeep args
        ENTER_ARGS.clear()
        probe_bad = _probe_chains()
        if probe_bad or len(ENTER_ARGS) != 1:
            print("FAIL validation.py's Deep chains do not agree on one furnished EnterDeep: %s %s"
                  % (sorted(ENTER_ARGS), probe_bad[:3]))
            return 1
        enter_args = ENTER_ARGS.pop()
    else:
        enter_args = ""
    print("EnterDeep args: %r" % enter_args)
    entered = s.static(HARNESS, "EnterDeep", enter_args)
    print("EnterDeep: " + entered)
    ok = True
    try:
        if clause == "A1":
            info = s.call("jawa/map_info")
            print("map_info: " + json.dumps({k: info.get(k) for k in ("biome", "mapBiome", "sizeX", "mapIndex", "tile")}))
            ok = (info.get("mapBiome") == "RM_LanternDeeps" and entered.startswith("entered ") and "biome=RM_LanternDeeps" in entered and "pocket=True" in entered
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
