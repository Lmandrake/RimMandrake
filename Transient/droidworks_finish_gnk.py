import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/damage", {"thingId": "RSW_DW_Race_OuterRim_GNKDroid16918", "damageDef": "Bomb", "amount": 5000, "bodyPart": "Torso"})
    print("damage2:", json.dumps(r)[:300])
    time.sleep(1)
    g = rb.call("jawa/list_pawns", {})["pawns"]
    hit = [p for p in g if p["id"] == "RSW_DW_Race_OuterRim_GNKDroid16918"]
    print("still-listed after 2nd hit:", json.dumps(hit)[:300])
    corpses = rb.call("jawa/list_things", {"group": "Corpse"})
    print("corpses:", json.dumps(corpses)[:600])
