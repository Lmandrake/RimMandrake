#!/usr/bin/env python3
"""Selftest for clockgate.py. Offline: a scripted FakeClockSession stands in
for the bridge. Run: python3 selftest_clockgate.py  (prints N/N passed)."""
import json
import os
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import clockgate as cg  # noqa: E402

RESULTS = []


def ok(cond, label):
    print("%-4s %s" % ("ok" if cond else "FAIL", label))
    RESULTS.append((bool(cond), label))


def raises(exc, fn):
    try:
        fn()
    except exc:
        return True
    except Exception:
        return False
    return False


class FakeClockSession:
    """Scripted bridge. mode: 'normal' | 'truncate' | 'overshoot' | 'stall'
    | 'jump_back'. `running_drift` ticks are added on every time_clock read
    while not paused (simulates a game that is really running)."""

    def __init__(self, tick=1000, mode="normal", paused=True,
                 running_drift=0):
        self.tick, self.mode, self.paused = tick, mode, paused
        self.running_drift = running_drift
        self.calls = []

    def call(self, tool, **p):
        self.calls.append((tool, p))
        if tool == "jawa/time_clock":
            if not self.paused:
                self.tick += self.running_drift
            return {"success": True, "ticksGame": self.tick,
                    "paused": self.paused,
                    "curTimeSpeed": "Normal"}  # real bridge: paused flag, speed stays Normal
        if tool == "rimworld/step_game_ticks":
            n = p["ticks"]
            if self.mode == "truncate":
                n = max(1, n // 2)
            elif self.mode == "overshoot":
                n = n + 7
            elif self.mode == "stall":
                n = 0
            elif self.mode == "jump_back":
                self.tick = 50
                return {"success": True}
            self.tick += n
            return {"success": True}
        if tool == "rimworld/pause_game":
            self.paused = bool(p.get("pause"))
            return {"success": True}
        return {"success": False}

    def steps(self):
        return [c for c in self.calls if c[0] == "rimworld/step_game_ticks"]


def test_between_call_ticks_charged():
    s = FakeClockSession(1000)
    g = cg.ClockGate(10000)
    ok(g.observe(1000) == 0, "first observation sets base, charges nothing")
    s.tick = 1250  # time passed while nobody was looking
    ok(g.observe(1250) == 250 and g.component_spent == 250,
       "ticks between calls are charged")
    # sanity probe: a gate that ignored between-call drift would read 0
    ok(g.observe(1250) == 0, "probe: re-observing the same tick charges 0")


def test_step_charges_measured_and_records_overshoot():
    s = FakeClockSession(0, mode="overshoot")
    g = cg.ClockGate(10000)
    with g.frame("component", 5000):
        adv = cg.step(s, g, 100, chunk=50)
    ch = [e for e in g.entries if e["reason"] == "step"]
    ok(g.component_spent == adv == s.tick, "step charges measured delta "
       "(%d), not requested 100" % adv)
    ok(adv > 100 and all(e.get("overshoot") == 7 for e in ch),
       "overshoot recorded on every charge")
    s2 = FakeClockSession(0)
    g2 = cg.ClockGate(10000)
    cg.step(s2, g2, 100, chunk=50)
    ok(all("overshoot" not in e for e in g2.entries),
       "probe: exact stepping records no overshoot")


def test_truncation_is_looped():
    s = FakeClockSession(0, mode="truncate")
    g = cg.ClockGate(10000)
    adv = cg.step(s, g, 200, chunk=100)
    ok(adv >= 200 and len(s.steps()) > 2,
       "truncated steps are re-issued until the real clock moved n")


def test_negative_delta_new_epoch():
    g = cg.ClockGate(10000)
    g.observe(5000)
    g.observe(5100)
    before = g.component_spent
    d = g.observe(40)
    ok(d == 0 and g.epoch == 1 and g.component_spent == before,
       "negative delta => epoch+1, zero charge, nothing negative")
    ok(any(e["kind"] == "epoch" and e["tick_to"] == 40 for e in g.entries),
       "epoch change recorded in ledger")
    g.observe(9000, epoch_change=True)
    ok(g.epoch == 2 and g.component_spent == before,
       "flagged forward jump also starts an epoch, charges nothing")
    ok(g.observe(9060) == 60 and g.component_spent == before + 60,
       "charging resumes from the new base")
    s = FakeClockSession(1000, mode="jump_back")
    g2 = cg.ClockGate(10000)
    ok(raises(cg.ClockLost, lambda: cg.step(s, g2, 100)),
       "a save/load mid-step aborts the step instead of freeing time")


def test_overhead_counts_against_session_cap():
    g = cg.ClockGate(1000)
    g.observe(0)
    with g.frame("component", 900):
        with g.overhead():
            g.observe(700, reason="helper")
        ok(g.overhead_spent == 700 and g.component_spent == 0,
           "overhead tick lands in the overhead ledger only")
        ok(g.remaining() == 300, "remaining() = min(frame 900, session 300)")
        g.observe(1100, reason="work")
        ok(raises(cg.BudgetExceeded, g.check),
           "overhead + component beyond the hard session cap raises")
    g2 = cg.ClockGate(1000)
    g2.observe(0)
    g2.observe(700)
    ok(not raises(cg.BudgetExceeded, g2.check),
       "probe: 700 of 1000 with no overhead does not raise")
    g3 = cg.ClockGate(10000)
    g3.observe(0)
    with g3.frame("chain", 100):
        g3.observe(150)
        try:
            g3.check()
            e = None
        except cg.BudgetExceeded as ex:
            e = ex
    ok(e is not None and e.scope == "chain" and e.spent == 150
       and e.cap == 100, "BudgetExceeded carries scope, spent, cap")


def test_refuses_before_spending():
    s = FakeClockSession(0)
    g = cg.ClockGate(10000)
    with g.frame("component", 300):
        r = raises(cg.BudgetExceeded, lambda: cg.step(s, g, 301, chunk=100))
        ok(r and not s.steps(),
           "over-cap request refused with ZERO step calls made")
        cg.step(s, g, 300, chunk=100)
        ok(s.tick == 300 and g.remaining() == 0,
           "probe: a request exactly at remaining() runs")
    # chunk is capped by remaining()
    s = FakeClockSession(0)
    g = cg.ClockGate(10000)
    with g.frame("component", 250):
        cg.step(s, g, 250, chunk=1000)
    ok(max(c[1]["ticks"] for c in s.steps()) <= 250,
       "chunk never exceeds remaining()")


def test_stall():
    s = FakeClockSession(0, mode="stall")
    g = cg.ClockGate(10000)
    ok(raises(cg.ClockStall, lambda: cg.step(s, g, 100)),
       "ClockStall raised on zero movement")
    ok(len(s.steps()) == 3, "after exactly K=3 attempts (got %d)"
       % len(s.steps()))


def test_lease():
    g = cg.ClockGate(100)
    ok(raises(cg.UnleasedTickMove, g.assert_leased),
       "unleased tick move refused")
    with g.lease("x"):
        ok(not raises(cg.UnleasedTickMove, g.assert_leased),
           "leased tick move allowed")
    ok(raises(cg.UnleasedTickMove, g.assert_leased),
       "lease ends with its context")
    seen = []
    cg.step(FakeClockSession(0), g, 10,
            on_chunk=lambda now: seen.append(g._lease_depth))
    ok(seen and seen[0] > 0, "step() holds a lease while it moves ticks")


def test_on_chunk_hook_and_abort():
    s = FakeClockSession(0)
    g = cg.ClockGate(10000)
    nows = []
    cg.step(s, g, 300, chunk=100, on_chunk=nows.append)
    ok(nows == [100, 200, 300], "on_chunk called after each chunk")

    class Stop(Exception):
        pass

    def boom(now):
        raise Stop()
    s = FakeClockSession(0)
    g = cg.ClockGate(10000)
    ok(raises(Stop, lambda: cg.step(s, g, 300, chunk=100, on_chunk=boom))
       and len(s.steps()) == 1, "hook may raise to abort the step")


def test_verify_pause():
    frozen = FakeClockSession(500, paused=True)
    ok(cg.verify_pause(frozen, sleep=lambda s: None),
       "frozen ticks + paused flag => verified")
    moving = FakeClockSession(500, paused=True, running_drift=3)
    # flag says paused but ticks creep: simulate by drifting while 'paused'
    orig = moving.call

    def creeping(tool, **p):
        r = orig(tool, **p)
        if tool == "jawa/time_clock":
            moving.tick += 3
        return r
    moving.call = creeping
    ok(not cg.verify_pause(moving, sleep=lambda s: None),
       "ticks moving between samples => NOT paused despite the flag")
    flag_off = FakeClockSession(500, paused=False)
    ok(not cg.verify_pause(flag_off, sleep=lambda s: None),
       "paused flag false => not verified")
    # equal first two reads, third differs -> two equal reads are not proof
    seq = iter([500, 500, 509])
    s = FakeClockSession(500, paused=True)

    def scripted(tool, **p):
        if tool == "jawa/time_clock":
            return {"ticksGame": next(seq), "paused": True,
                    "curTimeSpeed": "Paused"}
        return {}
    s.call = scripted
    ok(not cg.verify_pause(s, samples=3, sleep=lambda x: None),
       "two equal reads then a move is caught by the third sample")
    # ensure_paused retries via pause_game
    s = FakeClockSession(500, paused=False)
    ok(cg.ensure_paused(s, sleep=lambda x: None)
       and any(c[0] == "rimworld/pause_game" and c[1] == {"pause": True}
               for c in s.calls), "ensure_paused issues pause_game(pause=True)")
    s = FakeClockSession(500, paused=False)
    s.call = lambda tool, **p: {"ticksGame": 1, "paused": False}
    ok(raises(cg.PauseUnverified,
              lambda: cg.ensure_paused(s, tries=2, sleep=lambda x: None)),
       "ensure_paused raises PauseUnverified when pause never takes")


def test_supervisor():
    main = threading.current_thread()
    got = {}

    def expire():
        got["thread"] = threading.current_thread()
    killed = []
    with cg.Supervisor(0.05, expire, kill_worker=lambda: killed.append(1)) \
            as sv:
        sv.done.wait(2)
    ok(sv.expired and got.get("thread") is not main
       and got["thread"] is not None and killed == [1],
       "supervisor fires on_expire (and kill_worker) from another thread")
    ok(sv.reason and "expired" in sv.reason, "expiry reason recorded")

    fired = []
    with cg.Supervisor(0.3, lambda: fired.append(1)) as sv2:
        pass  # stopped immediately
    time.sleep(0.45)
    ok(not fired and not sv2.expired, "a stopped supervisor never fires")

    def bad():
        raise RuntimeError("x")
    with cg.Supervisor(0.02, bad) as sv3:
        sv3.done.wait(2)
    ok(sv3.expired and isinstance(sv3.error, RuntimeError),
       "a failing on_expire is recorded, not lost")


def test_ledger_roundtrip():
    s = FakeClockSession(0, mode="overshoot")
    g = cg.ClockGate(10000)
    with g.frame("suite", 9000):
        with g.frame("component", 500):
            cg.step(s, g, 100, chunk=50)
            with g.overhead():
                g.observe(s.tick + 40, reason="helper")
            g.observe(5, reason="reload")
            d = g.as_dict()
    back = json.loads(json.dumps(d))
    ok(back == d, "as_dict round-trips through json unchanged")
    kinds = {e["kind"] for e in d["entries"]}
    ok(kinds == {"charge", "epoch"} and d["epoch"] == 1
       and d["overhead_spent"] == 40
       and all("reason" in e and "tick_from" in e and "tick_to" in e
               for e in d["entries"]),
       "ledger lists charges+epochs with reason, epoch, tick range")
    ok(any(e["scope"] == ["suite", "component"] for e in d["entries"]
           if e["kind"] == "charge" and e["ledger"] == "component"),
       "component charges name every open frame")


def main():
    for t in (test_between_call_ticks_charged,
              test_step_charges_measured_and_records_overshoot,
              test_truncation_is_looped,
              test_negative_delta_new_epoch,
              test_overhead_counts_against_session_cap,
              test_refuses_before_spending,
              test_stall, test_lease, test_on_chunk_hook_and_abort,
              test_verify_pause, test_supervisor, test_ledger_roundtrip):
        try:
            t()
        except Exception as e:  # a crashing test is a failed check
            ok(False, "%s crashed: %r" % (t.__name__, e))
    n = sum(1 for r, _ in RESULTS if r)
    print()
    print("%d/%d passed" % (n, len(RESULTS)))
    if n != len(RESULTS):
        for r, label in RESULTS:
            if not r:
                print("  - FAIL:", label)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
