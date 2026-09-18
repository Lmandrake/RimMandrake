#!/usr/bin/env python3
"""canon_census.py — derive ruled/unruled/non-conforming counts for
design/RimStarWars/canon_references/*/description.md, instead of grepping.

WHY (C8, infrastructure/DETERMINISM_ASSESSMENT.md)
====================================================
A census once reported "2 of 137 canon entries ruled"; the real figure is 25.
Two later subagents each measured 25 independently and both had to refuse the
briefed wrong number. A count two agents can disagree about, that a human then
has to arbitrate, should come from a command instead of a grep. This is that
command.

    python3 src/RimMandrake/Utils/canon_census.py                       # counts
    python3 src/RimMandrake/Utils/canon_census.py --list ruled          # slugs
    python3 src/RimMandrake/Utils/canon_census.py --list unruled
    python3 src/RimMandrake/Utils/canon_census.py --list non-conforming
    python3 src/RimMandrake/Utils/canon_census.py --lint                # exit 1
                                                                          # if any
                                                                          # non-
                                                                          # conforming

THE THREE BUCKETS (AGENT_BRIEF.md: "he rules only on ambiguity, deliberate
departures and contested regens" — an empty `## ruling` means canon stands
unopposed, NOT that the entry is broken)
====================================================================================
  * **ruled**          — the `## ruling` body contains a literal `**RULED**`
                          marker block.
  * **unruled**         — the body IS the known "not reviewed yet" boilerplate,
                          in any of its known wordings (measured 2026-09-17:
                          seven exact strings, varying only in "owner" vs "the
                          owner" and the noun — race/creature/species/chassis —
                          and one droid entry that appends an extra sentence
                          inside the same parens). `_BOILERPLATE_RE` matches all
                          of them by shape (`(empty …has not reviewed… )`)
                          rather than by an exact-string allowlist, so a new
                          wording (a new noun, a rephrase) still passes as long
                          as it keeps that shape. That is deliberate tolerance,
                          not sloppiness: the boilerplate's AUTHOR is the batch
                          agent writing new entries, not the owner, so its exact
                          words are not a fact worth pinning.
  * **non-conforming** — neither of the above: a genuinely blank body (`zeer`,
                          measured), or free-form prose with no `**RULED**`
                          marker (`gizka`, measured — a dated owner quote that
                          IS a real ruling, just not shaped like one).

⛔ NO "NEEDS RULING" HEURISTIC. This module never says an entry *should* be
ruled — only what shape its `## ruling` section currently has. Whether an
unruled entry deserves the owner's attention is his call, per AGENT_BRIEF.md.

THE GIZKA DECISION
===================
`gizka` carries a real ruling — a dated 2026-09-16 owner quote — but as free
prose with no `**RULED**` marker. Two readings compete:
  (a) count it as "ruled" anyway, because a human reading the file would call
      it a ruling;
  (b) count it as "non-conforming", because the CENSUS bucket for "ruled" is
      defined mechanically (marker present) and gizka's shape does not carry
      that marker.

**This module chooses (b).** `--lint` and the default census both classify
gizka as non-conforming, alongside `zeer`. Reasons:
  1. It keeps "ruled" a purely mechanical, marker-based test — the entire
     point of C8 is to stop a count from depending on a reader's judgment
     about what "counts as" a ruling. Any prose classifier sophisticated
     enough to recognize gizka's shape as "a real ruling" is exactly the kind
     of heuristic that produced the disputed "2" in the first place.
  2. It does not hide gizka. `--list non-conforming` surfaces it BY NAME, and
     a human (or CLAUDE.md) reading that list sees immediately that it is a
     real, dated ruling that simply never got the marker — a fact worth
     knowing, which a silent "ruled" bucket would bury.
  3. The lint's whole job is "assert every entry is one of the two known
     shapes" — a body that is real prose with no marker is, by that lint's own
     definition, the shape it exists to catch, precisely so a THIRD shape
     (like gizka's) cannot quietly multiply unnoticed.
So: **ruled=24, unruled=111, non-conforming=2** (gizka, zeer) is what this
tool prints. The "true" human-legible ruled count is 25 (24 marked + gizka's
prose ruling) — CLAUDE.md's corrected figure — and this module's report text
says so explicitly rather than folding it into the mechanical "ruled" bucket.

Stdlib only.
"""
import argparse
import os
import re
import sys

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DEFAULT_DIR = os.path.join(ROOT, "design", "RimStarWars", "canon_references")

RULED_MARKER = "**RULED**"

# Matches the "(empty — [the ]owner has not reviewed this <noun> yet[...])"
# boilerplate across all observed wordings (measured 2026-09-17: differs in
# "owner"/"the owner", the noun, and one entry with an extra trailing
# sentence still inside the parens). Bounded gaps so it does not swallow an
# arbitrarily long free-form ruling that merely happens to start with the
# word "empty".
_BOILERPLATE_RE = re.compile(
    r"^\(\s*empty\b.{0,220}?\bhas not reviewed\b.{0,220}\)$",
    re.IGNORECASE | re.DOTALL,
)

BUCKETS = ("ruled", "unruled", "non-conforming")


def ruling_body(text):
    """Return the stripped body of the `## ruling` section, or None if the
    entry carries no such heading at all (a shape this tool has never seen on
    the real corpus, but must not crash on)."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip() == "## ruling":
            start = i + 1
            break
    if start is None:
        return None
    end = start
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    return "\n".join(lines[start:end]).strip()


def classify(body):
    """(bucket, reason) for a ruling body. `body` is None means no `## ruling`
    heading was found at all — treated as non-conforming with its own reason
    so it is never silently absent from a report."""
    if body is None:
        return "non-conforming", "no `## ruling` heading found"
    if body == "":
        return "non-conforming", "`## ruling` body is genuinely blank"
    if RULED_MARKER in body:
        return "ruled", None
    if _BOILERPLATE_RE.match(body):
        return "unruled", None
    preview = body.replace("\n", " ").strip()
    if len(preview) > 70:
        preview = preview[:67] + "..."
    return "non-conforming", "free-form text with no %s marker: %r" % (RULED_MARKER, preview)


def find_entries(root_dir):
    """Sorted (slug, description_path) for every entry dir under root_dir
    that carries a description.md. Silently skips non-entry files/dirs
    (INDEX.md, gen_index.py, __pycache__, ...) — presence of description.md
    IS the definition of "is a canon entry", same test gen_index.py uses."""
    out = []
    if not os.path.isdir(root_dir):
        return out
    for name in sorted(os.listdir(root_dir)):
        entry_dir = os.path.join(root_dir, name)
        if not os.path.isdir(entry_dir):
            continue
        desc = os.path.join(entry_dir, "description.md")
        if os.path.isfile(desc):
            out.append((name, desc))
    return out


def census(root_dir):
    """-> dict[bucket] = list of (slug, reason_or_None), plus 'total'."""
    result = {b: [] for b in BUCKETS}
    for slug, desc_path in find_entries(root_dir):
        try:
            with open(desc_path, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError as exc:
            result["non-conforming"].append((slug, "could not read description.md: %s" % exc))
            continue
        body = ruling_body(text)
        bucket, reason = classify(body)
        result[bucket].append((slug, reason))
    result["total"] = sum(len(result[b]) for b in BUCKETS)
    return result


def render_report(result):
    lines = []
    lines.append("canon census — %d entries" % result["total"])
    for b in BUCKETS:
        lines.append("  %-14s %d" % (b + ":", len(result[b])))
    gizka_note = [s for s, _ in result["non-conforming"] if s == "gizka"]
    if gizka_note:
        lines.append("")
        lines.append(
            "  note: 'gizka' is counted non-conforming (free-form prose, no **RULED**\n"
            "  marker) but IS a real dated owner ruling — see --list non-conforming.\n"
            "  Human-legible ruled count including it: %d." % (len(result["ruled"]) + 1)
        )
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dir", default=DEFAULT_DIR,
                     help="canon_references directory to scan (default: %(default)s)")
    ap.add_argument("--list", choices=BUCKETS, help="list slugs in one bucket, one per line")
    ap.add_argument("--lint", action="store_true",
                     help="exit 1 if any entry is non-conforming (with reasons)")
    a = ap.parse_args()

    result = census(a.dir)

    if a.list:
        for slug, reason in result[a.list]:
            if reason:
                print("%s\t%s" % (slug, reason))
            else:
                print(slug)
        return 0

    if a.lint:
        bad = result["non-conforming"]
        if not bad:
            print("canon_census --lint: all %d entries are ruled or unruled boilerplate."
                  % result["total"])
            return 0
        print("canon_census --lint: %d non-conforming entr%s:"
              % (len(bad), "y" if len(bad) == 1 else "ies"))
        for slug, reason in bad:
            print("  %s: %s" % (slug, reason))
        return 1

    print(render_report(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
