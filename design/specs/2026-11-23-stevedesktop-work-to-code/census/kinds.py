#!/usr/bin/env python3
"""kinds.py - each job of the window that did not finish DONE gets ONE setup kind by its cause and note (first rule that
matches); each DONE job is read for the setup faults a DONE outcome hides. Prints counts, dates, an example, lane hours."""
import collections, json, re
from common import *
R, bad = records(); C = collections.Counter
FW = [(ts(w["start"]), ts(w["end"]) if w.get("end") else END, w["id"]) for w in json.load(open(Q + "/fault_windows.json"))]
RULES = [   # (kind, regex on note, (outcome, cause) or None)
 ("wrong game: Steve2's job refused, its own game still up", r"is running; it rewrites Prefs", None),
 ("stale deploy: bridge companion not built from the job's sources", r"companion STALE|not built from this job's sources", None),
 ("wrong mod list: the list could not be written (swap marker or before-copy)", r"modset_builder --tier .* --apply failed|REFUSING TO WRITE|swap marker", None),
 ("wrong mod list: the running load was not the composed list", r"stale_load|loaded but not composed", None),
 ("wrong map: the game held no test map the runner may use", r"NOT READY: a game is Playing|launch gate REFUSES to start a map|LaunchGateRefused", None),
 ("runner clone could not update", r"runner pull failed", None),
 ("wrong contract: the worker's result shape was refused", r"broke contracts", None),
 ("stopped from outside", r"stopped \(SIGTERM\)", None),
 ("game process gone under the job", r"the game loaded as pid .* is gone", None),
 ("red canary", r"canary was red", None),
 ("harness read fault (broken JSON, bad python, bridge closed, no sheet)", r"modcheck exit|no sheet|Fatal Python|bridge", ("INVALID", "HARNESS")),
 ("game crashed or never got ready while loading", r".", ("INVALID", "LOAD")),
]
def kind(d):
    r = d["result"]; n = str(r.get("note") or "")
    for k, rx, oc in RULES:
        if oc and (r.get("outcome"), r.get("cause")) != oc: continue
        if re.search(rx, n, re.S): return k
    return "other (%s %s)" % (r.get("outcome"), r.get("cause"))
def inside(d):
    s, f = ts(d.get("sent")) or d["_sub"], d["_fin"]
    return any(a < f and s < b for a, b, _ in FW)
def rep(G, title):
    print("\n" + title)
    for k, v in sorted(G.items(), key=lambda kv: -len(kv[1])):
        h = sum(((d["_fin"] - ts(d["sent"])).total_seconds() / 3600) for d in v if d.get("sent"))
        print("%4d quarantined %3d in-window %3d asked %3d filler %3d lane %5.1f h  %s..%s  last %s  %s" % (
            len(v), sum(d["_state"] == "quarantined" for d in v), sum(map(inside, v)), sum("filler" not in str(d["job"]["requested_by"]) for d in v),
            sum("filler" in str(d["job"]["requested_by"]) for d in v), h, v[0]["_fin"].strftime("%m-%d"), v[-1]["_fin"].strftime("%m-%d"), v[-1]["job"]["id"], k))
G = collections.defaultdict(list)
for d in R:
    if d["result"].get("outcome") != "DONE": G[kind(d)].append(d)
print("jobs", len(R), "DONE", sum(d["result"].get("outcome") == "DONE" for d in R), "unreadable", len(bad))
rep(G, "NOT DONE, by kind (a job has one kind)")
H = collections.defaultdict(list)
FIXED = ts("2026-11-24T00:35:00Z")    # 3bfaf78cd0
for d in R:
    if d["result"].get("outcome") != "DONE": continue
    rows = d["result"].get("rows") or []; det = [str(r.get("detail")) for r in rows]
    bads = [r for r in rows if r.get("verdict") in ("UNMEASURED", "NOT_RUN")]
    if d.get("host") == "stevedesktop.b" and d["_fin"] < FIXED: H["wrong build attested: a Steve2 result that checked Steve1's install (before 3bfaf78cd0)"].append(d)
    if rows and len(bads) == len(rows): H["ran to the end and measured nothing (every row UNMEASURED or NOT_RUN)"].append(d)
    if any(re.search(r"UNMEASURED SITE|could not make a .* site current|GENERATED as|needs a (Desert|generated)|not a dune field|no map \(map_info|game is not Playing|needs the \S+ site", x) for x in det): H["wrong save, site or map: at least one row says so"].append(d)
    if any(re.search(r"dead colonists|could not hold the site quiet", x) for x in det): H["kept game was spoiled: dead colonist or site not quiet"].append(d)
    if any(re.search(r"No module named|cannot reach the bridge from WSL|no route to 127|bridge unreachable", x) for x in det): H["missing tool, package or the wrong python on the machine"].append(d)
    if any(re.search(r"PROOF BUILD REQUIRED|at the current mod hash|no \S+ result|no driver drives", x) for x in det): H["check cannot run in this lane (needs a driver, proof build or result made elsewhere)"].append(d)
    if any("preview plan, absent from the sheet" in x for x in det): H["planned rows that never ran"].append(d)
    if d["_state"] == "done" and (d.get("fault_window") or inside(d)):
        m = (d.get("fault_window") or {}).get("mode"); H["inside a machine-fault window and kept (%s)" % m].append(d)
        g = d.get("ingested") or {}
        if g.get("result") or g.get("run") or g.get("groups"): H["   of those, written to the ledger as a verdict"].append(d)
rep(H, "DONE, faults inside (a job can be in several)")
print("\nledger verdicts from kept in-window jobs:", C(str((d.get("ingested") or {}).get("result"))[:40] for d in H["   of those, written to the ledger as a verdict"]))
u = [d for d in R if d["_state"] == "done" and d["result"].get("outcome") == "DONE"]
print("DONE and kept:", len(u), "in a fault window:", sum(1 for d in u if inside(d)), "tagged:", sum(1 for d in u if d.get("fault_window")), "in-window but not tagged:", sum(1 for d in u if inside(d) and not d.get("fault_window")))
wh = sum((min(b, END) - max(a, START)).total_seconds() for a, b, _ in FW if b > START and a < END) / 3600
print("fault windows in the window: %d, %.1f h" % (sum(1 for a, b, _ in FW if b > START), wh), "last end", max(b for _, b, _ in FW))
SETUP = ("wrong game", "stale deploy", "wrong mod list", "wrong map", "runner clone", "wrong contract")
def allnone(d):
    v = [r.get("verdict") for r in d["result"].get("rows") or []]
    return d["result"].get("outcome") == "DONE" and bool(v) and not set(v) & {"PASS", "FAIL"}
for name, sel in (("all", lambda d: True), ("asked (agent, visit feed, old tick)", lambda d: "filler" not in str(d["job"]["requested_by"])), ("filler", lambda d: "filler" in str(d["job"]["requested_by"]))):
    for per, a in (("21 days", START), ("last 7 days", END - timedelta(days=7))):
        X = [d for d in R if sel(d) and d["_fin"] >= a]; nd = [d for d in X if d["result"].get("outcome") != "DONE"]
        s = [d for d in nd if kind(d).startswith(SETUP)]; z = [d for d in X if allnone(d)]
        print("%-36s %-11s jobs %d, not DONE %d, of them setup %d; DONE but measured nothing %d; DONE with a PASS or FAIL %d" % (name, per, len(X), len(nd), len(s), len(z), len(X) - len(nd) - len(z)))
X = [d for d in R if d["_fin"] >= END - timedelta(days=7) and d["result"].get("outcome") != "DONE"]
print("last 7 days, not DONE by kind", C(kind(d) for d in X))
