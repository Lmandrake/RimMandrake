"""Analyse the in-session attribution A/B: python3 Transient/foundry_tps_ab_analyse_20261010.py
Joins the schedule (block UTC bounds) to the disk TPS record windows whose whole span lies inside a block."""
import json, glob, os, datetime, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__))
D = '/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/JawaBench/tps'
sched = json.load(open(os.path.join(HERE, 'foundry_tps_ab_schedule_20261010.json')))
rows = []
for f in sorted(glob.glob(os.path.join(D, 'tps_20261010T210001Z_*.jsonl'))):
    for ln in open(f, encoding='utf-8', errors='replace'):
        try:
            r = json.loads(ln)
        except ValueError:
            continue
        if r.get('kind') == 'sample':
            rows.append(r)


def t(s):
    return datetime.datetime.strptime(s.rstrip('Z')[:26], '%Y-%m-%dT%H:%M:%S.%f')


out = []
for b in sched['blocks']:
    s0, s1 = t(b['start']), t(b['end'])
    w = []
    for r in rows:
        end = t(r['utc'])
        start = end - datetime.timedelta(seconds=r.get('dReal') or 0)
        if start >= s0 and end <= s1 and r.get('state') == 'run':
            w.append(r)
    dt = sum(r['dTicks'] for r in w)
    dr = sum(r['dReal'] for r in w)
    sim = sum(r.get('simMs') or 0 for r in w)
    ratios = [r['ratio'] for r in w if r.get('ratio') is not None]
    out.append({'speed': b['speed'], 'attr': b['attribution'], 'windows': len(w), 'ticks': dt,
                'tpsWall': round(dt / dr, 1) if dr else None,
                'simMsPerTick': round(sim / dt, 3) if dt else None,
                'ratioMean': round(st.mean(ratios), 3) if ratios else None,
                'fps': round(st.mean([r['fps'] for r in w]), 1) if w else None,
                'profEstMs': sum((r.get('profEstMs') or 0) for r in w)})
for o in out:
    print(o)
print('\nper speed: attribution ON vs OFF (mean of the two blocks each)')
summary = {}
for sp in dict.fromkeys(o['speed'] for o in out):
    on = [o for o in out if o['speed'] == sp and o['attr'] and o['ticks']]
    off = [o for o in out if o['speed'] == sp and not o['attr'] and o['ticks']]
    if not on or not off:
        print(sp, 'insufficient windows'); continue
    def m(xs, k):
        return st.mean([x[k] for x in xs])
    son, soff = m(on, 'simMsPerTick'), m(off, 'simMsPerTick')
    ton, toff = m(on, 'tpsWall'), m(off, 'tpsWall')
    summary[sp] = {'simMsPerTick_on': round(son, 3), 'simMsPerTick_off': round(soff, 3),
                   'simOverheadPct': round(100 * (son - soff) / soff, 1),
                   'tpsWall_on': round(ton, 1), 'tpsWall_off': round(toff, 1),
                   'tpsCostPct': round(100 * (toff - ton) / toff, 1),
                   'blockSpread_simMsPerTick_on': [x['simMsPerTick'] for x in on],
                   'blockSpread_simMsPerTick_off': [x['simMsPerTick'] for x in off]}
    print(sp, summary[sp])
json.dump({'blocks': out, 'summary': summary}, open(os.path.join(HERE, 'foundry_tps_ab_result_20261010.json'), 'w'), indent=1)
