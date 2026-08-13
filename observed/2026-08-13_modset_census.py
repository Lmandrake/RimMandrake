#!/usr/bin/env python3
import os, re, json, xml.etree.ElementTree as ET

CFG = "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Config/ModsConfig.xml"
ROOTS = [("workshop", "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100"),
         ("local",    "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods"),
         ("data",     "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data")]

tree = ET.parse(CFG); root = tree.getroot()
active = [(li.text or "").strip() for li in root.find("activeMods").findall("li")]
ke = root.find("knownExpansions")
known = [(li.text or "").strip() for li in ke.findall("li")] if ke is not None else []
raw_li = len(list(root.iter("li")))

present, noid, folders_scanned = {}, [], {}
for src, r in ROOTS:
    if not os.path.isdir(r): continue
    dirs = [d for d in sorted(os.listdir(r)) if os.path.isdir(os.path.join(r, d))]
    folders_scanned[r] = len(dirs)
    for d in dirs:
        folder = os.path.join(r, d)
        ax = None
        for ad in os.listdir(folder):
            if ad.lower() == "about" and os.path.isdir(os.path.join(folder, ad)):
                for f in os.listdir(os.path.join(folder, ad)):
                    if f.lower() == "about.xml":
                        ax = os.path.join(folder, ad, f); break
                break
        pid = name = None
        if ax:
            try:
                # ROOT-LEVEL child only: nested <packageId> inside <modDependencies> must not win
                mroot = ET.parse(ax).getroot()
                e = mroot.find("packageId");  pid  = (e.text or "").strip() if e is not None and e.text else None
                e = mroot.find("name");       name = (e.text or "").strip() if e is not None and e.text else None
            except Exception:
                txt = open(ax, encoding="utf-8-sig", errors="replace").read()
                # strip dependency blocks before regexing
                txt2 = re.sub(r"<(modDependencies|loadAfter|loadBefore|incompatibleWith)[^>]*>.*?</\1>", "", txt, flags=re.S | re.I)
                m = re.search(r"<packageId>(.*?)</packageId>", txt2, re.I | re.S)
                if m: pid = m.group(1).strip()
                m = re.search(r"<name>(.*?)</name>", txt2, re.I | re.S)
                if m: name = m.group(1).strip()
        rec = {"folder": folder, "name": name, "packageId": pid, "source": src, "about": ax}
        if pid: present.setdefault(pid.lower(), []).append(rec)
        else:   noid.append(rec)

missing = [{"index": i, "packageId": p} for i, p in enumerate(active) if p.lower() not in present]
active_lower = {p.lower() for p in active}
inactive = sorted(k for k in present if k not in active_lower)
dupes = {k: v for k, v in present.items() if len(v) > 1}

report = {
    "raw_li": raw_li, "activeMods_count": len(active), "knownExpansions": known,
    "folders_scanned": folders_scanned, "present_unique_packageIds": len(present),
    "folders_without_packageId": [r["folder"] for r in noid],
    "missing": missing, "missing_count": len(missing),
    "inactive_count": len(inactive),
    "inactive": [{"packageId": k, "name": present[k][0]["name"], "folder": present[k][0]["folder"]} for k in inactive],
    "duplicates": {k: [{"folder": x["folder"], "source": x["source"], "name": x["name"]} for x in v] for k, v in dupes.items()},
    "expansions_present": {e: [x["folder"] for x in present.get(e.lower(), [])] for e in known},
    "core_present": [x["folder"] for x in present.get("ludeon.rimworld", [])],
}
json.dump(report, open("/tmp/claude-1000/-mnt-d-Luke-dev-Rimworld/ecde650f-35cb-40a9-8cb8-5cff10e81ffd/scratchpad/report.json", "w"), indent=1)
json.dump({"generated": "2026-08-13", "modsconfig": CFG,
           "roots": [r for _, r in ROOTS],
           "method": "root-level <packageId> child of <ModMetaData> in About/About.xml; case-insensitive compare",
           "activeMods_order": active, "knownExpansions": known,
           "packageId_to_folders": {k: [x["folder"] for x in v] for k, v in present.items()},
           "folders_without_packageId": [r["folder"] for r in noid]},
          open("/mnt/d/Luke/dev/Rimworld/observed/2026-08-13_modset_map.json", "w"), indent=0)
print("active", len(active), "raw_li", raw_li, "present", len(present),
      "missing", len(missing), "inactive", len(inactive), "dupes", len(dupes), "noid", len(noid))
print("folders", folders_scanned)
