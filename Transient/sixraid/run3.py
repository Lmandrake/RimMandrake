# -*- coding: utf-8 -*-
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

FACTIONS = [
    "Jawa_HuttCartel",
    "Jawa_FreeDroidEnclaves",
    "Jawa_WildsteamClan",
    "Jawa_GeonosianFoundryHive",
    "Jawa_AscendantHelix",
    "Jawa_Junkers",
    "Jawa_DeepwaterCompact",
]
OUT = r"D:\Luke\dev\Rimworld\Transient\sixraid\raw_run3.json"
raw = {}

def interesting(msgs):
    out = []
    for m in msgs or []:
        t = m.get("type"); tx = m.get("text", "")
        if t in ("Error", "Warning"):
            out.append((t, tx[:500]))
        elif any(k in tx.lower() for k in ("raid", "pawngroup", "group maker", "spawning raid", "relation")):
            out.append((t, tx[:500]))
    return out[:12]

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for F in FACTIONS:
        rec = {}
        rec["hostile"] = rb.call("jawa/faction_relations_set",
                                 {"faction": F, "other": "Player", "kind": "Hostile"})
        rb.call("jawa/drain_log", {})
        rec["fire"] = rb.call("jawa/fire_raid", {"points": 3000, "faction": F, "dryRun": False})
        rec["log"] = rb.call("jawa/drain_log", {})
        rec["restore"] = rb.call("jawa/faction_relations_set",
                                 {"faction": F, "other": "Player", "kind": "Neutral", "goodwill": 0})
        raw[F] = rec
        h, f = rec["hostile"], rec["fire"]
        print("#####", F)
        print("  relset success:", h.get("success"), "| now:",
              json.dumps({k: h.get(k) for k in ("kind", "goodwill", "hostileToPlayer", "now", "nowKindA", "notes") if k in h})[:400])
        print("  executed:", f.get("executed"))
        print("  actual:", json.dumps(f.get("actual")))
        print("  arrived:", json.dumps(f.get("arrived")))
        print("  note:", (f.get("note") or "")[:250])
        for t, tx in interesting(rec["log"].get("messages")):
            print("   LOG[%s] %s" % (t, tx))

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(raw, fh, indent=1, default=str, ensure_ascii=False)
print("RAW ->", OUT)
