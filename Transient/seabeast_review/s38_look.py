import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\Transient\seabeast_review")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from sb_common import rb
import game_focus
game_focus.focus_game()
time.sleep(2)
tag = str(int(time.time()))
with rb() as b:
    b.call("rimworld/set_camera_zoom_extension", {"enabled": True})
    b.call("jawa/clear_ui", {})
    b.call("jawa/screenshot_mode", {"enabled": True})
    for nm, x, z, root in [("rowD", 100, 140, 30), ("cellD2", 100, 140, 10)]:
        b.call("rimworld/jump_camera_to_cell", {"x": x, "z": z})
        b.call("rimworld/set_camera_zoom", {"rootSize": root})
        time.sleep(2)
        s = b.call("jawa/take_screenshot", {"fileName": "look_%s_%s" % (nm, tag)})
        print(nm, s.get("fileName"))
