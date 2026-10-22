#!/usr/bin/env python3
"""Selftest for pipecheck.py (NORTHSTAR_FAST_DRIVER_1). Offline; a fake bridge, no game.

    python3 src/RimMandrake/Utils/northstar_driver/selftest_pipecheck.py

Falsification: each fault the live proof exists to catch must flip the verdict away from PASS --
a dropped pipelined reply, replies matched to the wrong request, a mutating tool in the batch.
The fake answers pipelined requests in REVERSE order, so a PASS also proves id matching.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import pipecheck as P               # noqa: E402
from transport import TimedTransport  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, detail))
    if not cond:
        FAILS.append(name)


class FakeRB(object):
    """Answers call() serially and _send/_recv_raw pipelined; faults: drop, swap, volatile."""

    def __init__(self, fault=None):
        self.fault, self.queue, self.events, self.n = fault, [], [], 0

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def looks_read_only(self, tool):
        return tool.split("/", 1)[-1].startswith(("get_", "list_"))

    def check_params(self, tool, params):
        return None

    def _answer(self, tool):
        self.n += 1
        if self.fault == "allvolatile":
            return self.n
        r = {"tool": tool, "ticksGame": 1000, "windows": ["a", "b"]}
        if self.fault == "volatile":
            r["now"] = self.n
        if self.fault == "duration":            # agrees on both serial reads, differs pipelined (live 2026-10-21)
            r["operation"] = {"DurationMs": 13 if self.n <= 12 else 16, "Success": True}
        return r

    def call(self, tool, params=None, check=True):
        return self._answer(tool)

    def _send(self, env):
        self.queue.append(env)

    def _recv_raw(self):
        if self.queue:                                  # first read: answer everything sent, reversed
            sent, self.queue = self.queue, []
            replies = [{"type": "response", "id": e["id"],
                        "result": self._answer(e["params"]["name"])} for e in sent]
            if self.fault == "drop":
                replies = replies[1:] + [{"type": "response", "id": "stray", "result": {}}]
            if self.fault == "swap" and len(replies) > 1:
                a, b = replies[0]["result"], replies[1]["result"]
                replies[0]["result"], replies[1]["result"] = b, a
            self.replies = [{"type": "event", "x": 1}] + list(reversed(replies))
        return self.replies.pop(0)


CALLS = [(t, {}) for _ in range(3) for t in ("rimworld/get_game_info", "rimworld/get_ui_state")]


def run(fault=None, calls=CALLS):
    rb = FakeRB(fault)
    return P.check(TimedTransport(rb, pipeline=False), TimedTransport(rb, pipeline=True), calls)


r = run()
check("clean fake, reversed replies -> PASS", r["status"] == "PASS", r["evidence"])
check("event interleaved is not taken for a reply", r["stable"] == len(CALLS), str(r["stable"]))
check("timing fields present", r["serial_ms"] >= 0 and r["pipelined_ms"] >= 0 and "speedup" in r)

r = run("drop")
check("dropped pipelined reply -> FAIL", r["status"] == "FAIL", r["evidence"])

r = run("swap")
check("replies on the wrong request -> FAIL", r["status"] == "FAIL", r["evidence"])

r = run("volatile")
check("a volatile field is ignored, the stable ones still compared -> PASS", r["status"] == "PASS",
      r["evidence"])

r = run("duration")
check("envelope DurationMs that drifts only on the pipelined run is not a FAIL", r["status"] == "PASS",
      r["evidence"])
check("VOLATILE spares game state", not P.VOLATILE.search("/ticksGame") and not P.VOLATILE.search(
    "/operation/Success") and not P.VOLATILE.search("/windows[0]") and not P.VOLATILE.search("/items")
    and not P.VOLATILE.search("/rooms") and not P.VOLATILE.search("/alarms"))
check("VOLATILE still drops millisecond fields", all(P.VOLATILE.search(k) for k in (
    "/waitMs", "/took_ms", "/operation/DurationMs", "/ELAPSED_MS")))


class FakeRetiredRB(FakeRB):
    def check_params(self, tool, params):
        if tool.endswith("list_bad"):
            raise ValueError("bad params for %s" % tool)


rb = FakeRetiredRB()
try:
    TimedTransport(rb, pipeline=True).call_many([("rimworld/get_game_info", {}), ("rimworld/list_bad", {})])
    check("a refused call in a pipelined batch raises", False, "no raise")
except ValueError:
    check("a refused call sends nothing (no orphan replies to desync the stream)", rb.queue == [],
          "%d request(s) on the wire" % len(rb.queue))

r = run("allvolatile")
check("nothing stable -> UNMEASURED, never PASS", r["status"] == "UNMEASURED", r["evidence"])

try:
    run(calls=[("rimworld/spawn_thing", {})])
    check("mutating tool refused", False, "no raise")
except ValueError as ex:
    check("mutating tool refused", "spawn_thing" in str(ex), str(ex))

print("%d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
