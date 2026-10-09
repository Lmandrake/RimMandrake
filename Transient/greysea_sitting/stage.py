"""Stage Grey Sea floor map 4 for the owner's walk. python.exe, repo root."""
import sys, json, re, time, collections, random
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rb
h,p,t = rb.resolve_endpoint(); S = rb.RimBridge(host=h,port=p,token=t,timeout=300.0); S.connect()
def call(n, **a):
    r = S.call(n, a) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    if isinstance(r, dict): r.pop("operation",None); r.pop("state",None)
    return r
MAP=4
print("CUR", call("jawa/set_current_map", mapId=MAP).get("biome"))
call("rimworld/set_time_speed", speed=0) if False else None
# feature window: densest pillar/crystal/chimney area
r = call("jawa/list_things", defName="RM_SaltPillar,RM_SaltChimney,RM_GreatSaltCrystal_White,RM_GreatSaltCrystal_Pink,RM_GreatSaltCrystal_Amber,RM_GreatSaltCrystal_Violet,RM_SaltDome", limit=3000)
pts = [(th.get("x"), th.get("z"), th.get("def")) for th in r.get("things") or []]
print("feature sample keys", list((r.get("things") or [{}])[0].keys()))
W,H = 44,26
best=None
for x0 in range(5, 250-W-5, 4):
    for z0 in range(5, 250-H-5, 4):
        inn=[d for (x,z,d) in pts if x0<=x<x0+W and z0<=z<z0+H]
        kinds=len(set(d for d in inn))
        sc = kinds*10 + len(inn)
        if not best or sc>best[0]: best=(sc,x0,z0,collections.Counter(inn))
_,X0,Z0,cnt = best
print("WINDOW", X0,Z0,W,H, dict(cnt))
# open cells in window
cl = []
for zz in (Z0, Z0+H//2):
    cl += call("rimworld/get_cells_info", x=X0, z=zz, width=W, height=H//2).get("cells") or []
openc = [(c["x"],c["z"]) for c in cl if c.get("walkable") and not c.get("thingCount")]
terr = collections.Counter(c.get("terrain") for c in cl)
print("TERRAIN in window", dict(terr), "open", len(openc))
# colonists at window edge so the map is home
cx, cz = openc[len(openc)//2]
sp = call("jawa/spawn_pawn", kindDef="Colonist", x=X0+2, z=Z0+2, count=3, faction="PlayerColony")
print("COLONISTS", sp.get("success"), sp.get("message"))
# hostiles
for _ in range(6):
    hs=[q for q in call("jawa/list_pawns", limit=500).get("pawns",[]) if q.get("hostile")]
    if not hs: break
    for q in hs: call("jawa/damage", thingId=q["id"], damageDef="Bomb", amount=9999)
print("HOSTILES_LEFT", len([q for q in call("jawa/list_pawns", limit=500).get("pawns",[]) if q.get("hostile")]))
# STAGED flora (the Plants genstep grows none - see sitting doc): 4 of each ruled plant in the window
b = open(r"src\RimMandrake\TerminalBiomes\Defs\BiomeDefs\RM_GreySea.xml", encoding="utf-8").read()
m = re.search(r"<wildPlants>(.*?)</wildPlants>", b, re.S); plants = re.findall(r"<(\w+)[^>]*>[\d.]+</\1>", m.group(1))
random.seed(7); random.shuffle(openc)
used=set(); placed=collections.Counter(); fails=collections.Counter()
i=0
for pl in plants:
    for k in range(4):
        while i < len(openc) and openc[i] in used: i+=1
        if i>=len(openc): break
        x,z = openc[i]; used.add((x,z)); i+=1
        rr = call("rimworld/spawn_thing", defName=pl, x=x, z=z)
        if rr.get("success"): placed[pl]+=1
        else: fails[pl]+=1; 
        if not rr.get("success") and fails[pl]==1: print("  spawnfail", pl, rr.get("message") or rr.get("error"))
print("FLORA placed", dict(placed), "fails", dict(fails))
json.dump({"window":[X0,Z0,W,H]}, open(r"Transient\greysea_sitting\window.json","w"))
