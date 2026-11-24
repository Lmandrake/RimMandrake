#!/bin/bash
# Acceptance test (offline proxy) for RIMMANDRAKE_REPAIR_SLACK_GRAVSHIP_SCENE_PASSES_ON_ONE_LAMP. Exit 0 = pass, 1 = fail, 2 = could not look.
# Usage: bash <this file> [file ...]     (default: gravship_scene.py + bridgetools/prove_gravship.py)   |   bash <this file> --selftest
# The scene text (design/concepts/GimmeSomeSlack/scenes.json, sc_gravship) asks for four things: wall-bracket anchors, a battery,
# two consumers, and a planted control (the pre-launch cord set fed to the true-to-grid read against the landed map).
# This proxy reads CODE (string literals and names, not comments or docstrings) for each. It cannot prove the LIVE flight: that
# part is UNRUN (a result JSON from gravship_scene.py must carry a control row that FAILS by name when planted).
cd "$(dirname "$0")/../../.." || exit 2
DEF="src/RimMandrake/GimmeSomeSlack/northstar/gravship_scene.py src/RimMandrake/bridgetools/prove_gravship.py"
exec python3 -I - "$@" "$DEF" <<'PY'
import ast, re, sys, os, tempfile
NEED = [("wall-bracket anchors", r"wallbracket"), ("a battery", r"battery"), ("two consumers", r"consumer"), ("the planted control", r"control")]
def words(src):
    t = ast.parse(src); out = []
    docs = set()
    for n in ast.walk(t):
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef)) and n.body and isinstance(n.body[0], ast.Expr) and isinstance(getattr(n.body[0], "value", None), ast.Constant):
            docs.add(id(n.body[0].value))
    for n in ast.walk(t):
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in docs: out.append(n.value.lower())
        elif isinstance(n, ast.Name): out.append(n.id.lower())
        elif isinstance(n, ast.Attribute): out.append(n.attr.lower())
        elif isinstance(n, ast.keyword) and n.arg: out.append(n.arg.lower())
    return " ".join(out)
def judge(files):
    blob = ""
    for f in files:
        try: blob += words(open(f, encoding="utf-8").read()) + " "
        except Exception as e: print("could not look: %s: %s" % (f, e)); return 2
    miss = [n for n, rx in NEED if not re.search(rx, blob)]
    print("staging asks for %d things; the code names %d; missing: %s (files read %d)" % (len(NEED), len(NEED) - len(miss), miss or "none", len(files)))
    return 1 if miss else 0
if sys.argv[1:2] == ["--selftest"]:
    d = tempfile.mkdtemp(); ok = True
    def case(name, src, want):
        global ok
        p = os.path.join(d, name + ".py"); open(p, "w").write(src)
        got = judge([p]); g = got == want; ok &= g
        print("  case %-18s want rc %d got rc %d %s" % (name, want, got, "ok" if g else "WRONG"))
    case("docstring_only", '"""wall bracket battery consumer control"""\nx=1\n', 1)
    case("one_lamp", 'B.ap("place:StandingLamp:1,1")\n', 1)
    case("all_four", 'B.ap("place:RM_AerialWallBracket:1,1")\nB.ap("place:Battery:2,2")\nconsumers = 2\nrow = {"control": 1}\n', 0)
    case("unreadable", "def (:\n", 2)
    print("SELFTEST OK" if ok else "SELFTEST BROKEN"); sys.exit(0 if ok else 1)
a = [x for x in sys.argv[1:-1]]
files = a if a else sys.argv[-1].split()
sys.exit(judge(files))
PY
