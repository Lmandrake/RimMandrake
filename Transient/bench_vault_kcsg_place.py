import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

TEMPLATES = [
    ("RUT_VaultType1_MechanoidGarrison", 50, 50),
    ("RUT_VaultType2_FleshWeaponLoose", 150, 50),
    ("RUT_VaultType3_FrozenRakata", 50, 150),
]

with RimBridge(host, port, token) as rb:
    for defName, cx, cz in TEMPLATES:
        rect = f"{cx-30},{cz-30},61,61"
        res = rb.call("jawa/kcsg_place", {
            "layoutType": "structure",
            "defName": defName,
            "rect": rect,
        })
        print(defName, "place result:", json.dumps({k: res.get(k) for k in ("success","message","at","requested")}))
