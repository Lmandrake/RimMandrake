import sys, json, os
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
with RimBridge(h,p,t) as rb:
    names = sorted(x.get("name") for x in rb.list_tools())
json.dump(names, open("Transient/l1sweep_toolnames.json","w"))
print(len(names))
