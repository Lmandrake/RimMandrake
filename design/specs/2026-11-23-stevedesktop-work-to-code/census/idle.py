#!/usr/bin/env python3
"""idle.py - wall time of the window per local day: lane job running (sent -> finished, per game), machine down, paused,
free. Reads done/quarantined/cancelled records, lane_windows.jsonl and steward.jsonl. Steve2 counts from steve2.on."""
import collections, json
from datetime import timedelta
from common import *
R, _ = records(("done", "quarantined"))
STEVE2_ON = ts("2026-11-23T10:56:00Z")            # mtime of steve2.on
DAY = lambda t: (t - timedelta(hours=8)).strftime("%m-%d")
def union(iv):
    out = []
    for a, b in sorted(iv):
        if out and a <= out[-1][1]: out[-1][1] = max(out[-1][1], b)
        else: out.append([a, b])
    return out
def spread(iv):
    c = collections.Counter()
    for a, b in union(iv):
        while a < b:
            mid = (a - timedelta(hours=8)).replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1, hours=8)
            e = min(b, mid); c[DAY(a)] += (e - a).total_seconds() / 3600; a = e
    return c
def clip(a, b): return (max(a, START), min(b, END))
busy = {"Steve1": [], "Steve2": []}; nosent = 0; real = []; fill = []
for d in R:
    s, f = ts(d.get("sent")), d["_fin"]
    if not s or not f: nosent += 1; continue
    h = "Steve2" if d.get("host") == "stevedesktop.b" else "Steve1"
    busy[h].append(clip(s, f))
    (fill if "filler" in str(d["job"]["requested_by"]) else real).append(clip(s, f))
L = [json.loads(l) for l in open(Q + "/lane_windows.jsonl")]
def win(kind): return [clip(ts(x["since"]), ts(x["until"])) for x in L if x["kind"] == kind and x.get("until") and ts(x["until"]) > START]
print("lane_windows kinds", collections.Counter(x["kind"] for x in L), "open-ended", sum(not x.get("until") for x in L))
down, maint = win("machine_down"), win("maintenance")
# steward states: time in each state (an event holds until the next state event)
S = [json.loads(l) for l in open(Q + "/steward.jsonl")]
S = [(ts(x["ts"]), x["state"], x.get("reason")) for x in S if x.get("event") == "state" and x.get("by") != "watch"]
st = collections.defaultdict(list)
for (a, s, r), n in zip(S, S[1:] + [(END, None, None)]):
    if n[0] > START: st[s].append(clip(max(a, START), n[0]))
b1, b2, dn = spread(busy["Steve1"]), spread(busy["Steve2"]), spread(down)
rl, fl = spread(real), spread(fill)
print("jobs with no sent time", nosent)
print("day   Steve1 busy  Steve2 busy  down | real  filler | steward states (h)")
sp = {k: spread(v) for k, v in st.items()}
t = START; days = sorted({DAY(START + timedelta(hours=h)) for h in range(0, DAYS * 24)} | {DAY(END)})
for x in days:
    print(x, "%6.1f %6.1f %6.1f | %5.1f %5.1f |" % (b1[x], b2[x], dn[x], rl[x], fl[x]), {k: round(v[x], 1) for k, v in sp.items() if v[x] >= .1})
tot = lambda c: round(sum(c.values()), 1)
print("TOTAL Steve1", tot(b1), "Steve2", tot(b2), "down", tot(dn), "maint", tot(spread(maint)), "real", tot(rl), "filler", tot(fl), "window h", DAYS * 24, {k: tot(v) for k, v in sp.items()})
# queue wait of real jobs
w = sorted(((ts(d["sent"]) - d["_sub"]).total_seconds() / 60 for d in R if d.get("sent") and "filler" not in str(d["job"]["requested_by"])))
print("queue wait min, asked jobs: n %d median %.1f p90 %.1f max %.0f" % (len(w), w[len(w)//2], w[int(len(w)*.9)], w[-1]))
