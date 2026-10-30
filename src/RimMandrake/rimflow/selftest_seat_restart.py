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
import inspect
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


def _no_presence():
    raise AssertionError("seat_restart read the owner's presence (owner 2026-10-30: never)")


def obs(sessions=None, request=None, tx=None, helpers=(), bridge=None, game=None, armed=None, intile=None,
        paused=None, killed=None, work=(), human_since=(), cursor=(), last_human=(None, None, None, 0)):
    """One tick's reading. Defaults: the window idle and quiet (ended its turn long ago), nothing held."""
    tx = dict({"last_kind": "assistant_end", "last_at": T0 - 600, "last_user_at": T0 - 900, "ctx_tokens": 50_000},
              **(tx or {}))
    return {"paused": paused,
            "owner": _no_presence,      # owner 2026-10-30: never read; calling it fails the tick
            "agents": {"state": "MEASURED", "sessions": [sess()] if sessions is None else sessions},
            "seat_restart": {"request": lambda seat: request,
                        "tx": lambda seat, s: tx,
                        "helpers": lambda seat, s: None if helpers is None else list(helpers),
                        "killed": lambda seat: killed,
                        "start": lambda pid: 77,
                        "bridge": lambda seat: bridge or {"state": "MEASURED", "holders": []},
                        "game": lambda seat: game,
                        "armed": lambda seat: armed,
                        "intile": lambda seat, killed_at: intile,
                        "work": lambda seat, since: None if work is None else list(work),
                        "human_since": lambda seat, s, off, after: None if human_since is None else list(human_since),
                        "cursor": lambda seat, s, rs: None if cursor is None else (clean_scan() if cursor == () else cursor),
                        "last_human": lambda seat, s: last_human}}


def clean_scan(**kw):
    """A full cursor read that found nothing: no input, every record parsed, a fixed size (no growth)."""
    return dict({"human": [], "inputs": [], "last_at": None, "size": 100, "malformed": None, "torn": None}, **kw)


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
    sr = real.get("seat_restart") or {}
    # Owner 2026-10-28 ("Less cautioun, more progress?") took it live after the dry request was taken, held and
    # cancelled on new input: the shipped schedule is now enabled and wet, or switched off.
    check(sr.get("enabled") is False or (sr.get("enabled") is True and sr.get("dry") in (False, None)),
          "the shipped schedule has seat_restart present and either enabled:false or enabled live (dry off)")
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
    # CONDUCTOR_RCNAME_RENAME_DISPATCHER_ALIAS: seat BENCH answers to CONDUCTOR and its pre-rename alias AGENT BENCH
    for n in ("CONDUCTOR", "CONDUCTOR \u25b6 ITEM_X", "AGENT BENCH", "AGENT BENCH \u25b6 ITEM_X"):
        ok, why = SR.check_request("BENCH", {"pid": 4242, "sessionId": "sid-old", "name": n}, [])
        check(ok, "BENCH's window named %r may request its restart (%s)" % (n, why))
    for n in ("AGENT CONDUCTOR", "CONDUCTORX", "AGENT FOUNDRY"):
        ok, why = SR.check_request("BENCH", {"pid": 4242, "sessionId": "sid-old", "name": n}, [])
        check(not ok, "a window named %r cannot request BENCH's restart (%s)" % (n, why))
    cfg = SR.config({"seats": {"BENCH": {"session_name": "CONDUCTOR", "session_aliases": ["AGENT BENCH"],
                                            "clone": "/c"}},
                        "seat_restart": {"enabled": True, "seats": {"BENCH": {}}}})["BENCH"]
    check(cfg["session_name"] == "CONDUCTOR" and cfg.get("session_aliases") == ["AGENT BENCH"],
          "seat_restart's cfg carries the schedule's session_aliases")
    argv = SR.relaunch_argv("BENCH", cfg)
    check(argv[argv.index("--name") + 1] == "CONDUCTOR" == argv[argv.index("--remote-control") + 1],
          "a BENCH relaunch takes the NEW name, never the alias")


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
    check(SR.tx_summary(os.path.join(proj, "sid-x.jsonl")) is None,
          "tx_summary: a malformed line is UNMEASURED, not skipped (review 2 P0-2: fail closed)")
    with open(os.path.join(proj, "sid-x.jsonl"), "w") as f:
        f.write("\n".join(json.dumps(r) for r in main) + "\n")
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
    o.update({"peek": lambda seat: None,
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
    o2.update({k: o[k] for k in ("peek", "events", "consumed", "alive")})
    acts = D.decide(sch, st2, o2, T0 + SR.DEFAULTS["grace_s"] + 5, False)
    D.execute(acts, sch, st2, os.path.join(TMP, "dry"), False, T0 + SR.DEFAULTS["grace_s"] + 5, fx)
    check("restart_kill" in dos(acts) and calls == [], "dispatcher dry-run decides the kill and kills nothing")
    with open(os.path.join(TMP, "dry", "journal.jsonl")) as f:
        j = [json.loads(x) for x in f]
    check(any(r["do"] == "restart_kill" and "DRY" in str(r.get("result")).upper() for r in j),
          "the dry kill is journalled")


def test_dry_key_under_live_apply():
    """seat_restart.dry true: the live --apply timer walks the whole restart and kills nothing, so the first ticket after
    enabling is a dry ticket (golive §10 step 2: the timer is no longer dry by then)."""
    sch = sched()
    sch["seat_restart"]["dry"] = True
    calls = []
    fx = {"seat_restart": {"session_file": lambda pid: {"pid": pid, "sessionId": "sid-old", "name": "AGENT FOUNDRY",
                                                         "status": "idle"},
                           "kill": lambda pid, start=None: calls.append(pid) or "SIGTERM",
                           "write_killed": lambda s, r: None, "recheck": lambda *a: [], "start": lambda pid: 77,
                           "consume": lambda seat, **k: calls.append("consume") or None,
                           "fallback": lambda argv: calls.append(argv) or "ran"},
          "lock": lambda: None}
    o = {"owner": _no_presence, "peek": lambda seat: None,
         "events": lambda seat, since: [], "consumed": lambda seat, rid: None, "alive": lambda pid: True}
    st = fresh()
    root = os.path.join(TMP, "livedry")
    os.makedirs(root, exist_ok=True)
    all_acts = []
    for now, ob in ((T0 + 1, obs(request=req())), (T0 + SR.DEFAULTS["grace_s"] + 5, obs(request=req()))):
        ob.update(o)
        acts = D.decide(sch, st, ob, now, True)
        D.execute(acts, sch, st, root, True, now, fx)
        all_acts += acts
    check("restart_kill" in dos(all_acts) and calls == [],
          "seat_restart.dry under --apply: the kill is decided, nothing is killed, consumed or launched (%s, %s)"
          % (dos(all_acts), calls))
    with open(os.path.join(root, "journal.jsonl")) as f:
        j = [json.loads(x) for x in f]
    check(any(r["do"] == "restart_kill" and "WOULD SIGTERM" in str(r.get("result")).upper() for r in j),
          "seat_restart.dry: the would-be kill is journalled in the LIVE journal")
    rs = st["seat_restart"]["FOUNDRY"]
    check(rs.get("state") == "dry" and not SR.in_flight(st, "FOUNDRY", sch, T0 + SR.DEFAULTS["grace_s"] + 125),
          "seat_restart.dry: the dry ticket ends in state dry, which does not fence FOUNDRY's rings (%s)" % rs.get("state"))


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


def test_r2_owner_presence_never_holds():
    """Owner 2026-10-30: "I really, really need you to strip "when I come back to the machine" as an event for
    anything changing." obs()'s owner observer raises if read; the restart goes ahead with no owner hold."""
    sch, st = sched(), fresh()
    run(sch, st, obs(request=req()), T0 + 1)
    acts = run(sch, st, obs(), T0 + SR.DEFAULTS["grace_s"] + 5)
    check("restart_kill" in dos(acts) and not any("owner" in (a.get("why") or "").lower() and a["do"] == "restart_hold"
                                                  for a in acts),
          "R2 presence is never read and never holds: grace over -> kill (%s)" % dos(acts))
    check(not hasattr(SR, "owner_ok") and not hasattr(SR, "owner_need")
          and "owner_idle_s" not in SR.DEFAULTS and "backstop_owner_idle_s" not in SR.DEFAULTS,
          "R2 the owner-idle gate and its knobs are gone")


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

def test_c1_recheck_reads_pause_not_owner():
    sch, st = sched(), fresh()
    rs = {"ts": T0, "session_id": "sid-old"}
    pdir = os.path.join(TMP, "state")
    os.makedirs(pdir, exist_ok=True)
    holds = SR.recheck_at_kill("FOUNDRY", sch, rs, {"pid": 1, "sessionId": "sid-old", "cwd": CLONE},
                               paused=lambda: "owner said stop")
    check(any("PAUSE" in h for h in holds) and not any("idle" in h for h in holds),
          "C1 the kill-time recheck reads PAUSE again, never an owner idle clock (%s)" % holds)
    check("owner" not in inspect.signature(SR.recheck_at_kill).parameters, "C1 recheck_at_kill takes no owner reader")


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


# ---- v3 does MORE (owner 2026-10-28 ~21:50 PDT: "All three. We don't want to waste time waiting.")

def test_v1_foundry_grace_is_30_s():
    with open(os.path.join(HERE, "dispatcher_schedule.json"), encoding="utf-8") as f:
        live = json.load(f)
    check(SR.config(live).get("FOUNDRY", {}).get("grace_s") == 30,
          "V1 the live schedule gives FOUNDRY a 30 s restart grace (%s)" % SR.config(live).get("FOUNDRY", {}).get("grace_s"))


def _tx_file(name, recs):
    p = os.path.join(TMP, "v2_%s.jsonl" % name)
    with open(p, "w") as f:
        f.write("\n".join(json.dumps(r) for r in recs) + "\n")
    return p


def _u(ts, content, **kw):
    r = {"type": "user", "timestamp": ts, "message": {"role": "user", "content": content}}
    r.update(kw)
    return r


def test_v2_only_a_human_prompt_counts_as_new_input():
    """The dry request of 2026-10-29 was cancelled at 04:27:29Z by the Dispatcher's own ring (a Stop-hook
    task-notification). Machine and peer-seat input must never cancel a restart; a human prompt must."""
    end = {"type": "assistant", "timestamp": "2026-10-29T04:20:05Z", "message": {"stop_reason": "end_turn"}}
    human = _u("2026-10-29T04:20:00Z", "do the thing", origin={"kind": "human"}, promptSource="typed")
    machine = [
        _u("2026-10-29T04:27:29Z", "<task-notification>\n<summary>Stop hook feedback</summary>\n</task-notification>\n"
           "<system-reminder>\nStop hook blocking error from command \"Stop\": [RimFlow Dispatcher \u2014 a program, not "
           "a person; ring FOUNDRY-1-1]\n</system-reminder>",
           origin={"kind": "task-notification", "producer": "session-task"}, promptSource="system",
           turnOrigin="task_notification"),
        _u("2026-10-29T04:28:00Z", "<task-notification> <task-id>a1</task-id> done", origin={"kind": "task-notification"},
           promptSource="system", turnOrigin="task_notification"),
        _u("2026-10-29T04:28:10Z", 'Another Claude session sent a message: <cross-session-message from-name="CONDUCTOR" '
           'from-mode="bypass">\ngo\n</cross-session-message>', origin={"kind": "peer", "name": "CONDUCTOR"},
           promptSource="system", turnOrigin="peer"),
        _u("2026-10-29T04:28:20Z", 'Another Claude session sent a message: <cross-session-message '
           'from-name="AGENT BENCH \u25b6 ITEM_X" from-mode="bypass">\ngo\n</cross-session-message>',
           origin={"kind": "peer"}, promptSource="system", turnOrigin="peer"),
        _u("2026-10-29T04:28:30Z", "[RimFlow Dispatcher \u2014 a program, not a person; ring FOUNDRY-2-1]\nSeat FOUNDRY"),
        _u("2026-10-29T04:28:40Z", "[RimFlow seat restart] You are a FRESH FOUNDRY window"),
        _u("2026-10-29T04:28:50Z", "[Cross-session idle notice] \"bench-66\" is idle now", promptSource="system",
           turnOrigin="system"),
        _u("2026-10-29T04:29:00Z", "probe", promptSource="sdk", turnOrigin="sdk"),
        _u("2026-10-29T04:29:05Z", "scheduled probe", promptSource="system", turnOrigin="scheduled"),
    ]
    names = ["CONDUCTOR", "AGENT BENCH", "AGENT FOUNDRY"]
    s = SR.tx_summary(_tx_file("machine", [human, end] + machine + [end]), peers=names)
    check(s["last_user_at"] == D.S.parse_ts("2026-10-29T04:20:00Z"),
          "V2 rings, task notifications, seat peers (CONDUCTOR / AGENT BENCH), [RimFlow] prompts, sdk and scheduled "
          "input are not new input (last_user_at %s)" % SR._iso(s["last_user_at"] or 0))
    for i, h in enumerate([
            _u("2026-10-29T04:30:00Z", "stop that", origin={"kind": "human"}, promptSource="typed"),
            _u("2026-10-29T04:30:00Z", "queued words", origin={"kind": "human"}, promptSource="queued"),
            _u("2026-10-29T04:30:00Z", "legacy prompt with no origin"),
            _u("2026-10-29T04:30:00Z", 'Another Claude session sent a message: <cross-session-message from-name="OWNER" '
               'from-mode="bypass">\nGame is up\n</cross-session-message>', origin={"kind": "peer", "name": "OWNER"},
               promptSource="system", turnOrigin="peer")]):
        s = SR.tx_summary(_tx_file("human%d" % i, [human, end] + machine + [h, end]), peers=names)
        check(s["last_user_at"] == D.S.parse_ts("2026-10-29T04:30:00Z"),
              "V2 a human prompt still counts as new input (%d: %s)" % (i, h["message"]["content"][:30]))
    dflt = SR.peer_names()
    check("CONDUCTOR" in dflt and "AGENT BENCH" in dflt,
          "V2 the default peer names come from the schedule and include the Conductor's (%s)" % dflt)
    s = SR.tx_summary(_tx_file("dflt", [human, end] + machine + [end]))
    check(s["last_user_at"] == D.S.parse_ts("2026-10-29T04:20:00Z"),
          "V2 tx_summary with no peers argument still ignores the Conductor")


def test_v2_no_ring_while_a_restart_is_pending():
    """A ring into a window whose restart is pending would start a new ticket in it (then busy -> failed). Rings wait
    while the restart is pending, but only for a bounded time, so a held restart cannot starve the seat."""
    sch = sched()
    st = fresh()
    st["seat_restart"] = {"FOUNDRY": {"state": "pending", "ts": T0, "session_id": "sid-old"}}
    why = SR.ring_hold(st, "FOUNDRY", sch, T0 + 20)
    check(bool(why), "V2 a fresh pending restart holds the Dispatcher's ring (%s)" % why)
    check(not SR.ring_hold(st, "FOUNDRY", sch, T0 + 10_000), "V2 a long-held pending restart no longer holds rings")
    st["seat_restart"]["FOUNDRY"]["state"] = "cancelled"
    check(not SR.ring_hold(st, "FOUNDRY", sch, T0 + 20), "V2 no restart pending -> rings as usual")
    st = fresh()
    st["seat_restart"] = {"FOUNDRY": {"state": "pending", "ts": T0, "session_id": "sid-old"}}
    st["seats"]["FOUNDRY"] = {"session_id": "sid-old", "idle_since": T0 - 10_000}
    o = obs()
    o.update({"peek": lambda seat: {"id": "SOME_ITEM", "needs": "offline"}, "events": lambda seat, since: [], "consumed": lambda seat, rid: None,
              "alive": lambda pid: True, "armed": lambda seat: {"session_id": "sid-old", "pid": 4242}})
    acts = D.decide(sch, st, o, T0 + 20, True)
    check("ring" not in dos(acts), "V2 the Dispatcher does not ring a seat whose restart is pending (%s)" % dos(acts))
    st["seat_restart"]["FOUNDRY"]["state"] = "cancelled"
    acts = D.decide(sch, st, o, T0 + 20, True)
    check("ring" in dos(acts), "V2 control: the same idle seat with no restart pending IS rung (%s)" % dos(acts))


def _request(sch, ctx, extra=(), seat="FOUNDRY", name="AGENT FOUNDRY"):
    """cmd_request on a simulated window whose transcript says ctx tokens -> (exit, printed, request written?)."""
    import contextlib
    import io
    saved = {k: getattr(SR, k) for k in ("unpublished_shard", "_schedule", "session_file", "helpers_of", "reg_start",
                                         "proc_start", "tx_summary", "last_human")}
    try:
        # his last message is the goodbye, ending at byte 100 of a 200-byte transcript (a Conductor request binds it)
        SR.last_human = lambda path, peers=None: (T0 - 5, {"message": {"content": "goodbye"}}, 100, 200)
        SR.unpublished_shard = lambda seat, clone: None
        SR._schedule = lambda: sch
        SR.session_file = lambda pid: {"pid": pid, "sessionId": "sid-old", "name": name, "cwd": CLONE,
                                       "procStart": "77"}
        SR.helpers_of = lambda path, now=None: []
        SR.reg_start = lambda sf: 77
        SR.proc_start = lambda pid: 77
        SR.tx_summary = lambda path, *a, **k: {"last_kind": "assistant_tool", "last_at": T0, "last_user_at": T0 - 5,
                                               "ctx_tokens": ctx}
        rp = SR.request_path(seat)
        if os.path.exists(rp):
            os.remove(rp)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = SR.main(["request", "--seat", seat, "--ticket", "T_DONE", "--pid", "4242", "--note", "landed x"]
                         + list(extra))
        return rc, out.getvalue(), os.path.exists(rp)
    finally:
        for k, v in saved.items():
            setattr(SR, k, v)


def test_v3_close_out_continues_while_context_is_ok():
    """FOUNDRY_IDLE_DIAGNOSE_CAP_STARVES_TRIAGE: one ring per sub-minute ticket spent the wake cap. Under the backstop
    the close-out writes NO request and tells the seat to pull its next ticket itself; over it, it asks for a fresh
    window."""
    raw = {"seats": {"FOUNDRY": {"session_name": "AGENT FOUNDRY", "clone": CLONE}},
           "seat_restart": {"enabled": True, "seats": {"FOUNDRY": {"backstop_ctx_tokens": 110_000}}}}
    rc, out, wrote = _request(raw, 60_000)
    check(rc == 0 and not wrote and "next --seat FOUNDRY" in out and "CONTEXT OK" in out,
          "V3 context 60k < 110k: no request written, the seat is told to run next (rc %s, wrote %s, %r)"
          % (rc, wrote, out[-200:]))
    rc, out, wrote = _request(raw, 120_000)
    check(rc == 0 and wrote and "RESTART REQUESTED" in out,
          "V3 context 120k >= 110k: the fresh-window request is written (rc %s, wrote %s)" % (rc, wrote))
    rc, out, wrote = _request(raw, None)
    check(rc == 0 and wrote, "V3 context UNMEASURED: ask for the fresh window (never continue blind) (wrote %s)" % wrote)
    rc, out, wrote = _request(raw, 60_000, ["--fresh"])
    check(rc == 0 and wrote, "V3 --fresh asks for the fresh window whatever the context (wrote %s)" % wrote)
    raw["seat_restart"]["seats"]["FOUNDRY"]["grace_s"] = 30
    rc, out, wrote = _request(raw, 120_000)
    check("30 s grace" in out, "V3 the request names the seat's configured grace, not the default (%r)" % out[-160:])
    with open(SR.seat_log_path("FOUNDRY"), encoding="utf-8") as f:
        log = f.read()
    check(log.count("landed x") >= 5, "V3 the note reaches the seat log whether or not a restart is requested")
    fmd = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), "infrastructure", "agents", "FOUNDRY.md")
    with open(fmd, encoding="utf-8") as f:
        doc = f.read()
    check("CONTEXT OK" in doc and "next --seat FOUNDRY" in doc and "--ringed" not in doc and "110000" in doc.replace(",", "").replace(" ", ""),
          "V3 FOUNDRY.md's close-out tells the seat to continue on CONTEXT OK and names the 110000 backstop")


# ---- Codex review 2026-10-29 (rev/out.txt P1 1 + 2)

def _ev(event, tid, ts, **kw):
    e = {"seat": "FOUNDRY", "event": event, "id": tid, "ts": ts}
    e.update(kw)
    return e


def test_w1_new_work_after_the_request_voids_it():
    """SEAT_RESTART_FIX_KILL_AFTER_NEW_WORK: a seat that took new work after its restart request (a ring, `next`, a
    peer-assigned ticket) and then idles at a turn boundary must not be killed by the stale request."""
    sch = sched()
    later = SR._iso(T0 + 10)
    for name, ev in [("lease take", _ev("lease", "NEW_TICKET_1", later, action="take")),
                     ("claim", _ev("claim", "NEW_TICKET_1", later)),
                     ("start", _ev("start", "NEW_TICKET_1", later)),
                     ("lease renew of another ticket", _ev("lease", "NEW_TICKET_1", later, action="renew"))]:
        st = fresh()
        run(sch, st, obs(request=req()), T0 + 1)
        a = run(sch, st, obs(work=[ev]), T0 + SR.DEFAULTS["grace_s"] + 5)
        check(state(st) == "cancelled" and "restart_kill" not in dos(a) and "restart_cancel" in dos(a),
              "W1 %s after the request -> void, never killed (%s %s)" % (name, state(st), dos(a)))
    st = fresh()
    run(sch, st, obs(request=req()), T0 + 1)
    a = run(sch, st, obs(work=[_ev("lease", "SOME_TICKET_DONE", later, action="release"),
                               _ev("close", "SOME_TICKET_DONE", later),
                               _ev("lease", "SOME_TICKET_DONE", later, action="renew")]),
            T0 + SR.DEFAULTS["grace_s"] + 5)
    check("restart_kill" in dos(a), "W1 control: the request's own ticket closing/releasing is not new work (%s)" % dos(a))
    st = fresh()
    run(sch, st, obs(request=req()), T0 + 1)
    a = run(sch, st, obs(work=None), T0 + SR.DEFAULTS["grace_s"] + 5)
    check(state(st) == "pending" and "restart_kill" not in dos(a),
          "W1 the seat's shard unreadable (UNMEASURED) holds, never kills (%s %s)" % (state(st), dos(a)))
    # machine rings alone still do not cancel (0cf054ade8): a ring transcript record with no new ledger work
    st = fresh()
    run(sch, st, obs(request=req()), T0 + 1)
    a = run(sch, st, obs(work=[]), T0 + SR.DEFAULTS["grace_s"] + 5)
    check("restart_kill" in dos(a), "W1 control: no new work and no human input -> the restart proceeds (%s)" % dos(a))
    # the reader: a real shard, events at or after the request's second, other seats ignored
    clone = os.path.join(TMP, "w1clone")
    shard = os.path.join(clone, "infrastructure", "state", "ledger", "events")
    os.makedirs(shard, exist_ok=True)
    with open(os.path.join(shard, "FOUNDRY.jsonl"), "w") as f:
        for e in [_ev("lease", "OLD", SR._iso(T0 - 5), action="take"), dict(_ev("claim", "X", later), seat="BENCH"),
                  _ev("lease", "NEW_TICKET_1", later, action="take")]:
            f.write(json.dumps(e) + "\n")
        f.write("{not json\n")
    got = SR.work_since(clone, "FOUNDRY", T0 + 0.5)
    check([e["id"] for e in got or []] == ["NEW_TICKET_1"],
          "W1 work_since reads the seat's own shard from the request's second on (%s)" % got)
    check(SR.work_since(os.path.join(TMP, "w1none"), "FOUNDRY", T0) == [], "W1 no shard yet -> no work (empty)")
    # the kill-time re-check reads it again
    holds = SR.recheck_at_kill("FOUNDRY", sch, {"ts": T0, "ticket": "SOME_TICKET_DONE", "session_id": "sid-old"},
                               {"pid": 1, "sessionId": "sid-old", "cwd": CLONE},
                               paused=lambda: None,
                               work=lambda seat, ts: [_ev("lease", "NEW_TICKET_1", later, action="take")])
    check(any("new work" in h for h in holds), "W1 the kill-time re-check holds on new work (%s)" % holds)
    holds = SR.recheck_at_kill("FOUNDRY", sch, {"ts": T0, "ticket": "SOME_TICKET_DONE", "session_id": "sid-old"},
                               {"pid": 1, "sessionId": "sid-old", "cwd": CLONE},
                               paused=lambda: None,
                               work=lambda seat, ts: None)
    check(any("UNMEASURED" in h for h in holds), "W1 the kill-time re-check holds on an unreadable shard (%s)" % holds)


def test_w2_human_origin_beats_text_markers():
    """SEAT_RESTART_FIX_HUMAN_INPUT_MARKERS: the record's structural origin decides; text markers are only the fallback
    for a record that carries none. MEASURED 2026-10-29 over every bench/foundry transcript: no origin.kind human
    record carries a machine marker, every ring is a task-notification or an sdk prompt."""
    names = ["CONDUCTOR", "AGENT BENCH", "AGENT FOUNDRY"]
    for i, h in enumerate([
            _u("2026-10-29T04:30:00Z", "Explain \u201ca program, not a person\u201d", origin={"kind": "human"},
               promptSource="typed", turnOrigin="human"),
            _u("2026-10-29T04:30:00Z", "[RimFlow Dispatcher \u2014 a program, not a person; ring X] why did this fire?",
               origin={"kind": "human"}, promptSource="queued", turnOrigin="human"),
            _u("2026-10-29T04:30:00Z", "<task-notification> pasted by me", turnOrigin="human"),
            _u("2026-10-29T04:30:00Z", "[RimFlow pasted", promptSource="typed")]):
        check(SR._is_human_input(h, names), "W2 a human-origin prompt quoting a machine marker is human (%d)" % i)
    for i, m in enumerate([
            _u("2026-10-29T04:30:00Z", "[RimFlow Dispatcher \u2014 a program, not a person; ring X]"),
            _u("2026-10-29T04:30:00Z", "<task-notification> x", origin={"kind": "task-notification"},
               turnOrigin="human"),
            _u("2026-10-29T04:30:00Z", "plain words", origin={"kind": "human"}, promptSource="sdk")]):
        check(not SR._is_human_input(m, names),
              "W2 no structural origin -> text markers decide; a machine field anywhere wins (%d)" % i)


# ---- CONDUCTOR_GOODBYE_DESIGN_FRESH_EACH_TIME: the Conductor (seat BENCH) restarts after his goodbye. BENCH has no
# doorbell (its Stop hook is FOUNDRY-only), so it verifies by the new window ending its first turn, and its relaunch
# prompt is the Conductor's wake, not the doorbell ritual.

BCLONE = os.path.join(TMP, "bench")
BLOG = os.path.join(TMP, "conductor", "log.md")


def bsched(**seat_kw):
    seat = {"kind": "conductor", "grace_s": 120, "seat_log": BLOG, "backstop": True,
            "backstop_ctx_tokens": 120_000, "backstop_idle_s": 3600, "backstop_human_idle_s": 14_400}
    seat.update(seat_kw)
    s = {"seats": {"BENCH": {"enabled": True, "wake": False, "recover_dead": False, "session_name": "CONDUCTOR",
                             "session_aliases": ["AGENT BENCH"], "clone": BCLONE, "model": "opus"}},
         "seat_restart": {"enabled": True, "seats": {"BENCH": seat}},
         "ledger_notes": False, "publish": False}
    p = os.path.join(TMP, "bsched.json")
    with open(p, "w") as f:
        json.dump(s, f)
    return D.load_schedule(p)


def bsess(sid="sid-old", status="idle", pid=4242, name="CONDUCTOR"):
    return dict(sess(sid, status, pid, name), cwd=BCLONE)


def breq(ts=T0, sid="sid-old"):
    return dict(req(ts, sid), seat="BENCH", ticket="GOODBYE", reason="goodbye", tx_offset=0)


def bstate(st):
    return (st.get("seat_restart") or {}).get("BENCH", {}).get("state")


def test_g1_bench_relaunch_argv_is_the_conductor_wake():
    cfg = SR.config(bsched())["BENCH"]
    argv = SR.relaunch_argv("BENCH", cfg, "goodbye")
    check(argv[argv.index("--name") + 1] == "CONDUCTOR" and argv[argv.index("--remote-control") + 1] == "CONDUCTOR"
          and argv[argv.index("--model") + 1] == "opus",
          "G1 BENCH relaunch: --name/--remote-control CONDUCTOR, --model opus (%s)" % argv[:-1])
    import install_wt_seat_profiles as W
    launch = W.LAUNCH.format(script=W.BOUNDED.format(home=BCLONE), label="CONDUCTOR", model="opus")
    launch = [x.strip("'") for x in launch.split()]
    check(argv[:-1] == launch, "G1 BENCH relaunch argv is the WT profile's own LAUNCH line (%s vs %s)" % (argv[:-1], launch))
    p = argv[-1]
    check("Conductor" in p and "wake --seat BENCH" in p and "CONDUCTOR.md" in p and "doorbell" not in p,
          "G1 the BENCH first prompt is the Conductor wake, not the doorbell ritual (%r)" % p)
    f = SR.relaunch_argv("FOUNDRY", SR.config(sched())["FOUNDRY"])[-1]
    check("doorbell" in f and "Conductor" not in f, "G1 control: FOUNDRY keeps its doorbell prompt (%r)" % f[:80])


def test_g2_bench_restart_holds_on_helpers_input_owner_and_reply():
    sch = bsched()
    late = T0 + 605                      # past goodbye_quiet_s (600 s; review 2 P0-1), not just the 120 s grace
    st = fresh()
    a = run(sch, st, obs(sessions=[bsess(name="CONDUCTOR ▶ SOME_ITEM")], request=breq()), T0 + 1)
    check(bstate(st) == "pending" and "restart_kill" not in dos(a), "G2 a goodbye request is pending through the grace")
    a = run(sch, st, obs(sessions=[bsess()]), T0 + 60)
    check(bstate(st) == "pending" and "restart_kill" not in dos(a), "G2 inside the 120 s grace: no kill (%s)" % dos(a))
    a = run(sch, st, obs(sessions=[bsess()], helpers=[{"id": "agent-h1", "alive": True, "last_at": late}]), late)
    check(bstate(st) == "pending" and "restart_kill" not in dos(a)
          and any("helper" in (x.get("why") or "") for x in a), "G2 a live helper of the Conductor holds the kill (%s)" % a[-1:])
    a = run(sch, st, obs(sessions=[bsess()], helpers=None), late)
    check(bstate(st) == "pending" and "restart_kill" not in dos(a), "G2 helper inventory UNMEASURED holds the kill")
    a = run(sch, st, obs(sessions=[bsess(status="busy")], tx={"last_kind": "assistant_tool", "last_at": late - 1}), late)
    check(bstate(st) == "pending" and "restart_kill" not in dos(a), "G2 the window mid-reply is never killed (%s)" % dos(a))
    a = run(sch, st, obs(sessions=[bsess()], tx={"last_user_at": T0 + 90, "last_kind": "assistant_end",
                                                  "last_at": T0 + 95}), late)
    check(bstate(st) == "cancelled" and "restart_kill" not in dos(a),
          "G2 he wrote again during the grace -> cancelled, never killed (%s)" % dos(a))
    st = fresh()
    run(sch, st, obs(sessions=[bsess()], request=breq()), T0 + 1)
    a = run(sch, st, obs(sessions=[bsess()]), late)
    k = [x for x in a if x["do"] == "restart_kill"]
    check(len(k) == 1 and k[0]["session_names"] == ["CONDUCTOR", "AGENT BENCH"] and "Conductor" in k[0]["argv"][-1],
          "G2 control: grace over, nothing held, quiet -> one kill carrying the Conductor relaunch (%s)" % dos(a))
    st = fresh()
    run(sch, st, obs(sessions=[bsess(), bsess(sid="sid-2", pid=9, name="AGENT BENCH")], request=breq()), T0 + 1)
    check(bstate(st) == "cancelled", "G2 two windows answer to the Conductor's names -> cancelled, never a guess")


def test_g3_bench_verifies_by_the_first_turn_not_the_doorbell():
    sch = bsched()

    def kst():
        st = fresh()
        st["seat_restart"] = {"BENCH": {"state": "killed", "session_id": "sid-old", "pid": 4242, "killed_at": T0 + 200,
                                        "ts": T0, "source": "request", "ticket": "GOODBYE"}}
        return st
    st = kst()
    new = [bsess(sid="sid-new", pid=5555)]
    run(sch, st, obs(sessions=new, intile={"at": T0 + 205}), T0 + 230)
    check(bstate(st) == "relaunched", "G3 a new CONDUCTOR window -> relaunched")
    a = run(sch, st, obs(sessions=new, tx={"last_kind": "assistant_tool", "last_at": T0 + 240}), T0 + 250)
    check(bstate(st) == "relaunched", "G3 the fresh window still in its first turn -> not yet verified")
    a = run(sch, st, obs(sessions=new, tx={"last_kind": "assistant_end", "last_at": T0 + 100}), T0 + 260)
    check(bstate(st) == "relaunched", "G3 a turn end OLDER than the relaunch is not the new window's (stale read)")
    a = run(sch, st, obs(sessions=new, tx={"last_kind": "assistant_end", "last_at": T0 + 290}), T0 + 300)
    check(bstate(st) == "verified" and "restart_verified" in dos(a),
          "G3 the fresh Conductor ended its first turn -> verified with no doorbell (%s)" % dos(a))
    st = kst()
    run(sch, st, obs(sessions=new), T0 + 230)
    a = run(sch, st, obs(sessions=new, tx={"last_kind": "assistant_tool", "last_at": T0 + 240}),
            T0 + 230 + SR.DEFAULTS["arm_s"] + 1)
    check(bstate(st) == "failed" and any(x["do"] == "alarm" for x in a), "G3 never ended a turn in arm_s -> failed + alarm")
    st = killed_state(fresh())
    run(sched(), st, obs(sessions=[sess(sid="sid-new", pid=5555)]), T0 + 230)
    run(sched(), st, obs(sessions=[sess(sid="sid-new", pid=5555)], tx={"last_kind": "assistant_end", "last_at": T0 + 290}),
        T0 + 300)
    check(state(st) == "relaunched", "G3 mutation control: a doorbell seat (FOUNDRY) is NOT verified by a turn end")


def test_g4_bench_backstop_only_after_long_human_idle():
    sch = bsched()
    over = {"ctx_tokens": 150_000, "last_kind": "assistant_end", "last_at": T0 - 4000}
    for lu, why in ((T0 - 600, "he wrote 10 min ago"), (None, "no human message readable (fails closed)"),
                    (T0 - 14_000, "he wrote 3.9 h ago")):
        st = fresh()
        run(sch, st, obs(sessions=[bsess()], tx=dict(over, last_user_at=lu)), T0)
        check(bstate(st) is None, "G4 BENCH backstop does not fire: %s" % why)
    st = fresh()
    run(sch, st, obs(sessions=[bsess()], tx=dict(over, last_user_at=T0 - 15_000)), T0)
    check(bstate(st) == "pending" and st["seat_restart"]["BENCH"]["source"] == "backstop",
          "G4 control: context over, idle 1 h, no human message for 4 h+ -> backstop pending")
    st = fresh()
    run(sched(), st, obs(tx={"ctx_tokens": 130_000, "last_at": T0 - 2000, "last_user_at": None}), T0)
    check(state(st) == "pending", "G4 FOUNDRY (no backstop_human_idle_s) is unchanged by the human-idle gate")


def test_g5_live_schedule_has_the_conductor_entry():
    with open(os.path.join(HERE, "dispatcher_schedule.json"), encoding="utf-8") as f:
        live = json.load(f)
    raw = ((live.get("seat_restart") or {}).get("seats") or {}).get("BENCH") or {}
    # BENCH is OFF in the live schedule (blind review 3, test_k1); the entry stays complete for his choice, so judge it
    # as it would run if switched back on
    on = json.loads(json.dumps(live))
    on["seat_restart"]["seats"]["BENCH"]["enabled"] = True
    c = SR.config(on).get("BENCH") or {}
    check(c.get("kind") == "conductor" and c.get("session_name") == "CONDUCTOR" and c.get("model") == "opus"
          and c.get("clone") == "/home/mandrake/rm/bench", "G5 the live schedule restarts BENCH as the Conductor (%s)"
          % {k: c.get(k) for k in ("kind", "session_name", "model", "clone")})
    check((c.get("grace_s") or 0) >= 120, "G5 BENCH grace is at least 120 s (%s)" % c.get("grace_s"))
    check(c.get("backstop") is not True or ((c.get("backstop_human_idle_s") or 0) >= 7200
                                            and (c.get("backstop_idle_s") or 0) >= 1800),
          "G5 a BENCH backstop waits >= 2 h without a human message and >= 30 min idle (%s / %s)"
          % (c.get("backstop_human_idle_s"), c.get("backstop_idle_s")))
    nh = (live.get("no_handoff") or {}).get("conductor_log") or D.no_handoff_rule(live).get("conductor_log")
    check(c.get("seat_log") == nh, "G5 the close-out note goes to the Conductor log (%s vs %s)" % (c.get("seat_log"), nh))
    ph = raw.get("goodbye_phrases") or []
    need = {"goodbye", "bye", "gn", "good night", "done for now", "thats all"}
    check(need <= set(ph), "G5 goodbye_phrases carry the ruled list (missing %s)" % sorted(need - set(ph)))
    check(all(raw.get(k) for k in ("_why", "_why_backstop")), "G5 the BENCH entry explains itself (_why, _why_backstop)")
    check((SR.config(live).get("FOUNDRY") or {}).get("kind", "doorbell") == "doorbell", "G5 FOUNDRY stays a doorbell seat")


def test_g6_wake_lists_his_messages_after_the_goodbye():
    import contextlib
    import io
    home = os.path.join(TMP, "claude_home")
    os.environ["CLAUDE_CONFIG_DIR"] = home
    sch = bsched()
    saved = SR._schedule
    try:
        SR._schedule = lambda: sch
        tx = SR.transcript_path(BCLONE, "sid-bye")
        os.makedirs(os.path.dirname(tx), exist_ok=True)
        with open(tx, "w") as f:
            first = json.dumps(_u("1970-01-12T13:45:00Z", "goodbye", origin={"kind": "human"}, promptSource="typed"))
            f.write(first + "\n")
            for r in (
                      _u("1970-01-12T13:47:00Z", "oh and park the hose test", origin={"kind": "human"},
                         promptSource="typed"),
                      _u("1970-01-12T13:47:30Z", "[RimFlow Dispatcher - a program, not a person; ring]",
                         origin={"kind": "task-notification"}, promptSource="system")):
                f.write(json.dumps(r) + "\n")
        os.makedirs(os.path.dirname(BLOG), exist_ok=True)
        with open(BLOG, "w") as f:
            f.write("## earlier\nconductor note ABC\n")
        SR.write_killed("BENCH", {"seat": "BENCH", "session_id": "sid-bye", "killed_at": T0 + 300,
                                  "req_ts": SR._ts("1970-01-12T13:46:00Z"), "ticket": "GOODBYE", "gen": "g6",
                                  "tx_path": tx, "tx_offset": len(first) + 1})
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = SR.main(["wake", "--seat", "BENCH", "--gen", "g6"])
        o = out.getvalue()
    finally:
        SR._schedule = saved
        os.environ.pop("CLAUDE_CONFIG_DIR", None)
    check(rc == 0 and "conductor note ABC" in o, "G6 wake prints the Conductor log tail (%r)" % o[:120])
    check("park the hose test" in o and "goodbye\n" not in o.split("after the close-out")[-1] and "a program" not in o,
          "G6 wake lists his messages to the old window after the request, and only his (%r)" % o[-400:])
    check("doorbell" not in o, "G6 the Conductor wake does not tell it to wait for a doorbell")


def test_g7_killed_record_carries_the_request_time():
    sch = bsched()
    calls = []
    fx = {"session_file": lambda pid: {"pid": pid, "sessionId": "sid-old", "name": "CONDUCTOR", "status": "idle"},
          "kill": lambda pid, start=None: "SIGTERM", "write_killed": lambda seat, rec: calls.append(rec),
          "recheck": lambda *a: [], "start": lambda pid: 77, "final": lambda *a: []}
    st = fresh()
    run(sch, st, obs(sessions=[bsess()], request=breq()), T0 + 1)
    a = [x for x in run(sch, st, obs(sessions=[bsess()]), T0 + 605) if x["do"] == "restart_kill"][0]
    SR.execute(a, sch, st, True, T0 + 610, fx)
    check(calls and calls[0].get("req_ts") == T0, "G7 the killed record carries the request time (%s)" % calls[:1])


def test_g8_bench_request_logs_to_the_conductor_log():
    raw = bsched()
    rc, out, wrote = _request(raw, 30_000, ["--fresh"], seat="BENCH", name="CONDUCTOR")
    check(rc == 0 and wrote and "RESTART REQUESTED" in out, "G8 a goodbye request (--fresh) is written at any context")
    with open(BLOG, encoding="utf-8") as f:
        log = f.read()
    check("landed x" in log, "G8 the close-out note lands in the Conductor log, not seat_log/BENCH.md")


def test_g9_wt_bench_keeps_the_conductor_wake_under_seat_loop():
    import install_wt_seat_profiles as W
    real = W.restart_seats
    try:
        W.restart_seats = lambda path=None: {"BENCH", "FOUNDRY"}
        b = W.build("BENCH")[0]["commandline"]
        f = W.build("FOUNDRY")[0]["commandline"]
    finally:
        W.restart_seats = real
    check("seat_loop.sh BENCH " in b and "Fresh CONDUCTOR window" in b and "doorbell" not in b,
          "G9 WT: BENCH under seat_loop keeps its Conductor wake prompt (%s)" % b[-200:])
    check("seat_loop.sh FOUNDRY " in f and "doorbell" in f, "G9 WT control: FOUNDRY keeps the doorbell first launch")


# ---------------------------------------------------------------------------------------------------------------------
# Blind review round 1 (v3_review/blind/goodbye/review.md): each test fails on the code before the fix.

H_HOME = os.path.join(TMP, "claude_home_h")


def _hu(iso, text, **kw):
    return _u(iso, text, origin={"kind": "human"}, promptSource="typed", **kw)


def _ha(iso, stop="end_turn", pad=0):
    return {"type": "assistant", "timestamp": iso,
            "message": {"role": "assistant", "stop_reason": stop, "content": [{"type": "text", "text": "x" * pad}],
                        "usage": {"input_tokens": 10}}}


def _bt(sid, recs):
    """A BENCH transcript at the path transcript_for() resolves (CLAUDE_CONFIG_DIR = H_HOME) -> (path, line ends)."""
    os.environ["CLAUDE_CONFIG_DIR"] = H_HOME
    p = SR.transcript_path(BCLONE, sid)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    ends, n = [], 0
    with open(p, "w", encoding="utf-8") as f:
        for r in recs:
            line = json.dumps(r) + "\n"
            f.write(line)
            n += len(line.encode("utf-8"))
            ends.append(n)
    return p, ends


GB = "1970-01-12T13:45:00Z"           # the goodbye (T0 is 1970-01-12T13:46:40Z)
GB_T = SR._ts(GB)


def _brequest(recs, extra=("--fresh",), unpub=None):
    """cmd_request in the BENCH window over a REAL transcript file (only identity and git are faked)."""
    import contextlib
    import io
    _bt("sid-old", recs)
    sch = bsched()
    saved = {k: getattr(SR, k) for k in ("unpublished_shard", "_schedule", "session_file", "helpers_of", "reg_start",
                                         "proc_start")}
    try:
        SR.unpublished_shard = lambda seat, clone: unpub
        SR._schedule = lambda: sch
        SR.session_file = lambda pid: {"pid": pid, "sessionId": "sid-old", "name": "CONDUCTOR", "cwd": BCLONE,
                                       "procStart": "77"}
        SR.helpers_of = lambda path, now=None: []
        SR.reg_start = lambda sf: 77
        SR.proc_start = lambda pid: 77
        rp = SR.request_path("BENCH")
        if os.path.exists(rp):
            os.remove(rp)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = SR.main(["request", "--seat", "BENCH", "--ticket", "GOODBYE", "--reason", "goodbye", "--pid", "4242",
                          "--note", "n"] + list(extra))
        return rc, out.getvalue(), SR._read_json(rp)
    finally:
        for k, v in saved.items():
            setattr(SR, k, v)


def test_h1_cancel_window_starts_at_the_goodbye_not_the_request():
    # P0-1: he wrote again during the close-out, before the request -> refused (answer him first)
    rc, out, rq = _brequest([_hu(GB, "Good night!"), _ha("1970-01-12T13:45:10Z", "tool_use"),
                             _hu("1970-01-12T13:45:30Z", "wait, continue with the hose"),
                             _ha("1970-01-12T13:46:00Z", "tool_use")])
    check(rc == 3 and rq is None and "REFUSED" in out, "H1 a message after the goodbye, before the request: REFUSED (%s)"
          % out.strip()[-160:])
    rc, out, rq = _brequest([_hu(GB, "Good night!"), _ha("1970-01-12T13:45:10Z", "tool_use")])
    p, ends = _bt("sid-old", [_hu(GB, "Good night!"), _ha("1970-01-12T13:45:10Z", "tool_use")])
    check(rc == 0 and rq and rq.get("input_ts") == GB_T and rq.get("tx_offset") == ends[0],
          "H1 the request binds the goodbye: input_ts %s, cursor %s (want %s, %s)" % (
              (rq or {}).get("input_ts"), (rq or {}).get("tx_offset"), GB_T, ends[0]))
    # a human message between the goodbye and the request time cancels the pending restart
    sch, st = bsched(), fresh()
    r = dict(breq(), input_ts=GB_T, tx_offset=ends[0])
    run(sch, st, obs(sessions=[bsess()], request=r, tx={"last_user_at": GB_T + 20}), T0 + 1)
    check(bstate(st) == "cancelled", "H1 input after the goodbye but before the request ts cancels (%s)" % bstate(st))


def test_h2_cancel_evidence_survives_a_long_tail():
    # P0-2: his "stop" followed by > 4 MiB of output must still cancel; tx_summary's tail cannot see it
    big = [_ha("1970-01-12T13:45:%02dZ" % (20 + i), "tool_use", pad=600_000) for i in range(8)]
    p, ends = _bt("sid-old", [_hu(GB, "goodbye"), _hu("1970-01-12T13:45:15Z", "no wait, keep going")] + big
                  + [_ha("1970-01-12T13:46:00Z")])
    tail = SR.tx_summary(p)
    check(tail and tail.get("last_user_at") is None, "H2 control: the 4 MiB tail cannot see his message (%s)" % (
        (tail or {}).get("last_user_at")))
    hs = SR.human_since_offset(p, ends[0])
    check(hs and "keep going" in SR._text(hs[0]), "H2 the cursor scan from the goodbye finds it (%s)" % (hs and len(hs)))
    check(SR.human_since_offset(p, ends[-1] + 10) is None, "H2 a cursor past EOF (truncated) is UNMEASURED")
    sch, st = bsched(), fresh()
    r = dict(breq(), input_ts=GB_T, tx_offset=ends[0])
    o = obs(sessions=[bsess()], request=r, tx={"last_user_at": None})
    o["seat_restart"]["cursor"] = lambda seat, s, rs: SR.cursor_scan(p, rs.get("tx_offset"))
    run(sch, st, o, T0 + 1)
    check(bstate(st) == "cancelled", "H2 decide() cancels on the cursor scan (%s)" % bstate(st))
    sch, st = bsched(), fresh()
    o = obs(sessions=[bsess()], request=r, tx={"last_user_at": None})
    o["seat_restart"]["cursor"] = lambda seat, s, rs: None
    run(sch, st, o, T0 + 1)
    a = run(sch, st, o, T0 + 700)
    check(bstate(st) == "pending" and "restart_kill" not in dos(a), "H2 cursor UNMEASURED holds, never kills")
    sch, st = bsched(), fresh()
    o = obs(sessions=[bsess()], request=dict(breq(), tx_offset=None), tx={"last_user_at": None})
    run(sch, st, o, T0 + 1)
    a = run(sch, st, o, T0 + 700)
    check("restart_kill" not in dos(a), "H2 a Conductor request with no cursor never reaches the kill (%s)" % dos(a))
    rs = {"ts": T0, "cancel_after": GB_T, "tx_offset": ends[0], "source": "request"}
    holds = SR.recheck_at_kill("BENCH", sch, rs, bsess(),
                               paused=lambda: None, work=lambda s_, ts: [])
    check(any("keep going" in h or "new input" in h for h in holds), "H2 the kill-time re-check reads the cursor (%s)"
          % holds)


def test_h3_final_fence_after_the_killed_record():
    # P0-3 (narrowed): one more cursor read after the killed record is written, right before the signal
    sch = bsched()
    kills, recs = [], []
    fx = {"session_file": lambda pid: {"pid": pid, "sessionId": "sid-old", "name": "CONDUCTOR", "status": "idle"},
          "kill": lambda pid, start=None: kills.append(pid) or "SIGTERM", "write_killed": lambda seat, rec: recs.append(rec),
          "recheck": lambda *a: [], "start": lambda pid: 77, "final": lambda *a: ["new input at 13:47 (fence)"]}
    st = fresh()
    r = dict(breq(), input_ts=GB_T, tx_offset=0)
    o = obs(sessions=[bsess()], request=r)
    o["seat_restart"]["human_since"] = lambda *a: []
    run(sch, st, o, T0 + 1)
    a = [x for x in run(sch, st, o, T0 + 605) if x["do"] == "restart_kill"]
    res = SR.execute(a[0], sch, st, True, T0 + 610, fx) if a else "no kill action"
    check(not kills and recs and recs[-1].get("aborted") and bstate(st) == "pending",
          "H3 input seen at the final fence: no signal, killed record aborted, back to pending (%s)" % res)
    p, ends = _bt("sid-old", [_hu(GB, "goodbye"), _ha("1970-01-12T13:45:10Z"), _hu("1970-01-12T13:47:00Z", "one more")])
    f = SR.final_fence("BENCH", sch, {"cancel_after": GB_T, "tx_offset": ends[0]}, bsess())
    check(f and "new input" in f[0], "H3 the default fence reads the old transcript from the cursor (%s)" % f)
    check(SR.final_fence("BENCH", sch, {"cancel_after": GB_T}, bsess()), "H3 the fence holds a Conductor kill with no cursor")
    check(SR.final_fence("FOUNDRY", sched(), {"ts": T0}, sess()) == [], "H3 control: FOUNDRY without a cursor passes")


def test_h4_unmeasured_publication_refuses():
    # P1-4: git cannot say whether the shard is published -> REFUSED, no request
    rc, out, rq = _brequest([_hu(GB, "goodbye"), _ha("1970-01-12T13:45:10Z", "tool_use")],
                            unpub="UNMEASURED: git failed (timeout)")
    check(rc == 3 and rq is None and "REFUSED" in out, "H4 UNMEASURED publication refuses the request (%s)" % out.strip()[-120:])


def test_h5_wake_gives_every_message_whole():
    # P1-5: no 2000-char cut, non-text blocks named, nothing lost past an 8 MiB tail, coverage stated
    import contextlib
    import io
    long_msg = "start " + "y" * 3000 + " END_OF_LONG"
    big = [_ha("1970-01-12T13:47:%02dZ" % (10 + i), "tool_use", pad=1_200_000) for i in range(8)]
    img = _hu("1970-01-12T13:46:50Z", "", uuid="u-img")
    img["message"]["content"] = [{"type": "text", "text": "see pic"}, {"type": "image", "source": {"type": "base64"}}]
    p, ends = _bt("sid-bye2", [_hu(GB, "goodbye"), _hu("1970-01-12T13:46:45Z", long_msg), img] + big)
    sch = bsched()
    saved = SR._schedule
    try:
        SR._schedule = lambda: sch
        SR.write_killed("BENCH", {"seat": "BENCH", "session_id": "sid-bye2", "killed_at": T0 + 300, "req_ts": T0,
                                  "input_ts": GB_T, "tx_offset": ends[0], "ticket": "GOODBYE", "gen": "g5",
                                  "tx_path": p})
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            SR.main(["wake", "--seat", "BENCH", "--gen", "g5"])
        o = out.getvalue()
    finally:
        SR._schedule = saved
    check("END_OF_LONG" in o, "H5 a message past 2000 chars is printed whole")
    check("see pic" in o and "image" in o and "u-img" in o, "H5 an image block is named with its record uuid")
    check("from byte %d of %s" % (ends[0], p) in o, "H5 the wake states its coverage (%r)" % o[-200:])


def _queued(iso, text):
    """A message he typed while a turn ran: the transcript holds only this attachment (MEASURED: 440 of 444)."""
    return {"type": "attachment", "timestamp": iso, "uuid": "u-q-" + iso,
            "attachment": {"type": "queued_command", "prompt": text, "commandMode": "prompt",
                           "origin": {"kind": "human"}, "timestamp": iso}}


def test_h6_a_message_typed_mid_turn_cancels():
    # found while fixing P0-1: a "wait" typed DURING the close-out turn lands only as a queued_command attachment
    recs = [_hu(GB, "goodbye"), _ha("1970-01-12T13:45:10Z", "tool_use"),
            _queued("1970-01-12T13:45:20Z", "wait, one more thing"), _ha("1970-01-12T13:45:40Z")]
    p, ends = _bt("sid-old", recs)
    tx = SR.tx_summary(p)
    check(tx and tx.get("last_user_at") == SR._ts("1970-01-12T13:45:20Z") and tx.get("last_kind") == "assistant_end",
          "H6 tx_summary sees the queued prompt as his input, turn state unchanged (%s)" % tx)
    hs = SR.human_since_offset(p, ends[0])
    check(hs and "one more thing" in SR._text(hs[0]), "H6 the cursor scan sees it (%s)" % (hs and len(hs)))
    rc, out, rq = _brequest(recs)
    check(rc == 3 and rq is None, "H6 a goodbye request after a queued 'wait' is REFUSED (%s)" % out.strip()[-120:])
    m = [_queued("1970-01-12T13:45:20Z", "x")]
    m[0]["attachment"]["commandMode"] = "task-notification"
    p, ends = _bt("sid-old", [_hu(GB, "goodbye")] + m + [_ha("1970-01-12T13:45:40Z")])
    check(SR.human_since_offset(p, ends[0]) == [], "H6 control: a queued task notification is not his input")


# --- blind review 2 (2026-10-29): quiet window, fail closed, no clock filter, tx_path, generation -------------------

def _j_run(sch, st, o, times):
    """-> {tick time: [actions]} over a pending BENCH request."""
    return {t: run(sch, st, o, t) for t in times}


def test_j1_conductor_waits_a_quiet_window_not_the_grace():
    # P0-1 simplified: after a goodbye the kill needs goodbye_quiet_s (600 s) of silence on the transcript
    check(SR.DEFAULTS.get("goodbye_quiet_s") == 600, "J1 goodbye_quiet_s defaults to 600 s (%s)"
          % SR.DEFAULTS.get("goodbye_quiet_s"))
    sch = bsched()
    st = fresh()
    run(sch, st, obs(sessions=[bsess()], request=breq()), T0 + 1)
    a = run(sch, st, obs(sessions=[bsess()]), T0 + 125)
    check(bstate(st) == "pending" and "restart_kill" not in dos(a),
          "J1 past the 120 s grace but inside the quiet window: no kill (%s)" % dos(a))
    # the transcript grows at T0+300 (the window wrote something): the quiet clock restarts there
    run(sch, st, obs(sessions=[bsess()], cursor=clean_scan(size=250)), T0 + 300)
    a = run(sch, st, obs(sessions=[bsess()], cursor=clean_scan(size=250)), T0 + 650)
    check(bstate(st) == "pending" and "restart_kill" not in dos(a),
          "J1 transcript growth at +300 s restarts the quiet clock: no kill at +650 (%s)" % dos(a))
    # a record stamped later than the Dispatcher saw growth also anchors the window
    a = run(sch, st, obs(sessions=[bsess()], cursor=clean_scan(size=250, last_at=T0 + 500)), T0 + 905)
    check(bstate(st) == "pending" and "restart_kill" not in dos(a),
          "J1 a record stamped +500 s anchors the quiet window: no kill at +905 (%s)" % dos(a))
    a = run(sch, st, obs(sessions=[bsess()], cursor=clean_scan(size=250, last_at=T0 + 500)), T0 + 1105)
    check([x for x in a if x["do"] == "restart_kill"], "J1 control: ten silent minutes on every clock -> one kill (%s)"
          % dos(a))


def test_j2_any_input_after_the_goodbye_cancels_a_conductor():
    # P0-1 simplified: a ring, a task notification or a queue enqueue after the goodbye all cancel, not just his text
    tn = _u("1970-01-12T13:47:30Z", "[RimFlow Dispatcher - a program, not a person; ring]",
            origin={"kind": "task-notification"}, promptSource="system")
    enq = {"type": "queue-operation", "operation": "enqueue", "timestamp": "1970-01-12T13:47:31Z",
           "content": "hello?"}
    for extra, what in (([tn], "a task notification"), ([enq], "a queue-operation enqueue"),
                        ([_queued("1970-01-12T13:47:32Z", "x")], "a queued_command attachment")):
        p, ends = _bt("sid-old", [_hu(GB, "goodbye"), _ha("1970-01-12T13:45:10Z")] + extra)
        sc = SR.cursor_scan(p, ends[1])
        check(sc and sc["inputs"], "J2 cursor_scan counts %s as input (%s)" % (what, sc and len(sc["inputs"])))
        sch, st = bsched(), fresh()
        o = obs(sessions=[bsess()], request=dict(breq(), input_ts=GB_T, tx_offset=ends[1]))
        o["seat_restart"]["cursor"] = lambda seat, s_, rs, p=p: SR.cursor_scan(p, rs.get("tx_offset"))
        run(sch, st, o, T0 + 1)
        check(bstate(st) == "cancelled", "J2 %s after the goodbye cancels the Conductor restart (%s)" % (what, bstate(st)))
    p, ends = _bt("sid-old", [_hu(GB, "goodbye"), _ha("1970-01-12T13:45:10Z"),
                              {"type": "queue-operation", "operation": "dequeue", "timestamp": "1970-01-12T13:47:33Z"}])
    sc = SR.cursor_scan(p, ends[1])
    check(sc and not sc["inputs"] and not sc["human"], "J2 control: a dequeue alone is not input (%s)" % sc)


def test_j3_malformed_cancels_and_torn_holds():
    # P0-2: no record is skipped; a bad complete line cancels, a half-written last line holds, every reader fails closed
    p, ends = _bt("sid-old", [_hu(GB, "goodbye"), _ha("1970-01-12T13:45:10Z")])
    with open(p, "a") as f:
        f.write("{not json\n")
    sc = SR.cursor_scan(p, ends[1])
    check(sc and sc["malformed"] and not sc["torn"], "J3 a malformed complete line is reported (%s)" % sc)
    check(SR.human_since_offset(p, ends[1]) is None, "J3 human_since_offset is UNMEASURED on a malformed line")
    check(SR.last_human(p) is None, "J3 last_human is UNMEASURED on a malformed line")
    sch, st = bsched(), fresh()
    o = obs(sessions=[bsess()], request=dict(breq(), input_ts=GB_T, tx_offset=ends[1]))
    o["seat_restart"]["cursor"] = lambda seat, s_, rs: SR.cursor_scan(p, rs.get("tx_offset"))
    run(sch, st, o, T0 + 1)
    check(bstate(st) == "cancelled", "J3 a malformed record after the goodbye cancels (%s)" % bstate(st))
    p, ends = _bt("sid-old", [_hu(GB, "goodbye"), _ha("1970-01-12T13:45:10Z")])
    with open(p, "a") as f:
        f.write(json.dumps(_hu("1970-01-12T13:47:00Z", "wait"))[:40])       # torn: no newline yet
    sc = SR.cursor_scan(p, ends[1])
    check(sc and sc["torn"] and not sc["malformed"], "J3 a torn last record is reported (%s)" % sc)
    check(SR.human_since_offset(p, ends[1]) is None, "J3 human_since_offset is UNMEASURED on a torn record")
    check(SR.tx_summary(p) is None, "J3 tx_summary is UNMEASURED on a torn tail")
    try:
        SR._tail_records(p, 1 << 20)
        raised = False
    except SR.Torn:
        raised = True
    check(raised, "J3 _tail_records raises Torn on a torn tail, never drops it")
    sch, st = bsched(), fresh()
    o = obs(sessions=[bsess()], request=dict(breq(), input_ts=GB_T, tx_offset=ends[1]))
    o["seat_restart"]["cursor"] = lambda seat, s_, rs: SR.cursor_scan(p, rs.get("tx_offset"))
    run(sch, st, o, T0 + 1)
    a = run(sch, st, o, T0 + 2000)
    check(bstate(st) == "pending" and "restart_kill" not in dos(a), "J3 a torn record holds, never kills (%s)" % dos(a))
    sub = os.path.join(os.path.dirname(p), "sid-old", "subagents")
    os.makedirs(sub, exist_ok=True)
    with open(os.path.join(sub, "agent-torn.jsonl"), "w") as f:
        f.write(json.dumps(_ha("1970-01-12T13:45:10Z")) + "\n" + '{"type": "assi')
    check(SR.helpers_of(p) is None, "J3 helpers_of is UNMEASURED on a torn helper transcript")
    os.remove(os.path.join(sub, "agent-torn.jsonl"))


def test_j4_no_clock_filter_after_the_cursor():
    # P0-3: a human record after the cursor whose clock reads BEFORE the goodbye still cancels
    p, ends = _bt("sid-old", [_hu(GB, "goodbye"), _ha("1970-01-12T13:45:10Z"),
                              _hu("1970-01-12T13:44:00Z", "clock went backwards, still me")])
    hs = SR.human_since_offset(p, ends[1])
    check(hs and "backwards" in SR._text(hs[0]), "J4 the scan after the cursor ignores timestamps (%s)" % hs)
    sch, st = bsched(), fresh()
    o = obs(sessions=[bsess()], request=dict(breq(), input_ts=GB_T, tx_offset=ends[1]))
    o["seat_restart"]["cursor"] = lambda seat, s_, rs: SR.cursor_scan(p, rs.get("tx_offset"))
    run(sch, st, o, T0 + 1)
    check(bstate(st) == "cancelled", "J4 decide() cancels on it (%s)" % bstate(st))
    # the backstop binds its cursor to the end of his LAST input, not offset 0 plus a time filter
    over = {"ctx_tokens": 150_000, "last_kind": "assistant_end", "last_at": T0 - 4000, "last_user_at": T0 - 15_000}
    st = fresh()
    run(sch, st, obs(sessions=[bsess()], tx=over, last_human=(T0 - 15_000, {}, 4321, 9000)), T0)
    rs = st["seat_restart"].get("BENCH") or {}
    check(rs.get("source") == "backstop" and rs.get("tx_offset") == 4321,
          "J4 the backstop cursor is the end of his last input (%s)" % rs.get("tx_offset"))
    st = fresh()
    run(sch, st, obs(sessions=[bsess()], tx=over, last_human=None), T0)
    check(bstate(st) is None, "J4 an unreadable transcript gives no backstop (fail closed)")


def _wake(rec, gen):
    import contextlib
    import io
    sch = bsched()
    saved = SR._schedule
    try:
        SR._schedule = lambda: sch
        SR.write_killed("BENCH", rec)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            SR.main(["wake", "--seat", "BENCH"] + (["--gen", gen] if gen else []))
        return out.getvalue(), SR._read_json(SR.killed_path("BENCH")) or {}
    finally:
        SR._schedule = saved


def test_j5_wake_reads_the_transcript_the_record_names():
    # P1-4: the old window ran in another clone (or CLAUDE_CONFIG_DIR): the wake follows tx_path, not cfg["clone"]
    other = os.path.join(TMP, "elsewhere", "sid-far.jsonl")
    os.makedirs(os.path.dirname(other), exist_ok=True)
    first = json.dumps(_hu(GB, "goodbye")) + "\n"
    with open(other, "w") as f:
        f.write(first + json.dumps(_hu("1970-01-12T13:47:00Z", "FAR_AWAY_NOTE")) + "\n")
    check(other != SR.transcript_path(BCLONE, "sid-far"), "J5 control: the path is not the cfg clone's")
    o, _ = _wake({"seat": "BENCH", "session_id": "sid-far", "killed_at": T0 + 300, "req_ts": T0, "ticket": "GOODBYE",
                  "gen": "g-far", "tx_path": other, "tx_offset": len(first)}, "g-far")
    check("FAR_AWAY_NOTE" in o, "J5 the wake reads the transcript named in the killed record (%r)" % o[-200:])


def test_j6_wake_is_bound_to_one_restart():
    # P1-5: aborted, another generation, no --gen, or already woken -> nothing replayed; a full read marks it woken
    p = os.path.join(TMP, "elsewhere", "sid-gen.jsonl")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    first = json.dumps(_hu(GB, "goodbye")) + "\n"
    with open(p, "w") as f:
        f.write(first + json.dumps(_hu("1970-01-12T13:47:00Z", "GEN_NOTE")) + "\n")
    rec = {"seat": "BENCH", "session_id": "sid-gen", "killed_at": T0 + 300, "req_ts": T0, "ticket": "GOODBYE",
           "gen": "g1", "tx_path": p, "tx_offset": len(first)}
    o, _ = _wake(dict(rec, aborted="final fence: input"), "g1")
    check("GEN_NOTE" not in o and "ABORTED" in o, "J6 an aborted restart is not replayed (%r)" % o[-160:])
    o, _ = _wake(rec, "g0")
    check("GEN_NOTE" not in o, "J6 another restart's generation is not replayed")
    o, _ = _wake(rec, None)
    check("GEN_NOTE" not in o, "J6 a wake without --gen replays nothing")
    o, after = _wake(rec, "g1")
    check("GEN_NOTE" in o and after.get("woken_at"), "J6 the right generation reads it and marks it woken (%s)"
          % after.get("woken_at"))
    o, _ = _wake(after, "g1")
    check("GEN_NOTE" not in o and "already" in o, "J6 a second wake of the same restart replays nothing")
    o, after = _wake(dict(rec, tx_path=p + ".missing"), "g1")
    check("UNMEASURED" in o and not after.get("woken_at"), "J6 an UNMEASURED read is not marked woken")
    cfg = SR.config(bsched())["BENCH"]
    argv = SR.relaunch_argv("BENCH", cfg, "goodbye", gen="abc123")
    check("wake --seat BENCH --gen abc123" in argv[-1], "J6 the relaunch prompt carries the generation (%r)" % argv[-1])


def test_j7_fence_scans_then_status_last():
    # P0-1: the order of the final fence: transcript scan, then the window status (no owner clock since 2026-10-30)
    order = []
    p, ends = _bt("sid-old", [_hu(GB, "goodbye"), _ha("1970-01-12T13:45:10Z")])
    real = SR.cursor_scan
    try:
        SR.cursor_scan = lambda *a, **k: order.append("scan") or real(*a, **k)
        rs = {"cancel_after": GB_T, "tx_offset": ends[1], "tx_path": p, "seen_size": os.path.getsize(p),
              "quiet_since": T0 - 5000, "ts": T0 - 5000}
        f = SR.final_fence("BENCH", bsched(), rs, bsess(), now=T0 + 5000)
    finally:
        SR.cursor_scan = real
    check(f == [] and order == ["scan"] and "owner" not in inspect.signature(SR.final_fence).parameters,
          "J7 the fence scans and reads no owner clock (%s, %s)" % (order, f))
    rs2 = dict(rs, seen_size=rs["seen_size"] - 1)
    f = SR.final_fence("BENCH", bsched(), rs2, bsess(), now=T0 + 5000)
    check(f and "grew" in f[0], "J7 any growth since the claiming tick holds at the fence (%s)" % f)
    sch, st = bsched(), fresh()
    order2, kills = [], []
    fx = {"session_file": lambda pid: order2.append("status") or {"pid": pid, "sessionId": "sid-old",
                                                                  "name": "CONDUCTOR", "status": "idle"},
          "kill": lambda pid, start=None: kills.append(pid) or "SIGTERM", "write_killed": lambda seat, rec: None,
          "recheck": lambda *a: [], "start": lambda pid: 77, "final": lambda *a: order2.append("final") or []}
    run(sch, st, obs(sessions=[bsess()], request=breq()), T0 + 1)
    a = [x for x in run(sch, st, obs(sessions=[bsess()]), T0 + 605) if x["do"] == "restart_kill"]
    SR.execute(a[0], sch, st, True, T0 + 610, fx) if a else None
    i = order2.index("final") if "final" in order2 else -1
    check(a and kills and i >= 0 and "status" in order2[i + 1:],
          "J7 execute re-reads the window status after the fence, right before the signal (%s)" % order2)
    fx["session_file"] = lambda pid, n=[0]: (n.__setitem__(0, n[0] + 1) or
                                             {"pid": pid, "sessionId": "sid-old", "name": "CONDUCTOR",
                                              "status": "idle" if n[0] == 1 else "busy"})
    kills.clear()
    st = fresh()
    run(sch, st, obs(sessions=[bsess()], request=breq()), T0 + 1)
    a = [x for x in run(sch, st, obs(sessions=[bsess()]), T0 + 605) if x["do"] == "restart_kill"]
    res = SR.execute(a[0], sch, st, True, T0 + 610, fx) if a else "no kill"
    check(not kills, "J7 busy at the last status read: no signal (%s)" % res)


def test_j8_request_stores_the_transcript_it_read():
    rc, out, rq = _brequest([_hu(GB, "goodbye"), _ha("1970-01-12T13:45:10Z", "tool_use")])
    p = SR.transcript_path(BCLONE, "sid-old")
    check(rc == 0 and rq and rq.get("tx_path") == p, "J8 the request carries tx_path (%s)" % (rq or {}).get("tx_path"))



def test_k1_goodbye_kill_on_backstop_off():
    # owner 2026-10-29 after blind review 3: "Leave the goodbye kill on. If I'm typing at the same time it's an
    # acceptable risk." The context backstop stays off: he ruled only on the goodbye kill
    with open(os.path.join(HERE, "dispatcher_schedule.json"), encoding="utf-8") as f:
        live = json.load(f)
    raw = live["seat_restart"]["seats"]["BENCH"]
    check(raw.get("enabled") is True and raw.get("backstop") is False and "_why_off" not in raw
          and "acceptable risk" in (raw.get("_why_enabled") or "") and "2026-10-29" in raw.get("_why_enabled", ""),
          "K1 live: BENCH enabled true with his words and date in _why_enabled, backstop false, no _why_off")
    check("BENCH" in SR.config(live) and "FOUNDRY" in SR.config(live),
          "K1 live: BENCH and FOUNDRY are both in seat_restart.config (%s)" % sorted(SR.config(live)))
    over = {"ctx_tokens": 150_000, "last_kind": "assistant_end", "last_at": T0 - 40_000, "last_user_at": T0 - 40_000}

    def ticks(sch, st, request):
        seen = []
        for t in range(0, 20_000, 300):   # a backstop-eligible window, every tick for 5.5 h
            a = run(sch, st, obs(sessions=[bsess()], request=breq() if (request and t == 0) else None, tx=over,
                                 last_human=(T0 - 40_000, {}, 10, 100)), T0 + t)
            seen += [x["do"] for x in a if x.get("seat") == "BENCH"]
        return seen
    # the live backstop setting, on the test seat: no goodbye, so only a backstop could kill
    off = bsched(backstop=raw.get("backstop"))
    seen = []
    for start in (None, "cancelled"):
        st = fresh()
        if start:
            st["seat_restart"] = {"BENCH": {"state": start, "source": "backstop", "ts": T0 - 90_000, "ended_at": T0 - 90_000}}
        seen += ticks(off, st, False)
    check(not [d for d in seen if d in ("restart_kill", "restart_request")],
          "K1 backstop off: no backstop restart_request or restart_kill over 5.5 h of eligible ticks (%s)" % sorted(set(seen)))
    ctl = ticks(bsched(backstop=True), fresh(), False)
    check("restart_kill" in ctl, "K1 control: backstop on, the same ticks reach restart_kill (%s)" % sorted(set(ctl)))
    gb = ticks(off, fresh(), True)
    check("restart_kill" in gb, "K1 goodbye on: with the backstop off, a goodbye request still reaches restart_kill (%s)"
          % sorted(set(gb)))
    # the guard stays: a seat switched off is never killed, whatever action reaches execute
    sch = bsched(enabled=False, backstop=False)
    kills = []
    fx = {"session_file": lambda pid: {"pid": pid, "sessionId": "sid-old", "name": "CONDUCTOR", "status": "idle"},
          "kill": lambda pid, start=None: kills.append(pid) or "SIGTERM", "write_killed": lambda seat, rec: None,
          "recheck": lambda *a: [], "start": lambda pid: 77, "final": lambda *a: []}
    st = fresh()
    st["seat_restart"] = {"BENCH": {"state": "claimed", "session_id": "sid-old", "pid": 4242, "start": 77}}
    act = {"do": "restart_kill", "seat": "BENCH", "pid": 4242, "session_id": "sid-old", "session_name": "CONDUCTOR",
           "session_names": ["CONDUCTOR"], "argv": ["x", "p"], "gen": "g"}
    res = SR.execute(act, sch, st, True, T0, fx)
    check(not kills and res.startswith("refused") and st["seat_restart"]["BENCH"]["state"] == "cancelled",
          "K1 BENCH off: execute refuses a restart_kill that reaches it, nothing signalled (%s)" % res)
    lo = json.loads(json.dumps(live))
    lo["seat_restart"]["seats"]["BENCH"]["enabled"] = False
    res = SR.execute(act, lo, st, True, T0, fx)
    check(not kills and res.startswith("refused"), "K1 the live schedule with BENCH switched off refuses it too (%s)" % res)
    # control: the same action with the seat on reaches the kill path (the guard is what stopped it)
    st["seat_restart"]["BENCH"]["state"] = "claimed"
    SR.execute(act, bsched(), st, True, T0, fx)
    check(kills == [4242], "K1 control: BENCH switched on, the same claimed action signals (%s)" % kills)
    # the window's own request asks for nothing while off
    import contextlib
    import io
    saved = (SR._schedule, SR.unpublished_shard)
    try:
        SR._schedule = lambda: sch
        SR.unpublished_shard = lambda seat, clone: None     # a published shard: only the off switch can stop it
        rp = SR.request_path("BENCH")
        if os.path.exists(rp):
            os.remove(rp)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = SR.main(["request", "--seat", "BENCH", "--ticket", "GOODBYE", "--reason", "goodbye", "--pid", "4242",
                          "--note", "n", "--fresh"])
    finally:
        SR._schedule, SR.unpublished_shard = saved
    check(rc == 0 and not os.path.exists(rp) and "not enabled" in out.getvalue(),
          "K1 BENCH off: `request` writes no request (%r)" % out.getvalue()[-120:])


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
