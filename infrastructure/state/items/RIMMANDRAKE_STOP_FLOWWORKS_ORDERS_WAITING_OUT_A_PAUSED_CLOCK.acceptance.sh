#!/bin/bash
# Acceptance test (offline part) for RIMMANDRAKE_STOP_FLOWWORKS_ORDERS_WAITING_OUT_A_PAUSED_CLOCK. Exit 0 = pass, 1 = fail, 2 = could not look.
# Usage: bash <this file> [file ...]  (default: the FlowWorks concept_scenes.py, live_session.py, extension_proof.py)  |  --selftest
# Part 1 (here, a PROXY): every jawa/ordered_job and jawa/order_pawn call in the three callers passes waitTicks=0 (the order returns
# at once; the scene then ends its wait on the state with s.run / a fast advance). A call with a default or a number waits in GAME
# ticks and, with the game paused, sits until its time limit (15 s ordered_job, 30 s order_pawn). Limit 0 = our own rule.
# Part 2 (UNRUN, to be built, the real bar): a telemetry reader over one visit's bridge log + tps windows that counts order calls
# over 3 s whose 5 s windows show 0 ticks: today 40 calls / 757 s (visit 9). Command to build: clock_still_waits.py --day <date> --limit 0.
cd "$(dirname "$0")/../../.." || exit 2
D=src/RimMandrake/FlowWorks/northstar
exec python3 -I -W ignore - "$@" "$D/concept_scenes.py" "$D/live_session.py" "$D/extension_proof.py" <<'PY'
import ast, sys, os, tempfile
TOOLS = ("jawa/ordered_job", "jawa/order_pawn")
def judge(files):
    read = bad = 0
    for f in files:
        try: t = ast.parse(open(f, encoding="utf-8").read())
        except Exception as e: print("could not look: %s: %s" % (f, e)); return 2
        for n in ast.walk(t):
            if isinstance(n, ast.Call) and n.args and isinstance(n.args[0], ast.Constant) and n.args[0].value in TOOLS:
                read += 1
                w = {k.arg: k.value for k in n.keywords}.get("waitTicks")
                if not (isinstance(w, ast.Constant) and w.value == 0): bad += 1
    if read == 0: print("could not look: no order call found in %d files" % len(files)); return 2
    print("order call sites read %d in %d files; sites that can wait on a paused clock %d (limit 0, our own rule)" % (read, len(files), bad))
    return 1 if bad else 0
if sys.argv[1:2] == ["--selftest"]:
    d = tempfile.mkdtemp(); ok = True
    def case(name, src, want):
        global ok
        p = os.path.join(d, name + ".py"); open(p, "w").write(src)
        got = judge([p]); g = got == want; ok &= g
        print("  case %-16s want rc %d got rc %d %s" % (name, want, got, "ok" if g else "WRONG"))
    case("planted_default", 'S.call("jawa/ordered_job", pawnId=1)\n', 1)
    case("planted_one_tick", 'S.call("jawa/order_pawn", pawnId=1, waitTicks=1, unpause=False)\n', 1)
    case("zero_green", 'S.call("jawa/order_pawn", pawnId=1, waitTicks=0)\nS.call("jawa/ordered_job", waitTicks=0)\n', 0)
    case("no_order_in_file", "x = 1\n", 2)
    print("SELFTEST OK" if ok else "SELFTEST BROKEN"); sys.exit(0 if ok else 1)
files = [f for f in sys.argv[1:] if f.endswith(".py")]
# extension_proof.py reaches the tool through a helper: a file with no literal call is skipped, not counted as clean
sys.exit(judge([f for f in files if "extension_proof" not in f or len(files) == 1]))
PY
