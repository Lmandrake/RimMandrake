#!/usr/bin/env python3
"""Selftest for canon_materials_audit.py: clean tree passes; each planted defect is caught."""
import os, re, shutil, sys, tempfile
import xml.etree.ElementTree as ET
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import canon_materials_audit as A

fails = []
def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  " + str(detail)))
    if not cond: fails.append(name)

GAME = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data/Odyssey/Defs"
FIX_STEPS = '''<Defs>%s</Defs>''' % "".join(
    f'<GenStepDef><defName>{s}</defName><genStep><mineableCounts><MineableGold>1~2</MineableGold>'
    f'<MineablePlasteel>1~2</MineablePlasteel><MineableComponentsIndustrial>1~2</MineableComponentsIndustrial>'
    f'</mineableCounts></genStep></GenStepDef>' for s in ("Asteroid", "Asteroid_NoRuins", "AsteroidBasic", "Other"))
FIX_LOC = ('<Defs><GeneratedLocationDef><defName>Asteroids</defName><preciousResources><li>MineableGold</li>'
           '<li>MineablePlasteel</li><li>MineableComponentsIndustrial</li></preciousResources></GeneratedLocationDef></Defs>')

def apply_patch(patch_path, trees):
    """minimal PatchOperationRemove simulator over {name: ElementTree root}."""
    n = 0
    for op in ET.parse(patch_path).getroot().iter("Operation"):
        xp = op.findtext("xpath").replace("/Defs/", "./").replace("[text()=", "[.=").replace('"', "'")
        for root in trees.values():
            parent_map = {c: p for p in root.iter() for c in p}
            for hit in root.findall(xp):
                parent_map[hit].remove(hit); n += 1
    return n

def main():
    base = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    check("clean: dangling", A.dangling(base) == [], A.dangling(base))
    check("clean: roster", A.roster(base) == [], A.roster(base))
    check("clean: odyssey", A.odyssey(base) == [], A.odyssey(base))
    check("clean: remelt", A.remelt(base) == [], A.remelt(base))
    # patch effect on fixture (and on the real Odyssey files when readable)
    pp = os.path.join(base, "RimStarWars", "Armoury", "Patches", A.ODYSSEY_PATCH)
    trees = {"steps": ET.fromstring(FIX_STEPS), "loc": ET.fromstring(FIX_LOC)}
    n = apply_patch(pp, trees)
    left = {e.tag for e in trees["steps"].iter()} | {e.text for e in trees["loc"].iter("li")}
    other = trees["steps"].findall("GenStepDef[defName='Other']/genStep/mineableCounts/MineablePlasteel")
    check("patch removes plasteel/components from allowlist only", n == 8 and "MineableGold" in left and len(other) == 1
          and not trees["loc"].findall(".//li[.='MineablePlasteel']"), n)
    if os.path.exists(GAME):
        real = {k: ET.parse(os.path.join(GAME, k)).getroot() for k in ("MapGeneration/SpaceMapGenerator.xml", "GeneratedLocationDefs/GeneratedLocations.xml")}
        n = apply_patch(pp, real)
        txt = "".join(ET.tostring(r, encoding="unicode") for r in real.values())
        check("real Odyssey files: no plasteel/components left in asteroid steps", n == 7 and
              txt.count("MineablePlasteel") == 0 and txt.count("MineableComponentsIndustrial") == 0, (n, txt.count("MineablePlasteel")))
    # planted defects
    tmp = tempfile.mkdtemp()
    try:
        t = os.path.join(tmp, "src"); os.makedirs(os.path.join(t, "A", "Defs")); os.makedirs(os.path.join(t, "RimMandrake", "Utils"))
        open(os.path.join(t, "A", "Defs", "x.xml"), "w").write("<Defs><ThingDef><defName>X</defName><costList><Make_PlasteelGF>3</Make_PlasteelGF>"
              "<Steel>1</Steel></costList><recipe>KOTOR_AlloyDurasteel</recipe></ThingDef></Defs>")
        got = A.dangling(t)
        check("planted dangling tag and text caught", len(got) == 2, got)
        open(os.path.join(t, "RimMandrake", "Utils", "gen_x.py"), "w").write("s='<thingDef>OuterRim_Durasteel</thingDef>'")
        check("planted generator re-emit caught", len(A.roster(t)) >= 1, A.roster(t))
        check("missing odyssey patch caught", A.odyssey(t) != [])
        check("missing remelt recipes caught", len(A.remelt(t)) == 2, A.remelt(t))
        os.makedirs(os.path.join(t, "P"))
        open(os.path.join(t, "P", A.ODYSSEY_PATCH), "w").write('<Patch><Operation><xpath>/Defs/GenStepDef[defName="Asteroid"]/genStep/mineableCounts/MineableGold</xpath></Operation></Patch>')
        got = A.odyssey(t)
        check("planted gold removal and short allowlist caught", any("MineableGold" in g for g in got) and any("allowlist" in g for g in got), got)
    finally:
        shutil.rmtree(tmp)
    print("selftest:", "FAIL %d" % len(fails) if fails else "ok")
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
