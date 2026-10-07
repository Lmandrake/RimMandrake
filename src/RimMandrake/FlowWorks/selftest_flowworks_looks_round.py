#!/usr/bin/env python3
"""FLOWWORKS_REVIEW_LOOKS_ROUND_1 — the parts of the owner's 2026-10-06 review a machine can check, read from the
shipped XML (never from the generator's intentions):

  3  no "channel" / "excavation" / "brimming" / "half-full" in any fill or dug terrain label or description; every
     fill tier is named by depth like vanilla's shores (shallow / chest-deep / deep / very deep <liquid>).
  2  tar is opaque dark grey: Solid (plain terrain) shader over white, R=G=B tint, neutral gloss.
  4  blood, chemfuel, astrofuel, white slime, red slime are canal FluidDefs with all four fill terrains defined, a
     surface look, and a station on the review map.
  7  acid is yellow-green and bubbles; slimes bubble lightly; boiling water bubbles hard.
  8  propane is a medium-pale neutral grey on a white texture.
 10  water is see-through; tar/oil/slime/blood are not.

    python3 src/RimMandrake/FlowWorks/selftest_flowworks_looks_round.py
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFS = HERE / "Defs"
BAD = re.compile(r"channel|excavat|brimming|half-full", re.I)
TIER = {"Trace": "shallow ", "Half": "chest-deep ", "Brim": "deep ", "Superdeep": "very deep "}
NEW = ("Blood", "Chemfuel", "Astrofuel", "SlimeWhite", "SlimeRed")


def tint(text):
    return tuple(float(v) for v in text.strip("()").split(","))


def looks():
    """defName -> {field: text} for every surfaceLook, from the registry and the FluidDef looks patch."""
    out = {}
    reg = ET.parse(DEFS / "LiquidTypes" / "LiquidDefs" / "RM_LiquidDefRegistry.xml").getroot()
    for d in reg:
        sl = d.find("surfaceLook")
        if sl is not None:
            out[d.findtext("defName")] = {c.tag: c.text for c in sl}
    pat = ET.parse(HERE / "Patches" / "LiquidTypes" / "RM_FluidSurfaceLooks.xml").getroot()
    for op in pat:
        name = re.search(r'defName="(\w+)"', op.findtext("xpath")).group(1)
        out[name] = {c.tag: c.text for c in op.find("value/surfaceLook")}
    return out


def main():
    terrains = {}
    for f in (DEFS / "Canals" / "TerrainDefs").glob("*.xml"):
        for t in ET.parse(f).getroot().iter("TerrainDef"):
            terrains[t.findtext("defName")] = (t.findtext("label") or "", t.findtext("description") or "")
    assert len(terrains) >= 40, "sanity probe: canal terrains not found (%d)" % len(terrains)
    fills = 0
    for dn, (label, desc) in terrains.items():
        assert not BAD.search(label) and not BAD.search(desc), "%s still says %r / %r" % (dn, label, desc)
        m = re.match(r"RM_Fill_(\w+?)_(Trace|Half|Brim|Superdeep)$", dn)
        if m:
            fills += 1
            assert label.startswith(TIER[m.group(2)]), "%s label %r is not named by depth" % (dn, label)
    assert fills >= 40, "sanity probe: fill tiers found %d" % fills

    fluids = {}
    for f in (DEFS / "Canals" / "FluidDefs").glob("*.xml"):
        for d in ET.parse(f).getroot():
            fluids[d.findtext("defName")] = d
    L = looks()
    vis = {s["setup"]["fluid"] for s in json.loads((HERE / "review_map_stations_visuals.json").read_text())["stations"]}
    for n in NEW:
        fd = fluids.get("RM_Fluid_" + n)
        assert fd is not None, "no FluidDef RM_Fluid_" + n
        for tag in ("floodTerrain", "fillTerrainHalf", "fillTerrainBrim", "fillTerrainSuperdeep"):
            assert fd.findtext(tag) in terrains, "RM_Fluid_%s %s %s is not defined" % (n, tag, fd.findtext(tag))
        assert ("RM_Fluid_" + n) in L or ("RM_Liquid_" + n) in L, "RM_Fluid_%s has no surface look" % n
        assert ("RM_Fluid_" + n) in vis, "RM_Fluid_%s has no review-map station" % n
    for n in ("Chemfuel", "Astrofuel"):
        assert fluids["RM_Fluid_" + n].findtext("fireKind") == "Detonation", n + " must detonate"
    assert fluids["RM_Fluid_Blood"].findtext("fireKind") in (None, "None"), "blood does not burn"

    tar = L["RM_Liquid_Tar"]
    r, g, b = tint(tar["tint"])
    # live 2026-10-06: the water shader read blue, the lava-flow shader read OLIVE; only the plain terrain shader
    # over white gives exactly the tint
    assert tar.get("shader") == "Solid" and tar.get("texture") == "White", "tar must be Solid over White"
    assert r == g == b and r <= 0.3, "tar tint %s is not a neutral dark grey" % tar["tint"]
    hl = tint(tar.get("highlight", "(1,1,1)"))
    assert hl[0] == hl[1] == hl[2], "tar gloss must have no hue: %s" % tar.get("highlight")
    for name in ("RM_Liquid_SlimeRed", "RM_Liquid_SlimeGreen", "RM_Liquid_SlimeWhite", "RM_Liquid_SlimeYellow"):
        assert 0 < float(L[name].get("bubbles", 0)) <= 0.15, name + " should bubble lightly"
        assert float(L[name].get("seeThrough", 0)) == 0, name + " is opaque"
    acid = L["RM_Liquid_AcidWater"]
    r, g, b = tint(acid["tint"])
    assert g > r > b and g - b > 0.6, "acid tint %s is not an eerie yellow-green" % acid["tint"]
    assert float(acid.get("bubbles", 0)) > float(L["RM_Liquid_SlimeRed"]["bubbles"]), "acid bubbles more than slime"
    assert float(L["RM_Liquid_BoilingWater"].get("bubbles", 0)) >= 0.5, "boiling water bubbles quite a bit"
    prop = L["RM_Liquid_Propane"]
    r, g, b = tint(prop["tint"])
    assert prop.get("texture") == "White" and abs(r - g) < 0.02 and abs(g - b) < 0.02 and 0.55 <= r <= 0.75, \
        "propane is not a medium-pale neutral grey on white: %s %s" % (prop.get("texture"), prop["tint"])
    assert float(L["RM_Liquid_FreshWater"].get("seeThrough", 0)) > 0, "water is see-through"
    for name in ("RM_Liquid_Tar", "RM_Fluid_Oil", "RM_Fluid_Blood"):
        assert float(L[name].get("seeThrough", 0)) == 0, name + " must stay opaque"
    print("ok  looks round: %d canal terrains named by depth, %d new fluids wired, tar/acid/propane/bubbles/see-through"
          % (len(terrains), len(NEW)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
