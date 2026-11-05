#!/usr/bin/env python3
"""selftest_dispatcher_blocked_top_cursor.py - two Dispatcher doors the v3 audit found unproven (T15,
DISPATCHER_PROVE_BLOCKED_TOP_AND_CURSOR; design/RimMandrake/rimflow_v3_risk_response_2026-10-29.md R03 and T15).

    python3 src/RimMandrake/rimflow/selftest_dispatcher_blocked_top_cursor.py

1. A BLOCKED TOP ITEM DOES NOT HIDE LOWER WORK. Real path: cli.py on a throwaway ledger, read by the Dispatcher's own
   dispatcher.peek_ticket (the subprocess `rimflow next --peek` + parse_peek the tick runs), then dispatcher.decide
   rings the stalled seat with that ticket. The planted fault is the block itself: the raised item is offered first
   while clear (the instrument can see it), and once blocked the lower offline item is the ticket and the ring. Same
   for a top item blocked `--on` an open predecessor; all blocked -> {} and no ring; unblocked -> back on top.

2. THE EVENT CURSOR SURVIVES A 7 H OUTAGE. role_launch's `event_cursor` (EVENT_LOOKBACK_S = 6 h behind it) through
   dispatcher.decide: (a) no tick at all for 7 h (the timer dead), events landing all through it, the oldest 6 h 35 min
   before the resume tick -- the first tick back launches one event run that names the oldest and counts the rest,
   moves the cursor and re-fires nothing after; (b) the ticks keep running every 2 min but the ledger is unreadable
   for 7 h -- the cursor does not move and the first readable tick launches on the same events. Planted fault: the
   same runs with a window measured from NOW (now - 6 h) instead of from the cursor -- the checks that pass on the
   real code fail.
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


# ---------------------------------------------------------------- 2. the event cursor across a 7 h outage

H = 3600


def now_window(resume):
    """The planted fault: a lookback measured from the resume tick, not from the cursor."""
    real = RL.unseen

    def fake(evs, rs):
        return [e for e in real(evs, rs) if e[0] > resume - RL.EVENT_LOOKBACK_S]
    return real, fake


def producer_outage(blind_ticks, planted=False):
    """Cursor at the 09:00 run; nothing read for 7 h; events at +30 min, +3 h, +6.5 h. -> (launches, st, resume)."""
    t9 = SD.at_local("09:00", plus_s=0)
    resume = t9 + 7 * H + 300
    items = {"PLAN_A": SD.FakeItem(raised="2026-10-28T01:00:00Z"), "PLAN_ROW": SD.FakeItem(row="R3")}
    evs = [SD.BASE_EV,
           dict(SD.BASE_EV, event="note", id="ROLES_ITEM_X", text="REPLAN REQUEST: the plan slips", ts=SD.lts(t9 + 1800)),
           dict(SD.BASE_EV, event="verify", id="PLAN_A", result="fail", ts=SD.lts(t9 + 3 * H)),
           dict(SD.BASE_EV, event="block", id="PLAN_ROW", ts=SD.lts(t9 + 6 * H + 1800))]
    st = SD.fresh()
    st["roles"] = {"Producer": {"done": {"%s 09:00" % RL.day_of(t9): "launch"}, "runs": [], "event_cursor": t9,
                                "events_seen": []}}
    p = SD.producer(after_role=None)

    def boom():
        raise ValueError("selftest: ledger unreadable")
    cursors = set()
    for k in range(blind_ticks):          # the ticks of a blind outage (ledger unreadable); 0 = timer dead
        tk = t9 + 120 * (k + 1)
        SD.rdecide([p], st, SD.lrobs(SD.ops_status(tk), boom), tk)
        cursors.add(st["roles"]["Producer"].get("event_cursor"))
    real, fake = now_window(resume)
    if planted:
        RL.unseen = fake
    try:
        a = SD.role_acts(SD.rdecide([p], st, SD.lrobs(SD.ops_status(resume), SD.lread(evs, items)), resume))
    finally:
        RL.unseen = real
    return [x for x in a if x["do"] == "role_launch"], st, resume, cursors, (p, evs, items)


def producer_checks(label, blind_ticks, planted):
    la, st, resume, cursors, (p, evs, items) = producer_outage(blind_ticks, planted)
    ok = []
    if blind_ticks:
        ok.append(("%s: the cursor never moved during %d blind ticks" % (label, blind_ticks),
                   cursors == {SD.at_local("09:00", plus_s=0)}))
    ok.append(("%s: the first tick back launches ONE event run" % label, len(la) == 1 and la[0]["mode"] == "event"))
    why = la[0]["why"] if la else ""
    ok.append(("%s: it names the oldest unread event (6 h 35 min old) and counts the other two" % label,
               "replan request on ROLES_ITEM_X" in why and "+2 more" in why))
    ok.append(("%s: the launch moves the cursor to the resume tick" % label,
               st["roles"]["Producer"]["event_cursor"] == resume))
    a = SD.role_acts(SD.rdecide([p], st, SD.lrobs(SD.ops_status(resume + 120), SD.lread(evs, items)), resume + 120))
    ok.append(("%s: the next tick re-fires nothing" % label, not [x for x in a if x["do"] == "role_launch"]))
    return ok


def test_cursor_survives_7h_outage():
    rows = producer_checks("timer dead 7 h", 0, False) + producer_checks("ledger blind 7 h", 210, False)
    for msg, ok in rows:
        check(ok, msg)
    # the planted fault on the same path: a window from now, not from the cursor. Each scenario must catch it.
    for label, rows in (("timer dead 7 h", producer_checks("timer dead 7 h", 0, True)),
                        ("ledger blind 7 h", producer_checks("ledger blind 7 h", 210, True))):
        bad = [m for m, ok in rows if not ok]
        check(bool(bad), "planted fault (lookback from now) is caught by the %s case: %s" % (label, bad[:1]))


def main():
    test_blocked_top_does_not_hide_lower()
    test_cursor_survives_7h_outage()
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
