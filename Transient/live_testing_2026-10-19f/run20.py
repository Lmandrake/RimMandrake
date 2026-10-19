import json, os, sys, time
sys.path.insert(0, os.path.join("src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
h, p, t = resolve_endpoint(); out = {}
with RimBridge(h, p, t, timeout=120.0) as rb:
    for args in ({"speed": "Superfast"}, {"speed": "Fast"}):
        try: out["set"] = rb.call("rimworld/set_time_speed", args); out["unpause"] = rb.call("rimworld/pause_game", {"pause": False}); break
        except Exception as e: out["set_err"] = str(e)[:300]
    time.sleep(30)
    try: out["pause"] = rb.call("rimworld/pause_game", {"pause": True})
    except Exception as e: out["pause_err"] = str(e)[:300]
    out["info"] = rb.call("rimworld/get_game_info", {})
json.dump(out, open(sys.argv[1], "w"), indent=1, default=str)
print({k: str(v)[:160] for k, v in out.items()})
