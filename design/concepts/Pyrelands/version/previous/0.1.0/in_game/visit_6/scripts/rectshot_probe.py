"""python.exe: rimworld/screenshot_cell_rect as suite.screenshot calls it (rect, no ppc), on a 48 and a 250 square. Visit 6."""
import sys, json, time
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h, p, tk = resolve_endpoint()
with RimBridge(h, p, tk) as rb:
    for (x, z, w, hh) in ((100, 100, 48, 48), (0, 0, 250, 250)):
        try:
            rb.call("jawa/clear_ui", {})
            t0 = time.time()
            r = rb.call("rimworld/screenshot_cell_rect", {"x": x, "z": z, "width": w, "height": hh, "paddingCells": 1,
                                                          "fileName": "pv6_rectshot_%d" % w})
            print(w, "->", round(time.time() - t0, 1), "s", json.dumps({k: r.get(k) for k in ("success", "path", "message", "error")})[:300])
        except Exception as e:
            print(w, "RAISED", type(e).__name__, str(e)[:400])
