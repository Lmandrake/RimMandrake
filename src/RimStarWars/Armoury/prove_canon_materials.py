#!/usr/bin/env python3
"""prove_canon_materials.py -- CANON_MATERIALS_BUILD_1 offline (L0) proof, one verdict per criterion.

The functional script for the canon-materials work (design/RimMandrake/debug_process.md). Pure file reads, no game.

  python3 prove_canon_materials.py [--selftest]      exit 1 on any FAIL; OWED/PARTIAL do not fail the run.

Verdicts: PASS (criterion provable offline and proven), PARTIAL (some of it built, named gaps), OWED (not built, or only a
live load can say), FAIL (built and wrong). Only PASS may be passed to `rimflow verify --criterion`.

Instruments (each has a sanity probe, printed beside the result, because a check that cannot find anything reads clean):
  * def universe  = latest DefDump capture (every defType, live set) + every <defName> under src/ + Core Data XML fallback
  * ref resolution over the material-owned defs and patches (thing/thingDef/filter li/categories/products/research)
  * texture existence: loose PNG under src/*/*/Textures, else a texPath the base game itself uses (capture)
  * the Armoury's own static checks (validation.py) and canon_materials_audit.py
Learned 2026-10-11: the capture already holds RSW_Durasteel/RSW_Phrik, so "defined in src" and "loaded by a game" are separate
facts; this script proves the first only. L10 is the second and stays OWED until a minimal-list load reads Player.log.
"""
import glob, json, os, re, sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", ".."))
ARM = HERE
UTILS = os.path.join(SRC, "RimMandrake", "Utils")
sys.path.insert(0, UTILS)
from game_paths import LOCALLOW  # noqa: E402
CAPTURES = os.path.join(LOCALLOW, "DefDump", "captures")

MAT_DEFS = ["RSW_Durasteel", "RSW_Doonium", "RSW_Phrik", "RSW_Transparisteel", "RSW_Zersium", "RSW_Duranium", "RSW_Stygium", "RSW_Coaxium"]
MAT_PATCHES = ["RSW_AlloyForge_Durasteel", "RSW_DurasteelConvert", "RSW_DurasteelConvert_OuterRim", "RSW_OdysseyAsteroidNoPlasteel",
               "RSW_OdysseyAsteroid_Doonium", "RSW_PlasteelRecipesCut", "RSW_Smelter_Alloys", "RSW_Transparisteel_GlassFold",
               "RSW_DurasteelProducersZeroed", "RSW_SalvageByComposition", "RSW_BeskarNeverReforged", "RSW_ZeroedOreGates",
               "RSW_StygiumConvert", "RSW_CanonMaterialsTrade"]
OWNED_ROLES = ["RSW_Duranium", "RSW_Doonium", "RSW_Phrik", "RSW_Transparisteel", "RSW_Stygium", "RSW_Coaxium"]


def xml_files(root, skip=("Assemblies", "Textures", ".git", "__pycache__", "_artsrc")):
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in skip]
        for f in fn:
            if f.endswith(".xml"):
                yield os.path.join(dp, f)


def parse(p):
    try:
        return ET.parse(p).getroot()
    except ET.ParseError:
        return None


# ---------------------------------------------------------------- instruments
def latest_capture():
    caps = sorted(glob.glob(os.path.join(CAPTURES, "*", "defs")))
    return caps[-1] if caps else None


def capture_universe():
    """(names:set, texpaths:set, capdir) from the newest capture, or (None,None,None) = UNMEASURED."""
    d = latest_capture()
    if not d:
        return None, None, None
    names, tex = set(), set()
    for f in glob.glob(os.path.join(d, "*.json")):
        try:
            for x in json.load(open(f)).get("defs", []):
                names.add(x["defName"])
                if x.get("defType") == "ThingDef":
                    gd = (x.get("fields") or {}).get("graphicData") or {}
                    tp = gd.get("texPath") if isinstance(gd, dict) else None
                    if tp:
                        tex.add(tp)
        except Exception:
            pass
    return names, tex, d


def src_defnames():
    out = {}
    for p in xml_files(SRC):
        r = parse(p)
        if r is None:
            continue
        for dn in r.iter("defName"):
            if dn.text:
                out.setdefault(dn.text.strip(), p)
    return out


def refs_in(root):
    """defName-like references in a def/patch tree. Skips xpaths, and any <li> carrying MayRequire (optional by design)."""
    out = []
    SINGLE = {"thing", "thingDef", "mineableThing", "researchPrerequisite", "stuff", "smeltProduct", "butcherProduct"}
    LISTS = {"thingDefs", "categories", "thingCategories", "recipeUsers", "researchPrerequisites", "disallowedThingDefs"}

    def walk(e, par):
        for c in list(e):
            if c.tag in ("xpath", "success", "defName", "label", "description", "labelNoun", "jobString", "workerClass"):
                continue
            t = (c.text or "").strip()
            if c.tag in SINGLE and t and re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", t) and c.get("MayRequire") is None:
                out.append((c.tag, t))
            if c.tag == "li" and par.tag in LISTS and t and re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", t) and c.get("MayRequire") is None:
                out.append((par.tag, t))
            if c.tag in ("products", "smeltProducts", "costList", "killedLeavings", "butcherProducts"):
                for k in c:
                    if re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", k.tag) and k.tag != "li":
                        out.append((c.tag, k.tag))
            walk(c, c)
    walk(root, root)
    return out


def tex_ok(texpath, cap_tex):
    for png in glob.glob(os.path.join(SRC, "*", "*", "Textures", texpath + "*.png")):
        return "loose"
    for png in glob.glob(os.path.join(SRC, "*", "*", "Textures", os.path.dirname(texpath), os.path.basename(texpath) + "_*.png")):
        return "loose"
    if cap_tex and texpath in cap_tex:
        return "game"
    return None


# ---------------------------------------------------------------- criteria
R = {}   # id -> (verdict, [lines])


def put(cid, verdict, *lines):
    R[cid] = (verdict, list(lines))


DONOR_REV = "96be3c36c"
DONOR_FILE = "src/RimStarWars/Armoury/Defs/Absorbed_KotorCore/ThingDefs_Resources/Absorbed_KotorCore_KotORResource_Metals2.xml"
ZERO_PATCH = os.path.join(ARM, "Patches", "RSW_DurasteelProducersZeroed.xml")


def git_show(rev, path):
    import subprocess
    try:
        return subprocess.run(["git", "-C", SRC, "show", "%s:%s" % (rev, path)], capture_output=True, check=True, timeout=60).stdout.decode("utf-8", "replace")
    except Exception:
        return None


def capture_producers():
    """Pre-patch live census: ThingDefs mining into RSW_Durasteel (scatter/deep >0) and GenStepDefs naming them."""
    d = latest_capture()
    if not d:
        return None
    ores = {}
    for x in json.load(open(os.path.join(d, "ThingDef.json")))["defs"]:
        f = x.get("fields") or {}
        b = f.get("building") or {}
        if b.get("mineableThing") == "RSW_Durasteel":
            ores[x["defName"]] = (b.get("mineableScatterCommonality") or 0, f.get("deepCommonality") or 0)
    gen = {}
    for x in json.load(open(os.path.join(d, "GenStepDef.json")))["defs"]:
        s = json.dumps(x)
        for o in ores:
            if '"%s"' % o in s:
                gen.setdefault(o, []).append(x["defName"])
    # donor chunk-mineable (yields slag chunks that re-melt): scatter listed too
    kz = None
    for x in json.load(open(os.path.join(d, "ThingDef.json")))["defs"]:
        if x["defName"] == "KOTOR_MineableDurasteel":
            kz = ((x["fields"].get("building") or {}).get("mineableScatterCommonality") or 0)
    return {"ores": ores, "gen": gen, "kotor_scatter": kz,
            "summary": "ores %r, genstep refs %r, KOTOR_MineableDurasteel scatter %r" % (ores, gen, kz)}


VANILLA_OPS = {"PatchOperationAdd", "PatchOperationInsert", "PatchOperationRemove", "PatchOperationReplace",
               "PatchOperationAttributeAdd", "PatchOperationAttributeSet", "PatchOperationAttributeRemove",
               "PatchOperationAddModExtension", "PatchOperationSetName", "PatchOperationSequence", "PatchOperationFindMod",
               "PatchOperationConditional", "PatchOperationTest"}   # every PatchOperation subclass in decompiled 1.6 Verse


def patch_classes_bad(path):
    """Operation/li Class values that are not a vanilla PatchOperation (2026-10-11: PatchOperationAddOrReplace is in no
    vanilla assembly and in no installed mod DLL, so a patch using it fails to load)."""
    from lxml import etree as LX
    bad = []
    for el in LX.parse(path).iter():
        c = el.get("Class") if isinstance(el.tag, str) else None
        if c and c.startswith("PatchOperation") and c not in VANILLA_OPS:
            bad.append("%s: <%s Class=%s> is not a vanilla PatchOperation" % (os.path.basename(path), el.tag, c))
    return bad


def replay(root, patch, mods=()):
    """Replay a Patch file on an lxml fixture the way Verse does: FindMod matches on display name in `mods`, Conditional on
    xpath existence, Sequence stops at the first failure; Add/Replace/Remove fail on no match unless success=Always.
    Unknown classes raise (a sim that guesses is no instrument)."""
    from lxml import etree as LX

    def val(o):
        return [LX.fromstring(LX.tostring(c)) for c in o.find("value") if isinstance(c.tag, str)]

    def op(o):
        cls = o.get("Class")
        always = (o.findtext("success") or "").strip() == "Always"
        if cls == "PatchOperationFindMod":
            want = [li.text for li in o.find("mods")]
            br = o.find("match") if any(w in mods for w in want) else o.find("nomatch")
            ok = op(br) if br is not None else True
        elif cls == "PatchOperationSequence":
            ok = True
            for li in o.find("operations"):
                if isinstance(li.tag, str) and not op(li):
                    ok = False
                    break
        elif cls == "PatchOperationConditional":
            hit = root.xpath(o.findtext("xpath"))
            br = o.find("match") if hit else o.find("nomatch")
            ok = op(br) if br is not None else (o.find("match") is not None)
        elif cls == "PatchOperationSetName":
            hits = root.xpath(o.findtext("xpath"))
            for n in hits:
                n.tag = o.findtext("name").strip()
            ok = bool(hits)
        elif cls in ("PatchOperationRemove", "PatchOperationReplace", "PatchOperationAdd"):
            hits = root.xpath(o.findtext("xpath"))
            for n in hits:
                if cls == "PatchOperationRemove":
                    n.getparent().remove(n)
                elif cls == "PatchOperationReplace":
                    par, i = n.getparent(), n.getparent().index(n)
                    par.remove(n)
                    for k, v in enumerate(val(o)):
                        par.insert(i + k, v)
                else:
                    for v in val(o):
                        n.append(v)
            ok = bool(hits)
        else:
            raise ValueError("sim does not know " + str(cls))
        return ok or always
    for o in patch.getroot():
        if isinstance(o.tag, str):
            op(o)


def producers_zeroed(prod, patch_path=None):
    """Replay the zeroing patch (lxml, FindMod assumed matched) on a fixture rebuilt from the census + the donor's real patch
    shape (workshop 3565716659 LKOre_Patches*: shorthand mineableCounts, li in PreciousLump). Returns problems."""
    from lxml import etree as LX
    patch_path = patch_path or ZERO_PATCH
    bad = []
    if not os.path.exists(patch_path):
        return ["zeroing patch missing: %s" % os.path.basename(patch_path)]
    xml = ("<Defs>"
           "<ThingDef><defName>LKDurasteel_Ore</defName><building><mineableThing>RSW_Durasteel</mineableThing><mineableScatterCommonality>0.5</mineableScatterCommonality></building></ThingDef>"
           "<ThingDef><defName>KOTOR_MineableDurasteel</defName><building><mineableThing>KotORChunk_durasteel</mineableThing><mineableScatterCommonality>0.15</mineableScatterCommonality></building></ThingDef>"
           "<GenStepDef><defName>PreciousLump</defName><genStep><mineables><li>MineableGold</li><li>LKDurasteel_Ore</li><li>LKBeskar_Ore</li></mineables></genStep></GenStepDef>"
           + "".join("<GenStepDef><defName>%s</defName><genStep><mineableCounts><MineableGold>33~42</MineableGold><LKDurasteel_Ore>40~45</LKDurasteel_Ore><LKBeskar_Ore>20~45</LKBeskar_Ore></mineableCounts></genStep></GenStepDef>" % n
                     for n in ("Asteroid", "Asteroid_NoRuins", "AsteroidBasic")) + "</Defs>")

    def left(root):
        t = []
        t += ["PreciousLump still lists LKDurasteel_Ore"] if root.xpath('//GenStepDef[defName="PreciousLump"]//li[text()="LKDurasteel_Ore"]') else []
        t += ["%s mineableCounts still has LKDurasteel_Ore" % g.findtext("defName") for g in root.xpath('//GenStepDef[genStep/mineableCounts/LKDurasteel_Ore]')]
        for n in ("LKDurasteel_Ore", "KOTOR_MineableDurasteel"):
            v = root.xpath('//ThingDef[defName="%s"]/building/mineableScatterCommonality/text()' % n)
            if v != ["0"]:
                t.append("%s scatter %r after patch" % (n, v))
        return t
    # planted defect: the empty patch must leave all of it standing (proves the checker can see it)
    r0 = LX.fromstring(xml)
    if len(left(r0)) < 6:
        bad.append("SANITY: unpatched fixture shows only %d producer(s), want 6" % len(left(r0)))
    r1 = LX.fromstring(xml)
    replay(r1, LX.parse(patch_path), {"LK Mineable Resources Outer Rim"})
    bad += left(r1)
    keep = r1.xpath('//GenStepDef[defName="Asteroid"]//MineableGold/text()') + r1.xpath('//GenStepDef[defName="PreciousLump"]//li/text()')
    if keep != ["33~42", "MineableGold", "LKBeskar_Ore"]:
        bad.append("patch removed more than the durasteel rows: %r" % keep)
    # every ore the live capture shows mining durasteel with scatter>0 or a genstep must be one the patch names
    named = open(patch_path, encoding="utf-8").read()
    for o, (sc, dp) in prod["ores"].items():
        if (sc or dp or o in prod["gen"]) and ('"%s"' % o) not in named:
            bad.append("live producer %s (scatter %s, deep %s, gensteps %s) is not named by the zeroing patch" % (o, sc, dp, prod["gen"].get(o)))
    if prod["kotor_scatter"] and '"KOTOR_MineableDurasteel"' not in named:
        bad.append("KOTOR_MineableDurasteel still scatters (%s) and is not zeroed" % prod["kotor_scatter"])
    return bad


# ---------------------------------------------------------------- phase 2 (2026-10-11): L5, L7, ore gates, L8, L9
SALVAGE_PATCH = os.path.join(ARM, "Patches", "RSW_SalvageByComposition.xml")
BESKAR_PATCH = os.path.join(ARM, "Patches", "RSW_BeskarNeverReforged.xml")
GATES_PATCH = os.path.join(ARM, "Patches", "RSW_ZeroedOreGates.xml")
B1 = ["RSW_DW_Race_JDSCIS_B1_Battle_Droid", "RSW_DW_Race_JDSCIS_B1_Security_Droid", "RSW_DW_Race_JDSCIS_B1_Commander_Droid"]
ALL_MODS = {"LK Mineable Resources Outer Rim", "Outer Rim - Core", "Star Wars KotOR Resources and Materials",
            "Vanilla Factions Expanded - Pirates"}
# Fixture shapes copied from the real defs (Core Buildings_Exotic.xml, Biotech Buildings_Misc.xml, VFE Pirates 1.6
# Buildings_Gauntlet/ShipChunks.xml, Droidworks Races_JDS.xml), not invented.
SALVAGE_FIXTURE = ("<Defs>"
    "<ThingDef ParentName=\"BuildingBase\" Name=\"ShipChunkBase\"><defName>ShipChunk</defName><costList><ComponentIndustrial>11</ComponentIndustrial><Steel>40</Steel></costList>"
    "<killedLeavings><ChunkSlagSteel>2</ChunkSlagSteel><ComponentIndustrial>1</ComponentIndustrial></killedLeavings></ThingDef>"
    "<ThingDef ParentName=\"ShuttleBase\" Name=\"ShuttleCrashedBase\"><defName>ShuttleCrashed</defName><costList><Steel>40</Steel><Plasteel>70</Plasteel><ComponentIndustrial>10</ComponentIndustrial></costList></ThingDef>"
    "<ThingDef ParentName=\"BuildingBase\" Name=\"VFEP_CrashedShip\" Abstract=\"True\"><killedLeavings><Steel>120</Steel><ComponentIndustrial>6</ComponentIndustrial><ChunkSlagSteel>4</ChunkSlagSteel></killedLeavings></ThingDef>"
    "<ThingDef ParentName=\"VFEP_BuildingChunkBase\"><defName>VFEP_ShipChunkReactor</defName><costList><Steel>120</Steel><ComponentIndustrial>8</ComponentIndustrial><ComponentSpacer>8</ComponentSpacer></costList></ThingDef>"
    + "".join("<AlienRace.ThingDef_AlienRace ParentName=\"DW_Family_Battle\"><defName>%s</defName>%%s</AlienRace.ThingDef_AlienRace>" % b for b in B1)
    + "</Defs>")


def salvage_check(patch_path=None, b1_extra=""):
    """L5 replay. b1_extra plants a pre-existing B1 butcher product (double-route defect). Returns (problems, info)."""
    from lxml import etree as LX
    patch_path = patch_path or SALVAGE_PATCH
    if not os.path.exists(patch_path):
        return ["salvage patch missing"], []
    root = LX.fromstring(SALVAGE_FIXTURE % ((b1_extra,) * len(B1)))
    replay(root, LX.parse(patch_path), ALL_MODS)
    bad, info = [], []

    def has(xp, mat):
        return bool(root.xpath(xp + "/" + mat))
    want = {  # source -> materials its composition must yield (design 0b / 3 / 3.3)
        ('//ThingDef[defName="ShipChunk"]/costList', "ship chunk"): ["RSW_Durasteel", "Plasteel"],
        ('//ThingDef[defName="ShuttleCrashed"]/costList', "crashed shuttle"): ["RSW_Durasteel", "Plasteel", "RSW_Duranium", "RSW_Doonium"],
        ('//ThingDef[@Name="VFEP_CrashedShip"]/killedLeavings', "VFE pirate wreck"): ["RSW_Durasteel", "Plasteel", "RSW_Duranium", "RSW_Doonium"],
        ('//ThingDef[defName="VFEP_ShipChunkReactor"]/costList', "VFE reactor chunk"): ["RSW_Doonium"],
    }
    seen = set()
    for (xp, label), mats in want.items():
        miss = [m for m in mats if not has(xp, m)]
        seen |= {m for m in mats if has(xp, m)}
        if miss:
            bad.append("%s yields no %s" % (label, ", ".join(miss)))
    for m in ("RSW_Durasteel", "Plasteel", "RSW_Duranium", "RSW_Doonium"):
        if m not in seen:
            bad.append("no salvage source yields %s" % m)
    for b in B1:
        n = len(root.xpath('//*[defName="%s"]/butcherProducts/Plasteel' % b))
        if n != 1:
            bad.append("%s plasteel butcher routes = %d, want exactly 1" % (b, n))
    info.append("salvage replay: 4 sources x composition, 3 B1 races x 1 plasteel route")
    return bad, info


def b1_other_routes():
    """Live-set + source evidence that B1 remains have no second plasteel route. Returns (problems, info)."""
    bad, info = [], []
    d = latest_capture()
    if not d:
        return [], ["UNMEASURED: no capture for B1 meat/leather/recipe routes"]
    T = {x["defName"]: x for x in json.load(open(os.path.join(d, "ThingDef.json")))["defs"]}
    probe = T.get("RSW_DW_Race_JDSCIS_B1_Battle_Droid")
    if probe is None:
        return ["SANITY: B1 race absent from capture"], []
    corpses = set()
    for b in B1:
        r = (T.get(b) or {}).get("fields", {}).get("race") or {}
        for k in ("meatDef", "leatherDef"):
            if r.get(k) == "Plasteel":
                bad.append("%s race.%s is Plasteel (second route)" % (b, k))
        if r.get("corpseDef"):
            corpses.add(r["corpseDef"])
        if (T.get(b) or {}).get("fields", {}).get("butcherProducts"):
            info.append("%s already has butcherProducts in the capture: %r" % (b, T[b]["fields"]["butcherProducts"]))
    n = 0
    for x in json.load(open(os.path.join(d, "RecipeDef.json")))["defs"]:
        f = x.get("fields") or {}
        al = set(((f.get("fixedIngredientFilter") or {}).get("allowedDefs")) or [])
        if al & corpses:
            n += 1
            if any(p.get("thingDef") == "Plasteel" for p in f.get("products") or []):
                bad.append("recipe %s takes a B1 corpse and makes Plasteel (second route)" % x["defName"])
    cs = [p for p in glob.glob(os.path.join(SRC, "RimStarWars", "Droidworks", "Source", "**", "*.cs"), recursive=True)
          if "Plasteel" in open(p, encoding="utf-8", errors="ignore").read()]
    bad += ["Droidworks C# names Plasteel: %s" % os.path.basename(p) for p in cs]
    info.append("B1 routes: meatDef %s, leatherDef %s; %d recipes admit a B1 corpse (butchery only), none makes Plasteel; "
                "Droidworks C# naming Plasteel: %d" % (probe["fields"]["race"].get("meatDef"), probe["fields"]["race"].get("leatherDef"), n, len(cs)))
    if n == 0:
        bad.append("SANITY: no recipe admits a B1 corpse (butchery should)")
    return bad, info


BESKAR_FIXTURE = ("<Defs>"
    "<ThingDef Name=\"OuterRimMetal\" Abstract=\"True\"><smeltable>true</smeltable></ThingDef>"
    "<ThingDef ParentName=\"OuterRimMetal\"><defName>OuterRim_Beskar</defName><deepCommonality>.75</deepCommonality></ThingDef>"
    "<ThingDef ParentName=\"OuterRimMetal\"><defName>OuterRim_PureBeskar</defName><deepCommonality>.75</deepCommonality></ThingDef>"
    "<ThingDef ParentName=\"RockBase\"><defName>LKBeskar_Ore</defName><building><mineableThing>OuterRim_Beskar</mineableThing><mineableScatterCommonality>0.3</mineableScatterCommonality></building></ThingDef>"
    "<ThingDef ParentName=\"RockBase\"><defName>LKPureBeskar_Ore</defName><building><mineableThing>OuterRim_PureBeskar</mineableThing><mineableScatterCommonality>0.3</mineableScatterCommonality></building></ThingDef>"
    "<GenStepDef><defName>PreciousLump</defName><genStep><mineables><li>MineableGold</li><li>LKBeskar_Ore</li><li>LKPureBeskar_Ore</li></mineables></genStep></GenStepDef>"
    + "".join("<GenStepDef><defName>%s</defName><genStep><mineableCounts><MineableGold>33~42</MineableGold><LKBeskar_Ore>20~45</LKBeskar_Ore><LKPureBeskar_Ore>20~45</LKPureBeskar_Ore></mineableCounts></genStep></GenStepDef>" % n
              for n in ("Asteroid", "Asteroid_NoRuins"))
    + "<SitePartDef><defName>WorkSite_Mining</defName><lootTable><li><thing>Gold</thing><weight>1</weight></li><li><thing>OuterRim_Beskar</thing><weight>0.15</weight></li><li><thing>OuterRim_PureBeskar</thing><weight>0.1</weight></li></lootTable></SitePartDef>"
    "<RecipeDef><defName>kotor_IngotBeskar_recipe</defName><products><KOTOR_IngotBeskar>1</KOTOR_IngotBeskar></products></RecipeDef>"
    "<RecipeDef><defName>kotor_IngotBeskar_10xrecipe</defName><products><KOTOR_IngotBeskar>10</KOTOR_IngotBeskar></products></RecipeDef>"
    "</Defs>")
BESKAR = ("KOTOR_IngotBeskar", "KOTOR_RawBeskar", "OuterRim_Beskar", "OuterRim_PureBeskar")


def beskar_check(patch_path=None):
    """L7 replay + source. Returns problems."""
    from lxml import etree as LX
    patch_path = patch_path or BESKAR_PATCH
    if not os.path.exists(patch_path):
        return ["beskar patch missing"]
    root = LX.fromstring(BESKAR_FIXTURE)
    replay(root, LX.parse(patch_path), ALL_MODS)
    bad = []
    for r in root.xpath("//RecipeDef"):
        if any(c.tag in BESKAR for c in r.find("products")):
            bad.append("recipe %s still makes beskar" % r.findtext("defName"))
    for n in ("OuterRim_Beskar", "OuterRim_PureBeskar"):
        if root.xpath('//ThingDef[defName="%s"]/smeltable/text()' % n) != ["false"]:
            bad.append("%s smelts back to beskar (smeltable not false on the def)" % n)
        if root.xpath('//ThingDef[defName="%s"]/deepCommonality/text()' % n) not in (["0"], []):
            bad.append("%s still a deep-drill deposit" % n)
    for n in ("LKBeskar_Ore", "LKPureBeskar_Ore"):
        if root.xpath('//ThingDef[defName="%s"]/building/mineableScatterCommonality/text()' % n) != ["0"]:
            bad.append("%s still scatters" % n)
        if root.xpath('//GenStepDef//li[text()="%s"] | //GenStepDef//mineableCounts/%s' % (n, n)):
            bad.append("%s still placed by a GenStep" % n)
    if root.xpath('//SitePartDef[defName="WorkSite_Mining"]/lootTable/li[thing="OuterRim_Beskar" or thing="OuterRim_PureBeskar"]'):
        bad.append("mining worksite still loots beskar")
    if root.xpath('//GenStepDef[defName="Asteroid"]//MineableGold/text()') != ["33~42"] or not root.xpath('//li[thing="Gold"]'):
        bad.append("beskar patch removed more than beskar")
    return bad


def beskar_src_check():
    bad = []
    for p in xml_files(os.path.join(SRC, "RimStarWars")):
        r = parse(p)
        if r is None:
            continue
        for rd in r.iter("RecipeDef"):
            pr = rd.find("products")
            if pr is not None and any(c.tag in BESKAR for c in pr):
                bad.append("src recipe %s (%s) makes beskar" % (rd.findtext("defName"), os.path.basename(p)))
        for td in r.iter("ThingDef"):
            if td.findtext("defName") == "KOTOR_MineableBeskar":
                b = td.find("building")
                if b.findtext("mineableScatterCommonality") != "0" or b.findtext("mineablePreventMeteorite") != "true":
                    bad.append("KOTOR_MineableBeskar not zeroed+meteorite-proof in source")
            if td.findtext("defName") == "KOTOR_IngotBeskar" and td.findtext("smeltable") == "true":
                bad.append("KOTOR_IngotBeskar smeltable")
    return bad


# ---------------------------------------------------------------- phase 3 (2026-10-11): L7 lesser ores, L1/L7 Mines 2.0 shafts
KERNEL_CS = os.path.join(ARM, "Source", "Kernel", "RSW_ArmouryKernel.cs")
SMELT_CS = os.path.join(ARM, "Source", "CanonMaterials", "RSW_BeskarSmelt.cs")
GATE_CS = os.path.join(ARM, "Source", "CanonMaterials", "RSW_MineShaftCanonGate.cs")
CSPROJ = os.path.join(ARM, "Source", "JawaArmoury.csproj")
SETTINGS_CS = os.path.join(ARM, "Source", "RSW_ArmourySettings.cs")


def _read(p):
    return open(p, encoding="utf-8").read() if os.path.exists(p) else ""


def cs_array(text, name):
    """The string literals of `public static readonly string[] <name> = { ... };` in kernel text, or None if absent."""
    m = re.search(r"string\[\]\s+%s\s*=\s*\{(.*?)\};" % re.escape(name), text, re.S)
    return None if m is None else re.findall(r'"([^"]+)"', m.group(1))


def lesser_ores_check(kernel=None, smelt=None, csproj=None, settings=None):
    """L7 'smelting beskar yields lesser ores': the C# is wired the way Thing.SmeltProducts / Thing.Smeltable need (decompiled 1.6).
    Static: the behaviour itself is fuzzed by the Armoury selftest family `materials`. Returns problems."""
    kernel = _read(KERNEL_CS) if kernel is None else kernel
    smelt = _read(SMELT_CS) if smelt is None else smelt
    csproj = _read(CSPROJ) if csproj is None else csproj
    settings = _read(SETTINGS_CS) if settings is None else settings
    bad = []
    bes = cs_array(kernel, "Beskar")
    if bes is None:
        bad.append("kernel has no Beskar list")
    else:
        miss = [b for b in BESKAR if b not in bes]
        if miss:
            bad.append("kernel Beskar list misses %s (smelting it would return it or nothing)" % ", ".join(miss))
    if not smelt:
        bad.append("RSW_BeskarSmelt.cs missing")
    else:
        if not re.search(r"\[HarmonyPatch\(typeof\(Thing\),\s*nameof\(Thing\.SmeltProducts\)\)\]", smelt):
            bad.append("no postfix on Thing.SmeltProducts")
        if not re.search(r"\[HarmonyPatch\(typeof\(Thing\),\s*nameof\(Thing\.Smeltable\),\s*MethodType\.Getter\)\]", smelt):
            bad.append("no postfix on the Thing.Smeltable getter (beskar gear would stay unsmeltable: Stuff.smeltable is false)")
        for need in ("ThingDefOf.Steel", "ThingDefOf.ChunkSlagSteel", "CostListAdjusted(thing.Stuff", "RSW_MaterialsKernel.LesserOres",
                     "IsRelic()", "PatchApplier.Apply"):
            if need not in smelt:
                bad.append("RSW_BeskarSmelt.cs lacks %s" % need)
        if smelt.count("beskarLesserOresEnabled") < 3:
            bad.append("smelt patches not both gated on beskarLesserOresEnabled")
        if "IsBeskar(t.def.defName)) continue" not in smelt:
            bad.append("SmeltProducts postfix does not drop beskar the vanilla list yields")
    for f in ("CanonMaterials\\RSW_BeskarSmelt.cs", "CanonMaterials\\RSW_MineShaftCanonGate.cs"):
        if '<Compile Include="%s" />' % f not in csproj:
            bad.append("%s not in JawaArmoury.csproj (EnableDefaultCompileItems is false: it would compile into nothing)" % f)
    for fld in ("beskarLesserOresEnabled", "mineShaftCanonGateEnabled"):
        if not re.search(r"public static bool %s = true;" % fld, settings) or ('"%s"' % fld) not in settings:
            bad.append("setting %s missing, not default-on, or not scribed" % fld)
    return bad


def mineshaft_check(kernel=None, gate=None, recipes=None, rocks=None):
    """L1/L7 Mines 2.0: replay RSW_MineShaftCanonGate's rule (Mines prefixes + product in the kernel's banned list) over the live
    capture's Mines recipes. The must-unlist set is derived here independently: products of every zeroed/gated rock (GATED, read
    from the capture's mineableThing) plus every beskar def and Plasteel. Returns (problems, info)."""
    kernel = _read(KERNEL_CS) if kernel is None else kernel
    gate = _read(GATE_CS) if gate is None else gate
    bad, info = [], []
    banned = cs_array(kernel, "MineShaftBanned") or []
    prefixes = cs_array(kernel, "MineShaftPrefixes") or []
    if not banned or not prefixes:
        return ["kernel has no MineShaftBanned / MineShaftPrefixes"], info
    for need in ("MinesAutomated.CreateRecipeDefs", "MinesAutomatedExtension.OnStartup", "RunClassConstructor", "recipeUsers?.Clear()",
                 "allRecipesCached", "MinesAutomated_ThingDef_Mine", "mineShaftCanonGateEnabled"):
        if need not in gate:
            bad.append("RSW_MineShaftCanonGate.cs lacks %s" % need)
    if recipes is None or rocks is None:
        d = latest_capture()
        if not d:
            return bad + ["UNMEASURED: no capture for the Mines 2.0 replay"], info
        R = json.load(open(os.path.join(d, "RecipeDef.json")))["defs"]
        recipes = [(x["defName"], [p.get("thingDef") for p in (x["fields"].get("products") or [])]) for x in R]
        T = json.load(open(os.path.join(d, "ThingDef.json")))["defs"]
        rocks = {t["defName"]: ((t["fields"].get("building") or {}).get("mineableThing")) for t in T if t["defName"] in GATED or t["defName"] == "MineablePlasteel"}
    must = set(BESKAR) | {"Plasteel"} | {v for v in rocks.values() if v}
    mines = [(n, ps) for n, ps in recipes if any(n.startswith(px) for px in prefixes)]
    if not mines:
        return bad + ["SANITY: no Mines 2.0 recipe in the capture (prefixes wrong, or the mod not loaded)"], info
    unlisted = sorted(n for n, ps in mines if any(p in banned for p in ps))
    for n, ps in mines:
        hit = [p for p in ps if p in must]
        if hit and n not in unlisted:
            bad.append("Mines 2.0 shaft %s still makes %s" % (n, ", ".join(hit)))
    over = [n for n in unlisted if not any(p in must for p in dict(mines)[n])]
    info.append("Mines 2.0 replay: %d shaft recipes in capture, %d unlisted (%s); must-unlist products %d; unlisted beyond them: %s"
                % (len(mines), len(unlisted), ", ".join(u.split("_RecipeDef_")[-1] for u in unlisted), len(must), over or "none"))
    if not unlisted:
        bad.append("SANITY: the gate unlists nothing on the live capture")
    return bad, info


GATES_FIXTURE = ("<Defs><TileMutatorDef><defName>MineralRich</defName><resourceBlacklist><li>MineableObsidian</li></resourceBlacklist></TileMutatorDef>"
    + "".join("<ThingDef><defName>%s</defName><building><mineableScatterCommonality>0</mineableScatterCommonality></building></ThingDef>" % r
              for r in ("LKDurasteel_Ore", "LKBeskar_Ore", "LKPureBeskar_Ore"))
    + "<ThingDef><defName>KOTOR_MineableDurasteel</defName><building><mineablePreventMeteorite>true</mineablePreventMeteorite></building></ThingDef>"
    "<ThingDef><defName>KOTOR_MineableBeskar</defName><building><mineablePreventMeteorite>true</mineablePreventMeteorite></building></ThingDef>"
    "<ThingDef><defName>RSW_MineableDoonium</defName><building><mineablePreventMeteorite>true</mineablePreventMeteorite></building></ThingDef></Defs>")
GATED = ("LKDurasteel_Ore", "LKBeskar_Ore", "LKPureBeskar_Ore", "KOTOR_MineableDurasteel", "KOTOR_MineableBeskar", "RSW_MineableDoonium")


def gates_check(patch_path=None):
    from lxml import etree as LX
    patch_path = patch_path or GATES_PATCH
    if not os.path.exists(patch_path):
        return ["ore gates patch missing"]
    root = LX.fromstring(GATES_FIXTURE)
    replay(root, LX.parse(patch_path), ALL_MODS)
    bad = []
    bl = root.xpath('//TileMutatorDef[defName="MineralRich"]/resourceBlacklist/li/text()')
    for r in GATED:
        if r not in bl:
            bad.append("%s not on MineralRich resourceBlacklist (mineral-rich tiles would scatter it)" % r)
        if root.xpath('//ThingDef[defName="%s"]/building/mineablePreventMeteorite/text()' % r) != ["true"]:
            bad.append("%s can fall as a meteorite" % r)
    if "MineableObsidian" not in bl:
        bad.append("gates patch dropped the vanilla blacklist row")
    return bad


ROLE_FILES = {
    "RM_CloakLacquer": os.path.join(SRC, "RimMandrake", "Scarlands", "Defs", "ThingDefs_Items", "RM_CloakLacquer.xml"),
    "RUT_Mindstone": os.path.join(SRC, "RimUtinni", "UtinniPatches", "Defs", "ThingDefs_Items", "RUT_Mindstone.xml"),
    "RSW_Leather_KraytDragon": os.path.join(SRC, "RimStarWars", "SWBestiary", "Defs", "ThingDefs_Items", "RSW_MlieWaveC_Resources.xml"),
}


def role_problems(name, desc):
    """L8: section 3.9 roles. Mindstone: the droid-mind crystal; the legend's droid fear (mindstone_arc_legends.md Entry I,
    owner-ruled lore) is consistent with that and is kept. Lacquer: personal only, never a ship. Krayt: ordinary top leather."""
    d = (desc or "").lower()
    if name == "RUT_Mindstone":
        return [] if re.search(r"droid'?s? (head|mind)|hold a mind|droid-mind", d) and "machine" in d else ["mindstone description does not give the droid-mind role"]
    if name == "RM_CloakLacquer":
        return [] if re.search(r"(never|no amount|not)[^.]{0,60}\bship", d) else ["cloak lacquer description does not rule out ships"]
    if name == "RSW_Leather_KraytDragon":
        b = ["krayt hide description carries a special rule (%s)" % w for w in ("heirloom", "beskar", "quest", "sacred") if w in d]
        return b + ([] if "ordinary" in d or "best of the hides" in d else ["krayt hide description does not read as an ordinary top leather"])
    return ["unknown role " + name]


def roles_check():
    bad, info = [], []
    for n, p in ROLE_FILES.items():
        r = parse(p)
        desc = None
        if r is not None:
            for td in r.iter("ThingDef"):
                if td.findtext("defName") == n:
                    desc = td.findtext("description")
        if desc is None:
            bad.append("%s not found in %s" % (n, os.path.basename(p)))
            continue
        bad += role_problems(n, desc)
    # DefInjected overrides would replace the text in game: none may exist
    for p in glob.glob(os.path.join(SRC, "*", "*", "Languages", "*", "DefInjected", "**", "*.xml"), recursive=True):
        txt = open(p, encoding="utf-8", errors="ignore").read()
        for n in ROLE_FILES:
            if "<%s.description>" % n in txt:
                bad.append("%s description overridden by %s" % (n, os.path.relpath(p, SRC)))
    info.append("3 role descriptions read from src; DefInjected overrides: none" if not [b for b in bad if "overridden" in b] else "")
    return bad, info


# ---------------------------------------------------------------- phase 4 (2026-10-11): L6 trade goods, stygium conversion
TRADE_PATCH = os.path.join(ARM, "Patches", "RSW_CanonMaterialsTrade.xml")
STYG_PATCH = os.path.join(ARM, "Patches", "RSW_StygiumConvert.xml")
ORBITAL_KINDS = ("Orbital_Exotic", "OuterRim_OrbitalTrade_CzerkaCorp")
TRADE_ONLY = ("RSW_Stygium", "RSW_Coaxium")
ALIAS_FILE = os.path.join(SRC, "RimMandrake", "EnvironmentalHazards", "Defs", "Misc", "RM_MaterialMerges_Aliases.xml")
LANTERN_PATCH = os.path.join(SRC, "RimUtinni", "UtinniPatches", "Patches", "RUT_LanternstoneKotorCrystals.xml")
# Files allowed to name a trade-only material: its own def, the trade rows, the conversion (consumer renames), the save alias.
TRADE_ONLY_ALLOWED = {os.path.join(ARM, "Defs", "ThingDefs", "RSW_Stygium.xml"), os.path.join(ARM, "Defs", "ThingDefs", "RSW_Coaxium.xml"),
                      TRADE_PATCH, STYG_PATCH, ALIAS_FILE}
# Every src file that names the donor stygium item or formation, and why it is covered (the fixture below copies its shape).
STYG_DONOR_FILES = {
    "Absorbed_KotorCore_KotORResource_Stygium.xml": "the donor item + formation (yield stripped, item removed)",
    "Absorbed_KotorCore_CrystalMapGenerator.xml": "KOTOR_CrystalFormation genstep row (removed)",
    "Absorbed_KotorCore_GadgetApparel_SWStealthBelts.xml": "costList 1 (renamed, count kept)",
    "Absorbed_KotorWeapons_GadgetApparel_KotORStealthBelts.xml": "costList 4 (renamed, count kept)",
    "Absorbed_Kotorweapons_TheForceLightsabers_HiltPartDefs_KotORPowerCrystals.xml": "hilt part requiredComponent (replaced)",
    "RUT_LanternDeepGateKotorStygium.xml": "prose only (comment)",
}
TRADE_FIXTURE = ("<Defs>" + "".join(
    "<TraderKindDef><defName>%s</defName><orbital>true</orbital><stockGenerators><li Class=\"StockGenerator_SingleDef\"><thingDef>Silver</thingDef>"
    "<countRange>2000~4000</countRange></li></stockGenerators></TraderKindDef>" % k for k in ORBITAL_KINDS) + "</Defs>")
# Shapes copied from the Armoury's absorbed defs (KotORResource_Stygium.xml, CrystalMapGenerator.xml, the two stealth-belt files,
# the hilt-part file), not invented.
STYG_FIXTURE = ("<Defs>"
    "<ThingDef ParentName=\"KOTOR_CrystalFormation_Base\"><defName>KOTOR_StygiumCrystal</defName><building/><modExtensions>"
    "<li Class=\"SecondaryMineableYield.ModExtension_SecondaryMineableYield\"><mineableDropChance>1.0</mineableDropChance><entries>"
    "<li><randomWeight>0.60</randomWeight><mineableThing>guy762_crystalitem_stygium</mineableThing><mineableYield>3</mineableYield></li>"
    "</entries></li></modExtensions></ThingDef>"
    "<ThingDef ParentName=\"guy762_crystalbase\"><defName>guy762_crystalitem_stygium</defName><tradeTags><li>ExoticMisc</li></tradeTags>"
    "<thingSetMakerTags><li>RewardStandardLowFreq</li></thingSetMakerTags></ThingDef>"
    "<GenStepDef><defName>KOTOR_CrystalFormation</defName><genStep><groups><li><things><KOTOR_SmallCrystal_red>0.15</KOTOR_SmallCrystal_red>"
    "<KOTOR_StygiumCrystal>0.15</KOTOR_StygiumCrystal></things></li></groups></genStep></GenStepDef>"
    "<ThingDef><defName>guy762_stealthbelt</defName><costList><ComponentSpacer>2</ComponentSpacer><guy762_crystalitem_stygium>1</guy762_crystalitem_stygium></costList></ThingDef>"
    "<ThingDef><defName>guy762_stealthbelt_kotor</defName><costList><guy762_crystalitem_stygium>4</guy762_crystalitem_stygium></costList></ThingDef>"
    "<Lightsaber.HiltPartDef><defName>guy762_SWForceLightsabers_CrystalPart_stygium</defName><requiredComponent>guy762_crystalitem_stygium</requiredComponent></Lightsaber.HiltPartDef>"
    "<RecipeDef><defName>ZZ_FilterProbe</defName><fixedIngredientFilter><thingDefs><li>guy762_crystalitem_stygium</li></thingDefs></fixedIngredientFilter></RecipeDef>"
    "</Defs>")


def owned_def(name, path=None):
    r = parse(path or os.path.join(ARM, "Defs", "ThingDefs", name + ".xml"))
    if r is None:
        return None
    for td in r.iter("ThingDef"):
        if td.findtext("defName") == name:
            return td
    return None


def l6_defs_check(override=None):
    """Each of the six is defined with a label and a canon description, trader-sellable; stygium says it cloaks ships, coaxium
    carries its cold/explodes hazard; the two trade-only ones carry no reward tag. override = {name: ThingDef element}."""
    bad = []
    for n in OWNED_ROLES:
        td = (override or {}).get(n, owned_def(n))
        if td is None:
            bad.append("%s not defined in Defs/ThingDefs/%s.xml" % (n, n))
            continue
        d = (td.findtext("description") or "").lower()
        if not (td.findtext("label") or "").strip() or len(d) < 40:
            bad.append("%s has no label or no real description" % n)
        if (td.findtext("tradeability") or "All").strip() not in ("All", "Sellable"):
            bad.append("%s tradeability %r: traders cannot sell it" % (n, td.findtext("tradeability")))
        if n == "RSW_Stygium" and not (re.search(r"cloak", d) and re.search(r"\bships?\b", d)):
            bad.append("stygium description does not say it cloaks ships")
        if n == "RSW_Coaxium" and not (re.search(r"\bcold\b", d) and re.search(r"explod", d)):
            bad.append("coaxium description lacks its canon hazard (kept cold, explodes)")
        if n in TRADE_ONLY:
            for tag in ("thingSetMakerTags", "butcherProducts", "smeltProducts", "killedLeavings"):
                if td.find(tag) is not None:
                    bad.append("%s carries <%s>: a second source" % (n, tag))
            if (td.findtext("building/mineableThing") or "").strip():
                bad.append("%s is a mineable" % n)
    return bad


def trade_check(patch_path=None):
    """Replay the trade patch on orbital trader fixtures: every one of the six gets a SingleDef row in each orbital kind, with a
    countRange that can come out empty (low frequency) and can come out positive; nothing already there is touched."""
    from lxml import etree as LX
    patch_path = patch_path or TRADE_PATCH
    if not os.path.exists(patch_path):
        return ["trade patch missing"]
    root = LX.fromstring(TRADE_FIXTURE)
    replay(root, LX.parse(patch_path), ALL_MODS | {"Outer Rim - Core"})
    bad = []
    for k in ORBITAL_KINDS:
        rows = {}
        for li in root.xpath('//TraderKindDef[defName="%s"]/stockGenerators/li[@Class="StockGenerator_SingleDef"]' % k):
            rows[li.findtext("thingDef")] = li.findtext("countRange")
        if rows.get("Silver") != "2000~4000":
            bad.append("%s: the trade patch disturbed existing stock" % k)
        for n in OWNED_ROLES:
            cr = rows.get(n)
            if cr is None:
                bad.append("%s does not stock %s" % (k, n))
                continue
            m = re.fullmatch(r"(-?\d+)~(-?\d+)", cr.strip())
            if not m or int(m.group(2)) <= 0:
                bad.append("%s stocks %s with countRange %r: never any" % (k, n, cr))
            elif int(m.group(1)) > 0:
                bad.append("%s stocks %s on every visit (%s): not low frequency" % (k, n, cr))
    return bad


def sole_source_check(extra=None):
    """Stygium and coaxium have no source but trade: no src file outside TRADE_ONLY_ALLOWED may name them at all (a product,
    a mineable, a leaving, a genstep, a reward list or a recipe ingredient would each show up here). extra = {path: xml}."""
    bad = []
    items = [(p, None) for p in xml_files(SRC)] + list((extra or {}).items())
    for p, txt in items:
        if p in TRADE_ONLY_ALLOWED:
            continue
        if txt is None:
            try:
                txt = open(p, encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
        for n in TRADE_ONLY:
            if re.search(r"(<|>)%s\b" % n, txt):
                bad.append("%s named in %s: trade-only materials may have no other route" % (n, os.path.relpath(p, SRC)))
    return bad


def stygium_convert_check(patch_path=None, lantern=None, alias=None, extra_files=None):
    """Replay RSW_StygiumConvert.xml on donor-shaped fixtures, then check the Lantern Deeps source, the save alias, and that every
    src file naming the donor stygium is one the fixture covers. Returns problems."""
    from lxml import etree as LX
    patch_path = patch_path or STYG_PATCH
    if not os.path.exists(patch_path):
        return ["stygium conversion patch missing"]
    root = LX.fromstring(STYG_FIXTURE)
    replay(root, LX.parse(patch_path), ALL_MODS)
    bad = []
    left = LX.tostring(root).decode()
    if "guy762_crystalitem_stygium" in left:
        bad.append("donor stygium still named after the patch (%d places)" % left.count("guy762_crystalitem_stygium"))
    if not root.xpath('//ThingDef[defName="KOTOR_StygiumCrystal"]'):
        bad.append("the formation def was removed (it must stay loadable for saves)")
    if root.xpath('//ThingDef[defName="KOTOR_StygiumCrystal"]//mineableThing'):
        bad.append("the stygium formation still yields when mined")
    if root.xpath('//GenStepDef//things/KOTOR_StygiumCrystal'):
        bad.append("a genstep still places the stygium formation")
    if root.xpath('//GenStepDef//things/KOTOR_SmallCrystal_red/text()') != ["0.15"]:
        bad.append("the patch removed other crystal rows")
    if root.xpath('//ThingDef[defName="guy762_crystalitem_stygium"]'):
        bad.append("donor stygium item still defined")
    for belt, want in (("guy762_stealthbelt", "1"), ("guy762_stealthbelt_kotor", "4")):
        got = root.xpath('//ThingDef[defName="%s"]/costList/RSW_Stygium/text()' % belt)
        if got != [want]:
            bad.append("%s costs %r RSW_Stygium, want %s" % (belt, got, want))
    if root.xpath('//requiredComponent/text()') != ["RSW_Stygium"]:
        bad.append("stygium hilt part does not require RSW_Stygium")
    lt = _read(LANTERN_PATCH) if lantern is None else lantern
    if "<KOTOR_StygiumCrystal>" in lt:
        bad.append("RUT_LanternstoneKotorCrystals.xml still places the stygium formation in the Lantern Deeps")
    al = _read(ALIAS_FILE) if alias is None else alias
    if "<from>guy762_crystalitem_stygium</from><to>RSW_Stygium</to>" not in al:
        bad.append("no save alias guy762_crystalitem_stygium -> RSW_Stygium")
    found = set()
    for p in list(xml_files(SRC)) + list(extra_files or []):
        txt = open(p, encoding="utf-8", errors="ignore").read() if os.path.exists(p) else (extra_files or {}).get(p, "")
        if p in TRADE_ONLY_ALLOWED:
            continue
        if "guy762_crystalitem_stygium" in txt or "KOTOR_StygiumCrystal" in txt:
            found.add(os.path.basename(p))
    for f in sorted(found - set(STYG_DONOR_FILES) - {"RUT_LanternstoneKotorCrystals.xml"}):
        bad.append("%s names the donor stygium and is not covered by the conversion fixture" % f)
    if not found & set(STYG_DONOR_FILES):
        bad.append("SANITY: the donor-stygium census found none of the known files")
    return bad


def universe_and_refs():
    names, tex, capdir = capture_universe()
    mine = src_defnames()
    lines = []
    if names is None:
        return None, None, None, ["UNMEASURED: no DefDump capture reachable"]
    U = names | set(mine)
    # sanity probes: must find, must not find
    must = ["Steel", "Plasteel", "ResourcesRaw", "ElectricSmelter", "RSW_Durasteel"]
    gone = ["ZZ_NoSuchDef_Probe", "KOTOR_AlloyBronzium_ZZ"]
    miss = [m for m in must if m not in U]
    found = [g for g in gone if g in U]
    if miss or found:
        return None, None, None, ["SANITY PROBE FAILED: missing %r, spurious %r" % (miss, found)]
    lines.append("universe %d names (capture %s + %d src); probes ok (%d present, %d absent)" % (len(U), os.path.basename(os.path.dirname(capdir)), len(mine), len(must), len(gone)))
    return U, tex, mine, lines


def run():
    info_l1 = []
    U, cap_tex, mine, ulines = universe_and_refs()
    from modcheck import Suite  # noqa: F401  (validation.py imports it)
    sys.path.insert(0, ARM)
    import validation as v
    import canon_materials_audit as cma

    static = {}
    for fn in ("durasteel_static", "durasteel_convert_static", "durasteel_outerrim_static", "plasteel_cut_static",
               "transparisteel_fold_static", "ores_and_smelts_static"):
        static[fn] = getattr(v, fn)()
    # ---- reference resolution over every material-owned file
    unresolved, nrefs = [], 0
    files = [os.path.join(ARM, "Defs", "ThingDefs", n + ".xml") for n in MAT_DEFS] + \
            [os.path.join(ARM, "Patches", n + ".xml") for n in MAT_PATCHES]
    missing_files = [f for f in files if not os.path.exists(f)]
    if U is not None:
        for f in files:
            r = parse(f)
            if r is None:
                unresolved.append((os.path.basename(f), "XML", "does not parse"))
                continue
            for tag, name in refs_in(r):
                nrefs += 1
                if name not in U:
                    unresolved.append((os.path.basename(f), tag, name))
    # ---- textures
    texbad, texn = [], 0
    for n in MAT_DEFS + ["RSW_Phrikite", "RSW_DooniumOre"]:
        p = os.path.join(ARM, "Defs", "ThingDefs", n + ".xml")
        if not os.path.exists(p):
            continue
        for tp in ET.parse(p).getroot().iter("texPath"):
            texn += 1
            if not tex_ok(tp.text.strip(), cap_tex):
                texbad.append(tp.text.strip())
    # ---- L1 stats + producers
    l1 = []
    dur = parse(os.path.join(ARM, "Defs", "ThingDefs", "RSW_Durasteel.xml"))
    donor_xml = git_show(DONOR_REV + "^", DONOR_FILE)
    donor = ET.fromstring(donor_xml) if donor_xml else None

    def stats(root, name):
        for td in root.iter("ThingDef"):
            if td.findtext("defName") == name:
                sb, sf = td.find("statBases"), td.find("stuffProps/statFactors")
                return ({c.tag: c.text for c in sb} if sb is not None else {}), ({c.tag: c.text for c in sf} if sf is not None else {})
        return None, None
    if dur is None:
        l1.append("RSW_Durasteel.xml missing")
    else:
        ds, df = stats(dur, "RSW_Durasteel")
        os_, of = stats(donor, "KOTOR_AlloyDurasteel") if donor is not None else (None, None)
        if os_ is not None:   # donor ParentName KOTOR_Metal (abstract) supplies Beauty -1 and stuff defaults
            ps, pf = stats(donor, "KOTOR_Metal")
            os_ = dict(ps or {}, **os_)
            of = dict(pf or {}, **of)
        if os_ is None:
            l1.append("UNMEASURED: donor def not readable from git %s^ (stat equality unproven)" % DONOR_REV)
        else:
            if ds.get("StuffPower_Armor_Sharp") != "0.9":
                l1.append("sharp armor power %r, want 0.9" % ds.get("StuffPower_Armor_Sharp"))
            diff = {k: (os_.get(k), ds.get(k)) for k in set(os_) | set(ds) if k != "StuffPower_Armor_Sharp" and os_.get(k) != ds.get(k)}
            fd = {k: (of.get(k), df.get(k)) for k in set(of) | set(df) if of.get(k) != df.get(k)}
            if diff:
                l1.append("statBases differ from donor beyond sharp armor: %r" % diff)
            if fd:
                l1.append("stuff statFactors differ from donor: %r" % fd)
            info_l1.append("stat probe: donor sharp was %s -> ours %s; %d donor statBases compared" % (os_.get("StuffPower_Armor_Sharp"), ds.get("StuffPower_Armor_Sharp"), len(os_)))
        # producers still alive in the pre-patch live capture, and the patch that must zero each
        prod = capture_producers()
        if prod is None:
            l1.append("UNMEASURED: no capture to census producers")
        else:
            info_l1.append("capture census (pre-patch): %s" % prod["summary"])
            l1 += producers_zeroed(prod)
        l1 += static["durasteel_convert_static"] + static["durasteel_static"]
        l1 += gates_check() + patch_classes_bad(ZERO_PATCH)   # 2026-10-11: the first zero patch used a non-vanilla op class
        ms, msi = mineshaft_check()
        l1 += ms
        info_l1 += msi
    put("L1", "FAIL" if [x for x in l1 if not x.startswith(("UNMEASURED", "OWED"))] else ("PARTIAL" if l1 else "PASS"), *(info_l1 + l1 or ["RSW_Durasteel stats == KOTOR_AlloyDurasteel's except sharp 0.9; no mineable/deep-drill/recipe producer in src; forge route static shape ok"]))
    # ---- L2
    l2 = static["durasteel_convert_static"] + static["durasteel_outerrim_static"]
    put("L2", "FAIL" if l2 else "PASS", *(l2 or ["donor durasteel (KOTOR + OuterRim) redirected, counts matched, recipes + donor defs removed by patch, aliases kept for saves; salvage re-melt covered by L4 remelt check"]))
    # ---- L3 (audit written to the item/doc by the caller)
    import io, contextlib
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            rc = cma.main() if hasattr(cma, "main") else 0
    except SystemExit as e:
        rc = e.code or 0
    out = buf.getvalue()
    info = [l for l in out.splitlines() if "INFO" in l]
    put("L3", "FAIL" if rc else "PASS", *(info + ["canon_materials_audit exit %s; filters+fixed audits printed above" % rc]))
    # ---- L4
    l4 = static["plasteel_cut_static"] + static["ores_and_smelts_static"]
    put("L4", "FAIL" if l4 else "PASS", *(l4 or ["kotor_Plasteel_recipe(+10x) / Make_PlasteelGF / Make_PlasteelComposite cut; Odyssey allowlist drops MineablePlasteel+MineableComponentsIndustrial; plasteel + durasteel slag re-melt at the smelter (cma remelt)"]))
    # ---- L5/L6/L7/L8/L9: what exists
    have = [n for n in OWNED_ROLES if n in (mine or {})]
    lack = [n for n in OWNED_ROLES if n not in (mine or {})]
    # ---- L5 salvage by composition
    l5, l5i = salvage_check()
    b1b, b1i = b1_other_routes()
    l5 += [b for b in b1b if not b.startswith("UNMEASURED")]
    l5 += patch_classes_bad(SALVAGE_PATCH)
    put("L5", "FAIL" if l5 else "PASS", *(l5i + b1i + l5 + ([] if l5 else ["RSW_Duranium defined (Defs/ThingDefs/RSW_Duranium.xml); amounts PROVISIONAL"])))
    l6 = l6_defs_check() + trade_check() + sole_source_check() + stygium_convert_check()
    l6 += patch_classes_bad(TRADE_PATCH) + patch_classes_bad(STYG_PATCH)
    put("L6", "FAIL" if (l6 and not lack) else ("PARTIAL" if lack else "PASS"), *(["defined: %s" % ", ".join(have)] + (["NOT defined: %s" % ", ".join(lack)] if lack else []) + l6 + ([] if l6 else [
        "orbital stock (Orbital_Exotic + Czerka) for all six, low-frequency rows (PROVISIONAL counts); the Bazaar is the window over that stock",
        "stygium + coaxium: no src file outside their def/trade/convert/alias names them; stygium says it cloaks ships, coaxium carries its hazard",
        "donor stygium: formation yield stripped and out of every genstep (Lantern Deeps rows deleted at source), consumers renamed with counts kept, item removed, save alias added"])))
    # ---- L7 beskar never reforged
    l7 = beskar_check() + beskar_src_check() + patch_classes_bad(BESKAR_PATCH)
    gates = gates_check() + patch_classes_bad(GATES_PATCH) + patch_classes_bad(ZERO_PATCH)
    l7 += lesser_ores_check()
    ms7, msi7 = mineshaft_check()
    l7 += [x for x in ms7 if not x.startswith("UNMEASURED")]
    put("L7", "FAIL" if (l7 or gates) else ("PARTIAL" if [x for x in ms7 if x.startswith("UNMEASURED")] else "PASS"), *(l7 + gates + msi7 + [
        "kotor_IngotBeskar_recipe(+10x) deleted from src and FindMod-removed from the donor; Outer Rim beskars smeltable=false; "
        "LK beskar rocks unscattered + out of PreciousLump/asteroids; deep deposits 0; worksite loot rows removed; "
        "meteorite + MineralRich gates on every zeroed rock (replayed on donor-shaped fixtures)",
        "smelting beskar gear: smeltable again via the Thing.Smeltable postfix, returns steel (vanilla 25% share) + 1 slag chunk, never beskar "
        "(RSW_BeskarSmelt.cs; behaviour fuzzed: selftest_armoury_fuzz.py --fuzz-only materials); Mines 2.0 shafts unlisted by product "
        "(RSW_MineShaftCanonGate.cs). Live behaviour is L10's load"] + [x for x in ms7 if x.startswith("UNMEASURED")]))
    # ---- L8 roles
    l8, l8i = roles_check()
    put("L8", "FAIL" if l8 else "PASS", *(l8 + [x for x in l8i if x] + ([] if l8 else [
        "lacquer: personal only, never a ship; mindstone: droid-mind crystal (legend's droid fear kept, owner-ruled lore); krayt: ordinary top leather"])))
    # ---- L9 key-job census
    import canon_materials_census as cen
    cd = latest_capture()
    if not cd:
        put("L9", "OWED", "UNMEASURED: no capture for the census")
    else:
        rows = cen.census(cd)
        pb = cen.probes(rows)
        if pb:
            put("L9", "FAIL", "census probes failed: %r" % pb)
        else:
            sm = cen.summarize(rows)
            lines = ["census %d consumer rows, probes 5/5 (python3 canon_materials_census.py --csv <out>)" % len(rows)]
            for job, s in sm.items():
                lines.append("%-21s right %-13s %s" % (job, s["right"], ("FIXED in %d: %s" % (len(s["fixed_right"]), ", ".join(s["fixed_right"][:4]))) if s["enforced"] else "preference only"))
            lines.append("RULING CONFLICT: item L9/design 4 say preferences only; the later card (2026-10-09 15:01, BENCH note) says plasteel "
                         "HARD for droid shells + prosthetics, duranium HARD for large frames, doonium HARD for cores. Census measures; verdict waits")
            put("L9", "PARTIAL", *lines)
    put("L10", "OWED", "live minimal-list load required (L1 level)")
    # ---- cross-cutting
    xr = []
    xr.append("ref resolution: %d refs in %d material-owned files; %d unresolved" % (nrefs, len(files) - len(missing_files), len(unresolved)))
    for u in unresolved:
        xr.append("  UNRESOLVED %s: <%s> %s" % u)
    xr.append("textures: %d texPaths, %d unresolved %r" % (texn, len(texbad), texbad))
    xr.append("missing material files: %r" % missing_files)
    return ulines, xr, bool(unresolved or texbad or missing_files)


def selftest():
    # planted defect: a ref that cannot resolve is caught; a real one resolves
    r = ET.fromstring("<Defs><RecipeDef><ingredients><li><filter><thingDefs><li>Steel</li><li>NoSuchMat_ZZ</li></thingDefs></filter></li></ingredients></RecipeDef></Defs>")
    got = [n for _, n in refs_in(r)]
    assert got == ["Steel", "NoSuchMat_ZZ"], got
    assert tex_ok("Things/Item/Resource/NoSuchTex_ZZ", set()) is None
    import tempfile
    prod = {"ores": {"LKDurasteel_Ore": (0.5, 0)}, "gen": {"LKDurasteel_Ore": ["PreciousLump"]}, "kotor_scatter": 0.15}
    with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False) as f:
        f.write("<Patch></Patch>")
    try:
        planted = producers_zeroed(prod, f.name)
    finally:
        os.unlink(f.name)
    assert len(planted) >= 6, planted          # an empty patch must leave every producer standing and be named
    assert producers_zeroed(prod) == [], producers_zeroed(prod)   # the shipped patch zeroes them all
    # phase 2 planted defects: each checker must go red on a defect and green on the shipped file
    with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False) as f:
        f.write("<Patch></Patch>")
    try:
        assert len(salvage_check(f.name)[0]) >= 8, salvage_check(f.name)
        assert len(beskar_check(f.name)) >= 7, beskar_check(f.name)
        assert len(gates_check(f.name)) >= 9, gates_check(f.name)
    finally:
        os.unlink(f.name)
    assert salvage_check()[0] == [], salvage_check()[0]
    dbl = salvage_check(b1_extra="<butcherProducts><Plasteel>5</Plasteel></butcherProducts>")[0]
    assert len([x for x in dbl if "butcher routes = 2" in x]) == 3, dbl        # a pre-existing plasteel route is caught
    assert beskar_check() == [], beskar_check()
    assert gates_check() == [], gates_check()
    with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False) as f:
        f.write('<Patch><Operation Class="PatchOperationAddOrReplace"><xpath>/Defs</xpath><value><a/></value></Operation></Patch>')
    try:
        assert len(patch_classes_bad(f.name)) == 1
    finally:
        os.unlink(f.name)
    for pth in (ZERO_PATCH, SALVAGE_PATCH, BESKAR_PATCH, GATES_PATCH):
        assert patch_classes_bad(pth) == [], patch_classes_bad(pth)
    old = {"RUT_Mindstone": "A fist-sized crystal ... as if it were learning the shape of your voice. Droids do not like to be near it.",
           "RM_CloakLacquer": "A shimmering film scraped from a chotrix's hide. It bends light. Worked into a cloak at a tailoring bench, it makes the wearer vanish while they stand still and unseen. The effect never wears off.",
           "RSW_Leather_KraytDragon": "Tanned krayt scales, an heirloom hide."}
    for n, d in old.items():
        assert role_problems(n, d), n                     # the pre-2026-10-11 texts (and an heirloom krayt) fail
    assert roles_check()[0] == [], roles_check()[0]
    # phase 3 planted defects: a kernel list missing a beskar, a csproj without the files, a gate whose banned list lacks Plasteel
    assert lesser_ores_check() == [], lesser_ores_check()
    k = _read(KERNEL_CS)
    assert any("misses OuterRim_PureBeskar" in x for x in lesser_ores_check(kernel=k.replace('"OuterRim_PureBeskar" };', '};'))), "dropped beskar not caught"
    assert len([x for x in lesser_ores_check(csproj="") if "csproj" in x]) == 2
    assert len(lesser_ores_check(smelt="")) >= 1 and len(lesser_ores_check(settings="")) == 2
    fake_rocks = {"LKBeskar_Ore": "OuterRim_Beskar", "MineablePlasteel": "Plasteel", "KOTOR_MineableDurasteel": "KotORChunk_durasteel"}
    fake = [("MinesAutomated_RecipeDef_MineableSteel", ["Steel"]), ("MinesAutomated_RecipeDef_LKBeskar_Ore", ["OuterRim_Beskar"]),
            ("MinesAutomated_RecipeDef_MineablePlasteel", ["Plasteel"]), ("MinesAutomated_RecipeDef_KOTOR_MineableDurasteel", ["KotORChunk_durasteel"]),
            ("MinesAutomatedExtension_RecipeDef_OuterRim_PureBeskar", ["OuterRim_PureBeskar"]), ("Make_Plasteel", ["Plasteel"])]
    assert mineshaft_check(recipes=fake, rocks=fake_rocks)[0] == [], mineshaft_check(recipes=fake, rocks=fake_rocks)
    planted_k = k.replace('"KotORChunk_durasteel", "Plasteel", "RSW_DooniumOre",', '"KotORChunk_durasteel", "RSW_DooniumOre",')
    assert planted_k != k
    pb = mineshaft_check(kernel=planted_k, recipes=fake, rocks=fake_rocks)[0]
    assert pb == ["Mines 2.0 shaft MinesAutomated_RecipeDef_MineablePlasteel still makes Plasteel"], pb
    assert any("SANITY" in x for x in mineshaft_check(recipes=[("Make_Steel", ["Steel"])], rocks=fake_rocks)[0])
    assert any("lacks recipeUsers" in x for x in mineshaft_check(gate="", recipes=fake, rocks=fake_rocks)[0])
    # phase 4 planted defects: L6
    assert l6_defs_check() == [], l6_defs_check()
    assert trade_check() == [], trade_check()
    assert sole_source_check() == [], sole_source_check()
    assert stygium_convert_check() == [], stygium_convert_check()
    with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False) as f:
        f.write("<Patch></Patch>")
    try:
        assert len(trade_check(f.name)) == 12, trade_check(f.name)                   # 6 materials x 2 traders unstocked
        assert len(stygium_convert_check(f.name)) >= 6, stygium_convert_check(f.name)
    finally:
        os.unlink(f.name)
    ev = ET.fromstring("<ThingDef><defName>RSW_Stygium</defName><label>stygium</label><description>Rare crystals that bend light; "
                       "used in stealth fields worn by a few people.</description><thingSetMakerTags><li>RewardStandardLowFreq</li></thingSetMakerTags></ThingDef>")
    pl = l6_defs_check({"RSW_Stygium": ev})
    assert any("cloaks ships" in x for x in pl) and any("thingSetMakerTags" in x for x in pl), pl
    with open(TRADE_PATCH, encoding="utf-8") as fh:
        tp = fh.read()
    with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False) as f:
        f.write(tp.replace("<countRange>-4~2</countRange>", "<countRange>1~2</countRange>"))
    try:
        assert [x for x in trade_check(f.name)] == ["Orbital_Exotic stocks RSW_Stygium on every visit (1~2): not low frequency",
                                                   "OuterRim_OrbitalTrade_CzerkaCorp stocks RSW_Stygium on every visit (1~2): not low frequency"], trade_check(f.name)
    finally:
        os.unlink(f.name)
    leak = os.path.join(SRC, "RimMandrake", "ZZ_Planted", "Recipe.xml")
    assert sole_source_check({leak: "<Defs><RecipeDef><products><RSW_Coaxium>5</RSW_Coaxium></products></RecipeDef></Defs>"}) == \
        ["RSW_Coaxium named in RimMandrake/ZZ_Planted/Recipe.xml: trade-only materials may have no other route"]
    assert any("Lantern Deeps" in x for x in stygium_convert_check(lantern="<things><KOTOR_StygiumCrystal>0.08</KOTOR_StygiumCrystal></things>"))
    assert any("save alias" in x for x in stygium_convert_check(alias=""))
    assert stygium_convert_check(extra_files={leak: "<Defs><ThingDef><costList><guy762_crystalitem_stygium>2</guy762_crystalitem_stygium></costList></ThingDef></Defs>"}) == \
        ["Recipe.xml names the donor stygium and is not covered by the conversion fixture"]
    print("selftest ok (empty patch leaves %d producer findings; shipped patch leaves 0; L5/L7/gates/L8 planted defects red, shipped green)" % len(planted))


def main():
    if "--selftest" in sys.argv:
        selftest()
        return 0
    selftest()
    ulines, xr, bad = run()
    for l in ulines:
        print(l)
    for cid in ("L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8", "L9", "L10"):
        v, ls = R[cid]
        print("%-4s %s" % (cid, v))
        for l in ls:
            print("       " + l)
    print("--")
    for l in xr:
        print(l)
    fails = [c for c, (v, _) in R.items() if v == "FAIL"]
    tally = {k: sum(1 for v, _ in R.values() if v == k) for k in ("PASS", "PARTIAL", "OWED", "FAIL")}
    print("TALLY", tally)
    return 1 if fails or bad else 0


if __name__ == "__main__":
    sys.exit(main())
