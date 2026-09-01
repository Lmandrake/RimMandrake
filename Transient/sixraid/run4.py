# -*- coding: utf-8 -*-
import sys, io, json, collections
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
OUT = r"D:\Luke\dev\Rimworld\Transient\sixraid\raw_run4.json"
raw = {}

def census(rb):
    r = rb.call("jawa/list_pawns", {"limit": 500})
    c = collections.Counter()
    kinds = collections.defaultdict(collections.Counter)
    for p in r.get("pawns", []):
        f = p.get("factionDef") or p.get("faction") or "(none)"
        c[f] += 1
        kinds[f][p.get("kindDef")] += 1
    return c, kinds, r.get("count")

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for F in FACTIONS:
        rec = {}
        rec["hostile"] = rb.call("jawa/faction_relations_set",
                                 {"faction": F, "other": "Player", "kind": "Hostile"})
        before, _, nb = census(rb)
        rb.call("jawa/drain_log", {"limit": 200})
        rec["fire"] = rb.call("jawa/fire_raid", {"points": 3000, "faction": F, "dryRun": False})
        rec["skyfallers"] = rb.call("jawa/list_things", {"group": "Everything", "limit": 200}) if False else None
        rec["pods"] = rb.call("jawa/list_things", {"defName": "DropPodIncoming,ShipLandingBeacon,ActiveDropPod", "limit": 50})
        rec["errs_immediate"] = rb.call("jawa/drain_log", {"limit": 60, "errorsOnly": True})
        rec["step"] = rb.call("rimworld/step_game_ticks", {"ticks": 300, "timeoutMs": 120000})
        after, kinds, na = census(rb)
        rec["errs_after"] = rb.call("jawa/drain_log", {"limit": 60, "errorsOnly": True})

        delta = {k: after[k] - before.get(k, 0) for k in after if after[k] - before.get(k, 0) != 0}
        f = rec["fire"]
        print("#####", F)
        print("  hostileOk:", f.get("actual", {}).get("substituted") is False, "executed:", f.get("executed"))
        print("  actual:", json.dumps(f.get("actual")))
        print("  arrived_instant:", json.dumps(f.get("arrived")))
        print("  pods_instant:", rec["pods"].get("count"), [t.get("defName") for t in (rec["pods"].get("things") or [])][:10])
        print("  pawns before/after: %s -> %s" % (nb, na))
        print("  DELTA by faction:", json.dumps(delta))
        for fac in delta:
            if fac.startswith("Jawa_") or delta[fac] > 0:
                print("    kinds[%s]: %s" % (fac, dict(kinds[fac])))
        for tag in ("errs_immediate", "errs_after"):
            for m in (rec[tag].get("messages") or [])[:8]:
                print("   %s[%s] %s" % (tag, m.get("type"), m.get("text", "")[:300]))
        raw[F] = rec

        rb.call("jawa/destroy_bulk", {"filter": "nonColonists", "dryRun": False})
        rb.call("jawa/faction_relations_set", {"faction": F, "other": "Player", "kind": "Neutral", "goodwill": 0})

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(raw, fh, indent=1, default=str, ensure_ascii=False)
print("RAW ->", OUT)
