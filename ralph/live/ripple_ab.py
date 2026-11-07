import json, sys, time, shutil
sys.path.insert(0, "src/RimMandrake/GimmeSomeSlack/northstar_matrix"); sys.path.insert(0, "src/RimMandrake/Utils")
import run_live as RL
B = RL.LiveBridge()
OUT = r"D:\ClaudeWork\rimmandrake\ralph_gss\shots"
def shot(n):
    B.call("jawa/clear_ui", all=True)
    u = "%s_%d" % (n, int(time.time()))
    r = B.call("rimworld/screenshot_cell_rect", x=164, z=128, width=9, height=7, paddingCells=0, fileName=u, rootSize=3.6)
    s = r.get("filePath") or r.get("path") or r.get("savedPath")
    if not s:
        print(json.dumps(r)[:600]); time.sleep(3)
        r = B.call("rimworld/screenshot_cell_rect", x=164, z=128, width=9, height=7, paddingCells=0, fileName=u + "b", rootSize=3.6)
        s = r.get("filePath") or r.get("path") or r.get("savedPath"); print(json.dumps(r)[:300])
    time.sleep(2.5); shutil.copyfile(s, OUT + "\\" + n + ".png")
print(B.probe(sys.argv[1] + "floorRipple=True") if len(sys.argv) > 1 else "")
B.call("rimworld/set_time_speed", speed=0)
print("wind", B.probe("census")["settings"].get("floorRipple") if isinstance(B.probe("census")["settings"], dict) else "?")
shot("p7c_ripple_on")
print(json.dumps(B.probe("set:floorRipple=False"))[:200])
B.probe("rebuild")
time.sleep(1)
shot("p7c_ripple_off")
print(json.dumps(B.probe("set:floorRipple=True"))[:200])
