#!/usr/bin/env python3
# selftest-timeout: 300
"""selftest_texture_gap_lint.py — a texPath that resolves to no loadable picture is caught, and the real repo's gaps are all listed.

Part 1, synthetic: an index where one path is shipped by an ACTIVE mod, one only by an INACTIVE mod, one by the base-game
bundle, one nowhere; src resolves a Graphic_Random folder and a Graphic_Multi file and ignores masks. The planted defects
(inactive-only, nowhere) must be flagged, every good path must not be; lint() fails an unlisted gap, a stale entry, an entry
added after the freeze.
Part 2, the REAL repo (skipped as UNMEASURED without the gametex cache): the lint passes, and SANITY PROBE: a texPath known to
resolve in src is OK_SRC and a planted nowhere-path run through the real roots and index is MISSING, so the scan is demonstrably looking.
"""
from __future__ import annotations

# selftest temp containment (wave 7, DIRTY_CODE_REVIEW_STANDING_LOOP_1): every mkdtemp/mkstemp below,
# and every child process via TMPDIR, lands in one private dir removed at exit — this
# test used to leave its temp dirs behind in the seat TMPDIR on every run.
import atexit as _st_atexit, os as _st_os, shutil as _st_shutil, tempfile as _st_tempfile  # noqa: E401
_st_tempfile.tempdir = _st_os.environ["TMPDIR"] = _st_tempfile.mkdtemp(prefix="st_selftest_texture_gap_lint_")
_st_atexit.register(_st_shutil.rmtree, _st_tempfile.tempdir, True)
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

    # templated texPaths (GSS fills "{look}" from AerialStyles.Looks): judged per expansion, values read from the C#
    cs = d / "Styles.cs"
    cs.write_text('public static readonly string[] Looks = { "Alpha", "Beta" };\n')
    saved = dict(T.TEMPLATE_SOURCES)
    T.TEMPLATE_SOURCES["look"] = (cs, r"\bLooks\s*=\s*\{([^}]*)\}")
    for rel in ("Pole/Alpha/Span.png", "Pole/Beta/Span.png", "Half/Alpha/Span.png"):
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGBA", (4, 4), (1, 2, 3, 255)).save(root / rel)
    tg = T.census({"Pole/{look}/Span": ["t.xml"], "Half/{look}/Span": ["t.xml"], "Odd/{shade}/Span": ["t.xml"]},
                  [root], ix)
    check(T.expand("Pole/{look}/Span") == ["Pole/Alpha/Span", "Pole/Beta/Span"], "a template expands to the C# values",
          T.expand("Pole/{look}/Span"))
    check(tg["Pole/{look}/Span"]["class"] == "OK_SRC" and not T.lint(
        {"Pole/{look}/Span": tg["Pole/{look}/Span"]}, {"frozen": "2026-10-10", "entries": []}),
        "a template whose every expansion resolves is OK, not a gap", tg["Pole/{look}/Span"])
    hf = T.lint(tg, {"frozen": "2026-10-10", "entries": []})
    check(tg["Half/{look}/Span"]["class"] == "TEMPLATE_GAP" and tg.get("Half/Beta/Span", {}).get("class") == "MISSING"
          and any("TEXTURE GAP: Half/Beta/Span" in x for x in hf) and not any("Half/{look}" in x for x in hf),
          "PLANTED: one missing expansion is a gap under its literal path", hf)
    check(tg["Odd/{shade}/Span"]["class"] == "MISSING", "PLANTED: a placeholder with no known source stays a gap",
          tg["Odd/{shade}/Span"])
    T.TEMPLATE_SOURCES.clear()
    T.TEMPLATE_SOURCES.update(saved)
    check(T.template_values("look") and "Scrapper" in T.template_values("look"),
          "probe: the real {look} values are read from GSS AerialStyles.cs", T.template_values("look"))

    T._DISK = None
    if T.load_index() is None:
        print("UNMEASURED part 2: no gametex cache on this machine")
    else:
        real = T.census()
        # 2026-10-18: the repo's last MISSING gaps got their art (49f734a92), so "at least one genuine MISSING gap" stopped
        # being true of the repo while the instrument still worked. The probe now plants a path through the REAL roots and
        # REAL index: the live scan must call it MISSING.
        planted = T.census(paths={"Things/RM_SelftestProbe/NoSuchTexture_probe": ["selftest"]})
        check(planted["Things/RM_SelftestProbe/NoSuchTexture_probe"]["class"] == "MISSING",
              "probe: the real scan calls a planted nowhere-path MISSING", planted)
        check(sum(1 for v in real.values() if v["class"] == "OK_SRC") > 1000, "probe: thousands of real texPaths resolve in src")
        allow = T.json.loads(T.ALLOWLIST.read_text())
        fails = T.lint(real, allow)
        check(not fails, "the real repo: every gap is listed and no entry is stale", fails)
    print("FAILED" if FAILS else "ALL PASS", len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
