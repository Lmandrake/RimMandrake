import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
CH = chr(92)
OUT = r"D:\Luke\dev\Rimworld\Transient\dw_personality_verify_full.json"

FAMILIES = {
    "labour":   "RSW_DW_OuterRim_ImperialLaborDroid",
    "protocol": "RSW_DW_OuterRim_ProtocolDroid",
    "astromech":"RSW_DW_OuterRim_RSeriesDroid",
    "battle":   "RSW_DW_OuterRim_BattleDroid",
    "heavy":    "RSW_DW_OuterRim_SuperTacticalDroid",
    "probe":    "RSW_DW_KotORDroidColonist_KX12UPD",
    "power":    "RSW_DW_OuterRim_GNKDroid",
    "primitive":"RSW_DW_Primitive_G2",
}
EXPECTED_TRAIT = {
    "labour": "Industriousness", "protocol": "Abrasive", "astromech": "TooSmart",
    "battle": "ShootingAccuracy", "heavy": "Tough", "probe": "GreatMemory",
    "power": "Nerves", "primitive": "SlowLearner",
}
N_PER_FAMILY = 3

def call(rb, tool, args=None, label=None):
    r = rb.call(tool, args or {})
    print(f"--- {label or tool} --- success={r.get('success')}")
    return r

results = {"spawns": {}}
with RimBridge(host, port, token) as rb:
    x0, z0 = 100, 100
    idx = 0
    for fam, kind in FAMILIES.items():
        results["spawns"][fam] = []
        for i in range(N_PER_FAMILY):
            x, z = x0 + (idx % 10) * 2, z0 + (idx // 10) * 2
            idx += 1
            path = "Actions" + CH + "Spawn Pawn..." + CH + kind
            r = rb.call("rimworld/execute_debug_action", {"path": path, "x": x, "z": z})
            logs = r.get("effects", {}).get("logs", [])
            results["spawns"][fam].append({"x": x, "z": z, "success": r.get("success"), "logs": logs})
        print(f"spawned {N_PER_FAMILY} of {fam} ({kind})")

    time.sleep(1)
    r = rb.call("jawa/list_pawns", {})
    results["list_pawns"] = r

with open(OUT, "w") as f:
    json.dump(results, f, indent=1)
print("wrote", OUT)

pawns = results["list_pawns"].get("pawns", [])
by_kind = {}
for p in pawns:
    by_kind.setdefault(p.get("kindDef"), []).append(p)

print("\n=== spawned counts by ACTUAL kindDef (checking substitution trap) ===")
for fam, kind in FAMILIES.items():
    actual = by_kind.get(kind, [])
    print(f"{fam:10s} requested={kind:35s} actual_count={len(actual)} (expected {N_PER_FAMILY})")
