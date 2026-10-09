import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
mid = int(open("Transient/belt_acc2_ls_map_id.txt").read())
S.call("jawa/set_current_map", mapId=mid)
l = S.call("jawa/list_things", defName="RM_LongShadeCleanPatch", rect="0,0,100,100", limit=3)
t = l.get("things", [])
print(len(t), [x["id"] for x in t])
if t: print(json.dumps(S.call("jawa/inspect_string", thingIds=t[0]["id"]).get("things"), default=str)[:300])
ps = S.call("jawa/list_pawns", limit=300).get("pawns") or []
print([ (p["kind"], p["x"], p["z"]) for p in ps if p["kind"] in ("RM_Mirrak","RM_Gulloth")][:6])
# stampede: heat
print(S.call("jawa/game_condition", action="start", condition="HeatWave", durationTicks=30000).get("success"))
S.run(600)
mi = S.call("jawa/map_info"); print("outdoorTemp", mi.get("outdoorTempNow"))
rn = [p for p in ps if p["kind"] == "RSW_Runyip"]
print("runyip", len(rn))
if rn:
    print(S.call("jawa/thing_ambient_temp", thing=rn[0]["id"]).get("ambient"))
fi = S.call("jawa/fire_incident", incidentDef="RM_ShadeStampede", dryRun=True)
print(fi.get("canFireNow"), fi.get("message"))
