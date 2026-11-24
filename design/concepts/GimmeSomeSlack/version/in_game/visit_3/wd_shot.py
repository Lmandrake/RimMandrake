"""wd_shot.py name: the wire-down plot staged on the map that is up, cut, and captured. python.exe."""
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
GSS = os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack"); sys.path[:0] = [GSS, os.path.join(GSS, "northstar"), os.path.join(REPO, "src", "RimMandrake", "Utils")]
import validation as V, validation_aerial as VA, save_wire_down as WD
B = VA.A(); WD.stage(B, V); WD.wire_down(B); r = WD.read(B); print(r["ends"], r["cords"], WD.midway(r))
B.call("jawa/clear_ui"); B.call("rimworld/jump_camera_to_cell", x=69, z=217); B.call("rimworld/set_camera_zoom", rootSize=11); time.sleep(1.2)
print(B.call("rimworld/take_screenshot", fileName=sys.argv[1]).get("path"))
