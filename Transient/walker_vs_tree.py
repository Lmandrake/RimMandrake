import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rb
host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=120.0); S.connect()
def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
w = call("jawa/debug_actions", query="canal", maxMillis=8000, limit=20)
print("WALKER matched:", w.get("matched"), json.dumps(w.get("matches"), default=str)[:400])
t = call("rimworld/search_debug_actions", query="canal", limit=10)
print("HOST TREE totalMatchCount:", t.get("totalMatchCount"))
