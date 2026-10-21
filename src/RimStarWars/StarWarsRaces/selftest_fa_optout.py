#!/usr/bin/env python3
"""FACE_OPTOUT_REPAIR_ONLY_AT_HOME offline check: the Facial Animation opt-out we SHIP covers every xenotype of ours
that wears one of our RSW_ head types.

Facial Animation (workshop 1635901197) skips a race-xenotype only when its key is ticked off in the player's own
settings file; it reads no def or patchable XML. StarWarsRaces ships the list as data
(Defs/Misc/RSW_FacialAnimationOptOut.xml) and a postfix on FacialAnimationModSettings.ShouldDrawRaceXenoType
(Source/RSW_FacialAnimationOptOut.cs). This test checks, offline:
  1. every XenotypeDef under src/ whose genes force an RSW_ HeadTypeDef is on the shipped list (gene inheritance
     through Name/ParentName is followed);
  2. every listed name is a XenotypeDef defined under src/;
  3. the owner's own FA config entries `Human-RSW_*` are all on the list (UNMEASURED-free skip when the file is absent);
  4. the XML def class equals the C# class, the csproj compiles the opt-out file, and the C# target names match FA's
     DLL (method ShouldDrawRaceXenoType on FacialAnimation.FacialAnimationModSettings) when FA is installed;
  5. planted defects (an RSW_-head xenotype removed from the list; a list name that does not exist) are caught.
Offline only: it proves nothing about the live game. Live check is owed (fresh FA config, painted head stays clean).
    python3 src/RimStarWars/StarWarsRaces/selftest_fa_optout.py
"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(os.path.dirname(HERE))
DEF_XML = os.path.join(HERE, "Defs", "Misc", "RSW_FacialAnimationOptOut.xml")
CS = os.path.join(HERE, "Source", "RSW_FacialAnimationOptOut.cs")
CSPROJ = os.path.join(HERE, "Source", "RSW_StarWarsRaces.csproj")
FA_CONFIG = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Config/"
             "Mod_1635901197_FacialAnimationMod.xml")
FA_DLL = ("/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/1635901197/1.6/Assemblies/"
          "FacialAnimation.dll")
DEF_CLASS = "RimMandrake.StarWars.Races.RSW_FacialAnimationOptOutDef"


def shipped_list():
    root = ET.parse(DEF_XML).getroot()
    defs = [d for d in root if d.tag == DEF_CLASS]
    assert len(defs) == 1, "expected one %s in %s, found %d" % (DEF_CLASS, DEF_XML, len(defs))
    return [li.text.strip() for li in defs[0].findall("xenotypes/li") if li.text]


def scan_src():
    """XenotypeDef -> genes, GeneDef -> forced head types (inheritance resolved), defined HeadTypeDef names."""
    xenos, genes_raw, named, heads = {}, {}, {}, set()
    for f in glob.glob(os.path.join(SRC, "**", "Defs", "**", "*.xml"), recursive=True):
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError:
            continue
        for el in root:
            dn = el.findtext("defName")
            if el.tag == "XenotypeDef" and dn:
                xenos[dn] = [li.text.strip() for li in el.findall("genes/li") if li.text]
            elif el.tag == "GeneDef":
                ht = [li.text.strip() for li in el.findall("forcedHeadTypes/li") if li.text]
                rec = (ht, el.get("ParentName"), el.find("forcedHeadTypes") is not None)
                if el.get("Name"):
                    named[el.get("Name")] = rec
                if dn:
                    genes_raw[dn] = rec
            elif el.tag == "HeadTypeDef" and dn:
                heads.add(dn)

    def resolve(rec, depth=0):
        ht, parent, has = rec
        if has or not parent or depth > 10 or parent not in named:
            return ht
        return resolve(named[parent], depth + 1)

    gene_heads = {g: resolve(r) for g, r in genes_raw.items()}
    return xenos, gene_heads, heads


def check(listed, xenos, gene_heads, heads):
    errs = []
    listed_set = set(listed)
    wearers = {}
    for x, gl in xenos.items():
        rsw = sorted({h for g in gl for h in gene_heads.get(g, []) if h.startswith("RSW_") and h in heads})
        if rsw:
            wearers[x] = rsw
    for x in sorted(wearers):
        if x not in listed_set:
            errs.append("xenotype %s wears %s but is not on the FA opt-out list" % (x, wearers[x][0]))
    for x in listed:
        if x not in xenos:
            errs.append("listed %s is not a XenotypeDef under src/" % x)
    if len(listed_set) != len(listed):
        errs.append("duplicate names on the list")
    return errs, wearers


def main():
    fails = []
    listed = shipped_list()
    xenos, gene_heads, heads = scan_src()
    # sanity probe: the instrument can see (a zero here is a scan bug, not a pass)
    if len(xenos) < 50 or len(heads) < 50:
        print("FAIL scan too small: %d xenotypes, %d head types under src/" % (len(xenos), len(heads)))
        return 1
    errs, wearers = check(listed, xenos, gene_heads, heads)
    fails += errs
    print("list %d names; %d xenotypes under src/ wear an RSW_ head, %d covered" %
          (len(listed), len(wearers), sum(1 for x in wearers if x in set(listed))))

    if os.path.exists(FA_CONFIG):
        cfg = re.findall(r"<li>Human-(RSW_[^<]+)</li>", open(FA_CONFIG, encoding="utf-8-sig").read())
        missing = sorted(set(cfg) - set(listed))
        print("owner FA config: %d Human-RSW_ entries, %d missing from the shipped list" % (len(cfg), len(missing)))
        if not cfg:
            fails.append("owner FA config parsed to 0 Human-RSW_ entries (instrument blind?)")
        fails += ["owner config excludes %s but the shipped list does not" % m for m in missing]
    else:
        print("note: owner FA config absent on this machine; check 3 skipped")

    cs = open(CS, encoding="utf-8").read()
    ns = re.search(r"namespace\s+([\w.]+)", cs).group(1)
    if ns + ".RSW_FacialAnimationOptOutDef" != DEF_CLASS or "class RSW_FacialAnimationOptOutDef" not in cs:
        fails.append("XML def class %s does not match the C# class" % DEF_CLASS)
    tt = re.search(r'TargetType\s*=\s*"([^"]+)"', cs).group(1)
    tm = re.search(r'TargetMethodName\s*=\s*"([^"]+)"', cs).group(1)
    if "RSW_FacialAnimationOptOut.cs" not in open(CSPROJ, encoding="utf-8").read():
        fails.append("csproj does not compile RSW_FacialAnimationOptOut.cs (EnableDefaultCompileItems=false)")
    if os.path.exists(FA_DLL):
        try:
            import dnfile
            pe = dnfile.dnPE(FA_DLL)
            found = False
            tns, tname = tt.rsplit(".", 1)
            for t in pe.net.mdtables.TypeDef.rows:
                if str(t.TypeName) == tname and str(t.TypeNamespace) == tns:
                    found = any(str(m.row.Name) == tm for m in t.MethodList)
            if not found:
                fails.append("FA DLL has no %s.%s: the postfix would never apply" % (tt, tm))
            else:
                print("FA DLL: %s.%s present" % (tt, tm))
        except ImportError:
            print("note: dnfile missing; FA DLL target check skipped")
    else:
        print("note: FA not installed on this machine; DLL target check skipped")

    # planted defects
    if wearers:
        victim = sorted(wearers)[0]
        e, _ = check([x for x in listed if x != victim], xenos, gene_heads, heads)
        if not any(victim in m for m in e):
            fails.append("plant: removing %s from the list was not caught" % victim)
    e, _ = check(listed + ["RSW_NoSuchXenotype"], xenos, gene_heads, heads)
    if not any("RSW_NoSuchXenotype" in m for m in e):
        fails.append("plant: a nonexistent listed name was not caught")

    for f in fails:
        print("FAIL " + f)
    print("PASS" if not fails else "FAIL %d" % len(fails))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
