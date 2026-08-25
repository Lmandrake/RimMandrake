from common import *
import pickle,shutil,sys,csv as _csv
tiles,nb,roads,setts,objs=load()
DRAFT=B+'ASHKARR_DRAFT_2026-08-24'
rivers=json.load(open(O+'rivers_raw.json'))
COLS='tile,biome,elevation,temperature,rainfall,hilliness,swampiness,pollution,riverDist,feature,featureId,waterCovered,roadCount,riverCount,mutatorCount'.split(',')

def write_bundle(stem, roadG, positions):
    src=list(_csv.DictReader(open(B+'_now2.csv')))
    rc={}; 
    for a,d in roadG.items(): rc[a]=len(d)
    with open(stem+'_tiles.csv','w',newline='') as f:
        w=_csv.DictWriter(f,fieldnames=COLS); w.writeheader()
        for r in src:
            t=int(r['tile']); o={k:r.get(k,'') for k in COLS}
            o['roadCount']=rc.get(t,0)
            w.writerow(o)
    with open(stem+'_links.csv','w',newline='') as f:
        w=_csv.writer(f); w.writerow(['kind','a','b','def'])
        seen=set()
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
        w=_csv.writer(f); w.writerow(['id','def','faction','factionName','name','tile','layer'])
        for o in setts:
            w.writerow([o['id'],o['def'],o['faction'],o['factionName'],o['name'],positions[o['id']],o['layer']])
    for suf in ('_landmarks.csv','_mutators.csv','_meta.json'):
        shutil.copy(DRAFT+suf, stem+suf)
    print('wrote',stem)

before_pos={o['id']:o['tile'] for o in setts}
write_bundle(O+'before', roads, before_pos)
d=pickle.load(open(O+'final.pkl','rb'))
after_pos={o['id']:d['plan'].get(o['id'],o['tile']) for o in setts}
write_bundle(O+'after', d['newroads'], after_pos)
