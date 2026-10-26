#!/usr/bin/env python3
"""selftest_retired_donor_refs.py -- retired_donor_refs.py finds dead references and only dead ones,
and today's src/ holds none to Alpha Biomes (ALPHA_BIOMES_RETIRE_THE_LAST_PLANT_DONOR, plan step 5).

    python3 src/RimMandrake/Utils/selftest_retired_donor_refs.py
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import retired_donor_refs as R  # noqa: E402

FAILS = []


def check(cond, what, detail=""):
    print(("PASS " if cond else "FAIL ") + what + ("" if cond else "  -- %s" % (detail,)))
    if not cond:
        FAILS.append(what)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def synthetic():
    with tempfile.TemporaryDirectory() as t:
        donor = os.path.join(t, "donor")
        write(os.path.join(donor, "1.6", "Defs", "Plants.xml"), """<Defs>
  <ThingDef Name="DN_PlantBase" Abstract="True"><category>Plant</category></ThingDef>
  <ThingDef Name="Plant_Bush" Abstract="True"><category>Plant</category></ThingDef>
  <ThingDef ParentName="DN_PlantBase"><defName>DN_Fern</defName></ThingDef>
  <BiomeDef><defName>DN_Swamp</defName></BiomeDef>
  <ThingDef><defName>DebrisStoneA</defName></ThingDef>
  <ThingDef><defName>DN_KeptName</defName></ThingDef>
</Defs>""")
        write(os.path.join(donor, "1.6", "Mods", "Odyssey", "Defs", "More.xml"),
              "<Defs>" + "".join("<ThingDef><defName>DN_Filler%02d</defName></ThingDef>" % i
                                 for i in range(60)) + "</Defs>")
        write(os.path.join(donor, "1.6", "Patches", "NotDefs.xml"),
              "<Patch><Operation Class='PatchOperationAdd'><xpath>Defs</xpath><value>"
              "<ThingDef><defName>DN_FromPatch</defName></ThingDef></value></Operation></Patch>")
        inv = R.inventory("test.donor", donor)
        check("DN_Fern" in inv["defs"] and "DN_Swamp" in inv["defs"], "inventory reads Defs/ (incl. Mods/ subfolders)")
        check("DN_PlantBase" in inv["abstracts"] and "DN_PlantBase" not in inv["defs"],
              "inventory keeps abstract Name= apart from concrete defNames")
        check("DN_FromPatch" not in inv["defs"], "inventory ignores Patches/ (not a Defs folder)")
        inv = R.drop_live(inv, {"DebrisStoneA": "ludeon.rimworld", "Plant_Grass": "ludeon.rimworld"}, "capX")
        check("DebrisStoneA" not in inv["defs"] and inv["alsoLive"] == {"DebrisStoneA": "ludeon.rimworld"},
              "a name the donor-off capture still defines is live, not dead", inv["alsoLive"])
        facts = os.path.join(t, "facts")
        write(os.path.join(facts, "test.donor.json"), json.dumps(inv))

        src = os.path.join(t, "src")
        write(os.path.join(src, "Mod", "Patches", "P.xml"), """<Patch>
  <!-- DN_Fern in a comment is not a reference -->
  <Operation Class="PatchOperationConditional">
    <xpath>/Defs/ThingDef[defName="DN_Fern"]/altitudeLayer</xpath>
  </Operation>
  <Operation Class="PatchOperationRemove">
    <xpath>/Defs/ThingDef[defName="Live_Race"]/race/wildBiomes/DN_Swamp</xpath>
  </Operation>
  <Operation Class="PatchOperationAdd">
    <xpath>/Defs/ThingDef[defName="Plant_Bush"]/comps</xpath>
  </Operation>
</Patch>""")
        write(os.path.join(src, "Mod", "Defs", "D.xml"), """<Defs>
  <ThingDef ParentName="DN_PlantBase"><defName>RM_Child</defName>
    <graphicData><texPath>Things/Plants/DN_Fern</texPath></graphicData>
    <plant><wildBiomes><DN_Swamp>1</DN_Swamp></wildBiomes></plant>
  </ThingDef>
  <BiomeDef><defName>RM_Bog</defName><wildPlants><li>DN_Filler01</li></wildPlants></BiomeDef>
  <ThingDef><defName>DN_KeptName</defName></ThingDef>
  <ThingDef><defName>RM_UsesKept</defName><thing>DN_KeptName</thing></ThingDef>
  <ThingDef><defName>RM_Allowed</defName><thing>DN_Filler02</thing></ThingDef>
</Defs>""")
        allow = {("src/Mod/Defs/D.xml", "DN_Filler02"): "test reason"}
        status, rows = R.check(None, src=src, facts=facts, allow=allow, repo=t)
        got = {(r["file"].split("/")[-1], r["form"], r["name"]) for r in rows if not r["allowed"]}
        want = {("P.xml", "xpath", "DN_Fern"), ("P.xml", "xpath", "DN_Swamp"),
                ("D.xml", "parent", "DN_PlantBase"), ("D.xml", "tag", "DN_Swamp"),
                ("D.xml", "value", "DN_Filler01")}
        check(status == "HITS", "synthetic tree reads HITS", status)
        check(want <= got, "finds xpath target, xpath path step, ParentName, row tag and whole value",
              sorted(want - got))
        check(not any(n == "Plant_Bush" for _f, _k, n in got),
              "a donor abstract named like a live def (Plant_Bush) is not a hit outside ParentName", got)
        check(not any(n == "DN_KeptName" for _f, _k, n in got), "a name our own XML defines is ours, not dead")
        check(not any(f == "D.xml" and n == "DN_Fern" for f, _k, n in got),
              "a texture path is not a reference")
        check(len(got) == len(want), "no hit beyond the five expected", sorted(got - want))
        al = [r for r in rows if r["allowed"]]
        check(len(al) == 1 and al[0]["name"] == "DN_Filler02", "ALLOW marks a deliberate hit allowed", al)

        small = os.path.join(t, "small")
        write(os.path.join(small, "x.json"), json.dumps({"packageId": "x", "defs": ["A"], "abstracts": []}))
        status, _ = R.check(None, src=src, facts=small, repo=t)
        check(status == "UNMEASURED", "an inventory under the floor reads UNMEASURED, never CLEAN", status)
        status, _ = R.check(None, src=src, facts=os.path.join(t, "none"), repo=t)
        check(status == "UNMEASURED", "no inventory reads UNMEASURED", status)


def real_tree():
    invs = R.load_inventories("sarg.alphabiomes")
    inv = invs.get("sarg.alphabiomes")
    check(inv is not None, "the committed Alpha Biomes inventory exists")
    if not inv:
        return
    check("AB_Bryolux" in inv["defs"] and "AB_PyroclasticConflagration" in inv["defs"]
          and "AB_CavePlantBase" in inv["abstracts"],
          "SANITY: the inventory holds known donor plant, biome and abstract names")
    status, rows = R.check("sarg.alphabiomes")
    live = [(r["file"], r["name"]) for r in rows if not r["allowed"]]
    check(status == "CLEAN", "src/ names no Alpha Biomes def outside ALLOW", live[:12])


if __name__ == "__main__":
    synthetic()
    real_tree()
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    sys.exit(1 if FAILS else 0)
