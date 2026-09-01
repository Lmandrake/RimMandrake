import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
want = {"jawa/world_view","rimworld/get_ui_layout","rimworld/click_ui_target","rimworld/load_game","rimworld/load_game_ready","jawa/take_screenshot","jawa/clear_ui","rimworld/list_saves"}
with RimBridge(host, port, token) as rb:
    for d in rb.list_tools():
        if d.get("name") in want:
            print("###", d["name"], "|", (d.get("description") or "")[:400])
            print("   ", json.dumps(d.get("inputSchema"))[:900])
