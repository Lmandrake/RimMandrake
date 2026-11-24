#!/usr/bin/env python3
"""run_end_wake.py: a finished detached run reaches the live Conductor window at once
(RIMMANDRAKE_WAKE_CONDUCTOR_ON_RUN_END_LOG_ONLY_TODAY).

WHY. A run's end wrote one Conductor log line and nothing else, so its result sat unread while a window was alive and
he was quiet (Gimme Some Slack blind cycle 3, 2026-11-15 4:47 PM PST, unread until the next window's wake). The role
file's hand-armed Monitor on the log covers it only when the window arms one: 1 of the 8 Conductor windows of
2026-11-18 did (measured over their transcripts).

HOW (the doorbell's pattern, doorbell.py, with no Dispatcher in the path):
  * The Conductor window's Stop hook (.claude/hooks/run_end_wake.py, `asyncRewake`) ARMS: <state>/run_end_wake/
    armed.json holds its own pid, the window's pid and session. Then it waits for pending/*.json, takes each by an
    atomic rename into delivered/ (the rename is the consume: two waiters never deliver one twice), prints them and
    exits 2, which wakes the idle window with the text. Only the newest waiter delivers (an older one sees another pid
    in armed.json and leaves); it dies with its window and gives up after MAX_WAIT_S.
  * `detached_helper.finish` calls post() for a run of the Conductor's seat (BENCH): with a live armed window it writes
    ONE pending/<unit>.json carrying the run id, its terminal state and the full result path; with none it writes
    nothing (the Conductor log line is the record; left_open_continue.py and MATURATION_NOW carry a run left open).
  * Nothing is delivered while the window's restart drain stands (seat_restart.handoff_drain): the pending file waits
    for the next window, which arms on its first Stop.
Only the Conductor window arms: AGENT_SEAT BENCH, a session named CONDUCTOR (or its alias), and an interactive
`claude` (session entrypoint `cli`; a detached `claude -p` run reads `sdk-cli`, measured 2026-11-18), so a detached run on
seat BENCH never arms and can never take a delivery meant for him. Arming, the owner check and the consume share one
lock, so a superseded waiter never delivers; a waiter that gives up (MAX_WAIT_S) or outlives its window disarms, so no
run end is posted to a window nobody waits in (after 23 h idle the log line is the record).
"""
import fcntl
import json
import os
import sys
import time
from contextlib import contextmanager

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import doorbell  # noqa: E402

SEAT = "BENCH"
NAMES = ("CONDUCTOR", "AGENT BENCH")      # the window's session name and its pre-rename alias (dispatcher_schedule)
MAX_WAIT_S = 23 * 3600                    # under Claude Code's 86400 s hook timeout, as the doorbell's
POLL_S = 3.0


def wake_dir(root=None):
    return os.path.join(root or doorbell.state_dir(), "run_end_wake")


def armed_path(root=None):
    return os.path.join(wake_dir(root), "armed.json")


@contextmanager
def _locked(root=None):
    os.makedirs(wake_dir(root), exist_ok=True)
    with open(os.path.join(wake_dir(root), "lock"), "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        yield


def _disarm_if_mine(me, root=None):
    with _locked(root):
        rec = doorbell._read_json(armed_path(root)) or {}
        if rec.get("pid") == me:
            try:
                os.remove(armed_path(root))
            except OSError:
                pass


def live_window(root=None, alive=None):
    """-> the armed record when its window is alive, else None (no marker, unreadable, or its window gone)."""
    rec = doorbell._read_json(armed_path(root))
    if not isinstance(rec, dict) or not rec.get("window_pid"):
        return None
    return rec if (alive or doorbell._alive)(int(rec["window_pid"])) else None


def post(unit, state, result_path, item=None, root=None, alive=None, now=None):
    """-> the pending file written for a live Conductor window, or None (no live window: nothing is pending)."""
    if not live_window(root, alive):
        return None
    d = os.path.join(wake_dir(root), "pending")
    path = os.path.join(d, "%s.json" % unit)
    doorbell._write_json_atomic(path, {"unit": unit, "state": state, "result": result_path, "item": item,
                                       "at": now or time.time()})
    return path


def render(recs):
    lines = ["[RimFlow] %d detached run(s) ended (run_end_wake.py): read each result, act on it, tell him if it "
             "matters to him:" % len(recs)]
    for r in recs:
        lines.append("- %s ended %s; item %s; full result: %s" % (r.get("unit"), r.get("state"), r.get("item") or "-",
                                                                  r.get("result") or "UNMEASURED (no path recorded)"))
    return "\n".join(lines)


def take(root=None):
    """-> [pending record] this caller consumed (renamed into delivered/), oldest first. A file another waiter took
    first, or one unreadable, is skipped; an unreadable one stays for a look."""
    d = os.path.join(wake_dir(root), "pending")
    done = os.path.join(wake_dir(root), "delivered")
    try:
        names = sorted(n for n in os.listdir(d) if n.endswith(".json"))
    except OSError:
        return []
    os.makedirs(done, exist_ok=True)
    out = []
    for n in names:
        rec = doorbell._read_json(os.path.join(d, n))
        if not isinstance(rec, dict):
            continue
        try:
            os.replace(os.path.join(d, n), os.path.join(done, n))
        except OSError:
            continue                      # another waiter took it
        out.append(rec)
    return sorted(out, key=lambda r: r.get("at") or 0)


def is_conductor_window(pid):
    """-> True only for the Conductor window: its session file names CONDUCTOR (or the alias) and it is an interactive
    `claude` (entrypoint `cli`, never a `claude -p` run's `sdk-cli`). Unreadable -> False."""
    try:
        import seat_restart as SR
        import session_match as SM
        sf = SR.session_file(pid) or {}
        return (bool(sf.get("name")) and SM.name_matches(sf.get("name"), list(NAMES))
                and sf.get("entrypoint") == "cli")
    except Exception:  # noqa: BLE001 - not provably the Conductor: never arm
        return False


def hold_for(hook):
    """-> a callable, True while nothing may reach the window: this turn said HANDOFF READY (the sibling Stop hook is
    still recording the restart) or its restart drain stands (doorbell.handoff_hold, the same rule). Unreadable: hold."""
    try:
        return doorbell.handoff_hold(SEAT, hook)
    except Exception:  # noqa: BLE001 - never wake into a restart
        return lambda: True


def deliver(me, root=None):
    """Under the lock: -> the pending records this waiter consumed, or None when it is no longer the armed one."""
    with _locked(root):
        rec = doorbell._read_json(armed_path(root)) or {}
        if rec.get("pid") != me:
            return None
        return take(root)


def wait(session_id, window_pid, root=None, me=None, clock=time.time, sleep=time.sleep, max_wait=None,
         alive=None, hold=None):
    """Arm, then wait for pending run ends. -> (2, text) to wake the window, or (0, why) when it leaves quietly."""
    me = me or os.getpid()
    alive = alive or doorbell._alive
    hold = hold or (lambda: False)
    max_wait = MAX_WAIT_S if max_wait is None else max_wait
    with _locked(root):
        doorbell._write_json_atomic(armed_path(root), {"pid": me, "window_pid": window_pid, "session_id": session_id,
                                                       "armed_at": clock()})
    end = clock() + max_wait
    while clock() < end:
        if not alive(window_pid):
            _disarm_if_mine(me, root)
            return 0, "the window is gone"
        if not hold():
            got = deliver(me, root)
            if got is None:
                return 0, "superseded by a newer Stop"
            if got:
                return 2, render(got)
        elif (doorbell._read_json(armed_path(root)) or {}).get("pid") != me:
            return 0, "superseded by a newer Stop"
        sleep(POLL_S)
    _disarm_if_mine(me, root)
    return 0, "gave up after %d s" % max_wait


def hook_main(stdin=None, env=None):
    """The Stop hook: -> exit code (2 wakes the window with the text on stderr)."""
    env = os.environ if env is None else env
    if (env.get("AGENT_SEAT") or "").strip().upper() != SEAT:
        return 0
    try:
        hook = json.load(stdin or sys.stdin)
    except ValueError:
        hook = {}
    anc = doorbell.claude_ancestor()
    if anc is None or not is_conductor_window(anc):
        return 0
    code, text = wait(hook.get("session_id"), anc, hold=hold_for(hook))
    if code == 2:
        sys.stderr.write(text + "\n")
    return code


if __name__ == "__main__":
    try:
        sys.exit(hook_main())
    except Exception:  # noqa: BLE001 - a hook never breaks the window it runs in
        sys.exit(0)
