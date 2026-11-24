#!/usr/bin/env python3
"""selftest_on_pit.py [--label | --receipt]: 0 holds, 1 fails (no argument: both).

--label: on_pit.label names a hostile on a pit square (held, climber in gear, neither, unread), and trench.py calls it.
--receipt: gear_climber_g4.json (a live run of gear_climber.py) has every row PASS, and its own traced reads say the same: the
climber stood on the pit square unheld about 450 ticks a step and left it; the man without gear never entered, and was held when
set in it; with the pits switch off (the planted fault) the same man reads ONPIT."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def label_fails():
    try:
        import on_pit
    except ImportError as e:
        return ['on_pit.py: %s' % e]
    free, held = 'TRAP descents=0 held=False last=-', 'TRAP descents=1 held=True last=-'
    cases = [(held, ['RM_ClimbingGear'], 'HELD'), (held, [], 'HELD'), (free, ['Apparel_Parka', 'RM_ClimbingGear'], 'CLIMBER'),
             (free, ['Apparel_Parka'], 'ONPIT'), (free, [], 'ONPIT'), (free, None, 'GEAR-UNREAD'),
             ('REFUSED: no spawned pawn', ['RM_ClimbingGear'], 'TRAP-UNREAD'), ('', [], 'TRAP-UNREAD')]
    bad = ['label(%r, %r) = %s, want %s' % (t, a, on_pit.label(t, a), w) for t, a, w in cases if on_pit.label(t, a) != w]
    replies = [({'success': True, 'pawns': [{'apparel': [{'def': 'RM_ClimbingGear'}]}]}, ['RM_ClimbingGear']),
               ({'success': True, 'pawns': [{'apparel': []}]}, []), ({'success': True, 'pawns': []}, None),
               ({'success': False, 'message': 'no pawn'}, None), (None, None), ({'success': True, 'pawns': [{}]}, None)]
    bad += ['worn(%r) = %r, want %r' % (r, on_pit.worn(r), w) for r, w in replies if on_pit.worn(r) != w]
    if 'on_pit.label(' not in (HERE / 'trench.py').read_text(encoding='utf-8'):
        bad.append('trench.py does not call on_pit.label')
    return bad


def receipt_fails():
    f = HERE / 'gear_climber_g4.json'
    if not f.exists():
        return ['no %s' % f.name]
    d = json.loads(f.read_text(encoding='utf-8'))
    rows = {r['id']: r['status'] for r in d.get('rows', [])}
    need = ['GEAR_steps_in', 'GEAR_climbs_out_unheld', 'GEAR_reads_climber', 'PLAIN_never_enters_open_pit', 'PLAIN_in_pit_is_held',
            'PLANT_switch_off_reads_onpit']
    bad = ['row %s = %s' % (n, rows.get(n)) for n in need if rows.get(n) != 'PASS']
    sq, strip = tuple(d['geometry']['sq']), tuple(d['geometry']['strip'])
    tr = {k: [(x[0], tuple(x[1]), x[2]) for x in v['trace']] for k, v in d['TRACE'].items()}

    def t_at(k, c):
        return next((t for t, at, _ in tr.get(k, []) if at == c), None)
    first_out = next((t for t, at, _ in tr.get('gear_out', []) if at != sq), None)
    for what, t in (('step in', t_at('gear_in', sq)), ('step out', first_out)):
        if t is None or not 420 <= t <= 510:
            bad.append('%s took %s ticks, not one 450-tick step' % (what, t))
    if t_at('gear_out', strip) is None or any(h for k in ('gear_in', 'gear_out') for _, _, h in tr.get(k, [])):
        bad.append('the climber was held or never reached the strip')
    if not tr.get('plain_in') or any(at == sq for _, at, _ in tr['plain_in']):
        bad.append('the man without gear entered (or was not read)')
    if not tr.get('plain_out') or not all(at == sq and h for _, at, h in tr['plain_out']):
        bad.append('the man without gear was not held on the square all along')
    if d.get('labels', {}).get('gear') != 'CLIMBER' or d.get('labels', {}).get('plant') != 'ONPIT' or d['labels'].get('plain') != 'HELD':
        bad.append('live labels %s' % d.get('labels'))
    return bad


if __name__ == '__main__':
    bad = ([] if '--receipt' in sys.argv else label_fails()) + ([] if '--label' in sys.argv else receipt_fails())
    print('FAIL' if bad else 'PASS', *bad, sep='\n  ')
    sys.exit(1 if bad else 0)
