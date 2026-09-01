import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

# Law 3 coefficient calibration: does K x bodySize blunt damage down an
# unarmored pawn at bull/muffalo bodySize 2.4, for K in {12, 13.5, 15}?
BODYSIZE = 2.4
KS = [12.0, 13.5, 15.0]

with RimBridge(host, port, token) as rb:
    results = []
    for k in KS:
        amount = round(k * BODYSIZE, 1)
        spawn = rb.call("jawa/spawn_pawn", {
            "kindDef": "Colonist", "x": 50, "z": 50, "faction": "player", "count": 3,
        })
        pawns = spawn.get("pawns") or spawn.get("spawned") or []
        ids = [p.get("id") or p.get("thingId") for p in pawns] if isinstance(pawns, list) else []
        if not ids:
            results.append({"k": k, "amount": amount, "error": "no pawn ids", "raw_spawn": spawn})
            continue
        for pid in ids:
            rb.call("jawa/pawn_gear", {"pawn": pid, "action": "clear", "clearWhat": "apparel"})
        row = {"k": k, "amount": amount, "hits": []}
        for pid in ids:
            dmg = rb.call("jawa/damage", {
                "damageDef": "Blunt", "amount": amount, "thingId": pid,
                "armorPenetration": 0.0, "allowColonists": True, "bodyPart": "Head",
            })
            targets = dmg.get("results") if isinstance(dmg, dict) else None
            t = targets[0] if targets else {}
            row["hits"].append({
                "pawn": pid,
                "damageDealt": t.get("totalDamageDealt"),
                "downed": t.get("downed"),
                "dead": t.get("dead"),
            })
        results.append(row)

print(json.dumps(results, indent=2, default=str))
