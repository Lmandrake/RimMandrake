#!/usr/bin/env python3
"""code_review_status.py — what CLEAN means, and the review record.

`check` reads CLEAN against a page of promises (owner, 2026-11-19,
standing_rulings.md §Code is clean when its promises are tested; this tool's
own page: design/specs/2026-11-19-clean-means-promises-tested/boundary.md).
A file is CLEAN when a boundary page names it, each promise there has a test
of the same name, and the page's tests file passes. DIRTY: a promise lacks a
test or the tests fail. UNREADABLE: a page or tests file could not be read or
run. NO PAGE: no page names it (not a defect; it gets a page when next changed).
A file inside a mod (src/RimMandrake/<Mod>/) also reads against its mod's
locked bars: the bars are the promises, the test table rows that decide each
bar are the tests (owner, by card 2026-11-19; `mod_page_state`).

The review record below (`mark-clean`, `reopen`, `list`, `check --record`)
records that a review round was done on exact bytes. It makes nothing CLEAN.
Two meanings, named apart: PAGE-CLEAN is `check` (each promise has a passing
test); READ-CLEAN is the review record (a cold read found nothing significant).

FLAGGED (owner, by card 2026-11-19 5:54 PM PST): a file whose one blind reread
of a fix also found and fixed a significant finding. Nobody reviews it again:
`list` counts it FLAGGED, never review debt, and `mark-clean` refuses it. The
weekly examination reads `list --flagged` and ends a flag with `unflag`. A flag
is not a page state: `check` answers as before.

🔴 This is not a Python-only tool. It covers ANY file that contributes to
what the game actually loads — .py tooling, .cs mod source, .xml Defs and
Patches alike. The clean rule (CLAUDE.md) never said Python; do not
narrow it. Owner ruling 2026-09-03, after an agent was
told mid-review not to mark-clean a .cs file "because C# isn't in scope
yet" — it always was.

    python3 src/RimMandrake/Utils/code_review_status.py check <path> [<path> ...]   exit 0/1/3/4 (page above)
    python3 src/RimMandrake/Utils/code_review_status.py check --record <path> ...  the review record, exit 0/1
    python3 src/RimMandrake/Utils/code_review_status.py mark-clean <path> [--sha <sha>]
        [--gpt-job <job> | --reviewer-seat <SEAT> [--reviewer-session <id>] [--reviewer-agent <name>]]
        records WHO reviewed (default: this process, whoami()) apart from the recording seat; see review_identity.py
    python3 src/RimMandrake/Utils/code_review_status.py reopen <path> [<path> ...] --reason "…"
    python3 src/RimMandrake/Utils/code_review_status.py list
    python3 src/RimMandrake/Utils/code_review_status.py list --show-untracked  # + files never entered at all
    python3 src/RimMandrake/Utils/code_review_status.py flag <path> --why "…"     # the reread also fixed a significant finding
    python3 src/RimMandrake/Utils/code_review_status.py unflag <path> --why "…"   # the weekly examination ends the flag
    python3 src/RimMandrake/Utils/code_review_status.py list --flagged           # exit 0, or 3 when a flag shard is unreadable
    python3 src/RimMandrake/Utils/code_review_status.py migrate-hashes   # one-time, see below

The log (`infrastructure/state/code_review/<SEAT>.jsonl`, append-only records,
one shard per seat, `merge=union`) is owned by this script — do not hand-edit
it, the same convention as the ledger. It replaced the single
`CODE_REVIEW_STATUS.json` on 2026-10-02 (git plan Phase 5); that file's 3,911
entries were migrated once into `code_review/SEED.jsonl` and the JSON removed.

🔴 SCALING REWRITE, owner ruling 2026-09-05 — "I think we need a different
implementation for the clean/dirty code database... this isn't scaling
properly, it's a bottleneck": the previous implementation answered every
`check`/`list` call by asking git (`git status --porcelain` PLUS `git log`
PER PATH). At 1 caller that's fine; with this repo's usual load — many
concurrent review agents, each walking dozens of paths — it fanned out into
hundreds of `git` subprocess spawns hammering one `.git` directory on a
WSL-over-Windows-drive mount, and a single `list` over ~800 recorded entries
alone was ~1,600 spawns. That is what a background agent was seen stuck on
for 10 minutes.

The fix: CLEAN/DIRTY is now answered by comparing a SHA-256 of the file's
current bytes against a hash recorded at `mark-clean` time — zero git calls
for `list` and for `check` of recorded paths; `check` on paths with no entry
and `reopen` add ONE batched `git ls-files` spawn (drvfs case
canonicalization), never one per path. `mark-clean` still makes a
small, BEST-EFFORT, TIMEOUT-GUARDED git call or two (to check the file is
tracked, to refuse on uncommitted changes exactly as documented in CLAUDE.md,
and to record an informational commit sha/date) — but those calls happen
once per reviewed file, not once per file per query, and a hung/slow git can
never again hang this tool: every git() call has a hard timeout and a
failure path that still lets the hash-based core answer correctly.

`migrate-hashes` is the one-time backfill for entries recorded before this
rewrite (they carry {sha, date, cleanCount} but no {hash}): for each one it
reads the file's content AS IT WAS AT THE RECORDED SHA (`git show sha:path`)
and hashes that — not the current working-tree copy, which may already have
diverged — so a legacy CLEAN entry's true reviewed content is preserved
exactly, not silently reset to whatever happens to be on disk today. An
entry whose sha no longer resolves gets no hash and reads as DIRTY
("legacy entry, needs re-verification") — the same outcome the old
"recorded sha not found — log is stale" case produced.
"""
import argparse
import contextlib
import fcntl
import glob
import hashlib
import json
import os
import re
import stat as stat_mod
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import boundary_check as BC  # noqa: E402  the page reader and the promise-to-test match
sys.path.append(os.path.join(os.path.dirname(HERE), "rimflow"))  # judge_certificate, for mod pages (last: shadows nothing)
# CODE_REVIEW_STATUS_ROOT redirects the whole tool at a throwaway repo, same
# discipline as rimflow's RIMFLOW_LEDGER/RIMFLOW_ITEMS — a selftest must never
# run mark-clean/reopen against this repo's own real ledger.
ROOT = os.environ.get("CODE_REVIEW_STATUS_ROOT") or os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
# 🔴 APPEND-ONLY RECORDS, git plan Phase 5 (2026-10-02, design/RimMandrake/
# git_migration_phase5_2026-10-02.md). The single CODE_REVIEW_STATUS.json was a
# whole-file rewrite every seat committed, so every concurrent mark-clean was a
# merge conflict (X2 replay: 15 conflicted commits at K=5). It is now one
# append-only JSONL shard per seat under `code_review/`, merged by
# `.gitattributes` `merge=union`; a record is
#   {path, sha256, verdict: clean|dirty|pruned, ts, seat, sha, date, cleanCount}
# and the CURRENT state of a path is its last record, ordered by (ts, seat, line).
# `load()` still returns the old {path: entry} dict, so every reader is unchanged.
# The old JSON was migrated once into `code_review/SEED.jsonl` and removed.
REC_DIR = os.path.join(ROOT, "infrastructure", "state", "code_review")
LOG_PATH = REC_DIR          # kept for messages/back-compat: the record directory
LOCK_PATH = os.path.join(REC_DIR, ".lock")

GIT_TIMEOUT = 8  # seconds. A hung/contended git call fails fast, never hangs the caller.


@contextlib.contextmanager
def locked():
    """Exclusive lock across a load-mutate-save critical section. This repo
    is shared by two live agent windows (BENCH/FOUNDRY); without this, two
    concurrent mark-clean calls on different files is a lost-update race —
    whichever save() runs last wins and the other's entry silently vanishes.

    Still held only around the tiny load/save below, never around any git
    call — that discipline predates this rewrite and stays: a lock held
    across a slow subprocess is exactly how one stuck caller would freeze
    out every other one."""
    os.makedirs(os.path.dirname(LOCK_PATH), exist_ok=True)
    fd = os.open(LOCK_PATH, os.O_WRONLY | os.O_CREAT, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def _seat():
    """Which shard this process appends to. Same order as rimflow's resolver
    minus the refusal: a code-review record's seat is provenance, not a
    permission, so an unresolvable seat writes to UNSEATED.jsonl rather than
    blocking a review."""
    import re as _re
    for val in (os.environ.get("RIMFLOW_SEAT"), os.environ.get("AGENT_SEAT")):
        if val and _re.fullmatch(r"[A-Za-z0-9_]+", val.strip()):
            return val.strip().upper()
    sid = os.environ.get("CLAUDE_SESSION_ID")
    if sid:
        try:
            with open(os.path.join(ROOT, ".claude", "session_roles", sid), encoding="utf-8") as fh:
                for w in fh.read().replace("-", " ").split():
                    if w.upper() in ("BENCH", "FOUNDRY", "BUILD", "DECIDE", "OWNER"):
                        return w.upper()
        except OSError:
            pass
    return "UNSEATED"


def _record_files():
    try:
        names = sorted(n for n in os.listdir(REC_DIR) if n.endswith(".jsonl"))
    except FileNotFoundError:
        return []
    return [os.path.join(REC_DIR, n) for n in names]


def read_records():
    """Every record across every shard, in state order (ts, seat, file line).
    Identical duplicate lines (a union merge of the same append) collapse."""
    out, seen = [], set()
    for fp in _record_files():
        with open(fp, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                if line.startswith(("<<<<<<<", "=======", ">>>>>>>")):
                    sys.exit("FAIL: %s holds merge conflict markers — the shards are "
                             "merge=union and must never conflict; fix .gitattributes." % fp)
                try:
                    rec = json.loads(line)
                except ValueError as e:
                    sys.exit("FAIL: %s line %d is not valid JSON: %s" % (fp, i + 1, e))
                if line in seen:
                    continue
                seen.add(line)
                out.append(((rec.get("ts", ""), rec.get("seat", ""), os.path.basename(fp), i), rec))
    out.sort(key=lambda t: t[0])
    return [r for _, r in out]


def _entry_from(rec):
    e = {"sha": rec.get("sha", "unknown"), "date": rec.get("date", "unknown")}
    if rec.get("sha256"):
        e["hash"] = rec["sha256"]
    if "cleanCount" in rec:
        e["cleanCount"] = rec["cleanCount"]
    if rec.get("verdict") == "dirty":
        e["status"] = "dirty"
    else:
        e.update({k: rec[k] for k in REVIEW_KEYS if k in rec})
    return e


def load():
    """-> {path: entry} — the current state, last record per path. Same shape
    the single JSON file had, so codebase_health/project_maturity readers are
    unchanged."""
    data = {}
    for rec in read_records():
        path = rec.get("path")
        if not path:
            continue
        if rec.get("verdict") == "pruned":
            data.pop(path, None)
        else:
            data[path] = _entry_from(rec)
    return data


_last_ts = [0]


def _ts():
    # Strictly increasing within a process, so two records one call writes for
    # the same path can never tie and reorder.
    ns = max(time.time_ns(), _last_ts[0] + 1000)
    _last_ts[0] = ns
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(ns // 10**9)) + ".%06dZ" % ((ns % 10**9) // 1000)


#: who reviewed a clean mark (review_identity): carried on clean records only, never on dirty/pruned ones
REVIEW_KEYS = ("reviewer", "recorder", "review_mac")


def _record(path, entry, seat, ts):
    if entry is None:
        return {"path": path, "sha256": None, "verdict": "pruned", "ts": ts, "seat": seat}
    rec = {"path": path, "sha256": entry.get("hash"),
           "verdict": "dirty" if entry.get("status") == "dirty" else "clean",
           "ts": ts, "seat": seat,
           "sha": entry.get("sha", "unknown"), "date": entry.get("date", "unknown")}
    if "cleanCount" in entry:
        rec["cleanCount"] = entry["cleanCount"]
    if rec["verdict"] == "clean":
        rec.update({k: entry[k] for k in REVIEW_KEYS if k in entry})
    return rec


def append_records(recs, shard=None, rec_dir=None):
    """Append records to this seat's shard: one O_APPEND write, fsynced. Never
    rewrites an existing line — the shard is append-only (lint enforces it)."""
    if not recs:
        return
    rec_dir = rec_dir or REC_DIR
    os.makedirs(rec_dir, exist_ok=True)
    fp = os.path.join(rec_dir, (shard or _seat()) + ".jsonl")
    body = "".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n" for r in recs)
    dlock = _dir_lock(os.path.dirname(fp))
    try:
        fd = _open_shard_locked(fp)
        try:
            os.write(fd, body.encode("utf-8"))
            os.fsync(fd)
        finally:
            os.close(fd)       # closing drops the flock
    finally:
        if dlock is not None:
            os.close(dlock)


def _dir_lock(d):
    """A SHARED flock on the shard's directory for the whole append: relentless level_books holds it EXCLUSIVE while git
    replaces the shards, so no line lands on a file mid-checkout. -> the fd, or None where the filesystem has no
    directory flock (the per-file lock still serialises writers)."""
    import fcntl
    try:
        fd = os.open(d, os.O_RDONLY)
    except OSError:
        return None
    try:
        fcntl.flock(fd, fcntl.LOCK_SH)
    except OSError:
        os.close(fd)
        return None
    return fd


def _open_shard_locked(fp):
    """-> an O_APPEND fd on `fp` holding its flock, on the inode now at `fp`. relentless level_books takes this flock
    while it compares a reordered shard and puts HEAD's order back, and while git replaces it: an append waits instead
    of landing in between and being cut away; if the file was replaced meanwhile, this reopens the new one."""
    for _ in range(5):
        fd = os.open(fp, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
        fcntl.flock(fd, fcntl.LOCK_EX)
        try:
            here = os.stat(fp)
        except FileNotFoundError:
            here = None
        st = os.fstat(fd)
        if here is not None and (here.st_dev, here.st_ino) == (st.st_dev, st.st_ino):
            return fd
        os.close(fd)
    raise OSError("%s kept moving under its lock: records not written" % fp)


def save(data):
    """Make the current state equal `data` by APPENDING one record per path
    whose entry changed (and a `pruned` record per path removed). Callers keep
    the load-mutate-save shape under `locked()`; nothing is ever rewritten."""
    current = load()
    seat = _seat()
    recs = []
    for path in sorted(set(current) | set(data)):
        new = data.get(path)
        if new == current.get(path):
            continue
        recs.append(_record(path, new, seat, _ts()))
    append_records(recs)


# FLAGGED: its own append-only shards, `code_review/flags/<SEAT>.jsonl`, so no
# reader of the review records (load(), code_review_since.py) ever sees a flag
# as a clean or dirty mark. A record is {event: flag|unflag, path, why, ts,
# seat, sha256}; a path is flagged while its last record is a flag.
def flag_dir():
    """Read at call time from ROOT, so a selftest that moves ROOT moves the flags too."""
    return os.path.join(ROOT, "infrastructure", "state", "code_review", "flags")


class FlagsUnreadable(Exception):
    """A flag shard could not be read or parsed: whether a path is flagged is unknown."""


def flags():
    """-> {path: its last flag record} for every path flagged now. Raises FlagsUnreadable."""
    d = flag_dir()
    try:
        names = sorted(n for n in os.listdir(d) if n.endswith(".jsonl"))
    except FileNotFoundError:
        return {}
    except OSError as e:
        raise FlagsUnreadable("%s: %s" % (d, e))
    recs = []
    for n in names:
        fp = os.path.join(d, n)
        try:
            with open(fp, encoding="utf-8") as f:
                lines = f.read().splitlines()
        except (OSError, UnicodeDecodeError) as e:
            raise FlagsUnreadable("%s: %s" % (fp, e))
        for i, line in enumerate(lines):
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except ValueError as e:
                raise FlagsUnreadable("%s line %d is not valid JSON: %s" % (fp, i + 1, e))
            if not isinstance(rec, dict) or rec.get("event") not in ("flag", "unflag") or not rec.get("path"):
                raise FlagsUnreadable("%s line %d is not a flag record" % (fp, i + 1))
            recs.append(((rec.get("ts", ""), rec.get("seat", ""), n, i), rec))
    out = {}
    for _, rec in sorted(recs, key=lambda t: t[0]):
        if rec["event"] == "flag":
            out[rec["path"]] = rec
        else:
            out.pop(rec["path"], None)
    return out


def _flag_target(path, why):
    """-> (rel, None) or (None, exit code) after printing the refusal."""
    rel = canonical_rel(repo_rel(path))
    if rel.startswith("../") or rel == "..":
        print(f"FAIL: {rel} is outside the repo root.", file=sys.stderr)
        return None, 2
    if not (why or "").strip():
        print("FAIL: --why is empty: say what the reread found, or what the examination decided.", file=sys.stderr)
        return None, 2
    return rel, None


def cmd_flag(path, why):
    rel, rc = _flag_target(path, why)
    if rel is None:
        return rc
    if not os.path.isfile(os.path.join(ROOT, rel)):
        print(f"FAIL: {rel} does not exist under the repo root.", file=sys.stderr)
        return 2
    h = file_hash(rel)
    append_records([{"event": "flag", "path": rel, "why": why.strip(), "ts": _ts(), "seat": _seat(),
                     "sha256": h if isinstance(h, str) else None}], rec_dir=flag_dir())
    print(f"FLAGGED  {rel}  nobody reviews it again; the weekly examination reads `list --flagged`")
    return 0


def cmd_unflag(path, why):
    rel, rc = _flag_target(path, why)
    if rel is None:
        return rc
    try:
        now = flags()
    except FlagsUnreadable as e:
        print(f"UNREADABLE  flags: {e}", file=sys.stderr)
        return 3
    if rel not in now:
        print(f"FAIL: {rel} is not flagged.", file=sys.stderr)
        return 2
    append_records([{"event": "unflag", "path": rel, "why": why.strip(), "ts": _ts(), "seat": _seat()}],
                   rec_dir=flag_dir())
    print(f"UNFLAGGED  {rel}")
    return 0


def cmd_list_flagged():
    try:
        now = flags()
    except FlagsUnreadable as e:
        print(f"UNREADABLE  flags: {e}")
        return 3
    if not now:
        print("(no file is flagged)")
    for rel in sorted(now):
        rec = now[rel]
        print(f"FLAGGED  {rel}  {rec.get('ts', '?')} {rec.get('seat', '?')}: {rec.get('why', '')}")
    print(f"\nTALLY  FLAGGED {len(now)}")
    return 0


def repo_rel(path):
    ap = os.path.abspath(path)
    rel = os.path.relpath(ap, ROOT).replace(os.sep, "/")
    if (rel.startswith("../") or rel == "..") and \
            ap.lower().startswith(ROOT.rstrip("/").lower() + "/"):
        # drvfs resolves case-insensitively, so /mnt/d/luke/... IS this repo;
        # a case-mismatched ROOT prefix must not read as "outside the repo".
        rel = ap[len(ROOT.rstrip("/")) + 1:].replace(os.sep, "/")
    return rel


_dir_cache = {}


def exact_case_isfile(rel):
    """True iff every segment of rel exists with EXACTLY this spelling.
    os.path.isfile on drvfs answers case-insensitively, so after a case-only
    rename the stale spelling still 'exists' and would read CLEAN forever.
    Pure listdir + cache — no subprocess, safe in list's 1500-entry loop.
    Unreadable directories answer True: ignorance must not invent DIRTY."""
    cur = ROOT
    for part in rel.split("/"):
        names = _dir_cache.get(cur)
        if names is None:
            try:
                names = set(os.listdir(cur))
            except OSError:
                return True
            _dir_cache[cur] = names
        if part not in names:
            # The cache can be stale for files created after it filled (a
            # long-lived importer, the selftest): re-list before concluding
            # absence. A stale True only delays phantom detection one call;
            # a stale False would invent DIRTY, so absence must be re-proven.
            try:
                names = set(os.listdir(cur))
            except OSError:
                return True
            _dir_cache[cur] = names
            if part not in names:
                return False
        cur = os.path.join(cur, part)
    return True


def canonical_rels(rels):
    """/mnt/d (drvfs) resolves paths case-insensitively, but the ledger and
    git are case-sensitive: a mis-cased argument reads as "never reviewed"
    and then fails mark-clean's tracked-file gate with a false message. Ask
    git for the tracked spelling — in ONE `ls-files` spawn for the whole
    batch, because a spawn per path is the exact bottleneck this rewrite
    removed. Returns ({rel: canonical}, certain): identity for anything
    out-of-repo, ambiguous, or unknown to git; certain is False when git
    itself could not answer (timeout/lock) — a caller whose CORRECTNESS
    depends on canonicalization must refuse on ignorance, not proceed on
    the identity mapping as if it were an answer."""
    out = {r: r for r in rels}
    ask = [r for r in rels if not (r.startswith("../") or r == "..")]
    if not ask:
        return out, True
    # (icase,literal): literal kills glob interpretation — "[", "*", "?" in a
    # filename are pathspec magic by default and would match a DIFFERENT file.
    # -z: NUL-separated is the only mode git never quotes in ('"' and '\\'
    # are still C-quoted even under quotePath=false).
    r = git(["ls-files", "-z", "--"]
            + [":(icase,literal)" + a for a in ask])
    if r.returncode != 0:
        return out, False
    lines = [l for l in r.stdout.split("\0") if l]
    exact = set(lines)
    by_fold = {}
    for l in lines:
        by_fold.setdefault(l.lower(), []).append(l)
    for a in ask:
        if a in exact:
            continue
        ci = by_fold.get(a.lower(), [])
        if len(ci) == 1:
            out[a] = ci[0]
    return out, True


def canonical_rel(rel):
    """Single-path form of canonical_rels(); identity on ignorance (the
    callers behind this form all have their own honest git-failure gates)."""
    return canonical_rels([rel])[0][rel]


def git(args):
    """Run git with a hard timeout, decoding output as text. A
    `.git/index.lock` collision (many concurrent callers, exactly this
    repo's normal load) now fails fast with returncode -1 instead of
    hanging the caller — every use site below treats a git failure as
    "cannot tell, fall back / refuse", never as silent success, so a
    timeout is always safe, just less informative."""
    try:
        # surrogateescape: with core.quotePath=false a non-UTF-8 tracked path
        # (possible on WSL's ext4 side) must degrade, not traceback the caller.
        return subprocess.run(["git"] + args, cwd=ROOT, capture_output=True,
                               text=True, errors="surrogateescape",
                               timeout=GIT_TIMEOUT)
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(args, -1, "", "git timed out after %ss" % GIT_TIMEOUT)
    except OSError as e:
        # git missing/unexecutable must degrade to refuse like every other
        # git failure, not traceback past the documented contract.
        return subprocess.CompletedProcess(args, -1, "", "git could not run: %s" % e)


def git_bytes(args):
    """Same as git(), but returns raw bytes (stdout) instead of decoded
    text — `migrate-hashes` uses this for `git show sha:path`, and many of
    this repo's reviewed paths are PNGs, which are not valid UTF-8 and
    would crash a text-mode decode."""
    try:
        return subprocess.run(["git"] + args, cwd=ROOT, capture_output=True,
                               text=False, timeout=GIT_TIMEOUT)
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(args, -1, b"", b"git timed out after %ds" % GIT_TIMEOUT)
    except OSError as e:
        return subprocess.CompletedProcess(args, -1, b"", b"git could not run: %s" % str(e).encode())


#: file_hash sentinel — compare with `is`. Never a valid hex digest.
UNREADABLE = "<unreadable>"


def proven_gone(rel):
    """PROVEN absent (or no longer a regular file) only. os.path.isfile
    answers False for IGNORANCE too (EACCES/EIO/drvfs stale read); acting
    on ignorance destroys valid entries (prune) or tells a caller an
    existing file does not exist (check). Ignorance answers False here."""
    try:
        st = os.stat(os.path.join(ROOT, rel))
    except (FileNotFoundError, NotADirectoryError):
        return True
    except OSError:
        return False
    return not stat_mod.S_ISREG(st.st_mode)


def file_hash(relpath):
    """SHA-256 of the file's current bytes on disk, or None if it doesn't
    exist / can't be read. This is the WHOLE clean/dirty answer now — no
    git call, no subprocess, safe to run thousands of times in a `list`."""
    try:
        with open(os.path.join(ROOT, relpath), "rb") as f:
            h = hashlib.sha256()
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
            return h.hexdigest()
    except (FileNotFoundError, NotADirectoryError, IsADirectoryError):
        # IsADirectoryError must land here, not in UNREADABLE: the FILE is
        # gone, and clean_state's "path is now a directory" branch reads it.
        return None
    except OSError:
        # Exists but cannot be read (permissions, drvfs IO fault). NOT the
        # same answer as "gone" — the remedies differ.
        return UNREADABLE


def clean_state(rel, entry):
    """Returns (state, detail) where state is CLEAN/DIRTY. `entry` may be
    None (never marked). Shared by `check` and `list` so the two commands
    cannot disagree about what CLEAN means. Pure Python, zero subprocess
    calls — this is the fix for the scaling bottleneck: the old version
    made two `git` spawns per path here."""
    if entry is None:
        return "DIRTY", "never marked clean"
    if entry.get("status") == "dirty":
        # reopen() flipped this rather than deleting it - PRESERVE HISTORY
        # (owner ruling 2026-09-04): the streak/cleanCount stays visible on
        # the health board across the reopen.
        streak = entry.get("cleanCount", 0)
        return "DIRTY", "reopened — needs a fresh full-file review before " \
            "mark-clean (prior clean streak: %d)" % streak
    recorded_hash = entry.get("hash")
    if not recorded_hash:
        # A pre-rewrite entry that `migrate-hashes` couldn't backfill (its
        # sha no longer resolved) — same outcome as the old "log is stale".
        return "DIRTY", "legacy entry with no recorded hash — needs re-verification"
    current = file_hash(rel)
    if current is None:
        if os.path.isdir(os.path.join(ROOT, rel)):
            return "DIRTY", "path is now a directory"
        return "DIRTY", "file no longer exists on disk"
    if current is UNREADABLE:
        return "DIRTY", "file exists but could not be read (permissions/IO?) — not evidence of change"
    # Phantom test BEFORE the hash comparison: a case-renamed entry whose
    # content ALSO changed must name the phantom (whose remedy, reopen/prune,
    # actually works) — "content changed" would send the reviewer to a
    # mark-clean that refuses on the dead spelling.
    if not exact_case_isfile(rel):
        # drvfs found the bytes case-insensitively, but this exact spelling
        # is gone (case-only rename): a phantom entry, not a clean file.
        return "DIRTY", "recorded spelling no longer exists on disk (case-renamed?) — reopen or prune this entry"
    if current != recorded_hash:
        return "DIRTY", "content changed since clean mark at %s on %s" % (
            entry.get("sha", "?"), entry.get("date", "?"))
    return "CLEAN", "clean at %s on %s" % (entry.get("sha", "?"), entry.get("date", "?"))


# ---- CLEAN against a page of promises (owner, 2026-11-19) -------------------
# `check` reads CLEAN only against a stated page of promises whose tests pass:
# design/specs/2026-11-19-clean-means-promises-tested/boundary.md. The review
# record above answers only `check --record` (a review round on these bytes).
PAGES = BC.PAGES  # page -> its tests file, repo-relative; boundary_check.py owns the list


def code_files(page):
    """-> the repo-relative files that a page's first `Code:` or `Source:`
    sentence names in backticks (ACCEPTS a-code-line on the page above).
    Raises BC.Unreadable when the page cannot be read or has no such line."""
    try:
        with open(page, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except (OSError, UnicodeDecodeError) as e:
        raise BC.Unreadable("%s: %s" % (page, e))
    start = next((i for i, ln in enumerate(lines) if re.match(r"(Code|Source):\s", ln)), None)
    if start is None:
        raise BC.Unreadable("%s: no `Code:` or `Source:` line, so the files it names cannot be read" % page)
    para = []
    for ln in lines[start:]:
        if not ln.strip():
            break
        para.append(ln.strip())
    tokens = []
    for i, part in enumerate(" ".join(para).split("`")):
        if i % 2:
            tokens.append(part.strip())
        elif re.search(r"\.(\s|$)", part):
            break  # the sentence ends at a `.` outside backticks
    isfile = lambda rel: os.path.isfile(os.path.join(ROOT, rel))
    full = [t for t in tokens if "/" in t and isfile(t)]
    dirs = list(dict.fromkeys(os.path.dirname(t) for t in full))
    ancestors = list(dict.fromkeys(a for d in dirs for a in
                                   ("/".join(d.split("/")[:n]) for n in range(len(d.split("/")), 0, -1))))
    out = set(full)
    for t in tokens:
        if t in out or not re.fullmatch(r"[\w./-]+\.\w+", t):
            continue
        for d in (ancestors if "/" in t else dirs):
            if isfile(d + "/" + t):
                out.add(os.path.normpath(d + "/" + t).replace(os.sep, "/"))
                break
    return out


# Danger: a tests file that never ends hangs `check` and every caller (ship_check,
# run_mutation, a publish); open-ended calls hung runs before (call_deadline_lint.py,
# CALL_DEADLINES_ENFORCE_130_OPEN_ENDED). The slowest tests file a page registers ran
# well under a minute on 2026-11-19 (14 of them in 109 s in one check). Past it: UNREADABLE.
TESTS_TIMEOUT_S = 600


def _run_tests(tests):
    """-> (exit code, last output line) of one tests file run from the root, or
    the cause string when it could not start or did not end in time."""
    try:
        r = subprocess.run([sys.executable, os.path.join(ROOT, tests)], cwd=ROOT, capture_output=True,
                           text=True, errors="replace", timeout=TESTS_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return "did not end within %d s (TESTS_TIMEOUT_S)" % TESTS_TIMEOUT_S
    except OSError as e:
        return "could not start: %s" % e
    tail = [ln for ln in (r.stdout + r.stderr).splitlines() if ln.strip()]
    return r.returncode, (tail[-1].strip() if tail else "no output")


# A mod's locked bars are the page of every file inside the mod (owner, by card
# 2026-11-19 evening, "Locked bars are the page"); the test table rows that
# decide a bar are its promise tests. Page: version 0.3.0 of the page above.
MOD_SRC = ("src", "RimMandrake")
INGAME_KINDS = ("live_minimal", "live_full", "look")   # run in the game; `check` reads no game run
MOD_CAUSES_SHOWN = 6   # causes named in one detail line; the counts carry the rest


def mod_of(rel):
    """-> the mod a repo-relative path lies inside (src/RimMandrake/<Mod>/... with
    design/concepts/<Mod>/), or None."""
    parts = rel.split("/")
    if len(parts) >= 4 and tuple(parts[:2]) == MOD_SRC and \
            os.path.isdir(os.path.join(ROOT, "design", "concepts", parts[2])):
        return parts[2]
    return None


def _mod_json(mod, name):
    """-> (obj, None), (None, "no file") or (None, cause) for design/concepts/<mod>/version/<name>."""
    p = os.path.join(ROOT, "design", "concepts", mod, "version", name)
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f), None
    except FileNotFoundError:
        return None, "no file"
    except (OSError, UnicodeDecodeError, ValueError) as e:
        return None, "version/%s cannot be read: %s" % (name, str(e))


def ingame_standing(mod, tt):
    """-> the ids of `tt`'s in-game checks whose last in-game run stands: a PASS that no change since has touched, read
    by the Stage 6 reader (maturation.ingame_to_run: the rows of every visit and every `live-row`, and
    rerun_relation) as the next visit would read them. Raises when the rows or the relation cannot be read."""
    import maturation as M  # noqa: E402  (rimflow/) the one reader of in-game runs; loaded only for a mod with one
    ns = M.visit_numbers(ROOT, mod)
    _to_run, counted = M.ingame_to_run(ROOT, mod, (max(ns) if ns else 0) + 1, tt)
    return set(counted)


def mod_page_state(mod, builds=None):
    """-> (state, detail) of the files inside `mod` against its locked bars (the
    mod promises on the page above). `builds` caches each test's build id."""
    import judge_certificate as JC  # noqa: E402  the build a recorded run is bound to (rimflow/)
    builds = {} if builds is None else builds
    head = "mod %s" % mod
    v, err = _mod_json(mod, "VERSION.json")
    if err == "no file":
        return "NO PAGE", "%s has no version/VERSION.json, so no locked bars" % head
    if err or not isinstance(v, dict):
        return "UNREADABLE", "%s: %s" % (head, err or "version/VERSION.json is not an object")
    ver, st = v.get("version"), str(v.get("state") or "")
    head = "mod %s %s" % (mod, ver)
    if not re.match(r"(locked|passed)\b", st):
        return "NO PAGE", "%s is not locked (state %r), so it has no locked bars" % (head, st)
    lb, err = _mod_json(mod, "locked_bars.json")
    if err == "no file":
        return "NO PAGE", ("%s is %s but has no version/locked_bars.json, so no locked bars "
                           "(`maturation.py lock-bars %s` records them)" % (head, st, mod))
    if err:
        return "UNREADABLE", "%s: %s" % (head, err)
    ids = lb.get("ids") if isinstance(lb, dict) else None
    if not isinstance(ids, list) or not ids or not all(isinstance(i, str) and i for i in ids) \
            or len(set(ids)) != len(ids):
        return "UNREADABLE", "%s: version/locked_bars.json holds no list of unique bar ids" % head
    if lb.get("version") != ver:
        return "UNREADABLE", "%s: version/locked_bars.json records version %s's bars" % (head, lb.get("version"))
    tt, err = _mod_json(mod, "test_table.json")
    if err == "no file":
        return "DIRTY", "%s: no version/test_table.json, so none of its %d locked bars has a test" % (head, len(ids))
    if err:
        return "UNREADABLE", "%s: %s" % (head, err)
    bars = tt.get("bars") if isinstance(tt, dict) else None
    tests = tt.get("tests") if isinstance(tt, dict) else None
    if not isinstance(bars, list) or not isinstance(tests, dict):
        return "UNREADABLE", "%s: version/test_table.json holds no bars list and tests map" % head
    if tt.get("version") != ver:
        return "UNREADABLE", "%s: version/test_table.json is version %s's table" % (head, tt.get("version"))
    rows = {b.get("id"): b for b in bars if isinstance(b, dict)}
    standing = []           # [] = not read yet; then [the set of standing in-game checks] or [the exception]
    count = {"green": 0, "DIRTY": 0, "UNRUN": 0, "STALE": 0, "UNREADABLE": 0}
    causes = []
    for bid in ids:
        b, bad = rows.get(bid), []    # bad: (kind, cause); kind DIRTY, UNRUN, STALE or UNREADABLE
        ds = b.get("decides") if isinstance(b, dict) else None
        if b is None:
            bad.append(("DIRTY", "bar %s is not in the test table" % bid))
        elif not isinstance(ds, list) or not ds:
            bad.append(("DIRTY", "bar %s decides on no test" % bid))
        for d in ds if b is not None and isinstance(ds, list) else []:
            t = tests.get(d)
            if not isinstance(t, dict):
                bad.append(("DIRTY", "bar %s's test %s is not in the table" % (bid, d)))
                continue
            if t.get("known_red"):
                bad.append(("DIRTY", "bar %s's test %s carries known_red %s" % (bid, d, t["known_red"])))
                continue
            if t.get("kind") == "look":
                bad.append(("UNRUN", "bar %s's test %s is his walk (look), and check reads no walk" % (bid, d)))
                continue
            if t.get("kind") in INGAME_KINDS:
                if not standing:
                    try:
                        standing.append(ingame_standing(mod, tt))
                    except Exception as e:  # noqa: BLE001  could not look is said, never green
                        standing.append(e)
                if isinstance(standing[0], Exception):
                    bad.append(("UNREADABLE", "bar %s's test %s runs in the game, and its in-game runs cannot be "
                                "read: %s: %s" % (bid, d, type(standing[0]).__name__, standing[0])))
                elif d not in standing[0]:
                    bad.append(("UNRUN", "bar %s's test %s runs in the game (%s), and no in-game PASS of it stands "
                                "(none recorded, or a change since touched it: maturation.ingame_to_run)"
                                % (bid, d, t.get("kind"))))
                continue
            if not t.get("command"):
                bad.append(("DIRTY", "bar %s's test %s runs offline and has no command" % (bid, d)))
                continue
            r = t.get("runs_today") if isinstance(t.get("runs_today"), dict) else {}
            if not r.get("ran"):
                bad.append(("UNRUN", "bar %s's test %s has no recorded run" % (bid, d)))
                continue
            if d not in builds:
                try:
                    builds[d] = JC.test_build(ROOT, t)
                except (OSError, UnicodeDecodeError) as e:
                    builds[d] = e
            if isinstance(builds[d], Exception):
                bad.append(("UNREADABLE", "bar %s's test %s: its build cannot be read: %s" % (bid, d, builds[d])))
            elif not r.get("build") or r["build"] != builds[d]:
                bad.append(("STALE", "bar %s's test %s ran on build %s, not this build %s (`maturation.py "
                            "certificate %s --run`)" % (bid, d, r.get("build") or "(none)", builds[d], mod)))
            elif r.get("command") is not None and r["command"] != t["command"]:
                bad.append(("STALE", "bar %s's test %s ran another command than the table's" % (bid, d)))
            elif not (r.get("rc") == 0 and r.get("result", "PASS") == "PASS"):
                bad.append(("DIRTY", "bar %s's test %s is red on this build (rc %s, %s)"
                            % (bid, d, r.get("rc"), r.get("result"))))
        kinds = [k for k, _c in bad]
        worst = next((k for k in ("DIRTY", "UNREADABLE", "STALE", "UNRUN") if k in kinds), "green")
        count[worst] += 1
        causes += [(k, c) for k, c in bad if k == worst][:1]
    tally = ", ".join(["bars green %d of %d" % (count["green"], len(ids))]
                      + ["%s %d" % (k, n) for k, n in count.items() if k != "green" and n])
    order = ("DIRTY", "UNREADABLE", "STALE", "UNRUN")
    shown = [c for _k, c in sorted(causes, key=lambda kc: order.index(kc[0]))]   # worst first, stable
    more = len(shown) - MOD_CAUSES_SHOWN
    detail = "%s locked bars: %s%s%s" % (head, tally, "; " if shown else "", "; ".join(shown[:MOD_CAUSES_SHOWN])
                                         + ("; +%d more" % more if more > 0 else ""))
    state = "DIRTY" if count["DIRTY"] else "UNREADABLE" if len(ids) - count["green"] else "CLEAN"
    return state, detail


def _with_mod(page_answer, mod_answer):
    """-> the worse of a file's page answer and its mod answer (a-mod-file-on-a-page-takes-the-worse)."""
    if mod_answer is None:
        return page_answer
    (ps, pd), (ms, md) = page_answer, mod_answer
    if ms == "NO PAGE":
        return (ps, pd) if ps != "NO PAGE" else (ps, "%s; %s" % (md, pd))
    if ps == "NO PAGE":
        return ms, md
    rank = ("DIRTY", "UNREADABLE", "CLEAN")
    return min((ps, ms), key=rank.index), "%s; %s" % (pd, md)


def page_states(rels):
    """-> [(state, rel, detail)], state CLEAN / DIRTY / UNREADABLE / NO PAGE,
    for repo-relative file paths (the promises on the page above)."""
    out = _boundary_states(rels)
    mods, builds = {}, {}
    for i, (state, rel, detail) in enumerate(out):
        mod = mod_of(rel)
        if mod is None:
            continue
        if mod not in mods:
            try:
                mods[mod] = mod_page_state(mod, builds)
            except ImportError as e:
                mods[mod] = ("UNREADABLE", "mod %s: the build reader judge_certificate cannot load: %s" % (mod, e))
        s, d = _with_mod((state, detail), mods[mod])
        out[i] = (s, rel, d)
    return out


def _boundary_states(rels):
    """-> [(state, rel, detail)] against the boundary pages alone."""
    named = {}
    for page in sorted(glob.glob(os.path.join(ROOT, "design", "specs", "*", "boundary.md"))):
        rel_page = os.path.relpath(page, ROOT).replace(os.sep, "/")
        try:
            named[rel_page] = code_files(page)
        except BC.Unreadable as e:
            named[rel_page] = e
    blind = ["%s" % v for v in named.values() if isinstance(v, BC.Unreadable)]
    runs, out = {}, []
    for rel in rels:
        mine = [p for p, v in named.items() if not isinstance(v, BC.Unreadable) and rel in v]
        if not mine:
            if blind:
                out.append(("UNREADABLE", rel, "no readable page names it, and whether these name it is unknown: "
                            + "; ".join(blind)))
            else:
                out.append(("NO PAGE", rel, "no design/specs/*/boundary.md names it in its Code: sentence"))
            continue
        dirty, unread, ok = [], [], []
        for page in mine:
            tests = PAGES.get(page)
            if not tests:
                unread.append("%s has no tests file registered in boundary_check.py PAGES" % page)
                continue
            try:
                names = BC.promises(os.path.join(ROOT, page))
                _have, ran = BC.tests_in(os.path.join(ROOT, tests))
            except BC.Unreadable as e:
                unread.append(str(e))
                continue
            if not names:
                dirty.append("%s lists no promise" % page)
                continue
            missing = [n for n in names if BC.test_name(n) not in ran]
            dirty += ["promise %s on %s has no test %s that main() runs in %s" % (n, page, BC.test_name(n), tests)
                      for n in missing]
            if missing:
                continue
            if tests not in runs:
                runs[tests] = _run_tests(tests)
            res = runs[tests]
            if isinstance(res, str):
                unread.append("tests file %s %s" % (tests, res))
            elif res[0] != 0:
                dirty.append("tests file %s exit %d (%s)" % (tests, res[0], res[1]))
            else:
                ok.append("%s: promises covered %d of %d, %s passes" % (page, len(names), len(names), tests))
        state = "DIRTY" if dirty else "UNREADABLE" if unread else "CLEAN"
        out.append((state, rel, "; ".join(dirty + unread + ok)))
    return out


#: exit code per answer, worst first (the-worst-answer-sets-the-exit)
CHECK_EXIT = (("DIRTY", 1), ("UNREADABLE", 3), ("UNREVIEWABLE", 3), ("NO PAGE", 4), ("CLEAN", 0))


def cmd_check(paths):
    """CLEAN / DIRTY / UNREADABLE / NO PAGE against the pages of promises."""
    rows, ask = [], []
    for p in paths:
        rel = repo_rel(p)
        if rel.startswith("../") or rel == "..":
            rows.append(("UNREVIEWABLE", p, "outside the repo root"))
        elif os.path.isdir(os.path.join(ROOT, rel)):
            rows.append(("UNREVIEWABLE", rel, "a directory, not a file"))
        elif proven_gone(rel):
            rows.append(("UNREVIEWABLE", rel, "no such file under the repo root"))
        else:
            ask.append(rel)
            rows.append(None)
    answers = iter(page_states(ask))
    rows = [r if r is not None else next(answers) for r in rows]
    for state, rel, detail in rows:
        print("%s  %s  (%s)" % (state, rel, detail))
    seen = {r[0] for r in rows}
    return next((code for state, code in CHECK_EXIT if state in seen), 0)


def cmd_check_record(paths):
    """`check --record`: the review record's answer (the meaning of `check`
    before 2026-11-19), for callers that track a review round."""
    data = load()
    rels = [repo_rel(p) for p in paths]
    # One batched spawn for every entry-less path (never one per path).
    missing = [r for r in rels
               if not (r.startswith("../") or r == "..")
               and data.get(r) is None
               and not os.path.isdir(os.path.join(ROOT, r))]
    canon, canon_certain = (canonical_rels(missing) if missing else ({}, True))
    # (check errs safe on canonicalization ignorance — no false CLEAN is
    # possible — but the never-marked reason gets an honesty caveat below.)
    any_dirty = False
    for p, rel in zip(paths, rels):
        # Answer honestly for paths that cannot be reviewed at all, instead
        # of a reassuring "DIRTY (never marked clean)" that is
        # indistinguishable from a real file awaiting review.
        if rel.startswith("../") or rel == "..":
            any_dirty = True
            print(f"UNREVIEWABLE  {p}  (outside the repo root)")
            continue
        if os.path.isdir(os.path.join(ROOT, rel)) and data.get(rel) is None:
            # With a recorded entry, fall through: clean_state answers
            # "path is now a directory", telling the operator a stale entry
            # exists for prune to drop — check and list must agree.
            any_dirty = True
            print(f"UNREVIEWABLE  {rel}  (a directory, not a file)")
            continue
        if data.get(rel) is None:
            rel = canon.get(rel, rel)
        if data.get(rel) is None and proven_gone(rel):
            # proven_gone, not isfile: an unreadable-but-existing path must
            # answer "never marked clean", never a false "no such file".
            any_dirty = True
            print(f"UNREVIEWABLE  {rel}  (no such file under the repo root)")
            continue
        state, detail = clean_state(rel, data.get(rel))
        if state == "DIRTY" and data.get(rel) is None and not canon_certain:
            detail += ("; NOTE git could not answer case canonicalization — "
                       "a mis-cased recorded spelling would also read this way")
        if state == "DIRTY":
            any_dirty = True
            print(f"DIRTY  {rel}  ({detail})")
        else:
            print(f"CLEAN  {rel}  ({detail})")
    return 1 if any_dirty else 0


def cmd_mark_clean(path, sha, reviewer=None, gpt_job=None):
    """reviewer: {"kind": "agent", seat, session, agent} when another agent did the review (the recorder's word);
    gpt_job: a gpt_consult job id whose receipt must show it answered on exactly these bytes. Neither: the recorder
    (this process, whoami()) is the reviewer. See review_identity.py."""
    rel = canonical_rel(repo_rel(path))
    if rel.startswith("../") or rel == "..":
        print(f"FAIL: {rel} is outside the repo root.", file=sys.stderr)
        return 2
    if not os.path.isfile(os.path.join(ROOT, rel)):
        print(f"FAIL: {rel} does not exist under the repo root.", file=sys.stderr)
        return 2
    try:
        flagged = flags().get(rel)
    except FlagsUnreadable as e:
        print(f"FAIL: could not read the flags, so whether {rel} is FLAGGED is unknown: {e}", file=sys.stderr)
        return 3
    if flagged:
        print(f"FAIL: {rel} is FLAGGED ({flagged.get('ts', '?')}: {flagged.get('why', '')}). Nobody reviews it "
              "again. Only the weekly examination ends a flag: code_review_status.py unflag <path> --why \"…\".",
              file=sys.stderr)
        return 2
    current_hash = file_hash(rel)
    if current_hash is None or current_hash is UNREADABLE:
        print(f"FAIL: could not read {rel} to hash it.", file=sys.stderr)
        return 2
    # A path git does not track has no commit to anchor a clean mark to.
    # Still enforced (policy, not a correctness need under hash-based
    # tracking): a clean mark should point at real, shippable, committed
    # content. `vendor/mod_sources/**` is ignored, and this tool's docstring
    # puts .cs mod source in scope.
    # :(literal) — a bare rel is a glob pathspec, and "a[b].xml" would match
    # tracked "ab.xml", letting an untracked file through this gate as CLEAN.
    tracked = git(["ls-files", "--error-unmatch", "--", ":(literal)" + rel])
    if tracked.returncode not in (0, 1):
        # A timeout/lock/missing-git failure must not wear the untracked
        # message — that told reviewers to `git add` already-tracked files.
        print(f"FAIL: git could not answer whether {rel} is tracked "
              f"({(tracked.stderr or '').strip() or 'index lock?'}). Try again.",
              file=sys.stderr)
        return 2
    if tracked.returncode == 1:
        print(f"FAIL: {rel} is not tracked by git — commit it first, or it can "
              "never be measured dirty again.", file=sys.stderr)
        return 2
    # Uncommitted changes to this exact file mean HEAD is not what will
    # actually ship — refuse rather than record a clean mark whose
    # informational sha doesn't reflect what was reviewed. `diff --quiet`
    # is scoped to one path and skips the untracked-file directory walk
    # `git status` does, so it's the cheaper of the two for this check.
    # Resolve HEAD ONCE and diff against that sha, not the symbolic HEAD:
    # with several windows committing into this checkout, a commit landing
    # between the diff and a later rev-parse would record a sha whose blob
    # is not the hashed bytes — exactly what the explicit --sha path refuses.
    head = git(["rev-parse", "--short", "HEAD"])
    head_sha = head.stdout.strip() if head.returncode == 0 and head.stdout.strip() else None
    diff = git(["diff", "--quiet", head_sha or "HEAD", "--", ":(literal)" + rel])
    if diff.returncode not in (0, 1):
        print(f"FAIL: git could not report status for {rel} (index lock? bad path?). Try again.", file=sys.stderr)
        return 2
    if diff.returncode == 1:
        print(f"FAIL: {rel} has uncommitted changes. Commit first, then mark-clean.", file=sys.stderr)
        return 2
    if sha is None:
        sha = head_sha or "unknown"
    else:
        # An unvalidated --sha is recorded verbatim. A typo poisons the entry
        # permanently: every later `check` says "recorded sha not found — log is
        # stale", which reads as a repo fault rather than a bad argument, and the
        # bogus mark still burned a cleanCount increment on the health board.
        r = git(["rev-parse", "--verify", "--short", "%s^{commit}" % sha])
        if r.returncode == -1:
            # A git failure must not wear the bad-argument message — that
            # sends a reviewer chasing a nonexistent typo.
            print(f"FAIL: git could not answer whether --sha {sha} resolves "
                  f"({(r.stderr or '').strip() or 'timeout/lock?'}). Try again.",
                  file=sys.stderr)
            return 2
        if r.returncode != 0 or not r.stdout.strip():
            print(f"FAIL: --sha {sha} does not resolve to a commit.", file=sys.stderr)
            return 2
        sha = r.stdout.strip()
        # And it must be an ancestor of HEAD. `git log <sha>..HEAD` is empty for
        # any sha HEAD can already reach FROM, so a mark against a commit ahead
        # of HEAD would read CLEAN no matter what HEAD's copy of the file says.
        anc = git(["merge-base", "--is-ancestor", sha, "HEAD"])
        if anc.returncode not in (0, 1):
            print(f"FAIL: git could not answer whether --sha {sha} is an "
                  f"ancestor ({(anc.stderr or '').strip() or 'timeout/lock?'}). "
                  "Try again.", file=sys.stderr)
            return 2
        if anc.returncode == 1:
            print(f"FAIL: --sha {sha} is not an ancestor of HEAD; a clean mark "
                  "there could never be measured dirty.", file=sys.stderr)
            return 2
        # And its copy of the file must BE the reviewed bytes: the recorded
        # hash is the worktree's content, so accepting an older sha whose
        # blob differs would point every later reader at a commit that does
        # not contain what was reviewed.
        blob = git_bytes(["show", "%s:%s" % (sha, rel)])
        if blob.returncode != 0:
            print(f"FAIL: git could not read {rel} at --sha {sha}.",
                  file=sys.stderr)
            return 2
        if hashlib.sha256(blob.stdout).hexdigest() != current_hash:
            print(f"FAIL: {rel} at --sha {sha} differs from the working tree — "
                  "the clean mark must name a commit whose bytes were reviewed.",
                  file=sys.stderr)
            return 2
    import review_identity as RI
    if gpt_job:
        receipt = RI.find_receipt(gpt_job)
        if not RI.receipt_covers(receipt, rel, current_hash):
            why = ("no verifiable receipt for that job" if receipt is None else
                   "the job did not answer" if not receipt.get("answered") else
                   "the job did not inline these bytes of %s" % rel)
            print(f"FAIL: --gpt-job {gpt_job}: {why} (receipts: {RI.receipts_path()}). Run gpt_consult on the "
                  "committed file, then mark it with the job id it prints.", file=sys.stderr)
            return 2
        reviewer = {"kind": "external", "tool": "gpt_consult", "job": gpt_job, "model": receipt.get("model")}
    review = RI.review_block(rel, current_hash, reviewer or {"kind": "self"})
    if "review_mac" not in review:
        print("WARN: no close-evidence key: the reviewer is recorded unsealed and reads 'unknown' to the Arbiter",
              file=sys.stderr)
    # sha/date below are informational display only — the hash is the real
    # clean/dirty mechanism, so a git failure here degrades the printout,
    # never the correctness of what gets recorded.
    date = "unknown"
    if sha != "unknown":
        r = git(["log", "-1", "--format=%ad", "--date=short", sha])
        if r.returncode == 0 and r.stdout.strip():
            date = r.stdout.strip()
    with locked():
        data = load()
        prior = data.get(rel) or {}
        # cleanCount: how many times THIS path has ever been marked clean. A
        # file already dirty again despite N prior clean marks is exactly the
        # "reviewed and it keeps coming back dirty" signal codebase_health.py
        # surfaces — see its's classify().
        clean_count = prior.get("cleanCount", 0) + 1
        data[rel] = dict({"hash": current_hash, "sha": sha, "date": date, "cleanCount": clean_count}, **review)
        save(data)
    print(f"CLEAN  {rel}  recorded at {sha} ({date})"
          + (f"  [clean mark #{clean_count}]" if clean_count > 1 else ""))
    return 0


def cmd_reopen(paths, reason):
    """Undo a clean mark: a fix is not a review. Finding a bug and fixing it
    means the file was DIRTY and someone edited it - it does not mean a
    full-file review found nothing, which is the only thing mark-clean is
    allowed to certify. `reopen` flips the entry's `status` to "dirty" so it
    must survive a genuine follow-up review (only minor comments at most)
    before mark-clean can be called on it again - but PRESERVES the entry
    (cleanCount and streak intact), per owner ruling 2026-09-04 (card,
    re-confirmed 2026-09-19): "PRESERVE HISTORY - reopen marks the entry
    dirty but keeps it, cleanCount and streak intact; schema gains a status
    field." `--reason` is required and goes to stdout / the caller's commit
    message, not into the ledger itself - git history is this repo's
    provenance, not a second copy of it here."""
    if not reason or not reason.strip():
        print("FAIL: --reason is required - say why this is being reopened.", file=sys.stderr)
        return 2
    # Validate every path BEFORE touching the log. Without this a typo prints
    # the reassuring "(already not clean)" and exits 0 while the file the
    # operator meant to retract stays marked CLEAN — a silent no-op in the one
    # command whose entire job is undoing a wrong clean mark.
    rels = []
    raws = [repo_rel(p) for p in paths]
    canon, certain = canonical_rels(raws)
    preview = load()   # unlocked peek, validation UX only — the locked
    # section below re-checks membership before mutating anything.
    if not certain and any(r not in preview for r in raws):
        # With git down, a mis-cased path would look up the wrong key and
        # print the reassuring "(already not clean)" rc 0 while the wrong
        # CLEAN mark stays live — the exact silent no-op this command
        # exists to prevent. Refuse rather than guess.
        print("FAIL: git could not answer path canonicalization "
              "(timeout/lock?) and a typed path is not an exact ledger key — "
              "cannot tell which entry you mean. Try again.", file=sys.stderr)
        return 2
    for path in paths:
        raw = repo_rel(path)
        # The typed spelling wins when IT holds the entry: canonicalizing
        # unconditionally made reopen retract a DIFFERENT key than asked and
        # exit 0 while the stale entry survived (case-rename phantom).
        rel = raw if raw in preview else canon[raw]
        if rel.startswith("../") or rel == "..":
            print(f"FAIL: {rel} is outside the repo root.", file=sys.stderr)
            return 2
        # A wrong clean mark on a since-deleted path must still be
        # retractable — only refuse paths that neither exist NOR have an
        # entry to retract.
        if not os.path.isfile(os.path.join(ROOT, rel)) and rel not in preview:
            print(f"FAIL: {rel} does not exist under the repo root and has "
                  "no entry to retract.", file=sys.stderr)
            return 2
        rels.append(rel)
    with locked():
        data = load()
        changed = []
        for rel in rels:
            if rel in data and data[rel].get("status") != "dirty":
                # Flip status in place - keep hash/sha/date/cleanCount so the
                # streak survives. codebase_health.review_verdicts() and
                # classify() only ever read this dict with .get(), so a
                # dirty-status stub (or one missing "hash" entirely) is safe
                # for both of them.
                data[rel]["status"] = "dirty"
                changed.append(rel)
        if changed:
            save(data)
    for rel in changed:
        print(f"REOPENED  {rel}  ({reason})")
    for rel in rels:
        if rel not in changed:
            print(f"(already not clean)  {rel}")
    return 0


def orphaned(rel):
    """The entry names no reviewable file: deleted, moved away, or left behind
    by a case-only rename. One predicate for prune's scan, prune's under-lock
    re-test AND list's tally — the scan and the re-test briefly disagreed and
    prune --apply printed "dropped" for a case-rename phantom while removing
    nothing (review 2026-09-09)."""
    return (proven_gone(rel)
            or not exact_case_isfile(rel))  # drvfs: a case-renamed spelling
                                            # "exists" but is a phantom


def orphan_reason(rel):
    ap = os.path.join(ROOT, rel)
    if os.path.isdir(ap):
        return "path is now a directory"
    if os.path.isfile(ap):
        return "case-renamed phantom — the bytes exist under another spelling"
    return "no longer exists on disk"


def cmd_prune(apply):
    """Drop entries whose path no longer exists on disk AT ALL - a file that was
    deleted or `git mv`'d to a new path with no entry ever written for the new
    path. Found 2026-09-05: three such orphans (two deleted score_*.py scripts,
    one file moved src/SPLIT_Phase3 -> src/RimUtinni) plus a whole 8-file block
    for a mod folder relocated wholesale (StickCuisine -> RimStarWars/Cuisine)
    sat in the ledger reading DIRTY forever, because nothing could ever mark a
    path CLEAN or re-review a path that isn't there to review. This is NOT the
    same question `check`/`list` answer (dirty vs clean); a missing path is
    neither - it is not reviewable at all, and its entry is pure noise.

    Deliberately narrow: only removes a path with ZERO bytes to hash (a real
    rename fix belongs at the NEW path via mark-clean, not here) - it does not
    try to guess where content moved to.
    """
    _orphaned, _why = orphaned, orphan_reason

    data = load()
    orphans = [rel for rel in data if _orphaned(rel)]
    if not orphans:
        print("(nothing to prune - every recorded path still exists on disk)")
        return 0
    if not apply:
        for rel in sorted(orphans):
            print(f"would drop  {rel}  ({_why(rel)})")
        print(f"\n{len(orphans)} orphaned entr{'y' if len(orphans) == 1 else 'ies'} - re-run with --apply to remove.")
        return 0
    with locked():
        # Re-test under the lock against the fresh reload: a mark-clean that
        # landed between the unlocked scan above and here must not lose its
        # entry, and a path re-created meanwhile is no longer an orphan
        # (review finding 2026-09-06). The dir-listing cache may be stale by
        # now — re-derive it so the re-test answers from the live disk.
        _dir_cache.clear()
        data = load()
        removed = [rel for rel in orphans if rel in data and _orphaned(rel)]
        for rel in removed:
            data.pop(rel, None)
        save(data)
    # "dropped" is printed only for entries the locked section actually
    # removed — never from the unlocked scan's guess.
    for rel in sorted(removed):
        print(f"dropped  {rel}  ({_why(rel)})")
    print(f"\n{len(removed)} orphaned entr{'y' if len(removed) == 1 else 'ies'} removed.")
    return 0


# The three extensions CLAUDE.md's own docstring above names as in scope
# ("not a Python-only tool... .py tooling, .cs mod source, .xml Defs and
# Patches alike"). Scoped to src/ - "what the game actually loads" - not the
# whole repo (design docs, infrastructure/state's own JSON, etc. are not
# reviewable "code" in this sense).
UNTRACKED_SCAN_DIR = "src"
UNTRACKED_SCAN_EXTS = (".py", ".cs", ".xml")


def find_untracked(data):
    """-> sorted list of repo-relative paths under UNTRACKED_SCAN_DIR, of the
    scanned extensions, that are tracked by git but have NEVER been given an
    entry here at all.

    🔴 THIS IS A DIFFERENT QUESTION FROM DIRTY. `list`/`check` report DIRTY
    only for a path that already has an entry and no longer matches it -
    a path with NO entry at all does not appear there, and CLAUDE.md's own
    "no entry ... is DIRTY" rule means those files are dirty too, just
    invisible to a report that only ever iterates recorded entries. Found by
    the owner 2026-09-05, questioning a reported "0 DIRTY" that turned out to
    be true only for the ~917 paths ever entered here, out of 1,402 real
    .py/.cs/.xml files under src/ - the other ~485 were never tracked at all.
    """
    # -z (NUL-separated): the ONLY mode git never quotes in. quotePath=false
    # still C-quotes '"', '\\' and control chars, silently dropping such a
    # path from the census this instrument exists for.
    r = git(["ls-files", "-z", "--", UNTRACKED_SCAN_DIR])
    if r.returncode != 0:
        return None  # caller must not treat this as "no untracked files"
    tracked = [p for p in r.stdout.split("\0")
               if p and p.endswith(UNTRACKED_SCAN_EXTS)]
    return sorted(p for p in tracked if p not in data)


def cmd_list(show_untracked=False):
    data = load()
    tally = {"CLEAN": 0, "DIRTY": 0, "ORPHANED": 0, "FLAGGED": 0}
    try:
        flagged, flags_err = flags(), None
    except FlagsUnreadable as e:
        flagged, flags_err = {}, str(e)
        print(f"UNREADABLE  flags: {e} (FLAGGED files may read DIRTY below)")
    if not data:
        print("(empty — nothing has ever been marked clean)")
    else:
        for rel in sorted(data):
            entry = data[rel]
            if rel in flagged:
                # Not review debt: nobody reviews a FLAGGED file again (owner, by card 2026-11-19).
                tally["FLAGGED"] += 1
                print(f"{'FLAGGED':35s} {rel}  ({flagged[rel].get('ts', '?')}: {flagged[rel].get('why', '')})")
                continue
            state, detail = clean_state(rel, entry)
            # An entry naming no reviewable file is NOT dirty code: there is
            # nothing to review, and its remedy is `prune`, not reviewer time.
            # Folded together, 97 orphans made a 130-file backlog read as 227
            # (DETERMINISM_ASSESSMENT.md C7) — so they are counted apart, and
            # `orphaned()` is the same predicate prune drops on.
            if state == "CLEAN":
                label, bucket = state, "CLEAN"
            elif orphaned(rel):
                label, bucket = f"ORPHANED ({detail})", "ORPHANED"
            else:
                # The real reason, not a hardcoded one: "no recorded hash" and
                # "content changed" need different remedies.
                label, bucket = f"DIRTY ({detail})", "DIRTY"
            tally[bucket] += 1
            cc = entry.get("cleanCount", 1)
            streak = f"  [x{cc}]" if cc > 1 else ""
            print(f"{label:35s} {rel}  ({entry.get('sha', '?')}, {entry.get('date', '?')}){streak}")
    for rel in sorted(set(flagged) - set(data)):
        tally["FLAGGED"] += 1
        print(f"{'FLAGGED':35s} {rel}  ({flagged[rel].get('ts', '?')}: {flagged[rel].get('why', '')})")
    if show_untracked:
        untracked = find_untracked(data)
        if untracked is not None:
            untracked = [p for p in untracked if p not in flagged]
        print()
        if untracked is None:
            print("UNTRACKED scan skipped: git ls-files failed (timeout or not a git repo).")
        elif not untracked:
            print("UNTRACKED (never reviewed at all): none — every "
                  f"{'/'.join(UNTRACKED_SCAN_EXTS)} file under {UNTRACKED_SCAN_DIR}/ "
                  "has at least one entry here.")
        else:
            print(f"UNTRACKED (never reviewed at all) — {len(untracked)} file(s), "
                  "DIRTY by CLAUDE.md's own default, invisible to the report above "
                  "because no entry has ever been written for them:")
            for rel in untracked:
                print(f"  {rel}")
        if untracked:
            tally["NEVER ENTERED"] = len(untracked)
    if flags_err:
        tally["FLAGGED"] = "UNREADABLE"
    print("\nTALLY  " + "  ".join(f"{k} {v}" for k, v in tally.items()))
    print("  review debt is DIRTY + NEVER ENTERED. ORPHANED is not reviewable at "
          "all — its remedy is `prune`, and counting it as debt overstates the "
          "backlog (97 of 227 on 2026-09-17). FLAGGED is not review debt: nobody "
          "reviews it again, and the weekly examination reads `list --flagged`.")
    return 3 if flags_err else 0


def _batch_cat_file(specs):
    """Resolve many `sha:path` object specifiers in ONE `git cat-file --batch`
    call instead of one `git show` subprocess per entry — migrate-hashes is a
    one-time pass but was still doing a full git spawn per pre-rewrite entry.
    Returns {spec: bytes-or-None} (None means the object does not resolve).
    Binary-safe: reads exactly the declared byte count per object rather than
    splitting on newlines, so a PNG's own embedded newlines can't desync the
    parse."""
    if not specs:
        return {}
    stdin = ("\n".join(specs) + "\n").encode("utf-8", errors="surrogateescape")
    r = subprocess.run(["git", "cat-file", "--batch"], cwd=ROOT, input=stdin,
                        capture_output=True, timeout=GIT_TIMEOUT)
    out, results, pos = r.stdout, {}, 0
    for spec in specs:
        nl = out.index(b"\n", pos)
        header = out[pos:nl].decode("utf-8", errors="surrogateescape")
        pos = nl + 1
        parts = header.split(" ")
        if parts[-1] == "missing":
            results[spec] = None
            continue
        size = int(parts[-1])
        results[spec] = out[pos:pos + size]
        pos += size + 1  # the single trailing newline cat-file appends per object
    return results


def cmd_migrate_hashes():
    """One-time backfill for entries recorded before this rewrite (they have
    {sha, date, cleanCount} but no {hash}). For each, hash the file's
    content AS IT WAS AT THE RECORDED SHA — not the current working-tree
    copy, which may have already drifted since. Resolved via a single
    `git cat-file --batch` call for every entry at once (see
    `_batch_cat_file`), not a `git show` subprocess per entry. An entry whose
    sha no longer resolves is left without a hash, which `clean_state`
    correctly reads as DIRTY ("needs re-verification"), the same outcome the
    pre-rewrite tool gave for "recorded sha not found". Safe to run more than
    once: an entry that already has a hash is skipped, never re-derived."""
    data = load()
    todo = {rel: entry for rel, entry in data.items() if not entry.get("hash")}
    if not todo:
        print("Nothing to migrate — every entry already carries a hash.")
        return 0
    print(f"Migrating {len(todo)} entr{'y' if len(todo) == 1 else 'ies'} without a recorded hash...")
    migrated, unresolvable = 0, 0
    resolvable = {}
    for rel, entry in todo.items():
        sha = entry.get("sha")
        if not sha or sha == "unknown":
            unresolvable += 1
            continue
        resolvable[rel] = "%s:%s" % (sha, rel)
    blobs = _batch_cat_file(list(resolvable.values()))
    for rel, spec in resolvable.items():
        content = blobs.get(spec)
        if content is None:
            unresolvable += 1
            print(f"  UNRESOLVABLE  {rel}  (sha {todo[rel]['sha']} no longer resolves for this path — stays DIRTY until re-reviewed)")
            continue
        todo[rel]["hash"] = hashlib.sha256(content).hexdigest()
        migrated += 1
    if migrated:
        with locked():
            # Reload under the lock in case another writer landed a change
            # while this ran (a bulk migration is the one case here slow
            # enough for that to matter) — merge our new hashes into
            # whatever is current rather than clobbering it.
            fresh = load()
            for rel, entry in todo.items():
                if entry.get("hash") and rel in fresh and not fresh[rel].get("hash"):
                    fresh[rel]["hash"] = entry["hash"]
            save(fresh)
    print(f"Migrated {migrated}, left {unresolvable} unresolvable (will read DIRTY until re-reviewed).")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_check = sub.add_parser("check", help="CLEAN / DIRTY / UNREADABLE / NO PAGE against the pages of promises")
    p_check.add_argument("paths", nargs="+")
    p_check.add_argument("--record", action="store_true",
                         help="answer from the review record instead (a review round on these bytes, not CLEAN)")

    p_mark = sub.add_parser("mark-clean", help="record a path as reviewed clean at a commit")
    p_mark.add_argument("path")
    p_mark.add_argument("--sha", default=None, help="defaults to current HEAD")
    p_mark.add_argument("--gpt-job", help="the review was a gpt_consult job (its id, printed by gpt_consult): refused "
                                          "unless its receipt shows it answered on exactly these bytes")
    p_mark.add_argument("--reviewer-seat", help="another agent reviewed it: its seat (recorded as that agent's word)")
    p_mark.add_argument("--reviewer-session", help="with --reviewer-seat: the reviewing agent's session id")
    p_mark.add_argument("--reviewer-agent", help="with --reviewer-seat: the reviewing agent's name/id")

    p_reopen = sub.add_parser("reopen", help="undo a clean mark - a fix is not a review")
    p_reopen.add_argument("paths", nargs="+")
    p_reopen.add_argument("--reason", required=True, help="why this is being reopened")

    p_list = sub.add_parser("list", help="show every recorded entry and its current state")
    p_list.add_argument("--show-untracked", action="store_true",
                        help="also list src/*.py|.cs|.xml files with NO entry at all - "
                             "DIRTY by default but invisible to the recorded-entries report")
    p_list.add_argument("--flagged", action="store_true", help="only the FLAGGED files, each with its why")

    p_flag = sub.add_parser("flag", help="the one blind reread of a fix also fixed a significant finding: "
                                         "nobody reviews this file again")
    p_flag.add_argument("path")
    p_flag.add_argument("--why", required=True, help="what the reread found and fixed")
    p_unflag = sub.add_parser("unflag", help="the weekly examination ends a flag")
    p_unflag.add_argument("path")
    p_unflag.add_argument("--why", required=True, help="what the examination decided")
    sub.add_parser("migrate-hashes", help="one-time backfill of {hash} onto pre-rewrite entries")

    p_prune = sub.add_parser("prune", help="drop entries for paths deleted or moved with no new entry")
    p_prune.add_argument("--apply", action="store_true", help="without this, only reports what would be dropped")

    args = ap.parse_args()
    if args.cmd == "check":
        sys.exit(cmd_check_record(args.paths) if args.record else cmd_check(args.paths))
    elif args.cmd == "reopen":
        rc = cmd_reopen(args.paths, args.reason)
        sys.exit(rc)
    elif args.cmd == "mark-clean":
        if args.gpt_job and (args.reviewer_seat or args.reviewer_session or args.reviewer_agent):
            print("FAIL: --gpt-job names the reviewer; it cannot be combined with --reviewer-*", file=sys.stderr)
            sys.exit(2)
        if (args.reviewer_session or args.reviewer_agent) and not args.reviewer_seat:
            print("FAIL: --reviewer-session/--reviewer-agent need --reviewer-seat", file=sys.stderr)
            sys.exit(2)
        rv = ({"kind": "agent", "seat": args.reviewer_seat.strip().upper(), "session": args.reviewer_session,
               "agent": args.reviewer_agent} if args.reviewer_seat else None)
        rc = cmd_mark_clean(args.path, args.sha, reviewer=rv, gpt_job=args.gpt_job)
        sys.exit(rc)
    elif args.cmd == "list":
        sys.exit(cmd_list_flagged() if args.flagged else cmd_list(args.show_untracked))
    elif args.cmd == "flag":
        sys.exit(cmd_flag(args.path, args.why))
    elif args.cmd == "unflag":
        sys.exit(cmd_unflag(args.path, args.why))
    elif args.cmd == "migrate-hashes":
        rc = cmd_migrate_hashes()
        sys.exit(rc)
    elif args.cmd == "prune":
        rc = cmd_prune(args.apply)
        sys.exit(rc)


if __name__ == "__main__":
    main()
