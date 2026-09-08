import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\Transient\seabeast_review")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from sb_common import rb
import game_focus

print("focus fns:", [n for n in dir(game_focus) if not n.startswith("_")])
prev = game_focus.focus_game()
print("prev focus:", prev)
time.sleep(2)
tag = str(int(time.time()))
with rb() as b:
    b.call("jawa/clear_ui", {})
    b.call("jawa/screenshot_mode", {"enabled": True})
    for nm, x, z, root in [("a2", 100, 32, 12), ("a2off", 100, 50, 12)]:
        b.call("rimworld/jump_camera_to_cell", {"x": x, "z": z})
        b.call("rimworld/set_camera_zoom", {"rootSize": root})
        time.sleep(1)
        r = b.call("jawa/take_screenshot", {"fileName": "f_%s_%s" % (nm, tag)})
        print(nm, r.get("fileName"))
