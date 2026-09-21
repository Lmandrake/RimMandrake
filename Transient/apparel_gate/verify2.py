import sys, json, time, collections
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

hp = call("jawa/harmony_patches")
txt = json.dumps(hp)
i = txt.find("GenerateStartingApparelFor")
print("harmony report mentions GenerateStartingApparelFor:", i >= 0)
if i >= 0: print(txt[max(0,i-500):i+700])
else: print("harmony_patches raw head:", txt[:600])

KINDS = ["RSW_DW_KotORDroidBad_hk50","RSW_DW_KotORDroidBad_ADMkI",
         "RSW_DW_KotORDroidGood_KM1HMD","RSW_DW_KotORDroidGood_KX12UPD",
         "RSW_DW_OuterRim_GNKDroid"]
print("=== spawning ===")
for n,k in enumerate(KINDS):
    r = call("jawa/spawn_pawn", kindDef=k, x=60+n*8, z=60, faction="player", count=5)
    print(k, json.dumps(r)[:200])

pl = call("jawa/list_pawns", limit=500)
pawns = pl.get("pawns") if isinstance(pl, dict) else pl
if pawns is None:
    print("RAW:", json.dumps(pl)[:1500]); sys.exit(1)
print("total pawns:", len(pawns))
print("keys:", sorted(pawns[0].keys()))
agg = collections.defaultdict(lambda: [0,0,[]])
for p in pawns:
    kind = p.get("kindDef") or p.get("kind") or "?"
    if not str(kind).startswith("RSW_DW"): continue
    ap = p.get("apparel")
    a = agg[kind]; a[0]+=1
    if ap: a[1]+=1; a[2].append(ap)
print("=== RESULT ===")
for k,(n,worn,ex) in sorted(agg.items()):
    print(f"{k}: {worn}/{n} wearing   e.g. {json.dumps(ex[:1])[:400]}")
json.dump(pawns, open(r"D:\Luke\dev\Rimworld\Transient\apparel_gate\pawns.json","w"), indent=1)
