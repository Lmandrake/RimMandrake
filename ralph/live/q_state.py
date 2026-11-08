"""Ad-hoc read of the current map for the mast scene: blueprints/frames of the lamp mast, colonists' health and jobs."""
import json, os, sys
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "GimmeSomeSlack", "northstar_matrix"))
import run_live as RL
B = RL.LiveBridge()
for d in ("Blueprint_RM_AerialLampMast", "Frame_RM_AerialLampMast", "RM_AerialLampMast"):
    r = B.call("jawa/list_things", defName=d, limit=10)
    print(d, json.dumps([{k: t.get(k) for k in ("id", "x", "z", "position", "faction")} for t in r.get("things") or []])[:300])
for p in B.call("jawa/list_pawns").get("pawns") or []:
    if p.get("isPlayer"):
        print(json.dumps({k: p.get(k) for k in ("name", "downed", "job", "curJob", "health", "position", "x", "z", "mentalState")})[:300])
for n in sys.argv[1:]:
    print(n, json.dumps(B.call(n))[:1500])
