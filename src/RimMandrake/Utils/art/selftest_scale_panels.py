#!/usr/bin/env python3
"""selftest_scale_panels.py — the scaled portrayal is on EVERY biome sheet (owner, 2026-10-05: "You also did not
include the scaled portrayal on that sheet"). Asserts, on the sheets as built: each carries scale items with a
picture (scale_ image), and the ground colour of Leaning Scrub is measured from a real texture."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import art_sheet as A  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def main():
    sheets = sorted(A.BIOME_OUT.glob("*_sheet_*.html"))
    check(len(sheets) >= 20, f"sanity probe: found {len(sheets)} built biome sheets")
    for f in sheets:
        h = f.read_text()
        m = re.search(r'<script id="ITEMS" type="application/json">(.*?)</script>', h, re.S)
        items = json.loads(m.group(1)) if m else []
        n = sum(1 for i in items if (i.get("scale") or {}).get("img"))
        check(n > 0 or not items, f"{f.stem}: {n} of {len(items)} rows carry a scale panel picture")
    rgb, src = A.measure_ground("RM_LeaningScrub")
    check(rgb is not None and "Sand" in src, f"Leaning Scrub ground measured: {rgb} from {src}")
    source_xml_fallback()
    print(f"{len(FAILS)} failed" if FAILS else "all passed")
    return 1 if FAILS else 0


def source_xml_fallback():
    """A plant NEWER than the live dump is sized from its source XML (ParentName followed within src/, engine defaults at
    a vanilla parent) and stays FALLBACK — never "measured" — with the real quad, so a tree is not drawn as one cell."""
    import tempfile
    import scale_panel as SP
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "src" / "ModX" / "Defs"
        d.mkdir(parents=True)
        (d / "a.xml").write_text('<Defs><ThingDef ParentName="TreeBase" Name="ST_TreeAbs" Abstract="True">'
                                 '<plant><visualSizeRange>4~7.5</visualSizeRange></plant></ThingDef>'
                                 '<ThingDef ParentName="ST_TreeAbs"><defName>ST_NewTree</defName></ThingDef>'
                                 '<ThingDef ParentName="BuildingBase"><defName>ST_NotPlant</defName></ThingDef></Defs>')
        R = SP.Resolver()
        R.SRC_ROOT = Path(td) / "src"
        z = R.size({"key": "ST_NewTree", "defNames": ["ST_NewTree"]})
        check(z["status"] == "fallback" and z.get("kind") == "plant" and z.get("quad") == 7.5 and z.get("cells") == 7.5,
              f"source-XML tree: inherited visualSizeRange 7.5 x engine drawSize 1 = 7.5-cell quad, FALLBACK: {z.get('quad')} {z['status']}")
        check(z["source"].startswith("FALLBACK from source XML") and "TreeBase" in z["source"],
              f"source-XML size names its file, its chain and FALLBACK: {z['source'][:120]}")
        n = R.size({"key": "ST_NotPlant", "defNames": ["ST_NotPlant"]})
        check(n.get("cells") == 1.0 and "1 cell" in n["source"], "a non-plant missing from the dump keeps the 1-cell FALLBACK")
        m = R.size({"key": "ST_Absent", "defNames": ["ST_Absent"]})
        check(m.get("cells") == 1.0 and m["status"] == "fallback", "a def in neither dump nor src keeps the 1-cell FALLBACK")


if __name__ == "__main__":
    sys.exit(main())
