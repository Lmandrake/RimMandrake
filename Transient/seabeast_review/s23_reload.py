import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\Transient\seabeast_review")
from sb_common import rb
from rimbridge_client import RimBridge, resolve_endpoint

try:
    with rb() as b:
        r = b.call("rimworld/load_game", {"saveName": "SEABEAST_FAMILIES_20260903"})
        print("LOAD:", json.dumps(r)[:300])
except Exception as e:
    print("load raised (expected on timeout):", type(e).__name__, str(e)[:120])

for i in range(40):
    time.sleep(10)
    try:
        with rb() as b:
            lp = b.call("jawa/list_pawns", {"limit": 5})
        s = json.dumps(lp)
        if "No current map" in s:
            print(i, "no map"); continue
        print(i, "READY", s[:120]); break
    except Exception as e:
        print(i, "poll", type(e).__name__, str(e)[:100])
