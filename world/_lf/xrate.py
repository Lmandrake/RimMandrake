# -*- coding: utf-8 -*-
"""Is the kind.xenotypeSet bypass a GATE or a ROLL? Spawn 12 of each and count."""
import sys, json, io, collections
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"EXC":str(e),"success":False}
for k in ('Jawa_Spawn_Hutt','Jawa_Spawn_Lasat','Jawa_Gamorrean_Guard'):
    got=collections.Counter()
    for i in range(12):
        r=c('jawa/spawn_pawn',{'kindDef':k,'x':40+i,'z':40,'faction':'Jawa_IndigenousTribes','count':1})
        rows=r.get('pawns') or []
        if rows: got[rows[0].get('xenotype')]+=1
        else: got['SPAWN_FAILED']+=1
    print("  %-24s %s"%(k, dict(got)))
