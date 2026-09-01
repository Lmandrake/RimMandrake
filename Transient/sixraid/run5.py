# -*- coding: utf-8 -*-
"""Forced-strategy / forced-arrival raid, Hutt vs Empire control, with a real log diff."""
import sys, io, json, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

def census(rb):
    r = rb.call("jawa/list_pawns", {"limit": 500})
    c = collections.Counter()
    for p in r.get("pawns", []):
        c[p.get("faction")] += 1
    return c, r.get("totalOnMap")

def logsnap(rb):
    r = rb.call("jawa/drain_log", {"limit": 400})
    return [(m.get("type"), m.get("text", "")) for m in (r.get("messages") or [])]

def logdiff(a, b):
    # b is newer; find the tail of b that is not in a (list of tuples, order preserved)
    if not a:
        return b
    last = a[-1]
    try:
        i = len(b) - 1 - b[::-1].index(last)
        return b[i + 1:]
    except ValueError:
        return b

host, port, token = resolve_endpoint()
CASES = [
    ("Empire", None, None),
    ("Jawa_HuttCartel", None, None),
    ("Jawa_HuttCartel", "ImmediateAttack", "EdgeWalkIn"),
    ("Jawa_FreeDroidEnclaves", "ImmediateAttack", "EdgeWalkIn"),
]
with RimBridge(host, port, token) as rb:
    pv = rb.call("jawa/raid_preview", {"points": 3000})
    print("PREVIEW usableStrategies:", [s["def"] for s in pv.get("usableStrategies", [])])
    print("PREVIEW arrivalModes:", [a["def"] for a in pv.get("arrivalModes", [])][:30])
    print("PREVIEW defaultParms:", json.dumps(pv.get("defaultParms")))
    for F, strat, arr in CASES:
        rb.call("jawa/faction_relations_set", {"faction": F, "other": "Player", "kind": "Hostile"})
        before, nb = census(rb)
        l0 = logsnap(rb)
        args = {"points": 3000, "faction": F, "dryRun": False}
        if strat: args["strategy"] = strat
        if arr: args["arrivalMode"] = arr
        f = rb.call("jawa/fire_raid", args)
        l1 = logsnap(rb)
        rb.call("rimworld/step_game_ticks", {"ticks": 240, "timeoutMs": 120000})
        after, na = census(rb)
        l2 = logsnap(rb)
        print("=====", F, strat, arr)
        print("  executed:", f.get("executed"), "actual:", json.dumps(f.get("actual")))
        print("  arrived_instant:", json.dumps(f.get("arrived")))
        print("  pawns %s -> %s   delta: %s" % (nb, na, json.dumps({k: after[k]-before.get(k,0) for k in set(after)|set(before) if after[k]-before.get(k,0)})))
        print("  --- log during fire ---")
        for t, tx in logdiff(l0, l1)[-25:]:
            print("    [%s] %s" % (t, tx[:260]))
        print("  --- log during 240 ticks ---")
        for t, tx in logdiff(l1, l2)[-15:]:
            print("    [%s] %s" % (t, tx[:260]))
        rb.call("jawa/destroy_bulk", {"filter": "nonColonists", "dryRun": False})
        rb.call("jawa/faction_relations_set", {"faction": F, "other": "Player", "kind": "Neutral", "goodwill": 0})
