#!/usr/bin/env python3
"""doorbell.py — the channel the Dispatcher uses to wake an IDLE Claude Code window (RimFlow v3.0).

Design: `design/RimMandrake/rimflow_v3_2026-10-26.md` §2/§6 item 1; item RIMFLOW_V3_BUILD_DISPATCHER_FIRST.

HOW A WINDOW IS WOKEN
=====================
Claude Code (2.1.3xx) runs a hook marked `"asyncRewake": true` in the BACKGROUND and, when that hook exits with
code 2, wakes the model with the hook's output as a system reminder — even though the window is idle at its prompt.
This script is that hook, registered on `Stop` (the moment a window finishes a turn and goes idle):

    {"hooks": {"Stop": [{"hooks": [{"type": "command", "asyncRewake": true, "timeout": 86400,
        "command": "python3 \"${CLAUDE_PROJECT_DIR:-.}/src/RimMandrake/rimflow/doorbell.py\""}]}]}}

On every Stop it ARMS: writes `armed/<SEAT>.json` (its pid + session id), then waits for `inbox/<SEAT>.json`. The
Dispatcher RINGS by writing that inbox file. The doorbell renames it into `consumed/` (the consume is the Dispatcher's
first proof the message was delivered), prints the message and exits 2 — the window wakes and reads it.

Rules:
  * Not a seat (no AGENT_SEAT / RIMFLOW_SEAT in the environment) -> exit 0 at once. Owner-only windows never arm.
  * ONE doorbell per seat: a newer Stop re-arms with its own pid; an older doorbell that sees another pid in the
    armed file exits 0 quietly (it was superseded, not rung).
  * Dies with its window: it finds its Claude Code ancestor at start and exits 0 the moment that process is gone
    (measured 2026-10-26: killing a session left its doorbell running, re-parented to /init, for 23 h).
  * Gives up (exit 0, disarms) after RM_DOORBELL_MAX_WAIT_S (default 23 h), before Claude Code's hook timeout.
  * Rings that the window started a turn in the meantime are still delivered: the Dispatcher only rings an idle
    window, and a message arriving mid-turn is read at the next opportunity instead of lost.

Never names a host or account. State dir: RM_DISPATCHER_STATE (default under D:\\ClaudeWork, see dispatcher.py).
"""
import json
import os
import sys
import time

DEFAULT_STATE = "/mnt/d/ClaudeWork/rimmandrake/dispatcher"
POLL_S = 3.0


def state_dir():
    return os.environ.get("RM_DISPATCHER_STATE", DEFAULT_STATE)


def seat_name():
    s = (os.environ.get("AGENT_SEAT") or os.environ.get("RIMFLOW_SEAT") or "").strip().upper()
    return s or None


def _write_json_atomic(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = "%s.tmp.%d" % (path, os.getpid())
    with open(tmp, "w") as f:
        json.dump(obj, f)
    os.replace(tmp, path)


def _read_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def armed_path(seat, root=None):
    return os.path.join(root or state_dir(), "armed", "%s.json" % seat)


def inbox_path(seat, root=None):
    return os.path.join(root or state_dir(), "inbox", "%s.json" % seat)


def arm(seat, session_id, root=None, pid=None, owner_pid=None):
    rec = {"seat": seat, "pid": pid or os.getpid(), "session_id": session_id, "owner_pid": owner_pid,
           "armed_at": time.time()}
    _write_json_atomic(armed_path(seat, root), rec)
    return rec


def take_ring(seat, root=None):
    """If a ring is waiting: move it to consumed/ (atomic, so exactly one doorbell wins) and return its record."""
    src = inbox_path(seat, root)
    if not os.path.exists(src):
        return None
    dst_dir = os.path.join(root or state_dir(), "consumed")
    os.makedirs(dst_dir, exist_ok=True)
    dst = os.path.join(dst_dir, "%s-%d-%d.json" % (seat, int(time.time() * 1000), os.getpid()))
    try:
        os.rename(src, dst)
    except OSError:
        return None          # another doorbell (or the dispatcher withdrawing it) got there first
    rec = _read_json(dst) or {}
    rec["consumed_at"] = time.time()
    rec["consumed_by_pid"] = os.getpid()
    _write_json_atomic(dst, rec)
    return rec


def render(rec):
    return (rec.get("message") or "The Dispatcher rang with no message.").strip()


def claude_ancestor(pid=None):
    """-> pid of the nearest ancestor process named claude (the window that ran this hook), or None."""
    pid = pid or os.getpid()
    for _ in range(12):
        try:
            with open("/proc/%d/stat" % pid) as f:
                ppid = int(f.read().rsplit(")", 1)[1].split()[1])
        except (OSError, ValueError, IndexError):
            return None
        if ppid <= 1:
            return None
        try:
            with open("/proc/%d/cmdline" % ppid, "rb") as f:
                argv0 = f.read().split(b"\0")[0].decode("utf-8", "replace")
            with open("/proc/%d/comm" % ppid) as f:
                comm = f.read().strip()
        except OSError:
            return None
        if os.path.basename(argv0) == "claude" or comm == "claude" or "/claude/versions/" in argv0:
            return ppid
        pid = ppid
    return None


def _alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def wait(seat, session_id, root=None, max_wait=None, poll=POLL_S, clock=time.time, sleep=time.sleep,
         owner_pid=None):
    """Arm, then wait. -> (exit_code, text). 2 = rung (text is the message), 0 = superseded/gave up/orphaned.
    `owner_pid`: the window's process; when it is gone the doorbell exits instead of waiting out its day."""
    me = arm(seat, session_id, root, owner_pid=owner_pid)
    deadline = clock() + (max_wait if max_wait is not None
                          else float(os.environ.get("RM_DOORBELL_MAX_WAIT_S", 23 * 3600)))
    while True:
        rec = take_ring(seat, root)
        if rec is not None:
            _disarm_if_mine(seat, me["pid"], root)
            return 2, render(rec)
        cur = _read_json(armed_path(seat, root)) or {}
        if cur.get("pid") != me["pid"]:
            return 0, "superseded by doorbell pid %s" % cur.get("pid")
        if owner_pid and not _alive(owner_pid):
            _disarm_if_mine(seat, me["pid"], root)
            return 0, "window process %d is gone" % owner_pid
        if clock() >= deadline:
            _disarm_if_mine(seat, me["pid"], root)
            return 0, "gave up waiting"
        sleep(poll)


def _disarm_if_mine(seat, pid, root=None):
    p = armed_path(seat, root)
    cur = _read_json(p) or {}
    if cur.get("pid") == pid:
        try:
            os.remove(p)
        except OSError:
            pass


def main():
    seat = seat_name()
    if not seat:
        return 0
    try:
        hook = json.load(sys.stdin)
    except ValueError:
        hook = {}
    code, text = wait(seat, hook.get("session_id"), owner_pid=claude_ancestor())
    if code == 2:
        sys.stderr.write(text + "\n")
    return code


if __name__ == "__main__":
    sys.exit(main())
