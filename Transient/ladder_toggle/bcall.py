"""bcall.py TOOL '{json args}' - one bridge call, prints JSON result (scratch helper for FLOWWORKS_LADDER_RAISE_LOWER_1)."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src", "RimMandrake", "Utils"))
import rimbridge_client as rb
h, p, t = rb.resolve_endpoint()
s = rb.RimBridge(host=h, port=p, token=t, timeout=600.0); s.connect()
r = s.call(sys.argv[1], json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}) or {}
if isinstance(r, dict) and r.get("content"):
    try: r = json.loads(r["content"][0]["text"])
    except Exception: pass
print(json.dumps(r)[:int(os.environ.get("BCALL_MAX", "3000"))])
