#!/usr/bin/env python3
"""biome_preflight offline rows on fixtures: the texture classes (OK / BASEGAME / SKIP / MISSING / NODEF), the `_m`
mask trap, inheritance of texPath through ParentName, the derived roster on the real repo, and the manifest row."""
import json
import os
import sys
import tempfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from northstar_driver import biome_preflight as BP  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    if not cond:
        FAILS.append("%s %s" % (name, str(detail)[:300]))


DEFS = """<Defs>
  <ThingDef Name="AnimalBase" Abstract="True"><race /></ThingDef>
  <ThingDef ParentName="AnimalBase"><defName>RSW_Anooba</defName></ThingDef>
  <PawnKindDef Name="KindBase" Abstract="True"><lifeStages><li><bodyGraphicData><texPath>Pawn/Anooba_m</texPath>
    </bodyGraphicData></li></lifeStages></PawnKindDef>
  <PawnKindDef ParentName="KindBase"><defName>RSW_Anooba</defName><race>RSW_Anooba</race></PawnKindDef>
  <ThingDef Name="PlantBase" Abstract="True"><graphicData><texPath>Things/Plant/RM_Rand</texPath></graphicData></ThingDef>
  <ThingDef ParentName="PlantBase"><defName>RM_Good</defName><modExtensions><li><flecksTexPath>Things/Plant/Gone/F</flecksTexPath></li></modExtensions></ThingDef>
  <ThingDef ParentName="PlantBase"><defName>RM_Plain</defName></ThingDef>
  <ThingDef><defName>RM_NoArt</defName><graphicData><texPath>Things/Plant/Nowhere</texPath></graphicData></ThingDef>
</Defs>"""
CORE = """<Defs><ThingDef><defName>Plant_Brambles</defName><graphicData><texPath>Things/Plant/Brambles</texPath>
  </graphicData></ThingDef></Defs>"""

d = tempfile.mkdtemp(prefix="bpf_")
tex = os.path.join(d, "Textures")
for rel in ("Pawn/Anooba_m_south.png", "Things/Plant/RM_Rand/a.png"):
    p = os.path.join(tex, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "wb").write(b"png")
check("resolve _m texPath (mask trap)", BP.resolve_loose("Pawn/Anooba_m", [tex]))
check("resolve Random folder", BP.resolve_loose("Things/Plant/RM_Rand", [tex]))
check("nowhere is nowhere", BP.resolve_loose("Things/Plant/Nowhere", [tex]) is None)

ix = BP.DefIndex()
ix.add_tree(ET.fromstring(DEFS), "mandrake.rsw.swbestiary")
ix.add_tree(ET.fromstring(CORE), "ludeon.rimworld")
ix.finish()
kind, tps = BP.tex_paths_for(ix, "RSW_Anooba")
check("race texPath inherited from the kind's parent", kind == "race" and tps == ["Pawn/Anooba_m"], (kind, tps))
kind, tps = BP.tex_paths_for(ix, "RM_Good")
check("plant texPath inherited + own extension path", tps == ["Things/Plant/RM_Rand", "Things/Plant/Gone/F"], tps)

tier = ["mandrake.rsw.swbestiary", "ludeon.rimworld", "mandrake.rut.patches"]
rows = [("RM_X", "wildAnimals", "RSW_Anooba", {}),
        ("RM_X", "wildPlants", "RM_Plain", {}),
        ("RM_X", "wildPlants", "RM_Good", {}),
        ("RM_X", "wildPlants", "RM_NoArt", {}),
        ("RM_X", "wildPlants", "Plant_Brambles", {}),
        ("RM_X", "wildAnimals", "RM_Ghost", {}),
        ("RM_X", "wildAnimals", "AA_Off", {"may_require": "sarg.alphaanimals"}),
        ("RM_X", "wildAnimals", "Pm_Off", {"patch_mod": "mandrake.rut.other"})]
got = {n: cl for n, cl, _ in BP.classify_rows(rows, tier, ix, [tex], {"bundle_files": {}})}
want = {"RSW_Anooba": "OK", "RM_Plain": "OK", "RM_Good": "MISSING", "RM_NoArt": "MISSING",
        "Plant_Brambles": "BASEGAME", "RM_Ghost": "NODEF", "AA_Off": "SKIP", "Pm_Off": "SKIP"}
check("classes", got == want, {k: (got.get(k), v) for k, v in want.items() if got.get(k) != v})
got = {n: cl for n, cl, _ in BP.classify_rows(rows[:2], tier, ix, [tex], {"bundle_files": {"pawn/anooba_m": 1}})}
check("bundle rung", got["RSW_Anooba"] == "OK")

# real repo: the derived roster is non-empty for all three sprint biomes (instrument can see)
for b in ("Cauldron", "Contagion", "LeaningScrub"):
    check("derived roster " + b, len(BP.derived_roster(b)) > 10, len(BP.derived_roster(b)))

# manifest row: absent -> UNMEASURED; malformed -> FAIL
c = BP.Ctx("Cauldron", manifest_path=os.path.join(d, "none.json"))
check("no manifest is UNMEASURED", BP.o_manifest(c).status == BP.UNMEASURED)
mp = os.path.join(d, "m.json")
json.dump({"requirement_ids": [], "rows": ["nope/nope"], "inferred_ok": ["x/y"]}, open(mp, "w"))
r = BP.o_manifest(BP.Ctx("Cauldron", manifest_path=mp))
check("bad manifest FAILs", r.status == BP.FAIL and "requirement_ids" in r.evidence and "inferred_ok" in r.evidence, r.evidence)

print("FAIL: " + " | ".join(FAILS) if FAILS else "OK selftest_biome_preflight")
sys.exit(1 if FAILS else 0)
