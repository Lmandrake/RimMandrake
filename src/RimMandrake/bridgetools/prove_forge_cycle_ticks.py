"""Run the current RM_TheForge map at Ultrafast and sample weather, conditions, terrain census and
Forge-related log lines until a full grand cycle (~6 days) has elapsed. Windows python.exe, repo root.
usage: python.exe src/RimMandrake/bridgetools/prove_forge_cycle_ticks.py OUT.json [maxSeconds]"""
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
_mi = call("jawa/map_info")
if _mi.get("mapBiome") != "RM_TheForge":   # any other map "completes a cycle" too, with an empty forgeLog: not a Forge proof
    sys.exit("current map biome is %r, not RM_TheForge - refusing to sample (%s)" % (_mi.get("mapBiome"), str(_mi)[:200]))
SX, SZ = int(_mi["sizeX"]), int(_mi["sizeZ"])   # not a hardcoded 250: on a bigger map that silently censused only the 250x250 corner
BAND = max(1, 70000 // SX)   # get_terrain_batch refuses > 70,000 cells per call (MaxCells): z-bands, or a 275+ map never reads
MAP_ID = _mi.get("mapId")
def log_blind(since):
    # an empty forgeLog is only clean if the log could be seen: a Player.log that shrank (the game restarted)
    # or a silenced Verse.Log (cap reached, logger off) writes nothing (BRIDGE_PROOFS_W50_BLIND_LOG_AND_WRONG_MAP)
    if os.path.getsize(LOG) < since: return "Player.log shrank since the start (game restarted): log unread"
    hl = call("jawa/health", action="status"); lg = hl.get("log") if isinstance(hl, dict) else None
    if not isinstance(lg, dict) or lg.get("state") != "emitting":
        return "game log not proven to be writing (%s): log unread" % ((lg.get("text") or lg.get("state")) if isinstance(lg, dict) else str(hl)[:200])
    return None
def terrain():
    mid = call("jawa/map_info").get("mapId")
    if mid != MAP_ID:   # a sample of whatever map took focus would be filed as the Forge's cycle
        raise SystemExit("the current map is now %r, not the Forge map %s - refusing to sample another map" % (mid, MAP_ID))
    c = collections.Counter(); g = {}
    for z0 in range(0, SZ, BAND):
        g = call("jawa/get_terrain_batch", rects="0,%d,%d,%d" % (z0, SX, min(BAND, SZ - z0)))
        for op in (g.get("ops") or "").split(";"):
            if ":" not in op: continue
            d, rect = op.split(":", 1); parts = rect.split(",")
            c[d] += int(parts[2]) * int(parts[3]) if len(parts) == 4 else 1
    if sum(c.values()) != SX * SZ:
        raise SystemExit("terrain census read %d of %d cells (%s) - instrument blind, refusing to report deltas"
                         % (sum(c.values()), SX * SZ, str(g)[:200]))
    return dict(c.most_common(30)), g.get("ticksGame")
since = os.path.getsize(LOG)
out = {"samples": []}
t0c, _ = terrain(); out["terrain0"] = t0c
start_ticks = call("jawa/weather_get").get("ticksGame")
call("rimworld/set_time_speed", speed="Ultrafast", ultraSpeedBoost=True)
call("rimworld/pause_game", pause=False)
limit = float(sys.argv[2]) if len(sys.argv) > 2 else 1500
t0 = time.time()
try:
    while time.time() - t0 < limit:
        time.sleep(20)
        w = call("jawa/weather_get"); tc, tk = terrain()
        cond = [(c.get("def"), c.get("label")) for c in w.get("conditions", [])]
        s = {"t": int(time.time() - t0), "ticks": tk, "weather": (w.get("weather") or {}).get("current"), "conditions": cond,
             "terrainDelta": {k: v - t0c.get(k, 0) for k, v in tc.items() if v != t0c.get(k, 0)}}
        out["samples"].append(s); print(s["t"], s["ticks"], s["weather"], cond, list(s["terrainDelta"].items())[:5], flush=True)
        json.dump(out, open(sys.argv[1], "w"), indent=1)
        if tk and start_ticks and tk - start_ticks > 400000: out["cycleComplete"] = True; break
finally:
    call("rimworld/pause_game", pause=True)
    with open(LOG, "rb") as f: f.seek(since); txt = f.read().decode("utf-8", "replace")
    out["forgeLog"] = [l[:300] for l in txt.split("\n") if re.search(r"[Ff]orge|RMTheForge", l)][-60:]
    out["errors"] = list(dict.fromkeys(l[:300] for l in txt.split("\n") if not l.startswith(("  at ", "  - ")) and re.search(r"Exception|rror", l)))[:40]
    out["logBlind"] = log_blind(since)
    json.dump(out, open(sys.argv[1], "w"), indent=1)
if out["logBlind"]:
    sys.exit(out["logBlind"] + " - an empty forgeLog/errors list would read as a clean cycle")
# running out of wall-clock before ~6 game days is a PARTIAL cycle: say so, never exit 0 on it
if not out.get("cycleComplete"):
    sys.exit("only %s of 400000 ticks elapsed in %.0f s - partial cycle, not a proof (raise maxSeconds)"
             % ((out["samples"][-1]["ticks"] - start_ticks) if out["samples"] and out["samples"][-1]["ticks"] and start_ticks
                else "?", limit))
