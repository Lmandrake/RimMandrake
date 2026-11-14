#!/usr/bin/env python3
"""T_CUT_STAYS_CUT (Pyrelands 0.1.0, RIMMANDRAKE_PIN_PYRE_CUT_LEGS_ABSENT): the three cut legs stay cut.

  firebreak          (inv_firebreak_firefoam; owner 2026-11-05 "I don't think this is a needed feature for this mod")
                     no Firebreak def or FirebreakLine code; no chemfuel-cost floor of ours
  lightning breaker  (inv_lightning_breaker; owner "Drop both" 2026-10-16) no breaker or fulgurite def, code or text
  world migration    (inv_ullai_herd_giant; his card 2026-10-23, commit 84cc81013d) no furnace-herd world object,
                     seeder, map-removal patch or setting; no shipped text (XML element text, not comments, in Defs,
                     About, Languages and Patches) says "migrat"; the shipped DLL holds none of the cut type names.
                     Vanilla map herd migration of ullai is kept (owner by card 2026-11-14, "Yes, let them cross"):
                     herdMigrationAllowed is not a cut leg; T_ULLAI_HERD_MIGRATES checks the ullai can still be picked.
Every planted fault (one per leg part) must go red and the clean copy stay green.
Run: python3 <this file>      exit 0 = PASS, 1 = FAIL
"""
import glob
import os
import re
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
MOD = "src/RimMandrake/Pyrelands"
CUT_TYPES = ["WorldObject_RM_FurnaceHerd", "WorldComponent_RM_FurnaceHerdSeeder", "Patch_FurnaceHerdMapRemoval",
             "FirebreakLine", "LightningBreaker", "Fulgurite"]
CUT_SETTINGS = ["furnaceWorldMigrationEnabled", "furnaceHerdCount"]
CUT_DEF = re.compile(r"firebreak|breaker|fulgurite|FurnaceHerd", re.I)


def _xml(root):
    out = []
    for sub in ("Defs", "About", "Languages", "Patches"):
        out += glob.glob(os.path.join(root, MOD, sub, "**", "*.xml"), recursive=True)
    return out


def facts(root):
    out = []

    def fact(name, bad, detail=""):
        out.append((name, not bad, "; ".join(bad)[:300] if bad else detail))

    texts, defnames, chem_floor, unparsed = [], [], [], []
    for f in _xml(root):
        try:
            r = ET.parse(f).getroot()
        except ET.ParseError:
            unparsed.append(os.path.relpath(f, root))
            continue
        rel = os.path.relpath(f, root)
        for e in r.iter():
            if e.text and e.text.strip():
                texts.append((rel, e.tag, e.text))
            if e.tag == "defName" and e.text:
                defnames.append((rel, e.text.strip()))
        for t in r.iter("TerrainDef"):
            cost = t.find("costList")
            if cost is not None and cost.find("Chemfuel") is not None:
                chem_floor.append("%s %s" % (rel, t.findtext("defName")))
    fact("xml_parses", unparsed)
    fact("no_cut_def", ["%s %s" % d for d in defnames if CUT_DEF.search(d[1])], "%d defNames" % len(defnames))
    fact("no_chemfuel_floor", chem_floor)
    fact("no_migration_text", ["%s <%s>" % (f, tag) for f, tag, x in texts if re.search(r"migrat", x, re.I)],
         "%d text elements" % len(texts))
    fact("no_breaker_text", ["%s <%s>" % (f, tag) for f, tag, x in texts
                             if re.search(r"lightning ?breaker|fulgurite|firebreak", x, re.I)])
    src = {os.path.relpath(f, root): open(f, errors="replace").read()
           for f in glob.glob(os.path.join(root, MOD, "Source", "**", "*.cs"), recursive=True)}
    fact("no_cut_type_in_source", ["%s in %s" % (t, f) for f, s in src.items() for t in CUT_TYPES
                                   if re.search(r"\b(class|struct)\s+%s\b" % t, s)], "%d .cs files" % len(src))
    fact("no_cut_setting", ["%s in %s" % (n, f) for f, s in src.items() for n in CUT_SETTINGS if re.search(r"\b%s\b" % n, s)])
    proj = open(os.path.join(root, MOD, "Source", "FireEcologyHook.csproj"), errors="replace").read()
    fact("csproj_compiles_no_cut_file", [t for t in CUT_TYPES if t in proj])
    dll = os.path.join(root, MOD, "Assemblies", "FireEcologyHook.dll")
    blob = open(dll, "rb").read() if os.path.exists(dll) else b""
    fact("dll_holds_no_cut_type", ["dll missing"] if not blob else [t for t in CUT_TYPES if t.encode() in blob],
         "%d bytes" % len(blob))
    return out


def _put(root, rel, old, new):
    p = os.path.join(root, rel)
    t = open(p, errors="replace").read() if os.path.exists(p) else ""
    if old is None:
        t = new
    else:
        assert old in t, "mutant anchor not found in %s: %r" % (rel, old)
        t = t.replace(old, new, 1)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(t)


DEFS = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<Defs>%s</Defs>\n"
MUTANTS = [
    ("firebreak terrain back", MOD + "/Defs/TerrainDefs/Firebreak.xml", None,
     DEFS % "<TerrainDef><defName>RM_FE_Firebreak</defName><costList><Chemfuel>2</Chemfuel></costList></TerrainDef>"),
    ("chemfuel floor by another name", MOD + "/Defs/TerrainDefs/Strip.xml", None,
     DEFS % "<TerrainDef><defName>RM_FE_PavedStrip</defName><costList><Chemfuel>2</Chemfuel></costList></TerrainDef>"),
    ("lightning breaker def back", MOD + "/Defs/ThingDefs_Buildings/Breaker.xml", None,
     DEFS % "<ThingDef><defName>RM_LightningBreaker</defName></ThingDef>"),
    ("fulgurite in text", MOD + "/Languages/English/Keyed/Pyrelands.xml", "</LanguageData>",
     "<RM_X>Lightning leaves fulgurite here.</RM_X></LanguageData>"),
    ("migration promised in About", MOD + "/About/About.xml", "</description>", " Herds migrate across the world.</description>"),
    ("world herd class back", MOD + "/Source/WorldObject_RM_FurnaceHerd.cs", None,
     "namespace RimMandrake.Pyrelands { public class WorldObject_RM_FurnaceHerd { } }"),
    ("migration setting back", MOD + "/Source/RM_PyrelandsMod.cs", "public static float sandShovelYieldMultiplier",
     "public static bool furnaceWorldMigrationEnabled = true;\n        public static float sandShovelYieldMultiplier"),
    ("csproj compiles it", MOD + "/Source/FireEcologyHook.csproj", "</Project>",
     "<ItemGroup><Compile Include=\"Patch_FurnaceHerdMapRemoval.cs\" /></ItemGroup></Project>"),
]


def _copy(dst):
    for sub in ("Defs", "About", "Languages", "Patches", "Source", "Assemblies"):
        s = os.path.join(REPO, MOD, sub)
        if os.path.isdir(s):
            shutil.copytree(s, os.path.join(dst, MOD, sub))


def main():
    bad = 0
    for name, ok, det in facts(REPO):
        print("%-30s %s  %s" % (name, "ok  " if ok else "FAIL", det))
        bad += not ok
    tmp = tempfile.mkdtemp(prefix="pyre_cut_mut_")
    red = 0
    try:
        base = os.path.join(tmp, "base")
        _copy(base)
        if not all(ok for _, ok, _ in facts(base)):
            print("FAIL: the unchanged copy is not green")
            return 1
        for i, (label, rel, old, new) in enumerate(MUTANTS):
            m = os.path.join(tmp, "m%d" % i)
            shutil.copytree(base, m)
            _put(m, rel, old, new)
            fails = [n for n, ok, _ in facts(m) if not ok]
            print("mutant %-32s %s %s" % (label, "red " if fails else "NOT CAUGHT", ",".join(fails)))
            bad += not fails
            red += bool(fails)
            shutil.rmtree(m)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if bad:
        print("FAIL: %d fact(s) or mutant(s) wrong" % bad)
        return 1
    print("PASS: the three cut legs stay cut, %d of %d mutants red, the clean copy green" % (red, len(MUTANTS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
