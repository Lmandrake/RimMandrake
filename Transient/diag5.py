import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    try:
        rb.call("jawa/set_thing_props", {"bogus": 1})
    except Exception as e:
        print("declared:", str(e).split("Declared:")[-1])
