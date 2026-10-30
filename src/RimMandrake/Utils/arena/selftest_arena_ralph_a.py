#!/usr/bin/env python3
"""selftest_arena_ralph_a.py - ralph_a_loop.py (ARENA_RALPHA_BUILD_TESTER_PASS_EACH_BUILD), offline.

No real model, gate, seat, bridge or systemd: the builder and the tester are fake callables (one test kills a real
`sleep` subprocess through CmdModel's timeout), the gate is a fake that runs a check against the candidate tree, the
arm clone is a temp git repo, and the signed event log lives under a temp ARENA_ROOT.

Each criterion is proved by FORCED FAILURE: the scenario is run against the real loop (must be green) and against a
copy of the loop's source with the guarding line mutated away (must go red). A mutation that leaves its scenario
green is itself a failure of this selftest.
  A planted failing check: the first candidate fails the gate, is not published, its failure feeds the next pass,
    which repairs it and is published.                                             mutation: gate bypass, note feed
  B a killed pass (real SIGKILL at the timeout; and rc -9 after a commit) is not published; the next pass recovers.
                                                                                  mutation: rc check removed
  K the LOOP is killed between build_end and the tester: a new loop refuses a build pass and runs the tester first.
  C a planted defect the gate passes is caught by the tester pass, and fixed by the build pass it feeds.
                                                                                  mutation: tester pass skipped
  D the loop refuses a build pass while a build_end has no test_start from a different agent (missing, or the
    builder testing itself), without invoking the model.                           mutation: require_tested removed
  E a live task waits on its lane: no build and no tester pass until the lane has a verdict.
                                                                                  mutation: lane wait removed
  F runway low / UNMEASURED / garbled threshold refuses every pass.                mutation: runway check removed
  I blindness: the tester prompt has no builder output, prompt or failure note; its cwd has no .git.
                                                                                  mutation: tester cwd = the clone
  S the tester id may never equal the builder's.                                   mutation: id check removed
  plus: park after 3 tries, red start without a failure note writes STOP, STOP, flock, the real signed
  HarnessWriter (untested_builds == [] and no same-agent flag), run_selftests --quick selection, bridge release --mine.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import arena_eventlog as L  # noqa: E402
import arena_tasks as A  # noqa: E402
import ralph_a_loop as R  # noqa: E402

FAILS = []
SRC = (HERE / "ralph_a_loop.py").read_text()


def check(ok, msg):
    print(("ok   " if ok else "FAIL ") + msg)
    if not ok:
        FAILS.append(msg)


def variant(old=None, new=None):
    """The loop module, or a copy with one line mutated (exec'd with the real __file__ so its imports resolve)."""
    if old is None:
        return R
    assert SRC.count(old) == 1, "mutation anchor not unique/absent: %r" % old
    m = types.ModuleType("ralph_a_loop_mut")
    m.__file__ = str(HERE / "ralph_a_loop.py")
    exec(compile(SRC.replace(old, new), m.__file__, "exec"), m.__dict__)
    return m


def sh(cwd, *a):
    return subprocess.run(list(a), cwd=str(cwd), capture_output=True, text=True, check=True).stdout.strip()


TASK = {"id": "RA_ABSDIFF", "kind": "code", "size": "S", "area": "x", "live": "none", "base_sha": "",
        "prompt": "write absdiff(a, b) in mod.py returning |a - b|", "criteria": "absdiff(a, b) == |a - b| for all ints",
        "proof": "python3 -c 'import mod; assert mod.absdiff(5, 3) == 2'"}
GOOD = "def absdiff(a, b):\n    return abs(a - b)\n"
WEAK = "def absdiff(a, b):\n    return a - b\n"           # passes the gate's check (5, 3), fails the tester's (3, 5)
BROKEN = "def absdiff(a, b):\n    return 0\n"           # fails the gate's check


class World:
    """A temp arm clone + control dir + fakes. `builder(prompt) -> (source or None, rc)`, `tester(prompt, cwd)`."""

    def __init__(self, tmp, name, mod=R, builder=None, tester=None, writer=None, task=TASK, lane=None,
                 runway=None, precheck=None, new_id=None, tester_workdir=None):
        self.d = tmp / name
        self.root, self.ctl = self.d / "arm", self.d / "ctl"
        self.root.mkdir(parents=True)
        sh(self.root, "git", "init", "-q", "-b", "main")
        sh(self.root, "git", "config", "user.email", "t@t")
        sh(self.root, "git", "config", "user.name", "t")
        (self.root / "README").write_text("arm\n")
        sh(self.root, "git", "add", "README")
        sh(self.root, "git", "commit", "-q", "-m", "init")
        self.published, self.calls, self.prompts = [], [], []
        pub = self.d / "pub.py"
        pub.write_text("import subprocess,sys\nopen(sys.argv[1],'a').write(subprocess.run(['git','rev-parse',"
                       "'HEAD'],capture_output=True,text=True).stdout)\n")
        self.publog = self.d / "published.txt"
        self.builder = builder or (lambda prompt: (GOOD, 0))
        self.tester = tester or default_tester
        self.writer = writer or R.ListWriter()
        self.mod = mod
        self.loop = mod.Loop(self.root, self.ctl, [task], model=self.model, gate=self.gate, writer=self.writer,
                             lane=lane, runway=runway or (lambda: {"state": "MEASURED", "runway": 0.9}),
                             precheck=precheck or (lambda log: True), release=lambda: None,
                             publish_cmd="%s %s %s" % (sys.executable, pub, self.publog), new_id=new_id,
                             tester_workdir=tester_workdir)

    def model(self, role, prompt, *, cwd, agent_id, run_id, timeout_s, log):
        self.calls.append((role, agent_id, str(cwd)))
        self.prompts.append((role, prompt))
        if role == "build":
            src, rc = self.builder(prompt)
            if src is not None:
                (Path(cwd) / "mod.py").write_text(src)
                sh(cwd, "git", "add", "mod.py")
                if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=str(cwd)).returncode:
                    sh(cwd, "git", "commit", "-q", "-m", "build %s" % agent_id)   # unchanged -> empty candidate
            return {"rc": rc, "text": "BUILDER-TRANSCRIPT-%s" % agent_id}
        return {"rc": 0, "text": self.tester(prompt, Path(cwd))}

    def gate(self, task, base, head, phase, log):
        src = sh(self.root, "git", "show", "%s:mod.py" % head) if head != base else ""
        ns = {}
        try:
            exec(src, ns)
            tests = "PASS" if ns["absdiff"](5, 3) == 2 else "FAIL"
        except Exception:  # noqa: BLE001
            tests = "FAIL"
        recs = self.writer.records()
        builders = {(r.get("detail") or {}).get("builder") for r in recs if r["event"] == "build_end" and r.get("sha") == head}
        tested = any(r["event"] == "test_end" and r.get("sha") == head and r.get("verdict") == "pass"
                     and (r.get("detail") or {}).get("tester") not in builders for r in recs)
        steps = {"scope": "PASS", "placeholders": "PASS", "tests": tests, "xml": "NA", "csharp": "NA",
                 "deploy_plan": "NA", "proof": tests, "live": "NA", "test_record": "PASS" if tested else "FAIL"}
        ok = all(v in ("PASS", "NA") for v in steps.values())
        return {"verdict": "pass" if ok else "fail", "steps": {k: {"status": v} for k, v in steps.items()}}

    def main_src(self):
        r = subprocess.run(["git", "show", "main:mod.py"], cwd=str(self.root), capture_output=True, text=True)
        return r.stdout if r.returncode == 0 else None

    def pubs(self):
        return self.publog.read_text().split() if self.publog.exists() else []

    def roles(self):
        return [c[0] for c in self.calls]


def default_tester(prompt, cwd):
    """The fake tester: breaks it with a case the gate does not run (absdiff(3, 5))."""
    ns = {}
    try:
        exec((cwd / "mod.py").read_text(), ns)
        got = ns["absdiff"](3, 5)
    except Exception as e:  # noqa: BLE001
        return "ran absdiff(3, 5): crashed %s\nVERDICT: FAIL" % e
    if got != 2:
        return "ran absdiff(3, 5): expected 2, got %r\nVERDICT: FAIL" % got
    return "absdiff(5,3), absdiff(3,5), absdiff(0,0) all right\nVERDICT: PASS"


def repairs(prompt):
    """A builder that writes BROKEN first, the right code once a failure note is in its prompt."""
    return (GOOD, 0) if "## LAST FAILURE" in prompt else (BROKEN, 0)


def run_steps(w, n=6):
    out = []
    for _ in range(n):
        out.append(w.loop.step())
        if out[-1].startswith(("published", "parked", "STOP", "done", "runway", "waiting")):
            break
    return out


# ------------------------------------------------------------------------------------------------ scenarios
# each returns True when the criterion holds (green); the mutation runs expect False or an exception

def sc_planted_check(tmp, mod, tag):
    w = World(tmp, "A" + tag, mod, builder=repairs)
    out = run_steps(w)
    pubs = w.pubs()
    note_fed = any(r == "build" and "## LAST FAILURE" in p and "tests=FAIL" in p for r, p in w.prompts)
    return (pubs and len(pubs) == 1 and w.main_src() == GOOD and note_fed and out[0].startswith("failed")
            and not (w.ctl / "last_failure.md").exists())


def sc_killed_after_commit(tmp, mod, tag):
    seen = []

    def b(prompt):
        seen.append(prompt)
        return (GOOD, -9) if len(seen) == 1 else (GOOD + "# repaired\n", 0)
    w = World(tmp, "B" + tag, mod, builder=b)
    first = w.loop.step()
    nothing = not w.pubs() and w.main_src() is None
    out = run_steps(w)
    return (nothing and "killed" in first and "## LAST FAILURE" in seen[1] and len(w.pubs()) == 1
            and w.main_src() == GOOD + "# repaired\n" and out[-1].startswith("published"))


def sc_tester_catches(tmp, mod, tag):
    def b(prompt):
        return (GOOD, 0) if "absdiff(3, 5): expected 2, got -2" in prompt else (WEAK, 0)
    w = World(tmp, "C" + tag, mod, builder=b)
    out = run_steps(w)
    roles = w.roles()
    return ("tester pass FAIL" in out[0] and "absdiff(3, 5)" in out[0] and w.main_src() == GOOD and len(w.pubs()) == 1 and roles[:2] == ["build", "test"]
            and roles.count("build") == 2 and WEAK not in (w.main_src() or ""))


def sc_refuses_untested(tmp, mod, tag):
    ok = True
    # (1) a build_end with no test_start at all
    w = World(tmp, "D1" + tag, mod)
    w.writer.emit(R.ARM, "build_end", lane="build", run_id="x", task=TASK["id"], sha="a" * 40,
                  detail={"builder": "ralph_a-build-old", "build_id": "RA_ABSDIFF.aaaa"})
    try:
        w.loop.step()
        ok = False
    except R.Refused as e:
        ok = ok and "no test_start" in str(e)
    ok = ok and w.calls == []
    # (2) the builder 'testing' its own build
    w = World(tmp, "D2" + tag, mod)
    w.writer.emit(R.ARM, "build_end", lane="build", run_id="x", task=TASK["id"], sha="b" * 40,
                  detail={"builder": "ralph_a-build-same", "build_id": "RA_ABSDIFF.bbbb"})
    w.writer.emit(R.ARM, "test_start", lane="build", run_id="x", task=TASK["id"], sha="b" * 40,
                  detail={"tester": "ralph_a-build-same", "build_id": "RA_ABSDIFF.bbbb"})
    try:
        w.loop.step()
        ok = False
    except R.Refused:
        pass
    return ok and w.calls == []


def sc_loop_killed(tmp, mod, tag):
    class Killed(BaseException):
        pass
    hit = []

    def wd(sha, dest):
        if not hit:
            hit.append(1)
            raise Killed()
        return w.loop._export_tree(sha, dest)
    w = World(tmp, "K" + tag, mod, tester_workdir=wd)
    try:
        w.loop.step()
        return False
    except Killed:
        pass
    # restart: a new Loop over the same control dir and the same event log
    w.loop = mod.Loop(w.root, w.ctl, [TASK], model=w.model, gate=w.gate, writer=w.writer, release=lambda: None,
                      runway=lambda: {"state": "MEASURED", "runway": 0.9}, precheck=lambda log: True,
                      publish_cmd=w.loop.publish_cmd)
    try:
        w.loop.build_pass(TASK)                  # asked directly for a build pass: refused by the hard check
        return False
    except mod.NotTested:
        pass
    n = len(w.calls)
    out = w.loop.step()
    return out.startswith("published") and [c[0] for c in w.calls[n:]] == ["test"] and len(w.pubs()) == 1


def sc_lane_wait(tmp, mod, tag):
    class Lane:
        def __init__(self):
            self.pub, self.res = [], None

        def publish(self, task, sha, builder, files):
            self.pub.append((sha, builder, files))

        def result(self, task, sha):
            return self.res
    lane = Lane()
    w = World(tmp, "E" + tag, mod, task=dict(TASK, live="minimal"), lane=lane)
    s1 = w.loop.step()
    n = len(w.calls)
    s2, s3 = w.loop.step(), w.loop.step()
    idle = len(w.calls) == n and s2.startswith("waiting") and s3.startswith("waiting") and not w.pubs()
    lane.res = {"verdict": "pass"}
    s4 = w.loop.step()
    return (s1.startswith("waiting") and idle and lane.pub and lane.pub[0][2] == ["mod.py"]
            and s4.startswith("published") and len(w.calls) == n)


def sc_runway(tmp, mod, tag):
    ok = True
    for i, rw in enumerate(({"state": "MEASURED", "runway": 0.10}, {"state": "UNMEASURED", "why": "no meter"},
                            {"state": "MEASURED", "runway": None}, "garbage")):
        w = World(tmp, "F%d%s" % (i, tag), mod, runway=lambda rw=rw: rw)
        ok = ok and w.loop.step().startswith("runway") and w.calls == []
    os.environ["RALPH_A_RUNWAY_MIN"] = "not-a-number"
    try:
        w = World(tmp, "Fg" + tag, mod)
        ok = ok and w.loop.step().startswith("runway") and w.calls == []
    finally:
        os.environ.pop("RALPH_A_RUNWAY_MIN")
    # a pending tester pass is a pass too: low runway does not start it
    w = World(tmp, "Fp" + tag, mod)
    w.loop.state["pending"] = {"build_id": "x", "base": "HEAD", "head": "HEAD", "builder": "b"}
    w.loop.runway = lambda: {"state": "MEASURED", "runway": 0.01}
    return ok and w.loop.step().startswith("runway") and w.calls == []


def sc_blind(tmp, mod, tag):
    seen = {}

    def t(prompt, cwd):
        seen.update(prompt=prompt, cwd=cwd, git=(cwd / ".git").exists(), files=sorted(os.listdir(cwd)))
        return default_tester(prompt, cwd)

    def b(prompt):
        return (GOOD, 0) if "## LAST FAILURE" in prompt else (BROKEN, 0)
    w = World(tmp, "I" + tag, mod, builder=b, tester=t)
    run_steps(w)
    p = seen.get("prompt", "")
    root = str(w.root.resolve())
    return (bool(p) and "BUILDER-TRANSCRIPT" not in p and "LAST FAILURE" not in p and "## TASK" not in p
            and (R.ARM_DIR / "PROMPT.md").read_text()[:60] not in p and "## DIFF" in p and "## FROZEN SPEC" in p
            and "## TEST PLAN" in p and "+    return abs(a - b)" in p and not seen["git"]
            and not str(Path(seen["cwd"]).resolve()).startswith(root) and seen["files"] == ["README", "mod.py"])


def sc_same_id(tmp, mod, tag):
    w = World(tmp, "S" + tag, mod, new_id=lambda role: "ralph_a-same")
    try:
        w.loop.step()
        return False
    except R.Refused as e:
        return "equals the builder" in str(e) and [c[0] for c in w.calls] == ["build"]


MUTATIONS = [
    ("A gate bypass", sc_planted_check, "            ok, why = build_gate_ok(g)\n", "            ok, why = True, 'x'\n"),
    ("A failure note not fed", sc_planted_check, "            if self._note(name):\n", "            if False:\n"),
    ("B rc ignored", sc_killed_after_commit, "if rc != 0 else", "if False else"),
    ("C tester pass skipped", sc_tester_catches,
     "        return self.tester_pass(task)                             # AT ONCE",
     "        self.state['pending'] = None; return self._final(task, self.state.get('pending') or "
     "{'base': base, 'head': head}, n)  # AT ONCE"),
    ("C tester FAIL ignored", sc_tester_catches, "        if verdict != \"pass\":\n", "        if False:\n"),
    ("D require_tested removed", sc_refuses_untested,
     "        require_tested(self.writer.records())                     # HARD CHECK",
     "        pass                                                      # HARD CHECK"),
    ("K hard check removed (restart)", sc_loop_killed,
     "        require_tested(self.writer.records())                     # HARD CHECK",
     "        pass                                                      # HARD CHECK"),
    ("E lane wait removed", sc_lane_wait, "        if self.state.get(\"lane_wait\"):\n", "        if False:\n"),
    ("F runway check removed", sc_runway, "        if why:\n            return self.status(\"runway: \" + why)",
     "        if False:\n            return self.status(\"runway: \" + why)"),
    ("I tester cwd = the clone", sc_blind, "        work = self.tester_workdir(pend[\"head\"], bundle / \"tree\")",
     "        work = self.root"),
    ("S tester id check removed", sc_same_id, "            if L.norm_id(tester) == L.norm_id(pend[\"builder\"]):",
     "            if False:"),
]


def guarded(fn, *a):
    try:
        return bool(fn(*a))
    except Exception as e:  # noqa: BLE001
        print("     (%s raised %s: %s)" % (fn.__name__, type(e).__name__, str(e)[:160]))
        return False


# ------------------------------------------------------------------------------------------------ extra checks
def t_park_redstart_stop_lock(tmp):
    w = World(tmp, "P", builder=lambda p: (BROKEN, 0))
    out = run_steps(w, 5)
    br = subprocess.run(["git", "rev-parse", "-q", "--verify", "ralph/failed/RA_ABSDIFF"], cwd=str(w.root),
                        capture_output=True, text=True).returncode == 0
    check(out[-1].startswith("parked") and len(out) == 3 and br and w.main_src() is None and not w.pubs()
          and w.loop.step().startswith("done"), "three failed tries park the item on ralph/failed/<item>: %s" % out)
    w = World(tmp, "R", precheck=lambda log: False)
    s = w.loop.step()
    check(s.startswith("red start") and (w.ctl / "STOP").exists() and w.calls == [],
          "a red pre-check without last_failure.md writes STOP and runs no model")
    w = World(tmp, "R2", precheck=lambda log: False)
    (w.ctl / "last_failure.md").write_text("try 1 broke the suite\n")
    s = w.loop.step()
    check(w.roles()[:1] == ["build"], "a red pre-check explained by last_failure.md runs the repair pass")
    w = World(tmp, "T")
    (w.ctl / "STOP").touch()
    check(w.loop.run(3) == ["STOP"] and w.calls == [], "a STOP file stops the loop before any pass")
    import fcntl
    w = World(tmp, "U")
    fh = open(w.ctl / "loop.lock", "w")
    fcntl.flock(fh, fcntl.LOCK_EX)
    try:
        w.loop.run(1)
        check(False, "a second loop on the same control dir is refused (flock)")
    except R.Refused:
        check(w.calls == [], "a second loop on the same control dir is refused (flock)")
    finally:
        fh.close()


def t_cmdmodel_kill(tmp):
    m = R.CmdModel("%s -c \"import time; print('started', flush=True); time.sleep(60)\"" % sys.executable)
    log = tmp / "kill.out"
    import time
    t0 = time.time()
    r = m("build", "x", cwd=tmp, agent_id="a", run_id=0, timeout_s=1, log=log)
    check(r["rc"] == -9 and time.time() - t0 < 30 and "started" in log.read_text(),
          "CmdModel kills a pass at its timeout (process group SIGKILL, rc -9)")
    m = R.CmdModel("%s -c \"import os,sys; d=sys.stdin.read(); print(os.environ['RALPH_A_ROLE'], "
                   "os.environ['RM_ARM'], 'ARENA_EVENT_TOKEN_FILE' in os.environ, d)\"" % sys.executable)
    r = m("test", "PROMPTBODY", cwd=tmp, agent_id="a", run_id=0, timeout_s=30, log=log)
    check(r["rc"] == 0 and r["text"].split() == ["test", "ralph_a", "False", "PROMPTBODY"],
          "CmdModel: prompt on stdin, role + RM_ARM set, arena token path not passed to the agent")
    try:
        R.CmdModel("")
        check(False, "no model command refuses")
    except R.Refused:
        check(True, "no model command refuses")
    check(R.parse_verdict("x\nVERDICT: FAIL\nmore\nVERDICT: PASS\n") == "pass" and R.parse_verdict("pass") is None,
          "the tester verdict is the last VERDICT line; none -> None")


def t_signed_writer(tmp):
    root = tmp / "arena"
    os.environ["ARENA_ROOT"] = str(root)
    os.environ["ARENA_CLONES"] = str(root / "clones")
    os.environ["ARENA_EVENT_TOKEN_FILE"] = str(tmp / "secret" / "event_token")
    os.environ["ARENA_ANCHOR_FILE"] = str(tmp / "secret" / "anchors.jsonl")
    os.environ["ARENA_WITNESS"] = str(tmp / "secret" / "witness.jsonl")
    p = A.paths()
    L.init_token(p)
    sw = R.SignedWriter(p)

    def b(prompt):
        return (GOOD, 0) if "expected 2, got -2" in prompt else (WEAK, 0)
    w = World(tmp, "H", builder=b, writer=sw)
    run_steps(w)
    acc = sw.records()
    ev = [r["event"] for r in acc if r["event"] in ("build_end", "test_start", "test_end")]
    builders = {r["detail"]["builder"] for r in acc if r["event"] == "build_end"}
    testers = {r["detail"]["tester"] for r in acc if r["event"] == "test_start"}
    check(w.main_src() == GOOD and L.untested_builds(acc) == [] and L.flagged_same_agent(acc) == []
          and ev == ["build_end", "test_start", "test_end"] * 2 and not builders & testers and len(builders) == 2,
          "signed HarnessWriter log: every build_end tested by a different agent before the next build: %s" % ev)


def t_quick():
    sys.path.insert(0, str(HERE.parent))
    import run_selftests as RS
    tests = [Path("a/selftest_fast.py"), Path("a/selftest_slow.py"), Path("a/selftest_new.py")]
    prior = {"a/selftest_fast.py": 2.0, "a/selftest_slow.py": 99.0}
    kept, dropped = RS.quick_select(tests, prior, 20.0, rel=lambda t: str(t))
    check([str(t) for t in kept] == ["a/selftest_fast.py", "a/selftest_new.py"]
          and [str(t) for t in dropped] == ["a/selftest_slow.py"],
          "run_selftests --quick drops only tests whose last timing exceeds the limit (untimed kept)")
    r = subprocess.run([sys.executable, str(HERE.parent / "run_selftests.py"), "--quick", "--only", "x.py"],
                       capture_output=True, text=True, timeout=120)
    check(r.returncode != 0, "--quick with --only is refused")


def t_bridge_mine(tmp):
    cli = HERE.parents[1] / "rimflow" / "cli.py"
    os.makedirs(tmp / "rf" / "items")
    base = {k: v for k, v in os.environ.items() if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID")}
    base.update(RIMFLOW_LEDGER=str(tmp / "rf" / "events.jsonl"), RIMFLOW_ITEMS=str(tmp / "rf" / "items"),
                RIMFLOW_SHARED_BRIDGE=str(tmp / "rf" / "shared.json"), RIMFLOW_PROBE="no-reading")

    def rf(seat, *a):
        return subprocess.run([sys.executable, str(cli)] + list(a), env=dict(base, RIMFLOW_SEAT=seat),
                              capture_output=True, text=True, timeout=120)
    rf("FOUNDRY", "bridge", "take", "--for", "selftest")
    r = rf("BENCH", "bridge", "release", "--mine")
    who = rf("BENCH", "bridge", "who").stdout
    check(r.returncode == 0 and "nothing released" in r.stdout and "FOUNDRY" in who,
          "bridge release --mine by a non-holder releases nothing and exits 0: %r / who %r" % (r.stdout.strip(), who.strip()))
    r = rf("FOUNDRY", "bridge", "release", "--mine")
    who = rf("FOUNDRY", "bridge", "who").stdout
    check(r.returncode == 0 and "FOUNDRY" not in who.replace("FOUNDRY_", ""),
          "bridge release --mine by the holder releases it: %r / who %r" % (r.stdout.strip(), who.strip()))
    r = rf("FOUNDRY", "bridge", "take", "--mine", "--for", "x")
    check(r.returncode != 0, "--mine on another bridge verb is refused")


def main():
    tmp = Path(tempfile.mkdtemp(prefix="selftest_ralph_a_"))
    saved = {k: os.environ.get(k) for k in ("ARENA_ROOT", "ARENA_CLONES", "ARENA_EVENT_TOKEN_FILE",
                                             "ARENA_ANCHOR_FILE", "ARENA_WITNESS", "RM_ARM")}
    os.environ.pop("RM_ARM", None)
    try:
        for name, fn in (("A planted failing check recovers", sc_planted_check),
                         ("B killed pass is not published and recovers", sc_killed_after_commit),
                         ("K loop killed before the tester: restart tests first", sc_loop_killed),
                         ("C planted defect the gate passes is caught by the tester", sc_tester_catches),
                         ("D build pass refused without a different-agent test_start", sc_refuses_untested),
                         ("E live task waits on the lane", sc_lane_wait),
                         ("F runway low/UNMEASURED refuses", sc_runway),
                         ("I tester is blind", sc_blind),
                         ("S tester id never the builder's", sc_same_id)):
            check(guarded(fn, tmp, R, ""), "green: " + name)
        for i, (name, fn, old, new) in enumerate(MUTATIONS):
            check(not guarded(fn, tmp, variant(old, new), "_m%d" % i), "mutation goes RED: " + name)
        for fn, a in ((t_park_redstart_stop_lock, (tmp,)), (t_cmdmodel_kill, (tmp,)), (t_quick, ()),
                      (t_bridge_mine, (tmp,)), (t_signed_writer, (tmp,))):
            try:
                fn(*a)
            except Exception as e:  # noqa: BLE001
                check(False, "%s crashed: %s: %s" % (fn.__name__, type(e).__name__, e))
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(tmp, ignore_errors=True)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
