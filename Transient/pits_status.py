import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token, timeout=15) as rb:
    for tool in ["rimworld/list_colonists", "rimworld/get_camera_state"]:
        try:
            r = rb.call(tool, {})
            print(f"=== {tool} ===")
            print(json.dumps(r, indent=2)[:1200])
        except Exception as e:
            print(tool, "EXC", e)
