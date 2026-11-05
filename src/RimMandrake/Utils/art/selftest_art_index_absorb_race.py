#!/usr/bin/env python3
"""selftest_art_index_absorb_race.py — ART_INDEX_CACHE_FIX_ABSORB_RACE.

artledger._absorb used to re-sign the cached Index with _shard_sig() AFTER its own flush, so a line another process
appended between cached_index() and that flush was signed over and never read: a keep/purge written concurrently was
invisible to later install guards in a long-running port script. Now each flush records its shard's size before and
after under the lock, and _absorb folds only when the shards read exactly as the cached signature plus our own bytes;
anything else drops the cache so the next cached_index() rebuilds.

  1  a clean own-append folds into the SAME Index object (no rebuild) and is signed
  2  a foreign append to ANOTHER seat's shard in the window is seen by the next cached_index()
  3  a foreign append to OUR OWN shard in the window is seen too
  4  a bare append() elsewhere in the process (bytes not in `evs`) is not signed over
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TMP = Path(tempfile.mkdtemp(prefix="st_art_absorb_race_"))
os.environ["ARTSTORE"] = str(TMP / "store")
os.environ["ART_LEDGER_DIR"] = str(TMP / "ledger")
os.environ["ART_SRC_ROOT"] = str(TMP / "src")
os.environ["ART_SEAT"] = "BUILD"
(TMP / "ledger" / "events").mkdir(parents=True)
sys.path.insert(0, str(HERE))
import artledger as L  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def ids():
    return {e["id"] for e in L.cached_index().events}


def own(n, between=None):
    idx = L.cached_index()
    w = L.Writer({e["id"] for e in idx.events})
    ev = {"type": "note", "id": f"own{n}", "text": "mine"}
    w.add(ev)
    if between:
        between()                                # the race window: after cached_index(), before our flush
    added = list(w.buf)
    w.flush()
    L._absorb(added)
    return ev["id"]


def foreign(shard, n):
    # another process's append, written the way Writer.flush writes it
    line = json.dumps({"type": "note", "id": f"foreign{n}", "seat": "OTHER", "ts": L.now()},
                      sort_keys=True, separators=(",", ":")) + "\n"
    with open(TMP / "ledger" / "events" / shard, "a", encoding="utf-8") as fh:
        fh.write(line)
    return f"foreign{n}"


def main():
    try:
        own(0)                                   # create our shard
        first = L.cached_index()
        i1 = own(1)
        check(L.cached_index() is first and i1 in ids(), "1 clean own-append folds into the cached Index, no rebuild")

        own(2, lambda: foreign("OTHER.jsonl", 2))
        f2 = "foreign2"
        check(f2 in ids(), "2 a foreign append to another shard in the window is visible to the next cached_index()")

        own(3, lambda: foreign("BUILD.jsonl", 3))
        f3 = "foreign3"
        check(f3 in ids(), "3 a foreign append to our own shard in the window is visible too")

        own(4, lambda: L.append({"type": "note", "id": "bare4", "text": "unabsorbed"}))
        check("bare4" in ids(), "4 a bare append() (not in _absorb's evs) is not signed over")
    finally:
        shutil.rmtree(TMP, True)
    print("FAILED %d" % len(FAILS) if FAILS else "ALL OK")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
