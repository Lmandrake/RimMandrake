#!/usr/bin/env python3
"""selftest_vre_xeno_mods_retired.py — VRE_XENO_MODS_RETIRE_DEFOF_HOLDOUTS. Offline, no game.

VRE Archon, VRE Fungoid and VRE Phytokin hold five cut xenotypes (VRE_Archon, VRE_Fungoid, VRE_Gauranlenkin,
VRE_Animakin, VRE_Poluxkin) that their own assemblies name, so Cherry Picker cannot delete them; the cut is retiring
the three mods (NONSW_XENOTYPES_SCOPE_1). Reds if:
  * a current tier list (modlists/ModsConfig.*.RULED_2026-10-20.xml, ModsConfig.FULL.LATEST.xml) activates one;
  * Patches/VREArchon_MortisRename.xml (the Archon text patch) still exists;
  * an About.xml of ours names one in modDependencies, loadAfter, loadBefore or any element, or UtinniPatches' About still names Archon (its only
    Archon patch was MortisRename);
  * a src .xml names one of their mod names / packageIds in a patch that is not FindMod- or MayRequire-guarded
    (a FindMod <mods> block or a MayRequire attribute is the guard; anything else would fire without the mod);
  * a src .xml names one of THEIR defs (defNames read from the mods' own Workshop Defs) that we do not define,
    unguarded (VRE_ShortPregnancy, the Jawa xenotype's gene, is absorbed into StarWarsRaces under its own name);
  * the canonical start save (canon.yml planet.start_savegame) names, as any element text or tag, a def of theirs
    we do not define, or holds a Class= of their assemblies; filter allowedDefs and ignored* <li> entries tolerated.
Sanity probes: each tier list must parse with >50 active mods incl. ludeon.rimworld; the mods must yield >=100 defs
incl. VRE_Archon; the save must show >1000 `<def>`. Mutants (an injected archon line, an unguarded op, an unguarded
gene ref, the absorb removed) must go red. UNMEASURED (exit 2) if the Workshop copies or the save are unreadable.
Exit 0 pass, 1 fail, 2 UNMEASURED (save unreadable). The save scan is iterparse over any tag (gen 3), not <def> only.
"""
import glob
import os
import re
import sys
import tempfile
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


def src_def_ref_findings(paths, theirs, ours):
    """def_ref_findings over files; a file is read only if one of its word tokens is a def of theirs."""
    refs = []
    for x in paths:
        if "/About/" in x or "/Textures/" in x:
            continue
        t = Path(x).read_text(encoding="utf-8", errors="replace")
        if not set(re.findall(r"[\w.]+", t)) & theirs.keys():
            continue
        try:
            refs += ["%s: %s" % (os.path.relpath(x, ROOT), u) for u in def_ref_findings(t, theirs, ours)]
        except ET.ParseError:
            pass                                        # not a def file (the game would refuse it too)
    return refs


TOLERATED_LISTS = ("allowedDefs", "disallowedDefs")    # a ThingFilter's def lists; plus any ignored* list


def mod_namespaces():
    """C# namespaces of their assemblies: each DLL's stem without '-' (VREArchon, VanillaRacesExpandedFungoid, ...)."""
    return sorted({f.stem.replace("-", "") for wid in MOD_DIRS for f in (WORKSHOP / wid).rglob("*.dll")})


def save_findings(path, theirs, ours, spaces):
    """Streams the save (iterparse). Findings: a def of theirs we do not define, as ANY element's text or tag
    (<def>, <xenotype>, <kindDef>, ...), except an <li> of a filter allowedDefs/disallowedDefs or an ignored* list
    (the loader drops a missing list entry); and any Class= in one of their assemblies' namespaces (the scribed
    object needs their DLL). Blind below 1000 <def>."""
    n, bad, stack = 0, set(), []
    for ev, el in ET.iterparse(str(path), events=("start", "end")):
        if ev == "start":
            stack.append(el.tag)
            c = el.get("Class") or ""
            if c.split(".")[0] in spaces:
                bad.add("Class=%s" % c)
            continue
        stack.pop()
        txt = (el.text or "").strip()
        if el.tag == "def":
            n += 1
        parent = stack[-1] if stack else ""
        tolerated = el.tag == "li" and (parent in TOLERATED_LISTS or parent.startswith("ignored"))
        for name in (txt, el.tag):
            if name in theirs and name not in ours and not tolerated:
                bad.add("<%s>%s" % ("/".join(stack[-2:] + [el.tag]), name))
        el.clear()
    if n <= 1000:
        return ["instrument blind: %d <def>" % n]
    return sorted(bad)


def save_mutants(theirs, ours, spaces):
    """Synthetic saves: each clause must go red, the tolerated list entries must not."""
    import tempfile
    filler = "<def>Steel</def>" * 1001
    cases = {
        "xenotype tag": ("<pawn><genes><xenotype>VRE_Archon</xenotype></genes></pawn>", True),
        "kindDef tag": ("<pawn><kindDef>ArchonWarrior</kindDef></pawn>", True),
        "def tag": ("<li><def>VRE_Archon</def></li>", True),
        "their def as a tag name": ("<map><VRE_Archon>1</VRE_Archon></map>", True),
        "their assembly Class": ('<components><li Class="VREArchon.GameComponent_TranscendentPawns" /></components>', True),
        "filter/ignore list entries tolerated": (
            "<filter><allowedDefs><li>VREA_Apparel_Archoplate</li></allowedDefs></filter>"
            "<c><ignoredFactions><li>VRE_Archons</li></ignoredFactions></c>", False),
    }
    out = {}
    for label, (body, want_red) in cases.items():
        with tempfile.NamedTemporaryFile("w", suffix=".rws", delete=False) as fh:
            fh.write("<savegame><game>%s%s</game></savegame>" % (filler, body))
        try:
            got = save_findings(fh.name, theirs, ours, spaces)
        finally:
            os.unlink(fh.name)
        out[label] = (got != []) == want_red, got
    return out


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

    # 3. About.xml: no element of ours (modDependencies, loadAfter, loadBefore, ...) names a retired mod
    def about_findings(xml_text):
        r = ET.fromstring(xml_text.encode())
        own = r.findtext("packageId", "").strip().lower()
        return ["<%s>%s" % (e.tag, (e.text or "").strip()) for e in r.iter()
                if ((e.text or "").strip().lower() in PIDS or (e.text or "").strip() in NAMES)
                and (e.text or "").strip().lower() != own]
    abouts = sorted(glob.glob(str(ROOT / "src" / "**" / "About" / "About.xml"), recursive=True))
    check("sanity: About.xml files found", len(abouts) >= 10, len(abouts))
    for about in abouts:
        bad = about_findings(Path(about).read_text(encoding="utf-8"))
        check("no dep or load hint %s" % os.path.relpath(about, ROOT), bad == [], bad)
    ut = (HERE / "About" / "About.xml").read_text(encoding="utf-8")
    check("UtinniPatches About names no Archon", "vanillaracesexpanded.archon" not in ut.lower())
    for tag in ("loadAfter", "loadBefore", "modDependencies"):
        li = "<li>vanillaracesexpanded.fungoid</li>" if tag != "modDependencies" else \
            "<li><packageId>vanillaracesexpanded.fungoid</packageId></li>"
        m = ut.replace("</ModMetaData>", "<%s>%s</%s></ModMetaData>" % (tag, li, tag), 1)
        check("mutant: a %s entry reds" % tag, m != ut and about_findings(m) != [], about_findings(m))

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
    src_xml = glob.glob(str(ROOT / "src" / "**" / "*.xml"), recursive=True)
    refs = src_def_ref_findings(src_xml, theirs, ours)
    check("src def refs absorbed or guarded", refs == [], refs)
    # the prefilter is the theirs set itself: 3 of their defs carry no VRE/Archon/Polux/Dryad keyword
    kwless = sorted(n for n in theirs if not any(k in n for k in ("VRE", "Archon", "Polux", "Dryad")))
    check("sanity: keyword-less defs of theirs exist to probe", len(kwless) >= 1, kwless)
    with tempfile.TemporaryDirectory() as td:
        probe = Path(td) / "Defs" / "zzprobe" / "p.xml"
        probe.parent.mkdir(parents=True)
        probe.write_text("<Defs><AbilityGroupDef>%s</AbilityGroupDef></Defs>"
                         % "".join("<li>%s</li>" % n for n in kwless), encoding="utf-8")
        got = src_def_ref_findings([str(probe)], theirs, ours)
        check("mutant: a src file naming only keyword-less defs of theirs reds",
              bool(got) and all(any(f.endswith(" " + n) for f in got) for n in kwless if n not in ours), got)
    mut = ('<Defs><XenotypeDef><genes><li>VRE_LongPregnancy</li></genes></XenotypeDef>'
           '<Operation Class="PatchOperationFindMod"><match><li>VREA_PsychicStorm</li></match></Operation></Defs>')
    check("mutant: an unguarded gene ref reds, a FindMod one passes",
          def_ref_findings(mut, theirs, ours) == ["<li> VRE_LongPregnancy"], def_ref_findings(mut, theirs, ours))

    # 6. the canonical start save
    sp = start_save()
    if sp is None or not sp.exists():
        print("UNMEASURED  start save not readable: %s" % sp)
        return 2
    spaces = mod_namespaces()
    check("sanity: their assembly namespaces read", "VREArchon" in spaces and len(spaces) >= 3, spaces)
    sf = save_findings(sp, theirs, ours, spaces)
    check("start save %s: names no def or class of theirs" % sp.name, sf == [], sf)
    check("mutant: their def unabsorbed reds",
          any("VRE_ShortPregnancy" in f for f in save_findings(sp, theirs, ours - {"VRE_ShortPregnancy"}, spaces)))
    for label, (ok, got) in save_mutants(theirs, ours, spaces).items():
        check("save mutant: %s" % label, ok, got)

    print("FAIL %d: %s" % (len(FAILS), FAILS) if FAILS else "PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
