#!/usr/bin/env python3
"""selftest_arena_rounds.py — sibling order is enforced by the planners (ARENA_PLANNERS_ENFORCE_SIBLING_ORDER).

  relation   contains_for on a real linear git history: a later base contains the earlier task's fix
  static     chrono_order is a linear extension (seeded, deterministic, varies where the relation allows);
             check_rounds refuses a same-round pair and a too-early task (forced failures); a cycle is refused
  replay     arena_replay.schedule(contains=...) puts every contained task first in every arm; with the chrono
             builder swapped for the plain shuffle the SAME call raises TaskRefused (the check is live, not
             decoration); run_schedule computes the relation itself and runs each arm in chrono order
  dynamic    guard_give refuses a task while a contained task is held by another member or still free, gives it
             once that task is done; first_givable skips blocked tasks in the planner's own order
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arena_rounds as RD  # noqa: E402
import arena_replay as R  # noqa: E402

FAILS = []
H = "ab" * 32


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def refused(fn, *a, **k):
    try:
        fn(*a, **k)
    except RD.TaskRefused as e:
        return str(e)
    return None


def git_repo(d: Path) -> list[str]:
    def g(*a):
        return subprocess.run(["git", "-C", str(d), *a], capture_output=True, text=True, check=True).stdout.strip()
    subprocess.run(["git", "init", "-q", str(d)], check=True)
    shas = []
    for i in range(5):
        (d / "f.txt").write_text("v%d\n" % i)
        g("add", "f.txt")
        g("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "c%d" % i)
        shas.append(g("rev-parse", "HEAD"))
    return shas


def t_relation(c):
    tasks = {"T1": {"base_sha": c[0], "fix_sha": c[1]}, "T2": {"base_sha": c[1], "fix_sha": c[2]},
             "T3": {"base_sha": c[3], "fix_sha": c[4]}}
    rel = RD.contains_for(tasks, REPO)
    check(rel == {"T1": [], "T2": ["T1"], "T3": ["T1", "T2"]}, "contains_for on a linear history: %s" % rel)
    return tasks, rel


def t_static(rel):
    o = RD.chrono_order(rel, rel, seed=1)
    check(o == ["T1", "T2", "T3"], "chrono_order of a total relation is the chronology: %s" % o)
    loose = {"a": [], "b": [], "c": [], "d": ["a"]}
    outs = {tuple(RD.chrono_order(loose, loose, seed=s)) for s in range(40)}
    check(all(x.index("a") < x.index("d") for x in outs) and len(outs) > 3,
          "a loose relation keeps the seeded variety (%d orders) and always puts a before d" % len(outs))
    check(RD.chrono_order(loose, loose, seed=7) == RD.chrono_order(loose, loose, seed=7), "seeded: deterministic")
    check(refused(RD.check_rounds, [["T1", "T2"], ["T3"]], rel) is not None, "FORCED: a same-round pair is refused")
    check(refused(RD.check_rounds, ["T2", "T1", "T3"], rel) is not None, "FORCED: a task before its contained task is refused")
    check(refused(RD.check_rounds, ["T1", "T2", "T3"], rel) is None, "the chronological order passes")
    check(refused(RD.chrono_order, ["x", "y"], {"x": ["y"], "y": ["x"]}) is not None, "a cyclic relation is refused")


def t_replay(tasks, rel):
    arms = ["a1", "a2", "a3"]
    s = R.schedule(H, arms, list(tasks), rel)
    check(s["sibling_order"] and all(o == ["T1", "T2", "T3"] for o in s["orders"].values()),
          "schedule(contains) orders every arm chronologically: %s" % s["orders"])
    check(not R.schedule(H, arms, list(tasks))["sibling_order"], "schedule without contains says it did not order")
    real = R.arm_chrono_order
    R.arm_chrono_order = lambda fh, arm, ts, contains, salt=0: R.arm_order(fh, arm, ts, salt)
    try:
        why = None
        for h in ("ab" * 32, "cd" * 32, "ef" * 32):          # some plain shuffle puts T2 or T3 too early
            why = why or refused(R.schedule, h, arms, list(tasks), rel)
        check(why is not None, "FORCED: with the chrono builder replaced by the shuffle, schedule refuses: %s" % why)
    finally:
        R.arm_chrono_order = real
    seen = []
    real_one = R.run_one
    R.run_one = lambda arm, task, *a, **k: seen.append((arm, task)) or "ok"
    try:
        res = R.run_schedule(H, tasks, ["a1", "a2"], None, None, str(REPO), None)
    finally:
        R.run_one = real_one
    per = {a: [t for x, t in seen if x == a] for a in ("a1", "a2")}
    check(len(res) == 6 and all(v == ["T1", "T2", "T3"] for v in per.values()),
          "run_schedule computes the relation itself and runs each arm in chrono order: %s" % per)


def t_dynamic(rel):
    pool = list(rel)
    check(refused(RD.guard_give, "T2", rel, set(), pool) is not None, "FORCED: T2 refused while T1 is still free")
    check(refused(RD.guard_give, "T2", rel, set(), pool) is not None and not RD.may_give("T3", rel, {"T1"}, pool),
          "T3 refused while T2 (held by the other member) is not done")
    check(refused(RD.guard_give, "T2", rel, {"T1"}, pool) is None, "T2 given once T1 is done")
    check(RD.may_give("T2", rel, set(), ["T2", "T3"]), "a contained task outside the planner's pool does not block")
    tid, skipped = RD.first_givable(["T3", "T2", "T1"], rel, set(), pool)
    check(tid == "T1" and set(skipped) == {"T3", "T2"}, "first_givable skips the blocked, gives %s" % tid)


if __name__ == "__main__":
    d = Path(tempfile.mkdtemp(prefix="arena_rounds_"))
    try:
        REPO = d
        c = git_repo(d)
        tasks, rel = t_relation(c)
        t_static(rel)
        t_replay(tasks, rel)
        t_dynamic(rel)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    print("%d failure(s)" % len(FAILS))
    sys.exit(1 if FAILS else 0)
