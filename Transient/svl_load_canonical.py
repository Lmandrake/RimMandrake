import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("rimworld/load_game", {"saveName": "CANONICAL_ASHKARR_START_2026-09-12"})
    print("LOAD_CALL_RESULT", json.dumps(r)[:2000])

    for i in range(40):
        time.sleep(15)
        info = rb.call("rimworld/get_game_info", {})
        status = info.get("status")
        program = info.get("programState") or (info.get("result") or {}).get("programState")
        print(f"poll {i} status={status} info_keys={list(info.keys())}")
        print(json.dumps(info)[:1500])
        if status == "game_loaded" or program == "Playing":
            print("GAME_LOADED_CONFIRMED")
            break
