#!/usr/bin/env python3
"""RW2 by planted workers on the real path: relentless.tick, a real git clone read by the real Effects methods, a
Claude-format transcript read by the real parser. Only the units and the ledger are FakeWorld's."""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import circling as C  # noqa: E402
import relentless as R  # noqa: E402
import selftest_relentless as SR  # noqa: E402

BLOCK = R.rules(os.path.join(R.HERE, "relentless_rules.json"))["circling"]
FAILS = []
HOME = tempfile.mkdtemp(prefix="circ-home-")
os.environ["HOME"] = HOME


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


class World(SR.FakeWorld):
    circling_tree = R.Effects.circling_tree
    transcripts = R.Effects.transcripts


class Worker:
    """One planted worker: a real clone, a real transcript, 120 s ticks."""

    def __init__(self, c=None, **rules):
        self.rig = SR.Rig(1, run_max_s=10**7, stale_s=10**7, circling=dict(BLOCK, **(c or {})), **rules)
        self.rig.w = World(1)
        self.rig.run_one("I0")
        self.clone = tempfile.mkdtemp(prefix="circ-clone-")
        self.git("init", "-q", "-b", "main")
        self.git("-c", "user.email=a@b", "-c", "user.name=a", "commit", "-q", "--allow-empty", "-m", "base")
        self.base = self.git("rev-parse", "HEAD").strip()
        s = self.rig.s
        st = s.load("I0")
        st["clone"], st["base"] = self.clone, self.base
        s.save(st)
        d = os.path.join(HOME, ".claude/projects", re.sub(r"[^A-Za-z0-9]", "-", self.clone))
        os.makedirs(d, exist_ok=True)
        self.log = os.path.join(d, "s.jsonl")
        self.n = 0
        self.tick_only()

    def git(self, *a):
        return subprocess.run(["git", *a], cwd=self.clone, check=True, capture_output=True, text=True).stdout

    def _row(self, kind, block, t):
        stamp = datetime.datetime.fromtimestamp(t, datetime.timezone.utc).isoformat().replace("+00:00", "Z")
        with open(self.log, "a") as f:
            f.write(json.dumps({"type": kind, "timestamp": stamp, "message": {"content": [block]}}) + "\n")

    def tool(self, name, inp, secs):
        """A tool that began now and takes `secs`, the transcript written before the tick that passes the time."""
        t = self.rig.now
        self.n += 1
        self._row("assistant", {"type": "tool_use", "id": str(self.n), "name": name, "input": inp}, t)
        self._row("user", {"type": "tool_result", "tool_use_id": str(self.n)}, t + secs)

    def write(self, name, text):
        with open(os.path.join(self.clone, name), "w") as f:
            f.write(text)

    def tick_only(self, dt=120):
        return self.rig.tick(dt)

    def hits(self):
        return {h["kind"] for h in C.hits_seen(self.rig.s)}

    def done(self):
        self.rig.done()
        shutil.rmtree(self.clone, ignore_errors=True)


def run(worker, minutes, act):
    for i in range(minutes // 2):
        act(worker, i)
        worker.tick_only()
    return worker.hits()


def t_test_share():
    w = Worker()
    w.write("a.py", "x = 1\n")
    got = run(w, 40, lambda x, i: x.tool("Bash", {"command": "python3 src/run_selftests.py --only selftest_x.py"}, 110))
    ok("test_share" in got, "S1 planted test-share worker named")
    st = w.rig.st("I0")
    ok(st["status"] == "running" and not w.rig.w.stops, "S4 named, not stopped: the run goes on")
    w.done()


def t_no_change():
    w = Worker()
    w.write("a.py", "x = 1\n")
    got = run(w, 40, lambda x, i: x.tool("Read", {"file_path": "/same/file.py"}, 5))
    ok("no_change" in got and "test_share" not in got, "S1 planted no-change worker named")
    w.done()


def t_aba():
    w = Worker()
    got = run(w, 16, lambda x, i: x.write("a.py", "x = %d\n" % (i % 2)))
    ok("oscillation" in got, "S1 planted A-B-A worker named")
    rows = C.samples_of(w.rig.s, "I0", w.rig.st("I0")["gen"])
    ok(len(C._collapse([s.get("sub") for s in rows])) >= 5, "S1 the tree series really went A-B-A-B-A")
    w.done()


def t_aba_needs_the_limit():
    w = Worker(c={"oscillation_limit": 3})
    seq = ["x = 1\n", "x = 2\n", "x = 1\n"]
    got = run(w, 6, lambda x, i: x.write("a.py", seq[i]))
    ok("oscillation" not in got, "S1 one return under the limit is not named")
    w.done()


def t_churn_comment():
    w = Worker()
    w.write("a.py", "x = 1\n")

    def act(x, i):
        x.write("a.py", "x = 1\n# note %d\n" % i)
        x.tool("Read", {"file_path": "/new/%d.py" % i}, 5)
    got = run(w, 34, act)
    ok("trivial_churn" in got and "no_change" not in got, "S2 comment-only churn named, its reads are not no-change")
    w.done()


def t_churn_tweak():
    w = Worker()
    w.write("a.py", "".join("line%d = 0\n" % n for n in range(50)))

    def act(x, i):
        x.write("a.py", "".join("line%d = %d\n" % (n, i if n == 0 else 0) for n in range(50)))
        x.tool("Read", {"file_path": "/new/%d.py" % i}, 5)
    got = run(w, 34, act)
    ok("trivial_churn" in got, "S2 one number tweaked over and over named")
    w.done()


def t_long_read():
    w = Worker()
    w.write("a.py", "x = 1\n")

    def act(x, i):
        x.tool("Read", {"file_path": "/repo/%d.py" % i}, 30)
        x.tool("Bash", {"command": "grep -n thing /repo/%d.txt" % i}, 20)
        x.tool("Bash", {"command": "python3 relentless.py learn --item I0 same words"}, 1)
    got = run(w, 80, act)
    ok(not got, "S3 80 min read-only investigation left alone: %s" % sorted(got))
    w.done()


def t_long_build():
    w = Worker()

    def act(x, i):
        x.write("a.py", "".join("def f%d():\n    return %d\n" % (n, n) for n in range((i + 1) * 5)))
        x.tool("Bash", {"command": "python3 src/run_selftests.py --only selftest_a.py"}, 60)
        x.tool("Bash", {"command": "python3 src/RimMandrake/Utils/winbuild.py X"}, 50)
    got = run(w, 80, act)
    ok(not got, "S3 80 min build with a moving diff left alone: %s" % sorted(got))
    w.done()


def t_blind():
    w = Worker()
    shutil.rmtree(os.path.join(w.clone, ".git"))
    got = run(w, 40, lambda x, i: x.tool("Bash", {"command": "python3 selftest_x.py"}, 110))
    rows = open(os.path.join(w.rig.s.item_dir("I0"), "circling.jsonl")).read()
    ok(not got and "unmeasured" in rows, "an unreadable clone is unmeasured, never a hit: %s" % sorted(got))
    w.done()


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


def t_stop_path():
    """Past the gate, the same planted worker goes by the existing path: gen bumped, clone kept, reading carried."""
    d = tempfile.mkdtemp(prefix="circ-s-")
    on = dict(BLOCK, stop=True)
    p = verdict(d, on)
    real, C.VERDICT = C.VERDICT, p
    try:
        w = Worker(c={"stop": True})
        w.write("a.py", "x = 1\n")
        gen = w.rig.st("I0")["gen"]
        for _ in range(25):
            w.tool("Read", {"file_path": "/same.py"}, 5)
            w.tick_only()
            if w.rig.st("I0")["status"] != "running":
                break
        st = w.rig.st("I0")
        ok(st["gen"] == gen + 1 and st["last_fail"]["class"] == "circling", "S4 past the gate: stopped, gen moved")
        ok("no_change" in st["last_fail"]["detail"], "S4 the reading is carried to the next run")
        ok(st["approach"] != "build", "S4 a stop forces a change of approach: %s" % st["approach"])
        ok(w.rig.w.stops and os.path.exists(os.path.join(w.clone, "a.py")), "S4 work kept in the clone")
        w.done()
    finally:
        C.VERDICT = real
    shutil.rmtree(d, ignore_errors=True)


def t_replay():
    """The replay tool on stored runs: wrongful and missed counted, a run with no record unmeasured."""
    bad, fine = Worker(), Worker()
    bad.write("a.py", "x = 1\n")
    fine.write("a.py", "x = 1\n")
    run(bad, 40, lambda x, i: x.tool("Read", {"file_path": "/same.py"}, 5))
    run(fine, 40, lambda x, i: x.tool("Read", {"file_path": "/n/%d.py" % i}, 5))
    gb, gf = bad.rig.st("I0")["gen"], fine.rig.st("I0")["gen"]
    v = C.replay(bad.rig.s, [{"item": "I0", "gen": gb, "label": "circling"}, {"item": "I0", "gen": gb, "label": "fine"},
                             {"item": "NOPE", "gen": 0, "label": "fine"}], BLOCK)
    ok(v["circling"] == 1 and v["missed"] == 0 and v["wrongful"] == 1, "replay counts a wrongful stop")
    ok(v["unmeasured"] == ["NOPE gen 0"], "replay: no record is unmeasured")
    v = C.replay(fine.rig.s, [{"item": "I0", "gen": gf, "label": "circling"}], BLOCK)
    ok(v["missed"] == 1, "replay counts missed waste")
    bad.done()
    fine.done()


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
    ok(k("python3 - <<'E'\nprint('selftest_a.py')\nE") == "editing", "a heredoc mentioning a selftest is editing")
    ok(k("python3 - <<'E'\nedit\nE\ntimeout 9 python3 a/selftest_b.py > o; tail o") == "selftest", "a test after a heredoc is a test")
    ok(k("python3 relentless.py learn --item I x") == "other", "a learn line is no finding")


def main():
    for t in (t_classify, t_test_share, t_no_change, t_aba, t_aba_needs_the_limit, t_churn_comment, t_churn_tweak,
              t_long_read, t_long_build, t_blind, t_gate, t_stop_path, t_replay):
        t()
    shutil.rmtree(HOME, ignore_errors=True)
    print("%d failed" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
