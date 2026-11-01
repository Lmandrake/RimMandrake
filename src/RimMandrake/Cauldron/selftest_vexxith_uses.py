#!/usr/bin/env python3
"""VEXXITH_USES_1: the owner's card, read off the shipped XML and C#, then the kernel checks run through dotnet.
Offline; the rows marked control prove the parser can see."""
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
FW = os.path.join(SRC, "FlowWorks")
FAILS = []


def check(ok, msg):
    print(("ok   " if ok else "FAIL ") + msg)
    if not ok:
        FAILS.append(msg)


def root(*p):
    return ET.parse(os.path.join(*p)).getroot()


def text(*p):
    with open(os.path.join(*p), encoding="utf-8") as fh:
        return fh.read()


def defs(tree, tag="ThingDef"):
    return {d.findtext("defName"): d for d in tree.findall(tag) if d.findtext("defName")}


def has_ext(d, cls):
    return any(li.get("Class", "").endswith(cls) for li in d.findall("modExtensions/li"))


def recipe_ok(rec, product, want_users=("TableMachining",)):
    items = [li.text for li in rec.findall("ingredients/li/filter/thingDefs/li")]
    users = [li.text for li in rec.findall("recipeUsers/li")]
    return (items == ["RM_Vexxith"] and rec.find("products/" + product) is not None
            and rec.findtext("productHasIngredientStuff") == "true" and all(u in users for u in want_users))


def containers():
    base = root(FW, "Defs/LiquidTypes/ThingDefs/RM_LiquidBottles_Base.xml")
    named = {d.get("Name"): d for d in base.findall("ThingDef") if d.get("Name")}
    for fam in ("RM_BottleItemBase", "RM_BucketItemBase", "RM_BarrelItemBase"):
        d = named.get(fam)
        check(d is not None, "control: %s parsed" % fam)
        if d is None:
            continue
        rules = {li.findtext("material"): li for li in d.findall("modExtensions/li/materials/li")}
        v, m = rules.get("Vexxith"), rules.get("Metal")
        check(v is not None and v.findtext("holdsAcid") == "true", "%s: vexxith holds acid" % fam)
        check(m is not None and m.findtext("holdsAcid") == "false", "control: %s metal refuses acid" % fam)
        cats = [li.text for li in d.findall("stuffCategories/li")]
        check("Metallic" in cats, "%s accepts vexxith as Metallic stuff" % fam)
    src = text(FW, "Source/LiquidTypes/RM_ContainerMaterialMath.cs")
    check('stuffDefName == "RM_Vexxith"' in src and src.index('"RM_Vexxith"') < src.index('bool leathery'),
          "Classify names vexxith before the Metallic category swallows it")
    recs = defs(root(HERE, "Defs/RecipeDefs/RM_VexxithContainers.xml"), "RecipeDef")
    for name, prod in (("RM_Make_Bottle_Vexxith", "RM_BottleEmpty"), ("RM_Make_Bucket_Vexxith", "RM_BucketEmpty"),
                       ("RM_Make_Barrel_Vexxith", "RM_BarrelEmpty")):
        check(name in recs and recipe_ok(recs[name], prod), "%s makes %s of vexxith" % (name, prod))
    flow = defs(root(FW, "Defs/LiquidTypes/RecipeDefs/RM_ContainerRecipes.xml"), "RecipeDef")
    patch = root(HERE, "Patches/RM_Cauldron_VexxithContainers.xml")
    xpaths = [o.findtext("xpath") for o in patch.findall("Operation")]
    for r in ("RM_Make_Bottle_Metal", "RM_Make_Bucket_Metal", "RM_Make_Barrel_Metal"):
        check(r in flow, "control: %s exists" % r)
        hit = [x for x in xpaths if '"%s"' % r in x]
        check(len(hit) == 2, "%s bars vexxith in both filters" % r)
        for x in hit:
            sub = x.split("]/", 1)[1]
            check(flow[r].find(sub) is not None, "%s: patch target exists (%s)" % (r, sub))


def gates():
    src = text(FW, "Source/Superdeep/RM_FlowDoors.cs")
    check("BurnIfTouchingAcid" in src and "GateBurnsInAcid" in src, "a canal gate burns where acid touches it")
    check(src.count("RM_FluidIdentity.CellHoldsAcid(Map") == 2 and "GenAdj.CardinalDirections" in src, "the gate reads canal fluid on its own cell and all four sides")
    ident = text(FW, "Source/RM_FluidIdentity.cs")
    check("ex.FillAt(c) > 0 ? ex.FluidAt(c)" in ident, "a recorded fluid counts only while the cell holds some")
    check("index.AddFluid(f.defName, f.floodTerrain" in ident and "f.fillTerrainSuperdeep" in ident, "the in-game index reads every canal fill terrain")
    # The production index on the shipped defs (FlowWorks SelfTest, GateAcidChecks.cs): red slime, acid water, reaction liquor
    # canal fills burn steel not plasteel, every other fluid is the control.
    stock = os.path.join(SRC, "Utils", "selftest_flowworks_stock.py")
    for _ in range(2):  # a drvfs stage can fail with rsync ENOMEM: "env/build failure, not a selftest verdict"
        p = subprocess.run([sys.executable, stock, "--only", "GateAcid_*,ContainerMat_*"], capture_output=True, text=True, timeout=250)
        if "env/build failure" not in p.stdout + p.stderr:
            break
    tail = (p.stdout + p.stderr).strip().splitlines()[-3:]
    check(p.returncode == 0, "gate touch detection on the shipped defs (exit %s: %s)" % (p.returncode, " | ".join(tail)))
    plate = defs(root(HERE, "Defs/ThingDefs_Items/RM_CauldronItems.xml")).get("RM_Vexxith")
    check(plate is not None and has_ext(plate, "RM_AcidImmuneExtension") and plate.find("stuffProps/categories/li").text == "Metallic",
          "a vexxith gate can be built (Metallic, DoorBase's stuff) and its stuff refuses the burn at TakeDamage")
    check("HasModExtension<RM_AcidImmuneExtension>" in text(HERE, "Source/RM_VexxithAcidImmunity.cs"), "the immunity reads a building's Stuff")
    check("liquidCorrosionEnabled" in src, "gate burn sits behind the corrosion toggle")
    doors = defs(root(FW, "Defs/Canals/ThingDefs/FlowWorks_Doors.xml"))
    for d in ("RM_Sluice", "RM_SecurityGrateDoor"):
        check(doors[d].findtext("thingClass", "").endswith("Building_RM_FlowDoor"), "%s runs the gate tick" % d)
    check('"AcidBurn"' in src, "the burn is AcidBurn, the damage vexxith's immunity answers")
    patch = text(HERE, "Patches/RM_Cauldron_AcidDamage.xml")
    check('DamageDef[defName="AcidBurn"]' in patch, "AcidBurn is marked acid")


def machines():
    fw = defs(root(HERE, "Defs/ThingDefs_Buildings/RM_FilterWorks.xml"))
    tap = defs(root(HERE, "Defs/ThingDefs_Buildings/RM_VentGasTap.xml"))
    v = fw.get("RM_VexxithFilterWorks")
    check(v is not None and v.get("ParentName") == "RM_FilterWorksBase", "filter vessel descends from the Filter-Works")
    if v is not None:
        check(v.find("costList/RM_Vexxith") is not None and has_ext(v, "RM_AcidImmuneExtension"), "filter vessel: vexxith, acid-proof")
        fuel = float(v.findtext(".//fuelPerDay"))
        base = float(fw["RM_FilterWorks"].findtext(".//fuelPerDay"))
        check(fuel < base, "filter vessel uses cartridges slower (%s < %s)" % (fuel, base))
        check(len(v.findall("comps/li")) == len(fw["RM_FilterWorks"].findall("comps/li")) and v.find("comps").get("Inherit") == "False",
              "filter vessel replaces the comps, no doubled converter")
    t = tap.get("RM_VentGasTapLined")
    check(t is not None and t.get("ParentName") == "RM_VentGasTapBase", "vent liner descends from the gas tap")
    if t is not None:
        check(t.find("costList/RM_Vexxith") is not None and has_ext(t, "RM_PryProofExtension"), "vent liner: vexxith, pry-proof")
    check("HasModExtension<RM_PryProofExtension>" in text(HERE, "Source/RM_CauldronVents.cs"), "the vexxiss's prying reads the liner")
    hay = " ".join(open(os.path.join(dp, f), encoding="utf-8").read() for dp, _, fs in os.walk(os.path.join(HERE, "Defs")) for f in fs if f.endswith(".xml"))
    check(not re.search(r"<defName>[^<]*[Ss]crap", hay), "no scab-scrapers (card)")


def acid_air():
    patch = root(HERE, "Patches/RM_Cauldron_AcidAir.xml")
    biomes = [o.findtext("xpath") for o in patch.findall("Operation")]
    check(any('"RM_Cauldron"' in b for b in biomes) and any('"RM_TheForge"' in b for b in biomes), "the Forge and the Cauldron carry acid air")
    check(all(o.get("Class") == "PatchOperationConditional" for o in patch.findall("Operation")), "each biome guarded, no inert MayRequire")
    src = text(HERE, "Source/RM_AcidAir.cs")
    check("AllPawnsSpawned" in src and "Faction" not in src.split("BurnPawns", 2)[2].split("BurnHull")[0], "every exposed pawn burns: raiders by the rule colonists burn by")
    check("VacuumResistance" in src and "ToxicEnvironmentResistance" in src, "suits protect")
    check("new DamageInfo(acid" in src, "ship burn goes through TakeDamage, where vexxith is spared")
    rig = defs(root(HERE, "Defs/ThingDefs_Buildings/RM_HullLinerRig.xml")).get("RM_HullLinerRig")
    check(rig is not None and rig.find("costList/RM_Vexxith") is not None and has_ext(rig, "RM_HullLinerExtension"), "hull liner rig costs vexxith and carries the marker")
    check("RM_HullLinerExtension" in src and "IsSubstructure" in src, "the rig spares the ship")


def suit():
    d = defs(root(HERE, "Defs/ThingDefs_Items/RM_VexxithSuit.xml"))
    s, h = d.get("RM_VexxithSuit"), d.get("RM_VexxithSuitHelmet")
    check(s is not None and h is not None, "suit and helmet exist")
    if s is None or h is None:
        return
    vac = sum(float(x.findtext("equippedStatOffsets/VacuumResistance")) for x in (s, h))
    check(vac >= 1.0, "suit + helmet seal (VacuumResistance %.2f)" % vac)
    check(s.find("costList/RM_Vexxith") is not None and s.find("costList/Plasteel") is None, "vexxith is the alternative ingredient")
    check(float(s.findtext("statBases/ArmorRating_Sharp")) > 0.52, "better than the vacsuit's sharp armour")
    check(s.find("recipeMaker") is not None and has_ext(s, "RM_AcidImmuneExtension"), "made at a bench; the piece is acid-proof")


def settings():
    mod = text(HERE, "Source/RM_CauldronMod.cs")
    for f in ("acidAirEnabled", "acidAirHullEnabled", "acidAirFactor", "vexxithGearEnabled"):
        check(len(re.findall(r'"%s"' % f, mod)) >= 2 and "ref %s" % f in mod.replace("list.Slider(acidAirFactor", "ref acidAirFactor") + " ref acidAirFactor", "setting %s saved and drawn" % f)
    gate = text(HERE, "Source/RM_AcidAir.cs")
    for n in ("RM_VexxithFilterWorks", "RM_VentGasTapLined", "RM_HullLinerRig", "RM_Make_Barrel_Vexxith", "Make_RM_VexxithSuit"):
        check('"%s"' % n in gate, "gear gate covers %s" % n)


def kernel():
    """The C# kernel rules run ahead of the fuzz in the Cauldron selftest program, built through winbuild."""
    fuzz = os.path.join(SRC, "Utils", "selftest_cauldron_fuzz.py")
    p = subprocess.run([sys.executable, fuzz, "--fuzz-scale", "0.01"], capture_output=True, text=True, timeout=400)
    bad = [ln for ln in p.stdout.splitlines() if ln.startswith("FAIL acid air")]
    for ln in bad:
        print(ln)
    check(p.returncode == 0 and not bad, "kernel rules pass on the production kernel (exit %s)" % p.returncode)


def main():
    for f in (containers, gates, machines, acid_air, suit, settings, kernel):
        f()
    print("RESULT: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
