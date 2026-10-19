import json,os,sys
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.join(HERE,"..","..","src","RimMandrake","Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
m=json.load(open(os.path.join(HERE,"..","..","design","RimMandrake","retired_mutators_port_map.json")))
want=[]
for t in("TileMutatorDef","LandmarkDef"):
    for k,v in m[t].items():
        if v.get("new"): want.append("%s/%s"%(t,v["new"]))
h,p,t=resolve_endpoint()
with RimBridge(h,p,t,timeout=120.0) as rb:
    r=rb.call("jawa/get_defs",{"defs":";".join(want),"fields":"defName,shortHash,label"})
json.dump({"requested":want,"result":r},open(os.path.join(HERE,"b_mutators_raw.json"),"w"),indent=1,default=str)
print(r.get("message"),r.get("notFound"),r.get("malformed"))
for d in r["defs"]: print(d["requested"],d.get("found"),d.get("fields",{}).get("shortHash"),d.get("packageId"))
