import sys, json, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

SAVE   = "WORLDMAP_V1_original"
CENTER = 8858     # nearest settlement to the 3D centroid of all 121 authored holdings
host, port, token = resolve_endpoint()
rb = RimBridge(host, port, token, timeout=1800.0); rb.connect()

def call(t, **p):
    r = rb.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r

def show(tag, r, keys=None):
    d = {k: r.get(k) for k in keys} if keys else r
    print(tag, json.dumps(d)[:1100]); sys.stdout.flush()

names = [d["name"] for d in rb.list_tools()]
print("world_map_mode registered:", "jawa/world_map_mode" in names,
      "| jawa tools:", len([n for n in names if n.startswith("jawa/")]))
if "jawa/world_map_mode" not in names:
    print("ABORT: new tool did not register"); sys.exit(1)

print("=== loading %s ===" % SAVE); t0 = time.time()
show("load:", call("rimworld/load_game_ready", saveName=SAVE, readiness="gameData",
                   timeoutMs=1500000, pauseIfNeeded=True),
     ["success","message","readiness"])
print("load wall %.0fs" % (time.time()-t0))
time.sleep(45)                                   # the mandated settle
show("ui:", call("rimworld/get_ui_state"), ["programState","currentMapId"])

print("=== planet view ===")
show("world_view:", call("jawa/world_view", show=True, centerTile=CENTER,
                         altitude=520, northUp=True),
     ["success","worldSelected","centeredOn","message"])
time.sleep(3)

print("=== map mode state BEFORE ===")
st = call("jawa/world_map_mode")
show("state:", st, ["success","frameworkPresent","modeBefore","worldRendered","message"])
print("available:", json.dumps([m.get("defName") for m in (st.get("availableModes") or [])]))

print("=== switch to FactionTerritories ===")
sw = call("jawa/world_map_mode", mapModeDefName="FactionTerritories")
show("switch:", sw, ["success","switched","refusal","modeBefore","modeAfter",
                     "modeChanged","regenerateNow","regenBusy","message"])

print("=== waiting for the async border regeneration ===")
for i in range(180):
    time.sleep(2)
    s = call("jawa/world_map_mode")
    if i % 5 == 0 or (not s.get("regenBusy") and not s.get("regenerateNow")):
        print("  t=%3ds mode=%s busy=%s regenNow=%s tiles=%s/%s" % (
            i*2, s.get("modeAfter"), s.get("regenBusy"), s.get("regenerateNow"),
            s.get("tilesPrepared"), s.get("tilesToPrepare"))); sys.stdout.flush()
    if s.get("regenBusy") is False and s.get("regenerateNow") is False and i > 2:
        print("  REGEN SETTLED at t=%ds" % (i*2)); break

for label, alt in (("ashkarr_territories_centre", 520),
                   ("ashkarr_territories_wide", 1000),
                   ("ashkarr_territories_close", 260)):
    call("jawa/world_view", show=True, centerTile=CENTER, altitude=alt, northUp=True)
    time.sleep(4)
    call("jawa/clear_ui", devWindows=True, clearSelection=True)
    time.sleep(1)
    shot = call("jawa/take_screenshot", fileName=label)
    show("shot %s:" % label, shot, ["success","path","fullPath","fileName","message"])

print("=== final state ===")
show("final:", call("jawa/world_map_mode"),
     ["modeAfter","regenBusy","regenerateNow","worldRendered","tilesPrepared"])
