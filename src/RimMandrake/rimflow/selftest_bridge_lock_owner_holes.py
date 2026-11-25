#!/usr/bin/env python3
"""RIMMANDRAKE_HARDEN_BRIDGE_LOCK_OWNER_HOLES: the holes the GPT bridge review (2026-11-15) found in the lock, each
staged on throwaway state only (temp ledger, lock, fence, transcripts, stamp). Every case below FAILED on
the base commit ba67ffeb5d except those marked control.

  fence    p2.F1: a live holder's fence is never broken by age; a dead holder's is broken at once; an uninspectable one
           after FENCE_STALE_S; a fence re-made between the stale read and the rename is put back
  owner    p2.F3: on Archmagi a script take or forced release of his lock, past its heartbeat, still runs his rule
           (his chat 5 min ago, an UNMEASURED stamp) and ignores a free-string owner_cleared; elsewhere the heartbeat
           rule passes it, said on stderr
  fenced   p2.F4: a forced release judges the OWNER rule on the lock inside the fence, not on an earlier read
  release  p2.F10: a guard or driver release that failed exits nonzero and writes no `released` event
"""
import contextlib
import io
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import types

T = tempfile.mkdtemp(prefix="rf_lockholes_")
for k in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID", "CLAUDECODE", "RIMFLOW_RAN_BY", "RIMFLOW_BRIDGE_SEAT",
          "RM_ROLE_UNIT", "RM_HOST", "RM_GAME_INSTANCE", "RM_HOST_GUARD_GEN"):
    os.environ.pop(k, None)
os.makedirs(os.path.join(T, "items"))
os.makedirs(os.path.join(T, "chat"))
open(os.path.join(T, "events.jsonl"), "w").close()
os.environ.update(RIMFLOW_LEDGER=os.path.join(T, "events.jsonl"), RIMFLOW_ITEMS=os.path.join(T, "items"),
                  RIMFLOW_SEAT="BENCH",
                  RIMFLOW_OWNER_CHAT_DIRS=os.path.join(T, "chat"), RIMFLOW_OWNER_TERMINAL="0",
                  RIMFLOW_OWNER_ACT_STAMP=os.path.join(T, "OWNER_LAST_ACT.json"),
                  RIMFLOW_DISPATCH_LOCK=os.path.join(T, "dispatch.lock"),
                  RIMFLOW_BRIDGE_LOCK=os.path.join(T, "bridge.lock"),
                  RIMFLOW_DRIVER_LOCK=os.path.join(T, "DRIVER_LOCK.json"))

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from rimflow import cli, driver_lock as D, host_guard as H, model  # noqa: E402
cli._bind_paths()      # RIMFLOW_LEDGER binds only in cli.main(); without this the in-process calls wrote the real ledger

FAILS = []
LOCK = os.environ["RIMFLOW_DRIVER_LOCK"]
OP = LOCK + ".op"
CHAT = os.path.join(T, "chat")
STAMP = os.environ["RIMFLOW_OWNER_ACT_STAMP"]


def check(ok, msg, detail=""):
    print(("ok    " if ok else "FAIL  ") + msg + ("  [%s]" % str(detail)[:220] if detail and not ok else ""))
    if not ok:
        FAILS.append(msg)


def iso(age_s):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - age_s))


def clean():
    for p in (LOCK, OP, LOCK + ".gen"):
        if os.path.isdir(p):
            shutil.rmtree(p)
        elif os.path.exists(p):
            os.remove(p)
    for f in os.listdir(CHAT):
        os.remove(os.path.join(CHAT, f))
    if os.path.isdir(STAMP):
        shutil.rmtree(STAMP)
    elif os.path.exists(STAMP):
        os.remove(STAMP)


def age(path, s):
    t = time.time() - s
    os.utime(path, (t, t))


def gone_identity():
    p = subprocess.Popen(["true"])
    p.wait()
    return {"pid": p.pid, "start": 1.0, "boot_id": D.current_boot_id(), "platform": "wsl", "host": socket.gethostname()}


def live_identity(proc):
    return {"pid": proc.pid, "start": D._proc_start(proc.pid), "boot_id": D.current_boot_id(), "platform": "wsl",
            "host": socket.gethostname()}


def write_lock(seat, ident, hb_age):
    with open(LOCK, "w") as f:
        json.dump({"seat": seat, "purpose": "playing", "identity": ident, "acquired": iso(hb_age),
                   "heartbeat": iso(hb_age), "generation": 3}, f)


def chat_at(age_s):
    rec = {"type": "user", "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime(time.time() - age_s)),
           "origin": {"kind": "human"}, "promptSource": "typed", "turnOrigin": "human",
           "message": {"role": "user", "content": "hello"}}
    with open(os.path.join(CHAT, "s.jsonl"), "w") as f:
        f.write(json.dumps(rec) + "\n")


def test_fence(sleeper):
    me = D.my_identity()
    wait = D.FENCE_WAIT_S
    D.FENCE_WAIT_S = 0.5
    try:
        clean()
        D.acquire(LOCK, "BENCH", "x", me)
        live = json.dumps(dict(live_identity(sleeper), t="1.0"))
        with open(OP, "w") as f:
            f.write(live)
        age(OP, 100)
        r = D.release(LOCK, "BENCH", me)
        check(not r["ok"] and "contended" in r["why"] and os.path.exists(LOCK) and open(OP).read() == live,
              "fence: a LIVE holder's fence 100 s old is not broken by age (release waits, then refuses)", r)
        with open(OP, "w") as f:
            f.write(json.dumps(dict(gone_identity(), t="1.0")))
        r = D.release(LOCK, "BENCH", me)
        check(r["ok"] and not os.path.exists(LOCK) and not os.path.exists(OP),
              "fence: a DEAD holder's fresh fence is broken at once", r)
        D.acquire(LOCK, "BENCH", "x", me)
        with open(OP, "w") as f:
            f.write("4242 otherhost 1.0")                  # a legacy fence: its holder cannot be inspected
        age(OP, 30)
        r = D.release(LOCK, "BENCH", me)
        check(not r["ok"] and os.path.exists(LOCK), "fence: an uninspectable fence 30 s old is still waited on", r)
        age(OP, D.FENCE_STALE_S + 5)
        r = D.release(LOCK, "BENCH", me)
        check(r["ok"] and not os.path.exists(OP), "control: an uninspectable fence past FENCE_STALE_S is broken", r)
        # the stale fence is replaced by a fresh live one between its read and the rename: the fresh one is put back
        D.acquire(LOCK, "BENCH", "x", me)
        with open(OP, "w") as f:
            f.write("4242 otherhost 1.0")
        age(OP, 1000)
        real_rename = os.rename

        def racing_rename(src, dst, _fired=[]):
            if src == OP and not _fired:
                _fired.append(1)
                with open(OP, "w") as f:
                    f.write(live)
            return real_rename(src, dst)
        os.rename = racing_rename
        try:
            r = D.release(LOCK, "BENCH", me)
        finally:
            os.rename = real_rename
        check(not r["ok"] and os.path.exists(OP) and open(OP).read() == live and os.path.exists(LOCK),
              "fence: a fence re-made between the stale read and the rename is put back, never robbed", r)
    finally:
        D.FENCE_WAIT_S = wait


def take(host, **kw):
    os.environ["RM_HOST"] = host
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err):
            r = H.acquire("RUNNER", "job", path=LOCK, identity=dict(gone_identity(), pid=7, host="elsewhere"), **kw)
    finally:
        os.environ.pop("RM_HOST", None)
    return r, err.getvalue()


def test_owner():
    clean()
    write_lock("OWNER", gone_identity(), 3000)          # his take's process exited; heartbeat 50 min old
    chat_at(300)
    r, _ = take("archmagi")
    check(not r["ok"] and "chat prompt" in r["why"] and D._read(LOCK)[0]["seat"] == "OWNER",
          "owner: Archmagi script take of his 50-min lock refuses while he chatted 5 min ago", r)
    r, _ = take("archmagi", force="cut", owner_cleared="the owner has not interacted (free string)")
    check(not r["ok"] and D._read(LOCK)[0]["seat"] == "OWNER",
          "owner: on Archmagi a free-string owner_cleared + --force does not pass his rule", r)
    os.environ["RM_HOST"] = "archmagi"
    try:
        rr = H.release("RUNNER", force="cut", identity=dict(gone_identity(), pid=7, host="elsewhere"), path=LOCK)
    finally:
        os.environ.pop("RM_HOST", None)
    check(not rr["ok"] and D._read(LOCK)[0]["seat"] == "OWNER",
          "owner: Archmagi forced release of his 50-min lock refuses while he chatted 5 min ago", rr)
    clean()
    write_lock("OWNER", gone_identity(), 3000)
    os.makedirs(STAMP)                                   # an unreadable ./bridge stamp: UNMEASURED
    r, _ = take("archmagi")
    check(not r["ok"] and "UNMEASURED" in r["why"], "owner: an UNMEASURED source refuses the take", r)
    clean()
    write_lock("OWNER", gone_identity(), 3000)
    r, _ = take("archmagi")
    check(r["ok"], "control: everything of his 50 min old -> the script takes it", r)
    clean()
    write_lock("OWNER", gone_identity(), 3000)
    chat_at(300)
    r, err = take("stevedesktop")
    check(r["ok"] and "UNMEASURED on this machine" in err,
          "owner: off Archmagi the heartbeat rule passes his lock, and says his interactions are UNMEASURED", (r, err))


def test_fenced_release():
    clean()
    os.environ["RM_HOST"] = "stevedesktop"
    write_lock("OWNER", gone_identity(), 60)            # on disk: his fresh hold
    real_read = D._read
    calls = []

    def stale_read(p):
        calls.append(p)
        if len(calls) == 1:                              # host_guard's own early read saw an older seat lock
            return {"seat": "RUNNER", "identity": {"pid": 1}, "heartbeat": iso(99999)}, None
        return real_read(p)
    D._read = stale_read
    try:
        r = H.release("BENCH", force="cut", identity=dict(gone_identity(), pid=8, host="elsewhere"), path=LOCK)
    except TypeError as e:
        r = {"ok": None, "why": "crash %s" % e}
    finally:
        D._read = real_read
        os.environ.pop("RM_HOST", None)
    cur = real_read(LOCK)[0]
    check(not r["ok"] and cur and cur["seat"] == "OWNER",
          "fenced: a forced release judges his rule on the lock inside the fence, not on an earlier read", r)


def released():
    return [e for e in model.read() if e.get("event") == "bridge" and e.get("state") == "released"]


def run(fn):
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            rc = fn()
    except SystemExit as e:
        rc = e.code
    return rc, out.getvalue()


def test_release_exit():
    clean()
    real_guard, real_drv, real_read = cli._guard_call, cli._driver_release, cli.lock_reading
    args = types.SimpleNamespace(action="release", purpose=None, force=None)
    try:
        cli.lock_reading = lambda hk=None: None      # stevedesktop as ANOTHER machine's game, on any host (on SteveDesktop
        #                                              it is local, and its local test lock answered without the guard)
        n0 = len(released())
        cli._guard_call = lambda hk, a: (255, "ssh to stevedesktop timed out after 60 s")
        rc, out = run(lambda: cli._bridge_other_host_locked(args, "BENCH", cli.load()[1], "stevedesktop"))
        check(rc not in (0, None) and "NOT released" in out and len(released()) == n0,
              "release: an unreachable guard exits nonzero and writes no `released` event", (rc, out))
        cli._guard_call = lambda hk, a: (75, "REFUSED driver lock is held by RUNNER (wsl pid 9), not this process")
        rc, out = run(lambda: cli._bridge_other_host_locked(args, "BENCH", cli.load()[1], "stevedesktop"))
        check(rc == 0 and len(released()) == n0 + 1,
              "control: a guard held by another process (never ours) still records the ledger release", (rc, out))
        n0 = len(released())
        cli._driver_release = lambda seat, force=None: {"ok": False, "why": "driver lock contended: fence held"}
        rc, out = run(lambda: cli._bridge_release_write("BENCH", cli.load()[1], "BENCH"))
        check(rc not in (0, None) and "NOT released" in out and len(released()) == n0,
              "release: an Archmagi driver lock left held (contended) exits nonzero, no `released` event", (rc, out))
        cli._driver_release = lambda seat, force=None: {"ok": False, "why": "driver lock is held by FOUNDRY (wsl pid "
                                                         "9), not this process; only the holder releases it"}
        rc, out = run(lambda: cli._bridge_release_write("BENCH", cli.load()[1], "BENCH"))
        check(rc == 0 and len(released()) == n0 + 1, "control: a driver lock that was never ours: released, exit 0",
              (rc, out))
    finally:
        cli._guard_call, cli._driver_release, cli.lock_reading = real_guard, real_drv, real_read


def test_take_exit():
    """A refused take on another machine's game says what its guard said: 75 (held) passes through as held; an
    unreachable guard is never reported as a held lock (A1 live check of BRIDGE_LOCK_HARDEN_ALIVE_MEANS_A_PID, 2026-11-25:
    the held refusal exited 2, the could-not-look code)."""
    clean()
    real_guard, real_read = cli._guard_call, cli.lock_reading
    args = types.SimpleNamespace(action="take", purpose="selftest take", force=None, idle_ok=False, flyer=False)
    try:
        cli.lock_reading = lambda hk=None: None      # another machine's game, as in test_release_exit
        cli._guard_call = lambda hk, a: (75, "REFUSED driver lock held by BENCH (wsl pid 9), holder process pid 9 alive")
        rc, out = run(lambda: cli._bridge_other_host_locked(args, "BENCH", cli.load()[1], "stevedesktop"))
        check(rc == 75 and "driver lock is held" in out,
              "take: a guard that says held exits 75 and names the held driver lock", (rc, out))
        cli._guard_call = lambda hk, a: (255, "ssh to stevedesktop timed out after 60 s")
        rc, out = run(lambda: cli._bridge_other_host_locked(args, "BENCH", cli.load()[1], "stevedesktop"))
        check(rc not in (0, 75, None) and "is held" not in out and "could not" in out,
              "take: an unreachable guard exits nonzero, not 75, and does not call the lock held", (rc, out))
    finally:
        cli._guard_call, cli.lock_reading = real_guard, real_read


def main():
    sleeper = subprocess.Popen(["sleep", "120"])
    try:
        for t in (test_fence, test_owner, test_fenced_release, test_release_exit, test_take_exit):
            try:
                t(sleeper) if t is test_fence else t()
            except Exception as e:                       # a crash is a failure of that group, never a pass
                check(False, "%s crashed: %r" % (t.__name__, e))
    finally:
        sleeper.kill()
        shutil.rmtree(T, ignore_errors=True)
    print("%d failed" % len(FAILS) if FAILS else "all passed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
