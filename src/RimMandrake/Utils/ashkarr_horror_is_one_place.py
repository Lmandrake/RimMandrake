#!/usr/bin/env python3
"""HorrorWastes becomes ONE place: the cold nightside. Its warm band becomes Desert.

🔴 **The defect this closes.** Two owner rulings were each applied correctly and nobody
noticed they collided on the same biome:

  1. 2026-08-22 — *"HorrorWastes should be on the night-side where the ancient bioweapons
     have adapted to the extreme cold"*, narrowed to *"closer to the frozen side of the
     terminator, agreed taken from RockyCrags"*.
  2. 2026-08-23 00:16 — *"we will use HorrorWastes instead of RockyCrags for any tile
     above 0C"* (`eb7da875`, `ashkarr_warm_crags_to_horror.py`).

⇒ `HorrorWastes` ended up holding 807 tiles in TWO disjoint climates with a 20 °C hole
between them and no tile in the gap:

    cold  468 tiles  −74.9 … −33.9 °C   arc 125–171   elev median 753 m
    ⛔ gap   0 tiles  −20 …    0 °C
    warm  339 tiles    0.1 …  19.8 °C   arc  78–103   elev median  99 m

That is `AB_RockyCrags`' own hundred-degree-span defect inherited whole, which is why
`ROCKY_CRAGS_SPANS_HUNDRED_DEGREES_1` closed finding the carve had narrowed nothing.

🔑 **WHY THE COLD HALF KEEPS THE NAME, and the warm half does not.**
`ASHKARR_WORLD_DEFINITION.md` §6c is the owner's own two-class table: `HorrorWastes` is
**bioweapon class** — engineered life that adapted and is *still alive*, the danger is the
wildlife, and it is one of only four biomes licensed to cast anomaly entities. Ruling 1 is
a statement about that class. Ruling 2 was a **cleanup of `AB_RockyCrags`** — its purpose
was to get warm tiles OUT of a biome that made no sense at +19.8 °C, and `HorrorWastes` was
the destination reached for, not the subject being decided.

⇒ Honouring both means the warm tiles leave `AB_RockyCrags` (2) **and** `HorrorWastes` is
cold (1). They need a third home, and it must not be bioweapon-coded.

⭐ **`Desert` is that home, and it is measured, not chosen by taste.** The 339 are dry
(rain_mm median 0), low (99 m), and sit at arc 78–103. `Desert` on this planet already
spans −15.0 … +62.4 °C across arc 14–115 and **already holds 1,324 land tiles in the very
0–20 °C band these occupy**. They land inside a biome envelope this world already uses;
nothing new is asserted about the planet, and `Desert` needs no def change.

⛔ **NOT a generator.** One deterministic pass over the one map, two rules, no parameter to
sweep. `--apply` writes; without it nothing is touched. Reverting is `git checkout` of the
tiles CSV — the world after this pass differs from the world before it only in the `biome`
column of 339 rows.

    python3 src/RimMandrake/Utils/ashkarr_horror_is_one_place.py
    python3 src/RimMandrake/Utils/ashkarr_horror_is_one_place.py --apply
"""
from __future__ import annotations
import argparse, collections, csv, os, statistics as st, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
TILES = os.path.join(ROOT, 'world', 'ASHKARR_WORLDMAP_tiles.csv')

BIOME = 'HorrorWastes'
WARM_TO = 'Desert'
ABOVE_C = 0.0


def stats(rows, b):
    s = [float(r['temp_c']) for r in rows if r['biome'] == b]
    if not s:
        return f"{b:16s}     0 tiles"
    return (f"{b:16s} {len(s):5d} tiles · span {max(s)-min(s):5.1f} °C "
            f"({min(s):.1f} … {max(s):.1f}, median {st.median(s):.1f})")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    a = ap.parse_args()

    with open(TILES, encoding='utf-8') as fh:
        rd = csv.DictReader(fh)
        rows = list(rd)
        cols = rd.fieldnames

    moved = [r for r in rows if r['biome'] == BIOME and float(r['temp_c']) > ABOVE_C]
    if not moved:
        print(f"nothing to do: no {BIOME} tile is above {ABOVE_C:g} °C")
        return 0

    print("BEFORE")
    for b in (BIOME, WARM_TO):
        print("  " + stats(rows, b))

    for r in moved:
        r['biome'] = WARM_TO

    print(f"\n{len(moved)} tiles: {BIOME} -> {WARM_TO}  (temp > {ABOVE_C:g} °C)")
    print("  regions touched: " + ", ".join(
        f"{n} ({c})" for n, c in collections.Counter(r['region'] for r in moved).most_common(8)))

    print("\nAFTER")
    for b in (BIOME, WARM_TO):
        print("  " + stats(rows, b))

    # the point of the pass: HorrorWastes must come out ONE place, with no climate hole.
    hw = sorted(float(r['temp_c']) for r in rows if r['biome'] == BIOME)
    gaps = [(hw[i], hw[i+1]) for i in range(len(hw)-1) if hw[i+1] - hw[i] > 10.0]
    print(f"\n{BIOME} is now {len(hw)} tiles, {min(hw):.1f} … {max(hw):.1f} °C")
    print("  ✅ no climate hole wider than 10 °C" if not gaps
          else f"  🔴 STILL BIMODAL — holes at {gaps}")

    if not a.apply:
        print("\n(dry run — pass --apply to write)")
        return 0
    with open(TILES, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print(f"\nwrote {TILES}")
    print("⚠️ Now restamp the freeze:  python3 src/RimMandrake/Utils/verify_frozen.py "
          "--restamp world/ASHKARR_WORLDMAP_tiles.csv")
    return 0


if __name__ == '__main__':
    sys.exit(main())
