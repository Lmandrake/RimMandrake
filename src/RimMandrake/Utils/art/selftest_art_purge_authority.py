#!/usr/bin/env python3
"""selftest_art_purge_authority.py — `art.py purge` takes the owner's authority the way install does
(ART_PURGE_WIRE_BY_CARD_FLAG_MISSING, 2026-10-24).

The owner decided the CrystalMit purge by question card; `purge --release-keep` accepted only --owner-said, and a
card label is OUR text, so it may never go in `said`. Purge now takes one field per kind of authority, as rimflow
and `art.py install` do: --owner-said (his words -> `said`), --by-card (card pick -> `by_card`), --per-ruling (a
standing ruling cited by reference -> `per_ruling`), plus --why (the agent's reason; grants nothing). Checked on a
disposable fixture: each field lands on the purge event and on every keep release, never in the wrong field;
--why alone, an empty card and a quoted "ruling" are refused; the words route is unchanged.
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
CARD = "CrystalMit: purge the six kept pictures? → Purge all six"


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
    except TypeError as e:          # an unknown keyword before the feature exists counts as a failure, not a crash
        return f"TypeError: {e}"
    return None


def fixture():
    tmp = Path(tempfile.mkdtemp(prefix="art-purge-auth-"))
    os.environ["ARTSTORE"] = str(tmp / "store")
    os.environ["ART_LEDGER_DIR"] = str(tmp / "ledger")
    os.environ["ART_SRC_ROOT"] = str(tmp / "src")
    os.environ["ART_SEAT"] = "BUILD"
    (tmp / "ledger" / "events").mkdir(parents=True)
    (tmp / "src" / "RimStarWars" / "SWBestiary" / "Textures").mkdir(parents=True)
    return tmp


def run(argv):
    import art
    out, err = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = art.main(argv)
    except SystemExit as e:          # argparse refusal of an unknown flag
        rc = e.code
    return rc, out.getvalue() + err.getvalue()


def picture(L, color, name):
    sha = L.store_put_bytes(png(color))
    L.append({"type": "variant", "id": f"v-{name}", "sha": sha, "res": f"Things/{name}/{name}", "facing": "south",
              "kind": "render"})
    return sha


def keep(L, sha, name):
    L.append({"type": "ruling", "id": f"keep-{name}", "target": {"sha": sha}, "verdict": "keep", "by": "owner",
              "trust": "ruled", "via": "art install (owner words)", "said": "keep this one", "subject_key": ""})


def events_for(L, sha, typ):
    return [e for e in L.read_events() if e.get("type") == typ and (e.get("sha") == sha or
                                                                     (e.get("target") or {}).get("sha") == sha)]


def test_library():
    import artledger as L
    colors = iter([(i * 20, 10, 10, 255) for i in range(1, 12)])

    # no authority at all, or only the agent's reason: refused
    s0 = picture(L, next(colors), "none")
    check(refused(L.purge, s0) is not None, "purge with no authority is refused")
    check(refused(L.purge, s0, why="looks bad to me") is not None, "--why alone grants nothing: refused")
    check(refused(L.purge, s0, by_card="   ") is not None, "an empty card label is refused")
    check(refused(L.purge, s0, per_ruling="he said delete it") is not None,
          "a --per-ruling with spaces (a quote, not a reference) is refused")
    check(not L.Index().is_purged(s0) and L.store_has(s0), "…and nothing was purged by any refused call")

    # by card, unkept picture
    s1 = picture(L, next(colors), "card")
    m = refused(L.purge, s1, by_card=CARD, why="enact phase 2")
    check(m is None, f"purge --by-card succeeds ({m})")
    pe = events_for(L, s1, "purge")
    check(len(pe) == 1 and pe[0].get("by_card") == CARD and "said" not in pe[0] and pe[0].get("by") == "owner",
          "the purge event carries by_card, no `said` (a card label is not his words)")
    check(pe and pe[0].get("why") == "enact phase 2", "…and the agent's --why alongside")
    check(L.Index().is_purged(s1) and not L.store_has(s1), "…state purged, bytes gone")

    # by card, KEPT picture: refused without release_keep, then releases with it
    s2 = picture(L, next(colors), "kept")
    keep(L, s2, "kept")
    m = refused(L.purge, s2, by_card=CARD)
    check(m is not None and "keep" in m, "a kept picture still refuses a by-card purge without --release-keep")
    m = refused(L.purge, s2, by_card=CARD, release_keep=True)
    check(m is None, f"purge --by-card --release-keep releases the keep ({m})")
    rel = [e for e in events_for(L, s2, "ruling") if e.get("verdict") == "release"]
    check(len(rel) == 1 and rel[0].get("by_card") == CARD and "said" not in rel[0] and rel[0].get("releases") == "keep-kept",
          "the release ruling carries by_card, no `said`, and names the keep it releases")
    check(not L.Index().protected(s2), "…the keep is no longer active")

    # per ruling
    s3 = picture(L, next(colors), "per")
    m = refused(L.purge, s3, per_ruling="OWNER.jsonl:1729700000")
    pe = events_for(L, s3, "purge")
    check(m is None and pe and pe[0].get("per_ruling") == "OWNER.jsonl:1729700000" and "said" not in pe[0],
          "purge --per-ruling records per_ruling only")

    # words route unchanged
    s4 = picture(L, next(colors), "words")
    keep(L, s4, "words")
    L.purge(s4, owner_said="delete it", release_keep=True)
    pe = events_for(L, s4, "purge")
    rel = [e for e in events_for(L, s4, "ruling") if e.get("verdict") == "release"]
    check(pe and pe[0].get("said") == "delete it" and "by_card" not in pe[0], "owner-said purge records `said` as before")
    check(rel and rel[0].get("said") == "delete it", "…and on the release")


def test_cli():
    import artledger as L
    s5 = picture(L, (1, 200, 1, 255), "cli")
    keep(L, s5, "cli")
    rc, out = run(["purge", s5[:12], "--release-keep"])
    check(rc == 2, f"art.py purge with no authority is refused (rc={rc})")
    rc, out = run(["purge", s5[:12], "--why", "mine"])
    check(rc == 2, f"art.py purge --why alone is refused (rc={rc})")
    rc, out = run(["purge", s5[:12], "--by-card", CARD, "--release-keep", "--why", "enact cauldron phase 2"])
    check(rc == 0, f"art.py purge --by-card --release-keep succeeds (rc={rc}: {out.strip()[:160]})")
    pe = events_for(L, s5, "purge")
    check(pe and pe[0].get("by_card") == CARD and pe[0].get("why") == "enact cauldron phase 2",
          "CLI records by_card and why on the purge event")
    s6 = picture(L, (1, 1, 200, 255), "cliper")
    rc, out = run(["purge", s6[:12], "--per-ruling", "ART_PURGE_WIRE_BY_CARD_FLAG_MISSING"])
    check(rc == 0 and L.Index().is_purged(s6), f"art.py purge --per-ruling succeeds (rc={rc})")


def main():
    sys.path.insert(0, str(HERE))
    fixture()
    test_library()
    test_cli()
    print(f"\n{'FAIL' if FAILS else 'OK'}: {len(FAILS)} failure(s)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
