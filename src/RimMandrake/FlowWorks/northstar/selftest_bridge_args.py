"""Offline selftest: every jawa/ bridge call in the northstar drivers names only parameters the C# [Tool] method declares.

The bridge's binder DROPS an unknown argument silently (JawaBenchArgGuard.cs): a wrong name (set_draft `draft=` for `drafted=`,
stop_job `action=` for `mode=`) runs the tool on its defaults and answers success. This reads the [Tool] signatures out of
src/RimMandrake/bridgetools/JawaBench.BridgeTools/*.cs and every `X.call("jawa/<tool>", kw=...)` in the listed drivers.
Can fail: CASES below feed it a wrong name and it must report it. A tool unknown to the C# is reported, not skipped.
"""
import ast
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
TOOLS = os.path.join(ROOT, "src", "RimMandrake", "bridgetools", "JawaBench.BridgeTools")
# every non-selftest .py here (and live_probes/) that names a jawa/ tool: listed by glob so a new driver is covered at once.
# (fakegame.py is the mock, not a driver: it has no bridge calls of its own to check.) EITHER quote: the glob once matched
# '"jawa/' only, so concept_scenes.py and three other single-quoted drivers were never checked
# (RIMMANDRAKE_FINISH_FLOWWORKS_WALK_SCENE_HALF_THE_BAR_UNASKED).
JAWA = re.compile(r"[\"']jawa/")
DRIVERS = tuple(sorted(
    os.path.relpath(f, HERE) for f in glob.glob(os.path.join(HERE, "*.py")) + glob.glob(os.path.join(HERE, "live_probes", "*.py"))
    if not os.path.basename(f).startswith("selftest_") and JAWA.search(open(f, encoding="utf-8").read())))
# a driver's own call() wrapper consumes these before the bridge sees them (validation_core's _answer, concept_scenes' allow_refusal)
LOCAL_KW = ("_answer", "allow_refusal")
# bridge tools that live in the core RimBridge server, not in JawaBench.BridgeTools: not checkable here
EXTERNAL_OK = ()


def signatures():
    sigs = {}
    for f in glob.glob(os.path.join(TOOLS, "*.cs")):
        txt = open(f, encoding="utf-8", errors="ignore").read()
        for m in re.finditer(r'\[Tool\(\s*"([^"]+)"(.*?)public static (?:async )?(?:Task<\w+>|\w+) \w+\((.*?)\)\s*\{', txt, re.S):
            sig = m.group(3).replace("\n", " ") + ","
            sigs[m.group(1)] = re.findall(r'\b[A-Za-z\[\]<>?]+\s+(\w+)\s*(?:=|,)', sig)
    return sigs


def check_source(src, sigs, name="<src>"):
    """-> [problem strings] for the jawa/ calls in `src`."""
    out = []
    for n in ast.walk(ast.parse(src)):
        fn = n.func.attr if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) else (
            n.func.id if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) else "")
        if (isinstance(n, ast.Call) and fn.lstrip("_") in ("call", "bridge_call", "tool") and n.args
                and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str) and n.args[0].value.startswith("jawa/")):
            tool = n.args[0].value
            if tool not in sigs:
                out.append("%s:%d unknown tool %s" % (name, n.lineno, tool))
                continue
            bad = [k.arg for k in n.keywords if k.arg and k.arg not in LOCAL_KW and k.arg not in sigs[tool]]
            if bad:
                out.append("%s:%d %s has no parameter %s (declared: %s)" % (name, n.lineno, tool, bad, sigs[tool]))
    return out


FAILS = []


def check(label, ok, why=""):
    print("%s  %s %s" % ("ok  " if ok else "FAIL", label, "" if ok else why))
    if not ok:
        FAILS.append(label)


sigs = signatures()
check("the C# signatures were read (set_draft takes drafted, pawn_health takes confirmDestructive)",
      "drafted" in sigs.get("jawa/set_draft", []) and "confirmDestructive" in sigs.get("jawa/pawn_health", []), sorted(sigs)[:5])
check("can-fail: a wrong name is caught", check_source('B.call("jawa/set_draft", pawnId=1, draft=True)', sigs) != [])
check("can-fail: an unknown tool is caught", check_source('B.call("jawa/no_such_tool", x=1)', sigs) != [])
check("control: the right names pass", check_source('B.call("jawa/set_draft", pawnId=1, drafted=True)', sigs) == [])
check("the driver glob found the drivers (not an empty loop)", len(DRIVERS) >= 15, DRIVERS)
check("a single-quoted driver is covered (concept_scenes.py, the Stage 3 scenes)", "concept_scenes.py" in DRIVERS, DRIVERS)
check("can-fail: a single-quoted wrong name is caught", check_source("S.call('jawa/set_draft', pawnId=1, draft=True)", sigs) != [])


def returned_fields(tool):
    """The field names of the anonymous object a [Tool] returns on success (`new { success = true, a = .., b = .. }`)."""
    for f in glob.glob(os.path.join(TOOLS, "*.cs")):
        txt = open(f, encoding="utf-8", errors="ignore").read()
        m = re.search(r'\[Tool\(\s*"%s"' % re.escape(tool), txt)
        if m:
            i = m.start()
            k = txt.find("success = true", i)
            j = txt.rfind("new", i, k)
            if k < 0 or j < 0:
                return set()
            body = txt[j:txt.find("};", k)]
            return set(re.findall(r"^\s*(\w+)\s*=", body, re.M))
    return set()


# the walk scene's digest reads these engine_state keys: each must be a field the tool returns, or the digest compares
# None with None and passes (Stage 6 visit 1: the draft read 'stock' and 'cells')
_walk_src = open(os.path.join(HERE, "concept_scenes.py"), encoding="utf-8").read().split("def _walk(S):", 1)[1].split("\ndef ", 1)[0]
_keys = re.search(r"keys = \(([^)]*)\)", _walk_src)
_got = returned_fields("jawa/flowworks_engine_state")
check("engine_state's returned fields were read (not an empty set)", {"bodyCount", "nextPulseTick"} <= _got, sorted(_got))
_want = set(re.findall(r"'(\w+)'", _keys.group(1))) if _keys else set()
check("the walk digest reads only fields engine_state returns", _want and _want <= _got, sorted(_want - _got) or _want)
check("can-fail: the draft's 'stock' key is not a returned field", "stock" not in _got and "cells" not in _got)
for d in DRIVERS:
    probs = check_source(open(os.path.join(HERE, d), encoding="utf-8").read(), sigs, d)
    check("%s: every jawa/ call names declared parameters" % d, not probs, probs)
print("selftest_bridge_args: %s" % ("FAIL" if FAILS else "ok"))
sys.exit(1 if FAILS else 0)
