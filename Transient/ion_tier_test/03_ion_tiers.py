import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
OUT = r"D:\Luke\dev\Rimworld\Transient\ion_tier_test\tiers_result.json"
DAMAGE_DEF = "JawaIon_Damage"
CX, CZ = 125, 125  # map center, mapSize 250, away from the crashlanded colonists

out = {}

with RimBridge(host, port, token, timeout=30) as rb:
    # --- Tier 1: machine, fresh Mech_Scyther ---
    sp = rb.call("jawa/spawn_pawn", {"kindDef": "Mech_Scyther", "x": CX, "z": CZ,
                                      "faction": "hostile", "count": 1}, check=False)
    out["spawn_mech"] = sp
    mech_id = sp["pawns"][0]["id"] if sp.get("pawns") else None
    if mech_id:
        d = rb.call("jawa/damage", {"damageDef": DAMAGE_DEF, "amount": 8,
                                     "thingId": mech_id}, check=False)
        out["damage_mech"] = d
        lp = rb.call("jawa/list_pawns", {}, check=False)
        out["mech_after"] = next((p for p in lp.get("pawns", []) if p["id"] == mech_id), None)

with RimBridge(host, port, token, timeout=30) as rb:
    # --- Tier 2: droid, fresh OuterRim_BattleDroid ---
    sp = rb.call("jawa/spawn_pawn", {"kindDef": "OuterRim_BattleDroid", "x": CX + 5, "z": CZ,
                                      "faction": "hostile", "count": 1}, check=False)
    out["spawn_droid"] = sp
    droid_id = sp["pawns"][0]["id"] if sp.get("pawns") else None
    if droid_id:
        d = rb.call("jawa/damage", {"damageDef": DAMAGE_DEF, "amount": 8,
                                     "thingId": droid_id}, check=False)
        out["damage_droid"] = d
        lp = rb.call("jawa/list_pawns", {}, check=False)
        out["droid_after"] = next((p for p in lp.get("pawns", []) if p["id"] == droid_id), None)

with RimBridge(host, port, token, timeout=30) as rb:
    # --- Tier 3: flesh, 6x Tribal_Warrior, 6 hits @8 each on ONE of them ---
    sp = rb.call("jawa/spawn_pawn", {"kindDef": "Tribal_Warrior", "x": CX - 5, "z": CZ,
                                      "faction": "hostile", "count": 1}, check=False)
    out["spawn_tribal"] = sp
    tribal_id = sp["pawns"][0]["id"] if sp.get("pawns") else None
    hits = []
    if tribal_id:
        for i in range(6):
            d = rb.call("jawa/damage", {"damageDef": DAMAGE_DEF, "amount": 8,
                                         "thingId": tribal_id}, check=False)
            hits.append(d)
        lp = rb.call("jawa/list_pawns", {}, check=False)
        out["tribal_after"] = next((p for p in lp.get("pawns", []) if p["id"] == tribal_id), None)
    out["damage_tribal_hits"] = hits

with open(OUT, "w") as f:
    json.dump(out, f, indent=2, default=str)

print(json.dumps(out, indent=2, default=str))
