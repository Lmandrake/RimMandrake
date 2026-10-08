import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rbc
host, port, token = rbc.resolve_endpoint()
with rbc.RimBridge(host, port, token, timeout=120.0) as rb:
    lp = rb.call("jawa/list_pawns", {"includeHealth": True, "limit": 200}, check=False)
rows=[]
for p in lp["pawns"]:
    if p["kind"]!="RM_TheUnfinished": continue
    hs=[(h["def"],h.get("partLabel")) for h in p["health"]["hediffs"] if h["def"].startswith("RM_Unfinished")]
    rows.append({"id":p["id"],"downed":p["downed"],"cons":p["health"]["capacities"].get("Consciousness"),"limbs":hs})
json.dump(rows,open(r"Transient\belt_a4_unfinished.json","w"),indent=0)
print(len(rows))
