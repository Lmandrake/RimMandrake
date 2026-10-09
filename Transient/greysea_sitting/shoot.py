import sys, json, time
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rb
h,p,t = rb.resolve_endpoint(); S = rb.RimBridge(host=h,port=p,token=t,timeout=300.0); S.connect()
def call(n, **a):
    r = S.call(n, a) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    if isinstance(r, dict): r.pop("operation",None); r.pop("state",None)
    return r
X0,Z0,W,H = json.load(open(r"Transient\greysea_sitting\window.json"))["window"]
call("jawa/set_current_map", mapId=4)
call("jawa/world_view", show=False)
print("FOG", json.dumps(call("jawa/set_fog", action="unfog", rect="0,0,250,250"))[:200])
hr = call("jawa/static_call", type="RimWorld.GenLocalDate", method="HourOfDay", args="current")
print("HOUR", hr)
tg = call("rimworld/get_game_info").get("ticksGame")
try:
    hour = int(hr.get("result"))
    if not (10 <= hour <= 14):
        add = ((12 - hour) % 24) * 2500
        print("TIMESET", call("jawa/time_set_ticks", ticks=tg+add))
except Exception as e: print("hour parse fail", e)
print("HOUR2", call("jawa/static_call", type="RimWorld.GenLocalDate", method="HourOfDay", args="current").get("result"))
def shot(name):
    call("jawa/clear_ui")
    call("rimworld/jump_camera_to_cell", x=X0+W//2, z=Z0+H//2)
    call("rimworld/frame_cell_rect", x=X0, z=Z0, width=W, height=H, paddingCells=3)
    if ZOOM: print("ZOOM", call("rimworld/set_camera_zoom", rootSize=ZOOM).get("success")); call("rimworld/jump_camera_to_cell", x=X0+W//2, z=Z0+H//2)
    cam = call("rimworld/get_camera_state"); print("CAM", cam.get("mapId"), cam.get("rootSize"))
    time.sleep(5)
    r = call("rimworld/take_screenshot", fileName=name, suppressMessage=True); print("SHOT", r.get("path"))
mode = sys.argv[1]
if len(sys.argv) > 2: X0,Z0,W,H = [int(v) for v in sys.argv[2].split(",")]
ZOOM = float(sys.argv[5]) if len(sys.argv)>5 else 0
suffix = sys.argv[3] if len(sys.argv) > 3 else ""
if mode == "clear":
    print("W", call("jawa/weather_set", weather="Clear", lockWeather=True))
    shot("greysea_floor_clear"+suffix)
else:
    print("W", call("jawa/weather_set", weather="RM_GreySaltSnow", lockWeather=True))
    for _ in range(int(sys.argv[4]) if len(sys.argv)>4 else 3): call("rimworld/step_game_ticks", ticks=500)
    print("WGET", call("jawa/weather_get"))
    shot("greysea_floor_saltsnow"+suffix)
