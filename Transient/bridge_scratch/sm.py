import sys, json, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for d in rb.list_tools():
        if d["name"] in ("jawa/screenshot_mode","rimworld/screenshot_cell_rect"):
            print("###", d["name"], "|", (d.get("description") or "")[:300])
            print("  ", json.dumps(d.get("inputSchema"))[:600])
