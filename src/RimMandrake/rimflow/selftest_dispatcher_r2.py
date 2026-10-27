#!/usr/bin/env python3
"""Selftests for the dispatcher review r2 fixes (DISPATCHER_STOP_HARDEN_HANGS_SKIP_THE_KILL):
  #1 stop() isolates every target: a raising/hanging systemctl never skips the marker KILL;
  #2 the run's own wall-time bound (launch_argv, claude_bounded), the run registry supervised when state.json is
     unreadable, the dry-run tick's alarm, and `stop-runs` (stop and VERIFY before a rollback);
  #3 a same-user /proc entry that cannot be read and is not ruled out = UNMEASURED, the role stays busy;
  #4 withdraw() outcomes by ring id (both race sides, a permission failure) and what execute keeps;
  #5 a role_launch that raises before its run exists: reservation given back, fixed outcome, never "launched";
  #6 a disabled seat's ring is withdrawn before the agents gate; a consumed one is still verified.
Uses the fixtures of selftest_dispatcher.py (its import points RM_DISPATCHER_STATE at a temp dir)."""
import json
import os
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import selftest_dispatcher as T  # noqa: E402
from selftest_dispatcher import (D, RL, check, conductor, fresh, obs, operations, ops_status, robs,  # noqa: E402
                                 rdecide, role_acts, sched, stall, at_local)
import doorbell  # noqa: E402

TMP = tempfile.mkdtemp(prefix="selftest_dispatcher_r2_")


def _cp(rc=0, out=""):
    return subprocess.CompletedProcess([], rc, out, "")


# ------------------------------------------------------------------------------------------------ #1
def test_r2_1_stop_isolated():
    calls, sigs = [], []

    def hang(argv, **kw):              # every systemctl hangs: subprocess.run's timeout fires
        calls.append(list(argv))
        check(kw.get("timeout") and kw["timeout"] <= 30, "r2#1 each systemctl call is time-bounded (%r)" % kw.get("timeout"))
        raise subprocess.TimeoutExpired(argv, kw.get("timeout"))
    out = RL.stop("U", "S.scope", runner=hang, seat="BENCH", marker="U", force=True,
                  procs=lambda m, **k: [11, 12], kill=lambda p, s: sigs.append((p, s)))
    check(sigs == [(11, 9), (12, 9)], "r2#1 forced stop with every systemctl hanging: the marked processes are KILLed")
    check(calls == [["systemctl", "--user", "kill", "--signal=SIGKILL", "S.scope"],
                    ["systemctl", "--user", "stop", "--no-block", "S.scope"],
                    ["systemctl", "--user", "stop", "--no-block", "U"]],
          "r2#1 ... and every target is still tried after the first one hangs: %r" % calls)
    check("TimeoutExpired" in out and "KILL to 2 of 2" in out, "r2#1 the result says what hung and what was killed")
    # the first (scope) stop raises: the unit stop and the marker TERM still happen
    calls[:], sigs[:] = [], []

    def first_raises(argv, **kw):
        calls.append(list(argv))
        if len(calls) == 1:
            raise RuntimeError("dbus gone")
        return _cp()
    out = RL.stop("U", "S.scope", runner=first_raises, marker="U", procs=lambda m, **k: [11],
                  kill=lambda p, s: sigs.append((p, s)))
    check(len(calls) == 2 and calls[1][-1] == "U" and sigs == [(11, 15)] and "RuntimeError" in out,
          "r2#1 a raising scope stop: the unit is still stopped and the marked process TERMed (%r)" % out)
    # the MainPID scope lookup raises, the marker scan raises: stop still returns, never raises
    calls[:] = []

    def boom(argv, **kw):
        raise OSError("no systemctl")
    try:
        out = RL.stop("U", None, runner=boom, seat="BENCH", marker="U", procs=lambda m, **k: 1 / 0,
                      kill=lambda p, s: None)
        ok = "UNMEASURED" in out
    except Exception as e:  # noqa: BLE001
        ok, out = False, "raised %r" % e
    check(ok, "r2#1 scope lookup and marker scan both raise: stop returns and says UNMEASURED (%s)" % out[:120])
    # real processes: a TERM-ignoring marked child survives, every systemctl hangs; the forced stop kills it
    mk = "r2-selftest-%d" % os.getpid()
    t_run = time.time()
    p = subprocess.Popen(["sh", "-c", "trap '' TERM; sleep 30"], env=dict(os.environ, RM_ROLE_UNIT=mk))
    try:
        time.sleep(0.2)
        RL.stop(mk, "claude-seat-SCRATCH-%s.scope" % mk, runner=hang, marker=mk, force=False, since=t_run)
        time.sleep(0.3)
        check(p.poll() is None, "r2#1 probe: the marked shell survives TERM")
        RL.stop(mk, "claude-seat-SCRATCH-%s.scope" % mk, runner=hang, marker=mk, force=True, since=t_run)
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass
        check(p.poll() is not None, "r2#1 real /proc: the forced stop KILLs the surviving marked process although "
              "systemctl hangs")
    finally:
        if p.poll() is None:
            p.kill()
            p.wait()


# ------------------------------------------------------------------------------------------------ #2
def test_r2_2_bound_registry_rollback():
    role = conductor(run_max_s=1800)
    argv = RL.launch_argv(role, "UB", "m", "/o", "/e", "/usr/bin/claude")
    bound = 1800 + RL.SCOPE_GRACE_S
    check("CLAUDE_SCOPE_RUNTIME_MAX=%d" % bound in argv and "RuntimeMaxSec=%d" % bound in argv
          and "TimeoutStopSec=30" in argv, "r2#2 launch_argv: the scope and the unit carry run_max_s + grace as "
          "RuntimeMaxSec, KILL 30 s later")
    sh = os.path.join(HERE, "..", "Utils", "claude_bounded.sh")
    r = subprocess.run(["bash", sh, "--version"], env=dict(os.environ, CLAUDE_SCOPE_RUNTIME_MAX="abc",
                                                            AGENT_SEAT="SCRATCH"),
                       capture_output=True, text=True, timeout=60)
    check(r.returncode == 2 and "refusing to start unbounded" in (r.stdout + r.stderr),
          "r2#2 claude_bounded refuses a malformed bound (rc %d)" % r.returncode)
    src = open(sh, encoding="utf-8").read()
    check('"${SCOPE_TIME[@]}"' in src and "RuntimeMaxSec=" in src, "r2#2 claude_bounded puts the bound on its scope")

    # the registry: state.json unreadable -> the runs on runs.json are still supervised and stopped
    old_env = os.environ["RM_DISPATCHER_STATE"]
    try:
        root = os.path.join(TMP, "reg")
        os.environ["RM_DISPATCHER_STATE"] = root
        os.makedirs(root, exist_ok=True)
        t = at_local("19:00")
        run = {"unit": "rm-role-operations-9", "at": t, "day": RL.day_of(t), "budget": 1, "mode": "run",
               "state": "running", "seat": "BENCH", "run_max_s": 1800, "marker": "rm-role-operations-9",
               "scope": RL.role_scope("BENCH", "rm-role-operations-9")}
        st = fresh()
        st["roles"] = {"Operations": {"done": {}, "runs": [dict(run)]}}
        D.save(st, root)
        check(D.load_registry(root)["roles"]["Operations"]["runs"][0]["unit"] == run["unit"],
              "r2#2 every state save writes the run registry")
        with open(os.path.join(root, "state.json"), "w") as f:
            f.write("{torn")
        stops = []
        fx = {"role_stop": lambda *a, **k: stops.append((a, k)) or "stopped", "lock": lambda: None,
              "note": lambda i, tx: (True, ""), "publish": lambda n: "p"}
        o = obs()
        o["roles"] = robs(ops_status(t + 4000), unit="active")
        sch = sched(roles=[operations()])
        acts = D.tick(sch, True, obs=o, now=t + 4000, fx=fx)
        check(len(stops) == 1 and stops[0][0][0] == run["unit"] and stops[0][1].get("since") == t,
              "r2#2 state.json unreadable: the registry's overtime run is still stopped (%d stop(s))" % len(stops))
        check(any("UNREADABLE" in str(x.get("why")) for x in acts) and open(os.path.join(root, "state.json")).read()
              == "{torn", "r2#2 ... nothing else decided, the unreadable state.json is left for the owner")
        check(D.load_registry(root)["roles"]["Operations"]["runs"][0].get("stop_tries") == 1,
              "r2#2 ... and the registry keeps the stop count (KILL from the third)")
        os.remove(D.runs_path(root))
        acts = D.tick(sch, True, obs=o, now=t + 4300, fx=fx)
        check(len(stops) == 1 and "RuntimeMaxSec" in acts[0]["why"],
              "r2#2 state and registry both unreadable: says only the scope bound holds")
        # dry-run tick: the live root still has a running run -> alarm
        D.save(st, root)
        acts = D.tick(sched(), False, obs=obs(), now=t + 4400, fx={})
        check(any(x.get("kind") == "dry:live_runs_unsupervised" for x in acts),
              "r2#2 a dry-run tick says the live runs are unsupervised")
        D.save(fresh(), root)
        acts = D.tick(sched(), False, obs=obs(), now=t + 4500, fx={})
        check(not any(x.get("kind") == "dry:live_runs_unsupervised" for x in acts),
              "r2#2 ... and is quiet when no live run remains")
        # stop-runs: stops and VERIFIES, KILL after force_after_s; never ends -> False
        D.save(st, root)
        clock = {"t": 0.0}
        seen = []
        left = {"n": 3}

        def ustate(u):
            return "active" if left["n"] > 0 else "inactive"

        def stopper(unit, scope, **k):
            seen.append(k["force"])
            left["n"] -= 1
            return "x"
        ro = {"unit_state": ustate, "procs": lambda m, **k: []}
        ok, lines = D.stop_runs(sch, wait_s=120, force_after_s=10, obs=ro, clock=lambda: clock["t"],
                                sleep=lambda s: clock.__setitem__("t", clock["t"] + s), stopper=stopper)
        check(ok and seen == [False, False, True] and lines[-1].endswith("ENDED (verified)"),
              "r2#2 stop-runs: TERM, then KILL after force_after_s, ended verified (%r)" % seen)
        left["n"], clock["t"] = 10 ** 6, 0.0
        ok, lines = D.stop_runs(sch, wait_s=30, force_after_s=10, obs=ro, clock=lambda: clock["t"],
                                sleep=lambda s: clock.__setitem__("t", clock["t"] + s), stopper=stopper)
        check(not ok and lines[-1].endswith("STILL RUNNING"), "r2#2 stop-runs: a run that never ends -> not verified")
        ro2 = {"unit_state": lambda u: "inactive", "procs": lambda m, **k: None}
        ok, lines = D.stop_runs(sch, wait_s=10, force_after_s=5, obs=ro2, clock=lambda: clock["t"],
                                sleep=lambda s: clock.__setitem__("t", clock["t"] + s), stopper=lambda *a, **k: "x")
        check(not ok, "r2#2 stop-runs: a blind marker scan is never 'ended'")
        with open(os.path.join(root, "state.json"), "w") as f:
            f.write("{torn")
        os.remove(D.runs_path(root))
        ok, lines = D.stop_runs(sch, wait_s=10, force_after_s=5, obs=ro, stopper=lambda *a, **k: "x")
        check(not ok and "UNMEASURED" in lines[0], "r2#2 stop-runs: state and registry unreadable -> UNMEASURED, "
              "never 'all ended'")
    finally:
        os.environ["RM_DISPATCHER_STATE"] = old_env


# ------------------------------------------------------------------------------------------------ #3
def _fake_proc(base, procs, btime=1000):
    """procs: {pid: (environ bytes or None for unreadable, start epoch)}."""
    os.makedirs(base, exist_ok=True)
    with open(os.path.join(base, "stat"), "w") as f:
        f.write("cpu 1 2 3\nbtime %d\n" % btime)
    tck = os.sysconf("SC_CLK_TCK")
    for pid, (env, start) in procs.items():
        d = os.path.join(base, str(pid))
        os.makedirs(d, exist_ok=True)
        fields = ["S"] + ["0"] * 18 + [str(int((start - btime) * tck))] + ["0"] * 5
        with open(os.path.join(d, "stat"), "w") as f:
            f.write("%d (x y) %s\n" % (pid, " ".join(fields)))
        e = os.path.join(d, "environ")
        with open(e, "wb") as f:
            f.write(env or b"")
        if env is None:
            os.chmod(e, 0)
    return base


def test_r2_3_unreadable_is_unmeasured():
    if os.getuid() == 0:
        check(False, "r2#3 cannot run as root (mode 000 is readable): UNMEASURED")
        return
    run_at = 50000.0
    fp = _fake_proc(os.path.join(TMP, "proc3"), {101: (b"RM_ROLE_UNIT=uR\0", run_at + 3),
                                                  102: (None, run_at + 10),       # young, ours, unreadable
                                                  103: (None, 2000.0)})           # old (systemd/sd-pam): ruled out
    check(RL.procs_of("uR", proc=fp, since=run_at) is None,
          "r2#3 a same-user process younger than the run with unreadable environ: UNMEASURED (None)")
    check(RL.procs_of("uR", proc=fp) is None, "r2#3 ... and with no run start every unreadable same-user one is")
    check(RL.procs_of("uR", proc=fp, since=run_at, uid=os.getuid() + 1) == [101],
          "r2#3 another uid's unreadable process is ruled out")
    os.chmod(os.path.join(fp, "102", "environ"), 0o600)
    check(RL.procs_of("uR", proc=fp, since=run_at) == [101],
          "r2#3 a process older than the run (unreadable) is ruled out; the readable marked one is seen")
    os.chmod(os.path.join(fp, "102", "environ"), 0)
    run = {"unit": "uR", "scope": "S.scope", "marker": "uR", "at": run_at}
    ob = {"unit_state": lambda u: "inactive", "procs": lambda m, since=None: RL.procs_of(m, proc=fp, since=since)}
    v = RL.ended(run, "inactive", ob)
    check(v not in RL.TERMINAL and "UNMEASURED" in v, "r2#3 ended(): the blind scan keeps the run busy (%s)" % v)
    st = fresh()
    st["roles"] = {"Operations": {"done": {}, "runs": [dict(run, state="running", seat="BENCH", day="d",
                                                            budget=1, mode="run", run_max_s=1800)]}}
    o = robs(ops_status(run_at + 60), unit="inactive")
    o["procs"] = ob["procs"]
    rdecide([operations(runs_local=["23:59"])], st, o, run_at + 60)
    check(st["roles"]["Operations"]["runs"][0]["state"] == "running",
          "r2#3 supervise: the role stays busy while the scan is blind")
    os.chmod(os.path.join(fp, "102", "environ"), 0o600)


# ------------------------------------------------------------------------------------------------ #4
def test_r2_4_withdraw_outcomes():
    root = os.path.join(TMP, "w4")
    os.makedirs(root, exist_ok=True)
    inbox = doorbell.inbox_path("FOUNDRY", root)
    no = lambda r, s, i: None   # noqa: E731
    D.ring(root, "FOUNDRY", "R1", "m")
    w = D.withdraw(root, "FOUNDRY", "R1", consumed=no)
    check(w["outcome"] == "withdrawn" and w["ring_id"] == "R1" and not os.path.exists(inbox), "r2#4 withdrawn")
    # race side A: the doorbell took it before withdraw read the inbox
    w = D.withdraw(root, "FOUNDRY", "R2", consumed=lambda r, s, i: {"consumed_at": 77.0} if i == "R2" else None)
    check(w["outcome"] == "consumed" and w["consumed_at"] == 77.0, "r2#4 race A: consumed before the read -> consumed")
    # race side B: read it, the doorbell renamed it away before our rename
    D.ring(root, "FOUNDRY", "R3", "m")
    real = os.rename
    taken = {}

    def doorbell_wins(src, dst):
        if src == inbox:
            os.remove(src)
            taken["R3"] = {"consumed_at": 88.0}
            raise FileNotFoundError(src)
        return real(src, dst)
    D.os.rename = doorbell_wins
    try:
        w = D.withdraw(root, "FOUNDRY", "R3", consumed=lambda r, s, i: taken.get(i))
    finally:
        D.os.rename = real
    check(w["outcome"] == "consumed" and w["consumed_at"] == 88.0, "r2#4 race B: the doorbell won the rename -> "
          "consumed (%s)" % w["outcome"])
    check(D.withdraw(root, "FOUNDRY", "R9", consumed=no)["outcome"] == "absent", "r2#4 never written -> absent")
    # permission failure: withdrawn/ not writable, the ring still in the inbox -> failed
    D.ring(root, "FOUNDRY", "R4", "m")
    wd = os.path.join(root, "withdrawn")
    os.chmod(wd, 0o500)
    try:
        w = D.withdraw(root, "FOUNDRY", "R4", consumed=no)
    finally:
        os.chmod(wd, 0o700)
    check(w["outcome"] == "failed" and os.path.exists(inbox) and "PermissionError" in w["why"],
          "r2#4 permission failure: failed, the ring still in the inbox (%s)" % w.get("why"))
    os.chmod(inbox, 0)
    try:
        w = D.withdraw(root, "FOUNDRY", "R4", consumed=no)
    finally:
        os.chmod(inbox, 0o600)
    check(w["outcome"] == "failed" or os.getuid() == 0, "r2#4 unreadable inbox: failed (%s)" % w["outcome"])
    # execute keeps what the evidence says
    sch = sched()
    for res, want in (({"outcome": "failed", "ring_id": "R4", "why": "x"}, "kept"),
                      ("withdrawn", "kept"),                                    # not a known outcome: unknown
                      ({"outcome": "consumed", "ring_id": "R4", "consumed_at": 99.0}, "consumed"),
                      ({"outcome": "withdrawn", "ring_id": "R4"}, "gone")):
        st = fresh()
        pend = {"ring_id": "R4", "rung_at": 1.0, "rung_iso": "x", "attempt": 1, "ticket": "T"}
        acts = [{"do": "withdraw", "seat": "FOUNDRY", "ring_id": "R4", "pending": dict(pend), "at": "x"}]
        D.execute(acts, sch, st, root, True, 100.0, {"withdraw": lambda *a, **k: res, "lock": lambda: None})
        ring = st["seats"]["FOUNDRY"].get("ring")
        alarm = any(a.get("kind") == "withdraw_failed:FOUNDRY" for a in acts)
        got = ("consumed" if ring and ring.get("consumed_at") == 99.0 else "kept" if ring and alarm
               else "gone" if not ring and not alarm else "wrong")
        check(got == want, "r2#4 execute on %r: %s (got %s)" % (res if isinstance(res, str) else res["outcome"],
                                                                want, got))


# ------------------------------------------------------------------------------------------------ #5
def test_r2_5_raise_before_run():
    now = at_local("08:00")
    st = fresh()
    sch = sched(roles=[conductor()])
    o = obs()
    o["roles"] = robs(ops_status(now))
    acts = D.decide(sch, st, o, now, True)
    la = [a for a in acts if a["do"] == "role_launch"]
    check(len(la) == 1 and st["roles"]["Conductor"].get("pending_launch"), "r2#5 probe: decide reserved a launch")
    launched = []
    fx = {"role_launch": lambda *a, **k: launched.append(a) or (True, "u"), "off": lambda p: None,
          "paused": lambda: None, "lock": lambda: None, "note": lambda i, t: (True, ""), "publish": lambda n: "p",
          "persist": lambda: None}
    real = RL.run_paths

    def boom(*a):
        raise OSError("disk full")
    RL.run_paths = boom
    try:
        D.execute(acts, sch, st, os.path.join(TMP, "r5"), True, now, fx)
    finally:
        RL.run_paths = real
    rs = st["roles"]["Conductor"]
    check(not launched and not rs.get("pending_launch") and not rs.get("runs"),
          "r2#5 run_paths raises: nothing launched, the reservation is given back")
    check("NOT LAUNCHED" in la[0]["why"] and any(a.get("kind") == "role:Conductor:launch_failed" for a in acts),
          "r2#5 ... the note says NOT LAUNCHED and a launch_failed alarm is raised")
    st2 = fresh()
    D.decide(sch, st2, o, now, True)
    check(st2["roles"]["Conductor"].get("pending_launch"), "r2#5 ... and the slot is still due (a fresh decide "
          "reserves it again)")
    # a blind role: the shared item's fixed outcome is launch_failed, never "launched"
    st = fresh()
    a = {"do": "role_launch", "role": "Gone", "unit": "UG", "message": "m", "ticket": "X", "note": True,
         "mode": "quick", "budget": 1, "slot": "k", "band": "GREEN", "why": "w", "seat": "BENCH",
         "blind": {"role": "Gone", "outcome": "launched"}}
    st["roles"] = {"Gone": {"done": {"k": 5}, "pending_launch": {
        "unit": "UG", "mode": "quick", "key": "k", "done": None, "had_done": False, "alarms_seen": None,
        "event_cursor": None, "alarm_day": None, "events_seen": None, "alarm_last_run": None}}}
    acts = [a, {"do": "alarm", "kind": "after", "why": "w", "note": False}]
    D.execute(acts, sch, st, os.path.join(TMP, "r5"), True, now, fx)
    check(a["blind"]["outcome"] == "launch_failed" and not st["roles"]["Gone"].get("pending_launch")
          and st["roles"]["Gone"]["done"] == {} and "NOT LAUNCHED" in a["why"],
          "r2#5 role gone from the schedule (raise before the run): outcome launch_failed, slot given back")
    # a malformed reservation: the give-back raises too; execute still carries on with the next action
    st["roles"] = {"Gone": {"pending_launch": {"unit": "UG", "mode": "quick"}}}
    a2 = dict(a, why="w", blind={"role": "Gone", "outcome": "launched"})
    acts = [a2, {"do": "alarm", "kind": "after2", "why": "w", "note": False}]
    try:
        D.execute(acts, sch, st, os.path.join(TMP, "r5"), True, now, fx)
        ok = "after2" in st["alarms"] and a2["blind"]["outcome"] == "launch_failed"
    except Exception as e:  # noqa: BLE001
        ok = False
        print("   raised %r" % e)
    check(ok, "r2#5 a give-back that raises never escapes execute (the next action still runs)")


# ------------------------------------------------------------------------------------------------ #6
def test_r2_6_disabled_seat():
    t0 = 1000.0
    sch = sched()
    st = fresh()
    a = stall(sch, st, obs(), t0)
    rid = [x for x in a if x["do"] == "ring"][0]["ring_id"]
    sch["seats"]["FOUNDRY"]["enabled"] = False
    a = D.decide(sch, st, obs(agents_ok=False), t0 + sch["stall_after_s"] + 60, True)
    check(any(x["do"] == "withdraw" and x["ring_id"] == rid for x in a) and not st["seats"]["FOUNDRY"].get("ring"),
          "r2#6 disabled seat, claude agents UNMEASURED: its unconsumed ring is still withdrawn")
    st = fresh()
    a = stall(sched(), st, obs(), t0)
    pend = st["seats"]["FOUNDRY"]["ring"]
    pend["consumed_at"] = t0 + sched()["stall_after_s"] + 5
    ev = [{"event": "lease", "action": "take", "id": "SOME_ITEM_DO_IT", "ts": "9999-01-01T00:00:00Z"}]
    a = D.decide(sch, st, obs(events=ev), t0 + sch["stall_after_s"] + 60, True)
    check(any(x["do"] == "verified" and x["ring_id"] == pend["ring_id"] for x in a)
          and not st["seats"]["FOUNDRY"].get("ring"),
          "r2#6 disabled seat: a ring the doorbell took is still verified (%s)" % [x["do"] for x in a])
    st = fresh()
    a = D.decide(sch, st, obs(), t0, True)
    check(not st["seats"].get("FOUNDRY") and not [x for x in a if x.get("seat") == "FOUNDRY"],
          "r2#6 disabled seat with no ring: nothing done for it")


# ------------------------------------------------------------------------------------------------ review r3
def test_r3_lock_and_missing_state():
    """r3 #1: stop-runs holds the live tick.lock through snapshot + verification (a mid-launch tick cannot start a run
    after the snapshot). r3 #2: state.json MISSING with live runs on the registry is not a fresh start."""
    import fcntl
    old_env = os.environ["RM_DISPATCHER_STATE"]
    try:
        root = os.path.join(TMP, "r3")
        os.environ["RM_DISPATCHER_STATE"] = root
        os.makedirs(root, exist_ok=True)
        t = at_local("19:00")
        run = {"unit": "rm-role-operations-7", "at": t, "day": RL.day_of(t), "budget": 1, "mode": "run",
               "state": "running", "seat": "BENCH", "run_max_s": 1800, "marker": "rm-role-operations-7",
               "scope": RL.role_scope("BENCH", "rm-role-operations-7")}
        st = fresh()
        st["roles"] = {"Operations": {"done": {}, "runs": [dict(run)]}}
        D.save(st, root)
        sch = sched(roles=[operations()])
        ro = {"unit_state": lambda u: "inactive", "procs": lambda m, **k: []}
        # #1: a tick holds the lock -> stop-runs waits; past the budget it is UNMEASURED, never "all ended"
        clock = {"t": 0.0}
        with open(os.path.join(root, "tick.lock"), "w") as held:
            fcntl.flock(held, fcntl.LOCK_EX)
            ok, lines = D.stop_runs(sch, wait_s=10, force_after_s=5, obs=ro, clock=lambda: clock["t"],
                                    sleep=lambda s: clock.__setitem__("t", clock["t"] + s),
                                    stopper=lambda *a, **k: "x")
        check(not ok and "UNMEASURED" in lines[0] and clock["t"] >= sch.get("tick_budget_s", 420),
              "r3#1 stop-runs waits for a running tick's lock and never verifies around it (%r)" % lines[:1])
        ok, lines = D.stop_runs(sch, wait_s=10, force_after_s=5, obs=ro, stopper=lambda *a, **k: "x")
        check(ok, "r3#1 ... and with the lock free it verifies as before (%r)" % lines)
        lk = open(os.path.join(root, "tick.lock"), "w")
        try:
            fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
            freed = True
        except BlockingIOError:
            freed = False
        lk.close()
        check(freed, "r3#1 stop-runs releases the lock when it returns")
        # #2: state.json removed while the registry still lists a live run
        os.remove(os.path.join(root, "state.json"))
        try:
            D.load_state(root)
            raised = False
        except D.StateUnreadable:
            raised = True
        check(raised, "r3#2 state.json missing + a live run on the registry -> not a fresh state")
        stops = []
        fx = {"role_stop": lambda *a, **k: stops.append((a, k)) or "stopped", "lock": lambda: None,
              "note": lambda i, tx: (True, ""), "publish": lambda n: "p"}
        o = obs()
        o["roles"] = robs(ops_status(t + 4000), unit="active")
        acts = D.tick(sch, True, obs=o, now=t + 4000, fx=fx)
        check(not any(x.get("do") == "role_launch" for x in acts) and len(stops) == 1
              and not os.path.exists(os.path.join(root, "state.json")),
              "r3#2 ... the tick supervises the registry (overtime run stopped), launches nothing, writes no fresh "
              "state (%d stop(s))" % len(stops))
        ro_live = {"unit_state": lambda u: "active", "procs": lambda m, **k: []}
        ok, lines = D.stop_runs(sch, wait_s=0, force_after_s=0, obs=ro_live, stopper=lambda *a, **k: "x")
        check(not ok and any(run["unit"] in ln for ln in lines),
              "r3#2 stop-runs with state.json missing still finds the registry's live run (%r)" % lines)
        # a readable state that lost a run the registry still lists: the union is stopped
        D.save(fresh(), root)
        S_reg = {"roles": {"Operations": {"runs": [dict(run)]}}, "alarms": {}, "saved_at": time.time()}
        with open(D.runs_path(root), "w") as f:
            json.dump(S_reg, f)
        ok, lines = D.stop_runs(sch, wait_s=0, force_after_s=0, obs=ro_live, stopper=lambda *a, **k: "x")
        check(not ok and any(run["unit"] in ln for ln in lines),
              "r3#2 stop-runs takes the union of state and registry")
    finally:
        os.environ["RM_DISPATCHER_STATE"] = old_env


def main():
    for t in (test_r2_1_stop_isolated, test_r2_2_bound_registry_rollback, test_r2_3_unreadable_is_unmeasured,
              test_r2_4_withdraw_outcomes, test_r2_5_raise_before_run, test_r2_6_disabled_seat,
              test_r3_lock_and_missing_state):
        try:
            t()
        except Exception as e:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            check(False, "%s crashed: %s" % (t.__name__, e))
    print("%d failure(s)" % len(T.FAILS))
    return 1 if T.FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
