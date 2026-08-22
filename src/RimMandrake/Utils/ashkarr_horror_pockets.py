#!/usr/bin/env python3
"""Break the HorrorWastes polar cap into isolated pockets inside the Crags.

Owner, 2026-08-22: "the horror wastes should just be isolated pockets within the Crags in
the darkside."

It was placed as the coldest 1,200 contiguous tiles (arc 145-179) - one solid cap, which
reads as a second polar region rather than as contamination. Bioweapon ground should be
FOUND, not crossed.

⛔ Deterministic: seeds are chosen by an even stride over the cold-sorted candidates with a
minimum separation, then grown by proximity. No RNG.
"""
import argparse, csv, math, os, collections

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
TILES = os.path.join(ROOT, 'world', 'ASHKARR_WORLDMAP_tiles.csv')
HOST = 'AB_RockyCrags'

def xyz(r):
    la, lo = math.radians(float(r['lat'])), math.radians(float(r['lon']))
    return (math.cos(la)*math.cos(lo), math.cos(la)*math.sin(lo), math.sin(la))

def sep(a, b):
    return math.degrees(math.acos(max(-1, min(1, sum(x*y for x, y in zip(a, b))))))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--pockets', type=int, default=16)
    ap.add_argument('--size', type=int, default=28, help='tiles per pocket')
    ap.add_argument('--min-sep', type=float, default=9.0, help='degrees between pocket centres')
    ap.add_argument('--dark-arc', type=float, default=125.0, help='darkside starts here')
    a = ap.parse_args()

    with open(TILES, encoding='utf-8') as f:
        rd = csv.DictReader(f); tiles = list(rd); cols = rd.fieldnames
    X = {r['tile']: xyz(r) for r in tiles}

    # everything currently HorrorWastes goes home first; pockets are then re-cut from the
    # combined pool so a re-run with different numbers is idempotent, not cumulative.
    for r in tiles:
        if r['biome'] == 'HorrorWastes':
            r['biome'] = HOST
    pool = [r for r in tiles if r['biome'] == HOST and float(r['arc']) >= a.dark_arc]
    pool.sort(key=lambda r: float(r['temp_c']))          # coldest first
    print(f"candidate pool ({HOST} at arc >= {a.dark_arc}): {len(pool)}, "
          f"temp {float(pool[0]['temp_c']):.0f}..{float(pool[-1]['temp_c']):.0f}")

    # ⚠️ Seeding coldest-first put all 16 pockets at arc 151-179 - one polar cluster wearing
    # the word "pockets". Seed by an even stride around BEARING instead, so the pockets are
    # distributed around the dark hemisphere rather than piled at its pole.
    ring = sorted(pool, key=lambda r: (float(r['bearing']), float(r['arc'])))
    seeds = []
    stride = max(1, len(ring) // (a.pockets * 3))
    for i in range(0, len(ring), stride):
        r = ring[i]
        if len(seeds) >= a.pockets: break
        if all(sep(X[r['tile']], X[s['tile']]) >= a.min_sep for s in seeds):
            seeds.append(r)
    print(f"seeds placed: {len(seeds)} (min separation {a.min_sep} deg)")

    taken = set()
    for s in seeds:
        near = sorted(pool, key=lambda r: sep(X[s['tile']], X[r['tile']]))
        got = 0
        for r in near:
            if r['tile'] in taken: continue
            r['biome'] = 'HorrorWastes'; taken.add(r['tile']); got += 1
            if got >= a.size: break

    c = collections.Counter(r['biome'] for r in tiles)
    print(f"\nHorrorWastes {c['HorrorWastes']} tiles in {len(seeds)} pockets   {HOST} {c[HOST]}")
    hw = [r for r in tiles if r['biome'] == 'HorrorWastes']
    if hw:
        ts = [float(r['temp_c']) for r in hw]
        arcs = [float(r['arc']) for r in hw]
        print(f"  temp {min(ts):.0f}..{max(ts):.0f}   arc {min(arcs):.0f}..{max(arcs):.0f}")
    if not a.apply:
        print("\nDRY RUN - nothing written. Re-run with --apply")
        return
    with open(TILES, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(tiles)
    print(f"WROTE {TILES}")

if __name__ == '__main__':
    main()
