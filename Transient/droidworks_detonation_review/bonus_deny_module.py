import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
SPAWN_PAWN = "Actions\\Spawn Pawn..."

bonus = [
    {"cell": "DenyModule_control_OuterRim_Battle_d0_charge50",
     "kind": "RSW_DW_OuterRim_BattleDroid", "charge": 0.5, "x": 40, "z": 115,
     "expect": "NO explosion (density 0, no deliberateDenyModule)"},
    {"cell": "DenyModule_JDS_Battle_denyTrue_charge50",
     "kind": "RSW_DW_JDSCIS_B1_Battle_Droid", "charge": 0.5, "x": 65, "z": 115,
     "expect": "EXPLOSION (density 0 base, deliberateDenyModule raises floor to 1)"},
]

with RimBridge(host, port, token) as rb:
    kids = rb.call("rimworld/list_debug_action_children", {"path": SPAWN_PAWN})["children"]
    kind_set = set(b["kind"] for b in bonus)
    leaf_by_kind = {c["path"].split(chr(92))[-1]: c["path"] for c in kids
                    if c["path"].split(chr(92))[-1] in kind_set}
    print("leaves:", leaf_by_kind)

    for cell in bonus:
        path = leaf_by_kind[cell["kind"]]
        r = rb.call("rimworld/execute_debug_action", {"path": path, "x": cell["x"], "z": cell["z"]})
        print(cell["cell"], "spawn ->", json.dumps(r)[:150])

    # locate the two new pawns by listing mode
    pg = rb.call("jawa/pawn_get", {"pawn": "", "limit": 80})
    by_kind_pos = {}
    for row in pg["pawns"]:
        by_kind_pos.setdefault(row["kindDef"], []).append(row)

    for cell in bonus:
        candidates = by_kind_pos.get(cell["kind"], [])
        match = next((r for r in candidates if r["x"] == cell["x"] and r["z"] == cell["z"]), None)
        if match is None:
            print("NO MATCH for", cell["cell"])
            continue
        cell["pawnId"] = match["thingId"]
        print(cell["cell"], "-> pawnId", match["thingId"])

    for cell in bonus:
        if "pawnId" not in cell:
            continue
        r = rb.call("jawa/pawn_need", {"pawn": cell["pawnId"], "action": "need",
                                        "need": "RSW_DW_Power", "level": cell["charge"]})
        print(cell["cell"], "set need ->", json.dumps(r)[:150])

    for cell in bonus:
        if "pawnId" not in cell:
            continue
        r = rb.call("jawa/damage", {"damageDef": "Bomb", "amount": 2000, "thingId": cell["pawnId"]})
        print(cell["cell"], "damage ->", json.dumps(r)[:150])
        rectstr = "%d,%d,%d,%d" % (cell["x"] - 6, cell["z"] - 6, 12, 12)
        lt = rb.call("jawa/list_things", {"rect": rectstr, "includePawns": False})
        defs_here = [t.get("def") for t in lt.get("things", [])]
        has_explosion = any(d and "explosion" in d.lower() for d in defs_here)
        cell["things_after"] = defs_here
        cell["has_explosion"] = has_explosion
        print("  things:", defs_here, "EXPLOSION:", has_explosion, "expected:", cell["expect"])

    with open(r"D:\Luke\dev\Rimworld\Transient\droidworks_detonation_review\bonus_final.json", "w") as f:
        json.dump(bonus, f, indent=2)
