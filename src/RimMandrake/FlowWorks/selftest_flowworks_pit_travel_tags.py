#!/usr/bin/env python3
"""selftest_flowworks_pit_travel_tags.py — the pit-travel lore tags (PIT_TRAVEL_TAGS_VET_LORE_FIRST_GUESS).

Holds Patches/Canals/FlowWorks_PitTravel.xml to the judged list in
design/RimMandrake/pit_travel_jumpers_floaters_2026-10-20.md and reds when:
  - the patch's floats/jumps sets differ from the doc's two tables,
  - a tagged defName is not a race ThingDef under src/ (a typo matches nothing and logs nothing),
  - a tagged race is a flyer (MaxFlightTime: free already, the tag is dead),
  - a race whose CURRENT description matches the lore word list is neither tagged nor named in the
    doc's left-out section (a creature added after the vetting was never judged),
  - the doc lost its judge-vetting section.
Mutants are applied to in-memory copies, never the files.
"""
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

FW = Path(__file__).resolve().parent
REPO = FW.parents[2]
PATCH = FW / "Patches" / "Canals" / "FlowWorks_PitTravel.xml"
DOC = REPO / "design" / "RimMandrake" / "pit_travel_jumpers_floaters_2026-10-20.md"
ROOTS = [REPO / "src" / "RimMandrake", REPO / "src" / "RimStarWars", REPO / "src" / "RimUtinni"]
LORE = re.compile(r"\b(leap|bound|hop|hover|drift|float|levitat|jump|bounc|balloon|aloft|spring)\w*", re.I)
NAME = re.compile(r"`((?:RM|RSW|RUT)_[A-Za-z0-9]+)`")


def races():
    """defName -> (description, is_flyer) for every race ThingDef under the three roots."""
    out = {}
    for root in ROOTS:
        for p in sorted(root.glob("**/Defs/**/*.xml")):
            try:
                tree = ET.parse(p)
            except ET.ParseError:
                continue
            for td in tree.getroot().iter("ThingDef"):
                n = td.findtext("defName")
                if not n or td.find("race") is None or n in out:
                    continue
                desc = " ".join((td.findtext("description") or "").split())
                out[n] = (desc, any(e.tag == "MaxFlightTime" for e in td.iter()))
    return out


def patch_sets(text):
    sets = {"floats": set(), "jumps": set()}
    root = ET.fromstring(text)
    for op in root.iter("Operation"):
        match = op.find("match")
        if match is None:
            continue
        val = match.find("value")
        kind = [k for k in sets if val is not None and val.find(f"li/{k}") is not None]
        xp = match.findtext("xpath") or ""
        if len(kind) == 1:
            sets[kind[0]] |= set(re.findall(r'defName="([^"]+)"', xp))
            if set(re.findall(r'defName="([^"]+)"', op.findtext("xpath") or "")) != set(re.findall(r'defName="([^"]+)"', xp)):
                sets.setdefault("_mismatch", set()).add(kind[0])
    return sets


def doc_parts(doc):
    def section(head):
        m = re.search(rf"^## {head}.*?$(.*?)(?=^## |\Z)", doc, re.S | re.M)
        return m.group(1) if m else ""
    table = lambda body: {m.group(1) for m in re.finditer(r"^\| `([A-Za-z0-9_]+)` \|", body, re.M)}
    return (table(section("Floaters")), table(section("Jumpers")),
            set(NAME.findall(section("Matched a word but left out"))), section("Judge vetting"))


def findings(patch_text, doc, rc):
    out = []
    sets = patch_sets(patch_text)
    floats, jumps, left_out, judge = doc_parts(doc)
    for k in sets.pop("_mismatch", ()):
        out.append(f"{k}: Conditional xpath and match xpath name different races")
    if not floats or not jumps:
        out.append("doc tables unreadable (floaters or jumpers empty)")
    if sets["floats"] != floats:
        out.append(f"floats: patch {sorted(sets['floats'] ^ floats)} differ from the doc")
    if sets["jumps"] != jumps:
        out.append(f"jumps: patch {sorted(sets['jumps'] ^ jumps)} differ from the doc")
    tagged = sets["floats"] | sets["jumps"]
    for n in sorted(tagged):
        if n not in rc:
            out.append(f"{n}: tagged but no race ThingDef under src/")
        elif rc[n][1]:
            out.append(f"{n}: tagged but a flyer (MaxFlightTime)")
    for n, (desc, fly) in sorted(rc.items()):
        if not fly and LORE.search(desc) and n not in tagged and n not in left_out:
            out.append(f"{n}: matches the lore words but was never judged (tag it or list it as left out)")
    if "Judge vetting" not in doc or not re.search(r"\d{4}-\d{2}-\d{2}", judge) or "did not make" not in judge:
        out.append("doc lost its judge-vetting section")
    return out


def main():
    patch_text, doc, rc = PATCH.read_text(), DOC.read_text(), races()
    fails = []
    # sanity probe: the instrument must see races, lore matches and both tables before a clean pass means anything
    lore_hits = sum(1 for d, f in rc.values() if LORE.search(d))
    floats, jumps, left_out, _ = doc_parts(doc)
    if len(rc) < 200 or lore_hits < 20 or len(floats) < 5 or len(jumps) < 5 or len(left_out) < 20:
        fails.append(f"instrument blind: races={len(rc)} lore_hits={lore_hits} floats={len(floats)} "
                     f"jumps={len(jumps)} left_out={len(left_out)}")
    base = findings(patch_text, doc, rc)
    fails += [f"live: {f}" for f in base]
    mutants = {
        "drop a jumper from the patch": (patch_text.replace(' or defName="RSW_Clodhopper"', "", 1), doc, rc),
        "typo a floater": (patch_text.replace('"RM_Garsulix"', '"RM_Garsulixx"'), doc, rc),
        "a new unjudged hopper": (patch_text, doc, {**rc, "RM_ZzTestHopper": ("It hops about.", False)}),
        "a tagged race gains flight": (patch_text, doc, {**rc, "RM_Bulloo": (rc.get("RM_Bulloo", ("", False))[0], True)}),
        "judge section deleted": (patch_text, doc.split("## Judge vetting")[0], rc),
    }
    for label, args in mutants.items():
        if not findings(*args):
            fails.append(f"mutant not caught: {label}")
    for f in fails:
        print("FAIL", f)
    print(f"selftest_flowworks_pit_travel_tags: races={len(rc)} lore_hits={lore_hits} floats={len(floats)} "
          f"jumps={len(jumps)} left_out={len(left_out)} mutants={len(mutants)} -> {'FAIL' if fails else 'PASS'}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
