#!/usr/bin/env python3
"""selftest_arena_ralph_c.py - ralph_c_loop.py (ARENA_RALPHC_BUILD_BUILDERS_WAIT_ON_TESTERS), offline.

No real model, gate, seat, bridge, game or systemd. Builders and testers are fake callables, the gate is a fake that
always says scope PASS (so any area refusal seen is the LOOP's guard, not the gate's), each member's clone is a temp
git repo, and the runner queue is the REAL ralph_c_runner queue under a temp ARENA_ROOT; the stub runner writes its
result with ralph_c_runner.record_result.

Forced failures (each scenario green on the real loop, RED on a copy with the guarding line mutated away):
  P1 a STOLEN item's out-of-area edit is refused before the gate, not published, the refusal feeds the next pass,
     which stays in the area and is published.                              mutation: area guard removed
  P2 a builder whose live candidate waits for a runner gets no new live item (from its loop, and from the board
     even with the loop's state lost, read from the runner queue); it gets one once the runner has a verdict.
                                                                             mutation: runner-queue check removed
  P3 per loop: a build_end without a different-agent test_start refuses THAT loop's next build pass (no model call),
     and does not block the other loop.                                     mutation: require_tested removed
  P4 steal only when the member's own list is empty.                        mutation: steal-first
  P5 two loops on one board: every build_end is followed by a different-agent test_start before that loop's next
     build pass; no task held by both; both publish.
  plus: area map overlap / homeless / two-home tasks refused, STOP.ralph_c and the status file arena.py reads,
  the ralph_c build prompt, CmdModelC's child env, runner_loop STOP and status, the signed writer.
"""
from __future__ import annotations

import json
import os
import re
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
import ralph_a_loop as RA  # noqa: E402
import ralph_c_loop as C  # noqa: E402
import ralph_c_runner as RC  # noqa: E402
import arena_safe_git_traps as T  # noqa: E402

FAILS = []
SRC = (HERE / "ralph_c_loop.py").read_text()
MA, MB = "src/RimMandrake/ModA", "src/RimMandrake/ModB"
AREAS = {"a1": [MA + "/**"], "a2": [MB + "/**"]}


SKIPS = []


def check(ok, msg):
    print(("ok   " if ok else "FAIL ") + msg)
    if not ok:
        FAILS.append(msg)


def variant(old=None, new=None):
    if old is None:
        return C
    assert SRC.count(old) == 1, "mutation anchor not unique/absent: %r" % old
    m = types.ModuleType("ralph_c_loop_mut")
    m.__file__ = str(HERE / "ralph_c_loop.py")
    exec(compile(SRC.replace(old, new), m.__file__, "exec"), m.__dict__)
    return m


def sh(cwd, *a):
    return subprocess.run(list(a), cwd=str(cwd), capture_output=True, text=True, check=True).stdout.strip()


def task(tid, mod, live="none", **kw):
    t = {"id": tid, "kind": "code", "size": "S", "area": [mod + "/**"], "live": live, "base_sha": "",
         "prompt": "write %s" % tid, "criteria": "c", "proof": "python3 -c 'pass'"}
    t.update(kw)
    return t


def new_clone(d):
    d.mkdir(parents=True)
    sh(d, "git", "init", "-q", "-b", "main")
    sh(d, "git", "config", "user.email", "t@t")
    sh(d, "git", "config", "user.name", "t")
    (d / "README").write_text("arm\n")
    sh(d, "git", "add", "README")
    sh(d, "git", "commit", "-q", "-m", "init")
    return d


class Arena:
    """One temp arena: board, runner queue, shared writer, and one member World per loop."""

    def __init__(self, tmp, name, tasks, mod=C, writer=None):
        self.d = tmp / name
        self.aroot = self.d / "arena"
        os.environ["ARENA_ROOT"] = str(self.aroot)
        self.mod = mod
        self.rp = RC.rpaths()
        self.writer = writer or RA.ListWriter()
        self.board = mod.Board(self.rp["rc"] / "board.json", tasks, mod.load_areas(AREAS),
                               runner_pending=lambda: RC.pending(self.rp))
        self.calls = []                                  # (member, role, agent_id)
        self.status_seen = []

    def world(self, member, builder, tester=None, ctl=None):
        return World(self, member, builder, tester, ctl)

    def runner_verdict(self, item, verdict="pass"):
        """The stub runner: one counted result for the item's current candidate, green canary."""
        cur = RC.current(self.rp)[item]
        return RC.record_result(self.rp, {"run_id": "stub-%s-%s" % (item, cur["cand"]), "item": item,
                                          "sha": cur["sha"], "cand": cur["cand"], "verdict": verdict,
                                          "canary": {"ok": True}, "lane": "steve"})


class World:
    def __init__(self, arena, member, builder, tester, ctl):
        self.a, self.member = arena, member
        self.root = new_clone(arena.d / ("clone_" + member)) if not (arena.d / ("clone_" + member)).exists() \
            else arena.d / ("clone_" + member)
        self.ctl = arena.d / (ctl or ("ctl_" + member))
        self.builder = builder                           # (prompt, task_id) -> ({path: text}, rc)
        self.tester = tester or (lambda prompt, cwd: "VERDICT: FAIL" if "BAD" in prompt else "VERDICT: PASS")
        self.publog = arena.d / ("published_%s.txt" % member)
        pub = arena.d / "pub.py"
        pub.write_text("import subprocess,sys\nopen(sys.argv[1],'a').write(subprocess.run(['git','rev-parse',"
                       "'HEAD'],capture_output=True,text=True).stdout)\n")
        self.prompts = []
        self.loop = arena.mod.LoopC(member, self.root, self.ctl, arena.board, arena=arena.aroot, model=self.model,
                                    gate=self.gate, writer=arena.writer, lane=RA.RalphCLane(), sync=None, tester_tmp=str(arena.d / ('tt_' + member)),
                                    runway=lambda: {"state": "MEASURED", "runway": 0.9},
                                    precheck=lambda log: True, release=lambda: None,
                                    publish_cmd="%s %s %s" % (sys.executable, pub, self.publog))

    def model(self, role, prompt, *, cwd, agent_id, run_id, timeout_s, log, sandbox=None):
        self.a.calls.append((self.member, role, agent_id))
        self.prompts.append((role, prompt))
        st = self.a.aroot / "status" / "ralph_c.json"
        self.a.status_seen.append(json.loads(st.read_text())["state"] if st.exists() else None)
        if role == "build":
            files, rc = self.builder(prompt, self.loop.task()["id"])
            for path, text in files.items():
                f = Path(cwd) / path
                if text is None:                         # None = delete the file
                    sh(cwd, "git", "rm", "-q", path)
                    continue
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text(text)
                sh(cwd, "git", "add", path)
            if files:
                sh(cwd, "git", "commit", "-q", "-m", "build %s" % agent_id)
            return {"rc": rc, "text": "BUILDER-TRANSCRIPT"}
        return {"rc": 0, "text": self.tester(prompt, Path(cwd))}

    def gate(self, task, base, head, phase, log):
        recs = self.a.writer.records()
        builders = {(r.get("detail") or {}).get("builder") for r in recs if r["event"] == "build_end"
                    and r.get("sha") == head}
        tested = any(r["event"] == "test_end" and r.get("sha") == head and r.get("verdict") == "pass"
                     and (r.get("detail") or {}).get("tester") not in builders for r in recs)
        live_ok = task.get("live", "none") == "none" or phase == "build" or self._lane_ok(task, head)
        steps = {"scope": "PASS", "placeholders": "PASS", "tests": "PASS",
                 "live": "PASS" if live_ok else "FAIL", "test_record": "PASS" if tested else "FAIL"}
        ok = all(v == "PASS" for v in steps.values())
        return {"verdict": "pass" if ok else "fail", "steps": {k: {"status": v} for k, v in steps.items()}}

    def _lane_ok(self, task, head):
        try:
            RC.lane_record(self.a.rp, task["id"], head)
            return True
        except (LookupError, RC.StaleResult):
            return False

    def pubs(self):
        return self.publog.read_text().split() if self.publog.exists() else []

    def main_files(self):
        return sh(self.root, "git", "ls-tree", "-r", "--name-only", "main").split()


def run_steps(w, n=8, stop=("published", "parked", "STOP", "idle", "waiting", "runway")):
    out = []
    for _ in range(n):
        out.append(w.loop.step())
        if out[-1].startswith(stop):
            break
    return out


def guarded(fn, *a):
    """-> True/False from the scenario, or "crash" (a crash is neither green nor an honest red)."""
    try:
        return bool(fn(*a))
    except Exception as e:  # noqa: BLE001
        print("     (%s: %s: %s)" % (fn.__name__, type(e).__name__, str(e)[:200]))
        return "crash"


# ------------------------------------------------------------------------------------------------ scenarios
def sc_stolen_out_of_area(tmp, mod, tag):
    """P1: a1 has no own task, steals T_B (home a2), first edits ModA (its own area, outside the item's) as well."""
    ar = Arena(tmp, "P1" + tag, [task("T_B", MB)], mod)

    def b(prompt, tid):
        if "ralph_c area guard" in prompt:
            return {MB + "/b.py": "x = 2\n", MA + "/sneak.py": None}, 0
        return {MB + "/b.py": "x = 1\n", MA + "/sneak.py": "y = 2\n"}, 0
    w = ar.world("a1", b)
    out = run_steps(w)
    recs = ar.writer.records()
    assign = [r for r in recs if r["event"] == "assign"]
    first_fail = out and out[0].startswith("failed") and "area guard" in out[0]
    no_build_end_first = not any(r["event"] == "build_end" and r.get("sha") == recs[[x["event"] for x in recs]
                                 .index("pass_end")].get("sha") for r in recs) if "pass_end" in [x["event"] for x in
                                                                                                 recs] else False
    published = len(w.pubs()) == 1 and MA + "/sneak.py" not in w.main_files() and MB + "/b.py" in w.main_files()
    stolen = len(assign) == 1 and assign[0]["detail"]["stolen"] is True and assign[0]["detail"]["home"] == "a2"
    if tag == "":
        check(first_fail, "P1 the stolen item's first candidate (edits ModA) is refused by the area guard: %s" % out[:1])
        check(no_build_end_first, "P1 the refused candidate never reached build_end")
        check(stolen, "P1 the assign event records the steal (home a2)")
        check(published, "P1 the repaired candidate (inside the item's area) is published; ModA untouched on main")
        check(any("## LAST FAILURE" in p and "ralph_c area guard" in p for r, p in w.prompts if r == "build"),
              "P1 the refusal fed the next build pass")
    return first_fail and no_build_end_first and published and stolen


def sc_backpressure(tmp, mod, tag):
    """P2: a1 publishes live T_L1 to the runner queue; while it waits a1 gets no new live item (loop and board)."""
    ar = Arena(tmp, "P2" + tag, [task("T_L1", MA, live="minimal"), task("T_L2", MA, live="minimal"),
                                 task("T_O3", MA)], mod)
    w = ar.world("a1", lambda prompt, tid: ({MA + "/%s.py" % tid: "v = 1\n"}, 0))
    out = run_steps(w)
    waiting = out[-1].startswith("waiting") and len(RC.pending(ar.rp)) == 1
    n_calls = len(ar.calls)
    again = w.loop.step()
    loop_holds = again.startswith("waiting") and len(ar.calls) == n_calls
    t3, why3 = ar.board.assign("a1")                   # the board itself, asked directly while T_L1 waits
    board_live_refused = t3 is None and "waiting in the runner queue" in why3
    t4, _ = ar.board.assign("a2")                       # a2's list is empty and the open tasks are a1's: a2 steals
    board_live_refused = board_live_refused and t4 is not None and t4["id"] == "T_L2"
    ar.board.finish("a2", "T_L2", "test")
    # the runner gives its verdict: the loop publishes T_L1 and the next live item is given
    ar.runner_verdict("T_L1", "pass")
    out2 = run_steps(w)
    after = out2[0].startswith("published") and not RC.pending(ar.rp)
    out3 = run_steps(w)
    nxt = [r for r in ar.writer.records() if r["event"] == "assign"]
    given = after and nxt[-1]["task"] == "T_O3" and out3[-1].startswith("published")
    if tag == "":
        check(waiting, "P2 a1's live candidate T_L1 waits in the runner queue: %s" % out[-1])
        check(loop_holds, "P2 while it waits the loop runs no pass (no model call): %s" % again)
        check(board_live_refused, "P2 the board gives a1 nothing while T_L1 waits (%s); a2 is unaffected" % why3)
        check(given, "P2 after the runner's verdict T_L1 is published and a1 is given its next task T_O3: %s %s"
              % (out2[:1], out3[-1:]))
    return waiting and loop_holds and board_live_refused and given


def sc_lost_state_backpressure(tmp, mod, tag):
    """P2b: a restarted a1 (fresh ctl, empty loop state) with T_L1's candidate still pending gets no live item."""
    ar = Arena(tmp, "P2b" + tag, [task("T_L1", MA, live="minimal"), task("T_L2", MA, live="minimal"),
                                  task("T_O3", MA)], mod)
    w = ar.world("a1", lambda prompt, tid: ({MA + "/%s.py" % tid: "v = 1\n"}, 0))
    run_steps(w)
    ar.board.finish("a1", "T_L1", "lost")             # the board forgot it too: only the runner queue remembers
    t, why = ar.board.assign("a1")                      # offline work may still be given ...
    ok1 = t is not None and t["id"] == "T_O3"
    if t is not None:
        ar.board.finish("a1", t["id"], "test")
    w2 = ar.world("a1", w.builder, ctl="ctl_a1_restarted")
    n = len(ar.calls)
    r = w2.loop.step()                                  # ... but the live T_L2 is not
    ok = ok1 and r.startswith("idle") and "back-pressure" in r and "T_L2" in r and len(ar.calls) == n
    if tag == "":
        check(ok, "P2b with board and loop state lost, the runner queue alone keeps the live T_L2 from a1 "
              "(offline T_O3 given=%s): %s" % (ok1, r))
    return ok


def sc_tested_per_loop(tmp, mod, tag):
    """P3: a planted untested build_end of a1 refuses a1's next build pass, not a2's."""
    ar = Arena(tmp, "P3" + tag, [task("T_A", MA), task("T_B", MB)], mod)
    ar.writer.emit("ralph_c", "build_end", lane="build", run_id="ralph_c.a1.99", task="T_OLD", sha="ab" * 20,
                   detail={"builder": "ralph_c-a1-build-x", "build_id": "T_OLD.abababababab"})
    w1 = ar.world("a1", lambda prompt, tid: ({MA + "/a.py": "v = 1\n"}, 0))
    w2 = ar.world("a2", lambda prompt, tid: ({MB + "/b.py": "v = 1\n"}, 0))
    refused = False
    try:
        w1.loop.step()
    except C.NotTested:
        refused = True
    except Exception as e:  # noqa: BLE001 - a mutated module raises its own NotTested class
        refused = type(e).__name__ == "NotTested"
    a1_no_model = not any(m == "a1" for m, _, _ in ar.calls)
    out2 = run_steps(w2)
    a2_ok = out2[-1].startswith("published")
    if tag == "":
        check(refused and a1_no_model, "P3 a1's build pass refused (NotTested) with no model call")
        check(a2_ok, "P3 a2's loop is not blocked by a1's untested build: %s" % out2[-1:])
    return refused and a1_no_model and a2_ok


def sc_steal_last(tmp, mod, tag):
    """P4: a1 with an own open task never steals a2's."""
    ar = Arena(tmp, "P4" + tag, [task("T_B", MB), task("T_A", MA)], mod)
    t, why = ar.board.assign("a1")
    ok = t is not None and t["id"] == "T_A" and why == "own"
    if t is not None:
        ar.board.finish("a1", t["id"], "x")
    t2, why2 = ar.board.assign("a1")
    ok = ok and t2 is not None and t2["id"] == "T_B" and why2 == "steal"
    t3, why3 = ar.board.assign("a2")
    ok = ok and t3 is None
    if tag == "":
        check(ok, "P4 own task first (%s), steal only when own list empty (%s), a held task is not given twice "
              "(%s)" % (why, why2, why3))
    return ok


def sc_two_loops(tmp, mod, tag):
    """P5: a1 and a2 interleaved on one board, a tester FAIL included: every build_end is tested by a different
    agent before that loop's next build pass."""
    ar = Arena(tmp, "P5" + tag, [task("T_A1", MA), task("T_B1", MB), task("T_A2", MA), task("T_B2", MB)], mod)
    seen = {}

    def b(prompt, tid):
        k = seen[tid] = seen.get(tid, 0) + 1
        mod_ = MA if tid.startswith("T_A") else MB
        return {mod_ + "/%s.py" % tid: ("BAD = 1\n" if (tid == "T_B1" and k == 1) else "ok = %d\n" % k)}, 0
    w1, w2 = ar.world("a1", b), ar.world("a2", b)
    for _ in range(12):
        r1, r2 = w1.loop.step(), w2.loop.step()
        if r1.startswith("idle") and r2.startswith("idle"):
            break
    recs = ar.writer.records()
    ok = len(w1.pubs()) + len(w2.pubs()) == 4 and w1.pubs() and w2.pubs()
    for m in C.MEMBERS:
        mine = [r for r in L.ordered(recs) if r["run_id"].startswith("ralph_c.%s." % m)]
        ok = ok and L.untested_builds(mine) == [] and L.flagged_same_agent(mine) == []
        open_b = None
        for r in mine:
            if r["event"] == "build_end":
                open_b = r
            elif r["event"] == "test_start" and open_b and r["detail"]["tester"] != open_b["detail"]["builder"]:
                open_b = None
            elif r["event"] == "pass_start" and r["detail"]["role"] == "build" and open_b:
                ok = False                               # a build pass started while a build was untested
    snap = ar.board.snapshot()
    assigns = [r for r in recs if r["event"] == "assign"]
    ok = ok and sorted(snap["done"]) == ["T_A1", "T_A2", "T_B1", "T_B2"] and len(assigns) == 4 and \
        sorted(r["task"] for r in assigns) == ["T_A1", "T_A2", "T_B1", "T_B2"] and \
        all(r["detail"]["stolen"] == (r["detail"]["member"] != r["detail"]["home"]) for r in assigns) and \
        all(snap["holder"][r["task"]] == r["detail"]["member"] for r in assigns)
    fail_seen = any(r["event"] == "test_end" and r.get("verdict") == "fail" for r in recs)
    if tag == "":
        check(ok and fail_seen, "P5 two loops, one board: all 4 published once (a2 idle -> a1 steals what is left), each build_end tested by a different agent "
              "before that loop's next build pass (a tester FAIL included)")
    return ok


def sc_rename_out(tmp, mod, tag):
    """P1c: a2's file pre-exists on main; a1 renames it into its own area (git shows only the new path by default)."""
    ar = Arena(tmp, "P1c" + tag, [task("T_A", MA)], mod)
    w = ar.world("a1", lambda prompt, tid: ({}, 0))
    (w.root / MB).mkdir(parents=True)
    (w.root / MB / "theirs.py").write_text("z = 3\n" * 20)
    sh(w.root, "git", "add", MB)
    sh(w.root, "git", "commit", "-q", "-m", "theirs")

    def b(prompt, tid):
        if "ralph_c area guard" in prompt:
            return {MB + "/theirs.py": "z = 3\n" * 20, MA + "/mine.py": None}, 0
        (w.root / MA).mkdir(parents=True, exist_ok=True)
        sh(w.root, "git", "mv", MB + "/theirs.py", MA + "/mine.py")
        return {}, 0
    w.builder = b
    orig = w.model

    def model(role, prompt, **k):                       # the rename has no files dict: commit it here
        r = orig(role, prompt, **k)
        if role == "build" and sh(w.root, "git", "status", "--porcelain"):
            sh(w.root, "git", "commit", "-q", "-m", "rename")
        return r
    w.loop.model = lambda role, prompt, **k: model(role, w.loop.build_prompt(prompt) if role == "build" else prompt,
                                                   **k)
    out = run_steps(w)
    ok = out[0].startswith("failed") and "area guard" in out[0] and MB + "/theirs.py" in w.main_files() \
        and out[-1].startswith("published")
    if tag == "":
        check(ok, "P1c a rename out of the other member's area is refused (both paths diffed): %s" % out)
    return ok


def sc_crash_between_saves(tmp, mod, tag):
    """A crash after ralph_a saved task_i+1 but before the board heard: the next step must not redo the task."""
    ar = Arena(tmp, "CR" + tag, [task("T_A", MA), task("T_A2", MA)], mod)
    w = ar.world("a1", lambda prompt, tid: ({MA + "/%s.py" % tid: "v = 1\n"}, 0))
    real = w.loop._release_current if hasattr(w.loop, "_release_current") else None
    boom = []

    def crash(outcome):
        boom.append(outcome)
        raise KeyboardInterrupt("simulated crash")
    if real:
        w.loop._release_current = crash
    try:
        w.loop.step()
    except KeyboardInterrupt:
        pass
    w2 = ar.world("a1", w.builder)                      # restart on the same ctl
    out = run_steps(w2)
    asg = [r["task"] for r in ar.writer.records() if r["event"] == "assign"]
    ok = bool(boom) and asg == ["T_A", "T_A2"] and len(w.pubs()) == 2 and out[-1].startswith("published")
    if tag == "":
        check(ok, "crash between loop save and board.finish: restart finishes T_A, then takes T_A2: %s %s" % (asg, out))
    return ok


MUTATIONS = [
    ("P1c rename detection back on", sc_rename_out, '"--no-renames", ', ""),
    ("P1 area guard removed", sc_stolen_out_of_area, "        if bad:\n            Path(log)",
     "        if False:\n            Path(log)"),
    ("P2 runner-queue back-pressure removed", sc_backpressure,
     "waiting = bool(lane_wait) or bool(self.waiting_in_runner(member))", "waiting = bool(lane_wait)"),
    ("P2b runner-queue back-pressure removed (lost state)", sc_lost_state_backpressure,
     "waiting = bool(lane_wait) or bool(self.waiting_in_runner(member))", "waiting = bool(lane_wait)"),
    ("P3 per-loop require_tested removed", sc_tested_per_loop,
     "        require_tested(self.writer.records(), self.member)\n", ""),
    ("P4 steal first", sc_steal_last, "(own, False) if own else", "(own, False) if False else"),
]


# ------------------------------------------------------------------------------------------------ plain checks
def t_areas():
    def refused(fn, *a):
        try:
            fn(*a)
            return False
        except C.AreaRefused:
            return True
    ar = C.load_areas(AREAS)
    check(refused(C.load_areas, {"a1": ["src/**"], "a2": [MB + "/**"]}), "areas: overlapping globs refused")
    check(refused(C.load_areas, {"a1": [MA + "/**"]}), "areas: a missing member refused")
    check(refused(C.load_areas, {"a1": [], "a2": [MB + "/**"]}), "areas: an empty member refused")
    check(refused(C.home_of, task("T", "src/RimMandrake/ModC"), ar), "home: a task in no member's area refused")
    check(refused(C.home_of, dict(task("T", MA), area=[MA + "/**", MB + "/**"]), ar),
          "home: a task spanning both members refused")
    check(refused(C.home_of, dict(task("T", MA), area=[]), ar), "home: a task with no area refused")
    t = dict(task("T", MA), shared=["src/RimMandrake/Common/x.py"])
    check(C.area_violations(t, [MA + "/a.py", "src/RimMandrake/Common/x.py"], ar) == [],
          "guard: area and shared paths pass")
    check(len(C.area_violations(t, [MA + "/a.py", "README", MB + "/b.py"], ar)) == 2,
          "guard: a path outside the area and one in the other member's area are both refused")
    check(C.area_violations(t, [MA + "/deep/er/x.py"], ar) == [], "guard: ** crosses directories inside the area")


def t_stop_status_prompt(tmp):
    ar = Arena(tmp, "S", [task("T_A", MA)])
    w = ar.world("a1", lambda prompt, tid: ({MA + "/a.py": "v = 1\n"}, 0))
    run_steps(w)
    st = json.loads((ar.aroot / "status" / "ralph_c.json").read_text())
    check(ar.status_seen and all(s == "busy" for s in ar.status_seen),
          "status: ralph_c.json reads busy while a model pass runs: %s" % ar.status_seen)
    check(st["state"] == "idle", "status: ralph_c.json reads idle at a pass boundary")
    bp = [p for r, p in w.prompts if r == "build"][0]
    head = bp.split("## TASK")[0]
    check("## RALPH_C" in bp and "builder `a1`" in bp and "at most 4 subagents" in bp and "ralph_a" not in head
          and "Stolen: no" in bp, "prompt: the build prompt carries the ralph_c section and no ralph_a header")
    (ar.aroot / "STOP.ralph_c").touch()
    n = len(ar.calls)
    r = w.loop.step()
    check(r == "STOP" and len(ar.calls) == n, "STOP.ralph_c (arena.py's stop file) stops the loop: %s" % r)
    os.environ["RALPH_C_MAX_SUBAGENTS"] = "lots"
    check(C.max_subagents() == 0, "a garbled subagent bound means none, never unbounded")
    os.environ.pop("RALPH_C_MAX_SUBAGENTS")
    out = C.runner_loop("steve", str(tmp), aroot=ar.aroot, run_one=lambda: None, sleep=lambda s: None)
    check(out == ["STOP"], "runner_loop honours STOP.ralph_c")
    (ar.aroot / "STOP.ralph_c").unlink()
    seen = []

    def one():
        seen.append(json.loads((ar.aroot / "status" / "ralph_c.runner-archmagi.json").read_text())["state"])
        return None
    C.runner_loop("archmagi", str(tmp), aroot=ar.aroot, run_one=one, sleep=lambda s: None, max_steps=2)
    st = json.loads((ar.aroot / "status" / "ralph_c.json").read_text())
    check(seen == ["busy", "busy"] and st["state"] == "idle", "runner_loop: busy during a run, idle after")
    try:
        C.runner_loop("full", str(tmp), aroot=ar.aroot, run_one=lambda: None, max_steps=1)
        check(False, "runner_loop refuses an unknown lane")
    except C.Refused:
        check(True, "runner_loop refuses an unknown lane")


def t_default_gate(tmp):
    os.environ["RALPH_C_GATE_CMD"] = "%s -c \"import sys,json;print(json.dumps({'argv':sys.argv[1:]}))\"" % sys.executable
    try:
        r = C.cmd_gate_c({"id": "T"}, "b", "h", "build", root=tmp, log=tmp / "g.log")
    finally:
        os.environ.pop("RALPH_C_GATE_CMD")
    a = r.get("argv", [])
    check(a[a.index("--arm") + 1] == "ralph_c" if "--arm" in a else False,
          "default gate is called with --arm ralph_c (ralph_a's would read no ralph_c record): %s" % a)
    ar = Arena(tmp, "G", [task("T_A", MA)])
    lp = C.LoopC("a1", new_clone(tmp / "G" / "c"), tmp / "G" / "ctl", ar.board, arena=ar.aroot, model=None,
                 writer=ar.writer)
    check(lp.precheck.__code__ is not RA.Loop.__init__.__code__ and "precheck_c" in lp.precheck.__code__.co_names,
          "default precheck runs under RM_ARM=ralph_c")


def t_run_lock_and_idle(tmp):
    import fcntl
    ar = Arena(tmp, "RL", [task("T_A", MA)])
    w = ar.world("a1", lambda prompt, tid: ({MA + "/a.py": "v = 1\n"}, 0))
    slept = []
    w.loop.sleep = slept.append
    ar.board.path.parent.mkdir(parents=True, exist_ok=True)
    held = open(ar.board.path.parent / "loop.a1.lock", "w")
    fcntl.flock(held, fcntl.LOCK_EX)                     # another a1 process, started with some other --ctl
    try:
        w.loop.run(max_steps=3)
        check(False, "a second a1 loop (other ctl dir) is refused by the per-member lock")
    except C.Refused:
        check(True, "a second a1 loop (other ctl dir) is refused by the per-member lock")
    finally:
        held.close()
    out = w.loop.run(max_steps=10)
    check(out[-1].startswith("idle: no open task") and len(out) == 2 and not slept,
          "run() ends on an empty board instead of spinning: %s" % out)
    ar2 = Arena(tmp, "RL2", [task("T_L1", MA, live="minimal")])
    w2 = ar2.world("a1", lambda prompt, tid: ({MA + "/a.py": "v = 1\n"}, 0))
    w2.loop.sleep = slept.append
    out2 = w2.loop.run(max_steps=4)
    check(len(slept) == 4 and all(r.startswith("waiting") for r in out2),
          "run() sleeps between polls while its live candidate waits: %s" % out2)


def t_cmdmodel_env(tmp):
    m = C.CmdModelC("%s -c \"import os;print(os.environ['RM_ARM'], os.environ['RALPH_C_MEMBER'], "
                    "os.environ['RALPH_C_MAX_SUBAGENTS'])\"" % sys.executable, "a2")
    r = m("build", "", cwd=tmp, agent_id="x", run_id=0, timeout_s=30, log=tmp / "cm.log")
    check(r["rc"] == 0 and r["text"].split() == ["ralph_c", "a2", "4"], "CmdModelC: the child carries RM_ARM=ralph_c, "
          "its member and the subagent bound: %r" % r["text"])


def t_cmdmodel_tester_sandbox(tmp):
    """A tester pass through the REAL call signature (sandbox= as Loop passes it): no TypeError, scrubbed env (no
    RM_ARM / RALPH_*), run under the sandbox when bwrap is usable."""
    troot = tmp / "tsb"
    troot.mkdir()
    m = C.CmdModelC("%s -c \"import os;print(os.environ.get('RM_ARM'), os.environ.get('RALPH_C_MEMBER'), "
                    "os.environ.get('TESTER_ID','')[:7], os.environ['HOME'])\"" % sys.executable, "a2")
    r = m("test", "", cwd=troot, agent_id="x", run_id=0, timeout_s=30, log=troot / "t.log",
          sandbox={"root": troot, "hide": []})
    check(r["rc"] == 0 and r["text"].split() == ["None", "None", "tester-", str(troot / "home")],
          "CmdModelC tester pass takes sandbox= and runs in ralph_a's scrubbed tester env: %r" % r["text"])
    check(C.RA.bwrap_argv({"root": troot, "hide": []}, troot) == [] or "--bind" in
          C.RA.bwrap_argv({"root": troot, "hide": []}, troot), "bwrap_argv is reachable from the tester path")


def t_signed_writer(tmp):
    if not hasattr(L, "harness_pass"):
        SKIPS.append("t_signed_writer: arena_eventlog.harness_pass absent (ARENA_RALPHC_WIRE_ENTRYPOINT_AND_UNITS)")
        print("EXPECTED SKIP t_signed_writer: needs arena_eventlog.harness_pass, owed by "
              "ARENA_RALPHC_WIRE_ENTRYPOINT_AND_UNITS")
        return
    root = tmp / "signed"
    os.environ["ARENA_CLONES"] = str(root / "clones")
    os.environ["ARENA_EVENT_TOKEN_FILE"] = str(tmp / "secret" / "event_token")
    os.environ["ARENA_ANCHOR_FILE"] = str(tmp / "secret" / "anchors.jsonl")
    os.environ["ARENA_WITNESS"] = str(tmp / "secret" / "witness.jsonl")
    os.environ["ARENA_ROOT"] = str(root / "arena")
    p = A.paths()
    L.init_token(p)
    sw = C.SignedWriterC(p)
    ar = Arena(tmp / "signed", "W", [task("T_A", MA), task("T_B", MB)], writer=sw)
    w1 = ar.world("a1", lambda prompt, tid: ({MA + "/a.py": "v = 1\n"}, 0))
    w2 = ar.world("a2", lambda prompt, tid: ({MB + "/b.py": "v = 1\n"}, 0))
    run_steps(w1)
    run_steps(w2)
    acc = sw.records()
    check(len(w1.pubs()) == 1 and len(w2.pubs()) == 1 and L.untested_builds(acc) == []
          and {r["arm"] for r in acc} == {"ralph_c"} and sum(r["event"] == "assign" for r in acc) == 2,
          "signed HarnessWriter: both loops' events accepted under arm ralph_c, every build tested")


def t_wired(tmp):
    """ARENA_RALPHC_WIRE_ENTRYPOINT_AND_UNITS: the signer lists ralph_c_loop.py, and the installer plans the unit
    templates the arm.toml names (rm-ralph-loop@ and rm-runner@), whose ExecStart reaches the real entry scripts."""
    import arena as AR
    import arena_install as INS
    check("ralph_c_loop.py" in L.ENTRYPOINTS, "arena_eventlog.ENTRYPOINTS lists ralph_c_loop.py (a harness pass can open)")
    check("ralph_c_runner.py" not in L.ENTRYPOINTS, "the runner module is not an entrypoint (runner.sh execs ralph_c_loop.py)")
    cfg = AR.load_config(AR.TEMPLATES / "arm.toml.template")
    ud = tmp / "units"
    plan = {p.name: t for p, t in INS.plan_units(cfg, ud) if p.parent == ud}
    for nm in ("rm-ralph-loop@.service", "rm-runner@.service"):
        check(nm in plan, "installer plan writes the unit template %s" % nm)
    loop, run = plan.get("rm-ralph-loop@.service", ""), plan.get("rm-runner@.service", "")
    check("@ARENA_DIR@" not in loop + run, "no unrendered @ARENA_DIR@ left in a rendered unit")
    check("ralph_c/loop.sh" in loop and "ralph_c/runner.sh" in run and "%i" in loop and "%i" in run,
          "ExecStart passes the instance to ralph_c/loop.sh (member) and ralph_c/runner.sh (lane)")
    check((HERE / "ralph_c" / "loop.sh").exists() and (HERE / "ralph_c" / "runner.sh").exists(), "both entry scripts exist")
    check(str(HERE) in loop and str(HERE) in run, "ExecStart paths point at this arena directory")


def t_envfiles(tmp):
    """ARENA_UNIT_ENVFILES_WIRE_RALPH_RUNNER: env templates are planned (and never overwrite), carry no secrets and
    leave the refusal intact; the units do not respin on exit 2; the entry scripts really exit 2 when unconfigured."""
    import arena as AR
    import arena_install as INS
    cfg = AR.load_config(AR.TEMPLATES / "arm.toml.template")
    ed = tmp / "envd"
    plan = INS.plan_envfiles(cfg, ed)
    names = {p.name: t for _k, p, t in plan}
    check({"ralph-a1.env", "ralph-a2.env", "runner-steve.env", "runner-archmagi.env"} <= set(names),
          "env templates planned for every ralph_c loop and runner instance: %s" % sorted(names))
    check(all(k == "file_if_absent" for k, _p, _t in plan), "env files are written only when absent")
    check(all(not any(l.strip() and not l.startswith("#") for l in t.splitlines()) for t in names.values()),
          "templates are all comments: an untouched file stays an unset (refusing) configuration")
    check("RALPH_C_ROOT_A1" in names.get("ralph-a1.env", "") and "RALPH_C_RUNNER_CLONE_ARCHMAGI" in names.get("runner-archmagi.env", ""),
          "templates name the variables the entry scripts read")
    ed.mkdir(parents=True, exist_ok=True)
    (ed / "ralph-a1.env").write_text("MINE=1\n")
    INS.apply_plan(plan, True, out=lambda *_: None)
    check((ed / "ralph-a1.env").read_text() == "MINE=1\n" and (ed / "runner-steve.env").exists(),
          "apply keeps an existing env file and writes the missing ones")
    # TOCTOU (GPT review): a file that appears between the exists() check and the write must survive (exclusive create)
    (ed / "ralph-a2.env").write_text("RACE=1\n")
    _ex = Path.exists
    Path.exists = lambda self, *a, **k: False if self.name == "ralph-a2.env" else _ex(self, *a, **k)
    try:
        INS.apply_plan(plan, True, out=lambda *_: None)
    finally:
        Path.exists = _ex
    check((ed / "ralph-a2.env").read_text() == "RACE=1\n", "a file created between the check and the write is not truncated")
    for nm in ("rm-ralph-loop@.service.tmpl", "rm-runner@.service.tmpl"):
        check("RestartPreventExitStatus=2" in (AR.TEMPLATES / "systemd" / nm).read_text(), "%s stops restarting on exit 2" % nm)
    env = {k: v for k, v in os.environ.items() if not k.startswith("RALPH_") and k != "RM_ARM"}
    for args in (["ralph_a/loop.sh"], ["ralph_c/loop.sh", "a1"], ["ralph_c/runner.sh", "steve"]):
        r = subprocess.run(["bash", str(HERE / args[0])] + args[1:], env=env, capture_output=True, text=True, timeout=60)
        check(r.returncode == 2, "%s unconfigured exits 2 (got %s)" % (" ".join(args), r.returncode))
    e2 = dict(env, RALPH_A_ROOT="/x", RALPH_A_TASKS="T")
    r = subprocess.run(["bash", str(HERE / "ralph_a/loop.sh")], env=e2, capture_output=True, text=True, timeout=60)
    check(r.returncode == 2 and "MODEL_CMD" in r.stdout, "ralph_a without a model command exits 2 naming it")


def _plain_git_run(root, *a, transport=False, **kw):
    """The reverted fix: bare git, no safe env or config."""
    return subprocess.run(["git", "-C", str(root)] + list(a), **kw)


def t_runner_git_trust(tmp):
    """ARENA_EXPORT_FIX_BUILDER_GIT_TRUST: RunnerDriver.checkout fetches/checks out/cleans a clone whose .git the build
    helper wrote. Every trap is planted in a throwaway clone: bare git is fooled or runs its code, the driver is not;
    with arena_safe_git swapped for bare git (fix reverted) the same run is fooled again."""
    def clone_with(tag, traps, origin_url=None):
        origin, a, b = T.make_repo(tmp / ("rg_origin_" + tag), "origin")
        k = tmp / ("rg_clone_" + tag) / "tclone"
        k.parent.mkdir()
        subprocess.run(["git", "clone", "-q", str(origin), str(k)], check=True, env=T.ENV, capture_output=True)
        mk = T.plant(k, b, b, traps) if "replace" not in traps else T.plant(k, a, b, traps)
        for f in Path(mk).iterdir():
            f.unlink()
        if origin_url:
            T.git(k, "remote", "set-url", "origin", origin_url)
        return k, a, b, mk
    base = ("replace", "graft", "fsmonitor", "hooksPath", "filter", "textconv", "external")

    def run(tag, traps, sha_of, origin_url=None):
        k, a, b, mk = clone_with(tag, traps, origin_url)
        ok, out = RC.RunnerDriver().checkout(str(k), sha_of(a, b))
        head = T.git(k, "-c", "core.fsmonitor=false", "rev-parse", "HEAD", check=False, env=dict(T.ENV, GIT_NO_REPLACE_OBJECTS="1"))
        text = (k / "f.txt").read_text().strip() if (k / "f.txt").exists() else None
        return ok, out, head, text, T.fired(mk), (a, b)
    ok, out, head, text, fired, (a, b) = run("safe", base, lambda a, b: b)
    check(ok and head == b and text == "beta" and not fired,
          "checkout of a clone with replace/graft/fsmonitor/hooksPath/filter/textconv/diff.external planted: true sha, true "
          "content, none of the builder's code ran (%s %s %s %s)" % (ok, text, fired, out[:80]))
    real = RC.SG.git_run
    RC.SG.git_run = _plain_git_run
    try:
        ok, out, head, text, fired, (a, b) = run("plain", base, lambda a, b: b)
    finally:
        RC.SG.git_run = real
    check(text != "beta" or bool(fired),
          "RED: with the fix reverted (bare git) the same checkout is fooled (content %r) or runs builder code (%s)" % (text, fired))
    # fetch: core.sshCommand and remote.origin.uploadpack are the builder's commands too
    for trap, url in (("sshCommand", "ssh://nohost.invalid/x"), ("uploadpack", None)):
        ok, out, head, text, fired, _ = run("s_" + trap, (trap,), lambda a, b: b, url)
        check(trap not in fired, "fetch with %s planted in the clone: its command did not run (%s, ok=%s)" % (trap, fired, ok))
        k, a, b, mk = clone_with("p_" + trap, (trap,), url)      # the fix reverted: a bare `git fetch origin`
        subprocess.run(["git", "-C", str(k), "fetch", "-q", "origin"], capture_output=True, timeout=60, env=T.ENV)
        check(trap in T.fired(mk), "RED: a bare git fetch (fix reverted) runs the builder's %s as the harness (%s)" % (trap, T.fired(mk)))
    # a non-empty .git/info/attributes changes what a checkout writes (eol/ident/filter): refused
    ok, out, head, text, fired, _ = run("attr", ("attributes",), lambda a, b: b)
    check(not ok and "info/attributes" in out, "a clone with a non-empty .git/info/attributes is refused (%s)" % out[:80])
    check(not re.search(r"[\"']archive[\"']", (HERE / "ralph_c_runner.py").read_text()), "the runner never calls git archive")


def t_runner_git_trust2(tmp):
    """Opus review of b78de728b0: every git call of RunnerDriver (not only checkout), credential/askpass/insteadOf pins,
    ssh fallback, worktree/sparse/crlf/gitdir-file layouts, a forged object. Each trap is planted in a throwaway clone;
    the reverted fix (bare git / no verify) is fooled again."""
    import threading
    import http.server
    import zlib

    def mk_clone(tag, traps=()):
        origin, a, b = T.make_repo(tmp / ("r2_origin_" + tag), "origin")
        T.git(origin, "branch", "-M", "main")
        k = tmp / ("r2_clone_" + tag) / "tclone"
        k.parent.mkdir()
        subprocess.run(["git", "clone", "-q", str(origin), str(k)], check=True, env=T.ENV, capture_output=True)
        mk = T.plant(k, b, b, traps)
        for f in Path(mk).iterdir():
            f.unlink()
        return k, a, b, mk, origin
    drv = RC.RunnerDriver()
    real = RC.SG.git_run
    # (1) clone_head / clone_dirty / restore_mods run no builder code (fsmonitor + post-checkout hook planted)
    traps = ("fsmonitor", "hooksPath")
    k, a, b, mk, _ = mk_clone("calls", traps)
    h = drv.clone_head(str(k))
    d = drv.clone_dirty(str(k))
    ok, out, head = drv.restore_mods([], str(k))
    check(h == b and d == "" and ok and head == b and not T.fired(mk),
          "clone_head/clone_dirty/restore_mods on a clone with fsmonitor+hooksPath planted: true answers, no builder code (%s %r %s %s)" % (h == b, d, ok, T.fired(mk)))
    k, a, b, mk, _ = mk_clone("calls_red", traps)
    RC.SG.git_run = _plain_git_run
    try:
        drv.clone_dirty(str(k))
        drv.restore_mods([], str(k))
    finally:
        RC.SG.git_run = real
    check(bool(T.fired(mk)), "RED: with the fix reverted (bare git) clone_dirty/restore_mods run the builder's code (%s)" % T.fired(mk))
    # (2) credential.helper / core.askPass against an https origin answering 401; url.insteadOf refused
    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="x"')
            self.send_header("Content-Length", "0")
            self.end_headers()
        log_message = lambda *a: None
    os.environ["GIT_CONFIG_GLOBAL"] = os.devnull       # the owner's own credential manager is not under test
    srv = http.server.HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = "http://127.0.0.1:%d/x.git" % srv.server_port
    try:
        k, a, b, mk, _ = mk_clone("cred")
        sc = k.parent / "cred_scripts"
        sc.mkdir()
        helper = T._script(sc / "helper", "touch '%s/credential'\n" % mk)
        ask = T._script(sc / "ask", "touch '%s/askpass'\nexit 1\n" % mk)
        T.git(k, "remote", "set-url", "origin", url)
        T.git(k, "config", "credential.helper", "!" + helper)
        T.git(k, "config", "core.askPass", ask)
        drv.checkout(str(k), b)
        check(not T.fired(mk), "fetch from a 401 origin with credential.helper/core.askPass planted: neither ran (%s)" % T.fired(mk))
        try:
            subprocess.run(["git", "-C", str(k), "fetch", "-q", "origin"], capture_output=True, timeout=20, env=dict(T.ENV, GIT_TERMINAL_PROMPT="0", GIT_CONFIG_GLOBAL=os.devnull))
        except subprocess.TimeoutExpired:
            pass
        check("credential" in T.fired(mk) or "askpass" in T.fired(mk), "RED: a bare git fetch (fix reverted) runs the planted credential helper/askpass (%s)" % T.fired(mk))
    finally:
        srv.shutdown()
        os.environ.pop("GIT_CONFIG_GLOBAL", None)
    k, a, b, mk, origin = mk_clone("insteadof")
    T.git(k, "config", "url.%s/.insteadOf" % (tmp / "nowhere"), str(tmp) + "/")
    ok, out = drv.checkout(str(k), b)
    check(not ok and "insteadOf" in out, "a clone with url.*.insteadOf is refused for a fetch (%s)" % out[:80])
    # (3) no global core.sshCommand: plain `ssh` (an empty value fails every ssh origin); the fake ssh proves it is run
    gc = tmp / "empty_gitconfig"
    gc.write_text("")
    bin_ = tmp / "fakebin"
    bin_.mkdir(exist_ok=True)
    T._script(bin_ / "ssh", "touch '%s/ssh_used'\nexit 1\n" % tmp)
    saved = {k_: os.environ.get(k_) for k_ in ("GIT_CONFIG_GLOBAL", "PATH")}
    os.environ["GIT_CONFIG_GLOBAL"] = str(gc)
    os.environ["PATH"] = str(bin_) + os.pathsep + os.environ["PATH"]
    try:
        check(RC.SG.user_ssh_cfg() == ["-c", "core.sshCommand=ssh"], "no global core.sshCommand: falls back to plain ssh, not an empty value (%s)" % RC.SG.user_ssh_cfg())
        k, a, b, mk, _ = mk_clone("ssh")
        T.git(k, "remote", "set-url", "origin", "ssh://nohost.invalid/x")
        (tmp / "ssh_used").unlink(missing_ok=True)
        drv.checkout(str(k), b)
        check((tmp / "ssh_used").exists(), "an ssh origin fetch really runs `ssh` when the owner configured no sshCommand")
    finally:
        for k_, v in saved.items():
            if v is None:
                os.environ.pop(k_, None)
            else:
                os.environ[k_] = v
    # (4) core.worktree, sparse checkout, autocrlf, a gitdir: file
    k, a, b, mk, _ = mk_clone("wt")
    decoy = tmp / "decoy_tree"
    decoy.mkdir()
    (decoy / "precious.txt").write_text("keep me\n")
    T.git(k, "config", "core.worktree", str(decoy))
    ok, out = drv.checkout(str(k), b)
    check(not ok and "core.worktree" in out and (decoy / "precious.txt").exists(), "core.worktree planted: refused, decoy untouched (%s)" % out[:80])
    subprocess.run(["git", "-C", str(k), "clean", "-fdq"], env=T.ENV, capture_output=True)
    check(not (decoy / "precious.txt").exists(), "RED: a bare `git clean -fd` (fix reverted) deletes the decoy tree's files")
    (decoy / "precious.txt").write_text("keep me\n")
    r = RC.SG.git_run(k, "clean", "-fdq", capture_output=True, text=True)
    check((decoy / "precious.txt").exists(), "arena_safe_git itself pins the worktree: clean with core.worktree planted left the decoy alone (rc %s)" % r.returncode)
    def sparse_run(tag):
        k, a, b, mk, _ = mk_clone(tag)
        T.git(k, "config", "core.sparseCheckout", "true")
        (k / ".git" / "info" / "sparse-checkout").write_text("f.txt\n")
        T.git(k, "config", "core.autocrlf", "true")
        (k / "g.txt").unlink()
        ok, out = drv.checkout(str(k), b)
        return ok, out, (k / "g.txt").read_bytes() if (k / "g.txt").exists() else None
    ok, out, g = sparse_run("sparse")
    check(ok and g == b"keep\n", "sparseCheckout+autocrlf planted: g.txt is written, with the blob's bytes (%s %r %s)" % (ok, g, out[:60]))
    keep, RC.SG.WORKTREE_CFG = RC.SG.WORKTREE_CFG, []
    try:
        ok, out, g = sparse_run("sparse_red")
    finally:
        RC.SG.WORKTREE_CFG = keep
    check(g != b"keep\n", "RED: with the layout pins reverted the same clone loses g.txt (sparse) or gets CRLF (%r)" % g)
    k, a, b, mk, _ = mk_clone("gitfile")
    real_git = tmp / "gitfile_realgit"
    os.rename(k / ".git", real_git)
    (k / ".git").write_text("gitdir: %s\n" % real_git)
    ok, out = drv.checkout(str(k), b)
    check(not ok and "not a real directory" in out, "a `gitdir:` file in place of .git is refused (%s)" % out[:80])
    # (5) a forged object: the blob of f.txt@B stored with other content
    def forge(k, b):
        oid = T.git(k, "rev-parse", b + ":f.txt")
        pth = k / ".git" / "objects" / oid[:2] / oid[2:]
        pth.chmod(0o644)
        pth.write_bytes(zlib.compress(b"blob 5\0EVIL\n"))
        (k / "f.txt").unlink()                         # so the checkout has to write it from the object store
        return oid
    k, a, b, mk, _ = mk_clone("forge")
    forge(k, b)
    ok, out = drv.checkout(str(k), b)
    check(not ok and "forged" in out and not (k / "f.txt").exists(), "a forged blob object is detected before checkout (%s)" % out[:90])
    k, a, b, mk, _ = mk_clone("forge_red")
    forge(k, b)
    keepv = RC.SG.verify_tree
    RC.SG.verify_tree = lambda root, rev: (True, "")
    try:
        ok, out = drv.checkout(str(k), b)
    finally:
        RC.SG.verify_tree = keepv
    check(ok and (k / "f.txt").read_text() == "EVIL\n", "RED: without the verification the forged blob checks out and the tree reads sha B with EVIL content")
    k, a, b, mk, _ = mk_clone("honest")
    ok, out = drv.checkout(str(k), b)
    check(ok and (k / "f.txt").read_text() == "beta\n", "an honest clone still checks out (%s)" % out[:80])


def main():
    tmp = Path(tempfile.mkdtemp(prefix="selftest_ralph_c_"))
    saved = {k: os.environ.get(k) for k in ("ARENA_ROOT", "ARENA_CLONES", "ARENA_EVENT_TOKEN_FILE",
                                             "ARENA_ANCHOR_FILE", "ARENA_WITNESS", "RM_ARM", "RALPH_C_MAX_SUBAGENTS",
                                             "RALPH_C_GATE_CMD")}
    os.environ.pop("RM_ARM", None)
    os.environ.pop("RALPH_C_MAX_SUBAGENTS", None)
    try:
        for name, fn in (("P1 stolen item's out-of-area edit refused", sc_stolen_out_of_area),
                         ("P2 no new live item while a live candidate waits", sc_backpressure),
                         ("P2b back-pressure survives lost loop state", sc_lost_state_backpressure),
                         ("P3 tested check per loop", sc_tested_per_loop),
                         ("P4 steal only when own list empty", sc_steal_last),
                         ("P5 two loops, one board", sc_two_loops),
                         ("P1c rename out of the other area refused", sc_rename_out),
                         ("crash between saves recovered", sc_crash_between_saves)):
            check(guarded(fn, tmp, C, "") is True, "green: " + name)
        for i, (name, fn, old, new) in enumerate(MUTATIONS):
            check(guarded(fn, tmp, variant(old, new), "_m%d" % i) is False,
                  "mutation goes RED (a False verdict, not a crash): " + name)
        for fn, a in ((t_areas, ()), (t_stop_status_prompt, (tmp,)), (t_default_gate, (tmp,)), (t_run_lock_and_idle, (tmp,)), (t_cmdmodel_env, (tmp,)), (t_cmdmodel_tester_sandbox, (tmp,)),
                      (t_signed_writer, (tmp,)), (t_wired, (tmp,)), (t_envfiles, (tmp,)), (t_runner_git_trust, (tmp,)), (t_runner_git_trust2, (tmp,))):
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
