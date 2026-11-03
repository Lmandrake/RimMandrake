#!/usr/bin/env python3
"""selftest_swb_twins_dedupe.py -- offline proof for SWB_TWINS_DEDUPE_STILLSAND.

RSW_SandLion (SWBestiary) was a twin of RM_Vekka (Stillsand, mandrake.rm.biomes). The SWB copy is retired:
  1. no def anywhere under src/ is named RSW_SandLion;
  2. RM_Vekka exists as a ThingDef and a PawnKindDef;
  3. a save holding the old name loads it as RM_Vekka: RM_SWBRehome_Aliases.xml maps RSW_SandLion (ThingDef and
     PawnKindDef) and Corpse_RSW_SandLion;
  4. no XML outside that alias file names RSW_SandLion in an element, attribute or text (comments are history and
     are stripped), and no C# names it;
  5. the frozen RUT_ExtremeDesert row names RM_Vekka behind MayRequire="mandrake.rm.biomes";
  6. the Utinni stat patches were REPOINTED, not just stripped: AnimalTolerances_Ashkarr.xml targets
     ThingDef[defName="RM_Vekka"]/statBases/ComfyTemperatureMin and Max and writes -1.1 and 100;
     Doctrine/MegafaunaYield.xml targets RM_Vekka's statBases/MeatAmount and RM_BoneAmount and writes 280 and 100.

And one guard against the wrong dedupe: RSW_Vozzik is NOT a twin of RM_Vozzik. The owner gave them separate homes
on 2026-10-04 (LONGSHADE_SHEET_STRUCTURAL_RULINGS_1: RSW_Vozzik to the Rust Cathedral, "regenerate to make it
obviously entirely synthetic"; RM_Vozzik to the Warscar), so both must stay defined until a move gives RSW_Vozzik
its own RM_ name.

The reference scanner is probed first on planted text, so a blind scanner cannot pass.
Run bare: python3 src/RimStarWars/SWBestiary/selftest_swb_twins_dedupe.py   (exit 0 = clean)
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SRC = os.path.join(ROOT, "src")
ALIASES = os.path.join(SRC, "RimMandrake", "LeaningScrub", "Defs", "Misc", "RM_SWBRehome_Aliases.xml")
TOLER = os.path.join(SRC, "RimUtinni", "UtinniPatches", "Patches", "AnimalTolerances_Ashkarr.xml")
MEGA = os.path.join(SRC, "RimUtinni", "Doctrine", "Patches", "MegafaunaYield.xml")
EXTREME = os.path.join(SRC, "RimUtinni", "UtinniPatches", "Defs", "BiomeDefs", "RUT_ExtremeDesert.xml")
OLD, NEW = "RSW_SandLion", "RM_Vekka"
SKIP = {"obj", "bin", "Textures", ".git", "node_modules"}
COMMENT = re.compile(r"<!--.*?-->", re.S)

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, ("" if cond else detail)))
    if not cond:
        FAILS.append(name)


def files(exts):
    for d, dirs, fs in os.walk(SRC):
        dirs[:] = [x for x in dirs if x not in SKIP]
        for f in fs:
            if os.path.splitext(f)[1] in exts:
                yield os.path.join(d, f)


def read(p):
    with open(p, encoding="utf-8", errors="ignore") as fh:
        return fh.read()


def names_in(text, name):
    """Whole-token hits of `name` in text with XML comments removed (Corpse_RSW_SandLion counts too)."""
    body = COMMENT.sub("", text)
    return len(re.findall(r"(?<![A-Za-z0-9])" + re.escape(name) + r"(?![A-Za-z0-9])", body))


def defs_named(name):
    """[(path, def tag)] for every element whose <defName> is `name`, parsed as XML."""
    out = []
    for p in files({".xml"}):
        t = read(p)
        if name not in t:
            continue
        try:
            root = ET.fromstring(t.encode("utf-8"))
        except ET.ParseError:
            if re.search(r"<defName>\s*" + re.escape(name) + r"\s*</defName>", COMMENT.sub("", t)):
                out.append((p, "?unparsed"))
            continue
        for el in root.iter():
            dn = el.find("defName")
            if dn is not None and (dn.text or "").strip() == name:
                out.append((p, el.tag))
    return out


def patch_ops(text):
    """(xpaths, writes) of a patch file: every <xpath> text, and every (xpath, stat, value) an operation with a
    <value> child writes. Parsed as XML, so comments do not count."""
    root = ET.fromstring(text.encode("utf-8"))
    xpaths, writes = set(), set()
    for op in root.iter():
        xp = op.find("xpath")
        if xp is None or not (xp.text or "").strip():
            continue
        x = xp.text.strip()
        xpaths.add(x)
        val = op.find("value")
        if val is not None:
            for stat in val.iter():
                if stat is not val and len(stat) == 0:
                    writes.add((x, stat.tag, (stat.text or "").strip()))
    return xpaths, writes


def vekka_stat_checks(label, path, stats):
    """stats: {stat: value}. Each needs its own xpath on RM_Vekka and a write of that value under RM_Vekka."""
    base = '/Defs/ThingDef[defName="%s"]' % NEW
    xpaths, writes = patch_ops(read(path))
    for stat, value in stats.items():
        check("%s targets %s/statBases/%s" % (label, base, stat), base + "/statBases/" + stat in xpaths)
        ok = any(x.startswith(base) and t == stat and v == value for x, t, v in writes)
        check("%s writes %s=%s on RM_Vekka" % (label, stat, value), ok)


def main():
    # ---- sanity probes: the instruments can see
    check("probe: scanner sees a planted element", names_in("<a><RSW_SandLion>1</RSW_SandLion></a>", OLD) == 2)
    check("probe: scanner sees an xpath attribute", names_in('<x xpath="Defs/ThingDef[defName=\\"RSW_SandLion\\"]"/>', OLD) == 1)
    check("probe: scanner ignores a comment", names_in("<!-- RSW_SandLion --><a/>", OLD) == 0)
    check("probe: scanner sees Corpse_ prefix", names_in("<li>Corpse_RSW_SandLion</li>", OLD) == 1)
    check("probe: scanner is not fooled by a longer name", names_in("<li>RSW_SandLionX</li>", OLD) == 0)
    probe = defs_named(NEW)
    check("probe: def finder sees RM_Vekka", len(probe) >= 1, repr(probe))

    # 1. the SWB copy is gone
    old_defs = defs_named(OLD)
    check("1. no def named RSW_SandLion", not old_defs, repr(old_defs))

    # 2. the survivor exists, both halves
    tags = sorted({t for _, t in defs_named(NEW)})
    check("2. RM_Vekka is a ThingDef and a PawnKindDef", "ThingDef" in tags and "PawnKindDef" in tags, repr(tags))

    # 3. the aliases
    want = {(OLD, NEW, "ThingDef"), ("Corpse_" + OLD, "Corpse_" + NEW, "ThingDef"), (OLD, NEW, "PawnKindDef")}
    have = set()
    for li in ET.parse(ALIASES).getroot().iter("li"):
        f, t, k = li.findtext("from"), li.findtext("to"), li.findtext("defType")
        if f and t and k:
            have.add((f.strip(), t.strip(), k.strip()))
    check("3. RM_SWBRehome_Aliases maps the three old names", want <= have, repr(sorted(want - have)))

    # 4. nothing else names it
    hits = []
    for p in files({".xml", ".cs"}):
        if os.path.abspath(p) == os.path.abspath(ALIASES):
            continue
        t = read(p)
        if OLD not in t:
            continue
        n = names_in(t, OLD) if p.endswith(".xml") else len(re.findall(r"(?<![A-Za-z0-9])" + OLD + r"(?![A-Za-z0-9])",
                                                                       re.sub(r"//[^\n]*|/\*.*?\*/", "", t, flags=re.S)))
        if n:
            hits.append("%s x%d" % (os.path.relpath(p, ROOT), n))
    check("4. no live XML/C# reference to RSW_SandLion outside the alias file", not hits, "; ".join(hits))

    # 5. the frozen Extreme Desert row
    root = ET.parse(EXTREME).getroot()
    rows = {}
    for b in root.iter("BiomeDef"):
        if (b.findtext("defName") or "").strip() == "RUT_ExtremeDesert":
            wa = b.find("wildAnimals")
            for el in (list(wa) if wa is not None else []):
                rows[el.tag] = (el.text, el.get("MayRequire"))
    check("5a. RUT_ExtremeDesert has no RSW_SandLion row", OLD not in rows)
    check("5b. RUT_ExtremeDesert names RM_Vekka 0.5 behind mandrake.rm.biomes",
          rows.get(NEW) == ("0.5", "mandrake.rm.biomes"), repr(rows.get(NEW)))

    # 6. the Utinni stat patches point at RM_Vekka (probe first: the extractor sees a planted op)
    px, pw = patch_ops('<Patch><!-- <xpath>/Defs/ThingDef[defName="RM_Vekka"]/statBases/Fake</xpath> -->'
                       '<Operation><xpath>/Defs/ThingDef[defName="RM_Vekka"]/statBases</xpath>'
                       '<value><MeatAmount>280</MeatAmount></value></Operation></Patch>')
    check("probe: patch_ops sees an xpath and its write, not a commented one",
          px == {'/Defs/ThingDef[defName="RM_Vekka"]/statBases'}
          and pw == {('/Defs/ThingDef[defName="RM_Vekka"]/statBases', "MeatAmount", "280")}, repr((px, pw)))
    vekka_stat_checks("6a. AnimalTolerances", TOLER, {"ComfyTemperatureMin": "-1.1", "ComfyTemperatureMax": "100"})
    vekka_stat_checks("6b. MegafaunaYield", MEGA, {"MeatAmount": "280", "RM_BoneAmount": "100"})

    # guard: the vozziks are two creatures by the owner's 2026-10-04 placement
    for n in ("RSW_Vozzik", "RM_Vozzik"):
        k = sorted({t for _, t in defs_named(n)})
        check("guard: %s still defined (ThingDef + PawnKindDef)" % n, "ThingDef" in k and "PawnKindDef" in k, repr(k))

    print("\n%s: %d failure(s)" % ("CLEAN" if not FAILS else "FAIL", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
