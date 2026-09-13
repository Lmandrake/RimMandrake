import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    try: rb.call("jawa/spawn_batch", {"zzz": 1})
    except Exception as e: print("spawn_batch:", str(e).split("Declared:")[-1].strip())
