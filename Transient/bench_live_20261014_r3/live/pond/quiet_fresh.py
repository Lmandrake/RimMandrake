# fresh quicktest map, then quiet it: destroy non-colonists, vanish threat structures, clear incidents, Clear weather
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
import time
h, p, t = resolve_endpoint(); out = {}
def c(rb, tool, **a):
    r = rb.call(tool, a)
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
with RimBridge(h, p, t, timeout=600.0) as rb:
    out["menu"] = c(rb, "rimworld/go_to_main_menu").get("success")
    out["start"] = c(rb, "rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000).get("success")
    for _ in range(120):
        if (c(rb, "rimworld/get_ui_state") or {}).get("programState") == "Playing": break
        time.sleep(1)
    out["destroy"] = c(rb, "jawa/destroy_bulk", filter="nonColonists", dryRun=False).get("matchedCount")
    q = c(rb, "jawa/quiet_site", action="apply", clearThreats=True); out["threats"] = len(q.get("threats") or [])
    out["incidents"] = c(rb, "jawa/incident_queue_clear").get("success")
    out["weather"] = c(rb, "jawa/weather_set", weather="Clear", lockWeather=True).get("success")
    out["status_after"] = len((c(rb, "jawa/quiet_site", action="status").get("threats") or []))
print(json.dumps(out))
