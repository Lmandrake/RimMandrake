import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

SAVE = "CANONICAL_ASHKARR_START_2026-09-12"

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    print("=== load_game_ready ===")
    r = rb.call("rimworld/load_game_ready", {
        "saveName": SAVE,
        "readiness": "playable",
        "timeoutMs": 300000,
        "pollIntervalMs": 500,
    })
    print(json.dumps(r, indent=2)[:2000])

    print("=== get_game_info (post-load) ===")
    info = rb.call("rimworld/get_game_info", {})
    print(json.dumps(info, indent=2)[:2000])

    assert info.get("programState") == "Playing", f"programState was {info.get('programState')!r}, not Playing"
    assert info.get("mapCount", 0) > 0, f"mapCount was {info.get('mapCount')!r}"
    print("ASSERTIONS PASSED: programState=Playing, mapCount>0")
