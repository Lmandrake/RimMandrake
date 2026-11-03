#!/usr/bin/env python3
"""Offline check: the Fleshsop is a weapon system, not a sad zombie (FLESHSOP_REDESIGN_AS_WEAPON_SYSTEM).

Owner, 2026-10-24: "These are weapon systems, not sad zombies. Eliminate the 'it needs to be loved to live
another day.' That's ridiculous."

Static, no game. Goes red when:
  * RM_Fleshsop's ThingDef description, the cast doc's Fleshsop section, the BiomeDef roster comment or the
    art list's prompt/style_notes carry the pitiable framing again (wet rag, leans to stay standing, fed by
    hand, needs care/love, pitiable, asking to be kept, tired/sagging);
  * the def loses its weapon-system body: health scale < 1, manhunter-on-damage < 1, combatPower < 20, a
    melee tool under power 4, packs of one, or no sponge armour.
Each rule is mutation-checked against the pre-reframe text so a blind check cannot pass.

    python3 src/RimMandrake/Contagion/selftest_fleshsop_weapon_reframe.py
"""
import csv
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FAUNA = os.path.join(HERE, "Defs", "ThingDefs_Races", "RM_ContagionFauna.xml")
BIOME = os.path.join(HERE, "Defs", "BiomeDefs", "RM_Contagion.xml")
DOC = os.path.join(ROOT, "design", "Jawa", "worldbuilding", "biomes", "contagion_grotesque_cast_2026-09-27.md")
ARTLIST = os.path.join(ROOT, "infrastructure", "artpipe", "art_lists", "contagion_grotesque_cast.csv")

PITIABLE = re.compile(
    r"wet rag|lean(s|ing)? on things|stay standing|fed by hand|needs? (care|affection|to be loved)|"
    r"loved to live|(?<!never )pitiable|asking to be kept|tired face|needs the support",
    re.I)
# The owner's own quoted words (*"..."* in the doc) name the cut framing; they are stripped before checking.
OWNER_QUOTE = re.compile(r'\*"[^"]*"\*', re.S)

OLD_DESCRIPTION = ("A wet rag of a creature, barely holding a shape, that leans on things to stay standing. "
                   "What an Unfinished looks like when the goo forgets to take it back.")


def _read(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def _strip_xml_comments(s):
    return re.sub(r"<!--.*?-->", "", s, flags=re.S)


def pitiable_hits(text):
    text = OWNER_QUOTE.sub("", text)
    return sorted({m.group(0).lower() for m in PITIABLE.finditer(text)})


def fleshsop_defs(xml_text):
    root = ET.fromstring(xml_text)
    thing = kind = None
    for el in root:
        if el.findtext("defName") == "RM_Fleshsop":
            if el.tag == "ThingDef":
                thing = el
            elif el.tag == "PawnKindDef":
                kind = el
    return thing, kind


def body_failures(thing, kind):
    f = []
    if thing is None or kind is None:
        return ["RM_Fleshsop ThingDef or PawnKindDef missing"]

    def num(el, path, default=None):
        v = el.findtext(path)
        return float(v) if v is not None else default

    if num(thing, "race/baseHealthScale", 0) < 1.0:
        f.append("baseHealthScale < 1.0 (a screen must soak)")
    if num(thing, "race/manhunterOnDamageChance", 0) < 1.0:
        f.append("manhunterOnDamageChance < 1.0 (it answers every hit)")
    if num(kind, "combatPower", 0) < 20:
        f.append("combatPower < 20")
    if num(thing, "statBases/ArmorRating_Sharp", 0) <= 0:
        f.append("no ArmorRating_Sharp (sponge armour)")
    powers = [float(t.findtext("power")) for t in thing.findall("tools/li")]
    if not powers or min(powers) < 4:
        f.append(f"melee tool powers {powers}: a weak swipe is back")
    grp = kind.findtext("wildGroupSize") or ""
    m = re.match(r"\s*(\d+)\s*~\s*(\d+)", grp)
    if not m or int(m.group(2)) < 2:
        f.append(f"wildGroupSize {grp!r}: screens come in packs")
    return f


def doc_section(doc_text):
    i = doc_text.find("### Fleshsop (`RM_Fleshsop`)")
    if i < 0:
        return None
    j = doc_text.find("\n### ", i + 1)
    return doc_text[i:j if j > 0 else None]


def doc_rows(doc_text):
    return "\n".join(l for l in doc_text.splitlines() if "RM_Fleshsop" in l and l.startswith("|"))


def art_row_text(path):
    with open(path, encoding="utf-8", newline="") as fh:
        rows = [r for r in csv.DictReader(fh) if r.get("id") == "RM_Fleshsop"]
    if len(rows) != 1:
        return None
    return rows[0]["prompt"] + "\n" + rows[0]["style_notes"]


def main():
    fails = []
    fauna = _read(FAUNA)
    thing, kind = fleshsop_defs(fauna)
    desc = thing.findtext("description") if thing is not None else ""
    if pitiable_hits(desc):
        fails.append(f"def description pitiable: {pitiable_hits(desc)}")
    fails += [f"def: {x}" for x in body_failures(thing, kind)]

    biome_line = [l for l in _read(BIOME).splitlines() if "<RM_Fleshsop>" in l]
    if len(biome_line) != 1:
        fails.append(f"BiomeDef: expected 1 RM_Fleshsop roster line, found {len(biome_line)}")
    elif pitiable_hits(biome_line[0]) or "the-pitiable" in biome_line[0]:
        fails.append("BiomeDef roster comment pitiable")

    doc = _read(DOC)
    sec = doc_section(doc)
    if sec is None:
        fails.append("cast doc: Fleshsop section missing")
    elif pitiable_hits(sec) or pitiable_hits(doc_rows(doc)):
        fails.append(f"cast doc pitiable: {pitiable_hits(sec) + pitiable_hits(doc_rows(doc))}")

    art = art_row_text(ARTLIST)
    if art is None:
        fails.append("art list: expected exactly one RM_Fleshsop row")
    elif pitiable_hits(art):
        fails.append(f"art list prompt pitiable: {pitiable_hits(art)}")

    # mutation checks: the pre-reframe text and body must be caught
    mut = []
    if not pitiable_hits(OLD_DESCRIPTION):
        mut.append("old description not caught")
    if not pitiable_hits("a small pitiable creature ... asking to be kept anyway"):
        mut.append("old art prompt not caught")
    if not pitiable_hits("omnivore (fed by hand)") or not pitiable_hits("| the pitiable | **Fleshsop**"):
        mut.append("old doc text not caught")
    if pitiable_hits('*"These are weapon systems, not sad zombies. Eliminate the \'it needs to be loved to live\nanother day.\' That\'s ridiculous."*'):
        mut.append("owner's own quote wrongly flagged")
    if not pitiable_hits("a soaked sponge - pitiable, never comic"):
        mut.append("old style note 'pitiable, never comic' not caught")
    old = fauna
    for a, b in (("<baseHealthScale>1.2</baseHealthScale>", "<baseHealthScale>0.25</baseHealthScale>"),
                 ("<manhunterOnDamageChance>1.0</manhunterOnDamageChance>",
                  "<manhunterOnDamageChance>0.0</manhunterOnDamageChance>"),
                 ("<combatPower>30</combatPower>", "<combatPower>4</combatPower>"),
                 ("<wildGroupSize>2~4</wildGroupSize>", "<wildGroupSize>1~1</wildGroupSize>"),
                 ("<ArmorRating_Sharp>0.3</ArmorRating_Sharp>", "<ArmorRating_Sharp>0</ArmorRating_Sharp>"),
                 ("<power>5</power>", "<power>2</power>")):
        t_, k_ = fleshsop_defs(old)
        before = len(body_failures(t_, k_))
        i = old.index("<defName>RM_Fleshsop</defName>")
        j = old.index(a, i) if a in old[i:] else -1
        if j < 0:
            mut.append(f"mutation target {a} not found in RM_Fleshsop")
            continue
        m_ = old[:j] + b + old[j + len(a):]
        t2, k2 = fleshsop_defs(m_)
        if len(body_failures(t2, k2)) <= before:
            mut.append(f"mutation {b} not caught")
    # the live def's description reverted to the pre-reframe text must be caught through the same parse path
    t_, _ = fleshsop_defs(old)
    cur = t_.findtext("description") if t_ is not None else None
    if not cur:
        mut.append("RM_Fleshsop description not found for the revert mutation")
    else:
        t3, _ = fleshsop_defs(old.replace(cur, OLD_DESCRIPTION, 1))
        if not pitiable_hits(t3.findtext("description")):
            mut.append("description reverted to the pre-reframe text not caught")
    fails += [f"MUTATION: {x}" for x in mut]

    for x in fails:
        print("FAIL", x)
    print("RESULT", "FAIL" if fails else "PASS", f"({len(fails)} failures)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
