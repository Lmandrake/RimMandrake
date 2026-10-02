import sys, json, time
sys.path.insert(0, "src/RimMandrake/Utils"); sys.path.insert(0, "src/RimMandrake/Utils/modcheck")
from rimdrive.session import Session
with Session(strict=False, quiet=True, focus=False) as s:
    f = s.call("jawa/list_things", defName="Fire", limit=300)
    th = f["things"]; xs=[t["x"] for t in th]; zs=[t["z"] for t in th]
    print("fires", len(th), "x", min(xs), max(xs), "z", min(zs), max(zs), "centroid", sum(xs)//len(xs), sum(zs)//len(zs))
    # what burns: things in the cluster centre
    cx, cz = sum(xs)//len(xs), sum(zs)//len(zs)
    r = s.call("jawa/list_things", rect="%d,%d,12,12" % (cx-6, cz-6), limit=60)
    from collections import Counter
    print("things near centroid:", Counter(t["def"] for t in r["things"]).most_common(10))
    s.call("jawa/clear_ui", devWindows=True, clearSelection=True)
    s.call("rimworld/jump_camera_to_cell", x=cx, z=cz)
    s.call("rimworld/step_game_ticks", ticks=1, pauseFirst=True)
    r = s.call("rimworld/take_screenshot", fileName="np_fire122_%d" % int(time.time()), suppressMessage=True)
    print(r.get("path"), r.get("sizeBytes"))
    print("debug:", [ (m["type"], m["text"][:100]) for m in s.call("jawa/drain_log", limit=12)["messages"]])
