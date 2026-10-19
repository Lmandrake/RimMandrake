import json, os, sys
UT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "src", "RimMandrake", "Utils")
sys.path.insert(0, UT)
from rimbridge_client import RimBridge, resolve_endpoint
h, p, t = resolve_endpoint()
tool = sys.argv[1]; params = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
with RimBridge(h, p, t, timeout=float(os.environ.get("TO", "120"))) as rb:
    try:
        r = rb.call(tool, params)
    except Exception as ex:
        print("RAISED", type(ex).__name__, str(ex)[:2000]); sys.exit(2)
s = json.dumps(r, indent=1, default=str)
print(s[:int(os.environ.get("MAX", "4000"))])
