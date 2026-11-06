#!/usr/bin/env python3
"""selftest_art_purge_receipt_first.py — `artledger.purge` writes its purge event BEFORE it unlinks the store bytes
(ART_PURGE_FIX_BYTES_GONE_BEFORE_RECEIPT, 2026-11-06).

The old order unlinked the picture, then flushed the purge event: a crash between them lost the picture with no
purge record. Checked on a disposable fixture: a purge whose unlink crashes leaves the purge event on disk and the
bytes still in the store; a rerun dedups the event (one purge event) and finishes the deletion; a plain purge still
removes the bytes and records bytes_removed=True; a purge of a sha with no bytes records bytes_removed=False.
"""
from __future__ import annotations

import atexit
import os
import shutil
import sys
import tempfile
from io import BytesIO
from pathlib import Path

tempfile.tempdir = os.environ["TMPDIR"] = tempfile.mkdtemp(prefix="st_selftest_art_purge_receipt_first_")
atexit.register(shutil.rmtree, tempfile.tempdir, True)

HERE = Path(__file__).resolve().parent
FAILS = []
RULING = "CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM"


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def png(color):
    from PIL import Image
    b = BytesIO()
    Image.new("RGBA", (8, 8), color).save(b, "PNG")
    return b.getvalue()


def fixture():
    tmp = Path(tempfile.mkdtemp(prefix="art-purge-first-"))
    os.environ["ARTSTORE"] = str(tmp / "store")
    os.environ["ART_LEDGER_DIR"] = str(tmp / "ledger")
    os.environ["ART_SRC_ROOT"] = str(tmp / "src")
    os.environ["ART_SEAT"] = "BUILD"
    (tmp / "ledger" / "events").mkdir(parents=True)
    (tmp / "src" / "RimStarWars" / "SWBestiary" / "Textures").mkdir(parents=True)
    return tmp


def picture(L, color, name):
    sha = L.store_put_bytes(png(color))
    L.append({"type": "variant", "id": f"v-{name}", "sha": sha, "res": f"Things/{name}/{name}", "facing": "south",
              "kind": "render"})
    return sha


def purges(L, sha):
    return [e for e in L.read_events() if e.get("type") == "purge" and e.get("sha") == sha]


class Crash(Exception):
    pass


def main():
    fixture()
    sys.path.insert(0, str(HERE))
    import artledger as L
    auth = dict(per_ruling=RULING, why="selftest: Conductor instruction to purge the fixture picture")

    # 1. the unlink crashes: the purge must already be recorded, the bytes still present
    s1 = picture(L, (200, 20, 20, 255), "crash")
    target = L.store_path(s1)
    real_unlink = Path.unlink

    def crashing_unlink(self, *a, **kw):
        if Path(self) == target:
            raise Crash("simulated crash at unlink")
        return real_unlink(self, *a, **kw)

    Path.unlink = crashing_unlink
    try:
        try:
            L.purge(s1, **auth)
            crashed = False
        except Crash:
            crashed = True
    finally:
        Path.unlink = real_unlink
    check(crashed, "the simulated crash fired inside purge's store unlink")
    ev = purges(L, s1)
    check(len(ev) == 1, f"the purge event is on disk before the unlink (found {len(ev)})")
    check(L.store_has(s1), "the bytes are still in the store after the crash (nothing lost unrecorded)")
    check(L.Index().is_purged(s1), "the index reads the picture as purged after the crash")

    # 2. a rerun dedups the event and finishes the deletion
    r = L.purge(s1, **auth)
    check(not L.store_has(s1), "a rerun finishes the deletion")
    check(len(purges(L, s1)) == 1, "a rerun adds no second purge event")
    check(r["bytes_removed"] is True, "the rerun reports the bytes removed")

    # 3. the ordinary path
    s2 = picture(L, (20, 200, 20, 255), "plain")
    r = L.purge(s2, **auth)
    ev = purges(L, s2)
    check(not L.store_has(s2) and r["bytes_removed"] is True, "a plain purge removes the bytes")
    check(len(ev) == 1 and ev[0].get("bytes_removed") is True and ev[0].get("per_ruling") == RULING,
          "a plain purge records one event with bytes_removed=True and its authority")

    # 4. no bytes in the store: recorded, bytes_removed=False, no crash
    s3 = picture(L, (20, 20, 200, 255), "nobytes")
    L.store_path(s3).unlink()
    r = L.purge(s3, **auth)
    ev = purges(L, s3)
    check(r["bytes_removed"] is False and len(ev) == 1 and ev[0].get("bytes_removed") is False,
          "a purge with no stored bytes records bytes_removed=False")

    print(f"RESULT: {'FAIL' if FAILS else 'PASS'} ({len(FAILS)} failed)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
