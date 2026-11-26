"""Advance the current map N ticks through jawa/safe_advance (python.exe, bridge held); print the hour before and after."""
import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
n = int(sys.argv[1])
h, p, t = resolve_endpoint()
with RimBridge(h, p, t) as rb:
    print("hour before", rb.call("jawa/glow_at", {"cells": "125,125"}).get("hour"))
    left = n
    while left > 0:
        step = min(left, 5000)
        r = rb.call("jawa/safe_advance", {"ticks": step, "timeException": False})
        left -= int(r.get("executed") or step)
        if r.get("state") == "stopped":
            print("stopped", json.dumps(r)[:300]); break
    g = rb.call("jawa/glow_at", {"cells": "125,125"})
    print("hour after", g.get("hour"), "skyGlow", g.get("skyGlow"))
