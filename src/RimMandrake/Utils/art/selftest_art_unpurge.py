#!/usr/bin/env python3
"""selftest_art_unpurge.py — `art.py unpurge`: the owner's newer words reverse an older purge (2026-10-15).

He purged a picture on one sheet and later said "accept all the art you showed me" over a sheet that showed it.
The ledger now records that as an append-only `unpurge` event; the fold takes the latest of purge/unpurge.
Checked on a disposable fixture: owner words required, history kept, the fold is causal across shards, a
re-purge works, a mechanical install of a once-purged picture stays refused, and the CLI/status/variants show it.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
from io import BytesIO
from pathlib import Path

HERE = Path(__file__).resolve().parent
FAILS = []
WRITER = "script:src/RimMandrake/Utils/art/art.py"


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def png(color):
    from PIL import Image
    b = BytesIO()
    Image.new("RGBA", (8, 8), color).save(b, "PNG")
    return b.getvalue()


def refused(fn, *a, **kw):
    import artledger as L
    try:
        fn(*a, **kw)
    except L.Refused as e:
        return str(e)
    return None


def fixture():
    tmp = Path(tempfile.mkdtemp(prefix="art-unpurge-"))
    os.environ["ARTSTORE"] = str(tmp / "store")
    os.environ["ART_LEDGER_DIR"] = str(tmp / "ledger")
    os.environ["ART_SRC_ROOT"] = str(tmp / "src")
    os.environ["ART_SEAT"] = "BUILD"
    (tmp / "ledger" / "events").mkdir(parents=True)
    (tmp / "src" / "RimStarWars" / "SWBestiary" / "Textures").mkdir(parents=True)
    return tmp


def run(argv):
    import art
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = art.main(argv)
    return rc, out.getvalue()


def test_unpurge(tmp):
    import artledger as L
    canon = "src/RimStarWars/SWBestiary"
    rel = "Things/Nuna/Nuna_south.png"
    red, blue = png((255, 0, 0, 255)), png((0, 0, 255, 255))
    sred, sblue = L.store_put_bytes(red), L.store_put_bytes(blue)
    L.append({"type": "variant", "id": "v-red", "sha": sred, "res": "Things/Nuna/Nuna", "facing": "south", "kind": "render"})

    check(refused(L.unpurge, sred, owner_said="bring it back") is not None, "unpurge of a never-purged picture is refused")
    L.purge(sred, owner_said="delete this one")
    idx = L.Index()
    check(idx.is_purged(sred) and not L.store_has(sred), "purge: state purged, bytes gone")
    check(refused(L.install, canon, rel, sred, owner_said="yes") is not None, "a purged picture cannot be installed, even on words")

    for words in ("", "   ", None):
        check(refused(L.unpurge, sred, owner_said=words) is not None, f"unpurge without his words ({words!r}) is refused")
    rc, out = run(["unpurge", sred[:12]])
    check(rc == 2 and "REFUSED" in out, "art.py unpurge without --owner-said is refused")
    check(L.Index().is_purged(sred), "…and the picture stays purged")

    rc, out = run(["unpurge", sred[:12], "--owner-said", "accept all the art you showed me"])
    check(rc == 0 and "no bytes in the store" in out, f"art.py unpurge on his words succeeds and notes the missing bytes ({out.strip()[:80]})")
    idx = L.Index()
    check(not idx.is_purged(sred) and sred in idx.unpurged and idx.was_purged(sred), "fold: latest is the unpurge")
    evs = [e for e in L.read_events() if e.get("sha") == sred and e["type"] in ("purge", "unpurge")]
    check([e["type"] for e in evs] == ["purge", "unpurge"], "history kept whole: the purge event is still there")
    un = evs[-1]
    check(un["said"] == "accept all the art you showed me" and un["by"] == "owner" and un["follows"] == evs[0]["id"],
          "the unpurge records his words and names the purge it reverses")
    check(refused(L.unpurge, sred, owner_said="again") is not None, "a second unpurge (nothing purged) is refused")
    check(not idx.protected(sred), "unpurge mints no keep")

    check("not in the art store" in (refused(L.install, canon, rel, sred, owner_said="accept") or ""),
          "install still needs the bytes back in the store")
    L.store_put_bytes(red)
    m = refused(L.install, canon, rel, sred, reason=WRITER)
    check(m is not None and "purged by the owner" in m, "a MECHANICAL install of a once-purged picture stays refused")
    check(refused(L.install, canon, rel, sred, reason="artpipe-collect") is not None, "…artpipe-collect too")
    r = L.install(canon, rel, sred, owner_said="accept all the art you showed me")
    check(r["status"] == "installed" and (tmp / canon / "Textures" / rel).read_bytes() == red,
          "install on his words after the unpurge writes the file")

    # status / variants show it
    rc, out = run(["variants", "Nuna"])
    check("unpurged by the owner 1" in out, f"art.py variants counts the unpurge ({out.strip()[:200]!r})")
    L.store_put_bytes(blue)
    L.append({"type": "variant", "id": "v-blue", "sha": sblue, "res": "Things/Nuna/Nuna", "facing": "south", "kind": "render"})
    L.purge(sblue, owner_said="no")
    L.unpurge(sblue, owner_said="yes after all")
    rc, out = run(["variants", "Nuna"])
    check("UNPURGED " + sblue[:12] in out, "art.py variants tags a not-live unpurged picture UNPURGED")

    # re-purge after an unpurge: a NEW event (not deduped by id) that wins
    L.purge(sblue, owner_said="no, really delete it")
    idx = L.Index()
    check(idx.is_purged(sblue) and sum(1 for e in idx.purge_history[sblue] if e["type"] == "purge") == 2,
          "a re-purge after an unpurge is recorded and wins")
    L.store_put_bytes(blue)
    L.unpurge(sblue, owner_said="fine, keep it")
    check(not L.Index().is_purged(sblue), "a second unpurge reverses the second purge")


def test_fold_order():
    """Shards fold one seat after another: the causal `follows` link decides, then ts; a tie stays purged."""
    import artledger as L
    s = "c" * 64
    P = {"type": "purge", "id": "p1", "sha": s, "ts": "2026-10-15T10:00:00-0700"}
    U = {"type": "unpurge", "id": "u1", "sha": s, "follows": "p1", "ts": "2026-10-15T09:00:00-0700"}   # skewed clock
    for order in ([P, U], [U, P]):
        idx = L.Index(events=[dict(e) for e in order])
        check(not idx.is_purged(s), f"fold {[e['type'] for e in order]}: the unpurge that follows its purge wins")
    P2 = {"type": "purge", "id": "p2", "sha": s, "follows": "u1", "ts": "2026-10-15T08:00:00-0700"}
    for order in ([P, U, P2], [P2, U, P], [U, P2, P]):
        idx = L.Index(events=[dict(e) for e in order])
        check(idx.is_purged(s), f"fold {[e['id'] for e in order]}: the re-purge that follows the unpurge wins")
    T = "2026-10-15T10:00:00-0700"
    for order in ([{"type": "purge", "id": "a", "sha": s, "ts": T}, {"type": "unpurge", "id": "b", "sha": s, "ts": T}],
                  [{"type": "unpurge", "id": "b", "sha": s, "ts": T}, {"type": "purge", "id": "a", "sha": s, "ts": T}]):
        check(L.Index(events=order).is_purged(s), "an unlinked tie goes to the purge (fail safe)")


def main():
    sys.path.insert(0, str(HERE))
    tmp = fixture()
    test_unpurge(tmp)
    test_fold_order()
    print(f"\n{'FAIL' if FAILS else 'OK'}: {len(FAILS)} failure(s)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
