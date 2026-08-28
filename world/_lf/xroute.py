# -*- coding: utf-8 -*-
"""Prove LIVE that kind.xenotypeSet bypasses FactionDef.xenotypeChances.
Spawn a Jawa_Spawn_* / RimMandrake*_Kind with NO forced xenotype, in a faction that does not
list that xenotype, and read the xenotype off the INSTANCE."""
import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"EXC":str(e),"success":False}
# what does Jawa_IndigenousTribes actually allow?
fd=c('jawa/get_def',{'defName':'Jawa_IndigenousTribes','defType':'FactionDef'})
d=fd.get('def') or fd
xs=json.dumps(d.get('xenotypeSet') or d.get('xenotypeChances') or 'n/a')
print("Jawa_IndigenousTribes xenotypeSet:", xs[:300])
print()
KINDS=['Jawa_Spawn_Hutt','Jawa_Spawn_Lasat','Jawa_Spawn_Kubaz',
       'RimMandrakeWookiee_Kind','RimMandrakeChiss_Kind','Jawa_Gamorrean_Guard']
z=60
for k in KINDS:
    r=c('jawa/spawn_pawn',{'kindDef':k,'x':60,'z':z,'faction':'Jawa_IndigenousTribes','count':1})
    z+=2
    rows=r.get('pawns') or []
    if not rows:
        print("  %-26s -> %s"%(k,(r.get('message') or '')[:80])); continue
    print("  %-26s -> xenotype on the INSTANCE: %s"%(k, rows[0].get('xenotype')))
