"""treat.py name sink occl ox oz : set pitSinkPerLevel / pitLipOcclusion, shoot the bars1 depth ladder at (ox, oz)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fwb
from story1 import shot
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
B = fwb.FW()
name, sink, occl, ox, oz = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
T = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
for f, v in (("pitSinkPerLevel", sink), ("pitLipOcclusion", occl)):
    r = B.call("jawa/mod_settings_field", typeName=T, action="set", field=f, value=v) or {}
    print(f, r.get("valueBefore"), "->", r.get("valueAfter"))
B.call("rimworld/play_for", durationMs=400, speed="Normal")
shot(B, "tr_%s_a" % name, rect=(ox - 1, oz - 2, 12, 6))
shot(B, "tr_%s_b" % name, rect=(ox + 11, oz - 2, 11, 6))
