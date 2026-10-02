import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimdrive import Session
with Session(lock=None) as s:
    r = s.call("jawa/world_tile_map_generate", tile=4375, suggestedMapParent="Settlement")
    print("gen", json.dumps({k:v for k,v in r.items() if k!="operation"})[:700])
    mi = r.get("mapIndex")
    sm = s.call("jawa/map_set_current", mapId=0) if False else None
    for g in ("Plant","Pawn","Corpse"):
        pass
    li = s.call("jawa/list_pawns", limit=500); print("pawns", li.get("count"), [ (p.get("name"),p.get("faction")) for p in li.get("pawns",[])][:8])
    m = s.call("jawa/map_info"); print("map_info", json.dumps({k:v for k,v in m.items() if k!="operation"})[:500])
