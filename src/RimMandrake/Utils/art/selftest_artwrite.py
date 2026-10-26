#!/usr/bin/env python3
"""selftest_artwrite.py — TextureWriter, the script-side route into Textures/, on a fixture only.

Proves: copy/save/put install through the ledger (live event, reason script:<caller>); an
unchanged re-run is a no-op; an owner-kept picture is left in place and counted, never
overwritten or retired; sync() retires (archives + removes) PNGs a run did not write;
a non-PNG file is copied plainly.
"""
from __future__ import annotations

# selftest temp containment (wave 7, DIRTY_CODE_REVIEW_STANDING_LOOP_1): every mkdtemp/mkstemp below,
# and every child process via TMPDIR, lands in one private dir removed at exit — this
# test used to leave its temp dirs behind in the seat TMPDIR on every run.
import atexit as _st_atexit, os as _st_os, shutil as _st_shutil, tempfile as _st_tempfile  # noqa: E401
_st_tempfile.tempdir = _st_os.environ["TMPDIR"] = _st_tempfile.mkdtemp(prefix="st_selftest_artwrite_")
_st_atexit.register(_st_shutil.rmtree, _st_tempfile.tempdir, True)
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
    tmp = Path(tempfile.mkdtemp(prefix="artwrite-selftest-"))
    os.environ["ARTSTORE"] = str(tmp / "store")
    os.environ["ART_LEDGER_DIR"] = str(tmp / "ledger")
    os.environ["ART_SEAT"] = "BUILD"          # art ledger refuses to guess a seat
    os.environ["ART_SRC_ROOT"] = str(tmp / "src")
    sys.path.insert(0, str(HERE))
    import artledger as L
    from artwrite import TextureWriter
    from PIL import Image

    tex = tmp / "src" / "Fix" / "Textures" / "A"
    red, blue = png((255, 0, 0, 255)), png((0, 0, 255, 255))
    # the ledger now refuses a mod that is not a real folder (Textures/ or About/About.xml): make src/Fix one
    (tmp / "src" / "Fix" / "Textures").mkdir(parents=True)
    srcf = tmp / "red.png"
    srcf.write_bytes(red)

    tw = TextureWriter(__file__)
    check(tw.reason.startswith("script:") and tw.reason.endswith("selftest_artwrite.py"), "reason names the calling script")
    tw.copy(srcf, tex / "One_south.png")
    tw.save(Image.new("RGBA", (4, 4), (0, 255, 0, 255)), tex / "Two.png")
    tw.put(b"not a png", tex / "Three.dds")
    idx = L.Index()
    ev = idx.live.get(("src/Fix", "A/One_south.png"), {})
    check(ev.get("sha") == L.sha256_bytes(red) and ev.get("reason") == tw.reason, "copy installs via the ledger")
    check(("src/Fix", "A/Two.png") in idx.live, "save installs via the ledger")
    check((tex / "Three.dds").read_bytes() == b"not a png" and tw.counts["plain"] == 1, "non-PNG copied plainly")
    check(tw.counts["installed"] == 2, "counts installs")
    tw.save(Image.new("RGB", (4, 4)), tmp / "preview" / "sheet.png", optimize=True)
    tw.save(Image.new("RGB", (4, 4)), tmp / "preview" / "bg.jpg", "JPEG", quality=90)
    check((tmp / "preview" / "sheet.png").is_file() and (tmp / "preview" / "bg.jpg").is_file()
          and tw.counts["installed"] == 2, "a non-Textures path is written plainly (sheet, JPEG)")
    check(not tw.put(red, "/elsewhere/Mod/Textures/X.png") and tw.counts["kept"] == 1,
          "a PNG aimed at another repo's Textures/ is refused")

    tw2 = TextureWriter(__file__)
    tw2.copy(srcf, tex / "One_south.png")
    check(tw2.counts["unchanged"] == 1 and tw2.counts["installed"] == 0, "unchanged re-run is a no-op")

    # owner keeps One_south: a regenerated picture must not replace it, nor sync retire it
    L.append({"type": "ruling", "id": "k", "target": {"sha": L.sha256_bytes(red)}, "verdict": "keep",
              "by": "owner", "trust": "ruled"})
    tw3 = TextureWriter(__file__)
    ok = tw3.put(blue, tex / "One_south.png")
    check(not ok and (tex / "One_south.png").read_bytes() == red and tw3.counts["kept"] == 1,
          "owner-kept picture left in place")
    n = tw3.sync(tex)
    check((tex / "One_south.png").is_file(), "sync never retires an owner-kept picture it was refused on")
    check(not (tex / "Two.png").exists() and n == 1, "sync retires PNGs the run did not write")
    check(not (tex / "Three.dds").exists(), "sync removes a non-PNG the run did not write (rmtree-then-regenerate)")
    check(L.store_has(idx.live[("src/Fix", "A/Two.png")]["sha"]), "retired picture is archived")
    check(("src/Fix", "A/Two.png") not in L.Index().live, "retire recorded (no longer live)")
    check(tw3.report() == 1, "report returns the refusal count")
    check((tmp / "preview" / "sheet.png").is_file(), "sync stays inside the dir it was given")

    # wave 11: a RELATIVE dest is cwd-relative (as the img.save it replaces). From a mod folder,
    # "Textures/A/Rel.png" used to be read against the clone root by locate(), match no
    # src/**/Textures/, and be written PLAINLY past the ledger; a relative sync() root retired nothing.
    old_cwd = os.getcwd()
    os.chdir(tmp / "src" / "Fix")
    try:
        tw4 = TextureWriter(__file__)
        tw4.save(Image.new("RGBA", (4, 4), (9, 9, 9, 255)), "Textures/A/Rel.png")
        check(("src/Fix", "A/Rel.png") in L.Index().live and tw4.counts["plain"] == 0
              and tw4.counts["installed"] == 1, "a cwd-relative Textures PNG goes through the ledger, not plainly")
        (tex / "Stray.png").write_bytes(blue)
        L.append({"type": "live", "mod": "src/Fix", "rel": "A/Stray.png", "sha": L.store_put_bytes(blue),
                  "prev": None, "reason": "fixture"})
        n4 = tw4.sync("Textures/A")
        # exact: Stray is the only retirable PNG; One_south is owner-kept and this writer never touched it
        check(not (tex / "Stray.png").exists() and n4 == 1, "sync with a cwd-relative root retires what the run did not write")
        check((tex / "One_south.png").read_bytes() == red and tw4.counts["kept"] == 1,
              "sync by a writer that never touched an owner-kept picture still leaves it (refused, counted kept)")
        check((tex / "Rel.png").is_file(), "sync keeps what the run wrote via a relative path")
    finally:
        os.chdir(old_cwd)

    print("\nALL PASS" if not FAILS else f"\n{len(FAILS)} FAIL")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
