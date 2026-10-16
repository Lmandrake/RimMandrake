#!/usr/bin/env python3
"""save_donor_census.py - which donor defNames and packageIds a .rws savegame still names (Phase 0 step P6).

    python3 save_donor_census.py <save.rws> [--md out.md] [--json out.json]

Donor defNames are read from every `Defs/` folder under each donor's workshop `1.6/` (plus engine-made names:
Blueprint_/Blueprint_Install_/Frame_ for buildings, Corpse_/Meat_ for races). The save is parsed with ElementTree;
a hit is an element whose WHOLE text equals a donor name (instances, list rows, workgiver rows), grouped by the
element path. `Human` is counted as a control so a zero means "absent", not "blind". Also counts each donor
packageId in <meta>/<modIds>, and any donor name appearing as a substring of other text (reported, not rewritten).
Read-only. Exit 0 always; the report is the result.
"""
import argparse
import collections
import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

WS = "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100"
DONORS = {  # packageId (lower) -> (workshop id, action)
    "mlie.starwarsanimalcollection": ("3497316713", "retire"),
    "sarg.alphaanimals": ("1541721856", "retire"),
    "sarg.alphabiomes": ("1841354677", "report"),
}
CONTROL = "Human"


def donor_defs(wid):
    """{defName: defType} from every Defs/ folder under 1.6/."""
    out = {}
    for p in glob.glob(os.path.join(WS, wid, "1.6", "**", "*.xml"), recursive=True):
        if "/Defs/" not in p.replace("\\", "/"):
            continue
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        for d in root:
            dn = d.findtext("defName")
            if not dn:
                continue
            dn = dn.strip()
            out.setdefault(dn, d.tag)
            if d.tag == "ThingDef":
                if d.find("building") is not None or (d.findtext("category") or "").strip() == "Building":
                    for pre in ("Blueprint_", "Blueprint_Install_", "Frame_"):
                        out.setdefault(pre + dn, "ThingDef(engine)")
                if d.find("race") is not None:
                    out.setdefault("Corpse_" + dn, "ThingDef(engine)")
                    out.setdefault("Meat_" + dn, "ThingDef(engine)")
    return out


def path_of(stack):
    return "/".join(stack[-4:])


def census(save):
    names = {}
    for pkg, (wid, act) in DONORS.items():
        for dn, ty in donor_defs(wid).items():
            names.setdefault(dn, (pkg, ty, act))
    hits = collections.defaultdict(collections.Counter)  # name -> Counter(path)
    control = 0
    stack = []
    for ev, el in ET.iterparse(save, events=("start", "end")):
        if ev == "start":
            stack.append(el.tag)
            continue
        t = (el.text or "").strip()
        if t:
            if t == CONTROL and el.tag == "def":
                control += 1
            if t in names:
                hits[t][path_of(stack)] += 1
        stack.pop()
        if len(stack) <= 2:
            el.clear()
    raw = open(save, "rb").read()
    meta = {}
    for pkg in DONORS:
        meta[pkg] = len(re.findall(rb"(?i)<li>" + re.escape(pkg.encode()) + rb"</li>", raw))
    # substrings: donor names inside longer text (labels, Class= attributes, etc.)
    sub = {}
    for n in hits:
        whole = sum(hits[n].values())
        allc = len(re.findall(rb"(?<![A-Za-z0-9_])" + re.escape(n.encode()) + rb"(?![A-Za-z0-9_])", raw))
        if allc != whole:
            sub[n] = allc - whole
    return names, hits, control, meta, sub


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("save")
    ap.add_argument("--md")
    ap.add_argument("--json")
    a = ap.parse_args()
    names, hits, control, meta, sub = census(a.save)
    rows = sorted(hits, key=lambda n: (names[n][0], n))
    if a.json:
        json.dump({"control_Human_def": control, "meta": meta,
                   "hits": {n: {"pkg": names[n][0], "type": names[n][1], "paths": dict(hits[n])} for n in rows},
                   "token_extra": sub}, open(a.json, "w"), indent=1)
    lines = ["| donor | defName | def type | count | where (element path, count) |", "|---|---|---|---:|---|"]
    for n in rows:
        pkg, ty, act = names[n]
        where = "; ".join("`%s` %d" % (p, c) for p, c in hits[n].most_common())
        lines.append("| %s%s | `%s` | %s | %d | %s |" % (pkg, "" if act == "retire" else " (report)", n, ty,
                                                        sum(hits[n].values()), where))
    out = "\n".join(lines)
    summary = ["control `<def>Human</def>` = %d" % control,
               "donor defNames known: " + ", ".join("%s %d" % (p, sum(1 for v in names.values() if v[0] == p))
                                                     for p in DONORS),
               "donor names present in save: %d (total element hits %d)" % (len(rows),
                                                                           sum(sum(c.values()) for c in hits.values())),
               "packageIds as `<li>` rows: " + ", ".join("%s %d" % kv for kv in meta.items()),
               "names also appearing inside other text (not whole-element): " +
               (", ".join("`%s` +%d" % kv for kv in sub.items()) or "none")]
    rep = "\n".join("- " + s for s in summary) + "\n\n" + out + "\n"
    if a.md:
        open(a.md, "w").write(rep)
    print(rep if not a.md else "\n".join(summary))


if __name__ == "__main__":
    sys.exit(main())
