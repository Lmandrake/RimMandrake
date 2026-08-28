# -*- coding: utf-8 -*-
"""STRAY_COLONISTS_IN_JAWA_FACTIONS_1 - one spawn, full census before and after, 10 times."""
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
extra=[]
for i in range(10):
    before=census()
    r=c('jawa/spawn_pawn',{'kindDef':'Jawa_Tribal_Scavenger','x':150+i,'z':150,
                           'faction':'Jawa_IndigenousTribes','count':1})
    reported=[q['id'] for q in (r.get('pawns') or []) if q.get('id')]
    after=census()
    new=[k for k in after if k not in before]
    unasked=[after[k] for k in new if k not in reported]
    print("  run %2d: reported %d, appeared %d, UNASKED %d %s"%(
        i+1, len(reported), len(new), len(unasked),
        [(u.get('kindDef'),u.get('xenotype'),u.get('factionName')) for u in unasked]))
    extra.extend(unasked)
print()
print("total unasked pawns across 10 single spawns:", len(extra))
print(dict(collections.Counter((u.get('kindDef'),u.get('factionName')) for u in extra)))
json.dump([{k:u.get(k) for k in ('id','kindDef','xenotype','factionName','x','z')} for u in extra],
          open(r"D:\Luke\dev\Rimworld\world\_lf\stray_evidence.json","w"), indent=1)
