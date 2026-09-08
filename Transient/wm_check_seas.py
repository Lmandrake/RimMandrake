import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
with RimBridge(h,p,t) as rb:
    for n in ["RUT_TheScald","RUT_GreySea","RUT_TwilightSea","RUT_PropaneLake","RUT_NightsideIce"]:
        r = rb.call("jawa/get_defs", {"defs": "BiomeDef/"+n})
        ok = r.get("foundCount",0)
        d = (r.get("defs") or [{}])[0]
        print(f"  {n:18s} found={ok}  label={d.get('label')}")
