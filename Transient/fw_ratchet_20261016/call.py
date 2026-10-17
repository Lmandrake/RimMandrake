import sys,json
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, "src/RimMandrake/Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t=resolve_endpoint()
lim=int(sys.argv[3]) if len(sys.argv)>3 else 6000
with RimBridge(h,p,t) as rb:
    r=rb.call(sys.argv[1], json.loads(sys.argv[2]) if len(sys.argv)>2 else {})
    print(json.dumps(r)[:lim])
