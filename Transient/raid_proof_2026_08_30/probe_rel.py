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
print("SET:", json.dumps(call("jawa/set_faction_relation", faction="Jawa_HuttCartel", kind="Hostile", goodwill=-100))[:900])
print("LIST:", json.dumps(call("jawa/list_factions", defName="Jawa_HuttCartel"))[:900])
