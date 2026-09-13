import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
CH = chr(92)
DROID_ID = "RSW_DW_Race_guy762_DroidRace_T3series39455"
DROID_THING_ID = "Thing_" + DROID_ID
OUT = r"D:\Luke\dev\Rimworld\Transient\dw_module_personality_full.json"

def call(rb, tool, args=None, label=None):
    r = rb.call(tool, args or {})
    print(f"--- {label or tool} --- success={r.get('success')}")
    return r

results = {}
with RimBridge(host, port, token) as rb:
    call(rb, "rimworld/select_pawn", {"pawnId": DROID_THING_ID}, "select_pawn")
    results["before"] = call(rb, "jawa/pawn_get", {"pawn": DROID_ID}, "pawn_get BEFORE wear")

    wear_path = "Actions" + CH + "Wear apparel (selected)..." + CH + "RSW_DW_Module_DroidHardware_agility"
    results["wear"] = call(rb, "rimworld/execute_debug_action", {"path": wear_path}, "wear module")

    time.sleep(1)
    results["after_wear"] = call(rb, "jawa/pawn_get", {"pawn": DROID_ID}, "pawn_get AFTER wear")

    remove_path = "Actions" + CH + "Wear apparel (selected)..." + CH + "*Remove all apparel"
    results["remove"] = call(rb, "rimworld/execute_debug_action", {"path": remove_path}, "remove apparel")

    time.sleep(1)
    results["after_remove"] = call(rb, "jawa/pawn_get", {"pawn": DROID_ID}, "pawn_get AFTER remove")

with open(OUT, "w") as f:
    json.dump(results, f, indent=1)
print("wrote", OUT)

def hediff_names(pg):
    p = pg.get("pawns", [{}])[0]
    hd = p.get("hediffs") or []
    return [h.get("def") or h.get("defName") for h in hd]

def apparel_names(pg):
    p = pg.get("pawns", [{}])[0]
    return p.get("apparel") or p.get("wornApparel")

print("apparel before:", apparel_names(results["before"]))
print("hediffs before:", hediff_names(results["before"]))
print("apparel after wear:", apparel_names(results["after_wear"]))
print("hediffs after wear:", hediff_names(results["after_wear"]))
print("apparel after remove:", apparel_names(results["after_remove"]))
print("hediffs after remove:", hediff_names(results["after_remove"]))
