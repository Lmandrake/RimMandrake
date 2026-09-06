#!/usr/bin/env python3
"""check_config_errors.py — is a Player.log's Config-error/cross-reference
crowd the SAME crowd, or does it hold something new?

LOAD_CONFIG_ERROR_SWEEP_1's whole point was a frozen baseline so a genuinely
NEW `Config error in ...` or `Could not resolve cross-reference` line becomes
visible instead of hiding in a total that happens to still add up. A bare
LINE COUNT cannot do that: nine third-party sign errors disappearing and two
new ones appearing elsewhere can net to the same number and print "ok".

This is the command that replaces "remember to read the .txt and diff it by
eye": it reads a Player.log, extracts every Config-error/cross-reference line
the same way harvest_log.py does (grouped by message, not raw `grep -c`), and
matches each DISTINCT line against `infrastructure/state/facts/config_error_baseline_*.json`
(newest wins). Anything not in the baseline prints loud and fails the exit
code; a baseline entry marked "fixed" that reappears is a regression and also
fails.

    python3 src/RimMandrake/Utils/check_config_errors.py                  # live Player.log
    python3 src/RimMandrake/Utils/check_config_errors.py --log <path>     # a saved copy
    python3 src/RimMandrake/Utils/check_config_errors.py --baseline <path.json>

Exit codes: 0 nothing outside the baseline and no regression; 1 a NEW line or
a regression was found; 2 the log or baseline could not be read (UNMEASURED,
not a finding — see the printed reason).

⚠️ This does not replace harvest_log.py's freshness gate (mod-count vs
ModsConfig.xml, exit marker). Run that first if you need to know whether the
log is CURRENT; this script only diffs message content against the baseline,
on whatever log you hand it.
"""
from __future__ import annotations
import argparse
import glob
import json
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from game_paths import PLAYER_LOG                                    # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
FACTS_DIR = os.path.join(ROOT, "infrastructure", "state", "facts")

CONFIGERR_RX = re.compile(r"Config error in |Exception in ConfigErrors\(\) of ")
CROSSREF_RX = re.compile(r"Could not resolve cross-reference")


def newest_baseline() -> str | None:
    cands = sorted(glob.glob(os.path.join(FACTS_DIR, "config_error_baseline_*.json")))
    return cands[-1] if cands else None


def extract(path: str) -> list[str]:
    """Every Config-error/cross-reference line, message text only.

    Matches harvest_log.py's CHECKS regexes so the two instruments never
    silently diverge on WHAT counts as a hit.
    """
    hits = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            s = raw.rstrip("\n").strip()
            if CONFIGERR_RX.search(s) or CROSSREF_RX.search(s):
                hits.append(s)
    return hits


def classify(line: str, entries: list[dict]) -> dict | None:
    """First baseline entry whose pattern occurs in this line.

    Substring, not equality: the 2026-09-03 baseline's own cross-reference
    lines are themselves truncated captures, and a message occasionally wraps
    with different trailing punctuation across engine versions. A literal
    pattern occurring inside the real line is still an honest match; it is
    not a wildcard, so it cannot match something it was not written for.
    """
    for e in entries:
        if e["pattern"] in line:
            return e
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--log", default=PLAYER_LOG, help="Player.log to check (default: live)")
    ap.add_argument("--baseline", default=None, help="baseline JSON (default: newest in facts/)")
    a = ap.parse_args()

    if not os.path.exists(a.log):
        print(f"UNMEASURED no log at {a.log}")
        return 2

    baseline_path = a.baseline or newest_baseline()
    if not baseline_path or not os.path.exists(baseline_path):
        print(f"UNMEASURED no config_error_baseline_*.json under {FACTS_DIR}")
        return 2

    baseline = json.load(open(baseline_path, encoding="utf-8"))
    entries = baseline["entries"]

    hits = extract(a.log)
    counts = Counter(hits)

    print(f"log       {a.log}")
    print(f"baseline  {baseline_path}")
    print(f"lines     {len(hits)} total, {len(counts)} distinct\n")

    by_class: dict[str, list[tuple[str, int, dict]]] = {}
    new_lines: list[tuple[str, int]] = []
    for line, n in sorted(counts.items()):
        entry = classify(line, entries)
        if entry is None:
            new_lines.append((line, n))
        else:
            by_class.setdefault(entry["class"], []).append((line, n, entry))

    for cls in sorted(by_class):
        items = by_class[cls]
        total = sum(n for _, n, _ in items)
        print(f"  known [{cls}]: {len(items)} distinct line(s), {total} occurrence(s)")

    regressions = by_class.get("third-party-fixed", []) + \
        [it for it in by_class.get("third-party-absent", []) if it[1] > 0]

    if new_lines:
        print(f"\n\U0001F534 NEW — not in {os.path.basename(baseline_path)} "
              f"({len(new_lines)} distinct):")
        for line, n in new_lines:
            print(f"   x{n}  {line}")
    else:
        print("\nno lines outside the baseline")

    if regressions:
        print(f"\n⚠️  REGRESSION — baseline says this was fixed/absent, "
              f"but it's back ({len(regressions)}):")
        for line, n, entry in regressions:
            print(f"   x{n}  {line}\n        ({entry['note']})")

    ok = not new_lines and not regressions
    print(f"\n{'CLEAN' if ok else 'NOT CLEAN'} against {os.path.basename(baseline_path)}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
