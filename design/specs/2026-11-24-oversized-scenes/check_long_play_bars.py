#!/usr/bin/env python3
"""Outcome check of RIMMANDRAKE_RULE_LONG_PLAY_BARS_TWENTY_ARE_CLEANSED.

The need: no bar named in long_play_bars.md still asks for long play (the rule
standing_rulings.md §Season-long play is play testing). A bar passes when
  - its long-play words are gone from its live sentence, or
  - the bar is gone (the Conductor deleted it), or
  - long_play_bars.md §The Conductor's rulings holds a row `| <mod> | <bar> | kept: <why> |`.

Exit 0: every bar passes. Exit 1: a bar still asks for long play (each is named).
Exit 2: could not look (a file is missing or unreadable).
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = Path(__file__).with_name("long_play_bars.md")

# mod, bar id, the long-play words in tree.json `experience` (from long_play_bars.md).
TREE_BARS = [
    ("Contagion", "walk_red_lid", "lived-in Contagion colony"),
    ("Graffiti", "stories_not_tax", "three in-game weeks"),
    ("Graffiti", "walk_lived_in", "walks a lived-in colony"),
    ("Pyrelands", "walk_season_on_the_pyre", "two weeks"),
    ("FlowWorks", "walk_moat_season", "through a season"),
    ("GimmeSomeSlack", "walk_scavenger_base", "about a week"),
    ("PyrelandsMechanics", "walk_tribes_season", "In ordinary play"),
    ("Cauldron", "cauldron_walk", "Returning still offers"),
    ("GelatinousSlime", "repeat_walk", "carry on with a prepared colony"),
    ("Stillsand", "stillsand_walk", "expedition and resupply loop"),
]

# mod, whole-bar id in cleanse/bars.json; the long-play sign is "season" in `says`.
CLEANSE_BARS = [
    ("Abyss", "B8"), ("BlueDesert", "B8"), ("Cauldron", "whole"), ("Contagion", "season"),
    ("CrackedLands", "B8"), ("FeverWood", "whole"), ("GelatinousSlime", "whole"),
    ("LanternDeeps", "B8"), ("LongShade", "B8"), ("Miasma", "B9"), ("RustCathedral", "B7"),
    ("SleepingIce", "B8"), ("Stillsand", "B_WHOLE"), ("TerminalBiomes", "B8"),
    ("TheForge", "B8"), ("TheRot", "B7"), ("Warscar", "W9"), ("Wastes", "B8"),
    ("Webwork", "B8"), ("WeepingStones", "B9"),
]


def kept_rows(text):
    """(mod, bar) pairs that the Conductor's rulings section records as kept."""
    m = re.search(r"^## The Conductor's rulings\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not m:
        return set()
    out = set()
    for line in m.group(1).splitlines():
        cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
        if len(cells) >= 3 and cells[2].lower().startswith("kept:") and len(cells[2]) > 10:
            out.add((cells[0].split(" ")[0], cells[1]))
    return out


def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"COULD NOT LOOK: {path.relative_to(ROOT)}: {e}")
        sys.exit(2)


def main():
    try:
        kept = kept_rows(TABLE.read_text(encoding="utf-8"))
    except OSError as e:
        print(f"COULD NOT LOOK: {TABLE}: {e}")
        return 2
    still = []
    for mod, bar, words in TREE_BARS:
        leaves = load(ROOT / "design/concepts" / mod / "tree.json").get("leaves")
        if not isinstance(leaves, list):
            print(f"COULD NOT LOOK: {mod}/tree.json has no leaves list")
            return 2
        leaf = next((l for l in leaves if isinstance(l, dict) and l.get("id") == bar), None)
        if leaf and words.lower() in str(leaf.get("experience", "")).lower() and (mod, bar) not in kept:
            still.append(f"{mod} tree.json {bar}: still says {words!r}")
    for mod, bar in CLEANSE_BARS:
        data = load(ROOT / "design/concepts" / mod / "cleanse/bars.json")
        bars = data if isinstance(data, list) else data.get("bars")
        if not isinstance(bars, list):
            print(f"COULD NOT LOOK: {mod}/cleanse/bars.json has no bars list")
            return 2
        row = next((b for b in bars if isinstance(b, dict) and b.get("id") == bar), None)
        if row and re.search(r"season", str(row.get("says", "")), re.I) and (mod, bar) not in kept:
            still.append(f"{mod} cleanse/bars.json {bar}: `says` still names a season")
    n = len(TREE_BARS) + len(CLEANSE_BARS)
    if still:
        print(f"FAIL: {len(still)} of {n} bars still ask for long play")
        print("\n".join("  " + s for s in still))
        return 1
    print(f"PASS: none of the {n} bars asks for long play (cut, deleted or kept by ruling)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
