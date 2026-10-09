import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
d=S.call("jawa/ideo_of")
for i in d["ideos"]: print(i["id"], i["name"], i.get("initialPlayerIdeo"), i.get("isPlayerIdeo"), i.get("playerBelievers"), [k for k in i if "layer" in k])
pg = (S.call("jawa/pawn_get", pawn="Human25450").get("pawns") or [{}])[0]; print({k:v for k,v in pg.items() if "deo" in k})
