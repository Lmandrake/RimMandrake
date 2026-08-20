#!/usr/bin/env python3
"""Find every place a superseded instruction is still written down.

A ruling is only as good as its propagation. This sweeps the files that carry
STANDING DIRECTIVES -- run sheets, queues, scope tables, specs, agent roles --
for a phrase someone would act on, and separates hits that read as live
instructions from hits that read as historical record.

It does not judge. It builds the list you would otherwise have to remember to
build, so the judging is yours and none of it is missed.

    python3 stale_directives.py "mechanoids off"
    python3 stale_directives.py --regex "deploy.*Jawa_Patches" --root /path/to/repo
    python3 stale_directives.py "cherrypick" --all-md      # widen beyond defaults

Exit codes:  0 = no hits   1 = hits found (so it can gate a commit hook)
"""
import argparse
import os
import re
import sys

# Directive-bearing paths, most dangerous first. A hit in a run sheet is read for
# EXECUTION; a hit in a design spec is read for reference. Both matter, not equally.
DEFAULT_GLOBS = [
    ("run sheet", ("NEXT_RELOAD.md", "WORLDGEN_RUN.md", "RUN.md", "RUNBOOK.md")),
    ("queue",     ("queue/",)),
    ("scope",     ("V1.md", "V1_CHAIN.md", "V2_DREAMS.md", "ROADMAP.md", "SCOPE.md")),
    ("agent role", ("agents/", "CLAUDE.md", "POLICY.md", "AGENTS.md")),
    ("state",     ("infrastructure/state/",)),
    ("spec",      ("design/", "specs/")),
]

# Lines that read as an ORDER rather than a note. Deliberately broad: a false
# positive costs a glance, a false negative costs the thing this script exists for.
IMPERATIVE = re.compile(
    r"(?:^|[\s|*_`>-])(?:"
    r"do not|don't|never|always|must|should|shall|"
    r"deploy|disable|enable|remove|delete|cut|strip|turn (?:on|off)|"
    r"set |write |run |add |pin |untick|switch|ensure|make sure|required"
    r")\b", re.I)

# Lines that read as a RECORD of something already settled or already reversed.
HISTORICAL = re.compile(
    r"(?:~~|⛔|✅|\bdead\b|\bstruck\b|\bsuperseded\b|\breversed\b|\bclosed\b|"
    r"\bdropped\b|\bused to\b|\bno longer\b|\bwas wrong\b|\bstale\b|\bDEPRECATED\b|"
    r"\bformer\b|\bobsolete\b)", re.I)

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "observed"}


def classify(line):
    """live | record | mention -- a hint for the reader, not a verdict."""
    hist = bool(HISTORICAL.search(line))
    imp = bool(IMPERATIVE.search(line))
    if hist and imp:
        return "record"      # an order wrapped in a strike: already handled
    if hist:
        return "record"
    if imp:
        return "live"        # <-- these are the ones that bite
    return "mention"


def category_of(relpath):
    norm = relpath.replace(os.sep, "/")
    for label, needles in DEFAULT_GLOBS:
        for n in needles:
            if n.endswith("/"):
                if ("/" + norm).find("/" + n) >= 0:
                    return label
            elif norm.endswith(n):
                return label
    return None


def walk(root, all_md):
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS and not d.startswith(".")]
        for f in fn:
            if not f.endswith(".md"):
                continue
            full = os.path.join(dp, f)
            rel = os.path.relpath(full, root)
            cat = category_of(rel)
            if cat or all_md:
                yield full, rel, (cat or "other")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pattern", help="phrase someone would ACT on, e.g. 'mechanoids off'")
    ap.add_argument("--root", default=".", help="repo root (default: cwd)")
    ap.add_argument("--regex", action="store_true", help="treat pattern as a regex")
    ap.add_argument("--all-md", action="store_true",
                    help="search every .md, not only directive-bearing paths")
    ap.add_argument("--live-only", action="store_true",
                    help="show only lines that read as live instructions")
    a = ap.parse_args()

    try:
        rx = re.compile(a.pattern if a.regex else re.escape(a.pattern), re.I)
    except re.error as e:
        sys.exit("bad regex: %s" % e)

    order = [lbl for lbl, _ in DEFAULT_GLOBS] + ["other"]
    buckets = {k: [] for k in order}
    counts = {"live": 0, "record": 0, "mention": 0}

    for full, rel, cat in walk(a.root, a.all_md):
        try:
            with open(full, encoding="utf-8", errors="replace") as fh:
                lines = fh.readlines()
        except OSError:
            continue
        for i, line in enumerate(lines, 1):
            if not rx.search(line):
                continue
            kind = classify(line)
            if a.live_only and kind != "live":
                continue
            counts[kind] += 1
            buckets.setdefault(cat, []).append((rel, i, kind, line.strip()))

    total = sum(len(v) for v in buckets.values())
    if not total:
        print("no hits for %r -- nothing still says it" % a.pattern)
        return 0

    MARK = {"live": "🔴 LIVE   ", "record": "   record", "mention": "   mention"}
    for cat in order:
        hits = buckets.get(cat) or []
        if not hits:
            continue
        print("\n=== %s ===" % cat.upper())
        for rel, ln, kind, text in hits:
            if len(text) > 150:
                text = text[:147] + "..."
            print("  %s  %s:%d" % (MARK[kind], rel, ln))
            print("             %s" % text)

    print("\n%d hit(s): %d live, %d record, %d mention"
          % (total, counts["live"], counts["record"], counts["mention"]))
    if counts["live"]:
        print("\n🔴 The LIVE lines are the ones an agent would act on. Each needs to be")
        print("   struck with its reason, or confirmed as still correct.")
        print("   Striking beats deleting: deleted text leaves its evidence behind,")
        print("   and the next reader reconstructs the thing you killed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
