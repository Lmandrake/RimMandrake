"""The files a proof run in the books clone leaves dirty (relentless.BOOKS_LEFT_IN_PLACE), when origin moved one of them.

level_books leaves them in place, but `reset --keep` refuses a dirty file origin changed: the registry moved twice in
three days, and each time the engine froze on old code until someone cleared it, the journal saying only "books cannot
level" (BOOKS_REGISTRY_UNSTICK_MOVED_FILE). So such a file is set aside for the reset and handed back after it:

- the modcheck registry is a record of real runs (status.py writes it, nothing regenerates it). Books' entries are put
  back by key over origin's: every key books changed or removed against HEAD, the later `ts` winning a key both sides
  changed. Flush then publishes it, so a run recorded in books reaches origin like any other.
- anything else left in place (Transient/, a validation_triplet_ report) is look-once output: origin's copy stands and
  books' is kept, byte for byte, in the level's books_dirt folder.

Everything happens under the registry's own lock (status.py's `modcheck_status.json.lock`, fcntl), so a WSL run that
records between the set-aside and the hand-back waits for it. A python.exe writer over 9p falls back to a mkdir lock
this cannot see: its save is an atomic os.replace, so the worst it does is replace the registry during a level, which
the hand-back below reads as origin's and merges over, or which a refused reset leaves for the next tick."""
import contextlib
import fcntl
import json
import os
import shutil
import subprocess
import time

REGISTRY = "infrastructure/state/modcheck_status.json"


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def moved_rows(books, rows, prefixes):
    """-> the (state, path) rows under `prefixes` whose path origin/main changed against HEAD (added, edited, deleted)."""
    left = [(s, p) for s, p in rows if p.startswith(prefixes)]
    if not left:
        return []
    r = subprocess.run(["git", "-C", books, "diff", "--name-only", "--no-renames", "-z", "HEAD", "origin/main", "--",
                        *sorted({p for _s, p in left})], capture_output=True, text=True, timeout=120,
                       stdin=subprocess.DEVNULL)
    if r.returncode:
        raise RuntimeError("git diff: %s" % r.stderr[-200:])
    moved = set(filter(None, r.stdout.split("\0")))
    return [(s, p) for s, p in left if p in moved]


@contextlib.contextmanager
def registry_locked(books):
    """status.py's own mutex: the lock file beside the registry, flocked EXCLUSIVE."""
    lock = os.path.join(books, REGISTRY + ".lock")
    os.makedirs(os.path.dirname(lock), exist_ok=True)
    fd = os.open(lock, os.O_WRONLY | os.O_CREAT, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


def _show(books, rev, p):
    r = subprocess.run(["git", "-C", books, "show", "%s:%s" % (rev, p)], capture_output=True, timeout=60,
                       stdin=subprocess.DEVNULL)
    return r.stdout if r.returncode == 0 else None


def _write(path, data):
    """None removes; bytes replace atomically (status.py's own way: tmp + os.replace)."""
    if data is None:
        if os.path.lexists(path):
            os.remove(path)
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = "%s.tmp.%d.%d" % (path, os.getpid(), time.time_ns())
    with open(tmp, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def set_aside(books, moved, keep, held):
    """Each moved left file: books' bytes copied into `keep`, HEAD's put in its place (or the file removed where HEAD
    has none), so the reset sees it clean. `held` gets {path: (books' bytes or None, HEAD's bytes or None)} before the
    file is touched, so a caller's put_back undoes a set-aside that stopped part way."""
    for _s, p in moved:
        src = os.path.join(books, p)
        mine = None
        if os.path.isfile(src):
            with open(src, "rb") as f:
                mine = f.read()
            os.makedirs(os.path.dirname(os.path.join(keep, p)), exist_ok=True)
            shutil.copy2(src, os.path.join(keep, p))
        head = _show(books, "HEAD", p)
        held[p] = (mine, head)
        _write(src, head)


def put_back(books, held):
    """The level did not happen: every set-aside file gets books' bytes again, as the run left them."""
    for p, (mine, _head) in held.items():
        _write(os.path.join(books, p), mine)


def _entries(raw):
    if raw is None:
        return {}
    got = json.loads(raw.decode("utf-8"))
    if not isinstance(got, dict):
        raise ValueError("not an object")
    return got


def _ts(e):
    t = e.get("ts") if isinstance(e, dict) else None
    return t if isinstance(t, (int, float)) else None


def _merge_entry(_b, m, t):
    """A key both sides changed: the side with the later run (`ts`, which only record_run stamps) stands whole, so a
    run's fields never mix with another run's, and a re-run supersedes a minor declared on the other side as
    record_run itself does. An owner review is never lost, though: status.py's record_run carries the review it found, so a re-run on
    one side drops a review recorded on the other unless it is carried here, the later review winning, and a run that
    waited on exactly that review is GREEN, as record_owner_review makes it. Books' side on a tie or an unreadable time."""
    lm, lt = _ts(m), _ts(t)
    win, lose = (m, t) if lt is None or (lm is not None and lm >= lt) else (t, m)
    if not (isinstance(win, dict) and isinstance(lose, dict)):
        return win
    out = dict(win)
    rw, rl = win.get("owner_review"), lose.get("owner_review")
    if rl and (not rw or (_ts(rl) is not None and (_ts(rw) is None or _ts(rl) > _ts(rw)))):
        out["owner_review"] = rl
        if out.get("status") == "PENDING-OWNER-REVIEW":
            out["status"] = "GREEN"
    return out


def merge_registry(base, mine, theirs):
    """-> (merged, carried keys). Books' change against HEAD, key by key, over origin's: a key books changed or removed
    takes books' value (or goes); a key origin changed too is merged by _merge_entry, and a key one side removed while
    the other changed it keeps the changed side's entry."""
    out = dict(theirs)
    carried = []
    for k in sorted(set(base) | set(mine)):
        if (k in base) == (k in mine) and base.get(k) == mine.get(k):
            continue        # books did not touch it
        if (k in theirs) != (k in base) or theirs.get(k) != base.get(k):     # origin touched it too
            if k not in mine:
                continue    # books removed it, origin changed or removed it: origin's stands
            if k not in theirs and k in base:
                got = mine[k]   # origin removed it, books re-ran it: the run stands
            else:
                got = _merge_entry(base.get(k), mine[k], theirs.get(k))
            if got == theirs.get(k):
                continue
            out[k] = got
        elif k in mine:
            out[k] = mine[k]
        else:
            out.pop(k, None)
        carried.append(k)
    return out, carried


def hand_back(books, held, keep, journal):
    """After the reset: the registry gets books' entries back over origin's; any other file keeps origin's copy, books'
    in `keep`. Each is journalled by path, so a reader sees what moved and where books' bytes are."""
    for p, (mine, head) in sorted(held.items(), key=lambda kv: kv[0] != REGISTRY):     # the registry first: a journal
        # write failing on a look-once file must not leave books' entries unmerged, with nothing left to retry them
        src = os.path.join(books, p)
        if p != REGISTRY:
            journal({"at": iso(time.time()), "do": "books_left_file_replaced", "path": p,
                     "kept": os.path.join(keep, p) if mine is not None else None})
            continue
        if mine is None:    # deleted in books: no run removes the registry, so there is nothing of books' to carry
            journal({"at": iso(time.time()), "do": "books_registry_carried", "path": p, "keys": [], "kept": None})
            continue
        try:
            with open(src, "rb") as f:
                there = f.read()
        except FileNotFoundError:
            there = None
        try:
            merged, carried = merge_registry(_entries(head), _entries(mine), _entries(there))
        except (ValueError, UnicodeDecodeError) as e:   # conflict markers, a torn write: origin's stands, books' is kept
            journal({"at": iso(time.time()), "do": "books_registry_unmergeable", "path": p, "why": str(e)[:200],
                     "kept": os.path.join(keep, p)})
            continue
        if carried:
            _write(src, (json.dumps(merged, indent=2, sort_keys=True) + "\n").encode("utf-8"))
        journal({"at": iso(time.time()), "do": "books_registry_carried", "path": p, "keys": carried,
                 "kept": os.path.join(keep, p)})
