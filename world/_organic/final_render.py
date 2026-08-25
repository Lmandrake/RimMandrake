import json,csv,shutil,collections
B='/mnt/d/Luke/dev/Rimworld/world/'; O=B+'_organic/'
V=B+'ASHKARR_VIVIFIED_2026-08-24'
objs=json.load(open(O+'objects_live.json')); setts=[o for o in objs if o['isSettlement']]
links=json.load(open(O+'links_live.json')); rivers=json.load(open(O+'rivers_raw.json'))
stem=O+'live'
shutil.copy(V+'_tiles.csv',stem+'_tiles.csv'); shutil.copy(V+'_meta.json',stem+'_meta.json')
for s in ('_landmarks.csv','_mutators.csv'):
    try: shutil.copy(V+s,stem+s)
    except Exception: pass
with open(stem+'_links.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['kind','a','b','def']); seen=set()
    for l in rivers:
        for pr in l['potentialRivers']:
            k=(min(l['tile'],pr['neighbor']),max(l['tile'],pr['neighbor']))
            if k in seen: continue
            seen.add(k); w.writerow(['river',l['tile'],pr['neighbor'],pr['def']])
    seen=set()
    for l in links:
        for pr in l['potentialRoads']:
            k=(min(l['tile'],pr['neighbor']),max(l['tile'],pr['neighbor']))
            if k in seen: continue
            seen.add(k); w.writerow(['road',l['tile'],pr['neighbor'],pr['def']])
with open(stem+'_settlements.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['id','faction_def','faction','name','tile','why'])
    for o in setts: w.writerow([o['id'],o['faction'],o['factionName'],o['name'],o['tile'],''])
print('live bundle written')
