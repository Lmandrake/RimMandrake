#!/usr/bin/env python3
"""selftest_nightly_rerun.py -- NIGHTLY_REDS_FIX_RERUN_BEFORE_PAYING: before ops_watch files a nightly-red group, its
tests rerun once at origin/main with no LLM; a group green on that rerun files nothing and is counted as a flake.
Covers the gate in red_groups (green / red / unmeasured / budget spent / once per night / held groups untouched), its
wiring through nightly_news, and rerun_at_main against a real throwaway git origin (green, red, behind origin/main,
missing test, a green that did not run its check, a rerun past its budget)."""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
TMP = Path(tempfile.mkdtemp(prefix="nightly_rerun_"))
os.environ["RM_OPS_WATCH_DIR"] = str(TMP / "ops")
(TMP / "ops").mkdir()
import ops_watch as OW  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  -- %s" % (detail,)))
    if not cond:
        FAILS.append(name)


def grp(key, *tests):
    return {"key": "testing.red_" + key, "tests": list(tests), "said": "%d red: %s" % (len(tests), key), "due": "2026-11-07T11:00:00Z"}


class Fake:
    def __init__(self, verdicts):
        self.verdicts, self.calls = verdicts, []

    def __call__(self, tests, timeout):
        self.calls.append((tuple(tests), timeout))
        return self.verdicts[tests[0]], "fake", "abc1234567890"


NIGHT = "2026-11-04T11:00:00Z"
COP = {"detail_read": True, "groups": [grp("green", "src/x/selftest_flaky.py"), grp("red", "src/x/selftest_broken.py"),
                                       grp("unm", "src/x/selftest_cannot.py")]}
V = {"src/x/selftest_flaky.py": "green", "src/x/selftest_broken.py": "red", "src/x/selftest_cannot.py": "unmeasured"}

# ---- the gate in red_groups
f = Fake(V)
out = OW.red_groups(COP, NIGHT, state={}, rerun=f)
check("a group green on the rerun files nothing", "testing.red_green" not in out, sorted(out))
check("a group red on the rerun files as before", out.get("testing.red_red", {}).get("v") == 1, out.get("testing.red_red"))
check("a group the rerun could not measure files as before", out.get("testing.red_unm", {}).get("v") == 1, out.get("testing.red_unm"))
g = out.get("testing.nightly_reds_rerun_green", {})
check("the flake is counted, named and its sha said", g.get("m") == "MEASURED" and g.get("v") == 1
      and "selftest_flaky.py" in (g.get("x", {}).get("said") or "") and "abc1234567" in g["x"]["said"], g)
check("each group reran once, with the budget as its timeout", len(f.calls) == 3
      and all(0 < t <= OW.rerun_budget_s() for _, t in f.calls), f.calls)
check("the verdicts are kept for the night", OW.read_json(OW.rerun_path()).get("night") == NIGHT
      and len(OW.read_json(OW.rerun_path())["groups"]) == 3, OW.read_json(OW.rerun_path()))

f2 = Fake(V)
out2 = OW.red_groups(COP, NIGHT, state={}, rerun=f2)
check("the next pass of the same night reruns nothing and decides the same", not f2.calls
      and "testing.red_green" not in out2 and out2.get("testing.red_red", {}).get("v") == 1, (f2.calls, sorted(out2)))

f3 = Fake(V)
OW.red_groups(COP, "2026-11-05T11:00:00Z", state={}, rerun=f3)
check("a new night reruns its groups again", len(f3.calls) == 3, f3.calls)

f4 = Fake(V)
held = {"NIGHTLY_RED:testing.red_red": {}}
out4 = OW.red_groups({"detail_read": True, "groups": [grp("red", "src/x/selftest_broken.py")]}, "2026-11-06T11:00:00Z",
                     state=held, rerun=f4)
check("a group already filed (held) is never rerun", not f4.calls and out4.get("testing.red_red", {}).get("v") == 1, (f4.calls, out4))

f5 = Fake(V)
out5 = OW.red_groups(COP, "2026-11-07T11:00:00Z", state={}, rerun=None)
check("rerun=None turns the gate off: every group files, no flake reading", not f5.calls
      and all(k in out5 for k in ("testing.red_green", "testing.red_red", "testing.red_unm"))
      and "testing.nightly_reds_rerun_green" not in out5, sorted(out5))

# budget spent: a group the budget cannot reach waits (absent, not filed) and comes next pass
OW.rerun_path().unlink()
ticks = iter([0.0, 0.0, 200.0, 200.0, 200.0, 200.0])
gate = OW.RerunGate("2026-11-08T11:00:00Z", Fake(V), 100, clock=lambda: next(ticks))
check("within budget the group reruns", gate.verdict(COP["groups"][1]) == "red")
check("past the budget the group waits for the next pass", gate.verdict(COP["groups"][0]) == "later")
_saved = OW.rerun_budget_s
OW.rerun_budget_s = lambda: 0
f6 = Fake(V)
out6 = OW.red_groups(COP, "2026-11-09T11:00:00Z", state={}, rerun=f6)
check("no budget left: nothing reruns, nothing files, every group comes next pass", not f6.calls
      and not [k for k in out6 if k.startswith("testing.red_")], sorted(out6))
OW.rerun_budget_s = _saved

def boom(tests, timeout):
    raise RuntimeError("rerunner died")
out7 = OW.red_groups({"detail_read": True, "groups": [grp("dead", "src/x/selftest_flaky.py")]}, "2026-11-10T11:00:00Z",
                     state={}, rerun=boom)
check("a rerunner that dies files the group as before", out7.get("testing.red_dead", {}).get("v") == 1, out7)

# ---- wiring: the pass's own path (nightly_news -> red_groups) uses RERUN_REDS
import known_reds as K  # noqa: E402
_saved_measure, _saved_rr = K.measure, OW.RERUN_REDS
K.measure = lambda open_ids, now, with_cop=False: {"night": "2026-11-11T11:00:00Z", "news": [], "listed": [], "cured": [],
                                                    "reds": ["src/x/selftest_flaky.py"], "unlisted": ["src/x/selftest_flaky.py"],
                                                    "expired": [], "cop": {"detail_read": True, "overdue": [], "overdue_said": "",
                                                                           "groups": [grp("wire", "src/x/selftest_flaky.py")]}}
fw = Fake(V)
OW.RERUN_REDS = fw
try:
    pts = OW.nightly_news(0, {"open_ids": set()})
finally:
    K.measure, OW.RERUN_REDS = _saved_measure, _saved_rr
check("WIRE: the pass reruns a new group before filing it, and a green one files nothing", fw.calls
      and "testing.red_wire" not in pts and pts.get("testing.nightly_reds_rerun_green", {}).get("v") == 1, (fw.calls, sorted(pts)))
check("WIRE: the default rerunner is rerun_at_main", OW.RERUN_REDS is OW.rerun_at_main)

# ---- rerun_at_main against a real throwaway origin
STUB = '''import sys
names = [a for a in sys.argv[1:] if a != "--only"]
bad = [n for n in names if "red" in n]
if any("slow" in n for n in names):
    import time; time.sleep(30)
if any("blind" in n for n in names):
    print("UNMEASURED (1/1) -- did NOT run their check")
print("RESULT: " + ("RED" if bad else "GREEN") + " (green = FAIL 0 and CRASH 0)")
sys.exit(1 if bad else 0)
'''


def sh(*a, cwd=None):
    subprocess.run(a, cwd=cwd, check=True, capture_output=True)


org, wc = TMP / "origin.git", TMP / "wc"
sh("git", "init", "-q", "--bare", "-b", "main", str(org))
sh("git", "clone", "-q", str(org), str(wc))
(wc / "src/RimMandrake/Utils").mkdir(parents=True)
(wc / "src/RimMandrake/Utils/run_selftests.py").write_text(STUB)
for n in ("selftest_ok.py", "selftest_red.py", "selftest_blind.py", "selftest_slow.py"):
    (wc / "src/RimMandrake/Utils" / n).write_text("")
for a in (("add", "."), ("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "x"), ("push", "-q", "origin", "main")):
    sh("git", *a, cwd=wc)
U_ = "src/RimMandrake/Utils/"
v, said, sha = OW.rerun_at_main([U_ + "selftest_ok.py"], 20, root=wc)
check("rerun_at_main: green at origin/main is green, with the sha", v == "green" and sha and len(sha) == 40, (v, said, sha))
v, said, _ = OW.rerun_at_main([U_ + "selftest_ok.py", U_ + "selftest_red.py"], 20, root=wc)
check("rerun_at_main: a failing test is red", v == "red", (v, said))
v, said, _ = OW.rerun_at_main([U_ + "selftest_blind.py"], 20, root=wc)
check("rerun_at_main: a green whose test did not run its check is unmeasured, not green", v == "unmeasured", (v, said))
v, said, _ = OW.rerun_at_main([U_ + "selftest_slow.py"], 2, root=wc)
check("rerun_at_main: a rerun past its budget is unmeasured", v == "unmeasured" and "budget" in said, (v, said))
v, said, _ = OW.rerun_at_main([U_ + "selftest_gone.py"], 20, root=wc)
check("rerun_at_main: a test this checkout lacks is unmeasured", v == "unmeasured", (v, said))
other = TMP / "other"
sh("git", "clone", "-q", str(org), str(other))
(other / "f.txt").write_text("x")
for a in (("add", "f.txt"), ("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "y"), ("push", "-q", "origin", "main")):
    sh("git", *a, cwd=other)
v, said, sha = OW.rerun_at_main([U_ + "selftest_ok.py"], 20, root=wc)
_main = subprocess.run(["git", "-C", str(other), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
check("rerun_at_main: a checkout behind origin/main is fast-forwarded to it, then reruns there",
      v == "green" and sha == _main, (v, said, sha, _main))
(wc / "local.txt").write_text("x")
for a in (("add", "local.txt"), ("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "z")):
    sh("git", *a, cwd=wc)
(other / "f2.txt").write_text("x")
for a in (("add", "f2.txt"), ("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "w"), ("push", "-q", "origin", "main")):
    sh("git", *a, cwd=other)
v, said, _ = OW.rerun_at_main([U_ + "selftest_ok.py"], 20, root=wc)
check("rerun_at_main: a checkout that cannot reach origin/main (diverged) does not rerun: unmeasured, files as before",
      v == "unmeasured" and "git" in said, (v, said))

print("RESULT: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
sys.exit(1 if FAILS else 0)
