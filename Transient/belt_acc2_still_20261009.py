import sys, json, collections
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
try:
    old = int(open("Transient/belt_acc2_ls_map_id.txt").read()); S.drop_map(old, 114480)
except Exception: pass
mid = S.biome_map(114480, "RM_Stillsand", size=75, keeper=(5, 5))
open("Transient/belt_acc2_ls_map_id.txt", "w").write(str(mid))
ps = S.call("jawa/list_pawns", limit=200).get("pawns") or []
print(collections.Counter(p["kind"] for p in ps), flush=True)
seen = {}
for p in ps:
    if p["kind"] in seen or p.get("isPlayer"): continue
    r = S.call("jawa/thing_graphic", thing=p["id"])
    seen[p["kind"]] = (r.get("success"), str(r.get("message"))[:120])
for k, v in seen.items(): print(k, v)
