# -*- coding: utf-8 -*-
"""Is the Colonist substitution a count>1 group-maker path, or the faction itself?"""
import sys, json, io, collections
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
before={x['id'] for x in (b.call('jawa/list_pawns',{'limit':999}).get('pawns') or [])}
for i in range(6):
    b.call('jawa/spawn_pawn',{'kindDef':'Jawa_Tribal_Scavenger','x':100+i,'z':100,
                              'faction':'Jawa_IndigenousTribes','count':1})
after=b.call('jawa/list_pawns',{'limit':999}).get('pawns') or []
new=[x for x in after if x['id'] not in before]
print("six SEPARATE count=1 calls -> %d new pawns"%len(new))
for k,v in collections.Counter((x.get('kindDef'),x.get('xenotype')) for x in new).items():
    print("  %2d  %-26s %s"%(v,k[0],k[1]))
# arm/apparel read-back on each real scavenger
print()
ok=0
for x in new:
    if x.get('kindDef')!='Jawa_Tribal_Scavenger': continue
    d=b.call('jawa/pawn_get',{'pawn':x['id']})
    pw=(d.get('pawns') or [d])[0] if isinstance(d.get('pawns'),list) else d
    eq=[e.get('def') for e in (pw.get('equipment') or [])]
    ap=[a.get('def') for a in (pw.get('apparel') or [])]
    armed = len(eq)>0
    robe  = 'guy762_Robes_jawa' in ap
    hood  = 'guy762_JawaHood' in ap
    ok += 1 if (armed and robe) else 0
    print("  xeno=%-13s armed=%-5s robe=%-5s hood=%-5s weapon=%s apparel=%s"%(
        pw.get('xenotype'),armed,robe,hood,eq,ap))
print("\narmed+robed: %d"%ok)
