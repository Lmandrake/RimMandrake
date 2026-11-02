#!/usr/bin/env python3
"""selftest_move_mod_textures.py — move_mod_textures.py on a fixture art ledger only.

Proves: a PNG whose copy lands at the new path is retired at the old one; a PNG whose copy the
new path REFUSES (an owner-kept picture already sits there) stays at the old path instead of
being retired — before 2026-10-26 sync() retired it anyway, so the move ended with the picture
in neither tree's live set; and --leave-kept on the same fixture does not crash.
"""
from __future__ import annotations

import atexit as _st_atexit, os as _st_os, shutil as _st_shutil, tempfile as _st_tempfile  # noqa: E401
_st_tempfile.tempdir = _st_os.environ["TMPDIR"] = _st_tempfile.mkdtemp(prefix="st_selftest_move_mod_textures_")
_st_atexit.register(_st_shutil.rmtree, _st_tempfile.tempdir, True)
import contextlib
import io
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def png(color):
    from PIL import Image
    b = io.BytesIO()
    Image.new("RGBA", (8, 8), color).save(b, "PNG")
    return b.getvalue()


def main():
    tmp = Path(tempfile.mkdtemp(prefix="move-tex-selftest-"))
    os.environ["ARTSTORE"] = str(tmp / "store")
    os.environ["ART_LEDGER_DIR"] = str(tmp / "ledger")
    os.environ["ART_SEAT"] = "BUILD"
    os.environ["ART_SRC_ROOT"] = str(tmp / "src")
    sys.path.insert(0, str(HERE))
    import artledger as L
    import move_mod_textures as M

    red, green, blue = png((255, 0, 0, 255)), png((0, 255, 0, 255)), png((0, 0, 255, 255))
    old, new = tmp / "src" / "Old" / "Textures", tmp / "src" / "New" / "Textures"
    for d in (old / "A", new / "A"):
        d.mkdir(parents=True)
    for rel, data, mod, root in (("A/x.png", red, "src/Old", old), ("A/y.png", green, "src/Old", old),
                                 ("A/x.png", blue, "src/New", new)):
        (root / rel).write_bytes(data)
        L.append({"type": "live", "mod": mod, "rel": rel, "sha": L.store_put_bytes(data), "prev": None,
                  "reason": "fixture"})
    L.append({"type": "ruling", "id": "k", "target": {"sha": L.sha256_bytes(blue)}, "verdict": "keep",
              "by": "owner", "trust": "ruled"})

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        M.main([str(old), str(new)])
    out = buf.getvalue()
    live = L.Index().live
    check((new / "A" / "y.png").read_bytes() == green and ("src/New", "A/y.png") in live, "a landed PNG is live at the new path")
    check(not (old / "A" / "y.png").exists() and ("src/Old", "A/y.png") not in live, "a landed PNG is retired at the old path")
    check((new / "A" / "x.png").read_bytes() == blue, "the owner-kept picture at the new path is untouched")
    check((old / "A" / "x.png").is_file() and (old / "A" / "x.png").read_bytes() == red
          and ("src/Old", "A/x.png") in live, "a PNG whose copy was refused stays live at the old path")
    check("copy refused" in out, "the refused copy is reported")

    # --leave-kept on what is left: the refused copy must not crash the move halfway
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            M.main([str(old), str(new), "--leave-kept"])
        ok = True
    except Exception as e:  # noqa: BLE001
        ok = False
        print("raised:", type(e).__name__, e)
    check(ok and (old / "A" / "x.png").is_file(), "--leave-kept with a refused copy finishes and keeps the old PNG")

    # --only: a one-path rename inside one mod moves and retires that path, nothing else (STANDIN_PLANTS_RENAME_...)
    one = tmp / "src" / "One" / "Textures"
    (one / "P").mkdir(parents=True)
    for rel, data in (("P/AB_a.png", red), ("P/keep.png", green)):
        (one / rel).write_bytes(data)
        L.append({"type": "live", "mod": "src/One", "rel": rel, "sha": L.store_put_bytes(data), "prev": None,
                  "reason": "fixture"})
    with contextlib.redirect_stdout(io.StringIO()):
        M.main([str(one), str(one), "--only", "P/AB_a.png", "--rel-from", "P/AB_a.png", "--rel-to", "P/RM_a.png"])
    live = L.Index().live
    check((one / "P" / "RM_a.png").read_bytes() == red and ("src/One", "P/RM_a.png") in live
          and not (one / "P" / "AB_a.png").exists() and ("src/One", "P/AB_a.png") not in live,
          "--only renames the one path: live at the new name, retired at the old")
    check((one / "P" / "keep.png").is_file() and ("src/One", "P/keep.png") in live,
          "--only leaves every other picture of the tree live")
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            M.main([str(one), str(one)])
        refused = False
    except SystemExit:
        refused = True
    check(refused and (one / "P" / "keep.png").is_file(), "old == new without --only is refused (no self-sync)")

    print("\nALL PASS" if not FAILS else f"\n{len(FAILS)} FAIL")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
