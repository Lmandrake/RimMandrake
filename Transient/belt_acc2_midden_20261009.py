import sys, json, collections
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
old = int(open("Transient/belt_acc2_ls_map_id.txt").read())
S.drop_map(old, 114480)
res = []
for attempt in range(3):
    mid = S.biome_map(114480, "RM_LongShade", size=120, keeper=(5, 5))
    S.quiet()
    l = S.call("jawa/list_things", defName="RM_LongShadeMidden", rect="0,0,120,120", limit=50)
    ms = l.get("things") or []
    res.append((attempt, mid, len(ms), [(m["x"], m["z"]) for m in ms]))
    print(res[-1], flush=True)
    if ms: break
    S.drop_map(mid, 114480)
if ms:
    open("Transient/belt_acc2_ls_map_id.txt", "w").write(str(mid))
    m = ms[0]
    print("comp", S.call("jawa/comp_read", thing=m["id"], comp="MiddenHeap", members="spent").get("values"))
    c = S.call("jawa/spawn_pawn", kindDef="Colonist", x=m["x"] + 2, z=m["z"], faction="player", count=1)["pawns"][0]["id"]
    o = S.call("jawa/ordered_job", pawnId=c, jobDef="RM_SearchMidden", targetAId=m["id"], waitTicks=900)
    print("order", json.dumps({k: o.get(k) for k in o if k not in ("operation", "state")}, default=str)[:500])
    S.run(600)
    print("comp after", S.call("jawa/comp_read", thing=m["id"], comp="MiddenHeap", members="spent").get("values"))
    near = S.call("jawa/list_things", rect="%d,%d,7,7" % (m["x"] - 3, m["z"] - 3), limit=40, includePawns=False).get("things") or []
    print("items near", collections.Counter(t.get("def") for t in near).most_common(10))
