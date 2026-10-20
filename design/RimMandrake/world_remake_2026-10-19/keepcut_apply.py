#!/usr/bin/env python3
"""Apply the owner's keep/cut ruling (retirement_keepcut_sheet_2026-10-20) to the WAVE2 profile lists.
Writes ModsConfig.{DEV,TEST,AUTHORING,SHIP}.RULED_2026-10-20.xml (and PAINT only if changed). Offline; FULL.LATEST untouched.
cut = leave DEV/TEST/AUTHORING, stay in SHIP; the 4 DROPS leave every profile. Closure by mod_facts dependencies (About.xml)."""
import json, re, os, sys, xml.etree.ElementTree as ET
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
M = R + "/infrastructure/state/modlists/"
dec = json.load(open(R + "/Transient/retirement_keepcut_sheet_2026-10-20.decisions.json"))["decisions"]
DROPS = {"gravtide.mod", "deon.rimtek.core", "deon.rimtek.digipal", "deon.rimtek.docmate"}
facts = {}
for l in open(R + "/design/RimMandrake/mod_audit/facts/mod_facts.jsonl"):
    r = json.loads(l); facts[r["packageId"].lower()] = r
cuts = {k.lower() for k, v in dec.items() if v["decision"] == "cut"}
moves = cuts - DROPS
def load(p): return [e.text.strip() for e in ET.parse(M + "ModsConfig.%s.WAVE2_2026-10-19.xml" % p).find("activeMods")]
def write(p, ids):
    src = open(M + "ModsConfig.%s.WAVE2_2026-10-19.xml" % p, encoding="utf-8").read().split("\n")
    out, ina = [], False
    for l in src:
        if "<activeMods>" in l: ina = True
        if "</activeMods>" in l: ina = False
        m = re.match(r"\s*<li>([^<]+)</li>\s*$", l)
        if ina and m and m.group(1).strip().lower() not in ids: continue
        out.append(l)
    open(M + "ModsConfig.%s.RULED_2026-10-20.xml" % p, "w", encoding="utf-8").write("\n".join(out))
    return [e.text.strip() for e in ET.parse(M + "ModsConfig.%s.RULED_2026-10-20.xml" % p).find("activeMods")]
report, kept = {}, {}
for p in ["DEV", "TEST", "AUTHORING", "SHIP"]:
    old = load(p)
    gone = DROPS | (moves if p != "SHIP" else set())
    keep = {x.lower() for x in old} - gone
    # closure: iterate, restore any cut mod a retained mod hard-depends on
    while True:
        bad = {}
        for x in keep:
            for d in facts.get(x, {}).get("dependencies", []):
                dl = d.lower()
                if dl in gone and dl not in keep and dl in {o.lower() for o in old}: bad.setdefault(dl, []).append(x)
        bad = {d: s for d, s in bad.items() if d not in DROPS or True}
        if not bad: break
        for d in bad: keep.add(d); gone.discard(d)
        kept.setdefault(p, {}).update(bad)
    new = write(p, keep)
    report[p] = (len(old), len(new))
print(json.dumps(report)); print("closure restores:", json.dumps(kept))
paint = load("PAINT"); print("PAINT unchanged:", len(paint), "cut-in-PAINT:", [x for x in paint if x.lower() in cuts])
