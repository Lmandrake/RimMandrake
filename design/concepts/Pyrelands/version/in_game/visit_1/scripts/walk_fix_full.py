import sys, os, time, shutil
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,tk = resolve_endpoint()
SAVES=os.path.expandvars(r"%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves"); NAME="PYRELANDS_0.1.0_VISIT1_WALK_FULLLIST"
with RimBridge(h,p,tk) as rb:
    rb.call("jawa/map_fire",{"action":"extinguish","rect":"0,0,250,250"})
    lit=None
    for (x,z) in ((100,190),(140,190),(90,120),(170,140),(60,200),(200,200),(120,60)):
        r=rb.call("jawa/map_fire",{"action":"start","rect":"%d,%d,3,3"%(x,z),"fireSize":1.2})
        if (r.get("firesStarted") or 0)>=6: lit=(x+1,z+1); print("lit", x, z, r.get("firesStarted")); break
        rb.call("jawa/map_fire",{"action":"extinguish","rect":"%d,%d,3,3"%(x,z)})
    r=rb.call("jawa/review_label",{"action":"clear","tag":"pyre_visit1"})
    ruin=(rb.call("jawa/list_things",{"group":"BuildingArtificial","limit":400}).get("things") or [])
    ruin=[t for t in ruin if not t.get("faction") and t.get("def")=="Wall"][0]
    st=[(lit[0],lit[1]+4,"VISIT1 (his list, 2 game weeks walked): a fresh burn front in grass - unpause and watch it walk",(lit[0]-8,lit[1]-6,16,12)),
        (125,224,"VISIT1: creatures - ullai, furnace-beast giant, ashwallow",(117,211,18,12)),
        (ruin["x"],ruin["z"]+3,"VISIT1: a charred ruin",(ruin["x"]-6,ruin["z"]-5,12,10))]
    print("labels", rb.call("jawa/review_label",{"action":"add","tag":"pyre_visit1","ops":"\n".join("%d|%d|%s"%(x,z,s) for x,z,s,_ in st)}).get("success"))
    for f in os.listdir(r"Transient\pv1\shots"):
        if f.startswith("full_station_"): os.remove(os.path.join(r"Transient\pv1\shots",f))
    for i,(x,z,s,(rx,rz,rw,rh)) in enumerate(st):
        rb.call("jawa/clear_ui",{}); rb.call("rimworld/jump_camera_to_cell",{"x":rx+rw//2,"z":rz+rh//2})
        rb.call("rimworld/set_camera_zoom",{"rootSize":16}); time.sleep(0.4)
        pth=rb.call("rimworld/take_screenshot",{"fileName":"full_station_%d"%i}).get("path"); shutil.copy(pth, r"Transient\pv1\shots"); print("shot", i)
    before={f:os.stat(os.path.join(SAVES,f)).st_mtime for f in os.listdir(SAVES)}
    print("save", rb.call("rimworld/save_game",{"saveName":NAME}).get("success")); time.sleep(4)
    after={f:os.stat(os.path.join(SAVES,f)).st_mtime for f in os.listdir(SAVES)}
    print("new", [f for f in after if f not in before], "changed", [f for f in before if after.get(f)!=before[f]])
