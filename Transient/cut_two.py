import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
CUT = ("BreadMoAM_Turret_LargeShotgun", "VQE_AncientSpacerAutocannon")
DESTROY = "Actions" + chr(92) + "T: Destroy"
with RimBridge(host, port, token) as rb:
    r = rb.call("rimworld/save_game", {"saveName": "BENCH_patient_probe"})
    print("saved:", r.get("success"))
