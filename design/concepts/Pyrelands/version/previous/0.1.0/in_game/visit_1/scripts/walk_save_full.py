import sys, os, json, time, shutil
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,tk = resolve_endpoint()
SAVES=os.path.expandvars(r"%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves"); NAME="PYRELANDS_0.1.0_VISIT1_WALK_FULLLIST"
BL="RimMandrake.Pyrelands.MapComponent_BurnLine"
with RimBridge(h,p,tk) as rb:
    fx=fz=None
    for (x,z) in ((60,160),(190,160),(60,40),(200,60),(100,200),(160,100)):
        r=rb.call("jawa/map_fire",{"action":"start","rect":"%d,%d,3,3"%(x,z),"fireSize":1.2})
        if (r.get("firesStarted") or 0)>0: fx,fz=x+1,z+1; print("fire lit at", x, z, r.get("firesStarted")); break
    fruit=rb.call("jawa/list_things",{"defName":"RM_FE_Plant_ScorchFruit","limit":10}).get("things") or []
    ruins=[t for t in (rb.call("jawa/list_things",{"group":"BuildingArtificial","limit":400}).get("things") or []) if not t.get("faction") and t.get("def") in ("Wall","Column","Door")]
    print("fruit", [(t["x"],t["z"]) for t in fruit][:5], "ruins", len(ruins))
    ca=(125,215)
    for i in range(6): rb.call("jawa/spawn_pawn",{"kindDef":"RM_Ullai","x":ca[0]-6+i*2,"z":ca[1],"faction":"none","count":1})
    rb.call("jawa/spawn_pawn",{"kindDef":"RM_FurnaceBeast","x":ca[0],"z":ca[1]+5,"faction":"none","count":1})
    rb.call("jawa/spawn_pawn",{"kindDef":"RM_Ashwallow","x":ca[0]+8,"z":ca[1]+3,"faction":"none","count":1})
    st=[] if fx is None else [(fx,fz+6,"VISIT1 (his list, 2 game weeks walked): a fresh burn front - unpause and watch it walk",(fx-15,fz-10,30,22))]
    if fruit: st.append((fruit[0]["x"],fruit[0]["z"]+2,"VISIT1: scorch-fruit born of the second week's fire",(fruit[0]["x"]-8,fruit[0]["z"]-6,16,12)))
    st.append((ca[0],ca[1]+9,"VISIT1: creatures - ullai, furnace-beast giant, ashwallow",(ca[0]-10,ca[1]-4,22,14)))
    if ruins: st.append((ruins[0]["x"],ruins[0]["z"]+3,"VISIT1: a charred ruin",(ruins[0]["x"]-7,ruins[0]["z"]-6,14,12)))
    rb.call("jawa/review_label",{"action":"clear","tag":"pyre_visit1"})
    print("labels", rb.call("jawa/review_label",{"action":"add","tag":"pyre_visit1","ops":"\n".join("%d|%d|%s"%(x,z,s) for x,z,s,_ in st)}).get("success"))
    rb.call("rimworld/set_time_speed",{"speed":0})
    for i,(x,z,s,(rx,rz,rw,rh)) in enumerate(st):
        rb.call("jawa/clear_ui",{}); rb.call("rimworld/jump_camera_to_cell",{"x":rx+rw//2,"z":rz+rh//2})
        rb.call("rimworld/frame_cell_rect",{"x":rx,"z":rz,"width":rw,"height":rh,"paddingCells":3}); time.sleep(0.3)
        pth=rb.call("rimworld/take_screenshot",{"fileName":"full_station_%d"%i}).get("path"); shutil.copy(pth, r"Transient\pv1\shots"); print("shot", i, s)
    before={f:os.stat(os.path.join(SAVES,f)).st_mtime for f in os.listdir(SAVES)}
    print("save", rb.call("rimworld/save_game",{"saveName":NAME}).get("success")); time.sleep(4)
    after={f:os.stat(os.path.join(SAVES,f)).st_mtime for f in os.listdir(SAVES)}
    print("new", [f for f in after if f not in before], "changed", [f for f in before if after.get(f)!=before[f]])
