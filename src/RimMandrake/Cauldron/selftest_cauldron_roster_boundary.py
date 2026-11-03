#!/usr/bin/env python3
"""CAULDRON_ROSTER_BOUNDARY_RECONCILE_PATCH: the RM_Cauldron write-up names exactly the Star Wars rows the
Utinni patch really adds.

RM_Cauldron (RimMandrake tier) carries no Star Wars fauna inline; those rows ride
src/RimUtinni/UtinniPatches/Patches/WildAnimals_Cauldron.xml. Two texts describe that boundary: the
"NOT in this mod" paragraph of About.xml and the wildAnimals note in RM_Cauldron.xml's header. They had
drifted (named RSW_Screecher, cut from the patch by the owner's sheet note 2026-10-09; omitted RSW_Lylek,
RSW_Skalder, RSW_Silooth). This pins: patch rows parsed as XML elements == each text's RSW_ names, the
BiomeDef itself has no RSW_ row inline, and RSW_Screecher is not a patch row.

    python3 src/RimMandrake/Cauldron/selftest_cauldron_roster_boundary.py
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(os.path.dirname(HERE))
PATCH = os.path.join(SRC, "RimUtinni", "UtinniPatches", "Patches", "WildAnimals_Cauldron.xml")
ABOUT = os.path.join(HERE, "About", "About.xml")
BIOME = os.path.join(HERE, "Defs", "BiomeDefs", "RM_Cauldron.xml")
fails = []


def check(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)))
    if not ok:
        fails.append(name)


def patch_rows():
    rows = []
    for op in ET.parse(PATCH).getroot().iter("match"):
        if op.get("Class") != "PatchOperationAdd":
            continue
        if 'BiomeDef[defName="RM_Cauldron"]/wildAnimals' not in (op.findtext("xpath") or ""):
            continue
        value = op.find("value")
        rows += [c.tag for c in value if isinstance(c.tag, str)]
    return rows


rows = patch_rows()
# Sanity probe: the instrument must see rows at all before an equality means anything.
check("patch parse sees rows", len(rows) >= 5, rows)
check("patch rows are all RSW_", all(r.startswith("RSW_") for r in rows), rows)
check("RSW_Screecher is not a Cauldron patch row", "RSW_Screecher" not in rows, rows)
check("no duplicate patch rows", len(rows) == len(set(rows)), rows)
want = set(rows)

about = ET.parse(ABOUT).getroot().findtext("description") or ""
m = re.search(r"NOT in this mod:(.*?)that\s+inhabit", about, re.S)
check("About.xml has the NOT-in-this-mod list", m is not None)
about_names = set(re.findall(r"RSW_\w+", m.group(1))) if m else set()
check("About.xml list == patch rows", about_names == want,
      f"missing {sorted(want - about_names)} extra {sorted(about_names - want)}")

biome_text = open(BIOME, encoding="utf-8").read()
cm = re.search(r"- wildAnimals: every Star Wars(.*?)\n\s*- wildPlants", biome_text, re.S)
check("RM_Cauldron.xml header has the wildAnimals boundary note", cm is not None)
note = cm.group(1) if cm else ""
ride = note.split("is not one of them")[0]
named = set(re.findall(r"RSW_\w+", ride)) - {"RSW_Screecher"}
check("RM_Cauldron.xml note == patch rows", named == want,
      f"missing {sorted(want - named)} extra {sorted(named - want)}")

inline = []
for b in ET.parse(BIOME).getroot().iter("BiomeDef"):
    if b.findtext("defName") == "RM_Cauldron":
        wa = b.find("wildAnimals")
        inline = [c.tag for c in wa if isinstance(c.tag, str)] if wa is not None else []
check("RM_Cauldron inline roster parsed", len(inline) > 0)
check("RM_Cauldron inline roster has no RSW_ row", not any(t.startswith("RSW_") for t in inline), inline)

print(f"{'PASS' if not fails else 'FAIL'}  {len(fails)} failing")
sys.exit(1 if fails else 0)
