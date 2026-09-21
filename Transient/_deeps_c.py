import sys, json, time; sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge
T="4f3c0a7aa74e4446ac19465c14fd54a9"
b=RimBridge(token=T,timeout=60); b.connect()
def call(t,p): 
    r=b.call(t,p,check=False); print(t,"->",json.dumps(r)[:260]); return r
# existing colonists on the quicktest
pawns=call("jawa/list_pawns",{"faction":"player","limit":5})
ps=pawns.get("pawns") or []
if not ps: sys.exit("no colonists")
p=ps[0]; pid=p.get("id") or p.get("thingId"); pos=p.get("position") or {}
x,z=int(pos.get("x",125)),int(pos.get("z",125))
print("colonist",pid,"at",x,z)
# clear-ish spot 6 tiles east
px,pz=x+6,z
r=call("jawa/spawn_batch",{"ops":"RUT_LanternDeepEmergence:%d,%d,1"%(px,pz)})
th=call("jawa/list_things",{"defName":"RUT_LanternDeepEmergence","limit":3})
things=th.get("things") or []
if not things: sys.exit("portal not spawned")
tid=things[0].get("id") or things[0].get("thingId")
print("portal id",tid)
r=call("jawa/ordered_job",{"pawnId":str(pid),"jobDef":"EnterPortal","targetAId":str(tid)})
call("rimworld/set_game_speed",{"speed":3}) if False else None
