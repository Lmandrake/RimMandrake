"""Regenerate the current debug map as each given biome and census it: weather, wild pawns by kind,
plants by def, and new Player.log errors during generation. Run under Windows python.exe from the repo root.
usage: python.exe src/RimMandrake/bridgetools/prove_biome_quicktest.py OUT.json BIOME[@tempC] [BIOME[@tempC] ...]"""
import sys, json, time, collections, os, re
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rb
LOG = os.path.expandvars(r"%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log")
h, p, t = rb.resolve_endpoint(); S = rb.RimBridge(host=h, port=p, token=t, timeout=600.0); S.connect()

def call(n, **a):
    r = S.call(n, a) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    if isinstance(r, dict): r.pop("operation", None)
    return r

def log_size():
    return os.path.getsize(LOG)

def new_errors(since):
    with open(LOG, "rb") as f:
        f.seek(since); txt = f.read().decode("utf-8", "replace")
    out = []
    for l in txt.split("\n"):
        if l.startswith("  at ") or l.startswith("  - "): continue
        if re.search(r"Exception|Could not|rror", l) and "InputLegacyModule" not in l:
            out.append(l[:300])
    return list(dict.fromkeys(out))[:40]

def wait_playing(limit=300):
    t0 = time.time()
    while time.time() - t0 < limit:
        if call("rimworld/get_ui_state").get("programState") == "Playing": return True
        time.sleep(3)
    return False

out_path, biomes = sys.argv[1], sys.argv[2:]
results = {}
tile = call("jawa/map_info").get("tile")
for b in biomes:
    b, _, temp = b.partition("@")
    r = {"biome": b}; since = log_size()
    kw = {"temperature": float(temp)} if temp else {}
    w = call("jawa/world_tile_set", tiles=str(tile), biome=b, **kw); r["tile_set"] = w.get("success"), (w.get("message") or "")[:200]
    call("jawa/world_commit")
    g = call("rimworld/execute_debug_action", path=r"Actions\Regenerate Current Map"); r["regen"] = g.get("success"), (g.get("message") or "")[:200]
    time.sleep(5); r["playing"] = wait_playing()
    mi = call("jawa/map_info"); r["mapBiome"] = mi.get("mapBiome"); r["temp"] = mi.get("outdoorTempNow")
    wg = call("jawa/weather_get"); r["weather"] = {k: wg.get(k) for k in ("current", "currentWeather", "weather", "conditions", "activeConditions") if k in wg} or str(wg)[:300]
    pw = call("jawa/list_pawns", faction="nonplayer")
    pl = pw.get("pawns") or pw.get("results") or []
    r["wild"] = dict(collections.Counter(x.get("kindDef") or x.get("kind") or x.get("def") for x in pl).most_common(40))
    th = call("jawa/list_things", group="Plant")
    tl = th.get("things") or th.get("results") or []
    r["plants"] = dict(collections.Counter(x.get("defName") or x.get("def") for x in tl).most_common(30))
    r["errors"] = new_errors(since)
    results[b + ("@" + temp if temp else "")] = r
    print(b, r["mapBiome"], "wild", sum(r["wild"].values()), "plants", sum(r["plants"].values()), "errors", len(r["errors"]), flush=True)
    json.dump(results, open(out_path, "w"), indent=1)
