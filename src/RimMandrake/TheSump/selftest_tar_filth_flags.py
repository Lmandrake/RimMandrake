#!/usr/bin/env python3
"""selftest_tar_filth_flags.py — the tar filth-flag contract (LOAD13_CONFIGERRORS_TRIAGE_1).

Engine rules (RimSage, decompiled 1.6):
  * Verse/TerrainDef.cs:538 ConfigErrors: a terrain with generatedFilth must NOT
    have (filthAcceptanceMask & Terrain) — "makes terrain filth and also accepts it".
  * RimWorld/FilthMaker.TerrainAcceptsFilth: mask None -> refuse; otherwise
    (mask & placementMask) == placementMask.
  * FilthSourceFlags: Terrain=1 Natural=2 Unnatural=4 Pawn=8 Any=15.

Checks (each can go red):
  1. RM_TarShallow (patched mask + patched generatedFilth) does not accept Terrain.
  2. RUT_Filth_MouseTrack's placementMask is accepted by RM_TarShallow's patched mask
     (else the sump-mouse tracery never draws, silently).
  3. Every src TerrainDef that declares both generatedFilth and filthAcceptanceMask
     explicitly keeps Terrain out of the mask.
Mutants feed altered XML through the same functions and must go red.
"""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MASK_PATCH = ROOT / "src/RimUtinni/UtinniPatches/Patches/RUT_TarShallow_FilthAcceptance.xml"
GEN_PATCH = ROOT / "src/RimUtinni/UtinniPatches/Patches/RUT_TarShallow_GeneratedFilth.xml"
TRACK_DEF = ROOT / "src/RimMandrake/TheSump/Defs/ThingDefs_Misc/RUT_Filth_MouseTrack.xml"
FLAGS = {"None": 0, "Terrain": 1, "Natural": 2, "Unnatural": 4, "Pawn": 8, "Any": 15}


def _flags(node):
    if node is None:
        return None
    v = 0
    for li in node.findall("li"):
        v |= FLAGS[li.text.strip()]
    return v


def patched_mask(xml_text):
    for op in ET.fromstring(xml_text).iter("Operation"):
        if 'defName="RM_TarShallow"' in (op.findtext("xpath") or ""):
            m = _flags(op.find("value/filthAcceptanceMask"))
            if m is not None:
                return m
    return None


def patched_generates(xml_text):
    for op in ET.fromstring(xml_text).iter("Operation"):
        if 'defName="RM_TarShallow"' in (op.findtext("xpath") or ""):
            if (op.findtext("value/generatedFilth") or "").strip():
                return True
    return False


def track_mask(xml_text):
    for td in ET.fromstring(xml_text).iter("ThingDef"):
        if td.findtext("defName") == "RUT_Filth_MouseTrack":
            return _flags(td.find("filth/placementMask")) or 0
    return None


def tar_findings(mask_xml, gen_xml, track_xml):
    out = []
    mask, gen, pm = patched_mask(mask_xml), patched_generates(gen_xml), track_mask(track_xml)
    if mask is None:
        return ["UNMEASURED: no RM_TarShallow filthAcceptanceMask patch found"]
    if pm is None:
        return ["UNMEASURED: RUT_Filth_MouseTrack not found"]
    if gen and mask & FLAGS["Terrain"]:
        out.append("RM_TarShallow generates filth and its mask accepts Terrain (TerrainDef.cs:538 ConfigError)")
    if mask == 0 or (mask & pm) != pm:
        out.append(f"RM_TarShallow mask {mask} refuses RUT_Filth_MouseTrack placementMask {pm}: no mouse tracks")
    return out


def own_terrain_findings(files):
    out = []
    for f in files:
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError:
            continue
        for td in root.iter("TerrainDef"):
            gen = (td.findtext("generatedFilth") or "").strip()
            mask = _flags(td.find("filthAcceptanceMask"))
            if gen and mask is not None and mask & FLAGS["Terrain"]:
                out.append(f"{f.name}:{td.findtext('defName')} generates {gen} and accepts Terrain")
    return out


def main():
    fails = []
    m, g, t = MASK_PATCH.read_text(), GEN_PATCH.read_text(), TRACK_DEF.read_text()
    live = tar_findings(m, g, t)
    print("tar contract:", live or "ok")
    fails += live
    terrain_files = [p for p in (ROOT / "src").rglob("*.xml") if "TerrainDef" in p.read_text(errors="ignore")]
    own = own_terrain_findings(terrain_files)
    print(f"own TerrainDefs scanned in {len(terrain_files)} files:", own or "ok")
    fails += own
    # sanity: the scanner must see at least one generatedFilth terrain of ours
    seen = sum(1 for p in terrain_files if "<generatedFilth>" in p.read_text(errors="ignore"))
    if seen < 3:
        fails.append(f"SANITY: only {seen} files with generatedFilth seen (expected >=3)")
    # mutants
    mut = {
        "mask accepts Terrain": tar_findings(m.replace("<li>Natural</li>", "<li>Terrain</li>"), g, t),
        "track placed as Terrain": tar_findings(m, g, t.replace("<li>Pawn</li>", "<li>Terrain</li>")),
        "mask lacks Pawn": tar_findings(m.replace("<li>Pawn</li>", ""), g, t),
    }
    tmp = Path(__file__).with_name("_mutant_terrain.xml")
    try:
        tmp.write_text("<Defs><TerrainDef><defName>X</defName><generatedFilth>Filth_Dirt</generatedFilth>"
                       "<filthAcceptanceMask><li>Any</li></filthAcceptanceMask></TerrainDef></Defs>")
        mut["own terrain Any+generatedFilth"] = own_terrain_findings([tmp])
    finally:
        tmp.unlink(missing_ok=True)
    for name, res in mut.items():
        ok = bool(res) and not res[0].startswith("UNMEASURED")
        print(f"mutant {name}: {'red' if ok else 'STAYED GREEN'}")
        if not ok:
            fails.append(f"mutant stayed green: {name}")
    if any(f.startswith("UNMEASURED") for f in live):
        print("UNMEASURED")
        return 2
    print("FAIL" if fails else "PASS", *fails, sep="\n  ")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
