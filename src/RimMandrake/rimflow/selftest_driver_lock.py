"""selftest_driver_lock.py - the driver lock is exclusive, keyed on process identity, and loud when unreadable
(BRIDGE_LOCK_HARDEN_ALIVE_MEANS_A_PID). Written failing-first. Temp lock path; liveness faked per case.
"""
# selftest temp containment (wave 7, DIRTY_CODE_REVIEW_STANDING_LOOP_1): every mkdtemp/mkstemp below,
# and every child process via TMPDIR, lands in one private dir removed at exit — this
# test used to leave its temp dirs behind in the seat TMPDIR on every run.
import atexit as _st_atexit, os as _st_os, shutil as _st_shutil, tempfile as _st_tempfile  # noqa: E401
_st_tempfile.tempdir = _st_os.environ["TMPDIR"] = _st_tempfile.mkdtemp(prefix="st_selftest_driver_lock_")
_st_atexit.register(_st_shutil.rmtree, _st_tempfile.tempdir, True)
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import driver_lock as D  # noqa: E402
REAL_PROCESS_ALIVE = D.process_alive


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
    # the race itself: B read the lock as FREE before A created it (stale first read), so only O_EXCL stands
    # between B and overwriting A. Sequential calls alone never reach _create (review 2026-10-26).
    real_read, stale = D._read, [True]

    def racy_read(p):
        if stale and p == path:
            stale.pop()
            return None, None
        return real_read(p)
    D._read = racy_read
    try:
        r2 = D.acquire(path, "BENCH", "b", B)
    finally:
        D._read = real_read
    with open(path) as fh:
        holder = json.load(fh).get("seat")
    good.append(case("exactly one of two racing acquirers wins (O_EXCL), and the winner's lock is intact",
                     r1["ok"] and not r2["ok"] and not stale and holder == "FOUNDRY", (r1, r2, holder)))

    D.current_boot_id = real_boot
    good.append(case("owner identity finds a real process", D.my_identity()["pid"] > 1, D.my_identity()))

    good += fence_cases()
    good += win_probe_cases()
    good += cli_cases()
    print("%d/%d" % (sum(good), len(good)))
    return 0 if all(good) else 1


def _holder(path):
    try:
        with open(path) as fh:
            d = json.load(fh)
        return d.get("seat"), d.get("generation")
    except FileNotFoundError:
        return None, None


def fence_cases():
    """DRIVER_LOCK_FIX_UNFENCED_WRITES: a holder that read its lock, then lost it to a newer generation, must not
    overwrite (heartbeat) or delete (release) the replacement; a takeover must judge the whole lock it renames, not
    just its generation. Failing-first: each race is staged by a hook in the holder's read."""
    good = []
    path = os.path.join(tempfile.mkdtemp(), "DRIVER_LOCK.json")
    real_read, real_boot, real_wait = D._read, D.current_boot_id, D.FENCE_WAIT_S
    D.current_boot_id = lambda: "boot-1"
    D.FENCE_WAIT_S = 0.3
    alive = {}
    D.process_alive = lambda i: alive.get(i.get("pid"), False)
    A, B = ident(41), ident(42)
    try:
        for verb in ("heartbeat", "release"):
            if os.path.exists(path):
                os.remove(path)
            alive.update({41: True, 42: True})
            D.acquire(path, "BENCH", "A holds", A)
            got = {}

            def racing_read(p, _fired=[]):
                snap = real_read(p)
                if p == path and not _fired:        # A has read its own lock; now A's process dies and B takes over
                    _fired.append(1)
                    alive[41] = False
                    got["b"] = D.acquire(path, "FOUNDRY", "B takes over", B)
                return snap
            D._read = racing_read
            try:
                a_ok = D.heartbeat(path, A) if verb == "heartbeat" else D.release(path, "BENCH", A)["ok"]
            finally:
                D._read = real_read
            seat, gen = _holder(path)
            b_ok = got.get("b", {}).get("ok")
            # never both: if B was told it holds the lock, the lock on disk must still be B's
            good.append(case("a superseded holder's %s cannot %s the newer generation's lock" % (
                verb, "overwrite" if verb == "heartbeat" else "delete"),
                "b" in got and (not b_ok or (seat == "FOUNDRY" and gen == got["b"]["generation"])),
                (verb, a_ok, got.get("b"), seat, gen)))

        # a takeover whose rename catches a heartbeat renewed after its check (same generation) puts it back
        if os.path.exists(path):
            os.remove(path)
        alive.update({41: True, 42: True})
        a_gen = D.acquire(path, "BENCH", "A holds", A)["generation"]
        alive[41] = False                           # A reads as gone at the check...

        real_rename = os.rename

        def renewing_rename(src, dst, _fired=[]):
            if src == path and not _fired:          # ...and renews its heartbeat between the check and the rename
                _fired.append(1)                    # (outside any fence: an older clone), same generation
                alive[41] = True
                with open(path) as fh:
                    d = dict(json.load(fh), heartbeat="2099-01-01T00:00:00Z")
                with open(path, "w") as fh:
                    json.dump(d, fh)
            return real_rename(src, dst)
        os.rename = renewing_rename
        try:
            r = D.acquire(path, "FOUNDRY", "takeover", B)
        finally:
            os.rename = real_rename
        seat, gen = _holder(path)
        good.append(case("a takeover that renamed a renewed (same-generation) lock puts it back and re-judges",
                         not r["ok"] and seat == "BENCH" and gen == a_gen, (r, seat, gen)))

        # the liveness probe (a Windows one may take 30 s) never runs while the fence is held
        seen = []
        D.process_alive = lambda i: seen.append(os.path.exists(D._fence_path(path))) or False
        r = D.acquire(path, "FOUNDRY", "probe outside", B)
        good.append(case("liveness is judged outside the fence (a slow probe cannot age it into 'stale')",
                         r["ok"] and seen and not any(seen), (r, seen)))
        D.process_alive = lambda i: alive.get(i.get("pid"), False)
        D.release(path, "FOUNDRY", B)
        a_gen = D.acquire(path, "BENCH", "A holds", A)["generation"]
        # a crashed process's fence is broken after FENCE_STALE_S; a fresh one is waited on
        with open(D._fence_path(path), "w") as fh:
            fh.write("crashed")
        r = D.release(path, "BENCH", A)
        good.append(case("a live fence makes a release wait, then refuse - never act unfenced",
                         not r["ok"] and "contended" in r["why"] and os.path.exists(path), r))
        os.utime(D._fence_path(path), (1, 1))
        r = D.release(path, "BENCH", A)
        good.append(case("a stale fence (crashed holder) is broken and the release goes through",
                         r["ok"] and not os.path.exists(path) and not os.path.exists(D._fence_path(path)), r))
    finally:
        D._read, D.current_boot_id, D.FENCE_WAIT_S = real_read, real_boot, real_wait
    return good


def win_probe_cases():
    """DRIVER_LOCK_FIX_UNFENCED_WRITES: a failed inspection of a Windows holder is 'cannot inspect' (the heartbeat
    decides), never 'dead'; only a definite no-such-process is dead."""
    import subprocess
    good = []
    real_run, real_host, real_pa = D.subprocess.run, D._local_host, D.process_alive
    D.process_alive = REAL_PROCESS_ALIVE
    D._local_host = lambda: "archmagi"
    w = ident(77, start=123.0, platform="nt")

    def fake(result):
        def run(*a, **k):
            if isinstance(result, Exception):
                raise result
            return subprocess.CompletedProcess(a[0], result[0], stdout=result[1], stderr="")
        return run
    try:
        for label, res, want in (
                ("a PowerShell timeout", subprocess.TimeoutExpired("powershell.exe", 30), None),
                ("no powershell.exe", FileNotFoundError("powershell.exe"), None),
                ("unparseable output (StartTime refused)", (1, ""), None),
                ("a definite no-such-process", (0, "GONE\r\n"), False),
                ("the same start time", (0, "123000\r\n"), True),
                ("a reused pid (other start time)", (0, "999000\r\n"), False)):
            D.subprocess.run = fake(res)
            got = D.process_alive(w)
            good.append(case("windows holder, %s -> %s" % (label, want), got is want, got))
        D.subprocess.run = fake(subprocess.TimeoutExpired("powershell.exe", 30))
        fresh = {"seat": "BENCH", "identity": w, "heartbeat": D._now(), "generation": 3}
        alive, how = D._alive(fresh)
        good.append(case("a live-looking Windows holder whose inspection timed out is held on its fresh heartbeat",
                         alive and "not inspectable" in how, how))
        path = os.path.join(tempfile.mkdtemp(), "DRIVER_LOCK.json")
        with open(path, "w") as fh:
            json.dump(fresh, fh)
        r = D.acquire(path, "FOUNDRY", "ordinary take", ident(78))
        good.append(case("an ordinary take does not break it", not r["ok"] and _holder(path)[0] == "BENCH", r))
    finally:
        D.subprocess.run, D._local_host, D.process_alive = real_run, real_host, real_pa
    return good


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
        r = rf("BENCH", b.pid, "bridge", "idle", "--for", "a relentless stage")
        good.append(case("cli: `bridge idle` agrees with the take: B of the same seat reads NOT TAKEABLE",
                         r.returncode == 1 and "driver lock held by" in r.stdout, (r.stdout + r.stderr)[-200:]))
        r = rf("BENCH", a.pid, "bridge", "idle", "--for", "window A itself")
        good.append(case("cli: `bridge idle` from the holder's own process reads TAKEABLE",
                         r.returncode == 0 and r.stdout.startswith("TAKEABLE"), (r.stdout + r.stderr)[-200:]))
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
