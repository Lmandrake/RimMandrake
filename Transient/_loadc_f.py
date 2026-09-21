import sys, json, time; sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge
b=RimBridge(token="0370ddcc7f524e24a54e6cff36301136",timeout=90); b.connect()
def call(t,p={}):
    r=b.call(t,p,check=False); print(t,"->",json.dumps(r)[:240]); return r
mi=call("jawa/map_info",{})
call("rimworld/jump_camera_to_cell",{"x":17,"z":26,"zoom":12}); time.sleep(1)
call("rimworld/screenshot_cell_rect",{"x":2,"z":10,"width":32,"height":26})
