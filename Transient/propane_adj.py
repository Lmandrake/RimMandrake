import csv
from collections import Counter
live = {int(r['tile']): r['biome'] for r in csv.DictReader(open('Transient/v24_tiles_live.csv'))}
adj = {}
for r in csv.DictReader(open('world/world_neighbors_sub7b.csv')):
    t = int(r[list(r.keys())[0]])
    ns = [int(x) for x in list(r.values())[1:] if x and x.strip().lstrip('-').isdigit() and int(x)>=0]
    adj[t] = ns
pl = {t for t,b in live.items() if b=='AB_PropaneLakes'}
lk = {t for t,b in live.items() if b=='RUT_PropaneLake'}
border = Counter(live[n] for t in pl for n in adj.get(t,[]) if live.get(n) not in ('AB_PropaneLakes',None))
print("AB_PropaneLakes borders:", dict(border.most_common()))
lakeb = Counter(live[n] for t in lk for n in adj.get(t,[]) if live.get(n) != 'RUT_PropaneLake')
print("RUT_PropaneLake borders:", dict(lakeb.most_common()))
