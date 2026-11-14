#!/usr/bin/env python3
"""T_ULLAI_HERD_MIGRATES (Pyrelands 0.1.0, inv_ullai_herd_giant): the ullai stay a herd that vanilla herd migration can pick.

Owner by card 2026-11-14, on ullai crossing the map in vanilla herd migrations: "Yes, let them cross".
Vanilla's rule (RimWorld 1.6, decompiled): IncidentWorker_HerdMigration picks a PawnKindDef whose
RaceProps.CanDoHerdMigration holds (Animal, i.e. not a tool user, organic flesh, not an anomaly entity; and
herdMigrationAllowed, default true) and that the map's biome lists with commonality above 0
(IsValidBiomeAnimal; the fallback route adds a temperature test). Facts, read from the repo's XML and the game's
own abstract parents (Data/*/Defs/ThingDefs_Races):

  ullai_def           RM_Ullai is a ThingDef in the mod's Defs and every ParentName resolves
  herd_animal         race herdAnimal resolves true
  animal_not_tooluser race intelligence resolves to Animal (unset = Animal)
  organic_flesh       race fleshType resolves to Normal or Insectoid (unset = Normal)
  migration_allowed   race herdMigrationAllowed never resolves false
  no_patch_disables   no patch op (any src/Rim*/ Patches) sets herdMigrationAllowed for RM_Ullai or for every ThingDef,
                      or touches RM_Ullai's herdAnimal, intelligence or fleshType
  kind_exists         a PawnKindDef has race RM_Ullai
  biome_lists_it      RM_Pyrelands wildAnimals gives RM_Ullai a commonality above 0

Every planted fault must go red and the clean copy stay green.
Run: python3 <this file>      exit 0 = PASS, 1 = FAIL, 2 = UNMEASURED (the game's Data folder is not readable)
"""
import glob
import os
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
MOD = "src/RimMandrake/Pyrelands"
ULLAI = "RM_Ullai"
BIOME = "RM_Pyrelands"
GAME_DATA = os.environ.get("RIMWORLD_DATA", "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data")
ORGANIC = {"Normal", "Insectoid"}


def _parse(files):
    out = []
    for f in files:
        try:
            out.append((f, ET.parse(f).getroot()))
        except ET.ParseError:
            out.append((f, None))
    return out


def _vanilla_abstracts():
    """Named ThingDefs (abstract parents) the game ships, by Name."""
    named = {}
    for f, r in _parse(glob.glob(os.path.join(GAME_DATA, "*", "Defs", "ThingDefs_Races", "*.xml"))):
        if r is not None:
            for d in r.iter("ThingDef"):
                if d.get("Name"):
                    named.setdefault(d.get("Name"), d)
    return named


def facts(root, vanilla):
    out = []

    def fact(name, bad, detail=""):
        out.append((name, not bad, "; ".join(bad)[:300] if bad else detail))

    defs = _parse(glob.glob(os.path.join(root, MOD, "Defs", "**", "*.xml"), recursive=True))
    unparsed = [os.path.relpath(f, root) for f, r in defs if r is None]
    things = [d for _, r in defs if r is not None for d in r.iter("ThingDef")]
    named = dict(vanilla)
    named.update({d.get("Name"): d for d in things if d.get("Name")})
    ullai = [d for d in things if (d.findtext("defName") or "").strip() == ULLAI]
    chain, broken = [], []
    if ullai:
        d = ullai[0]
        while d is not None and len(chain) < 20:
            chain.append(d)
            p = d.get("ParentName")
            if not p:
                break
            d = named.get(p)
            if d is None:
                broken.append("parent %s not found in the mod or the game" % p)
    fact("ullai_def", unparsed + ([] if ullai else ["no ThingDef %s in %s/Defs" % (ULLAI, MOD)]) + broken,
         "chain %s" % " < ".join((c.get("Name") or c.findtext("defName") or "?") for c in chain))

    def race(field, default):
        for c in chain:
            r = c.find("race")
            if r is not None and r.find(field) is not None:
                return (r.findtext(field) or "").strip(), c.get("Name") or c.findtext("defName")
        return default, "default"

    v, src = race("herdAnimal", "false")
    fact("herd_animal", [] if v.lower() == "true" else ["herdAnimal %s (from %s)" % (v, src)], "true (from %s)" % src)
    v, src = race("intelligence", "Animal")
    fact("animal_not_tooluser", [] if v == "Animal" else ["intelligence %s (from %s)" % (v, src)], v)
    v, src = race("fleshType", "Normal")
    fact("organic_flesh", [] if v in ORGANIC else ["fleshType %s (from %s)" % (v, src)], v)
    v, src = race("herdMigrationAllowed", "true")
    fact("migration_allowed", [] if v.lower() != "false" else ["herdMigrationAllowed false (from %s)" % src],
         "%s (from %s)" % (v, src))

    pats = []
    for f in glob.glob(os.path.join(root, "src", "Rim*", "**", "Patches", "**", "*.xml"), recursive=True):
        pats.append(f)
    bad = []
    for f, r in _parse(sorted(set(pats))):
        if r is None:
            bad.append("%s does not parse" % os.path.relpath(f, root))
            continue
        for op in r.iter():
            xp = (op.findtext("xpath") or "") if op.find("xpath") is not None else None
            if xp is None:
                continue
            val = op.find("value")
            vs = ET.tostring(val, encoding="unicode") if val is not None else ""
            both = xp + " " + vs
            names_ullai = ('"%s"' % ULLAI) in xp or ("'%s'" % ULLAI) in xp
            generic = "defName" not in xp
            if "herdMigrationAllowed" in both and (names_ullai or generic):
                bad.append("%s: %s" % (os.path.relpath(f, root), xp))
            elif names_ullai and any(k in both for k in ("herdAnimal", "intelligence", "fleshType")):
                bad.append("%s: %s" % (os.path.relpath(f, root), xp))
    fact("no_patch_disables", bad, "%d patch files" % len(pats))

    kinds = [k for _, r in defs if r is not None for k in r.iter("PawnKindDef")
             if (k.findtext("race") or "").strip() == ULLAI]
    fact("kind_exists", [] if kinds else ["no PawnKindDef with race %s" % ULLAI], "%d kind(s)" % len(kinds))

    com = None
    for _, r in defs:
        if r is None:
            continue
        for b in r.iter("BiomeDef"):
            if (b.findtext("defName") or "").strip() == BIOME and b.find("wildAnimals") is not None:
                t = b.find("wildAnimals").findtext(ULLAI)
                com = float(t) if t not in (None, "") else None
    fact("biome_lists_it", [] if com and com > 0 else ["%s wildAnimals %s: %s" % (BIOME, ULLAI, com)],
         "commonality %s" % com)
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


RACE = MOD + "/Defs/ThingDefs_Races/RM_Ullai.xml"
BIOMEF = MOD + "/Defs/BiomeDefs/Pyrelands.xml"
HERD = "<herdAnimal>true</herdAnimal>"
PATCH = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<Patch>%s</Patch>\n"
OFF = "<value><herdMigrationAllowed>false</herdMigrationAllowed></value>"
MUTANTS = [
    ("migration turned off", RACE, HERD, HERD + "<herdMigrationAllowed>false</herdMigrationAllowed>"),
    ("not a herd animal", RACE, HERD, "<herdAnimal>false</herdAnimal>"),
    ("herdAnimal dropped", RACE, HERD, ""),
    ("tool user", RACE, HERD, HERD + "<intelligence>ToolUser</intelligence>"),
    ("mechanical flesh", RACE, HERD, HERD + "<fleshType>Mechanoid</fleshType>"),
    ("parent turns it off", RACE, "<ThingDef ParentName=\"AnimalThingBase\">\n    <defName>RM_Ullai</defName>",
     "<ThingDef Name=\"RM_X_NoMigrate\" ParentName=\"AnimalThingBase\" Abstract=\"True\"><race>"
     "<herdMigrationAllowed>false</herdMigrationAllowed></race></ThingDef>\n"
     "  <ThingDef ParentName=\"RM_X_NoMigrate\">\n    <defName>RM_Ullai</defName>"),
    ("parent missing", RACE, "<ThingDef ParentName=\"AnimalThingBase\">\n    <defName>RM_Ullai</defName>",
     "<ThingDef ParentName=\"RM_X_NoSuchBase\">\n    <defName>RM_Ullai</defName>"),
    ("patch turns it off", MOD + "/Patches/RM_X_UllaiNoMigrate.xml", None,
     PATCH % ("<Operation Class=\"PatchOperationAdd\"><xpath>Defs/ThingDef[defName=\"RM_Ullai\"]/race</xpath>%s"
              "</Operation>" % OFF)),
    ("patch turns all off", MOD + "/Patches/RM_X_AllNoMigrate.xml", None,
     PATCH % ("<Operation Class=\"PatchOperationAdd\"><xpath>Defs/ThingDef/race</xpath>%s</Operation>" % OFF)),
    ("patch removes herdAnimal", MOD + "/Patches/RM_X_UllaiNoHerd.xml", None,
     PATCH % "<Operation Class=\"PatchOperationRemove\"><xpath>Defs/ThingDef[defName=\"RM_Ullai\"]/race/herdAnimal"
             "</xpath></Operation>"),
    ("biome drops it", BIOMEF, "<RM_Ullai>0.35</RM_Ullai>", "<RM_Ullai>0</RM_Ullai>"),
    ("kind gone", RACE, "<race>RM_Ullai</race>", "<race>RM_UllaiX</race>"),
]


def _copy(dst):
    for sub in ("Defs", "Patches"):
        s = os.path.join(REPO, MOD, sub)
        if os.path.isdir(s):
            shutil.copytree(s, os.path.join(dst, MOD, sub))
    for f in glob.glob(os.path.join(REPO, "src", "Rim*", "**", "Patches", "**", "*.xml"), recursive=True):
        rel = os.path.relpath(f, REPO)
        if rel.startswith(MOD + "/"):
            continue
        os.makedirs(os.path.dirname(os.path.join(dst, rel)), exist_ok=True)
        shutil.copy2(f, os.path.join(dst, rel))


def main():
    vanilla = _vanilla_abstracts()
    if "AnimalThingBase" not in vanilla:
        print("UNMEASURED: the game's AnimalThingBase is not readable under %s (set RIMWORLD_DATA)" % GAME_DATA)
        return 2
    bad = 0
    for name, ok, det in facts(REPO, vanilla):
        print("%-22s %s  %s" % (name, "ok  " if ok else "FAIL", det))
        bad += not ok
    tmp = tempfile.mkdtemp(prefix="pyre_ullai_mut_")
    red = 0
    try:
        base = os.path.join(tmp, "base")
        _copy(base)
        if not all(ok for _, ok, _ in facts(base, vanilla)):
            print("FAIL: the unchanged copy is not green")
            return 1
        for i, (label, rel, old, new) in enumerate(MUTANTS):
            m = os.path.join(tmp, "m%d" % i)
            shutil.copytree(base, m)
            _put(m, rel, old, new)
            fails = [n for n, ok, _ in facts(m, vanilla) if not ok]
            print("mutant %-26s %s %s" % (label, "red " if fails else "NOT CAUGHT", ",".join(fails)))
            bad += not fails
            red += bool(fails)
            shutil.rmtree(m)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if bad:
        print("FAIL: %d fact(s) or mutant(s) wrong" % bad)
        return 1
    print("PASS: RM_Ullai is a herd vanilla herd migration can pick, %d of %d mutants red, the clean copy green"
          % (red, len(MUTANTS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
