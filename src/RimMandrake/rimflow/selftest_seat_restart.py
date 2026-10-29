#!/usr/bin/env python3
"""selftest_seat_restart.py — the fresh-window-per-ticket restart (seat_restart.py, wired into dispatcher.py).

FOUNDRY_CONTEXT_BUILD_FRESH_PER_TICKET. Every case runs on SIMULATED windows in a temp dir: no real Claude process is
killed or launched, nothing outside the temp dir is written. Covered:
  off by default        the schedule key `seat_restart` disabled -> nothing is decided, a request is left alone
  helper alive          a request is HELD while any helper of the window is alive (its subagent transcript is not
                        ended); a stale one holds too and alarms; the seat-side `request` refuses outright
  bridge / game hold    the shared bridge or the driver lock held by the seat, an unreadable bridge, or a transitional
                        game event by the seat -> HELD, never killed
  grace cancel          new input in the window's transcript after the request -> cancelled, never killed
  relaunch argv         the in-tile relaunch line is the WT profile's own LAUNCH + a first prompt: --remote-control and
                        --name carry 'AGENT <SEAT>'; the fallback is launch_fleet.ps1 narrowed to -Seats <SEAT>
  doorbell re-armed     verified only when armed/<SEAT>.json names the NEW session; otherwise failed + alarm
plus: kill only after sessions/<pid>.json names the session, dry-run never kills, busy -> failed, the backstop
threshold, the in-tile claim fires once per kill, and the Dispatcher neither rings nor 'recovers' a seat mid-restart.
"""
import json
import time
import subprocess
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="selftest_seat_restart_")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state")
os.environ["TESTQ_QUEUE"] = os.path.join(TMP, "testq")
os.environ["RM_SEAT_LOG_DIR"] = os.path.join(TMP, "seat_log")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import dispatcher as D  # noqa: E402
import seat_restart as SR  # noqa: E402

FAILS = []
CLONE = os.path.join(TMP, "foundry")
T0 = 1_000_000.0


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def sched(enabled=True, **seat_kw):
    seat = {"session_name": "AGENT FOUNDRY", "clone": CLONE, "model": "sonnet", "backstop": True}
    seat.update(seat_kw)
    s = {"seats": {"FOUNDRY": {"enabled": True, "wake": True, "recover_dead": True, "session_name": "AGENT FOUNDRY",
                               "clone": CLONE, "model": "sonnet"}},
         "seat_restart": {"enabled": enabled, "seats": {"FOUNDRY": seat}},
         "ledger_notes": False, "publish": False}
    p = os.path.join(TMP, "sched.json")
    with open(p, "w") as f:
        json.dump(s, f)
    return D.load_schedule(p)


def sess(sid="sid-old", status="idle", pid=4242, name="AGENT FOUNDRY"):
    return {"name": name, "status": status, "sessionId": sid, "pid": pid, "kind": "interactive", "cwd": CLONE,
            "procStart": "77"}


def obs(sessions=None, request=None, tx=None, helpers=(), bridge=None, game=None, armed=None, intile=None,
        paused=None, owner=None, killed=None):
    """One tick's reading. Defaults: the window idle and quiet (ended its turn long ago), nothing held."""
    tx = dict({"last_kind": "assistant_end", "last_at": T0 - 600, "last_user_at": T0 - 900, "ctx_tokens": 50_000},
              **(tx or {}))
    return {"paused": paused,
            "owner": lambda: owner or {"state": "MEASURED", "idle_seconds": 99_999},
            "agents": {"state": "MEASURED", "sessions": [sess()] if sessions is None else sessions},
            "seat_restart": {"request": lambda seat: request,
                        "tx": lambda seat, s: tx,
                        "helpers": lambda seat, s: None if helpers is None else list(helpers),
                        "killed": lambda seat: killed,
                        "start": lambda pid: 77,
                        "bridge": lambda seat: bridge or {"state": "MEASURED", "holders": []},
                        "game": lambda seat: game,
                        "armed": lambda seat: armed,
                        "intile": lambda seat, killed_at: intile}}


def req(ts=T0, sid="sid-old", pid=4242):
    return {"seat": "FOUNDRY", "pid": pid, "session_id": sid, "ticket": "SOME_TICKET_DONE", "reason": "closed", "ts": ts,
            "start": 77}


def fresh():
    return {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}


def run(sch, st, o, now, apply=True):
    acts = []

    def act(**kw):
        kw.setdefault("at", D.iso(now))
        acts.append(kw)
    SR.decide(sch, st, o, now, apply, act)
    return acts


def dos(acts):
    return [a["do"] for a in acts]


def state(st):
    return (st.get("seat_restart") or {}).get("FOUNDRY", {}).get("state")


def to_claim(sch, st, o, apply=True):
    """Request at T0, then a tick after the grace window: -> the actions of that second tick."""
    run(sch, st, o, T0 + 1, apply)
    return run(sch, st, o, T0 + SR.DEFAULTS["grace_s"] + 5, apply)


# ---------------------------------------------------------------------------------------------------------------------

def test_off_by_default():
    with open(D.DEFAULT_SCHEDULE) as f:
        real = json.load(f)
    check((real.get("seat_restart") or {}).get("enabled") is False,
          "the shipped schedule has seat_restart present and enabled:false")
    sch, st = sched(enabled=False), fresh()
    acts = run(sch, st, obs(request=req()), T0 + 500)
    check(acts == [] and not st.get("seat_restart"), "disabled: a request decides nothing (%s)" % dos(acts))


def test_grace_then_kill():
    sch, st = sched(), fresh()
    a1 = run(sch, st, obs(request=req()), T0 + 1)
    check(state(st) == "pending" and "restart_kill" not in dos(a1), "inside grace: pending, no kill (%s)" % dos(a1))
    check("restart_request" in dos(a1), "the taken request is journalled and consumed (%s)" % dos(a1))
    a2 = run(sch, st, obs(request=None), T0 + SR.DEFAULTS["grace_s"] + 5)
    k = [a for a in a2 if a["do"] == "restart_kill"]
    check(len(k) == 1 and k[0]["pid"] == 4242 and k[0]["session_id"] == "sid-old" and state(st) == "claimed",
          "after grace, quiet, nothing held: one restart_kill of the request's pid/session (%s)" % dos(a2))


def test_grace_cancel_on_new_input():
    sch, st = sched(), fresh()
    run(sch, st, obs(request=req()), T0 + 1)
    a = run(sch, st, obs(tx={"last_user_at": T0 + 30, "last_kind": "assistant_end", "last_at": T0 + 60}),
            T0 + SR.DEFAULTS["grace_s"] + 5)
    check(state(st) == "cancelled" and "restart_kill" not in dos(a) and "restart_cancel" in dos(a),
          "input after the request -> cancelled, never killed (%s)" % dos(a))
    st2 = fresh()
    run(sch, st2, obs(request=req()), T0 + 1)
    run(sch, st2, obs(sessions=[sess(sid="sid-other")]), T0 + 2)
    check((st2["seat_restart"]["FOUNDRY"]["state"]) == "cancelled", "the window's session changed under the request -> cancelled")
    st3 = fresh()
    a3 = run(sch, st3, obs(request=req(sid="sid-stale")), T0 + 1)
    check(state(st3) == "cancelled" and "restart_kill" not in dos(a3),
          "a request naming another session than the live one is cancelled at once")


def test_helper_alive_holds():
    sch, st = sched(), fresh()
    live = [{"id": "agent-a1", "alive": True, "last_at": T0 + 100}]
    a = to_claim(sch, st, obs(request=req(), helpers=live))
    check("restart_kill" not in dos(a) and "restart_hold" in dos(a) and state(st) == "pending",
          "a live helper holds the restart (%s)" % dos(a))
    check(any("helper" in (x.get("why") or "") for x in a if x["do"] == "restart_hold"), "the hold names the helper")
    a = run(sch, st, obs(helpers=[{"id": "agent-a1", "alive": False, "last_at": T0 + 100}]), T0 + 400)
    check("restart_kill" in dos(a), "the helper ended -> the kill goes ahead (%s)" % dos(a))
    st2 = fresh()
    stale = [{"id": "agent-old", "alive": True, "last_at": T0 - 2 * SR.DEFAULTS["helper_stale_s"]}]
    a2 = to_claim(sch, st2, obs(request=req(), helpers=stale))
    check("restart_kill" not in dos(a2) and any(x["do"] == "alarm" for x in a2),
          "a STALE live-looking helper still holds, and alarms (never read as dead) (%s)" % dos(a2))


def test_request_refused_with_live_helper():
    ok, why = SR.check_request("FOUNDRY", {"pid": 4242, "sessionId": "sid-old", "name": "AGENT FOUNDRY"},
                               [{"id": "agent-a1", "alive": True, "last_at": T0}])
    check(not ok and "agent-a1" in why, "seat-side request refuses while a helper is alive (%s)" % why)
    ok, why = SR.check_request("FOUNDRY", {"pid": 4242, "sessionId": "sid-old", "name": "AGENT FOUNDRY"}, [])
    check(ok, "no helper -> request allowed (%s)" % why)
    ok, why = SR.check_request("FOUNDRY", {"pid": 4242, "sessionId": "sid-old", "name": "AGENT BENCH"}, [])
    check(not ok, "a window whose session name is not the seat's cannot request the seat's restart")


def test_unpublished_shard_is_named():
    """V3_CUTOVER_MIGRATE_BENCH_LANE_TO_FOUNDRY: a close-out must not end with the seat's shard only in the clone."""
    root = tempfile.mkdtemp(prefix="unpub_", dir=TMP)
    origin, clone = os.path.join(root, "o.git"), os.path.join(root, "c")
    g = lambda *a: subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false"]
                                  + list(a), cwd=clone, capture_output=True, text=True)
    subprocess.run(["git", "init", "-q", "--bare", origin], capture_output=True)
    subprocess.run(["git", "clone", "-q", origin, clone], capture_output=True)
    shard = os.path.join(clone, "infrastructure", "state", "ledger", "events", "FOUNDRY.jsonl")
    os.makedirs(os.path.dirname(shard))
    open(shard, "w").write('{"a":1}\n')
    g("checkout", "-q", "-b", "main")
    g("add", "--", shard); g("commit", "-q", "-m", "x", "--", shard); g("push", "-q", "origin", "HEAD:main")
    g("fetch", "-q", "origin")
    check(SR.unpublished_shard("FOUNDRY", clone) is None, "a pushed, clean shard is published")
    open(shard, "a").write('{"a":2}\n')
    why = SR.unpublished_shard("FOUNDRY", clone)
    check(why is not None and "uncommitted" in why, "uncommitted shard lines are named (%s)" % why)
    g("commit", "-q", "-m", "y", "--", shard)
    why = SR.unpublished_shard("FOUNDRY", clone)
    check(why is not None and "not pushed" in why, "a committed but unpushed shard is named (%s)" % why)
    check(SR.unpublished_shard("BENCH", clone) is None, "another seat's shard is not this seat's concern")
    why = SR.unpublished_shard("FOUNDRY", os.path.join(root, "not_a_clone"))
    check(why is not None and why.startswith("UNMEASURED"), "a place git cannot read is UNMEASURED, never clean (%s)" % why)


def test_bridge_and_game_hold():
    sch = sched()
    for label, o in (
            ("shared bridge held by the seat", obs(request=req(), bridge={"state": "MEASURED", "holders": ["FOUNDRY"]})),
            ("bridge unreadable", obs(request=req(), bridge={"state": "UNMEASURED", "holders": [], "why": "x"})),
            ("game LOADING by the seat", obs(request=req(), game={"state": "LOADING", "at": T0 - 60})),
            ("PAUSE", obs(request=req(), paused="owner paused")),
            ("window busy", obs(request=req(), sessions=[sess(status="busy")]))):
        st = fresh()
        a = to_claim(sch, st, o)
        check("restart_kill" not in dos(a) and state(st) == "pending", "%s -> held, not killed (%s)" % (label, dos(a)))
    st = fresh()
    a = to_claim(sch, st, obs(request=req(), bridge={"state": "MEASURED", "holders": ["BENCH"]},
                              game={"state": "UP", "at": T0 - 60}))
    check("restart_kill" in dos(a), "bridge held by ANOTHER seat and a settled game -> not this seat's hold")
    st = fresh()
    st["seats"]["FOUNDRY"] = {"ring": {"ring_id": "r1", "rung_at": T0, "rung_iso": D.iso(T0), "attempt": 1}}
    a = to_claim(sch, st, obs(request=req()))
    check("restart_kill" not in dos(a), "a doorbell ring in flight holds the restart")


def test_busy_fails():
    sch, st = sched(), fresh()
    o = obs(request=req(), tx={"last_kind": "assistant_tool", "last_at": T0 + 100})
    run(sch, st, o, T0 + 1)
    for i in range(SR.DEFAULTS["busy_ticks"]):
        a = run(sch, st, o, T0 + SR.DEFAULTS["grace_s"] + 5 + 120 * i)
    check(state(st) == "failed" and "restart_kill" not in dos(a) and any(x["do"] == "alarm" for x in a),
          "never quiet for %d ticks -> failed: busy + alarm (%s)" % (SR.DEFAULTS["busy_ticks"], dos(a)))


def test_relaunch_argv():
    sch = sched()
    cfg = SR.config(sch)["FOUNDRY"]
    argv = SR.relaunch_argv("FOUNDRY", cfg)
    rc = argv.index("--remote-control")
    check(argv[rc + 1] == "AGENT FOUNDRY" and argv[argv.index("--name") + 1] == "AGENT FOUNDRY",
          "relaunch argv carries --remote-control 'AGENT FOUNDRY' and --name 'AGENT FOUNDRY' (%s)" % argv)
    check("--resume" not in argv and "--bg" not in argv and "-p" not in argv and "/login" not in " ".join(argv),
          "a FRESH interactive window: no --resume, no --bg, no -p, no /login")
    check("seat_restart.py wake --seat FOUNDRY" in argv[-1], "the first prompt runs the wake read (%s)" % argv[-1])
    import install_wt_seat_profiles as W
    launch = W.LAUNCH.format(script=W.BOUNDED.format(home=CLONE), label="AGENT_FOUNDRY", model="sonnet")
    launch = [x.replace("'AGENT_FOUNDRY'", "AGENT FOUNDRY") for x in launch.split()]
    check(argv[:-1] == launch, "relaunch argv is the WT profile's own LAUNCH line + the prompt (%s vs %s)"
          % (argv[:-1], launch))
    fb = SR.fallback_argv("FOUNDRY", {"relaunch": "powershell.exe -NoProfile -Command \"& 'X\\launch_fleet.ps1' "
                                                  "-Seats SERVER,HESTIA,EMERGENCY,FOUNDRY,BENCH\""})
    check(fb is not None and "-Seats FOUNDRY" in " ".join(fb) and "BENCH" not in " ".join(fb),
          "fallback narrows the fleet relaunch to -Seats FOUNDRY (%s)" % fb)


def test_kill_execute_and_dry():
    sch = sched()
    calls = []
    fx = {"session_file": lambda pid: {"pid": pid, "sessionId": "sid-old", "name": "AGENT FOUNDRY", "status": "idle"},
          "kill": lambda pid, start=None: calls.append(("kill", pid)) or "SIGTERM",
          "write_killed": lambda seat, rec: calls.append(("killed", seat, rec)),
          "recheck": lambda *a: [], "start": lambda pid: 77}
    st = fresh()
    a = [x for x in to_claim(sch, st, obs(request=req())) if x["do"] == "restart_kill"][0]
    res = SR.execute(a, sch, st, False, T0 + 200, fx)
    check(calls == [] and state(st) == "dry" and "DRY" in res.upper(), "dry run: nothing killed (%s, %s)" % (calls, res))
    st = fresh()
    a = [x for x in to_claim(sch, st, obs(request=req())) if x["do"] == "restart_kill"][0]
    bad = dict(fx, session_file=lambda pid: {"pid": pid, "sessionId": "sid-OTHER", "name": "AGENT FOUNDRY"})
    res = SR.execute(a, sch, st, True, T0 + 200, bad)
    check(calls == [] and state(st) == "failed", "sessions/<pid>.json names another session -> no kill (%s)" % res)
    st = fresh()
    a = [x for x in to_claim(sch, st, obs(request=req())) if x["do"] == "restart_kill"][0]
    res = SR.execute(a, sch, st, True, T0 + 200, fx)
    check(("kill", 4242) in calls and state(st) == "killed", "apply: the confirmed pid is killed (%s)" % res)
    rec = [c for c in calls if c[0] == "killed"][0][2]
    check("--remote-control" in rec["argv"] and rec["old_pid"] == 4242, "the killed record hands the tile its argv")


def killed_state(st, at=T0 + 200):
    st["seat_restart"] = {"FOUNDRY": {"state": "killed", "session_id": "sid-old", "pid": 4242, "killed_at": at,
                                 "ts": T0, "source": "request", "ticket": "SOME_TICKET_DONE"}}
    return st


def test_verify_and_rearm():
    sch = sched()
    st = killed_state(fresh())
    a = run(sch, st, obs(sessions=[]), T0 + 210)
    check(state(st) == "killed" and not [x for x in a if x["do"] in ("alarm", "restart_fallback")],
          "just killed, no window yet: wait")
    a = run(sch, st, obs(sessions=[sess(sid="sid-new", pid=5555)], intile={"at": T0 + 205}), T0 + 230)
    check(state(st) == "relaunched" and st["seat_restart"]["FOUNDRY"]["new_session"] == "sid-new",
          "a new session with the seat's name -> relaunched (%s)" % dos(a))
    a = run(sch, st, obs(sessions=[sess(sid="sid-new", pid=5555)], armed={"session_id": "sid-old", "pid": 4242}),
            T0 + 260)
    check(state(st) == "relaunched", "the OLD session's armed file is not a re-arm")
    a = run(sch, st, obs(sessions=[sess(sid="sid-new", pid=5555)], armed={"session_id": "sid-new", "pid": 5555}),
            T0 + 300)
    check(state(st) == "verified" and "restart_verified" in dos(a), "doorbell armed for the NEW session -> verified")
    st = killed_state(fresh())
    run(sch, st, obs(sessions=[sess(sid="sid-new", pid=5555)]), T0 + 230)
    a = run(sch, st, obs(sessions=[sess(sid="sid-new", pid=5555)], armed=None), T0 + 230 + SR.DEFAULTS["arm_s"] + 1)
    check(state(st) == "failed" and any(x["do"] == "alarm" for x in a),
          "never re-armed within arm_s -> failed + alarm (%s)" % dos(a))


def test_fallback_and_fail():
    sch = sched(machine={"relaunch": ["launch_fleet.ps1", "-Seats", "FOUNDRY"]})   # not the real machine.json
    st = killed_state(fresh())
    a = run(sch, st, obs(sessions=[]), T0 + 200 + SR.DEFAULTS["intile_wait_s"] + 1)
    check("restart_fallback" in dos(a), "no in-tile relaunch claimed in time -> launch_fleet fallback (%s)" % dos(a))
    a = run(sch, st, obs(sessions=[]), T0 + 210 + SR.DEFAULTS["intile_wait_s"] + 1)
    check("restart_fallback" not in dos(a), "the fallback fires once")
    a = run(sch, st, obs(sessions=[]), T0 + 200 + SR.DEFAULTS["intile_wait_s"] + SR.DEFAULTS["verify_s"] + 2)
    check(state(st) == "failed" and any(x["do"] == "alarm" for x in a), "no window at all -> failed + alarm")


def test_backstop():
    sch = sched(backstop_ctx_tokens=100_000, backstop_idle_s=900)
    st = fresh()
    a = run(sch, st, obs(tx={"ctx_tokens": 50_000, "last_at": T0 - 2000}), T0)
    check(not st.get("seat_restart", {}).get("FOUNDRY"), "under the context threshold: no backstop")
    a = run(sch, st, obs(tx={"ctx_tokens": 130_000, "last_at": T0 - 100}), T0)
    check(not st.get("seat_restart", {}).get("FOUNDRY"), "over threshold but idle only 100 s: no backstop")
    a = run(sch, st, obs(tx={"ctx_tokens": 130_000, "last_at": T0 - 2000},
                         helpers=[{"id": "h", "alive": True, "last_at": T0}]), T0)
    check(not st.get("seat_restart", {}).get("FOUNDRY"), "a live helper: no backstop")
    a = run(sch, st, obs(tx={"ctx_tokens": 130_000, "last_at": T0 - 2000}), T0)
    check(state(st) == "pending" and st["seat_restart"]["FOUNDRY"]["source"] == "backstop",
          "idle, no helper, context over threshold -> backstop restart pending (%s)" % dos(a))
    sch2 = sched(backstop=False)
    st2 = fresh()
    run(sch2, st2, obs(tx={"ctx_tokens": 130_000, "last_at": T0 - 2000}), T0)
    check(not st2.get("seat_restart", {}).get("FOUNDRY"), "backstop off for the seat -> nothing")


def test_transcript_readers():
    proj = os.path.join(TMP, "proj")
    sub = os.path.join(proj, "sid-x", "subagents")
    os.makedirs(sub)

    def rec(t, kind, ts, **kw):
        r = {"type": t, "timestamp": ts}
        r.update(kw)
        return r
    main = [rec("user", "u", "2026-10-28T01:00:00Z", message={"role": "user", "content": "do the thing"}),
            rec("assistant", "a", "2026-10-28T01:00:05Z", message={"stop_reason": "tool_use", "usage": {
                "input_tokens": 10, "cache_read_input_tokens": 90_000, "cache_creation_input_tokens": 1_000}}),
            rec("user", "tr", "2026-10-28T01:00:06Z", message={"role": "user", "content": [
                {"type": "tool_result", "content": "x"}]}),
            rec("assistant", "a", "2026-10-28T01:00:09Z", message={"stop_reason": "end_turn", "usage": {
                "input_tokens": 5, "cache_read_input_tokens": 95_000, "cache_creation_input_tokens": 0}})]
    with open(os.path.join(proj, "sid-x.jsonl"), "w") as f:
        f.write("garbage{\n" + "\n".join(json.dumps(r) for r in main) + "\n")
    s = SR.tx_summary(os.path.join(proj, "sid-x.jsonl"))
    check(s["last_kind"] == "assistant_end" and s["ctx_tokens"] == 95_005
          and s["last_user_at"] == D.S.parse_ts("2026-10-28T01:00:00Z"),
          "tx_summary: end_turn, context = last usage, a tool_result is not user input (%s)" % s)
    with open(os.path.join(sub, "agent-done.jsonl"), "w") as f:
        f.write("\n".join(json.dumps(r) for r in main) + "\n")
    with open(os.path.join(sub, "agent-live.jsonl"), "w") as f:
        f.write("\n".join(json.dumps(r) for r in main[:3]) + "\n"
                + json.dumps({"type": "attachment", "timestamp": "2026-10-28T01:00:07Z"}) + "\n")
    hs = {h["id"]: h["alive"] for h in SR.helpers_of(os.path.join(proj, "sid-x.jsonl"), now=None)}
    check(hs == {"agent-done": False, "agent-live": True}, "helpers_of: ended vs live subagent transcripts (%s)" % hs)


def test_intile_claim_once():
    root = os.path.join(TMP, "intile")
    os.makedirs(root)
    rec = {"seat": "FOUNDRY", "old_pid": 4242, "killed_at": T0, "argv": ["/x/claude_bounded.sh", "--remote-control",
                                                                          "AGENT FOUNDRY", "hi"]}
    SR.write_killed("FOUNDRY", rec, root=root)
    alive = {4242: False}
    a1 = SR.intile_claim("FOUNDRY", T0 + 5, alive=lambda p: alive.get(p, False), root=root)
    a2 = SR.intile_claim("FOUNDRY", T0 + 6, alive=lambda p: alive.get(p, False), root=root)
    check(a1 == rec["argv"] and a2 is None, "the in-tile relaunch is claimed exactly once per kill (%s, %s)" % (a1, a2))
    check(SR.read_intile("FOUNDRY", T0, root=root) is not None, "the claim leaves a marker the Dispatcher reads")
    SR.write_killed("FOUNDRY", dict(rec, killed_at=T0 + 100), root=root)
    check(SR.intile_claim("FOUNDRY", T0 + 100 + SR.DEFAULTS["intile_window_s"] + 1, alive=lambda p: False,
                          root=root) is None, "an old kill is never relaunched by a tile")
    SR.write_killed("FOUNDRY", dict(rec, killed_at=T0 + 200), root=root)
    check(SR.intile_claim("FOUNDRY", T0 + 205, alive=lambda p: True, root=root) is None,
          "the killed pid still alive -> no relaunch beside it")


def test_dispatcher_holds_seat_mid_restart():
    sch = sched()
    sch["seats"]["FOUNDRY"]["recover_dead"] = True
    st = killed_state(fresh())
    st["seats"]["FOUNDRY"] = {"session_id": "sid-old", "dead_since": T0 - 10_000}
    o = obs(sessions=[])
    o.update({"owner": lambda: {"state": "MEASURED", "idle_seconds": 99999}, "peek": lambda seat: None,
              "events": lambda seat, since: [], "consumed": lambda seat, rid: None, "alive": lambda pid: True})
    acts = D.decide(sch, st, o, T0 + 220, True)
    check("recover" not in dos(acts) and "ring" not in dos(acts),
          "Dispatcher: a seat mid-restart is neither rung nor 'recovered' (%s)" % dos(acts))
    calls = []
    fx = {"seat_restart": {"session_file": lambda pid: {"pid": pid, "sessionId": "sid-old", "name": "AGENT FOUNDRY",
                                                         "status": "idle"},
                           "kill": lambda pid, start=None: calls.append(pid) or "SIGTERM",
                           "write_killed": lambda s, r: None, "recheck": lambda *a: [], "start": lambda pid: 77,
                           "consume": lambda seat, **k: None, "fallback": lambda argv: calls.append(argv) or "ran"},
          "lock": lambda: None}
    st2 = fresh()
    run(sch, st2, obs(request=req()), T0 + 1)
    o2 = obs()
    o2.update({k: o[k] for k in ("owner", "peek", "events", "consumed", "alive")})
    acts = D.decide(sch, st2, o2, T0 + SR.DEFAULTS["grace_s"] + 5, False)
    D.execute(acts, sch, st2, os.path.join(TMP, "dry"), False, T0 + SR.DEFAULTS["grace_s"] + 5, fx)
    check("restart_kill" in dos(acts) and calls == [], "dispatcher dry-run decides the kill and kills nothing")
    with open(os.path.join(TMP, "dry", "journal.jsonl")) as f:
        j = [json.loads(x) for x in f]
    check(any(r["do"] == "restart_kill" and "DRY" in str(r.get("result")).upper() for r in j),
          "the dry kill is journalled")


def test_wt_profile_wrap_only_when_enabled():
    import install_wt_seat_profiles as W
    off = os.path.join(TMP, "sched_off.json")
    on = os.path.join(TMP, "sched_on.json")
    with open(off, "w") as f:
        json.dump({"seat_restart": {"enabled": False, "seats": {"FOUNDRY": {}}}}, f)
    with open(on, "w") as f:
        json.dump({"seat_restart": {"enabled": True, "seats": {"FOUNDRY": {}}}}, f)
    check(W.restart_seats(off) == set() and W.restart_seats(os.path.join(TMP, "missing.json")) == set(),
          "WT installer: key off or unreadable -> no seat wrapped")
    check(W.restart_seats(on) == {"FOUNDRY"}, "WT installer: key on -> the listed seat is wrapped")
    real = W.restart_seats
    try:
        W.restart_seats = lambda path=None: set()
        plain = W.build("FOUNDRY")[0]["commandline"]
        W.restart_seats = lambda path=None: {"FOUNDRY"}
        wrapped = W.build("FOUNDRY")[0]["commandline"]
    finally:
        W.restart_seats = real
    check("seat_loop.sh" not in plain and plain.endswith('exec $SHELL -l"') and "-eq 143 ] && exit 0" in plain, "WT: off -> the launch line is unchanged")
    check("seat_loop.sh FOUNDRY " in wrapped and "--remote-control 'AGENT FOUNDRY'" in wrapped,
          "WT: on -> seat_loop.sh wraps the same LAUNCH line (%s)" % wrapped[-160:])


def test_rollback_releases_the_seat():
    st = killed_state(fresh())
    check(SR.in_flight(st, "FOUNDRY", sched()), "enabled + killed: the restart owns the seat")
    check(not SR.in_flight(st, "FOUNDRY", sched(enabled=False)),
          "key turned off mid-restart: the Dispatcher gets the seat back (rollback)")


# ---- GPT review 2026-10-28 (foundry_fresh/gpt/review.md): HIGH 1-7, MEDIUM 8-10

def at_kill(sch, st, now=None):
    run(sch, st, obs(request=req()), T0 + 1)
    return run(sch, st, obs(), now or T0 + SR.DEFAULTS["grace_s"] + 5)


def test_r1_recheck_at_the_kill():
    sch, st = sched(), fresh()
    acts = at_kill(sch, st)
    k = [a for a in acts if a["do"] == "restart_kill"][0]
    calls = []
    fx = {"session_file": lambda pid: {"pid": pid, "sessionId": "sid-old", "name": "AGENT FOUNDRY", "status": "idle"},
          "kill": lambda pid, start=None: calls.append(pid) or "SIGTERM", "write_killed": lambda s_, r: None,
          "recheck": lambda seat, sch_, rs, sf: ["helper(s) alive: agent-x"], "start": lambda pid: 77}
    res = SR.execute(k, sch, st, True, T0 + 130, fx)
    check(calls == [] and state(st) == "pending", "R1 a hold that appears between decide and kill stops it (%s)" % res)
    st2 = fresh()
    k2 = [a for a in at_kill(sch, st2) if a["do"] == "restart_kill"][0]
    fx2 = dict(fx, recheck=lambda *a: [], session_file=lambda pid: {"pid": pid, "sessionId": "sid-old",
                                                                     "name": "AGENT FOUNDRY"})
    SR.execute(k2, sch, st2, True, T0 + 130, fx2)
    check(calls == [] and state(st2) != "killed", "R1 a session file without status is not idle: no kill")


def test_r2_owner_active_holds():
    sch, st = sched(), fresh()
    run(sch, st, obs(request=req()), T0 + 1)
    acts = run(sch, st, obs(owner={"state": "MEASURED", "idle_seconds": 20}), T0 + SR.DEFAULTS["grace_s"] + 5)
    check(dos(acts) == ["restart_hold"] and "owner" in acts[0]["why"], "R2 the owner at the keyboard holds (%s)" % acts)
    acts = run(sch, st, obs(owner={"state": "UNMEASURED"}), T0 + SR.DEFAULTS["grace_s"] + 10)
    check(dos(acts) == ["restart_hold"], "R2 owner presence unmeasured holds")


def test_r3_helpers_unreadable_hold_and_never_age_out():
    sch, st = sched(), fresh()
    run(sch, st, obs(request=req()), T0 + 1)
    acts = run(sch, st, obs(helpers=None), T0 + SR.DEFAULTS["grace_s"] + 5)
    check(dos(acts) == ["restart_hold"], "R3 helper inventory unreadable -> held (%s)" % dos(acts))
    tdir = os.path.join(TMP, "r3")
    sub = os.path.join(tdir, "sid", "subagents")
    os.makedirs(sub, exist_ok=True)
    main = os.path.join(tdir, "sid.jsonl")
    open(main, "w").close()
    with open(os.path.join(sub, "agent-old.jsonl"), "w") as f:
        f.write(json.dumps({"type": "assistant", "message": {"stop_reason": "tool_use"}}) + "\n")
    os.utime(os.path.join(sub, "agent-old.jsonl"), (1, 1))
    h = SR.helpers_of(main, now=time.time())
    check([x["id"] for x in h if x["alive"]] == ["agent-old"], "R3 a live-looking helper silent for days still counts")
    check(SR.helpers_of(os.path.join(tdir, "nope.jsonl"), now=time.time()) is None,
          "R3 no main transcript -> helpers UNMEASURED (None), not 'none'")


def test_r4_pid_identity_and_death():
    p = subprocess.Popen(["sleep", "60"])
    start = SR.proc_start(p.pid)
    check(start is not None, "R4 a live pid has a start time")
    check(SR.kill_pid(p.pid, start=start + 1) .startswith("refused"), "R4 a different start time (pid reused) -> refused")
    check(SR.proc_alive(p.pid, start), "R4 ... and the process was not touched")
    res = SR.kill_pid(p.pid, start=start)
    p.wait(timeout=5)
    check(res.startswith("SIGTERM") and not SR.proc_alive(p.pid, start), "R4 the right process is killed (%s)" % res)


def test_r5_fallback_and_tile_share_one_election():
    root = os.path.join(TMP, "r5")
    killed_at = T0 + 200
    SR.write_killed("FOUNDRY", {"seat": "FOUNDRY", "old_pid": 999999, "session_id": "sid-old", "killed_at": killed_at,
                                "argv": ["/bin/true"]}, root=root)
    ran = []
    st = killed_state(fresh(), at=killed_at)
    a = {"do": "restart_fallback", "seat": "FOUNDRY", "argv": ["x"], "killed_at": killed_at}
    r1 = SR.execute(a, sched(), st, True, killed_at + 40, {"fallback": lambda argv: ran.append(1) or "ran",
                                                            "root": root})
    check(ran == [1], "R5 the fallback claims the launch first (%s)" % r1)
    check(SR.intile_claim("FOUNDRY", killed_at + 41, alive=lambda pid: False, root=root) is None,
          "R5 ... so a late tile cannot launch a second window")
    r2 = SR.execute(a, sched(), st, True, killed_at + 42, {"fallback": lambda argv: ran.append(2) or "ran",
                                                            "root": root})
    check(ran == [1] and "claimed" in r2, "R5 a claimed launch is never run twice (%s)" % r2)


def test_r6_crash_after_the_kill_reconciles():
    sch, st = sched(), fresh()
    at_kill(sch, st)
    check(state(st) == "claimed", "R6 setup: claimed")
    acts = run(sch, st, obs(sessions=[], killed={"session_id": "sid-old", "killed_at": T0 + 126, "old_pid": 4242,
                                                  "old_alive": False}),
               T0 + 200)
    check(state(st) == "killed" and st["seat_restart"]["FOUNDRY"]["killed_at"] == T0 + 126,
          "R6 a killed record for the claimed session moves it to killed (%s)" % dos(acts))


def test_r7_rollback_fences_a_killed_window():
    st = killed_state(fresh(), at=time.time() - 30)
    check(SR.in_flight(st, "FOUNDRY", sched(enabled=False)), "R7 disabled right after a kill: still the restart's")
    st = killed_state(fresh(), at=time.time() - 3600)
    check(not SR.in_flight(st, "FOUNDRY", sched(enabled=False)), "R7 disabled, old kill: the Dispatcher's again")


def test_m8_recover_in_flight_holds():
    sch, st = sched(), fresh()
    run(sch, st, obs(request=req()), T0 + 1)
    st["seats"]["FOUNDRY"] = {"recover": {"at": T0}}
    acts = run(sch, st, obs(), T0 + SR.DEFAULTS["grace_s"] + 5)
    check(dos(acts) == ["restart_hold"], "M8 a recovery in flight holds the restart")


def test_m9_fallback_argv_tokenised():
    m = {"relaunch": ["powershell.exe", "-File", "launch_fleet.ps1", "-Seats", "SERVER,FOUNDRY,BENCH"]}
    check(SR.fallback_argv("FOUNDRY", m)[-2:] == ["-Seats", "FOUNDRY"], "M9 a tokenised -Seats list is narrowed")
    m = {"relaunch": ["pwsh", "-Command", "& 'x.ps1' -Seats FOUNDRY"]}
    check(SR.fallback_argv("FOUNDRY", m) == m["relaunch"], "M9 an already-narrow launcher is used as is")


def test_m10_consume_only_the_request_read():
    root = os.path.join(TMP, "m10")
    p = SR.request_path("FOUNDRY", root)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        json.dump({"ts": 222.0}, f)
    SR.consume_request("FOUNDRY", root, ts=111.0)
    check(os.path.exists(p), "M10 a newer request than the one decided on is left in place")
    SR.consume_request("FOUNDRY", root, ts=222.0)
    check(not os.path.exists(p), "M10 the request decided on is consumed")


# ---- GPT confirmation round 2026-10-28 (foundry_fresh/gpt/review2.md)

def test_c1_recheck_reads_owner_and_pause():
    sch, st = sched(), fresh()
    rs = {"ts": T0, "session_id": "sid-old"}
    pdir = os.path.join(TMP, "state")
    os.makedirs(pdir, exist_ok=True)
    holds = SR.recheck_at_kill("FOUNDRY", sch, rs, {"pid": 1, "sessionId": "sid-old", "cwd": CLONE},
                               owner=lambda: {"state": "MEASURED", "idle_seconds": 3}, paused=lambda: "owner said stop")
    check(any("owner" in h for h in holds) and any("PAUSE" in h for h in holds),
          "C1 the kill-time recheck reads the owner clock and PAUSE again (%s)" % holds)


def test_c3_unlistable_subagents_dir_is_unmeasured():
    tdir = os.path.join(TMP, "c3")
    os.makedirs(tdir, exist_ok=True)
    main = os.path.join(tdir, "sid.jsonl")
    open(main, "w").close()
    with open(os.path.join(tdir, "sid"), "w") as f:     # 'sid' is a FILE: the subagents dir cannot be listed
        f.write("x")
    check(SR.helpers_of(main, now=time.time()) is None, "C3 a subagents path that cannot be listed -> None")
    os.makedirs(os.path.join(TMP, "c3b"), exist_ok=True)
    m2 = os.path.join(TMP, "c3b", "s2.jsonl")
    open(m2, "w").close()
    check(SR.helpers_of(m2, now=time.time()) == [], "C3 no subagents dir at all -> no helpers (a window that never had one)")


def test_c6_reconcile_only_when_the_old_pid_is_dead():
    sch, st = sched(), fresh()
    at_kill(sch, st)
    run(sch, st, obs(killed={"session_id": "sid-old", "killed_at": T0 + 126, "old_pid": 4242, "old_alive": True}),
        T0 + 200)
    check(state(st) == "claimed", "C6 a killed record whose pid is still alive is NOT read as a kill (%s)" % state(st))


def test_c7_claimed_is_fenced_when_disabled():
    st = fresh()
    st["seat_restart"] = {"FOUNDRY": {"state": "claimed", "claimed_at": time.time() - 20, "session_id": "sid-old"}}
    check(SR.in_flight(st, "FOUNDRY", sched(enabled=False)), "C7 disabled right after a claim: still fenced")


def test_c8_pending_does_not_freeze_a_recovery():
    st = fresh()
    st["seat_restart"] = {"FOUNDRY": {"state": "pending", "ts": T0, "session_id": "sid-old"}}
    check(not SR.in_flight(st, "FOUNDRY", sched()), "C8 a PENDING restart leaves ring/recover to the Dispatcher")


# ---- GPT confirmation round 3 (foundry_fresh/gpt/review3.md)

def test_d1_kill_needs_the_birth_identity_seen_at_the_request():
    sch = sched()
    for label, start in (("a different start time", 78), ("no start time", None)):
        st, calls = fresh(), []
        k = [a for a in at_kill(sch, st) if a["do"] == "restart_kill"][0]
        if start is None:
            st["seat_restart"]["FOUNDRY"].pop("start", None)
        fx = {"session_file": lambda pid: {"pid": pid, "sessionId": "sid-old", "name": "AGENT FOUNDRY",
                                           "status": "idle"},
              "kill": lambda pid, start=None: calls.append(pid) or "SIGTERM", "write_killed": lambda s_, r: None,
              "recheck": lambda *a: [], "start": lambda pid: start if start is not None else 77}
        res = SR.execute(k, sch, st, True, T0 + 130, fx)
        check(calls == [] and state(st) == "failed", "D1 %s than the request's -> refused (%s)" % (label, res))


def test_d2_helpers_use_the_listing_they_checked():
    tdir = os.path.join(TMP, "d2")
    sub = os.path.join(tdir, "sid", "subagents")
    os.makedirs(sub, exist_ok=True)
    main = os.path.join(tdir, "sid.jsonl")
    open(main, "w").close()
    with open(os.path.join(sub, "agent-run.jsonl"), "w") as f:
        f.write(json.dumps({"type": "assistant", "message": {"stop_reason": "tool_use"}}) + "\n")
    real = SR.glob.glob
    SR.glob.glob = lambda *a, **k: []
    try:
        h = SR.helpers_of(main, now=time.time())
    finally:
        SR.glob.glob = real
    check(h and h[0]["alive"], "D2 a second enumeration that comes back empty cannot hide a live helper (%s)" % h)


def test_d3_no_tile_claim_after_the_relaunch_deadline():
    cfg = SR.config(sched(intile_window_s=999))["FOUNDRY"]
    check(cfg["intile_window_s"] <= cfg["intile_wait_s"] + cfg["verify_s"],
          "D3 a tile can never claim after decide() has given the relaunch up (%s)" % cfg["intile_window_s"])
    check(SR.DEFAULTS["intile_window_s"] <= SR.DEFAULTS["intile_wait_s"] + SR.DEFAULTS["verify_s"],
          "D3 ... and the tile's own default window agrees")


def test_e1_backstop_binds_the_registered_birth_identity():
    sch = sched(backstop_ctx_tokens=100_000, backstop_idle_s=900)
    for label, sf, seen in (("a reused pid (registered 77, live 78)", sess(), 78),
                            ("a registration without procStart", dict(sess(), procStart=None), 77)):
        st = fresh()
        o = obs(sessions=[sf], tx={"ctx_tokens": 130_000, "last_at": T0 - 2000})
        o["seat_restart"]["start"] = lambda pid, seen=seen: seen
        run(sch, st, o, T0)
        check(not st.get("seat_restart", {}).get("FOUNDRY"), "E1 backstop refused for %s" % label)
    st = fresh()
    run(sch, st, obs(tx={"ctx_tokens": 130_000, "last_at": T0 - 2000}), T0)
    check(st.get("seat_restart", {}).get("FOUNDRY", {}).get("start") == 77,
          "E1 a matching registration -> the backstop binds that birth time")


def test_e2_tile_claim_obeys_the_deadline_written_at_the_kill():
    sch = sched(intile_wait_s=10, verify_s=20)
    st, recs = fresh(), []
    k = [a for a in at_kill(sch, st) if a["do"] == "restart_kill"][0]
    fx = {"session_file": lambda pid: {"pid": pid, "sessionId": "sid-old", "name": "AGENT FOUNDRY", "status": "idle"},
          "kill": lambda pid, start=None: "SIGTERM", "write_killed": lambda s_, r: recs.append(r),
          "recheck": lambda *a: [], "start": lambda pid: 77}
    SR.execute(k, sch, st, True, T0 + 130, fx)
    check(recs and recs[0].get("window_s") == 30, "E2 the killed record carries the configured window (%s)" % recs)
    root = os.path.join(TMP, "e2")
    os.makedirs(root, exist_ok=True)
    SR.write_killed("FOUNDRY", {"seat": "FOUNDRY", "old_pid": 1, "killed_at": T0, "argv": ["x"], "window_s": 30},
                    root=root)
    check(SR.intile_claim("FOUNDRY", T0 + 40, alive=lambda p: False, root=root) is None,
          "E2 a tile 40 s after a kill whose window was 30 s does not claim")


def test_e3_helpers_never_skip_the_listing_on_a_stat_error():
    tdir = os.path.join(TMP, "e3")
    sub = os.path.join(tdir, "sid", "subagents")
    os.makedirs(sub, exist_ok=True)
    main = os.path.join(tdir, "sid.jsonl")
    open(main, "w").close()
    with open(os.path.join(sub, "agent-run.jsonl"), "w") as f:
        f.write(json.dumps({"type": "assistant", "message": {"stop_reason": "tool_use"}}) + "\n")
    real = SR.os.path.lexists
    SR.os.path.lexists = lambda p: False
    try:
        h = SR.helpers_of(main, now=time.time())
    finally:
        SR.os.path.lexists = real
    check(h and h[0]["alive"], "E3 a failed stat of the session dir cannot hide a live helper (%s)" % h)


def test_e4_no_launcher_fails_only_after_the_tile_window():
    sch = sched()
    cfg = SR.config(sch)["FOUNDRY"]
    st = killed_state(fresh())
    real = SR.fallback_argv
    SR.fallback_argv = lambda *a, **k: None
    try:
        a = run(sch, st, obs(sessions=[]), T0 + 200 + cfg["intile_wait_s"] + 1)
        check(state(st) == "killed" and "alarm" not in dos(a),
              "E4 no fleet launcher: no failure while a tile may still claim (%s)" % dos(a))
        a = run(sch, st, obs(sessions=[]), T0 + 200 + cfg["intile_wait_s"] + cfg["verify_s"])
        check(state(st) == "failed" and "alarm" in dos(a), "E4 ... failed + alarm at the deadline (%s)" % dos(a))
    finally:
        SR.fallback_argv = real
    root = os.path.join(TMP, "e4")
    os.makedirs(root, exist_ok=True)
    SR.write_killed("FOUNDRY", {"seat": "FOUNDRY", "old_pid": 1, "killed_at": T0, "argv": ["x"],
                                "window_s": cfg["intile_window_s"]}, root=root)
    check(SR.intile_claim("FOUNDRY", T0 + cfg["intile_wait_s"] + cfg["verify_s"], alive=lambda p: False,
                          root=root) is None, "E4 ... and no tile claims at that same second")


def test_e5_a_reused_old_pid_does_not_block_the_relaunch():
    me = os.getpid()
    root = os.path.join(TMP, "e5")
    os.makedirs(root, exist_ok=True)
    SR.write_killed("FOUNDRY", {"seat": "FOUNDRY", "old_pid": me, "old_start": SR.proc_start(me) + 1,
                                "killed_at": T0, "argv": ["x"]}, root=root)
    check(SR.intile_claim("FOUNDRY", T0 + 5, root=root) == ["x"],
          "E5 the killed pid now belongs to another process -> the tile still claims")
    SR.write_killed("FOUNDRY", {"seat": "FOUNDRY", "old_pid": me, "old_start": SR.proc_start(me) + 1,
                                "killed_at": T0 + 1, "argv": ["x"]}, root=root)
    res = SR.execute({"do": "restart_fallback", "seat": "FOUNDRY", "argv": ["y"], "killed_at": T0 + 1},
                     sched(), fresh(), True, T0 + 40, {"root": root, "fallback": lambda argv: "launched"})
    check(res == "launched", "E5 ... and so does the fallback (%s)" % res)


def test_e6_the_deadline_is_the_one_written_at_the_kill():
    st = fresh()
    k = [a for a in at_kill(sched(), st) if a["do"] == "restart_kill"][0]
    fx = {"session_file": lambda pid: {"pid": pid, "sessionId": "sid-old", "name": "AGENT FOUNDRY", "status": "idle"},
          "kill": lambda pid, start=None: "SIGTERM", "write_killed": lambda s_, r: None,
          "recheck": lambda *a: [], "start": lambda pid: 77}
    SR.execute(k, sched(), st, True, T0 + 130, fx)
    small = sched(intile_wait_s=10, verify_s=20)          # the config shrinks after the kill
    real = SR.fallback_argv
    SR.fallback_argv = lambda *a, **k: None
    try:
        a = run(small, st, obs(sessions=[]), T0 + 130 + 31)
        check(state(st) == "killed" and "alarm" not in dos(a),
              "E6 a shrunk config cannot fail the restart while the kill-time tile window is open (%s)" % dos(a))
        a = run(small, st, obs(sessions=[]), T0 + 130 + SR.DEFAULTS["intile_window_s"])
        check(state(st) == "failed", "E6 ... it fails at the kill-time window (%s)" % dos(a))
    finally:
        SR.fallback_argv = real
    st2 = fresh()
    st2["seat_restart"] = {"FOUNDRY": {"state": "claimed", "session_id": "sid-old", "pid": 4242, "ts": T0,
                                       "claimed_at": T0 + 120, "source": "request"}}
    run(sched(), st2, obs(sessions=[], killed={"session_id": "sid-old", "killed_at": T0 + 125, "old_alive": False,
                                              "window_s": 77}), T0 + 126)
    check(st2["seat_restart"]["FOUNDRY"].get("window_s") == 77, "E6 reconciliation restores the kill-time window")


def main():
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
            except Exception as e:  # noqa: BLE001
                import traceback
                traceback.print_exc()
                check(False, "%s raised %s: %s" % (name, type(e).__name__, e))
    print("\n%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
