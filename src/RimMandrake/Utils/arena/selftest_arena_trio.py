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
        os.environ.pop("TRIO_RIMFLOW_CMD", None)
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
        os.environ.pop("TRIO_RIMFLOW_CMD", None)
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
        os.environ.pop("TRIO_RIMFLOW_CMD", None)
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
        os.environ.pop("TRIO_RIMFLOW_CMD", None)
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
     "                self.emit(\"test_start\", task, sha=pend[\"head\"], detail={",
     "                dict(sha=pend[\"head\"], detail={"),
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
