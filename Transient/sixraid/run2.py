import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

FACTIONS = [
    "Jawa_HuttCartel",          # control - known to raid
    "Jawa_FreeDroidEnclaves",
    "Jawa_WildsteamClan",
    "Jawa_GeonosianFoundryHive",
    "Jawa_AscendantHelix",
    "Jawa_Junkers",
    "Jawa_DeepwaterCompact",
]

OUT = r"D:\Luke\dev\Rimworld\Transient\sixraid\raw_run2.json"
raw = {}

def interesting(msgs):
    out = []
    for m in msgs or []:
        t = m.get("type")
        tx = m.get("text", "")
        if t in ("Error", "Warning") or "raid" in tx.lower() or "pawn" in tx.lower() or "group" in tx.lower():
            out.append((t, tx[:400]))
    return out

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for F in FACTIONS:
        rec = {}
        rec["hostile_set"] = rb.call("jawa/set_faction_relation", {"faction": F, "kind": "Hostile"})
        rb.call("jawa/drain_log", {"max": 1000}) if "max" in (rb._param_map().get("jawa/drain_log") or set()) else rb.call("jawa/drain_log", {})
        rec["fire"] = rb.call("jawa/fire_raid", {"points": 3000, "faction": F, "dryRun": False})
        rec["log"] = rb.call("jawa/drain_log", {})
        rec["neutral_set"] = rb.call("jawa/set_faction_relation", {"faction": F, "kind": "Neutral"})
        raw[F] = rec

        h = rec["hostile_set"]
        f = rec["fire"]
        print("#####", F)
        print("  hostileToPlayer:", h.get("hostileToPlayer"), "kind:", h.get("kind"))
        print("  executed:", f.get("executed"), "success:", f.get("success"))
        print("  actual:", json.dumps(f.get("actual")))
        print("  arrived:", json.dumps(f.get("arrived")))
        print("  resolved:", json.dumps(f.get("resolved")))
        print("  factionNotes:", f.get("factionNotes"))
        print("  note:", (f.get("note") or "")[:300])
        print("  fire keys:", sorted(f.keys()))
        for t, tx in interesting(rec["log"].get("messages")):
            print("   LOG[%s] %s" % (t, tx))

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(raw, fh, indent=1, default=str)
print("RAW ->", OUT)
