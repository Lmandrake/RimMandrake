# -*- coding: utf-8 -*-
import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
for x in b.list_tools():
    if x.get("name") in ("rimworld/jump_camera_to_pawn","rimworld/get_ui_state","rimworld/frame_pawns"):
        print("###", x["name"], "::", json.dumps(x.get("inputSchema") or {})[:600]); print()
u=b.call('rimworld/get_ui_state',{}); u.pop('operation',None)
print("=== get_ui_state TOP-LEVEL keys ===")
print(sorted(u.keys()))
for k in ('currentMap','maps','mapCount','programState','hasCurrentGame'):
    print("   %-14s = %r"%(k, u.get(k,'<ABSENT>')))
