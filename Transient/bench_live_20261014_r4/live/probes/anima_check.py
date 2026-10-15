# ANIMA_TREE_FIX_TAKES_THE_SIDE_DOOR A1: fresh quicktest home map -> Plant_TreeAnima census, Base_Player genSteps,
# and a 100-day storyteller simulation (StorytellerUtility.DebugLogTestFutureIncidents -> Player.log).
import sys, os, json, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
h, p, t = resolve_endpoint(); out = {}
def c(rb, tool, **a):
    r = rb.call(tool, a)
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r or {}
with RimBridge(h, p, t, timeout=600.0) as rb:
    if "--no-new-map" not in sys.argv:
        out["menu"] = c(rb, "rimworld/go_to_main_menu").get("success")
        out["start"] = c(rb, "rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000).get("success")
        for _ in range(120):
            if c(rb, "rimworld/get_ui_state").get("programState") == "Playing": break
            time.sleep(1)
    gi = c(rb, "rimworld/get_game_info"); out["game"] = {k: gi.get(k) for k in ("ticksGame", "mapCount", "currentMap", "storyteller", "biome") if k in gi}
    out["anima_things"] = c(rb, "jawa/list_things", defName="Plant_TreeAnima", limit=10)
    out["control_trees"] = {k: v for k, v in c(rb, "jawa/list_things", defName="Plant_TreeOak,Plant_TreePine,Plant_TreeBirch,Plant_TreePoplar", limit=1).items() if k != "things"}
    out["base_player"] = c(rb, "jawa/get_defs", defs="MapGeneratorDef/Base_Player", fields="genSteps")
    out["incdef"] = c(rb, "jawa/get_defs", defs="IncidentDef/AnimaTreeSpawn;GenStepDef/AnimaTrees;ThingDef/Plant_TreeAnima")
    out["comps"] = c(rb, "jawa/storyteller_comps", find="AnimaTreeSpawn")
json.dump(out, open(os.path.join(os.path.dirname(__file__), "anima_check.json"), "w"), indent=1, default=str)
print(json.dumps(out, default=str)[:3000])
