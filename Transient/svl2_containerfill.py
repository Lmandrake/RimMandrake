import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for tool in ["jawa/container_fill", "jawa/battery_set"]:
        try:
            rb.call(tool, {"__bogus__": 1})
        except Exception as e:
            print(tool, "ERR", e)
