import os, sys, time, shutil, json
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "GimmeSomeSlack"))
import validation_aerial as VA
B = VA.A()
B.call("jawa/build_batch", ops="RM_PowerTapClamp:28,23", faction="player", wipeExisting=False)
B.call("jawa/map_commit"); B.ticks(5)
out = os.path.join(os.getcwd(), "Transient", "bench_live_20261011", "shots")
for name, (x, z) in (("tapclamp_EW_close", (28, 23)), ("tapclamp_NS_close", (57, 27))):
    for rs in (8, 12):
        B.call("jawa/clear_ui", all=True)
        r = B.call("rimworld/jump_camera_to_cell", x=x, z=z, rootSize=rs)
        time.sleep(2.0)
        cam = B.call("rimworld/get_camera_state")
        s = B.call("jawa/take_screenshot", fileName="%s_rs%d" % (name, rs))
        time.sleep(1.5)
        src = s.get("filePath")
        for _ in range(10):
            if src and os.path.exists(src): break
            time.sleep(0.5)
        shutil.copyfile(src, os.path.join(out, "%s_rs%d.png" % (name, rs)))
        print(name, rs, r.get("success"), json.dumps(cam)[:150])
