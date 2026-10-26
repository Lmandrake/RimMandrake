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

def log_blind(since):
    # an empty error list is only clean if the log could be seen: a Player.log that shrank (the game restarted)
    # or a silenced Verse.Log (cap reached, logger off) writes nothing (BRIDGE_PROOFS_W50_BLIND_LOG_AND_WRONG_MAP)
    if os.path.getsize(LOG) < since: return "Player.log shrank since the start (game restarted): errors unread"
    hl = call("jawa/health", action="status"); lg = hl.get("log") if isinstance(hl, dict) else None
    if not isinstance(lg, dict) or lg.get("state") != "emitting":
        return "game log not proven to be writing (%s): errors unread" % ((lg.get("text") or lg.get("state")) if isinstance(lg, dict) else str(hl)[:200])
    return None

def wait_new_map(old_id, limit=300):
    # programState stays Playing through a regen, so only a NEW mapId proves the map was rebuilt
    # (BIOMEPROOFS_FIX_OLD_MAP_AND_CAPS)
    t0 = time.time()
    while time.time() - t0 < limit:
        mi = call("jawa/map_info")
        if mi.get("mapId") not in (None, old_id) and call("rimworld/get_ui_state").get("programState") == "Playing":
            return mi
        time.sleep(3)
    return None

out_path, biomes = sys.argv[1], sys.argv[2:]
results = {}
mi0 = call("jawa/map_info"); tile, map_id = mi0.get("tile"), mi0.get("mapId")
if tile is None or tile == -1 or mi0.get("tileValid") is False or map_id is None:
    sys.exit("no current planet-tile map in jawa/map_info (%s) - nothing censused" % str(mi0)[:200])
for b in biomes:
    b, _, temp = b.partition("@")
    r = {"biome": b}; since = log_size()
    kw = {"temperature": float(temp)} if temp else {}
    w = call("jawa/world_tile_set", tiles=str(tile), biome=b, **kw); r["tile_set"] = w.get("success"), (w.get("message") or "")[:200]
    call("jawa/world_commit")
    g = call("rimworld/execute_debug_action", path=r"Actions\Regenerate Current Map"); r["regen"] = g.get("success"), (g.get("message") or "")[:200]
    mi = wait_new_map(map_id); r["regenerated"] = mi is not None
    if mi is None:
        r["errors"] = new_errors(since); results[b + ("@" + temp if temp else "")] = r
        json.dump(results, open(out_path, "w"), indent=1)
        sys.exit("%s: the map was not regenerated (mapId still %s) - a census now would read the OLD map" % (b, map_id))
    map_id = mi.get("mapId")
    if mi.get("tile") != tile:   # a new mapId on ANOTHER tile is another map (a quest/pocket map took focus), not the regen
        results[b + ("@" + temp if temp else "")] = r; json.dump(results, open(out_path, "w"), indent=1)
        sys.exit("%s: the new current map %s is on tile %r, not the regenerated tile %s - refusing to census it" % (b, map_id, mi.get("tile"), tile))
    r["mapBiome"] = mi.get("mapBiome"); r["temp"] = mi.get("outdoorTempNow"); r["biomeMatches"] = r["mapBiome"] == b
    if not r["biomeMatches"]:   # a failed world_tile_set regenerates the OLD biome: its census filed under b is a lie
        r["errors"] = new_errors(since); results[b + ("@" + temp if temp else "")] = r
        json.dump(results, open(out_path, "w"), indent=1)
        sys.exit("%s: the regenerated map is %r, not %s (tile_set %s) - refusing to census it as %s" % (b, r["mapBiome"], b, r["tile_set"], b))
    wg = call("jawa/weather_get"); r["weather"] = {k: wg.get(k) for k in ("weather", "conditions") if k in wg} or str(wg)[:300]
    pw = call("jawa/list_pawns", faction="nonplayer", limit=5000)
    pl = pw.get("pawns") if isinstance(pw.get("pawns"), list) else None
    r["wild"] = dict(collections.Counter(x.get("kindDef") for x in pl).most_common(40)) if pl is not None else "list_pawns failed: " + str(pw)[:200]
    r["wildTruncated"] = pw.get("truncated")
    # perDef counts EVERY matched plant; the `things` rows stop at `limit` (default 200)
    th = call("jawa/list_things", group="Plant", limit=1)
    pd = th.get("perDef") if isinstance(th.get("perDef"), dict) else None
    r["plants"] = dict(collections.Counter(pd).most_common(30)) if pd is not None else "list_things failed: " + str(th)[:200]
    r["plantsTotal"] = th.get("countMatched")
    r["errors"] = new_errors(since); r["errorsBlind"] = log_blind(since)
    results[b + ("@" + temp if temp else "")] = r
    print(b, r["mapBiome"], "wild", len(pl) if pl is not None else "?", "(TRUNCATED)" if r["wildTruncated"] else "",
          "plants", r["plantsTotal"], "errors", "BLIND: " + r["errorsBlind"] if r["errorsBlind"] else len(r["errors"]), flush=True)
    json.dump(results, open(out_path, "w"), indent=1)
    if r["errorsBlind"]: sys.exit("%s: %s - an empty error list would read as a clean generation" % (b, r["errorsBlind"]))
