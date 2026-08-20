#!/usr/bin/env python3
"""
cast_to_xml.py — the eleven prose cast files become CharacterDefs.

VERSION 1.0  (2026-08-20)   Project: D:/Luke/dev/Rimworld/src/RimMandrake/Utils/
Dependency-free: Python 3.8+ stdlib only. Keep it that way.

WHAT THIS IS FOR
----------------
`design/Jawa/bridge/INHABITED_CAST_*.md` hold 269 hand-authored people as PROSE,
because prose is what a human can write 269 of. The `Inhabited` mod needs them as
defs. This is the one-way bridge.

🔴 THE PROSE FILES ARE THE SOURCE OF TRUTH AND STAY THAT WAY. They are what a
human edits. This tool regenerates FROM them and never back into them, and the
XML it writes is derived: delete it and re-run, never hand-edit it.

WHAT THE PROSE CARRIES, AND WHAT IT DOES NOT
--------------------------------------------
Present on every entry:  name · race (prose, not a def) · gender · age ·
                         traits (REAL TraitDef names, some with a degree) ·
                         childhood · adult · hook
Absent from ALL of them: xenotype · pawnKind · faction defName · apparel · skills

⛔ Those four are DECIDE's to answer and this tool must never invent them. A
guessed xenotype ships a wrong-looking person into a world that is built once and
frozen, and nobody can see the mistake. They are emitted empty, which reads as a
question; a guess would read as an answer.

⚠️ THE DROID FILE IS DIFFERENT ON PURPOSE, by owner ruling: `chassis` stands in
for race and `service-years` for age. Handled, not normalised away.

⚠️ THE TWELFTH FACTION HAS NO CAST FILE. Deepwater Compact (*the Balance*) is
tabled in INHABITED_DESIGN.md but nobody has written its 25 people. That is
authoring debt, not a parser bug, and this tool reports it rather than failing.

TRAIT DEGREES
-------------
The prose writes degrees by NAME — `NaturalMood(Sanguine)`,
`DrugDesire(ChemicalFascination)` — because that is what fits in a writer's head.
The engine wants an integer. This resolves the name against the def dump's
`degreeDatas` and emits the integer, so nothing is looked up at runtime and

  🔴 A TRAIT OR DEGREE THAT DOES NOT RESOLVE FAILS HERE, LOUDLY, AT BUILD TIME
  rather than in somebody's game. That is the one thing in this tool that must
  never be soft.

USAGE
-----
    python3 src/RimMandrake/Utils/cast_to_xml.py            # report only
    python3 src/RimMandrake/Utils/cast_to_xml.py --write    # write the XML
    python3 src/RimMandrake/Utils/cast_to_xml.py --dump <path to DefDump/defs>
"""

import argparse
import json
import os
import re
import sys
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

CAST_DIR = os.path.join(ROOT, "design", "Jawa", "bridge")
OUT_DIR = os.path.join(ROOT, "src", "Jawa", "Inhabited", "Defs", "CastRosters")

_DUMPS = [
    r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios"
    r"\RimWorld by Ludeon Studios\DefDump\defs",
    "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios"
    "/RimWorld by Ludeon Studios/DefDump/defs",
]

# The twelfth faction. Tabled in the design, never authored.
MISSING_CASTS = ["DEEPWATER"]

# **Name** · race · gender · age
ENTRY_RE = re.compile(
    r"^\*\*(?P<name>[^*]+)\*\*\s*·\s*(?P<race>[^·]+?)\s*·\s*(?P<gender>[^·]+?)\s*·\s*(?P<age>[^·]+?)\s*$"
)
TRAITS_RE = re.compile(r"^`traits:\s*(?P<traits>.+?)`\s*$")
FIELD_RE = re.compile(r"^(?P<key>childhood|adult):\s*(?P<value>.+?)\s*$")
HOOK_RE = re.compile(r"^>\s?(?P<text>.*)$")
HEADING_RE = re.compile(r"^##\s+(?P<text>.+?)\s*$")
INT_RE = re.compile(r"\d[\d,]*")

# Years in service rather than years alive. The droid cast writes this six ways.
SERVICE_MARKERS = ("service-year", "since activation", "since assembly",
                   "since salvage", "since reactivation")
TRAIT_RE = re.compile(r"^(?P<def>[A-Za-z_][A-Za-z0-9_]*)(?:\((?P<degree>[^)]+)\))?$")

GENDER_MAP = {"m": "Male", "f": "Female"}


def die(msg):
    print("FAIL: " + msg, file=sys.stderr)
    sys.exit(2)


def first_existing(paths, what):
    for p in paths:
        if os.path.isdir(p):
            return p
    die("could not find " + what + "; tried:\n  " + "\n  ".join(paths))


def load_traits(dump_dir):
    """-> {defName: {normalised degree label: degree int}}  plus the degree set."""
    path = os.path.join(dump_dir, "TraitDef.json")
    if not os.path.isfile(path):
        die("no TraitDef.json at " + path + "\n"
            "      The def dump is how a trait name is proven to exist. Refresh it\n"
            "      (src/RimMandrake/Utils/refresh.py) or pass --dump.")
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    out = {}
    for d in data.get("defs", []):
        degrees = {}
        for dd in (d.get("fields") or {}).get("degreeDatas") or []:
            label = dd.get("untranslatedLabel") or dd.get("label") or ""
            degrees[norm(label)] = int(dd.get("degree", 0))
        out[d["defName"]] = degrees
    return out


def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def is_place_heading(text):
    """A place is written in CAPS. Prose sections are not."""
    head = re.split(r"\s+[—–-]\s+", text, maxsplit=1)[0]
    head = head.replace("*", "").replace("`", "").strip()
    letters = [c for c in head if c.isalpha()]
    if len(letters) < 2:
        return False
    return head == head.upper()


def slug(name):
    s = re.sub(r"[^A-Za-z0-9]+", " ", name).title().replace(" ", "")
    if s and s[0].isdigit():
        s = "N" + s
    return s


def parse_file(path, faction, traitdb, problems):
    """-> list of character dicts."""
    with open(path, "r", encoding="utf-8") as fh:
        lines = fh.read().splitlines()

    people = []
    place = None
    i = 0
    while i < len(lines):
        line = lines[i]

        h = HEADING_RE.match(line)
        if h:
            place = h.group("text") if is_place_heading(h.group("text")) else place
            i += 1
            continue

        m = ENTRY_RE.match(line)
        if not m:
            i += 1
            continue

        person = {
            "faction": faction,
            "place": (place or "").replace("*", "").strip(),
            "name": m.group("name").strip(),
            "race": m.group("race").strip(),
            "gender_text": m.group("gender").strip(),
            "age": -1,
            "service_years": -1,
            "age_text": "",
            "traits": [],
            "childhood": "",
            "adult": "",
            "hook": "",
            "line": i + 1,
        }

        age_raw = m.group("age").strip()
        person["age_text"] = age_raw
        years, is_service = parse_age(age_raw)
        if years is None:
            # "unknown" is authored on purpose for several characters and is not
            # a parse failure. The verbatim text is kept either way.
            if "unknown" not in age_raw.lower():
                problems.append("%s:%d  no number in age %r for %s"
                                % (os.path.basename(path), i + 1, age_raw, person["name"]))
        elif is_service:
            person["service_years"] = years
        else:
            person["age"] = years

        hook_lines = []
        i += 1
        while i < len(lines):
            nxt = lines[i]
            if ENTRY_RE.match(nxt) or HEADING_RE.match(nxt):
                break

            t = TRAITS_RE.match(nxt)
            if t:
                person["traits"] = parse_traits(
                    t.group("traits"), traitdb, path, i + 1, person["name"], problems)
                i += 1
                continue

            f = FIELD_RE.match(nxt)
            if f:
                person[f.group("key")] = f.group("value")
                i += 1
                continue

            hk = HOOK_RE.match(nxt)
            if hk:
                hook_lines.append(hk.group("text").strip())
                i += 1
                continue

            i += 1

        person["hook"] = " ".join(x for x in hook_lines if x).strip()
        if not person["hook"]:
            problems.append("%s:%d  no hook for %s"
                            % (os.path.basename(path), person["line"], person["name"]))
        people.append(person)

    return people


def parse_age(raw):
    """
    -> (years or None, is_service_years)

    The prose does NOT carry a plain integer on every entry, which is what the
    queue item's measurement said. Eleven files write it eight ways:

        101                     a plain year count
        ~90 / 60ish / 300+      approximate, and the author meant it
        six hems (33)           the Jawa file counts robe-hems; the years are
                                the parenthesised gloss, which is the real number
        312 service-years       droids, by owner ruling
        61 years since activation / since assembly / since salvage
        claims 40,000; is 90    a droid who lies about his age. The truth is last.
        unknown                 authored deliberately. Not a failure.

    🔑 THE LAST INTEGER IN THE STRING IS THE ANSWER IN EVERY ONE OF THESE CASES,
    including the two that look like exceptions -- the Jawa parenthetical gloss
    and Grandfather Kesh's boast. That is not luck: a writer puts the real number
    last because the clause before it is the flavour.

    ⛔ The verbatim text is kept on the def regardless. "six hems" IS the
    characterisation and reducing it to 33 would throw the interesting half away.
    """
    lower = raw.lower()
    hits = INT_RE.findall(raw)
    if not hits:
        return None, False
    years = int(hits[-1].replace(",", ""))
    is_service = any(marker in lower for marker in SERVICE_MARKERS)
    return years, is_service


def parse_traits(raw, traitdb, path, lineno, who, problems):
    out = []
    for piece in [p.strip() for p in raw.split(",") if p.strip()]:
        m = TRAIT_RE.match(piece)
        if not m:
            problems.append("%s:%d  unparseable trait %r on %s"
                            % (os.path.basename(path), lineno, piece, who))
            continue
        name = m.group("def")
        degree_name = (m.group("degree") or "").strip()

        if name not in traitdb:
            problems.append("%s:%d  TRAIT DOES NOT EXIST: %s (on %s)"
                            % (os.path.basename(path), lineno, name, who))
            continue

        degrees = traitdb[name]
        if degree_name:
            key = norm(degree_name)
            if key not in degrees:
                problems.append(
                    "%s:%d  %s has no degree %r (on %s); it has: %s"
                    % (os.path.basename(path), lineno, name, degree_name, who,
                       ", ".join(sorted(degrees)) or "none"))
                continue
            degree = degrees[key]
        elif 0 in degrees.values():
            degree = 0
        elif len(degrees) == 1:
            degree = list(degrees.values())[0]
        else:
            problems.append(
                "%s:%d  %s needs a degree (on %s); it has: %s"
                % (os.path.basename(path), lineno, name, who, ", ".join(sorted(degrees))))
            continue

        out.append({"def": name, "degree": degree, "degree_name": degree_name})
    return out


def emit(people, faction, defnames):
    rows = [
        '<?xml version="1.0" encoding="utf-8" ?>',
        "<Defs>",
        "",
        "  <!--",
        "    GENERATED by src/RimMandrake/Utils/cast_to_xml.py. Do not hand-edit.",
        "    The source of truth is design/Jawa/bridge/INHABITED_CAST_%s.md;" % faction,
        "    edit the prose there and re-run the tool.",
        "",
        "    xenotype, pawnKind, apparel and skills are deliberately absent: the",
        "    prose does not carry them and DECIDE owes them. Empty reads as a",
        "    question. A guess would read as an answer.",
        "  -->",
        "",
    ]
    for p in people:
        base = "Inhabited_%s_%s" % (faction.title(), slug(p["name"]))
        defname = base
        n = 2
        while defname in defnames:
            defname = "%s_%d" % (base, n)
            n += 1
        defnames.add(defname)

        rows.append("  <Inhabited.CharacterDef>")
        rows.append("    <defName>%s</defName>" % defname)
        rows.append("    <label>%s</label>" % escape(p["name"]))
        rows.append("    <faction>%s</faction>" % escape(faction))
        if p["place"]:
            rows.append("    <place>%s</place>" % escape(p["place"]))
        if p["service_years"] >= 0 or faction == "DROIDS":
            rows.append("    <chassis>%s</chassis>" % escape(p["race"]))
            if p["service_years"] >= 0:
                rows.append("    <serviceYears>%d</serviceYears>" % p["service_years"])
            elif p["age"] >= 0:
                rows.append("    <serviceYears>%d</serviceYears>" % p["age"])
        else:
            rows.append("    <race>%s</race>" % escape(p["race"]))
            if p["age"] >= 0:
                rows.append("    <age>%d</age>" % p["age"])
        rows.append("    <ageText>%s</ageText>" % escape(p["age_text"]))
        rows.append("    <genderText>%s</genderText>" % escape(p["gender_text"]))
        g = GENDER_MAP.get(p["gender_text"])
        if g:
            rows.append("    <gender>%s</gender>" % g)
        if p["childhood"]:
            rows.append("    <childhood>%s</childhood>" % escape(p["childhood"]))
        if p["adult"]:
            rows.append("    <adult>%s</adult>" % escape(p["adult"]))
        if p["hook"]:
            rows.append("    <hook>%s</hook>" % escape(p["hook"]))
        if p["traits"]:
            rows.append("    <traits>")
            for t in p["traits"]:
                rows.append("      <li>")
                rows.append("        <def>%s</def>" % t["def"])
                rows.append("        <degree>%d</degree>" % t["degree"])
                if t["degree_name"]:
                    rows.append("        <degreeName>%s</degreeName>" % escape(t["degree_name"]))
                rows.append("      </li>")
            rows.append("    </traits>")
        rows.append("  </Inhabited.CharacterDef>")
        rows.append("")
    rows.append("</Defs>")
    return "\n".join(rows) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true",
                    help="write the XML. Without this it reports and writes nothing.")
    ap.add_argument("--dump", help="path to DefDump/defs (for TraitDef.json)")
    args = ap.parse_args()

    dump = args.dump or first_existing(_DUMPS, "the def dump")
    traitdb = load_traits(dump)
    print("traits known: %d, from %s" % (len(traitdb), dump))

    files = sorted(f for f in os.listdir(CAST_DIR)
                   if f.startswith("INHABITED_CAST_") and f.endswith(".md"))
    if not files:
        die("no INHABITED_CAST_*.md under " + CAST_DIR)

    problems = []
    defnames = set()
    total = 0
    written = []

    for fn in files:
        faction = fn[len("INHABITED_CAST_"):-len(".md")]
        people = parse_file(os.path.join(CAST_DIR, fn), faction, traitdb, problems)
        total += len(people)
        xml = emit(people, faction, defnames)
        out = os.path.join(OUT_DIR, "CastRoster_%s.xml" % faction)
        if args.write:
            os.makedirs(OUT_DIR, exist_ok=True)
            with open(out, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(xml)
            written.append(out)
        ntr = sum(len(p["traits"]) for p in people)
        print("  %-12s %3d people, %3d traits  -> %s"
              % (faction, len(people), ntr, os.path.basename(out)))

    for m in MISSING_CASTS:
        print("  %-12s   0 people          -- NO CAST FILE. Authoring debt, not a bug."
              % m)

    print("\n%d characters across %d files" % (total, len(files)))

    if problems:
        print("\n%d PROBLEM(S):" % len(problems))
        for p in problems:
            print("  " + p)
        print("\nA trait that does not resolve is the one thing here that must fail.")
        return 1

    print("every trait and degree resolved against the dump.")
    if args.write:
        print("wrote %d file(s) to %s" % (len(written), OUT_DIR))
    else:
        print("nothing written. Re-run with --write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
