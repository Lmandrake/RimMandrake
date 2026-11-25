#!/usr/bin/env python3
"""selftest_game_lock_windows_python.py - a Windows python.exe bridge client obeys game a's driver lock.

Promise `a-windows-python-client-obeys-the-lock` of design/specs/2026-11-21-one-game-lock/boundary.md
(RIMMANDRAKE_READ_GAME_LOCK_FRESH_WINDOWS_PYTHON_SLIPPED_PAST_ONCE). Measured 2026-11-21 about 4:10 AM PST: a
python.exe command passed host_guard.crossing while another run held game a, because crossing() returned "allowed"
for every Windows process. Each case runs the REAL python.exe against a throwaway lock (RIMFLOW_DRIVER_LOCK, carried
to Windows by WSLENV /p) held by a real sleeping WSL process; nothing reads or writes a live lock, and no game is
reached (the bridge client is asked only whether it would refuse, never sent a call).

`timed` runs only promise a-windows-python-client-checks-the-lock-in-under-50-ms (selftest_game_lock.py calls it
by that name). Exit 0 all pass; 1 a case failed; 2 UNMEASURED (no python.exe on this machine: the cases cannot run, never a pass).
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

TIMED = r"""
import atexit, json, os, shutil, sys, tempfile, time
sys.path.insert(0, sys.argv[1]); sys.path.insert(0, sys.argv[2])
EV = tempfile.mkdtemp(prefix="st_gl_winpy_ev_")     # a Windows-native dir, as the real log (D:\\ClaudeWork) is: a log on
atexit.register(shutil.rmtree, EV, True)            # the \\wsl.localhost share costs ~30 ms a call in 9p writes alone
os.environ["RIMBRIDGE_EVIDENCE_LOG"] = os.path.join(EV, "evidence.jsonl")
os.environ["RM_BRIDGE_SPLIT"] = "0"
import rimbridge_client as RC
REPLY = {"content": [{"type": "text", "text": json.dumps({"success": True})}]}
RC.RimBridge._request = lambda self, method, params=None: REPLY     # no game: only the client's own steps are timed
b = RC.RimBridge(host="127.0.0.1", port=5175)
tool, params = "jawa/flowworks_excavation_drive", {"x": 10, "z": 10, "deepenLevels": 8}
b._call_one(tool, params, check=False)                              # warm: imports, first identity read
import subprocess
spawns = []
_init = subprocess.Popen.__init__
def _count(self, *a, **k):
    spawns.append(str(a[0] if a else k.get("args"))[:80])
    return _init(self, *a, **k)
subprocess.Popen.__init__ = _count                                  # every process a timed call starts is counted
n = int(sys.argv[3]); t0 = time.perf_counter()
for _ in range(n):
    b._call_one(tool, params, check=False)
ms = (time.perf_counter() - t0) / n * 1000
subprocess.Popen.__init__ = _init
print(json.dumps({"os": os.name, "mutating": not b.looks_read_only(tool, params), "n": n, "ms": ms,
                  "spawns": len(spawns), "spawned": spawns[:3]}))
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


def interop_down(text):
    """WSL's own words for "no Windows process was started", with no line from the probe."""
    return "UtilAcceptVsock" in text and "{" not in text


def probe(lock, timed=0, **extra):
    env = {k: v for k, v in os.environ.items() if k not in ("RM_HOST_GUARD_GEN", "RM_BRIDGE_CROSS_WHY",
                                                              "RIMFLOW_LEDGER", "RM_GAME_INSTANCE", "RM_DRIVER_PID")}
    env.update(RIMFLOW_DRIVER_LOCK=lock, **extra)
    names = ["RIMFLOW_DRIVER_LOCK/p"] + list(extra)
    env["WSLENV"] = ":".join([x for x in (os.environ.get("WSLENV") or "").split(":")
                              if x and x.split("/")[0] not in [n.split("/")[0] for n in names]] + names)
    script = os.path.join(TMP, "timed.py" if timed else "probe.py")
    with open(script, "w") as fh:
        fh.write(TIMED if timed else PROBE)
    for n in range(3):
        r = subprocess.run(["python.exe", win(script), win(HERE), win(os.path.join(CLONE, "src", "RimMandrake", "Utils"))]
                           + ([str(timed)] if timed else []),
                           capture_output=True, text=True, timeout=120, env=env, cwd=CLONE)
        if not interop_down(r.stdout + r.stderr):
            break
        time.sleep(5)
    else:       # python.exe never ran: could not look, which is no verdict on the lock (2026-11-23, load 60 on the machine)
        print("UNMEASURED: WSL could not start a Windows process (3 tries): %s" % (r.stdout + r.stderr).strip()[-160:])
        sys.exit(2)
    if "RmDataRootUnset" in r.stdout + r.stderr:    # the machine's environment, not the lock: no verdict (SteveDesktop)
        print("UNMEASURED: this machine's Windows python.exe has no RM_DATA_ROOT or LODESTAR_ROOT (rmpaths.RmDataRootUnset)"
              "; set one in the Windows user environment to run the Windows-client cases")
        sys.exit(2)
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


def main_timed():
    """`timed`: promise a-windows-python-client-checks-the-lock-in-under-50-ms only."""
    if not shutil.which("python.exe"):
        print("UNMEASURED: no python.exe on this machine; the timed case cannot run")
        return 2
    holder = sleeper()

    # a-windows-python-client-checks-the-lock-in-under-50-ms: the holder's own clone, no inherited take (a run that
    # took the bridge with `rimflow bridge take`, then drives with python.exe). Measured 2026-11-21: 233 ms of every
    # 255 ms mutating call went to a powershell.exe spawn reading this process's own start time in
    # driver_lock.my_identity (host_guard._reentrant), so a 2,000-cell dig took 11 min. 50 ms a call is the item's bar.
    r = probe(plant("timed", holder.pid, CLONE), timed=20)
    # The danger is a process spawned per call (233 ms each); its count does not move with the machine's load, so it
    # decides every run. The wall bound measures the machine as well: inside ./publish's side-by-side door tests it read
    # 109-130 ms against 36-43 ms quiet (2026-11-21, the same code), and refused publishes that touched no lock code.
    # So when the load average passes half the cores, a wall reading over the bound is printed UNMEASURED, not red.
    check(r.get("os") == "nt" and r.get("mutating") is True and r.get("spawns") == 0,
          "a mutating call starts no process (%s spawned over %s calls: %s)" % (r.get("spawns"), r.get("n"),
                                                                                r.get("spawned")), r)
    ms = r.get("ms")
    load, cores = os.getloadavg()[0], os.cpu_count() or 2
    if ms is not None and ms >= 50 and load > cores / 2:
        print("     UNMEASURED: the 50 ms wall bound, worst mean %.1f ms of %s calls at load %.1f on %d cores; the "
              "spawn count decides" % (ms, r.get("n"), load, cores))
    else:
        check(ms is not None and ms < 50, "a mutating call's client-side steps take under 50 ms under a live WSL "
              "holder (worst mean %s ms of %s calls, limit 50, load %.1f on %d cores)" % (
                  None if ms is None else round(ms, 1), r.get("n"), load, cores), r)


    print("\n%s: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main_timed() if sys.argv[1:] == ["timed"] else main())
