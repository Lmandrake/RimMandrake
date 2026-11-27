#!/usr/bin/env python3
"""plant_record.py: the record that `maturation.py red-seen` writes before it plants a fault, so that a kill which skips
every `finally` (SIGKILL) cannot leave the fault in the tree unnamed. The next `red-seen`, `certificate` or `./publish` on
the clone calls check(), which reverses a leftover plant and says so in one line.
Item RIMMANDRAKE_RESTORE_TREE_WHEN_RED_SEEN_IS_KILLED_PLANT_STAYED_APPLIED; page
design/specs/2026-11-27-red-seen-plant-record/boundary.md.

check(root) -> {"state", "line", "files"}. The states:
  clean           no record, or the record's files already hold their original bytes (the record is removed)
  restored        a leftover plant was reversed; the record is removed
  not restored    a leftover plant could not be reversed: a stop that names each file and the record
  could not look  the record is there but cannot be read, or git could not say where it is: never "clean"
  running         the pid that wrote the record is alive: its plant is in the tree on purpose
"""
import base64
import binascii
import datetime
import json
import os
import subprocess

NAME = "rm_red_seen_plant.json"
CLEAN, RESTORED, NOT_RESTORED, COULD_NOT_LOOK, RUNNING = "clean", "restored", "not restored", "could not look", "running"
STOPS = (NOT_RESTORED, COULD_NOT_LOOK, RUNNING)
# budget: danger=a hung git call holds red-seen, the certificate or a publish; longest=1s (git rev-parse and a one-file
# budget: git apply, the selftest fixtures, 2026-11-27)
GIT_TIMEOUT_S = 60


class Unreadable(Exception):
    pass


def path(root):
    """-> where this clone's record lives: the git dir (never the work tree), or `.rm_red_seen_plant.json` in root when
    root is not in a git work tree. Raises Unreadable when git could not answer."""
    try:
        r = subprocess.run(["git", "rev-parse", "--git-path", NAME], cwd=root, capture_output=True, text=True,
                           timeout=GIT_TIMEOUT_S)
    except (OSError, subprocess.TimeoutExpired) as e:
        raise Unreadable("git rev-parse could not run in %s: %s" % (root, e))
    if r.returncode == 0 and r.stdout.strip():
        p = r.stdout.strip()
        return p if os.path.isabs(p) else os.path.join(root, p)
    if "not a git repository" in r.stderr:
        return os.path.join(root, "." + NAME)
    raise Unreadable("git rev-parse --git-path failed in %s (rc %s): %s" % (root, r.returncode, r.stderr.strip()))


def _start_time(pid):
    """-> the pid's start time in clock ticks (/proc/<pid>/stat field 22), or None when it cannot be read."""
    try:
        with open("/proc/%d/stat" % pid) as f:
            return f.read().rsplit(")", 1)[1].split()[19]
    except (OSError, IndexError, ValueError):
        return None


def write(root, mod, test_id, patch_text, before):
    """Write the record before the plant: `before` maps each patched repo-relative path to its bytes (None: the file is
    absent). Written to a temporary file and renamed into place, so no reader sees half a record. Raises OSError or
    Unreadable."""
    p = path(root)
    rec = {"pid": os.getpid(), "pid_start": _start_time(os.getpid()), "mod": mod, "test": test_id,
           "at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "patch": patch_text,
           "files": {k: None if v is None else base64.b64encode(v).decode("ascii") for k, v in before.items()}}
    tmp = p + ".tmp.%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(rec, f)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, p)
    return p


def clear(root, where=None):
    """Remove the record (the plant is gone); `where`: its path, already known (no git call). Missing: nothing to do."""
    try:
        os.remove(where or path(root))
    except FileNotFoundError:
        pass


def _read(root, rel):
    fp = os.path.join(root, rel)
    if not os.path.isfile(fp):
        return None
    with open(fp, "rb") as f:
        return f.read()


def _alive(rec):
    pid = rec["pid"]
    if pid == os.getpid():
        return False    # this process's own earlier record: that red-seen has ended
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        pass
    start = rec.get("pid_start")
    return not (start and _start_time(pid) not in (None, start))


def _git_apply(root, args, patch_file):
    try:
        r = subprocess.run(["git", "apply"] + args + [patch_file], cwd=root, capture_output=True, text=True,
                           timeout=GIT_TIMEOUT_S)
        return r.returncode == 0, r.stderr.strip()
    except (OSError, subprocess.TimeoutExpired) as e:
        return False, str(e)


def check(root):
    """Read the clone's record and reverse a leftover plant. -> {"state", "line", "files"}; "line" is "" only for a
    clean tree with no record."""
    try:
        p = path(root)
    except Unreadable as e:
        return {"state": COULD_NOT_LOOK, "files": [], "line": "plant: could not look: %s; whether a planted fault of "
                "a killed red-seen is still in the tree is unknown" % e}
    try:
        with open(p, "rb") as f:
            raw = f.read()
    except FileNotFoundError:
        return {"state": CLEAN, "files": [], "line": ""}
    except OSError as e:
        raw, err = None, str(e)
    rec = None
    if raw is not None:
        try:
            rec = json.loads(raw.decode("utf-8"))
            files = {k: None if v is None else base64.b64decode(v, validate=True) for k, v in rec["files"].items()}
            if not (isinstance(rec["patch"], str) and isinstance(rec["pid"], int) and files):
                raise ValueError("no patch, pid or file")
        except (ValueError, KeyError, TypeError, AttributeError, binascii.Error) as e:
            rec, err = None, "%s: %s" % (type(e).__name__, e)
    if rec is None:
        return {"state": COULD_NOT_LOOK, "files": [], "line": "plant: could not look: the plant record %s cannot be "
                "read (%s), so whether a planted fault of a killed red-seen is still in the tree is unknown; compare "
                "the files it names with git, make them right, then delete the record" % (p, err)}
    who = "red-seen %s %s (pid %s, %s)" % (rec.get("mod"), rec.get("test"), rec["pid"], rec.get("at"))
    if _alive(rec):
        return {"state": RUNNING, "files": sorted(files), "line": "plant: running: %s is still running on this clone "
                "and its planted fault is in %s now; wait for it to end" % (who, ", ".join(sorted(files)))}
    differ = sorted(k for k, v in files.items() if _read(root, k) != v)
    if not differ:
        clear(root, p)
        return {"state": CLEAN, "files": [], "line": "plant: clean: the record of %s, which did not end, was found; "
                "the tree already holds the original bytes; record removed" % who}
    pf = p + ".patch"
    with open(pf, "w", encoding="utf-8") as f:
        f.write(rec["patch"])
    try:
        fits, err = _git_apply(root, ["-R", "--check"], pf)
        if fits:
            fits, err = _git_apply(root, ["-R"], pf)
    finally:
        os.remove(pf)
    if not fits:
        return {"state": NOT_RESTORED, "files": differ, "line": "plant: not restored: %s did not end, and its planted "
                "fault may still be in %s; its reverse does not apply (%s); restore each file by hand from its "
                "original bytes (base64) in %s, then delete the record" % (who, ", ".join(differ), err, p)}
    clear(root, p)
    still = sorted(k for k, v in files.items() if _read(root, k) != v)
    return {"state": RESTORED, "files": differ, "line": "plant: restored: %s did not end and left its planted fault "
            "in %s; the fault is reversed%s" % (who, ", ".join(differ), "; %s also holds later changes, kept" %
                                                 ", ".join(still) if still else "")}
