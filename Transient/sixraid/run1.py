import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

def p(tag, o):
    print("=====", tag)
    print(json.dumps(o, indent=1, default=str)[:5000])

host, port, token = resolve_endpoint()
F = "Jawa_FreeDroidEnclaves"
with RimBridge(host, port, token) as rb:
    p("colonists", rb.call("rimworld/list_colonists", {"currentMapOnly": True}))
    p("set_hostile", rb.call("jawa/set_faction_relation", {"faction": F, "goodwill": -100}))
    p("drain_pre", rb.call("jawa/drain_log", {}))
    p("dry", rb.call("jawa/fire_raid", {"points": 3000, "faction": F, "dryRun": True}))
