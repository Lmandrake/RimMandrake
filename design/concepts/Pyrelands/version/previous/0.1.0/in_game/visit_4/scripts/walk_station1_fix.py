"""Visit 4: station 1 of the walk save showed the six ullai head-on, as thin slivers hard to recognise (looked at:
screenshots/pv4_walk_station_1.jpg). Turn them side-on (east, locked), re-capture the station, and save the walk save again
under the same name (this run's own file), stat-diffing the Saves folder. python.exe, bridge held, the walk map current."""
import sys, json, os, time, shutil
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
SAVES = os.path.expandvars(r"%USERPROFILE%\AppData\Local" + r"Low\Ludeon Studios\RimWorld by Ludeon Studios\Saves")
NAME = "PYRELANDS_0.1.0_VISIT4_WALK"
h, p, tk = resolve_endpoint()
out = {}
with RimBridge(h, p, tk) as rb:
    call = lambda tool, **kw: rb.call(tool, kw)  # noqa: E731
    pw = call("jawa/list_pawns", limit=1000).get("pawns") or []
    ids = [q["id"] for q in pw if q.get("kindDef") == "RM_Ullai" and not q.get("dead")]
    out["ullai"] = ids
    out["rotated"] = [call("jawa/set_pawn_rotation", pawnId=i, dir="east", lockRotation=True).get("success") for i in ids]
    call("rimworld/set_time_speed", speed=0)
    call("jawa/clear_ui"); call("rimworld/jump_camera_to_cell", x=30, z=46)
    call("rimworld/frame_cell_rect", x=20, z=38, width=20, height=16, paddingCells=3); time.sleep(0.4)
    pth = call("rimworld/take_screenshot", fileName="pv4_walk_station_1b").get("path")
    if pth:
        shutil.copy(pth, r"Transient\pv4\shots"); out["shot"] = pth
    before = {f: os.stat(os.path.join(SAVES, f)).st_mtime for f in os.listdir(SAVES)}
    r = call("rimworld/save_game", saveName=NAME)
    time.sleep(4)
    after = {f: os.stat(os.path.join(SAVES, f)).st_mtime for f in os.listdir(SAVES)}
    out["save"] = {"success": r.get("success"), "path": r.get("path"), "new": [f for f in after if f not in before],
                   "changed": [f for f in before if f in after and after[f] != before[f]],
                   "bytes": os.path.getsize(os.path.join(SAVES, NAME + ".rws"))}
print(json.dumps(out, indent=1))
