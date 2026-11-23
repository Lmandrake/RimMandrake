"""python.exe: drive modcheck suite.TestContext._fit_rect_shot on the live game, exceptions shown. Visit 6."""
import sys, json, traceback
sys.path.insert(0, r"src\RimMandrake\Utils"); sys.path.insert(0, r"src\RimMandrake\Utils\modcheck")
from rimbridge_client import RimBridge, resolve_endpoint
import suite, play_zoom
h, p, tk = resolve_endpoint()
with RimBridge(h, p, tk) as rb:
    class S(object):
        def call(self, tool, **kw):
            r = rb.call(tool, kw)
            if "screenshot" in tool:
                print("  ", tool, {k: kw.get(k) for k in ("x", "z", "width", "height", "rootSize")},
                      "->", json.dumps({k: r.get(k) for k in ("success", "message", "appliedRootSize", "fullyVisible", "clipRect", "paddedRect")})[:400])
            return r
    t = suite.TestContext(S(), anchor=(125, 125))
    try:
        print("RESULT", t.screenshot(name="pv6_fitprobe", rect=(0, 0, 250, 250)))
    except Exception:
        traceback.print_exc()
    print("cal", t._zoom.k, t._zoom.tall, t._zoom.wide)
