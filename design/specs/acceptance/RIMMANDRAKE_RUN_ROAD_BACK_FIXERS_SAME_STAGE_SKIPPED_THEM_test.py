"""Acceptance: after a steward sends a mod down the blind_challenge -> blind_challenge road back, the Dispatch tick
(maturation_autonomy.resolve) gives each open road-back item its one fixer run BEFORE the next blind cycle launches.
rc 1 on the base de4383a05d (resolve passes a `launch` row straight through: decision launch, no fix_item); rc 0 on a fix."""
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "rimflow"))
import maturation_autonomy as A

fails = []
for dec in ("launch", "would_launch"):
    st = {"mods": {"M": {"road_back": {"caused_by": "ROUTE_X", "from": "blind_challenge"}}}}
    rows = [{"mod": "M", "stage": "blind_challenge", "decision": dec, "cycle": 2}]
    fx = {"open_items": lambda ids: [{"id": "FIX_ME", "title": "t"}] if "ROUTE_X" in ids else [],
          "designer_state": lambda m: {}, "version_locked": lambda m: True}
    rows, _ = A.resolve(ROOT, {}, st, {"M": {"version": "0.1.0"}}, rows, [], "2026-11-15T16:00:00Z", fx)
    if rows[0].get("fix_item") != "FIX_ME":
        fails.append("%s: decision %s, fix_item %s" % (dec, rows[0].get("decision"), rows[0].get("fix_item")))
# once every road-back item is closed, the cycle launches
st = {"mods": {"M": {"road_back": {"caused_by": "ROUTE_X", "from": "blind_challenge"}}}}
rows = [{"mod": "M", "stage": "blind_challenge", "decision": "launch", "cycle": 2}]
fx = {"open_items": lambda ids: [], "designer_state": lambda m: {}, "version_locked": lambda m: True}
rows, _ = A.resolve(ROOT, {}, st, {"M": {"version": "0.1.0"}}, rows, [], "2026-11-15T16:00:00Z", fx)
if rows[0].get("decision") not in ("launch", "launched", "would_launch") or st["mods"]["M"].get("road_back"):
    fails.append("closed road back: decision %s, road_back %s" % (rows[0].get("decision"), st["mods"]["M"].get("road_back")))
for f in fails:
    print("FAIL", f)
print("PASS" if not fails else "%d FAIL" % len(fails))
sys.exit(1 if fails else 0)
