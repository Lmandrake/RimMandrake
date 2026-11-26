"""run_store.py -- the run store (Store: items, journal, locks under /home/mandrake/rm/runs/store), the clone effects detached helpers use (Effects: bundle_clone, remove_clone, restore_bundle), rules() and pilot_tier.

Moved verbatim from rimflow/relentless.py (RIMMANDRAKE_SPLIT_LIVE_CODE_OUT_OF_RELENTLESS_NAMED_MODULES):
only the functions live code reaches (design/RimMandrake/retired_eras_index_2026-11-18.md).
"""
import contextlib
import fcntl
import filecmp
import json
import os
import re
import select
import shutil
import stat
import subprocess
import sys
import time
try:                                    # whole text, never a silent cut (RIMMANDRAKE_STORE_TEXT_WHOLE_NO_CUTS)
    from . import fulltext
except ImportError:
    import fulltext  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import clone_park  # noqa: E402
import clone_integrity  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RULES = os.path.join(HERE, "run_rules.json")
DEFAULT_ROOT = "/home/mandrake/rm/runs"
RESTORE_EMAIL = "relentless@localhost"     # the committer of every commit restore_commits carries back into a clone
GAME = "game"           # relentless_game.GAME: the store status of an item in its game phase
NOT_READ = object()
# dirt no worker made on purpose: session dumps and ledger shards the seats' projection rewrites. Bundled, never restored
POOL_STATE = ("infrastructure/state/lessons/",)     # records a worker commits as it finishes; the bundle carries them, a fresh clone re-applies them
POOL_NOISE = ("conversations/", "infrastructure/state/ledger/events/", "infrastructure/state/code_review/")
POOL_IGNORED_MAX = 2 * 10**9
# RELENTLESS_BUNDLES_FIX_FOURTEEN_GIG_PATCHES: a bundle holds a worker's WIP, never a tree. Over these it raises (the clone
# is kept and alarmed, bundle_failed) instead of writing 14 GB, as three bundles did on 2026-11-04/05.
BUNDLE_PATCH_MAX = 500 * 10**6
BUNDLE_MAX = POOL_IGNORED_MAX + 2 * BUNDLE_PATCH_MAX


def _worktree_blob(c, p):
    """-> the blob id git would store for `p` in clone `c`. A symlink's blob is its link text: `hash-object <path>` reads
    the target's bytes, so an unchanged tracked symlink never matched and its deletion was refused (Codex r6 #2)."""
    full = os.path.join(c, p)
    if os.path.islink(full):
        r = subprocess.run(["git", "-C", c, "hash-object", "--stdin"], input=os.fsencode(os.readlink(full)),
                           capture_output=True, timeout=120)
        return r.stdout.decode().strip() if r.returncode == 0 else None
    r = subprocess.run(["git", "-C", c, "hash-object", "--", p], capture_output=True, text=True, timeout=120,
                       stdin=subprocess.DEVNULL)
    return r.stdout.strip() if r.returncode == 0 else None


def restore_deleted(bundle, c):
    """A bundle's `deleted` paths go from the fresh clone `c`, each only while upstream still holds the very blob the worker
    removed (and the file is that blob). -> what was not removed, named."""
    path = os.path.join(bundle, "deleted")
    if not os.path.exists(path):
        return []

    def out(*a):
        return subprocess.run(["git", "-C", c, *a], capture_output=True, text=True, timeout=120,
                              stdin=subprocess.DEVNULL).stdout.strip()
    with open(os.path.join(bundle, "HEAD"), encoding="utf-8") as f:
        head = f.read().strip()
    with open(path, encoding="utf-8") as f:
        names = [x for x in f.read().split("\0") if x]
    bad = []
    for p in names:
        if not os.path.lexists(os.path.join(c, p)):
            continue
        was, now = (out("rev-parse", "--verify", "-q", "%s:%s" % (rev, p)) for rev in (head, "HEAD"))
        if was and was == now and _worktree_blob(c, p) == now:
            os.unlink(os.path.join(c, p))
        else:
            bad.append("deleted %s kept: upstream changed it since" % p)
    return bad


def tree_bytes(p):
    """-> bytes at `p` (a file, a symlink's own size, or a folder walked without following links); 0 when gone."""
    try:
        st = os.lstat(p)
    except OSError:
        return 0
    if not stat.S_ISDIR(st.st_mode):
        return st.st_size
    n = 0
    for dp, _dirs, files in os.walk(p):
        for x in files:
            try:
                n += os.lstat(os.path.join(dp, x)).st_size
            except OSError:
                pass
    return n


def capped_copy(argv, f, cap, name, timeout=300):
    """Run `argv`, its stdout copied into `f`, killed the moment it passes `cap` bytes: a runaway diff never fills the
    disk before the size is checked (Codex r6 #10). Raises on a nonzero exit, the cap or the timeout, which a silent child
    meets too: no read blocks past it (a stalled child held the whole tick, Codex r7)."""
    p = subprocess.Popen(argv, stdout=subprocess.PIPE, stdin=subprocess.DEVNULL)
    n, end = 0, time.monotonic() + timeout
    try:
        fd = p.stdout.fileno()
        while True:
            if not select.select([fd], [], [], max(0, end - time.monotonic()))[0]:
                raise subprocess.TimeoutExpired(argv, timeout)
            chunk = os.read(fd, 1 << 20)
            if not chunk:
                break
            n += len(chunk)
            if n > cap:
                raise RuntimeError("%s passed %d bytes, over the bundle cap %d: read this clone before it goes"
                                   % (name, n, cap))
            if time.monotonic() > end:
                raise subprocess.TimeoutExpired(argv, timeout)
            f.write(chunk)
        rc = p.wait(timeout=max(1, end - time.monotonic()))
        if rc:
            raise subprocess.CalledProcessError(rc, argv)
    finally:
        if p.poll() is None:
            p.kill()
            p.wait()
        p.stdout.close()


def bundle_bytes(d):
    """-> bytes under d, each inode once (real.patch is a hard link to diff.patch)."""
    seen, n = set(), 0
    for dp, _dirs, files in os.walk(d):
        for x in files:
            st = os.lstat(os.path.join(dp, x))
            if (st.st_dev, st.st_ino) not in seen:
                seen.add((st.st_dev, st.st_ino))
                n += st.st_size
    return n


def pilot_tier(clone, agent, default):
    """-> the model tier a Test Pilot sitting runs on. Owner 2026-11-16 10:13 PM: "Test Pilot should also run as Fable
    5.2 when it's called." The tier is the agent file's own `model:` line (.claude/agents/<agent>.md in `clone`, else
    this repo's), so the file stays the one place it is set; `--model` beats that line, so it must be passed. The
    launch turns the tier into its id (role_launch.launch_model: the bare CLI alias "fable" resolved to Fable 5.1,
    measured 2026-11-12 and 2026-11-16). No agent file or no line: `default`."""
    for base in (clone, os.path.dirname(os.path.dirname(os.path.dirname(HERE)))):
        try:
            with open(os.path.join(base or "", ".claude", "agents", "%s.md" % agent), encoding="utf-8") as f:
                head = f.read().split("\n---", 1)[0]
        except (OSError, TypeError):
            continue
        return next((ln.split(":", 1)[1].strip() for ln in head.splitlines() if ln.startswith("model:")), None) or default
    return default


def root():
    return os.environ.get("RM_RUNS_ROOT") or DEFAULT_ROOT


def rules(path=None):
    with open(path or os.environ.get("RM_RUNS_RULES") or RULES, encoding="utf-8") as f:
        r = json.load(f)
    if r.get("runner", "claude") not in ("claude", "codex"):
        raise ValueError("runner must be claude or codex")
    return r


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


# Moved verbatim from relentless_game.py: owner_queue.py reads a store item's game hold through it.
FLYER = "flyer:"


def flyer_hold(why):
    """This game hold's words say a flyer's flight, the one game hold only he can lift. Anchored where _hold writes the
    reason: the rest of a why is free text (proof paths, mod names, file names), and "flyer" in it says nothing."""
    return (why or "").startswith("game phase: " + FLYER)


# Copied from relentless_wake.py (which keeps its own until it is deleted with the wake poke): modledger_backfill.py reads it.
def store_dir(root=None):
    return os.path.join(root or os.environ.get("RM_RUNS_ROOT") or DEFAULT_ROOT, "store")


class Store:
    on_alarm = None     # the real Fx sets it: an alarm on the journal is a signal on the told ledger

    def __init__(self, base=None):
        self.root = base or root()
        self.dir = os.path.join(self.root, "store")
        os.makedirs(os.path.join(self.dir, "items"), exist_ok=True)

    def p(self, *a):
        return os.path.join(self.dir, *a)

    def item_dir(self, item):
        return self.p("items", item)

    @contextlib.contextmanager
    def lock(self):
        """Every transition holds this. Never held across a blocking effect (a stop, a launch, a publish)."""
        fd = os.open(self.p(".lock"), os.O_CREAT | os.O_RDWR, 0o644)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
            yield
        finally:
            os.close(fd)

    def _write(self, path, text):
        tmp = "%s.tmp.%d" % (path, os.getpid())
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        d = os.open(os.path.dirname(path), os.O_RDONLY)
        try:
            os.fsync(d)
        finally:
            os.close(d)

    def _append(self, path, line):
        with open(path, "a+b") as f:
            f.seek(0, os.SEEK_END)
            head = b""
            if f.tell():            # a torn last line (no newline) would glue this record onto it and lose both
                f.seek(-1, os.SEEK_END)
                head = b"" if f.read(1) == b"\n" else b"\n"
            f.write(head + (line.rstrip("\n") + "\n").encode("utf-8"))
            f.flush()
            os.fsync(f.fileno())

    def load(self, item):
        try:
            with open(os.path.join(self.item_dir(item), "state.json"), encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def save(self, st):
        os.makedirs(os.path.join(self.item_dir(st["item"]), "receipts"), exist_ok=True)
        self._write(os.path.join(self.item_dir(st["item"]), "state.json"), json.dumps(st, indent=1, sort_keys=True))

    def items(self):
        return sorted(os.listdir(self.p("items")))

    def states(self):
        return [s for s in (self.load(i) for i in self.items()) if s]

    def journal(self, rec):
        self._append(self.p("journal.jsonl"), json.dumps(rec, sort_keys=True))
        if self.on_alarm and rec.get("do") == "alarm":
            self.on_alarm(rec)


    def learn(self, item, text):
        self._append(os.path.join(self.item_dir(item), "learned.md"), text)


def new_state(item, now, why):
    return {"item": item, "status": "queued", "gen": 0, "enrolled_at": now, "why": why, "returned_at": None,
            "returns": 0, "failures": {}, "total_failures": 0, "approach": "build", "approach_changes": 0,
            "spent": 0, "attempts": 0, "unit": None, "scope": None, "clone": None, "started_at": None,
            "last_beat": None, "stopping_since": None, "contract": None, "candidate": None, "check": None,
            "hold": None, "last_fail": None, "last_sha": None, "sha_at_change": None, "run": None,
            "not_before": 0, "ledger_started": False, "start_intent": False, "done_at": None, "quarantined": []}


class Effects(object):
    """The real one. Every method here blocks, so none is called under the store lock."""

    def __init__(self, r, store):
        self.r = r
        self.store = store
        self.owner_pause_rule = owner_pause_rule()     # his pipeline-only switch, read once a tick (owner_pause)
        self.base = store.root
        self.books = os.path.join(self.base, "books")
        self._ledger = None
        self._budget = self._helpers = NOT_READ
        self.bounce = set()
        self.marked = set()


    def git(self, cwd, *args, timeout=120):
        return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=timeout,
                              stdin=subprocess.DEVNULL)


    # the showing stage (relentless_showing): an item waiting only on his look is staged before he is asked
    show_root = None        # relentless_showing.SHOW_DIR


    def git_ok(self, cwd, *args):
        r = self.git(cwd, *args, timeout=300)
        if r.returncode:
            raise RuntimeError("git %s: %s" % (args[0], r.stderr))
        return r.stdout

    def changed_paths(self, c):
        out = self.git_ok(c, "--no-optional-locks", "status", "--porcelain", "--untracked-files=normal", "--no-renames", "-z")
        return [x[3:] for x in out.split("\0") if x]

    def ignored_paths(self, c):
        """Ignored files are nobody else's copy either. Bytecode is the one thing that is only ever derived."""
        out = self.git_ok(c, "ls-files", "-z", "--others", "--ignored", "--exclude-standard").split("\0")
        return [p for p in out if p and "__pycache__/" not in p and not p.endswith(".pyc")]

    def keep_gitless(self, item, c):
        """A clone folder with no .git has nothing to bundle from, and its untracked files are the only copy: moved whole
        beside the item's bundles (a rename, same disk). -> (where it went, None); (None, None) when it held no file;
        (None, why) when it could not move, and the caller then keeps it."""
        def unreadable(e):      # os.walk swallows a listing error by default: an unread folder is not empty (r5 #17)
            raise e
        try:
            empty = not any(files or any(os.path.islink(os.path.join(dp, x)) for x in dirs)    # a symlinked dir
                            for dp, dirs, files in os.walk(c, onerror=unreadable))  # is a thing to keep too (a dir to os.walk)
        except OSError as e:
            return None, "its tree could not be read: %s" % str(e)
        if empty:
            return None, None
        home = self.store.p("items", item) if item and os.path.isdir(self.store.p("items", item)) else self.store.p("orphans")
        stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        out, n = os.path.join(home, "gitless", "%s-%s" % (stamp, os.path.basename(c))), 1
        while os.path.lexists(out):
            out, n = os.path.join(home, "gitless", "%s-%s-%d" % (stamp, os.path.basename(c), n)), n + 1
        try:
            os.makedirs(os.path.dirname(out), exist_ok=True)
            os.rename(c, out)
        except OSError as e:
            return None, "its git-less tree could not be kept aside: %s" % str(e)
        return out, None

    def bundle_clone(self, item, c):
        """Everything no remote has, on the store's disk, before a clone goes. -> the bundle dir, None when there is
        nothing. Raises when it cannot be sure: the caller then keeps the clone, and no half-written bundle stays.
        RELENTLESS_BUNDLES_FIX_FOURTEEN_GIG_PATCHES (2026-11-04): a scratch clone whose fetch failed after its `clone
        --no-checkout` had a .git, no index and no tree; every tracked file read as deleted, and three --binary patches each
        carried the whole 3.9 GB tree as preimage (14 GB a bundle, three bundles). So: no index means never checked out
        (missing files are not deletions); a deletion is a path in `deleted`, never a preimage (git apply refuses an
        --irreversible-delete patch); index.patch is kept only when it differs from diff.patch; and a bundle over
        BUNDLE_PATCH_MAX / BUNDLE_MAX raises instead of filling the disk."""
        unchecked = not os.path.exists(os.path.join(c, ".git", "index"))
        if unchecked:       # read-tree without -u writes only the index: present files then read as clean or changed
            self.git_ok(c, "read-tree", "HEAD")
        paths = self.changed_paths(c)
        commits = self.git_ok(c, "rev-list", "HEAD", "--branches", "--tags", "--not", "--remotes").strip()
        stash = self.git_ok(c, "stash", "list", "--format=%H").split()
        ignored = self.ignored_paths(c)
        deleted = [] if unchecked else [p for p in self.git_ok(c, "diff", "--name-only", "-z", "--no-renames",
                                                                     "--diff-filter=D", "HEAD").split("\0") if p]
        if unchecked:       # a file never checked out is not one a worker removed
            gone = set(p for p in self.git_ok(c, "diff", "--name-only", "-z", "--no-renames", "--diff-filter=D",
                                                "HEAD").split("\0") if p)
            paths = [p for p in paths if p not in gone]
        if not paths and not commits and not stash and not ignored:
            return None
        if sum(os.lstat(os.path.join(c, p)).st_size for p in ignored) > POOL_IGNORED_MAX:
            raise RuntimeError("ignored files over %d bytes: read them before this clone goes" % POOL_IGNORED_MAX)
        home = self.store.p("items", item) if os.path.isdir(self.store.p("items", item)) else self.store.p("orphans")
        stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        out, n = os.path.join(home, "bundles", "%s-%s" % (stamp, os.path.basename(c))), 1
        while os.path.exists(out):      # named by the second: never let an earlier bundle's files answer for this one
            out, n = os.path.join(home, "bundles", "%s-%s-%d" % (stamp, os.path.basename(c), n)), n + 1
        os.makedirs(out)
        try:
            self._bundle_write(c, out, paths, deleted, ignored, commits, stash)
        except BaseException:
            shutil.rmtree(out, ignore_errors=True)
            raise
        return out

    def _bundle_write(self, c, out, paths, deleted, ignored, commits, stash):
        real = [p for p in paths if not p.startswith(POOL_NOISE)]
        untracked = self.git_ok(c, "ls-files", "-z", "--others", "--exclude-standard").split("\0")
        untracked = [p for p in untracked if p]
        diff = ["git", "-C", c, "diff", "--binary", "--no-textconv", "--no-ext-diff", "--no-renames", "--diff-filter=d"]

        def write(name, argv, cap=BUNDLE_PATCH_MAX):
            path = os.path.join(out, name)
            with open(path, "wb") as f:
                if argv:
                    capped_copy(argv, f, cap, name)
            if os.path.getsize(path) > cap:
                raise RuntimeError("%s is %d bytes, over the bundle cap %d: read this clone before it goes"
                                   % (name, os.path.getsize(path), cap))
            return path
        with open(os.path.join(out, "HEAD"), "w", encoding="utf-8") as f:
            f.write(self.git_ok(c, "rev-parse", "HEAD"))
        whole = write("diff.patch", diff + ["HEAD"])
        index = write("index.patch", diff + ["--cached", "HEAD"])   # staged content the working file no longer shows
        if filecmp.cmp(index, whole, shallow=False):
            os.unlink(index)    # a second copy of diff.patch says nothing restore_bundle does not already know
        noisy = any(p.startswith(POOL_NOISE) for p in paths)
        if real and not noisy:
            os.link(whole, os.path.join(out, "real.patch"))     # the same bytes: one copy on disk
        else:   # noise excluded by prefix, never the paths listed: thousands of them overflow argv (E2BIG)
            write("real.patch", diff + ["HEAD", "--", ":(top)"] + [":(top,exclude)" + p for p in POOL_NOISE] if real else None)
        real_deleted = [p for p in deleted if not p.startswith(POOL_NOISE)]
        if real_deleted:        # a deletion's content is HEAD's: the path is all restore_bundle needs
            with open(os.path.join(out, "deleted"), "w", encoding="utf-8") as f:
                f.write("\0".join(real_deleted))
        for name, want in (("untracked.tar", untracked), ("ignored.tar", ignored),
                           ("real_untracked.tar", [p for p in untracked if not p.startswith(POOL_NOISE)])):
            if want:    # sized before tar writes a byte: the cap is a limit, never a post-mortem (Codex r6 #10)
                est = bundle_bytes(out) + sum(tree_bytes(os.path.join(c, p)) for p in want)
                if est > BUNDLE_MAX:
                    raise RuntimeError("%s would be %d bytes, over the bundle cap %d: read this clone before it goes"
                                       % (name, est, BUNDLE_MAX))
                subprocess.run(["tar", "-C", c, "--null", "-T", "-", "-cf", os.path.join(out, name)],
                               input="\0".join(want).encode(), check=True, timeout=300)
        for i, sha in enumerate(stash):   # refs/stash names only the newest; the rest live in a reflog no bundle carries
            self.git_ok(c, "update-ref", "refs/rm-stash/%d" % i, sha)
        if commits or stash:
            open(os.path.join(out, "carry"), "w").close()
            r = self.git(c, "bundle", "create", os.path.join(out, "commits.bundle"), "HEAD", "--all", "--not", "--remotes")
            if r.returncode:
                raise RuntimeError("git bundle: %s" % r.stderr)
        size = bundle_bytes(out)
        if size > BUNDLE_MAX:
            raise RuntimeError("bundle is %d bytes, over the cap %d: read this clone before it goes" % (size, BUNDLE_MAX))

    def restore_bundle(self, item, bundle, c):
        """A fresh clone takes the WIP of the one evicted. What will not apply stays in the bundle and the record says so."""
        bad = []
        cb = os.path.join(bundle, "commits.bundle")
        if os.path.exists(os.path.join(bundle, "carry")) and os.path.exists(cb):     # carried commits come back as commits
            bad.extend(self.restore_commits(item, bundle, cb, c))
            if bad:
                self.store.journal({"at": iso(time.time()), "do": "alarm", "kind": "restore_incomplete", "item": item,
                                    "bundle": bundle, "why": "; ".join(bad)})
        patch = os.path.join(bundle, "real.patch")
        if os.path.exists(patch) and os.path.getsize(patch):
            r = self.git(c, "apply", "--3way", "--whitespace=nowarn", patch, timeout=300)
            if r.returncode:
                bad.append("patch: %s" % r.stderr)
        bad.extend(restore_deleted(bundle, c))
        index, whole = (os.path.join(bundle, x) for x in ("index.patch", "diff.patch"))
        if os.path.exists(index) and os.path.getsize(index):
            with open(index, "rb") as a, open(whole, "rb") as b:
                if a.read() != b.read():
                    bad.append("the index held content the working tree did not: see index.patch")
        for name in ("real_untracked.tar", "ignored.tar"):
            tar = os.path.join(bundle, name)
            if not os.path.exists(tar):
                continue
            listed = subprocess.run(["tar", "-tf", tar], capture_output=True, text=True, timeout=300)
            clash = [p for p in listed.stdout.splitlines()     # any non-directory member whose path is already taken
                     if not p.endswith("/") and os.path.lexists(os.path.join(c, p.rstrip("/")))]
            if clash:   # upstream has since tracked the name (a file, a directory, a link): never overwritten, and said
                #   (a directory used to be skipped by --skip-old-files in silence; Codex, ..._TEN_MORE #5)
                bad.append("%s kept in the bundle, upstream has them: %s" % (name, ", ".join(clash[:5])))
            r = subprocess.run(["tar", "--skip-old-files", "-C", c, "-xf", tar], capture_output=True, text=True, timeout=300)
            if r.returncode:
                bad.append("%s: %s" % (name, r.stderr))
        if bad:
            self.store.learn(item, "\n%s relentless: your clone was evicted from a full pool and its WIP did not all "
                             "come back; it is in %s (%s)\n" % (iso(time.time()), bundle, "; ".join(bad)))
        return bad

    def restore_commits(self, item, bundle, cb, c):
        """Every commit and stash in the bundle comes back or is named. -> what did not. HEAD's line by cherry-pick along its
        first parents (a merge as one commit, -m 1, so a resolution made in the merge is kept); a branch or tag HEAD does not
        reach as that ref; each stash onto the stash list, oldest first so the order holds."""
        listed = self.git(c, "bundle", "list-heads", cb, timeout=300)
        heads = [ln.split(None, 1) for ln in listed.stdout.splitlines() if " " in ln]
        if listed.returncode or not heads:
            return ["commits.bundle: %s" % (listed.stderr or "no refs in it")]
        temp = ["refs/rm-carried/%d" % i for i in range(len(heads))]
        r = self.git(c, "fetch", "-q", "--no-tags", cb, *("+%s:%s" % (h[1], t) for h, t in zip(heads, temp)), timeout=300)
        if r.returncode:
            return ["commits.bundle: %s" % r.stderr]
        bad, picked, landed, side, stashes = [], 0, 0, [], []
        tip = next((sha for sha, ref in heads if ref == "HEAD"), None)
        shas = self.git(c, "rev-list", "--reverse", "--first-parent", tip, "--not", "--remotes", timeout=300).stdout.split() if tip else []
        for sha in shas:
            merge = len(self.git(c, "rev-list", "--parents", "-n1", sha, timeout=60).stdout.split()) > 2
            r = self.git(c, "-c", "user.name=relentless", "-c", "user.email=" + RESTORE_EMAIL, "cherry-pick", "--allow-empty",
                         *(("-m", "1") if merge else ()), sha, timeout=300)
            if not r.returncode:
                picked += 1
                continue
            started = self.git(c, "rev-parse", "-q", "--verify", "CHERRY_PICK_HEAD", timeout=60).returncode == 0
            if started and self.git(c, "diff", "--quiet", "HEAD", timeout=60).returncode == 0 \
                    and not self.git(c, "ls-files", "-u", timeout=60).stdout.strip():   # origin already holds it; an
                # unmerged path (a modify/delete conflict leaves the tree as HEAD) is no landing (Codex r5 part3 #3)
                self.git(c, "cherry-pick", "--skip", timeout=60)
                landed += 1
                continue
            self.git(c, "cherry-pick", "--abort", timeout=60)
            bad.append("commit %s did not re-apply: %s" % (sha[:10], r.stderr))
            break
        for sha, ref in heads:
            if not ref.startswith(("refs/heads/", "refs/tags/")):
                continue
            if tip and self.git(c, "merge-base", "--is-ancestor", sha, tip, timeout=60).returncode == 0:
                continue        # on HEAD's line: it came back above
            area, name = ("refs/heads/", ref[11:]) if ref.startswith("refs/heads/") else ("refs/tags/", ref[10:])
            want, n = ref, 1        # a name already taken (by the clone or an earlier restore) gets a fresh one: never
            while self.git(c, "rev-parse", "-q", "--verify", want, timeout=60).returncode == 0:    # overwritten
                want = "%scarried/%s" % (area, name) if n == 1 else "%scarried/%s-%d" % (area, name, n)
                n += 1      # (Codex, ..._TEN_MORE #4)
            r = self.git(c, "update-ref", want, sha, "0" * 40, timeout=60)     # old value zero: refuses if it now exists
            if r.returncode:
                bad.append("%s did not come back: %s" % (ref, r.stderr))
            else:
                side.append(want)
        for sha, ref in sorted((h for h in heads if h[1].startswith("refs/rm-stash/")), key=lambda h: -int(h[1].rsplit("/", 1)[1])):
            subject = self.git(c, "log", "-1", "--format=%s", sha, timeout=60).stdout.strip()
            r = self.git(c, "-c", "user.name=relentless", "-c", "user.email=relentless@localhost", "stash", "store", "-m", subject, sha, timeout=60)
            if r.returncode:
                bad.append("stash %s did not come back: %s" % (sha[:10], r.stderr))
            else:
                stashes.append(sha)
        for t in temp:
            self.git(c, "update-ref", "-d", t, timeout=60)
        said = []
        if picked:
            said.append("%d unlanded commit(s) came back by cherry-pick: land them or drop them" % picked)
        if landed:
            said.append("%d already on origin, skipped" % landed)
        if side:
            said.append("off HEAD's line, unlanded: %s" % ", ".join(side))
        if stashes:
            said.append("%d stash(es) back on git stash list" % len(stashes))
        if said:
            self.store.learn(item, "\n%s relentless: your clone went back while the item was put down; %s (bundle: %s)\n" % (
                iso(time.time()), "; ".join(said), bundle))
        return bad

    def remove_clone(self, st, before=None):
        """Nothing leaves the pool unbundled. -> the bundle dir or None; a bundle that fails keeps the clone."""
        c = st.get("clone")
        if not c:
            return None
        # Real paths on both sides (RIMMANDRAKE_RETURN_CLONE_UNDER_OLD_POOL_NAME_KEPT_SILENT): a record that names the pool
        # through a symlink (the old /home/mandrake/rm/relentless) is still a pool clone. A refusal is never silent.
        real = os.path.realpath(c)
        if not real.startswith(os.path.join(os.path.realpath(self.base), "clones") + os.sep):
            self.store.journal({"at": iso(time.time()), "do": "alarm", "kind": "clone_outside_pool", "clone": c,
                                "why": "not under %s: the clone is neither bundled nor removed" % os.path.join(self.base, "clones")})
            return None
        c = real
        out = None
        if os.path.exists(os.path.join(c, ".git")):
            try:
                out = self.bundle_clone(st.get("item") or clone_item(c), c)
            except (RuntimeError, OSError, ValueError, subprocess.SubprocessError) as e:
                self.store.journal({"at": iso(time.time()), "do": "alarm", "kind": "bundle_failed", "clone": c, "why": str(e)})
                return None
        elif os.path.isdir(c):  # no git to bundle from: its files are moved aside whole, never deleted (Codex #3)
            kept, why = self.keep_gitless(st.get("item") or clone_item(c), c)
            if why:
                self.store.journal({"at": iso(time.time()), "do": "alarm", "kind": "bundle_failed", "clone": c, "why": why})
                return None
            if kept:
                self.store.journal({"at": iso(time.time()), "do": "clone_kept_gitless", "clone": os.path.basename(c),
                                    "kept": kept})
        if before and out:
            before(out)         # the record learns of the bundle while the clone still stands
        warm = clone_park.park(c, os.path.join(self.base, "clones"), self.r.get("warm_clones", 0),
                                    clone_integrity.clone_damage) if os.path.isdir(os.path.join(c, ".git")) else None
        if warm:                # reused by the next clone instead of a fresh 3.6 GB checkout (DISK_CHURN_MEASURE_CLONES_EAT_THE_VHDX)
            self.store.journal({"at": iso(time.time()), "do": "clone_parked", "clone": os.path.basename(c),
                                "warm": os.path.basename(warm), "bundle": out})
            return out
        why = clone_park.remove_tree(c)
        if why:                 # still present, so still counted; the bundle stands. A clone already gone is removed.
            self.store.journal({"at": iso(time.time()), "do": "alarm", "kind": "remove_failed", "clone": c, "why": why})
        return out


def clone_item(c):
    """The item a pool clone's folder is named for: ITEM, ITEM.qN, check-ITEM-cN or help-ITEM-cN."""
    name = os.path.basename(c.rstrip("/"))
    for pre in ("check-", "help-"):
        if name.startswith(pre):
            return name[len(pre):].rsplit("-c", 1)[0]
    return re.sub(r"\.q\d+$", "", name)
OWNER_PAUSE = os.path.join(HERE, "owner_pause.json")


def owner_pause_rule(path=None):
    """The owner's pipeline-only switch as data (owner_pause.json), read once per tick by the real Effects
    (fx.owner_pause_rule; a test's Fx has none, so it reads off). No file: off. A file that cannot be read: on, said in
    its why, since his pause is the side that cannot start work against his word."""
    try:
        with open(path or OWNER_PAUSE, encoding="utf-8") as f:
            rule = json.load(f)
        if not isinstance(rule, dict):      # a hand-written `true` raised in every tick; `null` read as off
            raise ValueError("not a JSON object: %r" % (rule,))
        return rule
    except FileNotFoundError:
        return None
    except (OSError, ValueError) as e:
        return {"pipeline_only": True, "pipeline_prefixes": ["LIGHTSPEED_"], "unreadable": "%s: %s" % (type(e).__name__, e)}
