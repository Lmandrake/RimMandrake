#!/usr/bin/env python3
"""selftest_prove_gravship_fuel.py - prove_gravship.py fuels its ship by the mod list it finds.

PROVEGRAVSHIP_FIX_PIPES_FOR_ABSENT_VGE. LIVE 2026-11-06: on the Relentless game (no Vanilla Gravship Expanded) setup
laid VGE_AstrofuelPipe, the build failed ('FAIL: astrofuel pipe run built (12 cells)') and every gravship proof
(SEABED_DESCENT_ASCENT_1 among them) died before its clauses. Offline clauses, the script itself driven against a
fake bridge up to the first step after fuelling:

A1  gravship_fuel.fuel_mode: success -> pipe; "No ThingDef named ..." -> vanilla; a timeout, a typo'd def type or
    a non-dict -> None (no reading is never absence);
A2  fill labels match by exact prefix: VGE 'DEBUG: Fill', vanilla 'DEV: Set fuel to max'; 'Allow manual refill'
    and 'DEV: Set fuel to 0' never match;
A3  VGE ABSENT: the script lays no pipe, executes 'DEV: Set fuel to max' and reaches the thruster check;
A4  VGE PRESENT: the script lays the same 12-cell VGE_AstrofuelPipe run as before the fix and executes 'DEBUG: Fill';
A5  get_def gives no reading: the script exits 2 (UNMEASURED) and builds no pipe;
A6  prove_seabed_descent.py's refuel uses the shared is_fill_label, not a 'DEBUG: Fill' literal.
The running game's verdict (the vanilla ship's thruster goes active) is live clause A1 of this item.
"""
import os
import runpy
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gravship_fuel as gf  # noqa: E402

fails, ran = [], [0]


def check(name, ok, detail=""):
    ran[0] += 1
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else "  -- " + str(detail)))
    if not ok:
        fails.append(name)


class ReachedThrusterCheck(Exception):
    pass


class FakeBridge:
    """Answers the calls prove_gravship.py makes up to the thruster inspect, on an empty roof-free soil map."""

    def __init__(self, get_def_reply, gizmos):
        self.get_def_reply, self.gizmos = get_def_reply, gizmos
        self.things, self.builds, self.executed = {}, [], []

    def connect(self):
        pass

    def call(self, t, p):
        p = p or {}
        if t == "rimworld/get_game_info":
            return {"status": "main_menu"}
        if t == "jawa/gravship_status":
            return {"success": True, "engineCount": 0}
        if t == "jawa/get_roof_batch":
            return {"success": True, "roofs": ["None"] * 4}
        if t == "jawa/get_terrain_batch":
            return {"success": True, "terrains": ["Soil"] * 4}
        if t == "jawa/get_terrain_layers":
            return {"success": True, "cells": [{"x": 0, "z": 0, "isSubstructure": True}]}
        if t == "jawa/build_batch":
            self.builds.append(p["ops"])
            for op in p["ops"].split(";"):
                d, xy = op.split(":", 1)
                x, z = (int(v) for v in xy.split(",")[:2])
                self.things.setdefault((x, z), []).append({"defName": d})
            return {"success": True, "failed": 0}
        if t == "rimworld/get_cell_info":
            return {"cell": {"things": self.things.get((p["x"], p["z"]), [])}}
        if t == "jawa/get_def":
            return self.get_def_reply
        if t == "rimworld/list_selected_gizmos":
            return {"gizmos": [{"label": g, "gizmoId": i} for i, g in enumerate(self.gizmos)]}
        if t == "rimworld/execute_gizmo":
            self.executed.append(self.gizmos[p["gizmoId"]])
            return {"success": True}
        if t == "jawa/inspect_string":
            raise ReachedThrusterCheck()
        return {"success": True}


def drive(get_def_reply, gizmos):
    """Run prove_gravship.py whole against a FakeBridge. -> (bridge, outcome) with outcome 'reached' or exit code."""
    fake = FakeBridge(get_def_reply, gizmos)
    rb = types.ModuleType("rimbridge_client")
    rb.resolve_endpoint = lambda *a, **k: ("127.0.0.1", 0, "")
    rb.RimBridge = lambda **k: fake
    al = types.ModuleType("await_lifecycle")
    al.await_lifecycle = lambda call, state, timeout: types.SimpleNamespace(ok=True, reason="")
    saved = {k: sys.modules.get(k) for k in ("rimbridge_client", "await_lifecycle")}
    sys.modules.update(rimbridge_client=rb, await_lifecycle=al)
    out = open(os.devnull, "w")
    old_stdout, sys.stdout = sys.stdout, out
    try:
        runpy.run_path(os.path.join(HERE, "prove_gravship.py"), run_name="__main__")
        outcome = "finished"
    except ReachedThrusterCheck:
        outcome = "reached"
    except SystemExit as e:
        outcome = e.code
    finally:
        sys.stdout = old_stdout
        out.close()
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v
    return fake, outcome


def pipe_ops(fake):
    return [c for ops in fake.builds for c in ops.split(";") if c.startswith(gf.PIPE_DEF + ":")]


ABSENT = {"success": False, "message": "No ThingDef named 'VGE_AstrofuelPipe'."}
PRESENT = {"success": True, "defName": "VGE_AstrofuelPipe"}
VANILLA_GIZMOS = ["Allow manual refill", "DEV: Set fuel to 0", "DEV: Set fuel to 0.1", "DEV: Set fuel to max"]
VGE_GIZMOS = ["Allow manual refill", "DEBUG: Fill"]

# A1
check("A1 success -> pipe", gf.fuel_mode(PRESENT) == "pipe")
check("A1 'No ThingDef named' -> vanilla", gf.fuel_mode(ABSENT) == "vanilla")
for bad in ({"success": False, "message": "timeout"}, {"success": False, "message": "No def type named 'ThingDf'."},
            None, "x", {}):
    check("A1 no reading -> None: %r" % (bad,), gf.fuel_mode(bad) is None)

# A2
check("A2 VGE fill label", gf.is_fill_label("DEBUG: Fill (250)"))
check("A2 vanilla fill label", gf.is_fill_label("DEV: Set fuel to max"))
for bad in ("Allow manual refill", "DEV: Set fuel to 0", "DEV: Set fuel to 0.1", "", None, "fill"):
    check("A2 never matches %r" % (bad,), not gf.is_fill_label(bad))

# A3
fake, outcome = drive(ABSENT, VANILLA_GIZMOS)
check("A3 VGE absent: reaches the thruster check", outcome == "reached", outcome)
check("A3 VGE absent: no pipe laid", not pipe_ops(fake), pipe_ops(fake))
check("A3 VGE absent: ran 'DEV: Set fuel to max'", fake.executed == ["DEV: Set fuel to max"], fake.executed)

# A4: the pre-fix run, recomputed independently (site 30,40; thruster column tx = X+10)
X, Z = 30, 40
tx = X + 10
old = [(X + 14, pz) for pz in range(Z + 2, Z + 10)] + [(px, Z + 2) for px in range(X + 11, X + 14)] + [(tx, Z + 3)]
old = [c for c in dict.fromkeys(old) if c not in {(X + 14, Z + 10), (tx, Z + 1)}]
fake, outcome = drive(PRESENT, VGE_GIZMOS)
got = [tuple(int(v) for v in op.split(":", 1)[1].split(",")) for op in pipe_ops(fake)]
check("A4 VGE present: reaches the thruster check", outcome == "reached", outcome)
check("A4 VGE present: the same 12-cell pipe run", got == old and len(got) == 12, got)
check("A4 VGE present: ran 'DEBUG: Fill'", fake.executed == ["DEBUG: Fill"], fake.executed)

# A5
fake, outcome = drive({"success": False, "message": "timeout"}, VANILLA_GIZMOS)
check("A5 no reading: exit 2", outcome == 2, outcome)
check("A5 no reading: no pipe, no fill", not pipe_ops(fake) and not fake.executed, (pipe_ops(fake), fake.executed))

# A6
src = open(os.path.join(HERE, "prove_seabed_descent.py")).read()
check("A6 seabed refuel uses is_fill_label", "is_fill_label(g.get(\"label\"))" in src and
      'startswith("DEBUG: Fill")' not in src)
check("A6 prove_gravship has no pipe literal", '"VGE_AstrofuelPipe' not in
      open(os.path.join(HERE, "prove_gravship.py")).read())

print("\n%d/%d passed" % (ran[0] - len(fails), ran[0]))
sys.exit(1 if fails else 0)
