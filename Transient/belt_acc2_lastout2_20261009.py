import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
dz = [p for p in S.call("jawa/list_pawns", limit=100).get("pawns", []) if p["kind"] == "RM_Drazzik"][0]["id"]
def ins(i): return json.dumps(S.call("jawa/inspect_string", thingIds=i).get("things"), default=str)[:350]
print("0", ins(dz), flush=True)
for k in range(4):
    S.run(400); print(k, ins(dz), flush=True)
