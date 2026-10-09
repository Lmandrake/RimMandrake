import sys; sys.path.insert(0,"Transient")
from belt_lc6_lib import *
W=json.load(open("Transient/belt_lc6_w1.json"))["W"]
def snap():
    p=[a for a in census()["pawns"] if a["id"]==W]
    g=call("jawa/pawn_get", pawn=W)["pawns"]
    v=call("jawa/comp_read", thing=W, comp="WatcherStalk", members="phase,angle")["values"]
    hid=any(h["def"]=="RM_WatcherHidden" for h in g[0]["hediffs"]) if g else None
    sg=len(call("jawa/list_things", defName="RM_WatcherSign_SeamGlint")["things"])
    return (p[0]["job"]["def"] if p and p[0].get("job") else None, v["phase"], round(float(v["angle"])), hid, sg)
print("start", snap())
r=spawn_pawn("Colonist",96,45,"player",1)["pawns"][0]; cid=r["id"]; print("colonist at",r["x"],r["z"])
call("jawa/set_draft", pawnId=cid, drafted=True)
last=None; 
for i in range(60):
    step(10); s=snap()
    if s[:2]+s[3:]!=last: print((i+1)*10, s); last=s[:2]+s[3:]
    if s[1]=="Down" and s[3]: break
