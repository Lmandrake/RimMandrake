"""Stage keeper (d): tall venomvine on the Scrub site beside a human (python.exe). args X Z"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "src", "RimMandrake", "Utils"))
import validation_core as V
B = V.Bridge()
X, Z = int(sys.argv[1]), int(sys.argv[2])
B.call("jawa/destroy_batch", rects="%d,%d,34,12" % (X - 4, Z - 4), categories="Plant,Item,Filth")
B.call("jawa/set_fog", action="unfog", rect="%d,%d,40,20" % (X - 8, Z - 8))
row = ["RM_VenomvineThicket"] * 4 + ["RM_DrippingVenomvine", "RM_TwitcherVenomvine", "RM_HollowVenomvine", "RM_CrownVenomvine"]
for i, d in enumerate(row):
    r = B.call("jawa/set_plants", ops="%s:%d,%d,1,1" % (d, X + 3 * i, Z), growth=1.0)
    print(d, X + 3 * i, Z, r.get("planted"), r.get("rejectionReasons"))
r = B.call("jawa/spawn_pawn", kindDef="Colonist", x=X - 2, z=Z, count=1, faction="PlayerColony")
pid = r["pawns"][0]["id"]
B.call("jawa/set_draft", pawnId=pid, drafted=True)
B.call("jawa/set_pawn_rotation", pawnId=pid, dir="south", lockRotation=True)
B.call("jawa/set_pawn_identity", pawn=pid, single="human (scale)") if False else None
B.call("rimworld/set_time_speed", speed=0)
B.call("jawa/clear_ui")
B.call("rimworld/jump_camera_to_cell", x=X + 10, z=Z)
B.call("rimworld/frame_cell_rect", x=X - 3, z=Z - 3, width=30, height=8, paddingCells=2)
print(B.call("rimworld/take_screenshot", fileName="walk_venomvine").get("path"))
