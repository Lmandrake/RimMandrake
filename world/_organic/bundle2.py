from common import *
import pickle,shutil,csv as _csv
tiles,nb,roads,setts,objs=load()
V=B+'ASHKARR_VIVIFIED_2026-08-24'
rivers=json.load(open(O+'rivers_raw.json'))
def write(stem,roadG,positions):
    shutil.copy(V+'_tiles.csv', stem+'_tiles.csv')
    shutil.copy(V+'_meta.json', stem+'_meta.json')
    for s in ('_landmarks.csv','_mutators.csv'):
        try: shutil.copy(V+s, stem+s)
        except Exception: pass
    with open(stem+'_links.csv','w',newline='') as f:
        w=_csv.writer(f); w.writerow(['kind','a','b','def']); seen=set()
        for l in rivers:
            for pr in l['potentialRivers']:
                k=(min(l['tile'],pr['neighbor']),max(l['tile'],pr['neighbor']))
                if k in seen: continue
                seen.add(k); w.writerow(['river',l['tile'],pr['neighbor'],pr['def']])
        seen=set()
        for a,d in roadG.items():
            for b,df in d.items():
                k=(min(a,b),max(a,b))
                if k in seen: continue
                seen.add(k); w.writerow(['road',a,b,df])
    with open(stem+'_settlements.csv','w',newline='') as f:
        w=_csv.writer(f); w.writerow(['id','faction_def','faction','name','tile','why'])
        for o in setts:
            w.writerow([o['id'],o['faction'],o['factionName'],o['name'],positions[o['id']],''])
    print('wrote',stem)
write(O+'before',roads,{o['id']:o['tile'] for o in setts})
d=pickle.load(open(O+'final.pkl','rb'))
write(O+'after',d['newroads'],{o['id']:d['plan'].get(o['id'],o['tile']) for o in setts})
