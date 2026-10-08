import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rbc
host,port,token=rbc.resolve_endpoint()
with rbc.RimBridge(host,port,token) as rb:
    for t,a in [("jawa/running_mods",{"details":False}),("jawa/glow_at",{"cells":"50,50;60,60"}),("jawa/site_state",{}),("jawa/thing_graphic",{"rect":"40,40,20,20"}),("jawa/spawn_variant",{"def":"Steel","cell":"50,50"})]:
        r=rb.call(t,a,check=False)
        print(t,"success=",r.get("success"),json.dumps({k:v for k,v in r.items() if k not in("operation","state")})[:350]);print()
