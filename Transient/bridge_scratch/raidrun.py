import sys, json, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
rb = RimBridge(host, port, token, timeout=900.0); rb.connect()
def call(t, **p):
    r = rb.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
def j(o, n=1200): return json.dumps(o)[:n]

print("=== quicktest map ===")
r = call("rimworld/start_debug_game_ready", timeoutMs=600000, readiness="mapData", pauseIfNeeded=True)
print("start:", j({k: r.get(k) for k in ("success","message")}))
for _ in range(180):
    st = call("rimworld/get_ui_state")
    if st.get("programState") == "Playing" and st.get("currentMapId") is not None: break
    time.sleep(2)
print("ui:", j({k: st.get(k) for k in ("programState","currentMapId")}))
time.sleep(10)

TARGETS = ["Jawa_FreeDroidEnclaves", "Jawa_Junkers"]
ALL = ["Jawa_HuttCartel","Jawa_FreeDroidEnclaves","Jawa_WildsteamClan","Jawa_DeepwaterCompact",
       "Jawa_GeonosianFoundryHive","Jawa_AscendantHelix","Jawa_Junkers"]

for tgt in TARGETS:
    print("\n########## %s ##########" % tgt)
    for f in ALL:
        call("jawa/set_faction_relation", faction=f, kind=("Hostile" if f == tgt else "Neutral"))
    pv = call("jawa/raid_preview", points=3000)
    print("preview hostile:", j(pv.get("hostileFactions"), 400))
    print("preview strategies:", j(pv.get("strategies") or pv.get("raidStrategies"), 400))
    call("jawa/drain_log", limit=200)          # flush
    fr = call("jawa/fire_raid", points=3000, faction=tgt, dryRun=False)
    print("fire_raid:", j({k: fr.get(k) for k in
        ("success","message","resolved","spawned","pawnCount","strategy","arrivalMode","logCount")}, 1400))
    eff = fr.get("effects") or {}
    logs = eff.get("logs") or []
    print("effects.logs (%d):" % len(logs))
    for L in logs[:25]: print("   ", j(L, 320))
    call("rimworld/step_game_ticks", ticks=600)
    time.sleep(2)
    pawns = call("jawa/list_pawns", faction="nonplayer", limit=80)
    lst = pawns.get("pawns") or []
    from collections import Counter
    print("nonplayer pawns on map:", len(lst),
          j(Counter(p.get("faction") for p in lst).most_common(), 400))
    dl = call("jawa/drain_log", limit=60, errorsOnly=True)
    msgs = dl.get("messages") or dl.get("lines") or []
    print("drain_log errors (%d):" % len(msgs))
    for m in msgs[:20]: print("   ", j(m, 320))
