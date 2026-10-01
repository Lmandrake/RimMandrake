from bx import call
import collections
ps=call("jawa/list_pawns",{"limit":400}).get("pawns",[])
print([(p["id"],p["x"],p["z"],p.get("hostile"),p.get("downed")) for p in ps if p.get("kindDef")=="RM_Zuurrik"])
for d in ("Filth_Blood","Corpse_Chicken","Corpse_Hare","Corpse_Muffalo"):
    r=call("jawa/list_things",{"defName":d,"limit":200}); print(d,[(t.get("x"),t.get("z")) for t in r.get("things",[])][:30])
print(call("rimworld/get_game_info",{}).get("ticksGame") if False else call("jawa/map_info",{}).get("ticksGame"))
