import sys, json, time
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

print("== A. do strategies become usable at higher points? ==")
for pts in (35, 250, 1000, 3000):
    rp = call("jawa/raid_preview", points=pts)
    us = [s["def"] for s in (rp.get("usableStrategies") or [])]
    print("   points %-5s usable: %s" % (pts, us if us else "(none)"))

print("\n== B. condition end: does it actually clear once time passes? ==")
call("jawa/game_condition", action="start", condition="Eclipse", durationTicks=60000)
print("   started. active:", [c["def"] for c in call("jawa/weather_get")["conditions"]])
e = call("jawa/game_condition", action="end", condition="Eclipse")
print("   ended -> endsNextTick:", e.get("endsNextTick"), " gamePaused:", e.get("gamePaused"))
print("   caveat:", e.get("listCaveat"))
call("rimworld/step_game_ticks", ticks=5)
print("   after stepping 5 ticks, active:", [c["def"] for c in call("jawa/weather_get")["conditions"]])

print("\n== C. fire a REAL raid at workable points ==")
d = call("jawa/fire_raid", points=1000)
print("   dry run canFireNow:", d.get("canFireNow"), " resolved:", d.get("resolved"))
if d.get("canFireNow"):
    live = call("jawa/fire_raid", points=1000, dryRun=False)
    print("   LIVE -> success:", live.get("success"), " executed:", live.get("executed"), live.get("note"))
    call("rimworld/step_game_ticks", ticks=60)
    pl = call("jawa/pawn_get", limit=40)
    hostiles = [p for p in pl["pawns"] if p.get("faction") not in ("PlayerColony", None)]
    print("   pawns on map after:", pl.get("count"), " non-player:", len(hostiles))
    print("   factions present:", sorted(set(p.get("faction") for p in pl["pawns"])))
