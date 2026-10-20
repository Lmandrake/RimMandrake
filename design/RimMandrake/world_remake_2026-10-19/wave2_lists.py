#!/usr/bin/env python3
"""Write the Wave 2 FULL list, removed list, Cherry Picker candidate, and the DEV/TEST/AUTHORING/SHIP/PAINT
profiles, each closure-checked (About.xml modDependencies incl. v1.6 + mod_facts class_ref). Offline.
Usage: wave2_lists.py <ids.txt> <cp_keys.txt> <roots.json>"""
import json, re, sys, os, xml.etree.ElementTree as ET
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
W = os.path.join(R, "design/RimMandrake/world_remake_2026-10-19/")
M = os.path.join(R, "infrastructure/state/modlists/")
C = os.path.join(R, "infrastructure/state/cherrypicker/")
idsf, cpf, rootsf = sys.argv[1:4]
wave = [l.strip().lower() for l in open(idsf) if l.strip()]
roots = json.load(open(rootsf))
HOLD = {"vanillaexpanded.vanillabackstoriesexpanded": "founders' backstories (Yeku VBE_GiftedBurnout, Nekko VBE_ClonedHeir, Tobb VBE_Standardbearer)",
        "vanillaquestsexpanded.generator": "founder Nekko's adulthood VQE_PowerArchitect02"}
DATE = "2026-10-19"


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


def needs(p):
    """hard edges of p: About modDependencies (+v1.6) and mod_facts class_ref (dependant -> dependee)."""
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


CLASSREF = {}
for dep, j in facts.items():
    for d in j.get("dependants_detail") or []:
        if "class_ref" in d["kinds"] or "hard_dep" in d["kinds"] or "hard_dep_v1.6" in d["kinds"]:
            CLASSREF.setdefault(d["packageId"].lower(), set()).add(dep)


BASE = {li.text.strip().lower() for li in ET.parse(M + "ModsConfig.FULL.LATEST.xml").getroot().find("activeMods")}


def closure_missing(members):
    """Edges whose target is absent. Targets already absent from FULL.LATEST (the 498 list that cold-loaded
    clean, Wave 1) are stale 10-10 class_ref rows (retired donors, composed members) and are not counted."""
    s = set(members); miss = []
    for p in members:
        for q in needs(p) | CLASSREF.get(p, set()):
            if q and q not in s and q in BASE:
                miss.append((p, q))
    return miss


full = rewrite(M + "ModsConfig.FULL.LATEST.xml", M + "ModsConfig.FULL.WAVE2_%d_%s.xml" % (498 - len(wave), DATE),
               lambda p: p not in wave)
print("FULL", len(full), "dupes", len(full) - len(set(full)), "wave left", set(full) & set(wave),
      "closure-missing", closure_missing(full))
tsv = {}
for l in list(open(W + "07_profile_assignment.tsv"))[1:]:
    c = l.rstrip("\n").split("\t"); tsv[c[0].lower()] = c
names = {p: ((about(p).findtext("name") if about(p) is not None else "?") or "?").strip() for p in set(full) | set(wave)}
with open(M + "wave2_removed_%d.txt" % len(wave), "w") as f:
    f.write("# Retirement Wave 2 (prepared %s, NOT deployed). packageId<TAB>name<TAB>why\n" % DATE)
    for p in wave:
        why = {"DROP-112": "05 SAFE", "DROP-DEEPER": "07 DROP-DEEPER"}.get(tsv.get(p, ["", "", ""])[2],
              "owner 2026-10-19: retire Minerals Framework (with its whole family)")
        f.write("%s\t%s\t%s\n" % (p, names[p], why))
# Cherry Picker
gone = {l.strip() for l in open(cpf) if l.strip()}
out, r = [], 0
for l in open(C + "CherryPicker.SHIP.xml", encoding="utf-8").read().split("\n"):
    m = re.match(r"\s*<li>([^<]+)</li>\s*$", l)
    if m and m.group(1).strip() in gone:
        r += 1; continue
    out.append(l)
open(C + "CherryPicker.SHIP.WAVE2_CANDIDATE.xml", "w", encoding="utf-8").write("\n".join(out))
k = ET.parse(C + "CherryPicker.SHIP.WAVE2_CANDIDATE.xml").getroot().find("ModSettings/keys")
open(C + "cp_wave2_keys_%d.txt" % len(gone), "w").write("\n".join(sorted(gone)) + "\n")
print("CP candidate keys", len(k), "removed", r)
# profiles
lab = {}
for p, c in tsv.items():
    lab[p] = c[2]
lab["mandrake.rm.pyrinth"] = "DEV"  # our absorbed copy; 07 labelled the donor det.epochspyrinth DROP-W1
for p in HOLD: lab[p] = "TEST"
fs = set(full)
sets = {
    "DEV": {"DEV", "DEV-INSTR"},
    "TEST": {"DEV", "DEV-INSTR", "TEST"},
    "AUTHORING": {"DEV", "DEV-INSTR", "TEST", "AUTHORING"},
    "SHIP": {"DEV", "TEST", "SHIP"},
}
res = {}
for name, labs in sets.items():
    mem = [p for p in full if lab.get(p) in labs]
    pulled = []
    while True:
        miss = [q for _, q in closure_missing(mem) if q in fs and q not in mem]
        if not miss: break
        for q in sorted(set(miss)): pulled.append(q)
        mem = [p for p in full if p in set(mem) | set(miss)]
    unl = [p for p in full if p not in lab]
    lst = rewrite(M + "ModsConfig.FULL.WAVE2_%d_%s.xml" % (len(full), DATE),
                  M + "ModsConfig.%s.WAVE2_%s.xml" % (name, DATE), lambda p, s=set(mem): p in s)
    res[name] = {"n": len(lst), "pulled": pulled, "missing": closure_missing(lst),
                 "dlc": sorted(p for p in lst if p.startswith("ludeon."))}
    print(name, len(lst), "pulled", pulled, "missing", res[name]["missing"], "dlc", len(res[name]["dlc"]))
print("unlabelled in FULL:", [p for p in full if p not in lab])
json.dump(res, open(os.path.join(os.path.dirname(cpf), "profiles.json"), "w"), indent=1)
