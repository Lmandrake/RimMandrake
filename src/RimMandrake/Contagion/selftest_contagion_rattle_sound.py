#!/usr/bin/env python3
"""Offline check: the Burn's rattle tell carries a sound (CONTAGION_MECHANICS_BUILD_1 §1, audio ruling 2026-10-03).

Static, no game. Goes red when:
  * RM_Contagion's sky extension stops naming <tellRattleSound>, or names a SoundDef that no installed
    Core/DLC def (nor one of ours) declares, or one declared <sustain>True</sustain> (PlayOneShot on a
    sustainer plays nothing useful);
  * RM_ContagionSkyExtension loses the field, or DoTells stops calling tellRattleSound.PlayOneShot inside the
    rattler branch, or the DoTells call stops sitting under RM_ContagionSettings.burnTellsEnabled (the
    toggle that must silence it).
Each rule is mutation-checked below so a blind regex cannot pass. The installed game Data unreachable =
the SoundDef half is UNMEASURED, never a pass.

The audible clip and its live timing are not read here (audio has no state read); the tells' live state is
the follow-up CONTAGION_SKY_STATE_TOOL_1.

    python3 src/RimMandrake/Contagion/selftest_contagion_rattle_sound.py
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
GAME_DATA = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data"
UNMEASURED_PHRASE = "UNMEASURED, not a pass or a fail"


def _read(rel):
    with open(os.path.join(HERE, rel), encoding="utf-8") as fh:
        return fh.read()


def _strip_xml(s):
    return re.sub(r"<!--.*?-->", "", s, flags=re.S)


def _strip_cs(s):
    return re.sub(r"//[^\n]*", "", s)


def sound_defs(paths):
    """defName -> is_sustainer for every SoundDef in the given XML files (ParentName sustain inherited)."""
    out, parents = {}, {}
    pending = []
    for p in paths:
        with open(p, encoding="utf-8-sig", errors="replace") as fh:
            text = _strip_xml(fh.read())
        for m in re.finditer(r"<SoundDef\b([^>]*)>(.*?)</SoundDef>", text, flags=re.S):
            attrs, body = m.group(1), m.group(2)
            sus = re.search(r"<sustain>\s*true\s*</sustain>", body, flags=re.I) is not None
            name = re.search(r'(?<!Parent)Name="([^"]+)"', attrs)
            parent = re.search(r'ParentName="([^"]+)"', attrs)
            if name:
                parents[name.group(1)] = sus
            dn = re.search(r"<defName>\s*([^<\s]+)\s*</defName>", body)
            if dn:
                pending.append((dn.group(1), sus, parent.group(1) if parent else None))
    for dn, sus, parent in pending:
        out[dn] = sus or bool(parent and parents.get(parent))
    return out


def check(cs_ext, cs_sky, biome_xml, defs):
    """Return (bad, unmeasured)."""
    bad, unmeasured = [], []
    if not re.search(r"public\s+SoundDef\s+tellRattleSound\s*;", _strip_cs(cs_ext)):
        bad.append("RM_ContagionSkyExtension has no public SoundDef tellRattleSound field")
    sky = _strip_cs(cs_sky)
    body = sky.split("private void DoTells(", 1)
    if len(body) < 2:
        bad.append("DoTells not found in RM_MapComponent_ContagionSky.cs (probe blind)")
    else:
        rattler = body[1].split("tellRattlers.NullOrEmpty()", 1)
        if len(rattler) < 2 or "tellRattleSound.PlayOneShot(" not in rattler[1]:
            bad.append("DoTells' rattler branch does not play tellRattleSound")
    gate = re.search(r"if\s*\(\s*RM_ContagionSettings\.burnTellsEnabled\s*\)\s*\{\s*DoTells\(", sky)
    if not gate:
        bad.append("the DoTells call is not gated by RM_ContagionSettings.burnTellsEnabled")
    m = re.search(r"<tellRattleSound>\s*([^<\s]+)\s*</tellRattleSound>", _strip_xml(biome_xml))
    if not m:
        bad.append("RM_Contagion.xml names no <tellRattleSound>: the rattle is silent")
    elif defs is None:
        unmeasured.append("SoundDef %s: installed game Data unreachable" % m.group(1))
    elif m.group(1) not in defs:
        bad.append("tellRattleSound %s is no installed or src SoundDef" % m.group(1))
    elif defs[m.group(1)]:
        bad.append("tellRattleSound %s is a sustainer; PlayOneShot needs a one-shot" % m.group(1))
    return bad, unmeasured


def main():
    cs_ext = _read("Source/RM_ContagionSkyExtension.cs")
    cs_sky = _read("Source/RM_MapComponent_ContagionSky.cs")
    biome = _read("Defs/BiomeDefs/RM_Contagion.xml")
    files = glob.glob(os.path.join(GAME_DATA, "*", "Defs", "**", "*.xml"), recursive=True)
    defs = None
    if files:
        files += glob.glob(os.path.join(ROOT, "src", "*", "*", "Defs", "**", "*.xml"), recursive=True)
        defs = sound_defs(files)
        # sanity probe: a known one-shot and a known sustainer must read correctly, or the parser is blind
        if defs.get("LeavesRustle") is not False or defs.get("RitualSustainer_Christian") is not True:
            print("sound-def parser is blind (LeavesRustle=%r RitualSustainer_Christian=%r): %s"
                  % (defs.get("LeavesRustle"), defs.get("RitualSustainer_Christian"), UNMEASURED_PHRASE))
            defs = None

    fails = []

    def expect(name, cond):
        print("%s  %s" % ("ok  " if cond else "FAIL", name))
        if not cond:
            fails.append(name)

    bad, un = check(cs_ext, cs_sky, biome, defs)
    expect("shipped: rattle sound wired, gated and one-shot (%s)" % (bad or "clean"), not bad)
    fake = {"LeavesRustle": False, "Ambient_Rain": True}
    mut = [
        ("field removed", cs_ext.replace("public SoundDef tellRattleSound;", ""), cs_sky, biome),
        ("PlayOneShot removed", cs_ext, cs_sky.replace("tellRattleSound.PlayOneShot(", "tellRattleSound.ToString("), biome),
        ("toggle gate removed", cs_ext, cs_sky.replace("if (RM_ContagionSettings.burnTellsEnabled)", "if (true)"), biome),
        ("xml unwired", cs_ext, cs_sky, re.sub(r"<tellRattleSound>[^<]*</tellRattleSound>", "", biome)),
        ("unknown sound", cs_ext, cs_sky, re.sub(r"<tellRattleSound>[^<]*</tellRattleSound>",
                                                 "<tellRattleSound>NoSuchSound</tellRattleSound>", biome)),
        ("sustainer named", cs_ext, cs_sky, re.sub(r"<tellRattleSound>[^<]*</tellRattleSound>",
                                                   "<tellRattleSound>Ambient_Rain</tellRattleSound>", biome)),
    ]
    for label, e, s, b in mut:
        mb, _ = check(e, s, b, fake)
        expect("mutant %-20s goes red" % label, bool(mb))
    if un:
        print("%s (%s)" % (UNMEASURED_PHRASE, "; ".join(un)))
    print("\n%s" % ("ALL OK" if not fails else "FAILED: %s" % fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
