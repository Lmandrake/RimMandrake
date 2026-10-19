#!/usr/bin/env python3
"""selftest_xenotype_cut_nonsw.py — NONSW_XENOTYPES_SCOPE_1 (owner card 2026-10-09: cut every remaining
non-Star-Wars xenotype, same rule as the twelve; repoint raider xenotype sets). Offline, no game.

Reds if:
  * Patches/XenotypeCut_NonSW_SpawnSets.xml lacks a Conditional>Remove (all defs) for one of the 31, or an
    op is not Conditional>Remove with matching xpaths;
  * the def dump holds a xenotypeSet reference to one of the 31 on a path the patch does not reach — and, when
    the dump is post-patch (PirateWaster no longer names DV_Buzzer), ANY remaining reference (a live leak);
  * CherryPicker.SHIP.xml lacks a typed `XenotypeDef/<X>` key for one of the 26 cut defs, carries one for the
    five assembly-bound defs that stay (VRE_Archon/Fungoid/Phytokin 3), carries a bare type-agnostic key
    (a xenotype defName can also be a HediffDef), or lacks a companion key (Outland ascension/implanter,
    meta/retromorphosis) or one of the three cut scenarios;
  * any src .xml/.cs names one of the 31 in a race/xenotype position outside the cut file.
UNMEASURED (exit 2) without a readable dump. Sanity probes and mutants must go red.
"""
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parents[1] / "RimMandrake" / "Utils"))
PATCH = HERE / "Patches" / "XenotypeCut_NonSW_SpawnSets.xml"
PATCH_REL = "src/RimUtinni/UtinniPatches/Patches/XenotypeCut_NonSW_SpawnSets.xml"
SHIP = ROOT / "infrastructure" / "state" / "cherrypicker" / "CherryPicker.SHIP.xml"

CUT_DEF = ("BX_Beliar DV_Avaloi DV_Bogleg DV_Brawnum DV_Buzzer DV_Keshig DV_Venator HBX_Highborn KAR_Orc XylTitan "
           "BS_FrostJotunInBlue").split()
# the Alpha Genes 15 (AG_* and VRE_Ocularkin) left with sarg.alphagenes, retired 2026-10-18
# names compiled into their own mod's assembly: def kept, unreachable, until the mod is retired
KEPT = "VRE_Archon VRE_Fungoid VRE_Gauranlenkin VRE_Animakin VRE_Poluxkin".split()
ALL = CUT_DEF + KEPT
SCENARIOS = ("BX_BeliarStart",)
FAILS = []


def check(name, ok, detail=""):
    print("%s  %s %s" % ("ok  " if ok else "FAIL", name, "" if ok else detail))
    if not ok:
        FAILS.append(name)


def patch_findings(xml_text):
    covered, probs = set(), []
    for op in ET.fromstring(xml_text.encode()).findall("Operation"):
        m = op.find("match")
        if op.get("Class") != "PatchOperationConditional" or m is None or m.get("Class") != "PatchOperationRemove":
            probs.append("not Conditional>Remove: %s" % op.get("Class"))
            continue
        xp = (m.findtext("xpath") or "").strip()
        if xp != (op.findtext("xpath") or "").strip():
            probs.append("xpaths differ: %s" % xp)
        g = re.fullmatch(r"Defs/\*/xenotypeSet/xenotypeChances/(\w+)", xp)
        if g:
            covered.add(g.group(1))
        else:
            probs.append("unrecognised xpath: %s" % xp)
    return probs + ["no Remove for %s" % x for x in ALL if x not in covered]


def ship_findings(text):
    keys = set(re.findall(r"<li>([^<]+)</li>", text))
    out = ["missing XenotypeDef/%s" % x for x in CUT_DEF if "XenotypeDef/%s" % x not in keys]
    out += ["kept def cut: XenotypeDef/%s" % x for x in KEPT if "XenotypeDef/%s" % x in keys]
    out += ["bare key %s" % x for x in ALL if x in keys]
    for x in ALL:
        for k in ("GeneDef/Outland_XenotypeAscension_%s", "AbilityDef/Outland_XenotypeImplanter_%s",
                  "GeneDef/Outland_XenotypeImplanter_%s", "GeneDef/%s_Metamorphosis", "GeneDef/%s_Retromorphosis"):
            if k % x not in keys:
                out.append("missing companion " + k % x)
    out += ["missing ScenarioDef/%s" % s for s in SCENARIOS if "ScenarioDef/%s" % s not in keys]
    return out


def dump_refs(rows_by_type):
    cut, out = set(ALL), []
    for dt, rows in rows_by_type.items():
        for r in rows:
            for k, v in (r.get("fields") or {}).items():
                if isinstance(v, dict):
                    for c in v.get("xenotypeChances") or []:
                        if isinstance(c, dict) and c.get("xenotype") in cut:
                            out.append((dt, r["defName"], k, c["xenotype"]))
    return out


# a cut def may not be named anywhere structural; a KEPT def may still be relabelled by xpath (its text patch
# applies to a def that still loads), but never placed in a race/xenotype/spawn-set position
_REF = re.compile(r'(<race>|<xenotype>|<forcedXenotype>|<xenotypeDef>|xenotypeChances/)(%s)\b|(XenotypeDef\[defName=")(%s)\b'
                  % ("|".join(ALL), "|".join(CUT_DEF)))


def ref_findings(files_text):
    out = []
    for path, text in files_text:
        if path == PATCH_REL:
            continue
        for m in _REF.finditer(text):
            out.append("%s:%d %s" % (path, text.count("\n", 0, m.start()) + 1, m.group(0)))
    return out


def src_files():
    names = subprocess.run(["git", "-C", str(ROOT), "ls-files", "src"], capture_output=True, text=True).stdout.split()
    for n in names:
        if n.endswith((".xml", ".cs")):
            try:
                yield n, (ROOT / n).read_text(encoding="utf-8", errors="replace")
            except OSError:
                pass


def main():
    ptext, ship = PATCH.read_text(), SHIP.read_text()
    files = list(src_files())
    check("sanity: SHIP parses to >1000 keys", len(re.findall(r"<li>", ship)) > 1000)
    check("sanity: >1000 src files scanned", len(files) > 1000, len(files))
    check("sanity: the reference scan sees the cut file's own refs",
          len(ref_findings([("x.xml", ptext)])) >= len(ALL))
    f = patch_findings(ptext)
    check("spawn-set patch removes all 31 from every xenotypeSet", not f, f[:5])
    f = ship_findings(ship)
    check("SHIP: typed cuts for the 26, the 5 kept, companions and scenarios cut", not f, f[:5])
    f = ref_findings(files)
    check("no src file names one of the 31 as race/xenotype", not f, f[:5])
    try:
        import game_paths as GP
        rows = {dt: json.load(open(os.path.join(GP.DEF_DUMP, "defs", dt + ".json")))["defs"]
                for dt in ("FactionDef", "PawnKindDef")}
    except Exception as e:
        print("UNMEASURED: no readable def dump: %s" % e)
        return 2
    refs = dump_refs(rows)
    n_sets = sum(1 for rs in rows.values() for r in rs
                 if ((r.get("fields") or {}).get("xenotypeSet") or {}).get("xenotypeChances"))
    if n_sets < 100:
        print("UNMEASURED: dump shows only %d xenotypeSet defs (cannot see xenotypeSets)" % n_sets)
        return 2
    pre = any(n == "PirateWaster" and x == "DV_Buzzer" for _, n, _, x in refs)
    print("dump is %s the patch; %d references to the 31 on %d xenotypeSet defs" % ("BEFORE" if pre else "AFTER",
                                                                                     len(refs), n_sets))
    off = ["%s %s %s.%s" % r for r in refs if r[2] != "xenotypeSet"]
    check("every dump reference sits where the patch reaches (top-level xenotypeSet)", not off, off[:5])
    if not pre:
        check("post-patch dump: no reference survived (live)", not refs, refs[:5])
    # mutants
    check("mutant: a dropped Remove reds", patch_findings(re.sub(r"xenotypeChances/DV_Buzzer<", "xenotypeChances/DV_Buz<",
                                                                 ptext)) != [])
    check("mutant: Remove swapped for Add reds", patch_findings(
        ptext.replace('<match Class="PatchOperationRemove">', '<match Class="PatchOperationAdd">', 1)) != [])
    check("mutant: a dropped typed key reds", ship_findings(ship.replace("<li>XenotypeDef/KAR_Orc</li>", "")) != [])
    check("mutant: cutting a kept def reds", ship_findings(ship + "<li>XenotypeDef/VRE_Fungoid</li>") != [])
    check("mutant: a bare DV_Buzzer key reds", ship_findings(ship + "<li>DV_Buzzer</li>") != [])
    check("mutant: a CharacterDef race of KAR_Orc reds", ref_findings([("a.xml", "<race>KAR_Orc</race>")]) != [])
    check("mutant: a restored KAR_Orc relabel reds", ref_findings([("a.xml", 'Defs/XenotypeDef[defName="KAR_Orc"]')]) != [])
    if FAILS:
        print("\n%d non-SW xenotype cut selftest(s) FAILED" % len(FAILS))
        return 1
    print("\nall non-SW xenotype cut selftests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
