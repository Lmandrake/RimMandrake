#!/usr/bin/env python3
"""Offline proof for SUCCULENT_PLANTS_REDRAW_BORROWED_WARDROBE.

The item filed 14 defs whose sprites lived only in the donor mod
Vanilla Plants Expanded - Succulents (not Core 1.6). This check passes
(exit 0) when:
  1. every filed def's texPath resolves to an own PNG under src/*/Textures;
  2. no src XML graphic path anywhere lands in a donor succulent folder;
  3. when the donor mod is installed, no filed def's PNG is byte-identical
     to a donor PNG (a copied sprite is still borrowed).
Exit 1 on any failure, listing each.
"""
import glob
import hashlib
import os
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
SRC = os.path.join(ROOT, "src")
DONOR_DIR = "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/2198652536"
# The donor's Things/Plant folders (measured from the installed mod, 2026-11-03),
# used when the donor is not on disk.
DONOR_FOLDERS = {"AloeVera", "BunnyEarsCactus", "Echeveria", "FairyWashboard", "JadePlant",
                 "Peyote", "PincushionPlant", "Schlumbergera", "SnakePlant", "SweetheartPlant"}
FILED = ["RM_Glasskelle", "RM_Pulsebead", "RM_Rimebeard", "RM_Stillbloom", "RM_Simmerlace",
         "RM_Kettlewick", "RM_Vekkfan", "RM_Thurlsponge", "RM_Foamgorse", "RM_Seepcandle",
         "RM_Threshreed", "RM_NoothelmPlant", "RM_LungerFry", "RUT_LungerFry"]
PATH_TAGS = ("texPath", "iconPath", "graphicPath", "leaflessGraphicPath", "immatureGraphicPath")


def donor_folders():
    folders = set(DONOR_FOLDERS)
    pngs = glob.glob(os.path.join(DONOR_DIR, "**", "Textures", "Things", "Plant", "*", "*.png"),
                     recursive=True)
    folders |= {os.path.basename(os.path.dirname(p)) for p in pngs}
    md5s = {hashlib.md5(open(p, "rb").read()).hexdigest()
            for p in glob.glob(os.path.join(DONOR_DIR, "**", "*.png"), recursive=True)}
    return folders, md5s, bool(pngs)


def is_donor(path, folders):
    parts = path.strip().split("/")
    return len(parts) >= 3 and parts[0] == "Things" and parts[1] == "Plant" and parts[2] in folders


def own_pngs(texpath):
    hits = []
    for tex in glob.glob(os.path.join(SRC, "**", "Textures"), recursive=True):
        base = os.path.join(tex, texpath)
        hits += glob.glob(base + ".png") + glob.glob(base + "_*.png")
        if os.path.isdir(base):
            hits += glob.glob(os.path.join(base, "*.png"))
    return hits


def main():
    folders, md5s, donor_present = donor_folders()
    bad, found = [], {}
    for xml in glob.glob(os.path.join(SRC, "**", "*.xml"), recursive=True):
        try:
            root = ET.parse(xml).getroot()
        except ET.ParseError:
            continue
        for el in root.iter():
            if el.tag in PATH_TAGS and el.text and is_donor(el.text, folders):
                bad.append("donor path %s in %s" % (el.text.strip(), os.path.relpath(xml, ROOT)))
            dn = el.findtext("defName")
            if dn in FILED:
                tps = [t.text.strip() for t in el.iter("texPath") if t.text]
                if tps:
                    found.setdefault(dn, []).extend(tps)
    for dn in FILED:
        if dn not in found:
            bad.append("%s: no def with a texPath found" % dn)
            continue
        for tp in found[dn]:
            pngs = own_pngs(tp)
            if not pngs:
                bad.append("%s: texPath %s resolves to no PNG under src/*/Textures" % (dn, tp))
            for p in pngs:
                if hashlib.md5(open(p, "rb").read()).hexdigest() in md5s:
                    bad.append("%s: %s is a byte copy of a donor PNG" % (dn, os.path.relpath(p, ROOT)))
            print("%-18s %s (%d png)" % (dn, tp, len(pngs)))
    print("donor installed: %s (%d donor PNGs hashed)" % (donor_present, len(md5s)))
    for b in bad:
        print("FAIL", b)
    print("PASS" if not bad else "FAIL %d" % len(bad))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
