"""Measure silent stretches (stops) on ledger items over 7 days and classify who ended each.
Read-only. Run from the repo root. Writes JSON to argv[1]."""
import json, glob, os, re, sys, time, collections, datetime as dt

D = "/mnt/d/ClaudeWork/rimmandrake/dispatcher"
NOW = time.time()
SINCE = NOW - 7 * 86400
GAP_H = float(os.environ.get("GAP_H", "12"))

def ts(s):
    try:
        return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
    except Exception:
        return None

ev = collections.defaultdict(list)
for f in glob.glob("infrastructure/state/ledger/events/*.jsonl"):
    for l in open(f, errors="ignore"):
        try:
            d = json.loads(l)
        except Exception:
            continue
        if not d.get("id"):
            continue
        t = ts(d.get("ts", ""))
        if t is None:
            continue
        d["_t"] = t
        ev[d["id"]].append(d)

# who launched each detached unit
prog = ""
for p in [D + "/list_dispatch/state.json", D + "/list_dispatch/ticks.jsonl", D + "/maturation/state.json",
          D + "/maturation/ticks.jsonl", D + "/red_dispatch/state.json", D + "/red_dispatch/ticks.jsonl"] + \
        glob.glob(D + "/work_bundle/**/*", recursive=True) + glob.glob(D + "/list_effect/**/*", recursive=True):
    if os.path.isfile(p):
        prog += open(p, errors="ignore").read()
hand = open(D + "/maturation/hand_acts.jsonl", errors="ignore").read()
cont = set()
for f in glob.glob(D + "/detached/rm-detached-*.json"):
    if f.endswith((".out.json", ".alive.json")):
        continue
    try:
        d = json.load(open(f))
    except Exception:
        continue
    b = ""
    p = d.get("brief_file") or d.get("brief_src")
    if p and os.path.isfile(p):
        try:
            b = open(p, errors="ignore").read(400)
        except Exception:
            pass
    if "CONTINUED BY ITSELF" in b or "WORK BUNDLE RESTART" in b:
        cont.add(d.get("unit"))

def launcher(unit):
    if not unit:
        return None
    unit = re.sub(r"\.(service|scope)$", "", unit)
    if unit in hand:
        return "conductor"
    if unit in cont or unit in prog:
        return "program"
    return "conductor"   # a run no program record names: launched by the Conductor window (brief header check in evidence)

PROG_UNITS = ("rm-list-dispatch", "rm-list-effect", "rm-role-operations", "rm-maturation", "rm-deadman", "rm-ops",
              "rm-findings", "rm-role-designer", "rm-role-dispatcher", "rm-role-arbiter", "rm-role-auditor")
PROG_WHY = re.compile(r"^(detached run (clone returned|ended)|steward: the lane recovered|auto_judge|findings judge)", re.I)
UNIT_IN_TEXT = re.compile(r"(rm-detached-[a-z0-9-]+-\d{9,})")

def actor(d):
    seat = d.get("seat")
    ru = d.get("role_unit") or ""
    if d.get("ownerSaid") or d.get("byCard"):
        return "owner"
    if seat in ("RUNNER", "DISPATCHER"):
        return "program"
    if ru.startswith(PROG_UNITS):
        return "program"
    if ru == "rm-role-conductor" or ru.startswith("rm-role-conductor"):
        return "conductor"
    if ru.startswith("rm-detached-"):
        return launcher(ru) or "conductor"
    why = d.get("why") or ""
    if PROG_WHY.search(why):
        m = UNIT_IN_TEXT.search((d.get("text") or "") + " " + why)
        return launcher(m.group(1)) if m else "program"
    if seat == "OWNER":
        return "owner?"   # an OWNER-seat event with no words: recorded by someone with his authority
    return "conductor"

NOISE = {"lease", "home", "shape", "live", "raise", "finding", "seat", "game", "bridge", "guard"}
END = {"close", "drop", "supersede"}

stops, standing = [], []
for iid, es in ev.items():
    es.sort(key=lambda d: d["_t"])
    if es[-1]["_t"] < SINCE - 30 * 86400 and es[-1]["event"] in END:
        continue
    closed_at = None
    wait_until = 0.0
    last = None          # last progress event (time, event)
    filed = None
    for d in es:
        t, e = d["_t"], d["event"]
        if e == "file" and filed is None:
            filed = t
        if e in NOISE:
            continue
        if e == "wait":
            u = ts(str(d.get("until") or "")) or 0
            # the gap before a wait counts; from the wait on, the item waits on a date
        if last is not None and closed_at is None:
            gap_start = max(last[0], wait_until, SINCE)
            if t - gap_start >= GAP_H * 3600 and t > SINCE:
                stops.append({"id": iid, "from": gap_start, "to": t, "h": (t - gap_start) / 3600,
                              "ended_by_event": e, "ended_by": actor(d), "seat": d.get("seat"),
                              "role_unit": d.get("role_unit"), "why": (d.get("why") or "")[:160],
                              "before": last[1]})
        if e == "wait":
            wait_until = ts(str(d.get("until") or "")) or 0
        elif e == "unwait":
            wait_until = 0
        if e in END:
            closed_at = t
        elif e in ("reopen",) or (closed_at and e in ("claim", "start", "file")):
            closed_at = None
        last = (t, e)
    if closed_at is None and last is not None:
        gap_start = max(last[0], wait_until, SINCE)
        if NOW - gap_start >= GAP_H * 3600:
            standing.append({"id": iid, "from": gap_start, "h": (NOW - gap_start) / 3600, "last": last[1],
                             "waiting_until": wait_until if wait_until > NOW else None})

json.dump({"gap_h": GAP_H, "now": NOW, "since": SINCE, "stops": stops, "standing": standing},
          open(sys.argv[1], "w"), indent=0)
c = collections.Counter(s["ended_by"] for s in stops)
h = collections.Counter()
for s in stops:
    h[s["ended_by"]] += s["h"]
print("stops ended in window:", len(stops), dict(c), {k: round(v) for k, v in h.items()})
print("standing open stops:", len(standing), round(sum(s["h"] for s in standing)))
