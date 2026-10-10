#!/usr/bin/env python3
# selftest-timeout: 300
"""selftest_texture_gap_lint.py — a texPath that resolves to no loadable picture is caught, and the real repo's gaps are all listed.

Part 1, synthetic: an index where one path is shipped by an ACTIVE mod, one only by an INACTIVE mod, one by the base-game
bundle, one nowhere; src resolves a Graphic_Random folder and a Graphic_Multi file and ignores masks. The planted defects
(inactive-only, nowhere) must be flagged, every good path must not be; lint() fails an unlisted gap, a stale entry, an entry
added after the freeze.
Part 2, the REAL repo (skipped as UNMEASURED without the gametex cache): the lint passes, and SANITY PROBE: a texPath known to
resolve in src is OK_SRC and the known-owed RM_Ismerrow is a gap, so the scan is demonstrably looking.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import texture_gap_lint as T  # noqa: E402

FAILS = []


def check(cond, msg, detail=""):
    print(("PASS " if cond else "FAIL ") + msg + ("" if cond else f"  [{str(detail)[:500]}]"))
    if not cond:
        FAILS.append(msg)


def main() -> int:
    from PIL import Image
    d = Path(tempfile.mkdtemp(prefix="tgl_"))
    root = d / "Textures"
    for rel in ("Things/Plant/RM_Rand/a.png", "Things/Plant/RM_Rand/b.png", "Things/Plant/RM_Rand/am.png",
                "Things/Pawn/RM_Y/RM_Y_south.png", "Things/Item/RM_Z.png"):
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGBA", (4, 4), (1, 2, 3, 255)).save(p)
    ix = T.Index({"mods": [{"dir": "/act", "load_index": 5}, {"dir": "/off", "load_index": -1}],
                  "files": {"donor/active/art": [[0, 1, "single", "/act/x.png"]],
                            "donor/inactive/art": [[1, 1, "single", "/off/x.png"]]},
                  "bundle_files": {"name:cloth_a": [], "things/item/resource/steel": []}})
    T._DISK = []                                   # no disk fallback in the synthetic part
    paths = {"Things/Plant/RM_Rand": ["a.xml"], "Things/Pawn/RM_Y/RM_Y": ["a.xml"], "Things/Item/RM_Z": ["a.xml"],
             "donor/active/art": ["a.xml"], "Things/Item/Resource/Steel": ["a.xml"], "Things/Item/Resource/Cloth": ["a.xml"],
             "UI/Icons/Q": ["a.xml"], "donor/inactive/art": ["p.xml"], "Things/Plant/RM_Nowhere": ["b.xml"]}
    got = T.census(paths, [root], ix)
    cls = {k: v["class"] for k, v in got.items()}
    for good in ("Things/Plant/RM_Rand", "Things/Pawn/RM_Y/RM_Y", "Things/Item/RM_Z", "UI/Icons/Q"):
        check(cls[good] == "OK_SRC", f"src resolves {good}", cls[good])
    for good in ("donor/active/art", "Things/Item/Resource/Steel", "Things/Item/Resource/Cloth"):
        check(cls[good] == "OK_ACTIVE", f"active donor / bundle resolves {good}", cls[good])
    check(cls["donor/inactive/art"] == "MISSING", "PLANTED: a path only an inactive mod ships is a gap (disk list empty -> MISSING)", cls)
    check(cls["Things/Plant/RM_Nowhere"] == "MISSING", "PLANTED: a path nowhere is a gap", cls)
    check(T.census({"Things/Plant/RM_Nowhere": ["b.xml"]}, [root], None)["Things/Plant/RM_Nowhere"]["class"] == "UNMEASURED",
          "no index -> UNMEASURED, never MISSING")

    ok = {"frozen": "2026-10-10", "entries": [{"texPath": t, "owed": "x", "added": "2026-10-10"}
                                             for t in ("donor/inactive/art", "Things/Plant/RM_Nowhere")]}
    check(T.lint(got, ok) == [], "listed gaps pass")
    check(any("TEXTURE GAP" in x for x in T.lint(got, {"frozen": "2026-10-10", "entries": []})), "an unlisted gap fails")
    check(any("STALE" in x for x in T.lint({}, ok)), "a listed texPath that is no longer a gap fails (delete it)")
    late = {"frozen": "2026-10-10", "entries": [dict(ok["entries"][0], added="2026-10-11"), ok["entries"][1]]}
    check(any("GREW" in x for x in T.lint(got, late)), "an entry added after the freeze fails")

    T._DISK = None
    if T.load_index() is None:
        print("UNMEASURED part 2: no gametex cache on this machine")
    else:
        real = T.census()
        check(real.get("Things/Plant/RM_Ismerrow/RM_Ismerrow", {}).get("class") == "MISSING", "probe: RM_Ismerrow is seen and is a gap")
        check(sum(1 for v in real.values() if v["class"] == "OK_SRC") > 1000, "probe: thousands of real texPaths resolve in src")
        allow = T.json.loads(T.ALLOWLIST.read_text())
        fails = T.lint(real, allow)
        check(not fails, "the real repo: every gap is listed and no entry is stale", fails)
    print("FAILED" if FAILS else "ALL PASS", len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
