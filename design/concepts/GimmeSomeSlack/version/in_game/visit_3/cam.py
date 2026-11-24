import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
GSS = os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack"); sys.path[:0] = [GSS, os.path.join(GSS, "northstar"), os.path.join(REPO, "src", "RimMandrake", "Utils")]
import validation_aerial as VA
B = VA.A(); B.call("jawa/review_label", action="hide"); B.call("jawa/clear_ui")
for a in sys.argv[1:]:
    x, z, root, n = a.split(","); B.call("rimworld/jump_camera_to_cell", x=int(x), z=int(z)); B.call("rimworld/set_camera_zoom", rootSize=float(root)); time.sleep(1.5); B.call("jawa/clear_ui")
    print(B.call("rimworld/take_screenshot", fileName=n).get("path")); time.sleep(1.5)
B.call("jawa/review_label", action="show")
