#!/usr/bin/env python3
"""selftest_chat_review.py — the phone/chat art-question images: names sort and carry the plain subject, the scale
image is drawn at true scale with the human, and the facings strip shows every facing and folder variant."""
import sys
import tempfile
from io import BytesIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import chat_review as C  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def png(w, h, rgba=(200, 120, 40, 255)):
    from PIL import Image
    b = BytesIO()
    Image.new("RGBA", (w, h), rgba).save(b, "PNG")
    return b.getvalue()


def main():
    from PIL import Image
    check(C.slug("Black insect chitin") == "black_insect_chitin", "slug: plain subject, lower snake")
    check(C._wrap("a " * 100, 20) and all(len(x) <= 20 for x in C._wrap("a " * 100, 20)), "_wrap keeps lines short")
    size = {"status": "measured", "source": "fixture", "kind": "animal", "drawSize": [2.0, 2.0], "cells": 2.0}
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        q = {"def": "RM_Fixture", "label": "fixture beast", "tex": "Things/Fixture", "size": size,
             "cand": {"south": png(256, 256), "east": png(256, 256)}, "candLabel": "candidate — render fx_v1",
             "inst": ("installed now — Fixture Mod", {"east": png(128, 128, (90, 90, 90, 255))})}
        C.scale_image(q, td / "s.png")
        im = Image.open(td / "s.png")
        check(im.width >= 900 and im.height > 2 * 128, f"scale image holds candidate and installed panels ({im.size})")
        sc = C.ruled_scene(C._img(png(256, 256)), size, 128, "t")
        check(sc.width > 128 * 3, "ruled scene: human | subject at 128 px/cell plus the ruler margin")
        C.facings_image([("cand", q["cand"]), ("inst", {"AA_x_a": png(64, 64), "AA_x_b": png(64, 64)})], "t", td / "f.png")
        f = Image.open(td / "f.png")
        check(f.width >= 4 * C.TILE,
              "facings strip: south, east and both folder variants each get a column")
    check(C._main_face({"north": 1, "east": 1}, size) == "east", "an animal's main face is its side view")
    check(C._main_face({"north": 1, "south": 1}, {"kind": "thing"}) == "south", "a thing's main face is south")
    print(f"{'FAIL' if FAILS else 'PASS'} selftest_chat_review ({len(FAILS)} failed)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
