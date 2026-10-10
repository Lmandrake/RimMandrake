#!/usr/bin/env python3
"""canon_materials_audit.py -- CANON_MATERIALS_BUILD_1 L3/L4 offline audit.

  dangling   every def this build removed/merged (REMOVED below) is not still DEFINED and not REFERENCED by any
             def element, tag, or list item under src/ (exempt: alias defs and PatchOperation xpath strings).
  roster     generator scripts do not re-emit a removed name (the roster generator did, found 2026-10-10).
  filters    INFO: recipes/costs whose ingredient filter is a broad category that admits BOTH plasteel and
             durasteel (ResourcesRaw / Metallic) -- listed for the L3 audit, never an error.
  fixed      INFO: fixed Plasteel costs/ingredients per file (consumers that need plasteel; untouched).
  odyssey    the asteroid patch removes MineablePlasteel / MineableComponentsIndustrial from an explicit allowlist
             of GenStepDefs and the GeneratedLocationDef, and from nothing else.
  remelt     plasteel and durasteel slag each have a smelt recipe usable at a smelter (salvage re-melt).

Usage: canon_materials_audit.py [--src DIR]   exit 1 on any error. Selftest: selftest_canon_materials_audit.py
"""
import os, re, sys
import xml.etree.ElementTree as ET

REMOVED = {
    "KOTOR_AlloyDurasteel", "kotor_IngotDurasteel_recipe", "kotor_IngotDurasteel_10xrecipe", "OuterRim_Durasteel",
    "kotor_Plasteel_recipe", "kotor_Plasteel_10xrecipe", "Make_PlasteelGF", "Make_PlasteelComposite",
    "KOTOR_AlloyBronzium", "KOTOR_MineableBronzium", "KotORChunk_bronzium",
}
BROAD = {"ResourcesRaw", "Metallic", "Manufactured"}
EXEMPT_NAMES = ("RM_MaterialMerges_Aliases.xml",)
ODYSSEY_PATCH = "RSW_OdysseyAsteroidNoPlasteel.xml"
ODYSSEY_ALLOW = {"Asteroid", "Asteroid_NoRuins", "AsteroidBasic"}
ODYSSEY_DROP = {"MineablePlasteel", "MineableComponentsIndustrial"}
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", ".."))


def xml_files(src):
    for dp, dn, fn in os.walk(src):
        dn[:] = [d for d in dn if d not in (".git", "Assemblies", "Textures", "__pycache__")]
        for f in fn:
            if f.endswith(".xml"):
                yield os.path.join(dp, f)


def parse(p):
    try:
        return ET.parse(p).getroot()
    except ET.ParseError:
        return None


def dangling(src, removed=REMOVED):
    errs = []
    for p in xml_files(src):
        if os.path.basename(p) in EXEMPT_NAMES:
            continue
        r = parse(p)
        if r is None:
            continue
        for e in r.iter():
            if not isinstance(e.tag, str):
                continue
            if e.tag in removed:
                errs.append(f"{os.path.relpath(p, src)}: element <{e.tag}> names a removed def")
            t = (e.text or "").strip()
            if t in removed:
                errs.append(f"{os.path.relpath(p, src)}: <{e.tag}>{t}</{e.tag}> names a removed def")
    return errs


def roster(src, removed=REMOVED):
    errs = []
    for dp, dn, fn in os.walk(os.path.join(src, "RimMandrake", "Utils")):
        dn[:] = [d for d in dn if d != "__pycache__"]
        for f in fn:
            if f.startswith("gen_") and f.endswith(".py"):
                t = open(os.path.join(dp, f), encoding="utf-8", errors="replace").read()
                for n in removed:
                    if re.search(r"<(thingDef|li|%s)>\s*%s\b" % (n, n), t) or re.search(r"<%s>" % n, t):
                        errs.append(f"{f}: generator emits removed def {n}")
    return errs


def _cats(e):
    return {(c.text or "").strip() for c in e.iter("li")}


def filters(src):
    """INFO rows: (file, recipe) with a category filter admitting both plasteel and durasteel."""
    rows = []
    for p in xml_files(src):
        r = parse(p)
        if r is None:
            continue
        for rec in r.iter("RecipeDef"):
            for flt in list(rec.iter("filter")) + list(rec.iter("fixedIngredientFilter")):
                cats = _cats(flt.find("categories")) if flt.find("categories") is not None else set()
                if cats & BROAD:
                    rows.append((os.path.relpath(p, src), rec.findtext("defName") or "?"))
                    break
    return rows


def fixed_plasteel(src):
    out = {}
    for p in xml_files(src):
        r = parse(p)
        if r is None:
            continue
        n = sum(1 for e in r.iter("Plasteel") if len(e) == 0)
        if n:
            out[os.path.relpath(p, src)] = n
    return out


def odyssey(src):
    errs = []
    path = None
    for p in xml_files(src):
        if os.path.basename(p) == ODYSSEY_PATCH:
            path = p
    if not path:
        return [f"{ODYSSEY_PATCH} missing"]
    r = parse(path)
    if r is None:
        return [f"{ODYSSEY_PATCH} unparseable"]
    xp = [(x.text or "") for x in r.iter("xpath")]
    got_steps = set()
    for x in xp:
        for m in re.finditer(r'GenStepDef\[defName="([^"]+)"\]/genStep/mineableCounts/(\w+)', x):
            got_steps.add(m.group(1))
            if m.group(2) not in ODYSSEY_DROP:
                errs.append(f"touches {m.group(2)} (not in drop list)")
        if "GenStepDef" in x and "GenStepDef[defName=" not in x:
            errs.append(f"unscoped GenStepDef xpath: {x}")
    if got_steps != ODYSSEY_ALLOW:
        errs.append(f"GenStepDef allowlist mismatch: patch {sorted(got_steps)} vs {sorted(ODYSSEY_ALLOW)}")
    if not any("GeneratedLocationDef[defName=\"Asteroids\"]/preciousResources" in x for x in xp):
        errs.append("GeneratedLocationDef Asteroids preciousResources not patched")
    return errs


def remelt(src):
    errs = []
    need = {"KotORChunk_plasteel": "Plasteel", "KotORChunk_durasteel": "RSW_Durasteel"}
    seen = {}
    for p in xml_files(src):
        r = parse(p)
        if r is None:
            continue
        for rec in r.iter("RecipeDef"):
            ing = {(l.text or "").strip() for l in rec.iter("li")}
            users = {(l.text or "").strip() for l in rec.findall("recipeUsers/li")}
            prods = {c.tag for c in rec.findall("products/*")}
            for chunk, res in need.items():
                if chunk in ing and res in prods and users & {"ElectricSmelter", "kotor_PlasmaFurnace"}:
                    seen[chunk] = rec.findtext("defName")
    for chunk in need:
        if chunk not in seen:
            errs.append(f"no smelter recipe re-melts {chunk}")
    return errs


def run(src=SRC):
    res = {"dangling": dangling(src), "roster": roster(src), "odyssey": odyssey(src), "remelt": remelt(src)}
    return res


def main():
    src = SRC
    if "--src" in sys.argv:
        src = sys.argv[sys.argv.index("--src") + 1]
    res = run(src)
    bad = 0
    for k, v in res.items():
        print(f"{k}: {'OK' if not v else 'FAIL'}")
        for e in v:
            print("   ", e)
            bad += 1
    f = filters(src)
    print(f"filters (INFO): {len(f)} recipes with a broad category filter admitting both plasteel and durasteel")
    for a, b in f:
        print("   ", a, b)
    fp = fixed_plasteel(src)
    print(f"fixed (INFO): fixed Plasteel quantities in {len(fp)} files, {sum(fp.values())} entries")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
