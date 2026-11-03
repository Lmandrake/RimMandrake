#!/usr/bin/env python3
"""landmark_names_check.py - exit 0 when the canonical start save's landmark names hold.

Checks, on the save canon.yml names (planet.start_savegame) in the live Saves folder AND its
repo copy under world/: the two are byte-identical; no landmark name is held by two landmarks;
tile 2403's RUT_GapingDoom is named "The Gaping Doom"; every row of
world/ASHKARR_R3_landmark_renames_2026-11-03.json reads back with its new name.
A save that cannot be found fails (exit 1), never passes. LANDMARK_NAMING_PASS_1.
"""
import argparse
import collections
import hashlib
import json
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
from canon_save import start_savegame_name  # noqa: E402
from landmark_rename_save import read_landmarks  # noqa: E402

SAVES = "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Saves"
RENAMES = os.path.join(REPO, "world", "ASHKARR_R3_landmark_renames_2026-11-03.json")


def check_text(text, renames):
    """List of failure strings (empty = pass) and the row count."""
    rows = read_landmarks(text)
    fails = []
    # second instrument: a real XML parse must see the same (def, name) list the text reader saw
    inner = ET.fromstring(text.encode("utf-8")).find(".//landmarks/landmarks")
    parsed = [] if inner is None else [(v.findtext("def"), v.findtext("name")) for v in inner.find("values")]
    if parsed != [(r["def"], r["name"]) for r in rows]:
        fails.append(f"XML parse ({len(parsed)} landmarks) disagrees with the text reader ({len(rows)})")
    counts = collections.Counter(r["name"] for r in rows)
    for n, c in sorted(counts.items()):
        if c > 1:
            fails.append(f"name {n!r} held by {c} landmarks: "
                         + ", ".join(str(r["tile"]) for r in rows if r["name"] == n))
    by = collections.defaultdict(list)
    for r in rows:
        by[(r["tile"], r["def"])].append(r["name"])
    for rn in [{"tile": 2403, "def": "RUT_GapingDoom", "new": "The Gaping Doom"}] + list(renames):
        got = by.get((rn["tile"], rn["def"]), [])
        if got != [rn["new"]]:
            fails.append(f"tile {rn['tile']} {rn['def']}: {got!r}, want exactly [{rn['new']!r}]")
    return fails, len(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--saves", default=SAVES)
    ap.add_argument("--repo-only", action="store_true", help="skip the live Saves copy")
    a = ap.parse_args(argv)
    name = start_savegame_name()
    paths = [os.path.join(REPO, "world", name)]
    if not a.repo_only:
        paths.append(os.path.join(a.saves, name))
    renames = json.load(open(RENAMES, encoding="utf-8"))["renames"]
    ok, digests = True, set()
    for p in paths:
        if not os.path.isfile(p):
            print(f"FAIL {p}: missing")
            ok = False
            continue
        raw = open(p, "rb").read()
        digests.add(hashlib.sha256(raw).hexdigest())
        fails, n = check_text(raw.decode("utf-8"), renames)
        print(f"{'PASS' if not fails else 'FAIL'} {p}: {n} landmarks, {len(renames)} renames, "
              f"{len(fails)} failures")
        for f in fails[:40]:
            print("  " + f)
        ok = ok and not fails and n > 0
    if len(digests) > 1:
        print("FAIL: Saves copy and repo copy differ")
        ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
