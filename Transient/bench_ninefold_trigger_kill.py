import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
with RimBridge(h,p,t) as rb:
    r = rb.call("jawa/list_pawns", {"limit": 200})
    rats = [pw for pw in r.get("pawns", []) if pw.get("def")=="Rat" and not pw.get("dead")]
    print("rats available:", len(rats))
    target = rats[0]
    print("targeting:", target["id"], target["x"], target["z"])
    r2 = rb.call("jawa/damage", {"thingId": target["id"], "damageDef":"Bullet", "amount": 500, "armorPenetration": 1.0})
    print("DAMAGE RESULT:", json.dumps(r2)[:500])
    r3 = rb.call("jawa/drain_log", {"contains": "Ninefold] ", "limit": 50})
    for m in r3.get("messages", [])[-6:]:
        print(m["text"])
    # confirm death
    r4 = rb.call("jawa/list_pawns", {"includeDead": True, "limit": 200})
    dead = [pw for pw in r4.get("pawns", []) if pw.get("id")==target["id"]]
    print("post-state:", dead)
