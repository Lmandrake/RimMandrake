import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    try:
        rb.call("jawa/thing_stats", {"bogus":1})
    except Exception as e:
        print("declared:", str(e).split("Declared:")[-1].strip()[:100])
    r = rb.call("jawa/thing_stats", {"thing": "Turret_Zapper79712"})
    print(json.dumps(r)[:600])
