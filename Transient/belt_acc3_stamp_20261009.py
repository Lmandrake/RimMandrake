import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
mid=S.biome_map(114507,"RM_LongShade",size=75)
print("biome",S.call("jawa/map_info").get("mapBiome"),"temp",S.call("jawa/map_info").get("outdoorTempNow"))
print(json.dumps(S.call("jawa/get_defs",defs="IncidentDef/RM_ShadeStampede"))[:150])
S.call("jawa/kill_hostiles")
sc=S.Scene("stamp",30,30,7,7); sc.__enter__()
sc.room(roof=True)
print("area",json.dumps(S.call("jawa/map_zones",action="paintArea",area="Home",rect=sc.rect,value=True))[:200])
sc.colonist(3,3)
r=S.call("jawa/spawn_pawn",kindDef="RM_Chorn",x=60,z=60,faction="none",count=8); print("spawn",r.get("spawnedCount"),r.get("failedCount"))
def dry(tag):
    r=S.call("jawa/fire_incident",incidentDef="RM_ShadeStampede",dryRun=True); print(tag,json.dumps({k:r.get(k) for k in ("success","canFireNow","message")})[:300])
dry("herd+roof")
ch=[p for p in S.call("jawa/list_pawns",rect="55,55,10,10",limit=20).get("pawns",[]) if "Chorn" in str(p.get("kindDef") or p.get("def") or "")]
print("chorn",len(ch), "temp at chorn", S.call("jawa/cell_temperature",cell="60,60").get("temperature"))
with S.setting("RimMandrake.LongShade.RM_LongShadeSettings",stampedeEnabled=False):
    dry("setting off")
dry("on again")
