import sys; sys.path.insert(0,"Transient")
from cp_lib import *
c = call("jawa/pawn_census", ids="Human963"); p=c["pawns"][0]; print("snappy", p["x"], p["z"], "food", p["needs"]["food"])
x,z = p["x"]+3, p["z"]
for dn in ("Meat_Muffalo","MeatRaw","Meat_Megasloth"):
    r = call("rimworld/spawn_thing", defName=dn, x=x, z=z, stackCount=20); print(dn, J(r,350))
    if r.get("success"): break
