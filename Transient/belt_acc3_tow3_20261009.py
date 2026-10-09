import sys, json, collections
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
SET = "RimMandrake.LongShade.RM_LongShadeSettings"
mid = int(open("Transient/belt_acc3_tow_map_id.txt").read()); S.call("jawa/set_current_map", mapId=mid); S.quiet()
H = lambda: S.call("jawa/map_comp_read", comp="CrawlerHull", members="hullCenter,entered,towStartTick,towed")["values"]
d = lambda **k: S.call("jawa/fire_incident", incidentDef="RUT_JawaReturnTow", dryRun=True, **k)
print("before entry", H(), "dry", d(forced=True).get("canFireNow"), flush=True)
cx, cz = 86, 151
r = S.call("jawa/spawn_pawn", kindDef="Colonist", x=cx, z=cz, faction="player", count=1); print("colonist in hull", r.get("success"))
S.call("jawa/kill_hostiles")
S.run(240)
print("after entry", H(), flush=True)
print("dry forced/plain", d(forced=True).get("canFireNow"), d().get("canFireNow"), flush=True)
S.call("jawa/mod_settings_field", typeName=SET, action="set", field="jawaReturnEnabled", value="false")
print("toggle off dry forced", d(forced=True).get("canFireNow"), flush=True)
S.call("jawa/mod_settings_field", typeName=SET, action="set", field="jawaReturnEnabled", value="true")
b0 = S.call("jawa/list_things", rect="%d,%d,25,9" % (cx-12, cz-4), limit=400)
print("things in hull rect before", b0.get("count", b0.get("total")), flush=True)
f = S.call("jawa/fire_incident", incidentDef="RUT_JawaReturnTow", forced=True); print("fire", f.get("success"), f.get("fired"), str(f.get("message"))[:150], flush=True)
ps = S.call("jawa/list_pawns", limit=300).get("pawns") or []
print([(p["kind"], p.get("faction")) for p in ps if "Jawa" in str(p.get("kind")) or "Jawa" in str(p.get("faction"))][:8])
print("hull", H())
