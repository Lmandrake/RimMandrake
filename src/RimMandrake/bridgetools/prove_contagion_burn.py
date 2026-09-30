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
out = {"mapBiome": call("jawa/map_info").get("mapBiome")}
since = os.path.getsize(LOG)
out["spawn"] = "existing"
time.sleep(2)
for _ in range(3):
    call("rimworld/close_window", windowType="Dialog_NamePlayerFactionAndSettlement")
    if not call("rimworld/get_ui_state").get("windowsForcePause"): break
out["forcePause"] = call("rimworld/get_ui_state").get("windowsForcePause")
out["start"] = str(call("jawa/game_condition", action="start", condition="RM_ContagionBurnCondition", durationTicks=20000))[:300]
call("rimworld/set_time_speed", speed="Ultrafast", ultraSpeedBoost=True); call("rimworld/pause_game", pause=False)
out["samples"] = []
t0 = time.time()
try:
    while time.time() - t0 < 420:
        time.sleep(20)
        w = call("jawa/weather_get")
        pw = call("jawa/list_pawns", includeHealth=True).get("pawns") or []
        hd = collections.Counter()
        for x in pw:
            for hh in (x.get("hediffs") or []):
                d = hh.get("def") or hh.get("defName") if isinstance(hh, dict) else None
                if d and d.startswith("RM_"): hd[(d, "player" if (x.get("faction") or "").lower().startswith(("player","new")) else "other")] += 1
        s = {"t": int(time.time()-t0), "ticks": w.get("ticksGame"), "weather": (w.get("weather") or {}).get("current"),
             "conditions": [c.get("def") for c in w.get("conditions", [])], "hediffs": {"%s|%s" % k: v for k, v in hd.items()}, "pawns": len(pw)}
        out["samples"].append(s); print(s, flush=True); json.dump(out, open(sys.argv[1], "w"), indent=1)
finally:
    call("rimworld/pause_game", pause=True)
    with open(LOG, "rb") as f: f.seek(since); txt = f.read().decode("utf-8", "replace")
    out["log"] = [l[:300] for l in txt.split("\n") if re.search(r"Contagion|Burn|RM_", l) and not l.startswith("  at ")][-30:]
    out["errors"] = list(dict.fromkeys(l[:300] for l in txt.split("\n") if not l.startswith(("  at ", "  - ")) and re.search(r"Exception|rror", l)))[:30]
    json.dump(out, open(sys.argv[1], "w"), indent=1)
