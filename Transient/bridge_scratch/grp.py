import sys, json, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for d in rb.list_tools():
        n=d.get("name","")
        if "group" in n or "raid_preview" in n:
            print("###", n, "|", (d.get("description") or "")[:350])
            print("   ", json.dumps(d.get("inputSchema"))[:700])
