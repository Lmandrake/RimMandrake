import sys, json, collections
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rb
host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=180.0); S.connect()
def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
before = {p["id"] for p in call("jawa/list_pawns", limit=500)["pawns"]}
call("jawa/spawn_pawn", kindDef="RSW_DW_KotORDroidGood_KM1HMD", x=140, z=140, faction="player", count=15)
after = call("jawa/list_pawns", limit=500)["pawns"]
new = [p for p in after if p["id"] not in before and p.get("kindDef")=="RSW_DW_KotORDroidGood_KM1HMD"]
worn=0; ex=[]
for p in new:
    rec = (call("jawa/pawn_get", pawn=p["id"]).get("pawns") or [{}])[0]
    ap = rec.get("apparel") or []
    if ap: worn+=1; ex.append([x.get("defName") for x in ap])
print(f"KM1HMD second batch: {worn}/{len(new)} wearing  {json.dumps(ex[:4])}")
