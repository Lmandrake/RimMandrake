import sys, json
sys.path.insert(0, "Transient")
from belt_scald_probe import call
d = call("jawa/get_defs", defs="DamageDef/RUT_Scald"); print(json.dumps(d)[:900])
call("jawa/damage_log", action="clear")
for p in ("Human634", "Human637"):
    for i in range(6):
        r = call("jawa/damage", damageDef="RUT_Scald", amount=8, thingId=p, allowColonists=True, bodyPart="Torso")
        if i == 0: print(p, str(r)[:500])
ev = call("jawa/damage_log", action="read", pawnsOnly=True).get("events", [])
tot = {}
for e in ev:
    if e.get("damageDef") == "RUT_Scald" or "Scald" in str(e.get("damage") or e.get("def") or ""):
        k = e.get("victim") if not isinstance(e.get("victim"), dict) else e["victim"].get("id") or e["victim"].get("name")
        tot.setdefault(str(k), []).append((e.get("amount"), e.get("dealt")))
print(json.dumps(tot)[:1500])
if not tot: print(json.dumps(ev[:3])[:1500])
