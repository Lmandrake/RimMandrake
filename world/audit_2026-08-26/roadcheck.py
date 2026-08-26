# -*- coding: utf-8 -*-
import sys, json, os, io
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
A=r"D:\Luke\dev\Rimworld\world\_audit"
h,p,t=rc.resolve_endpoint(); b=rc.RimBridge(host=h,port=p,token=t); b.connect()
v=b.call('jawa/world_links_validate',{'limit':10})
print("VALIDATE:", json.dumps({k:v[k] for k in v if k not in ('operation','examples','asymmetric','nonAdjacent','hiddenByBiome','riverMouths')})[:600])
for k in ('asymmetric','nonAdjacent','hiddenByBiome'):
    if isinstance(v.get(k),list) and v[k]: print(" ",k,"->",json.dumps(v[k][:4])[:300])
N=21872; out=[]
for s in range(0,N,1000):
    r=b.call('jawa/world_links_get',{'range':'%d-%d'%(s,min(s+1000,N)-1),'onlyLinked':True,'limit':5000})
    out+= (r.get('tiles') or [])
json.dump(out, open(os.path.join(A,'after_links.json'),'w'))
print("linked tiles now:", len(out))
