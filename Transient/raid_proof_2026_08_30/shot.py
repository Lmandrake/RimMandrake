import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rbc
host, port, token = rbc.resolve_endpoint()
S = rbc.RimBridge(host=host, port=port, token=token, timeout=300.0); S.connect()
def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
print(json.dumps(call("jawa/clear_ui"))[:200])
p = call("jawa/list_pawns", faction="Jawa_GeonosianFoundryHive", limit=5)
rows = p.get("pawns", [])
if rows:
    pos = rows[0].get("position") or {}
    print("jump:", json.dumps(call("rimworld/jump_camera_to_cell", x=pos.get("x",100), z=pos.get("z",100)))[:200])
print(json.dumps(call("rimworld/take_screenshot"))[:400])
