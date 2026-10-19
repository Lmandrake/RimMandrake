import json,os,sys,time
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.join(HERE,"..","..","src","RimMandrake","Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
WG="RimMandrake.StarWars.WeatherSuite.WeatherGeometryUtility"
start,stride,n=int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3])
by=json.load(open(os.path.join(HERE,"c_tiles_by_biome.json")))
only=sys.argv[4].split(",") if len(sys.argv)>4 else None
land={t:b for b,v in by.items() if (b in only if only else b not in("Ocean","Lake","SeaIce","IceSheet")) for t in v}
h,p,tok=resolve_endpoint()
rows=[]
def maps(rb):
    r=rb.call("jawa/set_current_map",{"mapId":-987654})
    ms=(r.get("details") or {}).get("loadedMaps") or r.get("loadedMaps") or []
    return {m["mapId"]:m for m in ms}
with RimBridge(h,p,tok,timeout=240.0) as rb:
    cands=sorted(land)[start::stride]
    r=rb.call("jawa/tile_settleable",{"tiles":",".join(map(str,cands))})
    rr=r.get("tiles") or r.get("rows") or r.get("results") or []
    ok=cands[:n] if len(sys.argv)>5 else [int(x["tile"]) for x in rr if x.get("settleable") or x.get("valid") or x.get("ok")][:n]
    home=rb.call("jawa/map_info",{}).get("mapId")
    for tile in ok:
        before=maps(rb); t0=time.time()
        g=rb.call("jawa/world_tile_map_generate",{"tile":tile,"biome":land[tile],"sizeX":150,"sizeZ":150})
        new={k:v for k,v in maps(rb).items() if k not in before}
        if not new: rows.append({"tile":tile,"err":str(g)[:200]});continue
        mid=next(iter(new)); rb.call("jawa/set_current_map",{"mapId":mid})
        info=rb.call("jawa/map_info",{})
        term=rb.call("jawa/static_call",{"type":WG,"method":"MapInTerminatorBand","args":"current"})
        night=rb.call("jawa/static_call",{"type":WG,"method":"MapInNightsideBand","args":"current"})
        w=rb.call("jawa/weather_get",{})
        conds=sorted({c["def"] for c in w.get("conditions",[]) if c.get("affectsThisMap")})
        gy=rb.call("jawa/list_things",{"defName":"SteamGeyser","limit":500}).get("countMatched")
        pl=rb.call("jawa/list_things",{"group":"Plant","limit":1}).get("countMatched")
        rows.append({"tile":tile,"biome":land[tile],"mapBiome":info.get("mapBiome"),"terminator":term.get("result",term.get("message")),"nightside":night.get("result",night.get("message")),"conds":conds,"weather":w.get("weather",{}).get("current"),"geysers":gy,"plants":pl,"gen_s":round(time.time()-t0,1)})
        print(json.dumps(rows[-1]),flush=True)
        rb.call("jawa/set_current_map",{"mapId":home})
        idx=g.get("mapIndex",new[mid].get("index"))
        if idx is not None: rb.call("jawa/map_drop",{"mapIndex":idx,"notifyPlayer":False})
        if time.time()-t0>120: break
json.dump(rows,open(os.path.join(HERE,"c_geo_%d_%s.json"%(start,(sys.argv[4] if len(sys.argv)>4 else "land"))),"w"),indent=1)
