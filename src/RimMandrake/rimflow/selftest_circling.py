#!/usr/bin/env python3
"""selftest_circling.py -- the tool-call classifier pulse/time_ledger reads (circling.classify). The tree delta, the stop
gate and circling.watch went with the retired tick (RIMMANDRAKE_RETIRE_CIRCLING_WATCH_ONLY_THE_DEAD_TICK_CALLED); their
cases are in git with them."""
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import circling as C  # noqa: E402

FAILS = []
HOME = tempfile.mkdtemp(prefix="circ-home-")
os.environ["HOME"] = HOME


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


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
    for t in (t_classify,):
        t()
    shutil.rmtree(HOME, ignore_errors=True)
    print("%d failed" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
