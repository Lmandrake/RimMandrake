# -*- coding: utf-8 -*-
import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
for x in b.list_tools():
    if x.get("name") in ("rimworld/jump_camera_to_pawn","rimworld/get_ui_state","rimworld/frame_pawns"):
        print("###", x["name"]); print(json.dumps(x.get("inputSchema") or {})[:800]); print()
u=b.call('rimworld/get_ui_state',{}); u.pop('operation',None)
print("=== FULL get_ui_state keys ===")
print(json.dumps({k:v for k,v in u.items()}, indent=0)[:1400])
