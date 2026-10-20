#!/usr/bin/env python3
"""Retirement Wave 4 lists (offline). wave3_lists.py with per-id reasons and per-class profile scope.
Writes ModsConfig.FULL.WAVE4_<n>_2026-10-20.xml, wave4_removed_<n>.txt, and regenerates the RULED_2026-10-20 profile
lists IN PLACE; closure-checks every list (About.xml modDependencies incl. v1.6 + mod_facts class_ref/hard_dep).
Never touches FULL.LATEST or the live ModsConfig.
Usage: wave4_lists.py <wave4_ids.tsv: packageId<TAB>class<TAB>why> <roots.json> [<cp_keys.txt from wave3_prep.py>]
  class sheet-cut : leaves FULL, DEV, TEST, AUTHORING, SHIP (PAINT untouched: the final repaint's list)
  class world-only: leaves FULL, DEV, TEST, SHIP (AUTHORING and PAINT keep it: the final repaint needs it)
  class faction   : leaves every list"""
import json, os, re, sys, xml.etree.ElementTree as ET
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
M = os.path.join(R, "infrastructure/state/modlists/")
tsv, rootsf = sys.argv[1:3]
rows = [l.rstrip("\n").split("\t") for l in open(tsv) if l.strip() and not l.startswith("#")]
CLS = {r[0].lower(): r[1] for r in rows}
WHY = {r[0].lower(): r[2] for r in rows}
wave = list(CLS)
roots = json.load(open(rootsf))
DATE = "2026-10-20"
SCOPE = {"sheet-cut": {"FULL", "DEV", "TEST", "AUTHORING", "SHIP"},
         "world-only": {"FULL", "DEV", "TEST", "SHIP"},
         "faction": {"FULL", "DEV", "TEST", "AUTHORING", "SHIP", "PAINT"}}


def rewrite(src, dst, keep):
    out, inact = [], False
    for l in open(src, encoding="utf-8").read().split("\n"):
        if "<activeMods>" in l: inact = True
        if "</activeMods>" in l: inact = False
        m = re.match(r"\s*<li>([^<]+)</li>\s*$", l)
        if inact and m and not keep(m.group(1).strip().lower()):
            continue
        out.append(l)
    open(dst, "w", encoding="utf-8").write("\n".join(out))
    return [li.text.strip().lower() for li in ET.parse(dst).getroot().find("activeMods")]


def about(p):
    try:
        return ET.parse(roots[p] + "/About/About.xml").getroot()
    except Exception:
        return None


facts = {}
for l in open(os.path.join(R, "design/RimMandrake/mod_audit/facts/mod_facts.jsonl")):
    j = json.loads(l); facts[j["packageId"].lower()] = j
CLASSREF = {}
for dep, j in facts.items():
    for d in j.get("dependants_detail") or []:
        if {"class_ref", "hard_dep", "hard_dep_v1.6"} & set(d["kinds"]):
            CLASSREF.setdefault(d["packageId"].lower(), set()).add(dep)


def needs(p):
    r = about(p); h = set()
    if r is not None:
        for li in r.findall("modDependencies/li"):
            h.add((li.findtext("packageId") or "").strip().lower())
        for v in r.findall("modDependenciesByVersion"):
            for ver in v:
                if ver.tag == "v1.6":
                    for li in ver.findall("li"):
                        h.add((li.findtext("packageId") or "").strip().lower())
    return h


BASE = [li.text.strip().lower() for li in ET.parse(M + "ModsConfig.FULL.LATEST.xml").getroot().find("activeMods")]
BS = set(BASE)


def closure_missing(members):
    s = set(members)
    return [(p, q) for p in members for q in needs(p) | CLASSREF.get(p, set()) if q and q not in s and q in BS]


for p in BASE:
    if p in wave: continue
    hard = (needs(p) | CLASSREF.get(p, set())) & set(wave)
    r = about(p); la = set()
    if r is not None:
        for tag in ("loadAfter", "forceLoadAfter", "loadBefore", "forceLoadBefore"):
            la |= {(li.text or "").strip().lower() for li in r.findall(tag + "/li")} & set(wave)
    if hard or la:
        print("EDGE", p, "hard", sorted(hard), "order", sorted(la))


def drops(prof):
    return {p for p in wave if prof in SCOPE[CLS[p]]}


n = len(BASE) - len(drops("FULL") & BS)
fullf = M + "ModsConfig.FULL.WAVE4_%d_%s.xml" % (n, DATE)
full = rewrite(M + "ModsConfig.FULL.LATEST.xml", fullf, lambda p: p not in drops("FULL"))
print("FULL", len(BASE), "->", len(full), "dupes", len(full) - len(set(full)), "wave left", set(full) & drops("FULL"),
      "closure-missing", closure_missing(full), "dlc", sum(p.startswith("ludeon.") for p in full))
with open(M + "wave4_removed_%d.txt" % len(wave), "w") as f:
    f.write("# Retirement Wave 4 (prepared %s). packageId<TAB>name<TAB>class<TAB>why\n" % DATE)
    for p in wave:
        a = about(p)
        nm = ((a.findtext("name") if a is not None else None) or "?").strip()
        f.write("%s\t%s\t%s\t%s\n" % (p, nm, CLS[p], WHY[p]))
if len(sys.argv) > 3:  # Cherry Picker SHIP candidate without the keys that name a dropped def (wave3_prep.py's cp_wave3_keys.txt)
    C = os.path.join(R, "infrastructure/state/cherrypicker/")
    gone = {l.strip() for l in open(sys.argv[3]) if l.strip()}
    out, rm = [], 0
    for l in open(C + "CherryPicker.SHIP.xml", encoding="utf-8").read().split("\n"):
        m = re.match(r"\s*<li>([^<]+)</li>\s*$", l)
        if m and m.group(1).strip() in gone:
            rm += 1; continue
        out.append(l)
    open(C + "CherryPicker.SHIP.WAVE4_CANDIDATE.xml", "w", encoding="utf-8").write("\n".join(out))
    k = ET.parse(C + "CherryPicker.SHIP.WAVE4_CANDIDATE.xml").getroot().find("ModSettings/keys")
    open(C + "cp_wave4_keys_%d.txt" % len(gone), "w").write("\n".join(sorted(gone)) + ("\n" if gone else ""))
    print("CP candidate keys", len(k), "removed", rm)
for prof in ("DEV", "TEST", "AUTHORING", "SHIP", "PAINT"):
    f = M + "ModsConfig.%s.RULED_2026-10-20.xml" % prof
    before = [li.text.strip().lower() for li in ET.parse(f).getroot().find("activeMods")]
    d = drops(prof)
    lst = rewrite(f, f, lambda p: p not in d)
    print(prof, len(before), "->", len(lst), "removed", len(set(before) - set(lst)),
          "missing", closure_missing(lst), "dlc", sum(p.startswith("ludeon.") for p in lst))
