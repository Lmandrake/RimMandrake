#!/usr/bin/env python3
"""selftest_artwrite.py — TextureWriter, the script-side route into Textures/, on a fixture only.

Proves: copy/save/put install through the ledger (live event, reason script:<caller>); an
unchanged re-run is a no-op; an owner-kept picture is left in place and counted, never
overwritten or retired; sync() retires (archives + removes) PNGs a run did not write;
a non-PNG file is copied plainly.
"""
from __future__ import annotations

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
    check(L.store_has(idx.live[("src/Fix", "A/Two.png")]["sha"]), "retired picture is archived")
    check(("src/Fix", "A/Two.png") not in L.Index().live, "retire recorded (no longer live)")
    check(tw3.report() == 1, "report returns the refusal count")
    check((tmp / "preview" / "sheet.png").is_file(), "sync stays inside the dir it was given")

    print("\nALL PASS" if not FAILS else f"\n{len(FAILS)} FAIL")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
