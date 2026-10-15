import json,sys
from collections import Counter
r=json.load(open(sys.argv[1]))
rows=r['rows']
print(sys.argv[1], dict(Counter(x.get('status') for x in rows)), len(rows), 'wall', r.get('wall_s'), 'tier', r.get('tier'), 'certifiable', r.get('certifiable'))
print(' notpass', [(x['id'],x['status']) for x in rows if x.get('status')!='PASS'])
c=r.get('control_noise_calm') or {}
mf=c.get('mapFog') or {}
print(' calm', c.get('calm'), 'triggers', (c.get('fogTriggers') or {}).get('byDef'), 'nonCol', c.get('nonColonistsDestroyed'), 'hb', c.get('hostileBuildingsDestroyed'))
print(' mapFog', {k: mf.get(k) for k in ('foggedBefore','foggedNow','releasedByUnfog','sweepPasses','hostilesAfter','verified','error')})
for x in rows:
  if x['id'].startswith('P3_probes'):
    d=x['detail']; m=d.get('mapFogCleared') or {}
    print(' P3', x['status'], 'hostilePawnsLeft', d.get('hostilePawnsLeft'), 'mapFogCleared', {k:m.get(k) for k in ('foggedNow','releasedByUnfog','hostilesAfter','verified')})
