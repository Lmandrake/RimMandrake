#!/usr/bin/env python3
"""selftest_focus_cap.py - the Producer's WIP cap held by `rimflow next` (RO2, FOCUS_CAP_ENFORCE_IN_RIMFLOW_NEXT).

    python3 src/RimMandrake/rimflow/selftest_focus_cap.py

The planted fault runs on the real path: cli.py as a subprocess on a throwaway ledger, a schedule copied from the real
dispatcher_schedule.json so the number under test is the shipped one. N+1 ready items and N started: `next` offers no new
item; a dated wait frees one place; a third wait is refused; an expired wait counts again. Relentless reads the same key.
"""
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rimflow import model, priority, relentless  # noqa: E402

CLI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cli.py")
REAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dispatcher_schedule.json")
FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


class Sandbox(object):
    def __init__(self, **over):
        self.d = tempfile.mkdtemp(prefix="focus-cap-")
        self.ledger = os.path.join(self.d, "ledger")
        os.makedirs(self.ledger)
        self.sched = os.path.join(self.d, "schedule.json")
        with open(REAL) as f:
            c = json.load(f)["focus_cap"]
        c.update(over)
        self.cap = c
        with open(self.sched, "w") as f:
            json.dump({"focus_cap": c}, f)
        self.env = dict(os.environ, RIMFLOW_LEDGER=os.path.join(self.ledger, "events.jsonl"), RIMFLOW_SCHEDULE=self.sched,
                        RIMFLOW_ITEMS=os.path.join(self.d, "items"), RM_PRIORITY_LIST=os.path.join(self.d, "no_list.json"))

    def run(self, *a, seat="FOUNDRY"):
        return subprocess.run([sys.executable, CLI] + list(a), env=dict(self.env, RIMFLOW_SEAT=seat), capture_output=True,
                              text=True, timeout=120, stdin=subprocess.DEVNULL)

    def ok(self, *a, seat="FOUNDRY"):
        r = self.run(*a, seat=seat)
        assert r.returncode == 0, "%s: %s %s" % (a, r.stdout[-400:], r.stderr[-400:])
        return r.stdout

    def item(self, i, start=False):
        """Filed and, with `start`, claimed and started. A claim takes a lease, so a claimed item is already focus."""
        self.ok("file", i, "--for", "FOUNDRY", "--kind", "task", "--title", "t", "--target", "v1", seat="BENCH")
        if start:
            self.ok("claim", i)
            self.ok("start", i)


def offered(out):
    """The first item line, by the Dispatcher's own parser: what a ring would act on."""
    from rimflow import dispatcher
    return dispatcher.parse_peek(out).get("id")


def planted_overflow():
    x = Sandbox()
    n, waits = x.cap["per_seat"], x.cap["waits_max"]
    check(n >= 1 and waits == 2, "the shipped schedule holds the number: per_seat %d, waits_max %d" % (n, waits))
    focus = ["PLANT%s_FIX_STILL_OPEN" % "ABCDEFGHIJ"[k] for k in range(n + 1)]
    for i in focus[:n - 1]:
        x.item(i, start=True)
    x.item("FRESH_FIX_NOT_STARTED")
    out = x.ok("next", "--peek")
    check(offered(out) == "FRESH_FIX_NOT_STARTED" and "FOCUS CAP" not in out, "under the cap a new item is offered")

    x.item(focus[n - 1], start=True)    # the Nth: the planted fault is a fresh item ranked while N are open
    out = x.ok("next", "--peek")
    check("FOCUS CAP" in out and offered(out) != "FRESH_FIX_NOT_STARTED", "at %d focus items `next` offers no new item" % n)
    why = x.ok("why", "FRESH_FIX_NOT_STARTED")
    check("FOCUS CAP" in why, "`why` names the cap")
    check("ALSO" not in x.ok("next", "--peek"), "not even on an ALSO line")

    bad = x.run("wait", "FRESH_FIX_NOT_STARTED", "--until", "2099-01-01", "--reason", "x")
    check(bad.returncode != 0 and "not a focus item" in bad.stdout + bad.stderr, "a wait on a non-focus item frees nothing: refused")
    bad = x.run("wait", focus[0], "--until", "2001-01-01", "--reason", "x")
    check(bad.returncode != 0, "a past date is refused")
    bad = x.run("wait", focus[0], "--until", "soon", "--reason", "x")
    check(bad.returncode != 0, "a wait with no date is refused")

    x.ok("wait", focus[0], "--until", "2099-01-01", "--reason", "Steve job")
    out = x.ok("next", "--peek")
    check("FOCUS CAP" not in out and offered(out) == "FRESH_FIX_NOT_STARTED", "a dated wait frees one place")
    check("WAITING until" in x.ok("why", focus[0]), "`why` names the wait")

    x.ok("claim", "FRESH_FIX_NOT_STARTED")
    x.ok("start", "FRESH_FIX_NOT_STARTED")     # the place is taken, back at N
    check("FOCUS CAP" in x.ok("next", "--peek"), "the freed place is one place")
    x.ok("wait", focus[1], "--until", "2099-01-01", "--reason", "owner")
    bad = x.run("wait", "FRESH_FIX_NOT_STARTED", "--until", "2099-01-01", "--reason", "third")
    check(bad.returncode != 0 and "wait refused" in bad.stdout + bad.stderr, "a third wait is refused")
    w = model.replay(model_read(x))
    check(not w.items["FRESH_FIX_NOT_STARTED"].wait_until, "the refused wait wrote nothing")
    x.ok("wait", focus[0], "--until", "2099-06-01", "--reason", "re-dated")     # not a third: same item
    x.ok("unwait", focus[1])
    x.ok("wait", "FRESH_FIX_NOT_STARTED", "--until", "2099-01-01", "--reason", "now it fits")


def model_read(x):
    """The sandbox's whole ledger: every file under it, as a bare model.read() here would read the real one."""
    evs = []
    for root, _dirs, files in os.walk(x.ledger):
        for name in files:
            if name.endswith(".jsonl"):
                evs.extend(model.read(os.path.join(root, name)))
    assert evs, "the sandbox ledger read empty"
    return evs


def expired_wait_and_history():
    x = Sandbox(per_seat=2)
    x.item("APLANT_FIX_STILL_OPEN", start=True)
    x.item("BPLANT_FIX_STILL_OPEN", start=True)
    w = model.replay(model_read(x))
    now = model.epoch_now()
    a, b = w.items["APLANT_FIX_STILL_OPEN"], w.items["BPLANT_FIX_STILL_OPEN"]
    check(len(priority.focus_items(w, "FOUNDRY", now, x.cap["since"])) == 2, "started items count as focus")
    check(priority.focus_items(w, "FOUNDRY", now, "2099-01-01") == [], "`doing` older than since is history, not focus")
    a.wait_until = "2099-01-01T00:00:00Z"
    check(not priority.is_focus(a, now, x.cap["since"]), "a running wait is out of the count")
    a.wait_until = "2001-01-01T00:00:00Z"
    check(priority.is_focus(a, now, x.cap["since"]) and not priority.wait_running(a, now), "an expired wait counts again")
    b.blocked = True
    check(priority.is_focus(b, now, x.cap["since"]), "a block does not free a place")
    a.state = "built"
    check(not priority.is_focus(a, now, x.cap["since"]), "built work is not focus")


def unlisted_seat_and_damage():
    x = Sandbox(seats=["FOUNDRY"], per_seat=1)
    x.ok("file", "BENCHA_FIX_STILL_OPEN", "--for", "BENCH", "--kind", "task", "--title", "t", seat="BENCH")
    x.ok("claim", "BENCHA_FIX_STILL_OPEN", seat="BENCH")
    x.ok("start", "BENCHA_FIX_STILL_OPEN", seat="BENCH")
    x.ok("file", "BENCHB_FIX_STILL_OPEN", "--for", "BENCH", "--kind", "task", "--title", "t", seat="BENCH")
    x.ok("claim", "BENCHB_FIX_STILL_OPEN", seat="BENCH")
    check("FOCUS CAP" not in x.ok("next", "--peek", seat="BENCH"), "a seat not listed is not capped")
    with open(x.sched, "w") as f:
        f.write('{"focus_cap": {"per_seat": 0}}')
    r = x.run("next", "--peek")
    check(r.returncode != 0 and "focus cap is unknown" in r.stdout + r.stderr, "a damaged cap refuses, never lifts in silence")


def relentless_reads_the_same_number():
    x = Sandbox()
    os.environ["RIMFLOW_SCHEDULE"] = x.sched
    try:
        fx = relentless.Effects.__new__(relentless.Effects)
        n = relentless.Effects.focus_cap(fx)
        check(n == x.cap["per_seat"], "relentless reads focus_cap.per_seat: %s" % n)

        class F(object):
            focus_cap = staticmethod(lambda: n)

            @staticmethod
            def mem_gb():
                return 99

        check(relentless.worker_cap(F, {"max_workers": 10}) == n, "the number is the ceiling on its places")
        check(relentless.worker_cap(F, {"max_workers": 10}, extra=1) == n + 1, "a check still runs on top")
        with open(x.sched, "w") as f:
            f.write("{broken")
        check(relentless.Effects.focus_cap(fx) == 1, "damaged: the lowest, not unlimited")
    finally:
        del os.environ["RIMFLOW_SCHEDULE"]


def main():
    planted_overflow()
    expired_wait_and_history()
    unlisted_seat_and_damage()
    relentless_reads_the_same_number()
    print("FAILS: %d" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
