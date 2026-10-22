#!/usr/bin/env python3
"""archetype_seed.py -- the biome review sheet's plant columns (explosive_growth_ruled_spec_2026-10-16.md §9, D23),
seeded OFFLINE from the repo exactly as RM_ExplosiveGrowthRegistry.Rebuild seeds them at load (§4.3):

  archetype      exempt (built-in / exemptPlants / bandExemptPlants / growDays < 1 / a row says Exempt) > a row's own choice >
                 fire-adapted (fireAdapted flag, or in a fireAdaptedBiomes biome's wildPlants) > wet native (in a
                 wetNativeBiomes biome's wildPlants, even if a dry biome lists it too) > dry native (a roster row, a def our
                 tiers ship, or in one of our biomes' wildPlants and not a Ludeon def) > vanilla
  rupture odds   the row's ruptureChance; else 1 for a Burst row; else 1/3 (dry, fire) / 0 (wet)  (C3, OQ-5)
  violent top    the roster top (Churn = the default cycle; Slime/Tinder/Rupture/Flush keep their own odds)
  liquids        clean water + the row's adaptedLiquids (T2)
  sprouts        the row's sproutCount, else dry 4~7 / wet 1~2
  woody          harvestTag Wood / a Tree parent / harvestedThingDef WoodLog (EC1), and not a tree
  tree           tree_burst_design_2026-10-17.md §2: a native drawn at visual max 3.0+ (the def's own visualSizeRange; an
                 inherited one reads "UNMEASURED offline"), not a roster fungus, not treeRulesExempt (RM_Greatbole), not notTrees
  conflict       a plant in both a wet and a dry biome's list: surfaced, never silently resolved (§9, evictions stopped)

The sheet GENERATOR is not built here (UNMEASURED in the spec: owed with the biome review tooling); this is its data.
Offline reads cannot see a def's mod-of-origin, inheritance beyond a ParentName name test, or wildPlants patched in by
a non-trivial xpath: every such row says so ("UNMEASURED offline"), the live registry is the authority.

    python3 src/RimMandrake/ExplosiveGrowth/archetype_seed.py [--out FILE.json] [--biome RM_Greentide]
"""
import argparse
import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SRC = os.path.join(REPO, "src")
BUILTIN_EXEMPT = {"Plant_TreeAnima", "Plant_TreeGauranlen", "Plant_Ambrosia"}
CLEAN = "RM_Fluid_Water"
OURS = ("RM_", "RUT_", "RSW_")


def _xml_files():
    return [p for p in glob.glob(os.path.join(SRC, "**", "*.xml"), recursive=True) if "selftest_fixtures" not in p]


def _parse(p):
    try:
        return ET.parse(p).getroot()
    except ET.ParseError:
        return None


def load(files=None):
    files = files or _xml_files()
    rosters, biomes, plants = [], {}, {}
    patched = {}
    for p in files:
        txt = open(p, encoding="utf-8", errors="replace").read()
        if "RM_ExplosiveGrowthRosterDef" not in txt and "<BiomeDef" not in txt and "<plant>" not in txt and "wildPlants" not in txt:
            continue
        root = _parse(p)
        if root is None:
            continue
        if root.tag == "Patch":
            for op in root.iter("Operation"):
                xp = op.findtext("xpath") or ""
                m = re.search(r'BiomeDef\[defName="([^"]+)"\]/wildPlants', xp)
                val = op.find("value")
                if m and val is not None:
                    patched.setdefault(m.group(1), set()).update(c.tag for c in val)
            continue
        for d in root:
            if d.tag.endswith("RM_ExplosiveGrowthRosterDef"):
                rosters.append(d)
            elif d.tag == "BiomeDef" and d.findtext("defName"):
                wp = d.find("wildPlants")
                biomes[d.findtext("defName")] = {"file": os.path.relpath(p, REPO),
                                                 "plants": [c.tag for c in wp] if wp is not None else []}
            elif d.tag == "ThingDef" and d.find("plant") is not None and d.findtext("defName"):
                pl = d.find("plant")
                plants[d.findtext("defName")] = {
                    "growDays": pl.findtext("growDays"), "harvestTag": pl.findtext("harvestTag"),
                    "harvested": pl.findtext("harvestedThingDef"), "parent": d.get("ParentName") or "",
                    "cave": (pl.findtext("cavePlant") or "").strip().lower() == "true",
                    "visual": pl.findtext("visualSizeRange")}
    for b, extra in patched.items():
        if b in biomes:
            biomes[b]["plants"] = sorted(set(biomes[b]["plants"]) | extra)
            biomes[b]["patchAdded"] = sorted(extra)
    return rosters, biomes, plants


def seed(rosters, biomes, plants):
    rows, exempt, wet_b, fire_b = {}, set(BUILTIN_EXEMPT), set(), set()
    fungi, tree_exempt, not_trees = set(), set(), set()
    for r in rosters:
        fungi |= {(x.text or "").strip() for x in r.findall("fungi/li")}
        tree_exempt |= {(x.text or "").strip() for x in r.findall("treeRulesExempt/li")}
        not_trees |= {(x.text or "").strip() for x in r.findall("notTrees/li")}
        for li in r.findall("plants/li"):
            n = (li.findtext("plant") or "").strip()
            if n:
                rows[n] = li
        exempt |= {(x.text or "").strip() for x in r.findall("exemptPlants/li") + r.findall("bandExemptPlants/li")}
        wet_b |= {(x.text or "").strip() for x in r.findall("wetNativeBiomes/li")}
        fire_b |= {(x.text or "").strip() for x in r.findall("fireAdaptedBiomes/li")}
    wet_p = {p for b in wet_b if b in biomes for p in biomes[b]["plants"]}
    fire_p = {p for b in fire_b if b in biomes for p in biomes[b]["plants"]}
    ours_b = [b for b in biomes if b.startswith(OURS)]
    dry_b_p = {p for b in ours_b if b not in wet_b for p in biomes[b]["plants"]}
    our_p = {p for b in ours_b for p in biomes[b]["plants"]}

    def one(name):
        li = rows.get(name)
        pd = plants.get(name)
        notes = []
        try:
            gd = float(pd["growDays"]) if pd and pd["growDays"] else None
        except ValueError:
            gd = None
        if pd is None:
            notes.append("def not in this repo (vanilla, DLC or donor): mod-of-origin UNMEASURED offline")
        elif gd is None:
            notes.append("growDays inherited: UNMEASURED offline")
        choice = (li.findtext("archetype") if li is not None else None) or "Auto"
        fire_flag = li is not None and (li.findtext("fireAdapted") or "").strip().lower() == "true"
        top = ((li.findtext("top") if li is not None else None) or "Churn").strip()
        decided = choice != "Auto" or fire_flag      # a deciding row outranks the under-a-day clause (Pyrelands grass, C3)
        if name in exempt or choice == "Exempt" or (not decided and gd is not None and gd < 1) or (pd and pd["cave"] and li is None):
            a = "Exempt"
        elif choice in ("DryNative", "WetNative", "FireAdapted"):
            a = choice
        elif fire_flag or name in fire_p:
            a = "FireAdapted"
        elif name in wet_p:
            a = "WetNative"
        elif li is not None or name.startswith(OURS) or (name in our_p and pd is not None):
            a = "DryNative"
        else:
            a = "Vanilla"
        if a in ("Exempt", "Vanilla"):
            top = "None"
        rc = float(li.findtext("ruptureChance")) if li is not None and li.findtext("ruptureChance") else -1.0
        if rc < 0 and top == "Burst":
            rc = 1.0
        odds = rc if rc >= 0 else (0.0 if a == "WetNative" else 0.3333 if a in ("DryNative", "FireAdapted") else 0.0)
        if top in ("Slime", "Tinder", "Rupture", "Flush"):
            odds_label = "own top (%s)" % top
        elif top == "None":
            odds_label = "never cycles"
        else:
            odds_label = {0.0: "0", 1.0: "1 in 1", 0.3333: "1 in 3"}.get(round(odds, 4), "%.3g" % odds)
        sc = li.findtext("sproutCount") if li is not None else None
        sprouts = sc or ("1~2" if a == "WetNative" else "4~7" if a in ("DryNative", "FireAdapted") else "-")
        liquids = [CLEAN] + ([(x.text or "").strip() for x in li.findall("adaptedLiquids/li")] if li is not None else [])
        vmax = None
        if pd and pd.get("visual"):
            try:
                vmax = float(pd["visual"].split("~")[-1])
            except ValueError:
                vmax = None
        native = a in ("DryNative", "WetNative", "FireAdapted")
        if native and name not in fungi and name not in tree_exempt and vmax is None and pd is not None:
            notes.append("visualSizeRange inherited: tree or not UNMEASURED offline")
        tree = bool(native and name not in fungi and name not in tree_exempt and name not in not_trees and vmax is not None and vmax >= 2.999)
        woody = not tree and bool(pd and ((pd["harvestTag"] or "") == "Wood" or "Tree" in pd["parent"] or pd["harvested"] == "WoodLog"))
        conflict = name in wet_p and name in dry_b_p and choice == "Auto"
        if conflict:
            notes.append("multi-homed: in a wet AND a dry biome's list; seeded wet (the conservative rate) until its sheet rows decide")
        return {"plant": name, "archetype": a, "ruptureOdds": odds_label, "violentTop": top, "liquids": liquids,
                "sprouts": sprouts, "woody": woody, "tree": tree, "fungus": name in fungi, "conflict": conflict, "notes": notes}

    out = {}
    for b in sorted(ours_b):
        out[b] = {"file": biomes[b]["file"], "wet": b in wet_b, "fire": b in fire_b,
                  "rows": [one(p) for p in biomes[b]["plants"]]}
    return out, {"rosters": len(rosters), "biomes": len(ours_b), "rows": len(rows)}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--biome")
    a = ap.parse_args(argv)
    sheets, n = seed(*load())
    if not n["rosters"]:
        print("REFUSED: 0 RM_ExplosiveGrowthRosterDef found under src/ - every plant would seed as Vanilla (UNMEASURED, not a result)",
              file=sys.stderr)
        return 2
    if a.biome:
        if a.biome not in sheets:
            print("REFUSED: %r is not one of our biomes with a plant list (%d known): UNMEASURED, not an empty sheet"
                  % (a.biome, len(sheets)), file=sys.stderr)
            return 2
        sheets = {a.biome: sheets[a.biome]}
    if a.out:
        json.dump(sheets, open(a.out, "w", encoding="utf-8"), indent=1)
    rows = [r for s in sheets.values() for r in s["rows"]]
    by = {}
    for r in rows:
        by[r["archetype"]] = by.get(r["archetype"], 0) + 1
    print("archetype seed: %d rosters, %d of our biomes, %d sheet rows %s, %d multi-homed conflicts%s"
          % (n["rosters"], len(sheets), len(rows), json.dumps(by, sort_keys=True), sum(r["conflict"] for r in rows),
             (" -> " + a.out) if a.out else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
