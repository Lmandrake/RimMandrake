#!/usr/bin/env python3
"""check_canon.py — fail when a design doc contradicts `infrastructure/state/canon.yml`.

WHY
===
A 2026-08-20 audit of the 119-document design tier found 21 numbers asserted at two
or more different values, in files that all read as current. Water was 25%, 22–28%,
8.6%, 8.1% and 6.9%. Factions were 14, 13, 12 and 11. Twenty different mod counts
existed and four carried a date. Nothing was wrong by its own lights; every document
was written by someone who had measured something. What was missing was anything
that noticed when two of them disagreed.

    python3 src/RimMandrake/Utils/check_canon.py            # report, exit 1 if any
    python3 src/RimMandrake/Utils/check_canon.py --list      # the rules, and what they allow
    python3 src/RimMandrake/Utils/check_canon.py <path>...   # only these files

🔴 WHAT THIS TOOL DELIBERATELY DOES NOT DO
==========================================
It does not check every number in canon. Several canon entries are NOT single
values and forcing them to be one would destroy information:

  * **species** — 42 / 44 / 70 / 79 / 139 are five different denominators (one mod's
    roster, an art-audit subset, ours on disk, distinct species across all mods, live
    xenotypes). A doc citing 42 is not contradicting a doc citing 79.
  * **temperature** — +14 °C is OUR terminator and −37 °C is the MOD's at the same
    arc. Both are correct. The defect was never the numbers; it was labelling the
    mod's x=0.5 point "the terminator" when it is arc 45°.
  * **habitable ring** — 34–57 vs 40–57 is a genuine open question filed under
    `needs_ruling`. A checker that picked one would be inventing a decision.
  * **mod counts** — every one of the twenty was true the day it was written. The
    defect is an undated count, not a wrong count, so `--list` reports undated mod
    counts as ADVISORY and they never fail the build.

⛔ Do not "improve" this by adding rules for those. A checker that forces false
agreement is worse than no checker, because its silence then means nothing.

THE EXEMPTION RULE, AND THE TRAP IN IT
======================================
Prose that DOCUMENTS an old number must not trip the check. The obvious rule —
ignore any line containing `~~`, `superseded`, `was`, `formerly`, `dead` or `⛔` —
is wrong, and both counter-examples were found before this file was written:

  the_one_map.md:130   a table row whose RIGHT cell holds `~~worldgen_sea_spec.md
                       req 1 (22–28%)~~` while its LEFT cell asserts a LIVE target
  fauna_placement.md   a line opening `⛔ **Not** in Ocean/Lake` — the ⛔ negates a
                       fauna placement, not the biome

Both fail the same way: a **silent miss**, where the checker reports clean and the
contradiction survives. That is the expensive direction.

✅ So the marker is scoped to the CELL, not the line: in a table row the line is
split on `|` and only the cell holding the number is tested. Outside a table the
whole line is the cell.

Escape hatch: put `<!-- canon-ok: why -->` on the line, or on the line before it.
Use it when a doc genuinely needs to state a value canon disagrees with, and say why.

Stdlib plus PyYAML — the one non-stdlib import in the tooling, and canon.yml says
why it is worth it.
"""
import argparse
import os
import re
import sys

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
CANON = os.path.join(ROOT, "infrastructure", "state", "canon.yml")

# A cell is exempt if it is DOCUMENTING a value rather than asserting it.
HISTORICAL = re.compile(
    r"~~|superseded|formerly|\bwas\b|\bwere\b|\bdead\b|⛔|"
    r"used to (say|read)|no longer|previously", re.I)
ESCAPE = re.compile(r"<!--\s*canon-ok:")
# A DENIAL is not an assertion. "Water is 8.14% — not 25%" is the corrected sentence,
# and flagging it punishes exactly the docs that did the work. Scoped to the words
# immediately before the number so it cannot swallow a real claim further up the cell.
DENIAL = re.compile(r"(\bnot\b|\bnever\b|\bnor\b|≠|rather than|instead of)"
                    r"[\s~*_`(]*$", re.I)

# 🔴 The `modlist_undated` rule's own exemptions. It fires on a 5xx near the word "mod",
# and on the real corpus five of its hits were wrong in two distinct ways — reported
# 2026-08-20 by an agent whose files it flagged:
#
#   "the owner's real 578-mod list AS OF 2026-08-20"   ← already dated; the rule's entire
#                                                        point is the MISSING date
#   "that mod IS ACTIVE ... position 557"              ← a LOAD-ORDER POSITION, not a count
#   "Active at 573"                                    ← same
#
# ⚠️ This rule is advisory, so a false positive never blocks a commit — which makes it
# MORE dangerous, not less: nobody investigates a warning they have learned is usually
# wrong, and the real undated counts would sit inside the noise forever.
DATED = re.compile(r"20\d\d-\d\d-\d\d|\bas of\b|\bsince\b|\bon that day\b", re.I)
POSITION = re.compile(r"\b(position|slot|index|at)\s*$", re.I)
FENCE = re.compile(r"^\s*(```|~~~)")


class Rule:
    """One checkable fact.

    `bad`     — the contradicting value, matched anywhere in a cell.
    `context` — what else the cell must contain for the number to be ABOUT this fact.
                `66` is a settlement count, a BiomeDef count and a rainfall figure in
                three different files; without a context test the rule is a coin toss.

    🔴 AND KEEP THE COUNTED NOUN INSIDE `bad`, NOT IN `context`. A first pass matched
    a bare `14` in any cell containing the word "faction" and produced 24 hits, ALL of
    them false: the dates `2026-08-14`, section headings `## 14.`, the id range
    `0–21871`, a raid-weight sum `≈37`, and the index usage `faction 11` (a slot, not
    a count). A count is written next to its plural noun — `14 factions`, never
    `faction 14` — so requiring `factions` within a few words of the number is what
    separates a count from every one of those. 24 false positives went to 0 and no
    true positive was lost.

    ⚠️ Keep `context` a SEPARATE test, never an inline `(?=.*…)` lookahead on `bad`.
    A lookahead only sees text to the RIGHT of the number, so "Water is 25% of the
    spec" matches and "the 25% water spec" does not — the rule then fires or not on
    word order, which reads as working and is not. That bug was in the first draft of
    this file and was caught by the probe in `selftest_check_canon.py`.

    `why` is printed on every hit and is the whole value of the report: a bare
    "line 100 is wrong" sends the reader back to the audit we are trying to retire.
    """

    def __init__(self, key, bad, canon, why, context=None, advisory=False):
        self.key, self.canon, self.why = key, canon, why
        self.bad = re.compile(bad, re.I)
        self.context = re.compile(context, re.I) if context else None
        self.advisory = advisory


def rules(c):
    p, s, f = c["planet"], c["settlements"], c["factions"]
    return [
        Rule("water",
             r"(?<![\d.])(25\s*%|22\s*[-–]\s*28\s*%|6\.9\s*%|8\.6\s*%)(?=[^\w%]|$)",
             "%s%%" % p["water_pct"],
             "Water is %s%% — %d of %d tiles, measured. 25%%/22–28%% is the dead "
             "worldgen_sea_spec; 8.6%% was the target; 6.9%% measured a dead world."
             % (p["water_pct"], p["water_tiles"], p["tiles"]),
             context=r"water|ocean|sea\b|tiles"),

        Rule("tiles",
             r"\b(21,?87[013-9]|2187[0-9]{2})\b(?:[ \t]+\w+){0,2}[ \t-]+tiles?\b",
             str(p["tiles"]),
             "The planet is %d tiles — the engine's geodesic grid at subdivision 7."
             % p["tiles"], context=r"tile|grid|planet"),

        Rule("settlements",
             r"\b(66|37)\b(?:[ \t]+\w+){0,2}[ \t]+(settlements?|holdings?)\b",
             str(s["total"]),
             "There are %d settlements. 66 counted an earlier paint of this world; "
             "37 counted a dead one." % s["total"], context=r"settlement|holding"),

        Rule("factions",
             r"\b(fourteen|14|eleven|11)\b(?:[ \t]+\w+){0,2}[ \t]+factions\b"
             r"|\bfactions\b[ \t]*[:=][ \t]*(14|11)\b",
             str(f["count"]),
             "The roster is %d factions — %d FactionDefs we define plus 5 from vanilla "
             "and mods. The Unbound Hive was cut and the cut landed on disk. "
             "⚠️ 12 is CORRECT for 'factions holding settlements' or 'carrying "
             "dossiers' — name which, do not change it to 13."
             % (f["count"], f["defined_by_us"]), context=r"faction"),

        Rule("bestiary",
             r"\b78\b(?:[ \t]+\w+){0,2}[ \t-]+(creatures?|named|entries)\b"
             r"|(creatures?|names?)\b[ \t]*[:=][ \t]*78\b",
             str(c["bestiary"]["named"]),
             "Alien_Bestiary.md names %d creatures, not 78 — its own header says "
             "'all 104 VGE creatures plus the four special outputs'. The 78 parsed "
             "only the tables sharing one header row." % c["bestiary"]["named"],
             context=r"creature|bestiary|named|species"),

        Rule("axis",
             r"latitude is the axis|axis (is|=) latitude|keyed? on latitude",
             p["axis"],
             "The axis is ARC from the substellar point, not latitude — correlation "
             "−0.98 on the painted world, and the mod evaluates its own curve at "
             "Acos(cos lon · cos lat)/90, which is arc too."),

        Rule("terminator",
             r"\b(our|ours|the painted|ash'?karr'?s?)\b[^.|]{0,60}?terminator"
             r"[^.|]{0,30}?[-−]\s*37\s*°?\s*C\b",
             "%s °C" % c["temperature_curves"]["ours_terminator_c"],
             "OUR terminator is +%s °C (the owner's ruled endpoints, painted into the "
             "frozen save). −37 °C is the MOD's curve at the same arc, and the mod is "
             "worldgen-only so it cannot reach a hand-painted save. Both stand; do not "
             "merge them." % c["temperature_curves"]["ours_terminator_c"],
             # ADVISORY on purpose. Since the 2026-08-20 correction the RIGHT docs
             # discuss −37 °C constantly — explaining that it is the mod's, and that
             # a worldgen-only patch cannot reach a frozen save. A rule that fires on
             # correct prose is worse than none, so this flags for a human read and
             # never fails the build.
             advisory=True),

        Rule("lake",
             r"`?Lake`?\s*(is\s+)?cut\b|cut\s+`?Lake`?\b",
             "keep",
             "`Lake` STAYS. The Scald — one of exactly three ruled seas — is Lake for "
             "all %d of its tiles. Cutting the def deletes a named sea."
             % c["lake_biome"]["tiles"]),

        # ADVISORY — never fails the build. See the docstring: an undated mod count is
        # the defect, and no single number can be right for every line.
        Rule("modlist_undated",
             # ⚠️ ADJACENT to the noun, like the count rules above — the same lesson,
             # learned twice. Matching a 5xx anywhere near the word "mod" flagged a
             # file:line citation (`ship_distinctive_features.md:566` … "from Afterlife,
             # a mod") and a count of PLANTS ("566 of them across dozens of mods"). A
             # mod count is written next to its noun: `578-mod list`, `573 mods`.
             r"\b(5[4-8][0-9])[ \t]*-?[ \t]*mods?\b|\bmods?\b[ \t]*[:=][ \t]*(5[4-8][0-9])\b",
             "%d as of %s" % (c["modlist"]["official_count"], c["modlist"]["as_of"]),
             "A mod count with no as-of date reads as current forever. Stamp it with "
             "the date it was taken — do NOT replace the number.",
             advisory=True),
    ]


def cells(line):
    """The testable spans of a line. A table row splits on `|`; anything else is whole."""
    if line.count("|") >= 2:
        return [c for c in line.split("|") if c.strip()]
    return [line]


def scan(paths, rs):
    hits = []
    for path in paths:
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                lines = fh.read().splitlines()
        except OSError:
            continue
        infence = False
        for i, line in enumerate(lines, 1):
            if FENCE.match(line):
                infence = not infence
                continue
            if infence or line.lstrip().startswith(">"):
                continue                        # code and quotation are not assertions
            if ESCAPE.search(line) or (i > 1 and ESCAPE.search(lines[i - 2])):
                continue
            for cell in cells(line):
                if HISTORICAL.search(cell):
                    continue                    # this cell documents; it does not claim
                for r in rs:
                    if r.context and not r.context.search(cell):
                        continue            # the number is not about this fact
                    m = r.bad.search(cell)
                    if m and DENIAL.search(cell[:m.start()][-24:]):
                        continue            # "— not 25%" denies it; it does not claim it
                    if m and r.key == "modlist_undated":
                        if DATED.search(cell):
                            continue        # it HAS a date; that is the whole rule
                        if POSITION.search(cell[:m.start()][-14:]):
                            continue        # a load-order position, not a count
                    if m:
                        hits.append((path, i, r, m.group(0).strip(), line.strip()))
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*", help="files to check (default: all of design/)")
    ap.add_argument("--list", action="store_true", help="print the rules and exit")
    a = ap.parse_args()

    try:
        import yaml
    except ImportError:
        print("check_canon: PyYAML is not installed, so canon cannot be read.\n"
              "  pip install --user PyYAML\n"
              "  ⚠️ UNMEASURED is not the same as PASSED — do not read this exit as a pass.",
              file=sys.stderr)
        return 2
    with open(CANON, encoding="utf-8") as fh:
        canon = yaml.safe_load(fh)
    rs = rules(canon)

    if a.list:
        print("canon.yml v%s, as of %s\n" % (canon["version"], canon["as_of"]))
        for r in rs:
            print("  %-16s canon %-22s %s"
                  % (r.key + (" (advisory)" if r.advisory else ""), r.canon, r.why))
        print("\n  escape: <!-- canon-ok: why --> on the line, or the line above it")
        return 0

    if a.paths:
        paths = [os.path.join(ROOT, p) if not os.path.isabs(p) else p for p in a.paths]
    else:
        paths = []
        for dirpath, _dirs, files in os.walk(os.path.join(ROOT, "design")):
            paths += [os.path.join(dirpath, f) for f in files if f.endswith(".md")]
    paths.sort()

    hits = scan(paths, rs)
    hard = [h for h in hits if not h[2].advisory]
    soft = [h for h in hits if h[2].advisory]

    for group, label in ((hard, "CONTRADICTS CANON"), (soft, "advisory")):
        if not group:
            continue
        print("\n%s — %d" % (label, len(group)))
        for path, i, r, found, line in group:
            rel = os.path.relpath(path, ROOT)
            print("  %s:%d  [%s] found %r, canon says %s" % (rel, i, r.key, found, r.canon))
            print("      %s" % r.why.replace("\n", " "))
            print("      | %s" % (line[:150] + ("…" if len(line) > 150 else "")))

    print("\n%d file(s) checked. %d contradiction(s), %d advisory."
          % (len(paths), len(hard), len(soft)))
    if not hard:
        print("✅ no design doc contradicts canon.")
    return 1 if hard else 0


if __name__ == "__main__":
    sys.exit(main())
