import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    names = [t["name"] for t in rb.list_tools()]
    print([n for n in names if any(k in n for k in ("place","build","wall","spawn_batch"))][:10])
