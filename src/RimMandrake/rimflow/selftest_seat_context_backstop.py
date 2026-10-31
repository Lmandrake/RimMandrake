#!/usr/bin/env python3
"""selftest_seat_context_backstop.py — the size limit that reaches a BUSY window (SEAT_CONTEXT_BACKSTOP_BUILD_BUSY_WINDOWS_TOO).

Every case runs on SIMULATED windows in a temp dir (the harness of selftest_seat_restart.py); nothing real is signalled.
  soft      over backstop_ctx_tokens: told once per window through the doorbell, never a nag, never over a ring
  hard      over backstop_hard_tokens: restart at the first safe boundary, however busy the window has been
  boundary  every combination of what a window can be doing goes through the real decide(): a kill only when all is safe
  blind     no reading, or a stale one around a compaction, kills nothing
  alarm     no boundary within backstop_hard_alarm_s: a Conductor alarm with the conductor log, still never a kill
  wake      a forced restart's wake carries the open work out of the old transcript
"""
import argparse
import contextlib
import io
import itertools
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import selftest_seat_restart as T  # noqa: E402  (sets RM_DISPATCHER_STATE to its temp dir before dispatcher loads)
from selftest_seat_restart import D, SR, T0, check, dos, obs, run, sched, sess, state  # noqa: E402

SOFT, HARD = 110_000, 200_000
ROOT = os.environ["RM_DISPATCHER_STATE"]


def limits(**kw):
    return T.sched(**dict({"backstop_busy": True, "backstop_ctx_tokens": SOFT, "backstop_hard_tokens": HARD,
                           "backstop_hard_alarm_s": 3600, "grace_s": 30}, **kw))


def fresh():
    return {"seats": {}, "seat_restart": {}}


def armed():
    return {"pid": 999, "session_id": "sid-old"}


def busy(ctx, **kw):
    """A window in the middle of a turn, at this context."""
    a = dict(sessions=[sess(status="busy")], armed=armed(), tx={"ctx_tokens": ctx, "last_kind": "assistant_tool", "last_at": T0})
    a.update(kw)
    return obs(**a)


def ended(ctx, **kw):
    """A window whose turn ended 60 s ago, nothing else going on."""
    a = dict(armed=armed(), tx={"ctx_tokens": ctx, "last_kind": "assistant_end", "last_at": T0 + 1000})
    a.update(kw)
    return obs(**a)


def go(sch, st, acts, now, apply=True, **fx):
    """Carry a tick's restart actions out the way dispatcher.execute does."""
    fx = dict({"root": ROOT, "alive": lambda p: True, "recheck": lambda *a: [], "final": lambda *a: [],
               "session_file": lambda p: {"sessionId": "sid-old", "name": "AGENT FOUNDRY", "status": "idle"},
               "start": lambda p: 77, "kill": lambda p, start=None: "SIGTERM", "write_killed": lambda *a: None}, **fx)
    return [SR.execute(a, sch, st, apply, now, fx) for a in acts if a["do"] in SR.DOES]


def inbox():
    p = SR.doorbell.inbox_path("FOUNDRY", ROOT)
    return SR.doorbell._read_json(p)


def clear_inbox():
    p = SR.doorbell.inbox_path("FOUNDRY", ROOT)
    if os.path.exists(p):
        os.remove(p)


def test_soft_tells_once_and_never_nags():
    clear_inbox()
    sch, st = limits(), fresh()
    a = run(sch, st, busy(SOFT - 1), T0)
    check("restart_tell" not in dos(a) and inbox() is None, "under the soft limit: nothing said")
    told = 0
    for i in range(6):
        a = run(sch, st, busy(SOFT + 1000 + i), T0 + i * 120)
        told += dos(a).count("restart_tell")
        go(sch, st, a, T0 + i * 120)
        clear_inbox() if i else None
    check(told == 1, "soft: told exactly once over six ticks (%d)" % told)
    check(not state(st), "soft: a busy window is only told, no restart is pending (%s)" % state(st))
    clear_inbox()
    run(sch, st, busy(SOFT + 9), T0)
    st["seat_restart"]["FOUNDRY"] = {}
    a = run(sch, st, busy(SOFT + 9, sessions=[sess(sid="sid-new", status="busy")],
                          armed={"pid": 999, "session_id": "sid-new"}), T0 + 900)
    check(dos(a).count("restart_tell") == 1, "a new window is a new memo: it can be told once of its own (%s)" % dos(a))


def test_soft_message_says_what_to_do():
    clear_inbox()
    sch, st = limits(), fresh()
    go(sch, st, run(sch, st, busy(SOFT + 5), T0), T0)
    m = inbox() or {}
    text = m.get("message") or ""
    check(m.get("session_id") == "sid-old", "the tell is addressed to this window's session")
    check(all(w in text for w in ("stopping point", "handoff", "seat_restart.py request")),
          "the tell says reach a stopping point, write the handoff, request the restart: %r" % text[:120])
    clear_inbox()


def test_tell_never_clobbers_a_ring():
    clear_inbox()
    sch, st = limits(), fresh()
    st["seats"]["FOUNDRY"] = {"ring": {"id": "r1"}}
    a = run(sch, st, busy(SOFT + 5), T0)
    check("restart_tell" not in dos(a), "a ring in flight: the tell waits")
    st["seats"]["FOUNDRY"] = {}
    a = run(sch, st, busy(SOFT + 5, armed=None), T0 + 120)
    check("restart_tell" not in dos(a), "no doorbell armed: the tell waits (nothing could carry it)")
    a = run(sch, st, busy(SOFT + 5, armed={"pid": 999, "session_id": "other"}), T0 + 240)
    check("restart_tell" not in dos(a), "another session's doorbell: the tell waits")
    SR.doorbell._write_json_atomic(SR.doorbell.inbox_path("FOUNDRY", ROOT), {"ring_id": "theirs", "message": "ticket"})
    a = run(sch, st, busy(SOFT + 5), T0 + 360)
    r = go(sch, st, a, T0 + 360)
    check((inbox() or {}).get("ring_id") == "theirs", "an occupied inbox is never overwritten (%s)" % r)
    clear_inbox()
    a = run(sch, st, busy(SOFT + 5), T0 + 480)
    check("restart_tell" not in dos(a), "spaced: a tell that cannot go does not hold the rings every tick")
    check(SR.ring_hold(st, "FOUNDRY", sch, T0 + 481) is None, "the rings run between tries")
    a = run(sch, st, busy(SOFT + 5), T0 + 660)
    check(dos(a).count("restart_tell") == 1, "the unwritten tell is retried, it was never spent")
    a2 = run(sch, st, busy(SOFT + 5), T0 + 660)
    go(sch, st, a, T0 + 660)
    check(bool(inbox()), "the retried tell lands")
    check(SR.ring_hold(st, "FOUNDRY", sch, T0 + 661) is not None, "no ring the same tick: it would overwrite the tell")
    check(SR.ring_hold(st, "FOUNDRY", sch, T0 + 880) is None, "the ring hold of a tell lasts that tick only")
    clear_inbox()
    del a2


def test_dry_tells_nothing_and_says_it_once():
    clear_inbox()
    sch, st = limits(), fresh()
    n = 0
    for i in range(4):
        a = run(sch, st, busy(SOFT + 5), T0 + i * 120, apply=False)
        n += dos(a).count("restart_tell")
        r = go(sch, st, a, T0 + i * 120, apply=False)
        check(all(x.startswith("would") for x in r), "dry: only says what it would do (%s)" % r) if r else None
    check(n == 1 and inbox() is None, "dry: journalled once, nothing written (%d)" % n)


def test_off_unless_keyed():
    sch, st = T.sched(backstop_ctx_tokens=SOFT), fresh()
    a = run(sch, st, busy(500_000), T0)
    check(not state(st) and "restart_tell" not in dos(a), "no backstop_busy: a busy window is left alone, as before")
    sch = T.sched(backstop=False, backstop_busy=True, backstop_hard_tokens=HARD)
    a = run(sch, st, busy(500_000), T0)
    check(not state(st) and "restart_tell" not in dos(a), "backstop off for the seat: nothing")
    sch = limits(kind="conductor")
    a = run(sch, st, busy(500_000, sessions=[sess(status="busy")]), T0)
    check(not state(st) and "restart_tell" not in dos(a), "a Conductor is never on the busy path, whatever the keys say")


def test_hard_waits_for_the_boundary_then_restarts():
    clear_inbox()
    sch, st = limits(), fresh()
    run(sch, st, busy(HARD), T0)
    rs = st["seat_restart"].get("FOUNDRY") or {}
    check(rs.get("state") == "pending" and rs.get("source") == "backstop_hard", "hard: a restart goes pending (%s)" % rs)
    for i in range(1, 12):
        a = run(sch, st, busy(HARD + 50_000), T0 + 120 * i)
        check("restart_kill" not in dos(a), "hard: tick %d of a busy turn kills nothing" % i) if "restart_kill" in dos(a) else None
    check(state(st) == "pending", "hard: a long busy turn neither kills nor fails the restart (%s)" % state(st))
    a = run(sch, st, ended(HARD + 50_000), T0 + 120 * 12 + 1000 + 60)
    check("restart_kill" in dos(a), "hard: the first ended turn, quiet_s old, with nothing held: kill (%s)" % dos(a))
    clear_inbox()


def test_hard_does_not_wait_for_the_idle_window():
    sch, st = limits(backstop_idle_s=1800), fresh()
    run(sch, st, busy(HARD), T0)
    now = T0 + 1000 + 40
    a = run(sch, st, ended(HARD), now)
    check("restart_kill" in dos(a), "hard: 40 s after the turn ended is enough, not backstop_idle_s (%s)" % dos(a))


def test_soft_keeps_the_idle_rule():
    sch, st = limits(backstop_idle_s=1800), fresh()
    a = run(sch, st, ended(SOFT + 5), T0 + 1000 + 60)
    check(not state(st), "soft: a window idle 60 s is not restarted (%s)" % state(st))
    a = run(sch, st, ended(SOFT + 5), T0 + 1000 + 1801)
    check(state(st) == "pending" and st["seat_restart"]["FOUNDRY"]["source"] == "backstop",
          "soft: past backstop_idle_s the idle backstop stands (%s)" % dos(a))


def test_hard_outlives_new_work_but_not_his_input():
    sch, st = limits(), fresh()
    run(sch, st, busy(HARD), T0)
    a = run(sch, st, ended(HARD, work=[{"ts": T0 + 5, "op": "claim", "id": "OTHER_TICKET"}]), T0 + 1060)
    check("restart_kill" in dos(a), "hard: a ticket taken after it does not void it (that is the busy window) (%s)" % dos(a))
    sch, st = limits(), fresh()
    run(sch, st, busy(HARD, tx={"ctx_tokens": HARD, "last_kind": "assistant_tool", "last_at": T0, "last_user_at": T0 - 50}), T0)
    a = run(sch, st, ended(HARD, tx={"ctx_tokens": HARD, "last_kind": "assistant_end", "last_at": T0 + 1000,
                                     "last_user_at": T0 + 900}), T0 + 1060)
    check("restart_kill" not in dos(a) and state(st) == "cancelled", "hard: his input still cancels (%s)" % dos(a))


def test_compaction_stands_the_restart_down():
    sch, st = limits(), fresh()
    run(sch, st, busy(HARD), T0)
    a = run(sch, st, ended(79_000), T0 + 1060)
    check("restart_kill" not in dos(a) and state(st) == "cancelled",
          "hard: the context fell under the soft limit: stood down (%s)" % state(st))


def test_blind_reading_kills_nothing():
    sch, st = limits(), fresh()
    for label, tx in (("no ctx", {"ctx_tokens": None, "last_kind": "assistant_end", "last_at": T0 + 1000}),):
        a = run(sch, st, ended(0, tx=tx), T0 + 1060)
        check(not state(st), "%s: nothing starts" % label)
    o = ended(HARD)
    o["seat_restart"]["tx"] = lambda seat, s: None
    a = run(sch, st, o, T0 + 1060)
    check(not state(st) and not a, "unreadable transcript: nothing starts or is said")
    run(sch, st, busy(HARD), T0)
    check(state(st) == "pending", "pending first")
    a = run(sch, st, o, T0 + 1060)
    check("restart_kill" not in dos(a) and state(st) == "pending", "pending, transcript unreadable: held, no kill (%s)" % dos(a))
    a = run(sch, st, ended(0, tx={"ctx_tokens": None, "last_kind": "assistant_end", "last_at": T0 + 1000}), T0 + 1060)
    check("restart_kill" not in dos(a) and state(st) == "pending", "pending, no context reading: held, no kill (%s)" % dos(a))


def test_recheck_at_the_kill_is_blind_safe():
    tmp = os.path.join(T.TMP, "rk")
    os.makedirs(tmp, exist_ok=True)
    p = os.path.join(tmp, "t.jsonl")
    with open(p, "w") as f:
        f.write(json.dumps({"type": "assistant", "timestamp": "2020-01-01T00:00:00Z",
                            "message": {"stop_reason": "end_turn", "usage": {"input_tokens": 0}}}) + "\n")
        f.write(json.dumps({"type": "system", "subtype": "compact_boundary", "timestamp": "2020-01-01T00:00:01Z"}) + "\n")
    sch = limits()
    saved = SR.transcript_for, SR.helpers_of, SR.bridge_reading
    SR.transcript_for = lambda *a: p
    SR.helpers_of = lambda *a: []
    SR.bridge_reading = lambda seat: {"state": "MEASURED", "holders": []}
    try:
        holds = SR.recheck_at_kill("FOUNDRY", sch, {"hard": True, "ts": 1, "cancel_after": 1},
                                   {"pid": 1}, paused=lambda: None, work=lambda s, t: [], pending=lambda *a: [])
        check(any("context" in h for h in holds), "the kill-time re-read refuses a hard restart without a context reading (%s)" % holds)
        hold2 = SR.recheck_at_kill("FOUNDRY", sch, {"hard": True, "ts": 1, "cancel_after": 1, "ticket": None},
                                   {"pid": 1}, paused=lambda: None, work=lambda s, t: [{"op": "claim", "id": "X", "ts": 2}],
                                   pending=lambda *a: ["a doorbell message waits"])
        check(any("doorbell message" in h for h in hold2), "the kill-time re-read carries the pending-input holds")
        check(not any("X" in h and "took" in h for h in hold2), "new work is no hold on a hard restart at the kill either")
    finally:
        SR.transcript_for, SR.helpers_of, SR.bridge_reading = saved


def test_tx_summary_reading():
    tmp = os.path.join(T.TMP, "tx")
    os.makedirs(tmp, exist_ok=True)
    p = os.path.join(tmp, "t.jsonl")

    def write(*recs):
        with open(p, "w") as f:
            for r in recs:
                f.write(json.dumps(r) + "\n")

    def asst(n, model="m"):
        return {"type": "assistant", "timestamp": "2026-10-31T00:00:00Z",
                "message": {"model": model, "stop_reason": "end_turn",
                            "usage": {"input_tokens": n, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}}}
    write(asst(300_000), asst(0, "<synthetic>"))
    r = SR.tx_summary(p, peers=[])
    check(r["ctx_tokens"] == 300_000, "a zero-usage API-error record keeps the last true reading, it is not 0 (%s)" % r["ctx_tokens"])
    write(asst(300_000), {"type": "system", "subtype": "compact_boundary", "timestamp": "2026-10-31T00:00:01Z"})
    r = SR.tx_summary(p, peers=[])
    check(r["ctx_tokens"] is None, "after a compaction boundary the old size is no reading (%s)" % r["ctx_tokens"])
    write(asst(300_000), {"type": "system", "subtype": "compact_boundary", "timestamp": "2026-10-31T00:00:01Z"}, asst(79_000))
    check(SR.tx_summary(p, peers=[])["ctx_tokens"] == 79_000, "the first call after it is the reading")


def _holds_case(name):
    """-> kwargs of obs() that put hold `name` on the window."""
    return {"helper": {"helpers": [{"id": "h1", "alive": True, "last_at": T0 + 900}]},
            "helpers_blind": {"helpers": None},
            "bridge": {"bridge": {"state": "MEASURED", "holders": ["FOUNDRY"]}},
            "bridge_blind": {"bridge": {"state": "UNMEASURED", "why": "x"}},
            "game": {"game": {"state": "LOADING", "at": T0 + 4940}},
            "paused": {"paused": "stop"},
            "ledger_blind": {"work": None},
            "cursor_blind": {"cursor": None}}[name]


def test_every_hold_holds_and_no_boundary_alarms():
    for name in ("helper", "helpers_blind", "bridge", "bridge_blind", "game", "paused", "ledger_blind", "cursor_blind"):
        sch, st = limits(), fresh()
        run(sch, st, busy(HARD), T0)
        a = run(sch, st, ended(HARD, **_holds_case(name)), T0 + 1060)
        check("restart_kill" not in dos(a) and state(st) == "pending", "hold %s: no kill, still pending" % name)
    sch, st = limits(), fresh()
    run(sch, st, busy(HARD), T0)
    a = run(sch, st, busy(HARD), T0 + 3000)
    check("alarm" not in dos(a), "inside backstop_hard_alarm_s: no alarm")
    a = run(sch, st, busy(HARD), T0 + 3700)
    al = [x for x in a if x["do"] == "alarm" and x.get("kind") == "restart:FOUNDRY:hard_no_boundary"]
    check(len(al) == 1 and al[0].get("conductor_log") is True and al[0].get("note") is True and al[0].get("raise_first"),
          "no boundary inside the limit: an alarm that reaches the ledger and the conductor log (%s)" % al)
    check("restart_kill" not in dos(a) and state(st) == "pending", "the alarm kills nothing and leaves it pending")
    a = run(sch, st, ended(HARD, **_holds_case("helper")), T0 + 3800)
    check(any(x.get("kind") == "restart:FOUNDRY:hard_no_boundary" and "helper" in x.get("why", "") for x in a),
          "the alarm names what holds it (%s)" % [x.get("why") for x in a])


def test_the_pending_input_holds():
    sch, st = limits(), fresh()
    run(sch, st, busy(HARD), T0)
    o = ended(HARD)
    for label, val in (("a doorbell message waits", ["a doorbell message waits"]), ("unmeasured", None)):
        o["seat_restart"]["pending"] = lambda seat, s, v=val: v
        a = run(sch, st, o, T0 + 1060)
        check("restart_kill" not in dos(a) and state(st) == "pending", "pending input (%s): held" % label)
    o["seat_restart"]["pending"] = lambda seat, s: []
    a = run(sch, st, o, T0 + 1060)
    check("restart_kill" in dos(a), "pending input gone: the boundary is back (%s)" % dos(a))


def test_a_request_during_a_hard_pending_is_adopted():
    sch, st = limits(), fresh()
    run(sch, st, busy(HARD), T0)
    req = {"seat": "FOUNDRY", "ts": T0 + 200, "session_id": "sid-old", "pid": 4242, "start": 77, "ticket": "T1", "reason": "told"}
    a = run(sch, st, busy(HARD, request=req), T0 + 240)
    rs = st["seat_restart"]["FOUNDRY"]
    check("restart_request" in dos(a) and rs.get("req_ts") == T0 + 200 and rs.get("ticket") == "T1",
          "the seat's own request joins the hard restart and is consumed (%s)" % rs)
    n = run(sch, st, busy(HARD, request=req), T0 + 360)
    check("restart_request" not in dos(n), "adopted once")


def test_rings_wait_on_a_hard_pending():
    sch, st = limits(), fresh()
    run(sch, st, busy(HARD), T0)
    check(SR.ring_hold(st, "FOUNDRY", sch, T0 + 3000) is not None, "a hard pending holds rings past ring_hold_s")
    check(SR.ring_hold(st, "FOUNDRY", sch, T0 + 3600 + 30 + 600) is None, "and for a bounded time")


def test_model_every_window_state():
    """The model: every combination of a window's status, turn, age, context reading, and holds, through the real
    decide(). The rule under test: restart_kill => status idle, turn ended, quiet_s old, a real reading over the soft
    limit, and nothing held."""
    sch = limits()
    kills = total = 0
    for status, kind, age, ctx, hold in itertools.product(
            ("idle", "busy", "waiting", None), ("assistant_end", "assistant_tool", "assistant_other", "user"),
            (0, 29, 30, 4000), (None, 0, SOFT - 1, HARD, 400_000),
            (None, "helper", "helpers_blind", "bridge", "bridge_blind", "game", "paused", "ledger_blind", "cursor_blind", "input")):
        st = fresh()
        run(sch, st, busy(HARD), T0)
        now = T0 + 5000
        kw = dict(_holds_case(hold)) if hold and hold != "input" else {}
        o = obs(sessions=[sess(status=status)], armed=armed(),
                tx={"ctx_tokens": ctx, "last_kind": kind, "last_at": now - age}, **kw)
        if hold == "input":
            o["seat_restart"]["pending"] = lambda seat, s: ["a doorbell message waits"]
        a = run(sch, st, o, now)
        total += 1
        killed = "restart_kill" in dos(a)
        safe = status == "idle" and kind == "assistant_end" and age >= 30 and ctx is not None and ctx >= SOFT and not hold
        if killed != safe:
            check(False, "model: kill=%s, safe=%s at %s" % (killed, safe, (status, kind, age, ctx, hold)))
        kills += killed
    check(kills == 2 * 2 and total == 4 * 4 * 4 * 5 * 10,
          "model: %d states, a kill in exactly the %d safe ones" % (total, kills))


def test_background_commands_hold_a_window():
    root = os.path.join(T.TMP, "proc")

    def proc(pid, ppid, cmd):
        d = os.path.join(root, str(pid))
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "stat"), "w") as f:
            f.write("%d (x y) S %d 0 0\n" % (pid, ppid))
        with open(os.path.join(d, "cmdline"), "wb") as f:
            f.write(cmd.replace(" ", "\0").encode())
    proc(100, 1, "claude")
    proc(101, 100, "sh -c python3 doorbell.py")
    proc(102, 100, "node mcp-server")
    check(SR.background_commands(100, root) == [], "a doorbell hook and an MCP server are no background command")
    proc(103, 100, "/usr/bin/zsh -c source /home/x/.claude/shell-snapshots/snapshot-zsh-1.sh && eval sleep")
    check(SR.background_commands(100, root) == [103], "a Bash-tool child of the window is (%s)" % SR.background_commands(100, root))
    check(SR.background_commands(100, root + "-gone") is None, "no /proc reading: UNMEASURED, which holds")


def test_pending_holds_reading():
    clear_inbox()
    saved = SR.background_commands, SR.queue_depth
    SR.background_commands = lambda pid: []
    SR.queue_depth = lambda path: 0
    try:
        check(SR.pending_holds("FOUNDRY", 1, "p", ROOT) == [], "nothing waits: no hold")
        SR.doorbell._write_json_atomic(SR.doorbell.inbox_path("FOUNDRY", ROOT), {"ring_id": "r"})
        check(any("doorbell" in h for h in SR.pending_holds("FOUNDRY", 1, "p", ROOT)), "a waiting inbox file holds")
        clear_inbox()
        SR.queue_depth = lambda path: 1
        check(any("queued" in h for h in SR.pending_holds("FOUNDRY", 1, "p", ROOT)), "a queued prompt holds")
        SR.queue_depth = lambda path: 0
        SR.background_commands = lambda pid: [7]
        check(any("background" in h for h in SR.pending_holds("FOUNDRY", 1, "p", ROOT)), "a background command holds")
        SR.background_commands = lambda pid: None
        check(any("UNMEASURED" in h for h in SR.pending_holds("FOUNDRY", 1, "p", ROOT)), "an unreadable process table holds")
    finally:
        SR.background_commands, SR.queue_depth = saved


def _transcript(p):
    recs = [{"type": "user", "timestamp": "2026-10-31T10:00:00Z", "message": {"role": "user", "content": "work ITEM_ALPHA please"}},
            {"type": "assistant", "timestamp": "2026-10-31T10:00:05Z",
             "message": {"stop_reason": "tool_use", "content": [
                 {"type": "text", "text": "Starting."},
                 {"type": "tool_use", "name": "TodoWrite", "input": {"todos": [
                     {"content": "fix the parser", "status": "in_progress"}, {"content": "old step", "status": "completed"}]}},
                 {"type": "tool_use", "name": "Edit", "input": {"file_path": "/x/src/parser.py"}}]}},
            {"type": "assistant", "timestamp": "2026-10-31T10:01:00Z",
             "message": {"stop_reason": "end_turn", "content": [{"type": "text", "text": "Parser half done; tests next."}]}}]
    with open(p, "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")


def test_wake_carries_the_open_work():
    p = os.path.join(T.TMP, "old.jsonl")
    _transcript(p)
    out = "\n".join(SR.wake_digest({"tx_path": p, "source": "backstop_hard", "session_id": "sid-old", "ctx_tokens": 250_000},
                                   reader=lambda: ["ITEM_ALPHA doing"], tree=lambda: [" M src/parser.py"]))
    for want in ("work ITEM_ALPHA please", "Parser half done; tests next.", "fix the parser", "/x/src/parser.py",
                 "ITEM_ALPHA doing", " M src/parser.py", p):
        check(want in out, "the digest carries %r" % want)
    check("old step" not in out, "a finished todo is not open work")
    gone = "\n".join(SR.wake_digest({"tx_path": p + ".gone", "source": "backstop_hard"}, reader=lambda: None, tree=lambda: None))
    check("UNMEASURED" in gone, "an unreadable old transcript is said, never silently empty: %r" % gone[:160])


def test_cmd_wake_prints_the_digest_only_when_forced():
    p = os.path.join(T.TMP, "old2.jsonl")
    _transcript(p)
    sch = T.sched()
    saved = SR._schedule, SR.killed_path, SR.seat_log_path, SR.subprocess.run, SR.wake_digest
    kp = os.path.join(T.TMP, "killed.json")
    SR._schedule, SR.killed_path = (lambda: sch), (lambda seat, root=None: kp)
    SR.seat_log_path = lambda seat, cfg=None: os.path.join(T.TMP, "none.log")
    SR.subprocess.run = lambda *a, **k: argparse.Namespace(stdout="", stderr="")
    SR.wake_digest = lambda rec, **k: ["DIGEST OF " + str(rec.get("source"))]
    try:
        for src, want in (("backstop_hard", True), ("backstop", True), ("request", False)):
            with open(kp, "w") as f:
                json.dump({"session_id": "s", "killed_at": 1, "source": src, "tx_path": p}, f)
            b = io.StringIO()
            with contextlib.redirect_stdout(b):
                SR.cmd_wake(argparse.Namespace(seat="FOUNDRY", lines=5, gen=None))
            check(("DIGEST OF" in b.getvalue()) == want, "wake after source %s: digest %s" % (src, want))
            check("end it now" in b.getvalue(), "the first turn still ends, or the doorbell never arms (%s)" % src)
    finally:
        SR._schedule, SR.killed_path, SR.seat_log_path, SR.subprocess.run, SR.wake_digest = saved


def test_kill_record_names_the_source():
    sch = limits()
    a = {"pid": 1, "session_id": "s", "argv": ["x"], "ticket": None}
    rec = SR._kill_record("FOUNDRY", a, sch, {"source": "backstop_hard", "ctx_tokens": 250_000, "ts": 1}, 77, T0)
    check(rec.get("source") == "backstop_hard" and rec.get("ctx_tokens") == 250_000, "the killed record names why (%s)" % rec.get("source"))


def test_agents_listing_carries_no_birth():
    """`claude agents --json` has no procStart: the birth comes from sessions/<pid>.json. Reading it off the listing left
    the backstop dead in production from the day it shipped (0 starts in the live journal, 344k window measured)."""
    sch = limits()
    listing = sess(status="idle")
    listing.pop("procStart", None)
    for name, reg, want in (("the registration binds it", 41_000_000, True), ("no registration, no restart", None, False)):
        st = fresh()
        o = obs(sessions=[listing], armed=armed(), tx={"ctx_tokens": HARD, "last_kind": "assistant_end", "last_at": T0 - 60})
        o["seat_restart"]["start"] = lambda pid: 41_000_000
        o["seat_restart"]["registered"] = lambda s, r=reg: r
        run(sch, st, o, T0)
        check((st["seat_restart"].get("FOUNDRY", {}).get("state") == "pending") is want, "agents listing: " + name)
    idle = dict(sch)
    st = fresh()
    o = obs(sessions=[listing], armed=armed(), tx={"ctx_tokens": 150_000, "last_kind": "assistant_end", "last_at": T0 - 2000})
    o["seat_restart"]["start"] = lambda pid: 41_000_000
    o["seat_restart"]["registered"] = lambda s: 41_000_000
    run(idle, st, o, T0)
    check(st["seat_restart"].get("FOUNDRY", {}).get("source") == "backstop", "agents listing: the idle backstop starts too")


def test_review_findings():
    """Codex review 1: the holes it found, each fixed."""
    sch = limits()
    # 250k compacted to 150k: fresh reading over soft, under hard. The hard restart was for a size the window lost.
    st = fresh()
    run(sch, st, busy(HARD + 50_000), T0)
    a = run(sch, st, busy(150_000), T0 + 120)
    check(st["seat_restart"]["FOUNDRY"].get("state") != "pending", "a compaction under hard cancels the hard restart")
    # the idle backstop too: a blind reading can never complete a kill, a compaction cancels
    st = fresh()
    idle = {"ctx_tokens": 150_000, "last_kind": "assistant_end", "last_at": T0 - 2000}
    run(sch, st, obs(sessions=[sess()], armed=armed(), tx=idle), T0)
    check(st["seat_restart"]["FOUNDRY"].get("source") == "backstop", "idle size restart pending")
    a = run(sch, st, obs(sessions=[sess()], armed=armed(), tx=dict(idle, ctx_tokens=None)), T0 + 120)
    check("restart_kill" not in dos(a), "idle backstop: a blind reading kills nothing")
    a = run(sch, st, obs(sessions=[sess()], armed=armed(), tx=dict(idle, ctx_tokens=60_000)), T0 + 240)
    check(st["seat_restart"]["FOUNDRY"].get("state") != "pending", "idle backstop: compacted, cancelled")
    # the Dispatcher's own start consumes nothing
    st = fresh()
    a = run(sch, st, busy(HARD), T0)
    took = []
    r = [SR.execute(x, sch, st, True, T0, {"consume": lambda seat, ts=None: took.append(ts), "root": ROOT, "alive": lambda p: True})
         for x in a if x["do"] == "restart_request"]
    clear_inbox()
    check(r and not took, "a started restart never consumes a request it did not read (%s)" % r)
    # the tell is still owed when the hard restart got there first
    st = fresh()
    run(sch, st, busy(HARD, armed=None), T0)
    a = run(sch, st, busy(HARD), T0 + 120)
    check("restart_tell" in dos(a), "a tell that could not go at the crossing goes while hard-pending")
    # a full disk does not stop the tick
    saved = SR.doorbell._write_json_atomic

    def full(*_a, **_k):
        raise OSError("disk full")
    SR.doorbell._write_json_atomic = full
    try:
        clear_inbox()
        res = [SR.execute(x, sch, st, True, T0 + 120, {"root": ROOT, "alive": lambda p: True}) for x in a if x["do"] == "restart_tell"]
        check(res and "waits" in res[0] and not st["seat_context"]["FOUNDRY"].get("told_at"), "a failed write waits, unspent")
    finally:
        SR.doorbell._write_json_atomic = saved
    # the seat's own request survives a compaction that would cancel the forced restart
    st = fresh()
    run(sch, st, busy(HARD), T0)
    run(sch, st, busy(HARD, request={"ts": T0 + 100, "session_id": "sid-old", "ticket": "T1", "reason": "fresh"}), T0 + 120)
    run(sch, st, busy(150_000), T0 + 240)
    check(st["seat_restart"]["FOUNDRY"].get("state") == "pending", "a joined request is not cancelled by a compaction")
    p = os.path.join(T.TMP, "queue.jsonl")
    with open(p, "w") as f:
        f.write("{torn\n" + json.dumps({"type": "queue-operation", "operation": "enqueue"}) + "\n")
    check(any("UNMEASURED" in h for h in SR.pending_holds("FOUNDRY", None, p, ROOT)), "an unreadable queue holds the kill")
    # a Conductor's goodbye never cuts off a background command
    saved = SR.background_commands
    SR.background_commands = lambda pid, proc_root="/proc": [55]
    try:
        check(SR.background_holds(1) and "55" in SR.background_holds(1)[0], "a running background command holds any window")
    finally:
        SR.background_commands = saved
    # a machine enqueue left waiting
    p = os.path.join(T.TMP, "queue.jsonl")
    with open(p, "w") as f:
        f.write(json.dumps({"type": "queue-operation", "operation": "enqueue", "content": "<task-notification>"}) + "\n")
    check(SR.queue_depth(p) == 1, "a machine input left queued is seen")
    with open(p, "a") as f:
        f.write(json.dumps({"type": "queue-operation", "operation": "dequeue"}) + "\n")
    check(SR.queue_depth(p) == 0, "dequeued: nothing waits")
    # ids that never pair must not hold a kill for ever (review 5), and two queued with one taken still holds
    with open(p, "w") as f:
        for op in ({"operation": "enqueue", "commandUuid": None, "content": "typed by a human"},
                   {"operation": "dequeue", "commandUuid": "other"}):
            f.write(json.dumps(dict(op, type="queue-operation")) + "\n")
    check(not [h for h in SR.pending_holds("FOUNDRY", None, p, ROOT) if "queue" in h], "an unpaired id does not hold")
    with open(p, "a") as f:
        for op in ("enqueue", "enqueue", "dequeue"):
            f.write(json.dumps({"type": "queue-operation", "operation": op}) + "\n")
    check(SR.queue_depth(p) == 1, "the first of two queued inputs still waits")
    # a rejected tool call in the old transcript
    with open(p, "w") as f:
        f.write(json.dumps({"type": "assistant", "timestamp": "2026-10-31T00:00:00Z", "message": {"content": [
            {"type": "tool_use", "name": "TodoWrite", "input": {"todos": 1}},
            {"type": "tool_use", "name": "Write", "input": {"file_path": 7}}]}}) + "\n")
    out = SR.wake_digest({"tx_path": p, "source": "backstop_hard"}, reader=lambda: [], tree=lambda: [])
    check(isinstance("\n".join(out), str), "a malformed tool call cannot crash the digest")


def test_live_schedule():
    with open(os.path.join(HERE, "dispatcher_schedule.json")) as f:
        s = json.load(f)["seat_restart"]["seats"]
    fo, be = s["FOUNDRY"], s["BENCH"]
    check(fo.get("backstop_busy") is True and fo.get("backstop_ctx_tokens") == SOFT and fo.get("backstop_hard_tokens") == HARD,
          "live: FOUNDRY runs the busy limits, %s/%s" % (fo.get("backstop_ctx_tokens"), fo.get("backstop_hard_tokens")))
    check(be.get("backstop") is False and not be.get("backstop_busy") and not be.get("backstop_hard_tokens"),
          "live: BENCH stays backstop false, no busy limit")
    dead = D.load_schedule(os.path.join(HERE, "dispatcher_schedule.json"))
    check(fo.get("backstop_hard_alarm_s", 0) > 0 and SR.config(dead)["FOUNDRY"]["backstop_hard_tokens"] == HARD,
          "config() passes the new keys")


def main():
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
