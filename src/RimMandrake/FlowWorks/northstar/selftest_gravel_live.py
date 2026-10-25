"""Offline checks for gravel_live.py (DIG_SPOIL_BUILD_GRAVEL_PAYS_ITS_WAY + PIT_DIG_FIX_SAND_SLIDES_BACK_IN): the four row
verdicts can fail, and every bridge call's kwargs match the tool schemas. No bridge."""
import ast
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gravel_live as G  # noqa: E402

fails = []


def check(name, cond):
    print("%-4s  %s" % ("ok" if cond else "FAIL", name))
    if not cond:
        fails.append(name)


def probe(accepted, reason=None):
    return {"success": True, "designator": {"accepted": accepted, "reason": reason}}


SLID = "Sand and mud slide back in: they cannot be dug."
check("sand refused + soil accepted -> PASS", G.sand_verdict(probe(False, SLID), probe(True))[0] == "PASS")
check("sand accepted -> FAIL", G.sand_verdict(probe(True), probe(True))[0] == "FAIL")
check("sand refused for another reason -> FAIL", G.sand_verdict(probe(False, "Must designate diggable soil"), probe(True))[0] == "FAIL")
check("soil control refused too -> UNMEASURED, never PASS", G.sand_verdict(probe(False, SLID), probe(False, "x"))[0] == "UNMEASURED")
check("probe failed -> UNMEASURED", G.sand_verdict({"success": False}, probe(True))[0] == "UNMEASURED")

T = [{"def": "RM_Gravel", "stackCount": 3}, {"def": "RM_Gravel", "stackCount": 2}, {"def": "ChunkGranite", "stackCount": 1},
     {"def": "Steel", "stackCount": 50}]
s = G.stacks(T, ("RM_Gravel", "ChunkGranite"))
check("stacks sums stackCount per def and ignores others", s == {"RM_Gravel": 5, "ChunkGranite": 1})
check("spoil_delta sees a merged gravel stack grow", G.spoil_delta({"RM_Gravel": 5}, {"RM_Gravel": 6}) == {"RM_Gravel": 1})

check("cut: one gravel -> PASS", G.cut_verdict({"RM_Gravel": 1, "ChunkGranite": 0}) == "PASS")
check("cut: one chunk -> PASS", G.cut_verdict({"RM_Gravel": 0, "ChunkGranite": 1}) == "PASS")
check("cut: nothing -> FAIL", G.cut_verdict({"RM_Gravel": 0, "ChunkGranite": 0}) == "FAIL")
check("cut: both -> FAIL", G.cut_verdict({"RM_Gravel": 1, "ChunkGranite": 1}) == "FAIL")
check("cut: one gravel but D0 -> D2 -> FAIL", G.cut_verdict({"RM_Gravel": 1, "ChunkGranite": 0}, 2) == "FAIL")


def raises(resp):
    try:
        G.things_of(resp)
    except G.MeasureError:
        return True
    return False


check("things_of: a failed list_things raises, never reads as an empty plot", raises({"success": False}) and raises(None) and raises({}))
check("things_of: a successful empty read is []", G.things_of({"success": True, "things": []}) == [])

check("mine: a miss gave gravel, a hit gave a chunk -> PASS", G.mine_verdict([(1, 0), (0, 1)], 2) == "PASS")
check("mine: a miss gave nothing -> FAIL", G.mine_verdict([(1, 0), (0, 0)], 2) == "FAIL")
check("mine: a chunk and gravel together -> FAIL", G.mine_verdict([(1, 1)], 1) == "FAIL")
check("mine: every wall chunked -> UNMEASURED, never PASS", G.mine_verdict([(0, 1), (0, 1)], 2) == "UNMEASURED")
check("mine: nothing mined -> UNMEASURED", G.mine_verdict([], 4) == "UNMEASURED")
check("mine: one gravel wall of four, three unmeasured -> UNMEASURED, never PASS", G.mine_verdict([(1, 0)], 4) == "UNMEASURED")
check("mine: a bad wall among unmeasured ones -> FAIL", G.mine_verdict([(0, 0)], 4) == "FAIL")

# ICE_YIELD_DECIDE_ONE_CUT_FOUR_NOTCHES + ICE_MELT_TAME_STACK_FLOOD (owner cards 2026-10-25)
L0 = [0, 0, 0, 0, 0]
check("melt: one crushed ice is one notch (10000 dL), not a 1x1 tank", G.MELT_DL == 10000)
check("melt: +10000 -> PASS; +40000 (the old tank yield) -> FAIL",
      G.melt_verdict(True, L0, [10000, 0, 0, 0, 0]) == "PASS" and G.melt_verdict(True, L0, [40000, 0, 0, 0, 0]) == "FAIL")
check("thaw: one pile left after the first melt, +1 notch each time -> PASS",
      G.thaw_verdict(1, L0, [0, 0, 10000, 0, 0], [5000, 0, 15000, 0, 0]) == "PASS")
check("thaw: the whole stack at once (the old flood) -> FAIL", G.thaw_verdict(0, L0, [20000, 0, 0, 0, 0], None) == "FAIL")
check("thaw: first melt right but the second never seen -> UNMEASURED, never PASS",
      G.thaw_verdict(1, L0, [10000, 0, 0, 0, 0], None) == "UNMEASURED")
check("thaw: nothing melted -> UNMEASURED", G.thaw_verdict(None, L0, None, None) == "UNMEASURED")
check("thaw: tanked/released columns are not world water", G.thaw_verdict(1, L0, [0, 0, 0, 10000, 0], None) == "FAIL")
check("thaw row is listed and tied to its item", "GS_crushed_ice_stack_thaws_one_at_a_time" in G.ROWS
      and G.ROW_ITEM["GS_crushed_ice_stack_thaws_one_at_a_time"] == "ICE_MELT_TAME_STACK_FLOOD")

P = {"success": True, "designationPresent": True, "workGiver": {"hasJobOnCell": True, "jobDef": "RM_FillInCanalJob"}, "pawn": {}}
check("job_gate accepts the expected job", G.job_gate(P, {"accepted": True}, "RM_FillInCanalJob")[0])
check("job_gate refuses a different job", not G.job_gate(P, {"accepted": True}, "RM_DigCanalJob")[0])
check("job_gate refuses a refused order", not G.job_gate(P, {"accepted": False}, "RM_FillInCanalJob")[0])

_here = os.path.dirname(os.path.abspath(__file__))
_schemas = json.load(open(os.path.join(_here, "..", "..", "Utils", "northstar_driver", "tool_schemas.json")))["tools"]
_tree = ast.parse(open(os.path.join(_here, "gravel_live.py")).read())
_bad, _seen = [], 0
for n in ast.walk(_tree):
    if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "call" and n.args \
            and isinstance(n.args[0], ast.Constant) and str(n.args[0].value).startswith(("jawa/", "rimworld/")):
        tool = n.args[0].value
        sch = _schemas.get(tool)
        if sch is None:
            continue
        _seen += 1
        for kw in n.keywords:
            if kw.arg and not kw.arg.startswith("_") and kw.arg not in sch["parameters"]:
                _bad.append("%s %s=" % (tool, kw.arg))
check("scanned some schema-known calls (instrument sees)", _seen >= 10)
check("gravel_live bridge kwargs all match tool signatures %s" % _bad, not _bad)
for need in ("jawa/set_terrain", "jawa/flowworks_job_probe", "jawa/ordered_job", "jawa/list_things"):
    check("schema knows %s (the scan covers it)" % need, need in _schemas)
check("list_things rect/defName/limit are schema params", {"rect", "defName", "limit"} <= set(_schemas["jawa/list_things"]["parameters"]))
print("%d failed" % len(fails))
sys.exit(1 if fails else 0)
