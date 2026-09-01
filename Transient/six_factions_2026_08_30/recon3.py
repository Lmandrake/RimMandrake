import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
WANT = ["jawa/pawnkind_audit","jawa/raid_preview","jawa/incident_parms_preview","jawa/storyteller_fire",
        "jawa/forecast_incidents","jawa/faction_ideo_get","jawa/ideo_of","jawa/list_factions",
        "jawa/fire_raid","jawa/manhunter_preview","jawa/lord_assault_spawn","jawa/set_pawn_xenotype",
        "jawa/incident_schedule","jawa/harmony_patches","jawa/get_def"]
with RimBridge(host, port, token) as rb:
    for t in rb.list_tools():
        if t["name"] in WANT:
            print("###", t["name"])
            print("  desc:", (t.get("description") or "")[:400])
            sch = t.get("inputSchema") or t.get("input_schema") or {}
            print("  props:", json.dumps(sch.get("properties", {}))[:700])
            print("  req:", sch.get("required"))
