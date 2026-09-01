import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    # map size + a far corner probe
    info = rb.call("jawa/map_info", {}) if True else None
    print("map_info:", str(info)[:200])
