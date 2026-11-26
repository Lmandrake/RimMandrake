import sys, json, os, time, shutil
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,tk = resolve_endpoint()
SAVES=os.path.expandvars(r"%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves")
NAME="PYRELANDS_0.1.0_VISIT1_WALK"
stations=[(190,201,"VISIT1: burn scar regrown 7 days (33% green day 3, 70% day 7)",(180,180,20,20)),
          (168,30,"VISIT1: opening front scar (re-armed, lit 27)",(150,0,40,30)),
          (226,147,"VISIT1: charred ruin - floors kept, blackened (ruins check is stale)",(220,136,14,12)),
          (125,36,"VISIT1: fresh-burn bonus pad (+0.5 fertility, black rain watered)",(118,23,14,14)),
          (90,207,"VISIT1: LIVE burn front - unpause and watch it walk",(80,190,24,20)),
          (150,207,"VISIT1: creatures - ullai herd, furnace-beast giant, ashwallow",(140,195,24,14))]
with RimBridge(h,p,tk) as rb:
    rb.call("jawa/weather_set",{"unlock":True})
    for i in range(6):
        rb.call("jawa/spawn_pawn",{"kindDef":"RM_Ullai","x":142+i*2,"z":198,"faction":"none","count":1})
    rb.call("jawa/spawn_pawn",{"kindDef":"RM_FurnaceBeast","x":150,"z":203,"faction":"none","count":1})
    rb.call("jawa/spawn_pawn",{"kindDef":"RM_Ashwallow","x":158,"z":200,"faction":"none","count":1})
    rb.call("jawa/set_plants",{"ops":"RM_FE_Plant_EmberGrass:85,195,14,10","growth":1.0})
    print("fire", rb.call("jawa/map_fire",{"action":"start","rect":"88,198,3,3","fireSize":1.2}).get("firesStarted"))
    rb.call("jawa/review_label",{"action":"clear","tag":"pyre_visit1"})
    print("labels", rb.call("jawa/review_label",{"action":"add","tag":"pyre_visit1","ops":"\n".join("%d|%d|%s"%(x,z,s) for x,z,s,_ in stations)}).get("success"))
    rb.call("rimworld/set_time_speed",{"speed":0})
    os.makedirs(r"Transient\pv1\shots", exist_ok=True)
    for i,(x,z,s,(rx,rz,rw,rh)) in enumerate(stations):
        rb.call("jawa/clear_ui",{}); rb.call("rimworld/jump_camera_to_cell",{"x":rx+rw//2,"z":rz+rh//2})
        rb.call("rimworld/frame_cell_rect",{"x":rx,"z":rz,"width":rw,"height":rh,"paddingCells":3}); time.sleep(0.3)
        pth=rb.call("rimworld/take_screenshot",{"fileName":"walk_station_%d"%i}).get("path")
        shutil.copy(pth, r"Transient\pv1\shots"); print("shot", i)
    before={f:os.stat(os.path.join(SAVES,f)).st_mtime for f in os.listdir(SAVES)}
    r=rb.call("rimworld/save_game",{"saveName":NAME}); print("save", r.get("success"), r.get("path"))
    time.sleep(3)
    after={f:os.stat(os.path.join(SAVES,f)).st_mtime for f in os.listdir(SAVES)}
    print("new", [f for f in after if f not in before], "changed", [f for f in before if f in after and after[f]!=before[f]])
    print("size", os.path.getsize(os.path.join(SAVES,NAME+".rws")) if os.path.exists(os.path.join(SAVES,NAME+".rws")) else None)
