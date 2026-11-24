#!/bin/bash
# Acceptance test for RIMMANDRAKE_HOLD_FLOWWORKS_MOD_CHANGES_UNTIL_VISIT_READING_POINT. Exit 0 = pass, 1 = fail, 2 = could not look.
# Usage: bash <this file> [rows.jsonl] [limit]    (default: the newest FlowWorks visit's rows.jsonl, limit 0)
#        bash <this file> --selftest              (plants faults; must print SELFTEST OK)
# A "superseded PASS row" = a PASS row whose mod_sha is not the sha of that check's LAST row of the visit (the check ran again
# on a later build). The limit 0 is OUR OWN rule (hold the mod still), not the owner's bar. Measured source: visit 9 = 26 rows, 2,541 s.
cd "$(dirname "$0")/../../.." || exit 2
exec python3 -I - "$@" <<'PY'
import json, sys, os, glob, re, tempfile, subprocess
def judge(path, limit):
    rows = []
    try:
        for l in open(path, encoding="utf-8"):
            l = l.strip()
            if l:
                rows.append(json.loads(l))
        rows = [r for r in rows if "test" in r and "mod_sha" in r]
    except Exception as e:
        print("could not look: %s: %s" % (path, e)); return 2
    if not rows:
        print("could not look: no readable rows in", path); return 2
    last = {}
    for r in rows: last[r["test"]] = r["mod_sha"]
    sup = [r for r in rows if r.get("verdict") == "PASS" and r["mod_sha"] != last[r["test"]]]
    secs = sum(float(r.get("wall_s") or 0) for r in sup)
    print("rows read %d; superseded PASS rows %d (limit %d, our own rule); wasted seconds %.0f; file %s" % (len(rows), len(sup), limit, secs, path))
    return 0 if len(sup) <= limit else 1
def row(t, v, sha, s=10): return json.dumps({"test": t, "verdict": v, "mod_sha": sha, "wall_s": s})
if sys.argv[1:2] == ["--selftest"]:
    d = tempfile.mkdtemp(); ok = True
    def case(name, lines, want):
        global ok
        p = os.path.join(d, name); open(p, "w").write("\n".join(lines) + ("\n" if lines else ""))
        got = judge(p, 0); good = got == want; ok &= good
        print("  case %-22s want rc %d got rc %d %s" % (name, want, got, "ok" if good else "WRONG"))
    case("planted_superseded", [row("a", "PASS", "s1"), row("b", "PASS", "s1"), row("a", "PASS", "s2"), row("b", "PASS", "s2")], 1)
    case("one_build_stays_green", [row("a", "PASS", "s1"), row("b", "FAIL", "s1")], 0)
    case("fix_after_fail_not_waste", [row("a", "FAIL", "s1"), row("a", "PASS", "s2")], 0)
    case("empty_visit", [], 2)
    case("garbage", ["{not json"], 2)
    print("SELFTEST OK" if ok else "SELFTEST BROKEN"); sys.exit(0 if ok else 1)
a = sys.argv[1:]
if a: path, limit = a[0], int(a[1]) if len(a) > 1 else 0
else:
    vs = sorted(glob.glob("design/concepts/FlowWorks/version/in_game/visit_*/rows.jsonl"), key=lambda p: int(re.search(r"visit_(\d+)", p).group(1)))
    if not vs: print("could not look: no FlowWorks visit rows"); sys.exit(2)
    path, limit = vs[-1], 0
sys.exit(judge(path, limit))
PY
