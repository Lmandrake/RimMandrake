import sys, json, time
sys.path.insert(0, "src/RimMandrake/Utils"); sys.path.insert(0, "src/RimMandrake/Utils/modcheck")
from rimdrive.session import Session
def fires(s):
    f = s.call("jawa/list_things", defName="Fire", limit=300); return f["things"], f
with Session(strict=False, quiet=True, focus=False) as s:
    th,f = fires(s); print("t0 fires", len(th), f["countMatched"], s.call("jawa/time_clock")["ticksGame"])
    for i in range(4):
        s.call("rimworld/step_game_ticks", ticks=60, pauseFirst=True)
        th,f = fires(s); print("after +%d: fires %d (matched %s)" % (60*(i+1), len(th), f["countMatched"]))
    if th:
        xs=[t["x"] for t in th]; zs=[t["z"] for t in th]; cx,cz=sum(xs)//len(xs), sum(zs)//len(zs)
        print("bbox", min(xs),max(xs),min(zs),max(zs))
        s.call("jawa/clear_ui", devWindows=True, clearSelection=True)
        s.call("rimworld/jump_camera_to_cell", x=cx, z=cz)
        r = s.call("rimworld/take_screenshot", fileName="np_fires_%d" % int(time.time()), suppressMessage=True); print(r.get("path"))
    w = s.call("jawa/weather_get"); print("weather", w["weather"], [c["def"] for c in w["conditions"]])
    print("debug:", [(m["type"], m["text"][:100]) for m in s.call("jawa/drain_log", limit=12)["messages"]])
