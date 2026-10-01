from bx import call
import json
ps=call("jawa/list_pawns",{"limit":400}).get("pawns",[])
lo=[(p["id"],p["x"],p["z"],p.get("dead")) for p in ps if p.get("kindDef")=="RM_Loomma"]; print(lo)
for _,x,z,_ in lo:
    c=call("rimworld/get_cell_info",{"x":x,"z":z}); print(x,z,{k:c.get(k) for k in c if k in ("terrain","terrainDefName","roof","roofDefName","temperature","isRoofed")}, str(c)[:250])
print(json.dumps(call("jawa/time_clock",{}),default=str)[:800])
