#!/usr/bin/env python3
"""Retirement Wave 3 lists (offline). Writes the FULL list, the removed list, the Cherry Picker candidate,
and regenerates the RULED_2026-10-20 profile lists IN PLACE without the drops; closure-checks every list
(About.xml modDependencies incl. v1.6 + mod_facts class_ref/hard_dep). Never touches FULL.LATEST or live.
Usage: wave3_lists.py <ids.txt> <cp_keys.txt> <roots.json>"""
import json, os, re, sys, xml.etree.ElementTree as ET
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
M = os.path.join(R, "infrastructure/state/modlists/")
C = os.path.join(R, "infrastructure/state/cherrypicker/")
idsf, cpf, rootsf = sys.argv[1:4]
wave = [l.strip().lower() for l in open(idsf) if l.strip()]
roots = json.load(open(rootsf))
DATE = "2026-10-20"
WHY = {
    "mlie.nwnrealfogofwar": "owner card 2026-10-19: \"we should get rid of the Fog of War. I think I'm done with it. It's ugly.\" (supersedes Route B)",
    "gravtide.mod": "keep/cut sheet 2026-10-20: DROP (11_ruled_keepcut.md)",
    "deon.rimtek.core": "keep/cut sheet 2026-10-20: DROP (11_ruled_keepcut.md)",
    "deon.rimtek.digipal": "keep/cut sheet 2026-10-20: DROP (11_ruled_keepcut.md)",
    "deon.rimtek.docmate": "keep/cut sheet 2026-10-20: DROP (11_ruled_keepcut.md)",
    "boots.sensiblefactions": "owner card row 6 2026-10-19: drop permanently (no skill/src uses it; bridge has faction tools)",
}


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


# who on the base list names a drop (hard edge or loadAfter)
for p in BASE:
    if p in wave: continue
    hard = (needs(p) | CLASSREF.get(p, set())) & set(wave)
    r = about(p); la = set()
    if r is not None:
        for tag in ("loadAfter", "forceLoadAfter"):
            la |= {(li.text or "").strip().lower() for li in r.findall(tag + "/li")} & set(wave)
    if hard or la:
        print("EDGE", p, "hard", sorted(hard), "loadAfter", sorted(la))
n = len(BASE) - len(set(wave) & BS)
fullf = M + "ModsConfig.FULL.WAVE3_%d_%s.xml" % (n, DATE)
full = rewrite(M + "ModsConfig.FULL.LATEST.xml", fullf, lambda p: p not in wave)
print("FULL", len(full), "dupes", len(full) - len(set(full)), "wave left", set(full) & set(wave),
      "closure-missing", closure_missing(full), "dlc", sum(p.startswith("ludeon.") for p in full))
with open(M + "wave3_removed_%d.txt" % len(wave), "w") as f:
    f.write("# Retirement Wave 3 (prepared %s, NOT deployed). packageId<TAB>name<TAB>why\n" % DATE)
    for p in wave:
        nm = (about(p).findtext("name") if about(p) is not None else "?").strip()
        f.write("%s\t%s\t%s\n" % (p, nm, WHY[p]))
gone = {l.strip() for l in open(cpf) if l.strip()}
out, rm = [], 0
for l in open(C + "CherryPicker.SHIP.xml", encoding="utf-8").read().split("\n"):
    m = re.match(r"\s*<li>([^<]+)</li>\s*$", l)
    if m and m.group(1).strip() in gone:
        rm += 1; continue
    out.append(l)
open(C + "CherryPicker.SHIP.WAVE3_CANDIDATE.xml", "w", encoding="utf-8").write("\n".join(out))
k = ET.parse(C + "CherryPicker.SHIP.WAVE3_CANDIDATE.xml").getroot().find("ModSettings/keys")
open(C + "cp_wave3_keys_%d.txt" % len(gone), "w").write("\n".join(sorted(gone)) + ("\n" if gone else ""))
print("CP candidate keys", len(k), "removed", rm)
for prof in ("DEV", "TEST", "AUTHORING", "SHIP", "PAINT"):
    f = M + "ModsConfig.%s.RULED_2026-10-20.xml" % prof
    before = [li.text.strip().lower() for li in ET.parse(f).getroot().find("activeMods")]
    lst = rewrite(f, f, lambda p: p not in wave)
    print(prof, len(before), "->", len(lst), "removed", sorted(set(before) - set(lst)),
          "missing", closure_missing(lst), "dlc", sum(p.startswith("ludeon.") for p in lst))
