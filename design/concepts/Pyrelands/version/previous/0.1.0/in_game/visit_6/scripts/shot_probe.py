"""python.exe: does rimworld/take_screenshot (the no-rect path of suite.screenshot) answer on this game? Visit 6."""
import sys, json, traceback
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h, p, tk = resolve_endpoint()
with RimBridge(h, p, tk) as rb:
    for kw in ({"fileName": "pv6_shot_probe_a", "suppressMessage": True}, {"fileName": "pv6_shot_probe_b"}):
        try:
            r = rb.call("rimworld/take_screenshot", kw)
            print(sorted(kw), "->", json.dumps({k: r.get(k) for k in ("success", "path", "message", "error")})[:300])
        except Exception as e:
            print(sorted(kw), "RAISED", type(e).__name__, str(e)[:300])
