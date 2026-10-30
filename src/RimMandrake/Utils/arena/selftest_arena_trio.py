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
"""
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


def sc_invalid_critic(tmp, mod, tag):
    """A critic that never gives a verdict: 2 attempts per round, the round is spent, park after 4."""
    w = World(tmp, "F" + tag, mod, critic=Critic(lambda k, c: "invalid"))
    out = w.run()
    vs = w.recs("critic_round", "verdict")
    ok = (out[-1].startswith("parked") and w.calls.count("build") == 4 and len(w.critic.seen) == 8
          and [r["verdict"] for r in vs] == ["invalid"] * 4 and not w.pubs())
    print("     F%s: out %s, critic calls %d" % (tag, out[-1][:60], len(w.critic.seen)))
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


MUTATIONS = [
    ("A cap off by one", sc_never_satisfied, "ROUND_CAP = 4\n", "ROUND_CAP = 5\n"),
    ("A simplify trigger removed", sc_never_satisfied,
     "        if k >= SIMPLIFY_AFTER and simplify_rec(self.recs(), task[\"id\"]) is None:\n", "        if False:\n"),
    ("A park record not read on restart", sc_never_satisfied,
     "        if parked(self.recs(), task[\"id\"]):", "        if False:"),
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
     "                self.emit(\"test_start\", task, sha=pend[\"head\"], detail={",
     "                dict(sha=pend[\"head\"], detail={"),
    ("E recovery from the log removed", sc_killed_before_critic, "        self._recover(task)\n", "        pass\n"),
    ("F invalid counted as accept", sc_invalid_critic,
     "verdict = verdict if verdict in (\"accept\", \"reject\") else \"invalid\"",
     "verdict = verdict if verdict in (\"accept\", \"reject\") else \"accept\""),
    ("FK killed pass not a round", sc_killed_build,
     "        if self._round_open(task[\"id\"]):                           # a build-side failure ends the round\n"
     "            self._verdict(", "        if False:\n            self._verdict("),
    ("G spec integrity check removed", sc_spec_tamper,
     "            if not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest() != want:",
     "            if False:"),
]

SCENARIOS = [
    ("A never satisfied: simplify after 2, park after 4, never a 5th", sc_never_satisfied),
    ("R round count survives a restart with state.json lost", sc_restart_counts),
    ("B split: parts share the budget; the last part publishes once", sc_split),
    ("BP a split that keeps failing parks at 4", sc_split_parks),
    ("C the accept is bound to the published sha and tree", sc_bound),
    ("C a work branch moved after the accept is not published", sc_bound_moved),
    ("CF main already past the accepted sha: nothing published", sc_main_ahead),
    ("H killed after a part's accept: the restart builds the next part", sc_killed_after_part_accept),
    ("D a different-agent test_start follows every build_end", sc_test_follows),
    ("D a build pass is refused while a trio build is untested", sc_refuses_untested),
    ("E killed between build_end and the critic: the restart runs the critic", sc_killed_before_critic),
    ("F a critic with no verdict spends the round", sc_invalid_critic),
    ("FK a killed build pass spends the round; the simplified spec reaches round 3", sc_killed_build),
    ("G a tampered simplified spec refuses", sc_spec_tamper),
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
    TBASE[0] = Path(tempfile.mkdtemp(prefix="selftest_trio_rt_"))
    saved = os.environ.pop("RM_ARM", None)
    try:
        t_parse_simplify()
        for name, fn in SCENARIOS:
            check(guarded(fn, tmp, T, ""), name)
        for i, (name, fn, old, new) in enumerate(MUTATIONS):
            m = variant(old, new)
            check(not guarded(fn, tmp, m, ".m%d" % i), "RED with the fix reverted: " + name)
        check("trio_loop.py" in __import__("arena_eventlog").ENTRYPOINTS, "trio_loop.py is a harness entrypoint")
    finally:
        if saved is not None:
            os.environ["RM_ARM"] = saved
        shutil.rmtree(tmp, ignore_errors=True)
        shutil.rmtree(TBASE[0], ignore_errors=True)
    print("RESULT: %s (%d failure(s))" % ("GREEN" if not FAILS else "RED", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
