#!/usr/bin/env python3
"""role_clones.py — every Dispatcher role and the art daemon work in a clone of their own, never the seat clone.

RIMMANDRAKE_MOVE_SEAT_CLONE_WRITERS_INTO_OWN_POOL_CLONES (measured 2026-11-16): all role rows of
dispatcher_schedule.json and rm-artpiped.service ran in /home/mandrake/rm/bench, the Conductor's seat clone, and their
writes were most of the 150 dirty paths found there. Each role (roles[].name) and the art daemon (`artpiped`) now has
one long-lived clone ROOT/<name>, like /home/mandrake/rm/dispatch. Long-lived, not a per-run pool clone: the Designer
harvest and stage chain read a run's concept files from the role's clone after its unit has ended, and the next run of
the stage machine continues there.

  made     `role_clones.py ensure <name>...` (scratch_clone.py clone --dissociate: an independent copy, outside the
           pool and its cap), built under ROOT/.making-<name> and renamed into place, so no launch sees a half clone.
           A launch whose clone is missing starts that in a unit of its own (make_in_background: a clone takes
           26-153 s, past any beat) and waits as a planned hold (MAKING:), never an alarm; a make that FAILED is a
           launch failure naming it (RIMMANDRAKE_TRACE_DESIGNER_ROLE_CLONE_VANISHED_OPERATIONS_FAILS: the six disabled
           roles' clones were removed by hand 2026-11-18, and the Designer still runs by run-now).
  level    before systemd-run, role_launch.launch runs `level`: a commit the clone holds that is not on origin/main
           is landed with land.sh when it is ledger-only, and otherwise the launch is refused `STRANDED:` with the
           one fix line (dispatcher: ONE role:<name>:not_running alarm). Then the unit's first step is `./sync` in its
           clone (role_launch.launch_argv); a failed sync ends the unit SYNC_FAILED_EXIT before any pre-step or model
           starts: a role never runs stale code. RIMMANDRAKE_LAND_STRANDED_ROLE_COMMIT_OPERATIONS_DEAD_FOUR_HOURS
           (2026-11-19): a run's bare `git commit` of its shard made ./sync refuse every Operations launch for 4 h.
  landed   the unit's ExecStopPost runs `role_clones.py land --clone C --seat S` in its own transient unit: the safe
           classes of seat_dirt.py (conversation records, filed item prose) and the seat's ledger shard are published
           from the clone, and `level` lands a shard the run committed without publishing. ops_watch's disk.seat_dirt counts and tidies every role clone with the seat clone, so any
           other dirt alarms after an hour, naming its clone.
  carried  wrapup.py treats a role clone as carried, like the seat clone: it lives on between runs.

    role_clones.py ensure NAME...          make the missing clones (prints each path, or why it failed)
    role_clones.py land --clone C --seat S publish what the run left (one JSON line; exit 1 on a failure)
    role_clones.py level --clone C         land a stranded ledger-only commit (one JSON line; exit 1 unless level)
    role_clones.py list                    one JSON line per role clone on disk
"""
import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(os.path.dirname(HERE), "Utils")
ROOT = os.environ.get("RM_ROLE_CLONE_ROOT", "/home/mandrake/rm/roles")     # = seat_dirt.ROLE_CLONE_ROOT
LAND_SH = os.path.join(UTILS, "land.sh")
SEAT_SYNC = os.path.join(UTILS, "seat_sync.py")
SHARD_RE = re.compile(r"^infrastructure/state/ledger/events/[^/]+\.jsonl$")
STRANDED = "STRANDED:"      # a launch refused by level starts with it; the dispatcher alarms role:<name>:not_running
SYNC_FAILED_EXIT = 75       # EX_TEMPFAIL: the clone could not be levelled; nothing ran (a system failure, not a trial)
MAKING = "MAKING:"          # a launch held while its missing clone is made (make_in_background): a planned hold
MAKER_PREFIX = "rm-role-clone-"
PART_PREFIX = ".making-"    # NAME_RE refuses the dot: a clone being made is never a role clone (is_role_clone, existing)
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


def part_of(name):
    """Where ensure builds the clone of `name` before it renames it into place."""
    clone_of(name)
    return os.path.join(ROOT, PART_PREFIX + name)


def maker_unit(name):
    """The systemd unit that makes the clone of `name`: one at a time per role (systemd refuses a second)."""
    clone_of(name)
    return MAKER_PREFIX + name.lower()


def maker_log(name):
    return os.path.join(ROOT, ".%s.making.log" % name)


def ensure(name, runner=subprocess.run):
    """-> (ok, path or why). Makes ROOT/<name> when absent; an existing clone is left as it is (the unit syncs it).
    Built at part_of(name), then renamed: a make killed half-way leaves only the part, which the next make removes
    (only ensure writes there, under its lock)."""
    dest = clone_of(name)
    if os.path.isdir(os.path.join(dest, ".git")):
        return True, dest
    if os.path.exists(dest):
        return False, "%s exists but is not a git clone: look at it before removing it" % dest
    os.makedirs(ROOT, exist_ok=True)
    part = part_of(name)
    import fcntl   # here, not at the top: wrapup.py imports this module under Windows python.exe, which has no fcntl
    with open(part + ".lock", "w") as lk:
        try:
            fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return False, "another make of %s is running (lock %s.lock)" % (name, part)
        if os.path.isdir(os.path.join(dest, ".git")):
            return True, dest
        shutil.rmtree(part, ignore_errors=True)
        env = dict(os.environ, RM_SCRATCH_ROOT=os.path.dirname(ROOT), RM_SEAT=os.path.basename(ROOT))
        r = runner(["python3", os.path.join(UTILS, "scratch_clone.py"), "clone", "role clone for " + name, "--name",
                    os.path.basename(part), "--checkout", "--fetch", "--dissociate"], env=env, capture_output=True,
                   text=True, timeout=10800, stdin=subprocess.DEVNULL)  # budget: class=launch
        if r.returncode or not os.path.isdir(os.path.join(part, ".git")):
            shutil.rmtree(part, ignore_errors=True)
            return False, "scratch_clone failed (exit %d): %s" % (
                r.returncode, ((r.stdout or "") + (r.stderr or "")).strip())
        os.rename(part, dest)
    return True, dest


def _last_line(path):
    """The maker log's last line; None only when there is no log (no make has run). Any other read error raises: an
    unreadable log is never "no failed make" (the dispatcher's launch failure names it)."""
    if not os.path.lexists(path):
        return None
    with open(path, encoding="utf-8", errors="replace") as f:
        lines = [ln.strip() for ln in f if ln.strip()]
    return lines[-1] if lines else None


def make_in_background(name, runner=subprocess.run):
    """-> (kind, text): "ready" (the clone stands; text = its path), "making" (its maker unit was started or is already
    running: text starts MAKING:, a planned hold), or "failed" (a launch failure, its cause named: the path stands but
    is no clone, the maker unit could not start, or the last make FAILED; a new make is started all the same)."""
    dest = clone_of(name)
    if missing_why(dest) is None:
        return "ready", dest
    if os.path.exists(dest):
        return "failed", "role clone %s exists but is not a git clone: look at it before removing it" % dest
    os.makedirs(ROOT, exist_ok=True)
    log, unit = maker_log(name), maker_unit(name)
    last = _last_line(log)
    argv = ["systemd-run", "--user", "--quiet", "--collect", "--unit", unit,
            "-p", "StandardOutput=append:" + log, "-p", "StandardError=append:" + log,
            "--", "/usr/bin/python3", os.path.abspath(__file__), "ensure", name]
    try:
        # budget: danger=a hung systemd-run holds the launch of a role; never reached in the 14 days to 2026-11-24; no record of
        # budget: its run
        r = runner(argv, capture_output=True, text=True, timeout=30, stdin=subprocess.DEVNULL)
    except Exception as e:  # noqa: BLE001 - one answer, its cause named
        return "failed", "role clone %s is missing and its maker unit %s did not start: %s: %s" % (
            dest, unit, type(e).__name__, str(e))
    said = ((r.stdout or "") + (r.stderr or "")).strip()
    if r.returncode and "already" not in said:
        return "failed", "role clone %s is missing and its maker unit %s did not start (systemd-run exit %d: %s)" % (
            dest, unit, r.returncode, said)
    if last and last.startswith("FAILED"):
        return "failed", "role clone %s is missing: its last make said %s (log %s); unit %s makes it again" % (
            dest, last, log, unit)
    return "making", "%s role clone %s is missing: unit %s is making it (log %s); the launch waits for it" % (
        MAKING, dest, unit, log)


def _tidy(clone, settle_min):
    sys.path.insert(0, UTILS)
    import seat_dirt
    return seat_dirt.tidy(clone, settle_min=settle_min)


# budget: danger=a hung git holds the launch of a role; never reached in the 14 days to 2026-11-24; no record of its run
def _git(clone, *a, timeout=300):
    return subprocess.run(["git", "-C", clone] + list(a), capture_output=True, text=True, timeout=timeout,
                          stdin=subprocess.DEVNULL)


def fix_line(clone, rows):
    """The one shell line that lands each stranded commit (in order) and then levels the clone. --superseded names each
    commit the line just landed: seat_sync cannot always prove a twin by its bytes (a union shard plus a file origin
    changed since), and then refused the levelling (Operations, 2026-11-21)."""
    env = "LAND_REPO=%s" % shlex.quote(clone)
    lands = ["%s sh %s %s %s" % (env, shlex.quote(LAND_SH), r["sha"][:12], " ".join(shlex.quote(t) for t in r["touched"]))
             for r in rows]
    return " && ".join(lands + ["python3 %s --repo %s%s" % (
        shlex.quote(SEAT_SYNC), shlex.quote(clone),
        "".join(" --superseded %s" % r["sha"][:12] for r in rows))])


def level(clone, land_sh=None):
    """Land what a role clone holds that is not on origin/main, when that is safe. -> {"state", "landed", "left", "fix",
    "why"}; never raises. state: "level" (HEAD is origin/main: nothing was ahead of the clone's own origin/main ref, no
    fetch made; or all that was ahead was already on origin and seat_sync moved the clone) · "landed" (every stranded
    commit was ledger-only, is now published with land.sh <sha> <paths>, and the clone moved) · "stranded" (a commit
    that is not ledger-only, a merge, or one land.sh refused, stays; or seat_sync could not move the clone past commits
    already on origin; `fix` is the line that passes) · "UNMEASURED" (a git read or the fetch failed: could not look,
    never "level")."""
    out = {"clone": clone, "state": None, "landed": [], "left": [], "fix": None, "why": None}
    tool = land_sh or LAND_SH
    try:
        r = _git(clone, "rev-list", "refs/remotes/origin/main..HEAD", timeout=60)
        if r.returncode:
            return dict(out, state="UNMEASURED", why="git rev-list exit %d: %s" % (r.returncode, r.stderr.strip()))
        if not r.stdout.strip():
            return dict(out, state="level")
        f = _git(clone, "fetch", "-q", "origin")
        if f.returncode:
            return dict(out, state="UNMEASURED", why="git fetch exit %d: %s" % (f.returncode, f.stderr.strip()))
        sys.path.insert(0, UTILS)
        import seat_sync
        g = seat_sync.Git(clone)
        refused, done = {}, []
        for row in seat_sync.unlanded(g):
            if len(row["parents"]) != 1 or not row["touched"] or not all(SHARD_RE.match(t) for t in row["touched"]):
                continue
            p = subprocess.run(["sh", tool, row["sha"]] + row["touched"], cwd=clone, capture_output=True, text=True,
                               timeout=21600, stdin=subprocess.DEVNULL, env=dict(os.environ, LAND_REPO=clone))  # budget: class=publish
            m = re.search(r"PUBLISHED ([0-9a-f]{7,40})", p.stdout or "")
            if p.returncode or not m:
                refused[row["sha"]] = "land.sh exit %d: %s" % (p.returncode, ((p.stdout or "") + (p.stderr or "")).strip())
            else:
                out["landed"].append(m.group(1))
                done.append(row["sha"])
        if out["landed"]:
            _git(clone, "fetch", "-q", "origin")
        # Move the clone whenever all it holds ahead is on origin: a twin that ./publish landed while it left the
        # branch unmoved ("LANDED, CLONE NOT MOVED") is not unlanded, so the clone stayed ahead and read "level"
        # (RIMMANDRAKE_TRACE_DESIGNER_TWIN_COMMIT_LAND_SAID_LEVEL, the Designer clone, 2026-11-21).
        sync_said = None
        if out["landed"] or not seat_sync.unlanded(seat_sync.Git(clone)):
            s = subprocess.run(["python3", SEAT_SYNC, "--no-fetch", "--repo", clone]
                               + sum((["--superseded", c] for c in done), []),
                               # budget: danger=a hung seat_sync holds the launch of a role; never reached in the 14 days
                               # budget: to 2026-11-24; no record of its run
                               capture_output=True, text=True, timeout=600, stdin=subprocess.DEVNULL)
            sync_said = ((s.stdout or "") + (s.stderr or "")).strip()
        left = seat_sync.unlanded(seat_sync.Git(clone))
        ahead = _git(clone, "rev-list", "--reverse", "refs/remotes/origin/main..HEAD")   # _git's hang guard
        if ahead.returncode:
            return dict(out, state="UNMEASURED", why="git rev-list exit %d: %s" % (ahead.returncode, ahead.stderr.strip()))
    except Exception as e:  # noqa: BLE001 - one JSON answer, its cause named
        return dict(out, state="UNMEASURED", why="%s: %s" % (type(e).__name__, str(e)))
    out["left"] = [{"sha": r["sha"], "subject": r["subject"], "paths": r["touched"]} for r in left]
    if not left and ahead.stdout.strip():
        shas = ahead.stdout.split()
        out["fix"] = "python3 %s --repo %s%s" % (shlex.quote(SEAT_SYNC), shlex.quote(clone),
                                                 "".join(" --superseded %s" % c[:12] for c in shas))
        out["why"] = ("%d commit(s) ahead of origin/main are already on it, but seat_sync did not move the clone: %s"
                      % (len(shas), sync_said or "seat_sync did not run"))
        return dict(out, state="stranded")
    if not left:
        return dict(out, state="landed" if out["landed"] else "level")
    out["fix"] = fix_line(clone, left)
    out["why"] = "%d commit(s) not on origin/main that are not ledger-only: %s" % (
        len(left), "; ".join("%s%s" % (r["subject"], " (%s)" % refused[r["sha"]] if r["sha"] in refused else "")
                             for r in left))
    return dict(out, state="stranded")


def land(clone, seat, runner=subprocess.run, tidy=_tidy, exists=os.path.isdir, leveller=None):
    """Publish what a finished run left in its role clone. -> {"ok", "tidy", "shard", "why"}; never raises.
    The shard goes first: an item the run filed is "filed on origin" only once its `file` event is there, and only then
    is its prose a safe class. The unit has stopped, so nothing is mid-write: the safe classes land at settle 0.
    Anything else stays and is counted by ops_watch's disk.seat_dirt after an hour."""
    out = {"clone": clone, "seat": seat, "ok": True, "tidy": None, "shard": None, "level": None, "why": None}
    if not exists(os.path.join(clone, ".git")):
        return dict(out, ok=False, why="role clone %s is missing: nothing could be landed" % clone)
    shard = "infrastructure/state/ledger/events/%s.jsonl" % seat
    try:
        r = runner(["git", "status", "--porcelain", "--", shard], cwd=clone, capture_output=True, text=True, timeout=60)
        if r.returncode:
            out.update(ok=False, shard="UNMEASURED: git status exit %d: %s" % (r.returncode, (r.stderr or "").strip()))
        elif not (r.stdout or "").strip():
            out["shard"] = "clean"
        else:
            p = runner(["./publish", "-m", "ledger: %s role run (role clone %s)" % (seat, os.path.basename(clone)), shard],
                       cwd=clone, capture_output=True, text=True, timeout=21600, stdin=subprocess.DEVNULL)  # budget: class=publish
            said = ((p.stdout or "") + (p.stderr or "")).strip()
            m = re.search(r"PUBLISHED ([0-9a-f]{7,40})", said)
            if p.returncode or not m:
                out.update(ok=False, shard="FAILED: publish exit %d: %s" % (p.returncode, said))
            else:
                out["shard"] = "PUBLISHED " + m.group(1)
    except Exception as e:  # noqa: BLE001 - a timeout or OSError is a failure with its cause, still one JSON line
        out.update(ok=False, shard="FAILED: %s: %s" % (type(e).__name__, str(e)))
    # a shard the run committed but never published reads clean above: level lands it, and names any other strand
    # (a test's fake runner gets no real git on a real clone unless it passes its own leveller)
    lv = (leveller or (level if runner is subprocess.run else lambda c: {"state": "skipped"}))(clone)
    out["level"] = lv["state"] + (": " + lv["why"] if lv.get("why") else "") + (
        "; to pass: " + lv["fix"] if lv.get("fix") else "")
    if lv["state"] in ("stranded", "UNMEASURED"):
        out["ok"] = False
    try:
        out["tidy"] = tidy(clone, 0)
    except Exception as e:  # noqa: BLE001 - said in the result
        out.update(ok=False, tidy="FAILED: %s" % str(e))
    if not out["ok"]:
        out["why"] = "; ".join(x for x in (out["shard"], out["level"], out["tidy"])
                               if x and ("FAILED" in x or "UNMEASURED" in x or x.startswith("stranded")))
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
    vp = sub.add_parser("level")
    vp.add_argument("--clone", required=True)
    sub.add_parser("list")
    a = ap.parse_args(argv)
    if a.cmd == "level":
        res = level(a.clone)
        print(json.dumps(res))
        return 0 if res["state"] in ("level", "landed") else 1
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
