import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
GSS = os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack"); sys.path[:0] = [GSS, os.path.join(GSS, "northstar"), os.path.join(REPO, "src", "RimMandrake", "Utils")]
import validation as V, validation_aerial as VA
B = VA.A()
c = B.probe("census"); print(json.dumps(c.get("cordsAcrossNetsList"))[:900])
print("joins", json.dumps(B.probe("joins"))[:500])
r = B.probe("rect:220,54,16,12"); print({k: v for k, v in r.items() if k not in ("polylines",)})
for z in range(54, 66):
    for x in range(220, 236):
        n = B.ap("net:%d,%d" % (x, z))
        if n.get("things"): print((x, z), n["net"], [(t["def"], t["net"], t.get("connectParent"), t["id"]) for t in n["things"]])
B.call("rimworld/jump_camera_to_cell", x=228, z=60); B.call("rimworld/set_camera_zoom", rootSize=9); B.call("jawa/review_label", action="hide"); B.call("jawa/clear_ui"); time.sleep(1.2)
print(B.call("rimworld/take_screenshot", fileName="gss_v3_loop228").get("path")); B.call("jawa/review_label", action="show")
