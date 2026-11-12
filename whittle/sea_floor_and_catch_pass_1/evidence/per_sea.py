#!/usr/bin/env python3
"""Per-sea verdict for SEA_FLOOR_AND_CATCH_PASS_1, from the defs on disk (XML elements, never <li> counts).
Run from the repo root: python3 -I per_sea.py <census out.json>"""
import json, os, re, subprocess, sys
import xml.etree.ElementTree as ET

census = json.load(open(sys.argv[1]))
SEAS = ["RM_TheScald", "RM_GreySea", "RM_TwilightSea", "RM_TheChill"]
defs = {}
for dp, _, fns in os.walk("src"):
    for fn in fns:
        if fn.endswith(".xml"):
            try:
                root = ET.parse(os.path.join(dp, fn)).getroot()
            except ET.ParseError:
                continue
            for d in root:
                if isinstance(d.tag, str) and d.findtext("defName"):
                    defs.setdefault((d.tag, d.findtext("defName")), (d, os.path.join(dp, fn)))
wiring = open("src/RimMandrake/DivingInteraction/Patches/RM_SeabedFloorBiomeWiring.xml", encoding="utf-8").read()
sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
print("# Per-sea verdict at %s (parsed from src/, %d defs indexed)\n" % (sha, len(defs)))
for sea in SEAS:
    b, path = defs[("BiomeDef", sea)]
    print("## %s (%s)" % (sea, path))
    # shore
    ext = [li for li in b.iter("li") if "SeaShore" in (li.get("Class") or "")]
    if ext:
        e = ext[0]
        terr = {c.tag: (c.text or "").strip() for c in e if isinstance(c.tag, str) and not list(c)}
        missing = [v for k, v in terr.items() if "errain" in k and v and ("TerrainDef", v) not in defs]
        print("- shore: %s on the BiomeDef -> land tiles beside it get the RM_SeaCoast mutator; terrains %s; "
              "terrain defs missing from src: %s" % (e.get("Class"), terr, missing or "none"))
    else:
        print("- shore: NO RM_SeaShoreExtension")
    # floor
    m = re.search(r'BiomeDef\[defName="%s"\]/modExtensions</xpath>\s*<value>\s*<li Class="[^"]+">\s*<floorBiome>(\w+)' % sea, wiring)
    floor = m.group(1) if m else None
    fd = defs.get(("BiomeDef", floor))
    factor = gen = None
    if fd:
        for li in fd[0].iter("li"):
            if "FloorExtension" in (li.get("Class") or ""):
                gen = li.findtext("generator")
                # unset in XML = the C# field initialiser (RM_SeabedSiteParent.cs: animalDensityFactor = 30f), read, not assumed
                cs = open("src/RimMandrake/DivingInteraction/Source/RM_SeabedSiteParent.cs", encoding="utf-8").read()
                factor = li.findtext("animalDensityFactor") or re.search(r"animalDensityFactor = ([0-9.]+)f;", cs).group(1)
    gd = defs.get(("MapGeneratorDef", gen)) if gen else None
    steps = [x.text for x in gd[0].iter("li")] if gd else []
    dens = float(b.findtext("animalDensity") or 0)
    print("- floor: %s (exists: %s), animalDensityFactor %s -> floor animalDensity %.2f; generator %s (exists: %s), "
          "fauna genstep present: %s" % (floor, bool(fd), factor, dens * float(factor or 0), gen, bool(gd),
                                         any("Fauna" in (s or "") for s in steps)))
    v = census["seas"][sea]
    wa = [a["def"] for a in v["wildAnimals"]]
    nokind = [a for a in wa if ("PawnKindDef", a) not in defs]
    print("- floor cast: %d wildAnimals; races with no same-named PawnKindDef in src: %s" % (len(wa), nokind or "none"))
    rows = v["catches"]
    lack = v["catches_without_body_in_sea"]
    print("- catch: %d fishTypes rows; rows lacking a living body on this floor: %s" % (len(rows), lack or "none"))
    for r in rows:
        print("    %-22s %-20s body %s" % (r["item"], r["band"], ",".join(r["body_in_this_sea"]) or "-"))
    for setname, items in (v["rare"] or {}).items():
        for it in items:
            t = defs.get(("ThingDef", it))
            israce = t is not None and t[0].find("race") is not None
            print("    rare %-22s in %s: %s" % (it, setname, "RACE (bug)" if israce else ("item" if t else "engine/donor def")))
    print("- description: %s\n" % (b.findtext("description") or "").strip())
