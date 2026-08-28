# -*- coding: utf-8 -*-
import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
r=b.call('jawa/spawn_pawn',{'kindDef':'Jawa_Tribal_Scavenger','x':90,'z':90,
                            'faction':'Jawa_IndigenousTribes','count':8})
r.pop('operation',None)
print(r.get('message'))
rows=r.get('rows') or r.get('pawns') or []
ids=[]
for q in rows:
    print("  ok=%-5s id=%-10s xeno=%-14s name=%s"%(q.get('ok'),q.get('id'),q.get('xenotype'),q.get('name')))
    if q.get('id'): ids.append(q['id'])
print()
live={x['id']:x for x in (b.call('jawa/list_pawns',{'limit':999}).get('pawns') or [])}
for i in ids:
    x=live.get(i,{})
    print("  %-10s -> kindDef=%-24s xeno=%s"%(i,x.get('kindDef'),x.get('xenotype')))
