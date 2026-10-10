#!/usr/bin/env python3
"""Selftest for lint_calls.py (LINT_CALLS_1). Offline; no bridge.

    python3 src/RimMandrake/Utils/northstar_driver/selftest_lint_calls.py

Named selftest_*.py because run_selftests.py discovers `selftest*.py` (a differently
named file would never run). Falsification: the real defects measured 2026-10-01 are
linted against the COMMITTED snapshot and must be flagged; a correct call must pass.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lint_calls as L          # noqa: E402
import tool_schemas as T        # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, detail))
    if not cond:
        FAILS.append(name)


def kinds(src, tools):
    return [(r[1], r[2]) for r in L.lint_source(src, "x.py", tools)]


tools = L.load_tools()

# --- sanity probes: the snapshot can see things (a lint that finds nothing must prove it can find something)
check("snapshot has >=400 tools", len(tools) >= 400, "(%d)" % len(tools))
check("snapshot knows jawa/set_draft params",
      {"pawnId", "drafted", "fireAtWill"} <= set(tools["jawa/set_draft"]["parameters"]))
check("snapshot knows a required param somewhere", any(v["required"] for v in tools.values()))

# --- falsification: the real defects, against the real snapshot
k = kinds('t.bridge_call("jawa/set_draft", pawnId=p, draft=True)', tools)
check("set_draft draft= flagged UNDECLARED", ("jawa/set_draft", "UNDECLARED_PARAM") in k, str(k))
k = kinds('t.bridge_call("jawa/set_plants", defName="Plant_Grass", rect="1,1,2,2")', tools)
check("set_plants defName flagged", k.count(("jawa/set_plants", "UNDECLARED_PARAM")) == 2, str(k))
k = kinds('t.bridge_call("jawa/set_draft", pawnId=p, drafted=True)', tools)
check("correct set_draft passes", k == [], str(k))
k = kinds('t.bridge_call("jawa/set_plants", ops="Plant_Grass:1,1,2,2", growth=1.0)', tools)
check("correct set_plants passes", k == [], str(k))

# --- every call shape
check("unknown tool", kinds('s.call("jawa/no_such_tool")', tools) == [("jawa/no_such_tool", "UNKNOWN_TOOL")])
check("_call(s, ...) shape", ("jawa/set_draft", "UNDECLARED_PARAM") in kinds('_call(s, "jawa/set_draft", draft=1)', tools))
check("session.call shape", ("jawa/set_draft", "UNDECLARED_PARAM") in kinds('t.session.call("jawa/set_draft", draft=1)', tools))
check("literal params dict", ("jawa/set_draft", "UNDECLARED_PARAM") in kinds('s.call("jawa/set_draft", {"draft": 1})', tools))
check("params= dict", ("jawa/set_draft", "UNDECLARED_PARAM") in kinds('s.call("jawa/set_draft", params={"draft": 1})', tools))

# --- required, on a hand-built snapshot
mini = {"a/t": {"parameters": ["x", "y"], "required": ["x"]}}
check("missing required", kinds('s.call("a/t", y=1)', mini) == [("a/t", "MISSING_REQUIRED")])
check("required present", kinds('s.call("a/t", x=1)', mini) == [])
check("transport check= not a param", kinds('s.call("a/t", x=1, check=False)', mini) == [])

# --- never silently pass what cannot be seen
check("**kwargs UNCHECKED", kinds('s.call("a/t", **kw)', mini) == [("a/t", "UNCHECKED")])
check("**kwargs does not also claim missing required", ("a/t", "MISSING_REQUIRED") not in kinds('s.call("a/t", **kw)', mini))
check("literal-key splat checked: declared passes", kinds('s.call("a/t", **{"x": 1})', mini) == [])
check("literal-key splat checked: undeclared flagged",
      kinds('s.call("a/t", x=1, **{"def": 1})', mini) == [("a/t", "UNDECLARED_PARAM")])
check("non-literal-key splat still UNCHECKED", kinds('s.call("a/t", **{k: 1})', mini) == [("a/t", "UNCHECKED")])
check("non-literal tool UNCHECKED", kinds('s.call(tool, x=1)', mini) == [("?", "UNCHECKED")])
check("non-literal params dict UNCHECKED", kinds('s.call("a/t", d)', mini) == [("a/t", "UNCHECKED")])
check("unparseable file UNCHECKED", kinds('def (:', mini)[0][1] == "UNCHECKED")

# --- C# parser vs a known signature
cs = T.parse_csharp('''
    [Tool("jawa/demo", Description = "a (b) c, d")]
    public static object Demo(
        IRimBridgeContext ctx,
        [ToolParameter(Description = "has, comma (and paren)")] string need,
        [ToolParameter(DefaultValue = 5)] int n = 5,
        bool? flag = null)
    { return null; }''')
check("C# parser params", cs["jawa/demo"]["parameters"] == ["flag", "n", "need"], str(cs))
check("C# parser required", cs["jawa/demo"]["required"] == ["need"], str(cs))

# --- banned routes (FOCUS_HEAL_TAME_HANDS_OFF_HIS_WINDOWS): retired / discovery tools, direct or smuggled
for t in ("jawa/hot_reload_defs", "rimworld/search_debug_actions", "rimworld/list_debug_action_roots"):
    check("banned %s refused" % t, (t, "BANNED_ROUTE") in kinds('s.call("%s")' % t, tools), str(kinds('s.call("%s")' % t, tools)))
k = kinds('s.call("rimbridge/run_lua", code="return ctx.Tools.call(\'jawa/hot_reload_defs\')")', tools)
check("hot reload smuggled through run_lua refused", ("rimbridge/run_lua", "BANNED_ROUTE") in k, str(k))
k = kinds('s.call("jawa/static_call", type="Verse.PlayDataLoader", method="LoadAllPlayData")', tools)
check("def reload through static_call refused", ("jawa/static_call", "BANNED_ROUTE") in k, str(k))
k = kinds('s.call("jawa/static_call", type="Verse.Log", method="ResetMessageCount")', tools)
check("harmless static_call not banned", ("jawa/static_call", "BANNED_ROUTE") not in k, str(k))
check("safe list_debug_action_children not banned",
      ("rimworld/list_debug_action_children", "BANNED_ROUTE") not in kinds('s.call("rimworld/list_debug_action_children", path="x")', tools))

# --- the snapshot is not stale against the companion source (26 tools were missing on 2026-10-10)
import glob as _glob
_cs = {}
for _f in _glob.glob(os.path.join(os.path.dirname(os.path.dirname(HERE)), "bridgetools", "JawaBench.BridgeTools", "*.cs")):
    with open(_f, encoding="utf-8", errors="replace") as _fh:
        _cs.update(T.parse_csharp(_fh.read()))
_missing = sorted(set(_cs) - set(tools))
check("C# probe finds tools at all (sanity: >=300)", len(_cs) >= 300, "(%d)" % len(_cs))
check("every companion [Tool] in source is in the snapshot", not _missing, "%d missing: %s" % (len(_missing), _missing[:8]))

print("FAILED: %s" % FAILS if FAILS else "ALL PASS")
sys.exit(1 if FAILS else 0)
