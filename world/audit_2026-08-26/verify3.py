# -*- coding: utf-8 -*-
import sys, json, os, collections
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
A=r"D:\Luke\dev\Rimworld\world\_audit"
h,p,t=rc.resolve_endpoint(); b=rc.RimBridge(host=h,port=p,token=t); b.connect()
N=21872; after={}
for s in range(0,N,1000):
    r=b.call('jawa/world_mutators_get',{'range':'%d-%d'%(s,min(s+1000,N)-1),'onlyWithMutators':True,'limit':5000})
    for row in (r.get('tiles') or []): after[row['tile']]={m['def'] for m in row['mutators']}
lm=b.call('jawa/world_landmarks_get',{'limit':30000})
json.dump({str(k):sorted(v) for k,v in after.items()}, open(os.path.join(A,'after3_mutators.json'),'w'))
json.dump(lm['landmarks'], open(os.path.join(A,'after3_landmarks.json'),'w'))
before={t_['tile']:{m['def'] for m in t_['mutators']}
        for t_ in json.load(open(os.path.join(A,'now_mutators.json'),encoding='utf-8'))}
gain=collections.Counter(); lost=collections.Counter()
for k,v in after.items():
    prev=before.get(k,set())
    for d in v-prev: gain[d]+=1
    for d in prev-v: lost[d]+=1
for k,v in before.items():
    if k not in after:
        for d in v: lost[d]+=1
print("mutated tiles %d -> %d   landmarks %d -> %d"%(len(before),len(after),
      len(json.load(open(os.path.join(A,'now_landmarks.json'),encoding='utf-8'))), lm['count']))
print("\nGAINED"); 
for d,n in gain.most_common(24): print("  +%-5d %s"%(n,d))
print("\nLOST")
for d,n in lost.most_common(24): print("  -%-5d %s"%(n,d))
