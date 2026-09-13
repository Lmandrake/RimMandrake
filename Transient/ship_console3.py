import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    c = rb.call("jawa/build_check", {"def": "PilotConsole", "rect": "184,150,1,1", "rot": 0})
    print("check:", str({k: c.get(k) for k in ("success","ok","buildable","message")})[:200])
    b = rb.call("jawa/build_batch", {"ops": "PilotConsole:184,150,0", "faction": "player", "readBack": 1})
    print("build:", b.get("success"), "placed:", b.get("placed"), str(b.get("failed",""))[:150])
    rb.call("jawa/map_commit", {})
    chk = rb.call("jawa/list_things", {"defName": "PilotConsole", "rect": "143,59,86,133", "limit": 3})
    print("console:", chk.get("things", []))
