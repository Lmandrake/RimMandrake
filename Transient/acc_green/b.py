"""bridge call helper: python.exe Transient/acc_green/b.py <tool> key=val ... (values JSON if parseable)"""
import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rb
host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=300.0); S.connect()
def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
if __name__ == "__main__":
    kw = {}
    for a in sys.argv[2:]:
        k, v = a.split("=", 1)
        try: v = json.loads(v)
        except Exception: pass
        kw[k] = v
    print(json.dumps(call(sys.argv[1], **kw))[:2000000])
