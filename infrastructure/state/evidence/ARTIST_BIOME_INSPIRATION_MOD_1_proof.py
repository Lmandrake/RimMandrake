#!/usr/bin/env python3
"""Proof for ARTIST_BIOME_INSPIRATION_MOD_1 (criteria: a design doc with the variants weighed; the owner
rules it -- delegated, owner 2026-10-22; a build item is filed).

Exit 0 when every clause holds, 1 when any fails. `--mutants` instead applies each known break to the
doc text in memory and exits 0 only if every mutant goes red (the proof can see each clause break).
Reads only the repo: the design doc and the ledger shards (no cli.py, no RM_DATA_ROOT, no items/ tree).
"""
import glob
import json
import re
import sys

ITEM = "ARTIST_BIOME_INSPIRATION_MOD_1"
BUILD = "ARTIST_BIOME_INSPIRATION_BUILD_RESTLESS_MUSE"
DOC = "design/RimMandrake/artist_biome_inspiration_design.md"
# the three variants the item names, and a word each must carry in its heading
VARIANTS = (("1", "fixed"), ("2", "hated"), ("3", "restless"))
MIN_BODY = 3          # non-blank prose lines a variant must have to count as weighed


def section(text, title, level=2):
    """-> body of the `level`-hash heading `title` up to the next heading of that level or higher, or None."""
    lines = text.split("\n")
    head = re.compile(r"^#{1,%d} " % level)
    for i, ln in enumerate(lines):
        if ln.strip() == "#" * level + " " + title:
            end = next((j for j in range(i + 1, len(lines)) if head.match(lines[j])), len(lines))
            return "\n".join(lines[i + 1:end])
    return None


def doc_failures(text):
    bad = []
    if not re.search(r"^## Variants weighed\s*$", text, re.M):
        bad.append("no '## Variants weighed'")
    if not re.search(r"^## Ruling\s*$", text, re.M):
        bad.append("no '## Ruling'")
    if BUILD not in text:
        bad.append("doc does not name build item %s" % BUILD)
    vw = section(text, "Variants weighed") or ""
    subs = re.split(r"^(### .*)$", vw, flags=re.M)        # [pre, head1, body1, head2, body2, ...]
    heads = {subs[k]: subs[k + 1] for k in range(1, len(subs) - 1, 2)}
    for num, word in VARIANTS:
        hit = [(h, b) for h, b in heads.items() if h.startswith("### %s." % num)]
        if not hit:
            bad.append("variant %s missing under Variants weighed" % num)
            continue
        h, b = hit[0]
        if word not in h.lower():
            bad.append("variant %s heading lacks '%s': %r" % (num, word, h))
        body = [ln for ln in b.split("\n") if ln.strip()]
        if len(body) < MIN_BODY:
            bad.append("variant %s has %d body lines (< %d): not weighed" % (num, len(body), MIN_BODY))
    table = heads.get("### Decision table", "")
    rows = [ln for ln in table.split("\n") if ln.strip().startswith("|")]
    if len(rows) < 4 or not all(w in rows[0].lower() for _, w in VARIANTS):
        bad.append("decision table missing or does not compare all three variants")
    ru = section(text, "Ruling") or ""
    first = next((ln for ln in ru.split("\n") if ln.strip()), "")
    if not re.search(r"variant 3", first, re.I) or "restless" not in first.lower():
        bad.append("Ruling does not pick variant 3 (restless)")
    if not (re.search(r"variant 1", ru, re.I) and re.search(r"variant 2", ru, re.I)):
        bad.append("Ruling does not dispose of variants 1 and 2")
    return bad


def ledger_failures():
    ev = []
    for f in glob.glob("infrastructure/state/ledger/events/*.jsonl"):
        for ln in open(f, encoding="utf-8"):
            if "ARTIST_BIOME_INSPIRATION" in ln:
                try:
                    ev.append(json.loads(ln))
                except ValueError:
                    pass
    b = [e for e in ev if e.get("id") == BUILD]
    filed = any(e.get("event") == "file" and e.get("caused_by") == ITEM for e in b)
    dead = any(e.get("event") in ("drop", "supersede") for e in b)
    ruled = any(e.get("id") == ITEM and e.get("event") == "note" and str(e.get("text", "")).startswith("Ruled:")
                and str(e.get("why", "")).startswith("delegated") for e in ev)
    print("filed", filed, "dead", dead, "ruled", ruled)
    bad = []
    if not filed:
        bad.append("build item not filed caused_by %s" % ITEM)
    if dead:
        bad.append("build item dropped/superseded")
    if not ruled:
        bad.append("no delegated 'Ruled:' note")
    return bad


def mutants(text):
    lines = text.split("\n")
    vw0 = next(i for i, ln in enumerate(lines) if ln.strip() == "## Variants weighed")
    rd0 = next(i for i, ln in enumerate(lines) if ln.strip() == "## Recommended design")

    def drop_sub(prefix, keep_head):
        out, skip = [], False
        for ln in lines:
            if ln.startswith("### ") or ln.startswith("## "):
                skip = ln.startswith(prefix)
                if skip and keep_head:
                    out.append(ln)
                    continue
            if not skip:
                out.append(ln)
        return "\n".join(out)

    yield "checker's mutant: blank Variants weighed..Recommended design body", \
        "\n".join(lines[:vw0 + 1] + lines[rd0 - 1:])
    for num, _ in VARIANTS:
        yield "delete variant %s section" % num, drop_sub("### %s." % num, False)
        yield "empty variant %s body, keep heading" % num, drop_sub("### %s." % num, True)
    yield "delete decision table", drop_sub("### Decision table", False)
    yield "variant 3 retitled without 'restless'", re.sub(r"^### 3\..*$", "### 3. Something else", text, flags=re.M)
    yield "Ruling picks variant 1", re.sub(r"Variant 3 \(restless\) is the default", "Variant 1 (fixed) is the default",
                                         text)
    yield "drop the build id", text.replace(BUILD, "SOME_OTHER_ITEM")


def main():
    text = open(DOC, encoding="utf-8").read()
    if "--mutants" in sys.argv:
        survived = 0
        for name, mtext in mutants(text):
            assert mtext != text, "mutant %r changed nothing" % name
            red = doc_failures(mtext)
            print("%-6s %s%s" % ("RED" if red else "GREEN", name, (": " + red[0]) if red else ""))
            survived += not red
        print("mutants survived:", survived)
        return 1 if survived else 0
    bad = doc_failures(text) + ledger_failures()
    for b in bad:
        print("FAIL", b)
    print("PASS" if not bad else "FAIL")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
