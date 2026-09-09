#!/usr/bin/env python3
"""Derive rosters/_global.json from the 28 per-biome rosters + the creature register.

Everything ruled is written as data with its authority; everything derived is
recomputed on each run (never hand-edit _global.json — rerun this).
Live = not cut, not commonalityZeroed, not modDropped. Wild = kindOf in
{animal, insectoid}. Reserve pool = live wild minus every rostered def minus cuts.
"""
import json
import os
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..'))
REGISTER = os.path.join(ROOT, 'design', 'Jawa', 'worldbuilding', 'review',
                        'creature_register_rows.json')
OUT = os.path.join(HERE, '_global.json')

RULED = {
    'authority': 'owner cards 2026-09-09 (BIOME_FAUNA_ASSIGNMENT_SITTING_1) + prep §9 accepted in bulk',
    'earth_five_evicted_planet_wide': ['Rat', 'Hare', 'WildBoar', 'Raccoon', 'Warg'],
    'earth_five_carve_out': 'Rat rides the Fall Line injection only (prep §9)',
    'grindterra_rule': 'GRim* (mod GRiNDTerra) = Earth analogs, homeless-by-default; '
                       'GR_* = Vanilla Genetics Expanded chimeras, judged per sheet law '
                       '(prefix corrected 2026-09-09)',
    'in_jokes_kept_reskinned': {
        'Boomalope': 'homed: the_pyrelands (ash-grazer read); reskin rides the art lane',
        'Muffalo': 'NO wild home landed — reserve + reskin; doctrine calibration animal. '
                   'Owner review sheet decides if it gets a home.',
    },
    'ubiquity_25_dispositions': 'prep §9 table, accepted 2026-09-09 — trims enforced by '
                                '_validate.py --cross (ubiquity_exception rows carry their '
                                'own sheet-law argument, owner-review-flagged)',
}


def main():
    with open(REGISTER) as f:
        rows = json.load(f)['rows']

    rostered = {}
    cuts = []
    reserve_dispositions = {}
    for fn in sorted(os.listdir(HERE)):
        if not fn.endswith('.json') or fn.startswith('_'):
            continue
        with open(os.path.join(HERE, fn)) as f:
            d = json.load(f)
        for r in d.get('fauna', []):
            rostered.setdefault(r['def'], []).append(d.get('sheet', fn))
        for e in d.get('evictions', []):
            disp = (e.get('disposition') or '')
            if disp.startswith('cut:'):
                cuts.append({'def': e.get('def'), 'sheet': d.get('sheet', fn),
                             'ruling': disp[4:].strip(), 'reason': e.get('reason', '')})
            elif 'homeless-reserve' in disp:
                reserve_dispositions.setdefault(e.get('def'), []).append(d.get('sheet', fn))

    live_wild = [r for r in rows
                 if not r.get('cut') and not r.get('commonalityZeroed')
                 and not r.get('modDropped')
                 and r.get('kindOf') in ('animal', 'insectoid')]
    cut_defs = {c['def'] for c in cuts}
    grim = sorted(r['defName'] for r in live_wild if r['defName'].startswith('GRim'))
    reserve = sorted(
        r['defName'] for r in live_wild
        if r['defName'] not in rostered and r['defName'] not in cut_defs
    )

    out = {
        'derived': str(date.today()),
        'ruled': RULED,
        'measured': {
            'live_wild_creatures': len(live_wild),
            'rostered_defs': len(rostered),
            'reserve_pool': len(reserve),
            'cut_dispositions': len(cuts),
            'grindterra_grim_defs_live': len(grim),
        },
        'reserve_for_events': reserve,
        'reserve_evicted_from': {k: v for k, v in sorted(reserve_dispositions.items())
                                 if k in set(reserve)},
        'cuts': sorted(cuts, key=lambda c: (c['def'], c['sheet'])),
        'grindterra_defs': grim,
    }
    with open(OUT, 'w') as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    print(f"_global.json: {len(live_wild)} live wild MEASURED · {len(rostered)} rostered · "
          f"{len(reserve)} reserve · {len(cuts)} cut dispositions · {len(grim)} GRim defs")


if __name__ == '__main__':
    main()
