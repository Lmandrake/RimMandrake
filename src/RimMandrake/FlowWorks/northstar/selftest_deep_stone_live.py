"""Offline checks for deep_stone_live.job_gate (DEEP_STONE_FIX_NOBODY_PICKS_UP_SHOVEL). No bridge."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deep_stone_live as D  # noqa: E402

fails = []


def check(name, cond):
    print("%-4s  %s" % ("ok" if cond else "FAIL", name))
    if not cond:
        fails.append(name)


P = {"success": True, "designationPresent": True,
     "workGiver": {"shouldSkip": False, "hasJobOnCell": True, "jobDef": "RM_DigCanalJob", "designationDeletedByWorkGiver": False},
     "pawn": {"workTypeDisabled": False}}
O = {"accepted": True}
check("probe ok + order accepted: go", D.job_gate(P, O)[0] is True)
check("can-fail: giver hands no job", D.job_gate(dict(P, workGiver=dict(P["workGiver"], hasJobOnCell=False)), O)[0] is False)
check("can-fail: wrong job def", D.job_gate(dict(P, workGiver=dict(P["workGiver"], jobDef="Mine")), O)[0] is False)
check("can-fail: mining disabled", D.job_gate(dict(P, pawn={"workTypeDisabled": True}), O)[0] is False)
check("can-fail: no designation", D.job_gate(dict(P, designationPresent=False), O)[0] is False)
check("can-fail: order refused", D.job_gate(P, {"accepted": False, "note": "x"})[0] is False)
check("can-fail: probe tool missing", D.job_gate({"success": False, "message": "no tool"}, O)[0] is False)
check("can-fail: empty", D.job_gate({}, {})[0] is False)

# DEEP_STONE_FIX_PROBE_NEVER_NAMES_PAWN: every B.call("jawa/<tool>", k=...) kwarg in deep_stone_live.py must be a real tool parameter.
import ast, json  # noqa: E402
_here = os.path.dirname(os.path.abspath(__file__))
_schemas = json.load(open(os.path.join(_here, "..", "..", "Utils", "northstar_driver", "tool_schemas.json")))["tools"]
_tree = ast.parse(open(os.path.join(_here, "deep_stone_live.py")).read())
_bad, _seen = [], 0
for n in ast.walk(_tree):
    if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "call" and n.args \
            and isinstance(n.args[0], ast.Constant) and str(n.args[0].value).startswith("jawa/"):
        tool = n.args[0].value
        sch = _schemas.get(tool)
        if sch is None:
            continue
        _seen += 1
        for kw in n.keywords:
            if kw.arg and not kw.arg.startswith("_") and kw.arg not in sch["parameters"]:
                _bad.append("%s %s=" % (tool, kw.arg))
check("scanned some schema-known calls (instrument sees)", _seen >= 3)
check("deep_stone_live bridge kwargs all match tool signatures %s" % _bad, not _bad)
print("%d failed" % len(fails))
sys.exit(1 if fails else 0)
