"""Regenerate the current debug map as BIOME, then run it at Ultrafast and sample weather, conditions, terrain census and
Forge-related log lines until a full grand cycle (~6 days) has elapsed. Windows python.exe, repo root.
usage: python.exe src/RimMandrake/bridgetools/prove_biome_timelapse.py OUT.json BIOME maxSeconds maxTicks"""
import sys, json, time, collections, os, re
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rb
LOG = os.path.expandvars(r"%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log")
h, p, t = rb.resolve_endpoint(); S = rb.RimBridge(host=h, port=p, token=t, timeout=300.0); S.connect()
def call(n, **a):
    r = S.call(n, a) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    if isinstance(r, dict): r.pop("operation", None)
    return r
def terrain():
    # the WHOLE map, in z-bands under get_terrain_batch's 70,000-cell cap (a fixed 250x250 rect read part of a
    # 275/300 map and failed outright on a smaller one); a band with no ops is a failed read, never an empty map
    mi = call("jawa/map_info"); sx, sz = mi.get("sizeX"), mi.get("sizeZ")
    if not sx or not sz: raise SystemExit("jawa/map_info gave no map size (%s)" % str(mi)[:200])
    band = max(1, 70000 // sx); c = collections.Counter(); g = {}
    for z0 in range(0, sz, band):
        g = call("jawa/get_terrain_batch", rects="0,%d,%d,%d" % (z0, sx, min(band, sz - z0)))
        if not g.get("ops"): raise SystemExit("terrain read failed at z=%d: %s" % (z0, str(g)[:200]))
        for op in g["ops"].split(";"):
            if ":" not in op: continue
            d, rect = op.split(":", 1); parts = rect.split(",")
            c[d] += int(parts[2]) * int(parts[3]) if len(parts) == 4 else 1
    return dict(c.most_common(30)), g.get("ticksGame")
BIOME = sys.argv[2]
mi0 = call("jawa/map_info"); tile, id0 = mi0.get("tile"), mi0.get("mapId")
if tile is None or tile == -1 or mi0.get("tileValid") is False or id0 is None:
    sys.exit("no current planet-tile map in jawa/map_info (%s) - nothing regenerated" % str(mi0)[:200])
call("jawa/world_tile_set", tiles=str(tile), biome=BIOME); call("jawa/world_commit")
call("rimworld/execute_debug_action", path=r"Actions\Regenerate Current Map")
# programState stays Playing through a regen: only a NEW mapId proves the map was rebuilt (BIOMEPROOFS_FIX_OLD_MAP_AND_CAPS)
for _ in range(100):
    time.sleep(3)
    if call("jawa/map_info").get("mapId") not in (None, id0) and call("rimworld/get_ui_state").get("programState") == "Playing": break
else:
    sys.exit("the map was not regenerated (mapId still %s) - a timelapse now would run the OLD map" % id0)
since = os.path.getsize(LOG)
out = {"biome": call("jawa/map_info").get("mapBiome"), "samples": []}
t0c, _ = terrain(); out["terrain0"] = t0c
start_ticks = call("jawa/weather_get").get("ticksGame")
call("rimworld/set_time_speed", speed="Ultrafast", ultraSpeedBoost=True)
call("rimworld/pause_game", pause=False)
limit = float(sys.argv[3]); maxticks = int(sys.argv[4])
t0 = time.time()
try:
    while time.time() - t0 < limit:
        time.sleep(20)
        w = call("jawa/weather_get"); tc, tk = terrain()
        cond = [(c.get("def"), c.get("label")) for c in w.get("conditions", [])]
        pw = call("jawa/list_pawns", includeHealth=True, limit=5000).get("pawns") or []
        hd = collections.Counter(h.get("def") for x in pw for h in (x.get("hediffs") or []) if isinstance(h, dict))
        s0 = {"hediffs": {k: v for k, v in hd.items() if k and k.startswith("RM_")}, "pawns": len(pw)}
        s = {"t": int(time.time() - t0), "ticks": tk, "weather": (w.get("weather") or {}).get("current"), "conditions": cond,
             "extra": s0, "terrainDelta": {k: v - t0c.get(k, 0) for k, v in tc.items() if v != t0c.get(k, 0)}}
        out["samples"].append(s); print(s["t"], s["ticks"], s["weather"], cond, list(s["terrainDelta"].items())[:5], flush=True)
        json.dump(out, open(sys.argv[1], "w"), indent=1)
        if tk and start_ticks and tk - start_ticks > maxticks: break
finally:
    call("rimworld/pause_game", pause=True)
    with open(LOG, "rb") as f: f.seek(since); txt = f.read().decode("utf-8", "replace")
    out["forgeLog"] = [l[:300] for l in txt.split("\n") if re.search(r"\[RM|RimMandrake", l)][-60:]
    out["errors"] = list(dict.fromkeys(l[:300] for l in txt.split("\n") if not l.startswith(("  at ", "  - ")) and re.search(r"Exception|rror", l)))[:40]
    json.dump(out, open(sys.argv[1], "w"), indent=1)
