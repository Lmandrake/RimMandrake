# Pyrelands live quicktest battery — BENCH 2026-09-13
# Runs under python.exe (Windows). Proves: weather defs fire + read back,
# plants spawn with visible art, RUT fauna spawn. Screenshots to this folder.
import sys, time, json, traceback
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

OUT = r"D:\Luke\dev\Rimworld\Transient\pyrelands_quicktest_2026-09-13"
LOGP = OUT + r"\battery_log.txt"
log_f = open(LOGP, "w", encoding="utf-8")
def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True); log_f.write(s + "\n"); log_f.flush()

host, port, token = resolve_endpoint()

def fresh():
    rb = RimBridge(host, port, token)
    rb.connect()
    return rb

def call(rb, tool, params=None, timeout_ok=False):
    try:
        r = rb.call(tool, params or {})
        return r
    except Exception as e:
        log(f"CALL-EXC {tool}: {e}")
        if timeout_ok:
            return None
        raise

# ---- 1. start quicktest (timeout expected; reconnect + poll) ----
rb = fresh()
log("== start_debug_game_ready (timeout is normal) ==")
try:
    r = rb.call("rimworld/start_debug_game_ready", {})
    log("start returned:", str(r)[:200])
except Exception as e:
    log("start timed out as documented:", e)
try:
    rb.close()
except Exception:
    pass

map_up = False
for i in range(40):  # up to ~200s
    time.sleep(5)
    try:
        rb = fresh()
        r = rb.call("jawa/list_pawns", {})
        msg = str(r)[:120]
        if r and r.get("success") and "No current map" not in str(r.get("message", "")):
            log(f"poll {i}: map is up — {msg}")
            map_up = True
            rb.close()
            break
        log(f"poll {i}: not yet — {msg}")
        rb.close()
    except Exception as e:
        log(f"poll {i}: conn not ready: {e}")
if not map_up:
    log("FATAL: map never came up"); sys.exit(2)

log("settle 45s (bridge-answering != game-reactive)")
time.sleep(45)

rb = fresh()

# pause hard before anything else
call(rb, "rimworld/set_time_speed", {"speed": 0})
t1 = call(rb, "rimworld/get_game_info", {})
log("game info:", str(t1)[:200])

# ---- 2. verify defs live on this map's session ----
r = call(rb, "jawa/get_defs", {"defs": "WeatherDef/RM_FE_Weather_Cinderfall;WeatherDef/RM_FE_Weather_AshFall;WeatherDef/RM_FE_BlackRain;ThingDef/RM_FE_Plant_EmberGrass;ThingDef/RM_FE_Plant_ScorchFruit", "fields": "label"})
for d in r["defs"]:
    log("def:", d["requested"], d["found"])

# camera anchor: first colonist
col = call(rb, "rimworld/list_colonists", {"currentMapOnly": True})
log("colonists:", str(col)[:200])
cx, cz = 125, 125
try:
    p0 = col["colonists"][0]
    cx, cz = int(p0.get("x", cx)), int(p0.get("z", cz))
except Exception:
    log("no colonist coords; using map centre-ish", cx, cz)

def shot(name):
    call(rb, "jawa/clear_ui", {}, timeout_ok=True)
    r = call(rb, "rimworld/take_screenshot", {"fileName": name})
    log("shot:", name, str(r)[:160])
    return r

def set_weather(defname, tag):
    w0 = call(rb, "jawa/weather_get", {})
    r = call(rb, "jawa/weather_set", {"defName": defname})
    log(f"weather_set {defname}:", str(r)[:120])
    call(rb, "rimworld/step_game_ticks", {"ticks": 600})
    w1 = call(rb, "jawa/weather_get", {})
    log(f"weather read-back {defname}: before={str(w0)[:80]} after={str(w1)[:80]}")
    shot(f"pyre_qt_{tag}")

# ---- 3. weather battery ----
call(rb, "rimworld/jump_camera_to_cell", {"x": cx, "z": cz}, timeout_ok=True)
shot("pyre_qt_baseline")
for dn, tag in [("RM_FE_Weather_Cinderfall", "cinderfall"),
                ("RM_FE_Weather_AshFall", "ashfall"),
                ("RM_FE_BlackRain", "blackrain")]:
    try:
        set_weather(dn, tag)
    except Exception:
        log("weather leg failed:", dn); log(traceback.format_exc()[:400])

# ---- 4. plants ----
px = cx + 8
for i, dn in enumerate(["RM_FE_Plant_EmberGrass"] * 5 + ["RM_FE_Plant_ScorchFruit"] * 5):
    r = call(rb, "rimworld/spawn_thing", {"defName": dn, "x": px + (i % 5) * 2, "z": cz + (2 if i < 5 else 5)}, timeout_ok=True)
    log("spawn", dn, str(r)[:100])
cell = call(rb, "rimworld/get_cell_info", {"x": px, "z": cz + 2})
log("cell readback:", str(cell)[:250])
call(rb, "rimworld/jump_camera_to_cell", {"x": px + 4, "z": cz + 3}, timeout_ok=True)
shot("pyre_qt_plants")

# ---- 5. fauna (paused throughout; spawn at offset, batch of 3 each) ----
ch = call(rb, "rimworld/list_debug_action_children", {"path": "Actions\\Spawn Pawn..."})
paths = {}
for c in ch.get("children", []):
    leaf = c["path"].split("\\")[-1]
    if leaf.startswith("RUT_FireHawk") or leaf.startswith("RUT_FurnaceBeast"):
        paths[leaf.split("\t")[0].strip()] = c["path"]
log("spawn-pawn leaves found:", list(paths.keys()))
fy = cz - 8
for kind, path in paths.items():
    for j in range(3):
        r = call(rb, "rimworld/execute_debug_action", {"path": path, "x": px + j * 4, "z": fy}, timeout_ok=True)
        log("spawn pawn", kind, j, str(r)[:100])
    fy -= 5
pl = call(rb, "jawa/list_pawns", {})
names = [p.get("kindDef", p.get("name", "?")) for p in pl.get("pawns", [])] if pl else []
log("pawns on map now:", names[:40])
call(rb, "rimworld/jump_camera_to_cell", {"x": px + 4, "z": cz - 10}, timeout_ok=True)
shot("pyre_qt_fauna")

call(rb, "rimworld/set_time_speed", {"speed": 0})
log("== battery done ==")
rb.close()
log_f.close()
