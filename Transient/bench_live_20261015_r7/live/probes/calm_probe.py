"""r7 probe: where do the fleshbeasts at p2c's arm come from? fresh map -> proof_all.calm_map() -> list hostiles
(pawn_origin, incident journal, letters) BEFORE any save; then save/load and list again. No tick advance."""
import sys, os, json, time, argparse
ND = os.path.join(os.getcwd(), "src", "RimMandrake", "GimmeSomeSlack", "northstar")
sys.path.insert(0, ND)
import proof_all as PA
V = PA.V
B = PA.PB()
out = {}
def hostiles(tag):
    hp = B.call("jawa/list_pawns", faction="hostile", limit=200)
    ps = [p for p in hp.get("pawns") or [] if not p.get("dead")]
    ids = ",".join(str(p["id"]).lstrip("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_") for p in ps)
    org = B.call("jawa/pawn_origin", ids=ids) if ids else {}
    out[tag] = {"tick": B.call("rimworld/get_game_info").get("ticksGame"), "hostiles": [(p["id"], p.get("faction"), p.get("x"), p.get("z"), p.get("spawned")) for p in ps],
                "origin": org.get("pawns"), "notFound": org.get("notFound"),
                "journal": (B.call("jawa/incident_journal").get("rows") or [])[-10:],
                "letters": [(l.get("label"), l.get("def") or l.get("defName")) for l in (B.call("rimworld/list_letters").get("letters") or [])][-10:]}
    print(tag, json.dumps(out[tag])[:1500])
B.call("rimworld/go_to_main_menu")
B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
for _ in range(480):
    if B.call("rimworld/get_ui_state").get("programState") == "Playing" and B.call("jawa/map_info").get("success"): break
    time.sleep(0.5)
hostiles("fresh")
class P: pass
p = P(); p.B = B
G = PA._TG()
out["disarm"] = G.disarm_fog_triggers(B)
hb = [t for t in (B.call("jawa/list_things", group="BuildingArtificial", limit=5000).get("things") or [])
      if t.get("faction") and not str(t.get("faction")).startswith("Player") and t.get("x") is not None]
for t in hb:
    B.call("jawa/destroy_batch", rects="%d,%d,1,1" % (t["x"], t["z"]), categories="Building")
out["hostileBuildings"] = [t.get("def") for t in hb]
db = B.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False)
out["destroyed"] = sorted({x["def"] for x in db.get("destroyed") or []})
hostiles("after_destroy_bulk")
fg = B.call("jawa/fog_info") if False else None
out["fogged_things"] = B.call("jawa/list_things", group="Pawn", limit=500)
out["fog"] = G.clear_map_fog(B)
print("fog", json.dumps(out["fog"])[:300])
hostiles("after_calm")
name = "RM_r7_calmprobe_%s" % time.strftime("%Y%m%d%H%M%S")
B.call("rimworld/save_game", saveName=name); V._wait_saved(name)
hostiles("after_save")
B.call("rimworld/load_game", saveName=name); print("loaded", V._wait_playing(B))
hostiles("after_load")
json.dump(out, open(sys.argv[1], "w"), indent=1, default=str)
