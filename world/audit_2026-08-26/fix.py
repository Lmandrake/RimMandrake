# -*- coding: utf-8 -*-
import sys, json, os, csv
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
A=r"D:\Luke\dev\Rimworld\world\_audit"
h,p,t=rc.resolve_endpoint(); b=rc.RimBridge(host=h,port=p,token=t); b.connect()

# 1. tile 863: a dry-river landmark landed on a LIVE river tile. Undo it.
print("remove lmk 863:", json.dumps(b.call('jawa/world_landmarks_set',
      {'action':'remove','tiles':'863'}))[:120])
print("remove VEE_DryRiver:", json.dumps(b.call('jawa/world_mutators_set',
      {'action':'remove','mutators':'VEE_DryRiver','tiles':'863','readBack':0}))[:120])
print("restore River:", json.dumps(b.call('jawa/world_mutators_set',
      {'action':'add','mutators':'River','tiles':'863','readBack':1}))[:220])

# 2. the ruin clusters: the LANDMARK is 'Ruins', the mutator is 'AncientRuins'.
NB={int(r['tile']):[int(r['n%d'%i]) for i in range(6) if int(r['n%d'%i])>=0]
    for r in csv.DictReader(open(os.path.join(A,'neighbors.csv'),encoding='utf-8'))}
blocked=set()
for x in json.load(open(os.path.join(A,'after_landmarks.json'),encoding='utf-8')):
    blocked.add(x['tile']); blocked|=set(NB.get(x['tile'],()))
groups=json.load(open(os.path.join(A,'fix.json'),encoding='utf-8'))
got=0
for cands in groups:
    n=0
    for tile in cands:
        if n>=3: break
        if tile in blocked: continue
        r=b.call('jawa/world_landmarks_set',{'action':'add','def':'Ruins','tiles':str(tile),'checkValid':True})
        rows=r.get('tiles') or []
        if r.get('added',0)>=1 and rows and rows[0].get('landmark')=='Ruins':
            n+=1; got+=1; blocked.add(tile); blocked|=set(NB.get(tile,()))
print("Ruins landmarks placed:",got)
print("commit:", json.dumps(b.call('jawa/world_commit',{}))[:80])
