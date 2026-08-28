# -*- coding: utf-8 -*-
import sys, json, io, collections
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=90); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"EXC":str(e),"success":False}
def gear(pid):
    d=c('jawa/pawn_get',{'pawn':pid})
    pw=d.get('pawns')[0] if isinstance(d.get('pawns'),list) and d.get('pawns') else d
    return ([e.get('def') for e in (pw.get('equipment') or [])],
            [a.get('def') for a in (pw.get('apparel') or [])], pw.get('xenotype'))

print("=== J8: vanilla mechanoids must have NO relations ===")
ps=c('jawa/list_pawns',{'limit':999}).get('pawns') or []
mechs=[x for x in ps if x.get('isMechanoid') or (x.get('kindDef') or '').startswith('Mech_')]
print("  mechanoids on map:", [(m.get('kindDef'),m.get('id')) for m in mechs][:4])
for m in mechs[:2]:
    r=c('jawa/pawn_relations',{'pawn':m['id'],'action':'list'})
    rel=r.get('relations') or r.get('direct') or []
    print("  %-16s relations=%s  %s"%(m.get('kindDef'), (len(rel) if isinstance(rel,list) else rel),
          (r.get('message') or '')[:90]))

print("\n=== K6/K7: a Blackstar Leader must spawn ARMED ===")
for k,n in (('Jawa_Blackstar_Leader',4),('Jawa_Blackstar_Heavy',2)):
    r=c('jawa/spawn_pawn',{'kindDef':k,'x':60,'z':110,'faction':'Jawa_Junkers','count':n})
    for row in (r.get('pawns') or []):
        eq,ap,xe=gear(row['id'])
        print("  %-24s weapon=%-26s apparel=%s"%(k, json.dumps(eq)[:26], json.dumps(ap)[:70]))

print("\n=== N5: the Ancient Arsenal boss must draw from a real pool ===")
for k,n in (('AncientSoldierBoss',4),('AncientSoldierBossN',2)):
    r=c('jawa/spawn_pawn',{'kindDef':k,'x':70,'z':110,'faction':'Ancients','count':n})
    if not (r.get('pawns') or []):
        print("  %-20s -> %s"%(k,(r.get('message') or '')[:90])); continue
    for row in (r.get('pawns') or []):
        eq,ap,xe=gear(row['id'])
        print("  %-20s xeno=%-22s weapon=%-30s apparel=%s"%(k,xe,json.dumps(eq)[:30],json.dumps(ap)[:60]))
