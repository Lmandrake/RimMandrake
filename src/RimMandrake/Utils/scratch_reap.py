#!/usr/bin/env python3
"""scratch_reap.py — expire stale scratch clones and agent session dirs so nobody has to tidy them. Dry run by
default; --apply deletes. Anything that exists nowhere else is BUNDLED first, loudly, or the path is skipped.

Owner, 2026-10-18, by card (BUILDUP_BUILD_CLONES_STOP_BREEDING, Q2): "Reaper may delete stale scratch clones?
-> Yes, after 24h, if fully pushed". Owner, 2026-10-31 (SCRATCH_CLONES_BUILD_EXPIRY_NO_ONE_TIDIES): build it fully,
folded into the operating design. Authority for bundle-then-delete: design/RimMandrake/delegation_policy.md §2.2,
class `leftovers`; the archive root and acts.jsonl are leftovers.py's, so the digest lists every act.
Lesson behind the ledger check: a session scratchpad held the ONLY copy of CRACKEDLANDS_FULL_RENAME_1's three
commits and a hand cleanup deleted it (2026-10-18). Lesson behind inner clones: one bad clone kept a whole session
dir, and 150 GB stood REFUSED behind 15 session dirs.

    scratch_reap.py                 report every candidate: DELETE / ARCHIVE / REFUSE / YOUNG
    scratch_reap.py --apply         act on DELETE and ARCHIVE rows (each re-judged immediately before rmtree)
    scratch_reap.py --json          machine-readable rows
    scratch_reap.py --max-seconds N stop starting deletions N seconds after the run began; the next run takes the rest
    scratch_reap.py --pressure-check  if the root disk is low and no run is recent, start the reaper's unit now

Candidates (never anything else — loose files and other dirs are left alone):
  * a git clone anywhere under /home/mandrake/rm/scratch/** or ~/.seat-tmp/** (a dir holding `.git`);
  * an agent session dir  ~/.seat-tmp/<SEAT>/claude-*/<project>/<session-uuid>/ . Its inner clones are judged one by
    one, so one bad clone no longer keeps the rest; the session shell goes only when none of its clones is kept.

Verdicts:
  YOUNG    newest mtime or ctime anywhere inside (a session: anywhere in the session) is within the TTL. The TTL is 24 h and
           disk pressure never shortens it.
  DELETE   old, and nothing in it is missing elsewhere.
  ARCHIVE  old, and it holds a commit the mirror lacks (any readable ref, reflog or stash; a local tracking ref proves
           nothing, and a dead one holds nothing; a clone whose bundle is over the cap keeps only the objects GitHub's main
           and tags do not reach, make_residual),
           a dirty or untracked file, ignored files that are not build output, or loose session files: bundle + tar +
           index and worktree patches to a new archive dir, restore-tested, an acts.jsonl line, then delete. A commit
           whose author, dates and subject match main but whose content does not is kept as a patch: main's history was
           rewritten once, so old clones hold every commit under another hash, and a whole-history bundle is huge.
  REFUSE   skipped and reported. FAILS CLOSED: anything we cannot read or prove lands here.
           * protected: a seat, dispatch or anchor clone, arena, arena-vet, the replay root, store.git, mirror.git,
             retired-trees, the D: mirror; or a path inside or holding one of those;
           * a live session or process: running cwd, open file, mapping, exe, argv or environment inside it; session
             uuid in a process environment; transcript touched within the TTL. A process of ours we cannot inspect
             holds EVERYTHING;
           * borrowed: objects/info/alternates or a worktree `.git` file elsewhere points into it. An alternates
             file we cannot read holds EVERYTHING;
           * unreadable: any error walking it; git cannot read it; rebase/merge in progress; linked worktree;
             submodule; a nested repo; an assume-unchanged file; over the preserve caps; bundle or restore test failed;
           * a canonical save inside whose exact bytes the mirror does not hold;
           * named by an open item or, within 7 days, by a ledger event, closed item, handoff; or by a systemd unit.

Deletion is pinned: after the re-judgment and preservation the path is renamed aside, a fresh /proc scan and a fresh
walk prove nothing arrived, and only then is it removed; any doubt renames it back. The rename is what closes the gap
a check cannot: nothing new can reach the path once it is gone from under that name.

Stated limits, each a choice: hostile local processes are out of scope (a same-uid process calling itself ssh-agent
and going undumpable is not looked into, and root-owned processes cannot be inspected: they are counted in the record,
and nothing root-owned works in these roots). A borrower that is not running, beneath a dir of ours we cannot list under
/tmp or a reap root, or beneath another user's dir outside our trees, is not seen (a running one is, through its cwd; a
dir unreadable anywhere else holds everything). Tool caches named in DISPOSABLE_NAMES are never preserved, whatever they
hold. Hard links are a clone's own: a pinned tree's signature does not follow one out of the tree.
A borrower created in the two minutes between the borrower scan and a removal is not seen. A process whose cwd was
deleted has no repo left to name. An unreadable dir of ours can hide a borrower that is not running. A session of empty
directories and nothing else is not preserved: it holds no bytes and no file names, only directory names. Line endings
git normalises (a CRLF under text=auto) read as no change: comparing every worktree file to its blob is too much IO for
an hourly job over hundreds of clones. A process that holds a workspace only through an inotify watch
(no cwd, no open file, no path in argv or environ) is not seen: /proc shows a watch by inode, and a watcher loses nothing
it cannot rebuild. Also stated limits, from the full-file review: a C-quoted line in an alternates file ("\\303...") is read
as written; staging alone (`git rm --cached`) changes only .git/index, which the age of a clone does not count; a ref
that points straight at a blob or tree (`git replace` of a blob) is not a commit and is not preserved. Fixtures named selftest_* are disposable by design: a test's own scratch is removed
without a bundle, and a reader that starts inside one within the 20 s of a snapshot is not seen (a bind-mount alias of
a scratch dir likewise). A tmpXXXXXXXX dir with no repo or save in it is Python tempfile residue and goes unpreserved.
An exited thread leader's own cmdline/environ read empty; its workers' copies are not consulted.

Every run: runs.jsonl (rows), alarms.log (each new refusal once), last_run.json (apply runs: the record ops_watch
alarms on). An unexpected failure exits non-zero, which fails the unit, which reaches the Conductor (signal_watch).

Env (the selftest uses them): SCRATCH_REAP_ROOTS, _CORPUS, _SCAN, _MIRRORS, _PROTECTED (os.pathsep lists);
SCRATCH_REAP_TTL_HOURS, _STATE, _TRANSCRIPTS, _PRESSURE_GB, _COOLDOWN_MIN, _UNIT; LEFTOVERS_ARCHIVE_ROOT.
"""
from __future__ import annotations

import argparse
import bisect
import datetime as dt
import errno
import fcntl
import glob
import hashlib
import json
import ctypes
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import leftovers  # noqa: E402  (archive root, canonical marks: one definition, leftovers.py's)

HOME = Path.home()
RM = Path("/home/mandrake/rm")
# The replay root is deliberately NOT a root: it sits under arena, which the brief protects.
DEFAULT_ROOTS = [RM / "scratch", HOME / ".seat-tmp"]
DEFAULT_CORPUS = [RM / "bench", RM / "foundry"]
DEFAULT_SCAN = [HOME, Path("/tmp"), Path("/mnt/d/ClaudeWork/rimmandrake/pulse-deploy")]
PROTECTED = [RM / n for n in ("bench", "foundry", "dispatch", "anchor", "arena", "arena-vet", "store.git", "mirror.git",
                              "new.git", "retired-trees", "scratch_wallreach_slice")] + [Path("/mnt/d/Luke/dev/RimMandrake")]
UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
UUID_ANY = re.compile(rb"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
TOKEN = re.compile(r"[A-Za-z0-9_-]+")
TRANSIENT_FIND = re.compile(r"find: .(.+?).: Cannot allocate memory$")
FIXTURE_RECHECK_S = 20      # a fixture is deleted on a /proc reading no older than this
CTIME_COUNTS = True         # the selftest ages its fixtures with utime, which cannot set a ctime
SYSTEM_PATHS = ("/proc/", "/sys/", "/dev/", "/usr/", "/lib/", "/lib64/", "/bin/", "/sbin/", "/etc/", "/opt/", "/init")
GONE_LENDER = re.compile(r"error: (unable to normalize alternate object path: |object directory .* does not exist; check )")
MOUNTINFO = "/proc/self/mountinfo"
UNIX_SOCKETS = "/proc/net/unix"
# A clone's config may tell git to look less hard than this job must: it answers for the bytes on disk, on this filesystem.
HONEST_STATUS = [w for k in ("core.ignorecase=false", "core.trustctime=true", "core.checkStat=default", "core.fileMode=true",
                                    "core.symlinks=true", "core.ignoreStat=false", "core.fsmonitor=false", "core.untrackedCache=false") for w in ("-c", k)]
SANITY_DU_S = 240           # 94 GB took 18 s on 2026-11-01
FIXTURE_TTL_S = 24 * 3600   # owner-authority brief 2026-11-01: disposable selftest_* a day old may go
WALK_CAP = 3_000_000        # entries; a tree bigger than this is not aged (REFUSE: too big to age)
DIRTY_CAP = 2 * 1024 ** 3   # dirty/untracked bytes we will tar; more is skipped and reported
BROKEN_CAP = DIRTY_CAP      # a .git no bundle can read is tarred whole, up to this
RESIDUE_CAP = 512 * 1024 ** 2   # a session's loose files
BUNDLE_CAP = 5 * 1024 ** 3
MENTION_DAYS = 7
BLIND_RETRIES = 5
PRESSURE_GB = 420.0         # ops_watch_rules' DISK_TWO_DAYS line
COOLDOWN_MIN = 30
BORROW_REFRESH_S = 120
CHANGED_CAP = 2000          # commits kept as patches; more is refused
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
PIN = re.compile(r"^\.reaping-\d+-")      # a path renamed aside for deletion; a crash leaves one to be judged again
DISPOSABLE_NAMES = {"__pycache__", ".pytest_cache", ".mypy_cache", "node_modules"}     # tool caches by definition
DISPOSABLE_EXACT = {"Transient/codebase_health.html", "Transient/codebase_health.json", "Transient/codebase_health_artifact.html",
                    "Transient/codebase_health_hook.log", "infrastructure/state/codebase_health_last.json",
                    "infrastructure/state/codebase_health_last.json.lock"}
DISPOSABLE_DIRS = ("infrastructure/dashboards/hub/data/", "infrastructure/state/queue/")     # rendered from the ledger


def env_paths(name: str, default: list[Path]) -> list[Path]:
    v = os.environ.get(name)
    return [Path(x) for x in v.split(os.pathsep) if x] if v is not None else default


def roots() -> list[Path]:
    return env_paths("SCRATCH_REAP_ROOTS", DEFAULT_ROOTS)


def scan_roots() -> list[Path]:
    dflt = roots() + corpus_roots() if os.environ.get("SCRATCH_REAP_ROOTS") else DEFAULT_SCAN
    return env_paths("SCRATCH_REAP_SCAN", dflt)


def protected() -> list[Path]:
    return PROTECTED + env_paths("SCRATCH_REAP_PROTECTED", [])


def corpus_roots() -> list[Path]:
    return env_paths("SCRATCH_REAP_CORPUS", DEFAULT_CORPUS)


def ttl_s() -> float:
    return float(os.environ.get("SCRATCH_REAP_TTL_HOURS", "24")) * 3600


def state_dir() -> Path:
    return Path(os.environ.get("SCRATCH_REAP_STATE",
                               Path(os.environ.get("XDG_STATE_HOME", HOME / ".local" / "state")) / "rm-scratch-reap"))


def origin_mirrors() -> list[Path]:
    return env_paths("SCRATCH_REAP_MIRRORS", [RM / "mirror.git", RM / "store.git"])


def read_objects() -> list[str]:
    """Object dirs every read may use: a --shared clone whose lender lost objects still reads through these, and a
    commit found only here is on the mirror or store by definition."""
    out = []
    for m in origin_mirrors():
        for o in (m / "objects", m / ".git" / "objects"):
            if o.is_dir():
                out.append(str(o))
    return out


def git(repo: Path, *a, stdin: str | None = None, timeout: int = 600) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_") or k in ("GIT_CONFIG_GLOBAL", "GIT_CONFIG_SYSTEM")}
    env.update(GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0", GIT_NO_REPLACE_OBJECTS="1")
    ro = read_objects()
    if ro:
        env["GIT_ALTERNATE_OBJECT_DIRECTORIES"] = os.pathsep.join(ro)
    try:
        r = subprocess.run(["git", "-C", str(repo), *HONEST_STATUS, *a], capture_output=True, env=env, timeout=timeout,
                           input=None if stdin is None else stdin.encode("utf-8", "surrogateescape"))
        return subprocess.CompletedProcess(a, r.returncode, r.stdout.decode("utf-8", "surrogateescape"),
                                           r.stderr.decode("utf-8", "surrogateescape"))     # bytes: text mode eats a \r
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(a, 124, "", "git timed out")


# ---------------------------------------------------------------- discovery
def is_clone(d: Path) -> bool:
    """A `.git` dir with no repo in it is a selftest's sandbox marker: 1,640 read as refused clones on 2026-11-01."""
    g = d / ".git"
    if not os.path.lexists(g):
        return False
    if g.is_symlink() or not g.is_dir():
        return True
    try:
        with os.scandir(g) as it:
            return any(e.name in ("HEAD", "objects", "refs") for e in it)
    except OSError:
        return True                 # unreadable stays a candidate, and is refused for it


def find_clones(top: Path, depth: int = 8) -> list[Path]:
    """Every git work tree under `top` (top itself included), not descending into a found clone. A dir we cannot
    list is not a hole: walk() reports it and the containing candidate is REFUSED there."""
    out: list[Path] = []

    def walk(d: Path, k: int):
        if is_clone(d):
            out.append(d)
            return
        if k <= 0:
            return
        try:
            with os.scandir(d) as it:
                subs = [Path(e.path) for e in it if e.is_dir(follow_symlinks=False)]
        except OSError:
            return
        for s in subs:
            walk(s, k - 1)
    walk(top, depth)
    return out


def candidates() -> list[tuple[str, Path]]:
    """[(kind, path)]: session dirs, then clones outside any session."""
    cands: list[tuple[str, Path]] = []
    seen: set[Path] = set()
    for r in roots():
        if not r.is_dir():
            continue
        sess = glob.glob(str(r / "*" / "claude-*" / "*" / "*")) + glob.glob(str(r / "*" / "claude-*" / "*" / ".reaping-*"))
        for s in sess:                                                 # ~/.seat-tmp/<SEAT>/claude-*/<project>/<uuid>
            p = Path(s)
            if UUID.match(PIN.sub("", p.name)) and p.is_dir() and not p.is_symlink():
                cands.append(("session", p))
                seen.add(p)
        for c in find_clones(r):
            if not any(s == c or s in c.parents for s in c.parents if s in seen) and c not in seen:
                cands.append(("clone", c))
        for f in glob.glob(str(r / "*" / "enact_*")):                  # rm/scratch/<SEAT>/enact_*: art.py enact test fixtures
            fp = Path(f)
            if fp.is_dir() and not fp.is_symlink() and not (fp / ".git").exists() and not find_clones(fp):
                cands.append(("fixture", fp))
    return cands


# ---------------------------------------------------------------- measurements
def touched(st: os.stat_result) -> tuple:
    """`cp -a` and a tar extract keep old mtimes on a dir made a minute ago; the ctime says when it arrived."""
    return (st.st_mtime, st.st_ctime) if CTIME_COUNTS else (st.st_mtime,)


class Tree:
    """One walk of a candidate: newest mtime, bytes, unreadable spots, saves. Never follows symlinks."""

    def __init__(self, d: Path):
        self.newest, self.size, self.capped, self.errors, self.saves = 0.0, 0, False, [], []
        self.nested: list[str] = []                     # a `.git` below the top: another repo, ignored or not
        self.top_ctime = 0                              # the pin must see this unmoved: see act
        self.sig = 0                                    # order-free sum over every entry below the top; see signature()
        n = 0
        top = len(str(d))
        stack = [str(d)]
        # Reading a clone is not working in it: `git status` rewrites .git/index, and so .git's mtime. One look at sixteen
        # clones on 2026-11-01 made 94 GB a day younger.
        reads = {f"{d}/.git", f"{d}/.git/index"}
        while stack:
            cur = stack.pop()
            try:
                st = os.lstat(cur)
                if cur not in reads:
                    self.newest = max(self.newest, *touched(st))
                if cur == str(d):                       # a rename leaves the top's mtime and mode alone, not its ctime
                    self.top_ctime = st.st_ctime_ns
                    self.sig += int.from_bytes(hashlib.sha256(b"top %d %d" % (st.st_mtime_ns, st.st_mode)).digest(), "big")
                it = os.scandir(cur)
            except OSError as e:
                self.errors.append(f"{cur}: {e.strerror}")
                continue
            with it:
                for e in it:
                    n += 1
                    if n > WALK_CAP:
                        self.capped = True
                        return
                    try:
                        st = e.stat(follow_symlinks=False)
                        isdir = e.is_dir(follow_symlinks=False)
                    except OSError as x:
                        self.errors.append(f"{e.path}: {x.strerror}")
                        continue
                    if e.path not in reads:
                        self.newest = max(self.newest, *touched(st))
                    self.sig += int.from_bytes(hashlib.sha256(os.fsencode(f"{e.path[top:]}\0{st.st_ino}\0{st.st_mode}\0{st.st_size}\0"
                                               f"{st.st_mtime_ns}\0{st.st_ctime_ns}")).digest(), "big")
                    if e.name == ".git" and cur != str(d):
                        self.nested.append(e.path)
                    if isdir:
                        stack.append(e.path)
                    else:
                        self.size += st.st_size
                        if e.name.endswith(".rws"):
                            self.saves.append(e.path)

    def signature(self) -> str:
        """Names, inodes, modes, sizes, mtimes and ctimes of everything below the top; the top's mtime and mode."""
        return f"{self.sig % 2 ** 256:064x}"


_CANON: set[str] | None = None


def canon_save_names() -> set[str]:
    global _CANON
    if _CANON is None:
        _CANON = set()
        for r in corpus_roots():
            _CANON |= set(leftovers.Ctx.canon_save_names(type("C", (), {"repo": str(r), "_canon_saves": None})()))
    return _CANON


def canonical_saves(saves: list[str]) -> list[str]:
    names = canon_save_names()
    base = [(s, os.path.basename(s)) for s in saves]
    return [s for s, b in base if b in names or any(m in b for m in leftovers.CANONICAL_MARKS)]


def mirror_holds(f: Path) -> bool:
    """These exact bytes are a blob the mirror holds. Read from the worktree, so no index flag can hide a change."""
    try:
        st = os.lstat(f)
        if not os.path.isfile(f) or os.path.islink(f):
            return False
        h = hashlib.sha1(f"blob {st.st_size}\0".encode())
        with open(f, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
    except OSError:
        return False
    return any(git(m, "cat-file", "-e", h.hexdigest()).returncode == 0 for m in origin_mirrors())


def unpreserved_canon(c: Path, saves: list[str]) -> list[str]:
    """Canonical saves in clone `c` that exist only here. A checkout of the repo always carries the tracked ones."""
    return [os.path.relpath(s, c) for s in canonical_saves(saves) if not mirror_holds(Path(s))]


NONDUMPABLE = {"systemd", "(sd-pam)", "ssh-agent"}     # ours by uid, unreadable by design, never an agent session


def undumpable_system(base: str) -> bool:
    try:
        return open(f"{base}/comm").read().strip() in NONDUMPABLE
    except OSError:
        return False


_SYSTEM_PIDS: set[str] = set()


def dead(base: str) -> bool:
    """A zombie has let go of its cwd and files yet reads as denied, and a busy machine always has one exiting. A leader
    that exited while its threads run also shows Z and they hold everything, so every thread must be Z."""
    try:
        states = [open(f"{base}/task/{t}/stat", errors="replace").read().rsplit(")", 1)[1].split()[0]
                  for t in os.listdir(f"{base}/task")]
    except (OSError, IndexError):
        return False
    return bool(states) and all(st in ("Z", "X") for st in states)


def _who(base: str) -> str:
    """Name a blind process in the record: comm, state and parent are world-readable."""
    try:
        comm, _, rest = open(f"{base}/stat").read().rpartition(") ")
        return f"{comm.partition('(')[2]!r} {rest.split()[0]} ppid {rest.split()[1]}"
    except (OSError, IndexError):
        return "gone"


def under(keys: list[str], name: str) -> list[int]:
    """Indexes of a sorted key list that are `name` or inside it. Not one run: "/a/b-x" and "/a/b.c" sort between "/a/b"
    and "/a/b/c", so the dir itself and its children are two searches."""
    out = []
    i = bisect.bisect_left(keys, name)
    if i < len(keys) and keys[i] == name:
        out.append(i)
    i = bisect.bisect_left(keys, name + "/")
    while i < len(keys) and keys[i].startswith(name + "/"):
        out.append(i)
        i += 1
    return out


def path_forms(token: str, cwd: str, bare_must_exist: bool = False) -> list[str]:
    """Every absolute path a command-line word or environment value could name, as written (not normalised).

    One function owns the shapes, so a new one is a row in its test table and not another branch in the scan:
    a plain path; relative to the process's cwd; `--repo=/p`, `K=v`; `-I../x` and `-isystem/x`; PATH-like lists split on
    ':' and blanks; a value with a path from its first slash. A bare word (`worker`) names cwd/worker: from argv always,
    from an environment value only if it is there."""
    out: list[str] = []
    for part in [token] + re.split(r"[:\s,;()&|\"'`]+", token):      # a whole value too: a path may hold a blank or a colon
        if not part.strip(":,;()&|\"'` \t\n"):
            continue
        cands = [part]
        if part[:1] in ("@", "+", "<", ">", "!", "%"):       # @response-file, redirections
            cands.append(part[1:])
        if part[:1] == "-":
            cands += [part.partition("=")[2]] + [part[k:] for k in range(1, len(part))
                                                 if part[k - 1] not in "/-" and part[k] != "/"]   # -isystemscratch/c: the flag's length is unknown
        elif "=" in part:
            cands.append(part.partition("=")[2])
        for pre in ("$HOME", "${HOME}", "~"):                # a shell expands these only after the process was started
            if pre + "/" in part:                         # never bare HOME: naming it would make every home dir a lender walk
                cands += [x.replace(pre + "/", str(HOME) + "/", 1) for x in list(cands) if pre + "/" in x]
        if "/" in part:
            cands.append(part[part.index("/"):])
            m = re.search(r"\.\.?/", part)                 # `-isystem../x`: a relative path glued to a long flag
            if m:
                cands.append(part[m.start():])
        for c in cands:
            if not c:
                continue
            raw = c if c[:1] == "/" else os.path.join(cwd, c)
            if "/" not in c and bare_must_exist and not os.path.lexists(raw):
                continue
            if raw not in out:
                out.append(raw)
    return out


def proc_entries() -> list[str]:
    """The scan's whole world. A selftest narrows it to its own process tree; the reaper never does."""
    return os.listdir("/proc")


class Live:
    """One /proc + transcript snapshot: what is in use right now. Re-taken before each deletion batch."""

    def __init__(self, now: float):
        self.taken = time.time()
        self.paths: list[tuple[str, str]] = []
        self.sessions: set[str] = set()
        self.resolved: dict[str, str] = {}                  # the same few paths recur across hundreds of environments
        self.blind: list[str] = []
        self.other_uid = 0
        self.cwds: set[str] = set()
        self.named: set[str] = set()                    # every place a process names, for the same question
        cmds = []
        me, uid = os.getpid(), os.getuid()
        for pid in proc_entries():
            if not pid.isdigit() or int(pid) == me:
                continue
            base = f"/proc/{pid}"
            try:
                real_uid = next(int(ln.split()[1]) for ln in open(f"{base}/status") if ln.startswith("Uid:"))
            except (FileNotFoundError, ProcessLookupError, StopIteration, ValueError):
                continue                                        # the process just ended
            except OSError as e:
                self.blind.append(f"pid {pid}: status: {e.strerror}")
                continue
            if real_uid != uid:
                self.other_uid += 1                             # root daemons: unreadable by design, counted
                continue
            try:
                self._read(pid, base, cmds)
            except FileNotFoundError:
                continue
            except ProcessLookupError:
                continue
            except OSError as e:
                # Exempt only what stays unreadable: a forked child still called systemd must get to its exec.
                if pid in _SYSTEM_PIDS and undumpable_system(base):
                    continue
                if self._settles(pid, base, cmds) or dead(base):
                    continue
                if undumpable_system(base):
                    _SYSTEM_PIDS.add(pid)
                else:
                    self.blind.append(f"pid {pid} {_who(base)}: {e.strerror}")
        self.paths.append((os.getcwd(), str(me)))               # this job is a process too, and may stand in a candidate
        self._listeners()
        for cwd in sorted(self.cwds):
            self._lenders(cwd)
        for d in sorted(self.named - self.cwds):        # a path merely named may be anyone's: not seeing into it is not blind
            self._lenders(d, quiet=True)
        self.paths.sort()
        self.keys = [p for p, _ in self.paths]
        self.cmdblob = "\0".join(cmds)
        self.fresh = transcripts_fresh(now)
        if self.fresh is None:
            self.blind.append("transcript tree unreadable")
            self.fresh = {}

    def _listeners(self):
        """A listening socket's owner holds only `socket:[n]`, which names no path, and tar drops the socket. A dead one
        is in no table, so it holds nothing."""
        try:
            with open(UNIX_SOCKETS, errors="surrogateescape") as f:
                for ln in list(f)[1:]:
                    w = ln.rstrip("\n").split(None, 7)
                    if len(w) == 8 and w[7].startswith("/"):
                        self.paths.append((w[7], "a socket"))
        except OSError as e:
            self.blind.append(f"unix sockets: {e.strerror}")

    def _lenders(self, cwd: str, quiet: bool = False):
        """A running clone anywhere keeps what it borrows, even outside the scan roots.

        quiet: cwd is only a directory some process named, so a denial on the way up to a repo says nothing. Once a
        .git is found the rest counts: an unreadable one, or unreadable alternates, stay blind."""
        repo = self._repo_of(cwd.removesuffix(" (deleted)"), quiet)
        if repo is None:
            return
        todo, seen = [os.path.join(repo, "objects")], set()
        while todo:
            o = todo.pop()
            if o in seen:
                continue
            seen.add(o)
            try:
                text = open(os.path.join(o, "info", "alternates"), errors="surrogateescape").read()
            except FileNotFoundError:
                continue
            except OSError as e:
                self.blind.append(f"alternates of {o}: {e.strerror}")
                continue
            for ln in text.splitlines():
                if ln.strip() and not ln.startswith("#"):
                    t = os.path.realpath(os.path.join(o, ln.strip()))
                    self.paths.append((t, "a live clone borrows it"))
                    todo.append(t)

    def _repo_of(self, cwd: str, quiet: bool = False) -> str | None:
        """The git dir holding objects for a cwd, through a linked worktree's `.git` file. Not knowing is blind."""
        d = cwd
        while True:
            g = os.path.join(d, ".git")
            try:
                if os.path.lexists(g):
                    os.stat(g)
                    break
                os.stat(os.path.join(d, "."))           # lexists swallows a denial; this does not
                if os.path.isfile(os.path.join(d, "HEAD")) and os.path.isdir(os.path.join(d, "objects")):
                    return d                            # inside a bare repo
            except (FileNotFoundError, NotADirectoryError):
                pass
            except OSError as e:
                if not quiet:
                    self.blind.append(f"cannot see the repo of {cwd}: {e.strerror}")
                return None
            if os.path.dirname(d) == d:                 # and "//x" never reaches "/"
                return None
            d = os.path.dirname(d)
        if os.path.isdir(g):
            return g
        try:
            m = re.match(r"gitdir:\s*(.+)", open(g, errors="surrogateescape").read())
            if not m:
                raise OSError(0, "no gitdir line")
            gd = os.path.join(d, m.group(1).strip())
            os.stat(gd)                                 # a gitdir that is not there is not a repo that borrows nothing
            try:
                common = os.path.realpath(os.path.join(gd, open(os.path.join(gd, "commondir")).read().strip()))
            except FileNotFoundError:
                common = os.path.realpath(gd)
        except OSError as e:
            self.blind.append(f"{g}: {e.strerror}")
            return None
        self.paths.append((common, "a live worktree's repo"))
        return common

    def _settles(self, pid: str, base: str, cmds: list[str]) -> bool:
        """A child systemd has forked is undumpable until its exec, so every unit start would otherwise read as a
        blind spot and hold the whole run. Blind means it stays unreadable; retrying costs only when one is found."""
        for _ in range(BLIND_RETRIES):
            time.sleep(0.1)
            try:
                self._read(pid, base, cmds)
                return True
            except (FileNotFoundError, ProcessLookupError):
                return True
            except OSError:
                continue
        return False

    @staticmethod
    def _fds_and_maps(base: str, add):
        for e in os.scandir(f"{base}/fd"):
            try:
                add(os.readlink(e.path))
            except FileNotFoundError:
                pass
        with open(f"{base}/maps", errors="surrogateescape") as f:
            for ln in f:
                i = ln.find("/")
                if i > 0:
                    add(ln[i:].rstrip("\n"))
                    add(ln[i:].rstrip("\n").replace("\\012", "\n"))    # maps writes a newline in a name so

    @staticmethod
    def _tasks(base: str) -> list[str]:
        try:
            return os.listdir(f"{base}/task")
        except OSError:
            return []

    def _add(self, p: str, pid: str):
        if p.startswith("/"):
            self.paths.append((p.removesuffix(" (deleted)"), pid))
            if not p.startswith(SYSTEM_PATHS):
                self.named.add(os.path.dirname(p))
                self.named.add(p.removesuffix(" (deleted)"))    # a directory fd or a variable names the repo itself
                plain = p.removesuffix(" (deleted)")
                real = self.resolved.get(plain) or self.resolved.setdefault(plain, os.path.realpath(plain))
                if real != p:                                   # a shortcut in argv names what it points at
                    self.paths.append((real, pid))
                    self.named.update((real, os.path.dirname(real)))

    def _read(self, pid: str, base: str, cmds: list[str]):
        def add(p: str):
            self._add(p, pid)
        for link in ("cwd", "exe", "root"):
            try:
                t = os.readlink(f"{base}/{link}")
            except FileNotFoundError:
                # a zombie has none; a leader whose main thread exited has none, and its workers still hold theirs
                for tid in self._tasks(base):
                    try:
                        t = os.readlink(f"{base}/task/{tid}/{link}")
                    except OSError:
                        continue
                    if link != "root":
                        add(t)
                    if link == "cwd":
                        self.cwds.add(t)
                continue
            if link != "root":
                add(t)
            if link == "cwd":
                self.cwds.add(t)
        try:
            self._fds_and_maps(base, add)
        except FileNotFoundError:
            for tid in self._tasks(base):                       # an exited leader: its workers' tables are under task/
                try:
                    self._fds_and_maps(f"{base}/task/{tid}", add)
                except OSError:
                    continue
        with open(f"{base}/cmdline", "rb") as f:
            argv = f.read()
        cmds.append(argv.replace(b"\0", b" ").decode("utf-8", "surrogateescape"))
        try:
            cwd = os.readlink(f"{base}/cwd")
        except FileNotFoundError:
            cwd = next((os.readlink(f"{base}/task/{t}/cwd") for t in self._tasks(base)
                        if os.path.lexists(f"{base}/task/{t}/cwd")), "/")      # an exited leader: a worker's cwd, else the root
        for a in argv.split(b"\0"):
            self._name_token(a.decode("utf-8", "surrogateescape"), cwd, pid, False)
        with open(f"{base}/environ", "rb") as f:
            env = f.read()
        self.sessions.update(m.decode() for m in UUID_ANY.findall(env))
        for kv in env.split(b"\0"):
            self._name_token(kv.partition(b"=")[2].decode("utf-8", "surrogateescape"), cwd, pid, True)

    def _name_token(self, token: str, cwd: str, pid: str, bare_must_exist: bool):
        """Record every place one argv word or environment value could name. The only reader of path shapes."""
        for raw in path_forms(token, cwd, bare_must_exist):
            self._add(os.path.normpath(raw), pid)
            self._add(os.path.realpath(raw), pid)           # a link before the `..` means normpath named the wrong dir
            self.named.add(os.path.normpath(raw))

    def users(self, p: Path) -> list[str]:
        t = str(p)
        out = []
        unpinned = str(p.with_name(PIN.sub("", p.name)))  # a crash's pin must not hide who the path belongs to
        for name in sorted({t, os.path.realpath(t), unpinned}):     # /proc reports resolved paths; argv and env may not
            for i in under(self.keys, name):
                out.append(f"pid {self.paths[i][1]} uses {self.keys[i][:120]}")
                if len(out) >= 3:
                    break
            if name in self.cmdblob:
                out.append("a running command line names it")
        for part in (PIN.sub("", q) for q in p.parts):
            if UUID.match(part):
                if part in self.sessions:
                    out.append(f"live session {part}: a running process carries it")
                if part in self.cmdblob:
                    out.append(f"live session {part}: a running command line names it")
                if part in self.fresh:
                    out.append(f"live session {part}: transcript touched within the TTL")
        return out


def transcript_roots() -> list[Path]:
    cfg = Path(os.environ.get("CLAUDE_CONFIG_DIR", HOME / ".claude"))
    return env_paths("SCRATCH_REAP_TRANSCRIPTS", [cfg / "projects"])


def _raise(e: OSError):
    if not isinstance(e, FileNotFoundError):         # gone mid-walk is an ended process's tidying; the rest is blindness
        raise e


def newest_jsonl(top: str) -> float:
    t = 0.0
    for dp, _, fns in os.walk(top, onerror=_raise):
        for n in fns:
            if n.endswith(".jsonl"):
                t = max(t, os.lstat(os.path.join(dp, n)).st_mtime)
    return t


def transcripts_fresh(now: float) -> dict[str, float] | None:
    """{session uuid: newest transcript mtime} for transcripts inside the TTL (a subagent's counts); None = blind."""
    out: dict[str, float] = {}
    ttl = ttl_s()
    try:
        for r in transcript_roots():
            for proj in os.scandir(r):
                if not proj.is_dir(follow_symlinks=False):
                    continue
                for e in os.scandir(proj.path):
                    name = e.name.removesuffix(".jsonl")
                    if not UUID.match(name):
                        continue
                    t = e.stat(follow_symlinks=False).st_mtime
                    if e.is_dir(follow_symlinks=False):
                        t = max(t, newest_jsonl(e.path))
                    if now - t < ttl:
                        out[name] = t
    except OSError:
        return None
    return out


class Borrows:
    """Who points into whom: every objects/info/alternates and every `.git` FILE in the scan roots. An unreadable
    one means we no longer know what must stay, so `hold` stops every deletion."""

    @staticmethod
    def _walk(tops: list[str]) -> tuple[int, bytes, list[str]]:
        p = subprocess.run(["find", *tops, "(", "-path", "*.git/objects/[0-9a-f][0-9a-f]", "-o", "-path", "*.git/objects/pack",
                            ")", "-prune", "-o", "(", "-path", "*/objects/info/alternates", "-o", "(", "-name", ".git",
                            "-type", "f", ")", ")", "-print0"], capture_output=True, timeout=900)
        return p.returncode, p.stdout, [ln for ln in p.stderr.decode("utf-8", "replace").splitlines() if ln.strip()]

    def __init__(self):
        self.taken = time.time()
        self.hold: list[str] = []
        self.blind: list[str] = []
        self.pairs: list[tuple[str, str]] = []
        self.keys: list[str] = []
        pairs: list[tuple[str, str]] = []
        tops = [str(r) for r in scan_roots() if r.exists()]
        # Git's own loose objects and packs hold no borrower: skipping them turns a walk that outran 300 s at idle IO
        # into two minutes. Only inside a *.git directory, so a tree that merely has an objects/ab directory is walked.
        if not tops:
            raise RuntimeError("no scan root exists: the borrower map would be empty")
        try:
            rc, out, lines = self._walk(tops)
            # A drvfs directory answers ENOMEM under load and reads clean a moment later; one such line held every deletion.
            for wait in (0.5, 5, 30):
                again = [m.group(1) for m in (TRANSIENT_FIND.match(ln) for ln in lines) if m]
                if not again:
                    break
                time.sleep(wait)
                lines = [ln for ln in lines if not TRANSIENT_FIND.match(ln)]
                last, more, tail = self._walk(again)
                rc = rc if rc < 0 else last
                out += more
                lines += tail
        except subprocess.TimeoutExpired:
            # A hold, not a crash: the run refuses from here on and still writes its record of what it freed.
            self.hold.append("find outran 900 s: the borrower map is partial")
            return
        for ln in lines:
            if "No such file" in ln:
                continue                        # gone mid-walk is fine
            (self.blind if "Permission denied" in ln and self._harmless(ln) else self.hold).append(ln)
        if rc < 0 or (rc and not lines):
            self.hold.append(f"find ended {rc} with no reason given: the borrower map is partial")
        for raw in out.split(b"\0"):
            if not raw:
                continue
            f = os.fsdecode(raw)
            try:
                text = open(f, errors="surrogateescape").read()
            except FileNotFoundError:
                continue                        # gone since find met it: its repo borrows nothing now
            except OSError as e:
                self.hold.append(f"{f}: {e.strerror}")
                continue
            if f.endswith("/.git"):
                holder = os.path.dirname(f)
                m = re.match(r"gitdir:\s*(.+)", text)
                t = m.group(1).strip() if m else ""
                lines = [t if os.path.isabs(t) else os.path.join(holder, t)] if t else []
            else:
                holder = os.path.dirname(os.path.dirname(os.path.dirname(f)))    # <repo>/objects or <repo>/.git/objects
                base = os.path.dirname(os.path.dirname(f))
                lines = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.startswith("#")]
                lines = [ln if os.path.isabs(ln) else os.path.join(base, ln) for ln in lines]
                holder = holder.removesuffix("/.git")
            for ln in lines:
                pairs.append((os.path.realpath(ln), holder))
        pairs.sort()
        self.pairs, self.keys = pairs, [k for k, _ in pairs]

    @staticmethod
    def _harmless(ln: str) -> bool:
        """Another user's dir outside our trees cannot hold our borrower, and one on an ancestor of a live cwd goes
        blind through _lenders. Ours under a reap root is refused with its candidate, as is /tmp's selftest residue.
        Unreadable anywhere else holds."""
        m = re.search(r"(/.*?)['’]?: Permission denied", ln)
        if not m:
            return False
        rp = Path(m.group(1))
        try:
            foreign = os.lstat(rp).st_uid != os.getuid()
        except FileNotFoundError:
            return True                                 # gone since find met it: it holds nothing now
        except OSError:
            return False
        if foreign:
            return not any(r == rp or r in rp.parents for r in scan_roots() if r != Path("/tmp"))
        return any(r in rp.parents for r in [Path("/tmp"), *roots()])

    def of(self, target: Path) -> list[str]:
        t = os.path.realpath(target)
        out = []
        for i in under(self.keys, t):
            holder = self.pairs[i][1]
            if holder != t and not holder.startswith(t + "/"):
                out.append(f"{holder} borrows objects from it")
        return sorted(set(out))


# ---------------------------------------------------------------- what exists only here
def mirror_tips() -> list[str]:
    """origin/main per each mirror we can read, the first mirror's first (main_keys reads it), then each mirror's tags:
    the proof a commit is pushed even when a clone's refs are stale. mirror.py fetches GitHub's tags; only what GitHub has."""
    global _MIRROR_TIPS
    if _MIRROR_TIPS is None:
        _MIRROR_TIPS = []
        for m in origin_mirrors():
            for ref in ("refs/remotes/origin/main", "refs/heads/main"):
                r = git(m, "rev-parse", "-q", "--verify", ref + "^{commit}")
                if r.returncode == 0:
                    _MIRROR_TIPS.append(r.stdout.strip())
                    break
        for m in origin_mirrors():
            _MIRROR_TIPS.extend(git(m, "for-each-ref", "--format=%(objectname)", "refs/tags/").stdout.split())
    return _MIRROR_TIPS


_MIRROR_TIPS: list[str] | None = None
_MAIN_KEYS: dict[str, set[str]] | None = None


def commit_digests(repo: Path, *args, stdin: str | None = None) -> dict[str, tuple[str, str]] | None:
    """{sha: (author, dates and subject; digest of each changed path's mode, blob and name)}. Reads trees, never blobs.
    NUL ends every field: a path can hold a newline, never a NUL. None = unreadable."""
    a, b = f"<{os.urandom(16).hex()}>", f"<{os.urandom(16).hex()}>"    # a subject or a path may hold any fixed mark
    r = git(repo, "log", *args, "--no-renames", "--no-abbrev", "--raw", "-z", "--diff-merges=first-parent",
            f"--format={a}%H %at %ct %ae %s{b}", stdin=stdin, timeout=300)
    if r.returncode:
        return None
    out = {}
    for rec in r.stdout.split(a)[1:]:
        head, _, raw = rec.partition(b)
        sha, _, key = head.partition(" ")
        f = raw.lstrip("\0\n").split("\0")
        if not all(f[i].startswith(":") for i in range(0, len(f) - 1, 2)):
            return None                                 # a record not understood must not read as a commit with no changes
        ents = sorted("\0".join((f[i].split()[1], f[i].split()[3], f[i + 1], "")) for i in range(0, len(f) - 1, 2))
        out[sha] = (key, hashlib.sha1("".join(ents).encode("utf-8", "surrogateescape")).hexdigest())
    return out


def main_keys() -> dict[str, set[str]]:
    """A rewrite of main left old clones holding every commit under another hash. {key: digests on main}: a commit
    with main's key and digest is that commit, on main. An unreadable mirror yields nothing, so nothing is excused.
    A rewrite that also changed author email misses this key; a big clone from one is settled by make_residual."""
    global _MAIN_KEYS
    if _MAIN_KEYS is None:
        _MAIN_KEYS = {}
        tips = mirror_tips()
        d = commit_digests(origin_mirrors()[0], tips[0]) if tips else None
        for key, dig in (d or {}).values():
            _MAIN_KEYS.setdefault(key, set()).add(dig)
    return _MAIN_KEYS


def dead_ref_harmless(ref: str) -> bool:
    """Its object is gone, so walking it can find nothing; what it alone reached may survive, so a clone with one keeps its
    own object store and the names (clone_state, preserve). A tracking ref's name is the remote's. A tag GitHub has by that
    name is a tag that moved: a clone borrowing from a lender that dropped the old object after a history rewrite. Any
    other dead ref is local work we cannot read: a refusal."""
    if ref.startswith("refs/remotes/"):
        return True
    return ref.startswith("refs/tags/") and any(git(m, "show-ref", "-q", "--verify", ref).returncode == 0 for m in origin_mirrors())


def reflog_tips(c: Path) -> tuple[set[str], str | None]:
    tips: set[str] = set()
    logs = c / ".git" / "logs"
    for dp, _, fns in os.walk(logs, onerror=None):
        for n in fns:
            try:
                with open(os.path.join(dp, n), errors="surrogateescape") as f:
                    for ln in f:
                        w = ln.split(None, 2)
                        if len(w) >= 2 and len(w[1]) == 40:     # git keeps an entry's old value alive as well as its new
                            tips.update(x for x in w[:2] if x.strip("0"))
            except OSError as e:
                return tips, f"reflog unreadable: {e.strerror}"
    return tips, None


def unique_commits(c: Path, dead: list[str] | None = None) -> tuple[list[str], int, list[str], str | None]:
    """(heads to bundle, commits the mirror lacks, commits like main's with other content, error). Every readable ref,
    HEAD, stash and reflog entry counts. Only the mirror proves a push: a local tracking ref is local. A dead ref
    refuses unless dead_ref_harmless, which names it in `dead`; a dangling origin/HEAD is not listed at all."""
    fe = git(c, "for-each-ref", "--format=%(objectname) %(refname)")     # no %(objecttype): one dead ref would kill the list
    said = [x for x in fe.stderr.splitlines() if x.strip() and not GONE_LENDER.match(x)]    # judged elsewhere
    if fe.returncode or said:                           # git warns past a ref it cannot read, and succeeds
        return [], 0, [], f"cannot list refs ({' '.join(said)[:120] or fe.stderr.strip()[:120]})"
    tips, nots = set(), set(mirror_tips())
    refs = [ln.split(None, 1) for ln in fe.stdout.splitlines()]
    chk = git(c, "cat-file", "--batch-check", stdin="".join(sha + "\n" for sha, _ in refs))
    if chk.returncode:
        return [], 0, [], f"cannot list refs ({chk.stderr.strip()[:120]})"
    typ = {w[0]: w[1] for w in (ln.split() for ln in chk.stdout.splitlines()) if len(w) >= 2}
    for sha, ref in refs:
        if typ.get(sha) in ("commit", "tag"):
            tips.add(sha)
        elif typ.get(sha, "missing") == "missing":
            if not dead_ref_harmless(ref):
                return [], 0, [], f"cannot list refs (missing object {sha} for {ref})"
            if dead is not None:
                dead.append(f"{sha} {ref}")
    h = git(c, "rev-parse", "-q", "--verify", "HEAD^{commit}")
    if h.returncode == 0:
        tips.add(h.stdout.strip())
    elif git(c, "symbolic-ref", "-q", "HEAD").returncode:
        return [], 0, [], "HEAD is unreadable"
    logged, err = reflog_tips(c)
    if err:
        return [], 0, [], err
    logged -= tips
    if logged:                               # a reflog line may name a commit gc already took: only live ones count
        chk = git(c, "cat-file", "--batch-check", stdin="\n".join(sorted(logged)) + "\n")
        if chk.returncode:
            return [], 0, [], f"cannot read reflog commits ({chk.stderr.strip()[:120]})"
        tips |= {w[0] for w in (ln.split() for ln in chk.stdout.splitlines()) if len(w) >= 2 and w[1] == "commit"}
    if not tips:
        return [], 0, [], None
    r = git(c, "rev-list", "--stdin", stdin="\n".join(sorted(tips) + ["^" + n for n in sorted(nots)]) + "\n")
    if r.returncode:
        return [], 0, [], f"cannot list commits ({r.stderr.strip()[:120]})"
    unique = r.stdout.split()
    own_tags = {sha for sha, _ in refs if typ.get(sha) == "tag" and sha not in nots}    # its commit may be pushed; its text is not
    if not unique:
        return sorted(own_tags), len(own_tags), [], None
    d = commit_digests(c, "--no-walk=unsorted", "--stdin", stdin="\n".join(sorted(unique)) + "\n")
    if d is None or set(d) != set(unique):
        return [], 0, [], "cannot read the commits the mirror lacks"
    keys = main_keys()
    changed = sorted(x for x, (k, dig) in d.items() if k in keys and dig not in keys[k])
    alone = {x for x, (k, _) in d.items() if k not in keys}
    if not alone:
        return sorted(own_tags), len(own_tags), changed, None
    par = git(c, "rev-list", "--parents", "--no-walk=unsorted", "--stdin", stdin="\n".join(sorted(alone)) + "\n")
    if par.returncode:
        return [], 0, [], f"cannot read parents ({par.stderr.strip()[:120]})"
    parents = {w for ln in par.stdout.splitlines() for w in ln.split()[1:]}
    return sorted((alone - parents) | own_tags), len(alone) + len(own_tags), changed, None


def disposable(path: str) -> bool:
    """Ignored is not disposable: only what a build or a hook writes again may go unpreserved."""
    p = path.rstrip("/")
    return (bool(DISPOSABLE_NAMES & set(p.split("/"))) or p.endswith(".pyc") or p in DISPOSABLE_EXACT
            or (path + "/").startswith(DISPOSABLE_DIRS))


def dirty_files(c: Path) -> tuple[list[str], int, int, int, str | None]:
    """(paths that exist, tracked changed, untracked, bytes, error)."""
    st = git(c, "status", "--porcelain=v1", "-z", "--untracked-files=normal", "--ignored=matching")
    if st.returncode:
        return [], 0, 0, 0, f"git status failed ({st.stderr.strip()[:120]})"
    recs = st.stdout.split("\0")
    paths, tracked, untracked, size = [], 0, 0, 0
    i = 0
    while i < len(recs):
        x = recs[i]
        i += 1
        if len(x) < 4:
            continue
        code, path = x[:2], x[3:]
        if code[0] in "RC":
            i += 1                           # -z: the old name is the next field
        if code == "!!" and disposable(path):
            continue
        untracked += code in ("??", "!!")
        tracked += code not in ("??", "!!")
        full = c / path
        if os.path.lexists(full):
            paths.append(path)
            t = Tree(full) if full.is_dir() and not full.is_symlink() else None
            size += t.size if t else os.lstat(full).st_size
    return paths, tracked, untracked, size, None


def filtered_paths(c: Path) -> list[str]:
    """Tracked paths a content filter stands between: git's status answers for the filtered bytes, not the file. A filter
    is named by an attribute and defined in any config, so the attribute is what is asked. Unreadable counts as filtered."""
    listed = git(c, "ls-files", "-z")
    attrs = git(c, "check-attr", "-z", "--stdin", "filter", stdin=listed.stdout)
    if listed.returncode or attrs.returncode:
        return ["?"]
    f = attrs.stdout.split("\0")
    return [f[i] for i in range(0, len(f) - 2, 3) if f[i + 2] not in ("unspecified", "unset")]


def gitlink_files(c: Path) -> list[str]:
    """git steps over the directory of an uninitialised submodule, so a file put there is in nobody's status."""
    out = []
    for ln in git(c, "ls-files", "-s", "-z").stdout.split("\0"):
        if ln.startswith("160000 "):
            path = ln.split("\t", 1)[1]
            try:
                with os.scandir(c / path) as it:
                    if any(it):
                        out.append(f"the submodule dir {path} holds files git does not look at")
            except (FileNotFoundError, NotADirectoryError):
                pass
            except OSError as e:
                out.append(f"the submodule dir {path}: {e.strerror}")
    return out


def clone_state(c: Path) -> dict:
    """{hard: reasons to skip, soft: reasons to bundle, tips, unique, dirty}."""
    out = {"hard": [], "soft": [], "tips": [], "unique": 0, "dirty": [], "changed": [], "tracked": 0}
    hard, soft = out["hard"], out["soft"]
    dotgit = c / ".git"
    if dotgit.is_file() or dotgit.is_symlink():
        hard.append(f"{c}: .git is a file/link (linked worktree or submodule) — its real repo is elsewhere")
        return out
    if git(c, "rev-parse", "--git-dir").returncode:
        hard.append(f"{c}: git cannot read it (corrupt or not a repo) — inspect by hand")
        return out
    for m in ("rebase-merge", "rebase-apply", "MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "BISECT_LOG"):
        if (dotgit / m).exists():
            hard.append(f"{c}: a {m} is in progress")
    for sub, what in (("worktrees", "linked worktrees"), ("modules", "submodules")):
        d = dotgit / sub
        try:
            if d.exists() and any(d.iterdir()):
                hard.append(f"{c}: has {what}; a bundle would not carry them")
        except OSError as e:
            hard.append(f"{c}: .git/{sub}: {e.strerror}")
    try:
        lfs = any(fns for _, _, fns in os.walk(dotgit / "lfs", onerror=_raise))
    except OSError as e:
        lfs = True
        hard.append(f"{c}: .git/lfs: {e.strerror}")
    if lfs or filtered_paths(c):
        hard.append(f"{c}: git-lfs or a content filter: a bundle holds the pointers, not the bytes")
    hard.extend(f"{c}: {x}" for x in gitlink_files(c))
    dead: list[str] = []
    tips, n, changed, err = unique_commits(c, dead)
    if err:
        hard.append(f"{c}: {err}")
    elif n:
        out["tips"], out["unique"] = tips, n
        no_remote = "" if git(c, "remote").stdout.strip() else ", no remote at all"
        soft.append(f"{c}: {n} commit(s) on no remote{no_remote}")
    if dead:
        size = Tree(dotgit / "objects").size
        if size > DIRTY_CAP:
            hard.append(f"{c}: {len(dead)} dead ref(s), and {human(size)} of own objects, over the {human(DIRTY_CAP)} preserve cap")
        else:
            out["dead_refs"] = dead
            soft.append(f"{c}: {len(dead)} dead ref(s): what they alone reached stays in its object store, so that is kept")
    if len(changed) > CHANGED_CAP:
        hard.append(f"{c}: {len(changed)} commits differ from main's under the same author and dates")
    elif changed:
        out["changed"] = changed
        soft.append(f"{c}: {len(changed)} commit(s) with main's author and dates but other content")
    flags = git(c, "ls-files", "-v", "-z")
    if flags.returncode:
        hard.append(f"{c}: cannot read the index flags")
    elif any(e and (e[0].islower() or (e[0] == "S" and os.path.lexists(c / e[2:]))) for e in flags.stdout.split("\0")):
        hard.append(f"{c}: a file is marked assume-unchanged or skip-worktree, so git status cannot vouch for it")
    paths, tracked, untracked, size, err = dirty_files(c)
    if err:
        hard.append(f"{c}: {err}")
    else:
        out["dirty"], out["tracked"] = paths, tracked
        if tracked:
            soft.append(f"{c}: {tracked} tracked file(s) changed")
        if untracked:
            soft.append(f"{c}: {untracked} untracked file(s)")
        if size > DIRTY_CAP:
            hard.append(f"{c}: {human(size)} of dirty files, over the {human(DIRTY_CAP)} preserve cap")
    return out


_CORPUS: list[tuple[str, str]] | None = None
_VOCAB: set[str] | None = None


def listed(d: Path, suffix: str, required: bool = False) -> list[str]:
    """The safety evidence in a dir. A required dir that is missing, or any dir we cannot list, stops the run."""
    try:
        with os.scandir(d) as it:
            return [e.path for e in it if e.name.endswith(suffix)]
    except FileNotFoundError:
        if required:
            raise RuntimeError(f"ledger corpus missing: {d}")
        return []
    except OSError as e:
        raise RuntimeError(f"ledger corpus unreadable: {d}: {e.strerror}")


def corpus() -> list[tuple[str, str]]:
    """[(file, text)] of every ledger file, item (live + closed), handoff in each seat clone, and our systemd units."""
    global _CORPUS
    if _CORPUS is None:
        _CORPUS = []
        files: list[str] = []
        for cr in corpus_roots():
            st = cr / "infrastructure" / "state"
            if (st / "ledger" / "events.jsonl").exists():
                files.append(str(st / "ledger" / "events.jsonl"))
            files += listed(st / "ledger" / "events", ".jsonl", True) + listed(st / "items", ".md", True)
            files += listed(st / "items" / "closed", ".md") + listed(st / "handoffs", ".md")
        if not os.environ.get("SCRATCH_REAP_CORPUS"):
            files += listed(HOME / ".config" / "systemd" / "user", ".service", True)
        for f in files:
            try:
                _CORPUS.append((f, open(f, encoding="utf-8", errors="replace").read()))
            except OSError as e:
                raise RuntimeError(f"ledger corpus unreadable: {f}: {e.strerror}")
    return _CORPUS


def vocab() -> set[str]:
    global _VOCAB
    if _VOCAB is None:
        _VOCAB = set()
        for _, text in corpus():
            _VOCAB.update(TOKEN.findall(text))
    return _VOCAB


def needles(p: Path, kind: str) -> list[str]:
    p = p.with_name(PIN.sub("", p.name))                # a crash's pin is still the path the ledger names
    n = {str(p), str(p).replace(str(HOME), "~", 1)}
    # A bare clone name is a word: 'linked', 'closeout' and 'stream-metrics' in any ledger line held 66 GB (2026-11-01).
    # Only a path, or `SEAT/name`, says which clone.
    n.add(p.name if kind == "session" else f"{p.parent.name}/{p.name}")   # session: its uuid
    return sorted(n)


def mention_blocks(f: str, line: str, now: float) -> bool:
    """An old mention is history and a bundle keeps the work; an open item, a unit, or anything recent still holds.
    A mention we cannot date holds."""
    limit = MENTION_DAYS * 86400
    if f.endswith(".jsonl"):
        try:
            ts = json.loads(line)["ts"]
            return now - dt.datetime.fromisoformat(str(ts).replace("Z", "+00:00")).timestamp() < limit
        except (ValueError, KeyError, TypeError):
            return True
    if "/items/closed/" in f or "/handoffs/" in f:
        try:
            return now - os.stat(f).st_mtime < limit
        except OSError:
            return True
    return True


def ledger_mentions(p: Path, kind: str, now: float | None = None) -> list[str]:
    now = time.time() if now is None else now
    hits = []
    for nd in needles(p, kind):
        # The needle's last token stands alone in any text that names it (the lookarounds below say so), so a set
        # lookup settles the common miss without touching ~100 MB of text once per candidate.
        keys = TOKEN.findall(nd)
        if keys and keys[-1] not in vocab():
            continue
        rx = re.compile(r"(?<![A-Za-z0-9_.-])" + re.escape(nd) + r"(?![A-Za-z0-9_-])")
        for f, text in corpus():
            if nd not in text:
                continue
            found = None
            for m in rx.finditer(text):
                line = text[text.rfind("\n", 0, m.start()) + 1: (text.find("\n", m.end()) + 1 or len(text) + 1) - 1]
                if mention_blocks(f, line, now):
                    found = line
                    break
            if found is not None:
                hits.append(f"{os.path.basename(f)} names '{nd}': …{found[:160].strip()}…")
                break
    return hits


# ---------------------------------------------------------------- verdicts
def mount_points() -> list[str]:
    """A bind mount has no mark a walk can see, and rmtree would go through it. Unreadable raises, which holds."""
    with open(MOUNTINFO, encoding="utf-8", errors="surrogateescape") as f:
        return [re.sub(r"\\([0-7]{3})", lambda m: chr(int(m[1], 8)), ln.split()[4]) for ln in f if ln.strip()]


class Ctx:
    def __init__(self, now: float):
        self.now = now
        self.live = Live(now)
        self.borrows = Borrows()

    def mounted(self, p: Path) -> list[str]:
        try:
            rp = os.path.realpath(p)
            ours = [os.path.realpath(r) for r in roots()]       # a bind above the candidate makes its name an alias
            return [f"a mount inside or above: {m}" for m in mount_points() if m == rp or m.startswith(rp + "/")
                    or (rp.startswith(m + "/") and any(m == r or m.startswith(r + "/") for r in ours))]
        except OSError as e:
            return [f"cannot read the mount table: {e.strerror}"]

    def refresh(self):
        self.now = time.time()
        self.live = Live(self.now)
        if self.now - self.borrows.taken > BORROW_REFRESH_S:
            self.borrows = Borrows()

    def global_holds(self) -> list[str]:
        return [f"cannot see a process: {x}" for x in self.live.blind[:3]] \
            + [f"cannot read a borrower file: {x}" for x in self.borrows.hold[:3]]


def guard(p: Path) -> str | None:
    rp = p.resolve()
    if p.is_symlink():
        return "a symlink"
    rs = [r.resolve() for r in roots()]
    if not any(r in rp.parents for r in rs):
        return "outside the reap roots, or a root itself"
    for q in protected():
        q = q.resolve()
        if rp == q or q in rp.parents or rp in q.parents:
            return f"protected: {q}"
    return None


def base_row(kind: str, p: Path, tree: Tree | None, now: float) -> dict:
    row = {"kind": kind, "path": str(p), "verdict": "DELETE", "why": [], "age_h": None, "bytes": None}
    if tree:
        row["age_h"], row["bytes"], row["sig"] = round((now - tree.newest) / 3600, 1), tree.size, tree.signature()
        row["top_ctime"] = tree.top_ctime
    return row


def refuse(row: dict, why: list[str]) -> dict:
    row.update(verdict="REFUSE", why=row["why"] + why)
    return row


def holds(p: Path, kind: str, ctx: Ctx, tree: Tree) -> list[str]:
    """Reasons that hold a whole candidate; common to clones and sessions."""
    why = list(ctx.global_holds()) + ctx.mounted(p)
    why += [f"unreadable: {e}" for e in tree.errors[:3]]
    why += ctx.live.users(p)
    why += ledger_mentions(p, kind, ctx.now)
    return why


def judge_clone(p: Path, ctx: Ctx) -> dict:
    tree = None
    bad = guard(p)
    if not bad:
        tree = Tree(p)
    row = base_row("clone", p, tree, ctx.now)
    if bad:
        return refuse(row, [bad])
    if tree.capped:
        return refuse(row, [f"more than {WALK_CAP} entries: too big to age safely; inspect by hand"])
    # Unreadable beats young: age cannot be proven over a tree we cannot read.
    if tree.errors:
        return refuse(row, [f"unreadable: {e}" for e in tree.errors[:3]])
    if ctx.now - tree.newest < ttl_s():
        row["verdict"] = "YOUNG"
        return row
    why = holds(p, "clone", ctx, tree) + ctx.borrows.of(p)
    st = clone_state(p)
    why += st["hard"]
    why += [f"canonical save inside: {s}" for s in unpreserved_canon(p, tree.saves)[:3]]
    why += [f"a repo nested inside: {n}" for n in tree.nested[:3]]
    if why:
        return refuse(row, why)
    if st["soft"]:
        row.update(verdict="ARCHIVE", why=st["soft"], tips=st["tips"], unique=st["unique"], dirty=st["dirty"],
                   changed=st["changed"], tracked=st["tracked"], dead_refs=st.get("dead_refs", []))
    return row


def has_loose_file(p: Path, clones: list[str]) -> bool:
    """An empty file still has a name someone chose. Only asked when a session's loose bytes come to nothing."""
    for dp, dns, fns in os.walk(p, onerror=_raise):
        if fns:
            return True
        dns[:] = [d for d in dns if os.path.join(dp, d) not in clones]
    return False


def judge_session(p: Path, ctx: Ctx) -> tuple[dict, list[dict]]:
    """(the session's row, one row per inner clone). A session's `bytes` is its loose residue, so no byte counts twice."""
    tree = None
    bad = guard(p)
    if not bad:
        tree = Tree(p)
    row = base_row("session", p, tree, ctx.now)
    if bad:
        return refuse(row, [bad]), []
    if tree.capped:
        return refuse(row, [f"more than {WALK_CAP} entries — too big to age safely; inspect by hand"]), []
    if ctx.now - tree.newest < ttl_s():
        row["verdict"] = "YOUNG"
        return row, []
    whole = [f"unreadable: {e}" for e in tree.errors[:3]] + ctx.global_holds() + ctx.mounted(p) + ctx.live.users(p) \
        + ledger_mentions(p, "session", ctx.now)        # what cannot be read may be what makes the session young
    if whole:
        return refuse(row, whole), []
    rows = [judge_clone(c, ctx) for c in find_clones(p, depth=8)]
    row["clones"] = [r["path"] for r in rows]
    row["bytes"] = max(0, tree.size - sum(r["bytes"] or 0 for r in rows))
    kept = [r for r in rows if r["verdict"] not in ("DELETE", "ARCHIVE")]
    why = ctx.borrows.of(p)                             # a bare repo is no clone: this is its only check
    loose = [s for s in tree.saves if not any(s.startswith(r["path"] + "/") for r in rows)]    # a clone answers for its own
    why += [f"canonical save inside: {s}" for s in canonical_saves(loose)[:3]]
    if kept:
        why.append(f"{len(kept)} inner clone(s) kept: {kept[0]['path']}: {(kept[0]['why'] or ['?'])[0][:160]}")
    if row["bytes"] > RESIDUE_CAP:
        why.append(f"{human(row['bytes'])} of loose files, over the {human(RESIDUE_CAP)} preserve cap")
    if why:
        return refuse(row, why), rows
    if row["bytes"] or has_loose_file(p, row["clones"]):
        row.update(verdict="ARCHIVE", why=[f"{p}: {human(row['bytes'])} of loose session files"])
    return row, rows


def judge_fixture(p: Path, ctx: Ctx) -> dict:
    """An `enact_*` selftest fixture dir (RM_SCRATCH_FIX_ENACT_DIRS_UNREAPED): regenerable, no repo, so no archive."""
    bad = guard(p)
    tree = None if bad else Tree(p)
    row = base_row("fixture", p, tree, ctx.now)
    if bad:
        return refuse(row, [bad])
    if tree.capped or tree.errors:
        return refuse(row, ["too big to age safely" if tree.capped else f"unreadable: {tree.errors[0]}"])
    if ctx.now - tree.newest < ttl_s():
        row["verdict"] = "YOUNG"
        return row
    why = holds(p, "session", ctx, tree) + ctx.borrows.of(p) + [f"a repo nested inside: {n}" for n in tree.nested[:3]]
    return refuse(row, why) if why else row


def judge_all(ctx: Ctx) -> list[dict]:
    rows = []
    for kind, p in candidates():
        if kind == "fixture":
            rows.append(judge_fixture(p, ctx))
        elif kind == "clone":
            rows.append(judge_clone(p, ctx))
        else:
            s, inner = judge_session(p, ctx)
            rows += inner + [s]
    return rows


def human(n: int | None) -> str:
    if n is None:
        return "?"
    for u in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or u == "TB":
            return f"{n:.1f} {u}" if u != "B" else f"{n} B"
        n /= 1024
    return "?"


# ---------------------------------------------------------------- bundle, restore-test, log
class PreserveFailed(Exception):
    pass


class Refused(PreserveFailed):
    """The clone cannot be preserved through no fault of the tool: a refusal, reported, not a failed run."""


class OverCap(Refused):
    """Too big to keep."""


class Unreadable(Refused):
    """Git cannot read the clone's own objects, so there is nothing whole to bundle. It stays, and stays reported."""


BROKEN_OBJECTS = re.compile(r"Could not read|bad object|missing (blob|tree|commit|object)|nonexistent object|"
                            r"revision walk setup failed|unable to read")


def must_read(r: subprocess.CompletedProcess, what: str) -> subprocess.CompletedProcess:
    """must(), for a step that reads the clone: its broken objects are a refusal, any other error is ours."""
    if r.returncode and BROKEN_OBJECTS.search(r.stderr or ""):
        raise Unreadable(f"{what}: {r.stderr.strip()[:160]}")
    return must(r, what)


def must(r: subprocess.CompletedProcess, what: str) -> subprocess.CompletedProcess:
    if r.returncode:
        raise PreserveFailed(f"{what}: {(r.stderr or r.stdout).strip()[:160]}")
    return r


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def archive_root() -> Path:
    """Never created here: a missing root means the D: drive is not mounted, and writing there would fill /."""
    try:
        a = Path(leftovers.default_archive_root())
    except SystemExit as e:                 # leftovers.py is a CLI: it exits when agent storage cannot be read
        raise PreserveFailed(f"archive root unknown: {e}")
    if not a.is_dir():
        raise PreserveFailed(f"archive root {a} is missing")
    return a


def make_bundle(c: Path, tips: list[str], work: Path) -> Path:
    """A bundle built in a throwaway repo that borrows the clone: the clone is not written (a pin ref there would
    reset its age), and a restore into an empty repo that sees only the store proves nothing is left behind."""
    src, dst, out = work / "src.git", work / "dst.git", work / "clone.bundle"
    for r in (src, dst):
        must(subprocess.run(["git", "init", "-q", "--bare", str(r)], capture_output=True, text=True), "git init")
    (src / "objects" / "info" / "alternates").write_text(str(c / ".git" / "objects") + "\n")
    for i, t in enumerate(tips):
        must_read(git(src, "update-ref", f"refs/rm/{i}", t), "pin tip")
    must_read(git(src, "bundle", "create", "-q", str(out), *[f"refs/rm/{i}" for i in range(len(tips))],
                  *["^" + b for b in sorted(set(mirror_tips()))], timeout=1800), "git bundle create")
    if out.stat().st_size > BUNDLE_CAP:
        raise OverCap(f"bundle is {human(out.stat().st_size)}, over the {human(BUNDLE_CAP)} cap")
    must(git(dst, "bundle", "verify", str(out)), "git bundle verify")
    must(git(dst, "fetch", "-q", str(out), "refs/rm/*:refs/rm/*", timeout=1800), "restore test")
    got = git(dst, "for-each-ref", "--format=%(objectname)", "refs/rm/").stdout.split()
    if sorted(got) != sorted(tips):
        raise PreserveFailed(f"restore test: {len(got)} of {len(tips)} tips came back")
    return out


def proved_objects() -> set[str]:
    """Every object the mirrors reach from origin/main and refs/tags: what GitHub holds, by id. A seat clone's refs are not
    in this. A mirror that cannot be walked adds nothing, so an unreadable one excuses nothing."""
    out: set[str] = set()
    for m in origin_mirrors():
        tags = git(m, "for-each-ref", "--format=%(objectname)", "refs/tags/")
        tips = [r.stdout.strip() for r in (git(m, "rev-parse", "-q", "--verify", x + "^{commit}")
                                           for x in ("refs/remotes/origin/main", "refs/heads/main")) if r.returncode == 0]
        if tags.returncode or not tips:
            continue
        r = git(m, "rev-list", "--objects", "--stdin", stdin="\n".join(tips + tags.stdout.split()) + "\n", timeout=1800)
        if r.returncode == 0:
            out.update(ln[:40] for ln in r.stdout.splitlines())
    return out


def make_residual(c: Path, tips: list[str], work: Path, why: str) -> tuple[list[Path], dict]:
    """A clone from before a history rewrite differs from GitHub in every commit hash and tag, and the bundle of that is
    the whole history. What can be lost is objects, so the proof is by object: a self-contained pack of every object the
    tips reach and the mirrors do not (commits and trees too: they hold names, modes and history), plus the ref list. The
    pack over RESIDUE_CAP is OverCap, a refusal, and so is an unreadable proving repo, since then all of it is residual."""
    src = work / "residual_src.git"
    must(subprocess.run(["git", "init", "-q", "--bare", str(src)], capture_output=True, text=True), "git init")
    (src / "objects" / "info" / "alternates").write_text(str(c / ".git" / "objects") + "\n")
    listed = must(git(src, "rev-list", "--objects", "--stdin", stdin="\n".join(tips) + "\n", timeout=1800), "git rev-list --objects")
    # No ^mirror tips here: they would drop objects before proved_objects() has shown any mirror can actually be walked.
    paths = {ln[:40]: ln[41:] for ln in listed.stdout.split("\n") if ln}
    left = sorted(set(paths) - proved_objects())
    chk = must(git(src, "cat-file", "--batch-check", stdin="".join(x + "\n" for x in left)), "git cat-file")
    rows = [ln.split() for ln in chk.stdout.splitlines()]
    if len(rows) != len(left) or any(len(w) != 3 for w in rows):
        raise PreserveFailed("an object the tips reach cannot be read")
    if sum(int(w[2]) for w in rows if w[1] == "blob") > RESIDUE_CAP * 8:     # do not pack what cannot fit, even compressed
        raise OverCap(f"{why}, and the blobs on no mirror cannot fit the {human(RESIDUE_CAP)} cap")
    made = [write_text_out(work / "residual.txt", subprocess.CompletedProcess([], 0, "".join(
                f"{w[0]} {w[1]} {w[2]} {paths[w[0]]}\n" for w in rows), ""), "residual list"),
            write_text_out(work / "refs.txt", git(c, "for-each-ref", "--format=%(objectname) %(refname)"), "git for-each-ref")]
    if not left:
        return made, {"objects": 0, "pack_bytes": 0, "instead_of": why}
    h = must(git(src, "pack-objects", "-q", str(work / "residual"), stdin="".join(x + "\n" for x in left), timeout=1800),
             "git pack-objects")
    pack = work / "residual.pack"
    (work / f"residual-{h.stdout.strip()}.pack").rename(pack)
    if pack.stat().st_size > RESIDUE_CAP:
        raise OverCap(f"{why}, and the objects on no mirror pack to {human(pack.stat().st_size)}, over the {human(RESIDUE_CAP)} cap")
    idx = work / "restored.idx"
    must(git(src, "index-pack", "-o", str(idx), str(pack), timeout=1800), "restore test")
    with open(idx, "rb") as f:
        shown = subprocess.run(["git", "show-index"], stdin=f, capture_output=True, text=True)
    if shown.returncode or {ln.split()[1] for ln in shown.stdout.splitlines()} != set(left):
        raise PreserveFailed("restore test: the residual pack does not hold every object it was given")
    return made + [pack], {"objects": len(left), "pack_bytes": pack.stat().st_size, "instead_of": why}


def write_text_out(out: Path, r: subprocess.CompletedProcess, what: str) -> Path:
    must(r, what)
    out.write_bytes(r.stdout.encode("utf-8", "surrogateescape"))
    return out


def make_index_state(c: Path, work: Path) -> list[Path]:
    """What a tar of the worktree cannot hold: every index entry with its mode, and the staged blobs, by id. Applying a
    patch here, even to a private index, refreshes the clone's object files, and that is a write, so nothing is applied
    in the clone. The clone's config chooses a diff's drivers, so those are switched off; the patches are for reading."""
    plain = ("-c", "diff.autoRefreshIndex=false", "diff", "--binary", "--no-ext-diff", "--no-textconv", "--no-color")
    made = [write_text_out(work / "status.txt", git(c, "status", "--porcelain=v2", "--branch"), "git status"),
            write_text_out(work / "unstaged.patch", git(c, *plain), "git diff"),
            write_text_out(work / "staged.patch", git(c, *plain, "--cached"), "git diff --cached"),
            write_text_out(work / "index.txt", git(c, "ls-files", "-s", "-z"), "git ls-files")]
    base = "HEAD" if git(c, "rev-parse", "-q", "--verify", "HEAD").returncode == 0 else EMPTY_TREE
    f = must(git(c, "diff-index", "--cached", "--no-renames", "--no-abbrev", "-z", base), "git diff-index").stdout.split("\0")
    top = work / "staged"
    for meta, path in zip(f[0::2], f[1::2]):
        w = meta.split()
        if w[4] == "D" or w[1] == "160000" or w[0] == ":160000":
            continue                                    # index.txt carries a deletion and a gitlink's commit
        if w[4] == "U":
            raise PreserveFailed(f"{path} is unmerged")
        blob = must(git(c, "cat-file", "blob", w[3]), f"staged {path}").stdout.encode("utf-8", "surrogateescape")
        if hashlib.sha1(b"blob %d\0" % len(blob) + blob).hexdigest() != w[3]:
            raise PreserveFailed(f"staged {path}: the bytes read are not the blob")
        top.mkdir(exist_ok=True)
        (top / w[3]).write_bytes(blob)
    if top.exists():
        make_tar(top, None, work / "staged.tar.gz")
        made.append(work / "staged.tar.gz")
    return made


def make_changed(c: Path, shas: list[str], out: Path) -> Path:
    """Commits that main rewrote with other content: their own diffs, not the old history under them."""
    with open(out, "wb") as f:
        for sha in shas:
            r = git(c, "show", "--binary", "--no-ext-diff", "--no-textconv", "--no-color", "--diff-merges=first-parent", "--format=fuller", sha)
            must(r, f"git show {sha[:10]}")
            f.write(r.stdout.encode("utf-8", "surrogateescape"))
    if out.stat().st_size > BUNDLE_CAP:
        raise OverCap(f"rewritten commits are {human(out.stat().st_size)}, over the {human(BUNDLE_CAP)} cap")
    return out


def make_tar(top: Path, paths: list[str] | None, out: Path):
    cmd = ["tar", "-C", str(top), "-czf", str(out)]
    if paths is None:
        cmd.append(".")
        inp = None
    else:
        cmd += ["--null", "--verbatim-files-from", "-T", "-"]
        inp = b"\0".join(os.fsencode(x) for x in paths) + b"\0"
    env = {k: v for k, v in os.environ.items() if k not in ("TAR_OPTIONS", "GZIP")}    # the options here are all of them
    r = subprocess.run(cmd, input=inp, capture_output=True, timeout=1800, env=env)
    if r.returncode:
        raise PreserveFailed(f"tar: {r.stderr.decode('utf-8', 'replace').strip()[:160]}")
    t = subprocess.run(["tar", "-tzf", str(out)], capture_output=True, timeout=600, env=env)
    if t.returncode or not t.stdout.strip():
        raise PreserveFailed("tar: the archive does not list back")


def acts_append(root: Path, rec: dict):
    with open(root / "acts.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def local_ts() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def durable(p: Path, must_sync: bool = True) -> None:
    """On disk, not in a cache: the source is about to go. Some filesystems do not implement a directory fsync, and only
    that refusal is forgiven: a failed one raises, and the source stays."""
    fd = os.open(p, os.O_RDONLY)
    try:
        os.fsync(fd)
    except OSError as e:
        if must_sync or e.errno not in (errno.EINVAL, errno.ENOTSUP):
            raise
    finally:
        os.close(fd)


def rename_new(src: Path, dst: Path):
    """rename(2) would swallow an empty dir someone has just made and entered; RENAME_NOREPLACE cannot."""
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.renameat2(-100, os.fsencode(src), -100, os.fsencode(dst), 1):   # AT_FDCWD, RENAME_NOREPLACE
        n = ctypes.get_errno()
        raise OSError(n, os.strerror(n), str(dst))


def preserve(row: dict) -> str:
    """Bundle and tar one ARCHIVE row, proved restorable, logged to acts.jsonl. -> the archive dir."""
    p = Path(row["path"])
    root = archive_root()
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", p.name)[:60] + "-" + hashlib.sha1(str(p).encode()).hexdigest()[:8]
    day = root / time.strftime("%Y-%m-%d") / "scratch_expiry"
    sd = state_dir() / "work"
    sd.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=sd) as td:
        work = Path(td)
        made = []
        if row["kind"] == "clone":
            if row.get("unique") and not row.get("tips"):
                raise PreserveFailed("commits are unique here, yet there is no tip to bundle")
            if row.get("tips"):
                try:
                    made.append(make_bundle(p, row["tips"], work))
                except OverCap as e:
                    (work / "clone.bundle").unlink(missing_ok=True)
                    files, row["residual"] = make_residual(p, row["tips"], work, str(e))
                    made += files
                except Unreadable as e:       # no bundle can read it: the store itself is all there is to keep
                    size = Tree(p / ".git").size
                    if size > BROKEN_CAP:
                        raise Unreadable(f"{e}; {human(size)} of .git, over the {human(BROKEN_CAP)} preserve cap") from e
                    (work / "clone.bundle").unlink(missing_ok=True)
                    make_tar(p, [".git"], work / "broken_git.tar.gz")
                    made.append(work / "broken_git.tar.gz")
                    row["broken"] = str(e)
            if row.get("dead_refs"):
                (work / "dead_refs.txt").write_text("\n".join(row["dead_refs"]) + "\n", errors="surrogateescape")
                make_tar(p, [".git/objects"], work / "objects.tar.gz")
                made += [work / "dead_refs.txt", work / "objects.tar.gz"]
            if row.get("changed"):
                made.append(make_changed(p, row["changed"], work / "rewritten.patch"))
            if row.get("tracked"):
                made += make_index_state(p, work)
            if row.get("dirty"):
                make_tar(p, row["dirty"], work / "dirty.tar.gz")
                made.append(work / "dirty.tar.gz")
        else:
            make_tar(p, None, work / "residue.tar.gz")
            made.append(work / "residue.tar.gz")
        if not made:
            raise PreserveFailed("nothing to preserve, yet the row says ARCHIVE")
        day.mkdir(parents=True, exist_ok=True)
        tmp = Path(tempfile.mkdtemp(dir=day, prefix=".incoming-"))      # a new dir per attempt: nothing is overwritten
        files = {}
        for f in made:
            h = sha256(f)
            shutil.copyfile(f, tmp / f.name)
            if sha256(tmp / f.name) != h:
                raise PreserveFailed(f"copy of {f.name} to the archive does not match")
            files[f.name] = h
        (tmp / "manifest.json").write_text(json.dumps({
            "path": row["path"], "kind": row["kind"], "bytes": row["bytes"], "age_h": row["age_h"], "why": row["why"],
            "tips": row.get("tips", []), "unique_commits": row.get("unique", 0), "dirty_paths": row.get("dirty", []),
            "rewritten_commits": row.get("changed", []), "files": files, "residual": row.get("residual"),
            "broken": row.get("broken"),
            "restore": "git clone --shared /home/mandrake/rm/store.git r && git -C r fetch clone.bundle "
                       "'refs/rm/*:refs/heads/rescued/*'; check out status.txt's base; tar -xzf staged.tar.gz -C blobs; "
                       "git -C r hash-object -w --no-filters blobs/*; git -C r read-tree --empty; "
                       "git -C r update-index -z --index-info < index.txt; tar -xzf dirty.tar.gz -C r; "
                       "the patches are for reading; a residual.pack instead of a bundle: copy it to "
                       "r/.git/objects/pack, git index-pack it there, then git cat-file -p the ids in residual.txt"}, indent=1))
        for f in tmp.iterdir():
            durable(f)
        durable(tmp, False)
        dest = day / f"{slug}-{int(time.time())}-{os.path.basename(tmp)[-8:]}"
        os.rename(tmp, dest)
        for q in (day, day.parent, root):               # each new link, up to the root that outlives them
            durable(q, False)
    manifest = dest / "manifest.json"
    acts_append(root, {"ts": local_ts(), "kind": "scratch-" + row["kind"], "path": row["path"], "size": row["bytes"],
                       "archive": str(dest), "manifest": str(manifest),
                       "verify": "residual pack indexed, every object listed; the rest is reachable on the mirrors; "
                                 "tar listed; sha256 matched on the archive" if row.get("residual")
                                 else "bundle restored into an empty repo; tar listed; sha256 matched on the archive",
                       "evidence": "; ".join(row["why"])[:300]})
    return str(dest)


def act(row: dict, ctx: Ctx, failures: list[str]) -> int:
    """Re-judge one row, preserve it if asked, delete it. -> bytes freed."""
    ctx.refresh()
    p = Path(row["path"])
    if row["kind"] == "fixture":
        again = judge_fixture(p, ctx)
    elif row["kind"] == "clone":
        again = judge_clone(p, ctx)
    else:
        again, inner = judge_session(p, ctx)
        if inner:
            again = refuse(again, [f"{len(inner)} inner clone(s) still present"])
    if again["verdict"] not in ("DELETE", "ARCHIVE"):
        row.update(verdict=again["verdict"], why=["changed since the scan:"] + again["why"])
        return 0
    row.update({k: v for k, v in again.items() if k not in ("verdict",)})
    row["verdict"] = again["verdict"]
    if row["verdict"] == "ARCHIVE":
        try:
            row["archive"] = preserve(row)
        except (PreserveFailed, OSError, subprocess.SubprocessError) as e:
            row.update(verdict="REFUSE", why=[f"could not preserve it, so it stays: {e}"] + row["why"])
            if not isinstance(e, Refused):
                failures.append(f"{row['path']}: {e}")
            return 0
    try:
        moved = os.lstat(p).st_ctime_ns != row.get("top_ctime")
    except OSError:
        moved = True
    if moved:                                           # the last moment the top's ctime means anything
        row.update(verdict="REFUSE", why=["its top changed while it was being preserved"])
        return 0
    pin = p.with_name(f".reaping-{os.getpid()}-{PIN.sub('', p.name)}")
    try:
        os.rename(p, pin)
    except OSError as e:
        failures.append(f"pin {p}: {e}")
        row.update(verdict="REFUSE", why=[f"could not pin it: {e}"])
        return 0
    late = pinned_holds(p, pin, row, ctx)
    if late:
        try:
            rename_new(pin, p)
        except FileExistsError:
            failures.append(f"unpin {p}: a new {p.name} stands there; the old tree waits at {pin}")
            row.update(verdict="REFUSE", why=[f"left pinned at {pin}: a new dir took its name"] + late)
            return 0
        except OSError as e:
            failures.append(f"unpin {p}: {e}")
        row.update(verdict="REFUSE", why=["arrived while it was being reaped:"] + late)
        return 0
    try:
        size = row["bytes"] or 0
        shutil.rmtree(pin)
    except OSError as e:
        failures.append(f"rmtree {pin}: {e}")
        row.update(verdict="REFUSE", why=[f"rmtree failed part way: {e}"])
        return 0
    row["verdict"] = "DELETED"
    return size


def pinned_holds(p: Path, pin: Path, row: dict, ctx: Ctx) -> list[str]:
    """The last look, with the path out of reach: anything using it now, or written to it since it was judged."""
    ctx.refresh()
    why = ctx.global_holds() + ctx.mounted(pin) + ctx.live.users(pin) + ctx.live.users(p) + ctx.borrows.of(pin) + ctx.borrows.of(p)
    tree = Tree(pin)
    if tree.errors:
        why.append(f"unreadable: {tree.errors[0]}")
    if tree.capped:
        why.append("grew past the walk's cap: not read whole")
    if tree.signature() != row.get("sig"):
        why.append("not the tree that was judged and preserved")     # every entry: an old mtime proves nothing
    return why


def apply_rows(rows: list[dict], ctx: Ctx, max_s: float, failures: list[str], started: float) -> tuple[int, int]:
    """Clones biggest first, then session shells, so a shell is judged with its clones already gone. The budget runs
    from the start of the run: a long scan spends it too, or systemd's limit kills the run before it writes its record."""
    freed, deferred = 0, 0
    todo = [r for r in rows if r["verdict"] in ("DELETE", "ARCHIVE")]
    todo.sort(key=lambda r: (r["kind"] != "clone", -(r["bytes"] or 0)))
    for r in todo:
        if max_s and time.time() - started > max_s:
            r["deferred"] = True
            deferred += 1
            continue
        freed += act(r, ctx, failures)
    return freed, deferred


def fixture_dirs() -> list[Path]:
    """~/.seat-tmp/<SEAT>/selftest_*: a selftest's tempfile prefix, so no agent's work lives there."""
    found = [Path(s) for r in roots() if r.name == ".seat-tmp" for s in glob.glob(str(r / "*" / "selftest_*"))]
    # tempfile.mkdtemp() names (tmp + 8 of [a-z0-9_]): selftests make them at import and never remove them (27k stood
    # under ~/.seat-tmp/BENCH on 2026-11-01, past the runner's per-test TMPDIR); same day-old, nothing-uses-it rule.
    found += [Path(s) for r in roots() if r.name == ".seat-tmp" for s in glob.glob(str(r / "*" / "tmp*"))
              if re.fullmatch(r"tmp[a-z0-9_]{8}", os.path.basename(s))]
    return [p for p in found if p.is_dir() and not p.is_symlink()]


def keeps_work(p: Path) -> bool:
    """A directory with a git repo or a savegame anywhere inside is work, not a fixture. A walk error says yes."""
    bad = []
    for _dp, dns, fns in os.walk(p, onerror=bad.append):
        if ".git" in dns or ".git" in fns or any(f.endswith(".rws") for f in fns):
            return True
    return bool(bad)


def sweep_fixtures(ctx: Ctx, apply: bool, deadline: float) -> dict:
    """Remove selftest fixtures a day untouched. run_selftests.py cleans its own; this catches a test run by hand or
    killed. Nothing is archived: the commits in a fixture's `c` clone are unpushed by construction. A path anything
    uses, mounts or borrows from, or that cannot be read whole, stays."""
    out = {"removed": 0, "bytes": 0, "young": 0, "held": 0, "deferred": 0}
    for p in fixture_dirs():
        if apply and deadline and time.time() > deadline:
            out["deferred"] += 1
            continue
        tree = None if guard(p) else Tree(p)
        if tree is not None and not p.name.startswith("selftest_") and keeps_work(p):
            out["held"] += 1                        # a mkdtemp name proves nothing: clones and saves get the full judgment
            continue
        if tree is None or tree.capped or tree.errors:
            out["held"] += 1
        elif ctx.now - tree.newest < FIXTURE_TTL_S:
            out["young"] += 1
        elif ctx.global_holds() or ctx.mounted(p) or ctx.live.users(p) or ctx.borrows.of(p):
            out["held"] += 1
        else:
            try:
                if apply:
                    if time.time() - ctx.live.taken > FIXTURE_RECHECK_S:     # a sweep of hundreds outlives its snapshot
                        ctx.refresh()
                        again = Tree(p)
                        if ctx.global_holds() or ctx.live.users(p) or ctx.borrows.of(p) or again.errors \
                                or ctx.now - again.newest < FIXTURE_TTL_S:
                            out["held"] += 1
                            continue
                    shutil.rmtree(p)
                out["removed"] += 1
                out["bytes"] += tree.size
            except OSError:
                out["held"] += 1
    return out


# ---------------------------------------------------------------- sanity: speak up at both ends of a run
def sanity_limits() -> dict:
    p = os.environ.get("SCRATCH_REAP_SANITY") or str(Path(__file__).with_name("scratch_reap_sanity.json"))
    return json.loads(Path(p).read_text())


def rm_scratch() -> Path:
    return Path(os.environ.get("SCRATCH_REAP_RM_SCRATCH", RM / "scratch"))


def unique_gb(p: Path) -> float | None:
    """One du over the tree counts a hardlink once: clones share their packs. None: no reading, which is itself a problem."""
    if not p.is_dir():
        return 0.0
    try:
        r = subprocess.run(["du", "-s", "-B1", str(p)], capture_output=True, text=True, timeout=SANITY_DU_S)
    except subprocess.TimeoutExpired:
        return None
    return round(int(r.stdout.split()[0]) / 1e9, 2) if r.stdout.strip() else None


def pool_measures() -> dict:
    """The worker pool, as its cap sees it. It counts relentless/clones alone; rm/scratch has its own lines."""
    try:
        import scratch_clone
        d = scratch_clone.pool_reading()
        return {k: d[j] for k, j in (("pool_clones", "count"), ("pool_clones_cap", "max_clones"), ("pool_gb", "gb"),
                                     ("pool_gb_cap", "max_gb"))}
    except Exception:  # noqa: BLE001 - a sanity reading never kills the run it reports on
        return {"pool_clones": None, "pool_clones_cap": None, "pool_gb": None, "pool_gb_cap": None}


def fixture_age_h(p: Path, now: float) -> float | None:
    """Hours since anything inside a fixture was touched: the SAME newest-content reading sweep_fixtures judges YOUNG
    by. A directory's own mtime is not it (an epoch-stamped dir holding fresh files read 498211 h old while the reaper
    rightly kept it). A tree the walk cannot read whole falls back to the directory's own stamps."""
    try:
        tree = Tree(p)
        if not (tree.capped or tree.errors):
            return max(0.0, now - tree.newest) / 3600
        st = p.lstat()
        return max(0.0, now - max(touched(st))) / 3600
    except OSError:
        return None


def measure(now: float, rows: list[dict] | None, prev: dict) -> dict:
    """The readings. Before work, `rows` is None and what only a judged run knows comes from the last run's record."""
    fx_ages = []
    for p in fixture_dirs():
        age = fixture_age_h(p, now)
        if age is not None:
            fx_ages.append(age)
    sessions = sum(1 for r in roots() for s in glob.glob(str(r / "*" / "claude-*" / "*" / "*"))
                   if UUID.match(os.path.basename(s)))
    scratch = rm_scratch()
    m = pool_measures()
    m.update(rm_scratch_clones=len(find_clones(scratch)) if scratch.is_dir() else 0, rm_scratch_gb=unique_gb(scratch),
             selftest_dirs=len(fx_ages), selftest_stale=sum(1 for a in fx_ages if a * 3600 >= FIXTURE_TTL_S),
             session_dirs=sessions, root_disk_pct=round(100 * (lambda u: u.used / u.total)(shutil.disk_usage("/")), 1))
    if rows is None:
        m.update(refused=(prev.get("counts") or {}).get("REFUSE"), refused_gb=round(prev.get("refused_bytes", 0) / 1e9, 2),
                 oldest_h=round(max(fx_ages + [prev.get("oldest_h") or 0.0]), 1))
    else:
        left = [r for r in rows if r["verdict"] not in ("DELETED", "YOUNG")]
        bad = [r for r in rows if r["verdict"] == "REFUSE"]
        m.update(refused=len(bad), refused_gb=round(sum(r["bytes"] or 0 for r in bad) / 1e9, 2),
                 oldest_h=round(max([r["age_h"] or 0.0 for r in left] + fx_ages, default=0.0), 1))
    return m


def judge_sanity(phase: str, m: dict) -> list[str]:
    """-> every line this reading is over, by the limits of that end of the run. No reading is a problem, never a pass."""
    lim = sanity_limits()[phase]
    out = []
    for key in ("pool_clones", "pool_gb"):
        if m.get(key) is None:
            out.append(f"{key}: no reading")
        elif m[key] > m[key + "_cap"]:
            out.append(f"{key} {m[key]} over the pool cap {m[key + '_cap']}")
    for key, line in lim.items():
        if m.get(key) is None:
            out.append(f"{key}: no reading")
        elif m[key] > line:
            out.append(f"{key} {m[key]} over {line}")
    return out


def refusal_reasons(rows: list[dict], top: int = 4) -> list[str]:
    """The residual, by why: the first reason of each refused row with its paths taken out."""
    n: dict[str, list] = {}
    for r in rows:
        if r["verdict"] == "REFUSE":
            why = re.sub(r"\S*/\S*:? ?", "", (r["why"] or ["?"])[0])[:60]
            n.setdefault(why, [0, 0])
            n[why][0] += 1
            n[why][1] += r["bytes"] or 0
    return [f"{c} refused, {human(b)}: {w}" for w, (c, b) in sorted(n.items(), key=lambda kv: -kv[1][1])[:top]]


def sanity_write(sd: Path, phase: str, m: dict, problems: list[str]):
    """On disk before the work starts: the Dispatcher reads this, so a run that dies has already spoken. A new start
    drops the last run's end, whose alarm belongs to that run."""
    p = sd / "sanity.json"
    rec = {}
    if phase != "start":
        try:
            rec = json.loads(p.read_text())
        except (OSError, ValueError):
            rec = {}
    rec[phase] = {"at": time.time(), "measures": m, "problems": problems}
    write_json(p, rec)
    durable(p)
    durable(sd, False)


def sanity_start(sd: Path, now: float) -> dict:
    """Never raises: a bad reading or limits file is said aloud in the record, and the run still runs."""
    try:
        m = measure(now, None, last_record(sd))
        problems = judge_sanity("start", m)
    except Exception as e:  # noqa: BLE001
        m, problems = {}, [f"sanity start blind: {type(e).__name__}: {str(e)[:160]}"]
    sanity_write(sd, "start", m, problems)
    return m


def sanity_end(sd: Path, now: float, rows: list[dict], rec: dict):
    try:
        m = measure(now, rows, rec)
        problems = judge_sanity("end", m)
    except Exception as e:  # noqa: BLE001
        m, problems = {}, [f"sanity end blind: {type(e).__name__}: {str(e)[:160]}"]
    if rec.get("failures"):
        problems.append(f"{len(rec['failures'])} failure(s): {rec['failures'][0][:160]}")
    if rec.get("deferred"):
        problems.append(f"{rec['deferred']} row(s) deferred past the time budget")
    if problems:
        problems += refusal_reasons(rows)
    sanity_write(sd, "end", m, problems)
    rec["oldest_h"] = m.get("oldest_h")


# ---------------------------------------------------------------- records
def free_gb(path: str = "/") -> float:
    return round(shutil.disk_usage(path).free / 1e9, 1)


def write_json(p: Path, obj):
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, indent=1))
    os.replace(tmp, p)


def record(sd: Path, rec: dict):
    """last_run.json: the record ops_watch alarms on. last_ok_epoch survives failed runs, so failure keeps aging."""
    try:
        prev = json.loads((sd / "last_run.json").read_text()).get("last_ok_epoch")
    except (OSError, ValueError, AttributeError):
        prev = None
    rec["last_ok_epoch"] = rec["end_epoch"] if rec["ok"] else prev
    write_json(sd / "last_run.json", rec)


def last_record(sd: Path) -> dict:
    try:
        rec = json.loads((sd / "last_run.json").read_text())
        return rec if isinstance(rec, dict) else {}
    except (OSError, ValueError):
        return {}


def rotate(p: Path, cap: int = 64 * 1024 ** 2):
    try:
        if p.stat().st_size > cap:
            os.replace(p, p.with_name(p.name + ".1"))
    except FileNotFoundError:
        pass


def new_alarms(rows: list[dict], sd: Path, stamp: str, apply: bool):
    """Each refusal once: a row an hour for 3,000 paths is noise nobody reads. Dry runs do not spend the memory."""
    if not apply:
        return
    seen_f = sd / "alarms_seen.json"
    try:
        seen = set(json.loads(seen_f.read_text()))
    except (OSError, ValueError):
        seen = set()
    cur, fresh = set(), []
    for r in rows:
        if r["verdict"] != "REFUSE":
            continue
        key = r["path"] + "|" + re.sub(r"\d+", "#", (r["why"] or [""])[0])[:120]
        cur.add(key)
        if key not in seen:
            fresh.append(f"{stamp} REFUSE {r['path']} ({human(r['bytes'])}, {r['age_h']} h): {(r['why'] or ['?'])[0]}"
                         + (f" (+{len(r['why']) - 1} more)" if len(r["why"]) > 1 else ""))
    rotate(sd / "alarms.log")
    with open(sd / "alarms.log", "a") as f:
        for ln in fresh:
            f.write(ln + "\n")
    write_json(seen_f, sorted(cur))


def pressure_check() -> int:
    """Runs on its own short timer. The TTL does not move; the point is not to wait for the next hour."""
    sd = state_dir()
    sd.mkdir(parents=True, exist_ok=True)
    line = float(os.environ.get("SCRATCH_REAP_PRESSURE_GB", PRESSURE_GB))
    cool = float(os.environ.get("SCRATCH_REAP_COOLDOWN_MIN", COOLDOWN_MIN)) * 60
    free = free_gb()
    if free >= line:
        print(f"pressure: {free} GB free, line {line}: nothing to do")
        return 0
    try:
        last = json.loads((sd / "last_run.json").read_text()).get("end_epoch", 0)
    except (OSError, ValueError, AttributeError):
        last = 0
    rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "free_gb": free, "line_gb": line}
    if time.time() - last < cool:
        print(f"pressure: {free} GB free, but a run ended within {cool / 60:.0f} min")
        return 0
    unit = os.environ.get("SCRATCH_REAP_UNIT", "rm-scratch-reap.service")
    r = subprocess.run(["systemctl", "--user", "start", "--no-block", unit], capture_output=True, text=True, timeout=30)
    rec.update(started=r.returncode == 0, unit=unit, err=r.stderr.strip()[:200])
    with open(sd / "pressure.jsonl", "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(json.dumps(rec))
    return r.returncode


def report(rows: list[dict], a, sd: Path, freed: int):
    order = {"DELETED": 0, "DELETE": 1, "ARCHIVE": 2, "REFUSE": 3, "YOUNG": 4}
    for r in sorted(rows, key=lambda r: (order[r["verdict"]], r["path"])):
        print(f"{r['verdict']:7} {r['kind']:7} {human(r['bytes']):>9} {str(r['age_h']):>7}h  {r['path']}")
        for w in r["why"][:4]:
            print(f"          - {w}")
        if len(r["why"]) > 4:
            print(f"          - … {len(r['why']) - 4} more")
    tot = {v: sum(1 for r in rows if r["verdict"] == v) for v in order}
    take = freed if a.apply else sum(r["bytes"] or 0 for r in rows if r["verdict"] in ("DELETE", "ARCHIVE"))
    print(f"\n{len(rows)} candidate(s): " + ", ".join(f"{v} {n}" for v, n in tot.items() if n)
          + f"; {'freed' if a.apply else 'would free'} {human(take)}"
          + ("" if a.apply else "  (dry run — --apply acts on DELETE and ARCHIVE rows)"))
    print(f"alarms: {sd / 'alarms.log'}")


def run(a, sd: Path) -> int:
    start = time.time()
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(start))
    before = free_gb()
    if a.apply:
        sanity_start(sd, start)
    ctx = Ctx(start)
    fixtures = sweep_fixtures(ctx, a.apply, start + a.max_seconds / 2 if a.max_seconds else 0)
    rows = judge_all(ctx)
    failures: list[str] = []
    freed, deferred = 0, 0
    if a.apply:
        freed, deferred = apply_rows(rows, ctx, a.max_seconds, failures, start)
    rotate(sd / "runs.jsonl")
    with open(sd / "runs.jsonl", "a") as f:
        f.write(json.dumps({"ts": stamp, "apply": a.apply, "rows": rows}) + "\n")
    new_alarms(rows, sd, stamp, a.apply)
    done = [r for r in rows if r["verdict"] == "DELETED"]
    if done:
        root = archive_root()
        dest = root / time.strftime("%Y-%m-%d") / "scratch_expiry"
        dest.mkdir(parents=True, exist_ok=True)
        m = dest / f"run-{stamp.replace(':', '')}.manifest.json"
        m.write_text(json.dumps([{k: r.get(k) for k in ("kind", "path", "bytes", "age_h", "archive", "why")}
                                 for r in done], indent=1))
        acts_append(root, {"ts": local_ts(), "kind": "scratch-expiry-run", "path": f"{len(done)} scratch path(s)",
                           "size": freed, "archive": str(dest), "manifest": str(m),
                           "verify": "every path re-judged immediately before rmtree",
                           "evidence": str(sd / "runs.jsonl")})
    counts = {}
    for r in rows:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    end = time.time()
    rec = {"ts": stamp, "end_epoch": end, "seconds": round(end - start), "apply": a.apply, "ok": not failures,
           "failures": failures[:10], "counts": counts, "fixtures": fixtures, "freed_bytes": freed, "deferred": deferred,
           "archived": sum(1 for r in done if r.get("archive")), "root_free_gb_before": before,
           "root_free_gb_after": free_gb(), "global_holds": ctx.global_holds(),
           "blind_dirs": len(ctx.borrows.blind), "other_uid_procs": ctx.live.other_uid,
           "refused_bytes": sum(r["bytes"] or 0 for r in rows if r["verdict"] == "REFUSE")}
    if a.apply:
        sanity_end(sd, end, rows, rec)
        record(sd, rec)
    else:
        write_json(sd / "last_dry_run.json", rec)
    if a.json:
        print(json.dumps(rows, indent=1))
    else:
        report(rows, a, sd, freed)
        print(f"selftest fixtures: {fixtures}")
    return 1 if failures else 0


def main(argv=None) -> int:
    global _CORPUS, _VOCAB, _MIRROR_TIPS, _CANON
    _CORPUS = _VOCAB = _MIRROR_TIPS = _CANON = None
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--apply", action="store_true", help="act on the DELETE and ARCHIVE rows (default: report only)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--sanity", action="store_true", help="print the sanity reading and its problems; touches nothing")
    ap.add_argument("--max-seconds", type=float, default=0, help="stop starting deletions after this long (0 = no limit)")
    ap.add_argument("--pressure-check", action="store_true", help="start the reaper's unit if the root disk is low")
    a = ap.parse_args(argv)
    if a.pressure_check:
        return pressure_check()
    sd = state_dir()
    sd.mkdir(parents=True, exist_ok=True)
    if a.sanity:
        m = measure(time.time(), None, last_record(sd))
        print(json.dumps({"measures": m, "problems": judge_sanity("start", m)}, indent=1))
        return 0
    with open(sd / "run.lock", "w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            print("another reaper run holds the lock")
            return 0
        try:
            return run(a, sd)
        except Exception as e:      # the record must say so; re-raised, so the unit fails and signal_watch sees it
            if a.apply:
                sanity_write(sd, "end", {}, [f"the run died: {type(e).__name__}: {str(e)[:200]}"])
                record(sd, {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "end_epoch": time.time(),
                            "apply": True, "ok": False, "failures": [f"{type(e).__name__}: {e}"]})
            raise


if __name__ == "__main__":
    sys.exit(main())
