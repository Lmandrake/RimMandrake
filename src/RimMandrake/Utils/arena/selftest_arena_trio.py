#!/usr/bin/env python3
"""selftest_arena_trio.py - functional selftest of trio_loop.py (ARENA_TRIO_BUILD_CRITIC_ROUND_CAP_PARKS).

Each scenario runs the REAL loop over a temp git repo with a fake builder, gate, critic and simplify agent, and an
in-memory event log. Then every scenario is run again against a copy of trio_loop.py with ONE line mutated (the
fix reverted), and must go RED there: that is the forced-failure proof.

  A  never satisfied: exactly 4 builds, one simplify between rounds 2 and 3, park after 4, never a 5th (also after a
     restart with state.json deleted); id and priority kept; main untouched
  B  split: the parts share the item's budget; the last part publishes once; a split that keeps failing parks at 4
  C  every critic accept is bound to the sha (and tree) it saw; a work branch moved after the accept is not published
  D  a test_start by a different agent follows every build_end before the next build; an untested build refuses
  E  killed between build_end and the critic: the restart runs the critic on that build (from the log)
  F  a critic that never gives a verdict spends the round; a killed build pass spends the round
  G  a simplified spec on disk that is not the one the log recorded refuses
  I  a critic infrastructure failure (rc 1, no envelope) retries and is never a verdict; an earlier round's verdict
     is never reused (TRIO_CRITIC_FIX_RC1_REREAD_BURNS_ROUNDS); an is_error envelope is infrastructure too; log
     recovery restores a build whose critic attempts were all infrastructure; answered invalids spent before an
     infra Refused stay spent across a restart (pending kept or lost), and a critic killed mid-review is not recovered;
     a critic answer logged before a kill is recorded on restart, never rerolled
  V  an appended void of an infra reject drops its round from round counting and drops a pending build of that
     round; an accept, a reject a critic answered (whatever its prose) and a parked round are never voidable
  S  the simplify work tree is on the tester root (ext4), never in ctl (TRIO_SIMPLIFY_FIX_TREE_ON_DRVFS_REFUSED)
"""
import json
import os
import time
import shlex
import shutil
import subprocess
import sys
import tempfile
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arena_critic_calib as CC  # noqa: E402
import ralph_a_loop as RA  # noqa: E402
import trio_loop as T  # noqa: E402

FAILS = []
SRC = (HERE / "trio_loop.py").read_text()
TBASE = [None]

TASK = {"id": "TRIO_ABSDIFF", "kind": "code", "size": "S", "area": "x", "live": "none", "base_sha": "",
        "priority": "P1", "prompt": "write absdiff(a, b) in mod.py returning |a - b|",
        "criteria": "absdiff(a, b) == |a - b| for all ints", "proof": "python3 -c 'import mod'"}
GOOD = "def absdiff(a, b):\n    return abs(a - b)\n"
BROKEN = "def absdiff(a, b):\n    return 0\n"
SPLIT = 'thinking...\n{"action": "split", "parts": [{"prompt": "add mod.py", "criteria": "mod.py exists"}, ' \
        '{"prompt": "make absdiff right", "criteria": "absdiff(3, 5) == 2"}]}'
SIMPLE = '{"action": "simplify", "spec": {"prompt": "absdiff in mod.py, abs of the difference", "criteria": "c2"}}'


def check(ok, msg):
    print(("ok   " if ok else "FAIL ") + msg)
    if not ok:
        FAILS.append(msg)


def variant(old=None, new=None):
    if old is None:
        return T
    assert SRC.count(old) == 1, "mutation anchor not unique/absent: %r" % old
    m = types.ModuleType("trio_loop_mut")
    m.__file__ = str(HERE / "trio_loop.py")
    exec(compile(SRC.replace(old, new), m.__file__, "exec"), m.__dict__)
    return m


def sh(cwd, *a):
    return subprocess.run(list(a), cwd=str(cwd), capture_output=True, text=True, check=True).stdout.strip()


class Critic:
    """A fake critic: `decide(round_no, c) -> accept|reject|invalid`; records what it saw."""
    name, needs_tree = "fake", True

    def __init__(self, decide):
        self.decide, self.seen = decide, []

    def review(self, c):
        f = Path(c.tree) / "mod.py"
        self.seen.append({"cid": c.cid, "mod": f.read_text() if f.is_file() else None, "criteria": c.criteria,
                          "prompt": c.prompt, "tree": str(c.tree)})
        v = self.decide(len(self.seen), c)
        return CC.CriticVerdict(verdict=v, reasons=["fake critic says %s" % v], meta={})


class World:
    def __init__(self, tmp, name, mod=T, builder=None, critic=None, simplifier=None, writer=None, task=TASK, **kw):
        self.d = tmp / name
        self.root, self.ctl = self.d / "arm", self.d / "ctl"
        self.root.mkdir(parents=True)
        for a in (("init", "-q", "-b", "main"), ("config", "user.email", "t@t"), ("config", "user.name", "t")):
            sh(self.root, "git", *a)
        (self.root / "README").write_text("arm\n")
        sh(self.root, "git", "add", "README")
        sh(self.root, "git", "commit", "-q", "-m", "init")
        self.main0 = sh(self.root, "git", "rev-parse", "main")
        self.calls, self.prompts = [], []
        self.publog = self.d / "published.txt"
        pub = self.d / "pub.py"
        pub.write_text("import subprocess,sys\nopen(sys.argv[1],'a').write(subprocess.run(['git','rev-parse',"
                       "'HEAD'],capture_output=True,text=True).stdout)\n")
        self.builder = builder or (lambda prompt: (GOOD, 0))
        self.nb = 0
        self.simplifier = simplifier or (lambda prompt: "no idea")
        self.critic = critic or Critic(lambda k, c: "reject")
        self.writer = writer or RA.ListWriter()
        self.mod, self.task, self.kw = mod, task, kw
        self.gate_hook = None
        self.publish_cmd = "%s %s %s" % (sys.executable, pub, self.publog)
        self.reopen()

    def reopen(self, drop_state=False):
        if drop_state:
            (self.ctl / "state.json").unlink(missing_ok=True)
        self.loop = self.mod.TrioLoop(
            self.root, self.ctl, [self.task], model=self.model, critic=self.critic, gate=self.gate,
            writer=self.writer, runway=lambda: {"state": "MEASURED", "runway": 0.9}, precheck=lambda log: True,
            release=lambda: None, publish_cmd=self.publish_cmd, sync=None, procs=None, tester_tmp=TBASE[0],
            **self.kw)
        return self.loop

    def model(self, role, prompt, *, cwd, agent_id, run_id, timeout_s, log, sandbox=None):
        self.calls.append(role)
        self.prompts.append((role, prompt))
        if role == "build":
            src, rc = self.builder(prompt)
            self.nb += 1
            if src is not None:
                src += "# build %d\n" % self.nb              # every pass a new candidate (never an empty one)
                (Path(cwd) / "mod.py").write_text(src)
                sh(cwd, "git", "add", "mod.py")
                if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=str(cwd)).returncode:
                    sh(cwd, "git", "commit", "-q", "-m", "build %s" % agent_id)
            return {"rc": rc, "text": "x"}
        return {"rc": 0, "text": self.simplifier(prompt)}

    def gate(self, task, base, head, phase, log):
        if self.gate_hook:
            self.gate_hook(phase)
        src = sh(self.root, "git", "show", "%s:mod.py" % head) if head != base else ""
        ns = {}
        try:
            exec(src, ns)
            tests = "PASS" if ns["absdiff"](5, 3) == 2 else "FAIL"
        except Exception:  # noqa: BLE001
            tests = "FAIL"
        steps = {"scope": "PASS", "placeholders": "PASS", "tests": tests, "proof": tests, "test_record": "PASS"}
        ok = all(v in ("PASS", "NA") for v in steps.values())
        return {"verdict": "pass" if ok else "fail", "steps": {k: {"status": v} for k, v in steps.items()}}

    def recs(self, event=None, kind=None):
        return [r for r in self.writer.records() if (event is None or r["event"] == event)
                and (kind is None or (r.get("detail") or {}).get("kind") == kind)]

    def pubs(self):
        return self.publog.read_text().split() if self.publog.exists() else []

    def main_now(self):
        return sh(self.root, "git", "rev-parse", "main")

    def run(self, n=20):
        out = []
        for _ in range(n):
            out.append(self.loop.step())
            if out[-1].startswith(("published", "parked", "STOP", "done")):
                break
        return out


def guarded(fn, *a):
    try:
        return bool(fn(*a))
    except Exception as e:  # noqa: BLE001
        print("     (%s raised %s: %s)" % (fn.__name__, type(e).__name__, str(e)[:160]))
        return False


def parks(w):
    f = w.ctl / "parks.jsonl"
    return [json.loads(x) for x in f.read_text().splitlines()] if f.exists() else []


# ------------------------------------------------------------------------------------------------ scenarios
def sc_never_satisfied(tmp, mod, tag):
    w = World(tmp, "A" + tag, mod)
    out = w.run()
    seq = [c for c in w.calls]
    builds = seq.count("build")
    simp_at = seq.index("simplify") if "simplify" in seq else -1
    pk = parks(w)
    round3 = [p for r, p in w.prompts if r == "build"][2:3]
    after = [w.loop.step(), w.loop.step()]
    w.reopen(drop_state=True)                                   # restart with no state: the log still says parked
    again = w.run(4) + [w.loop.step()]
    ok = (builds == 4 and seq.count("simplify") == 1 and simp_at == 2 and len(w.critic.seen) == 4
          and len(w.recs("critic_round", "park")) == 1 and len(pk) == 1 and pk[0]["priority"] == "P1"
          and pk[0]["rounds"] == 4 and pk[0]["last_verdict"] == "reject" and pk[0]["task"] == TASK["id"]
          and w.main_now() == w.main0 and not w.pubs() and out[-1].startswith("parked")
          and all(a.startswith("done") for a in after) and "from the log" in again[0] and again[-1].startswith("done")
          and w.calls.count("build") == 4 and bool(round3) and TASK["prompt"] in round3[0]
          and json.loads((w.ctl / "specs" / "TRIO_ABSDIFF.json").read_text())["action"] == "keep"
          and sh(w.root, "git", "rev-parse", T.FAILED_BRANCH % TASK["id"]))
    print("     A%s: calls %s, parks %s, out %s, again %s" % (tag, seq, len(pk), out[-1][:70], again[-1][:40]))
    return ok


def sc_restart_counts(tmp, mod, tag):
    """Rounds 1-2 run, the loop dies, state.json is lost: the restart simplifies next and parks after 4 in all."""
    w = World(tmp, "R" + tag, mod)
    for _ in range(2):
        w.loop.step()
    two = w.calls.count("build")
    w.reopen(drop_state=True)
    w.run()
    w.reopen(drop_state=True)
    w.run(3)
    ok = two == 2 and w.calls.count("build") == 4 and w.calls.index("simplify") == 2 and \
        len(w.recs("critic_round", "park")) == 1
    print("     R%s: calls %s" % (tag, w.calls))
    return ok


def sc_split(tmp, mod, tag):
    """Rejected twice, split into 2 parts: part 1 accepted at round 3, part 2 at round 4, published once."""
    def builder(prompt):
        return (GOOD + "# part 2\n", 0) if "PART 2 of 2" in prompt else (GOOD, 0)
    w = World(tmp, "B" + tag, mod, builder=builder, simplifier=lambda p: SPLIT,
              critic=Critic(lambda k, c: "reject" if k <= 2 else "accept"))
    out = w.run()
    vs = w.recs("critic_round", "verdict")
    ok = (out[-1].startswith("published") and len(w.pubs()) == 1 and w.calls.count("build") == 4
          and [r.get("verdict") for r in vs] == ["reject", "reject", "accept", "accept"]
          and [(r.get("detail") or {}).get("part") for r in vs][2:] == [0, 1]
          and all(r.get("task") == TASK["id"] for r in w.writer.records())
          and "PART 1 of 2" in w.critic.seen[2]["prompt"] and "PART 2 of 2" in w.critic.seen[3]["prompt"]
          and TASK["criteria"] in w.critic.seen[3]["criteria"] and TASK["criteria"] not in w.critic.seen[2]["criteria"]
          and w.pubs()[0] == w.main_now())
    print("     B%s: out %s, verdicts %s" % (tag, out[-1][:60], [r.get("verdict") for r in vs]))
    return ok


def sc_split_parks(tmp, mod, tag):
    w = World(tmp, "BP" + tag, mod, simplifier=lambda p: SPLIT,
              critic=Critic(lambda k, c: "accept" if k == 3 else "reject"))
    out = w.run()
    ok = out[-1].startswith("parked") and w.calls.count("build") == 4 and not w.pubs() and len(parks(w)) == 1
    w.loop.state["task_i"] = 0                                  # a corrupt/rolled-back state: build_pass itself refuses
    try:
        w.loop.build_pass(w.loop.frozen())
        ok = False
    except RA.Refused as e:
        ok = ok and "no 5th" in str(e)
    print("     BP%s: out %s, builds %d" % (tag, out[-1][:60], w.calls.count("build")))
    return ok


def sc_capture(tmp, mod, tag):
    """ARENA_TESTER_SPEND_ENFORCE_METERED_HOME: the critic's transcripts (work/home, kept: trio's critic persists its
    session) are copied to the meter's helper store keyed by its test_start record before the work dir is deleted."""
    works = []

    def decide(k, c):
        works.append(Path(c.work))
        pj = Path(c.work) / "home" / ".claude" / "projects" / "-crit"
        pj.mkdir(parents=True, exist_ok=True)
        (pj / "s.jsonl").write_text('{"type": "assistant"}\n')
        (Path(c.work) / "gpt").mkdir(exist_ok=True)          # the real critic's RM_GPT_CALL_LOG dir
        (Path(c.work) / "gpt" / "g.jsonl").write_text("{}\n")
        return "accept"
    w = World(tmp, "CAP" + tag, mod, critic=Critic(decide))
    w.run()
    starts = w.recs("test_start")
    mans = [mod.RA.HC.load(r)[0] for r in starts]
    return (bool(starts) and len(works) == len(starts) and not any(x.exists() for x in works)
            and all(m and m["claude_files"] == ["-crit/s.jsonl"] and m["gpt_files"] == ["g.jsonl"]
                    and m["arm"] == mod.ARM for m in mans)
            and mod.default_critic().persist_sessions is True)


def sc_bound(tmp, mod, tag):
    """Accept at round 1: the published sha is the accepted sha, the critic saw that sha's tree."""
    w = World(tmp, "C" + tag, mod, critic=Critic(lambda k, c: "accept"))
    out = w.run()
    acc = [r for r in w.recs("critic_round", "verdict") if r.get("verdict") == "accept"]
    pub = w.pubs()
    ok = (out[-1].startswith("published") and len(acc) == 1 and len(pub) == 1 and acc[0]["sha"] == pub[0]
          and acc[0]["detail"]["tree"] == sh(w.root, "git", "rev-parse", pub[0] + "^{tree}")
          and w.critic.seen[0]["mod"].strip() == sh(w.root, "git", "show", pub[0] + ":mod.py")
          and acc[0]["detail"]["critic"] != acc[0]["detail"]["builder"])
    other = w.loop.binding_refusal(TASK, {"head": w.main0, "builder": "trio-build-x"})
    ok = ok and bool(other) and "bound to" in other
    print("     C%s: out %s, other-sha refusal %r" % (tag, out[-1][:60], (other or "")[:60]))
    return ok


def sc_bound_moved(tmp, mod, tag):
    """The work branch moves after the accept (during the final gate): STOP, nothing published, main untouched."""
    w = World(tmp, "CM" + tag, mod, critic=Critic(lambda k, c: "accept"))

    def hook(phase):
        if phase == "final":
            (w.root / "extra.py").write_text("x = 1\n")
            sh(w.root, "git", "add", "extra.py")
            sh(w.root, "git", "commit", "-q", "-m", "after the accept")
    w.gate_hook = hook
    out = w.run()
    ok = out[-1].startswith("STOP") and not w.pubs() and w.main_now() == w.main0 and (w.ctl / "STOP").exists()
    print("     CM%s: out %s" % (tag, out[-1][:90]))
    return ok


def sc_main_ahead(tmp, mod, tag):
    """Main already holds a descendant of the accepted sha: the ff-merge is a no-op, so nothing may publish."""
    w = World(tmp, "CF" + tag, mod, critic=Critic(lambda k, c: "accept"))

    def hook(phase):
        if phase == "final":
            head = w.loop.state["pending"]["head"]
            j = sh(w.root, "git", "commit-tree", head + "^{tree}", "-p", head, "-m", "not accepted")
            sh(w.root, "git", "branch", "-f", "main", j)
    w.gate_hook = hook
    out = w.run()
    ok = out[-1].startswith("STOP") and not w.pubs() and (w.ctl / "STOP").exists()
    print("     CF%s: out %s" % (tag, out[-1][:90]))
    return ok


def sc_killed_after_part_accept(tmp, mod, tag):
    """Killed after part 1's accept is logged, before state is saved: the restart builds part 2, not re-reviews."""
    def builder(prompt):
        return (GOOD + "# part 2\n", 0) if "PART 2 of 2" in prompt else (GOOD, 0)
    w = World(tmp, "H" + tag, mod, builder=builder, simplifier=lambda p: SPLIT,
              critic=Critic(lambda k, c: "reject" if k <= 2 else "accept"))
    real = w.loop._after_accept

    def die(task, pend, n):
        raise Killed()
    w.loop._after_accept = die
    try:
        w.run()
    except Killed:
        pass
    w.loop._after_accept = real
    w.reopen()                                                  # state.json still holds part 1's pending build
    out = w.run()
    pub = w.pubs()
    ok = (out[-1].startswith("published") and w.calls.count("build") == 4 and len(pub) == 1
          and "# part 2" in sh(w.root, "git", "show", pub[0] + ":mod.py")
          and "PART 2 of 2" in w.critic.seen[-1]["prompt"])
    print("     H%s: out %s, builds %d" % (tag, out[-1][:60], w.calls.count("build")))
    return ok


def sc_test_follows(tmp, mod, tag):
    """In a 4-round run every build_end is followed by a different-agent test_start of that build before the next
    build pass_start."""
    w = World(tmp, "D" + tag, mod)
    w.run()
    recs = w.writer.records()
    ok = w.calls.count("build") == 4
    for i, r in enumerate(recs):
        if r["event"] != "build_end":
            continue
        nxt = next((j for j in range(i + 1, len(recs)) if recs[j]["event"] == "pass_start"
                    and recs[j]["detail"].get("role") == "build"), len(recs))
        ts = [x for x in recs[i + 1:nxt] if x["event"] == "test_start"
              and x["detail"]["build_id"] == r["detail"]["build_id"]
              and RA.agent_key(x["detail"]["tester"]) != RA.agent_key(r["detail"]["builder"])]
        ok = ok and bool(ts)
    print("     D%s: build_ends %d" % (tag, sum(r["event"] == "build_end" for r in recs)))
    return ok


def sc_refuses_untested(tmp, mod, tag):
    """A trio build_end with no test_start (another item's) refuses the build pass before the builder runs."""
    w = World(tmp, "DU" + tag, mod)
    w.writer.emit(T.ARM, "build_end", lane="build", run_id="trio.x", task="OTHER", sha="a" * 40,
                  detail={"builder": "trio-build-zzz", "build_id": "OTHER.aaaa", "base": "b" * 40})
    try:
        w.loop.step()
        refused = False
    except RA.NotTested:
        refused = True
    print("     DU%s: refused %s, builds %d" % (tag, refused, w.calls.count("build")))
    return refused and w.calls.count("build") == 0


class Killed(BaseException):
    pass


def sc_killed_before_critic(tmp, mod, tag):
    w = World(tmp, "E" + tag, mod, critic=Critic(lambda k, c: "accept"))
    real = w.loop.tester_pass

    def die(task):
        raise Killed()
    w.loop.tester_pass = die
    try:
        w.loop.step()
    except Killed:
        pass
    w.loop.tester_pass = real
    w.reopen(drop_state=True)
    out = w.run(4)
    ok = out[-1].startswith("published") and w.calls.count("build") == 1 and len(w.critic.seen) == 1
    print("     E%s: out %s, builds %d" % (tag, out[-1][:70], w.calls.count("build")))
    return ok


class SigWriter(RA.ListWriter):
    """ListWriter whose records carry a sig, as the signed log's do (a void names its verdict by sig)."""
    def emit(self, arm, event, **kw):
        rec = super().emit(arm, event, **kw)
        rec["sig"] = "SIG%04d" % len(self.recs)
        return rec


def _swept_world(tmp, name, mod, critic=None, marker=True, writer=None, before_kill=None):
    """A trio world killed before its critic verdict, whose clone is then replaced as arena_replay_run.start_repair
    + a fresh clone leave it: only main, the pending head's objects pruned, a ready marker created after the build
    (marker=False: no marker). state.json still names the pending build. -> (world, pending head, head gone?)."""
    import arena_replay as R
    w = World(tmp, name, mod, critic=critic or Critic(lambda k, c: "accept"), writer=writer or SigWriter())
    real = w.loop.tester_pass

    def die(task):
        if before_kill:
            before_kill(w, task)
        raise Killed()
    w.loop.tester_pass = die
    try:
        w.loop.step()
    except Killed:
        pass
    w.loop.tester_pass = real
    head = json.loads((w.ctl / "state.json").read_text())["pending"]["head"]
    if sh(w.root, "git", "rev-parse", "--abbrev-ref", "HEAD") != "main":
        sh(w.root, "git", "switch", "-q", "main")
    sh(w.root, "git", "branch", "-f", RA.WIP, "main")                # the fresh clone: only main
    sh(w.root, "git", "reflog", "expire", "--expire=now", "--all")
    sh(w.root, "git", "gc", "-q", "--prune=now")
    if marker:
        R._write_marker(w.root, {"nonce": "0" * 32, "created": time.time() + 2, "arm": "trio", "task": TASK["id"],
                                 "pid": os.getpid(), "state": "ready"})
    gone = subprocess.run(["git", "cat-file", "-e", head + "^{commit}"], cwd=str(w.root)).returncode != 0
    w.reopen()                                                      # state.json kept: the stale pointer
    return w, head, gone


def _refused_kept(w, n=3):
    try:
        w.run(n)
    except RA.Refused as e:
        pend = json.loads((w.ctl / "state.json").read_text()).get("pending")
        return str(e), bool(pend) and not w.recs("invalid") and not w.recs("critic_round", "verdict")
    return None, False


def sc_swept_pending(tmp, mod, tag):
    """SW TRIO_RESUME_FIX_SWEEP_DELETES_PENDING_BUILD: killed before the critic, then the runner's start sweep
    replaces the clone (the pending head's commit is gone) while state.json still names it. The stale pending is
    dropped with ONE infra invalid verdict voided by the harness orphan void (no round spent); a fresh build is
    critic-reviewed and published."""
    w, head, gone = _swept_world(tmp, "SW" + tag, mod)
    out = w.run(5)
    vs = w.recs("critic_round", "verdict")
    ok = (gone and out[-1].startswith("published") and w.calls.count("build") == 2 and len(w.critic.seen) == 1
          and [r["verdict"] for r in vs] == ["invalid", "accept"]
          and (vs[0].get("detail") or {}).get("stage") == "infra" and vs[1].get("sha") != head
          and [(r.get("detail") or {}).get("void_verdict_sig") for r in w.recs("invalid")] == [vs[0]["sig"]]
          and [r["verdict"] for r in mod.verdicts(w.writer.records(), TASK["id"])] == ["accept"]
          and mod.rounds_used(w.writer.records(), TASK["id"]) == 1)
    print("     SW%s: gone %s, out %s, builds %d, verdicts %s" % (
        tag, gone, out[-1][:60], w.calls.count("build"), [r["verdict"] for r in vs]))
    return ok


def sc_swept_guards(tmp, mod, tag):
    """SWG the repair refuses (pending kept, no verdict, no void) when: a critic already answered in the round; the
    clone has no marker newer than the build (no evidence of a sweep); a git probe fails (never read as absence)."""
    def answer(w, task):                                           # a critic answered fail, killed before the verdict
        p = w.loop.state["pending"]
        w.loop.emit("test_start", task, sha=p["head"], detail={"tester": "trio-critic-x1", "build_id": p["build_id"],
                                                               "role": "critic"})
        w.loop.emit("test_end", task, sha=p["head"], verdict="fail", detail={"tester": "trio-critic-x1",
                                                                             "build_id": p["build_id"], "role": "critic"})
    w1, _, g1 = _swept_world(tmp, "SWa" + tag, mod, before_kill=answer)
    e1, k1 = _refused_kept(w1)
    w2, _, g2 = _swept_world(tmp, "SWm" + tag, mod, marker=False)
    e2, k2 = _refused_kept(w2)
    w3, _, g3 = _swept_world(tmp, "SWp" + tag, mod)
    w3.loop._commit_state = lambda sha: None
    e3, k3 = _refused_kept(w3)
    ok = (g1 and g2 and g3 and k1 and "critic answered" in (e1 or "") and k2 and "marker" in (e2 or "")
          and k3 and "probe failed" in (e3 or ""))
    print("     SWG%s: answered %s | no marker %s | probe %s" % (tag, (e1 or "-")[-70:], (e2 or "-")[-60:],
                                                                 (e3 or "-")[-50:]))
    return ok


class DieOnVoid(SigWriter):
    """Dies once on the first harness-void `invalid` append (after the infra verdict was written)."""
    armed = True

    def emit(self, arm, event, **kw):
        if event == "invalid" and self.armed:
            self.armed = False
            raise Killed()
        return super().emit(arm, event, **kw)


def sc_swept_crash_before_void(tmp, mod, tag):
    """SWC killed between the infra verdict and its void: the restart reuses that verdict and appends exactly one
    void (never a second verdict, never a NotTested wedge), then a fresh build publishes."""
    w, _, gone = _swept_world(tmp, "SWc" + tag, mod, writer=DieOnVoid())
    try:
        w.run(1)
    except Killed:
        pass
    w.reopen()
    out = w.run(5)
    vs = w.recs("critic_round", "verdict")
    ok = (gone and out[-1].startswith("published") and [r["verdict"] for r in vs] == ["invalid", "accept"]
          and len(w.recs("invalid")) == 1 and w.calls.count("build") == 2)
    print("     SWC%s: out %s, verdicts %s, voids %d" % (tag, out[-1][:50], [r["verdict"] for r in vs],
                                                         len(w.recs("invalid"))))
    return ok


def sc_invalid_critic(tmp, mod, tag):
    """A critic that never gives a verdict: 2 attempts per round, the round is spent, park after 4."""
    w = World(tmp, "F" + tag, mod, critic=Critic(lambda k, c: "invalid"))
    out = w.run()
    vs = w.recs("critic_round", "verdict")
    ok = (out[-1].startswith("parked") and w.calls.count("build") == 4 and len(w.critic.seen) == 8
          and [r["verdict"] for r in vs] == ["invalid"] * 4 and not w.pubs())
    print("     F%s: out %s, critic calls %d" % (tag, out[-1][:60], len(w.critic.seen)))
    return ok


class InfraCritic(Critic):
    """`decide(k, c)` -> "infra" gives the real L4 no-envelope failure shape (rc 1, stderr_tail), else a verdict."""
    def review(self, c):
        self.seen.append({"cid": c.cid})
        v = self.decide(len(self.seen), c)
        if v == "infra":
            return CC.CriticVerdict(verdict="invalid", reasons=["no JSON envelope from claude (rc 1)"],
                                    meta={"rc": 1, "stderr_tail": "sandbox: bind refused", "wall_s": 3.0})
        return CC.CriticVerdict(verdict=v, reasons=["fake critic says %s" % v], meta={"rc": 0})


def sc_infra_retry(tmp, mod, tag):
    """I1 two critic infra failures (rc 1, no envelope) then an accept: retried, never a verdict; one build, one
    accept, published; each failure is noted with its stderr."""
    waits = []
    w = World(tmp, "I1" + tag, mod, critic=InfraCritic(lambda k, c: "infra" if k <= 2 else "accept"),
              sleep=waits.append)
    out = w.run(6)
    vs = w.recs("critic_round", "verdict")
    notes = sorted((w.ctl / "log").glob("critic_infra.*.json"))
    ok = (out[-1].startswith("published") and w.calls.count("build") == 1 and len(w.critic.seen) == 3
          and [r["verdict"] for r in vs] == ["accept"] and len(notes) == 2 and len(waits) == 2
          and all("bind refused" in n.read_text() for n in notes)
          and sum(1 for r in w.recs("test_end") if (r.get("detail") or {}).get("infra")) == 2)
    print("     I1%s: out %s, critic calls %d, verdicts %s, notes %d" % (
        tag, out[-1][:50], len(w.critic.seen), [r["verdict"] for r in vs], len(notes)))
    return ok


def sc_infra_exhausted(tmp, mod, tag):
    """I2 the critic never runs: CRITIC_INFRA_TRIES attempts, then Refused with NO verdict and the build kept
    pending (no round spent by the infrastructure)."""
    w = World(tmp, "I2" + tag, mod, critic=InfraCritic(lambda k, c: "infra"), sleep=lambda s: None)
    refused = None
    try:
        w.run(6)
    except RA.Refused as e:
        refused = str(e)
    pend = json.loads((w.ctl / "state.json").read_text()).get("pending")
    ok = (refused is not None and "no verdict recorded" in refused and not w.recs("critic_round", "verdict")
          and len(w.critic.seen) == mod.CRITIC_INFRA_TRIES and bool(pend) and w.calls.count("build") == 1)
    print("     I2%s: refused %s, critic calls %d" % (tag, (refused or "")[:60], len(w.critic.seen)))
    return ok


def sc_logged_verdict_round(tmp, mod, tag):
    """I3 an earlier round's verdict of the same build_id is never reused as this round's (the rc 1 reread that
    burned round 2 of the real task)."""
    w = World(tmp, "I3" + tag, mod, critic=Critic(lambda k, c: "invalid"))
    w.run(1)                                            # build round 1, critic invalid x2 -> round 1 verdict
    vs = w.recs("critic_round", "verdict")
    if len(vs) != 1:
        return False
    d = vs[0]["detail"]
    t = w.loop.task()
    w.loop.emit("pass_start", t, detail={"role": "build"})                 # round 2 opens, same build_id pending
    pend = {"build_id": d["build_id"], "head": vs[0].get("sha"), "base": w.main0, "builder": "trio-build-x"}
    got = w.loop._logged_verdict(t, pend)
    print("     I3%s: logged verdict reused -> %r" % (tag, got and str(got)[:60]))
    return got is None and len(w.recs("critic_round", "verdict")) == 1


def _sign(w):
    for i, r in enumerate(w.writer.recs):
        r.setdefault("sig", "SIG%03d" % i)


def sc_void_round(tmp, mod, tag):
    """V an appended void of an infra reject drops its whole round: rounds and verdicts fall back by one, the voided
    round's pending build is dropped and the next step is a fresh build of that round (not simplify); a plain reject
    is never voidable. Round 2 is the real incident's shape: its critic never answered (infra only) and a legacy
    `critic INVALID (from the log)` reject was written for it."""
    w = World(tmp, "V" + tag, mod, critic=InfraCritic(lambda k, c: "reject" if k == 1 else "infra"),
              sleep=lambda s: None)
    try:
        w.run(2)                                        # round 1 a critic reject; round 2 infra x4 -> Refused
    except RA.Refused:
        pass
    tid = TASK["id"]
    if len(w.recs("critic_round", "verdict")) != 1 or not w.loop.state.get("pending"):
        print("     V%s: %d verdicts, pending %s" % (tag, len(w.recs("critic_round", "verdict")),
                                                     w.loop.state.get("pending")))
        return False
    w.loop._verdict(w.loop.task(), "reject", stage="build", why="fake critic says reject")   # the legacy reject
    vs = w.recs("critic_round", "verdict")
    _sign(w)
    plain = mod.void_refusal(w.writer.records(), tid, vs[1]["sig"])[0]     # a non-infra why: refused
    vs[1]["detail"]["why"] = "critic INVALID (from the log): no JSON envelope from claude (rc 1)"
    first = mod.void_refusal(w.writer.records(), tid, vs[0]["sig"])[0]     # not the latest: refused
    why, v = mod.void_refusal(w.writer.records(), tid, vs[1]["sig"])
    bes = [r for r in w.recs("build_end")]
    w.writer.emit(mod.ARM, "invalid", lane="build", run_id=mod.VOID_RUN_ID, task=tid, sha=v.get("sha"),
                  detail={"build_id": bes[-1]["detail"]["build_id"], "why": mod.VOID_WHY,
                          "void_verdict_sig": vs[1]["sig"], "reason": "infra reject", "evidence": ["x"]})
    _sign(w)
    recs = w.writer.records()
    again = mod.void_refusal(recs, tid, vs[1]["sig"])[0]
    r_used, n_v = mod.rounds_used(recs, tid), len(mod.verdicts(recs, tid))
    import arena_analysis as AN
    seq = [r for r in recs]
    voided = AN.harness_voided_builds(seq)
    b2 = max(i for i, r in enumerate(seq) if r["event"] == "build_end")
    w.reopen()
    be2 = seq[b2]                                       # killed before pending was cleared: the voided build pending
    w.loop.state["pending"] = {"build_id": be2["detail"]["build_id"], "base": be2["detail"].get("base"),
                               "head": be2.get("sha"), "builder": be2["detail"].get("builder")}
    w.loop._save()
    w.critic.decide = lambda k, c: "reject"
    w.loop.step()
    after = w.recs("critic_round", "simplify")
    recs = w.writer.records()
    r2, n2 = mod.rounds_used(recs, tid), len(mod.verdicts(recs, tid))
    ok = (plain is not None and first is not None and why is None and again is not None
          and r_used == 1 and n_v == 1 and b2 in voided and not after and w.calls.count("build") == 3
          and n2 <= r2 == 2)
    print("     V%s: plain %s / first %s / why %s / again %s, rounds %d verdicts %d, build2 voided %s, builds %d, "
          "after the step rounds %d verdicts %d" % (tag, bool(plain), bool(first), why, bool(again), r_used, n_v,
                                                    b2 in voided, w.calls.count("build"), r2, n2))
    return ok


def sc_void_guards(tmp, mod, tag):
    """VG a void is refused for a real reject whose prose names an infra mark (a critic answered in the round), and
    for a round followed by a park (a void cannot undo a terminal park)."""
    tid = TASK["id"]
    w = World(tmp, "VG" + tag, mod, critic=Critic(lambda k, c: "reject"), sleep=lambda s: None)
    w.run(1)
    _sign(w)
    vs = w.recs("critic_round", "verdict")
    if len(vs) != 1:
        return False
    vs[0]["detail"]["why"] = "no JSON envelope for invalid requests; the structured error response is absent"
    prose = mod.void_refusal(w.writer.records(), tid, vs[0]["sig"])[0]
    w3 = World(tmp, "VI" + tag, mod, critic=Critic(lambda k, c: "invalid"), sleep=lambda s: None)
    w3.run(1)                                           # two ANSWERED invalids (no infra) -> a real invalid verdict
    _sign(w3)
    v3 = w3.recs("critic_round", "verdict")
    if len(v3) != 1:
        return False
    v3[0]["detail"]["why"] = "critic infrastructure changes cannot be assessed: the migration contract is omitted"
    inval = mod.void_refusal(w3.writer.records(), tid, v3[0]["sig"])[0]
    w2 = World(tmp, "VP" + tag, mod, critic=Critic(lambda k, c: "invalid"), sleep=lambda s: None)
    w2.run(8)                                           # 4 answered invalid rounds -> parked
    _sign(w2)
    v2 = w2.recs("critic_round", "verdict")
    if not v2 or not w2.recs("critic_round", "park"):
        print("     VG%s: no park (%d verdicts)" % (tag, len(v2)))
        return False
    v2[-1]["detail"]["why"] = "no JSON envelope from claude (rc 1)"
    park = mod.void_refusal(w2.writer.records(), tid, v2[-1]["sig"])[0]
    print("     VG%s: prose -> %s / invalid -> %s / park -> %s" % (tag, (prose or "")[:50], (inval or "")[:50],
                                                               (park or "")[:50]))
    return (prose is not None and "answered" in prose and inval is not None and "answered" in inval
            and park is not None and "park" in park)


def sc_infra_recover(tmp, mod, tag):
    """IR infra retries exhausted, then the state's pending is lost: recovery from the log still restores the build
    (its infra attempts are no test), and the critic reviews it: no new build, no "killed" round, one accept."""
    w = World(tmp, "IR" + tag, mod, critic=InfraCritic(lambda k, c: "infra"), sleep=lambda s: None)
    try:
        w.run(6)
    except RA.Refused:
        pass
    w.critic.decide = lambda k, c: "accept"
    w.reopen()
    w.loop.state["pending"] = None
    w.loop._save()
    w.loop.step()
    vs = w.recs("critic_round", "verdict")
    print("     IR%s: builds %d, verdicts %s" % (tag, w.calls.count("build"), [(r["verdict"], (r.get("detail") or {})
                                                                               .get("stage")) for r in vs]))
    return w.calls.count("build") == 1 and [r["verdict"] for r in vs] == ["accept"]


def sc_infra_recover_repeat(tmp, mod, tag):
    """IR2 an unchanged build repeats round 1's (build_id, sha) in round 2 and its critic only ever fails on
    infrastructure; pending lost: recovery restores ROUND 2's build (not hidden by the repeated-build_end dedupe)
    and its critic runs: no simplify, no new build. A build_end repeated after the round's verdict recovers nothing."""
    w = World(tmp, "IR2" + tag, mod, critic=InfraCritic(lambda k, c: "reject" if k == 1 else "accept"),
              sleep=lambda s: None)
    w.run(1)                                            # round 1: build B, critic reject
    t = w.loop.task()
    be = w.recs("build_end")[-1]
    w.loop.emit("build_end", t, sha=be.get("sha"), detail=dict(be["detail"]))    # a repeat after the verdict
    w.loop.state["pending"] = None
    closed = w.loop._recover(t)
    w.loop.emit("pass_start", t, detail={"role": "build"})                       # round 2: the same build again
    w.loop.emit("build_end", t, sha=be.get("sha"), detail=dict(be["detail"]))
    for c in ("trio-critic-infra000001", "trio-critic-infra000002"):
        w.loop.emit("test_start", t, sha=be.get("sha"), detail={"tester": c, "build_id": be["detail"]["build_id"],
                                                                 "role": "critic"})
        w.loop.emit("test_end", t, sha=be.get("sha"), verdict="invalid", detail={
            "tester": c, "build_id": be["detail"]["build_id"], "role": "critic", "infra": "no JSON envelope (rc 1)"})
    w.loop._save()
    w.reopen()
    w.loop.step()
    vs = w.recs("critic_round", "verdict")
    print("     IR2%s: after-verdict repeat recovered %r; builds %d, simplify %s, verdicts %s" % (
        tag, closed, w.calls.count("build"), bool(w.recs("critic_round", "simplify")), [r["verdict"] for r in vs]))
    return (closed is None and w.calls.count("build") == 1 and not w.recs("critic_round", "simplify")
            and [r["verdict"] for r in vs] == ["reject", "accept"])


def sc_infra_mixed(tmp, mod, tag):
    """IX an answered invalid, then CRITIC_INFRA_TRIES infra failures -> Refused; on resume (pending kept, and again
    with pending lost) the answered invalid already spent stays spent: the NEXT answered invalid closes the round as
    invalid and the critic is never asked again (no unbounded critic attempts across restarts), with no new build.
    A critic killed mid-review (test_start, no test_end) is never recovered past: that round is spent, as before."""
    res = []
    for lose in (False, True):
        seq = ["invalid"] + ["infra"] * mod.CRITIC_INFRA_TRIES + ["invalid", "accept"]
        w = World(tmp, "IX%d%s" % (lose, tag), mod, critic=InfraCritic(lambda k, c: seq[min(k, len(seq)) - 1]),
                  sleep=lambda s: None)
        refused = False
        try:
            w.run(6)
        except RA.Refused:
            refused = True
        w.reopen()
        if lose:
            w.loop.state["pending"] = None
            w.loop._save()
        w.loop.step()
        vs = w.recs("critic_round", "verdict")
        res.append(refused and len(w.critic.seen) == mod.CRITIC_INFRA_TRIES + 2 and w.calls.count("build") == 1
                   and [r["verdict"] for r in vs] == ["invalid"])
        print("     IX%s lose=%s: refused %s, critic calls %d, builds %d, verdicts %s" % (
            tag, lose, refused, len(w.critic.seen), w.calls.count("build"), [r["verdict"] for r in vs]))
    w = World(tmp, "IK" + tag, mod, critic=InfraCritic(lambda k, c: "infra"), sleep=lambda s: None)
    try:
        w.run(6)
    except RA.Refused:
        pass
    t = w.loop.task()
    be = w.recs("build_end")[-1]                        # then a critic killed mid-review: test_start, no test_end
    w.loop.emit("test_start", t, sha=be.get("sha"), detail={"tester": "trio-critic-killed00001",
                                                             "build_id": be["detail"]["build_id"], "role": "critic"})
    w.loop.state["pending"] = None
    killed = w.loop._recover(t)
    print("     IX%s killed critic recovered %r" % (tag, killed))
    return all(res) and killed is None


def sc_logged_answer(tmp, mod, tag):
    """IL killed after a critic's test_end and before the round verdict, the build kept pending: the restart records
    the LOGGED answer (two answered invalids -> invalid; an answered reject -> reject) and never asks a new critic,
    so a crash cannot reroll an answer or exceed CRITIC_TRIES."""
    res = []
    for name, seq, want in (("inv", ["invalid"] + ["infra"] * mod.CRITIC_INFRA_TRIES + ["invalid", "accept"], "invalid"),
                            ("rej", ["reject", "accept"], "reject")):
        w = World(tmp, "IL%s%s" % (name, tag), mod, critic=InfraCritic(lambda k, c, q=seq: q[min(k, len(q)) - 1]),
                  sleep=lambda s: None)
        try:
            w.run(6) if name == "inv" else None
        except RA.Refused:
            pass
        if name == "inv":
            w.reopen()

        def boom(*a, **k):
            raise KeyboardInterrupt("killed before the round verdict")
        w.loop._verdict = boom
        try:
            w.loop.step() if name == "inv" else w.run(1)
        except KeyboardInterrupt:
            pass
        calls = len(w.critic.seen)
        w.reopen()
        w.loop.step()
        vs = w.recs("critic_round", "verdict")
        res.append(len(w.critic.seen) == calls and [r["verdict"] for r in vs] == [want]
                   and w.calls.count("build") == 1)
        print("     IL%s %s: critic calls %d -> %d, builds %d, verdicts %s" % (
            tag, name, calls, len(w.critic.seen), w.calls.count("build"), [r["verdict"] for r in vs]))
    return all(res)


def sc_infra_prose(tmp, mod, tag):
    """IP an ANSWERED invalid whose prose starts "no JSON envelope" is a verdict, never infrastructure."""
    class ProseCritic(Critic):
        def review(self, c):
            self.seen.append({"cid": c.cid})
            return CC.CriticVerdict(verdict="invalid", reasons=[
                "no JSON envelope is produced by the submitted endpoint; its contract cannot be assessed"],
                meta={"rc": 0, "is_error": False, "answer": "{}", "answer_tail": "{}"})
    w = World(tmp, "IP" + tag, mod, critic=ProseCritic(lambda k, c: "invalid"), sleep=lambda s: None)
    w.run(1)
    vs = w.recs("critic_round", "verdict")
    print("     IP%s: critic calls %d, verdicts %s" % (tag, len(w.critic.seen), [r["verdict"] for r in vs]))
    return (len(w.critic.seen) == 2 and [r["verdict"] for r in vs] == ["invalid"]
            and not any((r.get("detail") or {}).get("infra") for r in w.recs("test_end")))


def sc_infra_error_envelope(tmp, mod, tag):
    """IE an is_error envelope with rc 0 (arena_critic_calib's `claude error:` path) is infrastructure too."""
    class EnvCritic(Critic):
        def review(self, c):
            self.seen.append({"cid": c.cid})
            if len(self.seen) <= 2:
                return CC.CriticVerdict(verdict="invalid", reasons=["claude error: sandbox: bind refused"],
                                        meta={"rc": 0, "is_error": True})
            return CC.CriticVerdict(verdict="accept", reasons=["ok"], meta={"rc": 0})
    w = World(tmp, "IE" + tag, mod, critic=EnvCritic(lambda k, c: "accept"), sleep=lambda s: None)
    w.run(6)
    vs = w.recs("critic_round", "verdict")
    print("     IE%s: critic calls %d, verdicts %s" % (tag, len(w.critic.seen), [r["verdict"] for r in vs]))
    return len(w.critic.seen) == 3 and [r["verdict"] for r in vs] == ["accept"]


def sc_void_accept(tmp, mod, tag):
    """VA an accept is never voided, and a void naming an accept drops nothing."""
    w = World(tmp, "VA" + tag, mod, critic=Critic(lambda k, c: "accept"))
    w.run(4)
    _sign(w)
    vs = w.recs("critic_round", "verdict")
    tid = TASK["id"]
    if not vs:
        return False
    vs[-1].setdefault("detail", {})["why"] = "no JSON envelope from claude (rc 1)"   # only the accept rule refuses
    refused = mod.void_refusal(w.writer.records(), tid, vs[-1]["sig"])[0]
    w.writer.emit(mod.ARM, "invalid", lane="build", run_id=mod.VOID_RUN_ID, task=tid,
                  detail={"why": mod.VOID_WHY, "void_verdict_sig": vs[-1]["sig"], "reason": "r"})
    recs = w.writer.records()
    return refused is not None and "accept" in refused and len(mod.verdicts(recs, tid)) == len(vs)


def sc_simplify_root(tmp, mod, tag):
    """S the simplify work tree is made under the tester root (ext4), never inside ctl (drvfs), and removed."""
    cwds = []
    w = World(tmp, "S" + tag, mod, simplifier=lambda p: SIMPLE)
    real = w.model

    def model(role, prompt, *, cwd, **kw):
        if role != "build":
            cwds.append(Path(cwd))
        return real(role, prompt, cwd=cwd, **kw)
    w.loop.model = model
    w.run(5)
    ok = (bool(cwds) and all(not c.resolve().is_relative_to(w.ctl.resolve()) for c in cwds)
          and all(c.resolve().is_relative_to(Path(TBASE[0]).resolve()) for c in cwds)
          and not any(c.exists() for c in cwds) and not list(w.ctl.glob("trio-simplify-*")))
    print("     S%s: simplify cwds %s" % (tag, [str(c)[-40:] for c in cwds]))
    return ok


def sc_killed_build(tmp, mod, tag):
    """A builder killed every time (rc -9): no critic runs, each pass is a spent round, park after 4."""
    w = World(tmp, "FK" + tag, mod, builder=lambda p: (BROKEN, -9), simplifier=lambda p: SIMPLE)
    out = w.run()
    third = [p for r, p in w.prompts if r == "build"][2]
    vs = w.recs("critic_round", "verdict")
    ok = (out[-1].startswith("parked") and w.calls.count("build") == 4 and not w.critic.seen
          and [(r["verdict"], r["detail"].get("stage")) for r in vs] == [("reject", "build")] * 4
          and "abs of the difference" in third and TASK["id"] in third)
    print("     FK%s: out %s" % (tag, out[-1][:60]))
    return ok


def sc_parked_spec_lost(tmp, mod, tag):
    """Parked, then the specs dir and state.json are lost: the log says parked, so no spec is needed and no build runs."""
    w = World(tmp, "PL" + tag, mod)
    w.run()
    shutil.rmtree(w.ctl / "specs")
    (w.ctl / "specs").mkdir()
    w.reopen(drop_state=True)
    out = w.loop.step()
    print("     PL%s: %s" % (tag, out[:60]))
    return out.startswith("parked") and w.calls.count("build") == 4


def sc_park_once(tmp, mod, tag):
    """Killed after the parks.jsonl line, before the park record: the restart parks again but writes no second line."""
    w = World(tmp, "PO" + tag, mod)
    real = w.loop.emit

    def em(event, task, **kw):
        if event == "critic_round" and kw.get("verdict") == "park":
            raise Killed()
        return real(event, task, **kw)
    w.loop.emit = em
    try:
        w.run()
    except Killed:
        pass
    w.reopen(drop_state=True)
    w.run()
    print("     PO%s: park lines %d" % (tag, len(parks(w))))
    return len(parks(w)) == 1 and len(w.recs("critic_round", "park")) == 1 and w.calls.count("build") == 4


FAKE_RIMFLOW = """import json, os, sys
st = os.environ["FAKE_RF_STORE"]
have = json.load(open(st)) if os.path.exists(st) else {}
a = sys.argv[1:]
if os.path.exists(st + ".fail"):
    sys.exit(3)
if a[0] == "file":
    open(st + ".calls", "a").write("x")
if a[0] == "namecheck":     # like the real one: exit 0 for a free name too; only the word 'exists:' says it is taken
    print(a[1] + " exists: state proposed, owner X" if a[1] in have and not os.path.exists(st + ".blind") else "OK")
    sys.exit(0)
if a[0] == "show":
    x = have.get(a[1], [])      # like the real show: a history line carrying caused_by=<id> and a following field
    print(a[1], "history:", ("caused_by=%s for=BENCH" % x[x.index("--caused-by") + 1]) if "--caused-by" in x else "")
    sys.exit(0)
if a[0] == "note":
    open(st + ".notes", "a").write(" ".join(a))
    sys.exit(0)
have[a[1]] = a
json.dump(have, open(st, "w"))
print("filed")
"""


# A scenario that parks without fake_rimflow must never reach the real rimflow: sc_never_satisfied once filed the
# fixture TRIO_ABSDIFF_VET_PARKED into the live ledger (TRIO_ABSDIFF_VET_PARKED, closed as this leak).
RF_INERT = "%s -c \"raise SystemExit(3)\"" % shlex.quote(sys.executable)
LEDGER_SHARDS = Path(__file__).resolve().parents[4] / "infrastructure" / "state" / "ledger" / "events"


def real_ledger_mentions():
    """How many real ledger lines name the fixture's park item: a selftest run must not move this number."""
    return sum(f.read_bytes().count(b"TRIO_ABSDIFF_VET_PARKED") for f in sorted(LEDGER_SHARDS.glob("*.jsonl")))


def fake_rimflow(w, tmp):
    d = Path(tmp) / ("rf_" + w.ctl.parent.name + w.ctl.name)
    d.mkdir(parents=True, exist_ok=True)
    (d / "rf.py").write_text(FAKE_RIMFLOW)
    os.environ["TRIO_RIMFLOW_CMD"] = "%s %s" % (sys.executable, d / "rf.py")
    os.environ["FAKE_RF_STORE"] = str(d / "store.json")
    return d


def sc_park_files_item(tmp, mod, tag):
    """A park files one rimflow item for the Conductor (BENCH), caused by the task, naming the branch; a restart and a
    second park visit file nothing more; parks.jsonl is still written."""
    w = World(tmp, "PF" + tag, mod)
    d = fake_rimflow(w, tmp)
    (d / "store.json.blind").write_text("x")                    # the namecheck cannot see an existing item
    try:
        w.run()
        first = (d / "store.json").exists()                     # filed on the park itself, not only on a restart
        w.reopen(drop_state=True)
        w.run(4)
        w.loop.step()
        have = json.loads((d / "store.json").read_text()) if (d / "store.json").exists() else {}
        calls1 = len((d / "store.json.calls").read_text()) if (d / "store.json.calls").exists() else 0
        (w.ctl / "parks_filed.json").unlink()                   # marker lost: the existing item still counts as filed
        (d / "store.json.blind").unlink()
        w.reopen(drop_state=True)
        w.run(4)
        calls2 = len((d / "store.json.calls").read_text()) if (d / "store.json.calls").exists() else 0
    finally:
        os.environ["TRIO_RIMFLOW_CMD"] = RF_INERT
    a = next(iter(have.values()), [])
    notes = (d / "store.json.notes").read_text() if (d / "store.json.notes").exists() else ""   # verdict/why/sha/branch ride in a note
    print("     PF%s: items %s calls %s/%s" % (tag, list(have), calls1, calls2))
    return (first and calls1 == 1 and calls2 == 1 and list(have) == ["TRIO_ABSDIFF_VET_PARKED"] and len(parks(w)) == 1 and "BENCH" in a and "TRIO_ABSDIFF" in a
            and T.FAILED_BRANCH % TASK["id"] in notes and "reject" in notes and a[a.index("--caused-by") + 1] == "TRIO_ABSDIFF")


def sc_park_filing_fails(tmp, mod, tag):
    """rimflow failing (exit 3) or crashing loses no parks.jsonl line and does not stop the loop; the next visit files it."""
    w = World(tmp, "PX" + tag, mod)
    d = fake_rimflow(w, tmp)
    (d / "store.json.fail").write_text("x")
    try:
        out = w.run()
        pk1 = len(parks(w))
        os.environ["TRIO_RIMFLOW_CMD"] = str(d / "does_not_exist_binary")
        w.reopen(drop_state=True)
        out2 = w.run(4)                                         # a crashing launcher: swallowed too
        os.environ["TRIO_RIMFLOW_CMD"] = "%s %s" % (sys.executable, d / "rf.py")
        (d / "store.json.fail").unlink()
        w.reopen(drop_state=True)
        w.run(4)
        have = json.loads((d / "store.json").read_text()) if (d / "store.json").exists() else {}
    finally:
        os.environ["TRIO_RIMFLOW_CMD"] = RF_INERT
    print("     PX%s: out %s / %s items %s" % (tag, out[-1][:30], out2[-1][:30], list(have)))
    return (out[-1].startswith("parked") and pk1 == 1 and len(parks(w)) == 1 and list(have) == ["TRIO_ABSDIFF_VET_PARKED"]
            and len(w.recs("critic_round", "park")) == 1)


def sc_park_names(tmp, mod, tag):
    """Park item names pass the real namecheck shape: <=44 chars, <=7 words, no trailing number, long ids shortened and
    still distinct; and a plain name already held by an UNRELATED item is never adopted (a different park is filed under
    the hashed variant, once)."""
    import re
    ids = ["TRIO_ABSDIFF", "ARENA_TRIO_BUILD_CRITIC_ROUND_CAP_PARKS", "ARENA_TRIO_BUILD_CRITIC_ROUND_CAP_PARKX",
           "ARENA_DRILL_PROVE_KILLED_PASS_RECOVERS", "TRIO_PARKS_WIRE_CONDUCTOR_INBOX", "TRIO_ABSDIFF_2", "ARENA_TRIO_FIX_THE_BAR_NOW"]
    names = [mod.park_item_name(i) for i in ids]
    ok = all(len(n) <= 44 and len(n.split("_")) <= 7 and n.endswith("_VET_PARKED") and not n.split("_")[0].isdigit() for n in names)
    ok = ok and len(set(names[1:3])) == 2
    w = World(tmp, "PN" + tag, mod)
    d = fake_rimflow(w, tmp)
    (d / "store.json").write_text(json.dumps({"TRIO_ABSDIFF_VET_PARKED": ["file", "TRIO_ABSDIFF_VET_PARKED", "--caused-by", "OTHER_TASK_9"]}))
    try:
        w.run()
        w.reopen(drop_state=True)
        w.run(4)
        have = json.loads((d / "store.json").read_text())
    finally:
        os.environ["TRIO_RIMFLOW_CMD"] = RF_INERT
    mine = [n for n in have if n != "TRIO_ABSDIFF_VET_PARKED"]
    print("     PN%s: names %s items %s" % (tag, names, list(have)))
    return ok and mine == [mod.park_item_name("TRIO_ABSDIFF", force_hash=True)] and len(have) == 2


def sc_spec_tamper(tmp, mod, tag):
    w = World(tmp, "G" + tag, mod, simplifier=lambda p: SIMPLE)
    for _ in range(3):
        w.loop.step()
    f = w.ctl / "specs" / ("%s.json" % TASK["id"])
    f.write_text(f.read_text().replace("abs of the difference", "anything at all"))
    try:
        w.loop.step()
        return False
    except RA.Refused as e:
        print("     G%s: refused: %s" % (tag, str(e)[:80]))
        return "not the one the log recorded" in str(e)


# ---- live_plan (TRIO_FROZEN_TASKS_WIRE_LIVE_PLAN): a live task runs ITS frozen TestPilot plan or parks; never the proof
PLAN = {"scenarios": [{"id": "s1", "argv": ["python3", "proof_live.py", "--case", "a"],
                       "footprint": {"files": ["mod.py"], "defs": []}, "fail_rc": 1}], "fixture_save": "fx"}


class FakeLane:
    def __init__(self, verdict="pass"):
        self.published, self.verdict = [], verdict

    def publish(self, task, sha, builder, files):
        self.published.append((task.get("live_plan"), sha))

    def result(self, task, sha):
        return {"verdict": self.verdict, "run_id": "fake"} if self.published else None


def _live_park(tmp, mod, tag, name, task, want):
    lane = FakeLane()
    w = World(tmp, name + tag, mod, task=task, critic=Critic(lambda k, c: "accept"), lane=lane)
    sh(w.root, "git", "branch", T.RA.WIP)                       # a work branch left by an earlier task: not evidence
    fake_rimflow(w, tmp)
    try:
        out = w.run(6)
    finally:
        os.environ["TRIO_RIMFLOW_CMD"] = RF_INERT
    pk = parks(w)
    br = subprocess.run(["git", "rev-parse", "--verify", "-q", T.FAILED_BRANCH % task["id"]], cwd=str(w.root),
                        capture_output=True, text=True).stdout.strip()
    pr = w.recs("critic_round", "park")
    print("     %s%s: out %s, builds %d, published %d, why %r" % (name, tag, out[-1][:90], w.calls.count("build"),
                                                                 len(lane.published), (pk[0]["last_why"] if pk else "")[:90]))
    return (out[0].startswith("parked") and w.calls.count("build") == 0 and not lane.published and not w.pubs()
            and len(pk) == 1 and want in pk[0]["last_why"] and "live_plan" in pk[0]["last_why"]
            and pk[0]["rounds"] == 0 and pk[0]["evidence"] is None and not br
            and len(pr) == 1 and want in pr[0]["detail"]["why"])


def sc_live_no_plan(tmp, mod, tag):
    """A live task frozen with no live_plan key parks at once with a named reason: no build round, no publish."""
    return _live_park(tmp, mod, tag, "LN", dict(TASK, live="minimal"), "no live_plan field")


def sc_live_null_plan(tmp, mod, tag):
    return _live_park(tmp, mod, tag, "LZ", dict(TASK, live="minimal", live_plan=None), "live_plan null")


def sc_live_bad_plan(tmp, mod, tag):
    """A plan key TestPilot does not read (a guessed schema field) is refused, not ignored."""
    bad = {"scenarios": [{"id": "s1", "argv": ["sh", "-c", "x"], "timeout_s": 5}]}
    return _live_park(tmp, mod, tag, "LB", dict(TASK, live="minimal", live_plan=bad), "timeout_s")


def sc_live_plan_published(tmp, mod, tag):
    """A valid frozen plan is what reaches the lane (not the proof); a lane pass then publishes."""
    lane = FakeLane()
    task = dict(TASK, live="minimal", live_plan=PLAN)
    w = World(tmp, "LP" + tag, mod, task=task, critic=Critic(lambda k, c: "accept"), lane=lane)
    out = w.run()
    print("     LP%s: out %s, published %s" % (tag, out[-1][:60], [p[0] for p in lane.published]))
    return (out[-1].startswith("published") and len(lane.published) == 1 and lane.published[0][0] == PLAN
            and len(w.pubs()) == 1)


def sc_pilot_lane_no_fallback(tmp, mod, tag):
    """TestPilotLane.publish enqueues the frozen plan verbatim and refuses (Refused, nothing enqueued) a live task
    with no valid plan or an offline task: the proof is never wrapped into a stand-in scenario."""
    got = []

    class TP:
        @staticmethod
        def enqueue(p, item, sha, builder, plan, changed_files=None):
            got.append(plan)
    lane = mod.TestPilotLane.__new__(mod.TestPilotLane)
    lane.TP, lane.p = TP, {}
    refused = []
    for t in (dict(TASK, live="minimal"), dict(TASK, live="minimal", live_plan=None),
              dict(TASK, live="minimal", live_plan={"scenarios": []}), dict(TASK)):
        try:
            lane.publish(t, "a" * 40, "b", ["mod.py"])
        except mod.Refused as e:
            refused.append(str(e))
    n_bad = len(got)
    lane.publish(dict(TASK, live="minimal", live_plan=PLAN), "a" * 40, "b", ["mod.py"])
    print("     LT%s: refused %d of 4, enqueued %s" % (tag, len(refused), got))
    return len(refused) == 4 and n_bad == 0 and got == [PLAN] and all(TASK["id"] in r for r in refused)


MUTATIONS = [
    ("SW stale pending of a swept clone not dropped", sc_swept_pending,
     "        self._drop_lost_pending(task)\n", ""),
    ("SWG an answered critic does not stop the repair", sc_swept_guards,
     "        if answered:\n            refuse(", "        if False:\n            refuse("),
    ("SWC a closed infra round is not completed by the repair", sc_swept_crash_before_void,
     "            if not (v.get(\"verdict\") == \"invalid\" and", "            if True or not (v.get(\"verdict\") == \"invalid\" and"),
    ("A cap off by one", sc_never_satisfied, "ROUND_CAP = 4\n", "ROUND_CAP = 5\n"),
    ("A simplify trigger removed", sc_never_satisfied,
     "        if k >= SIMPLIFY_AFTER and simplify_rec(self.recs(), task[\"id\"]) is None:\n", "        if False:\n"),
    ("A park record not read on restart", sc_never_satisfied,
     "        if fz is not None and parked(self.recs(), fz[\"id\"]):", "        if False:"),
    ("R rounds from loop memory", sc_restart_counts,
     "    return sum(1 for r in _task_recs(recs, tid, \"pass_start\") if (r.get(\"detail\") or {}).get(\"role\") == "
     "\"build\")", "    return 0"),
    ("B parts do not advance", sc_split, "        while i in done:\n", "        while False:\n"),
    ("BP build-pass cap removed", sc_split_parks, "        if k >= ROUND_CAP:\n            raise Refused(",
     "        if False:\n            raise Refused("),
    ("C binding check skipped", sc_bound_moved, "        bad = self.binding_refusal(task, pend)\n",
     "        bad = None\n"),
    ("C accept not bound to its sha", sc_bound, "        if v.get(\"sha\") != head:\n", "        if False:\n"),
    ("CF main ahead of the accept published", sc_main_ahead, "        if now != pend[\"head\"]:", "        if False:"),
    ("H logged part accept ignored on restart", sc_killed_after_part_accept,
     "        done = self._logged_verdict(task, pend)\n", "        done = None\n"),
    ("D require_tested removed", sc_refuses_untested,
     "        require_tested(self.recs())                                # HARD CHECK (trio records)",
     "        pass"),
    ("D critic test_start skipped", sc_test_follows,
     "                rec = self.emit(\"test_start\", task, sha=pend[\"head\"], detail={",
     "                rec = dict(sha=pend[\"head\"], detail={"),
    ("A2 critic capture skipped", sc_capture, "                RA.capture_tester(rec, work,",
     "                (lambda *a, **k: None)(rec, work,"),
    ("A2 critic GPT log not captured", sc_capture, "(rec, work, (getattr(v, \"meta\", None) or {}).get(\"rc\"))",
     "(rec, work, (getattr(v, \"meta\", None) or {}).get(\"rc\"), gpt=False)"),
    ("A2 critic sessions not persisted", sc_capture, "CC.L4OpusCritic(persist_sessions=True)", "CC.L4OpusCritic()"),
    ("E recovery from the log removed", sc_killed_before_critic, "        self._recover(task)\n", "        pass\n"),
    ("F invalid counted as accept", sc_invalid_critic,
     "verdict = verdict if verdict in (\"accept\", \"reject\") else \"invalid\"",
     "verdict = verdict if verdict in (\"accept\", \"reject\") else \"accept\""),
    ("FK killed pass not a round", sc_killed_build,
     "        if self._round_open(task[\"id\"]):                           # a build-side failure ends the round\n"
     "            self._verdict(", "        if False:\n            self._verdict("),
    ("PL parked check after the spec load", sc_parked_spec_lost,
     "        fz = self.frozen()\n        if fz is not None and parked(", "        fz = self.frozen()\n        task = self.task()\n        if fz is not None and parked("),
    ("PF free name (namecheck exit 0) never filed", sc_park_files_item, "            if \" exists:\" not in have.stdout:",
     "            if have.returncode != 0 and \" exists:\" not in have.stdout:"),
    ("PN long name over the word cap", sc_park_names, "or len(words) > 5 ", ""),
    ("PN unrelated item adopted", sc_park_names, "(\"caused_by=%s \" % tid) not in self._rimflow(\"show\", name).stdout", "False"),
    ("PO park line written twice", sc_park_once, "        if not any(json.loads(x).get(\"task\") == tid for x in have if x.strip()):",
     "        if True:"),
    ("PF filing not remembered", sc_park_files_item, "            if tid in done:\n                return done[tid]\n",
     "            pass\n"),
    ("PF existing item not recognised", sc_park_files_item, "\" exists:\" not in have.stdout", "\" exists:\" in have.stdout"),
    ("PF item not filed at all", sc_park_files_item, "        self._file_park_item(tid)\n        return self._advance(task, \"parked",
     "        return self._advance(task, \"parked"),
    ("PX filing failure not contained", sc_park_filing_fails, "        except Exception as e:  # noqa: BLE001  a filing",
     "        except KeyboardInterrupt as e:  # noqa: BLE001  a filing"),
    ("PX failed filing not retried from the log", sc_park_filing_fails,
     "            self._file_park_item(fz[\"id\"])                       # a filing", "            pass                                                 # a filing"),
    ("LN live task without a plan builds anyway", sc_live_no_plan,
     "        bad = live_plan_refusal(task)\n        if bad and not", "        bad = None\n        if bad and not"),
    ("LT proof fallback restored in TestPilotLane.publish", sc_pilot_lane_no_fallback,
     "        if bad or task.get(\"live\", \"none\") == \"none\":\n            raise Refused(\"refused: %s not published",
     "        if False:\n            raise Refused(\"refused: %s not published"),
    ("LN park keeps an evidence branch with no round", sc_live_no_plan,
     "self.git(\"rev-parse\", \"--verify\", \"-q\", RA.WIP, check=False) if k else None",
     "self.git(\"rev-parse\", \"--verify\", \"-q\", RA.WIP, check=False)"),
    ("I1 critic infra failure counted as a verdict", sc_infra_retry,
     "            inf = critic_infra(v) if verdict == \"invalid\" else None\n", "            inf = None\n"),
    ("I2 exhausted infra retries record a verdict", sc_infra_exhausted,
     "            inf = critic_infra(v) if verdict == \"invalid\" else None\n", "            inf = None\n"),
    ("I3 an earlier round's verdict reused", sc_logged_verdict_round,
     "                and (v.get(\"detail\") or {}).get(\"round\", k) == k]", "]"),
    ("V void not honoured by round counting", sc_void_round, "    drop = _void_spans(seq)\n    for i, r in enumerate(seq):\n",
     "    drop = set()\n    for i, r in enumerate(seq):\n"),
    ("V a non-infra reject voidable", sc_void_round, "    if not any(why.startswith(m) for m in INFRA_WHY_MARKS):",
     "    if False:"),
    ("V a voided round's pending build reviewed", sc_void_round,
     "        if pend and voided_build(self.recs(), task[\"id\"], pend.get(\"build_id\")):", "        if False:"),
    ("VG an answered reject voidable through its prose", sc_void_guards, "    if answered:\n        return \"verdict %s: a critic answered",
     "    if False:\n        return \"verdict %s: a critic answered"),
    ("VG a void after a park allowed", sc_void_guards,
     "    later = [r for r in seq[i + 1:] if r.get(\"event\") == \"critic_round\" and L.norm_id(r.get(\"task\")) == t]",
     "    later = [r for r in seq[i + 1:] if r.get(\"event\") == \"critic_round\" and L.norm_id(r.get(\"task\")) == t\n"
     "             and (r.get(\"detail\") or {}).get(\"kind\") in (\"verdict\", \"simplify\")]"),
    ("IR infra attempts block log recovery", sc_infra_recover,
     "        ends = [r for r in tests if r.get(\"event\") == \"test_end\" and not (r.get(\"detail\") or {}).get(\"infra\")]",
     "        ends = [r for r in tests if r.get(\"event\") == \"test_end\"]"),
    ("IE an is_error envelope is a verdict", sc_infra_error_envelope, "    if meta.get(\"is_error\"):", "    if False:"),
    ("IR2 recovery over the deduped log", sc_infra_recover_repeat,
     "    seq = [r for i, r in enumerate(seq) if i not in drop]\n    t = L.norm_id(tid)\n",
     "    seq = L.ordered(canon_records(recs))\n    t = L.norm_id(tid)\n"),
    ("IR2 a closed round recovered", sc_infra_recover_repeat,
     "        if not self._round_open(task[\"id\"]):               # the round has its verdict", "        if False:  # the round has its verdict"),
    ("IX infra exhaustion resets the answered-invalid budget", sc_infra_mixed,
     "        tries, infra = len(answered), 0\n", "        tries, infra = 0, 0\n"),
    ("IX an earlier answered invalid vetoes log recovery", sc_infra_mixed,
     "        if any(r.get(\"verdict\") in (\"pass\", \"fail\") for r in ends) or len(ends) >= CRITIC_TRIES or any(",
     "        if ends or any("),
    ("IX a critic killed mid-review recovered past", sc_infra_mixed,
     "        if any(r.get(\"verdict\") in (\"pass\", \"fail\") for r in ends) or len(ends) >= CRITIC_TRIES or any(",
     "        if any(r.get(\"verdict\") in (\"pass\", \"fail\") for r in ends) or len(ends) >= CRITIC_TRIES or False and any("),
    ("IL a logged answer rerolled after a kill", sc_logged_answer,
     "        logged = final is not None or tries >= CRITIC_TRIES\n", "        logged = False\n"),
    ("IP an answered invalid read as infra", sc_infra_prose,
     "    if \"stderr_tail\" in meta:", "    if \"stderr_tail\" in meta or \"no JSON envelope\" in str(getattr(v, \"reasons\", \"\")):"),
    ("VA an accept voidable", sc_void_accept,
     "    if v.get(\"verdict\") == \"accept\":\n        return \"verdict %s is an accept", "    if False:\n        return \"verdict %s is an accept"),
    ("VA a void drops an accept's round", sc_void_accept,
     "and (r.get(\"detail\") or {}).get(\"kind\") == \"verdict\" and r.get(\"verdict\") != \"accept\" and r.get(\"sig\")}",
     "and (r.get(\"detail\") or {}).get(\"kind\") == \"verdict\" and r.get(\"sig\")}"),
    ("S simplify tree back on ctl (drvfs)", sc_simplify_root, "        troot = self._tester_root()\n",
     "        troot = Path(tempfile.mkdtemp(prefix=\"trio-simplify-\", dir=str(self.ctl)))\n"),
    ("G spec integrity check removed", sc_spec_tamper,
     "            if not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest() != want:",
     "            if False:"),
]

SCENARIOS = [
    ("SW a pending build swept with its clone is dropped as a harness-voided infra round", sc_swept_pending),
    ("SWG the swept-pending repair refuses on an answered critic, no sweep evidence, a failed probe", sc_swept_guards),
    ("SWC killed between the infra verdict and its void: restart completes it once", sc_swept_crash_before_void),
    ("A never satisfied: simplify after 2, park after 4, never a 5th", sc_never_satisfied),
    ("R round count survives a restart with state.json lost", sc_restart_counts),
    ("B split: parts share the budget; the last part publishes once", sc_split),
    ("BP a split that keeps failing parks at 4", sc_split_parks),
    ("C the accept is bound to the published sha and tree", sc_bound),
    ("A2 critic spend captured before its work dir is deleted", sc_capture),
    ("C a work branch moved after the accept is not published", sc_bound_moved),
    ("CF main already past the accepted sha: nothing published", sc_main_ahead),
    ("H killed after a part's accept: the restart builds the next part", sc_killed_after_part_accept),
    ("D a different-agent test_start follows every build_end", sc_test_follows),
    ("D a build pass is refused while a trio build is untested", sc_refuses_untested),
    ("E killed between build_end and the critic: the restart runs the critic", sc_killed_before_critic),
    ("F a critic with no verdict spends the round", sc_invalid_critic),
    ("FK a killed build pass spends the round; the simplified spec reaches round 3", sc_killed_build),
    ("I1 critic infra failures retry and are never a verdict", sc_infra_retry),
    ("I2 exhausted critic infra retries refuse with no verdict, build kept pending", sc_infra_exhausted),
    ("I3 an earlier round's verdict of the same build is never reused", sc_logged_verdict_round),
    ("V an appended infra-reject void drops its round; rounds and verdicts honour it", sc_void_round),
    ("VA an accept is never voided", sc_void_accept),
    ("VG a void refuses an answered reject (prose marks) and a parked round", sc_void_guards),
    ("IR log recovery restores a build whose critic attempts were all infra", sc_infra_recover),
    ("IE an is_error envelope (rc 0) retries as infrastructure", sc_infra_error_envelope),
    ("IR2 recovery finds round 2's repeated build and runs its critic", sc_infra_recover_repeat),
    ("IX answered invalids spent before an infra Refused stay spent; a killed critic is not recovered", sc_infra_mixed),
    ("IL a critic answer logged before a kill is recorded, never rerolled", sc_logged_answer),
    ("IP an answered invalid is a verdict whatever its prose", sc_infra_prose),
    ("S the simplify work tree is on the tester root, not ctl, and removed", sc_simplify_root),
    ("PL a parked item with its spec file lost still advances", sc_parked_spec_lost),
    ("PF a park files one Conductor item, once", sc_park_files_item),
    ("PX a failed or crashing filing loses nothing and is retried", sc_park_filing_fails),
    ("PN park item names are valid and never adopt an unrelated item", sc_park_names),
    ("PO a killed park writes one parks.jsonl line", sc_park_once),
    ("G a tampered simplified spec refuses", sc_spec_tamper),
    ("LN a live task with no live_plan key parks before any round, named reason", sc_live_no_plan),
    ("LZ a live task with live_plan null parks, named reason", sc_live_null_plan),
    ("LB a live_plan with a key TestPilot does not read parks", sc_live_bad_plan),
    ("LP a valid frozen live_plan reaches the lane verbatim", sc_live_plan_published),
    ("LT TestPilotLane.publish never substitutes the proof", sc_pilot_lane_no_fallback),
]


def t_parse_simplify():
    p = T.parse_simplify
    check(p(SPLIT)["action"] == "split" and len(p(SPLIT)["parts"]) == 2, "parse: a split of 2 parts")
    check(p(SIMPLE)["spec"]["criteria"] == "c2", "parse: a simplify")
    four = '{"action": "split", "parts": [%s]}' % ", ".join(['{"prompt": "p", "criteria": "c"}'] * 4)
    check(p(four) is None and p('{"action": "split", "parts": [{"prompt": "p", "criteria": "c"}]}') is None,
          "parse: 1 or 4 parts refused")
    check(p('{"action": "simplify", "spec": {"prompt": "p", "criteria": "", "id": "X"}}') is None,
          "parse: empty criteria refused")
    check(p('{"action": "simplify", "spec": {"prompt": "p", "criteria": "c", "id": "X", "priority": "P9"}}')
          ["spec"] == {"prompt": "p", "criteria": "c"}, "parse: id/priority in the spec are dropped")
    check(p("no json here") is None and p('{"action": "simplify", "spec": ') is None, "parse: garbage refused")


def main():
    tmp = Path(tempfile.mkdtemp(prefix="selftest_trio_"))
    os.environ["ARENA_METER_HELPERS"] = str(tmp / "meter_helpers")      # tester captures: not the live arena root
    TBASE[0] = Path(tempfile.mkdtemp(prefix="selftest_trio_rt_"))
    saved = os.environ.pop("RM_ARM", None)
    os.environ["TRIO_RIMFLOW_CMD"] = RF_INERT
    ledger0 = real_ledger_mentions()
    check(ledger0 > 0, "the real-ledger probe can see the shards")
    try:
        t_parse_simplify()
        for name, fn in SCENARIOS:
            check(guarded(fn, tmp, T, ""), name)
        for i, (name, fn, old, new) in enumerate(MUTATIONS):
            m = variant(old, new)
            check(not guarded(fn, tmp, m, ".m%d" % i), "RED with the fix reverted: " + name)
        import arena_analysis as AN
        check(T.VOID_WHY == AN.HARNESS_ORPHAN_VOID_WHY and
              AN.stream_of("trio.3") + AN.HARNESS_VOID_STREAM_SUFFIX == T.VOID_RUN_ID,
              "the trio void is the one harness void arena_analysis.dq_tester honours")
        check("trio_loop.py" in __import__("arena_eventlog").ENTRYPOINTS, "trio_loop.py is a harness entrypoint")
        check(real_ledger_mentions() == ledger0, "no scenario wrote the fixture park into the real ledger")
    finally:
        os.environ.pop("TRIO_RIMFLOW_CMD", None)
        if saved is not None:
            os.environ["RM_ARM"] = saved
        shutil.rmtree(tmp, ignore_errors=True)
        shutil.rmtree(TBASE[0], ignore_errors=True)
    print("RESULT: %s (%d failure(s))" % ("GREEN" if not FAILS else "RED", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
