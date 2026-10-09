import sys, json, time
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
LOG = r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log"
def cnt(): return open(LOG, encoding="utf-8", errors="ignore").read().count("Root level exception")
print("maps", json.dumps(S.call("rimworld/get_game_info"), default=str)[:300])
mi = S.call("jawa/map_info"); print("cur map", mi.get("mapId"), mi.get("mapBiome"), "exc", cnt())
d = S.call("jawa/map_drop", mapIndex=1, notifyPlayer=False); print("drop", json.dumps(d, default=str)[:300])
time.sleep(2); print("exc after drop", cnt())
