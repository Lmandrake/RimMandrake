import json, sys
sys.path.insert(0, "src/RimMandrake/GimmeSomeSlack/northstar_matrix"); sys.path.insert(0, "src/RimMandrake/Utils")
import run_live as RL
B = RL.LiveBridge()
s = json.load(open("ralph/live/lived_state.json")); ox, oz = s["ox"], s["oz"]
print(ox, oz)
print(json.dumps(B.probe("ends:%d,%d,4" % (ox + 50, oz - 8)))[:900])
print(json.dumps(B.call("jawa/list_things", defName="Battery", rect="%d,%d,6,6" % (ox + 47, oz - 11), limit=5))[:500])
c = B.probe("census")
print(json.dumps([k for k in c["edgeHashes"] if "%d,%d" % (ox + 50, oz - 8) in k or "bat" in k.lower() or "Battery" in k])[:700])
print(json.dumps(c.get("ends"))[:400])
