#!/usr/bin/env python3
# selftest-timeout: 60
"""L22 no_hose_in_gss (GSS dense proofs 2026-11-12): the hose moved to FlowWorks, so Gimme Some Slack ships no hose.

The check: no def under Defs/ or Patches/ whose type (element tag), Class attribute or any field but prose (label, texPath,
topTexPath, texturePath, xpath ... all of them; description and the like skipped) names a hose, a reel or a pipe; no texture
file so named; no C# type so named under Source/; and no texture path in shipped C# (a string literal holding a "/", or a piece
of one built by concatenation, or a RM_/RSW_/RUT_ defName literal, under Source/ outside SelfTest/, which is its own project and never ships) that names one. XML is PARSED (comments and the About description that says where the
hose went are not defs). The shared draw-order table (_Shared/SlackGeometry/DrawOrder.cs: LayerHose, HoseQueue) is
compiled into the DLL but is not under this mod's Source/ and names an altitude, not a thing; it is not scanned.

Mutants, each in a temp copy of the mod (never the tree): a planted RM_HoseReel ThingDef, a planted texture, a planted
C# class, a planted Patches def, a texture inside a Hose/ folder and a comp named only by its Class attribute (both added by the
blind challenge of 2026-11-15, which saw them pass the old scan), a planted pipe ThingDef (blind cycle 2: the bar says "no pipe",
the old scan read hose|reel only), and three blind cycle 3 saw pass (a hose texture drawn from C# by a path literal, a pipe span
path built by concatenation, a ThingDef labelled "garden hose reel" under an innocent defName), and five blind cycle 4 saw pass (a
hose texture in a texture field the old tag list did not name, topTexPath; a reel texture in texturePath; a FlowWorks hose def type
under an innocent defName, named only by its element tag; an RM_HoseReel defName literal in C#, no "/" in it; a patch whose xpath
reaches into a hose reel's drawing) must each go red BY NAME; the clean copy and a hose COMMENT must stay green.
Exit 0 green, 1 red, 2 instrument broke (a mutant that never applied, or the clean copy read red).
"""
import re
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent   # the mod folder; this file sits in northstar/ so it never moves the mod hash
WORD = re.compile(r"hose|reel|pipe", re.I)   # the bar: "No hose, reel or pipe is drawn by this mod" (pipe added, blind cycle 2)
LIT = re.compile(r'"((?:[^"\\\n]|\\.)*)"')   # a C# string literal; one holding a "/" is (part of) a texture path
TYPE = re.compile(r"\b(?:class|struct|enum|interface|record)\s+(\w*(?:Hose|Reel|Pipe|hose|reel|pipe)\w*)")
# a defName literal by the naming scheme (RM_/RSW_/RUT_), e.g. DefDatabase lookups: no "/" in it (blind cycle 4)
DEFNAME = re.compile(r"^(?:RM|RSW|RUT)_\w+$")
# prose fields: they may say where the hose went; every other element's text is a def field and is read (blind cycle 4: the
# old fixed tag list missed topTexPath, texturePath and every modExtension field; label stays read, blind cycle 3)
PROSE = {"description", "jobString", "reportString", "letterText", "letterLabel", "tooltip", "text"}


def scan(mod):
    """Every hose/reel/pipe thing the mod ships, as 'kind: name (file)' strings (FlowWorks' pipe-pole spans are drawn with
    FlowWorks' own art and defs, so GSS ships no pipe of its own)."""
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
                if not isinstance(el.tag, str):
                    continue                    # a comment or processing instruction
                # the element's own tag: a def TYPE (<RimMandrake.FlowWorks.HoseLookDef>) names it under an innocent defName (blind cycle 4)
                if WORD.search(el.tag):
                    hits.append("tag: %s (%s)" % (el.tag, f.relative_to(mod)))
                # every def field but prose: label too (a hose reel under an innocent defName and texPath, blind cycle 3), any
                # texture field (topTexPath, texturePath, spanTexPath ...), and a patch's xpath into a hose def (blind cycle 4)
                if el.tag not in PROSE and el.text and el.text.strip() and WORD.search(el.text):
                    hits.append("%s: %s (%s)" % (el.tag, el.text.strip()[:120], f.relative_to(mod)))
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
        if "SelfTest" in f.relative_to(src).parts:
            continue                        # the selftest project is never shipped: its literals draw nothing
        for m in LIT.finditer(text):
            if "/" in m.group(1) and WORD.search(m.group(1)):
                hits.append("texpath: %s (%s)" % (m.group(1)[:80], f.relative_to(mod)))
            elif DEFNAME.match(m.group(1)) and WORD.search(m.group(1)):
                hits.append("defname-literal: %s (%s)" % (m.group(1)[:80], f.relative_to(mod)))
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


def _plant_pipe(m):
    p = m / "Defs" / "RM_PlantedPipe.xml"
    p.write_text('<?xml version="1.0" encoding="utf-8"?>\n<Defs><ThingDef><defName>RM_WaterPipe</defName>'
                 '<thingClass>Building</thingClass></ThingDef></Defs>\n', encoding="utf-8")
    return "defName: RM_WaterPipe"


def _plant_code_literal(m):
    (m / "Source" / "PlantedLiteral.cs").write_text('namespace X { static class D { static object T() => Verse.ContentFinder<UnityEngine.Texture2D>'
                                                    '.Get("RimMandrake/FlowWorks/Hose/HoseSegment", false); } }\n', encoding="utf-8")
    return "texpath: RimMandrake/FlowWorks/Hose/HoseSegment"


def _plant_code_concat(m):
    (m / "Source" / "PlantedConcat.cs").write_text('namespace X { static class D { static string P(string look) => '
                                                   '"RimMandrake/GimmeSomeSlack/Aerial/" + look + "/PipeSpan"; } }\n', encoding="utf-8")
    return "texpath: /PipeSpan"


def _plant_label(m):
    p = m / "Defs" / "RM_PlantedLabel.xml"
    p.write_text('<?xml version="1.0" encoding="utf-8"?>\n<Defs><ThingDef><defName>RM_CordCoil</defName><label>garden hose reel</label>'
                 '<thingClass>Building</thingClass><graphicData><texPath>RimMandrake/GimmeSomeSlack/Aerial/Coil</texPath></graphicData>'
                 '</ThingDef></Defs>\n', encoding="utf-8")
    return "label: garden hose reel"


def _plant_toptexpath(m):
    p = m / "Defs" / "RM_PlantedTop.xml"
    p.write_text('<?xml version="1.0" encoding="utf-8"?>\n<Defs><ThingDef><defName>RM_PlantedMast</defName><modExtensions>'
                 '<li><topTexPath>RimMandrake/FlowWorks/Hose/HoseReelTop</topTexPath></li></modExtensions></ThingDef></Defs>\n', encoding="utf-8")
    return "topTexPath: RimMandrake/FlowWorks/Hose/HoseReelTop"


def _plant_texturepath(m):
    p = m / "Defs" / "RM_PlantedOverlay.xml"
    p.write_text('<?xml version="1.0" encoding="utf-8"?>\n<Defs><DesignationDef><defName>RM_PlantedMark</defName>'
                 '<texturePath>RimMandrake/FlowWorks/Hose/ReelOverlay</texturePath></DesignationDef></Defs>\n', encoding="utf-8")
    return "texturePath: RimMandrake/FlowWorks/Hose/ReelOverlay"


def _plant_def_type_tag(m):
    p = m / "Defs" / "RM_PlantedLook.xml"
    p.write_text('<?xml version="1.0" encoding="utf-8"?>\n<Defs><RimMandrake.FlowWorks.HoseLookDef><defName>RM_Look_Scrapper</defName>'
                 '</RimMandrake.FlowWorks.HoseLookDef></Defs>\n', encoding="utf-8")
    return "tag: RimMandrake.FlowWorks.HoseLookDef"


def _plant_defname_literal(m):
    (m / "Source" / "PlantedDefName.cs").write_text('namespace X { static class D { public const string LegacyReelDef = "RM_HoseReel"; } }\n',
                                                    encoding="utf-8")
    return "defname-literal: RM_HoseReel"


def _plant_patch_xpath(m):
    d = m / "Patches"
    d.mkdir(exist_ok=True)
    (d / "RM_PlantedXpath.xml").write_text('<?xml version="1.0" encoding="utf-8"?>\n<Patch><Operation Class="PatchOperationAdd">'
                                           '<xpath>Defs/ThingDef[defName="RM_HoseReel"]/graphicData</xpath><value><drawSize>(2,2)</drawSize>'
                                           '</value></Operation></Patch>\n', encoding="utf-8")
    return 'xpath: Defs/ThingDef[defName="RM_HoseReel"]/graphicData'


def _green_selftest_literal(m):
    d = m / "Source" / "SelfTest"
    d.mkdir(parents=True, exist_ok=True)
    (d / "PlantedTestString.cs").write_text('namespace X { static class T { const string S = "a/hose/legacy name read"; } }\n', encoding="utf-8")
    return None


def _green_comment(m):
    p = m / "Defs" / "RM_PlantedComment.xml"
    p.write_text('<?xml version="1.0" encoding="utf-8"?>\n<Defs><!-- the hose reel lives in FlowWorks now --></Defs>\n', encoding="utf-8")
    return None


def main():
    if not (HERE / "Defs").is_dir():
        print("UNMEASURED: no Defs folder beside the selftest"); return 2
    real = scan(HERE)
    ok = True
    print("%s  T1_tree_ships_no_hose  %s" % ("PASS" if not real else "FAIL", real or "0 hose/reel/pipe defs, textures or types"))
    ok &= not real
    for name, plant in (("M1_planted_thingdef", _plant_def), ("M2_planted_texture", _plant_tex), ("M3_planted_class", _plant_type),
                        ("M4_planted_patch_def", _plant_patch),
                        ("M5_planted_texture_folder", _plant_tex_folder), ("M6_planted_comp_class_attr", _plant_class_attr), ("M7_planted_pipe_def", _plant_pipe),
                        ("M8_planted_code_texture_literal", _plant_code_literal), ("M9_planted_code_concat_path", _plant_code_concat),
                        ("M10_planted_label_hose_reel", _plant_label),
                        ("M11_planted_toptexpath", _plant_toptexpath), ("M12_planted_texturepath", _plant_texturepath),
                        ("M13_planted_def_type_tag", _plant_def_type_tag), ("M14_planted_defname_literal", _plant_defname_literal),
                        ("M15_planted_patch_xpath", _plant_patch_xpath), ("G2_selftest_literal_stays_green", _green_selftest_literal),
                        ("G1_hose_comment_stays_green", _green_comment), ("G0_clean_copy", None)):
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
