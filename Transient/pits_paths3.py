import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token, timeout=20) as rb:
    kids = rb.call("rimworld/list_debug_action_children", {"path": "Actions"})
    cats = kids.get("children", [])
    want = [c for c in cats if c.get("label") in (
        "T: PitCell: assign nearest prisoner",
        "T: PitCell: place assigned in cell",
        "T: PitCell: toggle gate",
        "T: PitCell: feed held captive",
        "T: Oiled: ignite (bypasses soaked/Sprung gate)",
        "T: Report pit state (RAW)",
        "T: Arm cover: woven scrap (40kg)",
        "Add Prisoner",
        "Spawn Pawn...",
        "Spawn thing...",
        "T: Set Faction",
    )]
    for c in want:
        print(json.dumps({k: c.get(k) for k in ("label","path","actionType")}))
