import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
# ART_OVERRIDE_FOLD_ALL_1 F3: close-up per specimen (camera root 11 = closest), then restore the camera.
ids = [i for i in sys.argv[1].split(",") if i]
old = S.call("rimworld/get_camera_state").get("rootSize")
S.call("rimworld/set_camera_zoom", rootSize=11)
for pid in ids:
    p = (S.call("jawa/pawn_get", pawn=pid).get("pawns") or [{}])[0].get("position") or {}
    if not p: print("NOPOS", pid); continue
    r = S.call("rimworld/screenshot_cell_rect", x=p["x"] - 2, z=p["z"] - 2, width=5, height=5, paddingCells=0,
               fileName="bridge7_f3_" + pid)
    print("SHOT", pid, p, r.get("path"))
S.call("rimworld/set_camera_zoom", rootSize=old or 24)
