#!/usr/bin/env python3
"""selftest_game_lock_windows_python.py - a Windows python.exe bridge client obeys game a's driver lock.

Promise `a-windows-python-client-obeys-the-lock` of design/specs/2026-11-21-one-game-lock/boundary.md
(RIMMANDRAKE_READ_GAME_LOCK_FRESH_WINDOWS_PYTHON_SLIPPED_PAST_ONCE). Measured 2026-11-21 about 4:10 AM PST: a
python.exe command passed host_guard.crossing while another run held game a, because crossing() returned "allowed"
for every Windows process. Each case runs the REAL python.exe against a throwaway lock (RIMFLOW_DRIVER_LOCK, carried
to Windows by WSLENV /p) held by a real sleeping WSL process; nothing reads or writes a live lock, and no game is
reached (the bridge client is asked only whether it would refuse, never sent a call).

Exit 0 all pass; 1 a case failed; 2 UNMEASURED (no python.exe on this machine: the cases cannot run, never a pass).
"""
import atexit
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
CLONE = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import driver_lock as D  # noqa: E402

TMP = tempfile.mkdtemp(prefix="st_gl_winpy_", dir="/tmp")
atexit.register(shutil.rmtree, TMP, True)
FAILS = []
SLEEPERS = []
atexit.register(lambda: [p.kill() for p in SLEEPERS])

PROBE = r"""
import json, os, sys
sys.path.insert(0, sys.argv[1]); sys.path.insert(0, sys.argv[2])
import host_guard, driver_lock, rimbridge_client
lk = host_guard.lock_path()
cur, _ = driver_lock._read(lk)
print(json.dumps({"os": os.name, "lock": lk, "crossing": host_guard.crossing(),
                  "new_run": host_guard.crossing(new_run=True),
                  "client": rimbridge_client._driver_crossing("127.0.0.1"),
                  "alive": list(driver_lock._alive(cur)) if cur else None}))
"""


def check(cond, msg, detail=""):
    print(("ok   " if cond else "FAIL ") + msg + ("" if cond else "  %s" % (detail,))[:700])
    if not cond:
        FAILS.append(msg)


def win(p):
    return subprocess.run(["wslpath", "-w", p], capture_output=True, text=True, check=True).stdout.strip()


def sleeper():
    p = subprocess.Popen(["sleep", "300"])
    SLEEPERS.append(p)
    time.sleep(0.05)
    return p


def ident(pid):
    return {"pid": pid, "start": D._proc_start(pid), "boot_id": D.current_boot_id(), "platform": "wsl",
            "host": __import__("socket").gethostname()}


def plant(name, holder_pid, clone, heartbeat_age_s=0, gen=7):
    path = os.path.join(TMP, name, "DRIVER_LOCK.json")
    os.makedirs(os.path.dirname(path))
    hb = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - heartbeat_age_s))
    body = {"seat": "BENCH", "purpose": "another run's visit", "identity": ident(holder_pid), "acquired": hb,
            "heartbeat": hb, "generation": gen, "clone": clone, "role_unit": "rm-detached-other"}
    with open(path, "w") as fh:
        json.dump(body, fh)
    return path


def probe(lock, **extra):
    env = {k: v for k, v in os.environ.items() if k not in ("RM_HOST_GUARD_GEN", "RM_BRIDGE_CROSS_WHY",
                                                              "RIMFLOW_LEDGER", "RM_GAME_INSTANCE", "RM_DRIVER_PID")}
    env.update(RIMFLOW_DRIVER_LOCK=lock, **extra)
    names = ["RIMFLOW_DRIVER_LOCK/p"] + list(extra)
    env["WSLENV"] = ":".join([x for x in (os.environ.get("WSLENV") or "").split(":")
                              if x and x.split("/")[0] not in [n.split("/")[0] for n in names]] + names)
    script = os.path.join(TMP, "probe.py")
    with open(script, "w") as fh:
        fh.write(PROBE)
    r = subprocess.run(["python.exe", win(script), win(HERE), win(os.path.join(CLONE, "src", "RimMandrake", "Utils"))],
                       capture_output=True, text=True, timeout=120, env=env, cwd=CLONE)
    try:
        return json.loads(r.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return {"error": (r.stdout + r.stderr)[-600:]}


def main():
    if not shutil.which("python.exe"):
        print("UNMEASURED: no python.exe on this machine; the Windows-client cases cannot run")
        return 2
    holder = sleeper()
    other = "/home/mandrake/rm/relentless/clones/SOME_OTHER_RUN.det"

    # 1. the measured case: another clone's live run holds the game, its heartbeat fresh
    r = probe(plant("other_fresh", holder.pid, other))
    check(r.get("os") == "nt", "the probe ran in Windows python", r)
    check(bool(r.get("crossing")), "python.exe from another clone is refused by host_guard.crossing", r)
    check(bool(r.get("client")), "the bridge client's mutating-call guard refuses it too", r)

    # 2. the holder has held for 50 min with no heartbeat since: still alive, so still refused (not heartbeat-judged)
    r = probe(plant("other_old", holder.pid, other, heartbeat_age_s=50 * 60))
    check(bool(r.get("crossing")) and (r.get("alive") or [None])[0] is True,
          "a live WSL holder with a 50-min-old heartbeat reads alive from Windows and still refuses", r)

    # 3. the holder process is gone: the game is free, the client passes
    dead = sleeper()
    lk = plant("dead", dead.pid, other)
    dead.kill()
    dead.wait()
    r = probe(lk)
    check(r.get("crossing") is None and (r.get("alive") or [None])[0] is False,
          "a gone WSL holder reads gone from Windows at once, and passes", r)

    # 4. a child of the holder's take (game_lock.py run exports RM_HOST_GUARD_GEN through WSLENV) passes
    r = probe(plant("inherited", holder.pid, other, gen=41), RM_HOST_GUARD_GEN="41")
    check(r.get("crossing") is None, "python.exe that inherited the take (RM_HOST_GUARD_GEN) passes", r)
    check(bool(r.get("new_run")), "...but a NEW run from it is still refused", r)

    # 5. the holder's own clone (a window that took the bridge, then runs python.exe from its shell) passes
    r = probe(plant("same_clone", holder.pid, CLONE))
    check(r.get("crossing") is None, "python.exe running the holder's own clone's code passes", r)

    # 6. a deliberate crossing still crosses
    r = probe(plant("crossed", holder.pid, other), RM_BRIDGE_CROSS_WHY="selftest")
    check(r.get("crossing") is not None, "host_guard.crossing itself still names the holder under RM_BRIDGE_CROSS_WHY "
          "(the client is what honours it)", r)

    print("\n%s: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
