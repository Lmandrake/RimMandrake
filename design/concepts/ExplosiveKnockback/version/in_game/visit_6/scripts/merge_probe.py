import sys,json; sys.path.insert(0, r"src\RimMandrake\Utils"); sys.path.insert(0, r"src\RimMandrake\ExplosiveKnockback")
import knockback_runner as K
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t=resolve_endpoint()
with RimBridge(host=h,port=p,token=t) as b:
    snap=K.snapshot_settings(b)
    try:
        for rep in range(3):
            K.call(b,"Settings","reset"); K.call(b,"Clear","x")
            o=K.call(b,"Origins","2").split(";")[1]
            print("stage",K.call(b,"Stage","closed_containers_control,"+o)[:120])
            ox,oz=map(int,o.split(","))
            last=None
            for n in range(0,301,15):
                K.advance_scene(b,15)
                r=b.call("jawa/list_things",{"defName":"Steel","rect":"%d,%d,30,40"%(max(0,ox-12),0),"limit":60})
                th=[(x.get("id"),x.get("x"),x.get("z"),x.get("stackCount"),x.get("forbidden")) for x in r.get("things",[])]
                pw=[(x["id"],x.get("job") or x.get("jobDef") ,x["x"],x["z"]) for x in b.call("jawa/list_pawns",{"rect":"%d,%d,30,40"%(max(0,ox-12),0)})["pawns"] if x.get("isPlayer") and not x["dead"]]
                if th!=last: print(n+15,th,pw); last=th
            print(K.call(b,"Verdict","closed_containers_control")[:200])
    finally: K.restore_settings(b,snap)
