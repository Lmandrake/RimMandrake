#!/usr/bin/env python3
"""donor_code_census.py -- which borrowed Alpha Animals creatures in OUR rosters ride the donor's own compiled code.

    python3 donor_code_census.py [--json out.json]

Item DONOR_DEFS_PORT_TO_OURS_1. Re-measures the 2026-09-24 census (15 HIGH of 66) against today's tree:

1. Roster membership: every XML under src/ parsed with ElementTree. A BiomeDef's <wildAnimals> children are read by
   ELEMENT NAME (BiomeAnimalRecord's custom loader: <AA_RedGoo>0.75</AA_RedGoo>, no <li>), and so are the <value>
   children of any PatchOperation whose own xpath targets a BiomeDef's wildAnimals (the patch-added half of a twin).
2. Donor resolution: the Alpha Animals mod (workshop 1541721856, packageId sarg.alphaanimals, 1.6 folder). Every
   ThingDef/PawnKindDef/PawnRenderTreeDef is parsed; a creature's ThingDef ParentName chain is walked (abstracts by
   Name=) and every attribute/element naming a class is collected, plus the PawnRenderTreeDef it names.
3. A class is DONOR-CODE when it is in the AlphaBehavioursAndEvents namespace -- the donor's one private DLL, which
   vanishes with the mod.

Sanity probe: prints the hit count for AA_RedGoo (known live) and the total AA_ roster rows, so a parse that sees
nothing cannot pass as "none use donor code".
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SRC = REPO / "src"
DONOR = Path("/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/1541721856")
PRIVATE_NS = "AlphaBehavioursAndEvents."
CLASS_KEYS = {"Class", "compClass", "workerClass", "deathActionWorkerClass", "thingClass", "hediffClass", "nodeClass",
              "graphicClass", "jobClass", "driverClass", "giverClass", "verbClass", "workerClass", "lordJobClass"}


def parse(p: Path):
    try:
        return ET.parse(p).getroot()
    except Exception:
        return None


def roster_rows():
    """{defName: [(biome, commonality, file, how)]} for every animal in an owned BiomeDef roster (direct or patch-added)."""
    rows = defaultdict(list)
    for p in SRC.rglob("*.xml"):
        if "/Textures/" in str(p) or "/art_source/" in str(p):
            continue
        root = parse(p)
        if root is None:
            continue
        for bd in root.iter("BiomeDef"):
            name = bd.findtext("defName") or bd.get("Name") or "?"
            wa = bd.find("wildAnimals")
            if wa is not None:
                for ch in wa:
                    if isinstance(ch.tag, str):
                        rows[ch.tag].append((name, (ch.text or "").strip(), str(p.relative_to(REPO)), "BiomeDef"))
        for op in root.iter():
            xp = op.find("xpath") if isinstance(op.tag, str) else None
            if xp is None or not xp.text or "BiomeDef" not in xp.text or "wildAnimals" not in xp.text:
                continue
            m = re.search(r'defName\s*=\s*["\']([^"\']+)', xp.text)
            biome = m.group(1) if m else "?"
            val = op.find("value")
            if val is None:
                continue
            for ch in val:
                if not isinstance(ch.tag, str):
                    continue
                if ch.tag == "wildAnimals":
                    for g in ch:
                        if isinstance(g.tag, str):
                            rows[g.tag].append((biome, (g.text or "").strip(), str(p.relative_to(REPO)), "patch"))
                else:
                    rows[ch.tag].append((biome, (ch.text or "").strip(), str(p.relative_to(REPO)), "patch"))
    return rows


def donor_defs():
    things, named, kinds, trees = {}, {}, {}, {}
    for p in (DONOR / "1.6").rglob("*.xml"):
        root = parse(p)
        if root is None:
            continue
        for el in root:
            if not isinstance(el.tag, str):
                continue
            dn, nm = el.findtext("defName"), el.get("Name")
            if nm:
                named[nm] = el
            if el.tag == "ThingDef" and dn:
                things[dn] = (el, p)
            elif el.tag == "PawnKindDef" and dn:
                kinds[dn] = el
            elif el.tag == "PawnRenderTreeDef" and dn:
                trees[dn] = el
    return things, named, kinds, trees


def classes_in(el):
    out = set()
    for e in el.iter():
        if not isinstance(e.tag, str):
            continue
        for k, v in e.attrib.items():
            if k in CLASS_KEYS and "." in v:
                out.add(v)
        if (e.tag in CLASS_KEYS or e.tag.endswith("Class")) and e.text and "." in e.text.strip():
            out.add(e.text.strip())
    return out


def chain(el, named):
    seen, cur = [], el
    while cur is not None and len(seen) < 20:
        seen.append(cur)
        cur = named.get(cur.get("ParentName")) if cur.get("ParentName") else None
    return seen


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    a = ap.parse_args(argv)
    rows = roster_rows()
    things, named, kinds, trees = donor_defs()
    aa = {k: v for k, v in rows.items() if k in things}
    print(f"SANITY roster AA_RedGoo rows={len(rows.get('AA_RedGoo', []))}  donor ThingDefs parsed={len(things)}  "
          f"roster creatures resolving to Alpha Animals={len(aa)}  rows={sum(len(v) for v in aa.values())}")
    out = []
    for dn in sorted(aa):
        el, p = things[dn]
        cls = set()
        for c in chain(el, named):
            cls |= classes_in(c)
        tree_name = None
        for c in chain(el, named):
            t = c.findtext(".//renderTree")
            if t:
                tree_name = t.strip()
                break
        if tree_name and tree_name in trees:
            cls |= {f"{x} (render tree {tree_name})" for x in classes_in(trees[tree_name])}
        if dn in kinds:
            cls |= {f"{x} (PawnKindDef)" for x in classes_in(kinds[dn])}
        private = sorted(c for c in cls if c.startswith(PRIVATE_NS))
        out.append({"defName": dn, "file": str(p.relative_to(DONOR)), "private": private,
                    "vef": sorted(c for c in cls if c.startswith("VEF.")),
                    "homes": sorted({(b, c) for b, c, _, _ in aa[dn]}), "renderTree": tree_name})
    hi = [o for o in out if o["private"]]
    print(f"RESULT {len(hi)} of {len(out)} roster Alpha Animals creatures use AlphaBehavioursAndEvents classes")
    for o in hi:
        print(" ", o["defName"], "|", ", ".join(f"{b} {c}" for b, c in o["homes"]), "|", "; ".join(o["private"]))
    if a.json:
        Path(a.json).write_text(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
