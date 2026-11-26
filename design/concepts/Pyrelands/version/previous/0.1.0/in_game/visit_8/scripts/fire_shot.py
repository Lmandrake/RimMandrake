import sys, time
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h, p, tk = resolve_endpoint()
with RimBridge(h, p, tk) as rb:
    c = lambda tool, **kw: rb.call(tool, kw)
    print(c("jawa/safe_advance", ticks=60)); 
    c("jawa/clear_ui"); time.sleep(2)
    print(c("rimworld/jump_camera_to_cell", x=30, z=28).get("success"))
    print(c("rimworld/screenshot_cell_rect", x=20, z=18, width=24, height=20, paddingCells=1, rootSize=14, fileName="pv8_fire_shot").get("path"))
