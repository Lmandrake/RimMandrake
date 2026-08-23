#!/usr/bin/env python3
"""Two owner rulings on the meridian coast, 2026-08-23, applied together because they
share the same shoreline and cannot be judged apart.

  E1  the drained Twilight/Grey Sea floor is ONE biome and reads as patches of desert
  E2  the sea ice ends on a hard vertical line at the terminator

🔴 OWNER, 2026-08-23, verbatim: *"I really must insist that you put some more variety in
the deserts that you inserted into the shrunk twilight sea regions (towards the night
side). It looks very strange just having patches of desert. Some arid scrubland against
the ocean waters perhaps? And please make the frozen ice not have a hard vertical line at
the terminator... make it look more natural."*

⛔ NOT a generator. One deterministic pass over the one map, run once. There is no seed
and no parameter that could produce a different planet. `--apply` writes; without it
nothing is touched. See `design/Jawa/worldbuilding/the_one_map.md`.

---
E1 — WHAT WAS MEASURED, and why the previous pass left it uniform

`ashkarr_shore_zonation.py` ran and deliberately excluded the drained seabed: commit
d0e1434f, *"A playa is bare: the dried seabed no longer counts as vegetated fringe."*
That reading was defensible and the owner has now overruled it at the water's edge.

State before this pass: **369 tiles** across `Twilight Sea` and `Grey Sea` that are not
water — **every one of them `ExtremeDesert`, every one carrying `VEE_SaltPlains`.** One
biome, one mutator, 369 tiles. That is the uniformity he is looking at.

🔑 **And `ExtremeDesert` is wrong on its own terms here.** These tiles run **0.1 – 25.4 °C,
median 10.8** — this is temperate ground beside water, not the hottest desert on the
planet. The biome was inherited from the halving pass, not chosen for this ground.

The zonation is driven by distance to the water that SURVIVED, which is the physical
story: a retreating sea leaves its damp, salt-tolerant fringe nearest the remaining
water and its bare playa in the middle of the basin.

---
E2 — WHAT WAS MEASURED

`Ocean` reaches arc **101.51**. `SeaIce` begins at arc **101.64**. **Zero overlap**, a
0.13° gap — every water tile on the planet freezes at one arc value. That is the vertical
line, and it is an artifact of freezing by a temperature threshold alone.

🔑 **Real sea ice is ragged because it does not form by latitude.** It forms first in
shallow sheltered water along a coast (fast ice) and last in open water, so the margin
runs in fingers and leaves open leads well into the cold. This pass reproduces that from
the geometry already on the map — coast proximity — rather than from noise.

⛔ **No RNG, no seed.** Ties inside the band break on a fixed integer hash of the tile id,
which is reproducible by construction. Re-running gives the same planet.
"""
from __future__ import annotations
import argparse, collections, csv, math, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
W = os.path.join(ROOT, 'world')
TILES = os.path.join(W, 'ASHKARR_WORLDMAP_tiles.csv')
MUTS = os.path.join(W, 'ASHKARR_WORLDMAP_mutators.csv')

WET = {'Ocean', 'Lake', 'SeaIce'}
DRAINED_REGIONS = {'Twilight Sea', 'Grey Sea'}
SALT = 'VEE_SaltPlains'

# E1 zonation. Tile spacing on this grid is ~1.44°, so these are "one hop" and "two hops".
SHORE_DEG = 1.6      # against the water
MID_DEG = 3.2        # one step inland
SHORE_MAX_C = 16.0   # 🔑 scrub needs the cooler shore. Above this the fringe is bare too.

# E2 freezing band. The current hard line sits at 101.5; this opens it either side.
BAND_LO, BAND_ARC_HI = 92.0, 112.0
COAST_REACH = 4.0    # degrees over which coast proximity still helps ice form
W_ARC, W_COAST = 0.45, 0.40
W_HASH = 0.15       # tie-break only — enough to ruffle an edge, never to decide a region


def xyz(r):
    la, lo = math.radians(float(r['lat'])), math.radians(float(r['lon']))
    return (math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la))


def sep(a, b):
    return math.degrees(math.acos(max(-1.0, min(1.0, sum(p * q for p, q in zip(a, b))))))


def nearest(p, pts):
    return min((sep(p, q) for q in pts), default=999.0)


def stable_unit(tile_id: str) -> float:
    """Deterministic 0..1 from the tile id. Not randomness — a fixed hash, so the same
    tile always gets the same value and re-running cannot produce a second planet."""
    return ((int(tile_id) * 2654435761) % 100003) / 100003.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true', help='write the CSVs; otherwise report only')
    a = ap.parse_args()

    with open(TILES, encoding='utf-8') as fh:
        rd = csv.DictReader(fh)
        tiles = list(rd)
        cols = rd.fieldnames
    X = {r['tile']: xyz(r) for r in tiles}

    muts = {}
    with open(MUTS, encoding='utf-8') as fh:
        mrd = csv.DictReader(fh)
        mcols = mrd.fieldnames
        for m in mrd:
            muts[m['tile']] = m['mutators']

    land_pts = [X[r['tile']] for r in tiles if r['biome'] not in WET]
    wet_pts = [X[r['tile']] for r in tiles if r['biome'] in WET]

    # ---------------------------------------------------------------- E1
    drained = [r for r in tiles if r['region'] in DRAINED_REGIONS and r['biome'] not in WET]
    e1 = collections.Counter()
    for r in drained:
        d = nearest(X[r['tile']], wet_pts)
        t = float(r['temp_c'])
        if d <= SHORE_DEG and t <= SHORE_MAX_C:
            new = 'AridShrubland'
        elif d <= MID_DEG or t <= SHORE_MAX_C:
            new = 'Desert'
        else:
            new = 'ExtremeDesert'
        e1[f"{r['biome']} -> {new}"] += 1
        r['biome'] = new
        # 🔑 A salt plain with scrub standing on it is a contradiction. The playa keeps
        # its mutator; the vegetated fringe gives it up.
        if new == 'AridShrubland':
            cur = [x for x in (muts.get(r['tile']) or '').split(';') if x and x != SALT]
            muts[r['tile']] = ';'.join(cur)

    # ---------------------------------------------------------------- E2
    water = [r for r in tiles if r['biome'] in ('Ocean', 'SeaIce')]
    target_ice = sum(1 for r in water if r['biome'] == 'SeaIce')
    band = [r for r in water if BAND_LO <= float(r['arc']) <= BAND_ARC_HI]
    scored = []
    for r in band:
        arc = float(r['arc'])
        coast = 1.0 - min(1.0, nearest(X[r['tile']], land_pts) / COAST_REACH)
        s = (W_ARC * (arc - BAND_LO) / (BAND_ARC_HI - BAND_LO)
             + W_COAST * coast
             + W_HASH * stable_unit(r['tile']))
        scored.append((s, r))
    # Everything colder than the band stays ice; everything warmer stays water. The band
    # is re-decided to hold the SAME total, so this changes the SHAPE and not the amount.
    fixed_ice = sum(1 for r in water if r['biome'] == 'SeaIce' and float(r['arc']) > BAND_ARC_HI)
    need = max(0, target_ice - fixed_ice)
    scored.sort(key=lambda sr: -sr[0])
    freeze = {id(r) for _, r in scored[:need]}
    e2 = collections.Counter()
    for r in band:
        new = 'SeaIce' if id(r) in freeze else 'Ocean'
        if new != r['biome']:
            e2[f"{r['biome']} -> {new}"] += 1
        r['biome'] = new
    for r in water:
        if float(r['arc']) > BAND_ARC_HI and r['biome'] != 'SeaIce':
            e2['(beyond band) Ocean -> SeaIce'] += 1
            r['biome'] = 'SeaIce'

    # ---------------------------------------------------------------- report
    oc = [float(r['arc']) for r in tiles if r['biome'] == 'Ocean']
    ic = [float(r['arc']) for r in tiles if r['biome'] == 'SeaIce']
    print("E1 drained seabed —", len(drained), "tiles")
    for k, v in sorted(e1.items(), key=lambda kv: -kv[1]):
        print(f"   {v:5d}  {k}")
    print("E2 ice margin —", len(band), "water tiles re-decided in the band")
    for k, v in sorted(e2.items(), key=lambda kv: -kv[1]):
        print(f"   {v:5d}  {k}")
    print(f"   ice total {sum(1 for r in tiles if r['biome']=='SeaIce')} "
          f"(was {target_ice} — the amount is held, only the shape moves)")
    if oc and ic:
        ov = max(0.0, max(oc) - min(ic))
        print(f"   Ocean reaches arc {max(oc):.1f} · SeaIce begins {min(ic):.1f} · "
              f"OVERLAP {ov:.1f}°" + ("   🔴 STILL A LINE" if ov <= 0.5 else "   ✅ interleaved"))

    if not a.apply:
        print("\n(dry run — pass --apply to write)")
        return 0

    with open(TILES, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(tiles)
    with open(MUTS, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=mcols)
        w.writeheader()
        # ⚠️ The file's convention is ONE ROW PER TILE THAT HAS MUTATORS — it carried zero
        # empty rows before this pass. A tile whose only mutator was the salt plain drops
        # out entirely rather than staying as a blank row.
        for t, mv in muts.items():
            if mv:
                w.writerow({'tile': t, 'mutators': mv})
    print(f"\nwrote {TILES}\nwrote {MUTS}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
