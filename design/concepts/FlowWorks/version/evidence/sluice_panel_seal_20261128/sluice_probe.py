"""Probe: a shut RM_Sluice in the middle of a 1-wide 2 m trench filled to 1.5 m; read each square and capture."""
import os, sys, time, json, shutil
REPO = sys.argv[1]; OUT = sys.argv[2]
for p in ("Utils", os.path.join("FlowWorks", "northstar")):
    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", p))
import proof_hose as PH
import validation_core as V
B = PH.PB()
def call(tool, **kw):
    try:
        return B.call(tool, **kw) or {}
    except Exception as ex:
        return {"success": False, "error": str(ex)}
ox, oz = 60, 100
rect = (ox - 3, oz - 2, 7, 9)
call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofResetRect", args="%d;%d;%d;%d" % rect)
print("sky", V.open_sky_site(B, rect).get("ok"))
call("jawa/destroy_batch", rects="%d,%d,%d,%d" % rect, categories="All")
call("jawa/set_terrain_batch", ops="Soil:%d,%d,%d,%d" % rect)
call("rimworld/pause_game")
for i in range(5):
    call("jawa/flowworks_excavation_drive", x=ox, z=oz + i, deepenLevels=4, setBodyWaterM=-1, fillInLevels=0)
r = call("jawa/spawn_batch", ops="RM_Sluice:%d,%d" % (ox, oz + 2), stuff="Steel")
print("spawn", json.dumps(r)[:300])
for a_ in ("%d,%d,1,5,1.5" % (ox, oz), "%d,%d,1,1,0" % (ox, oz + 2)):
    f = call("jawa/static_call", type="RimMandrake.FlowWorks.RM_SubmergeDraw", method="ProofFillRect", args=a_)
    print("fill", a_, f.get("result"))
call("rimworld/step_game_ticks", ticks=600)
ex = call("jawa/flowworks_excavation_rect", x=ox, z=oz, w=1, h=5, onlyNonZero=False, includeTerrain=True)
for q in ex.get("rows") or []:
    print(json.dumps(q)[:400])
call("jawa/clear_ui", all=True)
fn = "sluiceprobe_%d" % int(time.time())
r = call("rimworld/screenshot_cell_rect", x=ox - 1, z=oz, width=3, height=5, paddingCells=1, fileName=fn, suppressMessage=True)
src = str(r.get("path") or "")
for _ in range(20):
    if src and os.path.isfile(src) and os.path.getsize(src) > 0:
        time.sleep(0.8); break
    time.sleep(0.4)
if src and os.path.isfile(src):
    shutil.copyfile(src, OUT); print("shot", OUT)
