import json, sys, time, os, shutil
sys.path.insert(0, "src/RimMandrake/GimmeSomeSlack/northstar_matrix"); sys.path.insert(0, "src/RimMandrake/Utils")
import run_live as RL
B = RL.LiveBridge()
c = B.probe("census")
s = json.load(open("ralph/live/lived_state.json")); ox, oz = s["ox"], s["oz"]
print(ox, oz, json.dumps(c["edgeHashes"])[:1500])
B.call("jawa/clear_ui", all=True)
res = B.call("rimworld/screenshot_cell_rect", x=ox+18, z=oz+2, width=18, height=14, paddingCells=0, fileName="p7a_cutlead_"+str(int(time.time())), rootSize=7)
src = res.get("filePath") or res.get("path") or res.get("savedPath")
time.sleep(2.5); shutil.copyfile(src, r"D:\ClaudeWork\rimmandrake\ralph_gss\shots\p7a_cutlead.png"); print("ok")
