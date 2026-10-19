#!/usr/bin/env python3
"""Wave 1 dependency closure: which RETAINED active mod hard-depends (About.xml modDependencies,
incl. modDependenciesByVersion v1.6) on one of the 39? Also reports loadAfter (order only, not a stop).
Usage: closure.py <ModsConfig.xml> <ids.txt> <out.json>"""
import json, os, sys, xml.etree.ElementTree as ET
cfg, idsf, out = sys.argv[1:4]
active = [li.text.strip().lower() for li in ET.parse(cfg).getroot().find("activeMods")]
wave = [l.strip().lower() for l in open(idsf) if l.strip()]
roots = ["/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods",
         "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100"]
about = {}
for r in roots:
    for d in os.listdir(r):
        p = os.path.join(r, d, "About", "About.xml")
        if not os.path.isfile(p):
            continue
        try:
            root = ET.parse(p).getroot()
        except Exception as e:
            continue
        pid = (root.findtext("packageId") or "").strip().lower()
        if pid and pid not in about:
            about[pid] = (p, root)
def deps(root):
    hard, order = set(), set()
    for li in root.findall("modDependencies/li"):
        hard.add((li.findtext("packageId") or "").strip().lower())
    for v in root.findall("modDependenciesByVersion"):
        for ver in v:
            if ver.tag == "v1.6":
                for li in ver.findall("li"):
                    hard.add((li.findtext("packageId") or "").strip().lower())
    for tag in ("loadAfter", "forceLoadAfter"):
        for li in root.findall(tag + "/li"):
            order.add((li.text or "").strip().lower())
    return hard, order
missing_wave = [w for w in wave if w not in active]
missing_about = [a for a in active if a not in about and not a.startswith("ludeon.")]
retained = [a for a in active if a not in wave]
hard_hits, order_hits, inwave = [], [], []
for a in retained:
    if a not in about:
        continue
    h, o = deps(about[a][1])
    for w in wave:
        if w in h:
            hard_hits.append({"dependant": a, "on": w, "about": about[a][0]})
        if w in o:
            order_hits.append({"dependant": a, "on": w})
for a in wave:
    if a in about:
        h, _ = deps(about[a][1])
        for w in h:
            if w in wave:
                inwave.append({"dependant": a, "on": w})
res = {"active": len(active), "wave": len(wave), "wave_not_active": missing_wave,
       "active_without_about": missing_about, "retained": len(retained),
       "HARD_retained_on_wave": hard_hits, "loadAfter_retained_on_wave": order_hits,
       "hard_within_wave": inwave}
json.dump(res, open(out, "w"), indent=1)
print(f"active {len(active)} wave {len(wave)} not-active {missing_wave} no-about {len(missing_about)} "
      f"HARD retained->wave {len(hard_hits)} loadAfter {len(order_hits)} within-wave {len(inwave)}")
for h in hard_hits:
    print("HARD", h["dependant"], "->", h["on"])
