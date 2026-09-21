import sys, json; sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,T=resolve_endpoint(); b=RimBridge(token=T,timeout=120); b.connect()
b.call("jawa/set_current_map",{"mapId":4},check=False)
r=b.call("jawa/inspect_string",{"defName":"RSW_BloodropMoth","limit":3},check=False)
for t in r.get("things",[]): print(t["id"], t.get("x"),t.get("z"), t.get("inspect"))
b.call("jawa/clear_ui",{},check=False)
b.call("rimworld/jump_camera_to_cell",{"x":17,"z":26},check=False)
s=b.call("rimworld/take_screenshot",{},check=False); print("shot:", s.get("path") or s.get("filePath") or json.dumps(s)[:200])
