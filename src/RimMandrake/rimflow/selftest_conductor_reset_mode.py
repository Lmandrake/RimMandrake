#!/usr/bin/env python3
"""selftest_conductor_reset_mode.py — the Conductor's hold / ready / auto switch and the wake's re-show
(CONDUCTOR_RESET_FIX_KILLED_MID_READ). Simulated windows through the real decide(); nothing real is signalled.
  hold     no restart at the soft or the hard line, a pending one stands down, and the kill's own recheck refuses
  ceiling  past hold_ceiling_tokens or hold_max_s it yields to the ordinary limits, once said
  ready    fires at the next ended turn at any size, waits for helpers, never loops on the fresh window
  goodbye  outranks hold
  auto     no file, a torn file, another window's file: today's rule
  words    only his whole message flips it, only in the Conductor window
  badge    the status line shows it, only there, through the command settings.json registers
  wake     every wake prints the old window's last reply, a first launch after a boot too (found from the transcripts,
           through the command the wake prompt names); an aborted restart does not; both wake commands hold with no,
           a stale and an aborted record
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
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
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
    a = dict(tx={"ctx_tokens": ctx, "last_kind": "assistant_end", "last_at": ended_at, "last_user_at": human_at, "size": 0},
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
    # "visible in the window" means the command Claude Code runs, not the script above: run what settings.json registers
    with open(os.path.join(REPO, ".claude", "settings.json")) as f:
        reg = json.load(f).get("statusLine") or {}
    check(reg.get("type") == "command" and reg.get("command"), "a status line command is registered in .claude/settings.json")

    def registered(seat):
        r = subprocess.run(reg.get("command") or "true", shell=True, input=json.dumps({"session_id": "sid-line", "model": {"id": "x"}}),
                           capture_output=True, text=True, env=dict(os.environ, AGENT_SEAT=seat, CLAUDE_PROJECT_DIR=REPO), timeout=60)
        return r.stdout
    RM.write("BENCH", RM.HOLD, "sid-line", ROOT)
    check("reset HOLD" in registered("BENCH"), "the registered status line shows hold")
    RM.write("BENCH", RM.READY, "sid-line", ROOT)
    check("reset READY" in registered("BENCH"), "the registered status line shows ready")
    os.remove(p)
    check("reset auto" in registered("BENCH"), "the registered status line shows auto")


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
    check("UNMEASURED" in wake({}), "no record and no window to look in: said, never silent")
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


def write_tx(cfg_home, clone, sid, records, age_s=0):
    p = SR.transcript_path(clone, sid)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    t = T0 + 100000 - age_s
    os.utime(p, (t, t))
    return p


def window_recs(title, entry, *replies):
    out = [{"type": "custom-title", "customTitle": title}]
    for r in replies:
        out += [{"type": "user", "entrypoint": entry, "message": {"content": "q"}}, dict(say(r), entrypoint=entry)]
    return out


def proc_start(pid):
    with open("/proc/%d/stat" % pid) as f:
        return f.read().rsplit(")", 1)[1].split()[19]


def test_window_that_died_without_a_record():
    """The checker's case: the first launch after a boot, crash or account switch. Real files in a fake Claude home, driven
    through the very command the Conductor's first-launch wake prompt names, in a real subprocess."""
    import install_wt_seat_profiles as W
    prompt = W.WAKE_PROMPT["BENCH"]
    check("src/RimMandrake/Utils/handoff.py --wake" in prompt, "the first-launch wake prompt runs handoff.py --wake")
    check("BENCH" in W.OWN_WAKE, "and that is the Conductor tile's first launch")
    clone = json.load(open(os.path.join(HERE, "dispatcher_schedule.json")))["seat_restart"]["seats"]["BENCH"].get("clone") \
        or SR.config(SR._schedule())["BENCH"]["clone"]
    home = tempfile.mkdtemp(prefix="cr-home-")
    state = tempfile.mkdtemp(prefix="cr-state-")
    os.makedirs(os.path.join(home, "sessions"))
    env = dict(os.environ, CLAUDE_CONFIG_DIR=home, RM_DISPATCHER_STATE=state, AGENT_SEAT="BENCH", RIMFLOW_SEAT="BENCH")
    sid = "cccccccc-dead"
    old = SR.claude_home
    SR.claude_home = lambda: home
    try:
        def run_wake():
            r = subprocess.run([sys.executable, os.path.join(REPO, "src/RimMandrake/Utils/handoff.py"), "--wake"], cwd=REPO,
                               env=env, capture_output=True, text=True, timeout=120)
            return r.stdout + r.stderr
        check("LAST REPLY: UNMEASURED" in run_wake(), "nothing to read (an empty Claude home): said, never silent")
        write_tx(home, clone, "aaaaaaaa-older", window_recs("CONDUCTOR", "cli", "an older window's reply"), 7200)
        dead = write_tx(home, clone, sid, window_recs("CONDUCTOR", "cli", "first", "THE REPLY HE WAS READING"), 600)
        write_tx(home, clone, "dddddddd-ops", window_recs("CONDUCTOR", "sdk-cli", "a role launch talks to itself"), 60)
        write_tx(home, clone, "eeeeeeee-other", window_recs("AGENT BENCH", "cli", "a window with another name"), 50)
        out = run_wake()
        check("THE REPLY HE WAS READING" in out and "word for word" in out,
              "the first-launch wake shows the last reply of the window that died")
        shown = out.split(">>>", 1)[0]    # the reply block only: the real handoff text after it may say anything
        check("older window" not in shown and "role launch" not in shown and "another name" not in shown,
              "and only that one: not an older window, a role launch of the same name, or another title")
        check(out.lstrip().startswith("== the old window's LAST REPLY"), "it comes before the handoff text")
        # a stale record of an older restart must not outrank the window that actually died
        os.makedirs(os.path.dirname(SR.killed_path("BENCH", state)), exist_ok=True)
        with open(SR.killed_path("BENCH", state), "w") as f:
            json.dump({"tx_path": SR.transcript_path(clone, "aaaaaaaa-older"), "session_id": "aaaaaaaa-older", "killed_at": T0}, f)
        out = run_wake()
        check("THE REPLY HE WAS READING" in out and "an older window" not in out.split(">>>", 1)[0], "a stale killed record loses to the newer dead window")
        # a record of the restart that killed this very window: same reply, and it names the restart
        with open(SR.killed_path("BENCH", state), "w") as f:
            json.dump({"tx_path": dead, "session_id": sid, "killed_at": T0}, f)
        out = run_wake()
        check("THE REPLY HE WAS READING" in out and "restarted at" in out, "the record of this very restart is honoured")
        os.remove(SR.killed_path("BENCH", state))
        # a window alive right now is not dead: its screen still stands (this test's own process plays it)
        me = os.getpid()
        live_file = os.path.join(home, "sessions", "%d.json" % me)
        with open(live_file, "w") as f:
            json.dump({"pid": me, "sessionId": sid, "procStart": proc_start(me)}, f)
        out = run_wake()
        check("THE REPLY HE WAS READING" not in out and "an older window's reply" in out,
              "a live window is passed over: the newest DEAD one shows")
        # the boot case: the pid now belongs to something else, so the file's start tick no longer matches
        with open(live_file, "w") as f:
            json.dump({"pid": me, "sessionId": sid, "procStart": "1"}, f)
        check("THE REPLY HE WAS READING" in run_wake(), "a pid reused after a boot does not make a dead window read alive")
        with open(live_file, "w") as f:
            json.dump({"pid": me, "sessionId": sid, "startedAt": 1000}, f)
        check("THE REPLY HE WAS READING" in run_wake(), "nor does an older session file with no start tick")
        os.remove(live_file)
        # a window that died having said nothing: the one before it, what was last on any screen
        write_tx(home, clone, "ffffffff-mute", window_recs("CONDUCTOR", "cli") + [
            {"type": "user", "entrypoint": "cli", "message": {"content": "wake"}}], 5)
        check("THE REPLY HE WAS READING" in run_wake(), "a window that never spoke is passed over")
        # other seats print nothing
        r = subprocess.run([sys.executable, os.path.join(HERE, "seat_restart.py"), "last-reply", "--seat", "RUNNER"], cwd=REPO,
                           env=env, capture_output=True, text=True, timeout=60)
        check(r.returncode == 0 and "LAST REPLY" not in r.stdout, "a seat without the Conductor's kind prints nothing")
    finally:
        SR.claude_home = old


def test_both_wake_commands_with_every_record():
    """The blind check's gaps at 5d471d50: 'seat_restart.py wake' (what a Dispatcher relaunch runs) and 'handoff.py --wake'
    (what a first launch runs), as real subprocesses over real files in a fake Claude home, with no record, a stale record
    and an aborted record. The newest dead window's reply shows each time, and the dictated one-liners it ended on do not."""
    clone = json.load(open(os.path.join(HERE, "dispatcher_schedule.json")))["seat_restart"]["seats"]["BENCH"].get("clone") \
        or SR.config(SR._schedule())["BENCH"]["clone"]
    home = tempfile.mkdtemp(prefix="cr-home-")
    state = tempfile.mkdtemp(prefix="cr-state-")
    os.makedirs(os.path.join(home, "sessions"))
    env = dict(os.environ, CLAUDE_CONFIG_DIR=home, RM_DISPATCHER_STATE=state, AGENT_SEAT="BENCH", RIMFLOW_SEAT="BENCH")
    commands = {"seat_restart wake": [os.path.join(HERE, "seat_restart.py"), "wake", "--seat", "BENCH"],
                "handoff --wake": [os.path.join(REPO, "src/RimMandrake/Utils/handoff.py"), "--wake"]}
    old_home = SR.claude_home
    SR.claude_home = lambda: home
    rec_path = SR.killed_path("BENCH", state)
    os.makedirs(os.path.dirname(rec_path), exist_ok=True)

    def run_wake(argv):
        r = subprocess.run([sys.executable] + argv, cwd=REPO, env=env, capture_output=True, text=True, timeout=120)
        check(r.returncode == 0, "the wake exits clean: %s (rc %s) %s" % (" ".join(argv[-2:]), r.returncode, r.stderr[-300:]))
        return r.stdout + r.stderr
    try:
        older = "aaaaaaaa-older"
        write_tx(home, clone, older, window_recs("CONDUCTOR", "cli", "AN OLDER WINDOW'S REPLY"), 7200)
        write_tx(home, clone, "cccccccc-dead", window_recs("CONDUCTOR", "cli", "THE REPLY HE WAS READING") + [
            {"type": "user", "entrypoint": "cli", "message": {"content": "hold"}}, dict(say(RM.said(RM.HOLD, {})), entrypoint="cli"),
            {"type": "user", "entrypoint": "cli", "message": {"content": "goodbye"}},
            dict(say("Fresh Conductor now; nothing you send is lost."), entrypoint="cli")], 600)
        stale = {"tx_path": SR.transcript_path(clone, older), "session_id": older, "killed_at": T0}
        records = {"no record": None, "a stale record": stale, "an aborted record": dict(stale, aborted="called off")}
        for rec_name, rec in records.items():
            if rec is None:
                with contextlib.suppress(OSError):
                    os.remove(rec_path)
            else:
                with open(rec_path, "w") as f:
                    json.dump(rec, f)
            for cmd_name, argv in commands.items():
                out = run_wake(argv)
                where = "%s with %s" % (cmd_name, rec_name)
                check("THE REPLY HE WAS READING" in out and "word for word" in out, where + ": shows the newest dead window's reply")
                check("AN OLDER WINDOW'S REPLY" not in out, where + ": not the older window's")
                check("LAST REPLY: UNMEASURED" not in out, where + ": no false UNMEASURED")
                check("Reset switch:" not in out and "Fresh Conductor now" not in out, where + ": no dictated one-liner in its place")
    finally:
        SR.claude_home = old_home


def test_ready_gets_its_own_ticks():
    kicks, old = [], SR._tick_soon
    SR._tick_soon = lambda *d: kicks.append(d)
    try:
        for mode in (RM.HOLD, RM.AUTO):
            SR.set_mode("FOUNDRY", mode, "sid-t", root=ROOT, by="t")
        check(not kicks, "hold and auto need no tick")
        SR.set_mode("FOUNDRY", RM.READY, "sid-t", root=ROOT, by="t")
        check(len(kicks) == 1 and kicks[0] and min(kicks[0]) <= 20,
              "ready gets its own ticks, or it waits out the 120 s timer (%s)" % kicks)
    finally:
        SR._tick_soon = old
        os.remove(RM.path("FOUNDRY", ROOT))


def test_soft_backstop_under_hold():
    """The 110k line, not only the 200k one: pending stands down, and the kill's recheck refuses."""
    st, s = fresh(), sch()
    quiet = dict(human_at=NOW - 20000, ended_at=NOW - 2000)
    a = go(s, st, window(SOFT + 1, **quiet), NOW)
    rs = st["seat_restart"]["FOUNDRY"]
    check(rs["state"] == "pending" and rs.get("source") == "backstop", "the soft line goes pending in auto (%s, %s)" % (rs, dos(a)))
    a = go(s, st, window(SOFT + 1, RM.HOLD, **quiet), NOW + 60)
    check(st["seat_restart"]["FOUNDRY"]["state"] == "cancelled" and "restart_cancel" in dos(a) and not fires(a),
          "hold stands a pending SOFT restart down (%s)" % dos(a))
    tx = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False)
    tx.close()
    sid = "sid-soft"
    rs = {"source": "backstop", "ts": T0, "session_id": sid, "cancel_after": T0}
    RM.write("FOUNDRY", RM.HOLD, sid, ROOT)
    kw = dict(paused=lambda: None, work=lambda *a: [], pending=lambda *a: [], shard=lambda *a: None)
    old_tp, old_ff = SR.transcript_for, SR.final_fence
    SR.transcript_for = lambda *a: tx.name
    SR.final_fence = lambda *a, **k: []
    try:
        check(any("reset switch says hold" in h for h in SR.recheck_at_kill("FOUNDRY", s, rs, {"sessionId": sid, "pid": 1, "cwd": "/x"}, **kw)),
              "the kill's recheck refuses a SOFT restart too")
    finally:
        SR.transcript_for, SR.final_fence = old_tp, old_ff
        os.remove(RM.path("FOUNDRY", ROOT))


def test_live_schedule():
    with open(os.path.join(HERE, "dispatcher_schedule.json")) as f:
        b = json.load(f)["seat_restart"]["seats"]["BENCH"]
    check(b.get("hold_ceiling_tokens", 0) > b.get("backstop_hard_tokens", 0) and b.get("hold_max_s", 0) > 0, "live: a ceiling above the hard line")
    check(SR.config(D.load_schedule(os.path.join(HERE, "dispatcher_schedule.json")))["BENCH"]["hold_ceiling_tokens"] == b["hold_ceiling_tokens"],
          "config() carries it")
    check("mode" in SR.default_obs(D.load_schedule(os.path.join(HERE, "dispatcher_schedule.json")), lambda *a: []),
          "the live tick reads the switch: without this hold is a test-only feature")


# --- the blind check at 7065bf11 left mutants green; gen 26 swept 48 and pins each one inside a clause -------------------

def test_ready_fires_whatever_the_window_took_or_left_unpublished():
    """ready fires at the next ended turn: new work taken and an unpublished shard do not hold it (the next window has them),
    in decide() and in the kill's own recheck. The same two holds DO stand a goodbye down, so the control is real."""
    claim = {"seat": "FOUNDRY", "event": "claim", "id": "NEW_TICKET_1", "ts": SR._iso(NOW + 1)}
    st, s = fresh(), sch()
    o = window(5_000, RM.READY, ended_at=NOW - 4, work=[claim])
    o["seat_restart"]["shard"] = lambda seat: "1 line unpublished"
    a = go(s, st, o)
    check(fires(a) and st["seat_restart"]["FOUNDRY"]["source"] == "ready",
          "ready with new work and an unpublished shard: killed at the ended turn (%s)" % dos(a))
    st = fresh()
    a = go(s, st, window(HARD + 1, RM.AUTO, work=[claim]), NOW)
    a = go(s, st, window(HARD + 1, RM.AUTO, work=[claim]), NOW + 60)
    check(fires(a), "control: a size restart also ignores new work (%s)" % dos(a))
    tx = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False)
    tx.close()
    sid = "sid-ready-recheck"
    rs = {"source": "ready", "ts": T0, "session_id": sid, "cancel_after": T0, "now": True}
    sf = {"sessionId": sid, "pid": 1, "cwd": "/x"}
    RM.write("FOUNDRY", RM.READY, sid, ROOT)
    kw = dict(paused=lambda: None, work=lambda *a: [claim], pending=lambda *a: [], shard=lambda *a: "1 line unpublished")
    old_tp, old_ff = SR.transcript_for, SR.final_fence
    SR.transcript_for = lambda *a: tx.name
    SR.final_fence = lambda *a, **k: []
    try:
        h = SR.recheck_at_kill("FOUNDRY", s, rs, sf, **kw)
        check(not any("unpublished" in x or "NEW_TICKET_1" in x for x in h), "ready at the kill: no work or shard hold (%s)" % h)
        h = SR.recheck_at_kill("FOUNDRY", sch(kind="doorbell"), dict(rs, source="request"), sf, **kw)
        check(any("unpublished" in x for x in h) and any("NEW_TICKET_1" in x for x in h),
              "control: an ordinary seat's request at the kill IS held by both (%s)" % h)
    finally:
        SR.transcript_for, SR.final_fence = old_tp, old_ff
        os.remove(RM.path("FOUNDRY", ROOT))


def test_ready_is_bound_to_its_window_and_never_loops():
    s = sch()
    for label, patch in (("the pid is now another process", {"start": lambda pid: 99}),
                         ("no reading of his last message", {"last_human": lambda seat, c: None})):
        st = fresh()
        o = window(5_000, RM.READY, ended_at=NOW - 4)
        o["seat_restart"].update(patch)
        a = go(s, st, o)
        check(not {"restart_request", "restart_kill"} & set(dos(a)), "ready, %s: nothing armed (%s)" % (label, dos(a)))
    # NEGATIVE (SEATRESTART_AUDIT_WHOLE_FILE): the cursor is the END of the tx reading, never a later last_human read;
    # his input ending past that reading, or no byte end to bind to, arms nothing
    for label, patch in (("his input ended past the size reading",
                          {"last_human": lambda seat, c: (NOW - 300, None, 900, 1000)}),
                         ("the size reading has no byte end",
                          {"tx": lambda seat, c: {"ctx_tokens": 5_000, "last_kind": "assistant_end", "last_at": NOW - 4,
                                                  "last_user_at": NOW - 300}})):
        st = fresh()
        o = window(5_000, RM.READY, ended_at=NOW - 4)
        o["seat_restart"].update(patch)
        a = go(s, st, o)
        check("restart_request" not in dos(a), "ready, %s: nothing armed (%s)" % (label, dos(a)))
    st = fresh()
    o = window(5_000, RM.READY, ended_at=NOW - 4)
    o["seat_restart"]["tx"] = lambda seat, c: {"ctx_tokens": 5_000, "last_kind": "assistant_end", "last_at": NOW - 4,
                                               "last_user_at": NOW - 300, "size": 700}
    o["seat_restart"]["last_human"] = lambda seat, c: (NOW - 300, None, 500, 1000)
    go(s, st, o)
    check((st["seat_restart"].get("FOUNDRY") or {}).get("tx_offset") == 700,
          "ready: the cursor is the size reading's end (700), not the later file size (%s)" % st["seat_restart"].get("FOUNDRY"))
    # a ready restart that failed waits out its cooldown: no kill loop on a window that cannot be restarted
    st = fresh()
    st["seat_restart"]["FOUNDRY"] = {"state": "failed", "source": "ready", "ts": NOW - 100, "ended_at": NOW - 10,
                                     "cooldown_until": NOW + 600, "why": "x"}
    a = go(s, st, window(5_000, RM.READY, ended_at=NOW - 4))
    check(not {"restart_request", "restart_kill"} & set(dos(a)), "ready after a failure: held in cooldown (%s)" % dos(a))
    a = go(s, st, window(5_000, RM.READY, ended_at=NOW + 596), NOW + 601)
    check("restart_request" in dos(a), "and armed again once the cooldown is over (%s)" % dos(a))
    # his message the window shows after the one the round was armed from cancels it: the cancel window opens at his
    # last message, not at the tick
    st = fresh()
    o = window(5_000, RM.READY, ended_at=NOW - 4, helpers=[{"id": "h1", "alive": True, "desc": "x", "last_at": NOW}])
    o["seat_restart"]["tx"] = lambda seat, c: {"ctx_tokens": 5_000, "last_kind": "assistant_end", "last_at": NOW - 4,
                                               "last_user_at": NOW - 10, "size": 0}
    a = go(s, st, o)
    check(st["seat_restart"]["FOUNDRY"].get("cancel_after") == NOW - 300, "the round's cancel window opens at his last message")
    check(st["seat_restart"]["FOUNDRY"]["state"] == "cancelled" and not fires(a),
          "a message after that one cancels the round (%s, %s)" % (st["seat_restart"]["FOUNDRY"].get("state"), dos(a)))


def test_ceiling_at_the_kill():
    """Past the safety ceiling hold yields at the kill's recheck too, by size and by time; under it, it holds."""
    s = sch()
    tx = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False)
    tx.close()
    sid = "sid-ceil"
    rs = {"source": "backstop_hard", "hard": True, "ts": T0, "session_id": sid, "cancel_after": T0}
    sf = {"sessionId": sid, "pid": 1, "cwd": "/x"}
    kw = dict(paused=lambda: None, work=lambda *a: [], pending=lambda *a: [], shard=lambda *a: None)
    saved = SR.transcript_for, SR.final_fence, SR.tx_summary, SR.last_human
    SR.transcript_for = lambda *a: tx.name
    SR.final_fence = lambda *a, **k: []
    import time as _t
    try:
        for size, mode_age, human_age, holds_, label in ((HARD + 1, 60, 60, True, "under the ceiling"),
                                                         (CEIL, 60, 60, False, "at the token ceiling"),
                                                         (HARD + 1, 20000, 20000, False, "4 h with no word since the switch")):
            SR.tx_summary = lambda *a, size=size, **k: {"ctx_tokens": size, "last_kind": "assistant_end", "last_at": _t.time() - 100,
                                                         "last_user_at": None}
            SR.last_human = lambda *a, ha=human_age: (_t.time() - ha, None, None, 0)
            RM.write("FOUNDRY", RM.HOLD, sid, ROOT, now=_t.time() - mode_age)
            h = SR.recheck_at_kill("FOUNDRY", s, rs, sf, **kw)
            check(any("reset switch says hold" in x for x in h) == holds_, "hold at the kill, %s: %s (%s)" % (
                label, "holds" if holds_ else "yields", h))
    finally:
        SR.transcript_for, SR.final_fence, SR.tx_summary, SR.last_human = saved
        os.remove(RM.path("FOUNDRY", ROOT))


def test_only_the_conductor_can_flip_by_command():
    state = tempfile.mkdtemp(prefix="cr-mode-")
    home = tempfile.mkdtemp(prefix="cr-home-")
    env = dict(os.environ, RM_DISPATCHER_STATE=state, CLAUDE_CONFIG_DIR=home)

    def mode(*argv):
        return subprocess.run([sys.executable, os.path.join(HERE, "seat_restart.py"), "mode"] + list(argv), cwd=REPO, env=env,
                              capture_output=True, text=True, timeout=60)
    r = mode("hold", "--seat", "RUNNER", "--session", "sid-x")
    check(r.returncode == 2 and "REFUSED" in r.stdout and not os.path.exists(RM.path("RUNNER", state)),
          "another seat has no switch to set (%s %s)" % (r.returncode, r.stdout.strip()))
    r = mode("hold", "--seat", "BENCH")
    check(r.returncode == 2 and "which window" in r.stdout and not os.path.exists(RM.path("BENCH", state)),
          "no window named: refused, never a file for no window (%s %s)" % (r.returncode, r.stdout.strip()))
    r = mode("hold", "--seat", "BENCH", "--session", "sid-x")
    check(r.returncode == 0 and RM.read("BENCH", "sid-x", state)["mode"] == RM.HOLD, "control: the Conductor's window is set")


def test_only_the_switch_words():
    for said_ in ("ok", "okay", "yes", "go", "thanks", "sure", "stop", "wait", "reset", "no", "continue"):
        check(RM.mode_of_words(said_) is None, "%r is an ordinary reply, not the switch" % said_)
    # a goodbye outranks the switch in the hook: a message that is both closes out and sets nothing
    with open(os.path.join(HERE, "dispatcher_schedule.json")) as f:
        sch_ = json.load(f)
    sch_["seat_restart"]["seats"]["BENCH"]["goodbye_phrases"] = list(sch_["seat_restart"]["seats"]["BENCH"].get("goodbye_phrases") or []) + ["hold"]
    tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    json.dump(sch_, tmp)
    tmp.close()
    p = RM.path("BENCH", ROOT)
    with contextlib.suppress(OSError):
        os.remove(p)
    out = hook("hold", {"CONDUCTOR_GOODBYE_SCHEDULE": tmp.name})
    check(not os.path.exists(p) and "RESET SWITCH" not in out and out.strip(),
          "a message that is a goodbye and a switch word is the goodbye (%r)" % out[:120])


def test_status_line_says_past_the_ceiling():
    sl = os.path.join(REPO, "src", "RimMandrake", "Utils", "statusline.py")
    with open(os.path.join(HERE, "dispatcher_schedule.json")) as f:
        ceil = json.load(f)["seat_restart"]["seats"]["BENCH"]["hold_ceiling_tokens"]

    def line(used):
        ev = {"session_id": "sid-line", "model": {"id": "x"},
              "context_window": {"context_window_size": 1_000_000, "used_percentage": 100.0 * used / 1_000_000}}
        return subprocess.run([sys.executable, sl], input=json.dumps(ev), capture_output=True, text=True,
                              env=dict(os.environ, AGENT_SEAT="BENCH"), timeout=60).stdout
    RM.write("BENCH", RM.HOLD, "sid-line", ROOT)
    try:
        check("reset HOLD past its ceiling" in line(ceil + 1000), "hold past the token ceiling: the badge says so")
        check("reset HOLD" in line(ceil - 1000) and "past its ceiling" not in line(ceil - 1000), "under it: plain HOLD")
        check("past its ceiling" in RM.badge(RM.HOLD, True) and "past" not in RM.badge(RM.HOLD, False), "badge() carries it")
    finally:
        os.remove(RM.path("BENCH", ROOT))


def test_the_waking_window_is_never_the_dead_one():
    """last_dead_window passes over the window doing the waking even when no session file says it is alive."""
    home = tempfile.mkdtemp(prefix="cr-home-")
    os.makedirs(os.path.join(home, "sessions"))
    clone = tempfile.mkdtemp(prefix="cr-clone-")
    old = SR.claude_home
    SR.claude_home = lambda: home
    try:
        write_tx(home, clone, "aaaaaaaa-dead", window_recs("CONDUCTOR", "cli", "THE DEAD WINDOW'S REPLY"), 600)
        write_tx(home, clone, "bbbbbbbb-me", window_recs("CONDUCTOR", "cli", "THE WAKING WINDOW'S OWN WORDS"), 5)
        cfg = {"clone": clone, "session_name": "CONDUCTOR"}
        check("WAKING" in SR.last_dead_window(cfg)[1], "control: with no 'me' the newest transcript is taken")
        check("DEAD WINDOW" in SR.last_dead_window(cfg, "bbbbbbbb-me")[1], "with 'me' named, the waking window is passed over")
    finally:
        SR.claude_home = old


def test_handoff_says_when_the_reshow_crashed():
    """handoff.py --wake runs seat_restart.py last-reply; a crash there is said, never a silent empty block."""
    d = tempfile.mkdtemp(prefix="cr-site-")
    with open(os.path.join(d, "sitecustomize.py"), "w") as f:
        f.write("import os, sys\nif sys.argv and sys.argv[0].endswith('seat_restart.py'):\n    sys.stderr.write('boom')\n    sys.stderr.flush()\n    os._exit(5)\n")
    env = dict(os.environ, PYTHONPATH=d + os.pathsep + os.environ.get("PYTHONPATH", ""), AGENT_SEAT="BENCH", RIMFLOW_SEAT="BENCH")
    r = subprocess.run([sys.executable, os.path.join(REPO, "src/RimMandrake/Utils/handoff.py"), "--wake"], cwd=REPO, env=env,
                       capture_output=True, text=True, timeout=120)
    check("LAST REPLY: UNMEASURED (exit 5" in r.stdout, "a crashed re-show is said as UNMEASURED with its exit (%s)" % r.stdout[:200])


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
