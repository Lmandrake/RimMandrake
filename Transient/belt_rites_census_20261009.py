#!/usr/bin/env python3
"""Census of ritual defs under src/: RitualBehaviorDef must declare <roles/> (vanilla CreateRitualRoleAssignments foreach-es it)."""
import re, sys, pathlib
import xml.etree.ElementTree as ET
root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "src")
TYPES = ["RitualBehaviorDef","RitualPatternDef","RitualOutcomeEffectDef","RitualObligationTargetFilterDef","RitualObligationTrigger","RitualTargetFilter","RitualStageDef","RitualRoleDef","PreceptDef"]
hits = {t: [] for t in TYPES}
files = list(root.rglob("*.xml")); n_files = len(files)
fails = []
for f in files:
    try: tree = ET.parse(f)
    except Exception: continue
    for el in tree.getroot().iter():
        if el.tag in TYPES:
            dn = el.findtext("defName") or el.get("Name") or "?"
            if el.tag == "PreceptDef" and el.findtext("preceptClass") != "Precept_Ritual" and el.find("ritualPatternBase") is None: continue
            hits[el.tag].append((str(f), dn, el))
print("scanned xml files:", n_files)
for t, v in hits.items(): print(f"{t}: {len(v)}")
print("--- RitualBehaviorDef roles check")
probe = {"RUT_JoiningWaterBehavior","RUT_NineFaultsBehavior"}
seen = set()
for f, dn, el in hits["RitualBehaviorDef"]:
    ok = el.find("roles") is not None or el.get("ParentName") is not None
    print(("PASS" if ok else "FAIL"), dn, f)
    seen.add(dn)
print("--- PreceptDef ritual: pattern base must resolve")
pats = {dn for _,dn,_ in hits["RitualPatternDef"]}
for f, dn, el in hits["PreceptDef"]:
    pb = el.findtext("ritualPatternBase"); print(dn, "->", pb, "local" if pb in pats else "vanilla/other", f)
print("--- RitualPatternDef refs")
bs = {dn for _,dn,_ in hits["RitualBehaviorDef"]}
for f, dn, el in hits["RitualPatternDef"]:
    print(dn, "behavior", el.findtext("ritualBehavior"), "local" if el.findtext("ritualBehavior") in bs else "OTHER", "outcome", el.findtext("ritualOutcomeEffect"), "filter", el.findtext("ritualObligationTargetFilter"))
print("SANITY: found fixed behaviors:", sorted(seen & probe), "(TheReturn's behavior listed above if inline)")
