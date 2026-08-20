"""W4 proof: rivers/roads add, upgrade, refused downgrade, REMOVE, biome-hiding."""
import sys, json, time, csv as csvmod, os
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
print("world tiles:", call("jawa/world_layers").get("tilesCount"))

NB = r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\w4_neighbors.csv"
print("== dump the engine's own neighbour ordering ==")
d = call("jawa/world_neighbors", path=NB)
print("   tiles:", d.get("tiles"), "->", d.get("path"))
rows = {}
with open(NB, newline="") as f:
    for r in csvmod.DictReader(f):
        rows[int(r["tile"])] = [int(r[k]) for k in r if k.startswith("n") and r[k] not in ("", "-1")]
# a 4-tile chain of genuine neighbours
a = 5000
chain = [a]
while len(chain) < 4:
    for n in rows[chain[-1]]:
        if n not in chain:
            chain.append(n); break
print("   chain:", chain)

print("\n== 1. LAY a Creek along the chain (mouth first) ==")
r1 = call("jawa/world_links_set", kind="river", path=",".join(map(str, chain)), def_="Creek") if False else \
     call("jawa/world_links_set", kind="river", path=",".join(map(str, chain)), **{"def": "Creek"})
print("   laid:", r1.get("laid"), "refused:", r1.get("refused"))
for t in (r1.get("tiles") or [])[:4]:
    print("   tile", t["tile"], "rivers:", t["potentialRivers"], "riverDist:", t["riverDist"])

print("\n== 2. UPGRADE the first segment to HugeRiver (higher priority) ==")
r2 = call("jawa/world_links_set", kind="river", path="%d,%d" % (chain[0], chain[1]), **{"def": "HugeRiver"})
print("   ", (r2.get("tiles") or [{}])[0].get("potentialRivers"))

print("\n== 3. DOWNGRADE back to Creek - Overlay* should REFUSE silently ==")
r3 = call("jawa/world_links_set", kind="river", path="%d,%d" % (chain[0], chain[1]), **{"def": "Creek"})
print("   still:", (r3.get("tiles") or [{}])[0].get("potentialRivers"), " <- unchanged means the refusal is real")

print("\n== 4. CLEAR the middle segment - capability vanilla lacks ==")
c = call("jawa/world_links_clear", kind="river", tiles=str(chain[1]), to=chain[2])
print("   removedEntries:", c.get("removedEntries"), "tilesTouched:", c.get("tilesTouched"))
g = call("jawa/world_links_get", tiles="%d,%d" % (chain[1], chain[2]))
for t in g["tiles"]:
    print("   tile", t["tile"], "rivers now:", t["potentialRivers"])

print("\n== 5. BIOME HIDING: paint a biome with allowRivers=false under a river ==")
# find one
cand = None
for b in ("Ocean", "Lake", "IceSheet", "SeaIce"):
    q = call("jawa/get_def", defType="BiomeDef", defName=b)
    txt = json.dumps(q)
    if '"allowRivers": false' in txt or '"allowRivers":false' in txt:
        cand = b; break
print("   biome with allowRivers=false:", cand)
if cand:
    call("jawa/world_tile_set", tiles=str(chain[0]), biome=cand)
    t = call("jawa/world_links_get", tiles=str(chain[0]))["tiles"][0]
    print("   biome:", t["biome"], "allowRivers:", t["allowRivers"])
    print("   potentialRivers:", len(t["potentialRivers"]), " visibleRivers:", t["visibleRivers"],
          " hiddenByBiome:", t["hiddenByBiome"])

print("\n== 6. COMMIT + VALIDATE the whole network ==")
call("jawa/world_commit")
v = call("jawa/world_links_validate")
print("   riverEntries:", v.get("riverEntries"), "roadEntries:", v.get("roadEntries"))
print("   asymmetric:", v.get("asymmetricCount"), "nonAdjacent:", v.get("nonAdjacentCount"),
      "hiddenByBiome:", v.get("hiddenByBiomeCount"), "landlockedRiverTiles:", v.get("landlockedRiverTiles"))
for x in (v.get("asymmetric") or [])[:3]: print("    asym:", x)
