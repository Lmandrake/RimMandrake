import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
def fresh(): return RimBridge(host, port, token)
with fresh() as rb:
    r = rb.call("rimworld/load_game", {"saveName": "EXPERIMENTAL_shipcrewed_2026-09-09"})
    print("reload queued:", r.get("status"))
time.sleep(20)
for i in range(30):
    try:
        with fresh() as rb:
            p = rb.call("jawa/list_pawns", {"faction": "PlayerColony", "limit": 10})
            n = len(p.get("pawns", []))
            if n >= 5:
                names = [x.get("name") or x.get("label") for x in p.get("pawns", [])]
                print("crew restored:", n, names); break
            print("poll", i, "player pawns:", n)
    except Exception:
        print("poll", i, "quiet")
    time.sleep(8)
