#!/usr/bin/env python3
"""selftest_signal_watch.py -- the failed-unit, unfiled-alarm and standing-flag answers of signal_watch.py."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import signal_watch as SW  # noqa: E402

SCH = {"signal_watch": {"enabled": True, "ops_dir": "/nonexistent"}}
H, DAY = 3600, 86400
T0 = 100 * DAY + 5 * H


def ts(s):
    return float(s) if s is not None else None


def run(failed=(), timers=(), alarms=None, flags=None, st=None, now=T0, reading=True, paused=None, sch=SCH):
    st = {} if st is None else st
    acts = []
    alarms = {} if alarms is None else alarms
    flags = {"flags": []} if flags is None else flags
    if isinstance(flags, dict) and "at" not in flags:
        flags = dict(flags, at=str(now))
    obs = {"paused": paused, "signals": {"units": lambda: (list(failed), list(timers)) if reading else None,
                                         "alarms": lambda: alarms, "flags": lambda: flags}}
    SW.step(sch, st, obs, now, lambda **a: acts.append(a), str, ts)
    return acts, st


def test_gates():
    assert run(failed=["a.scope"], paused="x")[0] == []
    assert run(failed=["a.scope"], sch={})[0] == []
    _, st = run(failed=["a.scope"])
    assert run(failed=["a.scope"], st=st, now=T0 + 299)[0] == [], "throttled"
    acts, _ = run(reading=False)
    assert [a["kind"] for a in acts] == ["signal:units"], "no reading is said, never read as all clear"


def test_plan():
    c = SW.config(SCH)
    assert SW.plan(c, "rm-harness-1.scope", []) == "reset"
    assert SW.plan(c, "rm-scratch-reap.service", ["rm-scratch-reap.timer"]) == "start"
    assert SW.plan(c, "rm-scratch-reap.service", []) is None, "no timer: nothing says starting it is safe"
    assert SW.plan(c, "rm-selftests-nightly.service", ["rm-selftests-nightly.timer"]) is None, "not on the allow list"
    assert SW.plan(c, "Login-1.scope", []) is None, "the deny list ignores case"
    for u in ("rm-login-watch.service", "rm-account-switch.service", "rm-role-operations-1.service", "rm-role-1.scope"):
        assert SW.plan(c, u, [u.rsplit(".")[0] + ".timer"]) is None, u


def test_repair_bounded_then_alarm():
    u = "rm-pulse-update.service"
    st, kinds, now = {}, [], T0
    for i in range(4):
        acts, st = run([u], ["rm-pulse-update.timer"], st=st, now=now + i * 2000)
        kinds.append([(a["do"]) for a in acts])
    assert kinds == [["unit_repair"], ["unit_repair"], ["alarm"], ["alarm"]], kinds   # execute rate-limits the repeat
    acts, _ = run([u], ["rm-pulse-update.timer"], st=st, now=T0 + DAY)
    assert [a["do"] for a in acts] == ["unit_repair"], "a new day: a new repair"
    a = run([u], ["rm-pulse-update.timer"], now=T0)[0][0]
    assert a["how"] == "start"


def test_untouchable_alarms_after_standing():
    u = "rm-role-9.service"
    acts, st = run([u])
    assert acts == []
    acts, st = run([u], st=st, now=T0 + H)
    assert acts[0]["kind"] == "timer:" + u and acts[0]["conductor_log"] and "no safe" in acts[0]["why"]
    _, st = run([], st=st, now=T0 + DAY)
    assert st["signals"]["units"] == {}, "a unit that left is forgotten when its day ends"


def test_recovery_keeps_the_limit():
    u = "rm-pulse-update.service"
    st, kinds = {}, []
    for i in range(12):                     # fail, repair, recover, fail again: the unit flaps inside one day
        acts, st = run([u] if i % 2 == 0 else [], ["rm-pulse-update.timer"], st=st, now=T0 + i * 900)
        kinds += [a["do"] for a in acts]
    assert kinds.count("unit_repair") == 2 and "alarm" in kinds, kinds


def test_a_raising_reader_costs_only_itself():
    def boom():
        raise OSError("x")
    acts = []
    so = {"units": boom, "alarms": lambda: {}, "flags": boom}
    SW.step(SCH, {}, {"paused": None, "signals": so}, T0, lambda **a: acts.append(a), str, ts)
    assert [a["kind"] for a in acts] == ["signal:units", "signal:flags"], acts


def test_give_back_and_repair():
    _, st = run(["a.scope"])
    SW.give_back(st, {"unit": "a.scope"})
    assert st["signals"]["units"]["a.scope"]["n"] == 0
    SW.give_back(st, {"unit": "gone"})

    class R:
        def __init__(self, rc, err=""):
            self.returncode, self.stderr = rc, err
    calls = []
    assert SW.repair({"unit": "u", "how": "start"}, lambda a: calls.append(a) or R(0)).startswith("repaired")
    assert calls == [("reset-failed", "u"), ("start", "--no-block", "u")]
    calls.clear()
    assert SW.repair({"unit": "u", "how": "reset"}, lambda a: calls.append(a) or R(0)).startswith("repaired")
    assert calls == [("reset-failed", "u")]
    assert SW.repair({"unit": "u", "how": "start"}, lambda a: R(1, "nope")) == "FAILED: reset-failed: nope"

    def boom(a):
        raise OSError
    assert SW.repair({"unit": "u", "how": "reset"}, boom).startswith("FAILED")


def test_files():
    alarms = {"T:a": {"state": "PENDING", "error": "ModuleNotFoundError", "tries": 3},
              "T:b": {"state": "PENDING", "error": "x", "tries": 2},
              "T:c": {"state": "OPEN", "error": "x", "tries": 9}, "bad": 3}
    acts, _ = run(alarms=alarms)
    assert [a["kind"] for a in acts] == ["ops:file_failed:T:a"] and acts[0]["conductor_log"]


def test_flags():
    now = T0 + 10 * DAY
    fl = {"flags": [{"key": "k", "rule": "run", "since": str(T0), "detail": "d"},
                    {"key": "k", "rule": "target", "since": str(T0), "alarm": False},
                    {"key": "young", "rule": "run", "since": str(now + 7 * DAY)},
                    {"key": "filed", "rule": "run", "since": str(T0)},
                    {"key": "filed", "rule": "target", "since": str(T0), "alarm": True},
                    {"key": "nosince", "rule": "band"}, "junk"]}
    acts, st = run(flags=fl, now=now)
    assert [a["kind"] for a in acts] == ["ops:flag:k"], acts
    assert not acts[0].get("conductor_log"), "first answer: Operations"
    assert run(flags=fl, st=st, now=now + 6 * DAY)[0] == []
    acts, _ = run(flags=fl, st=st, now=now + 7 * DAY + 1)
    assert acts[0]["conductor_log"], "the note did not move it: now the Conductor"
    assert run()[0] == []
    _, st = run(flags={"flags": []}, st=st, now=now + 8 * DAY)
    assert st["signals"]["flags"] == {}, "a cleared flag starts over"


def test_blind_and_isolated():
    assert [a["kind"] for a in run(alarms="{")[0]] == ["signal:alarms"]
    assert [a["kind"] for a in run(flags="x")[0]] == ["signal:flags"]
    fl = {"flags": [{"key": "k", "since": str(T0 - 9 * DAY)}]}
    assert [a["kind"] for a in run(flags=dict(fl, at=str(T0 - DAY)))[0]] == ["signal:flags"], "a frozen snapshot is no standing flag"
    acts, _ = run(alarms={"a": {"state": "PENDING", "error": "e", "tries": "3"}}, flags=fl, st={"signals": {"units": ["bad"]}})
    assert [a["kind"] for a in acts] == ["ops:flag:k"], acts
    acts, _ = run(failed=["a.scope"], flags=fl, alarms={"b": {"state": "PENDING", "error": "e", "tries": 3}},
                  st={"signals": {"flags": 7}})
    kinds = [a.get("kind") for a in acts]
    assert "ops:file_failed:b" in kinds and "signal:flags" in kinds and None in kinds, kinds


if __name__ == "__main__":
    n = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            n += 1
    print("selftest_signal_watch: %d/%d" % (n, n))
