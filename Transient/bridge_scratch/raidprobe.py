import sys, json, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
rb = RimBridge(host, port, token, timeout=600.0); rb.connect()
def call(t, **p):
    r = rb.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
def show(tag, r, keys=None):
    d = {k: r.get(k) for k in keys} if keys else r
    print(tag, json.dumps(d)[:1400]); sys.stdout.flush()

for n in ("jawa/fire_raid","jawa/raid_preview","jawa/set_faction_relation","jawa/drain_log","jawa/list_pawns"):
    d = next((x for x in rb.list_tools() if x["name"] == n), None)
    print("###", n, json.dumps(d.get("inputSchema"))[:700] if d else "MISSING")
