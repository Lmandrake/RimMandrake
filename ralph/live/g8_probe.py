"""g8_probe.py -- read-only probes the g8_* scripts were built on (defs, settings, static_call conventions, camera)."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fwb  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
B = fwb.FW()
T = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"


def show(tag, r, n=700):
    r = dict(r or {})
    r.pop("operation", None)
    r.pop("state", None)
    print(tag, json.dumps(r, default=str)[:n], flush=True)


show("defs", B.call("jawa/get_defs", defs="DifficultyDef/Peaceful;DifficultyDef/Easy;StorytellerDef/Phoebe;ThingDef/Apparel_PackJump;"
                    "ThingDef/Apparel_ShieldBelt;ThingDef/RM_ClimbingGear;ThingDef/RM_LadderPortable;ThingDef/RM_Ladder;ThingDef/RM_LadderSteel;"
                    "PawnKindDef/Colonist;WeatherDef/Clear;TerrainDef/Soil", fields="defName,label,threatScale,allowThreats"), 3000)
for f in ("pitLookMode", "pitSinkPerLevel", "pitLipOcclusion", "pitSinkClampEnabled", "pitDepthDrawOffsetEnabled",
          "portableLadderEnabled", "portableLadderMaxLevels", "climbingGearEnabled", "ladderRaiseLowerEnabled"):
    r = B.call("jawa/mod_settings_field", typeName=T, action="get", field=f) or {}
    print("setting", f, r.get("value"), r.get("success"), r.get("message") or "")
cen = (B.call("jawa/pawn_census", faction="player") or {}).get("pawns") or []
print("player pawns", [(p.get("id"), p.get("x"), p.get("z"), p.get("isColonist")) for p in cen][:6])
pid = cen[0]["id"] if cen else None
if pid:
    for typ, meth, args in (("RimMandrake.FlowWorks.RM_Patch_PitDepthDrawOffset", "RestingSinkAt", "%s|%d,%d" % (pid, cen[0]["x"], cen[0]["z"])),
                            ("RimMandrake.FlowWorks.RM_Patch_PitDepthDrawOffset", "SinkOf", "%s|0,0,0" % pid),
                            ("RimMandrake.FlowWorks.RM_PitDepthDraw", "SinkOf", "%s|0,0,0" % pid),
                            ("RimMandrake.FlowWorks.RM_PromotionProofs", "ProofPawnSink", pid),
                            ("RimMandrake.FlowWorks.Pits.RM_SuspensionHang", "SetTreatment", "1"),
                            ("RimMandrake.FlowWorks.RM_NorthstarProofs", "ProofClimb", "pawn:" + pid),
                            ("RimMandrake.FlowWorks.Pits.RM_SuspensionProofs", "ProofReach", "%s;%d,%d" % (pid, cen[0]["x"] + 3, cen[0]["z"]))):
        show("static %s.%s(%s)" % (typ.split(".")[-1], meth, args), B.call("jawa/static_call", type=typ, method=meth, args=args), 600)
show("camera", B.call("rimworld/get_camera_state"), 900)
show("clock", B.call("jawa/time_clock"), 500)
show("saves", B.call("rimworld/list_saves"), 1500)
