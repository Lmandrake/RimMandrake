#!/usr/bin/env python3
"""selftest_vre_xeno_mods_retired.py — VRE_XENO_MODS_RETIRE_DEFOF_HOLDOUTS. Offline, no game.

VRE Archon, VRE Fungoid and VRE Phytokin hold five cut xenotypes (VRE_Archon, VRE_Fungoid, VRE_Gauranlenkin,
VRE_Animakin, VRE_Poluxkin) that their own assemblies name, so Cherry Picker cannot delete them; the cut is retiring
the three mods (NONSW_XENOTYPES_SCOPE_1). Reds if:
  * a current tier list (modlists/ModsConfig.*.RULED_2026-10-20.xml, ModsConfig.FULL.LATEST.xml) activates one;
  * Patches/VREArchon_MortisRename.xml (the Archon text patch) still exists;
  * an About.xml of ours lists one in modDependencies, or UtinniPatches' About still names Archon (its only
    Archon patch was MortisRename);
  * a src .xml names one of their mod names / packageIds in a patch that is not FindMod- or MayRequire-guarded
    (a FindMod <mods> block or a MayRequire attribute is the guard; anything else would fire without the mod);
  * a src .xml names one of THEIR defs (defNames read from the mods' own Workshop Defs) that we do not define,
    unguarded (VRE_ShortPregnancy, the Jawa xenotype's gene, is absorbed into StarWarsRaces under its own name);
  * the canonical start save (canon.yml planet.start_savegame) instances (`<def>X</def>`, streamed) a def of theirs
    that we do not define. Names in a filter or ignore list are tolerated (the loader drops a missing list entry).
Sanity probes: each tier list must parse with >50 active mods incl. ludeon.rimworld; the mods must yield >=100 defs
incl. VRE_Archon; the save must show >1000 `<def>`. Mutants (an injected archon line, an unguarded op, an unguarded
gene ref, the absorb removed) must go red. UNMEASURED (exit 2) if the Workshop copies or the save are unreadable.
Exit 0 pass, 1 fail, 2 UNMEASURED (save unreadable).
"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MODLISTS = ROOT / "infrastructure" / "state" / "modlists"
PIDS = ("vanillaracesexpanded.archon", "vanillaracesexpanded.fungoid", "vanillaracesexpanded.phytokin")
NAMES = ("Vanilla Races Expanded - Archon", "Vanilla Races Expanded - Fungoid", "Vanilla Races Expanded - Phytokin")
sys.path.insert(0, str(HERE.parents[1] / "RimMandrake" / "Utils"))
import game_paths  # noqa: E402

WORKSHOP = Path(game_paths.WORKSHOP)
MOD_DIRS = {"3067715093": PIDS[0], "3042690053": PIDS[1], "2927323805": PIDS[2]}   # Workshop ids, read from About.xml
SAVES = Path(game_paths.SAVES)
FAILS = []


def check(name, ok, detail=""):
    print("%s  %s %s" % ("ok  " if ok else "FAIL", name, "" if ok else detail))
    if not ok:
        FAILS.append(name)


def tier_lists():
    return sorted(glob.glob(str(MODLISTS / "ModsConfig.*.RULED_2026-10-20.xml"))) + [
        str(MODLISTS / "ModsConfig.FULL.LATEST.xml")]


def active(xml_text):
    return [(li.text or "").strip().lower() for li in ET.fromstring(xml_text.encode()).find("activeMods")]


def list_findings(xml_text):
    a = active(xml_text)
    if len(a) <= 50 or "ludeon.rimworld" not in a:
        return ["instrument blind: %d active" % len(a)]
    return [p for p in PIDS if p in a]


def unguarded(xml_text):
    """Elements naming a retired mod's packageId/name outside a FindMod <mods> list or MayRequire attribute."""
    root = ET.fromstring(xml_text.encode())
    out = []
    parent = {c: p for p in root.iter() for c in p}
    for el in root.iter():
        for k, v in el.attrib.items():
            if k.startswith("MayRequire"):
                continue
            if any(p in v.lower() for p in PIDS):
                out.append("attr %s=%s" % (k, v))
        txt = (el.text or "").strip()
        if txt and (txt.lower() in PIDS or txt in NAMES):
            p = parent.get(el)
            gp = parent.get(p) if p is not None else None
            if p is not None and p.tag == "mods" and gp is not None and "FindMod" in (gp.get("Class") or ""):
                continue
            out.append("<%s>%s" % (el.tag, txt))
    return out


def mod_defs():
    """defName -> packageId for every def the three mods define in 1.6 (or unversioned) Defs. {} if not installed."""
    out = {}
    for wid, pid in MOD_DIRS.items():
        for f in (WORKSHOP / wid).rglob("*.xml"):
            rel = f.relative_to(WORKSHOP / wid).as_posix()
            if re.match(r"1\.[0-5]/", rel) or "/Defs/" not in "/" + rel:
                continue
            for m in re.finditer(r"<defName>\s*([\w.]+)\s*</defName>", f.read_text(encoding="utf-8", errors="replace")):
                out[m.group(1)] = pid
    return out


def our_defs():
    out = set()
    for x in glob.glob(str(ROOT / "src" / "**" / "Defs" / "**" / "*.xml"), recursive=True):
        out |= set(re.findall(r"<defName>\s*([\w.]+)\s*</defName>", Path(x).read_text(encoding="utf-8", errors="replace")))
    return out


def _guarded(chain):
    """chain = the element and its ancestors. Guarded = a MayRequire attribute, or a FindMod/Conditional op above."""
    for e in chain:
        if any(k.startswith("MayRequire") for k in e.attrib):
            return True
        if any(w in (e.get("Class") or "") for w in ("FindMod", "Conditional")):
            return True
    return False


def def_ref_findings(xml_text, theirs, ours):
    """Elements naming one of their defs (as tag, text or defName="X" in an xpath) that we do not define, unguarded."""
    root = ET.fromstring(xml_text.encode())
    parent = {c: p for p in root.iter() for c in p}
    out = []
    for el in root.iter():
        txt = (el.text or "").strip()
        names = {el.tag, txt} | set(re.findall(r'defName\s*=\s*"([\w.]+)"', txt))
        hit = sorted(n for n in names if n in theirs and n not in ours)
        if not hit:
            continue
        chain, e = [], el
        while e is not None:
            chain.append(e)
            e = parent.get(e)
        if not _guarded(chain):
            out.append("<%s> %s" % (el.tag, ",".join(hit)))
    return out


def save_findings(path, theirs, ours):
    """Streams the save. Their defs instanced (`<def>X</def>`) that we do not define; blind below 1000 <def>."""
    n, bad = 0, set()
    pat = re.compile(r"<def>([\w.]+)</def>")
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            for m in pat.finditer(line):
                n += 1
                if m.group(1) in theirs and m.group(1) not in ours:
                    bad.add(m.group(1))
    if n <= 1000:
        return ["instrument blind: %d <def>" % n]
    return sorted(bad)


def start_save():
    canon = (ROOT / "infrastructure" / "state" / "canon.yml").read_text(encoding="utf-8")
    m = re.search(r"^\s*start_savegame:\s*(\S+)", canon, re.M)
    return SAVES / m.group(1) if m else None


def main():
    # 1. tier lists
    lists = tier_lists()
    check("tier lists found", len(lists) >= 6, str(lists))
    for f in lists:
        check("off list %s" % os.path.basename(f), list_findings(Path(f).read_text(encoding="utf-8")) == [],
              list_findings(Path(f).read_text(encoding="utf-8")))
    ship = Path(lists[0]).read_text(encoding="utf-8")
    check("mutant: injected archon reds",
          list_findings(ship.replace("<activeMods>", "<activeMods><li>vanillaracesexpanded.archon</li>", 1)) != [])

    # 2. the Archon text patch is gone
    check("MortisRename deleted", not (HERE / "Patches" / "VREArchon_MortisRename.xml").exists())

    # 3. About.xml
    for about in sorted(glob.glob(str(ROOT / "src" / "**" / "About" / "About.xml"), recursive=True)):
        r = ET.parse(about).getroot()
        deps = [(e.text or "").strip().lower() for e in r.iter("packageId")]
        deps += [(li.text or "").strip().lower() for md in r.iter("modDependencies") for li in md]
        bad = [p for p in PIDS if p in deps and r.findtext("packageId", "").strip().lower() != p]
        check("no hard dep %s" % os.path.relpath(about, ROOT), bad == [], bad)
    ut = (HERE / "About" / "About.xml").read_text(encoding="utf-8")
    check("UtinniPatches About names no Archon", "vanillaracesexpanded.archon" not in ut.lower())

    # 4. every src patch naming the mods is guarded
    hits = []
    for x in glob.glob(str(ROOT / "src" / "**" / "*.xml"), recursive=True):
        if "/About/" in x:
            continue
        t = Path(x).read_text(encoding="utf-8", errors="replace")
        if not any(p in t.lower() for p in PIDS) and not any(n in t for n in NAMES):
            continue
        try:
            hits += ["%s: %s" % (os.path.relpath(x, ROOT), u) for u in unguarded(t)]
        except ET.ParseError as e:
            hits.append("%s: parse %s" % (os.path.relpath(x, ROOT), e))
    check("src mod refs all guarded", hits == [], hits)
    mut = ('<Patch><Operation Class="PatchOperationSequence"><mods><li>%s</li></mods></Operation>'
           '<Operation Class="PatchOperationFindMod"><mods><li>%s</li></mods></Operation></Patch>' % (NAMES[0], NAMES[1]))
    check("mutant: unguarded op reds, FindMod one passes", len(unguarded(mut)) == 1, unguarded(mut))

    # 5. every src def reference to one of their defs is absorbed by us or guarded
    theirs = mod_defs()
    if len(theirs) < 100 or "VRE_Archon" not in theirs or "VRE_ShortPregnancy" not in theirs:
        print("UNMEASURED  the three mods' defs are not readable under %s (%d)" % (WORKSHOP, len(theirs)))
        return 2
    ours = our_defs()
    check("absorbed: VRE_ShortPregnancy defined in our src", "VRE_ShortPregnancy" in ours)
    refs = []
    for x in glob.glob(str(ROOT / "src" / "**" / "*.xml"), recursive=True):
        if "/About/" in x or "/Textures/" in x:
            continue
        t = Path(x).read_text(encoding="utf-8", errors="replace")
        if not any(k in t for k in ("VRE", "Archon", "Polux", "Dryad")):
            continue
        try:
            refs += ["%s: %s" % (os.path.relpath(x, ROOT), u) for u in def_ref_findings(t, theirs, ours)]
        except ET.ParseError:
            pass                                        # not a def file (the game would refuse it too)
    check("src def refs absorbed or guarded", refs == [], refs)
    mut = ('<Defs><XenotypeDef><genes><li>VRE_LongPregnancy</li></genes></XenotypeDef>'
           '<Operation Class="PatchOperationFindMod"><match><li>VREA_PsychicStorm</li></match></Operation></Defs>')
    check("mutant: an unguarded gene ref reds, a FindMod one passes",
          def_ref_findings(mut, theirs, ours) == ["<li> VRE_LongPregnancy"], def_ref_findings(mut, theirs, ours))

    # 6. the canonical start save
    sp = start_save()
    if sp is None or not sp.exists():
        print("UNMEASURED  start save not readable: %s" % sp)
        return 2
    sf = save_findings(sp, theirs, ours)
    check("start save %s: every instanced def of theirs is ours" % sp.name, sf == [], sf)
    check("mutant: their def unabsorbed reds", save_findings(sp, theirs, ours - {"VRE_ShortPregnancy"}) != [])

    print("FAIL %d: %s" % (len(FAILS), FAILS) if FAILS else "PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
