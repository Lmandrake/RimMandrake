import sys, json, os
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
qs = json.load(open(sys.argv[1])); out={}
with RimBridge(h,p,t) as rb:
    for tag,defs,fields,deep in qs:
        try:
            a={"defs":defs}
            if fields: a["fields"]=fields
            if deep: a["deep"]=True
            r = rb.call("jawa/get_defs", a)
            if isinstance(r,dict) and r.get("content"):
                r=json.loads(r["content"][0]["text"])
            out[tag]=r
        except Exception as ex:
            out[tag]={"err":repr(ex)[:300]}
json.dump(out, open(sys.argv[2],"w"), indent=1, default=str)
