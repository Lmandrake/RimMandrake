# -*- coding: utf-8 -*-
"""NEXT_RELOAD 24 - the Jawa hood. Absence of the config errors is necessary, not sufficient."""
import sys, json, io, collections
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=300); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"success":False,"EXC":str(e)}
ps=c('jawa/list_pawns',{'limit':400}).get('pawns') or []
anchor=[x for x in ps if x.get('x') is not None]
X,Z=(anchor[0]['x'], anchor[0]['z']) if anchor else (125,125)
print("map has %d pawns; anchoring near (%d,%d)"%(len(ps),X,Z))
KINDS=['Jawa_Colonist','Jawa_Tribal_Scavenger','Jawa_Tribal_Slinger','Jawa_Tribal_Elder']
out={}
for i,k in enumerate(KINDS):
    r=c('jawa/spawn_pawn',{'kindDef':k,'x':max(2,X-20+i*4),'z':max(2,Z-20),
                           'faction':'Jawa_IndigenousTribes','count':8})
    rows=r.get('pawns') or []
    if not rows:
        print("  %-24s SPAWN FAILED %s"%(k,(r.get('message') or '')[:80])); continue
    robe=hood=0; intruders=collections.Counter(); seen=[]
    for q in rows:
        d=c('jawa/pawn_get',{'pawn':q['id']})
        pw=d.get('pawns')[0] if isinstance(d.get('pawns'),list) and d.get('pawns') else d
        ap=[a.get('def') for a in (pw.get('apparel') or [])]
        seen.append(ap)
        robe += 1 if 'guy762_Robes_jawa' in ap else 0
        hood += 1 if 'guy762_JawaHood'   in ap else 0
        for bad in ('Apparel_WarVeil','Apparel_TribalHeaddress','Apparel_PlateArmor'):
            if bad in ap: intruders[bad]+=1
    n=len(rows)
    out[k]=dict(n=n,robe=robe,hood=hood,intruders=dict(intruders),sample=seen[0] if seen else [])
    print("  %-24s n=%d  robe=%d/%d  HOOD=%d/%d  intruders=%s"%(k,n,robe,n,hood,n,dict(intruders) or "none"))
    print("      one pawn's apparel: %s"%json.dumps(seen[0] if seen else []))
json.dump(out, open(r"D:\Luke\dev\Rimworld\world\_lf\lt_apparel.json","w"), indent=1)
