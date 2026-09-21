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

print("=== start debug game ===")
r = call("rimworld/start_debug_game_ready", readiness="playable", timeoutMs=300000, pauseIfNeeded=True)
print(json.dumps(r)[:400])

print("=== harmony patches on GenerateStartingApparelFor ===")
hp = call("jawa/harmony_patches")
txt = json.dumps(hp)
for frag in ("GenerateStartingApparelFor",):
    i = txt.find(frag)
    print(frag, "found" if i >= 0 else "NOT FOUND")
    if i >= 0:
        print(txt[max(0,i-400):i+600])

KINDS = ["RSW_DW_KotORDroidBad_hk50","RSW_DW_KotORDroidBad_ADMkI",
         "RSW_DW_KotORDroidGood_KM1HMD","RSW_DW_KotORDroidGood_KX12UPD",
         "RSW_DW_OuterRim_GNKDroid"]

print("=== spawning ===")
for k in KINDS:
    r = call("jawa/spawn_pawn", kindDef=k, x=100, z=100, faction="player", count=5)
    print(k, json.dumps(r)[:300])
    time.sleep(0.5)

print("=== reading back ===")
pl = call("jawa/list_pawns", limit=500)
pawns = pl.get("pawns") if isinstance(pl, dict) else pl
if pawns is None:
    print("RAW:", json.dumps(pl)[:2000]); sys.exit(1)
print("total pawns:", len(pawns))
print("sample keys:", sorted(pawns[0].keys()) if pawns else None)
agg = collections.defaultdict(lambda: [0,0,[]])
for p in pawns:
    kind = p.get("kindDef") or p.get("kind") or "?"
    if not str(kind).startswith("RSW_DW"): continue
    ap = p.get("apparel")
    a = agg[kind]
    a[0] += 1
    if ap: a[1] += 1; a[2].append(ap)
for k, (n, worn, ex) in sorted(agg.items()):
    print(f"{k}: {worn}/{n} wearing apparel   e.g. {json.dumps(ex[:1])[:300]}")
