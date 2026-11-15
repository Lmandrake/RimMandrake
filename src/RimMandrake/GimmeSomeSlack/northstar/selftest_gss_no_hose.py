#!/usr/bin/env python3
# selftest-timeout: 60
"""L22 no_hose_in_gss (GSS dense proofs 2026-11-12): the hose moved to FlowWorks, so Gimme Some Slack ships no hose.

The check: no def under Defs/ or Patches/ whose defName, thingClass or texPath names a hose or a reel; no texture file
so named; no C# type so named under Source/. XML is PARSED (comments and the About description that says where the
hose went are not defs). The shared draw-order table (_Shared/SlackGeometry/DrawOrder.cs: LayerHose, HoseQueue) is
compiled into the DLL but is not under this mod's Source/ and names an altitude, not a thing; it is not scanned.

Mutants, each in a temp copy of the mod (never the tree): a planted RM_HoseReel ThingDef, a planted texture, a planted
C# class, a planted Patches def, a texture inside a Hose/ folder and a comp named only by its Class attribute (both added by the
blind challenge of 2026-11-15, which saw them pass the old scan) must each go red BY NAME; the clean copy and a hose COMMENT must stay green.
Exit 0 green, 1 red, 2 instrument broke (a mutant that never applied, or the clean copy read red).
"""
import re
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent   # the mod folder; this file sits in northstar/ so it never moves the mod hash
WORD = re.compile(r"hose|reel", re.I)
TYPE = re.compile(r"\b(?:class|struct|enum|interface|record)\s+(\w*(?:Hose|Reel|hose|reel)\w*)")


def scan(mod):
    """Every hose/reel thing the mod ships, as 'kind: name (file)' strings."""
    mod = Path(mod)
    hits = []
    for top in ("Defs", "Patches"):
        for f in sorted((mod / top).rglob("*.xml")) if (mod / top).is_dir() else []:
            try:
                root = ET.parse(f).getroot()
            except ET.ParseError as e:
                hits.append("unparsable: %s (%s)" % (f.name, e))
                continue
            for el in root.iter():
                if el.tag in ("defName", "thingClass", "texPath", "graphicClass", "compClass", "workerClass") and el.text and WORD.search(el.text):
                    hits.append("%s: %s (%s)" % (el.tag, el.text.strip(), f.relative_to(mod)))
                # a comp, worker or graphic named by its Class attribute (<li Class="CompProperties_HoseReel" />) is a class too
                cls = el.get("Class")
                if cls and WORD.search(cls):
                    hits.append("Class: %s (%s)" % (cls, f.relative_to(mod)))
    tex = mod / "Textures"
    for f in sorted(tex.rglob("*")) if tex.is_dir() else []:
        # the whole path under Textures/, so a hose texture inside a Hose/ folder is seen (the bar's false pass: "missing a texture folder")
        if f.is_file() and WORD.search(str(f.relative_to(tex))):
            hits.append("texture: %s" % f.relative_to(mod))
    src = mod / "Source"
    for f in sorted(src.rglob("*.cs")) if src.is_dir() else []:
        text = re.sub(r"//[^\n]*|/\*.*?\*/", "", f.read_text(encoding="utf-8", errors="replace"), flags=re.S)
        for m in TYPE.finditer(text):
            hits.append("type: %s (%s)" % (m.group(1), f.relative_to(mod)))
    return hits


def _copy(dst):
    for top in ("Defs", "Patches", "Textures", "Source"):
        if (HERE / top).is_dir():
            shutil.copytree(HERE / top, Path(dst) / top, ignore=shutil.ignore_patterns("bin", "obj"))
    return Path(dst)


def _plant_def(m):
    p = m / "Defs" / "RM_Planted.xml"
    p.write_text('<?xml version="1.0" encoding="utf-8"?>\n<Defs><ThingDef><defName>RM_HoseReel</defName>'
                 '<thingClass>Building</thingClass></ThingDef></Defs>\n', encoding="utf-8")
    return "defName: RM_HoseReel"


def _plant_tex(m):
    d = m / "Textures" / "Things"
    d.mkdir(parents=True, exist_ok=True)
    (d / "RM_HoseReel_south.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    return "texture: Textures/Things/RM_HoseReel_south.png"


def _plant_type(m):
    (m / "Source" / "Planted.cs").write_text("namespace X { public class Building_HoseReel : object { } }\n", encoding="utf-8")
    return "type: Building_HoseReel"


def _plant_patch(m):
    d = m / "Patches"
    d.mkdir(exist_ok=True)
    (d / "RM_Planted.xml").write_text('<?xml version="1.0" encoding="utf-8"?>\n<Patch><Operation Class="PatchOperationAdd">'
                                      '<xpath>Defs</xpath><value><ThingDef><defName>RM_FireHose</defName></ThingDef></value>'
                                      '</Operation></Patch>\n', encoding="utf-8")
    return "defName: RM_FireHose"


def _plant_tex_folder(m):
    d = m / "Textures" / "Things" / "Hose"
    d.mkdir(parents=True, exist_ok=True)
    (d / "Segment_south.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    return "texture: Textures/Things/Hose/Segment_south.png"


def _plant_class_attr(m):
    d = m / "Patches"
    d.mkdir(exist_ok=True)
    (d / "RM_PlantedComp.xml").write_text('<?xml version="1.0" encoding="utf-8"?>\n<Patch><Operation Class="PatchOperationAdd">'
                                          '<xpath>Defs/ThingDef[defName="PowerConduit"]/comps</xpath><value>'
                                          '<li Class="CompProperties_HoseReel" /></value></Operation></Patch>\n', encoding="utf-8")
    return "Class: CompProperties_HoseReel"


def _green_comment(m):
    p = m / "Defs" / "RM_PlantedComment.xml"
    p.write_text('<?xml version="1.0" encoding="utf-8"?>\n<Defs><!-- the hose reel lives in FlowWorks now --></Defs>\n', encoding="utf-8")
    return None


def main():
    if not (HERE / "Defs").is_dir():
        print("UNMEASURED: no Defs folder beside the selftest"); return 2
    real = scan(HERE)
    ok = True
    print("%s  T1_tree_ships_no_hose  %s" % ("PASS" if not real else "FAIL", real or "0 hose/reel defs, textures or types"))
    ok &= not real
    for name, plant in (("M1_planted_thingdef", _plant_def), ("M2_planted_texture", _plant_tex), ("M3_planted_class", _plant_type),
                        ("M4_planted_patch_def", _plant_patch),
                        ("M5_planted_texture_folder", _plant_tex_folder), ("M6_planted_comp_class_attr", _plant_class_attr), ("G1_hose_comment_stays_green", _green_comment), ("G0_clean_copy", None)):
        with tempfile.TemporaryDirectory(prefix="gss_nohose_") as tmp:
            m = _copy(tmp)
            before = scan(m)
            if before:                      # the clean copy must read green, or no mutant result means anything
                print("UNMEASURED  %s  clean copy read red: %s" % (name, before)); return 2
            want = plant(m) if plant else None
            got = scan(m)
        if want is None:
            good = not got
        else:
            good = any(h.startswith(want) for h in got)
        print("%s  %s  want=%s got=%s" % ("PASS" if good else "FAIL", name, want or "green", got))
        ok &= good
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
