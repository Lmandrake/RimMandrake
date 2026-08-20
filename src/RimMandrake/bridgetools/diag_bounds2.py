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
print("probing which coordinate trips 'out of bounds':")
for a,b in (("10,10","20,10"),("30,30","40,30"),("50,50","60,50"),("60,60","70,60"),
            ("59,59","69,59"),("60,10","70,10"),("10,60","20,60"),("100,100","110,100")):
    r = call("jawa/connect_cells", **{"from":a,"to":b})
    m = (r.get("message") or "")[:60]
    print("   %-9s -> %-9s ok=%-5s %s" % (a, b, r.get("success"), m))
