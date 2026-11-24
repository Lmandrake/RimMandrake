#!/usr/bin/env python3
"""idle_why.py - steward fault/pause/brake time by reason head, and the hours with an asked job waiting and no job running."""
import collections, json, re
from common import *
def union(iv):
    out = []
    for a, b in sorted(x for x in iv if x[1] > x[0]):
        if out and a <= out[-1][1]: out[-1][1] = max(out[-1][1], b)
        else: out.append([a, b])
    return out
def inter(A, B):
    A, B = union(A), union(B); return [[max(a, c), min(b, d)] for a, b in A for c, d in B if max(a, c) < min(b, d)]
hrs = lambda iv: round(sum((b - a).total_seconds() for a, b in union(iv)) / 3600, 1)
S = [json.loads(l) for l in open(Q + "/steward.jsonl")]
S = [(ts(x["ts"]), x["state"], str(x.get("reason"))) for x in S if x.get("event") == "state" and x.get("by") != "watch"]
G = collections.defaultdict(list); st = collections.defaultdict(list)
for (a, s, r), n in zip(S, S[1:] + [(END, None, None)]):
    a, b = max(a, START), n[0]
    if b <= a: continue
    st[s].append([a, b])
    if s in ("PAUSED", "BRAKED", "IDLE_BY_RULE", "UNREACHABLE"):
        k = re.sub(r"F?\d{8}T\d{6}Z|\d{4}-\d\d-\d\dT[\d:]+Z|J\S+|\d+(\.\d+)?", "#", r)[:95]
        G[(s, k)].append([a, b])
for k, v in sorted(G.items(), key=lambda kv: -hrs(kv[1]))[:32]: print(hrs(v), len(v), v[0][0].strftime("%m-%d"), v[-1][1].strftime("%m-%d"), k)
R, _ = records(("done", "quarantined"))
busy = [[ts(d["sent"]), d["_fin"]] for d in R if d.get("sent")]
wait = [[d["_sub"], ts(d["sent"])] for d in R if d.get("sent") and "filler" not in str(d["job"]["requested_by"])]
quiet = [[START, END]]
for b in (union(busy),):
    out = []
    t = START
    for a, c in b:
        if a > t: out.append([t, a])
        t = max(t, c)
    if t < END: out.append([t, END])
    quiet = out
w = inter(wait, quiet)
print("hours an asked job waited while nothing ran:", hrs(w))
for s in st: print("   of those in state", s, hrs(inter(w, st[s])))
from datetime import timedelta
print("day: hours Steve1 idle-of-lane-jobs with an asked job waiting, by the steward's state")
d0 = (START - timedelta(hours=8)).replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(hours=8)
for i in range(DAYS + 1):
    a = d0 + timedelta(days=i); b = a + timedelta(days=1)
    x = inter(w, [[a, b]])
    if hrs(x) >= .5: print("  ", (a - timedelta(hours=8)).strftime("%m-%d"), hrs(x), {s: hrs(inter(x, st[s])) for s in st if hrs(inter(x, st[s])) >= .2})
bs = [x for x in R if x.get("sent")]
wj = sorted(((ts(x["sent"]) - x["_sub"]).total_seconds() / 3600, x["job"]["id"], x["job"]["requested_by"], x["job"]["mod"]) for x in bs if "filler" not in str(x["job"]["requested_by"]))
print("asked jobs that waited over 24 h:", sum(x[0] > 24 for x in wj), "over 2 h:", sum(x[0] > 2 for x in wj), "longest", [(round(x[0], 1),) + x[1:] for x in wj[-4:]])
since = ts("2026-11-21T21:20:00Z")
print("since 2026-11-21 1:20 PM PST (audio driver off): h", round((END - since).total_seconds() / 3600, 1), "Steve1 busy h", hrs(inter([[ts(x["sent"]), x["_fin"]] for x in bs if x.get("host") != "stevedesktop.b"], [[since, END]])))
