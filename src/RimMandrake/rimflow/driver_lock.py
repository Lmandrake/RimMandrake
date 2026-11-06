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
  * every change to an EXISTING lock (renew, heartbeat, break, release) runs inside a fence: a short-lived
    `<lock>.op` file made with O_CREAT|O_EXCL (DRIVER_LOCK_FIX_UNFENCED_WRITES). Without it a holder that read the
    lock, then lost it to a newer generation, overwrote (heartbeat) or deleted (release) the replacement, and both
    believed they held it. Creating a lock that is absent needs no fence: O_EXCL already picks one winner.

Release requires the same identity, or force (recorded). Disabled under a redirected RIMFLOW_LEDGER unless
RIMFLOW_DRIVER_LOCK names a path, so selftests never touch the real lock.
"""
import sys as _rm_sys, pathlib as _rm_pl  # noqa: E401
_rm_sys.path.insert(0, str(_rm_pl.Path(__file__).resolve().parents[3] / "src" / "RimMandrake" / "Utils"))
from rmpaths import rm_path, rm_str, rm_win  # noqa: E402,F401  (data root: rmpaths.py)
import calendar
import contextlib
import json
import os
import socket
import subprocess
import sys
import time

DEFAULT = rm_win("scratch", "DRIVER_LOCK.json") if os.name == "nt" else rm_str("scratch", "DRIVER_LOCK.json")
STALE_HEARTBEAT_S = 45 * 60          # only consulted when the holder process cannot be inspected
WRITING_GRACE_S = 3.0
FENCE_STALE_S = 10.0                 # a fence is held for milliseconds; one this old belongs to a crashed process
FENCE_WAIT_S = 15.0


class FenceBusy(Exception):
    pass


class _Moved(Exception):
    """The lock changed between the unfenced liveness judgment and the fenced re-read: judge again."""


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


def _win_probe(pid):
    """-> ("alive", start) | ("gone", None) | ("unknown", None). Only a definite "no such process" is "gone": a
    timeout, a missing powershell.exe, a refused StartTime or unparseable output is "unknown" (cannot inspect, so the
    heartbeat decides) - never death (DRIVER_LOCK_FIX_UNFENCED_WRITES: a PowerShell timeout on a LIVE holder read as
    dead and let an ordinary take break a fresh lock)."""
    try:
        r = subprocess.run(["powershell.exe", "-NoProfile", "-Command",
                            "$p = Get-Process -Id %d -ErrorAction SilentlyContinue; if ($null -eq $p) { 'GONE' } "
                            "else { ([DateTimeOffset]$p.StartTime).ToUnixTimeMilliseconds() }" % pid],
                           capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return "unknown", None
    out = (r.stdout or "").strip()
    if r.returncode == 0 and out == "GONE":
        return "gone", None
    try:
        return "alive", int(out) / 1000.0
    except ValueError:
        return "unknown", None


def _win_start(pid):
    """Start time of a Windows pid, or None (gone or not inspectable - callers that must tell them apart use
    _win_probe)."""
    return _win_probe(pid)[1]


def _local_host():
    return socket.gethostname().lower()


def process_alive(ident):
    """True / False / None (cannot inspect). Same pid AND same start time, or it is a different process.

    A holder on ANOTHER machine (identity host differs; BRIDGE_LOCK_WIDEN_ONE_PER_HOST) cannot be inspected from
    here: its pid means nothing in this machine's /proc, so it reads None and the heartbeat decides. Without this a
    lock Archmagi took on SteveDesktop read as "process gone" at once and any local take broke it."""
    host = (ident.get("host") or "").lower()
    if host and host != _local_host():
        return None
    plat = ident.get("platform")
    if plat == "wsl" and os.name != "nt":
        if ident.get("boot_id") and current_boot_id() and ident["boot_id"] != current_boot_id():
            return False
        st = _proc_start(int(ident.get("pid") or 0))
        return st is not None and ident.get("start") is not None and abs(st - ident["start"]) < 0.05
    if plat == "nt":
        state, st = _win_probe(int(ident.get("pid") or 0))
        if state == "gone":
            return False
        if state != "alive" or ident.get("start") is None:
            return None                       # cannot inspect: the heartbeat decides, never "dead"
        return abs(st - ident["start"]) < 1.0
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


def _heartbeat_age(cur):
    try:
        # calendar.timegm, not mktime + time.timezone: the latter is an hour off whenever DST is in force, so every
        # heartbeat read 3600 s too old and a not-inspectable holder was ALWAYS stale (found 2026-10-25, PDT).
        return time.time() - calendar.timegm(time.strptime(cur.get("heartbeat", ""), "%Y-%m-%dT%H:%M:%SZ"))
    except (ValueError, OverflowError):
        return None


def owner_held(cur, verdict=None):
    """His OWNER lock binds while its process lives, and for 45 min after: his `bridge take` process exits at once, the
    hold does not. Only a caller that measured his last interaction may pass (host_guard says why). verdict: an
    _alive(cur) already measured."""
    if not cur or cur.get("seat") != "OWNER":
        return False
    age = _heartbeat_age(cur)
    return (verdict or _alive(cur))[0] or (age is not None and age < STALE_HEARTBEAT_S)


def _alive(cur):
    """Holder liveness: process identity first; heartbeat only when the process cannot be inspected."""
    ident = cur.get("identity") or {}
    foreign = (ident.get("host") or "").lower() not in ("", _local_host())   # another machine's boot_id never matches
    if not foreign and ident.get("platform") == "wsl" and ident.get("boot_id") and current_boot_id() \
            and ident["boot_id"] != current_boot_id():
        return False, "holder's machine has rebooted since (boot_id changed)"
    a = process_alive(ident)
    if a is not None:
        return a, "holder process pid %s %s" % (ident.get("pid"), "alive" if a else "gone")
    age = _heartbeat_age(cur)
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


def _fence_path(path):
    return path + ".op"


@contextlib.contextmanager
def _fence(path):
    """Hold `<lock>.op` (O_EXCL) for one read-check-write of the lock. Raises FenceBusy after FENCE_WAIT_S. A fence
    older than FENCE_STALE_S is a crashed holder's and is broken; ours is removed only while it still holds our nonce,
    so a fence broken as stale and re-made by another process is never deleted by us."""
    op = _fence_path(path)
    nonce = "%d %s %.6f" % (os.getpid(), socket.gethostname(), time.time())
    deadline = time.time() + FENCE_WAIT_S
    while True:
        try:
            fd = os.open(op, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        except (FileExistsError, PermissionError):  # Windows: a fence pending delete refuses with access denied
            try:
                if time.time() - os.path.getmtime(op) > FENCE_STALE_S:
                    aside = "%s.stale.%d" % (op, os.getpid())
                    os.rename(op, aside)
                    os.remove(aside)
                    continue
            except OSError:
                pass
            if time.time() > deadline:
                raise FenceBusy("driver lock fence %s held past %.0f s" % (op, FENCE_WAIT_S))
            time.sleep(0.05)
            continue
        except OSError as e:                          # no lock directory, read-only disk: never act unfenced
            raise FenceBusy("driver lock fence %s cannot be made (%s)" % (op, e))
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(nonce)
        break
    try:
        yield
    finally:
        try:
            with open(op, encoding="utf-8") as fh:
                mine = fh.read() == nonce
            if mine:
                os.remove(op)
        except OSError:
            pass


def acquire(path, seat, purpose, identity, force=None, spare_owner=False, owner_heartbeat=None):
    """-> {ok, generation, why, broke, holder}. force: a reason string to break a live or unreadable lock."""
    # Liveness is judged OUTSIDE the fence (a Windows probe may take 30 s; a fence that old reads as a crashed
    # holder's), then the fenced pass acts only on the very lock that was judged, and judges again if it moved.
    for _ in range(20):
        pre, _p = _read(path)
        verdict = _alive(pre) if pre is not None else None

        def judge(cur, pre=pre, verdict=verdict):
            if cur != pre:
                raise _Moved()
            return verdict
        try:
            with _fence(path):
                return _acquire(path, seat, purpose, identity, force, spare_owner, owner_heartbeat, judge)
        except _Moved:
            continue
        except FenceBusy as e:
            return {"ok": False, "why": "driver lock contended: %s" % e}
    return {"ok": False, "why": "driver lock contended: it kept changing under 20 judgments"}


def _acquire(path, seat, purpose, identity, force, spare_owner, owner_heartbeat, judge):
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
            # owner_heartbeat: the lock of his the caller's verdict was measured on; any newer one was not cleared
            if owner_heartbeat and cur.get("seat") == "OWNER" and seat != "OWNER" \
                    and cur.get("heartbeat") != owner_heartbeat:
                return {"ok": False, "holder": cur, "why": "the OWNER's lock moved after his hold was measured (%s, "
                        "measured %s): measure again" % (cur.get("heartbeat"), owner_heartbeat)}
            alive, how = judge(cur)
            if (alive and not force) or (spare_owner and seat != "OWNER" and owner_held(cur, (alive, how))):
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
            # the WHOLE lock must be the one judged, not just its generation: a heartbeat renewed between the check
            # and the rename keeps the generation but was never judged (a writer outside the fence: an older clone)
            if prev is not None and (took != prev or (
                    owner_heartbeat and prev.get("seat") == "OWNER"
                    and (took or {}).get("heartbeat") != owner_heartbeat)):
                try:                                  # someone re-took or renewed between read and rename: put it back
                    if took is not None:              # (an unreadable one stays aside: _create(None) wrote "null")
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


def refusal(path, identity):
    """What acquire would say, without touching the lock -> why, or None (free, ours, or its holder is gone). A read-only
    gate must agree with the take behind it (TICK_SPEED_FIX_GAME_IDLES_WAITING: `bridge idle` said TAKEABLE, ours, while
    a window of the same seat held this lock, so Relentless planned 17 deploys per tick before the take refused it)."""
    cur, problem = _read(path)
    if problem == "WRITING":
        return None
    if problem:
        return "driver lock %s is %s" % (path, problem)
    if cur is None or same_process(cur["identity"], identity):
        return None
    alive, how = _alive(cur)
    if not alive:
        return None
    return "driver lock held by %s (%s), %s; for: %s" % (cur.get("seat"), _who(cur["identity"]), how, cur.get("purpose"))


def _who(i):
    return "%s pid %s" % (i.get("platform"), i.get("pid"))


def _replace(path, body):
    tmp = "%s.%d.tmp" % (path, os.getpid())
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(body, fh)
    os.replace(tmp, path)


def heartbeat(path, identity):
    """Renew our own lock -> True, or False when it is not ours (any more) or the fence stayed busy. Fenced: a holder
    superseded after its read can no longer overwrite the newer generation."""
    try:
        with _fence(path):
            cur, _problem = _read(path)
            if cur and same_process(cur["identity"], identity):
                cur["heartbeat"] = _now()
                _replace(path, cur)
                return True
            return False
    except FenceBusy:
        return False


def release(path, seat, identity, force=None):
    cur, problem = _read(path)
    if cur is None and not problem:
        return {"ok": True, "why": "already free"}      # nothing to fence (and no fence to make if the dir is gone)
    try:
        with _fence(path):
            return _release(path, seat, identity, force)
    except FenceBusy as e:
        return {"ok": False, "why": "driver lock contended: %s" % e}


def _release(path, seat, identity, force):
    cur, problem = _read(path)
    if cur is None and not problem:
        return {"ok": True, "why": "already free"}
    if problem and not force:
        return {"ok": False, "why": "driver lock is %s; release it with --force after looking" % problem}
    if cur is not None and not same_process(cur["identity"], identity) and not force:
        return {"ok": False, "why": "driver lock is held by %s (%s), not this process; only the holder releases "
                "it (or force, which is recorded)" % (cur.get("seat"), _who(cur["identity"]))}
    # remove only the lock that was judged: rename it aside, compare, put back anything else (a writer outside the
    # fence - an older clone - may have replaced it since the read)
    aside = "%s.release.%d" % (path, os.getpid())
    try:
        os.rename(path, aside)
    except FileNotFoundError:
        return {"ok": True, "why": "already free"}
    took, _p = _read(aside)
    if cur is not None and took != cur:
        restored = False
        try:
            if took is not None:
                _create(path, took)
                restored = True
        except (FileExistsError, OSError, TypeError):
            pass
        if restored:                                  # else the aside is the only copy left: keep it as the record
            try:
                os.remove(aside)
            except OSError:
                pass
        return {"ok": False, "why": "driver lock changed under the release (now %s generation %s): nothing released%s"
                % ((took or {}).get("seat"), (took or {}).get("generation"),
                   "" if restored else "; it could not be put back and is kept at %s" % aside)}
    try:
        os.remove(aside)
    except OSError:
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
