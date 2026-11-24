#!/bin/bash
# Acceptance test for RIMMANDRAKE_SHARE_FLOWWORKS_LIST_BETWEEN_TWO_LONE_CHECKS. Exit 0 = pass, 1 = fail, 2 = could not look.
# Usage: bash <this file> [rows.jsonl] [limit]   (default: newest FlowWorks visit, limit 2)  |  bash <this file> --selftest
# Counts the DISTINCT mod lists (each row's active_mods set) that a visit's rows ran on. Every extra list is a game restart
# (visit 9: 273 + 51 + 234 s for two single-check lists). Limit 2 = the 13-mod flowworks tier + ONE list that serves the other
# checks: our own rule. Measured: the evening_20261113 list (23 mods) holds every mod of both lone lists (superset, read from rows.jsonl).
cd "$(dirname "$0")/../../.." || exit 2
exec python3 -I - "$@" <<'PY'
import json, sys, glob, re, os, tempfile
def judge(path, limit):
    lists = {}
    try:
        for l in open(path, encoding="utf-8"):
            l = l.strip()
            if not l: continue
            r = json.loads(l)
            am = r.get("active_mods")
            if not isinstance(am, list) or not am:
                print("could not look: row %s has no active_mods" % r.get("test")); return 2
            lists.setdefault(frozenset(am), []).append(r.get("test"))
    except Exception as e:
        print("could not look: %s: %s" % (path, e)); return 2
    if not lists:
        print("could not look: no rows in", path); return 2
    print("mod lists in the visit: %d (limit %d, our own rule); rows per list %s; file %s" % (len(lists), limit, sorted(len(v) for v in lists.values()), path))
    return 0 if len(lists) <= limit else 1
def row(t, mods): return json.dumps({"test": t, "active_mods": mods})
if sys.argv[1:2] == ["--selftest"]:
    d = tempfile.mkdtemp(); ok = True
    def case(name, lines, want):
        global ok
        p = os.path.join(d, name); open(p, "w").write("\n".join(lines) + "\n")
        got = judge(p, 2); g = got == want; ok &= g
        print("  case %-20s want rc %d got rc %d %s" % (name, want, got, "ok" if g else "WRONG"))
    case("planted_three_lists", [row("a", ["x"]), row("b", ["x", "y"]), row("c", ["x", "y", "z"])], 1)
    case("two_lists_green", [row("a", ["x"]), row("b", ["x", "y"]), row("c", ["y", "x"])], 0)
    case("one_list_green", [row("a", ["x"])], 0)
    case("row_without_mods", [json.dumps({"test": "a"})], 2)
    case("empty_visit", [""], 2)
    print("SELFTEST OK" if ok else "SELFTEST BROKEN"); sys.exit(0 if ok else 1)
a = sys.argv[1:]
if a: path, limit = a[0], int(a[1]) if len(a) > 1 else 2
else:
    vs = sorted(glob.glob("design/concepts/FlowWorks/version/in_game/visit_*/rows.jsonl"), key=lambda p: int(re.search(r"visit_(\d+)", p).group(1)))
    if not vs: print("could not look: no FlowWorks visit rows"); sys.exit(2)
    path, limit = vs[-1], 2
sys.exit(judge(path, limit))
PY
