# -*- coding: utf-8 -*-
"""C40 - three Jawa fixes that only a load can prove. Live, full 582-mod list."""
import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()

before={x['id'] for x in (b.call('jawa/list_pawns',{'limit':400}).get('pawns') or [])}
def spawn(kind, faction, n, x, z):
    r=b.call('jawa/spawn_pawn',{'kindDef':kind,'x':x,'z':z,'faction':faction,'count':n})
    print("spawn %-26s %-26s -> %s %s"%(kind,faction,r.get('success'),(r.get('message') or '')[:110]))
    return r
spawn('Jawa_Tribal_Scavenger','Jawa_IndigenousTribes',6,120,120)
spawn('Jawa_Geonosian_Grunt','Jawa_GeonosianFoundryHive',2,135,120)
print()
after=b.call('jawa/list_pawns',{'limit':400}).get('pawns') or []
new=[x for x in after if x['id'] not in before]
print("NEW pawns:",len(new))
out=[]
for x in new:
    d=b.call('jawa/pawn_get',{'pawn':x['id']})
    pw=(d.get('pawns') or [d.get('pawn')] or [{}])[0] or {}
    eq=pw.get('equipment') or pw.get('weapon') or []
    ap=pw.get('apparel') or []
    print("%-24s xeno=%-16s weapon=%-22s apparel=%s"%(
        x.get('kindDef'), x.get('xenotype'),
        json.dumps(eq)[:22], json.dumps(ap)[:150]))
    out.append(pw)
json.dump(out, open(r"D:\Luke\dev\Rimworld\world\_lf\c40_pawns.json","w"), indent=1)
print("\nkeys of one pawn_get:", sorted(out[0].keys()) if out else "none")
