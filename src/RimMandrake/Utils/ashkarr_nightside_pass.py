#!/usr/bin/env python3
"""ONE combined edit to THE map. Five owner rulings from 2026-08-22, applied together
because they touch the same ground and cannot be judged separately.

  E1  halve the meridian water, shrinking from the margins inward
  E2  leave a Dead-Sea brine halo of small remnants around the Grey Sea
  E3  freeze the sub-freezing ocean into SeaIce
  E4  place HorrorWastes on the deep nightside, carved from AB_RockyCrags
  E5  scatter ancient-ice pools in the deep-nightside lowlands, sharing with the propane

⛔ This is NOT a generator. It edits the one map in place, once, deterministically.
   There is no seed sweep and no parameter that could produce a different planet.
   `--apply` writes; without it nothing is touched.

🔑 Why the freeze is justified: liquid water in this bundle is clamped at -2.0 C (213
tiles sit exactly there) while the LAND beside it at arc 120-130 reads -32 C. The clamp is
correct for liquid seawater, which cannot go below its own freezing point. Those tiles read
-2 only because the model still calls them liquid.
"""
import argparse, csv, math, os, sys, collections
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
TILES = os.path.join(ROOT, 'world', 'ASHKARR_WORLDMAP_tiles.csv')

MERIDIAN_ARC   = 82      # beyond this is "meridian" per ASHKARR_WORLD_DEFINITION s5
DEEP_NIGHT_ARC = 140
HALVE_TO       = 0.50    # owner: "shrink the meridian water bodies to around half"
BRINE_KEEP     = 0.12    # of the tiles the halving removes, this fraction stay as brine
HORROR_TILES   = 1200    # DECIDE's proposal; owner to adjust after looking
ICE_POOL_TILES = 80      # "small pools ... not a vast icy body"
GREY_SEA       = (92.0, 8.0)   # arc, bearing - the gazetteer entry

def load():
    with open(TILES, encoding='utf-8') as f:
        r = csv.DictReader(f)
        return list(r), r.fieldnames

def fnum(x, d=0.0):
    try: return float(x)
    except (TypeError, ValueError): return d

def angdist(a1, b1, a2, b2):
    """Rough angular separation using arc as colatitude and bearing as longitude."""
    p1, p2 = math.radians(90 - a1), math.radians(90 - a2)
    dl = math.radians(b1 - b2)
    v = math.sin(p1)*math.sin(p2) + math.cos(p1)*math.cos(p2)*math.cos(dl)
    return math.degrees(math.acos(max(-1, min(1, v))))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true', help='write the file; default is a dry run')
    a = ap.parse_args()

    rows, cols = load()
    for r in rows:
        r['_arc'] = fnum(r['arc']); r['_el'] = fnum(r['elev_m']); r['_t'] = fnum(r['temp_c'])
        r['_bear'] = fnum(r['bearing'])
    before = collections.Counter(r['biome'] for r in rows)
    changes = collections.Counter()

    # ---- E3 FREEZE FIRST -----------------------------------------------------------
    # Order matters and this used to be last. Ice PERSISTS; liquid sublimates. Freezing
    # after the halving dried 116 cold tiles that should have survived as ice, and left
    # only 157 SeaIce instead of 273.
    for r in rows:
        if r['biome'] in ('Ocean', 'Lake') and r['_t'] <= 0.0:
            r['biome'] = 'SeaIce'
            changes['E3 sub-freezing water -> SeaIce'] += 1

    # ---- E1/E2 operate on what is still LIQUID -------------------------------------
    # 🔴 The Scald is a ruled feature (312 Lake tiles, region "Scald", all at arc <= 82).
    # It is outside the meridian so the halving never reaches it - this guard makes that
    # explicit rather than incidental, so a later change to MERIDIAN_ARC cannot eat it.
    water = [r for r in rows if r['biome'] in ('Ocean', 'Lake')
             and r.get('region') != 'Scald']
    mer_water = [r for r in water if r['_arc'] > MERIDIAN_ARC]

    # ---- E1 halve the meridian water --------------------------------------------
    # 🔴 THE TWO SEAS SHRINK DIFFERENTLY - owner, 2026-08-22: "The Twilight Sea should not
    # have the dithered 'dessicating' terrain we just added, only the Grey sea should. It
    # simply needed its volume reduced."
    #
    # The first version ranked ALL meridian water by elevation and dried the top slice.
    # On a noisy seabed that is salt-and-pepper, not a retreating shoreline - it dithered
    # the Twilight Sea. Elevation rank is a depth proxy, not a geometry.
    #
    #   TWILIGHT SEA -> shoreline EROSION. Rank by distance to the nearest non-water tile
    #                   and remove the closest first. The sea retreats inward with a clean
    #                   edge, which is what "simply reduce its volume" means.
    #   GREY SEA     -> unchanged: elevation-ranked drying PLUS a scattered brine halo,
    #                   because that one is meant to read as desiccating.
    import math as _m
    def _xyz(r):
        la, lo = _m.radians(fnum(r['lat'])), _m.radians(fnum(r['lon']))
        return (_m.cos(la)*_m.cos(lo), _m.cos(la)*_m.sin(lo), _m.sin(la))
    def _sep(a, b):
        return _m.degrees(_m.acos(max(-1, min(1, sum(x*y for x, y in zip(a, b))))))

    twilight = [r for r in mer_water if r.get('region') == 'Twilight Sea']
    other    = [r for r in mer_water if r.get('region') != 'Twilight Sea']

    removed = []
    if twilight:
        wet_ids = {r['tile'] for r in rows if r['biome'] in ('Ocean', 'Lake', 'SeaIce')}
        dry_pts = [_xyz(r) for r in rows if r['tile'] not in wet_ids]
        for r in twilight:
            p = _xyz(r)
            r['_shore'] = min(_sep(p, q) for q in dry_pts)
        twilight.sort(key=lambda r: r['_shore'])          # nearest the shore goes first
        removed += twilight[:int(round(len(twilight) * (1 - HALVE_TO)))]

    other.sort(key=lambda r: -r['_el'])
    grey_removed = other[:int(round(len(other) * (1 - HALVE_TO)))]
    removed += grey_removed

    # ---- E2 brine halo, GREY SEA ONLY --------------------------------------------
    grey_removed.sort(key=lambda r: angdist(r['_arc'], r['_bear'], *GREY_SEA))
    n_brine = int(round(len(grey_removed) * BRINE_KEEP))
    near = grey_removed[:max(n_brine * 4, n_brine)]
    step = max(1, len(near) // max(n_brine, 1))
    brine = {id(r) for r in near[::step][:n_brine]}

    for r in removed:
        if id(r) in brine:
            changes['E2 brine remnant kept as water'] += 1      # stays Ocean/Lake, stays wet
            continue
        # dry it out: a tile is water because elevation <= 0, so it must RISE
        r['elev_m'] = f"{max(1.0, r['_el'] + 12.0):.1f}"
        r['biome'] = 'ExtremeDesert' if r['_t'] > 0 else 'AB_RockyCrags'
        r['water'] = '0'
        changes['E1 meridian water dried'] += 1

    # ---- E4 HorrorWastes on the deep nightside ------------------------------------
    cand = [r for r in rows if r['biome'] == 'AB_RockyCrags' and r['_arc'] >= DEEP_NIGHT_ARC]
    cand.sort(key=lambda r: r['_t'])            # coldest first
    for r in cand[:HORROR_TILES]:
        r['biome'] = 'HorrorWastes'
        changes['E4 RockyCrags -> HorrorWastes'] += 1

    # ---- E5 ancient-ice pools in the deep-nightside lowlands ----------------------
    # Owner: they SHARE the lowlands with AB_PropaneLakes. Draw only from what is left
    # of AB_RockyCrags, take the lowest, and scatter rather than pool them together.
    low = [r for r in rows if r['biome'] == 'AB_RockyCrags' and r['_arc'] >= DEEP_NIGHT_ARC]
    low.sort(key=lambda r: r['_el'])
    pool_src = low[:ICE_POOL_TILES * 3]
    step = max(1, len(pool_src) // max(ICE_POOL_TILES, 1))
    for r in pool_src[::step][:ICE_POOL_TILES]:
        r['biome'] = 'SeaIce'
        changes['E5 lowland ancient-ice pools'] += 1

    after = collections.Counter(r['biome'] for r in rows)
    print("EDITS")
    for k, v in sorted(changes.items()):
        print(f"  {v:6}  {k}")
    print("\nBIOME DELTA")
    for b in sorted(set(before) | set(after)):
        if before[b] != after[b]:
            print(f"  {before[b]:6} -> {after[b]:6}  {b}")
    wnow = sum(1 for r in rows if r['biome'] in ('Ocean', 'Lake'))
    ice  = sum(1 for r in rows if r['biome'] == 'SeaIce')
    print(f"\nwater: liquid {sum(1 for r in rows if r['biome'] in ('Ocean','Lake'))} "
          f"+ SeaIce {ice} = {wnow + ice}  ({100*(wnow+ice)/len(rows):.2f}% of {len(rows)} tiles)")
    print(f"  was 1780 = 8.14%  -- canon.yml planet.water_pct MUST be re-measured")

    if not a.apply:
        print("\nDRY RUN - nothing written. Re-run with --apply")
        return
    for r in rows:
        for k in list(r):
            if k.startswith('_'): del r[k]
    with open(TILES, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print(f"\nWROTE {TILES}")

if __name__ == '__main__':
    main()
