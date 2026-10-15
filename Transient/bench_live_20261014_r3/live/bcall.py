# usage: python.exe r3/bcall.py <out.json|-> <tool> '<json args>' [<tool> '<json>' ...]
import sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
h, p, t = resolve_endpoint()
out = sys.argv[1]; a = sys.argv[2:]; res = []
with RimBridge(h, p, t, timeout=600.0) as rb:
    for i in range(0, len(a), 2):
        r = rb.call(a[i], json.loads(a[i+1]) if i+1 < len(a) else {})
        if isinstance(r, dict) and r.get("content"):
            try: r = json.loads(r["content"][0]["text"])
            except Exception: pass
        res.append({"tool": a[i], "args": a[i+1] if i+1 < len(a) else "{}", "result": r})
s = json.dumps(res if len(res) > 1 else res[0], indent=1, default=str)
if out != "-": open(out, "w").write(s)
print(s[:3000])
