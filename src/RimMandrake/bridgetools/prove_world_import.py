"""W3 import/validate proof. Windows python only."""
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

CSV = r"D:\Luke\dev\Rimworld\world\ASHKARR_WORLDMAP_tiles.csv"

print("== quicktest ==")
call("rimworld/start_debug_game_ready", timeoutMs=280000, readiness="mapData", pauseIfNeeded=True)
for _ in range(120):
    st = call("rimworld/get_ui_state")
    if st.get("programState") == "Playing": break
    time.sleep(1)
print("   state:", st.get("programState"), " tiles:", call("jawa/world_layers").get("tilesCount"))

print("== 1. THE GUARD: expectTiles=21872 on a 119904-tile world must REFUSE ==")
g = call("jawa/world_tile_import", path=CSV, expectTiles=21872, apply=True)
print("   success:", g.get("success"))
print("   message:", (g.get("message") or "")[:160])

print("== 2. DRY RUN, no guard ==")
d = call("jawa/world_tile_import", path=CSV)
print("   dryRun:", d.get("dryRun"), "rows:", d.get("rows"), "applied:", d.get("applied"), "skipped:", d.get("skipped"))
print("   header:", d.get("header"))
print("   unknownBiomes:", d.get("unknownBiomes"))
print("   errors:", (d.get("errors") or [])[:3])

print("== 3. VALIDATE BEFORE import (should mismatch heavily) ==")
v0 = call("jawa/world_tile_validate", path=CSV, maxRows=3000)
print("   rows:", v0.get("rows"), "matched:", v0.get("matched"), "mismatched:", v0.get("mismatched"), "match%:", v0.get("matchPct"))

print("== 4. APPLY ==")
t0 = time.time()
a = call("jawa/world_tile_import", path=CSV, apply=True)
print("   applied:", a.get("applied"), "skipped:", a.get("skipped"), "in %.1fs" % (time.time()-t0))
print("   unknownBiomes:", a.get("unknownBiomes"))

print("== 5. COMMIT ==")
c = call("jawa/world_commit"); print("   ok:", c.get("success"), "failed:", c.get("failedSteps"))

print("== 6. VALIDATE AFTER ==")
v1 = call("jawa/world_tile_validate", path=CSV)
print("   rows:", v1.get("rows"), "matched:", v1.get("matched"), "mismatched:", v1.get("mismatched"), "match%:", v1.get("matchPct"))
print("   byField:", v1.get("byField"))
for d2 in (v1.get("diffs") or [])[:5]: print("    ", d2)
