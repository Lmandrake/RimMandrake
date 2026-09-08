import sys, json, re
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
with RimBridge(h,p,t) as rb:
    try:
        r = rb.call("jawa/mod_inventory", {})
        b = json.dumps(r)
        for m in re.finditer(r'\{[^{}]*[Nn]inefold[^{}]*\}', b):
            print("MODINV:", m.group(0)[:500])
    except Exception as e:
        print("mod_inventory ERR", str(e)[:200])
    try:
        r = rb.call("jawa/startup_types", {})
        b = json.dumps(r)
        hits = sorted(set(re.findall(r'[^"]*[Nn]inefold[^"]*', b)))
        print("STARTUP TYPES mentioning Ninefold:", len(hits))
        for x in hits[:12]: print("   ", x[:160])
    except Exception as e:
        print("startup_types ERR", str(e)[:200])
