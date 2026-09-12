import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

with RimBridge(host, port, token) as rb:
    pawns = rb.call("jawa/list_pawns", {})["pawns"]
    gnk = next(p for p in pawns if p["kind"] == "RSW_DW_OuterRim_GNKDroid")
    kotor = next(p for p in pawns if p["kind"] == "RSW_DW_KotORDroidColonist_T3UD")
    print("GNK:", gnk["id"], gnk["name"], " KotOR colonist:", kotor["id"], kotor["name"])

    # 1. Powered-down hediff add/remove on the KotOR colonist -- no NRE expected
    r1 = rb.call("jawa/pawn_health", {"pawn": kotor["id"], "action": "add", "hediff": "RSW_DW_PoweredDown", "severity": 1.0})
    print("add PoweredDown:", json.dumps(r1)[:200])
    r2 = rb.call("jawa/pawn_health", {"pawn": kotor["id"], "action": "remove", "hediff": "RSW_DW_PoweredDown"})
    print("remove PoweredDown:", json.dumps(r2)[:200])

    # 2. GNK: set full power, then kill -> expect detonation
    r3 = rb.call("jawa/pawn_need", {"pawn": gnk["id"], "need": "RSW_DW_Power", "action": "need", "level": 1.0})
    print("set GNK power=1.0:", json.dumps(r3)[:200])
    before = rb.call("jawa/list_things", {"group": "Corpse"})
    r4 = rb.call("jawa/damage", {"thingId": gnk["id"], "damageDef": "Bomb", "amount": 2000})
    print("damage GNK:", json.dumps(r4)[:200])
    time.sleep(1)
    after_corpse = rb.call("jawa/list_things", {"group": "Corpse"})
    print("corpse before/after count:", len(before.get("things", [])), len(after_corpse.get("things", [])))
    # look for an explosion / detonation artifact near the GNK's last position
    things_near = rb.call("jawa/list_things", {"group": "All"}) if False else None

print("DONE")
