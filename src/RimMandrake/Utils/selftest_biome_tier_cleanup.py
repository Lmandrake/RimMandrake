#!/usr/bin/env python3
"""Selftest: BIOME_TIER_CLEANUP_1, the free biome mods carry no campaign prefix and no Star Wars IP.

Offline, a few seconds. Comments are not content: XML is read through ElementTree (comments dropped), C# string
literals only. Checks:
 1 no <defName>RUT_ and no Name="RUT_ in any mandrake.rm.* mod under src/RimMandrake (a mandrake.rut.* mod living
   there, e.g. AssailantSalvage, keeps RUT_ by its own tier; lint_xmlonly_defs demands it)
 2 no C# class RUT_* in a mandrake.rm.* mod
 3 no "RUT_ string literal in FeverWood/ or EnvironmentalHazards/ C#, except the named cross-tier references
   below (each a campaign def or key the free code reads only when the campaign layer is loaded)
 4 no retired name (RETIRED, the 2026-11-02 renames) survives as a reference anywhere under src/: XML element
   text, XML tag names, attribute values and C# literals; a texture/sound path (token after "/") is not a
   reference, the art files keep their names
 5 every alias in RM_BiomeTierCleanup_Aliases.xml maps a RETIRED name to the RM_ def of the same type defined
   under src/RimMandrake
 6 no Force / dianoga / Lekku / Bantha / Jawaese in the text or defNames of the item's biome mods
 6b no RM_-prefixed defName or Name= anywhere under src/ (every tier: an RM_ name is free-tier by its prefix,
   wherever the def lives) carries one of those words; the Slime riders in UtinniPatches were renamed
   RM_Gene_B2_VestigialHeadTails / _B4_ThunderSnore / _B12_StartleShout (their campaign-layer labels may
   still say lekku/bantha/Jawaese: that text is UtinniPatches', not a free mod's)
 7 Miasma: About.xml description names no RSW_/RUT_/Star Wars; RM_Miasma lists no Rain* weather; the
   thessamor names no Grey Sea
 8 Greentide: RM_Greentide carries RM_RoilLock and RM_RoilWeather is defined in the free mod
 9 sanity probes: each scanner fires on a planted defect (an instrument that cannot see reads as a FAIL)

    python3 src/RimMandrake/Utils/selftest_biome_tier_cleanup.py
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SRC = os.path.join(REPO, "src")
RM = os.path.join(SRC, "RimMandrake")

# The 73 defs and 14 C# classes renamed RUT_ -> RM_ in place by BIOME_TIER_CLEANUP_1 (2026-11-02).
RETIRED = """
RUT_BeastBulge RUT_BoughSoil RUT_Boughway RUT_CrecheMarker RUT_DeepHum RUT_DigShaft RUT_DigStratumTable
RUT_FeverForged_Painworn RUT_FeverForged_Saltblood RUT_FeverForged_Toughskin RUT_FeverTrunkCore
RUT_FeverTrunkHeartwood RUT_FeverWoodMirrorPool RUT_FeverWood_MirrorBreak RUT_FeverWood_MirrorList
RUT_Filth_MouseTrack RUT_FoundrySalvageCache RUT_GenStep_CrecheScatterer RUT_GenStep_DeepBlackMere
RUT_GenStep_GradientAxis RUT_GenStep_GroundRefusal RUT_GenStep_ScaldSailScatterer RUT_GenStep_ScatterPools
RUT_GenStep_ScatterSentinelGraveWards RUT_GenStep_TarBeastPlacement RUT_GradientSurge RUT_HardenedImmunity_Animal_Flu
RUT_HardenedImmunity_Animal_Plague RUT_HardenedImmunity_Flu RUT_HardenedImmunity_Malaria RUT_HardenedImmunity_Plague
RUT_HardenedImmunity_SleepingSickness RUT_HardenedImmunity_WoundInfection RUT_HaulPawnAndExit
RUT_IncidentWorker_ContagionProbe RUT_IncidentWorker_MirrorBreak RUT_IncidentWorker_SporeCloud
RUT_IncidentWorker_TarPitBelch RUT_IncidentWorker_WalkerSurfacing RUT_LampBlack RUT_LordJob_SentinelDefend
RUT_MapComponent_TheTenant RUT_MiasmaExposure RUT_MiasmaWeather RUT_MiasmaWeatherLock RUT_Miasma_FeverTempered
RUT_Miasma_LoamLunged RUT_Miasma_MotherDreamed RUT_Miasma_SaltBlooded RUT_Miasma_SwarmMarked RUT_MoatFusePost
RUT_Plant_FalseFruit RUT_Plant_FlashFlora RUT_PreservedDrawJoint RUT_Scald RUT_ScaldBreath RUT_ScaldExposure
RUT_ScaldMargin RUT_ScaldSteam RUT_ScaldSteamCarrier RUT_ScaldSteamLock RUT_ScaldVent RUT_ScaldWaterDeep
RUT_ScaldWaterMovingChestDeep RUT_ScaldWaterMovingShallow RUT_ScaldWaterOceanDeep RUT_ScaldWaterOceanShallow
RUT_ScaldWaterShallow RUT_ScaldWreckFrame RUT_ScaldWreckHull RUT_ScaldWreckTank RUT_SteamCatch RUT_StiltPlatform
RUT_StrandedDeformation RUT_SumpDuskLock RUT_SumpWeather RUT_Surge RUT_SurgeWeather RUT_TarMoat RUT_TarPitBelch
RUT_TarSpent RUT_TenantEmergenceSpawner RUT_ThinkTree_SumpMouseWander RUT_VentFlashSpray RUT_WalkerSurfacing
RUT_WeatherEvent_VentFlash RUT_WeatherOverlay_ScaldSteam
""".split()

# Free C# that names a campaign-layer def or key on purpose (read only when that layer is loaded).
CROSS_TIER_LITERALS = {
    "RUT_ContagionProbe": "its letter keys live in UtinniPatches' RUT_Forge_Mechanics.xml",
    "RUT_ContagionProbeDesc": "its letter keys live in UtinniPatches' RUT_Forge_Mechanics.xml",
    "RUT_SentinelDefend": "the DutyDef is UtinniPatches' (RUT_SentinelDefend.xml)",
    "RUT_": "RM_DefAliases.RenamedClassName maps a saved RUT_ class name to its RM_ rename",
}

IP_MODS = ("TheRot", "FeverWood", "GelatinousSlime", "Miasma", "TheSump", "RustCathedral", "LanternDeeps", "Greentide")
IP_RE = re.compile(r"\bForce\b|dianoga|Lekku|Bantha|Jawaese", re.I)

fails = []


def fail(msg):
    fails.append(msg)


def walk(root, exts):
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in (".git", "bin", "obj", "Textures", "Sounds", "pulse", "northstar")]
        for f in fn:
            if f.endswith(exts):
                yield os.path.join(dp, f)


def package_id(mod_dir):
    p = os.path.join(mod_dir, "About", "About.xml")
    try:
        return (ET.parse(p).getroot().findtext("packageId") or "").strip().lower()
    except (OSError, ET.ParseError):
        return ""


def rm_mods():
    out = []
    for d in sorted(os.listdir(RM)):
        full = os.path.join(RM, d)
        if os.path.isdir(full) and package_id(full).startswith("mandrake.rm."):
            out.append(full)
    return out


def xml_root(path):
    try:
        return ET.parse(path).getroot()
    except (ET.ParseError, OSError, UnicodeDecodeError):
        return None


CS_LIT = re.compile(r'"((?:[^"\\\n]|\\.)*)"')


def cs_literals(text):
    text = re.sub(r"//[^\n]*", "", text)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return CS_LIT.findall(text)


def ref_tokens(s, names):
    """Whole-token occurrences of names in s that are not path segments (not right after '/' or '\\')."""
    hits = []
    for m in re.finditer(r"(?<![A-Za-z0-9_])RUT_[A-Za-z0-9_]+", s):
        tok = m.group(0)
        if tok in names and (m.start() == 0 or s[m.start() - 1] not in "/\\"):
            hits.append(tok)
    return hits


def check_defnames(mods):
    n = 0
    for mod in mods:
        for p in walk(mod, (".xml",)):
            r = xml_root(p)
            if r is None:
                continue
            for el in r.iter():
                n += 1
                if el.tag == "defName" and (el.text or "").strip().startswith("RUT_"):
                    fail(f"1 RUT_ defName {el.text.strip()} in {os.path.relpath(p, REPO)}")
                if (el.get("Name") or "").startswith("RUT_"):
                    fail(f"1 RUT_ abstract Name={el.get('Name')} in {os.path.relpath(p, REPO)}")
        for p in walk(mod, (".cs",)):
            t = open(p, encoding="utf-8-sig", errors="replace").read()
            for m in re.finditer(r"\b(?:class|struct|enum|interface)\s+(RUT_\w+)", t):
                fail(f"2 C# type {m.group(1)} in {os.path.relpath(p, REPO)}")
    return n


def check_literals(roots):
    for root in roots:
        for p in walk(root, (".cs",)):
            for lit in cs_literals(open(p, encoding="utf-8-sig", errors="replace").read()):
                m = re.match(r"RUT_[A-Za-z0-9_]*", lit)
                if m and m.group(0) not in CROSS_TIER_LITERALS:
                    fail(f'3 "{m.group(0)} literal in {os.path.relpath(p, REPO)}')


def check_retired(names):
    seen_files = 0
    for p in walk(SRC, (".xml",)):
        if p.endswith("_Aliases.xml"):
            continue
        r = xml_root(p)
        if r is None:
            continue
        seen_files += 1
        for el in r.iter():
            bits = [el.tag if isinstance(el.tag, str) else "", el.text or ""] + list(el.attrib.values())
            for b in bits:
                for tok in ref_tokens(b, names):
                    fail(f"4 retired {tok} still referenced in {os.path.relpath(p, REPO)}")
    for p in walk(SRC, (".cs",)):
        t = open(p, encoding="utf-8-sig", errors="replace").read()
        for lit in cs_literals(t):
            for tok in ref_tokens(lit, names):
                fail(f"4 retired {tok} in a C# literal in {os.path.relpath(p, REPO)}")
        code = re.sub(r"//[^\n]*", "", re.sub(r"/\*.*?\*/", "", t, flags=re.S))
        code = CS_LIT.sub('""', code)
        for tok in ref_tokens(code, names):
            fail(f"4 retired {tok} in C# code in {os.path.relpath(p, REPO)}")
    return seen_files


def defined_rm(mods):
    """defName -> def element tag, over the free mods."""
    out = {}
    for mod in mods:
        for p in walk(os.path.join(mod, "Defs"), (".xml",)) if os.path.isdir(os.path.join(mod, "Defs")) else ():
            r = xml_root(p)
            if r is None:
                continue
            for d in r:
                dn = (d.findtext("defName") or "").strip()
                if dn:
                    out[dn] = d.tag
    return out


def check_aliases(mods, names):
    p = os.path.join(RM, "EnvironmentalHazards", "Defs", "Misc", "RM_BiomeTierCleanup_Aliases.xml")
    r = xml_root(p)
    if r is None:
        fail("5 RM_BiomeTierCleanup_Aliases.xml missing or unparseable")
        return 0
    defs = defined_rm(mods)
    rows = r.findall(".//aliases/li")
    for li in rows:
        fr, to, ty = li.findtext("from"), li.findtext("to"), li.findtext("defType")
        if fr not in names:
            fail(f"5 alias from {fr}: not a retired name")
        if to != "RM_" + (fr or "")[4:]:
            fail(f"5 alias {fr} -> {to}: not the in-place rename")
        if defs.get(to) != ty:
            fail(f"5 alias {fr} -> {to}: {to} is {defs.get(to)!r} under src/RimMandrake, alias says {ty!r}")
    if len(rows) < 50:
        fail(f"5 only {len(rows)} alias rows (expected the 61 saveable renames)")
    return len(rows)


def check_ip():
    seen = 0
    for mod in IP_MODS:
        for p in walk(os.path.join(RM, mod), (".xml",)):
            r = xml_root(p)
            if r is None:
                continue
            for el in r.iter():
                for b in [el.text or ""] + list(el.attrib.values()):
                    seen += 1
                    m = IP_RE.search(b)
                    if m and "MayRequire" not in el.attrib:
                        fail(f"6 IP word {m.group(0)!r} in {os.path.relpath(p, REPO)} <{el.tag}>")
    return seen


def rm_name_ip_hits(root):
    """(name, word) for every RM_ defName / Name= under an XML root that carries an IP word."""
    hits = []
    for el in root.iter():
        names = [el.attrib.get("Name") or ""]
        if el.tag == "defName":
            names.append((el.text or "").strip())
        for n in names:
            if n.startswith("RM_"):
                m = IP_RE.search(n)
                if m:
                    hits.append((n, m.group(0)))
    return hits


def check_rm_names_ip():
    seen = 0
    for p in walk(SRC, (".xml",)):
        r = xml_root(p)
        if r is None:
            continue
        seen += 1
        for n, w in rm_name_ip_hits(r):
            fail(f"6b IP word {w!r} in RM_ name {n} ({os.path.relpath(p, REPO)})")
    return seen


def check_miasma_greentide():
    about = xml_root(os.path.join(RM, "Miasma", "About", "About.xml"))
    desc = about.findtext("description") if about is not None else None
    if not desc:
        fail("7 Miasma About.xml has no description")
    elif re.search(r"RSW_|RUT_|Star Wars", desc):
        fail("7 Miasma About.xml description names RSW_/RUT_/Star Wars")
    defs = {}
    for p in walk(os.path.join(RM, "Miasma", "Defs"), (".xml",)):
        r = xml_root(p)
        for d in (r if r is not None else []):
            defs[(d.tag, (d.findtext("defName") or "").strip())] = d
    b = defs.get(("BiomeDef", "RM_Miasma"))
    if b is None:
        fail("7 BiomeDef RM_Miasma not found")
    else:
        rains = [c.tag for c in b.findall("baseWeatherCommonalities/*") if "Rain" in c.tag]
        if rains:
            fail(f"7 RM_Miasma still lists {rains}")
    t = defs.get(("ThingDef", "RM_Thessamor"))
    if t is None:
        fail("7 ThingDef RM_Thessamor not found")
    elif "Grey Sea" in (t.findtext("description") or ""):
        fail("7 the thessamor's description names the Grey Sea")
    gdefs = {}
    for p in walk(os.path.join(RM, "Greentide", "Defs"), (".xml",)):
        r = xml_root(p)
        for d in (r if r is not None else []):
            gdefs[(d.tag, (d.findtext("defName") or "").strip())] = d
    g = gdefs.get(("BiomeDef", "RM_Greentide"))
    if g is None or "RM_RoilLock" not in [(li.text or "").strip() for li in g.findall(".//li")]:
        fail("8 RM_Greentide does not carry RM_RoilLock")
    if ("WeatherDef", "RM_RoilWeather") not in gdefs:
        fail("8 RM_RoilWeather is not defined in the free Greentide mod")


def probes(names):
    """Each scanner must fire on a planted defect."""
    global fails
    saved, fails = fails, []
    if ref_tokens("<li>RUT_TarMoat</li>", names) != ["RUT_TarMoat"]:
        saved.append("9 probe: ref_tokens misses a bare retired name")
    if ref_tokens("Things/Building/RUT_TarMoat", names):
        saved.append("9 probe: ref_tokens counts a texture path as a reference")
    if ref_tokens("TerrainDef/RUT_TarMoat", names) != []:
        pass  # DefType/name is a lookup, not a path; it is caught in C# literals by its own probe below
    lits = cs_literals('var a = "RUT_Foo"; // "RUT_Bar"\n')
    if lits != ["RUT_Foo"]:
        saved.append(f"9 probe: cs_literals read {lits}")
    planted = ET.fromstring('<Defs><GeneDef><defName>RM_Gene_B2_VestigialLekku</defName></GeneDef>'
                            '<ThingDef Name="RM_BanthaBase"/><GeneDef><defName>RUT_Lekku</defName></GeneDef></Defs>')
    if sorted(n for n, _ in rm_name_ip_hits(planted)) != ["RM_BanthaBase", "RM_Gene_B2_VestigialLekku"]:
        saved.append("9 probe: rm_name_ip_hits")
    if not IP_RE.search("a faint sense of the Force") or IP_RE.search("a forced march"):
        saved.append("9 probe: IP_RE")
    fails = saved


def main():
    mods = rm_mods()
    if len(mods) < 20 or not any(m.endswith("FeverWood") for m in mods):
        fail(f"0 sanity: only {len(mods)} mandrake.rm mods found")
    names = set(RETIRED)
    if len(names) != 87:
        fail(f"0 RETIRED holds {len(names)} names, expected 87")
    n_el = check_defnames(mods)
    check_literals([os.path.join(RM, "FeverWood"), os.path.join(RM, "EnvironmentalHazards")])
    n_xml = check_retired(names)
    n_alias = check_aliases(mods, names)
    n_ip = check_ip()
    n_all = check_rm_names_ip()
    check_miasma_greentide()
    probes(names)
    if n_el < 10000 or n_xml < 1000 or n_ip < 1000 or n_all < 2000:
        fail(f"0 sanity: scanned {n_el} elements, {n_xml} xml files, {n_ip} IP strings, {n_all} src xml files "
             "(instrument blind?)")
    for f in fails:
        print("FAIL", f)
    print(f"{'PASS' if not fails else 'FAIL'} selftest_biome_tier_cleanup: {len(mods)} rm mods, {n_el} elements, "
          f"{n_xml} xml files, {n_alias} aliases, {n_ip} IP strings, {n_all} src xml files for 6b, {len(fails)} failures")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
