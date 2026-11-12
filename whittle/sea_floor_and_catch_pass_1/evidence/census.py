#!/usr/bin/env python3
"""Sea floor/catch census. Run from the repo root: python3 -I census.py [src_dir] > out.json
Parses every .xml under src/ as XML elements (never counts text). Reports, per sea BiomeDef,
wildAnimals (inline + patch-added), fishTypes rows (inline + patch-added), rare-catch set contents,
and for each catch item the living body it pairs with."""
import json, os, re, sys
import xml.etree.ElementTree as ET

SRC = sys.argv[1] if len(sys.argv) > 1 else "src"
PAIRS = [("RUT_TheScald", "RM_TheScald"), ("RUT_GreySea", "RM_GreySea"),
         ("RUT_TwilightSea", "RM_TwilightSea"), ("RUT_PropaneLake", "RM_TheChill")]
ALIAS = {"RM_Saal": "RM_Noohm", "RUT_Saal": "RM_Noohm"}  # TerminalBiomes/validation.py CATCH_BODY_ALIAS
SEAS = {s for p in PAIRS for s in p} | {"RM_SeabedFloor", "RM_SeabedFloor_TheScald", "RM_SeabedFloor_GreySea",
                                        "RM_SeabedFloor_TwilightSea", "RM_SeabedFloor_TheChill"}
things, named, biomes, tsm, patch_wa, patch_ft, parse_err, nfiles = {}, {}, {}, {}, {}, {}, [], 0
XP = re.compile(r'BiomeDef\[defName="([^"]+)"\]((?:/[A-Za-z_]+)*)')


def rows_of(node):
    return [(c.tag, (c.text or "").strip(), c.get("MayRequire")) for c in node if isinstance(c.tag, str)]


def walk_patch(op, fn):
    for o in op.iter():
        xp = o.findtext("xpath")
        val = o.find("value")
        if not xp or val is None:
            continue
        m = XP.search(xp)
        if not m or m.group(1) not in SEAS:
            continue
        b, tail = m.group(1), m.group(2)
        cls = o.get("Class", "")
        if tail.endswith("/wildAnimals"):
            patch_wa.setdefault(b, []).extend((t, v, mr, fn, cls) for t, v, mr in rows_of(val))
        elif "/fishTypes" in tail:
            band = tail.split("/fishTypes")[1].strip("/") or "?"
            for t, v, mr in rows_of(val):
                if band == "?":  # whole bands added
                    sub = val.find(t)
                    for t2, v2, mr2 in rows_of(sub):
                        patch_ft.setdefault(b, []).append((t, t2, v2, fn))
                else:
                    patch_ft.setdefault(b, []).append((band, t, v, fn))
        elif tail == "":
            for w in val.findall("wildAnimals"):
                patch_wa.setdefault(b, []).extend((t, v, mr, fn, cls) for t, v, mr in rows_of(w))
            for f in val.findall("fishTypes"):
                for g in f:
                    if g.tag != "rareCatchesSetMaker":
                        patch_ft.setdefault(b, []).extend((g.tag, t, v, fn) for t, v, mr in rows_of(g))


for dp, _, fns in os.walk(SRC):
    for fn in fns:
        if not fn.endswith(".xml"):
            continue
        p = os.path.join(dp, fn)
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError as e:
            parse_err.append("%s: %s" % (p, e)); continue
        nfiles += 1
        rel = os.path.relpath(p, SRC)
        if root.tag == "Patch":
            walk_patch(root, rel); continue
        for d in root:
            if not isinstance(d.tag, str):
                continue
            dn = d.findtext("defName")
            if d.get("Name"):
                named[d.get("Name")] = d
            if d.tag == "ThingDef" and dn:
                things[dn] = (d, rel)
            elif d.tag == "BiomeDef" and dn in SEAS:
                biomes[dn] = (d, rel)
            elif d.tag == "ThingSetMakerDef" and dn:
                tsm[dn] = d


def is_race(d, depth=0):
    if d is None or depth > 12:
        return False
    if d.find("race") is not None:
        return True
    return is_race(named.get(d.get("ParentName")), depth + 1)


races = {n for n, (d, _) in things.items() if is_race(d)}


def tsm_items(name):
    d = tsm.get(name)
    if d is None:
        return None
    return sorted({e.text.strip() for e in d.iter() if e.tag in ("thingDef", "def") and e.text}
                  | {c.tag for e in d.iter() if e.tag in ("filter", "thingDefs") for c in e.iter()
                     if c.tag not in ("filter", "thingDefs", "li") and c.tag in things}
                  | {li.text.strip() for e in d.iter() if e.tag == "thingDefs" for li in e if li.text})


def body_for(catch):
    if catch in ALIAS:
        return ALIAS[catch]
    stem = re.sub(r"^(RM|RUT|RSW)_", "", catch)
    stem = re.sub(r"Catch$", "", stem)
    return stem


def candidates(catch):
    stem = body_for(catch)
    if stem in races:
        return [stem]
    return sorted(r for r in races if re.sub(r"^(RM|RUT|RSW|AA)_", "", r) == stem)


out = {"files_parsed": nfiles, "parse_errors": parse_err, "thingdefs": len(things), "race_thingdefs": len(races),
       "probe": {"RM_Essarn_is_race": "RM_Essarn" in races, "RM_EssarnCatch_is_race": "RM_EssarnCatch" in races,
                 "RM_EssarnCatch_is_thing": "RM_EssarnCatch" in things}, "seas": {}}
for sea in sorted(SEAS):
    if sea not in biomes:
        out["seas"][sea] = {"missing": True}; continue
    b, rel = biomes[sea]
    wa = [(t, v, mr, "inline") for t, v, mr in rows_of(b.find("wildAnimals"))] if b.find("wildAnimals") is not None else []
    wa += [(t, v, mr, fn) for t, v, mr, fn, cls in patch_wa.get(sea, [])]
    ft, rare = [], []
    f = b.find("fishTypes")
    if f is not None:
        for g in f:
            if g.tag == "rareCatchesSetMaker":
                rare.append(g.text.strip())
            else:
                ft += [(g.tag, t, v, "inline") for t, v, mr in rows_of(g)]
    ft += patch_ft.get(sea, [])
    wa_names = {r[0] for r in wa}
    catches = []
    for band, item, w, src in ft:
        c = candidates(item)
        catches.append({"band": band, "item": item, "w": w, "src": src, "item_is_thing": item in things,
                        "item_is_race_BUG": item in races, "body_defs": c,
                        "body_in_this_sea": [x for x in c if x in wa_names]})
    rare_rows = {r: tsm_items(r) for r in rare}
    out["seas"][sea] = {
        "file": rel, "animalDensity": b.findtext("animalDensity"), "maxFishPopulation": b.findtext("maxFishPopulation"),
        "wildAnimals": [{"def": t, "w": v, "MayRequire": mr, "src": s, "in_src": t in things, "is_race": t in races} for t, v, mr, s in wa],
        "catches": catches, "rare": rare_rows,
        "catches_without_body_in_sea": sorted({c["item"] for c in catches if not c["body_in_this_sea"]}),
        "catches_without_any_body_def": sorted({c["item"] for c in catches if not c["body_defs"]})}
json.dump(out, sys.stdout, indent=1)
