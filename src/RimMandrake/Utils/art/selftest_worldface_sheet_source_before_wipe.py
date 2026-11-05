#!/usr/bin/env python3
"""Selftest for WORLDFACE_SHEET_FIX_WIPE_BEFORE_SOURCE: a sheet rebuild checks its source BEFORE wiping the page's pictures.

world_face_variants.build_sheet and world_water_variants.copy_images empty Transient/<stem>_img and refill it from
<out>/sheet. Run without a prior `gen` (no <out>/sheet, an empty one, or no stats.json) they must refuse and leave the
existing pictures alone. A positive pass (source present) must still replace the old pictures, so the test can see a wipe.
"""
import os, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import biome_worldfaces as BW            # noqa: E402
import world_face_variants as WF         # noqa: E402
import world_water_variants as WW        # noqa: E402

FAILS = []


def check(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond: FAILS.append(msg)


def refuses(fn):
    try:
        fn()
    except SystemExit as e:
        return e.code not in (0, None)
    except Exception:                    # the pre-fix code wiped first, then crashed on the missing source
        return False
    return False


def main():
    with tempfile.TemporaryDirectory() as repo:
        WF.REPO = BW.REPO = repo
        trans = os.path.join(repo, "Transient"); os.makedirs(trans)
        cases = {"no sheet dir": lambda out: None,
                 "empty sheet dir": lambda out: os.makedirs(os.path.join(out, "sheet")),
                 "no stats.json": lambda out: (os.makedirs(os.path.join(out, "sheet")),
                                                open(os.path.join(out, "sheet", "a.jpg"), "w").write("x"))}
        for name, setup in cases.items():
            for tool, stem, call in (("face build_sheet", WF.STEM, lambda o: WF.build_sheet(o)),
                                     ("water copy_images", "ww_test", lambda o: WW.copy_images(o, "ww_test"))):
                img = os.path.join(trans, stem + "_img"); os.makedirs(img, exist_ok=True)
                keep = os.path.join(img, "old_picture.jpg"); open(keep, "w").write("old")
                out = tempfile.mkdtemp(dir=repo); setup(out)
                check(refuses(lambda: call(out)), f"{tool}: {name} -> refused")
                check(os.path.exists(keep), f"{tool}: {name} -> existing picture untouched")
        # positive: a real source replaces the old pictures (the instrument can see a wipe)
        out = tempfile.mkdtemp(dir=repo); os.makedirs(os.path.join(out, "sheet"))
        open(os.path.join(out, "sheet", "new.jpg"), "w").write("n"); open(os.path.join(out, "stats.json"), "w").write("{}")
        img = os.path.join(trans, "ww_test_img"); open(os.path.join(img, "old_picture.jpg"), "w").write("old")
        WW.copy_images(out, "ww_test")
        check(sorted(os.listdir(img)) == ["ww_new.jpg"], f"water copy_images with a source -> old wiped, new copied ({sorted(os.listdir(img))})")
    if FAILS:
        print(f"FAIL: {len(FAILS)} check(s)"); sys.exit(1)
    print("PASS")


if __name__ == "__main__":
    main()
