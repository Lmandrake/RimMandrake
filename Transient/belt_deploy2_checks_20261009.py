"""Belt deploy sitting 2 (2026-10-09) live checks on the owner's full list. Run under python.exe from the repo root.
Phase arg: menu | map | smoke_report"""
import sys, json, time
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S

def show(tag, r):
    print(tag, "|", json.dumps(r, default=str)[:1500]); sys.stdout.flush()

phase = sys.argv[1] if len(sys.argv) > 1 else "map"
SMOKE = "RimMandrake.RimDefDump.RM_SettingsOpenSmoke"
W = "RimMandrake.Webwork.RM_WebworkProof"

if phase == "menu":
    show("SMOKE_START", S.call("jawa/static_call", type=SMOKE, method="Run", args="reset=1"))
elif phase == "smoke_report":
    show("SMOKE_REPORT", S.call("jawa/static_call", type=SMOKE, method="Run", args="report=1"))
    show("MODINV", S.call("jawa/mod_inventory"))
elif phase == "startmap":
    show("START", S.call("rimworld/start_debug_game_ready"))
elif phase == "map":
    show("CARAVAN", S.call("jawa/get_defs", defs="TraderKindDef/RUT_Caravan_Junkers", fields="defName"))
    show("CORE", S.call("jawa/get_defs", defs="ThingDef/RM_HalfExtractedCore", fields="tradeability"))
    show("GOO", S.call("jawa/get_defs", defs="ThingDef/AA_GreenGoo", fields="race"))
    show("SALV", S.call("jawa/get_defs", defs="ThingDef/RUT_FoundrySalvageCache", fields="thingClass"))
    for a in ["true;RM_Webwork_Anchor;34", "true;RM_Webwork_Web;0", "false;RM_Webwork_Anchor;0"]:
        show("WEB " + a, S.call("jawa/static_call", type=W, method="ProofHarvest", args=a))
