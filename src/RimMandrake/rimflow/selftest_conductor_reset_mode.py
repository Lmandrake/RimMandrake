#!/usr/bin/env python3
"""selftest_conductor_reset_mode.py — the Conductor's hold / ready / auto switch and the wake's re-show
(CONDUCTOR_RESET_FIX_KILLED_MID_READ). Simulated windows through the real decide(); nothing real is signalled.
  hold     no restart at the soft or the hard line, a pending one stands down, and the kill's own recheck refuses
  ceiling  past hold_ceiling_tokens or hold_max_s it yields to the ordinary limits, once said
  ready    fires at the next ended turn at any size, waits for helpers, never loops on the fresh window
  goodbye  outranks hold
  auto     no file, a torn file, another window's file: today's rule
  words    only his whole message flips it, only in the Conductor window
  badge    the status line shows it, only there
  wake     every wake prints the old window's last reply; an aborted restart does not
"""
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import selftest_seat_restart as T  # noqa: E402  (sets RM_DISPATCHER_STATE to its temp dir before dispatcher loads)
from selftest_seat_restart import D, SR, T0, check, dos, obs, run, sess  # noqa: E402
import reset_mode as RM  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ROOT = os.environ["RM_DISPATCHER_STATE"]
SOFT, HARD, CEIL = 110_000, 200_000, 400_000
os.environ["SEAT_RESTART_NO_TICK"] = "1"


def sch(**kw):
    return T.sched(**dict({"kind": "conductor", "backstop_busy": True, "backstop_ctx_tokens": SOFT, "backstop_hard_tokens": HARD,
                           "backstop_human_idle_s": 14400, "grace_s": 20, "quiet_s": 20, "hold_ceiling_tokens": CEIL,
                           "hold_max_s": 14400, "backstop_idle_s": 1800}, **kw))


def fresh():
    return {"seats": {}, "seat_restart": {}}


NOW = T0 + 5000


def window(ctx, mode=None, mode_at=NOW - 60, human_at=NOW - 300, ended_at=NOW - 100, **kw):
    """The Conductor at this size, its turn ended long enough ago for any quiet, its switch at mode."""
    a = dict(tx={"ctx_tokens": ctx, "last_kind": "assistant_end", "last_at": ended_at, "last_user_at": human_at},
             last_human=(human_at, None, None, 0))
    a.update(kw)
    o = obs(**a)
    if mode is not None:
        o["seat_restart"]["mode"] = lambda seat, s: {"mode": mode, "at": mode_at}
    return o


def go(s, st, o, now=NOW):
    return run(s, st, o, now)


def fires(acts):
    return "restart_kill" in dos(acts)


def test_auto_still_fires_at_the_hard_line():
    """The control: without this the hold cases below could pass on a window that would never have fired."""
    st, s = fresh(), sch()
    a = go(s, st, window(HARD + 1), NOW)
    check("restart_request" in dos(a) and st["seat_restart"]["FOUNDRY"]["state"] in ("pending", "claimed"),
          "auto: 200k goes pending, today's rule (%s)" % dos(a))
    a = go(s, st, window(HARD + 1), NOW + 60)
    check(fires(a), "auto: and kills once grace and quiet are over (%s)" % dos(a))
    st = fresh()
    a = go(s, st, window(SOFT + 1, human_at=NOW - 20000, ended_at=NOW - 2000))
    check("restart_request" in dos(a), "auto: 110k, idle and no word for 4 h goes pending (%s)" % dos(a))


def test_hold_does_not_fire():
    for ctx, label, kw in ((HARD + 1, "200k, ended turn", {}), (CEIL - 1, "just under the ceiling", {}),
                           (SOFT + 1, "110k, long idle", {"human_at": NOW - 3000, "ended_at": NOW - 2000, "mode_at": NOW - 3000})):
        st, s = fresh(), sch()
        for tick in range(4):
            a = go(s, st, window(ctx, RM.HOLD, **kw), NOW + tick * 120)
            check(not {"restart_request", "restart_kill"} & set(dos(a)), "hold: %s, tick %d: no restart (%s)" % (label, tick, dos(a)))
    check(not (st["seat_restart"].get("FOUNDRY") or {}).get("state"), "hold: no restart record was ever made")


def test_hold_stands_a_pending_restart_down():
    st, s = fresh(), sch()
    go(s, st, window(HARD + 1), NOW)
    check(st["seat_restart"]["FOUNDRY"]["state"] == "pending", "pending first")
    a = go(s, st, window(HARD + 1, RM.HOLD), NOW + 60)
    check(st["seat_restart"]["FOUNDRY"]["state"] == "cancelled" and "restart_cancel" in dos(a) and not fires(a),
          "hold: flips a pending size restart to cancelled, with no kill (%s)" % dos(a))
    a = go(s, st, window(HARD + 1, RM.HOLD), NOW + 180)
    check(not {"restart_request", "restart_kill"} & set(dos(a)), "hold: and the next tick does not re-arm (%s)" % dos(a))
    a = go(s, st, window(HARD + 1, RM.AUTO), NOW + 300)
    check("restart_request" in dos(a), "back to auto: the limit applies again (%s)" % dos(a))


def test_hold_refused_at_the_kill():
    s = sch()
    tx = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False)
    tx.close()
    sid = "sid-recheck"
    rs = {"source": "backstop_hard", "hard": True, "ts": T0, "session_id": sid, "cancel_after": T0}
    sf = {"sessionId": sid, "pid": 1, "cwd": "/x"}
    RM.write("FOUNDRY", RM.HOLD, sid, ROOT)
    kw = dict(paused=lambda: None, work=lambda *a: [], pending=lambda *a: [], shard=lambda *a: None)
    old_tp, old_ff = SR.transcript_for, SR.final_fence
    SR.transcript_for = lambda *a: tx.name
    SR.final_fence = lambda *a, **k: []
    try:
        check(any("reset switch says hold" in h for h in SR.recheck_at_kill("FOUNDRY", s, rs, sf, **kw)),
              "hold set after the verdict: the recheck at the kill refuses")
        RM.write("FOUNDRY", RM.AUTO, sid, ROOT)
        check(not any("reset switch" in h for h in SR.recheck_at_kill("FOUNDRY", s, rs, sf, **kw)), "auto: the recheck says nothing of it")
        check(any("no longer ready" in h for h in SR.recheck_at_kill("FOUNDRY", s, dict(rs, source="ready", hard=False), sf, **kw)),
              "ready taken back after the verdict: the recheck refuses")
    finally:
        SR.transcript_for, SR.final_fence = old_tp, old_ff
        os.remove(RM.path("FOUNDRY", ROOT))


def test_ceiling():
    st, s = fresh(), sch()
    a = go(s, st, window(CEIL, RM.HOLD), NOW)
    al = [x for x in a if x.get("kind") == "restart:FOUNDRY:hold_ceiling"]
    check(al and al[0].get("conductor_log") and "restart_request" in dos(a), "over the token ceiling: said once, and the limit applies (%s)" % dos(a))
    a = go(s, st, window(CEIL, RM.HOLD), NOW + 60)
    check(not [x for x in a if x.get("kind") == "restart:FOUNDRY:hold_ceiling"] and fires(a), "said once only, and the kill goes (%s)" % dos(a))
    st = fresh()
    a = go(s, st, window(HARD + 1, RM.HOLD, mode_at=NOW - 14400, human_at=NOW - 20000))
    check("restart_request" in dos(a), "4 h with no word since the switch: hold yields (%s)" % dos(a))
    st = fresh()
    a = go(s, st, window(HARD + 1, RM.HOLD, mode_at=NOW - 20000, human_at=NOW - 3600))
    check("restart_request" not in dos(a), "his talking keeps it alive: an old switch but a recent message holds (%s)" % dos(a))
    check(SR.hold_past_ceiling({"hold_ceiling_tokens": CEIL, "hold_max_s": 100}, None, None, None, NOW) is None,
          "no reading at all is no ceiling reached (the window stays held, and auto's own blind rules never apply)")


def test_ready():
    st, s = fresh(), sch()
    a = go(s, st, window(5_000, RM.READY, ended_at=NOW - 4))
    check(fires(a) and st["seat_restart"]["FOUNDRY"]["source"] == "ready", "ready: small window, turn ended: killed in this tick (%s)" % dos(a))
    k = [x for x in a if x["do"] == "restart_kill"][0]
    check("ready" in " ".join(k["argv"]) or "reset switch" in " ".join(k["argv"]), "the fresh window is told why")
    st = fresh()
    busy = window(5_000, RM.READY, tx={"ctx_tokens": 5_000, "last_kind": "assistant_tool", "last_at": NOW - 1, "last_user_at": NOW - 300},
                  sessions=[sess(status="busy")])
    a = go(s, st, busy)
    check("restart_request" in dos(a) and not fires(a), "ready: mid-turn waits for the ended turn (%s)" % dos(a))
    a = go(s, st, window(5_000, RM.READY, ended_at=NOW - 4), NOW)
    check(fires(a), "and goes at it, without the 20 s of quiet (%s)" % dos(a))
    st = fresh()
    a = go(s, st, window(5_000, RM.READY, helpers=[{"id": "h1", "alive": True, "desc": "x", "last_at": NOW}]))
    check(not fires(a), "ready: a live helper holds it, it is not a goodbye (%s)" % dos(a))
    st = fresh()
    go(s, st, window(5_000, RM.READY, helpers=[{"id": "h1", "alive": True, "desc": "x", "last_at": NOW}]))
    a = go(s, st, window(5_000, RM.AUTO), NOW + 30)
    check(st["seat_restart"]["FOUNDRY"]["state"] == "cancelled" and not fires(a), "ready taken back while pending: cancelled (%s)" % dos(a))
    # his input cancels it, and the next tick re-arms since the switch still says ready
    st = fresh()
    go(s, st, window(5_000, RM.READY, helpers=[{"id": "h1", "alive": True, "desc": "x", "last_at": NOW}]))
    a = go(s, st, window(5_000, RM.READY, human_at=NOW + 5, ended_at=NOW + 10), NOW + 30)
    check(st["seat_restart"]["FOUNDRY"]["state"] == "cancelled" and not fires(a), "ready: a new message from him cancels this round (%s)" % dos(a))
    a = go(s, st, window(5_000, RM.READY, human_at=NOW + 5, ended_at=NOW + 10), NOW + 60)
    check(fires(a), "and the switch re-arms at the next tick (%s)" % dos(a))


def test_ready_does_not_loop_on_the_fresh_window():
    sid = "sid-ready"
    RM.write("FOUNDRY", RM.READY, sid, ROOT)
    try:
        check(SR.read_mode("FOUNDRY", sid)["mode"] == RM.READY, "the window it was set in reads ready")
        check(SR.read_mode("FOUNDRY", "sid-fresh")["mode"] == RM.AUTO, "the fresh window reads auto, off the same file")
        st, s = fresh(), sch()
        o = window(5_000)
        o["seat_restart"]["mode"] = lambda seat, c: SR.read_mode(seat, c.get("sessionId"))
        o["agents"]["sessions"] = [sess(sid="sid-fresh")]
        a = go(s, st, o)
        check(not dos(a), "a real read on the fresh session: no restart (%s)" % dos(a))
    finally:
        os.remove(RM.path("FOUNDRY", ROOT))


def test_goodbye_outranks_hold():
    st, s = fresh(), sch()
    bye = {"seat": "FOUNDRY", "pid": 4242, "session_id": "sid-old", "ticket": "GOODBYE", "reason": "goodbye", "ts": NOW,
           "start": 77, "now": True}
    a = go(s, st, window(HARD + 1, RM.HOLD, request=bye))
    check(fires(a) and st["seat_restart"]["FOUNDRY"]["source"] == "request", "goodbye in hold: fires this tick (%s)" % dos(a))
    # and when a size restart was already pending as the goodbye came, hold neither cancels nor delays the join
    st = fresh()
    go(s, st, window(HARD + 1), NOW)
    a = go(s, st, window(HARD + 1, RM.HOLD, request=dict(bye, ts=NOW + 10)), NOW + 11)
    check(fires(a) and st["seat_restart"]["FOUNDRY"]["source"] == "request", "goodbye joining a pending restart beats hold (%s)" % dos(a))


def test_only_the_conductor_has_a_switch():
    st, s = fresh(), sch(kind="doorbell", backstop_human_idle_s=0)
    a = go(s, st, window(5_000, RM.READY))
    check(not dos(a), "a doorbell seat ignores ready (%s)" % dos(a))
    st = fresh()
    a = go(s, st, window(HARD + 1, RM.HOLD, armed={"pid": 999, "session_id": "sid-old"}))
    check("restart_request" in dos(a), "a doorbell seat ignores hold (%s)" % dos(a))


def test_file_reads_auto():
    p = RM.path("FOUNDRY", ROOT)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    for raw, why in (("{torn", "torn"), ('{"mode":"bogus","session_id":"s"}', "unknown mode"), ('["hold"]', "not a dict"),
                     ('{"mode":"hold","session_id":"other"}', "another window's")):
        with open(p, "w") as f:
            f.write(raw)
        check(RM.read("FOUNDRY", "s", ROOT)["mode"] == RM.AUTO, "%s file reads auto" % why)
    os.remove(p)
    check(RM.read("FOUNDRY", "s", ROOT)["mode"] == RM.AUTO, "no file reads auto")
    for bad in (("nope", "s"), (RM.HOLD, None), (RM.HOLD, "")):
        try:
            RM.write("FOUNDRY", bad[0], bad[1], ROOT)
            check(False, "write took %r" % (bad,))
        except ValueError:
            check(True, "write refuses %r" % (bad,))


def hook(prompt, env_extra=None):
    env = dict(os.environ, AGENT_SEAT="BENCH", CONDUCTOR_GOODBYE_SESSION_NAME="CONDUCTOR")
    env.update(env_extra or {})
    r = subprocess.run([sys.executable, os.path.join(REPO, ".claude", "hooks", "conductor_goodbye.py")], capture_output=True, text=True,
                       input=json.dumps({"prompt": prompt, "session_id": "sid-hook"}), env=env, timeout=60)
    return r.stdout


def test_words_through_the_real_hook():
    p = RM.path("BENCH", ROOT)
    with contextlib.suppress(OSError):
        os.remove(p)
    for said_, mode in (("hold", RM.HOLD), ("Hold!", RM.HOLD), ("hold for user interaction", RM.HOLD),
                        ("ready to reset as soon as possible", RM.READY), ("READY.", RM.READY), ("auto", RM.AUTO)):
        out = hook(said_)
        check(RM.read("BENCH", "sid-hook", ROOT)["mode"] == mode and "ONE line" in out and mode.upper() in out,
              "his whole message %r sets %s and the window says so" % (said_, mode))
    os.remove(p)
    for said_ in ("hold on, one thing", "are you ready?", "put it on hold", "ready to go, do the hose", "auto mode for pipes", "holding"):
        out = hook(said_)
        check(not out and not os.path.exists(p), "%r is not the switch" % said_)
    check(not hook("hold", {"AGENT_SEAT": "RUNNER"}) and not os.path.exists(p), "another seat's window: no switch")
    check(not hook("hold", {"CONDUCTOR_GOODBYE_SESSION_NAME": "SOMETHING ELSE"}) and not os.path.exists(p), "another name: no switch")
    check(not hook("hold", {"CONDUCTOR_GOODBYE_SESSION_NAME": "__UNREADABLE__"}) and not os.path.exists(p), "unreadable identity: no switch")
    check("close-out" in hook("goodbye") or "GOODBYE" in hook("goodbye"), "goodbye still prints the close-out")


def test_status_line_shows_it():
    sl = os.path.join(REPO, "src", "RimMandrake", "Utils", "statusline.py")

    def line(seat):
        r = subprocess.run([sys.executable, sl], input=json.dumps({"session_id": "sid-line", "model": {"id": "x"}}), capture_output=True,
                           text=True, env=dict(os.environ, AGENT_SEAT=seat), timeout=60)
        return r.stdout
    p = RM.path("BENCH", ROOT)
    with contextlib.suppress(OSError):
        os.remove(p)
    check("reset auto" in line("BENCH"), "no switch set: the window shows auto")
    RM.write("BENCH", RM.HOLD, "sid-line", ROOT)
    check("reset HOLD" in line("BENCH"), "hold shows")
    RM.write("BENCH", RM.READY, "sid-line", ROOT)
    check("reset READY" in line("BENCH"), "ready shows")
    RM.write("BENCH", RM.HOLD, "another-window", ROOT)
    check("reset auto" in line("BENCH"), "another window's hold does not show here")
    check("reset " not in line("RUNNER"), "another seat has no switch to show")
    os.remove(p)


def wake(rec, kind="conductor"):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        SR._wake_last_reply(rec)
    return out.getvalue()


def tx_file(records):
    f = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False)
    for r in records:
        f.write(json.dumps(r) + "\n")
    f.close()
    return f.name


def say(text, **kw):
    return dict({"type": "assistant", "message": {"content": [{"type": "text", "text": text}]}}, **kw)


def test_wake_reshows_the_last_reply():
    REPLY = "The BENCH is underutilized.\nThree things are unmeasured.\n\n| a | b |"
    path = tx_file([say("an old reply"), {"type": "user", "message": {"content": "more"}}, say(REPLY),
                    {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Bash", "input": {}}]}},
                    say("a helper's talk", isSidechain=True), say("API Error: 500", isApiErrorMessage=True)])
    for src in ("backstop", "backstop_hard", "ready", "request"):
        out = wake({"tx_path": path, "session_id": "old", "killed_at": T0, "source": src})
        check(REPLY in out and "an old reply" not in out and "API Error" not in out and "helper's talk" not in out,
              "wake after %s prints the old window's last reply whole" % src)
        check("word for word" in out and "very top of your first reply" in out, "and orders it put in front of him (%s)" % src)
    # "hold" while reading, then a restart past the ceiling: the switch's dictated line must not bury what he was reading
    p2 = tx_file([say(REPLY), {"type": "user", "message": {"content": "hold"}}, say(RM.said(RM.HOLD, {})),
                  {"type": "user", "message": {"content": "goodbye"}}, say("Fresh Conductor now; nothing you send is lost.")])
    out = wake({"tx_path": p2, "killed_at": T0})
    check(REPLY in out and "Reset switch" not in out and "Fresh Conductor" not in out, "dictated one-liners are passed over")
    check(wake({"tx_path": path, "aborted": "x"}) == "", "an aborted restart killed nothing: the old screen still stands")
    check(wake({}) == "", "no record: a fleet launch, nothing to show")
    check("UNMEASURED" in wake({"session_id": "old", "killed_at": T0}), "no transcript named: said, never silent")
    check("UNMEASURED" in wake({"tx_path": "/no/such/file", "killed_at": T0}), "an unreadable transcript: said, never silent")
    # through the real cmd_wake, on the path that answers no replay: every wake, not only an unanswered one
    p = SR.killed_path("BENCH", ROOT)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        json.dump({"tx_path": path, "session_id": "old", "killed_at": T0, "gen": "g1", "woken_at": T0 + 1, "woken_by": "w"}, f)
    old_s, old_ans = SR._schedule, SR.answered
    SR._schedule = lambda: T.sched()
    SR.config, cfg_old = (lambda s: {"BENCH": dict(SR.DEFAULTS, kind="conductor", clone=REPO)}), SR.config
    SR.answered = lambda rec: True
    try:
        class A:
            seat, lines, gen = "BENCH", 3, None
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            SR.cmd_wake(A)
        check(REPLY in out.getvalue() and "already recovered" in out.getvalue(), "cmd_wake shows it even on an already answered restart")
    finally:
        SR._schedule, SR.answered, SR.config = old_s, old_ans, cfg_old
        os.remove(p)


def test_live_schedule():
    with open(os.path.join(HERE, "dispatcher_schedule.json")) as f:
        b = json.load(f)["seat_restart"]["seats"]["BENCH"]
    check(b.get("hold_ceiling_tokens", 0) > b.get("backstop_hard_tokens", 0) and b.get("hold_max_s", 0) > 0, "live: a ceiling above the hard line")
    check(SR.config(D.load_schedule(os.path.join(HERE, "dispatcher_schedule.json")))["BENCH"]["hold_ceiling_tokens"] == b["hold_ceiling_tokens"],
          "config() carries it")
    check("mode" in SR.default_obs(D.load_schedule(os.path.join(HERE, "dispatcher_schedule.json")), lambda *a: []),
          "the live tick reads the switch: without this hold is a test-only feature")


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
