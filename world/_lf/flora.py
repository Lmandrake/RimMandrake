# -*- coding: utf-8 -*-
import sys, json, io, collections
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"EXC":str(e),"success":False}
for x in b.list_tools():
    if x.get('name')=='jawa/list_things':
        print("list_things keys:", sorted((x.get('inputSchema',{}).get('properties') or {}).keys()))
        print("  ", (x.get('description') or '')[:200])
r=c('jawa/list_things',{'category':'Plant','limit':4000})
if not r.get('success'): r=c('jawa/list_things',{'limit':4000})
things=r.get('things') or []
print("\nthings returned:", len(things), "| keys:", sorted(things[0].keys()) if things else '-')
cnt=collections.Counter(x.get('def') or x.get('defName') for x in things)
plants={k:v for k,v in cnt.items() if k and ('Plant' in k or 'plant' in k.lower() or 'Tree' in k)}
print("\nplant-looking defs on this map:")
for k,v in sorted(plants.items(), key=lambda kv:-kv[1])[:25]: print("   %5d  %s"%(v,k))
print("\ntop 15 of everything:", [f"{k}:{v}" for k,v in cnt.most_common(15)])
