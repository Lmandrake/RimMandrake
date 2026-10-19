"""Load an _AREAFIX site save via test_site_saves.load_site(name=...). Usage: python.exe load_areafix.py <site> <out.json>"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
UT = os.path.join(ROOT, "src", "RimMandrake", "Utils")
sys.path[:0] = [os.path.join(UT, "modcheck"), UT]
import test_site_saves as T
from rimbridge_client import RimBridge, resolve_endpoint
site, out = sys.argv[1], sys.argv[2]
name = sys.argv[3] if len(sys.argv) > 3 else (T.SITES[site].get("save") or "") + "_AREAFIX2"
h, p, t = resolve_endpoint()
with RimBridge(h, p, t, timeout=300.0) as rb:
    call = lambda tool, **kw: rb.call(tool, kw)  # noqa: E731
    res = T.load_site(call, site, name=name)
with open(out, "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1, sort_keys=True, default=str)
print("load", name, "verified=%s" % res.get("verified"), "load_s=%s" % res.get("load_s"), res.get("problems"))
