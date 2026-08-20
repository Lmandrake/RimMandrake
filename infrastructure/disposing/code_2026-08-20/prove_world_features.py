"""G4 + G6 proof: named regions and world info, with a visible label change."""
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

print("== 1. WORLD INFO ==")
i = call("jawa/world_info_get")
inf = i.get("info") or {}
for k in ("name","seedString","planetCoverage","overallRainfall","overallTemperature",
          "overallPopulation","landmarkDensity","pollution","factionCount"):
    print("   %-22s %s" % (k, inf.get(k)))
print("   notPersisted:", i.get("notPersisted"))

print("\n== 2. INFO SET: rename, and the non-persisted refusal ==")
r = call("jawa/world_info_set", name="Ash'karr Test", overallPopulation="Little")
print("   changed:", r.get("changed"))
print("   refused:", r.get("refused"), " <- refused because it does not survive a load")
r2 = call("jawa/world_info_set", overallPopulation="Little", allowNonPersistent=True)
print("   with allowNonPersistent:", r2.get("changed"))

print("\n== 3. NAMED REGIONS the generator made ==")
f = call("jawa/world_features_get", limit=6)
print("   total features:", f.get("count"), " tilesWithNoFeature:", f.get("tilesWithNoFeature"),
      " textsCreated:", f.get("textsCreated"))
for x in (f.get("features") or [])[:5]:
    print("    id=%-4s %-14s %-26s tiles=%-6s angle=%s size=%.1f" % (
        x["uniqueID"], x["def"], x["name"], x["tileCount"], x["drawAngle"], x["maxDrawSizeInTiles"]))

print("\n== 4. RENAME + ROTATE a region (drawAngle is control vanilla never uses) ==")
feats = f.get("features") or []
if feats:
    big = max(feats, key=lambda x: x["tileCount"])
    print("   target:", big["uniqueID"], big["name"], "tiles", big["tileCount"])
    u = call("jawa/world_features_set", action="update", featureId=big["uniqueID"],
             name="THE DUNE SEA", drawAngle=35.0, maxDrawSizeInTiles=90.0)
    print("   ->", u.get("feature"))
    globals()['CENTER_TILE'] = (big.get("sampleTiles") or [0])[0]

print("\n== 5. CREATE a new region and assign tiles to it ==")
c = call("jawa/world_features_set", action="create", name="Scald Spine Test",
         range="40000-40120", drawAngle=0.0, maxDrawSizeInTiles=40.0, **{"def": "Peninsula"})
print("   created:", c.get("featureId"), "tilesAssigned:", c.get("tilesAssigned"))
print("   ->", c.get("feature"))

print("\n== 6. verify membership moved, then COMMIT ==")
g2 = call("jawa/world_features_get", limit=200)
made = [x for x in (g2.get("features") or []) if x["name"] == "Scald Spine Test"]
print("   new region reads back:", made[0] if made else "NOT FOUND")
call("jawa/world_commit")
print("   textsCreated after set:", g2.get("textsCreated"), "(false means the label will rebuild)")

print("\n== 7. DELETE it again, membership must be cleared ==")
if made:
    d = call("jawa/world_features_set", action="delete", featureId=made[0]["uniqueID"])
    print("   tilesCleared:", d.get("tilesCleared"))
    g3 = call("jawa/world_features_get", limit=200)
    print("   features now:", g3.get("count"), " tilesWithNoFeature:", g3.get("tilesWithNoFeature"))
