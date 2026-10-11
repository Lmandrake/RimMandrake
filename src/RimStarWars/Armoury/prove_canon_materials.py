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
CAPTURES = "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/DefDump/captures"

MAT_DEFS = ["RSW_Durasteel", "RSW_Doonium", "RSW_Phrik", "RSW_Transparisteel", "RSW_Zersium"]
MAT_PATCHES = ["RSW_AlloyForge_Durasteel", "RSW_DurasteelConvert", "RSW_DurasteelConvert_OuterRim", "RSW_OdysseyAsteroidNoPlasteel",
               "RSW_OdysseyAsteroid_Doonium", "RSW_PlasteelRecipesCut", "RSW_Smelter_Alloys", "RSW_Transparisteel_GlassFold"]
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
            if c.tag in ("products", "smeltProducts"):
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

    def replay(root, patch):
        def op(o):
            cls = o.get("Class")
            if cls == "PatchOperationFindMod":
                m = o.find("match")
                if m is not None:
                    op(m)
            elif cls == "PatchOperationSequence":
                for li in o.find("operations"):
                    op(li)
            elif cls == "PatchOperationRemove":
                for n in root.xpath(o.findtext("xpath")):
                    n.getparent().remove(n)
            elif cls == "PatchOperationAddOrReplace":
                xp = o.findtext("xpath")
                val = list(o.find("value"))[0]
                hits = root.xpath(xp)
                if hits:
                    hits[0].getparent().replace(hits[0], LX.fromstring(LX.tostring(val)))
                else:
                    par = root.xpath(xp.rsplit("/", 1)[0])
                    if par:
                        par[0].append(LX.fromstring(LX.tostring(val)))
            else:
                raise ValueError("sim does not know " + str(cls))
        for o in patch.getroot():
            op(o)

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
    replay(r1, LX.parse(patch_path))
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
    put("L1", "FAIL" if [x for x in l1 if not x.startswith("UNMEASURED")] else ("PARTIAL" if l1 else "PASS"), *(info_l1 + l1 or ["RSW_Durasteel stats == KOTOR_AlloyDurasteel's except sharp 0.9; no mineable/deep-drill/recipe producer in src; forge route static shape ok"]))
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
    put("L5", "OWED", "no salvage-by-composition patch: RSW_Duranium is undefined, and no ship-chunk / crashed-ship / B1-remains yield names durasteel+plasteel+duranium+doonium together (grep of src, 2026-10-11)")
    put("L6", "PARTIAL" if have else "OWED", "defined: %s" % ", ".join(have), "NOT defined: %s" % ", ".join(lack),
        "trader/Bazaar stock and KOTOR_StygiumCrystal / guy762 stygium conversion not built")
    beskar_live = any("kotor_IngotBeskar_recipe" in open(p, encoding="utf-8", errors="ignore").read()
                      for p in glob.glob(os.path.join(ARM, "Patches", "*.xml")))
    put("L7", "OWED", "kotor_IngotBeskar_recipe still defined in Metals2.xml and %s a removal patch in Armoury/Patches" % ("HAS" if beskar_live else "NO"))
    put("L8", "OWED", "RM_CloakLacquer says it cloaks the wearer but not 'never a ship'; RUT_Mindstone description does not say droid-mind crystal; krayt hide ok (no heirloom rule). Prose not yet written")
    put("L9", "OWED", "preference-only is a negative claim over every recipe and building; no census built, and 'layout grading' is a design page (Transient/canon_materials_jobs_layout_2026-10-09.html), not a def")
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
    print("selftest ok (empty patch leaves %d producer findings; shipped patch leaves 0)" % len(planted))


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
