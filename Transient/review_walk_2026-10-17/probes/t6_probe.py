"""T6 isolation: drafted colonist at thirst 0, read RM_Dehydration and need every 1,500 ticks (python.exe)."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "src", "RimMandrake", "Utils"))
import validation_core as V
B = V.Bridge()
r = B.call("jawa/spawn_pawn", kindDef="Colonist", x=170, z=150, count=1, faction="PlayerColony")
pid = r["pawns"][0]["id"]
B.call("jawa/set_draft", pawnId=pid, drafted=True)
for nd in ("Food", "Rest", "Joy", "Mood"):
    B.call("jawa/pawn_need", pawn=pid, action="need", need=nd, level=1.0)
B.call("jawa/pawn_need", pawn=pid, action="need", need="RM_Thirst", level=0.0)
t0 = B.call("rimworld/get_game_info").get("ticksGame")
for i in range(6):
    B.ticks(1500)
    t = B.call("rimworld/get_game_info").get("ticksGame")
    lv = [n["level"] for n in B.call("jawa/pawn_need", pawn=pid, action="list")["needs"] if n["need"] == "RM_Thirst"]
    hd = {h.get("def"): h.get("severity") for h in B.call("jawa/pawn_get", pawn=pid)["pawns"][0]["hediffs"]}
    print(t - t0, lv, hd, flush=True)
