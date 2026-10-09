import sys; sys.path.insert(0,"Transient")
from belt_lc6_lib import *
T="RimMandrake.Watchers.RM_WatchersSettings"
# clear every other pawn near, then flip hideAndFlinch off first (finer), then watchersEnabled
def hidden_ids():
    out=[]
    for p in census()["pawns"]:
        if p["kindDef"]=="RM_Piinnok" and not p["dead"]:
            g=call("jawa/pawn_get", pawn=p["id"])["pawns"][0]
            if any(h["def"]=="RM_WatcherHidden" for h in g["hediffs"]): out.append(p["id"])
    return out
print("hidden before", len(hidden_ids()))
call("jawa/mod_settings_field", typeName=T, action="set", field="watchersEnabled", value="false")
step(120)
print("watchersEnabled false -> hidden after 120:", len(hidden_ids()), "signs", len(call("jawa/list_things", defName="RM_WatcherSign_SandDimple")["things"]))
r=spawn_pawn("Colonist",30,50,"player",1)  # place near field edge? piinnok field is 40-60; put adjacent to one
ps=[p for p in census()["pawns"] if p["kindDef"]=="RM_Piinnok" and not p["dead"]]
a=ps[0]
r=spawn_pawn("Colonist",a["x"]+2,a["z"],"player",1); cid=r["pawns"][0]["id"]
step(240)
print("colonist adjacent, disabled -> hidden:", len(hidden_ids()), "signs", len(call("jawa/list_things", defName="RM_WatcherSign_SandDimple")["things"]))
kill(cid)
call("jawa/mod_settings_field", typeName=T, action="set", field="watchersEnabled", value="true")
print(call("jawa/mod_settings_field", typeName=T, action="get", field="watchersEnabled").get("value"))
