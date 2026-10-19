"""Offline selftest of live_session.py: the shared-clock scheduler, the zone plan, the verdict folding, and that --dry-run
and --mock both exit 0.  python3 src/RimMandrake/FlowWorks/northstar/selftest_live_session.py"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import live_session as L  # noqa: E402

FAILS = []


def check(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


class Clock(object):
    def __init__(self, stall_after=None):
        self.t, self.steps, self.stall_after = 0, [], stall_after

    def advance(self, n):
        self.steps.append(n)
        if self.stall_after is None or self.t < self.stall_after:
            self.t += n

    def now(self):
        return self.t


def waiter(n, log, name):
    yield L.Wait(n)
    log.append((name, "woke")),


def poller(clock, at, log):
    w = L.Wait(5000, until=lambda: clock.t >= at, every=100)
    yield w
    log.append(("poll", clock.t, w.timed_out))


def crasher():
    yield L.Wait(10)
    raise RuntimeError("boom")


# 1. three blocks each waiting 1,500 ticks cost 1,500 ticks, not 4,500 (the compression the session is built on)
c, log = Clock(), []
res, spent = L.run_shared({k: waiter(1500, log, k) for k in ("a", "b", "c")}, c.advance, c.now, log=lambda s: None)
check(spent == 1500 and all(v == "done" for v in res.values()), "parallel waits share one clock (%d ticks)" % spent)

# 2. a poll wakes as soon as its condition holds (within one poll period), and does not time out
c, log = Clock(), []
res, spent = L.run_shared({"p": poller(c, 730, log)}, c.advance, c.now, log=lambda s: None)
check(log and 730 <= log[0][1] <= 830 and log[0][2] is False, "until-poll wakes near its condition: %s" % log)

# 3. a poll whose condition never holds times out at its budget and says so
c, log = Clock(), []
res, spent = L.run_shared({"p": poller(c, 10 ** 9, log)}, c.advance, c.now, log=lambda s: None)
check(log and log[0][2] is True and spent == 5000, "never-true poll times out at 5000: %s spent %d" % (log, spent))

# 4. one crashing block never stops the others
c, log = Clock(), []
res, spent = L.run_shared({"x": crasher(), "a": waiter(300, log, "a")}, c.advance, c.now, log=lambda s: None)
check(res["x"].startswith("crashed") and res["a"] == "done", "a crash is isolated: %s" % res)

# 5. a clock that stops moving (live day 4: 0-tick steps) voids every waiting block instead of spinning
c, log = Clock(stall_after=0), []
res, spent = L.run_shared({"a": waiter(1000, log, "a")}, c.advance, c.now, log=lambda s: None)
check(res["a"].startswith("clock stalled"), "a stalled clock is reported: %s" % res)

# 5b. a block that FINISHES early never shrinks the later steps to 1 tick (live 2026-10-19: a finished block's stale
#     deadline left in `due` made B4 crawl one tick per call)
c, log = Clock(), []
res, spent = L.run_shared({"short": waiter(10, log, "s"), "long": waiter(3000, log, "l")}, c.advance, c.now, log=lambda s: None)
check(spent == 3000 and len(c.steps) <= 4, "a finished block leaves big steps: %d steps %s" % (len(c.steps), c.steps[:6]))

# 6. the zone plan: shared zones disjoint from each other and from the owner zone, all inside the map margins
z = L.plan_zones((250, 250))
shared = [z[n] for n in L.SHARED]
ok = all(not L.overlaps(a, b, 2) for i, a in enumerate(shared) for b in shared[i + 1:])
ok = ok and all(not L.overlaps(a, z["owner"], 2) for a in shared)
inside = all(r[0] >= 15 and r[1] >= 15 and r[0] + r[2] <= 235 and r[1] + r[3] <= 235 for r in z.values())
check(ok and inside, "zones disjoint and inside the 15-cell margin")
try:
    L.plan_zones((150, 150))
    check(False, "a too-small map refuses the plan")
except ValueError:
    check(True, "a too-small map refuses the plan")

# 7. verdict folding: any FAIL fails; all PASS passes; PASS + UNMEASURED is partial; OWED/SKIP give nothing
rows = [dict(id="r1", item="I", criterion="A1", status="PASS", cls="MOD"),
        dict(id="r2", item="I", criterion="A1", status="UNMEASURED", cls="HARNESS"),
        dict(id="r3", item="J", criterion="A2", status="PASS", cls="MOD"),
        dict(id="r4", item="J", criterion="A2", status="FAIL", cls="MOD"),
        dict(id="r5", item="K", criterion="A3", status="UNMEASURED", cls="OWED"),
        dict(id="r6", item="M", criterion="A4", status="PASS", cls="MOD")]
v = L.verdicts(rows)
check(v.get(("I", "A1"), ("",))[0] == "partial" and v.get(("J", "A2"), ("",))[0] == "fail"
      and ("K", "A3") not in v and v.get(("M", "A4"), ("",))[0] == "pass", "verdict folding: %s" % v)

# 8. every catalog row names a block the driver knows (or an explicit out-of-load bucket)
known = {b["id"] for b in L.BLOCKS} | {"OUT", "LATER", "P10"}
check(all(c["block"] in known for c in L.C), "catalog blocks are all known")

# 9. --dry-run and --mock exit 0 offline
for flag in ("--dry-run", "--mock"):
    d = tempfile.mkdtemp(prefix="ls_selftest_")
    r = subprocess.run([sys.executable, os.path.join(HERE, "live_session.py"), flag, "--no-owner-save", "--out-dir", d],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, timeout=600)
    check(r.returncode == 0 and "Traceback" not in r.stdout, "%s exits 0 with no traceback" % flag)

print("PASS: 0 failure(s)" if not FAILS else "FAIL: %d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
