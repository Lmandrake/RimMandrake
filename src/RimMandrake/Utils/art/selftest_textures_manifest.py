#!/usr/bin/env python3
"""art_sheet --textures: a texture C# draws with no def gets a census row sized by its manifest (runtimeSize), its
same-part rows are linked across looks, former paths ride on the resource, and the resolver honours the size."""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import art_sheet as A  # noqa: E402
import scale_panel as SP  # noqa: E402

fails = []


def check(cond, what):
    print(("PASS " if cond else "FAIL ") + what)
    if not cond:
        fails.append(what)


man = {"rows": [
    {"key": "T_00_Clamp_0Scrapper", "label": "clamp — Scrapper", "part": "Clamp", "look": "Scrapper", "section": "T",
     "resources": ["Mod/New/Clamp"], "former": ["Mod/Old/Clamp", "Mod/Old/Other"],
     "size": {"drawSize": [1.5, 1.5], "footprint": [2, 2], "source": "X.cs:1 TapSize"}, "render_match": "scrapper"},
    {"key": "T_00_Clamp_1Industrial", "label": "clamp — Industrial", "part": "Clamp", "look": "Industrial", "section": "T",
     "resources": ["Mod/New/Styles/Industrial/Clamp"], "size": {"drawSize": [0.32, 0.08], "source": "Y.cs:2"}}],
    "lead_html": "<p>LEAD</p>"}
with tempfile.TemporaryDirectory() as td:
    mp = Path(td) / "m.json"
    mp.write_text(json.dumps(man))
    old_out = A.BIOME_OUT
    A.BIOME_OUT = Path(td)
    try:
        cpath, key = A.textures_census("selftest_tex", mp, "T")
    finally:
        A.BIOME_OUT = old_out
    c = json.loads(cpath.read_text())
    b = c["biomes"][key]
    rows = {r["key"]: r for r in b["rows"]}
    check(b["lead_html"] == "<p>LEAD</p>", "lead html carried to the census")
    r0 = rows["T_00_Clamp_0Scrapper"]
    check([t["defName"] for t in r0["twins"]] == ["T_00_Clamp_1Industrial"], "same part linked across looks")
    check(r0["art"]["resources"][0]["former"] == ["Mod/Old/Clamp"], "former path kept only for the same file name")
    check(r0["render_match"] == "scrapper", "render filter carried")
    R = SP.Resolver()
    s = R.size(r0)
    check(s["status"] == "measured" and s["drawSize"] == [1.5, 1.5] and s["footprint"] == [2, 2]
          and "X.cs:1" in s["source"], "resolver sizes a runtime row from its manifest, citing the source")
    s1 = R.size(rows["T_00_Clamp_1Industrial"])
    check(s1["footprint"] == [1, 1] and s1["quad"] == 0.32, "default footprint 1x1, quad = drawn width")
    check(R.describe(r0).get("label") == "clamp — Scrapper", "describe uses the manifest")
print("ALL PASS" if not fails else f"{len(fails)} FAILED")
sys.exit(1 if fails else 0)
