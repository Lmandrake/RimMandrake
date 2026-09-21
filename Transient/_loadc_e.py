import sys, json, time; sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge
b=RimBridge(token="0370ddcc7f524e24a54e6cff36301136",timeout=90); b.connect()
def call(t,p={}):
    r=b.call(t,p,check=False); print(t,"->",json.dumps(r)[:220]); return r
call("jawa/set_current_map",{"mapId":4})
call("jawa/window_list_close",{"typeName":"EditWindow_Log"})
pw=b.call("jawa/list_pawns",{"limit":3},check=False)["pawns"]; p=pw[0]; x,z=int(p["x"]),int(p["z"]); print("pawn at",x,z)
call("rimworld/jump_camera_to_cell",{"x":x,"z":z,"zoom":18})
time.sleep(2)
r=call("rimworld/take_screenshot",{})
r2=call("rimworld/screenshot_cell_rect",{"x":x-20,"z":z-14,"width":40,"height":28})
