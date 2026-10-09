import sys, json, collections
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
SET = "RimMandrake.LongShade.RM_LongShadeSettings"
mid = int(open("Transient/belt_acc3_tow_map_id.txt").read()); S.call("jawa/set_current_map", mapId=mid); S.quiet()
d = lambda **k: S.call("jawa/fire_incident", incidentDef="RUT_JawaReturnTow", dryRun=True, **k).get("canFireNow")
t = S.call("jawa/list_things", defName="ChunkSlagSteel", rect="74,147,25,9", limit=50)
ids = [x["id"] for x in t.get("things") or []]; print("chunks", ids)
if ids:
    r = S.call("jawa/destroy_batch", rects="74,147,25,9", categories="Item"); print("destroy", r.get("success"), str(r.get("message"))[:100])
print("dry forced/plain", d(forced=True), d(), flush=True)
S.call("jawa/mod_settings_field", typeName=SET, action="set", field="jawaReturnEnabled", value="false")
print("toggle off", d(forced=True), flush=True)
S.call("jawa/mod_settings_field", typeName=SET, action="set", field="jawaReturnEnabled", value="true")
f = S.call("jawa/fire_incident", incidentDef="RUT_JawaReturnTow", forced=True); print("fire", f.get("success"), f.get("fired"), str(f.get("message"))[:150], flush=True)
ps = S.call("jawa/list_pawns", limit=300).get("pawns") or []
print(collections.Counter((p["kind"], p.get("faction")) for p in ps).most_common(8))
print(S.call("jawa/map_comp_read", comp="CrawlerHull", members="entered,towStartTick,towed,towTicks")["values"])
