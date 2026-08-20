"""W6 proof + the W5 clause I could not test without it: landmark on a settlement tile."""
import sys, json, time
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rb
host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=600.0); S.connect()
def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r

call("rimworld/start_debug_game_ready", timeoutMs=280000, readiness="mapData", pauseIfNeeded=True)
for _ in range(120):
    st = call("rimworld/get_ui_state")
    if st.get("programState") == "Playing": break
    time.sleep(1)

print("== 1. WORLD OBJECTS on the generated world ==")
o = call("jawa/world_objects_get", limit=4)
print("   total:", o.get("allObjectsOnPlanet"), " settlements:", o.get("settlements"),
      " noFaction:", o.get("objectsWithNoFaction"))
print("   byDef:", list((o.get("byDef") or {}).items())[:6])
print("   byFaction:", list((o.get("byFaction") or {}).items())[:5])
for x in (o.get("objects") or [])[:3]: print("    ", x)

print("\n== 2. VALIDATE - the faults that only appear after save/load ==")
v = call("jawa/world_objects_validate")
print("   nullFactionSettlements:", v.get("nullFactionSettlements"),
      " badTile:", v.get("badTileCount"),
      " onWater:", v.get("settlementsOnWater"),
      " onImpassable:", v.get("settlementsOnImpassable"),
      " stackedTiles:", v.get("stackedTiles"))

print("\n== 3. THE W5 ORDERING CLAUSE: landmark on a SETTLEMENT tile ==")
setts = call("jawa/world_objects_get", def_="Settlement", limit=3) if False else \
        call("jawa/world_objects_get", limit=200, **{"def": "Settlement"})
objs = setts.get("objects") or []
if not objs:
    print("   no settlements found")
else:
    s0 = objs[0]; tid = s0["tile"]
    print("   settlement", s0["id"], s0["name"], "on tile", tid, "faction", s0["faction"])
    before = call("jawa/world_mutators_get", tiles=str(tid))["tiles"][0]
    print("   landmark on that tile before:", before["landmark"])
    r = call("jawa/world_landmarks_set", action="add", tiles=str(tid), **{"def": "Oasis"})
    print("   validity report:", r.get("validity"))
    print("   added:", r.get("added"))
    after = call("jawa/world_mutators_get", tiles=str(tid))["tiles"][0]
    print("   landmark on that tile AFTER:", after["landmark"])
    if after["landmark"]:
        print("   >>> AddLandmark DID NOT REFUSE. IsValidTile is advisory, not enforced.")
        call("jawa/world_landmarks_set", action="remove", tiles=str(tid))
        print("   cleaned up:", call("jawa/world_mutators_get", tiles=str(tid))["tiles"][0]["landmark"])

print("\n== 4. RE-SITE a settlement (the OVERWRITE route) ==")
if objs:
    s0 = objs[0]; old = s0["tile"]
    new_tile = old + 7
    r = call("jawa/world_objects_set", ids=str(s0["id"]), tile=new_tile, name="Sunspire Test")
    print("   changed:", r.get("changed"))
    for x in (r.get("objects") or []): print("   ", x)
    call("jawa/world_objects_set", ids=str(s0["id"]), tile=old, name=s0["name"])
    print("   restored to tile", old)

print("\n== 5. REFUSAL: a FactionDef that exists but was not generated here ==")
r = call("jawa/world_objects_set", ids=str(objs[0]["id"]) if objs else "1", faction="Jawa_HuttCartel")
print("   success:", r.get("success"))
print("   message:", (r.get("message") or "")[:200])
