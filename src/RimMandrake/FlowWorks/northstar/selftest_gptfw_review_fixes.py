"""Offline guards for the GPT validation-suite review fixes (GPT_FW_REVIEW_VERIFY_REMAINING_FINDINGS).

Each case is the finding's failure scenario fed to the pure verdict it named; it failed before the fix and passes after.
  5.4 station_reach_live.rig_readable: tank=none / an unread water cell is no evidence the station skipped
  5.6 sitting_gaps_proof.s3_verdict: a hose with no readable poseCells is UNMEASURED, not "crosses nothing"
  6.5 walk_gaps_proof.thrown_verdict: a control that only gained RM_PitExposure did not fall
  5.9 / 6.1 validation_core.rows_exit: FAIL rows exit 1, UNMEASURED rows exit 2 (the drivers returned 0)
Run: python3 src/RimMandrake/FlowWorks/northstar/selftest_gptfw_review_fixes.py
"""
import ast
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


def t_station_reach():
    import station_reach_live as S
    check("5.4 station_reach exposes rig_readable", hasattr(S, "rig_readable"))
    if not hasattr(S, "rig_readable"):
        return
    good = {"kv": {"tank": "RM_Liquid_Water:0", "running": "True"}, "water0": [10, 12], "water1": [10, 12]}
    none_tank = dict(good, kv={"tank": "none", "running": "True"})
    blind = dict(good, water1=[10, None])
    check("5.4 a named tank with every read is a usable rig", S.rig_readable(good) is True)
    check("5.4 tank=none is not a usable rig", S.rig_readable(none_tank) is False)
    check("5.4 an unread water cell is not a usable rig", S.rig_readable(blind) is False)
    check("5.4 moved() still reads tank units", S.moved(dict(good, kv={"tank": "RM_Liquid_Water:7"})) == (True, 7))
    # review 2026-10-26: scene A graded on moved() with no readability gate; an unread fill after the wait read as a drop
    check("5.4 an unread fill after the wait is no channel fall",
          S.moved(dict(good, kv={"tank": "RM_Liquid_Water:0"}, water1=[None, None])) == (False, 0))
    check("5.4 a real channel fall still moves", S.moved(dict(good, water1=[9, 12]))[0] is True)


def t_s3():
    import sitting_gaps_proof as G
    laid = {"A": True, "B": True}
    st = G.s3_verdict(laid, {"A": [], "B": []}, {"A": True, "B": False}) if _takes(G.s3_verdict, 3) else ("PASS",)
    check("5.6 empty poseCells -> UNMEASURED", st[0] == "UNMEASURED", st)
    check("5.6 drawn and clear -> PASS", G.s3_verdict(laid, {"A": [], "B": []}, {"A": True, "B": True})[0] == "PASS"
          if _takes(G.s3_verdict, 3) else False)
    check("5.6 old two-argument call unchanged", G.s3_verdict(laid, {"A": [(1, 2)], "B": []})[0] == "FAIL")


def t_thrown():
    import walk_gaps_proof as W
    st = W.thrown_verdict([], ["RM_PitExposure"], True)
    check("6.5 control with only pit exposure -> UNMEASURED", st[0] == "UNMEASURED", st)
    check("6.5 control hurt, flyer unhurt -> PASS", W.thrown_verdict(["RM_PitExposure"], ["Bruise", "RM_PitExposure"], True)[0] == "PASS")
    check("6.5 control hurt, flyer hurt -> FAIL", W.thrown_verdict(["Bruise"], ["Bruise"], True)[0] == "FAIL")


def t_rows_exit():
    import validation_core as V
    check("5.9 validation_core.rows_exit exists", hasattr(V, "rows_exit"))
    if hasattr(V, "rows_exit"):
        check("rows_exit FAIL -> 1", V.rows_exit([{"status": "PASS"}, {"status": "FAIL"}, {"status": "UNMEASURED"}]) == 1)
        check("rows_exit UNMEASURED -> 2", V.rows_exit([{"status": "PASS"}, {"status": "UNMEASURED"}]) == 2)
        check("rows_exit all PASS -> 0", V.rows_exit([{"status": "PASS"}]) == 0)
        check("rows_exit no rows -> 2", V.rows_exit([]) == 2)
    # the two drivers must not end main() on a literal `return 0`
    for fn in ("sweep_identity_proof.py", "wet_costs_live.py"):
        with open(os.path.join(HERE, fn), encoding="utf-8") as f:
            tree = ast.parse(f.read())
        main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
        last = main.body[-1]
        lit0 = isinstance(last, ast.Return) and isinstance(last.value, ast.Constant) and last.value.value == 0
        check("5.9/6.1 %s main does not end in `return 0`" % fn, not lit0)


def _takes(fn, n):
    import inspect
    return len(inspect.signature(fn).parameters) >= n


def main():
    for t in (t_station_reach, t_s3, t_thrown, t_rows_exit):
        try:
            t()
        except Exception as e:  # noqa: BLE001 - a crash is a failed case, not a silent skip
            check(t.__name__ + " ran", False, repr(e))
    print("selftest_gptfw_review_fixes: %s" % ("FAIL %s" % FAILS if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
