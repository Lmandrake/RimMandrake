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

hp = call("jawa/harmony_patches", typeName="PawnApparelGenerator")
print("HARMONY:", json.dumps(hp)[:1500])
print()
pawns = json.load(open(r"D:\Luke\dev\Rimworld\Transient\apparel_gate\pawns.json"))
agg = collections.defaultdict(lambda: [0,0,[]])
for p in pawns:
    k = p.get("kindDef","")
    if not k.startswith("RSW_DW"): continue
    d = call("jawa/pawn_get", pawn=p["id"])
    if isinstance(d, dict) and "pawn" in d: d = d["pawn"]
    ap = d.get("apparel") if isinstance(d, dict) else None
    if ap is None and isinstance(d, dict) and "apparel" not in d:
        print("NO apparel key in pawn_get; keys=", sorted(d.keys())); break
    a = agg[k]; a[0]+=1
    if ap: a[1]+=1; a[2].append(ap)
print("=== RESULT (pawn_get) ===")
for k,(n,worn,ex) in sorted(agg.items()):
    print(f"{k}: {worn}/{n} wearing   e.g. {json.dumps(ex[:1])[:400]}")
