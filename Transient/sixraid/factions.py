import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    # find the right tool names
    tools = rb.call("rimbridge/list_tools", {}) if False else None
    for name in ("rimworld/list_factions", "jawa/list_factions", "jawa/raid_preview"):
        try:
            r = rb.call(name, {})
            print("====", name)
            print(json.dumps(r, indent=1)[:6000])
        except Exception as e:
            print("====", name, "ERR", e)
