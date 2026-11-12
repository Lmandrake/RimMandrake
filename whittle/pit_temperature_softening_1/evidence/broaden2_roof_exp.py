"""BROADEN: roof the open pit at noon (run 18 review save). Does the pit's resistance loss stop at once while heatstroke
lingers, and does the compassionate colonist's RM_ExposedPrisoner expire about a day after the roof goes on?"""
import sys, os, json, time
sys.path.insert(0, os.getcwd())
import proof_hose as PH
B = PH.PB()
NSP = "RimMandrake.FlowWorks.RM_NorthstarProofs"
OUT = sys.argv[1]
phase = sys.argv[2]
res = json.load(open(OUT)) if phase != "start" else {"save": "RM_PitExposure_Review_20261112T032231", "samples": []}
def sc(m, a):
    r = B.call("jawa/static_call", type=NSP, method=m, args=a, _answer=True) or {}
    return str(r.get("result") or r.get("message") or "")
def kv(s):
    return {k: v for k, v in (t.split("=", 1) for t in s.split() if "=" in t)}
def sample(label):
    pa = kv(sc("ProofExposure", "Human9195"))
    th = (B.call("jawa/pawn_thoughts", pawn="Human237") or {}).get("thoughts") or []
    mem = [(t.get("def"), t.get("moodOffset"), t.get("label")) for t in th if t.get("def") == "RM_ExposedPrisoner"]
    s = {"label": label, "hour": pa.get("hour"), "exposed": pa.get("exposed"), "marker": pa.get("marker"),
         "resistance": pa.get("resistance"), "heatstroke": pa.get("heatstroke"), "hurting": pa.get("hurting"),
         "roomTemp": pa.get("roomTemp"), "outdoor": pa.get("outdoor"), "outdoorRoom": pa.get("outdoorRoom"),
         "Manuel_RM_ExposedPrisoner": mem}
    res["samples"].append(s)
    print(json.dumps(s), flush=True)
    json.dump(res, open(OUT, "w"), indent=1)
if phase == "start":
    print(str(B.call("rimworld/load_game_ready", saveName=res["save"], timeoutMs=280000))[:120])
    print(PH.V._wait_playing(B, leave_s=0))
    B.call("jawa/clear_ui", all=True)
    B.call("jawa/storyteller_and_site", storyteller="off") if False else None
    sample("noon, open (before roof)")
    B.call("rimworld/step_game_ticks", ticks=2500, pauseFirst=True, timeoutMs=240000)
    sample("+1h, still open")
    res["roof"] = B.call("jawa/set_roof_batch", ops="RoofConstructed:109,120,5,5")
    res["roomA_after_roof"] = sc("ProofRoom", "111,122;111,126")
    print("roof", str(res["roof"])[:200], res["roomA_after_roof"])
    sample("roof just placed")
    phase = "run"
n = int(sys.argv[3]) if len(sys.argv) > 3 else 6
for i in range(n):
    B.call("rimworld/step_game_ticks", ticks=2500 if len(res["samples"]) < 10 else 1250, pauseFirst=True, timeoutMs=240000)
    sample("after roof")
