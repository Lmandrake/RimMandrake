"""Offline guards for FW_PROOF_DRIVERS_FIX_EARLY_FALSE_PASS (GPT review FF_validation_suite_3.x / 4.x / 5.1 / 6.6 / 6.7).

Each case feeds the finding's failure scenario (a missing, empty, truncated or stale read) to the driver code it named;
it failed on the old code (the driver read the blind case as PASS / exit 0) and passes after the fix. Grouped by driver.
Run: python3 src/RimMandrake/FlowWorks/northstar/selftest_falsepass_early.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
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


# ---------------------------------------------------------------------------------------------------- live_session.py
def t_live_session():
    import live_session as L

    class FeedS(object):
        mock = False

        def __init__(self, ride):
            self.pawns = {"ride": ride}
            self.calls = []

        def call(self, tool, **kw):
            if tool == "rimworld/list_colonists":
                return {"colonists": [{"pawnId": "P1"}, {"pawnId": "RIDE"}, {"pawnId": "P3", "dead": True}]}
            self.calls.append((tool, kw))
            return {"success": True}
    s = FeedS("RIDE")
    L.feed_colonists(s)
    ride_thirst = [kw for t, kw in s.calls if kw.get("pawn") == "RIDE" and kw.get("need") == "RM_Thirst"]
    check("3.1 feed_colonists never tops up the dehydration subject's RM_Thirst", not ride_thirst, ride_thirst)
    check("3.1 feed_colonists still tops up the other colonist's thirst",
          any(kw.get("pawn") == "P1" and kw.get("need") == "RM_Thirst" for t, kw in s.calls))

    if _has(L, "terrain_ops", "3.2") and _has(L, "flood_gone", "3.2"):
        check("3.2 a refused terrain read is unread, not ''", L.terrain_ops({"success": False}) is None)
        check("3.2 an empty terrain read is unread", L.terrain_ops({"success": True, "ops": ""}) is None)
        check("3.2 an unread flood read is not a recession", L.flood_gone(L.terrain_ops({"success": False})) is False)
        check("3.2 a read with no Flood is a recession", L.flood_gone("Soil:1,1,16,3") is True)
        check("3.2 a read with Flood is not", L.flood_gone("Floodwater:1,1,2,1") is False)
    if _has(L, "thaw_step", "3.2"):
        check("3.2 the ice count falling is a thaw", L.thaw_step([10, 7], 500) == 500)
        check("3.2 one read is no thaw", L.thaw_step([10], 500) is None)


# ---------------------------------------------------------------------------------------------------- player_missions.py
class _MB(object):
    """A bridge for player_missions.goal_check's chain branch: one colonist on the far bank, one destination tank that
    gained 4 drums, and a final pawn census that is TRUNCATED to one healthy pawn (the injured one is off the page)."""

    def __init__(self, truncated=True):
        self.truncated = truncated

    def call(self, tool, p=None):
        if tool == "rimworld/list_colonists":
            return {"colonists": [{"name": "Ada", "position": {"x": 50, "z": 50}}]}
        if tool == "jawa/list_pawns":
            r = {"pawns": [{"id": "A", "name": "Ada", "health": {"hediffs": [], "bleedRate": 0}}]}
            if self.truncated:
                r["truncated"] = 1
            else:
                r["pawns"].append({"id": "B", "name": "Bo", "health": {"hediffs": [], "bleedRate": 0}})
            return r
        if tool == "jawa/list_things":
            return {"things": [{"id": "RM_Tank7", "x": 10, "z": 10}], "isCompleteList": True}
        if tool == "rimworld/get_selection_semantics":
            return {"thingId": "RM_Tank7", "inspect": "Holding: 1 kL (1 kL / 2 kL)"}
        return {"success": True}


def _chain_run():
    return {"goal_check": {"kind": "chain", "far_bank": "far", "tank_def": "RM_Tank", "min_units": 1, "dest": "site"},
            "rects": {"far": [45, 45, 10, 10], "site": [5, 5, 10, 10]}, "colonist_roster": ["A", "B"],
            "tank_baseline": {"RM_Tank7": 0.0}}


def t_player_missions():
    import player_missions as P
    st, ev = P.goal_check(_MB(truncated=False), _chain_run())
    check("3.3 control: a full census with both colonists unhurt -> PASS", st == "PASS", (st, ev))
    st, ev = P.goal_check(_MB(truncated=True), _chain_run())
    check("3.3 a truncated final census is UNMEASURED, not PASS", st == "UNMEASURED", (st, ev.get("why")))

    if _has(P, "report_deadline", "3.4"):
        run = {"deadline": {"wall_s": 100, "ticks": 60000, "actions": 2}, "mission_start_wall": 1000.0, "tick0": 0}
        act = lambda end: {"kind": "act", "wall_end": end}
        check("3.4 inside every budget -> no deadline", P.report_deadline(run, [act(1050)], 100) is None)
        check("3.4 the last act ending past the wall budget is over",
              P.report_deadline(run, [act(1050), act(1101)], 100) is not None)
        obs = [act(1010), {"kind": "observe", "wall_end": 1020}, {"kind": "observe", "wall_end": 1030}]
        check("3.4 observes past the action budget are over", P.report_deadline(run, obs, 100) is not None)
        check("3.4 ticks past the deadline are still over", P.report_deadline(run, [act(1010)], 60001) is not None)


def t_live_session_late():
    import live_session as L
    downed = {"depth": 2}
    st = L.rescue_verdict(downed, {"id": "R", "undrafted": True})
    check("3.8 still in the pit with no medical bed read back -> UNMEASURED SITE", st == ("UNMEASURED", "SITE"), st)
    st = L.rescue_verdict(downed, {"id": "R", "undrafted": True, "bed": "Bed12"})
    check("3.8 still in with rescuer and bed -> FAIL MOD", st == ("FAIL", "MOD"), st)

    rows = [dict(id="RAID_a", item="I", criterion="raid", status="PASS", cls="MOD"),
            dict(id="RAID_outcome", item="I", criterion="raid", status="MEASURED", cls="MOD")]
    v = L.verdicts(rows).get(("I", "raid"))
    check("3.9 PASS + a descriptive MEASURED row -> pass", v is not None and v[0] == "pass", v)

    if _has(L, "guardrail_roundtrip_verdict", "3.11"):
        f, t = "<pitGuardrailEnabled>False</pitGuardrailEnabled>", "<other>1</other>"
        check("3.11 original False: flipped True then restored False -> PASS",
              L.guardrail_roundtrip_verdict(False, t, f) == "PASS")
        check("3.11 original True: flipped False then restored -> PASS", L.guardrail_roundtrip_verdict(True, f, t) == "PASS")
        check("3.11 original True: restore not written -> FAIL", L.guardrail_roundtrip_verdict("True", f, f) == "FAIL")
        check("3.11 original False: flip never written -> FAIL", L.guardrail_roundtrip_verdict("False", f, f) == "FAIL")


def t_preflight():
    import hashlib
    import tempfile
    import preflight_flowworks as PF
    import site_spec as S
    d = tempfile.mkdtemp(prefix="fp_e6_")
    dll = os.path.join(d, S.DLL_REL)
    os.makedirs(os.path.dirname(dll), exist_ok=True)
    with open(dll, "wb") as f:
        f.write(b"deployed")
    sha = hashlib.sha256(b"deployed").hexdigest()

    class E6S(object):
        def __init__(self, mvid_ok):
            self.mvid_ok = mvid_ok

        def call(self, tool, **kw):
            return {"success": True, "assemblyLocation": dll, "assemblyMvid": "m", "assemblyFileSha256": sha,
                    "mvidMatchesFile": self.mvid_ok}

    class P(object):
        deployed_mod = d
    old = PF.p_l1
    PF.p_l1 = lambda s, P, sc: PF.row("P-L1", PF.PASS, "ordered")
    try:
        ok_row = PF.p_e6(E6S(True), P, None)
        stale = PF.p_e6(E6S(False), P, None)
    finally:
        PF.p_l1 = old
    check("3.5 control: file and image match -> PASS", ok_row.status == PF.PASS, ok_row.evidence)
    check("3.5 mvidMatchesFile false (stale loaded image) -> FAIL", stale.status == PF.FAIL, stale.evidence)

    if _has(PF, "absent_fields", "3.13"):
        snap = {"RimMandrake.FlowWorks.RM_Settings": {"a": True, "b": "ABSENT"}}
        check("3.13 absent_fields names the ABSENT field", PF.absent_fields(snap) == ["RM_Settings.b"])
    import ast
    with open(os.path.join(HERE, "prep_site.py"), encoding="utf-8") as f:
        tree = ast.parse(f.read())
    prep = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "prep")
    calls = {getattr(n.func, "attr", None) for n in ast.walk(prep) if isinstance(n, ast.Call)}
    check("3.13 prep_site.prep refuses on absent_fields, as P-B4 does", "absent_fields" in calls)


def t_perf_and_reach():
    import pipe_levelling_perf_proof as LP
    if _has(LP, "staged_basins_ok", "3.6"):
        good = {"basin": (0, 0, 2, 2), "cells": 4, "dug": 4, "filled": 4, "refusedFills": 0}
        check("3.6 dug and filled -> staged", LP.staged_basins_ok([good]))
        check("3.6 dug but fills refused -> not staged", not LP.staged_basins_ok([dict(good, filled=0, refusedFills=4)]))
    kv = {"msAvg": "0.1", "msPerTick": "0.001", "allocKBAvg": "1", "moves": "0"}
    check("3.6 a timed cycle that moved nothing is not a perf PASS", LP.tick_verdict(kv, 5, 5, True)[0] == "UNMEASURED",
          LP.tick_verdict(kv, 5, 5, True))
    check("3.6 alloc row: moved nothing -> not PASS", LP.alloc_verdict(kv, 5, 5, True)[0] == "UNMEASURED")
    check("3.6 control: moved -> PASS", LP.tick_verdict(dict(kv, moves="3"), 5, 5, True)[0] == "PASS")

    import reach_map_proof as R
    if _has(R, "exit_code", "3.12"):
        rows = [{"status": "PASS", "class": "MOD"}, {"status": "UNMEASURED", "class": "SITE"},
                {"status": "UNMEASURED", "class": "OWED"}]
        check("3.12 a requested pair UNMEASURED/SITE exits 2", R.exit_code(rows) == 2)
        check("3.12 PASS + OWED only exits 0", R.exit_code([rows[0], rows[2]]) == 0)


def main():
    for t in (t_live_session, t_player_missions, t_live_session_late, t_preflight, t_perf_and_reach):
        try:
            t()
        except Exception as e:          # noqa: BLE001 -- a crash is a red check, not a silent skip
            check("%s ran" % t.__name__, False, "%s: %s" % (type(e).__name__, e))
    print("%d FAIL" % len(FAILS) if FAILS else "all ok")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
