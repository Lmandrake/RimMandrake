# rd.py <json> [n]: rows, holdLeft, and the hold trace (first n lines, then every line around a change of held=)
import json, sys
d = json.load(open(sys.argv[1])); n = int(sys.argv[2]) if len(sys.argv) > 2 else 6
print('status', d.get('status'), str(d.get('error'))[:200])
for r in d.get('rows') or []: print(' ', r['id'], r['status'], str(r.get('detail'))[:330])
print('held', d.get('holdHeld'), 'left', json.dumps(d.get('holdLeft'))[:700], 'raid', (d.get('raidFaction') or {}).get('faction'), (d.get('raidFaction') or {}).get('arrived'))
tr = d.get('holdTrace') or d.get('ptrCaptureTrace') or []
print('trace lines', len(tr))
def key(l): return tuple(sorted((w, ) for w in l.split() if w.startswith('held=') or 'ladders' in w))
show = set(range(n)) | {len(tr) - 1}
for i in range(1, len(tr)):
    hs = lambda l: [p.split(':')[0].split()[1] + p.split('held=')[1][:5] for p in l.split(' | ') if p.strip().startswith('H ') or ' H ' in p[:12]]
    if hs(tr[i]) != hs(tr[i - 1]) or tr[i].split('ladders=')[-1] != tr[i - 1].split('ladders=')[-1]: show |= {i - 1, i, i + 1}
for i in sorted(show):
    if 0 <= i < len(tr): print(i, tr[i][:520])
