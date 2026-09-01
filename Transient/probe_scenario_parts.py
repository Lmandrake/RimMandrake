import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for defType, defName, fields in [
        ("WorkGiverDef", "OperateDrillTurret", ["workType"]),
        ("WorkGiverDef", "Drill", ["workType"]),
        ("XenotypeDef", "MandrakeJawa", ["genes"]),
        ("ScenarioDef", "Jawa_UtinniStart", ["scenario", "parts"]),
        ("GeneDef", "RimMandrake_Jawa_MiningDisabled", ["disabledWorkTags"]),
    ]:
        try:
            r = rb.call("jawa/get_def", {"defType": defType, "defName": defName})
        except Exception as e:
            print(f"{defType}/{defName}: CALL FAILED: {e}")
            continue
        print(f"=== {defType}/{defName} ===")
        d = r.get("def") or r
        for f in fields:
            if isinstance(d, dict) and f in d:
                print(f"  {f}: {d[f]}")
        if not isinstance(d, dict):
            print(f"  raw: {str(r)[:800]}")
        else:
            missing = [f for f in fields if f not in d]
            if missing:
                print(f"  (fields not present: {missing}; keys: {list(d.keys())[:30]})")
