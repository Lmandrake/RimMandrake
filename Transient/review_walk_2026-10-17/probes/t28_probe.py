"""T28 isolation (python.exe): a sanguophage ingests a HemogenPack; thirst and the job log."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "src", "RimMandrake", "Utils"))
import validation_core as V
B = V.Bridge()
r = B.call("jawa/spawn_pawn", kindDef="Colonist", x=170, z=150, count=1, faction="PlayerColony", xenotype="Sanguophage")
pid = r["pawns"][0]["id"]
B.call("jawa/set_draft", pawnId=pid, drafted=True)
B.call("rimworld/set_colonist_job_logging", pawnId="Thing_" + pid, enabled=True)
lv = lambda: [n["level"] for n in B.call("jawa/pawn_need", pawn=pid, action="list")["needs"] if n["need"] == "RM_Thirst"]
B.call("jawa/pawn_need", pawn=pid, action="need", need="RM_Thirst", level=0.2)
genes = B.call("jawa/pawn_get", pawn=pid)["pawns"][0]
print("hediffs", genes.get("hediffs"))
t = B.call("rimworld/spawn_thing", defName="HemogenPack", x=171, z=150, stackCount=1)["thingId"].replace("Thing_", "")
o = B.call("jawa/ordered_job", pawnId=pid, jobDef="Ingest", targetAId=t, count=1, waitTicks=10)
print("order", {k: o.get(k) for k in ("accepted", "afterJobDef", "message")})
for i in range(30):
    B.ticks(60)
    print(i, lv(), [c.get("job") for c in B.call("rimworld/list_colonists", currentMapOnly=True)["colonists"] if c["pawnId"] == "Thing_" + pid])
