#!/usr/bin/env python3
"""selftest: the three zero-tile donor biome mods are retired, and RUT_Umbra keeps its poison shrub.

Item DONOR_BIOME_MODS_RETIRE_ZERO_TILES_LEFT (owner 2026-10-21: "No more tech debt. No more donor debt."):
mlie.advancedbiomes, zylle.morevanillabiomes and ironscruff.primordialgeysers leave the list, PoisonShrub is
ported for RUT_Umbra (the only painted biome that named a def of theirs), and src/ stops naming them.

1. No saved mod profile (the *.RULED_2026-10-20 tiers and FULL.LATEST) activates one of the three.
2. infrastructure/state/facts/retired_mods.json lists all three (generators read it).
3. No src/ XML names one of the three packageIds outside a comment (MayRequire, <li> in loadAfter, ...).
4. RUT_Umbra's wildPlants names RM_PoisonShrub and not the donor PoisonShrub; RM_PoisonShrub is defined in
   src/ and its texPath resolves to at least one PNG in the defining mod's Textures folder.
5. The checker can SEE: a fixture naming a packageId in an element is flagged, the same text in a comment is not.
Dead DEF references (not packageIds) are retired_donor_refs.py check's job, per donor inventory.
Offline, no game."""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SRC = os.path.join(ROOT, "src")
MODLISTS = os.path.join(ROOT, "infrastructure", "state", "modlists")
RETIRED = os.path.join(ROOT, "infrastructure", "state", "facts", "retired_mods.json")
UMBRA = os.path.join(SRC, "RimUtinni", "UtinniPatches", "Defs", "BiomeDefs", "RUT_Umbra.xml")
DONORS = ("mlie.advancedbiomes", "zylle.morevanillabiomes", "ironscruff.primordialgeysers")
COMMENT = re.compile(r"<!--.*?-->", re.S)
PID = re.compile(r"(?<![\w.])(%s)(?![\w.])" % "|".join(re.escape(d) for d in DONORS), re.I)

fails = []


def check(ok, what):
    print(("  ok   " if ok else "  FAIL ") + what)
    if not ok:
        fails.append(what)


def pid_hits(text):
    """packageIds of the three donors named in XML text outside comments."""
    return sorted({m.group(1).lower() for m in PID.finditer(COMMENT.sub("", text))})


print("1. saved mod profiles")
profiles = sorted(glob.glob(os.path.join(MODLISTS, "ModsConfig.*.RULED_2026-10-20.xml")))
profiles.append(os.path.join(MODLISTS, "ModsConfig.FULL.LATEST.xml"))
check(len(profiles) >= 5, "found %d profiles (sanity: the RULED tiers and FULL.LATEST)" % len(profiles))
for p in profiles:
    ids = [(li.text or "").strip().lower() for li in ET.parse(p).getroot().find("activeMods")]
    check(len(ids) > 50, "%s parses to %d active mods (sanity)" % (os.path.basename(p), len(ids)))
    bad = [i for i in ids if i in DONORS]
    check(not bad, "%s activates none of the three %s" % (os.path.basename(p), bad or ""))

print("2. retired_mods.json")
sys.path.insert(0, HERE)
import retired_mods  # noqa: E402
for d in DONORS:
    check(retired_mods.is_retired(d), "retired_mods lists %s" % d)

print("3. src/ XML names no packageId of the three")
scanned, hits = 0, []
for f in glob.glob(os.path.join(SRC, "**", "*.xml"), recursive=True):
    scanned += 1
    with open(f, encoding="utf-8", errors="replace") as fh:
        found = pid_hits(fh.read())
    if found:
        hits.append("%s %s" % (os.path.relpath(f, ROOT), found))
check(scanned > 1000, "scanned %d XML files (sanity)" % scanned)
check(not hits, "no element or attribute names them" + ("".join("\n         " + h for h in hits)))

print("4. RUT_Umbra keeps its poison shrub, ported")
umbra = ET.parse(UMBRA).getroot().find("BiomeDef")
plants = [e.tag for e in umbra.find("wildPlants")]
check("RM_PoisonShrub" in plants, "RUT_Umbra wildPlants names RM_PoisonShrub")
check("PoisonShrub" not in plants, "RUT_Umbra wildPlants no longer names the donor PoisonShrub")
defined = []
for f in glob.glob(os.path.join(SRC, "**", "Defs", "**", "*.xml"), recursive=True):
    with open(f, encoding="utf-8", errors="replace") as fh:
        t = fh.read()
    if "<defName>RM_PoisonShrub</defName>" in t:
        defined.append(f)
check(len(defined) == 1, "RM_PoisonShrub is defined exactly once in src/ (%d)" % len(defined))
if defined:
    root = ET.parse(defined[0]).getroot()
    td = [e for e in root.iter("ThingDef") if (e.findtext("defName") or "") == "RM_PoisonShrub"][0]
    tex = td.findtext("graphicData/texPath") or ""
    mod = defined[0].split(os.sep + "Defs" + os.sep)[0]
    pngs = glob.glob(os.path.join(mod, "Textures", *tex.split("/"), "*.png"))
    check(bool(tex) and len(pngs) >= 1, "texPath %r resolves to %d PNG(s) in %s" % (
        tex, len(pngs), os.path.relpath(mod, ROOT)))

print("5. the checker can see")
check(pid_hits('<li>Mlie.AdvancedBiomes</li>') == ["mlie.advancedbiomes"], "flags a packageId in an element")
check(pid_hits('<x MayRequire="zylle.MoreVanillaBiomes">1</x>') == ["zylle.morevanillabiomes"],
      "flags a packageId in an attribute")
check(pid_hits('<!-- ironscruff.primordialgeysers --><a/>') == [], "ignores a packageId inside a comment")
check(pid_hits('<li>noxilie.regrow.wmb.advancedbiomes</li>') == [], "does not match a longer packageId")

print("\n%s: %d failure(s)" % (os.path.basename(__file__), len(fails)))
sys.exit(1 if fails else 0)
