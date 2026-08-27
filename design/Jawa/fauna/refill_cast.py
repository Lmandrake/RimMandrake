#!/usr/bin/env python3
"""Refill ONLY the cast slots the owner's own cuts emptied. Change nothing else.

WHY THIS EXISTS RATHER THAN RE-RUNNING allocate_cast.py
=======================================================
181 of the 744 authored (biome, animal) entries name a creature the owner cut in
Cherry Picker, or one he threw out in his art review. A cut animal keeps its def and
its biome entry and gets `commonality: 0`, and `BiomeDef.AllWildAnimals` only yields
kinds above 0f — so it is registered and can never spawn, and nothing reports it.

🔴 THE OBVIOUS FIX IS THE WRONG ONE. `allocate_cast.py` now knows about both exclusion
sets, so re-running it produces a legal cast. Measured 2026-08-26: that re-run changes
**560 of 746 rows — 75% of the planet's fauna.** `AB_RockyCrags` keeps 0 of 29.

The allocator is greedy over a global `used` counter in biome order, so removing any
candidate cascades through every later pick. It is deterministic, not stable.

⛔ And the cast is not raw generator output any more. Standing on top of it are the
owner's 621 art rulings (`creature_art_decisions.json`, frozen), his size decisions
(`creature_size_decisions.json`), the resize patch built from them, and 12 hand-written
substitutions. Re-casting 75% of the roster discards the reviews that were made against
the creatures it removes — work no re-run can rebuild.

⇒ THIS SCRIPT IS A PATCH, NOT AN ALLOCATION. Every surviving row is carried through
byte-for-byte. Only the vacated slots are refilled, from the same candidate pool and the
same scoring the allocator uses, so a refilled slot is the pick the allocator would have
made had the ineligible creature never been a candidate for that slot.

    python3 design/Jawa/fauna/refill_cast.py                 # dry run: report only
    python3 design/Jawa/fauna/refill_cast.py --apply         # rewrite cast_assignment.csv
"""
import argparse, collections, csv, json, os, sys

FA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, FA)
import allocate_cast as AC                                        # noqa: E402
from dumppath import animals as animals_path                      # noqa: E402

CAST = f'{FA}/cast_assignment.csv'
FIELDS = ['biome', 'defName', 'label', 'mod', 'band', 'bodySize', 'commonality',
          'belong', 'standout', 'defence', 'status', 'reason', 'promoted']


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--apply', action='store_true', help='rewrite cast_assignment.csv')
    args = ap.parse_args()

    cut = AC.cherry_picker_cuts()
    rejected = AC.art_rejections()
    earth = AC.earth_fauna()
    if cut is None or rejected is None or earth is None:
        sys.exit("REFUSING: an exclusion source could not be read. Filling slots without "
                 "it would cast back the very creatures this repairs.")
    # 🔴 MEASURED, not assumed. CorellianHound is the ONE animal that reads commonality 0
    # in every biome it appears in (9 of them) and is NOT on the owner's cut list - so
    # something else zeroes it and this project cannot see what. Casting it would put a
    # known-dead entry into the roster on purpose. ⚠️ Re-check it against a later capture:
    # if it ever reads non-zero anywhere, delete this line.
    MEASURED_DEAD = {'CorellianHound'}
    ineligible = cut | rejected | earth | MEASURED_DEAD

    A, W, fit, tiles = AC.load()
    DENS = AC.biome_density()
    PDENS = AC.biome_plant_density()

    rows = list(csv.DictReader(open(CAST, encoding='utf-8')))
    by_biome = collections.defaultdict(list)
    for r in rows:
        by_biome[r['biome']].append(r)

    # 🔴 A BIOME MISSING FROM THE CAST IS 29 VACATED SLOTS, NOT A BIOME THAT DOES NOT EXIST.
    # Measured 2026-08-26: BiomeCypreJungle (191 tiles) and COMIGO_GreaterSwamp_Tropical
    # (60) are on Ash'karr and were in NO cast at all, so both kept their mod-default
    # rosters - ten Earth animals each, raccoon included. The pipeline skipped them from
    # its very first stage (they were absent from biome_terrain.csv, so biome_fit.py never
    # scored them, so the allocator had an empty pool) and reported it as a footnote under
    # "biomes short of a full pyramid" that nobody read.
    # ⛔ The planet is fixed and the animals adapt to it - owner, 2026-08-26. An Ash'karr
    # biome with no cast is a hole to fill, never a reason to change the map.
    for b in tiles:
        if b not in by_biome:
            by_biome[b] = []
            print(f"🔴 {b} is on Ash'karr ({len(tiles[b])} tiles) and had NO cast at all - "
                  f"filling all {sum(n for _, n in AC.SLOTS)} slots")

    # Reuse pressure is measured from the SURVIVORS, so a refill does not fight rows
    # that are about to be removed.
    keep = {b: [r for r in rs if r['defName'] not in ineligible] for b, rs in by_biome.items()}
    keep.update({b: [] for b in by_biome if b not in keep})
    used = collections.Counter(r['defName'] for rs in keep.values() for r in rs)
    dropped = {b: [r for r in rs if r['defName'] in ineligible] for b, rs in by_biome.items()}
    dropped.update({b: [] for b in by_biome if b not in dropped})

    out_rows, filled, unfilled = [], [], []
    for b in sorted(by_biome, key=lambda x: -len(tiles.get(x, []))):
        out_rows.extend(keep[b])
        need = collections.Counter(r['band'] for r in dropped[b])
        if not keep[b] and not dropped[b]:
            need = collections.Counter({bnd: n for bnd, n in AC.SLOTS})   # whole biome missing
        if not need:
            continue

        cold, hot = AC.pct(tiles[b], 0.25), AC.pct(tiles[b], 0.75)
        anomaly_ok = b in AC.ANOMALY_BIOMES
        pd = PDENS.get(b)
        barren = pd is not None and pd <= AC.NO_PLANT_DENSITY
        here = {r['defName'] for r in keep[b]}

        pool = []
        for dn, w in W.items():
            if dn in ineligible or dn in here:                continue
            if w['reason'] == 'anomaly' and not anomaly_ok:   continue
            if w['reason'] not in ('wildlife', 'anomaly'):    continue
            st = (A.get(dn, {}).get('stats') or {})
            lo, hi = st.get('ComfyTemperatureMin'), st.get('ComfyTemperatureMax')
            if lo is None or hi is None or not (lo <= cold and hi >= hot): continue
            if dn not in fit[b]:                              continue
            if barren and 'Vegetarian' in str(((A.get(dn, {}).get('race') or {}).get('foodType'))):
                continue
            pool.append(dn)

        # The predator cap is measured over the WHOLE biome, survivors included, so a
        # refill cannot quietly push the cast past it.
        def food(dn):
            return str(((A.get(dn, {}).get('race') or {}).get('foodType')))
        carn_cap = int(round(sum(n for _, n in AC.SLOTS) * AC.MAX_CARNIVORE_SHARE))
        carn_used = sum(1 for r in keep[b] if 'Carnivore' in food(r['defName']))

        for bnd, want in AC.SLOTS:
            if not need[bnd]:
                continue
            cands = [d for d in pool
                     if AC.band((A[d].get('race') or {}).get('baseBodySize')) == bnd]
            scored = []
            for d in cands:
                belong, standout = fit[b][d]
                s = (max(belong, standout * float(W[d]['defence']))
                     + (0.10 if W[d]['status'] == 'dormant' else 0.0)
                     + (0.15 if W[d]['reason'] == 'anomaly' else 0.0)
                     - AC.REUSE_PENALTY * used[d])
                scored.append((s, d))
            scored.sort(key=lambda z: (-z[0], z[1]))

            taken = 0
            for _, d in scored:
                if taken >= need[bnd]:
                    break
                if 'Carnivore' in food(d):
                    if carn_used >= carn_cap:
                        continue
                    carn_used += 1
                bel, sta = fit[b][d]
                out_rows.append({
                    'biome': b, 'defName': d, 'label': A[d].get('label'),
                    'mod': A[d].get('modName'), 'band': bnd,
                    'bodySize': (A[d].get('race') or {}).get('baseBodySize'),
                    'commonality': AC.commonality_for(b, bnd, DENS),
                    'belong': bel, 'standout': sta, 'defence': W[d]['defence'],
                    'status': W[d]['status'], 'reason': W[d]['reason'], 'promoted': 0})
                used[d] += 1
                pool.remove(d)
                here.add(d)
                taken += 1
                filled.append((b, bnd, d, A[d].get('label')))
            if taken < need[bnd]:
                unfilled.append((b, bnd, need[bnd] - taken))

    print(f"ineligible creatures: {len(cut)} Cherry Picker cuts + {len(rejected)} art rejections")
    print(f"rows {len(rows)} -> {len(out_rows)}    "
          f"carried through unchanged {sum(len(v) for v in keep.values())}    "
          f"vacated {sum(len(v) for v in dropped.values())}    refilled {len(filled)}")
    if unfilled:
        # 🔑 Named, never silent. A short band is a real hole in the biome's pyramid.
        print(f"\n⚠️ {sum(n for _, _, n in unfilled)} slot(s) COULD NOT be filled - no eligible "
              f"creature of that band fits the biome:")
        for b, bnd, n in unfilled:
            print(f"     {b:30s} {bnd:6s} short {n}")
    print(f"\nrefills, by biome:")
    for b in sorted({f[0] for f in filled}):
        got = [f for f in filled if f[0] == b]
        print(f"   {b:30s} {len(got):2d}  " + ", ".join(f"{f[3] or f[2]}" for f in got[:6])
              + (" …" if len(got) > 6 else ""))

    if not args.apply:
        print("\nDRY RUN - nothing written. Re-run with --apply.")
        return 0

    with open(CAST, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for r in out_rows:
            w.writerow({k: r.get(k) for k in FIELDS})
    print(f"\nwrote {CAST}: {len(out_rows)} rows")
    return 0


if __name__ == '__main__':
    sys.exit(main())
