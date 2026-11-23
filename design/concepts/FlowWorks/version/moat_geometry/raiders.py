"""Read every recorded sc_moat_raid run: the raised-bridge watch polled raider by raider up to the sluice order. Writes
raiders.json: per run the polls [(tick, {id: [x, z]})], and per raider the swim numbers the mod read (costX, enduranceH, class)."""
import glob, json, os, re
HERE = os.path.dirname(os.path.abspath(__file__)); IG = os.path.join(HERE, '..', 'in_game')
runs = []
for f in sorted(glob.glob(IG + '/visit_[3-8]/evidence/sc_moat_raid_*.json') + glob.glob(IG + '/testpilot_20261123/*.json')):
    d = json.load(open(f)); calls = d.get('calls') or []
    ids = None; polls = []; swim = {}; gate = False; cur = None
    for c in calls:
        t, a, r = c['tool'], c['args'], c['result']
        if not isinstance(r, dict): continue
        if t == 'jawa/lord_assault_spawn' and ids is None: ids = set(a['pawns'].split(','))
        elif ids is not None and t == 'jawa/list_pawns' and a.get('faction') == 'hostile':
            cur = (r.get('state') or {}).get('tick')
            polls.append([cur, {p['id']: [p['x'], p['z']] for p in r.get('pawns') or [] if p.get('id') in ids and not p.get('dead') and p.get('x') is not None}])
        elif ids is not None and t == 'jawa/static_call' and 'ProofSwim' in str(a):
            m = re.match(r'SWIM (\w+) class=(\w+) natural=\w+ load=([\d.]+) enduranceH=([\d.]+) costX=([\d.]+)', str(r.get('result')))
            if m and m.group(1) not in swim: swim[m.group(1)] = [m.group(2), float(m.group(3)), float(m.group(4)), float(m.group(5))]
        elif t == 'jawa/static_call' and 'ProofSetGate' in str(a) and '|true' in str(a): gate = True; break
    if not gate or not polls: continue
    R = {r['id']: r for r in d['rows']}
    held = re.search(r"'held': \[([^\]]*)\]", str(R.get('MOAT_two_held_and_captured', {}).get('detail', '')))
    ex = re.search(r"'exhaustion': (\{[^}]*\})", str(R['MOAT_raiders_swim']['detail']))
    runs.append({'file': os.path.relpath(f, IG), 'ids': sorted(ids), 'polls': polls, 'swim': swim,
                 'swimRow': R['MOAT_raiders_swim']['status'], 'swam': len(eval(ex.group(1))) if ex else 0,
                 'tired': sum(1 for x in eval(ex.group(1)).values() if x) if ex else 0,
                 'held': len([x for x in held.group(1).split(',') if x.strip()]) if held else None})
json.dump(runs, open(os.path.join(HERE, 'raiders.json'), 'w'))
print(len(runs), 'runs; swam', [r['swam'] for r in runs], 'tired', [r['tired'] for r in runs], 'held', [r['held'] for r in runs])
IN = lambda p: 60 <= p[0] <= 71 and 60 <= p[1] <= 71
wet = lambda p: IN(p) and not (62 <= p[0] <= 69 and 62 <= p[1] <= 69)
for r in runs:
    first = {}; last = r['polls'][-1]
    for t, ps in r['polls']:
        for k, p in ps.items():
            if p[1] >= 58 and k not in first: first[k] = t
    print(r['file'][-28:], 't0', r['polls'][0][0], 'end', last[0], 'bank', sorted(first.get(k, 9999) for k in r['ids']), 'wetNow', sum(map(wet, last[1].values())), 'plot', sum(IN(p) and not wet(p) for p in last[1].values()), 'held', r['held'], 'class', sorted(x[0] for x in r['swim'].values()).count('None'))
