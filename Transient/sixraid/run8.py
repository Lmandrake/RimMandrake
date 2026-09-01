# -*- coding: utf-8 -*-
"""Correlate raid success with leader / flags across many factions."""
import sys, io, json, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    fl = rb.call("jawa/list_factions", {})
    facs = [f for f in fl.get("factions", []) if not f.get("isPlayer")]
    lg = rb.call("jawa/faction_leader_get", {});
    import json as _j; print("LEADERGET KEYS", sorted(lg.keys())); print(_j.dumps({k:v for k,v in lg.items() if k!="operation"}, default=str)[:4000]);
    leaders = {}
    print("FACTION TABLE")
    rows = {}
    for f in facs:
        d = f["defName"]
        lead = leaders.get(d, {})
        flags = rb.call("jawa/faction_flags_set", {"faction": d, "dryRun": True})
        rows[d] = (f.get("settlementCount"), lead, flags)
        print("  %-32s settlements=%-3s leader=%s flags=%s" % (
            d, f.get("settlementCount"),
            json.dumps({k: v for k, v in lead.items() if k not in ("operation",)})[:220],
            json.dumps(flags.get("was") or flags.get("now"))))
