import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
CH = chr(92)
OUT = r"D:\Luke\dev\Rimworld\Transient\dw_module_single_clean_full.json"

def call(rb, tool, args=None, label=None):
    r = rb.call(tool, args or {})
    print(f"--- {label or tool} --- success={r.get('success')}")
    return r

results = {}
with RimBridge(host, port, token) as rb:
    X, Z = 130, 128
    spawn_path = "Actions" + CH + "Spawn Pawn..." + CH + "RSW_DW_KotORDroidColonist_T3UD"
    call(rb, "rimworld/execute_debug_action", {"path": spawn_path, "x": X, "z": Z}, "spawn fresh droid")
    time.sleep(1)

    r = rb.call("jawa/list_pawns", {})
    droid = None
    for p in r.get("pawns", []):
        if p.get("kindDef") == "RSW_DW_KotORDroidColonist_T3UD" and p.get("x") == X:
            droid = p
    DROID_ID = droid["id"]
    DROID_THING_ID = "Thing_" + DROID_ID
    print("droid:", DROID_ID)

    call(rb, "jawa/set_pawn_faction", {"pawn": DROID_ID, "faction": "PlayerColony"}, "set_pawn_faction")
    call(rb, "rimworld/select_pawn", {"pawnId": DROID_THING_ID}, "select_pawn")

    results["before"] = call(rb, "jawa/pawn_get", {"pawn": DROID_ID}, "pawn_get BEFORE (fresh droid)")

    wear_path = "Actions" + CH + "Wear apparel (selected)..." + CH + "RSW_DW_Module_DroidHardware_agility"
    results["wear"] = call(rb, "rimworld/execute_debug_action", {"path": wear_path}, "wear hardware ONLY")
    time.sleep(0.5)

    results["after_wear"] = call(rb, "jawa/pawn_get", {"pawn": DROID_ID}, "pawn_get AFTER wear")

    remove_path = "Actions" + CH + "Wear apparel (selected)..." + CH + "*Remove all apparel"
    results["remove"] = call(rb, "rimworld/execute_debug_action", {"path": remove_path}, "remove all apparel")
    time.sleep(0.5)

    results["after_remove"] = call(rb, "jawa/pawn_get", {"pawn": DROID_ID}, "pawn_get AFTER remove")

with open(OUT, "w") as f:
    json.dump(results, f, indent=1)
print("wrote", OUT)

def summarize(pg):
    p = pg.get("pawns", [{}])[0]
    return {
        "apparel": p.get("apparel"),
        "hediffs": [h.get("def") for h in (p.get("hediffs") or [])],
    }

print("BEFORE:", summarize(results["before"]))
print("AFTER WEAR (hardware only):", summarize(results["after_wear"]))
print("AFTER REMOVE:", summarize(results["after_remove"]))
print("wear logs:", results["wear"].get("effects", {}).get("logs", []))
