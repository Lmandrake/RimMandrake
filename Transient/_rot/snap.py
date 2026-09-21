import sys, json, os, io, time
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
ROOMS={"R1_control":(143,103),"R2_produce":(153,103),"R3_mat":(163,103),"R4_stone":(173,103),"R5_furnace":(183,103),"R6_shelter":(193,103)}
PAWNS={"BARE":["Human36838","Human36841","Human36844"],"ROOF":["Human36847","Human36850","Human36853"],
       "HELM":["Human36856","Human36859","Human36862"],"SYM":["Human36865","Human36868","Human36871"]}
def snapshot(rb):
    out={}
    out["ticksGame"]=rb.call("rimworld/get_game_info",{}).get("ticksGame")
    mi=rb.call("jawa/map_info",{}); out["outdoorTemp"]=mi.get("outdoorTempNow"); out["mapBiome"]=mi.get("mapBiome")
    out["weather"]=rb.call("jawa/weather_get",{}).get("current") or rb.call("jawa/weather_get",{})
    t={}
    for n,(x,z) in ROOMS.items():
        rg=rb.call("jawa/room_get",{"x":x,"z":z}); rm=(rg.get("rooms") or [{}])[0]
        t[n]={"roomTemp":rm.get("temperature"),"cells":rm.get("cellCount"),"openRoof":rm.get("openRoofCount"),
              "cellTemp":rb.call("jawa/cell_temperature",{"cell":"%d,%d"%(x,z)}).get("temperature")}
    out["rooms"]=t
    meat={}
    for tag,rect in (("outdoor","144,119,8,3"),("control","141,101,5,3")):
        ins=rb.call("jawa/inspect_string",{"defName":"Meat_Cow","rect":rect})
        meat[tag]=[{"id":r.get("id"),"x":r.get("x"),"z":r.get("z"),"text":(" // ".join(r.get("inspect") or [])).replace("\n"," | ")} for r in ins.get("things",[])]
    out["meat"]=meat
    ph={}
    allp=rb.call("jawa/list_pawns",{"faction":"player","includeHealth":True}).get("pawns",[])
    byid={p["id"]:p for p in allp}
    for g,ids in PAWNS.items():
        ph[g]={}
        for pid in ids:
            p=byid.get(pid,{})
            hed={h.get("def"):h.get("severity") for h in (p.get("health") or {}).get("hediffs",[])}
            ci=rb.call("rimworld/get_cell_info",{"x":p.get("x",0),"z":p.get("z",0)})["cell"]
            ph[g][pid]={"xz":[p.get("x"),p.get("z")],"roof":ci.get("roofDefName"),"dead":p.get("dead"),
                        "SheenCoating":hed.get("RUT_SheenCoating"),"SporeFlesh":hed.get("RUT_SporeFlesh"),
                        "SporesBuildup":hed.get("RUT_SporesBuildup"),"SheenSymbiosis":hed.get("RUT_SheenSymbiosis"),
                        "all":sorted(hed.keys())}
    out["pawns"]=ph
    fur=rb.call("jawa/inspect_string",{"defName":"RUT_GrownFurnace"})
    out["furnace"]=[{"id":r.get("id"),"text":(" // ".join(r.get("inspect") or [])).replace("\n"," | ")} for r in fur.get("things",[])]
    return out
if __name__=="__main__":
    host,port,token=resolve_endpoint()
    tag=sys.argv[1]
    with RimBridge(host,port,token) as rb:
        s=snapshot(rb)
    p="Transient/_rot/snap_%s.json"%tag
    json.dump(s,open(p,"w"),indent=1)
    print(p,"ticks",s["ticksGame"],"outdoor",s["outdoorTemp"],"weather",json.dumps(s["weather"])[:120])
    print("rooms", json.dumps(s["rooms"]))
    print("meat_outdoor", json.dumps(s["meat"]["outdoor"])[:600])
    print("meat_control", json.dumps(s["meat"]["control"])[:600])
    for g in s["pawns"]:
        print(g, json.dumps({k:{"roof":v["roof"],"SC":v["SheenCoating"],"SB":v["SporesBuildup"],"SF":v["SporeFlesh"]} for k,v in s["pawns"][g].items()}))
    print("furnace", json.dumps(s["furnace"])[:400])
