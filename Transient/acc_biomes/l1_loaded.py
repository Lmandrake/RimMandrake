import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rbc
host,port,token=rbc.resolve_endpoint()
with rbc.RimBridge(host,port,token) as rb:
    tl=rb.list_tools()
    for t in tl:
        n=t.get("name","")
        if n.split("/")[-1] in ("thing_graphic","spawn_variant","running_mods","glow_at","site_state","debug_action_yielders"):
            print(n, json.dumps(t.get("inputSchema",t.get("input_schema",{})).get("properties",{}))[:300], t.get("inputSchema",{}).get("required"))
    r=rb.call("jawa/get_defs",{"defs":"ThinkTreeDef/RM_Chotrix","fields":"thinkRoot","deep":True},check=False)
    print("tt",r.get("success"),r.get("foundCount"),r.get("notFound"),json.dumps(r.get("defs"))[:700])
