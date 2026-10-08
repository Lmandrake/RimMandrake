import sys, json, os
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
calls = json.load(open(sys.argv[1])); out=[]
with RimBridge(h,p,t) as rb:
    for tool,args in calls:
        try:
            r = rb.call(tool, args)
            if isinstance(r,dict) and r.get("content"):
                try: r=json.loads(r["content"][0]["text"])
                except Exception: pass
            out.append({"tool":tool,"args":args,"result":r})
        except Exception as ex:
            out.append({"tool":tool,"args":args,"err":repr(ex)[:300]})
json.dump(out, open(sys.argv[2],"w"), indent=1, default=str)
