import sys, json, os
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
h, p, t = resolve_endpoint()
out={}
with RimBridge(h, p, t) as rb:
    for tool,args in [("jawa/pawn_origin",{"ids":sys.argv[1]}),("jawa/incident_journal",{}),("rimworld/list_letters",{}) ]:
        try: out[tool]=rb.call(tool,args)
        except Exception as e: out[tool]={"err":repr(e)}
json.dump(out,open(sys.argv[2],"w"),indent=1)
for k,v in out.items(): print(k, json.dumps(v)[:900])
