"""E1 proof: weather (and that it does not hold), conditions, threat points, raid preview."""
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

call("rimworld/start_debug_game_ready", timeoutMs=280000, readiness="mapData", pauseIfNeeded=True)
for _ in range(120):
    st = call("rimworld/get_ui_state")
    if st.get("programState") == "Playing": break
    time.sleep(1)

print("== 1. READ: weather, conditions, and what the storyteller thinks you're worth ==")
w = call("jawa/weather_get")
print("   weather:", w.get("weather"))
print("   activeConditions:", w.get("activeConditionCount"), w.get("conditions"))
print("   threatPoints:", w.get("threatPoints"))
print("   wealth:", w.get("wealth"))
print("   storyteller:", w.get("storyteller"))

print("\n== 2. WEATHER: plain transition, then a LOCK ==")
t1 = call("jawa/weather_set", weather="Fog")
print("   transition:", t1.get("before"), "->", t1.get("after"), " lockInForce:", t1.get("lockInForce"))
print("   notes:", t1.get("notes"))
t2 = call("jawa/weather_set", weather="RainyThunderstorm", lockWeather=True)
print("   lock     :", t2.get("before"), "->", t2.get("after"), " lockInForce:", t2.get("lockInForce"))
print("   notes:", t2.get("notes"))
w2 = call("jawa/weather_get")
print("   conditions now:", [c["def"] for c in (w2.get("conditions") or [])])
t3 = call("jawa/weather_set", unlock=True)
print("   unlock   -> lockInForce:", t3.get("lockInForce"), t3.get("notes"))

print("\n== 3. GAME CONDITIONS ==")
c1 = call("jawa/game_condition", action="start", condition="Eclipse", durationTicks=60000)
print("   start Eclipse:", c1.get("notes"), " active:", [x["def"] for x in (c1.get("activeConditions") or [])])
c2 = call("jawa/game_condition", action="end", condition="Eclipse")
print("   end Eclipse  :", c2.get("notes"), " active:", [x["def"] for x in (c2.get("activeConditions") or [])])

print("\n== 4. PLANETKILLER IS HARD-BLOCKED ==")
pk = call("jawa/game_condition", action="start", condition="Planetkiller")
print("   success:", pk.get("success"))
print("   message:", (pk.get("message") or "")[:140])

print("\n== 5. RAID PREVIEW - read-only ==")
rp = call("jawa/raid_preview")
print("   defaultParms:", rp.get("defaultParms"))
print("   currentThreatPoints:", rp.get("currentThreatPoints"))
print("   hostile factions:", [f["def"] for f in (rp.get("hostileFactions") or [])][:6])
print("   usable strategies:", [s["def"] for s in (rp.get("usableStrategies") or [])])
print("   arrival modes:", [a["def"] for a in (rp.get("arrivalModes") or [])][:8])

print("\n== 6. FIRE_RAID defaults to DRY RUN - you must opt in ==")
d = call("jawa/fire_raid", points=500)
print("   dryRun:", d.get("dryRun"), " canFireNow:", d.get("canFireNow"))
print("   resolved:", d.get("resolved"))
print("   note:", d.get("note"))
