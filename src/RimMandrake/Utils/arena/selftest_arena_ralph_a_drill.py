#!/usr/bin/env python3
"""selftest_arena_ralph_a_drill.py - the failure-path drill (ARENA_DRILL_PROVE_KILLED_PASS_RECOVERS), offline.

Design: architecture_switch_harness_2026-10-29.md section 4.2 (carried over from Ralph section 8 point 4): plant a
failing check in one task, kill one build pass, kill the gate, kill a tester pass, all in `ralph_a`. Proven when
  P  nothing unchecked reaches the branch the judge reads (main: published only after the final gate and a tester
     verdict), whichever process died;
  R  each killed process's next pass recovers (a new Loop over the same control dir and signed log publishes);
  T  a killed TESTER pass leaves the builder blocked (no build pass is invoked until the tester has run), even when
     state.json was lost with it.
Every scenario runs against the real loop (must be green) and against a copy with its guard mutated away (must go
red). Each scenario also writes a `defect` record (detail.drill) to the SIGNED event log: the drill's record.

Kills: SIGKILL of a real process group for the build pass, the gate subprocess (cmd_gate) and the tester pass; a
BaseException raised inside the loop for "the loop process itself died here" (state on disk is exactly what a
SIGKILL leaves, because nothing after the raise runs).
"""
from __future__ import annotations

import os
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import arena_eventlog as L  # noqa: E402
import selftest_arena_ralph_a as S  # noqa: E402
from selftest_arena_ralph_a import GOOD, BROKEN, TASK, World, R, check, guarded, variant  # noqa: E402

FAILS = S.FAILS
TBASE = S.TBASE


class Killed(BaseException):
    """the process died here (nothing after the raise runs)"""


def reopen(w, mod, **kw):
    """The supervisor restarts the loop: a NEW Loop over the same control dir, clone and event log."""
    args = dict(model=w.model, gate=w.gate, writer=w.writer, release=lambda: None,
                runway=lambda: {"state": "MEASURED", "runway": 0.9}, precheck=lambda log: True,
                publish_cmd=w.loop.publish_cmd, sync=None, tester_tmp=TBASE[0])
    args.update(kw)
    w.loop = mod.Loop(w.root, w.ctl, [TASK], **args)
    return w.loop


DRILL = []      # (drill, last loop status) of each green-run scenario; main() writes them to the SIGNED log


def drill_note(w, name, outcome):
    if w.mod is R:                                       # the mutated runs are not the drill
        DRILL.append((name, str(outcome)[:200]))


def main_clean(w):
    """main holds only a tested sha, or nothing at all"""
    return w.main_src() in (None, GOOD, GOOD + "# repaired\n")


PASS_ALL = lambda prompt, cwd: "looked fine\nVERDICT: PASS"          # noqa: E731  a tester that waves everything through


def sc_planted(tmp, mod, tag):
    """P: a planted failing check is stopped by the BUILD gate (no tester pass spent), never published; the repair is."""
    w = World(tmp, "dA" + tag, mod, builder=S.repairs, tester=PASS_ALL)
    first = w.loop.step()
    ok = first.startswith("failed") and "gate steps not passed" in first and w.roles() == ["build"] \
        and not w.pubs() and w.main_src() is None
    reopen(w, mod)                                       # even across a restart the unchecked build stays off main
    out = S.run_steps(w)
    drill_note(w, "planted_check", out[-1])
    return ok and out[-1].startswith("published") and w.main_src() == GOOD and len(w.pubs()) == 1


def sc_planted_final(tmp, mod, tag):
    """P: a check that fails only at the FINAL gate (tester passed it) is never published."""
    w = World(tmp, "dA2" + tag, mod, tester=PASS_ALL)
    real = w.gate
    seen = []

    def gate(task, base, head, phase, log):
        rec = real(task, base, head, phase, log)
        if phase == "final" and not seen:
            seen.append(1)
            return dict(rec, verdict="fail")
        return rec
    reopen(w, mod, gate=gate)
    first = w.loop.step()
    ok = first.startswith("failed") and "final gate" in first and not w.pubs() and w.main_src() is None
    out = S.run_steps(w)
    drill_note(w, "planted_final_check", out[-1])
    return ok and out[-1].startswith("published") and len(w.pubs()) == 1


def sc_build_killed(tmp, mod, tag):
    """R+P: the loop dies inside the build pass, after the builder committed (unchecked) and left a half-written
    file. Nothing is published; the next pass gates the leftover commit and recovers (not 'empty candidate')."""
    state = []

    def b(prompt):
        if not state:
            state.append(1)
            (w.root / "mod.py").write_text(GOOD)
            (w.root / "half.txt").write_text("half written\n")
            S.sh(w.root, "git", "add", "mod.py")
            S.sh(w.root, "git", "commit", "-q", "-m", "unchecked wip")
            raise Killed()
        return None, 0                                   # the new builder finds the work already on wip
    w = World(tmp, "dB" + tag, mod, builder=b)
    try:
        w.loop.step()
        return False
    except Killed:
        pass
    ok = not w.pubs() and w.main_src() is None
    reopen(w, mod)
    out = S.run_steps(w)
    drill_note(w, "build_killed", out[-1])
    return ok and out[-1].startswith("published") and w.main_src() == GOOD and len(w.pubs()) == 1


def sc_build_gate_killed(tmp, mod, tag):
    """R+P: the build-phase gate dies; the build is not published, its next pass recovers."""
    calls = []
    w = World(tmp, "dC" + tag, mod)
    real = w.gate

    def gate(task, base, head, phase, log):
        calls.append(phase)
        if len(calls) == 1:
            raise Killed()
        return real(task, base, head, phase, log)
    w.gate = gate
    reopen(w, mod, gate=gate)
    try:
        w.loop.step()
        return False
    except Killed:
        pass
    ok = not w.pubs() and w.main_src() is None
    reopen(w, mod, gate=gate)
    out = S.run_steps(w)
    drill_note(w, "build_gate_killed", out[-1])
    return ok and out[-1].startswith("published") and w.main_src() == GOOD and len(w.pubs()) == 1


def sc_final_gate_killed(tmp, mod, tag):
    """R+P: the FINAL gate dies after a tester PASS: main has not moved; the restart tests again and publishes."""
    calls = []
    w = World(tmp, "dD" + tag, mod)
    real = w.gate

    def gate(task, base, head, phase, log):
        calls.append(phase)
        if phase == "final" and calls.count("final") == 1:
            raise Killed()
        return real(task, base, head, phase, log)
    reopen(w, mod, gate=gate)
    try:
        w.loop.step()
        return False
    except Killed:
        pass
    ok = not w.pubs() and w.main_src() is None
    reopen(w, mod, gate=gate)
    out = S.run_steps(w)
    drill_note(w, "final_gate_killed", out[-1])
    return ok and out[-1].startswith("published") and w.main_src() == GOOD and len(w.pubs()) == 1


def sc_gate_process_killed(tmp, mod, tag):
    """P: the real gate subprocess (cmd_gate) SIGKILLed: no JSON record -> an `invalid` verdict, never a pass."""
    d = Path(tmp) / ("dE" + tag)
    d.mkdir()
    fake = d / "gate.py"
    fake.write_text("import os, signal\nos.kill(os.getpid(), signal.SIGKILL)\n")
    os.environ["RALPH_A_GATE_CMD"] = "%s %s" % (sys.executable, fake)
    try:
        rec = mod.cmd_gate(TASK, "a" * 40, "b" * 40, "final", root=d, log=d / "g.out")
    finally:
        os.environ.pop("RALPH_A_GATE_CMD", None)
    return rec.get("verdict") == "invalid" and not mod.final_gate_ok(rec)[0] and not mod.build_gate_ok(rec)[0]


def tester_killed_world(tmp, mod, name, lose_state):
    """A World whose first tester pass dies after test_start; returns (world, builds_before_restart)."""
    w = World(tmp, name, mod)
    real_model = w.model
    hit = []

    def model(role, prompt, **kw):
        if role == "test" and not hit:
            hit.append(1)
            raise Killed()
        return real_model(role, prompt, **kw)
    w.model = model
    reopen(w, mod, model=model)
    try:
        w.loop.step()
        raise AssertionError("loop survived the kill")
    except Killed:
        pass
    if lose_state:
        (w.ctl / "state.json").unlink()
    return w


def sc_tester_killed(tmp, mod, tag):
    """T: the tester pass dies: the next pass is the TESTER (no build pass ahead of it), then it publishes."""
    w = tester_killed_world(tmp, mod, "dF" + tag, False)
    n = len(w.calls)
    ok = not w.pubs() and w.main_src() is None
    reopen(w, mod, model=w.loop.model)
    out = S.run_steps(w)
    drill_note(w, "tester_killed", out[-1])
    try:                                                 # the recovered tester pass must not leave the builder blocked FOREVER
        mod.require_tested(w.writer.records())
        unblocked = True
    except mod.NotTested:
        unblocked = False
    return ok and unblocked and [c[0] for c in w.calls[n:]] == ["test"] and out[-1].startswith("published") \
        and w.main_src() == GOOD and len(w.pubs()) == 1


def sc_tester_killed_lost_state(tmp, mod, tag):
    """T: as above with state.json lost too: the builder is still blocked (no build invoked), the tester runs."""
    w = tester_killed_world(tmp, mod, "dG" + tag, True)
    n = len(w.calls)
    reopen(w, mod, model=w.loop.model)
    try:
        w.loop.build_pass(TASK)                          # asked straight for a build pass: refused
        refused = False
    except mod.NotTested:
        refused = True
    ran_ahead = any(c[0] == "build" for c in w.calls[n:])
    out = S.run_steps(w)
    drill_note(w, "tester_killed_lost_state", out[-1])
    roles = [c[0] for c in w.calls[n:]]
    return refused and not ran_ahead and roles == ["test"] and out[-1].startswith("published") and len(w.pubs()) == 1


def sc_tester_retry_killed(tmp, mod, tag):
    """T: attempt 1 ended with no verdict, attempt 2 killed: the earlier test_end must not satisfy the guard."""
    n = []
    w = World(tmp, "dI" + tag, mod)
    real_model = w.model

    def model(role, prompt, **kw):
        if role == "test":
            n.append(1)
            if len(n) == 1:
                return {"rc": 0, "text": "no verdict given"}
            if len(n) == 2:
                raise Killed()
        return real_model(role, prompt, **kw)
    w.model = model
    reopen(w, mod, model=model)
    try:
        w.loop.step()
        return False
    except Killed:
        pass
    (w.ctl / "state.json").unlink()
    reopen(w, mod, model=model)
    c = len(w.calls)
    out = S.run_steps(w)
    drill_note(w, "tester_retry_killed", out[-1])
    return [x[0] for x in w.calls[c:]][:1] == ["test"] and out[-1].startswith("published")


SCENARIOS = [
    ("P planted failing check never reaches main; the repair does", sc_planted),
    ("P a check failing only at the final gate is never published", sc_planted_final),
    ("R build pass killed mid-run (unchecked commit, half-written file): next pass recovers", sc_build_killed),
    ("R build-phase gate killed: next pass recovers", sc_build_gate_killed),
    ("R final gate killed after a tester PASS: main unmoved, restart publishes", sc_final_gate_killed),
    ("P gate process SIGKILLed: invalid verdict, never a pass", sc_gate_process_killed),
    ("T tester pass killed: the next pass is the tester, builder blocked", sc_tester_killed),
    ("T killed tester RETRY after an ended attempt: builder still blocked", sc_tester_retry_killed),
    ("T tester pass killed AND state.json lost: builder still blocked", sc_tester_killed_lost_state),
]

MUTATIONS = [
    ("T recover counts a bare test_start as tested", sc_tester_killed_lost_state,
     '        if open_tester_build(recs[last + 1:]) != bid and any(\n                r.get("event") == "test_end"',
     '        if any(\n                r.get("event") in ("test_start", "test_end")'),
    ("T build_pass lets a started-never-ended tester pass through", sc_tester_killed_lost_state,
     '    if bid:\n        raise NotTested("refused: a tester', '    if False:\n        raise NotTested("refused: a tester'),
    ("T guard matches by build only, not attempt", sc_tester_retry_killed,
     'last[d["build_id"]] = r["event"]', 'last[d["build_id"]] = min(last.get(d["build_id"], "z"), r["event"])'),
    ("T guard matches per attempt: a killed attempt a later attempt finished blocks the builder forever", sc_tester_killed,
     'last[d["build_id"]] = r["event"]', 'last[d["build_id"]] = max(last.get(d["build_id"], ""), r["event"])'),
    ("T both guards removed: the builder runs ahead", sc_tester_killed_lost_state, None, None),
    ("P build-phase gate bypassed", sc_planted, "            ok, why = build_gate_ok(g)\n", "            ok, why = True, 'x'\n"),
    ("R leftover commit of a killed pass read as an empty candidate", sc_build_killed,
     "if head == base else (None, None)", "if True else (None, None)"),
    ("P gate with no JSON read as pass", sc_gate_process_killed,
     '        return {"verdict": "invalid", "steps": {}, "why": "gate printed no JSON record (rc %s)" % r.returncode}',
     '        return {"verdict": "pass", "steps": {}, "why": "x"}'),
    ("P final gate result ignored", sc_planted_final, "        ok, why = final_gate_ok(g)\n",
     "        ok, why = True, 'x'\n"),
]


def double_variant(a, b):
    src = S.SRC
    for old, new in a:
        assert src.count(old) == 1, old
        src = src.replace(old, new)
    import types
    m = types.ModuleType("ralph_a_loop_mut2")
    m.__file__ = str(HERE / "ralph_a_loop.py")
    exec(compile(src, m.__file__, "exec"), m.__dict__)
    return m


def main():
    tmp = Path(tempfile.mkdtemp(prefix="selftest_ralph_a_drill_"))
    TBASE[0] = Path(tempfile.mkdtemp(prefix="selftest_ralph_a_drill_rt_"))
    saved = {k: os.environ.get(k) for k in ("ARENA_ROOT", "ARENA_CLONES", "ARENA_EVENT_TOKEN_FILE",
                                             "ARENA_ANCHOR_FILE", "ARENA_WITNESS", "RM_ARM")}
    os.environ.pop("RM_ARM", None)
    try:
        # the signed log: every drill scenario's record lands in it (and the log verifies)
        p = S._arena_env(tmp, "drill")
        sw = R.SignedWriter(p)
        for name, fn in SCENARIOS:
            check(guarded(fn, tmp, R, ""), "green: " + name)
        for i, (name, fn, old, new) in enumerate(MUTATIONS):
            if old is None:
                mod = double_variant([
                    ('        if open_tester_build(recs[last + 1:]) != bid and any(\n                r.get("event") == "test_end"',
                     '        if any(\n                r.get("event") in ("test_start", "test_end")'),
                    ('    if bid:\n        raise NotTested("refused: a tester', '    if False:\n        raise NotTested("refused: a tester')], None)
            else:
                mod = variant(old, new)
            check(not guarded(fn, tmp, mod, "_m%d" % i), "mutation goes RED: " + name)
        for name, outcome in DRILL:
            sw.emit(R.ARM, "defect", lane="build", run_id="drill", task=TASK["id"],
                    detail={"drill": name, "outcome": outcome})
        got = [(r["detail"]["drill"]) for r in sw.records() if r.get("event") == "defect"]
        want = sorted(n for n, _ in DRILL)
        check(len(want) == 8 and sorted(got) == want and len(set(want)) == 8,
              "the drill is recorded in the signed event log (%d records): %s" % (len(got), sorted(got)))
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
