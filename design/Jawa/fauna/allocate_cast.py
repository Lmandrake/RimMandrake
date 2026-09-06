#!/usr/bin/env python3
"""Cast all 25 biomes: who lives where, how common, and who needs to be made bigger.

Owner's brief, 2026-08-22:
  "there should be many small, some medium, a few large, and one super-huge rare entity in
   each biome, their appearance should match the biome when possible, ignore existing stats
   like combat heat and diet as we can change that, try to make creatures unique to a biome
   as much as possible and not have ubiquitous creatures"
  "We may need to re-size some of them ... to fill in gaps (need more giant things)"
  "finding things that are WILDLY differently colored is also biologically plausible if they
   can defend themselves with poison or hostility ... So that's just one criteria."

⛔ Deterministic. No RNG. Same inputs -> same cast, so a re-run after a tweak is a diff.
"""
import argparse, csv, json, math, os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dumppath import animals as animals_path

FA = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(FA)))

# The pyramid, per biome. Sums to 29 - big enough to feel populated, small enough that a
# player learns the cast of a place.
SLOTS = [('tiny', 4), ('small', 8), ('med', 8), ('large', 5), ('huge', 3), ('SUPER', 1)]
# Commonality per band: the pyramid is about VARIETY; this is about how often you meet them.
COMMONALITY = {'tiny': 1.00, 'small': 0.70, 'med': 0.40, 'large': 0.18, 'huge': 0.07,
               'SUPER': 0.012}          # the set piece is genuinely rare
REUSE_PENALTY = 0.75                    # per biome already using this creature
# 🔴 The rare bands are scaled INVERSELY with the biome's animalDensity, against a reference.
# Commonality is RELATIVE, and total spawns scale with density - so a flat 0.012 makes the
# set piece 65x rarer in ExtremeDesert (density 0.1) than in AB_MiasmicMangrove (6.5). It
# would essentially never appear in a sparse biome, which defeats the point of having one.
DENSITY_REF = 1.8                       # AB_RockyCrags: a middling biome
RARE_SCALED = {'SUPER': (0.008, 0.20), 'huge': (0.05, 0.35)}   # (floor, ceiling) after scaling
# 🔴 DIET. A cast that cannot eat is not a cast.
#   - A strict vegetarian in a biome with no plants starves. SeaIce (plantDensity 0) was
#     given 14 herbivores and IceSheet 12.
#   - A cast that is more predator than prey eats itself. ZBiome_DesertOasis reached 1.07
#     carnivores per prey animal.
NO_PLANT_DENSITY = 0.02          # at or below this, treat the biome as having no forage
MAX_CARNIVORE_SHARE = 0.40       # of the whole cast
ANOMALY_BIOMES = {'HorrorWastes', 'AB_GelatinousSuperorganism', 'AB_OcularForest', 'Scarlands'}

# ==========================================================================
#  WHO IS INELIGIBLE, AND WHY IT IS NOT A JUDGEMENT CALL
# ==========================================================================
# Two sets of the OWNER'S OWN decisions used to be invisible to this allocator,
# and both of them silently cost slots.
#
#  1. CHERRY PICKER CUTS. He removes a def in Cherry Picker; the def stays in the
#     database and its biome `commonality` becomes 0. `AllWildAnimals` only yields
#     kinds above 0f, so the animal is registered and UNSPAWNABLE. Measured
#     2026-08-26: 181 of the 744 entries this file cast were cut animals - 157
#     distinct creatures, 100% of them on his list. A quarter of the planet's cast
#     could not appear, and nothing reported it.
#
#  2. HIS ART REJECTIONS. `creature_art_decisions.json` is frozen and his own
#     (savedBy creature_art_review.html). The 10 rows in state `replace` are
#     creatures he threw out by eye. Re-running this allocator without reading them
#     would put every one of them straight back and delete the 12 substituted rows
#     that replaced them - the file has no other record of that work.
#
# ⛔ BOTH LOADERS RETURN None, NEVER AN EMPTY SET, WHEN THEY CANNOT READ THE SOURCE.
# An empty set means "nobody is excluded" and would quietly restore exactly the
# creatures these exist to keep out. None makes the caller refuse.

def cherry_picker_cuts():
    """PawnKindDef names the owner has cut, or None if the settings file is unreadable."""
    sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
    import cherrypicker
    from dumppath import defs_dir
    try:
        cuts = cherrypicker.load()
    except IOError as exc:
        print(f"⚠️ {exc}")
        return None
    cut = cuts.names
    # He cuts ThingDefs; wildAnimals takes PawnKindDefs. Map through the race.
    kinds = set()
    pk = json.load(open(defs_dir() + '/PawnKindDef.json', encoding='utf-8'))
    pk = pk if isinstance(pk, list) else pk.get('defs')
    for x in pk:
        if not isinstance(x, dict):
            continue
        if x['defName'] in cut or ((x.get('fields') or {}).get('race')) in cut:
            kinds.add(x['defName'])
    print(cuts.provenance())
    print(f"-> {len(kinds)} ineligible pawn kinds")
    return kinds


def art_rejections():
    """Creatures the owner marked `replace` in his frozen art review, or None."""
    f = f'{FA}/creature_art_decisions.json'
    if not os.path.isfile(f):
        return None
    try:
        d = json.load(open(f, encoding='utf-8'))
    except Exception:
        return None
    out = {k for k, v in (d.get('decisions') or {}).items()
           if (v or {}).get('state') == 'replace'}
    print(f"art review: {len(out)} creature(s) the owner rejected by eye")
    return out


def earth_fauna():
    """defNames the owner has ruled off this planet, or None if the list is unreadable.

    ⛔ Every entry is validated against the live PawnKindDef roster on load. A name that
    does not resolve is a SILENT NO-OP - it excludes nothing and reads as if it did - so
    it is named out loud rather than skipped.
    """
    f = f'{FA}/EARTH_FAUNA_EXCLUDED.txt'
    if not os.path.isfile(f):
        return None
    names = [l.strip() for l in open(f, encoding='utf-8')
             if l.strip() and not l.lstrip().startswith('#')]
    from dumppath import defs_dir
    pk = json.load(open(defs_dir() + '/PawnKindDef.json', encoding='utf-8'))
    pk = pk if isinstance(pk, list) else pk.get('defs')
    kinds = {x['defName'] for x in pk if isinstance(x, dict)}
    bad = [n for n in names if n not in kinds]
    if bad:
        print(f"⚠️ EARTH_FAUNA_EXCLUDED.txt names {len(bad)} defName(s) that do not exist "
              f"and therefore exclude NOTHING: {', '.join(sorted(bad))}")
    print(f"Earth fauna: {len(names) - len(bad)} creature(s) ruled off the planet")
    return set(names)


def band(b):
    b = float(b or 0)
    return ('tiny' if b < 0.3 else 'small' if b < 0.8 else 'med' if b < 1.6
            else 'large' if b < 3.0 else 'huge' if b < 6.0 else 'SUPER')

def biome_plant_density():
    import json as _j
    from dumppath import defs_dir
    bl = _j.load(open(defs_dir() + '/BiomeDef.json', encoding='utf-8'))
    bl = bl if isinstance(bl, list) else bl.get('defs')
    return {x['defName']: ((x.get('fields') or {}).get('plantDensity'))
            for x in bl if isinstance(x, dict)}

def biome_density():
    import json as _j
    from dumppath import defs_dir
    bl = _j.load(open(defs_dir() + '/BiomeDef.json', encoding='utf-8'))
    bl = bl if isinstance(bl, list) else bl.get('defs')
    return {x['defName']: ((x.get('fields') or {}).get('animalDensity') or 1.0)
            for x in bl if isinstance(x, dict)}

def load():
    A = {x['defName']: x for x in json.load(open(animals_path(), encoding='utf-8'))['animals']}
    W = {r['defName']: r for r in csv.DictReader(open(f'{FA}/wildlife.csv', encoding='utf-8'))}
    fit = collections.defaultdict(dict)
    for r in csv.DictReader(open(f'{FA}/biome_fit.csv', encoding='utf-8')):
        fit[r['biome']][r['defName']] = (float(r['belong']), float(r['standout']))
    tiles = collections.defaultdict(list)
    sys.path.insert(0, os.path.join(ROOT, 'src', 'RimMandrake', 'Utils'))
    from verify_frozen import warn_if_stale
    warn_if_stale(f'{ROOT}/world/ASHKARR_WORLDMAP_tiles.csv')
    for r in csv.DictReader(open(f'{ROOT}/world/ASHKARR_WORLDMAP_tiles.csv', encoding='utf-8')):
        if r['biome'] not in ('Ocean', 'Lake'):
            tiles[r['biome']].append(float(r['temp_c']))
    return A, W, fit, tiles

def median(v):
    v = sorted(v); n = len(v)
    return v[n//2] if n % 2 else (v[n//2-1] + v[n//2]) / 2

def pct(v, p):
    v = sorted(v)
    return v[max(0, min(len(v) - 1, int(round(p * (len(v) - 1)))))]

def commonality_for(biome, bnd, DENS):
    c = COMMONALITY[bnd]
    if bnd not in RARE_SCALED:
        return c
    d = float(DENS.get(biome) or DENSITY_REF) or DENSITY_REF
    lo, hi = RARE_SCALED[bnd]
    return round(max(lo, min(hi, c * (DENSITY_REF / d))), 4)

def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--out', default=None,
                    help='write here instead of cast_assignment.csv (for a dry diff)')
    ap.add_argument('--i-know-this-overwrites-the-owners-substitutions', action='store_true',
                    dest='overwrite',
                    help='required to rewrite cast_assignment.csv in place')
    args = ap.parse_args()

    CUT = cherry_picker_cuts()
    REJECTED = art_rejections()
    EARTH = earth_fauna()
    if CUT is None:
        sys.exit("REFUSING: Cherry Picker's config could not be read, so every animal the "
                 "owner cut would be cast back in - registered, unspawnable and silent.\n"
                 "Looked for Config/Mod_3521312241_Mod_CherryPicker.xml.")
    if REJECTED is None:
        sys.exit("REFUSING: creature_art_decisions.json could not be read, so the 10 "
                 "creatures the owner threw out by eye would go straight back into the cast.")
    if EARTH is None:
        sys.exit("REFUSING: design/Jawa/fauna/EARTH_FAUNA_EXCLUDED.txt is missing, so every "
                 "terrestrial Earth animal the owner has ruled off this planet would be cast "
                 "back onto it. That rule lived nowhere but in his head until 2026-08-26; do "
                 "not let it go back there.")
    INELIGIBLE = CUT | REJECTED | EARTH

    A, W, fit, tiles = load()
    DENS = biome_density()
    PDENS = biome_plant_density()
    biomes = sorted(tiles, key=lambda b: -len(tiles[b]))
    used = collections.Counter()
    cast = {}
    promote = []                 # creatures we must enlarge to fill a SUPER slot

    for b in biomes:
        # 🔴 NOT the median. Filtering on the median put cows, geese and ostriches on SeaIce:
        # that biome inherited the -2 C LIQUID-WATER CLAMP, so its median reads -2 while the
        # biome actually spans -60..0. A creature must tolerate the biome's INTERQUARTILE
        # range, not its middle tile, or it dies on most of the ground it was cast onto.
        cold, hot = pct(tiles[b], 0.25), pct(tiles[b], 0.75)
        anomaly_ok = b in ANOMALY_BIOMES
        pool = []
        for dn, w in W.items():
            if w['reason'] == 'anomaly' and not anomaly_ok:  continue
            if w['reason'] not in ('wildlife', 'anomaly'):   continue
            st = (A.get(dn, {}).get('stats') or {})
            lo, hi = st.get('ComfyTemperatureMin'), st.get('ComfyTemperatureMax')
            if lo is None or hi is None or not (lo <= cold and hi >= hot): continue
            if dn in INELIGIBLE:                              continue
            if dn not in fit[b]:                              continue
            pool.append(dn)

        pd = PDENS.get(b)
        barren = pd is not None and pd <= NO_PLANT_DENSITY
        def food(dn):
            return str(((A.get(dn, {}).get('race') or {}).get('foodType')))
        if barren:
            # nothing to graze: a strict vegetarian here is a starvation report waiting to
            # happen. Omnivores stay - they can eat the carnivores' leavings.
            pool = [d for d in pool if 'Vegetarian' not in food(d)]
        carn_cap = int(round(sum(n for _, n in SLOTS) * MAX_CARNIVORE_SHARE))
        carn_used = 0

        chosen = []
        for bnd, want in SLOTS:
            here = [d for d in pool if band((A[d].get('race') or {}).get('baseBodySize')) == bnd]
            scored = []
            for d in here:
                belong, standout = fit[b][d]
                defence = float(W[d]['defence'])
                # STANDOUT is licensed by defence (aposematism); otherwise BELONG carries it.
                fitscore = max(belong, standout * defence)
                # a creature nobody has cast yet is worth more than one already placed
                dormant_bonus = 0.10 if W[d]['status'] == 'dormant' else 0.0
                anomaly_bonus = 0.15 if W[d]['reason'] == 'anomaly' else 0.0
                s = fitscore + dormant_bonus + anomaly_bonus - REUSE_PENALTY * used[d]
                scored.append((s, d))
            scored.sort(key=lambda z: (-z[0], z[1]))
            take = [d for _, d in scored[:want]]
            # SUPER slot empty? promote the best 'huge' instead of leaving the biome headless.
            # Excludes defNames this biome already chose (as 'huge' or otherwise) — without
            # this, a biome with few huge-band candidates could promote one of its own huge
            # picks, writing the same defName into the CSV twice for one biome.
            if bnd == 'SUPER' and not take:
                already = {d for d, _ in chosen}
                hp = [(max(fit[b][d][0], fit[b][d][1] * float(W[d]['defence'])) - REUSE_PENALTY*used[d], d)
                      for d in pool if band((A[d].get('race') or {}).get('baseBodySize')) == 'huge'
                      and d not in already]
                hp.sort(key=lambda z: (-z[0], z[1]))
                if hp:
                    take = [hp[0][1]]
                    promote.append((b, hp[0][1], (A[hp[0][1]].get('race') or {}).get('baseBodySize')))
            for d in take:
                if 'Carnivore' in food(d):
                    if carn_used >= carn_cap:
                        continue          # cast is already predator-heavy; skip this one
                    carn_used += 1
                used[d] += 1
                chosen.append((d, bnd))
        cast[b] = chosen

    # ---- write the assignment ----
    # 🔴 THE FILE HOLDS WORK THIS SCRIPT CANNOT REBUILD FROM NOTHING. 12 rows carry a
    # `substituted` status written by hand after the owner's art review. They ARE
    # reproducible now that `replace` is read above - but only because it is read, so
    # the overwrite still has to be asked for out loud.
    out = args.out or f'{FA}/cast_assignment.csv'
    if args.out is None and not args.overwrite:
        sys.exit(
            f"REFUSING: {out} carries 12 hand-substituted rows and this script rewrites "
            f"the whole file.\n"
            f"  --out <path>   write elsewhere and diff it first (do this)\n"
            f"  --i-know-this-overwrites-the-owners-substitutions   replace it in place")
    with open(out, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(['biome', 'defName', 'label', 'mod', 'band', 'bodySize', 'commonality',
                    'belong', 'standout', 'defence', 'status', 'reason', 'promoted'])
        promo = {(b, d) for b, d, _ in promote}
        for b in biomes:
            for d, bnd in cast[b]:
                bel, sta = fit[b][d]
                w.writerow([b, d, A[d].get('label'), A[d].get('modName'), bnd,
                            (A[d].get('race') or {}).get('baseBodySize'),
                            commonality_for(b, bnd, DENS), bel, sta, W[d]['defence'],
                            W[d]['status'], W[d]['reason'], int((b, d) in promo)])
    tot = sum(len(v) for v in cast.values())
    print(f"wrote {out}: {tot} (biome, creature) assignments across {len(biomes)} biomes")
    print(f"distinct creatures used: {len(used)} of {sum(1 for r in W.values() if r['reason'] in ('wildlife','anomaly'))} eligible")
    print(f"appear in exactly one biome: {sum(1 for c in used.values() if c==1)}   "
          f"in 2-3: {sum(1 for c in used.values() if 2<=c<=3)}   in 4+: {sum(1 for c in used.values() if c>=4)}")
    print(f"\nbiomes short of a full pyramid:")
    for b in biomes:
        c = collections.Counter(bnd for _, bnd in cast[b])
        miss = [f"{bnd} {c[bnd]}/{want}" for bnd, want in SLOTS if c[bnd] < want]
        if miss: print(f"   {b:30} {', '.join(miss)}")
    print(f"\nSUPER slots filled by PROMOTION ({len(promote)} biomes need a creature enlarged):")
    for b, d, sz in promote:
        print(f"   {b:30} {A[d].get('label') or d:28} bodySize {sz} -> needs >= 6.0")

if __name__ == '__main__':
    main()
