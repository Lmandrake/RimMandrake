"""Offline guards for FW_PROOF_DRIVERS_FIX_LATE_FALSE_PASS (GPT review F_validation_suite 7.3 - 7.10 and 8.1 - 8.9).

Each case feeds the finding's failure scenario (a short read, a failed staging write, an ordered-not-done ladder, a swell
frozen after it finished, a site the mechanism cannot reach, a switch credited by a row that runs it OFF) to the code it
named; it failed on the old code and passes after the fix. Grouped by driver. Section 8 (GimmeSomeSlack's northstar
matrix, proof_all, pole_shots) is here too: one late-false-pass item covers both sections.
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
    _t_rivers_build(RV)


class _RB(object):
    """A bridge for review_map_rivers.build: `fail` names the staging tools that refuse; list_things reads `built`."""
    def __init__(self, fail=(), built=("RM_Weir",)):
        self.fail, self.built, self.calls = set(fail), list(built), []

    def call(self, tool, **kw):
        self.calls.append(tool)
        if tool == "jawa/map_info":
            return {"success": True, "sizeX": 50, "sizeZ": 50}
        if tool == "jawa/static_call":
            return {"success": True, "result": "current=3 cells"}
        if tool in self.fail:
            return {"success": False, "error": "refused"} if tool != "jawa/build_batch" else {"survived": 0, "failed": ["x"]}
        if tool == "jawa/list_things":
            return {"success": True, "things": [{"def": d} for d in self.built] if "rect" in kw and "defName" not in kw else []}
        if tool == "jawa/spawn_pawn":
            return {"success": True, "pawns": [{"id": 7}]}
        if tool == "jawa/build_batch":
            return {"success": True, "survived": 1}
        return {"success": True}


class _RR(object):
    def __init__(self, B):
        self.B, self.notes = B, []

    def call(self, tool, **kw):
        r = self.B.call(tool, **kw)
        return r if isinstance(r, dict) else {}

    def say(self, msg):
        pass


def _t_rivers_build(RV):
    """7.4: build() records every failed staging write per station and hands it to river_verdict (it was never recorded:
    a refused terrain/item/pawn write still read 'built' whenever the buildings were found)."""
    from modcheck import reviewmap as RMH
    st = {"id": "ford"}
    cr = ((10, 10), 1, 3, (14, 10))
    o = {"terrain": [("RM_Ford", (11, 10))], "build": [("RM_Weir", (12, 10), None, None)], "hp": [],
         "items": [("Steel", 5, (13, 10))], "pawns": [("Muffalo", (12, 11), None, "")], "label": "R1"}
    saved = (RV.read_terrain, RV.plan, RV.labels, RV.sign_ops, RMH.place_signs)
    RV.read_terrain = lambda B, size: {}
    RV.plan = lambda terr, size: ([(st, cr, o)], [])
    RV.labels = lambda B, placed, line: None
    RV.sign_ops = lambda placed: []
    RMH.place_signs = lambda B, ops: {"count": 1}
    try:
        for fail, want, tag in ((("jawa/set_terrain_batch",), False, "terrain"),
                                (("rimworld/spawn_thing",), False, "item"),
                                (("jawa/spawn_pawn",), False, "pawn"),
                                (("jawa/build_batch",), False, "build"),
                                ((), True, None)):
            _p, verify = RV.build(_RR(_RB(fail)), "x")
            v = verify.get("R1") or {}
            check("7.4 build(): %s -> ok %s" % (fail[0] if fail else "nothing refused", want), v.get("ok") is want, v)
            if tag:
                check("7.4 build(): %s write named in staging_failed" % tag,
                      any(f.startswith(tag) for f in v.get("staging_failed") or []), v)
    finally:
        RV.read_terrain, RV.plan, RV.labels, RV.sign_ops, RMH.place_signs = saved


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
        _t_ladder_set(R)
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
    _t_clear_keeps_held(R)


class _LB(object):
    """list_selected_gizmos replies in turn from `seq` (the last repeats); execute_gizmo answers `ex`."""
    def __init__(self, seq, ex=None):
        self.seq, self.ex, self.pressed = list(seq), ex if ex is not None else {"success": True}, []

    def call(self, tool, **kw):
        if tool == "rimworld/list_selected_gizmos":
            return {"success": True, "gizmos": self.seq.pop(0) if len(self.seq) > 1 else self.seq[0]}
        if tool == "rimworld/execute_gizmo":
            self.pressed.append(kw.get("gizmoId"))
            return self.ex
        return {"success": True}


def _t_ladder_set(R):
    """7.5: Review.ladder_set presses the DEV set-now button and returns True only once the player's button READS done."""
    order = {"label": "Ladder up (ordered)", "gizmoId": 1}
    dev = {"label": "DEV: ladder up now", "gizmoId": 2}
    b = _LB([[order, dev], [{"label": "Ladder up", "gizmoId": 1}, dev]])
    r = R.Review(b)
    check("7.5 ladder_set: DEV pressed, then reads 'Ladder up' -> True", r.ladder_set(5, (3, 3), "raise") is True and b.pressed == [2],
          (b.pressed, r.notes))
    b = _LB([[order, dev]])
    r = R.Review(b)
    check("7.5 ladder_set: pressed but never reads done -> False", r.ladder_set(5, (3, 3), "raise") is False, b.pressed)
    check("7.5 ladder_set: 'never read' noted", any("never read" in n for n in r.notes), r.notes)
    b = _LB([[order, dev]], ex={"success": False, "error": "no"})
    r = R.Review(b)
    check("7.5 ladder_set: DEV button refused -> False", r.ladder_set(5, (3, 3), "raise") is False and
          any("refused" in n for n in r.notes), r.notes)
    b = _LB([[{"label": "Ladder down (ordered)", "gizmoId": 1}]])
    r = R.Review(b)
    check("7.5 ladder_set: only an order button -> False", r.ladder_set(5, (3, 3), "lower") is False, r.notes)


class _CB(object):
    """review_map.clear's bridge: one muffalo held in a kept gallery station, one raider loose outside it."""
    def __init__(self, held_at, loose_at):
        self.calls = []
        self.pawns = [{"id": 11, "x": held_at[0], "z": held_at[1], "kind": "Muffalo"},
                      {"id": 12, "x": loose_at[0], "z": loose_at[1], "kind": "Raider", "faction": "Pirates"}]

    def call(self, tool, **kw):
        self.calls.append((tool, kw))
        if tool == "jawa/list_pawns":
            return {"success": True, "pawns": [] if "rect" in kw else self.pawns}
        return {"success": True, "matchedCount": 2}


def _t_clear_keeps_held(R):
    """7.7: `--only visuals` rebuilt the visuals rect and swept map-wide (destroy_bulk nonColonists), killing the
    gallery's held animals and prisoners under signs still describing them. A partial rebuild keeps the part it leaves."""
    if not _has(R.Review, "held_rects", "7.7"):
        return
    S = [{"n": 1, "placeholder": False, "origin": (200, 200), "setup": {"keep": True}},
         {"n": 2, "placeholder": False, "origin": (240, 200), "setup": {}}]
    r = R.Review(None)
    kr = r.held_rects(S, "visuals")
    check("7.7 --only visuals holds the kept station's rect", len(kr) == 1 and kr[0][0] <= 200 < kr[0][0] + kr[0][2], kr)
    check("7.7 a full build holds nothing over", r.held_rects(S, None) == [] and r.held_rects(S, "gallery") == [])
    b = _CB((200, 200), (5, 5))
    r = R.Review(b)
    r.clear(S, {"stations": []}, only="visuals")
    tools = [t for t, _ in b.calls]
    check("7.7 clear(only=visuals) never destroy_bulks map-wide", "jawa/destroy_bulk" not in tools, tools)
    killed = [kw.get("pawn") for t, kw in b.calls if t == "jawa/pawn_force_incapacitate"]
    check("7.7 the loose raider is swept, the held muffalo is not", killed == ["12"], killed)


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


# --------------------------------------------------------------- GimmeSomeSlack: northstar matrix, proof_all, pole_shots
GSS = os.path.abspath(os.path.join(MOD, "..", "GimmeSomeSlack"))
NSM = os.path.join(GSS, "northstar_matrix")


def _gss_path():
    for p in (GSS, NSM):                      # NSM first: its scenes.py, not Utils/scenes (a package)
        if p in sys.path:
            sys.path.remove(p)
        sys.path.insert(0, p)
    sys.modules.pop("scenes", None)


def _cs_consts():
    """FlatVisible, PlumpExtra, WireVisibleWidth as shipped in FlowWorks/Source/Hose/HoseMath.cs."""
    import re
    src = open(os.path.join(MOD, "Source", "Hose", "HoseMath.cs"), encoding="utf-8").read()
    m = re.search(r"FlatVisible\s*=\s*([0-9.]+)\s*,\s*PlumpExtra\s*=\s*([0-9.]+)", src)
    w = re.search(r"WireVisibleWidth\s*=\s*([0-9. */+-]+);", src)
    if not (m and w):
        return None
    return float(m.group(1)), float(m.group(2)), eval(w.group(1), {"__builtins__": {}})   # noqa: S307 -- digits and */ only


def _func_src(path, name):
    import ast
    src = open(path, encoding="utf-8").read()
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.FunctionDef) and n.name == name:
            return ast.get_source_segment(src, n) or ""
    return ""


def t_gss():
    _gss_path()
    import design_spec as DS
    import fakegame as FG
    import run_live as RL
    # 8.1: the spec held the pre-2026-10-22 0.38/0.085 widths and a 4.0 ratio, so every correct live hose failed
    cs = _cs_consts()
    check("8.1 HoseMath.cs widths parsed", cs is not None)
    if cs and _has(DS, "hose_widths", "8.1"):
        f, p, w = cs
        check("8.1 design_spec widths == HoseMath.cs", abs(DS.HOSE_FLAT_VISIBLE - f) < 1e-9 and abs(DS.HOSE_PLUMP_EXTRA - p) < 1e-9
              and abs(DS.HOSE_WIRE_VISIBLE - w) < 1e-9, (DS.HOSE_FLAT_VISIBLE, DS.HOSE_PLUMP_EXTRA, DS.HOSE_WIRE_VISIBLE, cs))
        check("8.1 fakegame widths == HoseMath.cs", abs(FG.FLAT_VISIBLE - f) < 1e-9 and abs(FG.PLUMP_EXTRA - p) < 1e-9,
              (FG.FLAT_VISIBLE, FG.PLUMP_EXTRA, cs))
        lo, hi = DS.hose_widths("Flat")
        check("8.1 a shipped flat hose is inside the Flat window", lo <= f <= hi, (lo, hi, f))
        lo, hi = DS.hose_widths("Plump")
        check("8.1 a shipped plump hose is inside the Plump window", lo <= f + p <= hi, (lo, hi, f + p))
        check("8.1 the shipped flat hose clears the width/wire floor", f / w >= DS.HOSE_WIDTH_OVER_WIRE_GE,
              (f / w, DS.HOSE_WIDTH_OVER_WIRE_GE))
    # 8.2: SL3 read the floor cords before and after the load and never compared them
    sl = _func_src(os.path.join(GSS, "northstar", "proof_all.py"), "save_load")
    check("8.2 SL3 compares the floor cord sets", "_cord_set(cords_a)" in sl and "_cord_set(cords_b)" in sl)
    # 8.4: a refused fresh probe ({"success": False, "error": ...}) is truthy with no counters -- it read as fresh
    if _has(RL, "fresh_bad", "8.4"):
        good = {"success": True, "edges": 9, "different": 0, "missing": 0, "extra": 0}
        check("8.4 refused fresh reply -> bad", RL.fresh_bad([{"id": "B1", "fresh": {"success": False, "error": "timeout"}}]) != [])
        check("8.4 no fresh reply -> bad", RL.fresh_bad([{"id": "B1"}]) != [])
        check("8.4 an extra cached edge -> bad", RL.fresh_bad([{"id": "B1", "fresh": dict(good, extra=1)}]) != [])
        check("8.4 a clean fresh reply -> not bad", RL.fresh_bad([{"id": "B1", "fresh": good}]) == [])
        check("8.4 proof_all.determinism uses fresh_bad",
              "fresh_bad(" in _func_src(os.path.join(GSS, "northstar", "proof_all.py"), "determinism"))
    # 8.5 / 8.7: a scene whose staging failed, or whose factors are never staged, matched nothing it names
    if _has(RL, "scene_status", "8.5"):
        check("8.5 staging failed, census matches -> UNMEASURED SITE",
              RL.scene_status("floor", False, [], True) == ("UNMEASURED", "SITE"))
        check("8.5 mismatch + staging failed -> FAIL SITE", RL.scene_status("floor", False, ["x"], True) == ("FAIL", "SITE"))
        check("8.5 clean -> PASS", RL.scene_status("floor", False, [], False)[0] == "PASS")
        check("8.7 unstaged factors -> UNMEASURED HARNESS",
              RL.scene_status("matrix", True, [], False, ["hose=flat"]) == ("UNMEASURED", "HARNESS"))
        sc = RL.load_catalog("matrix")["scenes"]
        lev = [x for x in sc if any(x["factors"].get(k) not in (None, "none") for k in ("aerial", "hose"))]
        check("8.7 every matrix case with an aerial/hose level carries it as unstaged",
              lev and all(x.get("unstaged") for x in lev), len(lev))
        check("8.7 a case with neither carries none", all(not x.get("unstaged") for x in sc if x not in lev))
    # 8.6: a completed run with FAIL rows exited 0
    if _has(RL, "run_exit", "8.6"):
        check("8.6 FAIL row -> 1", RL.run_exit({"rows": [{"status": "PASS"}, {"status": "FAIL"}]}) == 1)
        check("8.6 UNMEASURED row -> 2", RL.run_exit({"rows": [{"status": "UNMEASURED"}]}) == 2)
        check("8.6 no rows -> 2", RL.run_exit({"rows": []}) == 2)
        check("8.6 aborted -> 1", RL.run_exit({"aborted": "x", "rows": [{"status": "PASS"}]}) == 1)
        check("8.6 all PASS -> 0", RL.run_exit({"rows": [{"status": "PASS"}]}) == 0)
        check("8.6 main returns run_exit", "run_exit(" in _func_src(os.path.join(NSM, "run_live.py"), "main"))
    # 8.8: every run wrote SHOTS/<name>.png, so a later run overwrote the shots an earlier record points at
    if _has(RL, "shot_run_dir", "8.8"):
        check("8.8 two runs in the same second get two folders", RL.shot_run_dir(1.0e9, 11) != RL.shot_run_dir(1.0e9, 12))
        src = open(os.path.join(NSM, "run_live.py"), encoding="utf-8").read()
        check("8.8 the shot record points into the run folder", 'self.shot_run + "/" + name' in src)
    # 8.9: masts with a STORED look were shot under every global look -- four identical pictures, four labels
    import pole_shots as PS
    if _has(PS, "default_look_masts", "8.9"):
        st = {"masts": [(1, 2, 3), (4, 5, 6, "Cybertek"), (7, 8, 9, None)]}
        check("8.9 stored-look masts are not default-look", PS.default_look_masts(st) == [(1, 2, 3), (7, 8, 9, None)],
              PS.default_look_masts(st))
        check("8.9 a station of stored looks only has none", PS.default_look_masts({"masts": [(1, 2, 3, "StarWars")]}) == [])


def main():
    for t in (t_review_map_rivers, t_review_map, t_validation, t_gss):
        try:
            t()
        except Exception as e:          # noqa: BLE001 -- a crash is a red check, not a silent skip
            check("%s ran" % t.__name__, False, "%s: %s" % (type(e).__name__, e))
    print("%d FAIL" % len(FAILS) if FAILS else "all ok")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
