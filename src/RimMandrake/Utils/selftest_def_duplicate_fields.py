#!/usr/bin/env python3
"""Selftest: no def in src/ repeats a field element (WILDGROUPSIZE_FIX_TWO_SPELLINGS_ONE_FIELD).

A def that writes a field twice is merged by the loader into ONE node, so `<wildGroupSize>2~5</wildGroupSize>`
plus `<wildGroupSize><min>4</min><max>8</max></wildGroupSize>` became `2~5<min>4</min><max>8</max>` and logged
"XML error: 2~5 doesn't correspond to any field in type IntRange" on every load (24 PawnKindDefs, 2026-11-04).
Offline, a few seconds. Checks:
 1 sanity probe: the scan parses at least 2000 top-level defs and sees RM_Chittik's PawnKindDef
 2 no top-level def under src/**/Defs or src/**/Patches (fixtures, backups, archives and retired trees skipped)
   has a direct child element name twice
 3 mutant probe: a fixture def with a doubled wildGroupSize is flagged; a clean one is not
 4 biome_group_sizes.field() reads the <min>/<max> spelling as "a~b" and refuses a def with two wildGroupSize
   elements or one that mixes both spellings

    python3 src/RimMandrake/Utils/selftest_def_duplicate_fields.py
"""
import collections
import os
import pathlib
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import biome_group_sizes as bgs  # noqa: E402

SRC = bgs.ROOT / "src"
SKIP = ("selftest_fixtures", "Backup", "backup", "_archive", "retired")


def repeats(root):
    """(defName, tag, count) for every top-level def under a <Defs> root that repeats a direct child."""
    out = []
    if root.tag != "Defs":
        return out
    for d in root:
        if not isinstance(d.tag, str):
            continue
        tags = collections.Counter(ch.tag for ch in d if isinstance(ch.tag, str))
        for tag, n in tags.items():
            if n > 1:
                out.append((d.findtext("defName") or d.get("Name") or d.tag, tag, n))
    return out


def scan():
    defs, seen, bad = 0, set(), []
    for p in sorted(SRC.rglob("*.xml")):
        rel = p.relative_to(SRC).as_posix()
        if any(s in rel for s in SKIP) or not ("/Defs/" in f"/{rel}" or "/Patches/" in f"/{rel}"):
            continue
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError:
            continue   # malformed XML is another selftest's business
        if root.tag == "Defs":
            for d in root:
                if isinstance(d.tag, str):
                    defs += 1
                    seen.add((d.tag, d.findtext("defName")))
        bad += [(rel, *r) for r in repeats(root)]
    return defs, seen, bad


def main():
    fails = []
    defs, seen, bad = scan()
    if defs < 2000 or ("PawnKindDef", "RM_Chittik") not in seen:
        fails.append(f"sanity: scanned {defs} defs, RM_Chittik PawnKindDef seen={('PawnKindDef', 'RM_Chittik') in seen}")
    for rel, dn, tag, n in bad:
        fails.append(f"{rel}: {dn} has {n} <{tag}> elements")

    doubled = ET.fromstring("<Defs><PawnKindDef><defName>X</defName><wildGroupSize>2~5</wildGroupSize>"
                            "<wildGroupSize><min>4</min><max>8</max></wildGroupSize></PawnKindDef></Defs>")
    clean = ET.fromstring("<Defs><PawnKindDef><defName>X</defName><wildGroupSize>2~5</wildGroupSize>"
                          "</PawnKindDef></Defs>")
    if repeats(doubled) != [("X", "wildGroupSize", 2)] or repeats(clean):
        fails.append(f"mutant: doubled={repeats(doubled)} clean={repeats(clean)}")

    minmax = ET.fromstring("<PawnKindDef><defName>Y</defName><wildGroupSize><min>4</min><max>8</max>"
                           "</wildGroupSize></PawnKindDef>")
    if bgs.field(minmax, "wildGroupSize", {}) != "4~8":
        fails.append(f"field(): min/max read as {bgs.field(minmax, 'wildGroupSize', {})!r}, want '4~8'")
    mixed = ET.fromstring("<PawnKindDef><defName>Z</defName><wildGroupSize>2~5<min>4</min><max>8</max>"
                          "</wildGroupSize></PawnKindDef>")
    for name, el in (("doubled", doubled[0]), ("mixed", mixed)):
        try:
            got = bgs.field(el, "wildGroupSize", {})
            fails.append(f"field(): {name} spelling read as {got!r} instead of refused")
        except ValueError:
            pass

    for f in fails:
        print("FAIL", f)
    print(f"{defs} defs scanned, {len(bad)} repeated fields, {len(fails)} failures")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
