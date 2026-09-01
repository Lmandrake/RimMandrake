import sys, json, io, time
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
rb = RimBridge(host, port, token, timeout=600.0); rb.connect()
def call(t, **p):
    r = rb.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
def j(o, n=1000): return json.dumps(o)[:n]
call("jawa/clear_ui", devWindows=True, clearSelection=True, all=True)
st = call("rimworld/get_ui_state")
print("map:", st.get("currentMapId"), "| state:", st.get("programState"))
if st.get("currentMapId") is None:
    print("NO MAP - abort"); sys.exit(0)

ALL = ["Jawa_HuttCartel","Jawa_FreeDroidEnclaves","Jawa_WildsteamClan","Jawa_DeepwaterCompact",
       "Jawa_GeonosianFoundryHive","Jawa_AscendantHelix","Jawa_Junkers"]
for tgt in ("Jawa_HuttCartel", "Jawa_FreeDroidEnclaves"):
    print("\n########## %s ##########" % tgt)
    for f in ALL:
        call("jawa/set_faction_relation", faction=f, kind=("Hostile" if f == tgt else "Neutral"))
    pv = call("jawa/raid_preview", points=3000)
    print("hostileFactions:", j(pv.get("hostileFactions"), 500))
    call("jawa/drain_log", limit=200)
    before = len((call("jawa/list_pawns", faction="nonplayer", limit=100).get("pawns") or []))
    fr = call("jawa/fire_raid", points=3000, faction=tgt, dryRun=False)
    print("fire_raid:", j({k: fr.get(k) for k in
        ("success","message","resolved","spawned","pawnCount","strategy","arrivalMode","logCount")}, 1200))
    logs = (fr.get("effects") or {}).get("logs") or []
    print("effects.logs (%d):" % len(logs))
    for L in logs[:20]: print("   ", j(L, 300))
    call("rimworld/step_game_ticks", ticks=900)
    time.sleep(2)
    lst = call("jawa/list_pawns", faction="nonplayer", limit=120).get("pawns") or []
    print("nonplayer pawns before=%d after=%d" % (before, len(lst)),
          j(Counter(p.get("faction") for p in lst).most_common(), 400))
    dl = call("jawa/drain_log", limit=60)
    msgs = dl.get("messages") or dl.get("lines") or dl.get("log") or []
    print("drain_log (%d):" % len(msgs))
    for m in msgs[-15:]: print("   ", j(m, 300))
