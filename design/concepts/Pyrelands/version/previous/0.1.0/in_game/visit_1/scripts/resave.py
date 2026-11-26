import sys, os, time
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,tk = resolve_endpoint()
SAVES=os.path.expandvars(r"%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves"); NAME="PYRELANDS_0.1.0_VISIT1_WALK"
stations=[(190,201,"VISIT1: burn scar regrown 7 days (33% green day 3, 70% day 7)"),
          (168,30,"VISIT1: opening front scar, laid ~11 days ago and grown back"),
          (226,147,"VISIT1: charred ruin - floors kept, blackened"),
          (125,36,"VISIT1: fresh-burn bonus pad (+0.5 fertility, black rain watered)"),
          (90,207,"VISIT1: LIVE burn front - unpause and watch it walk"),
          (150,207,"VISIT1: creatures - ullai herd (north view reads thin), furnace-beast giant, ashwallow")]
with RimBridge(h,p,tk) as rb:
    rb.call("jawa/review_label",{"action":"clear","tag":"pyre_visit1"})
    print(rb.call("jawa/review_label",{"action":"add","tag":"pyre_visit1","ops":"\n".join("%d|%d|%s"%s for s in stations)}).get("success"))
    rb.call("jawa/clear_ui",{}); rb.call("rimworld/jump_camera_to_cell",{"x":150,"z":200})
    before={f:os.stat(os.path.join(SAVES,f)).st_mtime for f in os.listdir(SAVES)}
    print(rb.call("rimworld/save_game",{"saveName":NAME}).get("success")); time.sleep(3)
    after={f:os.stat(os.path.join(SAVES,f)).st_mtime for f in os.listdir(SAVES)}
    print("new", [f for f in after if f not in before], "changed", [f for f in before if after.get(f)!=before[f]])
