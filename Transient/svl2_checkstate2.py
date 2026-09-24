import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    ci = rb.call("rimworld/get_cell_info", {"x": 0, "z": 0})
    print("STATE", json.dumps(ci.get("state"))[:600])
    letters = rb.call("jawa/letter_list", {})
    print("LETTERS", json.dumps(letters)[:3000])
