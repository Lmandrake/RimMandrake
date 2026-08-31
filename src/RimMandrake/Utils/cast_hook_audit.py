#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cast_hook_audit.py — does an authored character's HOOK agree with their TRAITS?

    python3 src/RimMandrake/Utils/cast_hook_audit.py                 # the flagged ones
    python3 src/RimMandrake/Utils/cast_hook_audit.py --all           # every character
    python3 src/RimMandrake/Utils/cast_hook_audit.py --who "Aureth"  # one person
    python3 src/RimMandrake/Utils/cast_hook_audit.py --json          # machine-readable

⭐ WHAT THIS IS FOR. `CharacterDef`'s own comment sets the standard: *"The hook and
the traits must agree — a hook the mechanics do not back is a lie the player will
catch."* Until now the only place anyone could see the two side by side was the
in-game debug action `Inhabited > Spawn authored character`, which needs a loaded
game, a live bridge and a spawned pawn to read one person.

🔑 IT NEEDS NONE OF THAT. The hook and the traits are BOTH in the generated XML, so
the comparison is a disk question, not a runtime one — 294 characters in under a
second, offline, with the game up or down. Written 2026-08-21 for
`INHABITED_DEBUG_ACTION_ABSENT_1`, whose cost was that
`CAST_ROSTER_269_LOAD_1`'s hook-versus-traits half had no instrument at all.

⛔ IT DOES NOT GRADE, AND MUST NOT START TO. Every line it prints is a QUESTION for
the author. Prose is allowed to describe a person the trait system cannot model —
a hook can be metaphor, a habit, or a thing that happens once. A flag here means
*"the words promise a mechanic; check that you meant to leave it unbacked"*, never
*"this is wrong"*. Anything that turned this into a pass/fail gate would start
deleting characterisation to satisfy a regex.

⚠️ THE XML IS GENERATED, THE PROSE IS THE SOURCE. `cast_to_xml.py` writes
`src/RimMandrake/Inhabited/Defs/CastRosters/*.xml` from `design/Jawa/bridge/INHABITED_CAST_*.md`.
Fix a disagreement in the PROSE and re-run that tool; an edit here or in the XML is
overwritten on the next generation.
"""
import argparse
import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
ROSTERS = os.path.join(REPO, "src", "Jawa", "Inhabited", "Defs", "CastRosters", "*.xml")

# ---------------------------------------------------------------------------
# THE CUE TABLE — hook language that PROMISES a mechanic.
# ---------------------------------------------------------------------------
# 🔑 Every trait named here is one the cast ACTUALLY uses; the table was built
# against the 25 distinct TraitDefs across the 294 characters, not against
# RimWorld's full trait list. A cue for a trait nobody carries can only produce
# noise, so there are none.
#
# ⚠️ Cues are deliberately NARROW. A cue that fires on "drink" would flag every
# tavern scene in the cast; one that fires on "into a stupor" flags the person the
# item was actually written about. When in doubt the cue was left out — a missed
# flag costs nothing, and a table nobody trusts costs everything.
#
# Each entry: (regex, [traits that would back it], what the words promise)
CUES = [
    (r"\b(?:drinks?|drinking|drank)\b[^.]{0,40}\b(?:stupor|blackout|senseless|oblivion|under)\b",
     ["DrugDesire", "Gourmand"], "habitual heavy drinking"),
    (r"\b(?:addict(?:ed|ion)?|junkie|craving|chem[- ]?fiend|withdrawal|dependent on)\b",
     ["DrugDesire"], "chemical dependency"),
    (r"\b(?:smoke(?:s|d)?|chews?|dose(?:s|d)?)\b[^.]{0,30}\b(?:constantly|all day|every hour|without stopping)\b",
     ["DrugDesire"], "constant use"),

    (r"\b(?:eats?|eating|ate)\b[^.]{0,40}\b(?:anything|constantly|everything|never stops|whatever)\b",
     ["Gourmand"], "compulsive eating"),
    (r"\b(?:human|people|long[- ]?pig|manflesh)\b[^.]{0,20}\bmeat\b|\bcannibal",
     ["Cannibal", "Psychopath"], "eating people"),

    # ⚠️ The window forbids `.` AND an em dash: "remembers your children — and every
    # trader…" is two clauses, and a cue that reads across the dash invented a flag.
    (r"\b(?:remembers?|recalls?|recites?)\b[^.—]{0,30}\b(?:every|verbatim|word for word|to the letter|exactly)\b",
     ["GreatMemory", "TooSmart"], "perfect recall"),
    (r"\bnever forgets?\b",
     ["GreatMemory"], "perfect recall"),

    (r"\b(?:picks? a fight|swings? first|throws? the first punch|would rather brawl|hates? guns?)\b",
     ["Brawler"], "melee by preference"),
    (r"\b(?:never misses|dead ?eye|crack shot|best shot|one shot, one)\b",
     ["ShootingAccuracy"], "marksmanship"),

    (r"\b(?:feels? nothing|no remorse|without pity|cannot be moved by|unmoved by (?:death|suffering))\b",
     ["Psychopath"], "absence of empathy"),
    (r"\b(?:cruel(?:ty)?|enjoys? (?:hurting|the pain|watching them))\b",
     ["Psychopath", "Masochist"], "taking pleasure in harm"),

    # ⚠️ NOT the bare word "rude": "refusing would be rude" is a reason, not a manner.
    (r"\b(?:is rude\b|rude to\b|rudeness|insult(?:s|ing)\b|abrasive|caustic|withering|contempt(?:uous)?)\b",
     ["Abrasive"], "habitual rudeness"),
    # ⚠️ NOT the bare word "kind": "the kind of man who…" is a noun.
    (r"\b(?:kind to\b|kindness|gentle with\b|warm to everyone|never unkind)\b",
     ["Kind"], "habitual kindness"),

    (r"\b(?:owns? nothing|no possessions|sleeps? on the floor|refuses? comfort|wants? for nothing)\b",
     ["Ascetic"], "asceticism"),
    (r"\b(?:envies?|envious|jealous(?:y)?|resents? (?:her|his|their) betters)\b",
     ["Jealous"], "envy"),

    (r"\b(?:frail|sickly|breaks? easily|bruises? at a touch|thin as|brittle)\b",
     ["Delicate"], "fragility"),
    (r"\b(?:slow to learn|never picked it up|could not be taught|dim|thick)\b",
     ["SlowLearner", "TooSmart"], "learning speed"),
    (r"\b(?:learns? (?:anything|fast|quickly)|picks? it up in|reads? once and)\b",
     ["FastLearner", "TooSmart"], "learning speed"),

    (r"\b(?:machine|augment(?:ed|ation)?|prosthetic|bionic|steel and|replace(?:d|s) (?:her|his|their) own)\b[^.]{0,40}\b(?:better|prefers?|wants? more|proud)\b",
     ["Transhumanist"], "wanting to be more machine"),
    (r"\b(?:wheez(?:e|es|ing)|rasp(?:s|ing)?|breath(?:es|ing) (?:wrong|loud|through))\b",
     ["CreepyBreathing"], "audible breathing"),
    (r"\b(?:voice like|grating voice|voice that|nasal|screech(?:es|y)?)\b",
     ["AnnoyingVoice"], "an unpleasant voice"),
    (r"\b(?:beautiful|striking|handsome|lovely to look at)\b",
     ["Beauty"], "notable appearance"),
    # ⚠️ NOT the bare word "ugly": the cast uses it of work, weather and debts far
    # more often than of a face.
    (r"\b(?:hideous|disfigured|ugly as\b|hard to look at)\b",
     ["Beauty"], "notable appearance"),
]

COMPILED = [(re.compile(rx, re.I), traits, why) for rx, traits, why in CUES]


def load():
    """Every CharacterDef on disk, in a stable order."""
    out = []
    for path in sorted(glob.glob(ROSTERS)):
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError as e:
            print("⚠️  %s did not parse: %s" % (os.path.basename(path), e), file=sys.stderr)
            continue
        for d in root.findall("Inhabited.CharacterDef"):
            traits = []
            for li in d.findall("./traits/li"):
                name = li.findtext("def") or "?"
                degree = li.findtext("degreeName")
                traits.append(name + ("(%s)" % degree if degree else ""))
            out.append({
                "file": os.path.basename(path),
                "defName": d.findtext("defName") or "?",
                "label": d.findtext("label") or "?",
                "faction": d.findtext("faction") or "-",
                "place": d.findtext("place") or "-",
                "hook": (d.findtext("hook") or "").strip(),
                "traits": traits,
                "traitDefs": [t.split("(")[0] for t in traits],
            })
    return out


def flags_for(c):
    """Cues the hook fires that no trait backs. Deterministic order."""
    out = []
    for rx, wanted, why in COMPILED:
        m = rx.search(c["hook"])
        if not m:
            continue
        if any(w in c["traitDefs"] for w in wanted):
            continue
        out.append({"phrase": m.group(0).strip(), "promises": why, "backed_by": wanted})
    return out


def render(c, flags, verbose):
    lines = ["%-46s  %-11s  %s" % (c["label"], c["faction"], c["place"])]
    lines.append("    traits: " + (", ".join(c["traits"]) if c["traits"] else "(none)"))
    if verbose:
        hook = c["hook"] or "(no hook)"
        lines.append("    hook:   " + hook)
    for f in flags:
        lines.append("    ⚠️  \"%s\" — promises %s; no %s"
                     % (f["phrase"], f["promises"], " / ".join(f["backed_by"])))
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--all", action="store_true",
                    help="every character, not just the flagged ones")
    ap.add_argument("--who", default=None,
                    help="substring of a label or defName; implies --all for the match")
    ap.add_argument("--json", action="store_true", help="machine-readable")
    a = ap.parse_args(argv)

    cast = load()
    if not cast:
        print("no CharacterDefs found under %s" % ROSTERS, file=sys.stderr)
        return 2

    rows = []
    for c in cast:
        c = dict(c)
        c["flags"] = flags_for(c)
        rows.append(c)

    if a.who:
        needle = a.who.lower()
        rows = [c for c in rows
                if needle in c["label"].lower() or needle in c["defName"].lower()]
        if not rows:
            print("no character matching %r" % a.who, file=sys.stderr)
            return 1

    if a.json:
        json.dump({"characters": rows,
                   "count": len(rows),
                   "flagged": sum(1 for c in rows if c["flags"])},
                  sys.stdout, indent=1, ensure_ascii=False)
        print()
        return 0

    show_all = a.all or bool(a.who)
    shown = 0
    for c in rows:
        if not show_all and not c["flags"]:
            continue
        print(render(c, c["flags"], verbose=show_all or bool(c["flags"])))
        print()
        shown += 1

    flagged = sum(1 for c in rows if c["flags"])
    no_hook = sum(1 for c in rows if not c["hook"])
    no_traits = sum(1 for c in rows if not c["traits"])
    print("%d characters across %d roster files; %d shown"
          % (len(rows), len({c["file"] for c in rows}), shown))
    print("  %d carry a hook cue no trait backs  (a QUESTION, not a defect)" % flagged)
    print("  %d have no hook at all" % no_hook)
    print("  %d carry no traits at all" % no_traits)
    # ⛔ Always 0. This reports; it does not gate. See the module docstring.
    return 0


if __name__ == "__main__":
    sys.exit(main())
