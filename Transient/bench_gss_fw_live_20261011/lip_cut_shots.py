"""FLOWWORKS_PIT_OCCUPANT_LIP_CUT_1 A1: occupied D1-D4 pits + unoccupied twins, captured with the occupant cut ON and OFF.
python.exe lip_cut_shots.py <x0>,<z0> <outdir-windows>"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.join("src", "RimMandrake", "Utils"))
import validation_core as V  # noqa: E402

x0, z0 = [int(v) for v in sys.argv[1].split(",")]
out = sys.argv[2]
os.makedirs(out, exist_ok=True)
B = V.Bridge()
ST = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
res = {"origin": [x0, z0]}
rect = (x0 - 2, z0 - 3, 20, 12)
res["killHostiles"] = B.call("jawa/artboard_stage", phase="ground", clearRect="%d,%d,%d,%d" % rect, ground="Soil",
                             killHostiles=True).get("success")
ops = []
for i, d in enumerate((1, 2, 3, 4)):
    x = x0 + i * 4
    ops.append("id=occ%d|kind=pit|x=%d|z=%d|w=1|h=1|depth=%d|fill=0" % (d, x, z0 + 4, d))
    ops.append("id=pawn%d|kind=pawn|x=%d|z=%d|def=Colonist|faction=player|rot=2" % (d, x, z0 + 4))
    ops.append("id=emp%d|kind=pit|x=%d|z=%d|w=1|h=1|depth=%d|fill=0" % (d, x, z0, d))
p = os.path.join(out, "ops.txt")
open(p, "w").write("\n".join(ops) + "\n")
st = B.call("jawa/artboard_stage", phase="subjects", opsPath=p)
res["stage"] = {"success": st.get("success"), "refused": [o for o in st.get("ops") or [] if not o.get("ok")]}
cap = dict(x=rect[0], z=rect[1], w=rect[2], h=rect[3], ppc=64)
for flag in ("true", "false"):
    res["set_" + flag] = B.call("jawa/mod_settings_field", typeName=ST, action="set", field="pitLipOccupantCutEnabled", value=flag).get("success")
    time.sleep(1.5)
    res["cap_" + flag] = B.call("jawa/artboard_capture", path=os.path.join(out, "cut_%s.png" % flag), **cap)
    B.call("rimworld/frame_cell_rect", x=rect[0], z=rect[1], width=rect[2], height=rect[3], paddingCells=1)
    time.sleep(2.0)
    res["shot_" + flag] = B.call("jawa/take_screenshot", fileName="bench_lipcut_%s" % flag)
B.call("jawa/mod_settings_field", typeName=ST, action="set", field="pitLipOccupantCutEnabled", value="true")
res["final_setting"] = B.call("jawa/mod_settings_field", typeName=ST, action="get", field="pitLipOccupantCutEnabled").get("value")
json.dump(res, open(os.path.join(out, "lip_report.json"), "w"), indent=1, default=str)
print(json.dumps(res, default=str)[:1500])
