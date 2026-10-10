import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
mid=S.biome_map(int(sys.argv[1]), "AridShrubland", size=200, keeper=(100,190))
print("MAP", mid, json.dumps(S.call("jawa/map_info"),default=str)[:300])
