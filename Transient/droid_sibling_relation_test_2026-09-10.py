import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
KINDS = ["RSW_DW_OuterRim_ProtocolDroid", "RSW_DW_KotORDroidColonist_KX12UPD"]

with RimBridge(host, port, token, timeout=60.0) as rb:
    cam = rb.call("rimworld/get_camera_state", {})
    print("camera", json.dumps(cam)[:300])
    cx = int(cam.get("x", 100)); cz = int(cam.get("z", 100))

    kids = rb.call("rimworld/list_debug_action_children", {"path": "Actions"})["children"]
    spawn_node = next(c["path"] for c in kids if "Spawn Pawn" in c["path"])
    print("spawn node:", spawn_node)

    grandkids = rb.call("rimworld/list_debug_action_children", {"path": spawn_node})["children"]
    paths_by_kind = {}
    for kind in KINDS:
        match = next((c["path"] for c in grandkids if kind in c["path"]), None)
        paths_by_kind[kind] = match
        print(kind, "->", match)

    results = {k: {"spawned": 0, "errors": []} for k in KINDS}
    for kind in KINDS:
        p = paths_by_kind[kind]
        if not p:
            results[kind]["errors"].append("NO DEBUG ACTION PATH FOUND")
            continue
        for i in range(10):
            x = cx + (i % 5) * 2
            z = cz + (i // 5) * 2
            r = rb.call("rimworld/execute_debug_action", {"path": p, "x": x, "z": z})
            eff = r.get("effects", {}) or {}
            logs = eff.get("logs", [])
            if r.get("success"):
                results[kind]["spawned"] += 1
            if logs:
                results[kind]["errors"].extend(logs)

    print(json.dumps(results, indent=2)[:4000])
