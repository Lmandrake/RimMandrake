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
    "lead_html": "<p>LEAD</p>", "ground_terrain": "RM_FE_Ash_Deep"}
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
    check(b["ground_terrain"] == "RM_FE_Ash_Deep", "manifest ground_terrain carried to the census")
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
# a texture-manifest row may name a corpse/dessicated render family exactly; a biome row never joins one
class _Idx:
    variants = {"s1": [{"kind": "artpipe", "job": "pyr_dessicated_wasp_south", "facing": "south", "date": "2026-10-14"}]}
    def is_purged(self, sha):
        return False
_none = A.name_render_cols(_Idx(), ["wasp"], ["pyr_dessicated_wasp"])
_one = A.name_render_cols(_Idx(), ["wasp"], ["pyr_dessicated_wasp"], exact_any=True)
check(_none == [], "a dessicated render never joins a body row, even named exactly")
check(len(_one) == 1 and _one[0]["faces"] == {"south": "s1"}, "a texture row joins the dessicated family it names")
_word = A.name_render_cols(_Idx(), ["wasp"], [], exact_any=True)
check(_word == [], "exact_any admits only EXACT names, never a corpse joined by word")
# a stand-in (vanilla art no ledger holds) becomes the row's IN GAME column, never purgeable, bytes put in the store
import hashlib as _h
_put = []
_orig_put = A.L.store_put_bytes
A.L.store_put_bytes = lambda b, sha: _put.append(sha)
try:
    with tempfile.TemporaryDirectory() as td2:
        f = Path(td2) / "x_south.png"
        f.write_bytes(b"not-really-a-png")
        sc = A.standin_col({"res": "Things/X", "label": "vanilla stand-in X", "source": "S", "faces": {"south": str(f)}})
finally:
    A.L.store_put_bytes = _orig_put
_sha = _h.sha256(b"not-really-a-png").hexdigest()
check(sc["faces"] == {"south": _sha} and _put == [_sha], "stand-in bytes stored and keyed by sha")
check(sc["kind"] == "donor" and sc["winner"] and not sc["ours"] and sc["label"].startswith("IN GAME"),
      "stand-in is the IN GAME donor column")
# a row whose IN GAME picture is a stand-in prefills the render named for it; a plain row keeps "what the game shows"
_ren = {"letter": "A", "kind": "artpipe", "bound": True, "faces": {"south": "r"}}
_std = dict(sc, letter="B")
_l, _why, _ = A.prefill_for({"cols": [_ren, _std]}, [])
check(_l == "A" and "stand-in" in _why, "stand-in row prefills the named render")
_l2, _, _ = A.prefill_for({"cols": [_ren, dict(_std, standin=False)]}, [])
check(_l2 == "B", "without a stand-in the prefill stays what the game shows now")
print("ALL PASS" if not fails else f"{len(fails)} FAILED")
sys.exit(1 if fails else 0)
