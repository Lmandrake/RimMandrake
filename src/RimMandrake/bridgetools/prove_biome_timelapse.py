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
    g = call("jawa/get_terrain_batch", rects="0,0,250,250")
    c = collections.Counter()
    for op in (g.get("ops") or "").split(";"):
        if ":" not in op: continue
        d, rect = op.split(":", 1); parts = rect.split(",")
        c[d] += int(parts[2]) * int(parts[3]) if len(parts) == 4 else 1
    return dict(c.most_common(30)), g.get("ticksGame")
BIOME = sys.argv[2]
tile = call("jawa/map_info").get("tile")
call("jawa/world_tile_set", tiles=str(tile), biome=BIOME); call("jawa/world_commit")
call("rimworld/execute_debug_action", path=r"Actions\Regenerate Current Map"); time.sleep(5)
for _ in range(100):
    if call("rimworld/get_ui_state").get("programState") == "Playing": break
    time.sleep(3)
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
        pw = call("jawa/list_pawns", includeHealth=True).get("pawns") or []
        hd = collections.Counter(h.get("def") or h.get("defName") for x in pw for h in ((x.get("health") or {}).get("hediffs") or []) if isinstance(h, dict))
        s0 = {"hediffs": {k: v for k, v in hd.items() if k and k.startswith("RM_")}, "pawns": len(pw)}
        s = {"t": int(time.time() - t0), "ticks": tk, "weather": (w.get("weather") or {}).get("current"), "conditions": cond,
             "extra": s0, "terrainDelta": {k: v - t0c.get(k, 0) for k, v in tc.items() if v != t0c.get(k, 0)}}
        out["samples"].append(s); print(s["t"], s["ticks"], s["weather"], cond, list(s["terrainDelta"].items())[:5], flush=True)
        json.dump(out, open(sys.argv[1], "w"), indent=1)
        if tk and start_ticks and tk - start_ticks > maxticks: break
finally:
    call("rimworld/pause_game", pause=True)
    with open(LOG, "rb") as f: f.seek(since); txt = f.read().decode("utf-8", "replace")
    out["forgeLog"] = [l[:300] for l in txt.split("\n") if re.search(r"\\[RM|RimMandrake", l)][-60:]
    out["errors"] = list(dict.fromkeys(l[:300] for l in txt.split("\n") if not l.startswith(("  at ", "  - ")) and re.search(r"Exception|rror", l)))[:40]
    json.dump(out, open(sys.argv[1], "w"), indent=1)
