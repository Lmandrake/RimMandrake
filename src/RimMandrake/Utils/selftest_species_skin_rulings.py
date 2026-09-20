#!/usr/bin/env python3
"""Assert that every owner ruling on a species' skin colour is still SHIPPED.

Why this test exists
====================
Owner, 2026-09-20, verbatim: *"I definitely have said this before. Please make it
stick this time, record it."*

He had ruled Ugnaught's skin on 2026-09-17 and the ruling WAS applied to the def.
It still failed to stick, because the only durable record of it was a git commit
message -- and nothing reads a commit message. Three days later the species'
canon_references entry still said "(empty -- owner has not reviewed this race
yet)", the entry went on arguing the ruled colour was wrong, and an agent
"corrected" that entry without noticing a ruling had already settled it.

A ruling recorded only as prose is a ruling waiting to be reversed by the next
correctness sweep. This test is the thing that reverses the sweep instead.

What it asserts
===============
For each entry in infrastructure/state/species_skin_rulings.json:
  - the named XenotypeDef still exists in the shipping def file;
  - it carries EVERY gene in `required_genes`;
  - it carries NONE of the genes in `forbidden_genes`.

🔑 A ruling OUTRANKS canon, the canon_references library, an infobox and any
measurement. He is ruling on what the species looks like in OUR game. So a
failure here is never "the ruling is out of date" -- it is someone having
quietly undone him. Fix the def, not this test, unless he says otherwise.

Run: bare `python3 selftest_species_skin_rulings.py`, stdlib only, no args.
"""

import json
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
RULINGS = os.path.join(REPO_ROOT, "infrastructure", "state",
                       "species_skin_rulings.json")
XENOTYPES = os.path.join(
    REPO_ROOT, "src", "RimStarWars", "StarWarsRaces", "Defs", "XenotypeDefs",
    "RimMandrakeXenotypes.xml")


def genes_of(text, xeno_defname):
    """Every <li> gene name inside the named XenotypeDef's block, or None if
    that def is not present at all.

    Comments are stripped first: a gene named only in an explanatory comment
    must not satisfy a ruling, and a forbidden gene mentioned in a comment
    explaining why it was removed must not fail one.
    """
    start = text.find("<defName>%s</defName>" % xeno_defname)
    if start == -1:
        return None
    end = text.find("</XenotypeDef>", start)
    block = text[start:end if end != -1 else len(text)]
    block = re.sub(r"<!--.*?-->", "", block, flags=re.DOTALL)
    return set(re.findall(r"<li>\s*([A-Za-z0-9_]+)\s*</li>", block))


def main():
    for path in (RULINGS, XENOTYPES):
        if not os.path.isfile(path):
            print("UNMEASURED, not a pass or a fail")
            print("reason: %s is not on this machine" % path)
            return 0

    with open(RULINGS, encoding="utf-8") as fh:
        data = json.load(fh)
    with open(XENOTYPES, encoding="utf-8") as fh:
        text = fh.read()

    rulings = data.get("rulings", [])
    if not rulings:
        # An empty roster would pass vacuously and silently stop protecting
        # anything -- which is the exact failure mode this file exists to stop.
        print("FAIL: species_skin_rulings.json holds no rulings at all.")
        return 1

    failures = []
    for r in rulings:
        species = r.get("species", "?")
        xeno = r.get("xenotype_defName")
        genes = genes_of(text, xeno)
        if genes is None:
            failures.append("%s: XenotypeDef %s is not in the shipping def file"
                            % (species, xeno))
            continue
        for g in r.get("required_genes", []):
            if g not in genes:
                failures.append(
                    "%s: RULED gene %s is MISSING. He said: %r (%s)"
                    % (species, g, r.get("owner_said", ""), r.get("ruled", "")))
        for g in r.get("forbidden_genes", []):
            if g in genes:
                failures.append(
                    "%s: FORBIDDEN gene %s is present. He said: %r (%s)"
                    % (species, g, r.get("owner_said", ""), r.get("ruled", "")))

    print("owner skin rulings checked: %d" % len(rulings))
    for r in rulings:
        print("  %-12s %s" % (r.get("species", "?"),
                              ", ".join(r.get("required_genes", [])) or "(none)"))

    pending = data.get("needs_ruling", [])
    if pending:
        print("awaiting his ruling (not a failure): %s"
              % ", ".join(p.get("species", "?") for p in pending))

    if failures:
        print("")
        for f in failures:
            print("FAIL: %s" % f)
        print("")
        print("🔑 A ruling outranks canon. Fix the def, not this test, unless he "
              "has said otherwise.")
        return 1

    print("PASS: every owner skin ruling is still shipped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
