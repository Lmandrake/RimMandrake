import sys, json, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
want = {"jawa/world_view","rimworld/get_ui_layout","rimworld/load_game","rimworld/load_game_ready","jawa/take_screenshot","rimworld/list_saves"}
with RimBridge(host, port, token) as rb:
    for d in rb.list_tools():
        if d.get("name") in want:
            print("###", d["name"], "|", (d.get("description") or "")[:500])
            print("   SCHEMA:", json.dumps(d.get("inputSchema"))[:1200])
