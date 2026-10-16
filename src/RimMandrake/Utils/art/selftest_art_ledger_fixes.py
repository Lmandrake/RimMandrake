#!/usr/bin/env python3
"""selftest_art_ledger_fixes.py — the 2026-10-15 art-ledger review fixes, on a disposable fixture.

B  mod/rel spelling is canonicalised inside install() (alias map at read and write, history never rewritten);
   `art.py put` / `install --file` get bytes into the store with containment and symlink checks.
"""
from __future__ import annotations

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
    tmp = Path(tempfile.mkdtemp(prefix="art-ledger-fixes-"))
    os.environ["ARTSTORE"] = str(tmp / "store")
    os.environ["ART_LEDGER_DIR"] = str(tmp / "ledger")
    os.environ["ART_SRC_ROOT"] = str(tmp / "src")
    os.environ["ART_SEAT"] = "BUILD"
    (tmp / "ledger" / "events").mkdir(parents=True)
    (tmp / "ledger" / "mod_aliases.json").write_text(json.dumps({"aliases": {"SWBestiary": "src/RimStarWars/SWBestiary"}}))
    (tmp / "src" / "RimStarWars" / "SWBestiary" / "Textures").mkdir(parents=True)
    (tmp / "src" / "RimMandrake" / "FlowWorks" / "Textures").mkdir(parents=True)
    return tmp


def test_b(tmp):
    import artledger as L
    import art
    canon = "src/RimStarWars/SWBestiary"
    # read side: every historical spelling folds to one key
    for spelling in ("SWBestiary", "RimStarWars/SWBestiary", canon, canon + "/", "/home/mandrake/rm/bench/" + canon,
                     str(tmp / canon)):
        check(L.mod_key(spelling) == canon, f"mod_key({spelling!r}) -> {canon}")
    check(L.mod_key("RimMandrake/FlowWorks") == "src/RimMandrake/FlowWorks", "tier-relative spelling gets src/")
    check(L.rel_key("Textures/a/b.png") == "a/b.png" and L.rel_key("a\\b.png") == "a/b.png",
          "rel_key strips a leading Textures/ and backslashes")
    # write side: resolved on disk, contained
    for spelling in ("SWBestiary", "RimStarWars/SWBestiary", canon, str(tmp / canon), str(tmp / canon / "Textures")):
        try:
            got = L.canonical_mod(spelling)
        except L.Refused as e:
            got = f"REFUSED {e}"
        check(got == canon, f"canonical_mod({spelling!r}) -> {canon} (got {got})")
    check(L.canonical_mod("FlowWorks") == "src/RimMandrake/FlowWorks", "a bare name with no alias resolves by folder")
    check(refused(L.canonical_mod, "NoSuchMod") is not None, "an unknown mod is refused (it used to land at <repo>/<mod>/)")
    check(refused(L.canonical_mod, "src/../../etc") is not None, "traversal out of src/ is refused")
    check(refused(L.canonical_mod, "/home/mandrake/rm/bench/" + canon) is not None
          or not Path("/home/mandrake/rm/bench").exists(),
          "another clone's absolute path is refused at write")
    outside = Path(tempfile.mkdtemp(prefix="art-outside-"))
    (tmp / "src" / "RimMandrake" / "Escape").symlink_to(outside)
    check(refused(L.canonical_mod, "src/RimMandrake/Escape") is not None, "a symlinked mod folder pointing outside is refused")
    check(L.canonical_rel("Textures/Things/X/X_south.png") == "Things/X/X_south.png", "rel accepted with Textures/")
    check(refused(L.canonical_rel, "../x.png") is not None and refused(L.canonical_rel, "/abs.png") is not None,
          "rel with .. or absolute is refused")

    # install with the trap spellings lands at the canonical file and records the canonical key
    red = png((255, 0, 0, 255))
    sred = L.store_put_bytes(red)
    r = L.install("SWBestiary", "Textures/Things/Nuna/Nuna_south.png", sred, reason=WRITER)
    f = tmp / canon / "Textures" / "Things" / "Nuna" / "Nuna_south.png"
    check(r.get("status") == "installed" and f.is_file(), "install('SWBestiary', 'Textures/…') writes the canonical file")
    lv = [e for e in L.read_events() if e.get("type") == "live"]
    check(lv and lv[-1]["mod"] == canon and lv[-1]["rel"] == "Things/Nuna/Nuna_south.png",
          "the live event is keyed canonically")
    check(not (tmp / "SWBestiary").exists() and not (tmp / "src" / "SWBestiary").exists(),
          "nothing written at <repo>/SWBestiary")

    # historical phantom keys fold onto the canonical slot (no false SHADOWED, the guard finds them)
    L.append({"type": "live", "mod": "SWBestiary", "rel": "Things/Nuna/Nuna_south.png", "sha": sred, "prev": None,
              "reason": "backfill-observed", "ts": "2026-10-01T00:00:00-0700"})
    idx = L.Index()
    keys = [k for k in idx.live if k[1] == "Things/Nuna/Nuna_south.png"]
    check(keys == [(canon, "Things/Nuna/Nuna_south.png")], f"a phantom spelling folds into one slot (got {keys})")

    # put: a supported way to get bytes into the store
    good = tmp / "Transient" / "new.png"
    good.parent.mkdir()
    blue = png((0, 0, 255, 255))
    good.write_bytes(blue)
    check(L.put_file_checked(good) == L.sha256_bytes(blue) and L.store_has(L.sha256_bytes(blue)), "put stores a PNG in the clone")
    (outside / "o.png").write_bytes(png((1, 2, 3, 255)))
    check(refused(L.put_file_checked, outside / "o.png") is not None, "put refuses a file outside the clone")
    link = tmp / "Transient" / "link.png"
    link.symlink_to(good)
    check(refused(L.put_file_checked, link) is not None, "put refuses a symlink")
    (tmp / "Transient" / "x.png").write_bytes(b"not a png")
    check(refused(L.put_file_checked, tmp / "Transient" / "x.png") is not None, "put refuses a non-PNG")
    rc = art.main(["put", str(good)])
    check(rc == 0, "art.py put exits 0")
    green = tmp / "Transient" / "green.png"
    green.write_bytes(png((0, 255, 0, 255)))
    rc = art.main(["install", "RimStarWars/SWBestiary", "Things/Nuna/Nuna_east.png", "--file", str(green),
                   "--reason", WRITER])
    check(rc == 0 and (tmp / canon / "Textures" / "Things" / "Nuna" / "Nuna_east.png").read_bytes() == green.read_bytes(),
          "art.py install --file puts and installs in one command")
    rc = art.main(["install", canon, "Things/Nuna/Nuna_west.png", "--reason", WRITER])
    check(rc == 2, "install with neither <sha> nor --file is refused")


def main():
    sys.path.insert(0, str(HERE))
    tmp = fixture()
    test_b(tmp)
    print(f"\n{'FAIL' if FAILS else 'OK'}: {len(FAILS)} failure(s)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
