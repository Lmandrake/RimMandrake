#!/usr/bin/env python3
"""defdump_db_tick.py: keeps the live DefDump's defs.sqlite current with its newest capture (rm-defdump-db.timer).

Page: design/specs/2026-11-26-defdump-db-tick/boundary.md. Each game load with RimDefDump writes a new capture; nothing
rebuilt the db after it, so every `dump_manifest.dump_db` reader read the db as stale and answered UNMEASURED
(SELFTEST_UNMEASURED_FOUR_REBUILD_DEFDUMP_DB). No game, no bridge, no model.

    defdump_db_tick.py tick [--root DIR]    one look; rebuild when absent or stale. exit 0 current or rebuilt;
                                            1 the build failed; 2 could not look
    defdump_db_tick.py check [--root DIR]   exit 0 the reading is fresh and the db is current (or stale inside the
                                            grace); 1 not, named; 2 could not look
    defdump_db_tick.py show                 the last reading

Reading: <RM_DISPATCHER_STATE>/defdump_db/reading.json (RM_DEFDUMP_DB_DIR overrides).
"""
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RIMFLOW = os.path.join(os.path.dirname(HERE), "rimflow")
for _p in (HERE, RIMFLOW):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import dump_manifest  # noqa: E402

DB_NAME = "defs.sqlite"
FAMILY = "defdump_db"
# budget: danger=a hung build holds the timer for good (systemd starts no second run); longest=68.7s (the first tick, of
# budget: capture 2026-11-27T06-22-12Z, 2026-11-26; another build took 28.7 s; page LIMITS)
BUILD_TIMEOUT_S = 900
# budget: danger=a dead timer reads alive; ends no work: `check` answers 1. The timer beats each 30 min.
FRESH_S = 7200
# budget: danger=a false red between a capture and the next tick; ends no work: `check` answers 1 past it
GRACE_S = 7200
_CAPTURE_ID = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z$")
COULD_NOT_LOOK = 2


def state_dir():
    d = os.environ.get("RM_DEFDUMP_DB_DIR")
    if not d:
        import doorbell
        d = os.path.join(doorbell.state_dir(), FAMILY)
    return d


def reading_path():
    return os.path.join(state_dir(), "reading.json")


def default_root():
    from game_paths import DUMP_ROOT
    return DUMP_ROOT


def newest_capture(root):
    """-> (capture id, path) of the newest capture under root/captures, or (None, None) when there is none.
    Raises OSError when root itself cannot be read."""
    os.listdir(root)                                  # an unreadable root is could-not-look, not "no capture"
    caps = os.path.join(root, "captures")
    if not os.path.isdir(caps):
        return None, None
    ids = sorted(d for d in os.listdir(caps)
                 if _CAPTURE_ID.match(d) and os.path.isfile(os.path.join(caps, d, "manifest.json")))
    if not ids:
        return None, None
    return ids[-1], os.path.join(caps, ids[-1])


def capture_age_s(capture_id, now=None):
    t = dt.datetime.strptime(capture_id, "%Y-%m-%dT%H-%M-%SZ").replace(tzinfo=dt.timezone.utc)
    return (now or time.time()) - t.timestamp()


def db_state(root):
    """-> ("absent"|"current"|"stale", why). Raises RuntimeError when the measure skill is not installed."""
    path = os.path.join(root, DB_NAME)
    if not os.path.exists(path):
        return "absent", "no %s at %s" % (DB_NAME, root)
    s = dump_manifest.skill_scripts()
    if s is None:
        raise RuntimeError("the measuring-large-artifacts skill is not installed (no measure/ under ~/.claude/skills)")
    if s not in sys.path:
        sys.path.insert(0, s)
    from measure.dumpdb import DumpDB
    try:
        db = DumpDB(path)
    except Exception as exc:                          # noqa: BLE001 - an unopenable db is rebuilt like an absent one
        return "absent", "the db did not open: %s" % exc
    try:
        stale = db.stale
    finally:
        db.close()
    return ("stale", str(stale)) if stale else ("current", "current with its capture")


def run_build(root):
    """-> (ok, line). Runs `measure --dump root build` once, cut at BUILD_TIMEOUT_S."""
    s = dump_manifest.skill_scripts()
    if s is None:
        return False, "the measuring-large-artifacts skill is not installed"
    cmd = [sys.executable, os.path.join(s, "measure", "cli.py"), "--dump", root, "build"]
    t0 = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=BUILD_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return False, "the build was cut at its limit of %d s (BUILD_TIMEOUT_S)" % BUILD_TIMEOUT_S
    out = ((r.stdout or "") + (r.stderr or "")).strip()
    verdict = next((ln for ln in out.splitlines() if ln.startswith("MEASURED")), None)
    if r.returncode != 0 or verdict is None:
        tail = out.splitlines()[-1] if out else "no output"
        return False, "measure build exit %d, no MEASURED line: %s" % (r.returncode, tail)
    return True, "%s (%.1f s)" % (verdict, time.time() - t0)


def write_reading(r):
    os.makedirs(state_dir(), exist_ok=True)
    p = reading_path()
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(r, fh, indent=1)
    os.replace(tmp, p)


def tick(root=None, builder=run_build):
    """One look. -> (exit code, reading)."""
    root = root or default_root()
    r = {"at": time.time(), "root": root}
    try:
        cid, _ = newest_capture(root)
        r["newest_capture"] = cid
        if cid is None:
            r.update(state="no_capture", act="none", why="no capture under %s/captures: nothing to build from" % root)
            write_reading(r)
            return 0, r
        state, why = db_state(root)
    except (OSError, RuntimeError) as exc:
        r.update(state="could_not_look", act="none", why=str(exc))
        write_reading(r)
        return COULD_NOT_LOOK, r
    r["before"] = {"state": state, "why": why}
    if state == "current":
        r.update(state="current", act="none", why=why)
        write_reading(r)
        return 0, r
    ok, line = builder(root)
    r["build"] = line
    if not ok:
        r.update(state="build_failed", act="build", why=line)
        write_reading(r)
        return 1, r
    try:
        after, why_after = db_state(root)
    except RuntimeError as exc:
        after, why_after = "could_not_look", str(exc)
    r.update(state="rebuilt" if after == "current" else "build_failed", act="build",
             why=why_after if after == "current" else "built, yet the db reads %s: %s" % (after, why_after))
    write_reading(r)
    return (0 if after == "current" else 1), r


def check(root=None, now=None):
    """-> (exit code, line)."""
    now = now or time.time()
    root = root or default_root()
    try:
        with open(reading_path(), encoding="utf-8") as fh:
            rd = json.load(fh)
    except FileNotFoundError:
        return 1, "no reading at %s: the tick has never run (rm-defdump-db.timer)" % reading_path()
    except (OSError, ValueError) as exc:
        return COULD_NOT_LOOK, "the reading cannot be read: %s" % exc
    age = now - float(rd.get("at") or 0)
    if age > FRESH_S:
        return 1, "the reading is %.0f s old (fresh for %d s): rm-defdump-db.timer is not running" % (age, FRESH_S)
    try:
        cid, _ = newest_capture(root)
        if cid is None:
            return 0, "no capture under %s: nothing to keep current" % root
        state, why = db_state(root)
    except (OSError, RuntimeError) as exc:
        return COULD_NOT_LOOK, "could not look at %s: %s" % (root, exc)
    if state == "current":
        return 0, "defs.sqlite is current with capture %s; reading %.0f s old" % (cid, age)
    if state == "absent":
        return 1, "defs.sqlite is absent at %s, newest capture %s: %s" % (root, cid, why)
    cage = capture_age_s(cid, now)
    if cage <= GRACE_S:
        return 0, "defs.sqlite is %s, capture %s is %.0f s old (grace %d s)" % (state, cid, cage, GRACE_S)
    return 1, "defs.sqlite is %s %.0f s after capture %s (grace %d s): %s" % (state, cage, cid, GRACE_S, why)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("tick", "check"):
        p = sub.add_parser(name)
        p.add_argument("--root", help="the DefDump root (default: game_paths.DUMP_ROOT)")
    sub.add_parser("show")
    a = ap.parse_args(argv)
    if a.cmd == "show":
        try:
            print(open(reading_path(), encoding="utf-8").read())
            return 0
        except OSError as exc:
            print("could not look: %s" % exc)
            return COULD_NOT_LOOK
    if a.cmd == "tick":
        rc, r = tick(a.root)
        print("%s: %s" % (r["state"], r["why"]) + ("; %s" % r["build"] if r.get("build") else ""))
        return rc
    rc, line = check(a.root)
    print(line)
    return rc


if __name__ == "__main__":
    sys.exit(main())
