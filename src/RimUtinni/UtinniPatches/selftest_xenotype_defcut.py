#!/usr/bin/env python3
"""VANILLA_XENOTYPE_DEFCUT_1 (slice 2 of the owner's 2026-10-03 "cut the twelve entirely"): the eleven
non-Sanguophage xenotypes are cut by TYPED Cherry Picker keys, have no PawnFlavor re-flavour block left, and no
src file names one as a race/xenotype outside the slice-1 spawn-set cut file. Sanguophage is kept on purpose
(XenotypeDefOf binding; "unreachable, def kept" goes to the owner). Offline, no game.

Reds if: a typed `XenotypeDef/<X>` key is missing from the SHIP profile; a bare `<X>` key (cut_name style)
appears instead (`Neanderthal` is also a Beasts-of-the-Rim animal); a PawnFlavor block for a cut def remains;
any src .xml/.cs names one in a race/xenotype position.
"""
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
CUT = ("Dirtmole", "Genie", "Highmate", "Hussar", "Impid", "Neanderthal", "Pigskin", "Starjack",
       "VRESaurids_Saurid", "Waster", "Yttakin")
SHIP = os.path.join(ROOT, "infrastructure", "state", "cherrypicker", "CherryPicker.SHIP.xml")
FLAVOR = os.path.join(ROOT, "src", "RimUtinni", "PawnFlavor", "Patches", "PawnFlavorPhase2_Xenotype.xml")
SPAWNSET_CUT = "src/RimUtinni/UtinniPatches/Patches/XenotypeCut_SpawnSets.xml"
FAILS = []


def check(name, ok, detail=""):
    print("%s  %s %s" % ("ok  " if ok else "FAIL", name, "" if ok else detail))
    if not ok:
        FAILS.append(name)


def cp_findings(text, cut=CUT):
    keys = set(re.findall(r"<li>([^<]+)</li>", text))
    out = ["missing typed key XenotypeDef/%s" % x for x in cut if "XenotypeDef/%s" % x not in keys]
    out += ["bare (type-agnostic) key %s" % x for x in cut if x in keys]
    return out


def flavor_findings(text, cut=CUT):
    named = set(re.findall(r'XenotypeDef\[defName="([^"]+)"\]', text))
    return sorted(named & set(cut))


_REF = re.compile(r'(<race>|<xenotype>|<forcedXenotype>|<xenotypeDef>|XenotypeDef\[defName="|xenotypeChances/)(%s)\b'
                  % "|".join(CUT))


def ref_findings(files_text):
    out = []
    for path, text in files_text:
        if path == SPAWNSET_CUT:
            continue
        for m in _REF.finditer(text):
            out.append("%s:%d %s" % (path, text.count("\n", 0, m.start()) + 1, m.group(0)))
    return out


def src_files():
    names = subprocess.run(["git", "-C", ROOT, "ls-files", "src"], capture_output=True, text=True).stdout.split()
    for n in names:
        if n.endswith((".xml", ".cs")):
            try:
                yield n, open(os.path.join(ROOT, n), encoding="utf-8", errors="replace").read()
            except OSError:
                pass


def main():
    ship = open(SHIP, encoding="utf-8").read()
    flavor = open(FLAVOR, encoding="utf-8").read()
    files = list(src_files())
    # sanity probes: the instruments can see what they claim to look for
    check("sanity: SHIP parses to >1000 keys", len(re.findall(r"<li>", ship)) > 1000)
    check("sanity: PawnFlavor still re-flavours Baseliner (the parser can see a block)", "Baseliner" in set(
        re.findall(r'XenotypeDef\[defName="([^"]+)"\]', flavor)))
    check("sanity: the reference scan sees the slice-1 cut file's own %d xenotypeChances refs" % len(CUT),
          len(ref_findings([("x.xml", open(os.path.join(ROOT, SPAWNSET_CUT), encoding="utf-8").read())])) >= len(CUT))
    check("sanity: >1000 src files scanned", len(files) > 1000, len(files))
    f = cp_findings(ship)
    check("SHIP cuts all eleven by typed XenotypeDef key", not f, f)
    check("Sanguophage is NOT cut (DefOf binding; owner decision pending)", "XenotypeDef/Sanguophage" not in ship)
    f = flavor_findings(flavor)
    check("no PawnFlavor block for a cut xenotype", not f, f)
    f = ref_findings(files)
    check("no src file names a cut xenotype as race/xenotype", not f, f[:5])
    # mutants
    check("mutant: a dropped typed key reds", cp_findings(ship.replace("XenotypeDef/Hussar", "XenotypeDef/Hus_sar")) != [])
    check("mutant: a bare Neanderthal key reds", any("bare" in x for x in cp_findings(ship + "<li>Neanderthal</li>")))
    check("mutant: a restored PawnFlavor block reds", flavor_findings(flavor + 'Defs/XenotypeDef[defName="Impid"]') == ["Impid"])
    check("mutant: a CharacterDef race of Yttakin reds", ref_findings([("a.xml", "<race>Yttakin</race>")]) != [])
    if FAILS:
        print("\n%d xenotype defcut selftest(s) FAILED" % len(FAILS))
        return 1
    print("\nall xenotype defcut selftests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
