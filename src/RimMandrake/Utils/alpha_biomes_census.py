#!/usr/bin/env python3
"""alpha_biomes_census.py -- every Alpha Biomes name we still say, and what was decided about it.

    python3 src/RimMandrake/Utils/alpha_biomes_census.py check [--json OUT]
    python3 src/RimMandrake/Utils/alpha_biomes_census.py md            (rewrites the name tables of the doc)

Item ALPHA_BIOMES_CENSUS_THE_REST_OF_IT. Decisions: design/RimMandrake/alpha_biomes_census_2026-11-01.json (hand-owned;
this tool never writes a decision). Doc: design/RimMandrake/alpha_biomes_census_2026-11-01.md.

`check` proves, against tracked files only (a stray untracked file must not move the verdict):
  1. every row is a real donor name: in the committed inventory facts/retired_donor_defs/sarg.alphabiomes.json;
  2. each of the six categories is complete (count == the recorded donor count) and carries exactly one decision;
     when the donor's install is on disk the element types are re-read from it, otherwise that line says UNMEASURED;
  3. every PORTED row names a def src/ defines as the SAME def type; VANILLA rows are named, never checked here;
  4. every AB_ token in tracked src/ text is known: a category row, or a `tokens` class in the JSON;
  5. no AB_ token is live: XML element text or attribute outside a path and outside About.xml prose, or a C# string
     outside comments. A retired_donor_refs ALLOW row (cited in `live_allowed`) is the one exception.
Exit 0 CLEAN, 1 findings, 2 UNMEASURED (blind: missing or undersized inputs; never a clean zero).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
DECISIONS = os.path.join(REPO, "design", "RimMandrake", "alpha_biomes_census_2026-11-01.json")
DOC = os.path.join(REPO, "design", "RimMandrake", "alpha_biomes_census_2026-11-01.md")
INVENTORY = os.path.join(REPO, "infrastructure", "state", "facts", "retired_donor_defs", "sarg.alphabiomes.json")
DONOR = "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/1841354677"
CATEGORIES = ("TerrainDef", "WeatherDef", "ThoughtDef", "BiomeDef", "TileMutatorDef", "LandmarkDef")
DECISION_WORDS = ("PORTED", "VANILLA", "DROPPED", "UNPORTED")
MIN_TOKENS = 100  # a scan seeing fewer was blind: src/ held 223 on 2026-11-01
TOKEN = re.compile(r"\bAB_[A-Za-z0-9_]+")
# Its fixtures are made-up AB_ names; every other tracked file counts.
FIXTURES = {"src/RimMandrake/Utils/selftest_alpha_biomes_census.py"}
BINARY = (".png", ".dds", ".dll", ".pdb", ".jpg", ".jpeg", ".wav", ".ogg", ".psd", ".mp3", ".zip", ".rws")


def tracked(repo, sub="src"):
    out = subprocess.run(["git", "-C", repo, "ls-files", "-z", sub], capture_output=True, text=True, check=True).stdout
    return [f for f in out.split("\0") if f and os.path.isfile(os.path.join(repo, f))]


def read(repo, rel):
    with open(os.path.join(repo, rel), encoding="utf-8", errors="replace") as fh:
        return fh.read()


def src_defs(repo, files):
    """defName -> set of def element tags, read as XML ELEMENTS from tracked src/ XML (comments never count)."""
    defs = {}
    for f in files:
        if not f.lower().endswith(".xml"):
            continue
        try:
            root = ET.fromstring(read(repo, f).encode("utf-8"))
        except ET.ParseError:
            continue
        for e in root:
            d = e.find("defName")
            if d is not None and d.text:
                defs.setdefault(d.text.strip(), set()).add(e.tag)
    return defs


def cs_live(text):
    """C# text with comments removed; string literals survive, so "http://x" is not eaten as a comment."""
    out, i, n = [], 0, len(text)
    while i < n:
        c, d = text[i], text[i:i + 2]
        if d == "//":
            j = text.find("\n", i)
            i = n if j < 0 else j
        elif d == "/*":
            j = text.find("*/", i + 2)
            i = n if j < 0 else j + 2
        elif c == '"':
            j = i + 1
            while j < n and text[j] != '"' and text[j] != "\n":
                j += 2 if text[j] == "\\" else 1
            out.append(text[i:j + 1])
            i = j + 1
        else:
            out.append(c)
            i += 1
    return "".join(out)


def xml_live_tokens(text):
    """AB_ tokens that are references: element text, tag or attribute, skipping any value holding a path."""
    try:
        root = ET.fromstring(text.encode("utf-8"))
    except ET.ParseError:
        return None
    hits = set()
    for e in root.iter():
        vals = [e.text or ""] + list(e.attrib.values()) + [str(e.tag)]
        for v in vals:
            if "/" in v and "defName=" not in v and e.tag != "xpath":
                continue
            hits.update(TOKEN.findall(v))
    return hits


def scan(repo, files):
    """token -> set of files (every context), plus the set of (token, file) that are live references."""
    seen, live = {}, set()
    for f in files:
        if f.lower().endswith(BINARY) or f in FIXTURES:
            continue
        s = read(repo, f)
        if "AB_" not in s:
            continue
        for t in TOKEN.findall(s):
            seen.setdefault(t, set()).add(f)
        low = f.lower()
        if low.endswith(".xml") and os.path.basename(low) != "about.xml":
            for t in xml_live_tokens(s) or ():
                live.add((t, f))
        elif low.endswith(".cs"):
            for t in TOKEN.findall(cs_live(s)):
                live.add((t, f))
    return seen, live


def donor_types(root):
    """category -> names read from the donor's install, or None when it is not on disk."""
    if not os.path.isdir(root):
        return None
    got = {c: set() for c in CATEGORIES}
    for dp, _dn, fn in os.walk(root):
        if "Defs" not in dp.replace(os.sep, "/").split("/"):
            continue
        for f in fn:
            if not f.lower().endswith(".xml"):
                continue
            try:
                r = ET.parse(os.path.join(dp, f)).getroot()
            except ET.ParseError:
                continue
            for e in r:
                d = e.find("defName")
                if e.tag in got and d is not None and d.text:
                    got[e.tag].add(d.text.strip())
    return got


def known_tokens(dec):
    names = set(dec["tokens"])
    for rows in dec["categories"].values():
        names.update(rows)
    return names


def verify(dec, inv, files, repo, donor_root=DONOR):
    """(status, findings, notes). status CLEAN / FINDINGS / UNMEASURED."""
    finds, notes = [], []
    cats = dec.get("categories") or {}
    if set(cats) != set(CATEGORIES) or not inv.get("defs") or len(inv["defs"]) < 50:
        return "UNMEASURED", ["categories or donor inventory missing or undersized"], notes
    invn = set(inv["defs"]) | set(inv.get("abstracts", []))
    defs = src_defs(repo, files)
    seen, live = scan(repo, files)
    if len(seen) < MIN_TOKENS:
        return "UNMEASURED", ["scan saw only %d AB_ tokens (floor %d): blind" % (len(seen), MIN_TOKENS)], notes

    for cat in CATEGORIES:
        rows = cats[cat]
        want = dec["donor_counts"].get(cat)
        if want != len(rows):
            finds.append("COUNT %s: %d rows, donor has %s" % (cat, len(rows), want))
        for name, row in rows.items():
            if name not in invn:
                finds.append("NOT_DONOR %s %s" % (cat, name))
            d = row.get("decision")
            if d not in DECISION_WORDS:
                finds.append("UNDECIDED %s %s (%r)" % (cat, name, d))
            if not row.get("why"):
                finds.append("NO_WHY %s %s" % (cat, name))
            if d == "PORTED":
                to = row.get("to") or []
                if not to:
                    finds.append("PORTED_TO_NOTHING %s %s" % (cat, name))
                for t in to:
                    if cat not in defs.get(t, ()):
                        finds.append("STALE_PORT %s %s -> %s (src defines it as %s)"
                                     % (cat, name, t, sorted(defs.get(t, ())) or "nothing"))
            if d == "VANILLA" and not row.get("to"):
                finds.append("VANILLA_TO_NOTHING %s %s" % (cat, name))

    real = donor_types(donor_root)
    if real is None:
        notes.append("donor install absent: element types UNMEASURED this run (counts still checked)")
    else:
        for cat in CATEGORIES:
            for n in sorted(real[cat] ^ set(cats[cat])):
                finds.append("DONOR_DRIFT %s %s" % (cat, n))

    known = known_tokens(dec)
    for t in sorted(set(seen) - known):
        finds.append("UNDECIDED_TOKEN %s in %s" % (t, sorted(seen[t])[0]))
    for t in sorted(set(dec["tokens"]) - set(seen)):
        finds.append("STALE_TOKEN %s (no longer in src/)" % t)
    allowed = {(a["token"], a["file"]) for a in dec.get("live_allowed", [])}
    for t, f in sorted(live - allowed):
        finds.append("LIVE %s in %s" % (t, f))
    for t, f in sorted(allowed - live):
        finds.append("STALE_ALLOW %s in %s" % (t, f))
    return ("FINDINGS" if finds else "CLEAN"), finds, notes


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def table(cat, rows):
    body = ["| name | decision | successor | why |", "|---|---|---|---|"]
    for n in sorted(rows):
        r = rows[n]
        to = ", ".join("`%s`" % t for t in r.get("to") or []) or "-"
        body.append("| `%s` | %s | %s | %s |" % (n, r["decision"], to, r["why"]))
    return "### %s (%d)\n\n" % (cat, len(rows)) + "\n".join(body) + "\n"


BEGIN, END = "<!-- tables:begin (alpha_biomes_census.py md) -->", "<!-- tables:end -->"


def write_tables(dec, doc=DOC):
    text = open(doc, encoding="utf-8").read()
    a, b = text.index(BEGIN) + len(BEGIN), text.index(END)
    new = "\n\n" + "\n".join(table(c, dec["categories"][c]) for c in CATEGORIES) + "\n"
    with open(doc, "w", encoding="utf-8") as fh:
        fh.write(text[:a] + new + text[b:])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("--json", default=None)
    sub.add_parser("md")
    a = ap.parse_args(argv)
    if not os.path.exists(DECISIONS) or not os.path.exists(INVENTORY):
        print("UNMEASURED: decisions or inventory file missing")
        return 2
    dec = load(DECISIONS)
    if a.cmd == "md":
        write_tables(dec)
        print("wrote", DOC)
        return 0
    status, finds, notes = verify(dec, load(INVENTORY), tracked(REPO), REPO)
    for line in finds + notes:
        print(line)
    tally = {c: {} for c in CATEGORIES}
    for cat in CATEGORIES:
        for r in dec["categories"].get(cat, {}).values():
            tally[cat][r.get("decision")] = tally[cat].get(r.get("decision"), 0) + 1
    print(status, json.dumps(tally))
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump({"status": status, "findings": finds, "notes": notes, "tally": tally}, fh, indent=1)
    return {"CLEAN": 0, "FINDINGS": 1}.get(status, 2)


if __name__ == "__main__":
    sys.exit(main())
