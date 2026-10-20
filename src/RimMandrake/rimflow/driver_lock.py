"""driver_lock.py - the exclusive bridge DRIVER lock, keyed on process identity (BRIDGE_LOCK_HARDEN_ALIVE_MEANS_A_PID).

The ledger lock (`rimflow bridge take`) knows SEATS and judges liveness from ledger events, so two BENCH windows
cannot be told apart (CLAUDE.md, handoff.py) and a crashed window stays "alive" for 45 minutes. This lock is a
second, stricter witness the ledger lock now consults:

  * ONE file on the drive every clone and python.exe can see (D:\\ClaudeWork\\rimmandrake\\scratch\\DRIVER_LOCK.json),
    created with O_CREAT|O_EXCL - the filesystem picks exactly one winner.
  * the holder is a PROCESS: {pid, start time, boot_id, platform}. The owner process is the nearest `claude`
    ancestor (the agent window), else the parent shell - not the short-lived rimflow process.
  * liveness is that process existing with the same start time on the same boot; a pid reused by a new process
    is a different holder. Heartbeat age is reported; it decides only when the process cannot be inspected.
  * an UNREADABLE lock is an explicit failure (never read as free); --force breaks it and records why.
  * every take bumps a generation (kept beside the lock), so a stale holder can tell it was superseded.

Release requires the same identity, or force (recorded). Disabled under a redirected RIMFLOW_LEDGER unless
RIMFLOW_DRIVER_LOCK names a path, so selftests never touch the real lock.
"""
import sys as _rm_sys, pathlib as _rm_pl  # noqa: E401
_rm_sys.path.insert(0, str(_rm_pl.Path(__file__).resolve().parents[3] / "src" / "RimMandrake" / "Utils"))
from rmpaths import rm_path, rm_str, rm_win  # noqa: E402,F401  (data root: rmpaths.py)
import json
import os
import socket
import subprocess
import sys
import time

DEFAULT = rm_win("scratch", "DRIVER_LOCK.json") if os.name == "nt" else rm_str("scratch", "DRIVER_LOCK.json")
STALE_HEARTBEAT_S = 45 * 60          # only consulted when the holder process cannot be inspected
WRITING_GRACE_S = 3.0


def lock_path():
    env = os.environ.get("RIMFLOW_DRIVER_LOCK")
    if env is not None:
        return env or None
    if os.environ.get("RIMFLOW_LEDGER"):
        return None
    return DEFAULT if os.path.isdir(os.path.dirname(DEFAULT)) else None


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def current_boot_id():
    try:
        with open("/proc/sys/kernel/random/boot_id") as fh:
            return fh.read().strip()
    except OSError:
        return None


def _proc_start(pid):
    """Start time of a Linux pid in seconds since boot (from /proc/<pid>/stat), or None."""
    try:
        with open("/proc/%d/stat" % pid) as fh:
            rest = fh.read().rsplit(")", 1)[1].split()
        return round(int(rest[19]) / os.sysconf("SC_CLK_TCK"), 2)
    except (OSError, IndexError, ValueError):
        return None


def _comm(pid):
    try:
        with open("/proc/%d/comm" % pid) as fh:
            return fh.read().strip()
    except OSError:
        return ""


def _ppid(pid):
    try:
        with open("/proc/%d/stat" % pid) as fh:
            return int(fh.read().rsplit(")", 1)[1].split()[1])
    except (OSError, IndexError, ValueError):
        return None


def owner_pid():
    """The process that owns a take: RM_DRIVER_PID, else the nearest `claude` ancestor, else the parent."""
    env = os.environ.get("RM_DRIVER_PID")
    if env and env.isdigit():
        return int(env)
    if os.name == "nt":
        return os.getppid()
    p = os.getpid()
    for _ in range(12):
        p = _ppid(p)
        if not p or p <= 1:
            break
        if _comm(p) == "claude":
            return p
    return os.getppid()


def my_identity():
    pid = owner_pid()
    if os.name == "nt":
        return {"pid": pid, "start": _win_start(pid), "boot_id": None, "platform": "nt", "host": socket.gethostname()}
    return {"pid": pid, "start": _proc_start(pid), "boot_id": current_boot_id(), "platform": "wsl",
            "host": socket.gethostname()}


def _win_start(pid):
    try:
        out = subprocess.run(["powershell.exe", "-NoProfile", "-Command",
                              "([DateTimeOffset](Get-Process -Id %d -ErrorAction Stop).StartTime)"
                              ".ToUnixTimeMilliseconds()" % pid], capture_output=True, text=True, timeout=30).stdout
        return int(out.strip()) / 1000.0
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None


def process_alive(ident):
    """True / False / None (cannot inspect). Same pid AND same start time, or it is a different process."""
    plat = ident.get("platform")
    if plat == "wsl" and os.name != "nt":
        if ident.get("boot_id") and current_boot_id() and ident["boot_id"] != current_boot_id():
            return False
        st = _proc_start(int(ident.get("pid") or 0))
        return st is not None and ident.get("start") is not None and abs(st - ident["start"]) < 0.05
    if plat == "nt":
        st = _win_start(int(ident.get("pid") or 0))
        if st is None:
            return False
        return ident.get("start") is not None and abs(st - ident["start"]) < 1.0
    return None


def same_process(a, b):
    return bool(a and b) and a.get("pid") == b.get("pid") and a.get("start") == b.get("start") \
        and a.get("boot_id") == b.get("boot_id") and a.get("platform") == b.get("platform")


def _read(path):
    """-> (dict|None, problem|None). Missing -> (None, None)."""
    try:
        with open(path, encoding="utf-8") as fh:
            raw = fh.read()
    except FileNotFoundError:
        return None, None
    except OSError as e:
        return None, "UNREADABLE (%s)" % e
    try:
        d = json.loads(raw)
        if not isinstance(d, dict) or "identity" not in d:
            raise ValueError("no identity")
        return d, None
    except ValueError as e:
        try:
            young = time.time() - os.path.getmtime(path) < WRITING_GRACE_S and not raw.strip()
        except OSError:
            young = False
        return None, ("WRITING" if young else "UNREADABLE (%s: %r)" % (e, raw[:60]))


def _gen_path(path):
    return path + ".gen"


def _last_gen(path, cur=None):
    g = (cur or {}).get("generation") or 0
    try:
        with open(_gen_path(path)) as fh:
            g = max(g, int(fh.read().strip() or 0))
    except (OSError, ValueError):
        pass
    return g


def _alive(cur):
    """Holder liveness: process identity first; heartbeat only when the process cannot be inspected."""
    ident = cur.get("identity") or {}
    if ident.get("platform") == "wsl" and ident.get("boot_id") and current_boot_id() \
            and ident["boot_id"] != current_boot_id():
        return False, "holder's machine has rebooted since (boot_id changed)"
    a = process_alive(ident)
    if a is not None:
        return a, "holder process pid %s %s" % (ident.get("pid"), "alive" if a else "gone")
    try:
        age = time.time() - time.mktime(time.strptime(cur.get("heartbeat", ""), "%Y-%m-%dT%H:%M:%SZ")) + time.timezone
    except (ValueError, OverflowError):
        age = None
    if age is not None and age < STALE_HEARTBEAT_S:
        return True, "holder process not inspectable from here; heartbeat %d s old" % age
    return False, "holder process not inspectable and heartbeat stale/absent"


def _create(path, body):
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(body, fh)
        fh.flush()
        os.fsync(fh.fileno())
    try:
        with open(_gen_path(path), "w") as fh:
            fh.write(str(body["generation"]))
    except OSError:
        pass


def acquire(path, seat, purpose, identity, force=None):
    """-> {ok, generation, why, broke, holder}. force: a reason string to break a live or unreadable lock."""
    for _ in range(20):
        cur, problem = _read(path)
        broke = False
        prev = None
        if problem == "WRITING":
            time.sleep(0.3)
            continue
        if problem:
            if not force:
                return {"ok": False, "why": "driver lock %s is %s - refusing to read it as free; break it with "
                        "--force \"<why>\" after looking at it" % (path, problem)}
            prev = None
        elif cur is not None:
            if same_process(cur["identity"], identity):
                cur["heartbeat"] = _now()
                cur["purpose"] = purpose or cur.get("purpose")
                _replace(path, cur)
                return {"ok": True, "generation": cur.get("generation"), "why": "already held by this process",
                        "broke": False}
            alive, how = _alive(cur)
            if alive and not force:
                return {"ok": False, "holder": cur, "why": "driver lock held by %s (%s), %s; for: %s" % (
                    cur.get("seat"), _who(cur["identity"]), how, cur.get("purpose"))}
            prev = cur
        if cur is not None or problem:
            aside = "%s.broken.%s.%d" % (path, time.strftime("%Y%m%dT%H%M%S"), os.getpid())
            try:
                os.rename(path, aside)
            except FileNotFoundError:
                continue
            took, _p = _read(aside)
            if prev is not None and (took or {}).get("generation") != prev.get("generation"):
                try:                                  # someone re-took between our read and rename: put it back
                    _create(path, took)
                except (FileExistsError, OSError, TypeError):
                    pass
                continue
            broke = True
        body = {"seat": seat, "purpose": purpose, "identity": identity, "acquired": _now(), "heartbeat": _now(),
                "generation": _last_gen(path, prev) + 1}
        if force and (broke or problem):
            body["override"] = force
        if broke and prev is not None:
            body["took_from"] = {"seat": prev.get("seat"), "identity": prev.get("identity"),
                                 "generation": prev.get("generation")}
        try:
            _create(path, body)
        except FileExistsError:
            continue
        return {"ok": True, "generation": body["generation"], "broke": broke, "why": "taken"}
    return {"ok": False, "why": "driver lock contended: gave up after 20 attempts"}


def _who(i):
    return "%s pid %s" % (i.get("platform"), i.get("pid"))


def _replace(path, body):
    tmp = "%s.%d.tmp" % (path, os.getpid())
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(body, fh)
    os.replace(tmp, path)


def heartbeat(path, identity):
    cur, problem = _read(path)
    if cur and same_process(cur["identity"], identity):
        cur["heartbeat"] = _now()
        _replace(path, cur)
        return True
    return False


def release(path, seat, identity, force=None):
    cur, problem = _read(path)
    if cur is None and not problem:
        return {"ok": True, "why": "already free"}
    if problem and not force:
        return {"ok": False, "why": "driver lock is %s; release it with --force after looking" % problem}
    if cur is not None and not same_process(cur["identity"], identity) and not force:
        return {"ok": False, "why": "driver lock is held by %s (%s), not this process; only the holder releases "
                "it (or force, which is recorded)" % (cur.get("seat"), _who(cur["identity"]))}
    try:
        os.remove(path)
    except FileNotFoundError:
        pass
    return {"ok": True, "why": "released" + (" (forced: %s)" % force if force else "")}


def status(path):
    cur, problem = _read(path)
    if problem:
        return {"state": problem}
    if cur is None:
        return {"state": "FREE", "generation": _last_gen(path)}
    alive, how = _alive(cur)
    return {"state": "HELD" if alive else "STALE", "seat": cur.get("seat"), "purpose": cur.get("purpose"),
            "identity": cur.get("identity"), "generation": cur.get("generation"), "heartbeat": cur.get("heartbeat"),
            "how": how}


if __name__ == "__main__":
    p = lock_path()
    print(json.dumps({"path": p, "me": my_identity(), "status": status(p) if p else None}, indent=1))
    sys.exit(0)
