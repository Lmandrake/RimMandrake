import sys, json, time
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

before = call("jawa/world_objects_get", limit=1)
print("before: objects=%s settlements=%s" % (before.get("allObjectsOnPlanet"), before.get("settlements")))
facs = list((before.get("byFaction") or {}).keys())
fac = next((f for f in facs if f not in ("(none)",)), None)
print("using faction:", fac)

print("\n== 1. REFUSAL: a factionless Settlement would be destroyed on load ==")
r = call("jawa/world_objects_add", tile=5000, **{"def": "Settlement"})
print("   ok:", r.get("success"), "|", (r.get("message") or "")[:130])

print("\n== 2. CREATE a real settlement ==")
c = call("jawa/world_objects_add", tile=5000, faction=fac, name="Rustjaw Hold", **{"def": "Settlement"})
print("   ok:", c.get("success"), "|", (c.get("message") or "")[:110])
print("   created:", c.get("created"))
print("   totals:", c.get("totalWorldObjects"), "/", c.get("totalSettlements"))

print("\n== 3. DUPLICATE on the same tile is refused ==")
d = call("jawa/world_objects_add", tile=5000, faction=fac, **{"def": "Settlement"})
print("   ok:", d.get("success"), "|", (d.get("message") or "")[:110])

print("\n== 4. READ IT BACK from the world ==")
g = call("jawa/world_objects_get", tiles="5000")
for o in (g.get("objects") or []): print("   ", o)

print("\n== 5. VALIDATE finds nothing wrong with it ==")
v = call("jawa/world_objects_validate")
print("   nullFactionSettlements:", v.get("nullFactionSettlements"),
      " onWater:", v.get("settlementsOnWater"), " stacked:", v.get("stackedTiles"))

print("\n== 6. REMOVE it again ==")
oid = (c.get("created") or {}).get("id")
rm = call("jawa/world_objects_remove", ids=str(oid))
print("   removed:", rm.get("removed"), " errors:", rm.get("errors"))
g2 = call("jawa/world_objects_get", tiles="5000")
print("   objects on tile 5000 now:", g2.get("count"))
