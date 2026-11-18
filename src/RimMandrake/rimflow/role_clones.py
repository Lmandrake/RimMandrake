#!/usr/bin/env python3
"""role_clones.py — every Dispatcher role and the art daemon work in a clone of their own, never the seat clone.

RIMMANDRAKE_MOVE_SEAT_CLONE_WRITERS_INTO_OWN_POOL_CLONES (measured 2026-11-16): all role rows of
dispatcher_schedule.json and rm-artpiped.service ran in /home/mandrake/rm/bench, the Conductor's seat clone, and their
writes were most of the 150 dirty paths found there. Each role (roles[].name) and the art daemon (`artpiped`) now has
one long-lived clone ROOT/<name>, like /home/mandrake/rm/dispatch. Long-lived, not a per-run pool clone: the Designer
harvest and stage chain read a run's concept files from the role's clone after its unit has ended, and the next run of
the stage machine continues there.

  made     `role_clones.py ensure <name>...` (scratch_clone.py clone --dissociate: an independent copy, outside the
           pool and its cap). role_launch.launch refuses a launch whose clone is missing, naming this command.
  level    the unit's first step is `./sync` in its clone (role_launch.launch_argv); a failed sync ends the unit
           SYNC_FAILED_EXIT before any pre-step or model starts: a role never runs stale code.
  landed   the unit's ExecStopPost runs `role_clones.py land --clone C --seat S` in its own transient unit: the safe
           classes of seat_dirt.py (conversation records, filed item prose) and the seat's ledger shard are published
           from the clone. ops_watch's disk.seat_dirt counts and tidies every role clone with the seat clone, so any
           other dirt alarms after an hour, naming its clone.
  carried  wrapup.py treats a role clone as carried, like the seat clone: it lives on between runs.

    role_clones.py ensure NAME...          make the missing clones (prints each path, or why it failed)
    role_clones.py land --clone C --seat S publish what the run left (one JSON line; exit 1 on a failure)
    role_clones.py list                    one JSON line per role clone on disk
"""
import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(os.path.dirname(HERE), "Utils")
ROOT = os.environ.get("RM_ROLE_CLONE_ROOT", "/home/mandrake/rm/roles")     # = seat_dirt.ROLE_CLONE_ROOT
SYNC_FAILED_EXIT = 75       # EX_TEMPFAIL: the clone could not be levelled; nothing ran (a system failure, not a trial)
NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")


def clone_of(name):
    """The clone of role (or daemon) `name`."""
    if not NAME_RE.match(name or ""):
        raise ValueError("not a role name: %r" % (name,))
    return os.path.join(ROOT, name)


def is_role_clone(path):
    """True for ROOT/<name> itself (not a path inside one)."""
    if not path:
        return False
    p = os.path.normpath(os.path.abspath(path))
    return os.path.dirname(p) == os.path.normpath(os.path.abspath(ROOT)) and bool(NAME_RE.match(os.path.basename(p)))


def missing_why(path):
    """None when the role clone stands, else the refusal (with the command that makes it)."""
    if os.path.isdir(os.path.join(path, ".git")):
        return None
    return ("role clone %s is missing: make it with python3 src/RimMandrake/rimflow/role_clones.py ensure %s"
            % (path, os.path.basename(os.path.normpath(path))))


def ensure(name, runner=subprocess.run):
    """-> (ok, path or why). Makes ROOT/<name> when absent; an existing clone is left as it is (the unit syncs it)."""
    dest = clone_of(name)
    if os.path.isdir(os.path.join(dest, ".git")):
        return True, dest
    if os.path.exists(dest):
        return False, "%s exists but is not a git clone: look at it before removing it" % dest
    env = dict(os.environ, RM_SCRATCH_ROOT=os.path.dirname(ROOT), RM_SEAT=os.path.basename(ROOT))
    r = runner(["python3", os.path.join(UTILS, "scratch_clone.py"), "clone", "role clone for " + name, "--name", name,
                "--checkout", "--fetch", "--dissociate"], env=env, capture_output=True, text=True, timeout=1800,
               stdin=subprocess.DEVNULL)
    if r.returncode or not os.path.isdir(os.path.join(dest, ".git")):
        return False, "scratch_clone failed (exit %d): %s" % (r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()[-400:])
    return True, dest


def _tidy(clone, settle_min):
    sys.path.insert(0, UTILS)
    import seat_dirt
    return seat_dirt.tidy(clone, settle_min=settle_min)


def land(clone, seat, runner=subprocess.run, tidy=_tidy, exists=os.path.isdir):
    """Publish what a finished run left in its role clone. -> {"ok", "tidy", "shard", "why"}; never raises.
    The shard goes first: an item the run filed is "filed on origin" only once its `file` event is there, and only then
    is its prose a safe class. The unit has stopped, so nothing is mid-write: the safe classes land at settle 0.
    Anything else stays and is counted by ops_watch's disk.seat_dirt after an hour."""
    out = {"clone": clone, "seat": seat, "ok": True, "tidy": None, "shard": None, "why": None}
    if not exists(os.path.join(clone, ".git")):
        return dict(out, ok=False, why="role clone %s is missing: nothing could be landed" % clone)
    shard = "infrastructure/state/ledger/events/%s.jsonl" % seat
    try:
        r = runner(["git", "status", "--porcelain", "--", shard], cwd=clone, capture_output=True, text=True, timeout=60)
        if r.returncode:
            out.update(ok=False, shard="UNMEASURED: git status exit %d: %s" % (r.returncode, (r.stderr or "").strip()[:200]))
        elif not (r.stdout or "").strip():
            out["shard"] = "clean"
        else:
            p = runner(["./publish", "-m", "ledger: %s role run (role clone %s)" % (seat, os.path.basename(clone)), shard],
                       cwd=clone, capture_output=True, text=True, timeout=600, stdin=subprocess.DEVNULL)
            said = ((p.stdout or "") + (p.stderr or "")).strip()
            m = re.search(r"PUBLISHED ([0-9a-f]{7,40})", said)
            if p.returncode or not m:
                out.update(ok=False, shard="FAILED: publish exit %d: %s" % (p.returncode, said[-300:]))
            else:
                out["shard"] = "PUBLISHED " + m.group(1)
    except Exception as e:  # noqa: BLE001 - a timeout or OSError is a failure with its cause, still one JSON line
        out.update(ok=False, shard="FAILED: %s: %s" % (type(e).__name__, str(e)[:200]))
    try:
        out["tidy"] = tidy(clone, 0)
    except Exception as e:  # noqa: BLE001 - said in the result
        out.update(ok=False, tidy="FAILED: %s" % str(e)[:300])
    if not out["ok"]:
        out["why"] = "; ".join(x for x in (out["shard"], out["tidy"]) if x and ("FAILED" in x or "UNMEASURED" in x))
    return out


def existing():
    """Every role clone on disk (ROOT/<name> with a .git), sorted; [] when ROOT holds none."""
    try:
        names = sorted(os.listdir(ROOT))
    except FileNotFoundError:
        return []
    return [os.path.join(ROOT, n) for n in names if NAME_RE.match(n) and os.path.isdir(os.path.join(ROOT, n, ".git"))]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("ensure")
    e.add_argument("names", nargs="+")
    lp = sub.add_parser("land")
    lp.add_argument("--clone", required=True)
    lp.add_argument("--seat", required=True)
    sub.add_parser("list")
    a = ap.parse_args(argv)
    if a.cmd == "ensure":
        bad = 0
        for n in a.names:
            ok, said = ensure(n)
            print(("OK " if ok else "FAILED ") + said)
            bad += not ok
        return 1 if bad else 0
    if a.cmd == "land":
        res = land(a.clone, a.seat)
        print(json.dumps(res))
        return 0 if res["ok"] else 1
    rows = existing()
    for c in rows:
        print(json.dumps({"clone": c}))
    if not rows:
        print(json.dumps({"clones": [], "root": ROOT, "why": "no role clone on disk"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
