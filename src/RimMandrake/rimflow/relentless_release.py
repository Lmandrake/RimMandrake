#!/usr/bin/env python3
"""One pinned daily release of Relentless's own code, with a way back (RELENTLESS_BUILD_DAILY_RELEASE_WITH_ROLLBACK).

Owner card 2026-11-06 (Subtract plan). Before this the tick ran out of the books clone, which it fast-forwards itself, so
every push to main redeployed it (109 core commits that day) with no record and no way back. Design note, with the
boundary of what is pinned: design/RimMandrake/relentless_daily_release_2026-11-06.md.

    <root>/release/<sha12>/   a tree the tick runs from: every .py under rimflow, Utils and contracts plus the
                              relentless*.json limits, AT THE SHA; everything else a symlink into books, so a path the
                              code derives from its own file (ledger, items, mods, design, even .git) still reads live data
    <root>/release/current    symlink to one of them, swapped atomically; the units start from what it names at that moment
    <root>/release/log.jsonl  the record, append only: every release and rollback, {at, date, sha, id, kind, why, from}

The tick is a oneshot, so it needs no stop: one running keeps its own tree to the end and the next start takes the new one.

    relentless_release.py cut --daily                    one a day (rm-relentless-release.timer), from origin/main
    relentless_release.py cut --emergency --why "..."    a named early release; --sha picks a landed commit
    relentless_release.py rollback [--why "..."]         back to the release before this one; --dry-run plans and tests it
    relentless_release.py status                         what is pinned, what the tick is running, how far main has moved

Exit: 0 done, 1 refused (nothing changed), 2 usage.
"""
import argparse
import calendar
import contextlib
import fcntl
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

DEFAULT_ROOT = "/home/mandrake/rm/relentless"
RIMFLOW = "src/RimMandrake/rimflow/"
PINNED_DIRS = (RIMFLOW, "src/RimMandrake/Utils/", "src/RimMandrake/contracts/")
PINNED_FILES = ("src/RimMandrake/bridgetools/companion_identity.py",)     # bridgetools is mod tooling, but the tick imports this
# his pipeline-only pause is a switch he throws by a commit, not a limit: it must reach the tick at once
LIVE_FILES = (RIMFLOW + "relentless_owner_pause.json",)
KEEP = 7                # releases kept on the way back, beyond the current one
GONE_AFTER_S = 2 * 86400     # a tree off that list stays this long: a live round or exam unit may still be running in it
SMOKE_S = 300
ENTRY_POINTS = ("relentless", "relentless_wake", "relentless_jobs", "relentless_block", "relentless_live_round",
                "relentless_broker", "cli")


class Refused(Exception):
    pass


def is_pinned(path):
    if path in PINNED_FILES:
        return True
    if not path.startswith(PINNED_DIRS) or path in LIVE_FILES:
        return False
    if path.endswith(".py"):
        return True
    base = os.path.basename(path)
    return path.startswith(RIMFLOW) and os.path.dirname(path) + "/" == RIMFLOW and re.fullmatch(r"relentless.*\.json", base) is not None


def git(cwd, *args, check=True, stdin=None, text=True, timeout=300):
    r = subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=text, timeout=timeout, input=stdin)
    if check and r.returncode:
        raise Refused("git %s: %s" % (" ".join(args), (r.stderr if text else r.stderr.decode(errors="replace"))[:300]))
    return r


class Release:
    def __init__(self, root=None, clock=time.time, smoke=None, day=None):
        self.root = root or os.environ.get("RELENTLESS_ROOT") or DEFAULT_ROOT
        self.books = os.path.join(self.root, "books")
        self.dir = os.path.join(self.root, "release")
        self.current = os.path.join(self.dir, "current")
        self.logfile = os.path.join(self.dir, "log.jsonl")
        self.clock = clock
        self.smoke = smoke or smoke_tree
        self.day = day or (lambda t: time.strftime("%Y-%m-%d", time.localtime(t)))

    # ---- the record
    def log(self):
        try:
            with open(self.logfile, encoding="utf-8") as f:
                return [json.loads(ln) for ln in f if ln.strip()]
        except FileNotFoundError:
            return []

    def _record(self, **row):
        now = self.clock()
        row = dict({"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)), "date": self.day(now)}, **row)
        with open(self.logfile, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, sort_keys=True) + "\n")
            f.flush()
            os.fsync(f.fileno())
        return row

    def stack(self):
        """The way back, oldest first; the last is what is pinned. A release pushes, a rollback pops: the record is the
        only state, and rolling back twice walks further back rather than bouncing between two."""
        out = []
        for row in self.log():
            if row["kind"] == "rollback":
                while out and out[-1] != row["id"]:
                    out.pop()
            elif not out or out[-1] != row["id"]:
                out.append(row["id"])
        return out

    def pinned_id(self):
        try:
            return os.path.basename(os.readlink(self.current))
        except OSError:
            return None

    # ---- the tree
    def build(self, sha):
        """Make release/<sha12> unless it is there. -> its id. Written beside the target and renamed, so a tree that
        exists is whole."""
        rid = sha[:12]
        dest = os.path.join(self.dir, rid)
        if os.path.exists(os.path.join(dest, ".release.json")):
            return rid
        tmp = tempfile.mkdtemp(prefix=".build-", dir=self.dir)
        try:
            write_tree(self.books, sha, tmp)
            with open(os.path.join(tmp, ".release.json"), "w", encoding="utf-8") as f:
                json.dump({"sha": sha, "id": rid}, f)
            os.chmod(tmp, 0o755)
            if os.path.exists(dest):
                shutil.rmtree(dest)
            os.rename(tmp, dest)
        except BaseException:
            shutil.rmtree(tmp, ignore_errors=True)
            raise
        return rid

    def _swap(self, rid):
        """A reader of `current` sees the old tree or the new one. (ext4 can miss one lookup during the rename, measured; a
        tick starting in that instant fails and the timer starts the next 15 s later.)"""
        tmp = self.current + ".new.%d" % os.getpid()
        with contextlib.suppress(FileNotFoundError):
            os.unlink(tmp)
        os.symlink(rid, tmp)
        os.replace(tmp, self.current)
        fd = os.open(self.dir, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    def _prune(self):
        keep = set(self.stack()[-(KEEP + 1):])
        now = self.clock()
        rows = self.log()
        for name in os.listdir(self.dir):
            p = os.path.join(self.dir, name)
            if name.startswith(".build-") and now - os.path.getmtime(p) > GONE_AFTER_S:     # a build a crash left
                shutil.rmtree(p, ignore_errors=True)
                continue
            if name in keep or os.path.islink(p) or not os.path.isfile(os.path.join(p, ".release.json")):
                continue
            if now - self._left_at(rows, name, p) > GONE_AFTER_S:
                shutil.rmtree(p, ignore_errors=True)

    @staticmethod
    def _left_at(rows, name, path):
        """When nothing new could start in this tree any more: the row after its last one. A tree never released (it
        failed its smoke test) counts from its build."""
        last = max((i for i, r in enumerate(rows) if r.get("id") == name), default=None)
        if last is None or last + 1 >= len(rows):
            return os.path.getmtime(path) if last is None else float("inf")
        return calendar.timegm(time.strptime(rows[last + 1]["at"], "%Y-%m-%dT%H:%M:%SZ"))

    def _heal(self):
        """A crash between a swap and its row leaves `current` ahead of the record, and the way back must still work during
        the incident. `current` is the truth: an id on the way back is a rollback that lost its row, any other a release."""
        pinned = self.pinned_id()
        stack = self.stack()
        if not pinned or (stack and stack[-1] == pinned):
            return
        with open(os.path.join(self.dir, pinned, ".release.json"), encoding="utf-8") as f:
            sha = json.load(f)["sha"]
        self._record(kind="rollback" if pinned in stack else "repair", sha=sha, id=pinned, by=who(),
                     why="current moved without a row (crash between swap and record)", **{"from": stack[-1] if stack else None})

    def _locked(self):
        os.makedirs(self.dir, exist_ok=True)
        f = open(os.path.join(self.dir, ".lock"), "w")
        fcntl.flock(f, fcntl.LOCK_EX)
        return f

    # ---- the acts
    def cut(self, kind, why=None, sha=None, by=None):
        """kind daily | emergency. -> the row, or None when today's release is already out (a daily only)."""
        if kind == "emergency" and not (why or "").strip():
            raise Refused("an emergency release names its reason (--why)")
        with self._locked():
            self._heal()
            if kind == "daily" and self._released_today():
                return None
            # the tick is what fetches books, and a dead tick is when this is needed most; a failed fetch leaves origin/main
            git(self.books, "fetch", "--quiet", "origin", check=False)
            head = git(self.books, "rev-parse", "origin/main").stdout.strip()
            sha = git(self.books, "rev-parse", "--verify", (sha or head) + "^{commit}").stdout.strip()
            if git(self.books, "merge-base", "--is-ancestor", sha, head, check=False).returncode:
                raise Refused("%s is not on origin/main: only landed code is released" % sha[:12])
            rid = self.build(sha)
            needs_test = rid != self.pinned_id()
        # outside the lock: a rollback must never wait on a test
        why_not = self.smoke(os.path.join(self.dir, rid), self.books) if needs_test else None
        if why_not:
            raise Refused("release %s fails its smoke test, the tick stays on %s: %s" % (rid, self.pinned_id(), why_not))
        with self._locked():
            self._heal()
            if kind == "daily" and self._released_today():     # a rollback during the test stands for the date
                return None
            before = self.pinned_id()
            if rid != before:
                self._swap(rid)
            row = self._record(kind=kind, sha=sha, id=rid, why=why or kind, by=by or who(), **{"from": before})
            self._prune()
            return row

    def _released_today(self):
        today = self.day(self.clock())
        return any(r["date"] == today for r in self.log())

    def rollback(self, why=None, dry_run=False, by=None):
        with self._locked():
            if not dry_run:
                self._heal()
            target, sha, pinned, left = self._way_back()
            if not dry_run:     # no test: the way back must not depend on anything that may be what broke
                self._swap(target)
                return self._record(kind="rollback", sha=sha, id=target, why=why or "rollback", by=by or who(), **{"from": pinned})
        why_not = self.smoke(os.path.join(self.dir, target), self.books)
        if why_not:
            raise Refused("release %s fails its smoke test: %s" % (target, why_not))
        return {"dry_run": True, "from": pinned, "id": target, "sha": sha, "smoke": "ok", "way_back_left": left}

    def _way_back(self):
        stack = self.stack()
        pinned = self.pinned_id()
        if not stack:
            raise Refused("nothing recorded in %s" % self.logfile)
        if len(stack) < 2:
            raise Refused("no earlier release to go back to (%s is the first)" % pinned)
        target = stack[-2]
        try:
            with open(os.path.join(self.dir, target, ".release.json"), encoding="utf-8") as f:
                return target, json.load(f)["sha"], pinned, len(stack) - 2
        except (OSError, ValueError, KeyError) as e:
            raise Refused("release %s cannot be read: %s" % (target, e)) from e

    def status(self):
        rid = self.pinned_id()
        rows = [r for r in self.log() if r.get("id") == rid]
        last = rows[-1] if rows else {}
        out = {"pinned": rid, "sha": last.get("sha"), "date": last.get("date"), "kind": last.get("kind"),
               "way_back": self.stack()[:-1][-KEEP:], "tick": tick_reading()}
        behind = git(self.books, "rev-list", "--count", "%s..origin/main" % last["sha"], check=False) if last else None
        out["main_ahead_by"] = int(behind.stdout) if behind is not None and behind.returncode == 0 else None
        return out


def who():
    return os.environ.get("RIMFLOW_SEAT") or os.environ.get("AGENT_SEAT") or "unattended"


def write_tree(books, sha, dest):
    """Pinned files at the sha; every sibling of a pinned path a symlink to the same path in books. Children of a real
    directory are the union of the sha's tree and the books working tree, so an ignored or untracked thing there (Transient/,
    .git) is still seen."""
    out = git(books, "ls-tree", "-r", "-z", "--full-tree", sha, text=False).stdout.decode("utf-8", "surrogateescape")
    tracked, blobs = [], []
    for rec in filter(None, out.split("\0")):
        meta, path = rec.split("\t", 1)
        mode, kind, blob = meta.split()
        tracked.append(path)
        if kind == "blob" and is_pinned(path):
            blobs.append((path, mode, blob))
    if not any(p == RIMFLOW + "relentless.py" for p, _, _ in blobs):
        raise Refused("%s holds no %srelentless.py" % (sha[:12], RIMFLOW))
    real_dirs = {""}
    for path, _, _ in blobs:
        d = os.path.dirname(path)
        while d and d not in real_dirs:
            real_dirs.add(d)
            d = os.path.dirname(d)
    children = {}
    for path in tracked:
        parts = path.split("/")
        for i in range(len(parts)):
            d = "/".join(parts[:i])
            if d in real_dirs:
                children.setdefault(d, set()).add(parts[i])
    pinned = {p for p, _, _ in blobs}
    for d in sorted(real_dirs):
        os.makedirs(os.path.join(dest, d), exist_ok=True)
        names = set(children.get(d, ()))
        try:
            names.update(os.listdir(os.path.join(books, d)))
        except FileNotFoundError:
            pass
        for name in sorted(names - {"__pycache__", ".pytest_cache"}):
            rel = os.path.join(d, name) if d else name
            # a path pinnable but not at this sha (an older --sha, an untracked .py) stays absent, as it was at the sha
            if rel in pinned or rel in real_dirs or is_pinned(rel):
                continue
            os.symlink(os.path.join(books, rel), os.path.join(dest, rel))
    for rel in LIVE_FILES:      # even absent today (no file means off): a later commit that restores it must still reach the tick
        if not os.path.lexists(os.path.join(dest, rel)):
            os.symlink(os.path.join(books, rel), os.path.join(dest, rel))
    feed = "".join(b + "\n" for _, _, b in blobs).encode()
    p = subprocess.run(["git", "-C", books, "cat-file", "--batch"], input=feed, capture_output=True, timeout=300)
    if p.returncode:
        raise Refused("git cat-file: %s" % p.stderr.decode(errors="replace")[:300])
    data, at = p.stdout, 0
    for path, mode, blob in blobs:
        nl = data.index(b"\n", at)
        head = data[at:nl].split()
        if len(head) != 3 or head[0].decode() != blob:
            raise Refused("git cat-file gave %r for %s" % (data[at:nl][:80], path))
        size = int(head[2])
        target = os.path.join(dest, path)
        with open(target, "wb") as f:
            f.write(data[nl + 1:nl + 1 + size])
        if mode == "100755":
            os.chmod(target, 0o755)
        at = nl + 1 + size + 1


def smoke_tree(tree, books):
    """-> None, or why this tree must not take the tick: its entry points import from the tree itself, the tree finds the
    real books, and one real tick runs on a scratch root (selftest_relentless_tick_once)."""
    here = os.path.join(tree, RIMFLOW)
    # the tree's own: PYTHONPATH may name a clone, and a module found there would prove nothing about this tree
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "CLAUDE_PROJECT_DIR", "RELENTLESS_ROOT")}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    code = ("import sys, os; sys.path.insert(0, %r)\n"
            "for n in %r:\n"
            "    m = __import__(n)\n"
            "    f = os.path.abspath(m.__file__)\n"
            "    assert f.startswith(%r), (n, f)\n"
            "import relentless_live\n"
            "print(relentless_live.BOOKS)\n") % (here.rstrip("/"), ENTRY_POINTS, tree.rstrip("/") + "/")
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=here, env=env, capture_output=True, text=True,
                           timeout=SMOKE_S, stdin=subprocess.DEVNULL)
        if r.returncode:
            return "imports: %s" % r.stderr.strip()[-400:]
        if os.path.realpath(r.stdout.strip().splitlines()[-1]) != os.path.realpath(books):
            return "the tree reads its data from %s, not %s" % (r.stdout.strip()[-200:], books)
        once = os.path.join(here, "selftest_relentless_tick_once.py")
        r = subprocess.run([sys.executable, once], cwd=here, env=env, capture_output=True, text=True, timeout=SMOKE_S,
                           stdin=subprocess.DEVNULL)
        if r.returncode:
            return "one scratch tick: %s" % r.stdout.strip()[-400:]
    except subprocess.TimeoutExpired as e:
        return "timed out after %s s: %s" % (SMOKE_S, e.cmd[1][:60])
    return None


def tick_reading():
    """What a tick in progress is running, read from the process itself; None between ticks or where there is no unit."""
    try:
        pid = subprocess.run(["systemctl", "--user", "show", "rm-relentless.service", "-p", "MainPID", "--value"],
                             capture_output=True, text=True, timeout=30).stdout.strip()
        if not pid or pid == "0":
            return None
        with open("/proc/%s/cmdline" % pid, "rb") as f:
            argv = f.read().decode(errors="replace").split("\0")
        return {"pid": int(pid), "script": argv[1] if len(argv) > 1 else None}
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("cut")
    g = c.add_mutually_exclusive_group(required=True)
    g.add_argument("--daily", action="store_true")
    g.add_argument("--emergency", action="store_true")
    c.add_argument("--why")
    c.add_argument("--sha")
    b = sub.add_parser("rollback")
    b.add_argument("--why")
    b.add_argument("--dry-run", action="store_true")
    sub.add_parser("status")
    a = ap.parse_args(argv)
    rel = Release()
    try:
        if a.cmd == "cut":
            if a.daily and a.sha:
                raise Refused("a daily release is origin/main; --sha is for --emergency")
            row = rel.cut("daily" if a.daily else "emergency", why=a.why, sha=a.sha)
            print(json.dumps(row, sort_keys=True) if row else "today's release is already out")
        elif a.cmd == "rollback":
            print(json.dumps(rel.rollback(why=a.why, dry_run=a.dry_run), sort_keys=True))
        else:
            print(json.dumps(rel.status(), sort_keys=True))
    except (Refused, OSError, subprocess.SubprocessError) as e:
        print("REFUSED %s" % e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
