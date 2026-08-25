import sys, json
sys.path.insert(0,r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
rb = RimBridge(h,p,t); rb.connect()
def brief(r):
    return {k:v for k,v in r.items() if k not in ("operation",)}
print("settleable 15509:", json.dumps(brief(rb.call("jawa/tile_settleable",{"tiles":"15509"})))[:300])
moves = [("246",21547,None,"The Free Charge -> Rust Cathedral centre"),
         ("140",21576,None,"The Godmouth -> Scarlands 16.55N 11.03E"),
         ("247",5072,None,"Second Speaker -> Mechanoid Intrusion"),
         ("192",15509,"Sufferband","Knife Canyon -> Fanground, renamed")]
for ids,tile,name,why in moves:
    a={"ids":ids,"tile":tile}
    if name: a["name"]=name
    r=rb.call("jawa/world_objects_set",a)
    print(why,"->",json.dumps(brief(r))[:300])
r=rb.call("jawa/world_objects_add",{"def":"Settlement","tile":1174,"faction":"Jawa_WildsteamClan","name":"Distant Scream"})
print("add Distant Scream ->", json.dumps(brief(r))[:400])
print("commit ->", json.dumps(brief(rb.call("jawa/world_commit",{})))[:300])
