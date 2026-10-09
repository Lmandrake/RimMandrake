import sys, json, collections
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
r = S.call("jawa/run_genstep", genStepDef="Animals"); print(r.get("success"), r.get("message"))
ps = S.call("jawa/list_pawns", limit=800).get("pawns") or []
print(collections.Counter(p["kind"] for p in ps).most_common(15))
ill = sorted((p["x"], p["z"]) for p in ps if p["kind"] == "RM_Illisk")
groups=[]
for c in ill:
    for g in groups:
        if any(abs(c[0]-d[0])<=10 and abs(c[1]-d[1])<=10 for d in g): g.append(c); break
    else: groups.append([c])
print("illisk", len(ill), "group sizes", [len(g) for g in groups])
