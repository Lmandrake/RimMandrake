import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token, timeout=20) as rb:
    colonists = rb.call("rimworld/list_colonists", {})["colonists"]
    for c in colonists:
        print(c["name"], c.get("mentalState"), c.get("job"))
