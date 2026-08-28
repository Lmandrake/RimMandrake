# -*- coding: utf-8 -*-
"""The one shakedown row that could not run: jawa/thing_stats needs an ARMED pawn.
Arm one, then read the same weapon on the ground and in the hands."""
import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=300); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"success":False,"EXC":str(e)}
r=c('jawa/spawn_pawn',{'kindDef':'Jawa_Tribal_Scavenger','x':140,'z':140,
                       'faction':'Jawa_IndigenousTribes','count':1})
pid=(r.get('pawns') or [{}])[0].get('id')
print("pawn:", pid)
eq=c('jawa/pawn_gear',{'pawn':pid,'action':'equip','def':'Gun_BoltActionRifle'})
print("equip ->", eq.get('success'), (eq.get('message') or json.dumps(eq))[:140])
d=c('jawa/pawn_get',{'pawn':pid})
pw=d.get('pawns')[0] if isinstance(d.get('pawns'),list) and d.get('pawns') else d
weap=[e.get('def') for e in (pw.get('equipment') or [])]
print("carrying:", weap)
for args,label in ((({'pawn':pid}),'by PAWN (the weapon in its hands)'),
                   (({'defName':'Gun_BoltActionRifle'}),'by DEFNAME')):
    s=c('jawa/thing_stats',args)
    print("\n%s -> success=%s"%(label, s.get('success')))
    print("   ", json.dumps({k:v for k,v in s.items() if k!='stats'})[:220])
    for q in (s.get('stats') or [])[:8]:
        print("      %-26s instance=%-10s def=%s"%(q.get('defName'), q.get('value'), q.get('defValue')))
