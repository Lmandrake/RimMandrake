# -*- coding: utf-8 -*-
"""LIVE_HALF_OF_LOAD_1 run 2: J8 (mech relations), K6/K7 (Blackstar leader armed), N5 (Ancient Arsenal boss)."""
import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=90); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"EXC":str(e),"success":False}
print("=== find the kinds ===")
for f in ('blackstar','ancient'):
    r=c('jawa/pawnkind_audit',{'filter':f,'limit':60,'includeHealthy':True})
    ks=[q.get('kind') for k in ('healthy','byDesign_noWeaponTags','emptyTagPool','cannotAfford','byDesign_zeroBudget')
        for q in (r.get(k) or [])]
    print("  %-10s -> %s"%(f, ks[:14]))
