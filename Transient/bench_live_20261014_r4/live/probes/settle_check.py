# TESTENV_QUICKTEST_DIAGNOSE_SPIKES_UNINVITED / TESTENV_TOXIC_DIAGNOSE_RIVER_SITE_SNIFFLES live check:
# fresh dev quicktest -> QuietSite isolated apply -> settle(); dump the receipt (arrivals[].origin, toxic_sources_cleared).
import sys, os, json, time
U = os.path.join(os.path.dirname(__file__), "..", "src", "RimMandrake", "Utils")
sys.path.insert(0, U); sys.path.insert(0, os.path.join(U, "modcheck"))
import validation_core as V
import quiet_site as Q
B = V.Bridge()
out = {"menu": (B.call("rimworld/go_to_main_menu") or {}).get("success")}
out["start"] = (B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000) or {}).get("success")
for _ in range(120):
    if (B.call("rimworld/get_ui_state") or {}).get("programState") == "Playing": break
    time.sleep(1)
qs = Q.apply_site_profile(B, row="r4_settle_check")
out["settle"] = qs.settle(max_ticks=int(sys.argv[1]) if len(sys.argv) > 1 else 900)
rc = qs.receipt()
out["arrivals"] = rc.get("arrivals")
out["toxic"] = [c for c in rc.get("controls", []) if c.get("name") == "toxic_sources_cleared"]
out["problems"] = rc.get("problems")
json.dump({"out": out, "receipt": rc}, open(os.path.join(os.path.dirname(__file__), "settle_check.json"), "w"), indent=1, default=str)
print(json.dumps(out, default=str)[:3000])
