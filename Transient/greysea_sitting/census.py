import sys, json, collections
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rb
h,p,t = rb.resolve_endpoint(); S = rb.RimBridge(host=h,port=p,token=t,timeout=300.0); S.connect()
def call(n, **a):
    r = S.call(n, a) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
print("CUR", json.dumps(call("jawa/set_current_map", mapId=int(sys.argv[1])))[:300])
P = call("jawa/list_pawns", limit=2000)
pw = P.get("pawns") or []
print("PAWNKEYS", list(pw[0].keys()) if pw else P)
c = collections.Counter((x.get("kindDef") or x.get("def") or x.get("kind"), x.get("faction"), x.get("hostile")) for x in pw)
for k,v in c.most_common(): print("PAWN", v, k)
for grp in ("Plant","BuildingArtificial","BuildingNatural"):
    T = call("jawa/list_things", group=grp, limit=5000)
    th = T.get("things") or []
    cc = collections.Counter(x.get("defName") or x.get("def") for x in th)
    print("GROUP", grp, len(th), T.get("total"), T.get("truncated"), cc.most_common(40))
