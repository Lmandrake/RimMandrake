import sys, json, time
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rb
h,p,t = rb.resolve_endpoint(); S = rb.RimBridge(host=h,port=p,token=t,timeout=300.0); S.connect()
def call(n, **a):
    r = S.call(n, a) or {}
    if isinstance(r, dict): r.pop("operation",None); r.pop("state",None)
    return r
call("jawa/set_current_map", mapId=4)
print("UNLOCK", call("jawa/weather_set", unlock=True))
print("WGET", json.dumps(call("jawa/weather_get"))[:300])
call("jawa/clear_ui")
call("rimworld/jump_camera_to_cell", x=143, z=201)
print("SAVE", call("rimworld/save_game", saveName="GreySeaFloor_Review_2026-10-08"))
time.sleep(4)
