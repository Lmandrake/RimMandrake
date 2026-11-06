#!/usr/bin/env python3
"""cause_book.py -- one repair item per alarm CAUSE (OPSWATCH_BUILD_ALARMS_KEYED_BY_CAUSE).

Owner, 2026-11-06: "Merging duplicate alarms just seems like common sense". ops_watch filed one item per alarm id, so
one cause read by several alarms (arena's removal, 1f0e666566: two red groups and the overdue chase on tests that no
longer exist) filed 9 items in 13 minutes, each built and checked on its own (lesson 20261106T070551Z, ~5.2M tokens).

The book is ops_watch's (ops_dir()/causes.json): {cause key: record}. The key is jam_classes.cause_key. A record:
  state       filing   its lead alarm's filing has begun (the name is saved before the spawn, like alarms.json)
              open     its repair item is on the ledger: every other alarm of the cause attaches to it, files nothing
              closed   its repair item closed: the next crossing of the cause begins a new record
  item        the repair item (a successor's new name once the filer renames it)
  aids        the alarms of this cause, the lead first; readings: the last READINGS_CAP attachments, said aloud
  dependents  {item: queued | blocked}: an alarm's own item filed before the book knew its cause. It is blocked on the
              repair (`rimflow block <dep> --kind item --on <repair> --until done`, WP-04's path), which lifts by itself
              when the repair closes.
Nothing here reads the ledger or spawns: ops_watch.run_alarms passes known_ids / open_ids in and files what it returns.

Every writer holds `locked(path)` from its load to its save (RELENTLESS_ROLE_LAUNCH_HARDEN_CAUSE_BOOK): ops_watch for
its whole alarm pass, role_launch's cause attach for one load-attach-save. An atomic replace kept the JSON whole but
not the update: a save from a stale load erased a reading or resurrected a closed record. A writer that cannot get the
lock in its wait raises Busy and keeps its update to retry; it never writes without the lock.
"""
import contextlib
import fcntl
import json
import os
import tempfile
import time
from datetime import datetime, timezone

LIVE = ("filing", "open")
READINGS_CAP = 20


def iso(t):
    return datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load(path):
    """-> {key: record}; a missing book is empty. An unreadable one raises ValueError: the caller holds filing."""
    try:
        with open(path, encoding="utf-8") as f:
            book = json.load(f)
    except FileNotFoundError:
        return {}
    if not isinstance(book, dict) or not all(isinstance(r, dict) for r in book.values()):
        raise ValueError("%s is not a JSON object of records" % path)
    return book


class Busy(Exception):
    """The book's lock stayed held past the caller's wait: nothing was read or written."""


def lock_path(path):
    return str(path) + ".lock"


@contextlib.contextmanager
def locked(path, wait_s=None, poll_s=0.05):
    """Hold the book's writer lock (an flock on <path>.lock) for a load..save span. wait_s None waits as long as it
    takes (ops_watch, the book's owner); a number raises Busy after that many seconds."""
    d = os.path.dirname(str(path)) or "."
    os.makedirs(d, exist_ok=True)
    with open(lock_path(path), "a") as lk:
        if wait_s is None:
            fcntl.flock(lk, fcntl.LOCK_EX)
        else:
            t0 = time.monotonic()
            while True:
                try:
                    fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    if time.monotonic() - t0 >= wait_s:
                        raise Busy("%s held for %.1f s" % (lock_path(path), wait_s))
                    time.sleep(poll_s)
        try:
            yield
        finally:
            fcntl.flock(lk, fcntl.LOCK_UN)


def save(path, book):
    d = os.path.dirname(str(path)) or "."
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".causes.", suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(book, f, indent=1, sort_keys=True)
    os.replace(tmp, str(path))


def live(book, key):
    """The cause's record while it is filing or open, else None."""
    rec = book.get(key)
    return rec if isinstance(rec, dict) and rec.get("state") in LIVE else None


def owner_of(book, item):
    """The live record whose repair item is `item`, as (key, record), else (None, None)."""
    for k, r in book.items():
        if r.get("state") in LIVE and r.get("item") == item:
            return k, r
    return None, None


def begin(book, key, aid, name, now):
    """The lead alarm's filing begins: the record is saved before the spawn, so a pass that dies mid-filing finds it."""
    book[key] = {"state": "filing", "item": name, "aids": [aid], "readings": [], "dependents": {},
                 "begun": iso(now), "opened": None, "closed_at": None, "closed_by": None}
    return book[key]


def attach(book, key, aid, said, now, own_item=None, open_ids=None):
    """Another alarm of a live cause: kept on the record, nothing filed. Its own item, if it has one still open and
    other than the repair, becomes a dependent to block (open_ids None: the ledger was not read, nothing is blocked). -> True when a new dependent was queued."""
    rec = live(book, key)
    if rec is None:
        raise KeyError("no live record for cause %s" % key)
    if aid not in rec["aids"]:
        rec["aids"].append(aid)
    rec["readings"] = (rec.get("readings") or [])[-(READINGS_CAP - 1):] + [{"t": iso(now), "aid": aid, "said": str(said or "")[:200]}]
    if own_item and own_item != rec["item"] and own_item in (open_ids or ()) \
            and own_item not in rec.setdefault("dependents", {}):
        rec["dependents"][own_item] = "queued"
        return True
    return False


def filed(book, key, name, now):
    """The lead filing landed (under `name`, a successor's when the filer renamed it). -> the old name."""
    rec = book.get(key)
    if not isinstance(rec, dict):
        return None
    old = rec.get("item")
    rec.update(state="open", item=name, opened=rec.get("opened") or iso(now))
    return old


def blocked(book, key, dep):
    rec = book.get(key)
    if isinstance(rec, dict) and dep in (rec.get("dependents") or {}):
        rec["dependents"][dep] = "blocked"


def queued_blocks(book):
    """-> [(key, dependent, repair)] owed a block edge: the record open (its repair is on the ledger) and the edge
    not yet written. A failed or deferred block stays queued, so every pass retries it."""
    return [(k, d, r["item"]) for k, r in sorted(book.items()) if r.get("state") == "open"
            for d, st in sorted((r.get("dependents") or {}).items()) if st == "queued"]


def reconcile(book, known_ids, open_ids, alarms, now):
    """Pass start. A record left in `filing` whose item the ledger knows completes (the pass that filed it died before
    saving: "completes on restart"); one whose lead alarm no longer files that name is dropped (cleared unfiled). An
    open record whose repair item closed closes with it. known_ids empty means the ledger was not read: nothing is
    judged. -> [log rows]."""
    out = []
    if not known_ids:
        return out
    for k in sorted(book):
        r = book[k]
        st = r.get("state")
        if st == "filing":
            if r.get("item") in known_ids and (open_ids is None or r["item"] in open_ids):   # a reopen of a
                # closed item is on the ledger before it is filed: it completes when the item is open again
                r.update(state="open", opened=r.get("opened") or iso(now))
                out.append({"event": "cause_completed_on_restart", "cause": k, "item": r["item"]})
            else:
                lead = alarms.get((r.get("aids") or [None])[0])
                if not (isinstance(lead, dict) and lead.get("name") == r.get("item") and lead.get("state") == "PENDING"):
                    out.append({"event": "cause_dropped_unfiled", "cause": k, "item": r.get("item")})
                    del book[k]
        elif st == "open" and open_ids is not None and r.get("item") not in open_ids:
            r.update(state="closed", closed_at=iso(now), closed_by="repair")
            out.append({"event": "cause_closed_with_repair", "cause": k, "item": r.get("item")})
    return out
