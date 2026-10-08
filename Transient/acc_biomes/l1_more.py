import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rbc
host,port,token=rbc.resolve_endpoint()
with rbc.RimBridge(host,port,token) as rb:
    for defs,f in [("JobDef/RM_ChotrixDragKill",None),("BiomeDef/RM_Warscar","modExtensions"),("BiomeDef/RM_Wasteland","modExtensions")]:
        a={"defs":defs,"deep":True}
        if f: a["fields"]=f
        r=rb.call("jawa/get_defs",a,check=False)
        print(defs,r.get("success"),r.get("foundCount"),json.dumps(r.get("defs"))[:1500]);print()
    r=rb.call("jawa/get_defs",{"defs":"BiomeDef/RM_Wasteland","fields":"modExtensions","deep":True,"typeNames":True},check=False)
    r=rb.call("jawa/debug_action_yielders",{"limit":60},check=False)
    print("YIELD",r.get("success"),json.dumps(r)[:500])
    print(json.dumps(rb.call("rimworld/get_game_info",{},check=False))[:200])
