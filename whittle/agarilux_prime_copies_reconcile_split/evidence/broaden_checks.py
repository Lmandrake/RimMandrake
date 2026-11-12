#!/usr/bin/env python3
"""BROADEN checks (suggested by GPT, 2026-11-11), offline:
 A. every mod in the full load set (ModsConfig.FULL.LATEST, 316 mods): does any other mod ship Textures/RotSpecies/AgariluxPrime*
    or Textures/Things/Plants/AB_AgariluxPrime* (any loadFolder / version subfolder)? Which copy wins by load order?
 B. every PatchOperation xpath in every Patches/ folder of that load set, evaluated with lxml against the RM_AgariluxPrime def
    (wrapped in <Defs>): which ones select the def, its graphicData or texPath? (A broad patch the deleted repoint used to override
    would now win.)
 C. image identity: the surviving PNG's bytes vs the v3 landing commit and the art ledger's live sha.
"""
import hashlib, os, re, subprocess, sys, xml.etree.ElementTree as ET
from pathlib import Path
from lxml import etree
REPO = Path(__file__).resolve().parents[3]
RW = Path("/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld")
ROOTS = [REPO / "src", RW / "Data", Path("/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100"), RW / "Mods"]
active = [li.text.strip().lower() for li in ET.parse(REPO / "infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml").find("activeMods")]
# packageId -> mod dir (first root wins, src first, so our mods are the repo's own)
where = {}
for root in ROOTS:
    if not root.is_dir():
        print("UNREADABLE root", root); continue
    for about in list(root.glob("*/About/About.xml")) + list(root.glob("*/*/About/About.xml")):
        try:
            pid = (ET.parse(about).getroot().findtext("packageId") or "").strip().lower()
        except ET.ParseError:
            continue
        if pid and pid not in where:
            where[pid] = about.parent.parent
found = [p for p in active if p in where]
print(f"load set: {len(active)} active, {len(found)} located; missing: {[p for p in active if p not in where][:10]}")
# A
print("\n== A. texture files at either path, across the located load set (all subfolders)")
hits = []
for i, pid in enumerate(active):
    d = where.get(pid)
    if not d:
        continue
    for dp, dn, fn in os.walk(d):
        if "/.git" in dp:
            continue
        for f in fn:
            low = f.lower()
            if low.startswith("agariluxprime") or low.startswith("ab_agariluxprime"):
                p = Path(dp) / f
                hits.append((i, pid, str(p)))
for i, pid, p in hits:
    print(f"   load#{i:3d} {pid:40s} {p}  md5={hashlib.md5(open(p,'rb').read()).hexdigest()[:12]}")
print(f"   {len(hits)} file(s)")
# B
print("\n== B. patch xpaths selecting RM_AgariluxPrime / its graphicData / texPath")
src = etree.parse(str(REPO / "src/RimMandrake/TheRot/Defs/ThingDefs_Plants/RM_TheRot_DonorPorts.xml"))
defs = etree.Element("Defs")
for d in src.getroot():
    if isinstance(d.tag, str) and d.findtext("defName") == "RM_AgariluxPrime":
        defs.append(d)
doc = etree.ElementTree(defs)
target = defs[0]
watch = {id(target): "def", id(target.find("graphicData")): "graphicData", id(target.find("graphicData/texPath")): "texPath",
         id(target.find("graphicData/graphicClass")): "graphicClass"}
nops = nfiles = nbad = 0
nrel = [0]
sel = []
for pid in active:
    d = where.get(pid)
    if not d:
        continue
    for pf in d.rglob("*.xml"):
        if "Patches" not in pf.parts:
            continue
        nfiles += 1
        try:
            proot = etree.parse(str(pf)).getroot()
        except Exception:
            nbad += 1; continue
        for xp in proot.iter("xpath"):
            t = (xp.text or "").strip()
            if not t:
                continue
            nops += 1
            # RimWorld runs an xpath against the XmlDocument node; lxml's ElementTree.xpath starts at the root element,
            # so a relative "Defs/ThingDef[...]" would silently miss here. Anchor relative paths at the document.
            if not t.startswith("/"):
                nrel[0] += 1
                t = "/" + t
            try:
                r = doc.xpath(t)
            except Exception:
                continue
            if isinstance(r, list):
                for n in r:
                    k = watch.get(id(n))
                    if k:
                        sel.append((pid, str(pf), k, t))
print(f"   {nfiles} patch files, {nops} xpaths evaluated ({nbad} files unparsable; {nrel[0]} relative xpaths anchored at /)")
for pid, pf, k, t in sel:
    print(f"   selects {k:12s} {pid:30s} {pf.split('/')[-1]}  {t[:110]}")
broad = [s for s in sel if s[2] in ("graphicData", "texPath", "graphicClass")]
print(f"   xpaths reaching graphicData/texPath/graphicClass: {len(broad)}")
# C
print("\n== C. image identity of the survivor")
cur = REPO / "src/RimMandrake/TheRot/Textures/RotSpecies/AgariluxPrime.png"
sha = hashlib.sha256(cur.read_bytes()).hexdigest()
blob_now = subprocess.run(["git", "-C", str(REPO), "hash-object", str(cur)], capture_output=True, text=True).stdout.strip()
blob_v3 = subprocess.run(["git", "-C", str(REPO), "rev-parse", "9d83052dca:src/RimUtinni/UtinniPatches/Textures/RotSpecies/AgariluxPrime.png"],
                         capture_output=True, text=True).stdout.strip()
print(f"   survivor sha256 {sha}")
print(f"   git blob now {blob_now}; at the v3 landing commit 9d83052dca ('Land the 4 v3 regens', 2026-09-20) {blob_v3}: "
      f"{'IDENTICAL' if blob_now == blob_v3 else 'DIFFERENT'}")
dep = RW / "Mods/RimMandrake.Biomes/Biomes/TheRot/Textures/RotSpecies/AgariluxPrime.png"
if dep.is_file():
    print(f"   deployed copy sha256 {hashlib.sha256(dep.read_bytes()).hexdigest()}: {'IDENTICAL' if hashlib.sha256(dep.read_bytes()).hexdigest() == sha else 'DIFFERENT'}")
