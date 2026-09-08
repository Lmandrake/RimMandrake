import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
with RimBridge(h,p,t) as rb:
    r = rb.call("jawa/list_pawns", {})
    pawns = r.get("pawns", [])
    print(json.dumps(pawns[0], indent=1))
    rat = [pw for pw in pawns if pw.get("def")=="Rat"]
    print("rat:", json.dumps(rat[0], indent=1) if rat else None)
