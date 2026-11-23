#!/usr/bin/env python3
"""selftest_dispatcher_blocked_top_cursor.py - a Dispatcher door the v3 audit found unproven (T15,
DISPATCHER_PROVE_BLOCKED_TOP_AND_CURSOR; design/RimMandrake/dispatcher_risk_response_2026-10-29.md R03 and T15).

    python3 src/RimMandrake/rimflow/selftest_dispatcher_blocked_top_cursor.py

1. A BLOCKED TOP ITEM DOES NOT HIDE LOWER WORK. Real path: cli.py on a throwaway ledger, read by the Dispatcher's own
   dispatcher.peek_ticket (the subprocess `rimflow next --peek` + parse_peek the tick runs), then dispatcher.decide
   rings the stalled seat with that ticket. The planted fault is the block itself: the raised item is offered first
   while clear (the instrument can see it), and once blocked the lower offline item is the ticket and the ring. Same
   for a top item blocked `--on` an open predecessor; all blocked -> {} and no ring; unblocked -> back on top.
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import selftest_dispatcher as SD  # noqa: E402  (sets the throwaway dispatcher state dirs first)
import dispatcher as D  # noqa: E402
import role_launch as RL  # noqa: E402

CLI = os.path.join(HERE, "cli.py")
FAILS = []
TOP, LOW = "TOPPER_FIX_STUCK_FAST", "LOWER_FIX_STILL_WAITING"


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


# ---------------------------------------------------------------- 1. blocked top item

class Ledger(object):
    """A throwaway ledger the real cli.py and dispatcher.peek_ticket both read (env, as the tick's subprocess does)."""

    def __init__(self):
        self.d = tempfile.mkdtemp(prefix="blocked-top-")
        os.makedirs(os.path.join(self.d, "ledger"))
        sch = os.path.join(self.d, "schedule.json")
        with open(sch, "w") as f:
            f.write("{}")
        self.env = {"RIMFLOW_LEDGER": os.path.join(self.d, "ledger", "events.jsonl"), "RIMFLOW_SCHEDULE": sch,
                    "RIMFLOW_ITEMS": os.path.join(self.d, "items"),
                    "RM_PRIORITY_LIST": os.path.join(self.d, "no_list.json")}

    def ok(self, *a):
        r = subprocess.run([sys.executable, CLI] + list(a), env=dict(os.environ, RIMFLOW_SEAT="BENCH", **self.env),
                           capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)
        assert r.returncode == 0, "%s: %s %s" % (a, r.stdout[-400:], r.stderr[-400:])
        return r.stdout

    def peek(self):
        """dispatcher.peek_ticket exactly as default_obs calls it, its env pointed at this ledger."""
        old = {k: os.environ.get(k) for k in self.env}
        os.environ.update(self.env)
        try:
            return D.peek_ticket(REPO, "BENCH")
        finally:
            for k, v in old.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v


def ring_for(ticket):
    """The stalled wake seat, its queue peeked as `ticket`: the ring actions of the second observation."""
    sch, st = SD.sched(), SD.fresh()
    o = SD.obs()
    o["peek"] = lambda seat: ticket
    rings = [a for a in SD.stall(sch, st, o) if a["do"] == "ring"]
    return rings, (st["seats"].get("FOUNDRY") or {}).get("ring", {}).get("ticket")


def test_blocked_top_does_not_hide_lower():
    x = Ledger()
    x.ok("file", LOW, "--for", "BENCH", "--kind", "task", "--title", "low", "--target", "v1", "--needs", "offline")
    x.ok("file", TOP, "--for", "BENCH", "--kind", "task", "--title", "top", "--target", "v1", "--needs", "offline")
    x.ok("raise", TOP, "--why", "selftest: the top item")
    t = x.peek()
    check(t == {"id": TOP, "needs": "offline"}, "sanity: the raised item is the Dispatcher's ticket while clear (%r)" % t)
    x.ok("block", TOP, "--reason", "selftest: waits outside", "--kind", "external")
    t = x.peek()
    check(t == {"id": LOW, "needs": "offline"}, "top blocked: the lower offline item is the ticket (%r)" % t)
    r, rung = ring_for(t)
    check(len(r) == 1 and rung == LOW, "top blocked: the stalled seat is rung for the lower item (%r)" % rung)
    x.ok("block", LOW, "--reason", "selftest: waits too", "--kind", "external")
    t = x.peek()
    check(t == {}, "every item blocked: the ticket is empty, not the blocked top (%r)" % t)
    check(ring_for(t)[0] == [], "every item blocked: no ring")
    x.ok("unblock", TOP, "--why", "selftest")
    t = x.peek()
    check(t == {"id": TOP, "needs": "offline"}, "top unblocked: it is the ticket again (%r)" % t)

    y = Ledger()      # the commonest block: the top item waits on a predecessor that is still open
    pred = "PREDECESSOR_FIX_STILL_OPEN"
    y.ok("file", pred, "--for", "OWNER", "--kind", "task", "--title", "pred", "--target", "v1")
    y.ok("file", LOW, "--for", "BENCH", "--kind", "task", "--title", "low", "--target", "v1", "--needs", "offline")
    y.ok("file", TOP, "--for", "BENCH", "--kind", "task", "--title", "top", "--target", "v1", "--needs", "offline")
    y.ok("raise", TOP, "--why", "selftest: the top item")
    t = y.peek()
    check(t.get("id") == TOP, "sanity: the raised item is the ticket while clear (%r)" % t)
    y.ok("block", TOP, "--reason", "selftest: waits on its predecessor", "--on", pred)
    t = y.peek()
    check(t == {"id": LOW, "needs": "offline"}, "top waiting on a predecessor: the lower offline item is the ticket (%r)"
          % t)


def main():
    test_blocked_top_does_not_hide_lower()
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
