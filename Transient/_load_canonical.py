import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
print("endpoint", host, port)
with RimBridge(host, port, token) as rb:
    ui = rb.call("rimworld/get_ui_state", {})
    print("programState:", ui.get("programState"), "hasCurrentGame:", ui.get("hasCurrentGame"))
