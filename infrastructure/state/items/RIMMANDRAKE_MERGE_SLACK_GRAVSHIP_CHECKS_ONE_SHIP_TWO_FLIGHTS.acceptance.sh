#!/bin/bash
# Acceptance test (offline part) for RIMMANDRAKE_MERGE_SLACK_GRAVSHIP_CHECKS_ONE_SHIP_TWO_FLIGHTS. Exit 0 = pass, 1 = fail, 2 = could not look.
# Usage: bash <this file> [prove_gravship.py] [limit_ticks]   |   bash <this file> --selftest
# Part 1 (here): the boarding order of the ship driver must not wait out a fixed long time. Today: jawa/order_pawn waitTicks=5000
# (83.4 s at normal speed, measured in all six flights on record). Limit 600 ticks (10 s) = OUR OWN rule: colonists reach the pad in
# about 5 s (guess); the boarding must END ON ARRIVAL (s.run until the colonists stand on the pad), with 600 as the ceiling.
# Part 2 (UNRUN, live): one ship built, saved boarded, flown with keepWiresOnGravship on, save reloaded, flown with it off:
#   telemetry shows 2 flights and 1 ship build per visit run. Command to be built: gravship_scene.py both --out RESULT.json,
#   then count rows GS1_..._on / GS1_..._off in RESULT.json == 2 and ship builds in the bridge log == 1.
cd "$(dirname "$0")/../../.." || exit 2
exec python3 -I - "$@" <<'PY'
import ast, sys, os, tempfile
def judge(path, limit):
    try: t = ast.parse(open(path, encoding="utf-8").read())
    except Exception as e: print("could not look: %s: %s" % (path, e)); return 2
    waits = []
    for n in ast.walk(t):
        if isinstance(n, ast.Call) and n.args and isinstance(n.args[0], ast.Constant) and n.args[0].value == "jawa/order_pawn":
            kw = {k.arg: k.value for k in n.keywords}
            w = kw.get("waitTicks")
            waits.append(w.value if isinstance(w, ast.Constant) and isinstance(w.value, int) else 10**9)
    if not waits: print("could not look: no jawa/order_pawn call in", path); return 2
    worst = max(waits)
    print("order_pawn calls read %d; worst waitTicks %s (limit %d, our own rule); file %s" % (len(waits), worst if worst < 10**9 else "not a number", limit, path))
    return 0 if worst <= limit else 1
if sys.argv[1:2] == ["--selftest"]:
    d = tempfile.mkdtemp(); ok = True
    def case(name, src, want):
        global ok
        p = os.path.join(d, name + ".py"); open(p, "w").write(src)
        got = judge(p, 600); g = got == want; ok &= g
        print("  case %-14s want rc %d got rc %d %s" % (name, want, got, "ok" if g else "WRONG"))
    case("planted_5000", 'call("jawa/order_pawn", pawnId="colonists", waitTicks=5000)\n', 1)
    case("short_green", 'call("jawa/order_pawn", pawnId="colonists", waitTicks=300)\n', 0)
    case("no_order", "x = 1\n", 2)
    case("unreadable", "def (:\n", 2)
    print("SELFTEST OK" if ok else "SELFTEST BROKEN"); sys.exit(0 if ok else 1)
a = sys.argv[1:]
sys.exit(judge(a[0] if a else "src/RimMandrake/bridgetools/prove_gravship.py", int(a[1]) if len(a) > 1 else 600))
PY
