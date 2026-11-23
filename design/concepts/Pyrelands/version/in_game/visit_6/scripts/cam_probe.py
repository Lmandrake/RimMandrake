"""python.exe: the camera state, then screenshot_cell_rect of a 250 square at rootSize 60 and 120. Visit 6."""
import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h, p, tk = resolve_endpoint()
with RimBridge(h, p, tk) as rb:
    c = rb.call("rimworld/get_camera_state", {})
    print(json.dumps({k: v for k, v in c.items() if k not in ("operation", "state")})[:700])
    for rs in (60, 120):
        r = rb.call("rimworld/screenshot_cell_rect", {"x": 0, "z": 0, "width": 250, "height": 250, "paddingCells": 1,
                                                      "rootSize": rs, "fileName": "pv6_rectshot_rs%d" % rs})
        print(rs, json.dumps({k: r.get(k) for k in ("success", "path", "message")})[:300])
