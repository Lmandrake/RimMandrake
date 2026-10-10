"""selftest_driver_lock.py - the driver lock is exclusive, keyed on process identity, and loud when unreadable
(BRIDGE_LOCK_HARDEN_ALIVE_MEANS_A_PID). Written failing-first. Temp lock path; liveness faked per case.
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import driver_lock as D  # noqa: E402


def case(name, cond, detail=""):
    print("%-4s %s %s" % ("ok" if cond else "FAIL", name, detail))
    return bool(cond)


def ident(pid, start=100.0, boot="boot-1", platform="wsl"):
    return {"pid": pid, "start": start, "boot_id": boot, "platform": platform, "host": "archmagi"}


def main():
    good = []
    path = os.path.join(tempfile.mkdtemp(), "DRIVER_LOCK.json")
    alive = {}
    D.process_alive = lambda i: alive.get((i.get("pid"), i.get("start")), False)
    real_boot = D.current_boot_id
    D.current_boot_id = lambda: "boot-1"

    A, B = ident(10), ident(20)
    alive[(10, 100.0)] = True
    alive[(20, 100.0)] = True
    r = D.acquire(path, "FOUNDRY", "probe", A)
    good.append(case("free lock is acquired", r["ok"] and r["generation"] == 1, r))
    r = D.acquire(path, "BENCH", "other", B)
    good.append(case("a live holder of another identity refuses the take", not r["ok"] and "alive" in r["why"], r))
    r = D.acquire(path, "FOUNDRY", "same seat other window", B)
    good.append(case("same SEAT, different process is still refused (two BENCH windows)", not r["ok"], r))
    r = D.acquire(path, "FOUNDRY", "again", A)
    good.append(case("re-take by the same process is idempotent", r["ok"] and r["generation"] == 1, r))

    alive[(10, 100.0)] = False
    r = D.acquire(path, "BENCH", "after death", B)
    good.append(case("a dead holder's lock is taken over, generation bumped", r["ok"] and r["generation"] == 2 and
                     r.get("broke"), r))

    # pid reuse: same pid, different start time is a different process
    alive[(20, 100.0)] = False
    alive[(20, 555.0)] = True
    r = D.acquire(path, "FOUNDRY", "pid reuse", ident(20, start=555.0))
    good.append(case("pid reused with a new start time does not inherit the lock as 'same process'",
                     r["ok"] and r["generation"] == 3 and r.get("broke"), r))

    r = D.release(path, "BENCH", B)
    good.append(case("release by a non-holder is refused", not r["ok"], r))
    r = D.release(path, "FOUNDRY", ident(20, start=555.0))
    good.append(case("release by the holder frees it", r["ok"] and not os.path.exists(path), r))

    with open(path, "w") as fh:
        fh.write("{not json")
    os.utime(path, (1, 1))
    r = D.acquire(path, "FOUNDRY", "x", A)
    good.append(case("an unreadable lock is an explicit failure, never 'free'", not r["ok"] and "UNREADABLE" in r["why"], r))
    r = D.acquire(path, "FOUNDRY", "x", A, force="owner said break it")
    good.append(case("force breaks an unreadable lock and records why", r["ok"] and r.get("broke"), r))
    with open(path) as fh:
        good.append(case("forced take records the override", "owner said" in json.load(fh).get("override", "")))

    # a holder on another boot (machine restarted) is dead without asking the process table
    D.process_alive = lambda i: True
    with open(path, "w") as fh:
        json.dump({"seat": "BENCH", "identity": ident(30, boot="boot-OLD"), "generation": 9, "acquired": "x",
                   "heartbeat": "x"}, fh)
    r = D.acquire(path, "FOUNDRY", "after reboot", A)
    good.append(case("holder from a previous boot is dead", r["ok"] and r["generation"] == 10, r))

    # O_EXCL: two acquirers see one winner
    os.remove(path)
    D.process_alive = lambda i: True
    r1 = D.acquire(path, "FOUNDRY", "a", A)
    r2 = D.acquire(path, "BENCH", "b", B)
    good.append(case("exactly one of two acquirers wins", r1["ok"] != r2["ok"]))

    D.current_boot_id = real_boot
    good.append(case("owner identity finds a real process", D.my_identity()["pid"] > 1, D.my_identity()))

    good += cli_cases()
    print("%d/%d" % (sum(good), len(good)))
    return 0 if all(good) else 1


def cli_cases():
    """rimflow bridge take/release consult the driver lock: two windows of the SAME seat are told apart."""
    import importlib
    import shutil
    import subprocess
    importlib.reload(D)
    here = os.path.dirname(os.path.abspath(__file__))
    cli = os.path.join(here, "cli.py")
    tmp = tempfile.mkdtemp(prefix="rf_dlock_")
    os.makedirs(os.path.join(tmp, "items"))
    a = subprocess.Popen(["sleep", "120"])
    b = subprocess.Popen(["sleep", "120"])
    base = {k: v for k, v in os.environ.items() if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID")}
    base.update(RIMFLOW_LEDGER=os.path.join(tmp, "events.jsonl"), RIMFLOW_ITEMS=os.path.join(tmp, "items"),
                RIMFLOW_SHARED_BRIDGE=os.path.join(tmp, "shared.json"), RIMFLOW_PROBE="no-reading",
                RIMFLOW_DRIVER_LOCK=os.path.join(tmp, "DRIVER_LOCK.json"))

    def rf(seat, pid, *args):
        e = dict(base, RIMFLOW_SEAT=seat, RM_DRIVER_PID=str(pid))
        return subprocess.run([sys.executable, cli] + list(args), env=e, capture_output=True, text=True)
    good = []
    try:
        r = rf("BENCH", a.pid, "bridge", "take", "--for", "window A")
        good.append(case("cli: BENCH window A takes", r.returncode == 0, r.stdout + r.stderr))
        r = rf("BENCH", b.pid, "bridge", "take", "--for", "window B")
        good.append(case("cli: BENCH window B (same seat, other process) is refused", r.returncode != 0 and
                         "driver lock" in (r.stdout + r.stderr), (r.stdout + r.stderr)[-200:]))
        r = rf("BENCH", b.pid, "bridge", "release")
        good.append(case("cli: window B's release leaves A's driver lock in place",
                         os.path.exists(base["RIMFLOW_DRIVER_LOCK"]), (r.stdout + r.stderr)[-200:]))
        a.kill()
        a.wait()
        r = rf("FOUNDRY", b.pid, "bridge", "take", "--for", "after A died")
        good.append(case("cli: once A's process is gone, the next take wins", r.returncode == 0,
                         (r.stdout + r.stderr)[-200:]))
        r = rf("FOUNDRY", b.pid, "bridge", "release")
        good.append(case("cli: holder release frees the driver lock", r.returncode == 0 and
                         not os.path.exists(base["RIMFLOW_DRIVER_LOCK"]), (r.stdout + r.stderr)[-200:]))
    finally:
        for p in (a, b):
            if p.poll() is None:
                p.kill()
        shutil.rmtree(tmp, ignore_errors=True)
    return good


if __name__ == "__main__":
    sys.exit(main())
