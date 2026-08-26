# -*- coding: utf-8 -*-
import sys, json, os, collections
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
A=r"D:\Luke\dev\Rimworld\world\_audit"
h,p,t=rc.resolve_endpoint(); b=rc.RimBridge(host=h,port=p,token=t); b.connect()
NAME={1:'Flat',2:'SmallHills',3:'LargeHills',4:'Mountainous',5:'Impassable'}
plan={int(k):v for k,v in json.load(open(os.path.join(A,'hills_plan.json'),encoding='utf-8')).items()}
by=collections.defaultdict(list)
for tile,v in plan.items(): by[v].append(tile)
for v in sorted(by):
    ts=sorted(by[v]); n=0
    for i in range(0,len(ts),400):
        r=b.call('jawa/world_tile_set',{'tiles':','.join(map(str,ts[i:i+400])),
                                        'hilliness':NAME[v],'readBack':0})
        if r.get('success') is not False: n+=len(ts[i:i+400])
    print("  -> %-12s %5d tiles written"%(NAME[v],n))
print("commit:", json.dumps(b.call('jawa/world_commit',{}))[:90])
# RAW read-back, because HillinessLabel is privately cached and would lie
import random
random.seed(5)
sample=random.sample(sorted(plan), 40)
rb=b.call('jawa/world_tile_get',{'tiles':','.join(map(str,sample)),'limit':60})
HIL={'Flat':1,'SmallHills':2,'LargeHills':3,'Mountainous':4,'Impassable':5}
bad=[]
for row in (rb.get('tiles') or []):
    want=plan[row['tile']]
    got=row.get('hilliness')
    gv=HIL.get(got, got if isinstance(got,int) else -1)
    if gv!=want: bad.append((row['tile'],NAME[want],got))
print("raw read-back of 40 sampled tiles: %d mismatches %s"%(len(bad),bad[:5]))
