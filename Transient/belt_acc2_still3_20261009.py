import sys, json, time
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
size = int(sys.argv[1])
mid = S.biome_map(114480, "RM_Stillsand", size=size, keeper=(5, 5))
print("generated", size, mid, flush=True)
for i in range(8):
    time.sleep(2)
    r = S.call("jawa/map_info"); print(i, r.get("success"), flush=True)
