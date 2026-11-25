#!/usr/bin/env python3
"""idle_stop.py - a SteveDesktop game that no job has used for IDLE_STOP_S is stopped, for the memory (owner, 2026-11-25:
"If you're not running the live game, kill them for the memory and simplicity."). The worker's load starts it again when
the next job comes. Page: design/specs/2026-11-25-steve-idle-game-stop/boundary.md. No AI.

The stop is the game's own `rw_game.sh down`, which refuses while a holder (the bridge lock, a host guard) uses the game.
"""
import os
import subprocess
import time

import schema as S

# budget: danger=a shorter time makes the next job pay one cold start (262 s, J20261125T200030Z-271675.a1, 2026-11-25);
# budget: evidence=18 of 458 gaps between jobs in the 7 days to 2026-11-25 were longer than 30 min (testq done records);
# budget: ends no work: an idle game with no job running or pending is stopped, and the next job starts it
IDLE_STOP_S = 30 * 60
# budget: danger=a `down` refused every minute while a helper drives the game; ends no work: the stop is asked again
RETRY_S = 30 * 60


def state_path(T, host):
    return T.q("%s_idle.json" % host)


def stamp(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def down_cmd(T, host):
    """The shell line that stops HOST's game on SteveDesktop (Steve2: its own clone and instance, as remote_cmd)."""
    runner, pre = (T.REMOTE_RUNNER_B, T.STEVE2_PREFIX) if host == T.STEVE2 else (T.REMOTE_RUNNER, "")
    return "cd %s && %sinfrastructure/stevedesktop/rw_game.sh down" % (runner, pre)


def ssh_run(T, cmd):
    import time_budget
    try:
        r = subprocess.run(T.SSH + [T.SSH_TARGET, cmd], capture_output=True, text=True, timeout=time_budget.CALL_S)
    except subprocess.TimeoutExpired:
        return None, "ssh timed out"
    return r.returncode, (r.stdout + r.stderr).strip()


def step(T, now=None, run=None):
    """One tick: -> {host: what was done}. Never raises into the tick (a failure is logged and returned)."""
    now = time.time() if now is None else now
    run = run or ssh_run
    out = {}
    try:
        busy_all = any(T.ready(j, now) for j in T.records("pending"))
        for host in T.STEVE_HOSTS:
            path = state_path(T, host)
            st = T.read_json(path) or {}
            if busy_all or T.lane_running(host):
                if st:
                    os.remove(path)
                out[host] = "in use"
                continue
            if not st.get("since"):
                S.dump({"since": stamp(now)}, path)
                out[host] = "idle from now"
                continue
            idle = now - S.parse_ts(st["since"])
            if idle < IDLE_STOP_S:
                out[host] = "idle %d s" % idle
                continue
            if st.get("refused_at") and now - S.parse_ts(st["refused_at"]) < RETRY_S:
                out[host] = "refused, waits"
                continue
            rc, text = run(T, down_cmd(T, host))
            name = T.GAME_NAMES.get(host, host)
            if rc == 0:
                S.dump({"since": stamp(now)}, path)        # a new idle clock: a game started again is asked again
                if "already stopped" not in (text or ""):
                    T.log("GAME %s idle %d min with no job: stopped for the memory (%s); the next job starts it"
                          % (name, idle // 60, (text or "")[-120:]))
                out[host] = "stopped"
            else:
                S.dump(dict(st, refused_at=stamp(now), why=(text or "")[-300:]), path)
                T.log("GAME %s idle %d min with no job: not stopped (exit %s: %s); asked again in %d min"
                      % (name, idle // 60, rc, (text or "")[-200:], RETRY_S // 60))
                out[host] = "refused"
    except Exception as e:  # noqa: BLE001 - the idle stop must never stop dispatch
        T.log("idle stop failed: %s: %s" % (type(e).__name__, e))
        out["error"] = "%s: %s" % (type(e).__name__, e)
    return out
