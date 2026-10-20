#!/usr/bin/env python3
"""ship_remap.py - apply the S10b remap table to a gravship layout (offline XML, no game).

  python3 ship_remap.py <in.xml> <out.xml> [--table ship_remap_S10b.json]
  python3 ship_remap.py --defs <layout.xml>      # print every def the layout names (one per line)

Table: design/RimMandrake/world_remake_2026-10-19/ship_remap_S10b.json. terrainDef rows are renamed;
thing rows are renamed or (to=null) dropped; special_filters_drop removes those storage-filter keys.
"""
import argparse, json, os, sys, xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
TABLE = os.path.join(REPO, "design/RimMandrake/world_remake_2026-10-19/ship_remap_S10b.json")


def layout_defs(root):
    """Every def the layout names: terrain, foundation, stuff, things, and special-filter keys."""
    d = {"terrain": set(), "thing": set(), "filter": set()}
    for tag in ("terrainDef", "foundationDef"):
        d["terrain"].update(e.text.strip() for e in root.iter(tag) if e.text and e.text.strip())
    for e in root.iter("stuffDef"):
        if e.text and e.text.strip():
            d["thing"].add(e.text.strip())
    for things in root.iter("things"):
        for li in things.findall("li"):
            n = li.find("defName")
            if n is not None and n.text:
                d["thing"].add(n.text.strip())
    for sf in root.iter("specialFilterStates"):
        for li in sf.findall("li"):
            k = li.find("key")
            if k is not None and k.text:
                d["filter"].add(k.text.strip())
    return d


def remap(root, table):
    n = {"terrain": 0, "thing": 0, "dropped": 0, "filters": 0}
    for tag in ("terrainDef", "foundationDef"):
        for e in root.iter(tag):
            r = table["terrain"].get((e.text or "").strip())
            if r:
                e.text = r["to"]; n["terrain"] += 1
    for things in root.iter("things"):
        for li in list(things.findall("li")):
            dn = li.find("defName")
            r = table["things"].get((dn.text or "").strip()) if dn is not None else None
            if r is None:
                continue
            if r["to"] is None:
                things.remove(li); n["dropped"] += 1
            else:
                dn.text = r["to"]; n["thing"] += 1
        if len(things) == 0:
            things.clear()
    drop = set(table["special_filters_drop"])
    for sf in root.iter("specialFilterStates"):
        for li in list(sf.findall("li")):
            k = li.find("key")
            if k is not None and (k.text or "").strip() in drop:
                sf.remove(li); n["filters"] += 1
    return n


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("src"); ap.add_argument("dst", nargs="?")
    ap.add_argument("--table", default=TABLE)
    ap.add_argument("--defs", action="store_true")
    a = ap.parse_args()
    tree = ET.parse(a.src)
    if a.defs:
        for k, v in layout_defs(tree.getroot()).items():
            for x in sorted(v):
                print(k, x)
        return 0
    n = remap(tree.getroot(), json.load(open(a.table)))
    ET.indent(tree, space="  ")
    tree.write(a.dst, encoding="utf-8", xml_declaration=True)
    print("remapped", n, "->", a.dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
