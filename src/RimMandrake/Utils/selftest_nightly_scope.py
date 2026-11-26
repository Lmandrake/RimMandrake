#!/usr/bin/env python3
"""selftest_nightly_scope.py: the acceptance test of RIMMANDRAKE_PAUSE_NIGHTLY_SWEEP_WRONG_PHASE_UNTIL_MOD_FINISHED.

The owner, by card 2026-11-15: "Nightly tests should check mods with finished versions, not mods in production. Code is
too fluid otherwise. Wrong phase." Cases, all on temp trees and fake systemctl (nothing live is read or stopped):
  1  no finished mod: empty set, the run says "nothing finished yet" and exits 0 without starting a sweep or a clone
  2  one mod with a passed version: exactly its tests (its folder + Utils/selftest_<mod>_*); a mod in production and the
     process machinery are not in the set; a version kept passed while the next is in production still counts
  3  run_selftests.py --nightly on such a tree runs exactly that mod's test; on a tree with none, 0/0 green
  4  the hold: recorded before the stop, covers its timers in timers_guard and deadman while it waits, refuses a bad
     hold, and `resume_due` starts them and drops the record once a mod has passed
  5  while it waits: no fixer (red_dispatch), no rerun, every nightly reading and held build-cop group 0 (ops_watch),
     no catch-up start
  6  the door: a change touching a pipeline file with a failing pipeline test is refused at publish; a change touching
     none runs nothing; the 13 publish tree checks still run
  7  the clean clone: made from origin, reset to origin/main each run, and the sweep runs inside it with ~/.local/bin
"""
import json
import re
import os
import subprocess
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "rimflow"))
TMP = tempfile.mkdtemp(prefix="nightly_scope_")
os.environ["RM_OPS_WATCH_DIR"] = os.path.join(TMP, "ops")
os.makedirs(os.environ["RM_OPS_WATCH_DIR"])
os.environ.pop("RM_NIGHTLY_HELD", None)

import nightly_scope as NS   # noqa: E402
import timers_guard as TG   # noqa: E402

FAILS = []


def check(name, ok, got=None):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok or got is None else "  -- %r" % (got,)))
    if not ok:
        FAILS.append(name)


def put(root, rel, text):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)


def stage(root, mod, st, kept=None):
    put(root, "design/concepts/%s/version/stage_record.json" % mod, json.dumps({"mod": mod, "stage": st}))
    if kept:
        put(root, "design/concepts/%s/version/stage_record_0.1.0.json" % mod, json.dumps({"mod": mod, "stage": kept}))


PASS_T = "print('PASS fixture')\n"


def tree(name):
    root = os.path.join(TMP, name)
    for m in ("Alpha", "Beta", "Gamma"):
        put(root, "src/RimMandrake/%s/selftest_%s.py" % (m, m.lower()), PASS_T)
        put(root, "src/RimMandrake/%s/Sub/selftest_%s_deep.py" % (m, m.lower()), PASS_T)
        put(root, "src/RimMandrake/Utils/selftest_%s_lint.py" % m.lower(), PASS_T)
    put(root, "src/RimMandrake/Utils/selftest_alphabet_soup.py", PASS_T)   # a prefix, not the mod's name word
    put(root, "src/RimMandrake/Utils/selftest_ops_machinery.py", PASS_T)
    put(root, "src/RimMandrake/rimflow/selftest_maturation_fixture.py", PASS_T)
    return root


# ---- 1. nothing finished ---------------------------------------------------------------------------------------------
A = tree("none")
stage(A, "Alpha", "offline_build")
stage(A, "Beta", "his_walk")
t = NS.tests_for(A)
check("1 no finished mod: the set is empty", t["finished"] == [] and t["tests"] == [], t)
calls = []
buf = types.SimpleNamespace(lines=[], write=lambda s: buf.lines.append(s), flush=lambda: None)
rc = NS.run(A, clone=os.path.join(TMP, "never_cloned"), origin="/nonexistent", runner=lambda *a, **k: calls.append(a),
            out=buf)
check("1 the run says 'nothing finished yet', exits 0, starts no sweep and makes no clone",
      rc == 0 and not calls and NS.NOTHING in "".join(buf.lines) and "RESULT: GREEN" in "".join(buf.lines)
      and not os.path.exists(os.path.join(TMP, "never_cloned")), (rc, calls, buf.lines))

# ---- 2. one finished mod ---------------------------------------------------------------------------------------------
B = tree("one")
stage(B, "Alpha", "offline_build")            # in production
stage(B, "Beta", "passed")                    # finished
t = NS.tests_for(B)
want = sorted(["src/RimMandrake/Beta/selftest_beta.py", "src/RimMandrake/Beta/Sub/selftest_beta_deep.py",
               "src/RimMandrake/Utils/selftest_beta_lint.py"])
check("2 one passed mod: exactly its tests", t["finished"] == ["Beta"] and t["tests"] == want, t)
check("2 a mod in production is excluded", not any("lpha" in x for x in t["tests"]), t["tests"])
check("2 process machinery is never in the set", not any("machinery" in x or "maturation" in x for x in t["tests"]))
stage(B, "Gamma", "designer", kept="passed")
check("2 a version kept passed while the next is in production stays finished",
      NS.finished_mods(B) == ["Beta", "Gamma"], NS.finished_mods(B))

# ---- 3. the runner ---------------------------------------------------------------------------------------------------
RUNNER = os.path.join(HERE, "run_selftests.py")


def sweep(root):
    env = dict(os.environ, RM_SELFTEST_REPO_ROOT=root, RM_SELFTEST_NESTED="1", RM_SELFTEST_SKIP_DISK_GUARD="1")
    r = subprocess.run([sys.executable, RUNNER, "--nightly", "--workers", "1"], capture_output=True, text=True,
                       env=env, timeout=600, stdin=subprocess.DEVNULL)
    return r.returncode, r.stdout + r.stderr


C = tree("runner")
stage(C, "Beta", "passed")
rc, o = sweep(C)
ran = sorted(ln.split()[-1] for ln in o.splitlines() if ln.startswith(("PASS ", "FAIL ", "CRASH ")) and ln.endswith(".py"))
check("3 run_selftests --nightly runs exactly the finished mod's tests, green",
      rc == 0 and len(ran) == 3 and all("beta" in x for x in ran), (rc, ran, o[-600:]))
rc, o = sweep(A)
check("3 run_selftests --nightly with nothing finished: 0/0, green, 'nothing finished yet'",
      rc == 0 and NS.NOTHING in o, (rc, o[-400:]))

# ---- 4. the hold -----------------------------------------------------------------------------------------------------
WAITS = [True]
TG.CONDITIONS["finished-mod"] = lambda: WAITS[0]
SC = []


def fake(argv, **kw):
    SC.append(list(argv))
    seen_record = os.path.exists(TG.held_file())
    out = "inactive\n" if argv[2:3] == ["is-active"] else ""
    return subprocess.CompletedProcess(argv, 0, out + ("" if seen_record else ""), "")


try:
    TG.hold(["rm-selftests-nightly.timer"], "finished-mod", "", "x", runner=fake)
    check("4 a hold without its ruling is refused", False)
except ValueError:
    check("4 a hold without its ruling is refused", True)
try:
    TG.hold(["rm-selftests-nightly.timer"], "someday", NS.ITEM, "x", runner=fake)
    check("4 a hold on an unknown condition is refused", False)
except ValueError:
    check("4 a hold on an unknown condition is refused", True)
order = []
TG.hold(list(NS.HELD_TIMERS), "finished-mod", NS.ITEM, "test",
        runner=lambda argv, **kw: (order.append((list(argv), os.path.exists(TG.held_file()))),
                                   subprocess.CompletedProcess(argv, 0, "", ""))[1])
check("4 the hold is recorded BEFORE the stop, one stop for all four timers",
      len(order) == 1 and order[0][0][:3] == ["systemctl", "--user", "stop"] and order[0][1]
      and sorted(order[0][0][3:]) == sorted(NS.HELD_TIMERS), order)
rec = TG.load_held()
check("4 each record names its ruling and condition",
      all(rec[n]["per_ruling"] == NS.ITEM and rec[n]["until"] == "finished-mod" for n in NS.HELD_TIMERS), rec)
states = {n: "inactive" for n in NS.HELD_TIMERS}
states["rm-other.timer"] = "inactive"
check("4 timers_guard: the held timers are covered, an unheld stopped timer still alarms",
      TG.judge(states, TG.held_covered()) == {"rm-other.timer": "inactive (stopped, not failed)"},
      TG.judge(states, TG.held_covered()))
import deadman_check as DC   # noqa: E402
check("4 deadman: a held timer's promise is excused, not an outage",
      DC.excused("unit=rm-selftests-nightly.timer max_age=75h", runner=fake)
      and DC.real_check("unit=rm-red-dispatch.timer reading=/nonexistent max_age=30m", runner=fake) == DC.EXCUSED)
check("4 deadman: a stopped timer with no hold is not excused",
      not DC.excused("unit=rm-other.timer max_age=1h", runner=fake))
SC.clear()
check("4 nothing resumes while it waits", TG.resume_due(runner=fake) == [] and not SC, SC)

# ---- 5. the gates while it waits -------------------------------------------------------------------------------------
import ops_watch as OW   # noqa: E402
import red_dispatch as RD   # noqa: E402
import nightly_catchup as NC   # noqa: E402
check("5 the gates read the hold: ops_watch, red_dispatch and the catch-up all held",
      OW.nightly_held() and RD.nightly_held() and NC.nightly_held())
keys = ("testing.nightly_news", "testing.nightly_known_reds", "testing.nightly_unparked_reds",
        "testing.nightly_reds_overdue")
r = OW.nightly_news(0, {})
check("5 ops_watch: every nightly reading is 0 while held", all(r[k]["v"] == 0 for k in keys), r)
r = OW.held_nightly(keys, state={"NIGHTLY_RED:testing.red_abc": {"state": "OPEN"}})
check("5 ops_watch: a build-cop group the alarms hold reads 0, so it clears (no NIGHTLY_RED alarm stays)",
      r.get("testing.red_abc", {}).get("v") == 0, r)
check("5 ops_watch: the catch-up reading is 0 while held",
      OW.nightly_catchup_reading()["testing.nightly_gave_up"]["v"] == 0)
check("5 ops_watch rerun-reds reruns nothing while held", "held" in OW.rerun_reds(now=0))

# resume: a mod passed
WAITS[0] = False
SC.clear()
started = TG.resume_due(runner=fake)
check("4 once a mod has passed, resume_due starts every held timer and drops the records",
      sorted(started) == sorted(NS.HELD_TIMERS) and SC and SC[0][:3] == ["systemctl", "--user", "start"]
      and TG.load_held() == {}, (started, SC, TG.load_held()))
check("5 after the resume the gates open", not OW.nightly_held() and not RD.nightly_held() and not NC.nightly_held())

# ---- 6. the door -----------------------------------------------------------------------------------------------------
import publish as P   # noqa: E402
D = os.path.join(TMP, "door")
put(D, "src/RimMandrake/rimflow/maturation_fix.py", "def f():\n    return 1\n")
put(D, "src/RimMandrake/rimflow/selftest_maturation_fix.py",
    "import sys\nimport maturation_fix\nsys.exit(0 if maturation_fix.f() == 2 else 1)\n")
put(D, "src/RimMandrake/rimflow/selftest_live_one.py", "import sys\nsys.exit(1)\n")
put(D, "src/RimMandrake/Utils/other.py", "x = 1\n")
put(D, "src/RimMandrake/rimflow/selftest_any_change.py", "import sys\nsys.exit(1)\n")
put(D, P.PIPELINE_TESTS, json.dumps({"nightly": False, "timeout_s": 60,
                                     "pipeline_files": ["src/RimMandrake/rimflow/maturation*.py"],
                                     "tests": [{"test": "src/RimMandrake/rimflow/selftest_maturation_fix.py"},
                                               {"test": "src/RimMandrake/rimflow/selftest_live_one.py"},
                                               {"test": "src/RimMandrake/rimflow/selftest_any_change.py",
                                                "any_change": True, "inputs": ["src/RimMandrake/Utils/*.py"]}],
                                     "live_excluded": {"src/RimMandrake/rimflow/selftest_live_one.py": "live"}}))
subprocess.run(["git", "init", "-q", D], check=True)
subprocess.run(["git", "-C", D, "add", "-A"], check=True)
try:
    P.pipeline_checks(D, ["src/RimMandrake/rimflow/maturation_fix.py"])
    check("6 a change touching a pipeline file with a failing pipeline test is refused at publish", False)
except P.Refuse as e:
    check("6 a change touching a pipeline file with a failing pipeline test is refused at publish",
          "selftest_maturation_fix.py" in str(e) and "selftest_live_one" not in str(e), str(e))
check("6 a change touching no pipeline file and no any_change input adds no tests",
      P.pipeline_checks(D, ["src/RimMandrake/rimflow/unrelated.py"]) == 0.0)
try:
    P.pipeline_checks(D, ["src/RimMandrake/Utils/other.py"])
    check("6 an any_change test runs at the door for a change to a non-pipeline file it reads, and refuses on red", False)
except P.Refuse as e:
    check("6 an any_change test runs at the door for a change to a non-pipeline file it reads, and refuses on red",
          "selftest_any_change.py" in str(e), str(e))
put(D, "src/RimMandrake/rimflow/maturation_fix.py", "def f():\n    return 2   # fixed (a new size: a same-size rewrite in the same second reuses the stale .pyc)\n")
check("6 the same change, fixed, passes the door", P.pipeline_checks(D, ["src/RimMandrake/rimflow/maturation_fix.py"]) > 0)
check("6 a live_excluded test never runs at the door",
      [c["test"] for c in P.pipeline_selection(D, ["src/RimMandrake/rimflow/maturation_fix.py"],
                                               json.load(open(os.path.join(D, P.PIPELINE_TESTS))))]
      == ["src/RimMandrake/rimflow/selftest_maturation_fix.py"])
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
tc = json.load(open(os.path.join(REPO, P.TREE_CHECKS), encoding="utf-8"))
src = open(os.path.join(HERE, "publish.py"), encoding="utf-8").read()
# the 13 tree checks this door was added beside (277260bc81): each stays; a check added later is no defect
# (RIMMANDRAKE_NAME_NIGHTLY_SCOPE_TREE_CHECKS_COUNT_GREW_TWICE: 6b4fb634a7 and 3928fbe2da each added one)
TREE_13 = (
        "src/RimMandrake/rimflow/selftest_bench_word_prose.py",
        "src/RimMandrake/Utils/selftest_biome_twins_retired.py",
        "src/RimMandrake/Utils/selftest_one_path_seam.py",
        "src/RimMandrake/rimflow/selftest_liveproofs_wrappers_ruling.py",
        "src/RimMandrake/Utils/selftest_rmpaths.py",
        "src/RimMandrake/Utils/modcheck/selftest_launch_gate.py",
        "src/RimMandrake/Utils/selftest_fauna_normalization.py",
        "src/RimMandrake/Utils/selftest_modlist_order_lint.py",
        "src/RimMandrake/Utils/selftest_fuelsnows_name_cull.py",
        "src/RimMandrake/Utils/art/selftest_drawn_art_ruled.py",
        "src/RimMandrake/rimflow/selftest_entrypoint_inventory.py",
        "src/RimMandrake/Utils/selftest_call_deadline_lint.py",
        "src/RimMandrake/Utils/selftest_alpha_biomes_census.py",
)
gone = [t for t in TREE_13 if t not in {c.get("test") for c in tc["checks"]}]
check("6 the 13 publish tree checks stay, and publish still runs them before the pipeline checks",
      len(TREE_13) == 13 and not gone   # in order, at any indent (c3dfdd7293 moved both into a try)
      and re.search(r"\n([ \t]+)tree_checks\(top, changed(?:, gate)?\)\n\1pipeline_checks\(top, changed(?:, gate)?\)\n", src) is not None,
      gone or len(tc["checks"]))
pc = json.load(open(os.path.join(REPO, P.PIPELINE_TESTS), encoding="utf-8"))
check("6 the shipped pipeline set is out of the nightly (one line, nightly: false) and lists only existing tests",
      pc["nightly"] is False and all(os.path.isfile(os.path.join(REPO, c["test"])) for c in pc["tests"])
      and all(os.path.isfile(os.path.join(REPO, t)) for t in pc["live_excluded"]))

# ---- 7. the clean clone ----------------------------------------------------------------------------------------------
O = os.path.join(TMP, "origin_work")
G = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false"]
os.makedirs(O)
subprocess.run(G + ["init", "-q", "-b", "main", O], check=True)
put(O, "a.txt", "one\n")
subprocess.run(G + ["-C", O, "add", "a.txt"], check=True)
subprocess.run(G + ["-C", O, "commit", "-q", "-m", "one"], check=True)
CL = os.path.join(TMP, "nightly_clone")
check("7 the clean clone is made from origin", NS.refresh_clone(CL, O) is None
      and open(os.path.join(CL, "a.txt")).read() == "one\n")
put(O, "a.txt", "two\n")
subprocess.run(G + ["-C", O, "commit", "-q", "-am", "two"], check=True)
put(CL, "a.txt", "local edit\n")
put(CL, "stray.txt", "left by a test\n")
check("7 a refresh lands on origin/main exactly: local edits and strays gone",
      NS.refresh_clone(CL, O) is None and open(os.path.join(CL, "a.txt")).read() == "two\n"
      and not os.path.exists(os.path.join(CL, "stray.txt")))
seen = {}
rc = NS.run(C, clone=CL, origin=O, out=buf,
            runner=lambda argv, **kw: (seen.update(argv=argv, **kw), subprocess.CompletedProcess(argv, 0))[1])
check("7 with a finished mod the sweep runs run_selftests --nightly IN the clean clone, ~/.local/bin first on PATH",
      rc == 0 and seen.get("cwd") == CL and seen["argv"][1:] == [os.path.join(CL, "src", "RimMandrake", "Utils",
                                                                               "run_selftests.py"), "--nightly"]
      and seen["env"]["PATH"].split(os.pathsep)[0] == os.path.expanduser("~/.local/bin"), seen)

print("RESULT: %s (%d fail)" % ("GREEN" if not FAILS else "RED", len(FAILS)))
sys.exit(1 if FAILS else 0)
