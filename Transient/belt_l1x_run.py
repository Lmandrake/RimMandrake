import sys, json, re
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rbc
host,port,token=rbc.resolve_endpoint()
m=json.load(open("Transient/foundry_l1x_manifest.json"))
out=[]
with rbc.RimBridge(host,port,token) as rb:
    for x in m:
        defs=[re.sub(r"\s*\(.*\)$","",d) for d in x["defs"]]
        r=rb.call("jawa/get_defs",{"defs":";".join(defs)},check=False)
        out.append({"item":x["item"],"criterion":x["criterion"],"asked":len(defs),"success":r.get("success"),"foundCount":r.get("foundCount"),"notFound":r.get("notFound"),"message":(r.get("message") or "")[:200]})
json.dump(out,open("Transient/foundry_l1x_results_20261008.json","w"),indent=1)
for o in out: print(o["item"],o["criterion"],o["success"],o["foundCount"],"/",o["asked"],o["notFound"])
