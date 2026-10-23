"""ap.py TYPENAME CMD... -- generic request/serial/result probe on the current map"""
import sys, json, time
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
H,P,T = resolve_endpoint()
TN=sys.argv[1]
with RimBridge(H,P,T) as B:
    g=lambda f: B.call("jawa/mod_settings_field", {"typeName":TN,"action":"get","field":f}).get("value")
    for cmd in sys.argv[2:]:
        b=g("serial"); B.call("jawa/mod_settings_field", {"typeName":TN,"action":"set","field":"request","value":cmd})
        t0=time.time(); out="TIMEOUT"
        while time.time()-t0<30:
            if g("serial")!=b: out=g("result"); break
            time.sleep(0.25)
        print(cmd,"->",str(out)[:6000])
