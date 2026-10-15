import sys, json, os
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
h, p, t = resolve_endpoint()
with RimBridge(h, p, t) as rb:
    ev = rb.call("jawa/vitals", {"action": "events"})
    hp = rb.call("jawa/list_pawns", {"faction": "hostile", "limit": 200})
    gi = rb.call("rimworld/get_game_info", {})
out = {"vitals_events": ev, "hostile_pawns": [x for x in (hp.get("pawns") or []) if not x.get("dead")], "game": {k: gi.get(k) for k in ("ticksGame", "programState")} if isinstance(gi, dict) else gi}
json.dump(out, open(sys.argv[1], "w"), indent=1)
evs = ev.get("events") or []
print("events", len(evs), "kinds", sorted({str(e.get("kind") or e.get("type")) for e in evs}), "hostiles", len(out["hostile_pawns"]), "success", ev.get("success"))
