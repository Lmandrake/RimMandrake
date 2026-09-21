import sys, time, json
sys.path.insert(0, r'src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint

SAVE = "FOUNDER_IMPORTER_LIVETEST_2026-09-21"
host, port, token = resolve_endpoint()

def fresh():
    return RimBridge(host, port, token)

# 1. kick the load on its own connection; a timeout here poisons only this socket
try:
    with fresh() as rb:
        rb.timeout = 600
        print("load_game ->", rb.call("rimworld/load_game", {"saveName": SAVE}).get("success"))
except Exception as e:
    print("load_game raised (expected if it outran the socket):", type(e).__name__, str(e)[:120])

# 2. poll the POST-CONDITION on new connections, never retry on the old one
ok = False
for i in range(120):
    time.sleep(10)
    try:
        with fresh() as rb:
            st = rb.call("rimbridge/get_bridge_status", {})["state"]
        if st.get("hasCurrentGame") and st.get("playable"):
            print(f"game playable after ~{(i+1)*10}s  mapCount={st.get('mapCount')}")
            ok = True
            break
    except Exception:
        continue
if not ok:
    print("NEVER BECAME PLAYABLE"); sys.exit(1)

time.sleep(45)   # the skill: drivable ~40s after the bridge says ready

# 3. the actual question: do all 6 founders carry Wimp?
with fresh() as rb:
    rb.timeout = 180
    cols = rb.call("rimworld/list_colonists", {"currentMapOnly": False})
pawns = cols.get("colonists") or cols.get("pawns") or []
print(f"\ncolonists returned: {len(pawns)}")
out = []
with fresh() as rb:
    rb.timeout = 180
    for p in pawns:
        pid = p.get("pawnId") or p.get("id")
        nm  = p.get("name") or p.get("label") or pid
        try:
            d = rb.call("jawa/pawn_detail", {"pawnId": str(pid).replace("Thing_", "")})
        except Exception as e:
            d = {"_err": str(e)[:80]}
        blob = json.dumps(d)
        out.append((nm, "Wimp" in blob, d.get("_err")))
for nm, has, err in out:
    print(f"  {'WIMP' if has else '----'}  {nm}" + (f"   [{err}]" if err else ""))
n = sum(1 for _, h, _ in out if h)
print(f"\nRESULT: {n} of {len(out)} colonists carry Wimp  (entry 4 PASSES only at 6)")
