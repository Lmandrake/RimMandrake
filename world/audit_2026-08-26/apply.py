# -*- coding: utf-8 -*-
"""Execute world/_audit/ops.json against the LIVE planet.  --apply to write.

Landmark success is `added>=1` AND the read-back showing our def on the tile.
`isValidTile` is NOT a gate: it is evaluated after the add, so it reports the
landmark we just placed. Measured 2026-08-26.
"""
import sys, json, io, os
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
A=r"D:\Luke\dev\Rimworld\world\_audit"
APPLY='--apply' in sys.argv
ONLY=[a.split('=',1)[1] for a in sys.argv if a.startswith('--only=')]
h,p,t=rc.resolve_endpoint(); b=rc.RimBridge(host=h,port=p,token=t); b.connect()
ops=json.load(open(os.path.join(A,'ops.json')))
NB={}
import csv
for r in csv.DictReader(open(os.path.join(A,'neighbors.csv'),encoding='utf-8')):
    NB[int(r['tile'])]=[int(r['n%d'%i]) for i in range(6) if int(r['n%d'%i])>=0]
existing={x['tile'] for x in json.load(open(os.path.join(A,'landmarks.json'),encoding='utf-8'))['landmarks']}
blocked=set(existing)
for t_ in existing: blocked|=set(NB.get(t_,()))
log=[]; fails=[]; placed=[]
def call(tool,params):
    try:
        r=b.call(tool,params)
        if isinstance(r,dict) and r.get('success') is False:
            fails.append((tool,str(params)[:70],str(r.get('message'))[:130]))
        return r
    except Exception as e:
        fails.append((tool,str(params)[:70],str(e)[:130])); return {'success':False}
def chunks(xs,n):
    for i in range(0,len(xs),n): yield xs[i:i+n]

# ---- phase 1: mutators and tile scalars
for o in ops:
    if ONLY and o['p'] not in ONLY: continue
    if o['kind']=='mutator':
        if APPLY:
            for c in chunks(o['tiles'],350):
                call('jawa/world_mutators_set',{'action':'add','mutators':o['mutators'],
                                                'tiles':','.join(map(str,c)),'readBack':0})
        log.append("%-11s mut   %-30s %5d"%(o['p'],o['mutators'],len(o['tiles'])))
    elif o['kind']=='tile_hilliness':
        if APPLY:
            call('jawa/world_tile_set',{'tiles':','.join(map(str,o['tiles'])),
                                        'hilliness':'Mountainous','readBack':0})
        log.append("%-11s tile  hilliness=Mountainous         %5d"%(o['p'],len(o['tiles'])))

# ---- phase 2: landmarks, one at a time, adjacency aware
for o in ops:
    if ONLY and o['p'] not in ONLY: continue
    if o['kind']!='landmark': continue
    got=0; tried=0; refused=0
    if APPLY:
        for tile in o['candidates']:
            if got>=o['want']: break
            if tile in blocked: continue
            tried+=1
            r=call('jawa/world_landmarks_set',{'action':'add','def':o['d'],
                                               'tiles':str(tile),'checkValid':True})
            rows=r.get('tiles') or []
            ok = r.get('added',0)>=1 and rows and rows[0].get('landmark')==o['d']
            if ok:
                got+=1; placed.append([o['d'],tile,rows[0].get('landmarkName')])
                blocked.add(tile); blocked|=set(NB.get(tile,()))
            else:
                refused+=1
    log.append("%-11s LMK   %-30s %d/%d placed, %d refused (%d tried)"%(
               o['p'],o['d'],got,o['want'],refused,tried))

# ---- phase 3: roads
for o in ops:
    if ONLY and o['p'] not in ONLY: continue
    if o['kind']!='road_detour': continue
    done=0
    if APPLY:
        for it in o['items']:
            call('jawa/world_links_clear',{'kind':'road','tiles':str(it['t']),'to':it['a'],'readBack':0})
            call('jawa/world_links_clear',{'kind':'road','tiles':str(it['t']),'to':it['c'],'readBack':0})
            r=call('jawa/world_links_set',{'kind':'road','def':it['d'],
                    'path':'%d,%d,%d,%d'%(it['a'],it['x'],it['y'],it['c']),'readBack':0})
            if r.get('success') is not False: done+=1
    log.append("%-11s ROAD  detours rerouted               %5d"%(o['p'],done if APPLY else len(o['items'])))

if APPLY:
    log.append("commit -> "+json.dumps(call('jawa/world_commit',{}))[:200])
with io.open(os.path.join(A,'apply_log.txt'),'w',encoding='utf-8') as f:
    f.write(("APPLIED" if APPLY else "DRY RUN")+"\n"+"\n".join(log)+"\n\nFAILURES %d\n"%len(fails))
    for x in fails[:80]: f.write("  %s\n"%(x,))
json.dump(placed,open(os.path.join(A,'landmarks_placed.json'),'w'))
print("\n".join(log)); print("failures:",len(fails))
for x in fails[:20]: print("  ",x)
