"""T13 isolation: a colonist at need 0 beside a painted strip of <terrain> only (python.exe). args: terrain x z"""
import sys, os, re, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "src", "RimMandrake", "FlowWorks", "northstar"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "src", "RimMandrake", "Utils"))
import validation_core as V
B = V.Bridge()
terr, X, Z = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
B.call("jawa/destroy_batch", rects="%d,%d,10,10" % (X - 3, Z - 3), categories="Plant,Item,Building")
B.call("jawa/set_terrain_batch", ops="Soil:%d,%d,10,10;%s:%d,%d,4,%d" % (X - 3, Z - 3, terr, X, Z, int(sys.argv[4]) if len(sys.argv) > 4 else 4))
r = B.call("jawa/spawn_pawn", kindDef="Colonist", x=X + 1, z=Z + 5, count=1, faction="PlayerColony")
pid = B.call("jawa/list_pawns", rect="%d,%d,1,1" % (X + 1, Z + 5)).get("pawns")[0]["id"]
for nd in ("Food", "Rest", "Joy", "Mood"):
    B.call("jawa/pawn_need", pawn=pid, action="need", need=nd, level=1.0)
if len(sys.argv) > 5:
    B.call("jawa/pawn_need", pawn=pid, action="need", need="RM_Thirst", level=float(sys.argv[5]))
    pre = []
    for i in range(10):
        B.ticks(100)
        pre += [c.get("job") for c in B.call("rimworld/list_colonists", currentMapOnly=True).get("colonists") if c.get("pawnId") == "Thing_" + pid]
    print("pre", pre)
B.call("jawa/pawn_need", pawn=pid, action="need", need="RM_Thirst", level=0.0)
B.call("rimworld/set_colonist_job_logging", pawnId="Thing_" + pid, enabled=True)
seen = []
for i in range(20):
    B.ticks(60)
    j = [c.get("job") for c in B.call("rimworld/list_colonists", currentMapOnly=True).get("colonists") if c.get("pawnId") == "Thing_" + pid]
    seen.append(j[0] if j else None)
    B.call("jawa/pawn_need", pawn=pid, action="need", need="RM_Thirst", level=0.0) if False else None
lv = [n for n in B.call("jawa/pawn_need", pawn=pid, action="list").get("needs") if n["need"] == "RM_Thirst"]
print(pid, seen, lv)
