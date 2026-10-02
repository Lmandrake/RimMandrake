#!/usr/bin/env python3
"""Subagent worktree pool — Claude Code WorktreeCreate/WorktreeRemove hook (plan §2.2, Phase 7).

    worktree_pool.py create         hook: stdin JSON {cwd, name, session_id, transcript_path, ...}
                                    -> stdout line 1 = slot path; exit 1 + stderr when the pool is full
    worktree_pool.py remove         hook: releases a clean, landed slot; never deletes anything
    worktree_pool.py status [--json]
    worktree_pool.py rescue-list [--json]
    worktree_pool.py submit         run INSIDE a slot: rebase on origin/main, push submit/<seat>/<name>

Layout: seat clones `/home/mandrake/rm/<seat>`; pool `/home/mandrake/rm/pool/<seat>/slot{0..N-1}`,
each a linked worktree of its seat's clone (so refs are shared with the seat). Env overrides, used
by the selftest: RM_SEAT_ROOT, RM_POOL_ROOT, RM_POOL_SLOTS (default 2), RM_POOL_OWNER_PID, AGENT_SEAT.

Ownership is the CONTENT of `slotN.lock` (the hook exits, so a flock cannot carry it):
{pid, pid_start, session_id, transcript_path, name, generation, base_sha, started}. A slot is busy
while that pid is alive with the same start time (defeats PID reuse) OR any process has its cwd
or an open fd under the slot. `alloc.mutex` is flocked only during allocation.

A dead slot is recycled only if clean AND landed (HEAD reachable from origin/main, from its
submit ref, from refs/landed/<seat>/<name> written by land_submissions.py, or every commit
patch-equivalent upstream). Otherwise it is snapshotted to a LOCAL `refs/rescue/<seat>/<name>-<utc>`
(never pushed), the snapshot is verified against the working tree, a `rescue` event is appended
to `<pool>/rescues.jsonl` (rimflow has no `rescue` verb), and only then is the slot reset.
"""
import argparse
import datetime
import fcntl
import json
import os
import re
import subprocess
import sys
import time

SEAT_ROOT = os.path.realpath(os.environ.get("RM_SEAT_ROOT", "/home/mandrake/rm"))
POOL_ROOT = os.path.realpath(os.environ.get("RM_POOL_ROOT", os.path.join(SEAT_ROOT, "pool")))
SLOTS = int(os.environ.get("RM_POOL_SLOTS", "2"))
RESCUE_MAX_BYTES = 5 * 1024 * 1024
LIST_CAP = 200
SHELLS = {"sh", "bash", "zsh", "dash", "fish"}

# §2.4 generated artifacts (plus build outputs) — a rescue classifies these as `generated`.
GENERATED = [
    re.compile(r"^infrastructure/state/queue/(BENCH|FOUNDRY|HUMAN)\.md$"),
    re.compile(r"^Transient/codebase_health[^/]*$"),
    re.compile(r"^infrastructure/state/codebase_health_last\.json$"),
    re.compile(r"^infrastructure/dashboards/hub/data/[^/]*\.json$"),
    re.compile(r"^infrastructure/artpipe/(pending|active|done|failed)/"),
    re.compile(r"(^|/)(bin|obj)/"),
    re.compile(r"\.(dll|pdb|srchash)$"),
    re.compile(r"(^|/)__pycache__/"),
]
SECRET_NAME = re.compile(r"(\.pem$|\.key$|(^|/)id_[^/]*$|token|(^|/)\.env(\.|$)|credential|secret)", re.I)
SECRET_CONTENT = re.compile(rb"(-----BEGIN [A-Z ]*PRIVATE KEY-----|ghp_[A-Za-z0-9]{20,}|github_pat_|"
                            rb"AKIA[0-9A-Z]{16}|xox[baprs]-|sk-ant-|sk-[A-Za-z0-9]{32,})")
DOC_EXT = (".md", ".txt", ".rst", ".adoc")


class PoolError(Exception):
    pass


# ---------------------------------------------------------------- git / proc helpers
def git(cwd, *args, env=None, input=None, check=True):
    p = subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True,
                       errors="surrogateescape", env=env, input=input)
    if check and p.returncode != 0:
        raise PoolError("git %s failed in %s: %s" % (" ".join(args), cwd, p.stderr.strip()))
    return p.stdout if not check else p.stdout.rstrip("\n")


def git_ok(cwd, *args, env=None):
    return subprocess.run(["git", "-C", cwd, *args], capture_output=True, env=env).returncode == 0


def ref_exists(cwd, ref):
    return git_ok(cwd, "rev-parse", "-q", "--verify", ref + "^{commit}")


def is_ancestor(cwd, a, b):
    return git_ok(cwd, "merge-base", "--is-ancestor", a, b)


def proc_stat(pid):
    """(state, ppid, starttime) or None. Field 22 of /proc/<pid>/stat is starttime."""
    try:
        rest = open("/proc/%d/stat" % pid).read().rsplit(")", 1)[1].split()
        return rest[0], int(rest[1]), int(rest[19])
    except (OSError, ValueError, IndexError):
        return None


def proc_argv(pid):
    try:
        return open("/proc/%d/cmdline" % pid, "rb").read().decode("utf-8", "replace").split("\0")
    except OSError:
        return []


def proc_comm(pid):
    try:
        return open("/proc/%d/comm" % pid).read().strip()
    except OSError:
        return ""


def is_claude(pid):
    argv = proc_argv(pid)
    a0 = os.path.basename(argv[0]) if argv else ""
    if proc_comm(pid) == "claude" or a0 in ("claude", "claude.exe"):
        return True
    return a0 in ("node", "bun") and len(argv) > 1 and "claude" in os.path.basename(argv[1])


def owner_pid():
    """The `claude` ancestor. X1 trap: getppid() is a dying `sh -c`, so a slot looked free at once."""
    if os.environ.get("RM_POOL_OWNER_PID"):
        return int(os.environ["RM_POOL_OWNER_PID"])
    p = os.getppid()
    first_non_shell = None
    while p > 1:
        if is_claude(p):
            return p
        if first_non_shell is None and proc_comm(p) not in SHELLS:
            first_non_shell = p
        st = proc_stat(p)
        if not st:
            break
        p = st[1]
    return first_non_shell or os.getppid()


def alive_match(pid, start):
    st = proc_stat(int(pid or 0)) if pid else None
    return bool(st) and st[0] != "Z" and (start is None or st[2] == start)


def users_of(path):
    """pids (not ours) whose cwd or any open fd is at/under path."""
    me = os.getpid()
    pre = path.rstrip("/") + "/"
    hits = []
    for d in os.listdir("/proc"):
        if not d.isdigit() or int(d) == me:
            continue
        cands = []
        try:
            cands.append(os.readlink("/proc/%s/cwd" % d))
        except OSError:
            pass
        try:
            for fd in os.listdir("/proc/%s/fd" % d):
                try:
                    cands.append(os.readlink("/proc/%s/fd/%s" % (d, fd)))
                except OSError:
                    pass
        except OSError:
            pass
        if any(c == path or c.startswith(pre) for c in cands):
            hits.append(int(d))
    return hits


def mem_available_kib():
    try:
        for line in open("/proc/meminfo"):
            if line.startswith("MemAvailable:"):
                return int(line.split()[1])
    except OSError:
        pass
    return None


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc)


def append_jsonl(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(obj, sort_keys=True) + "\n")


def log(msg):
    try:
        os.makedirs(POOL_ROOT, exist_ok=True)
        with open(os.path.join(POOL_ROOT, "hook.log"), "a") as f:
            f.write("%s [%d] %s\n" % (utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"), os.getpid(), msg))
    except OSError:
        pass


def telemetry(seat, slot, outcome, wait_s, **kw):
    rec = {"ts": utcnow().isoformat(timespec="seconds"), "seat": seat, "slot": slot,
           "outcome": outcome, "wait_s": round(wait_s, 3), "MemAvailable_kib": mem_available_kib()}
    rec.update(kw)
    append_jsonl(os.path.join(POOL_ROOT, "telemetry.jsonl"), rec)


# ---------------------------------------------------------------- seat / slot model
def seat_from_cwd(cwd):
    if cwd:
        real = os.path.realpath(cwd)
        for root, offset in ((POOL_ROOT, 0), (SEAT_ROOT, 0)):
            rel = os.path.relpath(real, root)
            if rel.startswith("..") or rel == ".":
                continue
            seat = rel.split(os.sep)[offset]
            if root == SEAT_ROOT and seat == os.path.basename(POOL_ROOT):
                continue
            if os.path.isdir(os.path.join(SEAT_ROOT, seat, ".git")):
                return seat
    env = os.environ.get("AGENT_SEAT", "").strip().lower()
    if env and os.path.isdir(os.path.join(SEAT_ROOT, env, ".git")):
        return env
    raise PoolError("worktree pool: cannot derive a seat from cwd %r — run from a seat clone "
                    "%s/<seat> or set AGENT_SEAT (no clone at %s/%s)"
                    % (cwd, SEAT_ROOT, SEAT_ROOT, env or "<unset>"))


def clone_of(seat):
    return os.path.join(SEAT_ROOT, seat)


def slot_path(seat, n):
    p = os.path.join(POOL_ROOT, seat, "slot%d" % n)
    if ".claude" in p.split(os.sep):
        raise PoolError("slot path %s contains a .claude component; refusing" % p)
    return p


def lock_path(seat, n):
    return os.path.join(POOL_ROOT, seat, "slot%d.lock" % n)


def read_lock(seat, n):
    try:
        with open(lock_path(seat, n)) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def write_lock(seat, n, obj):
    tmp = lock_path(seat, n) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1, sort_keys=True)
    os.replace(tmp, lock_path(seat, n))


def is_worktree(path):
    return os.path.exists(os.path.join(path, ".git"))


DONE_STATUSES = {"completed", "failed", "error", "killed", "cancelled", "interrupted"}


def subagent_finished(lk):
    """True when the owning session's transcript records this subagent's terminal tool result.

    MEASURED 2026-10-02 (CC 2.1.285): WorktreeRemove never fires, not even for a subagent that
    changed nothing, and the subagent runs inside the parent `claude` process — so on pid alone a
    long-lived seat session holds every slot it ever used until it exits (a 3rd SEQUENTIAL isolated
    subagent in one session got `pool full`). The parent transcript does record
    `toolUseResult: {status: "completed", agentId, worktreePath}` when the subagent returns; the
    hook's `name` is `agent-<agentId>`. Background (async) agents never match here, so they stay
    held until their session exits — conservative, never unsafe.
    """
    name, tp = lk.get("name") or "", lk.get("transcript_path") or ""
    if not name.startswith("agent-") or not tp:
        return False
    aid = name[len("agent-"):]
    try:
        with open(tp, encoding="utf-8", errors="replace") as f:
            for line in f:
                if aid in line and "toolUseResult" in line:
                    try:
                        tr = json.loads(line).get("toolUseResult")
                    except ValueError:
                        continue
                    if isinstance(tr, dict) and tr.get("agentId") == aid and tr.get("status") in DONE_STATUSES:
                        return True
    except OSError:
        pass
    return False


def busy_reasons(seat, n):
    lk = read_lock(seat, n) or {}
    why = []
    path = slot_path(seat, n)
    if lk and not lk.get("released") and alive_match(lk.get("pid"), lk.get("pid_start")):
        if not subagent_finished(lk):
            why.append("owner pid %s alive (%s)" % (lk.get("pid"), lk.get("name")))
        elif is_worktree(path) and (dirty_entries(path) or
                                    not landed_reason(seat, path, slot_name(seat, n, path))):
            # finished, but its session may still harvest the work: never rescue under a live owner
            why.append("%s finished but holds unlanded work; owner pid %s alive — submit/land or "
                       "discard it" % (lk.get("name"), lk.get("pid")))
    if os.path.isdir(path):
        users = users_of(path)
        if users:
            why.append("pids %s have cwd/fd under the slot" % users[:8])
    return why


def dirty_entries(path):
    return git(path, "status", "--porcelain", "--untracked-files=all", check=False).splitlines()


def landed_reason(seat, path, name):
    head = git(path, "rev-parse", "HEAD")
    if is_ancestor(path, head, "refs/remotes/origin/main"):
        return "HEAD reachable from origin/main"
    for ref in ("refs/remotes/origin/submit/%s/%s" % (seat, name), "refs/landed/%s/%s" % (seat, name)):
        if name and ref_exists(path, ref) and is_ancestor(path, head, ref):
            return "HEAD reachable from " + ref
    cherry = git(path, "cherry", "refs/remotes/origin/main", head, check=False)
    if cherry.strip() and not any(l.startswith("+") for l in cherry.splitlines()):
        return "every commit patch-equivalent on origin/main"
    return None


def slot_name(seat, n, path):
    lk = read_lock(seat, n) or {}
    if lk.get("name"):
        return lk["name"]
    br = git(path, "symbolic-ref", "-q", "--short", "HEAD", check=False).strip()
    return br[len("agent/"):] if br.startswith("agent/") else (br or "unknown")


# ---------------------------------------------------------------- classification + rescue
def classify(rel, absolute):
    if SECRET_NAME.search(rel):
        return "suspect-secret"
    head = b""
    try:
        if os.path.isfile(absolute):
            with open(absolute, "rb") as f:
                head = f.read(65536)
    except OSError:
        pass
    if head and SECRET_CONTENT.search(head):
        return "suspect-secret"
    if any(g.search(rel) for g in GENERATED):
        return "generated"
    if b"\0" in head[:8192]:
        return "binary"
    if rel.lower().endswith(DOC_EXT):
        return "doc"
    return "source"


def zlist(out):
    return [p for p in out.split("\0") if p]


def rescue_slot(seat, n, path, reason):
    """Snapshot everything in a dead slot to a local rescue ref, verify it, record it. Returns event."""
    clone = clone_of(seat)
    lk = read_lock(seat, n) or {}
    name = slot_name(seat, n, path)
    stamp = utcnow().strftime("%Y%m%dT%H%M%SZ")
    ref = "refs/rescue/%s/%s-%s" % (seat, re.sub(r"[^\w.-]", "-", name), stamp)
    head = git(path, "rev-parse", "HEAD")
    idx = os.path.join(POOL_ROOT, seat, ".rescue-index-slot%d" % n)
    if os.path.exists(idx):
        os.remove(idx)
    env = dict(os.environ, GIT_INDEX_FILE=idx, GIT_LITERAL_PATHSPECS="1")
    try:
        # 1) the real index (staged state), if it is writable as a tree (not mid-conflict)
        parents = ["-p", head]
        start = head
        idx_note = "index: captured as second parent"
        itree = subprocess.run(["git", "-C", path, "write-tree"], capture_output=True, text=True)
        if itree.returncode == 0:
            icommit = git(path, "commit-tree", itree.stdout.strip(), "-p", head,
                          input="rescue index of %s\n" % name)
            parents += ["-p", icommit]
            start = itree.stdout.strip()   # staged-new files are in neither HEAD nor --others
        else:
            idx_note = "index: NOT captured (%s)" % itree.stderr.strip()[:200]
        # 2) working tree: tracked changes + untracked non-ignored <= 5 MB
        git(path, "read-tree", start, env=env)
        git(path, "add", "-u", env=env)
        untracked = zlist(git(path, "ls-files", "-z", "--others", "--exclude-standard", check=False))
        small, large = [], []
        for rel in untracked:
            try:
                size = os.lstat(os.path.join(path, rel)).st_size
            except OSError:
                continue
            (small if size <= RESCUE_MAX_BYTES else large).append((rel, size))
        if small:
            git(path, "add", "--pathspec-from-file=-", "--pathspec-file-nul", env=env,
                input="\0".join(r for r, _ in small) + "\0")
        ignored = zlist(git(path, "ls-files", "-z", "--others", "--ignored", "--exclude-standard",
                            "--directory", check=False))
        wtree = git(path, "write-tree", env=env)
        lines = ["rescue %s/%s slot%d %s" % (seat, name, n, stamp), "",
                 "reason: " + reason, "owner: pid %s session %s started %s"
                 % (lk.get("pid"), lk.get("session_id"), lk.get("started")),
                 "base_sha: %s  head: %s" % (lk.get("base_sha"), head), idx_note,
                 "LOCAL ONLY — never push refs/rescue/*.", ""]
        lines.append("NOT STORED, untracked > 5 MB (%d):" % len(large))
        lines += ["  %s (%d bytes)" % (r, s) for r, s in large[:LIST_CAP]]
        lines.append("NOT STORED, ignored (%d entries):" % len(ignored))
        lines += ["  " + r for r in ignored[:LIST_CAP]]
        if len(ignored) > LIST_CAP:
            lines.append("  ... +%d more" % (len(ignored) - LIST_CAP))
        sha = git(path, "commit-tree", wtree, *parents, input="\n".join(lines) + "\n")
        # 3) verify: the snapshot index must match the working tree byte-for-byte
        drift = git(path, "diff", "--name-only", sha, env=env, check=False).strip()
        if drift:
            raise PoolError("rescue snapshot of slot%d does not match the working tree (%s); slot left "
                            "untouched" % (n, drift.splitlines()[:5]))
        git(clone, "update-ref", ref, sha)
    finally:
        if os.path.exists(idx):
            os.remove(idx)
    base = git(path, "merge-base", "refs/remotes/origin/main", head, check=False).strip() or head
    changed = zlist(git(path, "diff-tree", "-r", "-z", "--name-only", "--no-renames", base, sha, check=False))
    classes, by_class = {}, {}
    for rel in changed + [r for r, _ in large] + ignored:
        c = classify(rel, os.path.join(path, rel))
        classes[c] = classes.get(c, 0) + 1
        by_class.setdefault(c, [])
        if len(by_class[c]) < LIST_CAP:
            by_class[c].append(rel)
    ev = {"event": "rescue", "ts": utcnow().isoformat(timespec="seconds"), "seat": seat,
          "slot": n, "name": name, "ref": ref, "sha": sha, "head": head, "base": base,
          "reason": reason, "owner": {k: lk.get(k) for k in ("pid", "session_id", "transcript_path")},
          "classes": classes, "paths": by_class, "large_unstored": [r for r, _ in large],
          "ignored_unstored_count": len(ignored), "pushed": False, "status": "open"}
    append_jsonl(os.path.join(POOL_ROOT, "rescues.jsonl"), ev)
    log("rescued slot%d (%s) -> %s %s classes=%s" % (n, name, ref, sha[:10], classes))
    return ev


def reset_slot(seat, n, path, name):
    old = git(path, "symbolic-ref", "-q", "--short", "HEAD", check=False).strip()
    git(clone_of(seat), "worktree", "unlock", path, check=False)
    git(path, "checkout", "-q", "-f", "-B", "agent/" + name, "refs/remotes/origin/main")
    git(path, "clean", "-fdq")
    if old and old != "agent/" + name and old.startswith("agent/"):
        git(path, "branch", "-q", "-D", old, check=False)
    left = dirty_entries(path)
    if left:
        raise PoolError("slot%d not clean after reset: %s" % (n, left[:5]))


# ---------------------------------------------------------------- verbs
def fetch(seat):
    clone = clone_of(seat)
    r = subprocess.run(["git", "-C", clone, "fetch", "-q", "--prune", "origin",
                        "+refs/heads/main:refs/remotes/origin/main",
                        "+refs/heads/submit/%s/*:refs/remotes/origin/submit/%s/*" % (seat, seat)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        log("fetch failed (continuing on cached origin/main): " + r.stderr.strip()[:300])
    if not ref_exists(clone, "refs/remotes/origin/main"):
        raise PoolError("seat clone %s has no origin/main" % clone)


def cmd_create(d):
    t0 = time.time()
    seat = seat_from_cwd(d.get("cwd"))
    clone = clone_of(seat)
    raw = d.get("name") or d.get("worktree_name") or "wt"
    name = re.sub(r"[^\w.-]", "-", raw).strip(".-") or "wt"
    if not git_ok(clone, "check-ref-format", "--branch", "agent/" + name):
        raise PoolError("worktree name %r is not a valid branch name" % raw)
    os.makedirs(os.path.join(POOL_ROOT, seat), exist_ok=True)
    with open(os.path.join(POOL_ROOT, seat, "alloc.mutex"), "w") as mx:
        fcntl.flock(mx, fcntl.LOCK_EX)
        fetch(seat)
        held, problems, chosen = {}, [], None
        for n in range(SLOTS):
            why = busy_reasons(seat, n)
            if why:
                held[n] = why
                continue
            path = slot_path(seat, n)
            try:
                if is_worktree(path):
                    prev = slot_name(seat, n, path)
                    dirty = dirty_entries(path)
                    landed = landed_reason(seat, path, prev)
                    if dirty or not landed:
                        reason = ("dirty (%d entries)" % len(dirty) if dirty else "clean") + \
                                 ("" if landed else ", HEAD not landed")
                        ev = rescue_slot(seat, n, path, reason)
                        telemetry(seat, n, "rescue", time.time() - t0, name=prev, ref=ev["ref"])
                    reset_slot(seat, n, path, name)
                    log("recycled slot%d %s -> agent/%s" % (n, prev, name))
                else:
                    if os.path.exists(path):
                        aside = path + ".orphan-" + utcnow().strftime("%Y%m%dT%H%M%SZ")
                        os.rename(path, aside)
                        log("slot%d had no .git; moved aside to %s" % (n, aside))
                    git(clone, "worktree", "prune")
                    git(clone, "worktree", "add", "-q", "-B", "agent/" + name, path,
                        "refs/remotes/origin/main")
                    log("created slot%d agent/%s" % (n, name))
                chosen = n
                break
            except PoolError as e:
                problems.append("slot%d: %s" % (n, e))
                log("slot%d skipped: %s" % (n, e))
        if chosen is None:
            telemetry(seat, None, "full", time.time() - t0, name=name)
            owners = "; ".join("slot%d: %s" % (k, ", ".join(v)) for k, v in held.items())
            msg = "pool full: seat %s, all %d slots unavailable — held: %s" % (seat, SLOTS, owners or "none")
            if problems:
                msg += " — unusable: " + "; ".join(problems)
            raise PoolError(msg + ". Run the task without isolation if it is a quick single-path "
                            "edit, otherwise queue it. (`worktree_pool.py status` for detail)")
        path = slot_path(seat, chosen)
        prev = read_lock(seat, chosen) or {}
        gen = int(prev.get("generation", 0)) + 1
        pid = owner_pid()
        st = proc_stat(pid)
        git(clone, "worktree", "lock", "--reason", "%s gen %d" % (d.get("session_id"), gen), path,
            check=False)
        write_lock(seat, chosen, {
            "pid": pid, "pid_start": st[2] if st else None, "session_id": d.get("session_id"),
            "transcript_path": d.get("transcript_path"), "name": name, "generation": gen,
            "base_sha": git(path, "rev-parse", "HEAD"), "started": utcnow().isoformat(timespec="seconds")})
        telemetry(seat, chosen, "alloc", time.time() - t0, name=name, generation=gen)
    print(path)
    return 0


def slot_from_path(path):
    real = os.path.realpath(path or "")
    m = re.fullmatch(re.escape(POOL_ROOT) + r"/([^/]+)/slot(\d+)", real)
    return (m.group(1), int(m.group(2))) if m else (None, None)


def cmd_remove(d):
    path = d.get("worktree_path") or d.get("path") or ""
    seat, n = slot_from_path(path)
    if seat is None:
        log("remove: %r is not a pool slot; ignoring" % path)
        return 0
    with open(os.path.join(POOL_ROOT, seat, "alloc.mutex"), "w") as mx:
        fcntl.flock(mx, fcntl.LOCK_EX)
        name = slot_name(seat, n, path)
        dirty, landed = dirty_entries(path), landed_reason(seat, path, name)
        if dirty or not landed:
            log("remove slot%d: KEPT (dirty=%d landed=%s); rescue happens at next allocation"
                % (n, len(dirty), bool(landed)))
            return 0
        lk = read_lock(seat, n) or {}
        lk["released"] = utcnow().isoformat(timespec="seconds")
        write_lock(seat, n, lk)
        git(clone_of(seat), "worktree", "unlock", path, check=False)
        log("released slot%d (%s)" % (n, name))
    return 0


def seats():
    out = []
    if os.path.isdir(POOL_ROOT):
        out = sorted(s for s in os.listdir(POOL_ROOT) if os.path.isdir(os.path.join(POOL_ROOT, s)))
    return out


def cmd_status(as_json):
    rows = []
    for seat in seats():
        for n in range(SLOTS):
            path = slot_path(seat, n)
            lk = read_lock(seat, n) or {}
            row = {"seat": seat, "slot": n, "path": path, "exists": is_worktree(path),
                   "name": lk.get("name"), "generation": lk.get("generation"),
                   "owner_pid": lk.get("pid"), "started": lk.get("started"),
                   "released": lk.get("released"), "busy": busy_reasons(seat, n)}
            if row["exists"]:
                row["head"] = git(path, "rev-parse", "--short", "HEAD", check=False).strip()
                row["dirty"] = len(dirty_entries(path))
                row["landed"] = landed_reason(seat, path, slot_name(seat, n, path))
            rows.append(row)
    if as_json:
        print(json.dumps(rows, indent=1))
        return 0
    if not rows:
        print("no pool under %s" % POOL_ROOT)
    for r in rows:
        state = "BUSY" if r["busy"] else ("EMPTY" if not r["exists"] else
                "FREE" if not r.get("dirty") and r.get("landed") else "NEEDS-RESCUE")
        print("%-8s slot%d %-12s gen=%-3s %-28s head=%s dirty=%s  %s" % (
            r["seat"], r["slot"], state, r["generation"], (r["name"] or "-")[:28], r.get("head", "-"),
            r.get("dirty", "-"), "; ".join(r["busy"])))
    return 0


def cmd_rescue_list(as_json):
    events = {}
    try:
        for line in open(os.path.join(POOL_ROOT, "rescues.jsonl")):
            ev = json.loads(line)
            events[ev["ref"]] = ev
    except (OSError, ValueError):
        pass
    rows = []
    for seat in sorted(os.listdir(SEAT_ROOT)) if os.path.isdir(SEAT_ROOT) else []:
        clone = clone_of(seat)
        if not os.path.isdir(os.path.join(clone, ".git")):
            continue
        out = git(clone, "for-each-ref", "--format=%(refname) %(objectname:short) %(creatordate:iso-strict)",
                  "refs/rescue/", check=False)
        for line in out.splitlines():
            ref, sha, date = line.split(" ", 2)
            ev = events.get(ref, {})
            age = (utcnow() - datetime.datetime.fromisoformat(date)).days
            rows.append({"ref": ref, "sha": sha, "date": date, "age_days": age,
                         "classes": ev.get("classes"), "reason": ev.get("reason"),
                         "stale_over_30d": age > 30})
    if as_json:
        print(json.dumps(rows, indent=1))
    elif not rows:
        print("no rescue refs")
    else:
        for r in rows:
            print("%s %s %dd %s %s%s" % (r["ref"], r["sha"], r["age_days"], r["classes"], r["reason"],
                                        "  [>30 days: land, cherry-pick or drop]" if r["stale_over_30d"] else ""))
    return 0


def cmd_submit():
    top = git(os.getcwd(), "rev-parse", "--show-toplevel")
    seat, n = slot_from_path(top)
    if seat is None:
        raise PoolError("submit runs inside a pool slot (%s/<seat>/slotN); this is %s" % (POOL_ROOT, top))
    br = git(top, "symbolic-ref", "--short", "HEAD")
    if not br.startswith("agent/"):
        raise PoolError("slot branch is %r, expected agent/<name>" % br)
    name = br[len("agent/"):]
    if dirty_entries(top):
        print("warning: uncommitted changes in the slot are NOT submitted", file=sys.stderr)
    git(top, "fetch", "-q", "origin", "+refs/heads/main:refs/remotes/origin/main")
    git(top, "rebase", "-q", "refs/remotes/origin/main")
    files = git(top, "diff", "--name-only", "refs/remotes/origin/main...HEAD").splitlines()
    if not files:
        raise PoolError("nothing to submit: HEAD has no commits beyond origin/main")
    dlls = [f for f in files if f.lower().endswith(".dll")]
    if dlls:
        raise PoolError("slots never commit DLLs; the seat rebuilds. Remove: %s" % dlls)
    ref = "refs/heads/submit/%s/%s" % (seat, name)
    git(top, "push", "-q", "origin", "HEAD:" + ref)
    print("SUBMITTED %s %s (%d files) — the %s seat lands it with land_submissions.py"
          % (ref, git(top, "rev-parse", "HEAD"), len(files), seat))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("verb", choices=["create", "remove", "status", "rescue-list", "submit"])
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        if a.verb in ("create", "remove"):
            raw = sys.stdin.read()
            log("%s stdin=%s" % (a.verb, raw.strip()))
            d = json.loads(raw or "{}")
            return cmd_create(d) if a.verb == "create" else cmd_remove(d)
        if a.verb == "status":
            return cmd_status(a.json)
        if a.verb == "rescue-list":
            return cmd_rescue_list(a.json)
        return cmd_submit()
    except PoolError as e:
        log("%s FAILED: %s" % (a.verb, e))
        print(str(e), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
