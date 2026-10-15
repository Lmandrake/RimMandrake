#!/usr/bin/env python3
"""selftest_plant_draw_layers.py -- offline checks of plant_draw_layers.py's patch runner,
inheritance resolver, roster reader and classifier. No disk scan, no game; < 1 s."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lxml import etree as LX  # noqa: E402

import plant_draw_layers as P  # noqa: E402

FAILS = []


def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)


def doc():
    return LX.fromstring(b"""<Defs>
  <ThingDef Name="PlantBase" Abstract="True"><altitudeLayer>LowPlant</altitudeLayer>
    <graphicData><drawSize>(1,1)</drawSize></graphicData>
    <plant><visualSizeRange>0.3~0.9</visualSizeRange></plant></ThingDef>
  <ThingDef Name="TreeBase" ParentName="PlantBase" Abstract="True">
    <altitudeLayer>Building</altitudeLayer><plant><treeCategory>Full</treeCategory></plant></ThingDef>
  <ThingDef ParentName="PlantBase"><defName>Moss</defName><label>grey moss</label>
    <plant><visualSizeRange>0.4~0.6</visualSizeRange><maxMeshCount>9</maxMeshCount></plant></ThingDef>
  <ThingDef ParentName="TreeBase"><defName>Oak</defName><label>oak</label></ThingDef>
  <ThingDef ParentName="PlantBase"><defName>Cap</defName><label>tall mushroom</label></ThingDef>
  <BiomeDef><defName>B</defName><wildPlants>
    <Moss>2</Moss><Cap MayRequire="some.absent">1</Cap><li><plant>Oak</plant><commonality>0.5</commonality></li>
  </wildPlants></BiomeDef>
</Defs>""")


def run(root, xml, names=()):
    pt = P.Patcher(root, {"a.b"}, set(names))
    op = LX.fromstring(xml)
    return pt, pt.apply(op, "<test>")


def main():
    # inheritance: nearest declaration wins, default when absent
    root = doc()
    R = P.Resolver(root)
    check("inherit altitude from PlantBase", R.text(R.by_def["Moss"], "altitudeLayer") == "LowPlant")
    check("inherit altitude two levels", R.text(R.by_def["Oak"], "altitudeLayer") == "Building")
    check("child field overrides parent", R.text(R.by_def["Moss"], "plant/visualSizeRange") == "0.4~0.6")
    check("abstract defs not in by_def", "PlantBase" not in R.by_def)

    # conditional add (the shape our donor patch uses)
    root = doc()
    x = '/Defs/ThingDef[defName="Moss"]'
    _, ok = run(root, f"""<Operation Class="PatchOperationConditional"><xpath>{x}/altitudeLayer</xpath>
      <match Class="PatchOperationReplace"><xpath>{x}/altitudeLayer</xpath>
        <value><altitudeLayer>FloorEmplacement</altitudeLayer></value></match>
      <nomatch Class="PatchOperationConditional"><xpath>{x}</xpath>
        <match Class="PatchOperationAdd"><xpath>{x}</xpath>
          <value><altitudeLayer>FloorEmplacement</altitudeLayer></value></match></nomatch>
    </Operation>""".encode())
    R = P.Resolver(root)
    check("conditional nomatch->add lowers Moss",
          ok and R.text(R.by_def["Moss"], "altitudeLayer") == "FloorEmplacement")
    check("sibling untouched", R.text(R.by_def["Cap"], "altitudeLayer") == "LowPlant")

    # replace path on a second run (now declared on the def itself)
    _, ok = run(root, f"""<Operation Class="PatchOperationReplace"><xpath>{x}/altitudeLayer</xpath>
      <value><altitudeLayer>Filth</altitudeLayer></value></Operation>""".encode())
    check("replace hits own declaration",
          ok and P.Resolver(root).text(P.Resolver(root).by_def["Moss"], "altitudeLayer") == "Filth")

    # missing donor is a silent no-op that still reports success through Conditional
    root = doc()
    pt, ok = run(root, b"""<Operation Class="PatchOperationConditional">
      <xpath>/Defs/ThingDef[defName="Nope"]</xpath>
      <match Class="PatchOperationRemove"><xpath>/Defs/ThingDef</xpath></match></Operation>""")
    check("missing donor: no change", len(root.findall("ThingDef")) == 5)

    # sequence stops on first failure; success Always masks it
    root = doc()
    _, ok = run(root, b"""<Operation Class="PatchOperationSequence"><operations>
      <li Class="PatchOperationRemove"><xpath>/Defs/ThingDef[defName="Nope"]</xpath></li>
      <li Class="PatchOperationRemove"><xpath>/Defs/ThingDef[defName="Oak"]</xpath></li>
      </operations></Operation>""")
    check("sequence stops at failure", not ok and P.Resolver(root).by_def.get("Oak") is not None)

    # FindMod by mod NAME
    root = doc()
    _, ok = run(root, b"""<Operation Class="PatchOperationFindMod"><mods><li>Some Mod</li></mods>
      <match Class="PatchOperationRemove"><xpath>/Defs/ThingDef[defName="Oak"]</xpath></match>
      </Operation>""", names=("Some Mod",))
    check("findmod match runs", P.Resolver(root).by_def.get("Oak") is None)

    # unknown class counted, not crashed
    root = doc()
    pt, ok = run(root, b"""<Operation Class="XmlExtensions.Whatever"><xpath>/Defs/ThingDef/altitudeLayer</xpath></Operation>""")
    check("unknown class counted", pt.unsupported.get("Whatever") == 1 and len(pt.unsupported_watched) == 1)

    # roster: element shape + li shape, MayRequire honoured
    root = doc()
    recs = P._records(root.find("BiomeDef/wildPlants"), {"a.b"})
    names = [n for n, _ in recs]
    check("roster element+li shapes", names == ["Moss", "Oak"])
    check("roster MayRequire drops absent", "Cap" not in names)

    # classifier
    base = dict(tree=False, sowTags=[], matureCells=0.6, label="", description="", defName="X")
    check("moss -> GROUND_COVER", P.classify(dict(base, defName="GreyMoss"))[0] == "GROUND_COVER")
    check("cap -> UPRIGHT", P.classify(dict(base, defName="Glowcap", label="glow cap"))[0] == "UPRIGHT")
    check("tree -> UPRIGHT", P.classify(dict(base, tree=True, defName="Moss"))[0] == "UPRIGHT")
    check("crop -> UPRIGHT", P.classify(dict(base, sowTags=["Ground"], defName="Grass"))[0] == "UPRIGHT")
    check("big -> UPRIGHT", P.classify(dict(base, matureCells=2.0, defName="BigMoss"))[0] == "UPRIGHT")
    check("tall grass -> BORDERLINE",
          P.classify(dict(base, defName="TallGrass"))[0] == "BORDERLINE")
    check("neither -> BORDERLINE", P.classify(dict(base, defName="Zorb"))[0] == "BORDERLINE")
    check("override wins", P.classify(dict(base, defName="RM_Dewshrooms",
                                           label="caps"))[0] == "GROUND_COVER")
    check("target layer is >=3 under LowPlant",
          P.ALT["LowPlant"] - P.ALT[P.TARGET_ALT] >= 3 and P.ALT["Filth"] == P.MAX_SAFE)

    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
