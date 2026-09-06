#!/usr/bin/env python3
"""Zone the arid family by distance to water, and mark the dried seabeds as salt plains.

Owner, 2026-08-22, looking at the render: "I think you shrank the Twilight Sea into...
desert? ... much of that arid shrubland should be desert and the arid shrubland should be
moved to be near the shrunk twilight sea, right? ... Do we not have a salt flat?"

He is right on both. A retreating sea leaves PLAYA, not dunes, and the map had no zonation
at all - AridShrubland was scattered uniformly, so the shore looked like five hops inland.

⛔ NOT a generator. One deterministic pass over the one map. --apply writes.

🔴 Why this is distance-driven and not rainfall-driven, which was the first attempt:
   `rain_mm` is exactly 0 on 7,664 of the 8,231 arid tiles. There is no gradient to rank by.
   And distance ALONE, applied to every tile, collapses 7,726 of them into ExtremeDesert -
   that is erasure, not zonation. So this only moves the FRINGE and the tiles stranded
   away from it; the deep waste is left alone.
"""
import argparse, csv, math, os, collections

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
W = os.path.join(ROOT, 'world')
TILES = os.path.join(W, 'ASHKARR_WORLDMAP_tiles.csv')
LINKS = os.path.join(W, 'ASHKARR_WORLDMAP_links.csv')
MUTS  = os.path.join(W, 'ASHKARR_WORLDMAP_mutators.csv')

WET = {'Ocean', 'Lake', 'SeaIce'}
ARID = {'ExtremeDesert', 'Desert', 'AridShrubland'}
SALT_MUTATOR = 'VEE_SaltPlains'      # "The dried surface of an inland ocean."

def xyz(r):
    la, lo = math.radians(float(r['lat'])), math.radians(float(r['lon']))
    return (math.cos(la)*math.cos(lo), math.cos(la)*math.sin(lo), math.sin(la))

def sep(a, b):
    return math.degrees(math.acos(max(-1, min(1, sum(x*y for x, y in zip(a, b))))))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--fringe', type=float, default=8.0,
                    help='degrees from a SEA that count as fringe (tile spacing ~1.44)')
    ap.add_argument('--river-fringe', type=float, default=3.5,
                    help='degrees from a RIVER. Kept SHORTER than the sea fringe on purpose: '
                         'with one shared threshold the rivers took 439 of the 665 shrubland '
                         'tiles and the coasts got 226, so the sea looked bare - which is '
                         'exactly what the owner saw on the render.')
    a = ap.parse_args()

    with open(TILES, encoding='utf-8') as f:
        rd = csv.DictReader(f); tiles = list(rd); cols = rd.fieldnames
    X = {r['tile']: xyz(r) for r in tiles}
    P = {r['tile']: r for r in tiles}

    wet = [X[r['tile']] for r in tiles if r['biome'] in WET]
    riv = set()
    for l in csv.DictReader(open(LINKS, encoding='utf-8')):
        if l['kind'] == 'river':
            riv.add(l['a']); riv.add(l['b'])
    rivpts = [X[t] for t in riv if t in X]

    # 🔴 A DRIED SEABED IS NOT A FRINGE. Running the fringe first put 281 seabed tiles into
    # AridShrubland and then dropped VEE_SaltPlains on top - "vegetated fringe with a sterile
    # salt-plain surface", which is a contradiction. A playa is bare. Seabed tiles are the one
    # place NEAR water that must not be vegetated, so they are excluded here and forced to the
    # sterile biome below.
    SEABED_REGIONS = ('Twilight Sea', 'Grey Sea')
    seabed = [r for r in tiles if r['biome'] not in WET and r.get('region') in SEABED_REGIONS]

    moves = collections.Counter()
    for r in seabed:
        if r['biome'] != 'ExtremeDesert':
            moves[f"{r['biome']} -> ExtremeDesert (bare seabed)"] += 1
            r['biome'] = 'ExtremeDesert'
    seabed_ids = {r['tile'] for r in seabed}

    for r in tiles:
        if r['biome'] not in ARID or r['tile'] in seabed_ids:
            continue
        dw = min(sep(X[r['tile']], p) for p in wet)
        dr = min(sep(X[r['tile']], p) for p in rivpts) if rivpts else 1e9
        fringe = (dw <= a.fringe) or (dr <= a.river_fringe)
        if fringe and r['biome'] != 'AridShrubland':
            moves[f"{r['biome']} -> AridShrubland (fringe)"] += 1
            r['biome'] = 'AridShrubland'
        elif not fringe and r['biome'] == 'AridShrubland':
            moves['AridShrubland -> Desert (stranded inland)'] += 1
            r['biome'] = 'Desert'

    # ---- the dried seabeds become salt plains ------------------------------------
    # A tile is dried seabed if it is land NOW but belongs to a sea region. The region
    # column survives the biome change, which is what makes this identifiable at all.
    mut = {r['tile']: r['mutators'] for r in csv.DictReader(open(MUTS, encoding='utf-8'))}
    salted = 0
    for r in tiles:
        if r['biome'] in WET:
            continue
        if r.get('region') not in ('Twilight Sea', 'Grey Sea'):
            continue
        cur = mut.get(r['tile'], '')
        if SALT_MUTATOR in cur:
            continue
        mut[r['tile']] = (cur + ';' + SALT_MUTATOR).lstrip(';')
        salted += 1

    print(f"fringe threshold {a.fringe} deg (~{a.fringe/1.44:.1f} tiles)")
    for k, v in moves.most_common():
        print(f"  {v:5}  {k}")
    print(f"  {salted:5}  dried seabed tiles marked {SALT_MUTATOR}")
    c = collections.Counter(r['biome'] for r in tiles)
    print(f"\n  AridShrubland {c['AridShrubland']}   Desert {c['Desert']}   ExtremeDesert {c['ExtremeDesert']}")

    if not a.apply:
        print("\nDRY RUN - nothing written. Re-run with --apply")
        return
    with open(TILES, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(tiles)
    with open(MUTS, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(['tile', 'mutators'])
        for t in sorted(mut, key=int):
            if mut[t]: w.writerow([t, mut[t]])
    print(f"\nWROTE {TILES}\nWROTE {MUTS}")
    print("⚠️ Now restamp the freeze:  python3 src/RimMandrake/Utils/verify_frozen.py "
          "--restamp world/ASHKARR_WORLDMAP_tiles.csv")

if __name__ == '__main__':
    main()
