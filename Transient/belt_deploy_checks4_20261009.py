import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
def show(tag, r):
    print(tag, "|", json.dumps(r, default=str)[:1200]); sys.stdout.flush()
mi=S.call("jawa/map_info"); print("MAPINFO_BEFORE", json.dumps({k:v for k,v in mi.items() if 'ondition' in k or 'eather' in k},default=str)[:500])
with S.Scene("burst_tb", 30, 30, 30, 30) as sc:
    pid = sc.pawn("AA_Thunderbeast", 15, 15)
    show("DMG", S.call("jawa/damage", damageDef="Bomb", amount=5000, thingId=pid))
    S.run(60)
    mi=S.call("jawa/map_info"); print("MAPINFO_AFTER", json.dumps({k:v for k,v in mi.items() if 'ondition' in k or 'eather' in k},default=str)[:800])
    show("WEATHER", S.call("jawa/weather_get"))
