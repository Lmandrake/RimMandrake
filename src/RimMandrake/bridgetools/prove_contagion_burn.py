"""Force the Contagion Burn on the current RM_Contagion map, then run and sample: weather, conditions,
our hediffs on pawns (natives + spawned colonists), and new log errors. Windows python.exe, repo root.
usage: python.exe src/RimMandrake/bridgetools/prove_contagion_burn.py OUT.json"""
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
def log_blind(since):
    # an empty log/errors read is only clean if the log could be seen: a Player.log that shrank (the game restarted)
    # or a silenced Verse.Log (cap reached, logger off) writes nothing (BRIDGE_PROOFS_W50_BLIND_LOG_AND_WRONG_MAP)
    if os.path.getsize(LOG) < since: return "Player.log shrank since the start (game restarted): log unread"
    hl = call("jawa/health", action="status"); lg = hl.get("log") if isinstance(hl, dict) else None
    if not isinstance(lg, dict) or lg.get("state") != "emitting":
        return "game log not proven to be writing (%s): log unread" % ((lg.get("text") or lg.get("state")) if isinstance(lg, dict) else str(hl)[:200])
    return None
_mi = call("jawa/map_info"); MAP_ID = _mi.get("mapId")
out = {"mapBiome": _mi.get("mapBiome"), "mapId": MAP_ID}
if out["mapBiome"] != "RM_Contagion":   # the Burn on any other map samples nothing of ours
    sys.exit("current map biome is %r, not RM_Contagion - refusing to run" % out["mapBiome"])
since = os.path.getsize(LOG)
out["spawn"] = "existing"
time.sleep(2)
for _ in range(3):
    call("rimworld/close_window", windowType="Dialog_NamePlayerFactionAndSettlement")
    if not call("rimworld/get_ui_state").get("windowsForcePause"): break
out["forcePause"] = call("rimworld/get_ui_state").get("windowsForcePause")
st = call("jawa/game_condition", action="start", condition="RM_ContagionBurnCondition", durationTicks=20000)
out["start"] = str(st)[:300]
if not (isinstance(st, dict) and st.get("success")):   # 7 minutes of samples without the Burn would read as "nothing happened"
    json.dump(out, open(sys.argv[1], "w"), indent=1); sys.exit("the Burn did not start: " + out["start"])
call("rimworld/set_time_speed", speed="Ultrafast", ultraSpeedBoost=True); call("rimworld/pause_game", pause=False)
out["samples"] = []
t0 = time.time()
try:
    while time.time() - t0 < 420:
        time.sleep(20)
        mid = call("jawa/map_info").get("mapId")
        if mid != MAP_ID:   # weather/pawns of whatever map took focus would be filed as the Burn's
            raise SystemExit("the current map is now %r, not the Contagion map %s - refusing to sample another map" % (mid, MAP_ID))
        w = call("jawa/weather_get")
        pr = call("jawa/list_pawns", includeHealth=True, limit=5000); pw = pr.get("pawns")
        if not isinstance(pw, list): raise SystemExit("jawa/list_pawns failed (%s) - a hediff census of 0 pawns would read as none" % str(pr)[:200])
        hd = collections.Counter()
        for x in pw:
            # the hediff list is NESTED at row['health']['hediffs'] (list_pawns docs): row['hediffs'] was always empty
            for hh in (((x.get("health") or {}).get("hediffs")) or []):
                d = hh.get("def") if isinstance(hh, dict) else None
                if d and d.startswith("RM_"): hd[(d, "player" if (x.get("faction") or "").lower().startswith(("player","new")) else "other")] += 1
        s = {"t": int(time.time()-t0), "ticks": w.get("ticksGame"), "weather": (w.get("weather") or {}).get("current"),
             "conditions": [c.get("def") for c in w.get("conditions", [])], "hediffs": {"%s|%s" % k: v for k, v in hd.items()}, "pawns": len(pw)}
        out["samples"].append(s); print(s, flush=True); json.dump(out, open(sys.argv[1], "w"), indent=1)
finally:
    call("rimworld/pause_game", pause=True)
    with open(LOG, "rb") as f: f.seek(since); txt = f.read().decode("utf-8", "replace")
    out["log"] = [l[:300] for l in txt.split("\n") if re.search(r"Contagion|Burn|RM_", l) and not l.startswith("  at ")][-30:]
    out["errors"] = list(dict.fromkeys(l[:300] for l in txt.split("\n") if not l.startswith(("  at ", "  - ")) and re.search(r"Exception|rror", l)))[:30]
    out["logBlind"] = log_blind(since)
    json.dump(out, open(sys.argv[1], "w"), indent=1)
if out["logBlind"]:
    sys.exit(out["logBlind"] + " - an empty log/errors list would read as a clean Burn")
