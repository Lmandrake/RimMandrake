"""Visit 5 diagnostic (no verdict): the hediffs every player colonist carries on the freshly reloaded site (embergrass_regrow
lost a colonist to Plague mid-run: was the disease in the fixture, or caught in the run?). Exit 0 always."""
import json, os, sys
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 7))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils", "modcheck"))
from rimbridge_client import RimBridge, resolve_endpoint  # noqa: E402
import clockgate  # noqa: E402
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as raw:
    def call(name, **kw):
        return clockgate._unwrap(raw.call(name, kw))
    r = call("jawa/list_pawns", limit=1000, includeHealth=True) or {}
    for p in r.get("pawns") or []:
        if p.get("faction") == "PlayerColony" or p.get("isColonist"):
            hd = ((p.get("health") or {}).get("hediffs")) or []
            print("COLONIST", p.get("id"), p.get("x"), p.get("z"), json.dumps(
                [(h.get("def") or h.get("defName"), h.get("severity"), h.get("part")) for h in hd if isinstance(h, dict)])[:900])
    gi = call("rimworld/get_game_info") or {}
    print("TICKS", gi.get("ticksGame") or gi.get("tick"))
