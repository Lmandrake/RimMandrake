#!/usr/bin/env python3
"""A selftest's own scratch dir, gone even when the run is killed (REAPER_FIX_OWN_SELFTEST_LITTERS_FAKE_SAVES).

selftest_scratch_reap.py plants fake CANONICAL_*.rws saves inside git clones. A run killed at its timeout skipped its
TemporaryDirectory cleanup, and the real reaper then refused every planted clone forever: 954 of 1104 refusals on
2026-11-03. `own_dir` registers the dir with its owner's pid and start time; SIGTERM/SIGHUP unwind through the cleanup,
and a run killed harder is removed by the next run of the same tag (`reap`). A dir is removed only when its marker file
holds exactly the registered identity and that process is gone: the reaper's canonical guard is never asked to bend.

`legacy_litter` finds the dirs runs left before this existed, by the selftest's own fixture shape; `--apply` removes
the ones nothing uses. Report only by default, and report mode changes nothing (an unreadable fixture dir reads KEEP).
"""
import argparse
import atexit
import contextlib
import json
import os
import re
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

MARK = ".selftest_own_dir"


def registry() -> Path:
    return Path(os.environ.get("SELFTEST_OWN_DIRS_REG")
                or Path(os.environ.get("XDG_STATE_HOME") or Path.home() / ".local/state") / "rm-selftest-own-dirs")


GONE = "gone"


def proc_start(pid: int) -> str | None:
    """Field 22 of /proc/<pid>/stat: the start time that tells a reused pid from the one we recorded. GONE = no such
    process; None = it could not be read, which proves nothing."""
    try:
        with open(f"/proc/{pid}/stat", encoding="utf-8", errors="replace") as f:
            return f.read().rpartition(")")[2].split()[19]
    except (FileNotFoundError, ProcessLookupError):
        return GONE
    except (OSError, IndexError):
        return None


def alive(ident: dict) -> bool:
    """False only when the recorded process is provably gone: no such pid, or that pid now has another start time."""
    try:
        pid, want = int(ident["pid"]), ident["start"]
        start = proc_start(pid)
    except (KeyError, TypeError, ValueError, OverflowError):
        return True                                   # unreadable identity: keep, never guess
    if start == GONE:
        return False
    return start is None or want is None or want == GONE or start == want


def force_rm(p: Path) -> None:
    """The selftest chmods fixtures unreadable on purpose; rmtree alone leaves them."""
    shutil.rmtree(p, ignore_errors=True)
    if os.path.lexists(p):
        subprocess.run(["chmod", "-R", "u+rwx", str(p)], capture_output=True)
        shutil.rmtree(p, ignore_errors=True)


def reap(tag: str) -> list[str]:
    """Remove the dirs of earlier `tag` runs whose process is gone. Returns the removed paths."""
    removed = []
    for entry in sorted((registry() / tag).glob("*.json")):
        try:
            ident = json.loads(entry.read_text())
            if not isinstance(ident, dict) or not isinstance(ident.get("path"), str) or alive(ident):
                continue
            p = Path(ident["path"])
        except (OSError, ValueError):
            continue
        try:
            ours = p.is_absolute() and not p.is_symlink() and p.is_dir() and json.loads((p / MARK).read_text()) == ident
        except (OSError, ValueError):
            ours = False
        if ours:
            force_rm(p)
            if os.path.lexists(p):
                continue                              # could not remove it: try again next run
            removed.append(str(p))
        entry.unlink(missing_ok=True)                 # a dir not holding our identity is not ours to touch
    return removed


@contextlib.contextmanager
def own_dir(tag: str, dir: str | None = None):
    """A TemporaryDirectory that a killed run cannot strand. Yields the path as a str."""
    reap(tag)
    d = Path(tempfile.mkdtemp(prefix=f"selftest_{tag}_", dir=dir))
    ident = {"pid": os.getpid(), "start": proc_start(os.getpid()), "path": str(d), "tag": tag}
    (d / MARK).write_text(json.dumps(ident))
    reg = registry() / tag
    reg.mkdir(parents=True, exist_ok=True)
    entry = reg / f"{d.name}.json"
    entry.write_text(json.dumps(ident))
    saved = {}
    if threading.current_thread() is threading.main_thread():
        def unwind(sig, _frame):
            raise SystemExit(128 + sig)
        for s in (signal.SIGTERM, signal.SIGHUP):
            saved[s] = signal.signal(s, unwind)
    try:
        yield str(d)
    finally:
        for s, h in saved.items():
            signal.signal(s, h)
        force_rm(d)
        if not os.path.lexists(d):
            entry.unlink(missing_ok=True)


_RUN_DIRS = []


def own_dir_for_run(tag: str) -> str:
    """own_dir for a whole selftest process: tempfile.tempdir and TMPDIR point into it, so every bare mkdtemp of the
    run (and of its children) lands inside, and it goes at exit, on SIGTERM/SIGHUP, or at the next run of `tag`.
    Built for selftests that mkdtemp freely and never clean up (SELFTEST_LITTER_FIX_SEED_WALL_STRAGGLERS)."""
    stack = contextlib.ExitStack()
    d = stack.enter_context(own_dir(tag))
    _RUN_DIRS.append(stack)
    atexit.register(stack.close)
    tempfile.tempdir = d
    for k in ("TMPDIR", "TMP", "TEMP"):
        os.environ[k] = d
    return d


# --- the litter left before own_dir: found by the fixture's shape, never by a name alone ---------------------------

SHAPES = ({"origin.git", "archive", "live_elsewhere"},                         # selftest_scratch_reap.py run()
          {"archive_tags", "corpus", "origin", "r_tags", "state", "tr"})        # selftest_scratch_reap_archive_tags.py
TMP_NAME = re.compile(r"tmp[a-z0-9_]{8}")
FAKE_SAVE_MAX = 64                                                              # the fixtures write "save" and kin


# selftest_relentless_seeds.py repo()/delivered() and selftest_relentless_wall.py's sha256 repo, before own_dir_for_run:
# the mkdtemp prefix, the exact top-level entries, the git dir that holds the repo, and the fixture's own author/committer
# identities, and any uncommitted change on the fixture's own files only (a run killed mid-test leaves m.py staged). A
# dir is this litter only when every one of them matches.
GIT_FIXTURES = {
    "seedrepo": {"entries": ({".claude", ".git", "m.py"}, {".claude", ".git", "m.py", "new.py"}), "repo": "",
                 "who": {"a <a@b>", "relentless worker <worker@relentless>"}, "files": {"m.py", "new.py", ".claude/agents/rm-judge.md"}},
    "seeddest": {"entries": ({"case"},), "repo": "case", "inner": ({".claude", ".git", "m.py"}, {".claude", ".git", "m.py", "new.py"}),
                 "who": {"a <a@b>", "relentless worker <worker@relentless>"}, "files": {"m.py", "new.py", ".claude/agents/rm-judge.md"}},
    "wallsha256": {"entries": ({".git", "a.py"},), "repo": "", "who": {"t <t@t>"}, "files": {"a.py"}},
}
GIT_NAME = re.compile(r"(%s)[a-z0-9_]{8}" % "|".join(GIT_FIXTURES))
GIT_FIXTURE_MAX = 2 * 1024 * 1024                                              # the fixtures are a few KB


def git_fixture(p: Path) -> str | None:
    """None = a seed/wall selftest's git fixture; else why not. Read-only: git log reads, never writes."""
    m = GIT_NAME.fullmatch(p.name)
    if not m:
        return "not a git fixture's name"
    f = GIT_FIXTURES[m.group(1)]
    names = set(os.listdir(p))
    if names not in [set(e) for e in f["entries"]]:
        return "not the fixture's entries"
    repo = p / f["repo"] if f["repo"] else p
    if f.get("inner") and set(os.listdir(repo)) not in [set(e) for e in f["inner"]]:
        return "not the fixture's entries"
    for n in [p / x for x in names] + [repo / x for x in os.listdir(repo)]:
        if n.is_symlink():
            return f"a symlink inside: {n}"
    g = repo / ".git"
    if not (g.is_dir() and (g / "HEAD").is_file() and (g / "objects").is_dir()):
        return "no git dir of its own"
    if tree_bytes(p) > GIT_FIXTURE_MAX:
        return "too big for the fixture"
    try:
        return _git_fixture_history(repo, f)
    except (subprocess.SubprocessError, ValueError) as e:            # a hung or undecodable git keeps it, never aborts
        return f"git unreadable: {e!r}"[:200]


def _git(repo: Path, *a: str) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(["git", "-c", "core.fsmonitor=false", "-C", str(repo), "--no-optional-locks", *a],
                          capture_output=True, text=True, errors="replace", env=env, timeout=60)


def _git_fixture_history(repo: Path, f: dict) -> str | None:
    r = _git(repo, "log", "--all", "--format=%an <%ae>%n%cn <%ce>")
    who = {x for x in r.stdout.splitlines() if x}
    if r.returncode or not who:
        return "no readable history"
    if not who <= f["who"]:
        return f"someone else committed here: {sorted(who - f['who'])[:2]}"
    st = _git(repo, "status", "--porcelain", "-z", "--ignored", "--untracked-files=all")
    if st.returncode:
        return "no readable status"
    dirty = {e[3:] for e in st.stdout.split("\0") if len(e) > 3}
    if not dirty <= f["files"]:
        return f"uncommitted changes beyond the fixture's files: {sorted(dirty - f['files'])[:2]}"
    return None


def legacy_roots() -> list[Path]:
    env = os.environ.get("SELFTEST_OWN_DIRS_LEGACY_ROOTS")
    if env:
        return [Path(x) for x in env.split(os.pathsep) if x]
    return [*sorted((Path.home() / ".seat-tmp").glob("*")), Path("/tmp")]


def candidates() -> list[Path]:
    out = []
    def kids(d: Path) -> list[Path]:
        try:
            return [] if d.is_symlink() or not d.is_dir() else list(d.iterdir())
        except OSError:                               # another user's dir in /tmp
            return []
    for r in legacy_roots():
        tops = [p for p in kids(r) if TMP_NAME.fullmatch(p.name) or GIT_NAME.fullmatch(p.name)]
        tops += [q for p in kids(r) if p.name.startswith("selftest_run_") for q in kids(p) if TMP_NAME.fullmatch(q.name)]
        for p in tops:
            with contextlib.suppress(OSError):
                if p.is_dir() and not p.is_symlink():
                    out.append(p.resolve())           # /proc links are absolute and resolved: compare like with like
    return out


def shaped(p: Path) -> bool:
    """The fixture's own layout: every SHAPE entry a real dir, a bare repo among them."""
    try:
        names = set(os.listdir(p))
    except OSError:
        return False
    for shape in SHAPES:
        if shape <= names and all(not (p / n).is_symlink() and (p / n).is_dir() for n in shape):
            bare = p / ("origin.git" if "origin.git" in shape else "origin")
            if (bare / "HEAD").is_file() and (bare / "objects").is_dir() and (bare / "refs").is_dir():
                return True
    return False


def judge(p: Path, now: float, min_age_s: float, open_locked: bool) -> str | None:
    try:
        return _judge(p, now, min_age_s, open_locked)
    except OSError as e:                              # e.g. listable but not searchable: keep it, never abort the sweep
        return f"unjudgeable: {e}"


def _judge(p: Path, now: float, min_age_s: float, open_locked: bool) -> str | None:
    """None = selftest litter; else why it stays. Litter is the fixture's layout holding at least one fake CANONICAL_
    save, every save fixture-sized, every entry statable, untouched for min_age_s. open_locked: chmod the fixture's
    unreadable dirs so they can be seen (only when about to remove; report mode never changes a thing)."""
    top = os.lstat(p)
    if GIT_NAME.fullmatch(p.name):
        if top.st_uid != os.getuid():
            return "another user's"
        why = git_fixture(p)
        if why:
            return why if why in ("not a git fixture's name", "not the fixture's entries") else f"git fixture look-alike: {why}"
        newest = top.st_mtime
        for dp, dns, fns in os.walk(p):
            for n in dns + fns:
                newest = max(newest, os.lstat(os.path.join(dp, n)).st_mtime)
        return "young" if now - newest < min_age_s else None
    if not shaped(p):
        return "not a reaper selftest's shape"
    if top.st_uid != os.getuid():
        return "another user's"
    errs = []
    if open_locked:
        for _ in os.walk(p, onerror=errs.append):
            pass
        if errs:                                      # the fixture plants unreadable dirs on purpose: open them, look again
            subprocess.run(["chmod", "-R", "u+rwx", str(p)], capture_output=True)
            errs.clear()
    newest, fakes = top.st_mtime, 0                  # the dir's own mtime too: a tree moved in keeps its old stamps
    for dp, dns, fns in os.walk(p, onerror=errs.append):
        for n in dns + fns:
            fp = os.path.join(dp, n)
            try:
                st = os.lstat(fp)
            except FileNotFoundError:
                continue
            except OSError as e:
                return f"unstatable inside: {e}"
            newest = max(newest, st.st_mtime)
            if n.endswith(".rws"):
                if st.st_size > FAKE_SAVE_MAX or not stat.S_ISREG(st.st_mode):
                    return f"a real-sized save inside: {fp}"
                fakes += n.startswith("CANONICAL_")
    if errs:
        return f"unreadable inside: {errs[0]}"         # a save we cannot see could be real
    if not fakes:
        return "no fake canonical save: not this litter"
    if now - newest < min_age_s:
        return "young"
    return None


def users(paths: list[Path]) -> set[Path]:
    """Paths any process has as cwd, root or open file. An unreadable process is ours to skip, not to fear: the
    reaper's own selftests run as this user, so their cwds are readable."""
    used = set()
    keys = [(str(p) + "/", p) for p in paths]
    for pid in filter(str.isdigit, os.listdir("/proc")):
        links = []
        for n in ("cwd", "root"):
            with contextlib.suppress(OSError):
                links.append(os.readlink(f"/proc/{pid}/{n}"))
        try:
            fds = os.listdir(f"/proc/{pid}/fd")
        except OSError:
            fds = []
        for fd in fds:                                # one fd closing mid-scan must not hide the others
            with contextlib.suppress(OSError):
                links.append(os.readlink(f"/proc/{pid}/fd/{fd}"))
        for ln in links:
            for k, p in keys:
                if ln == str(p) or ln.startswith(k):
                    used.add(p)
    return used


def tree_bytes(p: Path) -> int:
    n = 0
    for dp, _, fs in os.walk(p):
        for f in fs:
            with contextlib.suppress(OSError):
                n += os.lstat(os.path.join(dp, f)).st_size
    return n


def legacy_litter(apply: bool, min_age_s: float = 6 * 3600) -> dict:
    now = time.time()
    found, kept = [], []
    for p in candidates():
        why = judge(p, now, min_age_s, open_locked=apply)
        (kept if why else found).append((p, why))
    parents = {p.parent for p, _ in found if p.parent.name.startswith("selftest_run_")}
    busy = users([p for p, _ in found] + sorted(parents))
    rows, removed, bytes_ = [], 0, 0
    for p, _ in found:
        if p in busy or p.parent in busy:
            rows.append({"path": str(p), "verdict": "KEEP", "why": "a process uses it or its runner dir"})
            continue
        try:
            size = tree_bytes(p)
            if apply:
                why = judge(p, time.time(), min_age_s, open_locked=True)    # again, just before: nothing moved in since
                if why:
                    rows.append({"path": str(p), "verdict": "KEEP", "why": why})
                    continue
                force_rm(p)
                if os.path.lexists(p):
                    rows.append({"path": str(p), "verdict": "KEEP", "why": "removal failed"})
                    continue
                run = p.parent
                if run in parents and set(os.listdir(run)) <= {"selftest_scratch_reap.lock"}:
                    force_rm(run)                     # the runner's TMPDIR, emptied of its only fixture, used by nobody
        except OSError as e:                          # a candidate that moved under us is skipped, never the sweep
            rows.append({"path": str(p), "verdict": "KEEP", "why": f"changed during the sweep: {e}"})
            continue
        removed += 1
        bytes_ += size
        rows.append({"path": str(p), "verdict": "REMOVED" if apply else "LITTER", "bytes": size})
    rows += [{"path": str(p), "verdict": "KEEP", "why": why} for p, why in kept
             if why not in ("not a reaper selftest's shape", "no fake canonical save: not this litter",
                            "not a git fixture's name", "not the fixture's entries")]
    return {"apply": apply, "litter": removed, "bytes": bytes_, "rows": rows}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--apply", action="store_true", help="remove the litter (default: report only)")
    ap.add_argument("--min-age-hours", type=float, default=6.0)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    r = legacy_litter(a.apply, a.min_age_hours * 3600)
    if a.json:
        print(json.dumps(r, indent=1))
    else:
        for row in r["rows"]:
            print(row["verdict"], row["path"], row.get("why", ""))
        print(f"{'removed' if a.apply else 'litter'} {r['litter']} fixture dirs, {r['bytes'] / 1e6:.1f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
