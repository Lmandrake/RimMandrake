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
DRIVERS = ("thirst_live.py", "thirst_fake.py", "river_site.py", "pond_pump.py", "raid_trench_proof.py")
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
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "call" and n.args
                and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str) and n.args[0].value.startswith("jawa/")):
            tool = n.args[0].value
            if tool not in sigs:
                out.append("%s:%d unknown tool %s" % (name, n.lineno, tool))
                continue
            bad = [k.arg for k in n.keywords if k.arg and k.arg not in sigs[tool]]
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
for d in DRIVERS:
    probs = check_source(open(os.path.join(HERE, d), encoding="utf-8").read(), sigs, d)
    check("%s: every jawa/ call names declared parameters" % d, not probs, probs)
print("selftest_bridge_args: %s" % ("FAIL" if FAILS else "ok"))
sys.exit(1 if FAILS else 0)
