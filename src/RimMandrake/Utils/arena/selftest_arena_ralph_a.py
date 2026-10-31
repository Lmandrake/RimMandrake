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
import time
import types
import io
import tarfile
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


SG_SRC = (HERE / "arena_safe_git.py").read_text()


def _mutated(pairs, tag):
    """The loop module with the (old, new) pairs applied. An anchor lives in exactly ONE of ralph_a_loop.py and
    arena_safe_git.py (the git hardening is defined once, in SG); a pair that hits SG is applied to a copy of SG that
    the mutated loop imports in place of the real one (restored afterwards, the real SG is never changed)."""
    src, sg_src = SRC, SG_SRC
    for old, new in pairs:
        n = src.count(old) + sg_src.count(old)
        assert n == 1, "mutation anchor not unique/absent: %r (%d hits)" % (old, n)
        if src.count(old):
            src = src.replace(old, new)
        else:
            sg_src = sg_src.replace(old, new)
    real = sys.modules.get("arena_safe_git")
    if sg_src != SG_SRC:
        sg = types.ModuleType("arena_safe_git")
        sg.__file__ = str(HERE / "arena_safe_git.py")
        exec(compile(sg_src, sg.__file__, "exec"), sg.__dict__)
        sys.modules["arena_safe_git"] = sg
    try:
        m = types.ModuleType("ralph_a_loop_" + tag)
        m.__file__ = str(HERE / "ralph_a_loop.py")
        exec(compile(src, m.__file__, "exec"), m.__dict__)
    finally:
        if real is not None:
            sys.modules["arena_safe_git"] = real
    return m


def variant(old=None, new=None):
    """The loop module, or a copy with one line mutated (exec'd with the real __file__ so its imports resolve)."""
    if old is None:
        return R
    return _mutated([(old, new)], "mut")


def variant_multi(pairs):
    """The loop module with SEVERAL lines mutated (defence in depth: every layer of one trap must be removed)."""
    return _mutated(pairs, "mut_multi")


def sh(cwd, *a):
    return subprocess.run(list(a), cwd=str(cwd), capture_output=True, text=True, check=True).stdout.strip()


TASK = {"id": "RA_ABSDIFF", "kind": "code", "size": "S", "area": "x", "live": "none", "base_sha": "",
        "prompt": "write absdiff(a, b) in mod.py returning |a - b|", "criteria": "absdiff(a, b) == |a - b| for all ints",
        "proof": "python3 -c 'import mod; assert mod.absdiff(5, 3) == 2'"}
GOOD = "def absdiff(a, b):\n    return abs(a - b)\n"
WEAK = "def absdiff(a, b):\n    return a - b\n"           # passes the gate's check (5, 3), fails the tester's (3, 5)
BROKEN = "def absdiff(a, b):\n    return 0\n"           # fails the gate's check


TBASE = [None]      # the testers' temp base: a sibling of the World dirs, never their ancestor (main sets it)


class World:
    """A temp arm clone + control dir + fakes. `builder(prompt) -> (source or None, rc)`, `tester(prompt, cwd)`."""

    def __init__(self, tmp, name, mod=R, builder=None, tester=None, writer=None, task=TASK, lane=None,
                 runway=None, precheck=None, new_id=None, tester_workdir=None, **kw):
        self.d = tmp / name
        self.root, self.ctl = self.d / "arm", self.d / "ctl"
        self.root.mkdir(parents=True)
        sh(self.root, "git", "init", "-q", "-b", "main")
        sh(self.root, "git", "config", "user.email", "t@t")
        sh(self.root, "git", "config", "user.name", "t")
        sh(self.root, "git", "config", "maintenance.auto", "false")    # a detached `git maintenance` outlives the commit
        sh(self.root, "git", "config", "gc.auto", "0")                 # and trips the loop's no-process-beside-it check
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
                             tester_workdir=tester_workdir, **dict(dict(sync=None, tester_tmp=TBASE[0]), **kw))

    def model(self, role, prompt, *, cwd, agent_id, run_id, timeout_s, log, sandbox=None):
        self.calls.append((role, agent_id, str(cwd)))
        self.sandbox = sandbox
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


def sc_capture(tmp, mod, tag):
    """ARENA_TESTER_SPEND_ENFORCE_METERED_HOME: the tester's Claude transcripts (HOME inside its root) and GPT call
    log (RM_GPT_CALL_LOG inside its root) are copied to the meter's helper store, keyed by its test_start record,
    BEFORE the root is deleted; the root is still deleted."""
    roots = []

    def t(prompt, cwd):
        root = cwd.parent
        roots.append(root)
        pj = root / "home" / ".claude" / "projects" / "-rt-tree"
        pj.mkdir(parents=True, exist_ok=True)
        (pj / "s.jsonl").write_text('{"type": "assistant"}\n')
        (root / "gpt").mkdir(exist_ok=True)
        (root / "gpt" / "c.jsonl").write_text('{"tokens_used": 1}\n')
        return default_tester(prompt, cwd)
    w = World(tmp, "CAP" + tag, mod, tester=t)
    run_steps(w)
    starts = [r for r in w.writer.records() if r["event"] == "test_start"]
    mans = [mod.HC.load(r)[0] for r in starts]
    return (bool(starts) and len(roots) == len(starts) and all(m and m["claude_files"] == ["-rt-tree/s.jsonl"]
            and m["gpt_files"] == ["c.jsonl"] and m["arm"] == R.ARM for m in mans)
            and not any(r.exists() for r in roots))


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
                      publish_cmd=w.loop.publish_cmd, sync=None, tester_tmp=TBASE[0])
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
            and "ralph" not in p.lower() and R.ARM not in p                       # L3: the prompt never names the arm
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


def sc_recover(tmp, mod, tag):
    """M1: killed after build_end was logged, before state.json was saved -> the restart runs the tester (from the
    log), never wedges; _recover is idempotent."""
    class Killed(BaseException):
        pass
    w = World(tmp, "M1" + tag, mod)
    real = w.loop._save

    def boom():
        if w.loop.state.get("pending"):
            raise Killed()
        real()
    w.loop._save = boom
    try:
        w.loop.step()
        return False
    except Killed:
        pass
    if (w.ctl / "state.json").exists():
        return False
    w.loop = mod.Loop(w.root, w.ctl, [TASK], model=w.model, gate=w.gate, writer=w.writer, release=lambda: None,
                      runway=lambda: {"state": "MEASURED", "runway": 0.9}, precheck=lambda log: True,
                      publish_cmd=w.loop.publish_cmd, sync=None, tester_tmp=TBASE[0])
    n = len(w.calls)
    out = w.loop.step()
    again = w.loop._recover(TASK)                # the build is tested and on main now: nothing to recover
    return (out.startswith("published") and [c[0] for c in w.calls[n:]] == ["test"] and len(w.pubs()) == 1
            and again is None)


def _arena_env(tmp, tag):
    root = tmp / ("arena" + tag)
    os.environ["ARENA_ROOT"] = str(root)
    os.environ["ARENA_CLONES"] = str(root / "clones")
    os.environ["ARENA_EVENT_TOKEN_FILE"] = str(tmp / ("secret" + tag) / "event_token")
    os.environ["ARENA_ANCHOR_FILE"] = str(tmp / ("secret" + tag) / "anchors.jsonl")
    os.environ["ARENA_WITNESS"] = str(tmp / ("secret" + tag) / "witness.jsonl")
    p = A.paths()
    L.init_token(p)
    return p


def sc_anchor(tmp, mod, tag):
    """M6: the signed log truncated below its anchor (state.json lost too) refuses before any pass; so does a log
    deleted outright."""
    ok = True
    for how in ("truncate", "delete"):
        p = _arena_env(tmp, "M6" + how + tag)
        sw = mod.SignedWriter(p)
        w = World(tmp, "M6" + how + tag, mod, writer=sw)
        if not run_steps(w)[-1].startswith("published"):
            return False
        logf = p["events"] / ("%s.jsonl" % R.ARM)
        lines = logf.read_text().splitlines(keepends=True)
        if how == "truncate":
            logf.write_text("".join(lines[:1]))
        else:
            logf.unlink()
        (w.ctl / "state.json").unlink()
        w2 = World(tmp, "M6b" + how + tag, mod, writer=mod.SignedWriter(p), task=dict(TASK, id="RA_NEXT"))
        try:
            w2.loop.step()
            ok = False
        except mod.Refused as e:
            ok = ok and "anchor" in str(e) and w2.calls == []
    return ok


def _orphan_cleanup(pgid):
    try:
        os.killpg(pgid, 9)
    except (ProcessLookupError, PermissionError):
        pass


def sc_orphan(tmp, mod, tag):
    """M2: a loop SIGKILLed mid-pass leaves its model group running; the next Loop.run kills that group (pidfile)
    before any step."""
    w = World(tmp, "M2" + tag, mod)
    log = w.d / "orphan.out"
    child = ("import sys; sys.path.insert(0, %r); import ralph_a_loop as R\n"
             "m = R.CmdModel(%r); m.pidfile = sys.argv[1]\n"
             "m('build', 'x', cwd=sys.argv[2], agent_id='a', run_id=0, timeout_s=300, log=sys.argv[3])\n"
             % (str(HERE), "%s -c \"import time; time.sleep(300)\"" % sys.executable))
    pr = subprocess.Popen([sys.executable, "-c", child, str(w.loop.pidfile), str(w.d), str(log)], cwd=str(w.d))
    t0 = time.time()
    while not w.loop.pidfile.exists() and time.time() - t0 < 30:
        time.sleep(0.1)
    try:
        pgid = json.loads(w.loop.pidfile.read_text())["pgid"]
    except (OSError, ValueError):
        pr.kill()
        return False
    pr.kill()                                    # the loop dies; its model's session may live on
    pr.wait()
    try:
        time.sleep(0.5)
        if not R.group_alive(pgid):
            # bwrap --die-with-parent (pid-namespace init) took the sandboxed model down with the loop: that path
            # leaves no orphan. The loop-start kill is defence in depth for one that escapes it: exercise it on a
            # stand-in group recorded in the same pidfile, exactly as spawn() records a model.
            # double fork: the stand-in is not our child, so once killed it is reaped (no zombie keeps its group)
            pgid = int(subprocess.run([sys.executable, "-c", "import subprocess, sys; print(subprocess.Popen("
                                       "[sys.executable, '-c', 'import time; time.sleep(300)'], "
                                       "start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, "
                                       "stderr=subprocess.DEVNULL).pid)"], capture_output=True, text=True).stdout)
            w.loop.pidfile.write_text(json.dumps({"pgid": pgid, "start": R.proc_start(pgid), "role": "build",
                                                  "agent": "a"}))
            if not R.group_alive(pgid):
                return False
        (w.ctl / "STOP").touch()
        out = w.loop.run(1)
        t0 = time.time()
        while R.group_alive(pgid) and time.time() - t0 < 3:
            time.sleep(0.1)
        return out == ["STOP"] and not R.group_alive(pgid) and not w.loop.pidfile.exists()
    finally:
        _orphan_cleanup(pgid)


def sc_busy_clone(tmp, mod, tag):
    """M2: a process with its cwd in the clone -> the build pass refuses, no model runs."""
    w = World(tmp, "M2b" + tag, mod)
    pr = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"], cwd=str(w.root))
    try:
        time.sleep(0.3)
        try:
            w.loop.step()
            return False
        except mod.Refused as e:
            return "cwd in the clone" in str(e) and w.calls == [] and pr.pid in R.procs_in(w.root)
    finally:
        pr.kill()
        pr.wait()


def sc_blind_root(tmp, mod, tag):
    """M3: no ancestor of the tester's cwd is (or is inside) the control dir, the clone or the World dir, and the
    tester root is gone after the pass."""
    seen = {}

    def t(prompt, cwd):
        seen["cwd"] = Path(cwd).resolve()
        anc = [seen["cwd"]] + list(seen["cwd"].parents)
        seen["leak"] = [str(a) for a in anc for b in (w.ctl, w.root, w.d)
                        if a == b.resolve() or a.is_relative_to(b.resolve())]
        seen["up"] = sorted(os.listdir(seen["cwd"].parent))
        return default_tester(prompt, cwd)
    w = World(tmp, "M3" + tag, mod, tester=t)
    out = run_steps(w)
    return (out[-1].startswith("published") and seen.get("leak") == [] and "last_failure.md" not in seen["up"]
            and "log" not in seen["up"] and not seen["cwd"].exists() and w.sandbox and w.sandbox.get("root"))


SANDBOX_PROBE = (
    "import os, sys, json\n"
    "res = {}\n"
    "for name, p in [('abs_note', sys.argv[1]), ('abs_clone', sys.argv[2]), ('up_note', '../ctl/last_failure.md'),"
    " ('upup', '../../ctl/last_failure.md')]:\n"
    "    try:\n"
    "        res[name] = open(p).read()\n"
    "    except OSError as e:\n"
    "        res[name] = 'ERR'\n"
    "res['write_own'] = open('mine.txt', 'w').write('x')\n"
    "print(json.dumps(res))\n")


def sc_bwrap(tmp, mod, tag):
    """M3: the tester model under bubblewrap cannot read the builder's notes or the clone by ABSOLUTE path, nor by
    ../ (needs /usr/bin/bwrap: none -> red, fail closed)."""
    if not (shutil.which("bwrap") or os.path.exists("/usr/bin/bwrap")):
        print("     (no bwrap on this machine: the M3 sandbox cannot be shown)")
        return False
    d = tmp / ("M3b" + tag)
    ctl, clone = d / "ctl", d / "arm"
    ctl.mkdir(parents=True)
    clone.mkdir()
    (ctl / "last_failure.md").write_text("BUILDER-NOTE")
    (clone / "secret.py").write_text("BUILDER-CLONE")
    troot = Path(tempfile.mkdtemp(prefix="rt-"))
    try:
        work = troot / "tree"
        work.mkdir()
        probe = troot / "probe.py"
        probe.write_text(SANDBOX_PROBE)
        m = mod.CmdModel("%s %s %s %s" % (sys.executable, probe, ctl / "last_failure.md", clone / "secret.py"))
        r = m("test", "P", cwd=work, agent_id="x-test-1", run_id=0, timeout_s=60, log=troot / "out.txt",
              sandbox={"root": troot, "hide": [ctl, clone]})
        res = json.loads(r["text"].strip().splitlines()[-1])
        return (r["rc"] == 0 and res["abs_note"] == "ERR" and res["abs_clone"] == "ERR" and res["up_note"] == "ERR"
                and res["upup"] == "ERR" and (work / "mine.txt").exists())
    except (ValueError, IndexError, KeyError) as e:
        print("     (sandbox probe output unreadable: %s)" % e)
        return False
    finally:
        shutil.rmtree(troot, ignore_errors=True)


def sc_env(tmp, mod, tag):
    """M4: the tester's env is an allow-list with a NEUTRAL id: no RM_ARM / RALPH_A_* / ARENA_*, no arm name in any
    value, a fresh HOME."""
    saved = {k: os.environ.get(k) for k in ("RM_ARM", "RALPH_A_TASKS", "RALPH_A_ROOT", "ARENA_X", "SECRET_X",
                                            "RM_GPT_CALL_LOG")}
    os.environ.update(RM_ARM="ralph_a", RALPH_A_TASKS="/x/tasks", RALPH_A_ROOT="/x/clone", ARENA_X="1",
                      SECRET_X="ralph_a", RM_GPT_CALL_LOG="/x/shared/gpt_calls.jsonl")
    troot = Path(tempfile.mkdtemp(prefix="rt-"))
    try:
        m = mod.CmdModel("%s -c \"import os, json, sys; sys.stdin.read(); print(json.dumps(dict(os.environ)))\""
                         % sys.executable)
        r = m("test", "P", cwd=troot, agent_id="ralph_a-test-abc", run_id=0, timeout_s=30, log=troot / "o.txt",
              sandbox=None)
        env = json.loads(r["text"].strip().splitlines()[-1])
        env.pop("PWD", None)
        bad = [k for k in env if k.startswith(("RALPH_A", "ARENA_", "RM_ARM")) or "ralph_a" in env[k].lower()]
        return (r["rc"] == 0 and not bad and env.get("TESTER_ID") == R.neutral_id("ralph_a-test-abc")
                and env.get("HOME") == str(troot / "home") and "SECRET_X" not in env
                # spend metering: the tester's GPT log is a dir in ITS root (captured before rmtree), never inherited
                and env.get("RM_GPT_CALL_LOG") == str(troot / "gpt") + "/" and (troot / "gpt").is_dir())
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(troot, ignore_errors=True)


def sc_homoglyph(tmp, mod, tag):
    """L1: a tester id that is the builder's with a Cyrillic look-alike or a combining accent is the SAME agent."""
    ok = True
    for i, fake in enumerate(("r\u0430lph_a-build-x", "ralph_a-bui\u0301ld-x", "RALPH_A-BUILD-\u0445")):
        lw = R.ListWriter()
        lw.emit(R.ARM, "build_end", lane="build", run_id="x", task="T", sha="c" * 40,
                detail={"builder": "ralph_a-build-x", "build_id": "T.c"})
        lw.emit(R.ARM, "test_start", lane="build", run_id="x", task="T", sha="c" * 40,
                detail={"tester": fake, "build_id": "T.c"})
        lw.emit(R.ARM, "test_end", lane="build", run_id="x", task="T", sha="c" * 40, verdict="pass",
                detail={"tester": fake, "build_id": "T.c"})     # ended: only the same-agent rule can refuse
        try:
            mod.require_tested(lw.records())
            ok = False
        except mod.NotTested:
            pass
    return ok and mod.agent_key("ralph_a-test-1") != mod.agent_key("ralph_a-build-1")


def sc_dup_build_end(tmp, mod, tag):
    """L2: a duplicated build_end then one test_start of that build does not wedge the (in-memory) log."""
    lw = R.ListWriter()
    for _ in range(2):
        lw.emit(R.ARM, "build_end", lane="build", run_id="x", task="T", sha="d" * 40,
                detail={"builder": "b1", "build_id": "T.d"})
    lw.emit(R.ARM, "test_start", lane="build", run_id="x", task="T", sha="d" * 40,
            detail={"tester": "t1", "build_id": "T.d"})
    lw.emit(R.ARM, "test_end", lane="build", run_id="x", task="T", sha="d" * 40, verdict="pass",
            detail={"tester": "t1", "build_id": "T.d"})
    mod.require_tested(lw.records())
    return True


def sc_runway_tester(tmp, mod, tag):
    """L4: runway good at the build, gone by the tester -> the tester pass does not start."""
    seq = iter([{"state": "MEASURED", "runway": 0.9}] + [{"state": "MEASURED", "runway": 0.01}] * 5)
    w = World(tmp, "L4" + tag, mod, runway=lambda: next(seq))
    out = w.loop.step()
    return out.startswith("runway") and w.roles() == ["build"] and w.loop.state.get("pending")


def sc_runway_neg(tmp, mod, tag):
    """L5: a negative / NaN threshold refuses instead of waving runway 0.0 through."""
    ok = True
    for v in ("-1", "nan", "-inf"):
        os.environ["RALPH_A_RUNWAY_MIN"] = v
        try:
            w = World(tmp, "L5%s%s" % (v.strip("-"), tag), mod, runway=lambda: {"state": "MEASURED", "runway": 0.0})
            ok = ok and w.loop.step().startswith("runway") and w.calls == []
        finally:
            os.environ.pop("RALPH_A_RUNWAY_MIN", None)
    return ok


def sc_sync(tmp, mod, tag):
    """L6: the build pass pulls main first (3 tries, 30/60 s apart); a pull that keeps failing stops the step before
    any model runs; a working origin is pulled."""
    slept = []
    w = World(tmp, "L6" + tag, mod, sync="default", sleep=slept.append)
    sh(w.root, "git", "remote", "add", "origin", str(tmp / "L6_nowhere.git"))   # a dead upstream: every pull fails
    out = w.loop.step()
    failed = out.startswith("sync failed") and slept == [30, 60] and w.calls == []
    origin = tmp / ("L6o" + tag + ".git")
    sh(tmp, "git", "clone", "-q", "--bare", str(w.root), str(origin))
    clone = tmp / ("L6c" + tag)
    sh(tmp, "git", "clone", "-q", "-b", "main", str(origin), str(clone))
    sh(clone, "git", "config", "user.email", "t@t")
    sh(clone, "git", "config", "user.name", "t")
    (clone / "NEW").write_text("x\n")
    sh(clone, "git", "add", "NEW")
    sh(clone, "git", "commit", "-q", "-m", "new")
    sh(clone, "git", "push", "-q", "origin", "main")
    sh(w.root, "git", "remote", "set-url", "origin", str(origin))
    sh(w.root, "git", "fetch", "-q", "origin")
    sh(w.root, "git", "branch", "-q", "--set-upstream-to=origin/main", "main")
    pulled = mod.default_sync(w.root, slept.append) and (w.root / "NEW").exists()
    return failed and pulled


def sc_sync_user_config(tmp, mod, tag):
    """The pull keeps the OWNER's git config (an insteadOf alias, as ssh/credential settings are) whether it lives in
    ~/.gitconfig or in the file $GIT_CONFIG_GLOBAL names: the alias URL only resolves through that config."""
    w = World(tmp, "L6u" + tag, mod)
    origin = tmp / ("L6uo" + tag + ".git")
    sh(tmp, "git", "clone", "-q", "--bare", str(w.root), str(origin))
    clone = tmp / ("L6uc" + tag)
    sh(tmp, "git", "clone", "-q", "-b", "main", str(origin), str(clone))
    sh(clone, "git", "config", "user.email", "t@t")
    sh(clone, "git", "config", "user.name", "t")
    gc = tmp / ("L6ugc" + tag)
    gc.write_text('[url "%s"]\n\tinsteadOf = fake://origin\n' % origin)
    sh(w.root, "git", "remote", "add", "origin", str(origin))
    sh(w.root, "git", "fetch", "-q", "origin")
    sh(w.root, "git", "branch", "-q", "--set-upstream-to=origin/main", "main")
    sh(w.root, "git", "remote", "set-url", "origin", "fake://origin")
    (clone / "NEW").write_text("x\n")
    sh(clone, "git", "add", "NEW")
    sh(clone, "git", "commit", "-q", "-m", "new")
    sh(clone, "git", "push", "-q", "origin", "main")
    saved = os.environ.get("GIT_CONFIG_GLOBAL")
    os.environ["GIT_CONFIG_GLOBAL"] = str(gc)
    try:
        return bool(mod.default_sync(w.root, lambda s: None, tries=1)) and (w.root / "NEW").exists()
    finally:
        if saved is None:
            os.environ.pop("GIT_CONFIG_GLOBAL", None)
        else:
            os.environ["GIT_CONFIG_GLOBAL"] = saved


def sc_dirty_sync(tmp, mod, tag):
    """GPT r1 P1: a builder killed mid-edit leaves a dirty tree (tracked edit + untracked file); the next sync must
    park it in the loop's own clone and still pull, instead of failing with `sync failed`."""
    w = World(tmp, "Q1dirty" + tag, mod)
    origin = tmp / ("P1do" + tag + ".git")
    sh(tmp, "git", "clone", "-q", "--bare", str(w.root), str(origin))
    sh(w.root, "git", "remote", "add", "origin", str(origin))
    sh(w.root, "git", "fetch", "-q", "origin")
    sh(w.root, "git", "branch", "-q", "--set-upstream-to=origin/main", "main")
    clone = tmp / ("P1dc" + tag)
    sh(tmp, "git", "clone", "-q", "-b", "main", str(origin), str(clone))
    sh(clone, "git", "config", "user.email", "t@t")
    sh(clone, "git", "config", "user.name", "t")
    (clone / "NEW").write_text("x\n")
    sh(clone, "git", "add", "NEW")
    sh(clone, "git", "commit", "-q", "-m", "new")
    sh(clone, "git", "push", "-q", "origin", "main")
    (w.root / "README").write_text("half-written by a killed builder\n")
    (w.root / "junk.tmp").write_text("x")
    ok = mod.default_sync(w.root, lambda s: None)
    clean = sh(w.root, "git", "status", "--porcelain") == ""
    kept = "ralph-a dirty" in sh(w.root, "git", "stash", "list")
    got = (bool(ok), clean, kept, (w.root / "NEW").exists())
    if not all(got):
        print("     (dirty sync: synced, clean, stashed, pulled = %s)" % (got,))
    return all(got)


RETIRED_OVERRIDES = {"RALPH_A_ALLOW_UNISOLATED_TESTER": "1", "RALPH_A_TESTER_SANDBOX": "none"}


class NoBwrap:
    """arm_sandbox sees no bubblewrap; the retired unisolated overrides are SET (they must change nothing)."""

    def __init__(self, mod, tmp):
        self.mod, self.tmp = mod, tmp

    def __enter__(self):
        self.bw = self.mod.AS.BWRAP
        self.env = {k: os.environ.get(k) for k in RETIRED_OVERRIDES}
        self.mod.AS.BWRAP = str(self.tmp / "no-such-bwrap")
        os.environ.update(RETIRED_OVERRIDES)

    def __exit__(self, *a):
        self.mod.AS.BWRAP = self.bw
        for k, v in self.env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def sc_unisolated(tmp, mod, tag):
    """GPT r1 P1 + ARENA_SANDBOX_HARDEN_RETIRED_TREES_VISIBLE: no bubblewrap -> the tester AND the builder are
    refused before anything is launched (no log written), and no env override brings an unisolated launch back."""
    d = tmp / ("U1" + tag)
    d.mkdir()
    m = mod.CmdModel("%s -c pass" % sys.executable)
    with NoBwrap(mod, tmp):
        for role in ("test", "build"):
            log = d / ("%s.out" % role)
            try:
                m(role, "P", cwd=d, agent_id="x-%s-1" % role, run_id=0, timeout_s=60, log=log, sandbox={"root": d})
                return False
            except mod.Refused as e:
                if "bwrap" not in str(e) or log.exists():
                    return False
    return True


def sc_builder_sandboxed(tmp, mod, tag):
    """ARENA_SANDBOX_HARDEN_RETIRED_TREES_VISIBLE: the BUILDER pass runs sandboxed too: the harness checkout, the
    retired pre-rewrite clones and the D:\\ mirror are invisible; its clone and scratch HOME are writable."""
    d = tmp / ("AB" + tag)
    d.mkdir()
    probe = d / "probe.py"
    probe.write_text("import os, json, sys\nsys.stdin.read()\n"
                     "seen = [p for p in sys.argv[1:] if os.path.exists(p)]\n"
                     "open('built.txt', 'w').write('x')\nopen(os.path.join(os.environ['HOME'], 'h'), 'w').write('x')\n"
                     "print(json.dumps({'seen': seen, 'home': os.environ['HOME']}))\n")
    hidden = [str(mod.HARNESS_REPO), "/home/mandrake/rm/retired-trees", "/mnt/d/Luke/dev/RimMandrake",
              str(Path.home() / ".claude" / "projects")]
    sanity = [p for p in hidden if os.path.exists(p)]
    m = mod.CmdModel("%s %s %s" % (sys.executable, probe, " ".join(hidden)))
    r = m("build", "P", cwd=d, agent_id="x-build-1", run_id=0, timeout_s=60, log=tmp / ("AB%s.out" % tag))
    try:
        res = json.loads(r["text"].strip().splitlines()[-1])
    except (ValueError, IndexError):
        print("     (builder probe output unreadable: %r)" % r["text"][-300:])
        return False
    if not sanity:
        print("     (none of the hidden paths exists on this machine: the probe cannot see a leak)")
        return False
    ok = r["rc"] == 0 and res["seen"] == [] and (d / "built.txt").exists() and res["home"] != str(Path.home())
    if not ok:
        print("     (builder probe: rc %s %r)" % (r["rc"], res))
    return ok


def sc_retry_fresh(tmp, mod, tag):
    """GPT r1 P2: a retried tester gets a fresh export, sandbox root and HOME, not the first tester's leftovers."""
    seen = []

    def t(prompt, cwd):
        root = cwd.parent
        leak = (root / "home" / "m1").exists() or (cwd / "mod.py").read_text() != GOOD or (root / "m1").exists()
        seen.append((str(root), leak))
        if len(seen) == 1:
            (root / "home").mkdir(exist_ok=True)
            (root / "home" / "m1").write_text("x")
            (root / "m1").write_text("x")
            (cwd / "mod.py").write_text("tampered\n")
            return "crashed without a verdict"
        return default_tester(prompt, cwd)
    w = World(tmp, "P2r" + tag, mod, tester=t)
    run_steps(w)
    return len(seen) == 2 and seen[0][0] != seen[1][0] and not seen[1][1]


def sc_refused_no_start(tmp, mod, tag):
    """GPT r2 (tester pass): a tester refused for lack of isolation never ran, so it leaves NO test_start (a false
    'tester started' record would satisfy require_tested if pending were lost); retries add none either."""
    nb = NoBwrap(mod, tmp)
    nb.__enter__()
    try:
        w = World(tmp, "NS" + tag, mod)
        real, pre = w.model, mod.CmdModel("true").preflight

        class M:
            preflight = staticmethod(pre)
            __call__ = staticmethod(real)
        w.loop.model = M()
        for _ in range(3):
            try:
                w.loop.step()
            except mod.Refused:
                pass
        recs = w.writer.records()
        return (not any(r.get("event") in ("test_start", "test_end") for r in recs)
                and not any(c[0] == "test" for c in w.calls)
                and any(r.get("event") == "build_end" for r in recs))
    finally:
        nb.__exit__()


def sc_publish_tested_sha(tmp, mod, tag):
    """GPT r2: what is published is the sha the gate and tester checked, even if the WIP ref moved meanwhile."""
    box = {}

    def t(prompt, cwd):
        r = box["w"].root
        (r / "evil.txt").write_text("untested\n")
        sh(r, "git", "add", "evil.txt")
        sh(r, "git", "commit", "-q", "-m", "untested commit on wip")
        return default_tester(prompt, cwd)
    w = World(tmp, "PT" + tag, mod, tester=t, builder=lambda p: (GOOD, 0))
    box["w"] = w
    run_steps(w)
    recs = w.writer.records()
    tested = [r.get("sha") for r in recs if r.get("event") == "test_start"]
    main = sh(w.root, "git", "rev-parse", "main")
    leaked = subprocess.run(["git", "cat-file", "-e", "main:evil.txt"], cwd=str(w.root), capture_output=True).returncode == 0
    return bool(tested) and main in tested and not leaked


# ---- RALPHA_EXPORT_FIX_BUILDER_GIT_TRUST: the builder owns .git; what the tester sees is the logged sha
def _git_world(tmp, name, mod):
    w = World(tmp, name, mod)
    (w.root / "mod.py").write_text(GOOD)
    sh(w.root, "git", "add", "mod.py")
    sh(w.root, "git", "commit", "-q", "-m", "good")
    return w


def sc_git_replace_ref(tmp, mod, tag):
    """T1: a replace ref the builder planted does not change the tester's tree or the diff of the sha."""
    w = _git_world(tmp, "GR" + tag, mod)
    good = sh(w.root, "git", "rev-parse", "HEAD")
    (w.root / "mod.py").write_text(BROKEN)
    sh(w.root, "git", "commit", "-q", "-am", "broken")
    bad = sh(w.root, "git", "rev-parse", "HEAD")
    sh(w.root, "git", "replace", bad, good)
    sane = sh(w.root, "git", "diff", "--stat", good, bad) == ""         # the trap is real: plain git sees no change
    dest = w.loop._export_tree(bad, tmp / ("GRx" + tag))
    diff = w.loop.git("diff", *mod.NO_DRIVER, good, bad)
    return sane and (dest / "mod.py").read_text() == BROKEN and "mod.py" in diff and "return" in diff \
        and GOOD.splitlines()[1] in diff


def sc_git_forged_blob(tmp, mod, tag):
    """T5 (final tester): a blob stored under another blob's name is refused by the tester export, not exported."""
    import zlib
    w = _git_world(tmp, "GF" + tag, mod)
    sha = sh(w.root, "git", "rev-parse", "HEAD")
    blob = sh(w.root, "git", "rev-parse", "HEAD:mod.py")
    good_ok = (w.loop._export_tree(sha, tmp / ("GFg" + tag)) / "mod.py").read_text() == GOOD
    sh(w.root, "git", "repack", "-a", "-d", "-q")
    op = w.root / ".git" / "objects" / blob[:2] / blob[2:]
    op.parent.mkdir(parents=True, exist_ok=True)
    op.write_bytes(zlib.compress(b"blob 7\0forged\n"))
    try:
        dest = w.loop._export_tree(sha, tmp / ("GFx" + tag))
    except mod.Refused:
        return good_ok
    return False


def sc_git_export_attrs(tmp, mod, tag):
    """T2: export-ignore / export-subst in the builder's .gitattributes do not change the tester's tree."""
    w = _git_world(tmp, "GE" + tag, mod)
    (w.root / "v.txt").write_text("$Format:%H$\n")
    (w.root / ".gitattributes").write_text("mod.py export-ignore\nv.txt export-subst\n")
    sh(w.root, "git", "add", "v.txt", ".gitattributes")
    sh(w.root, "git", "commit", "-q", "-m", "attrs")
    sha = sh(w.root, "git", "rev-parse", "HEAD")
    arch = subprocess.run(["git", "archive", "--format=tar", sha], cwd=str(w.root), capture_output=True).stdout
    lost = "mod.py" not in tarfile.open(fileobj=io.BytesIO(arch)).getnames()      # sanity: git archive loses it
    dest = w.loop._export_tree(sha, tmp / ("GEx" + tag))
    return lost and (dest / "mod.py").read_text() == GOOD and (dest / "v.txt").read_text() == "$Format:%H$\n"


def sc_git_grafts(tmp, mod, tag):
    """T3: a graft (info/grafts) does not rewrite the history the loop reads (merge-base of main and the head)."""
    w = _git_world(tmp, "GG" + tag, mod)
    main = sh(w.root, "git", "rev-parse", "HEAD")
    sh(w.root, "git", "switch", "-q", "-c", "feat")
    (w.root / "mod.py").write_text(BROKEN)
    sh(w.root, "git", "commit", "-q", "-am", "b")
    (w.root / "mod.py").write_text(GOOD + "# c\n")
    sh(w.root, "git", "commit", "-q", "-am", "c")
    head = sh(w.root, "git", "rev-parse", "HEAD")
    (w.root / ".git" / "info").mkdir(exist_ok=True)
    (w.root / ".git" / "info" / "grafts").write_text(head + "\n")        # head becomes a parentless commit
    plain = subprocess.run(["git", "merge-base", "main", head], cwd=str(w.root), capture_output=True, text=True)
    sane = plain.stdout.strip() != main                                  # sanity: plain git is fooled
    return sane and w.loop.git("merge-base", "main", head) == main


def _exec_marker(w, kind):
    """Plant a builder-owned execution hook (script touching `marker`); -> marker path."""
    marker = w.d / ("marker_" + kind)
    script = w.d / ("hook_" + kind + ".sh")
    script.write_text("#!/bin/sh\ntouch %s\n" % marker)
    script.chmod(0o755)
    cfg = lambda *a: sh(w.root, "git", "config", *a)                      # noqa: E731
    if kind == "fsmonitor":
        cfg("core.fsmonitor", str(script))
    elif kind == "textconv":
        cfg("diff.evil.textconv", str(script))
        (w.root / ".gitattributes").write_text("*.py diff=evil\n")
    elif kind == "external":
        cfg("diff.external", str(script))
    elif kind == "filter":
        cfg("filter.evil.clean", str(script))
        cfg("filter.evil.smudge", str(script))
        (w.root / ".git" / "info").mkdir(exist_ok=True)
        (w.root / ".git" / "info" / "attributes").write_text("*.py filter=evil\n")
    elif kind == "hooks":
        hd = w.d / "hooks"
        hd.mkdir()
        (hd / "post-checkout").write_text("#!/bin/sh\ntouch %s\n" % marker)
        (hd / "post-checkout").chmod(0o755)
        cfg("core.hooksPath", str(hd))
    return marker


def sc_git_exec(kind):
    def sc(tmp, mod, tag):
        w = _git_world(tmp, "GX" + kind + tag, mod)
        first = sh(w.root, "git", "rev-parse", "HEAD")
        (w.root / "mod.py").write_text(GOOD + "# more\n")
        sh(w.root, "git", "commit", "-q", "-am", "more")
        second = sh(w.root, "git", "rev-parse", "HEAD")
        marker = _exec_marker(w, kind)
        runs = {"fsmonitor": [("status",)] * 2, "textconv": [("diff", first, second)] * 2,
                "external": [("diff", first, second)] * 2,
                "hooks": [("switch", "-q", "-c", "other_s"), ("switch", "-q", "-c", "other_g")],
                "filter": [("add", "mod.py"), ("add", "mod.py")]}[kind]
        if kind == "filter":                              # a dirty file: `git add` runs the clean filter on it
            (w.root / "mod.py").write_text(GOOD + "# dirty one\n")
        subprocess.run(["git", *runs[0]], cwd=str(w.root), capture_output=True)    # sanity: plain git runs it
        if kind == "filter":
            (w.root / "mod.py").write_text(GOOD + "# dirty two, longer\n")
        sane = marker.exists()
        marker.unlink(missing_ok=True)
        extra = mod.NO_DRIVER if kind in ("textconv", "external") else ()
        w.loop.git(runs[1][0], *extra, *runs[1][1:])
        return sane and not marker.exists()
    sc.__name__ = "sc_git_exec_" + kind
    return sc



# ---- RALPHA_GIT_TRUST_NET: the pull and the failed-candidate resubmission (opus blind review of ralph_a)
def _pull_world(tmp, name, mod):
    """-> (w, origin path): an arm clone whose origin has one commit (NEW) the clone lacks."""
    w = World(tmp, name, mod)
    origin = tmp / (name + "_o.git")
    sh(tmp, "git", "clone", "-q", "--bare", str(w.root), str(origin))
    sh(w.root, "git", "remote", "add", "origin", str(origin))
    sh(w.root, "git", "fetch", "-q", "origin")
    sh(w.root, "git", "branch", "-q", "--set-upstream-to=origin/main", "main")
    clone = tmp / (name + "_c")
    sh(tmp, "git", "clone", "-q", "-b", "main", str(origin), str(clone))
    sh(clone, "git", "config", "user.email", "t@t")
    sh(clone, "git", "config", "user.name", "t")
    (clone / "NEW").write_text("x\n")
    sh(clone, "git", "add", "NEW")
    sh(clone, "git", "commit", "-q", "-m", "new")
    sh(clone, "git", "push", "-q", "origin", "main")
    return w, origin


def sc_pull_trap(kind):
    def sc(tmp, mod, tag):
        w, origin = _pull_world(tmp, "NP" + kind + tag, mod)
        marker = w.d / "marker"
        script = w.d / "evil.sh"
        script.write_text("#!/bin/sh\ntouch %s\nexit 1\n" % marker)
        script.chmod(0o755)
        cfg = lambda *a: sh(w.root, "git", "config", *a)                  # noqa: E731
        ok_extra = True
        if kind == "ssh":
            cfg("remote.origin.url", "ssh://nohost.invalid/x")
            cfg("core.sshCommand", str(script))
        elif kind == "uploadpack":
            cfg("remote.origin.uploadpack", str(script))
        elif kind == "ext":
            cfg("remote.origin.url", "ext::" + str(script))
            cfg("protocol.ext.allow", "always")
        elif kind == "merge":
            (w.root / "README").write_text("local edit\n")
            sh(w.root, "git", "commit", "-q", "-am", "local")
            (w.root / ".git" / "info").mkdir(exist_ok=True)
            (w.root / ".git" / "info" / "attributes").write_text("README merge=evil\n")
            cfg("merge.evil.driver", "%s %%A" % script)
            clone = tmp / ("NP" + kind + tag + "_c")
            (clone / "README").write_text("remote edit\n")
            sh(clone, "git", "commit", "-q", "-am", "remote")
            sh(clone, "git", "push", "-q", "origin", "main")
        elif kind == "insteadof":
            other = tmp / ("NP" + kind + tag + "_x.git")
            sh(tmp, "git", "clone", "-q", "--bare", str(origin), str(other))
            cfg("url.%s.insteadOf" % other, str(origin))
            ok_extra = False
        subprocess.run(["git", "pull", "--rebase", "-q"], cwd=str(w.root), capture_output=True, timeout=60,
                       env=dict(os.environ, GIT_TERMINAL_PROMPT="0"))       # sanity: plain git runs the planted command
        sane = marker.exists() or kind == "insteadof"
        marker.unlink(missing_ok=True)
        sh(w.root, "git", "rebase", "--abort") if (w.root / ".git" / "rebase-merge").exists() else None
        got = mod.default_sync(w.root, lambda s: None, tries=1)
        if kind == "insteadof":
            return not got            # the plain pull above followed the redirect; the loop refuses to pull at all
        return sane and not marker.exists()
    sc.__name__ = "sc_pull_trap_" + kind
    return sc


def sc_merge_driver_refused(tmp, mod, tag):
    """RALPHA_SYNC_MERGE_DRIVER_PIN_REFUSES: a builder-set `merge=<driver>` makes the pinned-false driver turn a CLEAN
    merge of that file into a conflict. The driver is never run, but the loop must not wedge on "sync failed": a
    defect event names the driver, the driver key is unset in the clone, the pull is retried and both edits land."""
    slept = []
    w = World(tmp, "MD" + tag, mod, sync="default", sleep=slept.append)
    base = "".join("line%d\n" % i for i in range(1, 8))
    (w.root / "README").write_text(base)
    sh(w.root, "git", "commit", "-q", "-am", "base")
    origin = tmp / ("MD" + tag + "_o.git")
    sh(tmp, "git", "clone", "-q", "--bare", str(w.root), str(origin))
    sh(w.root, "git", "remote", "add", "origin", str(origin))
    sh(w.root, "git", "fetch", "-q", "origin")
    sh(w.root, "git", "branch", "-q", "--set-upstream-to=origin/main", "main")
    clone = tmp / ("MD" + tag + "_c")
    sh(tmp, "git", "clone", "-q", "-b", "main", str(origin), str(clone))
    sh(clone, "git", "config", "user.email", "t@t")
    sh(clone, "git", "config", "user.name", "t")
    (clone / "README").write_text(base.replace("line7", "remote7"))
    sh(clone, "git", "commit", "-q", "-am", "remote")
    sh(clone, "git", "push", "-q", "origin", "main")
    (w.root / "README").write_text(base.replace("line1", "local1"))        # a different region: git merges it cleanly
    sh(w.root, "git", "commit", "-q", "-am", "local")
    marker = w.d / "marker"
    script = w.d / "evil.sh"
    script.write_text("#!/bin/sh\ntouch %s\nexit 1\n" % marker)
    script.chmod(0o755)
    (w.root / ".git" / "info").mkdir(exist_ok=True)
    (w.root / ".git" / "info" / "attributes").write_text("README merge=evil\n")
    sh(w.root, "git", "config", "merge.evil.driver", "%s %%A" % script)
    plain = subprocess.run(["git", "pull", "--rebase", "-q"], cwd=str(w.root), capture_output=True, timeout=60,
                           env=dict(os.environ, GIT_TERMINAL_PROMPT="0"))
    sane = marker.exists() and plain.returncode != 0                      # plain git runs the driver and stops
    marker.unlink(missing_ok=True)
    sh(w.root, "git", "rebase", "--abort") if (w.root / ".git" / "rebase-merge").exists() else None
    out = w.loop.step()
    defects = [r for r in w.writer.records() if r["event"] == "defect"
               and (r.get("detail") or {}).get("kind") == "sync_merge_driver_refused"]
    readme = sh(w.root, "git", "show", "main:README")
    left = subprocess.run(["git", "config", "--get-all", "merge.evil.driver"], cwd=str(w.root),
                          capture_output=True, text=True).stdout.strip()
    return (sane and not marker.exists() and not out.startswith("sync failed") and len(defects) == 1
            and "merge.evil.driver" in defects[0]["detail"]["drivers"] and left == ""
            and "local1" in readme and "remote7" in readme and slept == [])
sc_merge_driver_refused.__name__ = "sc_merge_driver_refused"


def sc_nochange_after_fail(tmp, mod, tag):
    """A builder that exits 0 with no change after a tester FAIL is a failed try: the failed sha is never gated or
    tested again, the second tester never gets to pass the already-failed diff and nothing merges."""
    seen = []

    def tester(prompt, cwd):
        seen.append(1)
        return "VERDICT: FAIL" if len(seen) == 1 else "VERDICT: PASS"
    builds = []

    def b(prompt):
        builds.append(1)
        return (WEAK, 0) if len(builds) == 1 else (None, 0)
    w = World(tmp, "NF" + tag, mod, builder=b, tester=tester)
    out = [w.loop.step(), w.loop.step()]
    return ("tester pass FAIL" in out[0] and out[1].startswith("failed") and len(seen) == 1
            and not w.pubs() and w.main_src() is None and w.roles() == ["build", "test", "build"])

def sc_pull_trap2(kind):
    """RALPHA_EXPORT_FIX_BUILDER_GIT_TRUST round 2 (opus blind review of 803f811f67): include.path, a remote section
    named like the pinned URL, an unset origin URL, and a signing program run by the rebase."""
    def sc(tmp, mod, tag):
        w, origin = _pull_world(tmp, "N2" + kind + tag, mod)
        marker = w.d / "marker"
        script = w.d / "evil.sh"
        script.write_text("#!/bin/sh\ntouch %s\nexit 1\n" % marker)
        script.chmod(0o755)
        cfg = lambda *a: sh(w.root, "git", "config", *a)                  # noqa: E731
        penv = dict(os.environ, GIT_TERMINAL_PROMPT="0")
        plain = ["git", "pull", "--rebase", "-q"]
        if kind == "include":
            other = tmp / ("N2" + kind + tag + "_x.git")
            sh(tmp, "git", "clone", "-q", "--bare", str(origin), str(other))
            inc = w.d / "inc.cfg"
            inc.write_text('[url "%s"]\n\tinsteadOf = %s\n' % (other, origin))
            cfg("include.path", str(inc))
            sane = bool(sh(w.root, "git", "config", "--get-regexp", r"^url\..*insteadof$"))      # git DOES read it
            got = mod.default_sync(w.root, lambda s: None, tries=1)
            return sane and not got                      # redirect by an included file: the loop refuses to pull
        if kind == "remote_section":
            U = "https://example.invalid/r.git"
            cfg("remote.origin.url", U)
            cfg("remote.%s.url" % U, str(origin))
            cfg("remote.%s.uploadpack" % U, str(script))
            subprocess.run(plain + [U, "main"], cwd=str(w.root), capture_output=True, timeout=60, env=penv)
            sane = marker.exists()                       # plain git ran the section's uploadpack
            marker.unlink(missing_ok=True)
            sh(w.root, "git", "rebase", "--abort") if (w.root / ".git" / "rebase-merge").exists() else None
            got = mod.default_sync(w.root, lambda s: None, tries=1)
            return sane and not got and not marker.exists() and not (w.root / "NEW").exists()
        if kind == "no_url":
            sh(w.root, "git", "remote", "remove", "origin")
            sh(tmp, "git", "clone", "-q", str(origin), str(w.root / "origin"))        # a builder-made ./origin repo
            c = w.root / "origin"
            sh(c, "git", "config", "user.email", "t@t")
            sh(c, "git", "config", "user.name", "t")
            (c / "EVIL").write_text("x\n")
            sh(c, "git", "add", "EVIL")
            sh(c, "git", "commit", "-q", "-m", "evil")
            (w.root / ".git" / "info").mkdir(exist_ok=True)
            (w.root / ".git" / "info" / "exclude").write_text("origin/\n")
            subprocess.run(plain + ["origin", "main"], cwd=str(w.root), capture_output=True, timeout=60, env=penv)
            sane = (w.root / "EVIL").exists()            # plain git pulled the builder's ./origin as "origin"
            sh(w.root, "git", "reset", "-q", "--hard", "HEAD~1") if sane else None
            got = mod.default_sync(w.root, lambda s: None, tries=1)
            return sane and not got and not (w.root / "EVIL").exists()
        if kind.startswith("gpg"):
            (w.root / "L").write_text("l\n")
            sh(w.root, "git", "add", "L")
            sh(w.root, "git", "commit", "-q", "-m", "local")
            cfg("commit.gpgSign", "true")
            cfg("user.signingkey", "x")
            fmt = {"gpg": None, "gpgssh": "ssh", "gpgx509": "x509"}[kind]
            key = {"gpg": "gpg.program", "gpgssh": "gpg.ssh.program", "gpgx509": "gpg.x509.program"}[kind]
            if fmt:
                cfg("gpg.format", fmt)
            cfg(key, str(script))
            subprocess.run(plain, cwd=str(w.root), capture_output=True, timeout=60, env=penv)
            sane = marker.exists()                       # plain git's rebase ran the signing program
            marker.unlink(missing_ok=True)
            sh(w.root, "git", "rebase", "--abort") if (w.root / ".git" / "rebase-merge").exists() else None
            got = mod.default_sync(w.root, lambda s: None, tries=1)
            return sane and not marker.exists() and got and (w.root / "NEW").exists()
        raise ValueError(kind)
    sc.__name__ = "sc_pull_trap2_" + kind
    return sc


def sc_same_tree_resubmit(kind):
    """A failed candidate re-presented under a NEW sha with the SAME tree (amend --no-edit semantics, or an empty
    commit on top) is the same diff: never gated or tested again; a failed try, no second tester."""
    def sc(tmp, mod, tag):
        seen = []

        def tester(prompt, cwd):
            seen.append(1)
            return "VERDICT: FAIL" if len(seen) == 1 else "VERDICT: PASS"
        builds = []
        holder = []

        def b(prompt):
            builds.append(1)
            if len(builds) == 1:
                return WEAK, 0
            r = holder[0].root
            if kind == "amend":
                sh(r, "git", "commit", "-q", "--amend", "--allow-empty", "-m", "reworded")
            else:
                sh(r, "git", "commit", "-q", "--allow-empty", "-m", "empty on top")
            return None, 0
        w = World(tmp, "TR" + kind + tag, mod, builder=b, tester=tester)
        holder.append(w)
        out = [w.loop.step(), w.loop.step()]
        return ("tester pass FAIL" in out[0] and out[1].startswith("failed") and len(seen) == 1
                and not w.pubs() and w.main_src() is None)
    sc.__name__ = "sc_same_tree_" + kind
    return sc


def sc_infra_retry(tmp, mod, tag):
    """A tester that gave NO verdict (infrastructure) does not condemn the candidate: the builder that rightly
    changes nothing on the retry gets the SAME candidate tested again (a try is still spent, MAX_TRIES bounds it)."""
    seen = []

    def tester(prompt, cwd):
        seen.append(1)
        return "tester crashed, no verdict" if len(seen) <= mod.TESTER_TRIES else default_tester(prompt, cwd)
    builds = []

    def b(prompt):
        builds.append(1)
        return (GOOD, 0) if len(builds) == 1 else (None, 0)
    w = World(tmp, "IR" + tag, mod, builder=b, tester=tester)
    out = [w.loop.step(), w.loop.step()]
    return "no verdict" in out[0] and out[1].startswith("published") and len(w.pubs()) == 1



MUTATIONS = [
    ("T1 replace refs honoured", sc_git_replace_ref, "\"GIT_NO_REPLACE_OBJECTS\": \"1\", ", ""),
    ("T1/T2 export read with git archive", sc_git_export_attrs,
     "        return export_tree(self.root, sha, dest)",
     "        subprocess.run(['git', '-C', str(self.root), 'archive', '--format=tar', '-o', str(dest) + '.tar', sha], "
     "check=True)\n        dest.mkdir(parents=True, exist_ok=True)\n        import tarfile\n"
     "        tarfile.open(str(dest) + '.tar').extractall(dest)\n        return dest"),
    ("T1 export via git archive honours replace refs", sc_git_replace_ref,
     "        return export_tree(self.root, sha, dest)",
     "        subprocess.run(['git', '-C', str(self.root), 'archive', '--format=tar', '-o', str(dest) + '.tar', sha], "
     "env=dict(os.environ), check=True)\n        dest.mkdir(parents=True, exist_ok=True)\n        import tarfile\n"
     "        tarfile.open(str(dest) + '.tar').extractall(dest)\n        return dest"),
    ("T5 export does not re-hash the objects", sc_git_forged_blob,
     "    ok, why = SG.verify_tree(root, sha)", "    ok, why = True, ''"),
    ("T3 grafts honoured", sc_git_grafts, "\"GIT_GRAFT_FILE\": os.devnull, ", ""),
    ("T4 fsmonitor not disabled", sc_git_exec("fsmonitor"), "\"-c\", \"core.fsmonitor=false\", ", ""),
    ("T4 hooksPath not disabled", sc_git_exec("hooks"), "\"-c\", \"core.hooksPath=\" + os.devnull, ", ""),
    ("T4 textconv run by the diff", sc_git_exec("textconv"), "NO_DRIVER = (\"--no-ext-diff\", \"--no-textconv\")",
     "NO_DRIVER = ()"),
    ("T4 diff.external run by the diff", sc_git_exec("external"), None, None),
    ("T4 filter clean/smudge drivers not neutralised", sc_git_exec("filter"),
     "head += no_filter_cfg(root)", "head += []"),
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
    ("F runway check removed", sc_runway,
     "        if why:\n            return self.status(\"runway: \" + why)\n        self._recover(task)",
     "        if False:\n            return self.status(\"runway: \" + why)\n        self._recover(task)"),
    ("I tester cwd = the clone", sc_blind, "        work = self.tester_workdir(pend[\"head\"], troot / \"tree\")",
     "        work = self.root"),
    ("S tester id check removed", sc_same_id, "            if agent_key(tester) == agent_key(pend[\"builder\"]) or not agent_key(tester):",
     "            if False:"),
    ("M1 recovery from the log removed", sc_recover, "        self._recover(task)\n", "        pass\n"),
    ("M6 anchor check removed", sc_anchor, "        if rep.get(\"refused\"):\n", "        if False:\n"),
    ("M2 stale pass not reaped", sc_orphan, "            reap_stale_pass(self.pidfile)", "            pass"),
    ("M2 busy-clone check removed", sc_busy_clone, "        busy = self.procs(self.root) if self.procs else []",
     "        busy = []"),
    ("M3 tester root under ctl", sc_blind_root,
     "            troot = self._tester_root()          # GPT r1 P2: export, sandbox root and HOME are fresh PER ATTEMPT\n",
     "            troot = self.ctl / \"tester\"; troot.mkdir(exist_ok=True)\n"),
    ("M3 no sandbox", sc_bwrap, "        argv, env = self.wrap(list(argv), env, cwd=cwd, rw=rw, home=home)\n", "        pass\n"),
    ("A1 builder launched unsandboxed", sc_builder_sandboxed, "        argv, env = self.wrap(list(argv), env, cwd=cwd, rw=rw, home=home)\n", "        pass\n"),
    ("M4 real id passed", sc_env, "TESTER_ID=neutral_id(agent_id))", "TESTER_ID=agent_id)"),
    ("M4 env not allow-listed", sc_env,
     "           if (k in keep or k.startswith(\"LC_\")) and not k.startswith((\"RALPH_A\", \"ARENA_\", \"RM_ARM\", \"RM_GPT_CALL_LOG\"))}",
     "           if True}"),
    ("A tester GPT log not set", sc_env, "    if gpt:\n", "    if False:\n"),
    ("A2 tester capture skipped", sc_capture, "                capture_tester(rec, troot, res.get(\"rc\"))", "                pass"),
    ("A2 tester capture after rmtree", sc_capture,
     "                capture_tester(rec, troot, res.get(\"rc\"))     # the meter reads the copy; the root dies next\n"
     "                shutil.rmtree(troot, ignore_errors=True)",
     "                shutil.rmtree(troot, ignore_errors=True)\n                capture_tester(rec, troot, res.get(\"rc\"))"),
    ("L1 norm_id only", sc_homoglyph, "                r = dict(r, detail=dict(d, **{k: agent_key(d[k])}))",
     "                pass"),
    ("L2 duplicate build_end kept", sc_dup_build_end, "                if key in seen:\n", "                if False:\n"),
    ("L4 tester runway unchecked", sc_runway_tester,
     "        why = self.runway_refusal()                               # re-checked here too",
     "        why = None                               # re-checked here too"),
    ("L5 negative threshold accepted", sc_runway_neg,
     "    return v if math.isfinite(v) and v >= 0 else float(\"inf\")", "    return v"),
    ("P1 dirty tree not parked", sc_dirty_sync,
     "    if git_run(root, \"status\", \"--porcelain\", capture_output=True, text=True).stdout.strip():", "    if False:"),
    ("P1 unisolated launch allowed", sc_unisolated, "            raise Refused(str(e))\n",
     "            return argv, env\n"),
    ("P2 tester context shared across retries", sc_retry_fresh,
     "            troot = self._tester_root()          # GPT r1 P2: export, sandbox root and HOME are fresh PER ATTEMPT",
     "            troot = self.__dict__.setdefault('_tr', self._tester_root())"),
    ("R2 test_start before isolation check", sc_refused_no_start,
     "                    pf(sandbox, work)\n", "                    pass\n"),
    ("R2 publish merges WIP not the tested sha", sc_publish_tested_sha,
     "self.git(\"merge\", \"-q\", \"--ff-only\", pend[\"head\"])", "self.git(\"merge\", \"-q\", \"--ff-only\", WIP)"),
    ("L6 pull drops the owner's $GIT_CONFIG_GLOBAL", sc_sync_user_config,
     "            if k in os.environ:\n                env[k] = os.environ[k]\n", ""),
    ("N1 ssh command from the clone's config", sc_pull_trap("ssh"),
     'return ["-c", "core.sshCommand=" + (vals[-1].decode("utf-8", "replace") if vals else "ssh")]', "return []"),
    ("N1 remote.origin.uploadpack from the clone's config", sc_pull_trap("uploadpack"),
     '"--upload-pack=git-upload-pack", url, MAIN', '"origin", MAIN'),
    ("N1 ext:: remote helper allowed", sc_pull_trap("ext"),
     [('env["GIT_ALLOW_PROTOCOL"] = "file:https:ssh"', "pass"), ('"-c", "protocol.ext.allow=never",', "")], None),
    ("N1 merge driver run by the rebase", sc_pull_trap("merge"), 'r"^merge\\..*\\.driver$"', 'r"^nomatch$"'),
    ("N1 url.insteadOf redirect followed", sc_pull_trap("insteadof"), 'r"^url\\..*\\.(push)?insteadof$"', 'r"^nomatch$"'),
    ("R2 include.path of the clone's config not read", sc_pull_trap2("include"),
     'if _clone_lines(root, ["config", "-z", "--name-only", "--get-regexp", r"^url',
     'if _clone_lines(root, ["config", "--local", "-z", "--name-only", "--get-regexp", r"^url'),
    ("R2 remote.<pinned url> section not refused", sc_pull_trap2("remote_section"),
     '        if url and any(k.startswith', '        if False and any(k.startswith'),
    ("R2 literal origin pulled when no URL is set", sc_pull_trap2("no_url"),
     "    if not url:\n        return False", "    url = url or 'origin'\n    if False:\n        return False"),
    ("R2 rebase honours commit.gpgSign and gpg.program", sc_pull_trap2("gpg"),
     [('"commit.gpgSign=false"', '"commit.gpgSign=true"'),
      ('"-c", "gpg.program=false", "-c", "gpg.openpgp.program=false",', "")], None),
    ("R2 rebase honours commit.gpgSign and gpg.ssh.program", sc_pull_trap2("gpgssh"),
     [('"commit.gpgSign=false"', '"commit.gpgSign=true"'), ('"-c", "gpg.ssh.program=false",', "")], None),
    ("R2 rebase honours commit.gpgSign and gpg.x509.program", sc_pull_trap2("gpgx509"),
     [('"commit.gpgSign=false"', '"commit.gpgSign=true"'), ('"-c", "gpg.x509.program=false"]', "]")], None),
    ("R2 rebase honours commit.gpgSign alone", sc_pull_trap2("gpg"),
     [('"commit.gpgSign=false"', '"commit.gpgSign=true"')], None),
    ("R3 failures keyed by sha only (amend)", sc_same_tree_resubmit("amend"),
     "        return r.stdout.strip() if r.returncode == 0 else None", "        return None"),
    ("R3 failures keyed by sha only (empty commit)", sc_same_tree_resubmit("empty"),
     "        return r.stdout.strip() if r.returncode == 0 else None", "        return None"),
    ("R4 tester infrastructure failure condemns the candidate", sc_infra_retry,
     "                record=verdict == \"fail\")", "                record=True)"),
    ("N2 failed candidate resubmitted by a no-change builder", sc_nochange_after_fail,
     "            if self.already_failed(task, head) else (None, None)", "            if False else (None, None)"),
    ("S1 merge-driver refusal wedges the loop", sc_merge_driver_refused,
     "            if drivers:                               # the pinned-false driver", "            if False:                               # the pinned-false driver"),
    ("S1 merge-driver refusal is silent", sc_merge_driver_refused, "                if report:\n", "                if False:\n"),
    ("L6 sync skipped", sc_sync, "        synced = self.sync is None or self.sync()", "        synced = True"),
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
    os.environ["ARENA_EVENT_TOKEN_FILE"] = "/nonexistent/token"
    r = m("build", "PROMPTBODY", cwd=tmp, agent_id="a", run_id=0, timeout_s=30, log=log)
    check(r["rc"] == 0 and r["text"].split() == ["build", "ralph_a", "False", "PROMPTBODY"],
          "CmdModel: prompt on stdin, builder role + RM_ARM set, arena token path not passed to the agent")
    # a builder's `git commit` must not leave a detached `git maintenance` with its cwd in the clone: the loop's next
    # "no process beside the build" check would refuse on it (ARENA_DRILL_SYNC_FLAKY_PENDING_MAIN, seen under load)
    sh(tmp, "git", "init", "-q", "-b", "main", "mnt")
    m = R.CmdModel("%s -c \"import subprocess; print(subprocess.run(['git','config','--get-all','maintenance.auto'],"
                   "capture_output=True,text=True).stdout.split(), subprocess.run(['git','config','--get','gc.auto'],"
                   "capture_output=True,text=True).stdout.split())\"" % sys.executable)
    r = m("build", "x", cwd=tmp / "mnt", agent_id="a", run_id=0, timeout_s=30, log=log)
    check(r["rc"] == 0 and r["text"].strip() == "['false'] ['0']",
          "CmdModel builder env pins maintenance.auto=false and gc.auto=0 (no detached git maintenance beside the pass)")
    check("maintenance.auto=false" in R.GIT_SAFE_CFG and "gc.auto=0" in R.GIT_SAFE_CFG,
          "the loop's own git calls pin maintenance.auto=false and gc.auto=0")
    m = R.CmdModel("%s -c \"import os,sys; d=sys.stdin.read(); print(os.environ.get('RALPH_A_ROLE'), "
                   "os.environ.get('RM_ARM'), os.environ['TESTER_ID'][:7], d)\"" % sys.executable)
    r = m("test", "PROMPTBODY", cwd=tmp, agent_id="a", run_id=0, timeout_s=30, log=log)
    check(r["rc"] == 0 and r["text"].split() == ["None", "None", "tester-", "PROMPTBODY"],
          "CmdModel tester role: prompt on stdin, no role/arm variables, a neutral TESTER_ID")
    pf = tmp / "pass.pid"
    # an orphan: not our child (its parent exits), so a killed one is reaped by init, as after a SIGKILLed loop
    gpid = int(subprocess.run([sys.executable, "-c", "import subprocess, sys; print(subprocess.Popen([sys.executable, "
                               "'-c', 'import time; time.sleep(60)'], start_new_session=True, stdout=subprocess.DEVNULL, "
                               "stderr=subprocess.DEVNULL).pid)"],
                              capture_output=True, text=True, timeout=30).stdout.strip())
    try:
        time.sleep(0.2)
        pf.write_text(json.dumps({"pgid": gpid, "start": "1"}))           # the pid now names another process
        check(R.reap_stale_pass(pf) is None and R.group_alive(gpid) and not pf.exists(),
              "M2 a pidfile whose pid was reused (start time differs) is dropped; that process is not killed")
        pf.write_text(json.dumps({"pgid": gpid, "start": R.proc_start(gpid)}))
        try:
            R.reap_stale_pass(pf, kill=lambda g, s: None, wait_s=0.2)
            check(False, "M2 an orphan group that will not die refuses the loop start")
        except R.Refused:
            check(R.group_alive(gpid), "M2 an orphan group that will not die refuses the loop start")
        check(R.reap_stale_pass(pf) == gpid and not R.group_alive(gpid) and not pf.exists(),
              "M2 reap_stale_pass kills the orphan's process group and drops the pidfile")
    finally:
        _orphan_cleanup(gpid)
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


QUICK_FIX = {
    "src/a/selftest_slow_ok.py": "import time; time.sleep(1.5); print('ok')\n",
    "src/b/selftest_slow_chg.py": "import time; time.sleep(1.5); print('ok')\n",
    "src/c/selftest_slow_red.py": "import time, sys; time.sleep(1.5); sys.exit(1)\n",
    "src/d/selftest_fast.py": "print('fast')\n",
}


def _quick_run(root, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("RM_SELFTEST_") and k != "PYTHONPATH"}
    env.update(RM_SELFTEST_REPO_ROOT=str(root), RM_SELFTEST_STATE_DIR=str(root / ".state"),
               RM_SELFTEST_LOCK=str(root / ".lock"), RM_SELFTEST_NO_HARNESS="1", RM_SELFTEST_QUICK_S="1.0",
               SELFTEST_TIMINGS_FILE=str(root / ".state" / "timings.json"))
    r = subprocess.run([sys.executable, str(HERE.parent / "run_selftests.py"), *args], cwd=str(root), env=env,
                       capture_output=True, text=True, timeout=300)
    return r.returncode, r.stdout + r.stderr


def _rs_variant(old=None, new=None):
    src = (HERE.parent / "run_selftests.py").read_text()
    if old is not None:
        assert src.count(old) == 1, "run_selftests mutation anchor: %r" % old
        src = src.replace(old, new)
    m = types.ModuleType("run_selftests_mut")
    m.__file__ = str(HERE.parent / "run_selftests.py")
    sys.modules["run_selftests_mut"] = m
    exec(compile(src, m.__file__, "exec"), m.__dict__)
    return m


def _quick_unit(RS):
    """quick_select over a fake state: only the unchanged slow PASS is skipped."""
    tests = [Path(x) for x in ("ok.py", "chg.py", "red.py", "fast.py", "new.py")]
    st = {"ok.py": {"state": "PASS", "secs": 50, "hash": "h"}, "chg.py": {"state": "PASS", "secs": 50, "hash": "old"},
          "red.py": {"state": "FAIL", "secs": 50, "hash": "h"}, "fast.py": {"state": "PASS", "secs": 1, "hash": "h"}}
    kept, skipped = RS.quick_select(tests, st, 20.0, rel=str, hash_of=lambda t: "h")
    return ([str(t) for t in kept] == ["chg.py", "red.py", "fast.py", "new.py"]
            and [str(t) for t, _ in skipped] == ["ok.py"] and skipped[0][1].startswith(RS.QUICK_TAG))


def t_quick(tmp):
    """H1: --quick skips ONLY a slow test that last PASSED with an unchanged source/dependency hash; every skip is
    printed SKIPPED(quick), counted, and named on the RESULT line; a changed-now-red or last-red slow test runs."""
    RS = _rs_variant()
    check(_quick_unit(RS), "H1 quick_select skips only the unchanged slow last-PASS test")
    for name, old, new in (
            ("hash ignored", "        if h is None or h != e[\"hash\"]:\n", "        if False:\n"),
            ("last state ignored", "        if not (slow and e.get(\"state\") == \"PASS\" and isinstance(e.get(\"hash\"), str)):",
             "        if not (slow and isinstance(e.get(\"hash\"), str)):")):
        check(not _quick_unit(_rs_variant(old, new)), "H1 mutation goes RED: quick_select %s" % name)
    root = tmp / "quickfix"
    for rel, body in QUICK_FIX.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(body)
    (root / ".state").mkdir()
    rc1, o1 = _quick_run(root, "--quick")
    (root / "src/b/selftest_slow_chg.py").write_text("import time, sys; time.sleep(1.5); sys.exit(1)\n")
    rc2, o2 = _quick_run(root, "--quick")
    (Path(tmp) / "quick2.out").write_text(o2)
    ran2 = [ln.split()[0] for ln in o2.splitlines() if "selftest_slow_chg.py" in ln or "selftest_slow_red.py" in ln]
    check(rc2 != 0 and "RESULT: RED" in o2 and "QUICK: 1 skipped" in o2 and "SKIPPED(quick)" in o2
          and any("SKIPPED(quick)" in ln and "selftest_slow_ok.py" in ln for ln in o2.splitlines())
          and ran2.count("FAIL") >= 2,
          "H1 --quick: the changed-now-red and the last-red slow tests RUN and fail the run; the unchanged slow PASS "
          "is SKIPPED(quick) and counted (rc1 %s, rc2 %s): %s" % (rc1, rc2, o2.strip()[-600:]))
    green, note = R.precheck_verdict(rc2, o2)
    check(not green, "H1 the loop's pre-check reads that quick run as red: %s" % note)
    for rel in ("src/b/selftest_slow_chg.py", "src/c/selftest_slow_red.py"):
        (root / rel).write_text("import time; time.sleep(1.5); print('ok')\n")
    rc3, o3 = _quick_run(root, "--quick")
    green, note = R.precheck_verdict(rc3, o3)
    check(rc3 == 0 and green and "pre-check only" in note and "QUICK: 1 skipped" in note,
          "H1 a quick green is logged as a pre-check only, with its skip count: %r rc %s %s" % (note, rc3,
                                                                                               o3.strip()[-300:]))
    check(R.precheck_verdict(0, "no result line")[0] is False and R.precheck_verdict(0, "RESULT: RED (x)")[0] is False
          and R.precheck_verdict(1, "RESULT: GREEN (x)")[0] is False
          and R.precheck_verdict(0, "RESULT: GREEN (x)") == (True, "pre-check green"),
          "H1 precheck_verdict: green needs rc 0 AND a RESULT: GREEN line")
    rc4, o4 = _quick_run(root, "--quick", "--only", "src/d/selftest_fast.py")
    check(rc4 != 0, "--quick with --only is refused")


def _red_out(*names):
    return "".join("[%d/9] FAIL 0.1s %s\n" % (i + 1, n) for i, n in enumerate(names)) + "RESULT: RED (x)\n"


def t_baseline_pinned(tmp):
    """Item ARENA_PRECHECK_HARDEN_BASELINE_FIRST_RED: a sandbox red is accepted only when the BASE commit is red on
    the same test; a builder's try that broke a test before the loop's first pre-check is never baselined."""
    c = tmp / "bl_clone"
    (c / "src").mkdir(parents=True)
    (c / "src/a.py").write_text("a = 1\n")
    g = ["git", "-C", str(c), "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run(["git", "init", "-q", "-b", "main", str(c)], check=True)
    subprocess.run(g + ["add", "-A"], check=True)
    subprocess.run(g + ["commit", "-q", "-m", "base"], check=True)
    base = subprocess.run(g + ["rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    tree = subprocess.run(g + ["rev-parse", "HEAD^{tree}"], capture_output=True, text=True).stdout.strip()
    logd = tmp / "bl_log"
    logd.mkdir()
    log = logd / "pre.0"
    calls = []

    def base_run(red):
        def f(root, b, lg):
            calls.append(b)
            return 1, _red_out(*red)
        return f
    # stale unkeyed baseline from the old code that holds the builder's break: never read
    (logd / "sandbox_red.json").write_text(json.dumps({"red": ["selftest_env.py", "selftest_broken.py"]}))
    (c / "src/a.py").write_text("a = 2  # the builder's unpublished try\n")
    subprocess.run(g + ["commit", "-q", "-am", "try"], check=True)
    v = R.baseline_verdict(1, _red_out("selftest_env.py", "selftest_broken.py"), log, root=c, base=base,
                           base_run=base_run(["selftest_env.py"]))
    check(v[0] is False and "selftest_broken.py" in v[1] and "selftest_env.py" not in v[1].split(":")[-1]
          and calls == [base, base],
          "BL1 the loop's FIRST red pre-check on a try that broke a test is RED (the base is run for the baseline, "
          "the stale unkeyed file ignored): %s" % (v,))
    bf = logd / ("sandbox_red.%s.json" % tree)
    check(bf.exists() and json.loads(bf.read_text())["red"] == ["selftest_env.py"],
          "BL1 the baseline is keyed by the base tree and holds only the base's reds")
    v = R.baseline_verdict(1, _red_out("selftest_env.py"), log, root=c, base=base,
                           base_run=base_run(["selftest_never.py"]))
    check(v[0] is True and len(calls) == 2 and "base" in v[1],
          "BL2 a red the base also has is green, LOUDLY, from the cached baseline (no second base run): %s" % (v,))
    # a clean clone AT the base tree: the run itself is the baseline (no export)
    c2 = tmp / "bl_clone2"
    subprocess.run(["git", "clone", "-q", str(c), str(c2)], check=True)
    subprocess.run(["git", "-C", str(c2), "checkout", "-q", base], check=True)
    log2 = tmp / "bl_log2" / "pre.0"
    log2.parent.mkdir()
    v = R.baseline_verdict(1, _red_out("selftest_env.py"), log2, root=c2, base=base,
                           base_run=base_run(["selftest_env.py"]))
    check(v[0] is True and len(calls) == 3 and "this run" in v[1],
          "BL3 a clean clone at base's tree counts its own run as one base observation (+1 export): %s" % (v,))
    # the same tree but DIRTY: the run is not the base's, so the base is run
    (c2 / "src/a.py").write_text("a = 3  # uncommitted\n")
    log3 = tmp / "bl_log3" / "pre.0"
    log3.parent.mkdir()
    v = R.baseline_verdict(1, _red_out("selftest_env.py", "selftest_broken.py"), log3, root=c2, base=base,
                           base_run=base_run(["selftest_env.py"]))
    check(v[0] is False and len(calls) == 5 and "selftest_broken.py" in v[1],
          "BL4 a dirty clone at base's tree runs the base for its baseline: %s" % (v,))

    # item ARENA_PRECHECK_FIX_FLAKY_BASE_RED: a test red at base only by chance (one of two base runs) is never
    # baselined, so a try that really breaks it stays red
    flips = []

    def flaky_base(root, b, lg):
        flips.append(str(lg))
        return 1, _red_out(*(["selftest_env.py", "selftest_flaky.py"] if len(flips) == 1 else ["selftest_env.py"]))
    log9 = tmp / "bl_log9" / "pre.0"
    log9.parent.mkdir()
    v = R.baseline_verdict(1, _red_out("selftest_env.py", "selftest_flaky.py"), log9, root=c, base=base,
                           base_run=flaky_base)
    bf9 = json.loads((log9.parent / ("sandbox_red.%s.json" % tree)).read_text())
    check(v[0] is False and "selftest_flaky.py" in v[1].split(":")[-1] and len(flips) == 2
          and len(set(flips)) == 2 and bf9["red"] == ["selftest_env.py"] and bf9["flaky"] == ["selftest_flaky.py"],
          "BL9 a test red in only one of two base runs is not excused (flaky, recorded apart): %s / %s" % (v, bf9))
    v = R.baseline_verdict(1, _red_out("selftest_env.py"), log9, root=c, base=base, base_run=flaky_base)
    check(v[0] is True and len(flips) == 2, "BL9 the base's steady red is still excused, from cache: %s" % (v,))
    # and the clean-at-base case: a flaky red in the clone's own run alone is not baselined either
    c2_clean = tmp / "bl_clone3"
    subprocess.run(["git", "clone", "-q", str(c), str(c2_clean)], check=True)
    subprocess.run(["git", "-C", str(c2_clean), "checkout", "-q", base], check=True)
    log10 = tmp / "bl_log10" / "pre.0"
    log10.parent.mkdir()
    v = R.baseline_verdict(1, _red_out("selftest_env.py", "selftest_flaky.py"), log10, root=c2_clean, base=base,
                           base_run=base_run(["selftest_env.py"]))
    check(v[0] is False and "selftest_flaky.py" in v[1].split(":")[-1],
          "BL9 a clean clone at base: its own flaky red without a second base red is red: %s" % (v,))

    def refused(root, b, lg):
        raise R.Refused("planted")
    log4 = tmp / "bl_log4" / "pre.0"
    log4.parent.mkdir()
    for name, kw in (("no base", dict(root=c, base=None)), ("no root", dict(root=None, base=base)),
                     ("refused base run", dict(root=c, base=base, base_run=refused)),
                     ("base run without RESULT", dict(root=c, base=base, base_run=lambda r, b, lg: (0, "nothing"))),
                     ("unknown base", dict(root=c, base="0" * 40))):
        v = R.baseline_verdict(1, _red_out("selftest_env.py"), log4, **kw)
        check(v[0] is False, "BL5 %s: a sandbox red cannot be baselined, it is red: %s" % (name, v))
    check(not list(log4.parent.glob("sandbox_red*")), "BL5 nothing was recorded as a baseline")
    check(R.baseline_verdict(0, "RESULT: GREEN (x)\n", log4) == (True, "pre-check green")
          and R.baseline_verdict(None, "", log4, root=c, base=base)[0] is False,
          "BL6 a green run needs no base; a refused sandbox is red")
    import ralph_c_loop as RC
    import trio_loop as TL
    check("pre_base" in R.Loop.build_pass.__code__.co_names
          and all("base" in f.__code__.co_varnames for f in (R.default_precheck, RC.precheck_c, TL.precheck_t)),
          "BL8 the build pass hands its base to the pre-check (ralph_a, ralph_c, trio)")
    # the real export path: base's tree exported beside the log with a harness-made .git, run sandboxed
    if shutil.which("bwrap"):
        e = tmp / "bl_exp"
        (e / "src/RimMandrake/Utils").mkdir(parents=True)
        (e / "src/RimMandrake/Utils/run_selftests.py").write_text(
            "import os, subprocess\n"
            "ok = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True).returncode == 0\n"
            "print('[1/1] FAIL 0.1s selftest_base_env.py')\n"
            "print('GIT_OK' if ok else 'GIT_MISSING'); print('RESULT: RED (x)')\n")
        ge = ["git", "-C", str(e), "-c", "user.name=t", "-c", "user.email=t@t"]
        subprocess.run(["git", "init", "-q", "-b", "main", str(e)], check=True)
        subprocess.run(ge + ["add", "-A"], check=True)
        subprocess.run(ge + ["commit", "-q", "-m", "base"], check=True)
        eb = subprocess.run(ge + ["rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        (e / "src/RimMandrake/Utils/run_selftests.py").write_text("print('RESULT: RED (try)')\n")
        subprocess.run(ge + ["commit", "-q", "-am", "try"], check=True)
        log5 = tmp / "bl_log5" / "pre.0"
        log5.parent.mkdir()
        v = R.baseline_verdict(1, _red_out("selftest_base_env.py", "selftest_broken.py"), log5, root=e, base=eb)
        blog = Path(str(log5) + ".base")
        check(v[0] is False and "selftest_broken.py" in v[1] and blog.exists() and "GIT_OK" in blog.read_text(),
              "BL7 the real base export runs base's run_selftests (sandboxed, in a harness-made repo), not the "
              "try's: %s / %s" % (v, blog.read_text()[-300:] if blog.exists() else "no base log"))


def t_precheck_era(tmp):
    """ARENA_REPLAY_PRECHECK_FIX_PRE_QUICK_ERA: a replay clone older than --quick gets its era's plain run, never an
    argparse refusal; a clone whose runner has --quick still gets it."""
    import ralph_a_loop as RAL
    for name, body, want in (("new", 'ap.add_argument("--quick", action="store_true")\n', ["--quick"]),
                             ("old", 'ap.add_argument("--full", action="store_true")\n', [])):
        f = tmp / ("era_" + name) / RAL.SELFTEST_RUNNER
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(body)
        a = RAL.precheck_argv(tmp / ("era_" + name))
        check(a[1] == RAL.SELFTEST_RUNNER and a[2:] == want,
              "pre-check argv for a %s-era clone: %s" % (name, " ".join(a[1:])))


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
    # M5: a take that lands between --mine's check and its release must survive. The test holds the bridge lock,
    # `release --mine` passes its fast check and blocks on the lock, BENCH's take is appended, the lock is dropped.
    base["RIMFLOW_BRIDGE_LOCK"] = str(tmp / "rf" / "bridge.lock")
    src = HERE.parents[1] / "rimflow"
    mut = tmp / "rf_mut" / "rimflow"
    shutil.copytree(src, mut, ignore=shutil.ignore_patterns("__pycache__"))
    mc = mut / "cli.py"
    s = mc.read_text()
    anchor = "            now2, tok2 = _bridge_hold(hk)\n"
    check(s.count(anchor) == 1, "M5 mutation anchor present once in cli.py")
    # Since 003240fec7 the check is made TWICE under the lock (here, and again in _bridge_release with expect_token),
    # and the first mutation (tok2 = None) was refused by the token compare, so it stopped being unsafe. The mutant
    # must remove BOTH re-checks to be the real race: the stale values from before the lock are trusted.
    anchor2 = "        holder, tok = _bridge_hold(model.DEFAULT_BRIDGE_HOST)\n        if holder != seat or tok != expect_token:\n"
    check(s.count(anchor2) == 1, "M5 second mutation anchor (_bridge_release re-check) present once in cli.py")
    mc.write_text(s.replace(anchor, "            now2, tok2 = now, tok\n")
                   .replace(anchor2, "        tok = expect_token\n        if holder != seat or tok != expect_token:\n"))
    for label, clip, want_safe in (("real", cli, True), ("mutant (no re-check inside the lock)", mc, False)):
        led = tmp / ("rf_race_%s" % want_safe)
        os.makedirs(led / "items")
        env = dict(base, RIMFLOW_LEDGER=str(led / "events.jsonl"), RIMFLOW_ITEMS=str(led / "items"),
                   RIMFLOW_SHARED_BRIDGE=str(led / "shared.json"),
                   PYTHONPATH=os.pathsep.join([str(HERE.parent)] + [x for x in [base.get("PYTHONPATH")] if x]))
        evp = led / "events" / "FOUNDRY.jsonl"
        subprocess.run([sys.executable, str(clip), "bridge", "take", "--for", "race"],
                       env=dict(env, RIMFLOW_SEAT="FOUNDRY"), capture_output=True, text=True, timeout=120)
        import fcntl
        fd = os.open(base["RIMFLOW_BRIDGE_LOCK"], os.O_RDWR | os.O_CREAT, 0o644)
        fcntl.flock(fd, fcntl.LOCK_EX)
        try:
            p = subprocess.Popen([sys.executable, str(clip), "bridge", "release", "--mine"],
                                 env=dict(env, RIMFLOW_SEAT="FOUNDRY"), stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, text=True)
            time.sleep(3.0)                     # let it pass the fast check and block on the lock
            evs = [json.loads(x) for x in evp.read_text().splitlines() if x.strip()]
            take = dict(evs[-1], seat="BENCH", ts=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        purpose="interleaved")
            take.pop("tsn", None)
            with open(led / "events" / "BENCH.jsonl", "a") as f:
                f.write(json.dumps(take) + "\n")
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)
        out = p.communicate(timeout=120)[0]
        who = subprocess.run([sys.executable, str(cli), "bridge", "who"], env=dict(env, RIMFLOW_SEAT="BENCH"),
                             capture_output=True, text=True, timeout=120).stdout
        crossed = any("out from under" in str(json.loads(x).get("override", ""))
                      for x in evp.read_text().splitlines() if x.strip())
        safe = "BENCH" in who and not crossed and "nothing released" in out
        check(safe == want_safe, "M5 interleaved take (%s): BENCH still holds=%s, no override=%s; out %r who %r"
              % (label, "BENCH" in who, not crossed, out.strip()[-160:], who.strip()[-160:]))


def main():
    tmp = Path(tempfile.mkdtemp(prefix="selftest_ralph_a_"))
    TBASE[0] = Path(tempfile.mkdtemp(prefix="selftest_ralph_a_rt_"))
    saved = {k: os.environ.get(k) for k in ("ARENA_ROOT", "ARENA_CLONES", "ARENA_EVENT_TOKEN_FILE",
                                             "ARENA_ANCHOR_FILE", "ARENA_WITNESS", "RM_ARM", "ARENA_METER_HELPERS")}
    os.environ.pop("RM_ARM", None)
    os.environ["RM_ARM_SANDBOX_SCRATCH"] = str(tmp / "armscratch")     # builder scratch: not the live arena root
    os.environ["ARENA_METER_HELPERS"] = str(tmp / "meter_helpers")      # tester captures: not the live arena root
    try:
        for name, fn in (("A planted failing check recovers", sc_planted_check),
                         ("B killed pass is not published and recovers", sc_killed_after_commit),
                         ("K loop killed before the tester: restart tests first", sc_loop_killed),
                         ("C planted defect the gate passes is caught by the tester", sc_tester_catches),
                         ("D build pass refused without a different-agent test_start", sc_refuses_untested),
                         ("A2 tester spend captured before its root is deleted", sc_capture),
                         ("E live task waits on the lane", sc_lane_wait),
                         ("F runway low/UNMEASURED refuses", sc_runway),
                         ("I tester is blind", sc_blind),
                         ("S tester id never the builder's", sc_same_id),
                         ("M1 killed after build_end: the restart tests that build (from the log)", sc_recover),
                         ("M6 signed log shorter than its anchor / deleted: refused before any pass", sc_anchor),
                         ("M2 an orphaned model group of a killed loop is killed on loop start", sc_orphan),
                         ("M2 a process working in the clone blocks the build pass", sc_busy_clone),
                         ("M3 tester root: no ancestor holds builder material", sc_blind_root),
                         ("M3 tester under bwrap cannot read builder paths", sc_bwrap),
                         ("M4 tester env allow-listed, neutral id", sc_env),
                         ("L1 homoglyph / accent builder id is the same agent", sc_homoglyph),
                         ("L2 duplicate build_end does not wedge", sc_dup_build_end),
                         ("L4 runway re-checked before the tester", sc_runway_tester),
                         ("L5 negative runway threshold refuses", sc_runway_neg),
                         ("L6 pull main first, 3 tries", sc_sync),
                         ("L6 the pull keeps the owner's $GIT_CONFIG_GLOBAL", sc_sync_user_config),
                         ("P1 dirty tree after killed build is parked", sc_dirty_sync),
                         ("P1 no bwrap: tester and builder refused, no override", sc_unisolated),
                         ("A1 the builder pass is sandboxed (no harness/retired/mirror)", sc_builder_sandboxed),
                         ("R2 refused tester logs no test_start", sc_refused_no_start),
                         ("R2 publishes the tested sha, not WIP", sc_publish_tested_sha),
                         ("P2 retried tester gets fresh context", sc_retry_fresh),
                         ("T1 a planted replace ref does not change the tested tree or diff", sc_git_replace_ref),
                         ("T2 export-ignore / export-subst do not change the tested tree", sc_git_export_attrs),
                         ("T5 a forged blob in the builder's object store is refused by the export", sc_git_forged_blob),
                         ("T3 a planted graft does not rewrite the history read", sc_git_grafts),
                         ("T4 builder fsmonitor does not run", sc_git_exec("fsmonitor")),
                         ("T4 builder core.hooksPath hooks do not run", sc_git_exec("hooks")),
                         ("T4 builder textconv driver does not run", sc_git_exec("textconv")),
                         ("T4 builder diff.external does not run", sc_git_exec("external")),
                         ("T4 builder filter.* clean/smudge drivers do not run", sc_git_exec("filter")),
                         ("N1 pull ignores the clone's core.sshCommand", sc_pull_trap("ssh")),
                         ("N1 pull ignores the clone's remote.origin.uploadpack", sc_pull_trap("uploadpack")),
                         ("N1 pull refuses an ext:: remote helper", sc_pull_trap("ext")),
                         ("N1 rebase runs no builder merge driver", sc_pull_trap("merge")),
                         ("N1 pull refuses a url.insteadOf redirect", sc_pull_trap("insteadof")),
                         ("R2 pull refuses a url.insteadOf set by an included file", sc_pull_trap2("include")),
                         ("R2 pull refuses a remote section named like the pinned URL", sc_pull_trap2("remote_section")),
                         ("R2 pull never takes the literal name origin", sc_pull_trap2("no_url")),
                         ("R2 rebase signs with no builder gpg.program", sc_pull_trap2("gpg")),
                         ("R2 rebase signs with no builder gpg.ssh.program", sc_pull_trap2("gpgssh")),
                         ("R2 rebase signs with no builder gpg.x509.program", sc_pull_trap2("gpgx509")),
                         ("R3 amended failed candidate (same tree) is not retested", sc_same_tree_resubmit("amend")),
                         ("R3 empty commit on a failed candidate is not retested", sc_same_tree_resubmit("empty")),
                         ("R4 a tester infrastructure failure does not condemn the candidate", sc_infra_retry),
                         ("N2 no-change builder after a FAIL cannot resubmit the failed sha", sc_nochange_after_fail),
                         ("S1 a merge driver in the clone never runs, never wedges the loop", sc_merge_driver_refused)):
            check(guarded(fn, tmp, R, ""), "green: " + name)
        for i, (name, fn, old, new) in enumerate(MUTATIONS):
            if isinstance(old, list):
                mod = variant_multi(old)
            elif old is None:        # diff.external: remove every layer (env, -c, flags)
                mod = variant_multi([("\"GIT_EXTERNAL_DIFF\": \"\", ", ""), ("\"-c\", \"diff.external=\",", ""),
                                     ("NO_DRIVER = (\"--no-ext-diff\", \"--no-textconv\")", "NO_DRIVER = ()")])
            else:
                mod = variant(old, new)
            check(not guarded(fn, tmp, mod, "_m%d" % i), "mutation goes RED: " + name)
        for fn, a in ((t_park_redstart_stop_lock, (tmp,)), (t_cmdmodel_kill, (tmp,)), (t_quick, (tmp,)), (t_precheck_era, (tmp,)), (t_baseline_pinned, (tmp,)),
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
        shutil.rmtree(TBASE[0], ignore_errors=True)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
