import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
CH = chr(92)

def call(rb, tool, args=None, label=None):
    r = rb.call(tool, args or {})
    print(f"--- {label or tool} ---")
    print(json.dumps(r)[:1200])
    return r

with RimBridge(host, port, token) as rb:
    X, Z = 126, 124

    spawn_path = "Actions" + CH + "Spawn Pawn..." + CH + "RSW_DW_KotORDroidColonist_T3UD"
    r = call(rb, "rimworld/execute_debug_action", {"path": spawn_path, "x": X, "z": Z}, "spawn droid")

    time.sleep(1)
    r = call(rb, "jawa/list_pawns", {}, "list_pawns after spawn")
    pawns = r.get("pawns", [])
    droid = None
    for p in pawns:
        if p.get("def", "").startswith("RSW_DW_KotOR") or "T3UD" in (p.get("kindDef") or ""):
            droid = p
    print("droid found:", droid)
