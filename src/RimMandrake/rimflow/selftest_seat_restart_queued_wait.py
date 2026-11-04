#!/usr/bin/env python3
"""CONDUCTOR_GOODBYE_FIX_QUEUED_WAIT_SKIPPED: a goodbye and a wait queued in one running turn.

Claude Code delivers the goodbye (queue-operation remove, then a queued_command attachment) while the wait stays in the
queue; the request's cursor binds just past the goodbye's attachment, so the wait's enqueue sits BEFORE the cursor and no
cursor read sees it. MEASURED 2026-11-03 over ~/.claude/projects (3942 transcripts, 26 batches of queued prompts): a batch
lands in enqueue order, so a wait that was delivered lies after the cursor; only a wait still in the queue hides.

- A goodbye still kills at once (owner 2026-11-01T12:05Z: "Additional text is just written to a handoff but does not stop
  the countdown"), but the still-queued wait must reach the AFTER GOODBYE seat log, not only the wake.
- Any other Conductor restart (his reset switch, a context backstop) must hold on it, at the tick (default_obs pending)
  and at the kill (recheck_at_kill), as a doorbell seat does (queue_depth).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import selftest_seat_restart as T  # noqa: E402  (its fixtures: a temp CLAUDE home, BENCH schedule, seat log dir)
import seat_restart as SR  # noqa: E402

check = T.check
WAIT = "wait, one more thing before you go"


def _recs(wait_delivered=False):
    recs = [T._hu("1970-01-12T13:40:00Z", "do the thing"),
            T._ha("1970-01-12T13:40:10Z", "tool_use"),
            {"type": "queue-operation", "operation": "enqueue", "timestamp": "1970-01-12T13:44:58Z",
             "content": "goodbye", "commandUuid": "g1"},
            {"type": "queue-operation", "operation": "enqueue", "timestamp": "1970-01-12T13:44:59Z",
             "content": WAIT, "commandUuid": "w1"},
            {"type": "queue-operation", "operation": "remove", "timestamp": "1970-01-12T13:45:00Z",
             "commandUuid": "g1"},
            {"type": "attachment", "timestamp": T.GB, "uuid": "att-g1",
             "attachment": {"type": "queued_command", "commandMode": "prompt", "prompt": "goodbye",
                            "origin": {"kind": "human"}}}]
    if wait_delivered:
        recs.append({"type": "queue-operation", "operation": "remove", "timestamp": "1970-01-12T13:45:01Z",
                     "commandUuid": "w1"})
    recs.append(T._ha("1970-01-12T13:45:30Z", "end_turn"))
    return recs


def _build(wait_delivered=False):
    p, ends = T._bt("sid-old", _recs(wait_delivered))
    return p, ends[5]                    # the cursor: just past the goodbye's queued_command attachment


def test_instance_the_cursor_cannot_see_the_wait():
    p, cur = _build()
    hs = SR.human_since_offset(p, cur)
    check(hs is not None and not any(WAIT in SR._text(r) for r in hs),
          "Q0 control: the cursor read from past the goodbye does not see the queued wait (%s)" % hs)
    check(SR.queue_depth(p) == 1, "Q0 control: queue_depth sees it (%s)" % SR.queue_depth(p))


def test_goodbye_logs_the_queued_wait():
    p, cur = _build()
    cfg = SR.config(T.bsched())["BENCH"]
    log = SR.seat_log_path("BENCH", cfg)
    if log and os.path.exists(log):
        os.remove(log)
    SR._log_after_goodbye("BENCH", cfg, {"tx_path": p, "tx_offset": cur, "source": "request"})
    body = open(log, encoding="utf-8").read() if log and os.path.exists(log) else ""
    check(WAIT in body, "Q1 the AFTER GOODBYE seat log carries the wait still in the queue (%r)" % body[-300:])


def _recheck(source, cur):
    rs = {"ts": T.T0, "cancel_after": T.GB_T, "tx_offset": cur, "source": source, "session_id": "sid-old"}
    return SR.recheck_at_kill("BENCH", T.bsched(), rs, T.bsess(), paused=lambda: None, work=lambda s_, ts: [],
                              shard=lambda s_: None)


def test_kill_recheck_holds_a_conductor_restart_on_the_queue():
    _, cur = _build()
    for src in ("ready", "backstop"):
        holds = _recheck(src, cur)
        check(any("queued prompt" in h for h in holds), "Q2 a %s Conductor restart holds at the kill on the queued "
              "wait (%s)" % (src, holds))
    holds = _recheck("request", cur)
    check(not any("queued prompt" in h for h in holds), "Q2 a goodbye does not wait for it (%s)" % holds)
    _, cur = _build(wait_delivered=True)
    holds = _recheck("ready", cur)
    check(not any("queued prompt" in h for h in holds), "Q2 control: an empty queue holds nothing (%s)" % holds)


def test_tick_pending_reads_the_conductor_queue():
    _build()
    o = SR.default_obs(T.bsched(), lambda *a, **k: [])
    p = o["pending"]("BENCH", T.bsess())
    check(p is not None and any("queued prompt" in h for h in p), "Q3 the tick's pending read of the Conductor "
          "sees the queued wait (%s)" % p)
    _build(wait_delivered=True)
    p = o["pending"]("BENCH", T.bsess())
    check(p is not None and not any("queued prompt" in h for h in p), "Q3 control: an empty queue (%s)" % p)


def test_tick_goodbye_kills_despite_the_queued_wait():
    """Q4 the tick, not only the kill: a goodbye (source=request) with the wait still queued is not held by it."""
    _build()
    pend = SR.default_obs(T.bsched(), lambda *a, **k: [])["pending"]
    p = pend("BENCH", T.bsess())
    check(p is not None and any("queued prompt" in h for h in p), "Q4 control: the real pending read sees the "
          "queued wait (%s)" % p)
    sch, late = T.bsched(), T.T0 + 605
    st = T.fresh()
    o = T.obs(sessions=[T.bsess()], request=T.breq())
    o["seat_restart"]["pending"] = pend
    T.run(sch, st, o, T.T0 + 1)
    o = T.obs(sessions=[T.bsess()])
    o["seat_restart"]["pending"] = pend
    a = T.run(sch, st, o, late)
    held = [x for x in a if x["do"] == "restart_hold" and "queued prompt" in (x.get("why") or "")]
    check(not held and "restart_kill" in T.dos(a), "Q4 a goodbye at the tick is not held by the queued wait and is "
          "killed (%s)" % [(x["do"], x.get("why")) for x in a])


def main():
    SR.UNFILED = lambda t: None
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
            except Exception as e:  # noqa: BLE001
                import traceback
                traceback.print_exc()
                check(False, "%s raised %s: %s" % (name, type(e).__name__, e))
    print("\n%s: %d failure(s)" % ("FAIL" if T.FAILS else "PASS", len(T.FAILS)))
    return 1 if T.FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
