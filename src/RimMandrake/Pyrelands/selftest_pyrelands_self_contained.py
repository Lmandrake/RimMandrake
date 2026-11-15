#!/usr/bin/env python3
"""T_SELF_CONTAINED_OFFLINE (Pyrelands 0.1.0, round-6 gaps g2 and g4; RIMMANDRAKE_FIX_PYRELANDS_ROUND_SIX_SEVENTEEN_GAPS).

Static reads of the shipped mod (XML comments are provenance and are skipped: ElementTree drops them):
  payload    RM_AcousticPayload_Pyrelands.xml: every top-level Operation is a PatchOperationFindMod on the Acoustic
             Scanner's own About.xml <name>, so with the scanner absent nothing applies and nothing logs; its xpath targets
             BiomeDef RM_Pyrelands, which our Defs declare; every thingDef / pawnRace / terrainDef it names is a defName
             one of our mods declares
  mutators   RM_RetiredMutatorPorts_Pyrelands.xml: every TileMutatorDef it declares is a mapped port (`new`) in
             design/RimMandrake/retired_mutators_port_map.json, and every Pyrelands port in the map is declared there
             (the canon save's tiles keep resolving; the donor-reference half is selftest_retired_mutator_ports.py)
  text       no label, description or Keyed text in the biome's Defs, Patches or Languages carries campaign vocabulary
             (RSW_/RUT_ names, Ashkarr, Jawa, Utinni, Tatooine, Star Wars canon words): the text is generic (PYRELANDS_GENERIC_TEXT_1)
  crossbiome the cross-biome section ships its "Unsupported" label (RM_Pyrelands_CrossBiomeUnsupported), and the settings
             screen draws it (owner 2026-10-15; the defaults-off half is T_SETTINGS_SWEEP_OFFLINE)
Every planted fault must go red and the clean copy stay green.
Run: python3 <this file>      exit 0 = PASS, 1 = FAIL
"""
import json
import os
import re
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SRC = os.path.join(REPO, "src")
SCANNER_ABOUT = os.path.join(SRC, "RimMandrake", "AcousticScanner", "About", "About.xml")
PORT_MAP = os.path.join(REPO, "design", "RimMandrake", "retired_mutators_port_map.json")
PAYLOAD = os.path.join("Patches", "RM_AcousticPayload_Pyrelands.xml")
PORTS = os.path.join("Defs", "RetiredMutatorPorts", "RM_RetiredMutatorPorts_Pyrelands.xml")
CAMPAIGN = re.compile(r"\b(RSW_\w+|RUT_\w+|Ashkarr\w*|Jawas?|Utinni|Tatooine|Star Wars|Jedi|Sith|Hutts?|sandcrawlers?|"
                      r"Mos Eisley|Tusken)\b", re.I)
TEXT_TAGS = {"label", "labelShort", "description", "descriptionHyperlinks", "jobString", "reportString", "letterLabel",
             "letterText", "text", "quietText", "reading", "gerund", "verb"}


def defnames(root_dir):
    out = set()
    for root, _, files in os.walk(root_dir):
        for f in [f for f in files if f.endswith(".xml")]:
            try:
                for el in ET.parse(os.path.join(root, f)).getroot().iter("defName"):
                    if el.text:
                        out.add(el.text.strip())
            except ET.ParseError:
                pass
    return out


def payload_errors(mod, declared):
    errs = []
    name = (ET.parse(SCANNER_ABOUT).getroot().findtext("name") or "").strip()
    if not name:
        return ["the Acoustic Scanner About.xml has no <name>"]
    root = ET.parse(os.path.join(mod, PAYLOAD)).getroot()
    ops = root.findall("Operation")
    if not ops:
        errs.append("payload: no Operation")
    for op in ops:
        if op.get("Class") != "PatchOperationFindMod":
            errs.append("payload: a top-level %s is not FindMod-guarded" % op.get("Class"))
            continue
        mods = [(li.text or "").strip() for li in op.findall("mods/li")]
        if mods != [name]:
            errs.append("payload: FindMod names %r, not the scanner's %r" % (mods, name))
        xp = op.findtext("match/xpath") or ""
        m = re.search(r'BiomeDef\[defName="([^"]+)"\]', xp)
        if not m or m.group(1) != "RM_Pyrelands" or "RM_Pyrelands" not in declared:
            errs.append("payload: xpath %r does not target our BiomeDef RM_Pyrelands" % xp)
        for tag in ("thingDefs", "pawnRaces", "terrainDefs"):
            for li in op.iter(tag):
                for x in li.findall("li"):
                    n = (x.text or "").strip()
                    if n and n not in declared:
                        errs.append("payload: %s %s is declared by none of our mods" % (tag, n))
    return errs


def mutator_errors(mod):
    pm = json.load(open(PORT_MAP, encoding="utf-8")).get("TileMutatorDef", {})
    mapped = {v.get("new") for v in pm.values() if isinstance(v, dict) and v.get("new")}
    root = ET.parse(os.path.join(mod, PORTS)).getroot()
    here = [(d.findtext("defName") or "").strip() for d in root.findall("TileMutatorDef")]
    errs = []
    if not here:
        errs.append("mutators: the ports file declares no TileMutatorDef")
    for n in here:
        if n not in mapped:
            errs.append("mutators: %s is no mapped port in retired_mutators_port_map.json" % n)
    pyre = {v.get("new") for v in pm.values() if isinstance(v, dict) and v.get("new") and "Pyre" in str(v.get("mod", ""))}
    for n in sorted(pyre - set(here)):
        errs.append("mutators: the map's Pyrelands port %s is not declared in the ports file" % n)
    return errs


def text_errors(mod):
    errs = []
    for sub in ("Defs", "Patches", "Languages"):
        for root, _, files in os.walk(os.path.join(mod, sub)):
            for f in [f for f in files if f.endswith(".xml")]:
                p = os.path.join(root, f)
                try:
                    tree = ET.parse(p).getroot()
                except ET.ParseError as e:
                    errs.append("text: %s does not parse (%s)" % (os.path.relpath(p, mod), e))
                    continue
                for el in tree.iter():
                    keyed = sub == "Languages" and el is not tree
                    if (el.tag in TEXT_TAGS or keyed) and el.text and CAMPAIGN.search(el.text):
                        errs.append("text: %s <%s> carries campaign vocabulary %r" % (
                            os.path.relpath(p, mod), el.tag, CAMPAIGN.search(el.text).group(0)))
    return errs


def crossbiome_errors(mod):
    errs = []
    keyed = os.path.join(mod, "Languages", "English", "Keyed", "RM_Pyrelands_CrossBiome.xml")
    t = ET.parse(keyed).getroot().findtext("RM_Pyrelands_CrossBiomeUnsupported") or ""
    if "unsupported" not in t.lower():
        errs.append("crossbiome: RM_Pyrelands_CrossBiomeUnsupported reads %r, no 'Unsupported'" % t)
    cs = open(os.path.join(mod, "Source", "RM_PyrelandsMod.cs"), encoding="utf-8").read()
    cs = re.sub(r"//[^\n]*", "", re.sub(r"/\*.*?\*/", "", cs, flags=re.S))
    if not re.search(r'\.Label\(\s*"RM_Pyrelands_CrossBiomeUnsupported"\.Translate\(\)', cs):
        errs.append("crossbiome: the settings screen never draws RM_Pyrelands_CrossBiomeUnsupported")
    return errs


def run(mod, declared=None):
    declared = declared if declared is not None else defnames(SRC)
    return payload_errors(mod, declared) + mutator_errors(mod) + text_errors(mod) + crossbiome_errors(mod)


def _sub(path, old, new, count=1):
    s = open(path, encoding="utf-8").read()
    if old not in s:
        raise AssertionError("mutant anchor %r not in %s" % (old, path))
    open(path, "w", encoding="utf-8").write(s.replace(old, new, count))


MUTANTS = [
    ("payload unguarded", PAYLOAD, 'Class="PatchOperationFindMod"', 'Class="PatchOperationSequence"'),
    ("payload names another mod", PAYLOAD, "<li>RimMandrake: Acoustic Scanner</li>", "<li>RimMandrake: Acoustic Scaner</li>"),
    ("payload targets another biome", PAYLOAD, 'defName="RM_Pyrelands"', 'defName="RM_Pyrelandz"'),
    ("payload names an undeclared def", PAYLOAD, "<li>RM_FE_Plant_ScorchFruit</li>", "<li>RM_FE_Plant_NoSuchFruit</li>"),
    ("mutator port unmapped", PORTS, "<defName>RM_GeothermalHotspots</defName>", "<defName>RM_GeothermalHotspotz</defName>"),
    ("campaign word in a def", PAYLOAD, "<quietText>Grass, ash", "<quietText>Jawa grass, ash"),
    ("unsupported label dropped", os.path.join("Languages", "English", "Keyed", "RM_Pyrelands_CrossBiome.xml"),
     "Unsupported: may work", "Experimental: may work"),
    ("unsupported label never drawn", os.path.join("Source", "RM_PyrelandsMod.cs"),
     'list.Label("RM_Pyrelands_CrossBiomeUnsupported".Translate());', 'list.Gap();'),
]


def main():
    declared = defnames(SRC)
    if len(declared) < 500:
        print("FAIL: the defName read sees only %d defs under src/ (instrument blind?)" % len(declared))
        return 1
    errs = run(HERE, declared)
    if errs:
        for e in errs:
            print("FAIL " + e)
        print("FAIL: %d problem(s) in the shipped Pyrelands" % len(errs))
        return 1
    tmp = tempfile.mkdtemp(prefix="pyre_selfcontained_")
    red = 0
    try:
        for name, rel, old, new in MUTANTS:
            mod = os.path.join(tmp, "m")
            shutil.rmtree(mod, ignore_errors=True)
            for sub in ("Patches", "Defs", "Languages", "Source"):
                shutil.copytree(os.path.join(HERE, sub), os.path.join(mod, sub))
            _sub(os.path.join(mod, rel), old, new)
            got = run(mod, declared - ({"RM_GeothermalHotspotz"} if "mutator" in name else set()))
            if got:
                red += 1
            else:
                print("FAIL mutant not caught: %s" % name)
        clean = os.path.join(tmp, "clean")
        for sub in ("Patches", "Defs", "Languages", "Source"):
            shutil.copytree(os.path.join(HERE, sub), os.path.join(clean, sub))
        clean_errs = run(clean, declared)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if red != len(MUTANTS) or clean_errs:
        print("FAIL: %d of %d mutants red; clean copy %s" % (red, len(MUTANTS), clean_errs or "green"))
        return 1
    print("PASS: payload FindMod-guarded on its own target, mutator ports mapped, text generic, cross-biome labelled "
          "unsupported; %d of %d mutants red, the clean copy green" % (red, len(MUTANTS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
