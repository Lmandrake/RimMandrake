import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,tk = resolve_endpoint()
keep = set(sys.argv[1].split(",")) if len(sys.argv)>1 else set()
with RimBridge(h,p,tk) as rb:
    r = rb.call("jawa/site_state", {})
    for q in r.get("pawns") or []:
        if q.get("faction")=="PlayerColony" and q["id"] not in keep or "Flamefang" in q["id"] or "Fox" in q["id"]:
            print(q["id"], q.get("x"), q.get("z"), q.get("job"), q.get("downed"))
    for pid in sys.argv[2].split(",") if len(sys.argv)>2 else []:
        q = next((q for q in r["pawns"] if q["id"]==pid), None)
        if q: print("clear", pid, rb.call("jawa/clear_area", {"rect":"%d,%d,1,1"%(q["x"],q["z"]),"dryRun":False}).get("success"))
