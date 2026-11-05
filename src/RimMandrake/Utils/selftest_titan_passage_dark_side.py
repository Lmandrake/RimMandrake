"""selftest_titan_passage_dark_side.py -- offline proof of the dark-side titan passage calls (NIGHTSIDE_TITAN_JUDGE_GIANTS_IN_THE_DARK).

    python3 src/RimMandrake/Utils/selftest_titan_passage_dark_side.py      -> "N/N PASS", exit 0

Owner, 2026-10-21: dark-side biomes host a titan passage "Only if giants can exist there." Each of the four biomes the
item names has a recorded call in design/RimMandrake/titan_passage_dark_side_calls_2026-11-05.md. This pins, from the
files alone:
  * every biome has a row in the call table, either "no passage" or "a giant can live there";
  * every no-passage biome gets RM_TitanPassageExtension none=true from src/RimMandrake/HugeThings/Patches/
    RM_TitanPassage_DarkSide.xml. The operation must be guarded by a Conditional on that very biome, use the extension's
    real class name (read from its .cs file), and name a defName that a BiomeDef in src/ really has;
  * no yes-giant biome is opted out, and each one names a roster item that exists as a live item in
    infrastructure/state/items/;
  * the patch is inside Huge Things, the mod that defines the extension class, so it never loads without the class.
A sanity probe proves the parser can see: a known BiomeDef (RM_SleepingIce) resolves from src/, and a deliberately
wrong defName does not.
"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
DOC = os.path.join(ROOT, "design", "RimMandrake", "titan_passage_dark_side_calls_2026-11-05.md")
PATCH = os.path.join(ROOT, "src", "RimMandrake", "HugeThings", "Patches", "RM_TitanPassage_DarkSide.xml")
EXT_CS = os.path.join(ROOT, "src", "RimMandrake", "HugeThings", "Source", "Titanic", "Events", "RM_TitanPassageExtension.cs")
ITEMS = os.path.join(ROOT, "infrastructure", "state", "items")

NO_PASSAGE = ["RM_SleepingIce", "RUT_SleepingIce"]
GIANT_HOMES = {"RUT_Umbra": "UMBRA_TITAN_POPULATE_BURNS_TO_WALK",
               "RM_TheChill": "CHILL_TITAN_POPULATE_WAX_GIANT_TOO_SMALL"}

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))


def biome_defnames():
    names = set()
    for f in glob.glob(os.path.join(ROOT, "src", "**", "Defs", "**", "*.xml"), recursive=True):
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError:
            continue
        for d in root.iter("BiomeDef"):
            n = d.findtext("defName")
            if n:
                names.add(n.strip())
    return names


def ext_class():
    src = open(EXT_CS, encoding="utf-8").read()
    ns = re.search(r"namespace\s+([\w.]+)", src).group(1)
    cls = re.search(r"public\s+class\s+(\w+)\s*:\s*DefModExtension", src).group(1)
    return ns + "." + cls


def patch_optouts():
    """{biome defName: (guard xpath, inner xpath, li Class, none text)} for each top-level Conditional."""
    out = {}
    for op in ET.parse(PATCH).getroot().findall("Operation"):
        if op.get("Class") != "PatchOperationConditional":
            continue
        guard = (op.findtext("xpath") or "").strip()
        m = op.find("match")
        if m is None or m.get("Class") != "PatchOperationAddModExtension":
            continue
        inner = (m.findtext("xpath") or "").strip()
        for li in m.findall("value/li"):
            g = re.fullmatch(r'Defs/BiomeDef\[defName="(\w+)"\]', guard)
            if g:
                out[g.group(1)] = (guard, inner, li.get("Class"), (li.findtext("none") or "").strip())
    return out


def doc_rows():
    rows = {}
    for line in open(DOC, encoding="utf-8"):
        m = re.match(r"\|\s*`(\w+)`\s*\|\s*\*\*(.+?)\*\*", line)
        if m:
            rows.setdefault(m.group(1), m.group(2))
    return rows


def main():
    biomes = biome_defnames()
    check("probe: RM_SleepingIce is a BiomeDef in src/", "RM_SleepingIce" in biomes)
    check("probe: a wrong defName is not", "RM_NightsideIce_NoSuchBiome" not in biomes)

    rows = doc_rows()
    for b in NO_PASSAGE:
        check(f"doc: {b} call is no passage", "no passage" in rows.get(b, ""), rows.get(b, "MISSING"))
    for b in GIANT_HOMES:
        check(f"doc: {b} call is a giant can live there", "a giant can live there" in rows.get(b, ""), rows.get(b, "MISSING"))

    cls = ext_class()
    opts = patch_optouts()
    for b in NO_PASSAGE:
        o = opts.get(b)
        check(f"patch: {b} opted out", o is not None, "no guarded op")
        if o is None:
            continue
        guard, inner, li_cls, none = o
        check(f"patch: {b} inner xpath equals its guard", inner == guard, inner)
        check(f"patch: {b} uses the real class {cls}", li_cls == cls, li_cls)
        check(f"patch: {b} none=true", none == "true", none)
        check(f"patch: {b} defName is a real BiomeDef", b in biomes)
    for b, item in GIANT_HOMES.items():
        xpaths = [x.text or "" for x in ET.parse(PATCH).getroot().iter("xpath")]
        check(f"patch: {b} is not opted out", b not in opts and not any(f'"{b}"' in x for x in xpaths))
        check(f"item: {item} is live", os.path.isfile(os.path.join(ITEMS, item + ".md")))
        check(f"doc: {b} names {item}", item in open(DOC, encoding="utf-8").read())
    check("patch: lives in Huge Things beside the extension class",
          os.path.commonpath([PATCH, EXT_CS]) == os.path.join(ROOT, "src", "RimMandrake", "HugeThings"))

    bad = [r for r in results if not r[1]]
    for name, ok, detail in results:
        if not ok:
            print(f"FAIL {name} {detail}")
    print(f"{len(results) - len(bad)}/{len(results)} PASS")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
