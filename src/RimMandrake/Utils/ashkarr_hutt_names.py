#!/usr/bin/env python3
"""Name the Hutt holdings by what they ARE, and make the oases visibly cluster there.

Owner's ruling, 2026-08-22:
  "The Hutt settlements that are on oasis should all be named (Hutt Lord's name)'s Palace.
   Other oases should occur nearby to that area too using mutators so it can be seen they
   'happen there.' The ones that are not, in the deeper desert, should have names like
   (Hutt Lord's name)'s Casino or Market or Station, etc. showing they've been reduced to
   providing service rather than just making a Palace."

The structure that falls out: EIGHT lords, each with one palace on an oasis, and the deep
desert posts belong to whichever lord's palace is nearest. That makes the map readable -
a run of "Zeddo's" holdings is Zeddo's reach.

⛔ Not a generator. One deterministic pass over the one map. --apply writes.
"""
import argparse, csv, math, os, collections

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
W = os.path.join(ROOT, 'world')
TILES = os.path.join(W, 'ASHKARR_WORLDMAP_tiles.csv')
SETTS = os.path.join(W, 'ASHKARR_WORLDMAP_settlements.csv')
MUTS  = os.path.join(W, 'ASHKARR_WORLDMAP_mutators.csv')

PALACE_MAX_DEG = 4.0        # the measured gap: 8 sit at <=3.9, 11 at >=15.9. Nothing between.

# Eight lords, in the Huttese register. `Gorga the Immense` is kept because the live game
# already generated it for this faction - continuity with something a player may have seen.
LORDS = ["Gorga the Immense", "Bloatu the Ninth", "Vexxa the Unblinking", "Norba the Wet",
         "Zeddo the Patient", "Hurgo the Vast", "Mokka the Unpaid", "Rulla the Deep"]

# What a reduced holding does, in rough order of how far it has fallen.
SERVICE = ["Casino", "Market", "Station", "Toll", "Vault", "Spicehouse",
           "Waystation", "Kennels", "Pit", "Yard", "Skimhouse"]

def xyz(la, lo):
    la, lo = math.radians(float(la)), math.radians(float(lo))
    return (math.cos(la)*math.cos(lo), math.cos(la)*math.sin(lo), math.sin(la))

def sep(a, b):
    return math.degrees(math.acos(max(-1, min(1, sum(x*y for x, y in zip(a, b))))))

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--apply', action='store_true')
    a = ap.parse_args()

    tiles = list(csv.DictReader(open(TILES, encoding='utf-8')))
    P = {r['tile']: r for r in tiles}
    X = {t: xyz(r['lat'], r['lon']) for t, r in P.items()}
    oasis_tiles = [r['tile'] for r in tiles if r['biome'] == 'ZBiome_DesertOasis']

    with open(SETTS, encoding='utf-8') as f:
        rd = csv.DictReader(f); setts = list(rd); scols = rd.fieldnames
    hut = [s for s in setts if 'hutt' in (s.get('faction', '') + s.get('faction_def', '')).lower()]

    for s in hut:
        s['_d'] = min(sep(X[s['tile']], X[o]) for o in oasis_tiles)
    palaces = sorted([s for s in hut if s['_d'] <= PALACE_MAX_DEG], key=lambda s: s['tile'])
    service = sorted([s for s in hut if s['_d'] > PALACE_MAX_DEG], key=lambda s: s['tile'])
    if len(palaces) > len(LORDS):
        raise SystemExit(f"{len(palaces)} palaces but only {len(LORDS)} lords authored")

    lord_of = {}
    renames = []
    for lord, s in zip(LORDS, palaces):
        lord_of[s['tile']] = lord
        renames.append((s['name'], f"{lord}'s Palace", s['tile'], 'palace'))
        s['name'] = f"{lord}'s Palace"

    # each deep post belongs to the nearest palace's lord; service type cycles so one
    # lord's holdings are not all Casinos
    # ⚠️ Pure nearest-palace gave ONE lord 8 of the 11 posts and six lords none, because the
    # palaces cluster and most of the deep desert is nearest the same one. That reads as a
    # single Hutt owning the desert, not eight with reach. So: nearest palace that still has
    # room, capacity CAP each, assigned shortest-distance-first.
    CAP = 2
    pairs = sorted(((sep(X[s['tile']], X[p['tile']]), si, pi)
                    for si, s in enumerate(service) for pi, p in enumerate(palaces)),
                   key=lambda z: z[0])
    used = collections.Counter()
    owner = {}
    for dist, si, pi in pairs:
        if si in owner or used[pi] >= CAP:
            continue
        owner[si] = pi; used[pi] += 1
    for si, s in enumerate(service):          # anything left over goes to the emptiest lord
        if si not in owner:
            pi = min(range(len(palaces)), key=lambda i: (used[i], i))
            owner[si] = pi; used[pi] += 1
    # The service TYPE comes from what the place already was, so the old names survive as
    # character instead of being flattened. A per-lord counter gave six Casinos and five
    # Markets and never a Vault; the hints give each post its own job.
    HINT = {
        'The Reckoning': 'Vault',      'The Debt House': 'Toll',
        'The Skim':      'Skimhouse',  'Tollwater':      'Waystation',
        'The Levy':      'Toll',       'Fatwell':        'Market',
        'Bloatwater':    'Spicehouse', 'Itunt':          'Casino',
        'Oilpalm':       'Market',     'Gorge Station':  'Station',
        'Slug Hollow':   'Kennels',
    }
    spare = collections.Counter()
    for si, s in enumerate(service):
        lord = lord_of[palaces[owner[si]]['tile']].split()[0]   # first name only for outposts
        kind = HINT.get(s['name'])
        if not kind:
            kind = SERVICE[spare['n'] % len(SERVICE)]; spare['n'] += 1
        renames.append((s['name'], f"{lord}'s {kind}", s['tile'], 'service'))
        s['name'] = f"{lord}'s {kind}"

    # ---- oases "happen there": put the Oasis mutator on and around each palace ----
    mut = {r['tile']: r['mutators'] for r in csv.DictReader(open(MUTS, encoding='utf-8'))}
    added = 0
    for p in palaces:
        near = sorted(P, key=lambda t: sep(X[p['tile']], X[t]))[:7]   # the tile + ~6 neighbours
        for t in near:
            if P[t]['biome'] in ('Ocean', 'Lake', 'SeaIce'):
                continue
            cur = mut.get(t, '')
            if 'Oasis' in cur:
                continue
            mut[t] = (cur + ';Oasis').lstrip(';')
            added += 1

    print(f"palaces {len(palaces)}   service posts {len(service)}   Oasis mutator added to {added} tiles")
    print(f"\n{'was':22} -> {'now':30} tier")
    for old, new, t, tier in renames:
        print(f"  {old[:21]:22} -> {new[:30]:30} {tier}")

    if not a.apply:
        print("\nDRY RUN - nothing written. Re-run with --apply")
        return
    for s in setts:
        s.pop('_d', None)
    with open(SETTS, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=scols); w.writeheader(); w.writerows(setts)
    with open(MUTS, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(['tile', 'mutators'])
        for t in sorted(mut, key=int):
            if mut[t]: w.writerow([t, mut[t]])
    print(f"\nWROTE {SETTS}\nWROTE {MUTS}")

if __name__ == '__main__':
    main()
