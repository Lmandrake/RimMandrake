import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
S.quiet()
def j(x,n=3000): return json.dumps(x,default=str)[:n]
r=S.call("jawa/get_defs", defs="ThingDef/AA_GreenGoo;ThingDef/AA_RedGoo;ThingDef/AA_AcanthamoebaGiganteaLarge;ThingDef/AA_AcanthamoebaGiganteaSmall;ThingDef/AA_RedSpore;ThingDef/AA_InfectedAerofleet;ThingDef/AA_Thunderbeast", fields="race", deep="true")
for d in r.get("defs") or r.get("results") or []:
    print("BURST", d.get("defName"), d.get("found"), j((d.get("fields") or {}).get("race",{}).get("deathAction") if isinstance((d.get("fields") or {}).get("race"),dict) else d.get("fields"),600))
print("BURST notFound", r.get("notFound"), "keys", list(r.keys())[:10])
r=S.call("jawa/get_defs", defs="ThingSetMakerDef/MapGen_AncientTempleContents", fields="root", deep="true")
print("RUINS", j(r,4000))
