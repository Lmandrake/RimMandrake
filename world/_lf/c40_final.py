# -*- coding: utf-8 -*-
"""C40 final read-back: arming + apparel on the 8 clean Jawa, plus the Geonosian, plus census."""
import sys, json, io, collections
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
gi=b.call('rimworld/get_game_info',{}); print("ticksGame",gi.get('ticksGame'),"maps",gi.get('mapCount'))
ps=b.call('jawa/list_pawns',{'limit':999}).get('pawns') or []
print("pawns on map:",len(ps))
print(dict(collections.Counter((x.get('kindDef'),x.get('factionName')) for x in ps if x.get('factionName'))))
print()
armed=robe=hood=0; jaw=[]
for x in ps:
    if x.get('kindDef')!='Jawa_Tribal_Scavenger': continue
    d=b.call('jawa/pawn_get',{'pawn':x['id']})
    pw=d.get('pawns')[0] if isinstance(d.get('pawns'),list) and d.get('pawns') else d
    eq=[e.get('def') for e in (pw.get('equipment') or [])]
    ap=[a.get('def') for a in (pw.get('apparel') or [])]
    jaw.append((pw.get('xenotype'),eq,ap))
    armed += 1 if eq else 0
    robe  += 1 if 'guy762_Robes_jawa' in ap else 0
    hood  += 1 if 'guy762_JawaHood' in ap else 0
n=len(jaw)
print("Jawa_Tribal_Scavenger on map: %d"%n)
print("  MandrakeJawa      : %d/%d"%(sum(1 for a,_,_ in jaw if a=='MandrakeJawa'),n))
print("  ARMED             : %d/%d"%(armed,n))
print("  guy762_Robes_jawa : %d/%d"%(robe,n))
print("  guy762_JawaHood   : %d/%d"%(hood,n))
print("  weapons seen:", sorted({w for _,e,_ in jaw for w in e}))
print("  apparel seen:", sorted({a for _,_,ap in jaw for a in ap}))
print()
for x in ps:
    if x.get('kindDef')!='Jawa_Geonosian_Grunt': continue
    d=b.call('jawa/pawn_get',{'pawn':x['id']})
    pw=d.get('pawns')[0] if isinstance(d.get('pawns'),list) and d.get('pawns') else d
    print("Geonosian: xeno=%s weapon=%s apparel=%s"%(pw.get('xenotype'),
      [e.get('def') for e in (pw.get('equipment') or [])],
      [a.get('def') for a in (pw.get('apparel') or [])]))
json.dump(jaw, open(r"D:\Luke\dev\Rimworld\world\_lf\c40_evidence.json","w"), indent=1)
