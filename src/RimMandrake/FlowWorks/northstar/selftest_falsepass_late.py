"""Offline guards for FW_PROOF_DRIVERS_FIX_LATE_FALSE_PASS (GPT review FF_validation_suite_7.3 - 7.10).

Each case feeds the finding's failure scenario (a short read, a failed staging write, an ordered-not-done ladder, a swell
frozen after it finished, a site the mechanism cannot reach, a switch credited by a row that runs it OFF) to the code it
named; it failed on the old code and passes after the fix. Grouped by driver.
Run: python3 src/RimMandrake/FlowWorks/northstar/selftest_falsepass_late.py
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, MOD)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "Utils")))

FAILS = []


def check(name, ok, detail=""):
    print(("ok   " if ok else "FAIL ") + name + ("" if ok else "  " + str(detail)))
    if not ok:
        FAILS.append(name)


def _has(mod, name, finding):
    ok = hasattr(mod, name)
    check("%s %s.%s exists" % (finding, mod.__name__, name), ok)
    return ok


# ------------------------------------------------------------------------------------------- review_map_rivers.py
def t_review_map_rivers():
    import review_map_rivers as RV
    # 7.3: a gallery asking for two of a def read ONE back -- the old set comparison called that complete
    if _has(RV, "missing_defs", "7.3"):
        m = RV.missing_defs([("RM_LiquidTank", 1, 1), ("RM_LiquidTank", 4, 1), ("RM_Vat", 2, 2)],
                            [{"def": "RM_LiquidTank"}, {"defName": "RM_Vat"}])
        check("7.3 two asked, one read -> short by one", m == ["RM_LiquidTank x1"], m)
        check("7.3 all read -> nothing missing",
              RV.missing_defs([("A", 0, 0), ("A", 1, 0)], [{"def": "A"}, {"def": "A"}]) == [])
        check("7.3 none read -> bare name", RV.missing_defs([("A", 0, 0)], []) == ["A"])
    # 7.4: a failed terrain/spawn/pawn write, or a short build, is FAIL; nothing to read and nothing failed is UNMEASURED
    if _has(RV, "river_verdict", "7.4"):
        check("7.4 staging write failed -> FAIL", RV.river_verdict(False, [], ["terrain RM_Ford"]) is False)
        check("7.4 staging failed although buildings read -> FAIL", RV.river_verdict(True, [], ["spawn"]) is False)
        check("7.4 building short -> FAIL", RV.river_verdict(True, ["RM_Weir"], []) is False)
        check("7.4 nothing built, nothing failed -> UNMEASURED", RV.river_verdict(False, [], []) is None)
        check("7.4 built and read back -> PASS", RV.river_verdict(True, [], []) is True)


# ------------------------------------------------------------------------------------------------- review_map.py
class _B(object):
    def __init__(self, log):
        self.log = log

    def ticks(self, n):
        self.log.append(("ticks", n))


class _Fake(object):
    def __init__(self):
        self.log = []
        self.B = _B(self.log)
        self.notes = []

    def hose_cmd(self, n, cmd):
        self.log.append(("hose", cmd))

    def call(self, tool, **kw):
        self.log.append(("call", tool))
        return {"survived": 1}


def t_review_map():
    import review_map as R
    # 7.5: the player's button only ORDERS the move ("Ladder up (ordered)"); the frozen map must show the state itself
    if _has(R, "ladder_plan", "7.5"):
        ordered = [{"label": "Ladder up (ordered)", "id": 1}, {"label": "DEV: ladder up now", "id": 2}]
        act, g = R.ladder_plan(ordered, "raise")
        check("7.5 'ordered' is not done; press the DEV set-now button", act == "press" and g and g["id"] == 2, (act, g))
        check("7.5 exact 'Ladder up' -> done", R.ladder_plan([{"label": "Ladder up"}], "raise")[0] == "done")
        check("7.5 only an order button -> cannot set (None)",
              R.ladder_plan([{"label": "Ladder down (ordered)"}], "lower") == (None, None))
        check("7.5 Review.ladder_set exists", hasattr(R.Review, "ladder_set"))
    # 7.6: the Filling hose is frozen mid-swell: from its flow order to the end of late_hoses < one transition
    T = R.HOSE_TRANSITION_TICKS
    S = [{"n": 1, "placeholder": False, "origin": (0, 0),
          "setup": {"hose_flow": [(1, 1, "Plump"), (3, 1, "Filling")], "hose_reelin": [(5, 1)],
                    "build_after": [("Wall", 2, 2, None, "WoodLog")]}}]
    f = _Fake()
    R.Review.late_hoses(f, S)
    i = next((k for k, e in enumerate(f.log) if e == ("hose", "flow:3,1=on")), None)
    after = sum(e[1] for e in f.log[i + 1:] if e[0] == "ticks") if i is not None else None
    check("7.6 Filling flow ordered", i is not None, f.log)
    check("7.6 ticks after the Filling order < transition (%d)" % T, after is not None and after < T, (after, f.log))
    j = next((k for k, e in enumerate(f.log) if e == ("hose", "flow:1,1=on")), None)
    plump = sum(e[1] for e in f.log[j + 1:] if e[0] == "ticks") if j is not None else 0
    check("7.6 Plump hose gets >= a transition", plump >= T, (plump, f.log))
    # 7.8: TanksFor reads adj8 tanks only -- each 2x2 tank must touch the 1x1 vat
    st = R.SETUPS["carry_kits"]

    def rect(x, z, w, h):
        x0, z0 = x - (w - 1) // 2, z - (h - 1) // 2       # GenAdj.OccupiedRect, rotation North
        return {(a, b) for a in range(x0, x0 + w) for b in range(z0, z0 + h)}

    def touches(A, Bc):
        return any(abs(a[0] - b[0]) <= 1 and abs(a[1] - b[1]) <= 1 for a in A for b in Bc)
    vats = [rect(x, z, 1, 1) for d, x, z, _r, _s in st["build"] if d == "RM_ReactionVat"]
    tanks = [rect(x, z, 2, 2) for d, x, z, _r, _s in st["build"] if d == "RM_LiquidTank"]
    check("7.8 one vat, two tanks staged", len(vats) == 1 and len(tanks) == 2, st["build"])
    check("7.8 every tank touches the vat", vats and all(touches(t, vats[0]) for t in tanks), st["build"])
    check("7.8 tanks do not overlap the vat", vats and all(not (t & vats[0]) for t in tanks), st["build"])
    tank_cells = {(x, z) for x, z, *_ in st["tank"]}
    built = {(x, z) for d, x, z, _r, _s in st["build"] if d == "RM_LiquidTank"}
    check("7.8 the filled tanks are the built tanks", tank_cells == built, (tank_cells, built))
    # 7.9: NotifyFireAt reaches adj8 only -- the 'light here' mark must touch a liquid cell
    for name in ("fire_lights", "fire_out", "look_fire"):
        s = R.SETUPS[name]
        liquid = set()
        for x, z, w, h, _d in s.get("dig", []):
            liquid |= {(a, b) for a in range(x, x + w) for b in range(z, z + h)}
        mx, mz = s["marks"][0][0], s["marks"][0][1]
        check("7.9 %s mark (%d,%d) is adj8 to its canal" % (name, mx, mz), touches({(mx, mz)}, liquid))


# ------------------------------------------------------------------------------------------------- validation.py
def t_validation():
    spec = importlib.util.spec_from_file_location("fw_validation_falsepass_late", os.path.join(MOD, "validation.py"))
    vm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vm)
    # 7.10: thirst_live.py's T3 runs with heat scaling OFF -- crediting the switch certified ON with no row measuring it
    t3 = next((r for r in vm.THIRST_LIVE if r[0] == "T3_need_falls"), None)
    check("7.10 T3_need_falls row present", t3 is not None)
    check("7.10 T3 claims no toggle", t3 is not None and t3[1] is None, t3 and t3[1])
    check("7.10 thirstHeatScaling named owed", "thirstHeatScaling" in vm.EXTENSION_TOGGLES_OWED)


def main():
    for t in (t_review_map_rivers, t_review_map, t_validation):
        try:
            t()
        except Exception as e:          # noqa: BLE001 -- a crash is a red check, not a silent skip
            check("%s ran" % t.__name__, False, "%s: %s" % (type(e).__name__, e))
    print("%d FAIL" % len(FAILS) if FAILS else "all ok")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
