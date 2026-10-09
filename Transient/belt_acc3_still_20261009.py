import sys, json, time, collections
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
mid = S.biome_map(114480, "RM_Stillsand", size=100, keeper=(50, 50))
open("Transient/belt_acc3_still_map_id.txt", "w").write(str(mid))
for dx in (3, -3, 6):
    S.call("jawa/spawn_pawn", kindDef="Colonist", x=50+dx, z=52, faction="player", count=1)
ps = S.call("jawa/list_pawns", limit=300).get("pawns") or []
print("map", mid, collections.Counter(p["kind"] for p in ps), flush=True)
t0 = S.ticks()
for i in range(3):
    n = S.run(1000)
    print("chunk", i, "ran", n, "ticks now", S.ticks(), flush=True)
print("TOTAL", S.ticks() - t0, flush=True)
