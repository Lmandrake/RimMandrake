import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
S.quiet()
def j(x,n=500): return json.dumps(x,default=str)[:n]
ps=[p for p in (S.call("jawa/list_pawns", faction="player", limit=50).get("pawns") or []) if p.get("isPlayer") and p.get("intelligence")=="Humanlike"]
c=ps[0]; bx,bz=c["x"]-40,c["z"]
print("colonist",c["x"],c["z"],"base",bx,bz)
print("weather0", j(S.call("jawa/weather_get"),700))
kinds=["AA_GreenGoo","AA_RedGoo","AA_AcanthamoebaGiganteaLarge","AA_AcanthamoebaGiganteaSmall","AA_RedSpore","AA_InfectedAerofleet","AA_Thunderbeast"]
for i,k in enumerate(kinds):
    x,z=bx+(i%4)*12, bz+(i//4)*14
    r=S.call("jawa/spawn_pawn", kindDef=k, x=x, z=z, faction="none", count=1)
    pw=(r.get("pawns") or [{}])[0]; pid=pw.get("id"); px,pz=pw.get("x",x),pw.get("z",z)
    f0=len(S.call("jawa/list_things", defName="Filth_SpentAcid", rect="%d,%d,9,9"%(px-4,pz-4)).get("things") or [])
    d=S.call("jawa/damage", damageDef="Crush", amount=5000, thingId=pid)
    S.run(30)
    f1=S.call("jawa/list_things", defName="Filth_SpentAcid", rect="%d,%d,9,9"%(px-4,pz-4))
    alive=S.call("jawa/pawn_get", pawn=pid)
    print("KILL",k,pid,"at",px,pz,"spawn",r.get("success"),"dmg",d.get("success"),j(d.get("message"),120),"dead",alive.get("dead"),"filth",f0,"->",len(f1.get("things") or []))
print("weather1", j(S.call("jawa/weather_get"),900))
log=S.call("jawa/drain_log") if False else None
