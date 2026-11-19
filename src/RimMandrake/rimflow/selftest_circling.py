#!/usr/bin/env python3
"""RW2's pure parts: the tool-call classifier (pulse/time_ledger reads it), the tree delta and the stop gate. The
planted-worker cases that drove the retired tick (relentless.tick over selftest_relentless's FakeWorld) went with it;
circling.watch, which only that tick called, is filed for removal."""
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import circling as C  # noqa: E402
import run_store as R  # noqa: E402

BLOCK = R.rules(os.path.join(R.HERE, "run_rules.json"))["circling"]
FAILS = []
HOME = tempfile.mkdtemp(prefix="circ-home-")
os.environ["HOME"] = HOME


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)






































def t_delta():
    d = C.delta
    ok(d({"a": list("abc")}, {"a": list("abc")}) == {}, "delta: same marks, nothing moved")
    ok(d({"a": ["+1"]}, {"a": ["+2"]}) == {"a": {"+1": -1, "+2": 1}}, "delta: one line replaced")
    ok(d({"a": ["+1", "+1"]}, {"a": ["+1"]}) == {"a": {"+1": -1}}, "delta: twin lines are counted, not merged")
    ok(d({}, {"a": ["+%d" % n for n in range(C.DELTA_MAX + 1)]}) is None, "delta: past the cap, none kept")
    net = C._net
    move = lambda *m: {"raw": str(m), "delta": {"a": {x[1:]: 1 if x[0] == "^" else -1 for x in m}}}
    ok(net([{"raw": "0"}, {"raw": "1"}]) is None, "a move with no delta is unknown, no hit")
    ok(net([{"raw": "0"}, move("^+1"), move("v+1", "^+2"), move("v+2", "^+3")]) == 1, "one line tweaked three times nets 1")
    ok(net([{"raw": "0"}, move("^+1", "^-0"), move("v+1", "^+2")]) == 1, "a replaced line nets 1 against the base")
    ok(net([{"raw": "0"}] + [move("^+%d" % n) for n in range(6)]) == 6, "a fresh line a move nets a line a move")
    ok(BLOCK["churn_max_lines"] < BLOCK["churn_moves"], "shipped thresholds: a line per move can never read as churn")


















def verdict(d, c, **kw):
    v = dict({"fingerprint": C.fingerprint(c), "measured": 30, "fine": 20, "circling": 10, "wrongful": 0}, **kw)
    p = os.path.join(d, "v.json")
    with open(p, "w") as f:
        json.dump(v, f)
    return p


def t_gate():
    d = tempfile.mkdtemp(prefix="circ-g-")
    off = dict(BLOCK)
    ok(BLOCK["stop"] is False and not C.stop_gate(off)[0], "S4 shipped rules: stopping is off")
    ok(not os.path.exists(C.VERDICT), "S4 no replay verdict ships")
    on = dict(BLOCK, stop=True)
    ok(not C.stop_gate(on, os.path.join(d, "none.json"))[0], "S4 the flag alone stops nothing")
    ok(not C.stop_gate(on, verdict(d, on, wrongful=1))[0], "S4 a replay at the limit does not beat it")
    ok(not C.stop_gate(on, verdict(d, on, measured=19))[0], "S4 too few labelled runs")
    ok(not C.stop_gate(on, verdict(d, on, circling=0))[0], "S4 a replay with no circling run proves nothing")
    p = verdict(d, on)
    ok(C.stop_gate(on, p)[0], "S4 a replay under the limit opens the gate")
    ok(not C.stop_gate(dict(on, no_change_min=31), p)[0], "S4 a changed threshold voids the replay")
    ok(not C.stop_gate(off, p)[0], "S4 a good replay with stop off stays report-only")
    shutil.rmtree(d, ignore_errors=True)






def t_classify():
    k = lambda c: C.classify("Bash", {"command": c})[0]
    ok(k("python3 src/RimMandrake/Utils/run_selftests.py --only x") == "selftest", "classify selftest")
    ok(k("python3 src/RimMandrake/Utils/winbuild.py X > o.txt") == "build", "classify build")
    ok(k("grep -n x y.txt | head") == "reading", "classify reading")
    ok(k("sed -i s/a/b/ f.py") == "editing", "classify editing")
    ok(k("./game --why x up") == "live", "classify live")
    ok(k("timeout 300 python3 src/x/selftest_a.py > o.txt 2>&1; tail o.txt") == "selftest", "classify a test behind timeout")
    ok(k("set -o pipefail; cd /x; python3 -m pytest -q | tail -5") == "selftest", "classify pytest in a chain")
    ok(k("grep -n def src/x/selftest_a.py") == "reading", "a grep of a selftest file is reading")
    ok(k("cat > src/x/selftest_a.py <<'E'\nrun_selftests\nE") == "editing", "a heredoc writing a selftest is editing")
    ok(k("python3 - <<'E'\nprint('selftest_a.py')\nE") == "other", "a heredoc mentioning a selftest runs none")
    ok(k("python3 - <<'E'\nedit\nE\ntimeout 9 python3 a/selftest_b.py > o; tail o") == "selftest", "a test after a heredoc is a test")
    ok(k("python3 - <<'E'\nopen('a.py', 'w').write('x')\nE") == "editing", "a heredoc that writes is editing")
    ok(C.classify("Bash", {"command": "python3 - <<'E'\nprint(1)\nE"})[1], "a heredoc that only looks has a target")
    ok(C.classify("Bash", {"command": "sed -i s/a/b/ f.py"})[1] is None, "an edit is no look")
    ok(C.classify("mcp__x__y", {"q": 1})[1] and C.classify("WebSearch", {"query": "q"})[1], "web and MCP calls have targets")
    ok(k("python3 relentless.py learn --item I x") == "other", "a learn line is no finding")
    ok(C.classify("Bash", {"command": "python3 src/rimflow/relentless.py learn --item I x"})[1] is None, "a learn line has no target")
    ok(C.classify("Bash", {"command": "python3 tools/x.py"}) == ("other", "python3 tools/x.py"), "a script call has a target")
    ok(k("git -C /x log -3") == "reading", "git -C log is reading")




def main():
    for t in (t_classify, t_delta, t_gate):
        t()
    shutil.rmtree(HOME, ignore_errors=True)
    print("%d failed" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
