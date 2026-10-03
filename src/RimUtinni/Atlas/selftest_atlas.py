#!/usr/bin/env python3
"""selftest_atlas.py -- offline coverage lint for the Scavenger's Atlas (mandrake.rut.atlas).

Run bare: python3 src/RimUtinni/Atlas/selftest_atlas.py   (exit 0 = clean)

Checks, every one of which a game load would otherwise be needed to find:
  1. every AtlasEntryDef has label, description, riddle, hint, a valid category and
     completion, and at least one trigger whose Class names a real C# trigger type;
  2. every SUBJECT the triggers name (things, terrains, hediffs, research, weather,
     conditions, planet layers) exists as a def of the right type in our src/ XML or
     in the installed game's Data (Core + DLC), and every rewardThing exists;
     subjects are resolved by NAME at runtime, so a typo would silently read
     "absent from this world" in game rather than erroring;
  3. every Keyed key the C# asks for exists in the English Keyed file;
  4. every .cs in Source/ has a <Compile Include> line (EnableDefaultCompileItems is
     false: a missing line compiles into nothing, with no error);
  5. a SANITY PROBE: the def index must find known defs (RSW_Mynock, Steel), so an
     index that sees nothing cannot report a clean bill of health.
Def lookups need the game's Data folder; when it is unreachable (the Mac), vanilla
names are reported UNMEASURED and only our own src/ defs are checked.
"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
GAME_DATA = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data"
ENTRY_TAG = "RimMandrake.Utinni.Atlas.AtlasEntryDef"
CATEGORIES = {"Creatures", "Giants", "Places", "Weather", "Resources", "Crafts", "Gods", "Ship"}
COMPLETIONS = {"Seen", "Used", "Performed"}
GODS = {"Ishko", "Ohm", "Oomo", "MobUnloo", "Rekko", "TaBaa", "Zizzik", "Shkaar", "Ozzik"}

# trigger field -> def element types that satisfy it
SUBJECT_FIELDS = {
    "things": ("ThingDef",),
    "thing": ("ThingDef",),
    "terrains": ("TerrainDef",),
    "projects": ("ResearchProjectDef",),
    "hediffs": ("HediffDef",),
    "weathers": ("WeatherDef",),
    "conditions": ("GameConditionDef",),
    "layer": ("PlanetLayerDef",),
}


def index_defs(roots):
    idx = {}
    for root in roots:
        for f in glob.glob(os.path.join(root, "**", "*.xml"), recursive=True):
            if "/Languages/" in f or "/Patches/" in f or "/About/" in f:
                continue
            try:
                r = ET.parse(f).getroot()
            except Exception:
                continue
            if r.tag != "Defs":
                continue
            for d in r:
                dn = d.findtext("defName")
                if dn:
                    idx.setdefault(dn, set()).add(d.tag)
    return idx


def main():
    fails = []
    src_idx = index_defs([os.path.join(REPO, "src")])
    game_ok = os.path.isdir(GAME_DATA)
    game_idx = index_defs([GAME_DATA]) if game_ok else {}

    # 5. sanity probe
    if "ThingDef" not in src_idx.get("RSW_Mynock", set()):
        fails.append("SANITY: src index cannot see ThingDef RSW_Mynock; the index is blind")
    if game_ok and "ThingDef" not in game_idx.get("Steel", set()):
        fails.append("SANITY: game Data index cannot see ThingDef Steel; the index is blind")

    def exists(name, types):
        tags = src_idx.get(name, set()) | game_idx.get(name, set())
        return any(t in tags for t in types)

    trig_classes = set(re.findall(r"public class (AtlasTrigger_\w+)",
                                  open(os.path.join(HERE, "Source", "AtlasTriggers.cs")).read()))

    entries = []
    for f in sorted(glob.glob(os.path.join(HERE, "Defs", "**", "*.xml"), recursive=True)):
        for e in ET.parse(f).getroot().findall(ENTRY_TAG):
            entries.append((os.path.basename(f), e))

    names = set()
    unmeasured = 0
    for fname, e in entries:
        dn = e.findtext("defName")
        where = "%s %s" % (fname, dn)
        if dn in names:
            fails.append("%s: duplicate defName" % where)
        names.add(dn)
        if not (dn or "").startswith("RUT_Atlas_"):
            fails.append("%s: defName must start RUT_Atlas_" % where)
        for field in ("label", "description", "riddle", "hint"):
            if not (e.findtext(field) or "").strip():
                fails.append("%s: missing %s" % (where, field))
        if e.findtext("category") not in CATEGORIES:
            fails.append("%s: bad category %r" % (where, e.findtext("category")))
        if e.findtext("completion") not in COMPLETIONS:
            fails.append("%s: bad completion %r" % (where, e.findtext("completion")))
        if (e.findtext("lore") or "").strip() and not (e.findtext("loreVoice") or "").strip():
            fails.append("%s: lore without a loreVoice (R25: lore speaks in a voice inside the world)" % where)
        trigs = e.find("triggers")
        if trigs is None or len(trigs) == 0:
            fails.append("%s: no triggers" % where)
            continue
        for t in trigs:
            cls = (t.get("Class") or "").rsplit(".", 1)[-1]
            if cls not in trig_classes:
                fails.append("%s: trigger Class %r is not a C# trigger type" % (where, t.get("Class")))
            if cls == "AtlasTrigger_GodUnveiled" and t.findtext("god") not in GODS:
                fails.append("%s: god %r is not a RimMandrake.Ninefold.God name" % (where, t.findtext("god")))
            for field, types in SUBJECT_FIELDS.items():
                node = t.find(field)
                if node is None:
                    continue
                subjects = [li.text for li in node.findall("li")] if len(node) else [node.text]
                for s in subjects:
                    if exists(s, types):
                        continue
                    if not game_ok and s not in src_idx:
                        unmeasured += 1
                        continue
                    fails.append("%s: %s %r not found as %s" % (where, field, s, "/".join(types)))
        rw = e.findtext("rewardThing")
        if rw and not exists(rw, ("ThingDef",)):
            if game_ok:
                fails.append("%s: rewardThing %r not found" % (where, rw))
            else:
                unmeasured += 1

    # 3. keyed keys used by C# exist
    keyed = open(os.path.join(HERE, "Languages", "English", "Keyed", "RUT_Atlas.xml")).read()
    have = set(re.findall(r"<(RUT_Atlas_\w+)>", keyed))
    cs = "".join(open(p).read() for p in glob.glob(os.path.join(HERE, "Source", "*.cs")))
    for k in sorted(set(re.findall(r'"(RUT_Atlas_\w+)"\s*\.Translate', cs))):
        if k not in have:
            fails.append("Keyed key %s used in C# but missing from RUT_Atlas.xml" % k)
    for prefix in ("RUT_Atlas_Category_", "RUT_Atlas_Region_"):
        for c in CATEGORIES:
            if prefix + c not in have:
                fails.append("Keyed key %s%s missing (built by string concatenation in C#)" % (prefix, c))
    for c in COMPLETIONS:
        if "RUT_Atlas_Completion_" + c not in have:
            fails.append("Keyed key RUT_Atlas_Completion_%s missing" % c)

    # 4. csproj lists every .cs
    proj = open(os.path.join(HERE, "Source", "RimMandrake.Utinni.Atlas.csproj")).read()
    listed = set(re.findall(r'<Compile Include="([^"]+)"', proj))
    for p in glob.glob(os.path.join(HERE, "Source", "*.cs")):
        if os.path.basename(p) not in listed:
            fails.append("Source/%s has no <Compile Include> line" % os.path.basename(p))

    print("atlas selftest: %d entries, %d trigger types, game Data %s, %d UNMEASURED"
          % (len(entries), len(trig_classes), "read" if game_ok else "UNREACHABLE", unmeasured))
    if len(entries) == 0:
        fails.append("zero entries parsed: the lint read nothing")
    for f in fails:
        print("FAIL", f)
    print("PASS" if not fails else "FAILED (%d)" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
