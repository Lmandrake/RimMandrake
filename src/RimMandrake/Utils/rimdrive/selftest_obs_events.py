"""Selftest for rimdrive.obs_events (observatory S1/S2, design 3.3 tests). Every guarantee has a
red-able counterpart: the test fails if the guarantee is removed.
Run: python3 selftest_obs_events.py"""
import json
import os
import sys
import tempfile
import threading
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))
from rimdrive import obs_events as O  # noqa: E402
from rimdrive.session import Session  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("PASS" if cond else "FAIL", name, detail))
    if not cond:
        FAILS.append(name)


def read(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


class FakeRB(object):
    def __init__(self, behaviour):
        self.behaviour = behaviour

    def call(self, tool, params):
        return self.behaviour(tool, params)


def stub_session(behaviour):
    s = Session.__new__(Session)          # no bridge: only call() is under test
    s.calls = 0
    s._rb = FakeRB(behaviour)
    s._keep_log_alive = lambda tool: None
    s._reconnect = lambda: None
    return s


tmp = tempfile.mkdtemp()

# 1. exact accounting: N logical calls -> exactly N starts and N ends, outcomes classified
sink = O.install("t1", tmp)
s = stub_session(lambda t, p: {"success": False} if t == "bad" else {"success": True})
for i in range(7):
    s.call("good")
s.call("bad")
sink.close()
ev = read(sink.path)
st = [e for e in ev if e["ev"] == "call_start"]
en = [e for e in ev if e["ev"] == "call_end"]
check("8 calls -> 8 starts, 8 ends", len(st) == 8 and len(en) == 8, (len(st), len(en)))
check("no duplicate req ids", len({e["req"] for e in en}) == 8)
check("reply_fail classified", [e["outcome"] for e in en].count("reply_fail") == 1)
check("run_end counts match", ev[-1]["ev"] == "run_end" and ev[-1]["emitted"] == 16 and ev[-1]["dropped"] == 0, ev[-1])
check("end carries latency/t_start/t_end/timeout", all(k in en[0] for k in ("latency_ms", "t_start", "t_end", "timeout", "run_id", "seq")))
check("per-producer seq strictly increasing", [e["seq"] for e in ev] == sorted(e["seq"] for e in ev) and len({e["seq"] for e in ev}) == len(ev))
O.uninstall()

# 2. a call that never returns leaves a call_start with no call_end (the hang is visible)
sink = O.install("t2", tmp)
release = threading.Event()
s = stub_session(lambda t, p: (release.wait(30), {"success": True})[1])
th = threading.Thread(target=lambda: s.call("hangs"), daemon=True)
th.start()
time.sleep(0.6)                               # writer flushes the start while the call is still hung
ev = read(sink.path)
check("hung call: call_start on disk, no call_end", [e["ev"] for e in ev] == ["call_start"], ev)
release.set()
th.join(5)
sink.close()
O.uninstall()

# 3. exception paths still END the call (never a phantom hang), timeout flagged
sink = O.install("t3", tmp)
def boom(t, p):
    if t == "to":
        raise TimeoutError("timed out")
    raise ValueError("x")
s = stub_session(boom)
for t in ("to", "other"):
    try:
        s.call(t)
    except Exception:
        pass
sink.close()
en = [e for e in read(sink.path) if e["ev"] == "call_end"]
check("timeout + error both ended", len(en) == 2 and en[0]["timeout"] is True and en[0]["outcome"] == "timeout" and en[1]["outcome"] == "error", en)
O.uninstall()

# 4. FULL buffer: drops and counts, emit/call never block, even with a stalled sink
gate = threading.Event()
class Stalled(object):
    def write(self, x):
        gate.wait(60)
    def flush(self): pass
    def close(self): pass
sink = O.install("t4", tmp, capacity=10, opener=lambda p: Stalled())
s = stub_session(lambda t, p: {"success": True})
t0 = time.monotonic()
for i in range(500):
    s.call("x")
dt = time.monotonic() - t0
check("500 calls through a stalled sink are not slowed", dt < 2.0, "%.3fs" % dt)
check("full buffer drops and counts", sink.dropped > 900 and sink.emitted == 1000, (sink.emitted, sink.dropped))
t0 = time.monotonic()
sink.close(join_s=1.0)
check("close() is bounded by join_s even when the writer is stalled", time.monotonic() - t0 < 2.0)
gate.set()
O.uninstall()

# 5. a failing sink (cannot open) never raises into the call path
def bad_open(p):
    raise OSError("disk full")
sink = O.install("t5", tmp, opener=bad_open)
s = stub_session(lambda t, p: {"success": True})
ok = True
try:
    for i in range(50):
        s.call("x")
except Exception:
    ok = False
check("unopenable sink: calls unaffected", ok)
time.sleep(0.4)
check("unopenable sink: error counted", sink.write_errors >= 1)
O.uninstall()

# 6. no sink installed: zero overhead path, results unchanged
O.uninstall()
s = stub_session(lambda t, p: {"success": True, "v": 7})
check("no sink: call returns the reply", s.call("x")["v"] == 7 and O.current() is None)

# 7. partial file readable after an abrupt end (no run_end): every line complete JSON
sink = O.install("t7", tmp)
s = stub_session(lambda t, p: {"success": True})
for i in range(5):
    s.call("x")
time.sleep(0.6)
ev = read(sink.path)                          # sink NOT closed == process killed
check("kill mid-run: partial file parses, has no run_end", len(ev) == 10 and ev[-1]["ev"] != "run_end")
O.uninstall()

if FAILS:
    print("\nFAILED: %s" % FAILS)
    sys.exit(1)
print("\nOK: selftest_obs_events")
