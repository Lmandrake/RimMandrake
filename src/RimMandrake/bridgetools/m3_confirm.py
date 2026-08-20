import sys, json
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rb
host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=300.0); S.connect()
def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
p = call("jawa/prefab_place", name="hut2", pos="200,160", faction="PlayerColony", readBack=40)
print("success:", p.get("success"), " spawnedCount:", p.get("spawnedCount"), " rot:", p.get("rot"))
if not p.get("success"): print("message:", p.get("message"))
from collections import Counter
c = Counter(t["def"] for t in (p.get("things") or []))
print("placed contents:", dict(c))
mins = [(t["x"], t["z"]) for t in (p.get("things") or [])]
if mins: print("min corner:", min(x for x,_ in mins), min(z for _,z in mins), " (asked pos 200,160, size 9x7)")
