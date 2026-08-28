# -*- coding: utf-8 -*-
"""The untested variable: count>1, which is the shape the original sighting used."""
import sys, json, io, collections
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"EXC":str(e),"success":False}
def census(): return {x['id']:x for x in (c('jawa/list_pawns',{'limit':999}).get('pawns') or [])}
tot=[]
for i,(kind,n,fac) in enumerate([('Jawa_Tribal_Scavenger',6,'Jawa_IndigenousTribes'),
                                 ('Jawa_Tribal_Scavenger',6,'Jawa_IndigenousTribes'),
                                 ('Jawa_Geonosian_Grunt',2,'Jawa_GeonosianFoundryHive')]):
    before=census()
    r=c('jawa/spawn_pawn',{'kindDef':kind,'x':200+i*3,'z':150,'faction':fac,'count':n})
    reported=[q['id'] for q in (r.get('pawns') or []) if q.get('id')]
    after=census()
    new=[k for k in after if k not in before]
    unasked=[after[k] for k in new if k not in reported]
    print("  %-24s count=%d -> reported %d, appeared %d, UNASKED %d %s"%(
        kind,n,len(reported),len(new),len(unasked),
        [(u.get('kindDef'),u.get('xenotype'),u.get('factionName')) for u in unasked]))
    tot.extend(unasked)
print("\ntotal unasked:", len(tot))
