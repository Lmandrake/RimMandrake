import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
def fresh(): return RimBridge(host, port, token)
with fresh() as rb:
    # census the companion: is the new build live?
    r = rb._request("tools/list", {})
    tools = [t["name"] for t in r.get("tools", [])]
    print("jawa tools:", sum(1 for t in tools if t.startswith("jawa/")), "| rename tool present:", "jawa/world_landmark_rename" in tools)
    l = rb.call("rimworld/load_game", {"saveName": "EXPERIMENTAL_shipcrewed_2026-09-09"})
    print("load:", l.get("status"))
time.sleep(20)
for i in range(30):
    try:
        with fresh() as rb:
            gi = rb.call("rimworld/get_game_info", {})
            t = gi.get("ticksGame")
            if t and t > 100000:
                print("crewed save LOADED, ticks", t); break
            print("poll", i, t)
    except Exception:
        print("poll", i, "quiet")
    time.sleep(10)
