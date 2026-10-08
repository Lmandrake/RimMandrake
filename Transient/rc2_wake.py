import sys, os, json, time
U=os.path.join(os.getcwd(),"src","RimMandrake","Utils"); sys.path.insert(0,U)
import rimbridge_client as rb
h,p,t=rb.resolve_endpoint(); c=rb.RimBridge(host=h,port=p,token=t,timeout=120.0); c.connect()
def call(tool,**a):
    r=c.call(tool,a)
    if isinstance(r,dict) and r.get("content"): r=json.loads(r["content"][0]["text"])
    return r
x,z=int(sys.argv[1]),int(sys.argv[2])
kinds=sys.argv[3].split(",")   # e.g. Elephant,Rat
call("jawa/destroy_batch",rects="%d,%d,30,30"%(x-15,z-15),categories="All")
ids={}
for i,k in enumerate(kinds):
    lz=z+i*6
    r=call("jawa/spawn_pawn",kindDef=k,x=x,z=lz,faction="none",count=1); pid=r["pawns"][0]["id"]; ids[k]=(pid,lz)
    for dx in range(3,15,2): call("jawa/spawn_batch",ops="Plant_Grass:%d,%d"%(x+dx,lz))
    print(k,pid,call("jawa/pawn_stats",pawn=pid,stats="BodySize",limit=4).get("stats"))
def filth(lz): 
    return call("jawa/list_things",defName="Filth_RubbleRock",rect="%d,%d,16,3"%(x,lz-1),limit=50).get("countMatched")
print("baseline filth",{k:filth(v[1]) for k,v in ids.items()})
for k,(pid,lz) in ids.items():
    j=call("jawa/ordered_job",pawnId=pid,jobDef="Goto",targetAX=x+15,targetAZ=lz,waitTicks=0,timeoutSeconds=60); print(k,"job",j.get("nowRunningRequested"))
call("rimworld/step_game_ticks",ticks=500) if False else None
t0=call("rimworld/get_ui_state").get("tick") if False else None
for _ in range(8):
    r=call("rimworld/step_game_ticks",ticks=100)
print(str(r)[:200])
print("after filth",{k:filth(v[1]) for k,v in ids.items()})
for k,v in ids.items():
    print(k,"plants",call("jawa/list_things",defName="Plant_Grass",rect="%d,%d,16,1"%(x,v[1]),limit=50).get("countMatched"))
for f in call("jawa/list_things",defName="Filth_RubbleRock",rect="%d,%d,30,30"%(x-15,z-15),limit=50).get("things"): print(f["x"],f["z"])
