#!/usr/bin/env python3
"""bottleneck_measure: who waits on whom, read from Relentless's own logs and the agents' transcripts.

Item HARNESS_BOTTLENECK_MEASURE_WHO_WAITS_ON_WHOM. Two questions from the owner (2026-10-22):
  Q1 "If we could test twice as many things in game but the llm delays were the same how much would that help?"
  Q2 per-writer clones vs the shared clone: "evidence based on our stats".

  game     Q1 from the Relentless store: game-phase timeline (proof runs from live/*.log, staging from
           game_stage -> game_staged), item-seconds spent waiting for the game split by what the game was
           doing meanwhile, per-item lead-time decomposition and the 2x-game projection, worker-slot pressure.
  publish  Q2 from transcripts: every ./publish call, its outcome class, time in the call and time from a
           refusal to the next PUBLISHED, grouped by writer model (per-writer Relentless clones vs the shared
           seat clones) and day.

Every number is MEASURED from the files named in the output, except the fields whose names start with
"proj_" (a projection, with the assumption stated beside it). Read-only: it writes only --out.
"""
import argparse
import bisect
import datetime as dt
import glob
import json
import os
import re
import statistics
import sys

DEFAULT_ROOT = "/home/mandrake/rm/relentless"
PROJECTS = os.path.expanduser("~/.claude/projects")
TICK_GAP_CAP = 1800      # a sample gap longer than this is the supervisor being down, not anyone waiting
LIVE_RE = re.compile(r"^(?P<item>.+?)-(?P<clause>[A-Z]+\d+)-(?P<ts>\d{8}T\d{6}Z)(?:-(?P<sub>[A-Za-z]+))?\.log$")
HOLD_RE = re.compile(r"one live user at a time: (\S+) holds the game phase")


# ---------- time and intervals ----------

def ts(s):
    """ISO-8601 'Z' or epoch number -> epoch seconds (float)."""
    if isinstance(s, (int, float)):
        return float(s)
    s = s.strip().replace("Z", "+00:00")
    if re.match(r"^\d{8}T\d{6}\+00:00$", s):
        return dt.datetime.strptime(s[:15], "%Y%m%dT%H%M%S").replace(tzinfo=dt.timezone.utc).timestamp()
    return dt.datetime.fromisoformat(s).timestamp()


def iso(t):
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def merge(iv):
    """Merge [(a,b)] into sorted disjoint intervals; empty or inverted ones are dropped."""
    out = []
    for a, b in sorted((a, b) for a, b in iv if b > a):
        if out and a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return [tuple(x) for x in out]


def total(iv):
    return sum(b - a for a, b in merge(iv))


def clip(iv, lo, hi):
    return [(max(a, lo), min(b, hi)) for a, b in iv if min(b, hi) > max(a, lo)]


def overlap(a, b, merged):
    """Seconds of [a,b) covered by the merged interval list."""
    return sum(max(0.0, min(b, y) - max(a, x)) for x, y in merged if y > a and x < b)


def subtract(iv, minus):
    """merged(iv) minus merged(minus)."""
    out = []
    minus = merge(minus)
    for a, b in merge(iv):
        cur = a
        for x, y in minus:
            if y <= cur or x >= b:
                continue
            if x > cur:
                out.append((cur, x))
            cur = max(cur, y)
        if cur < b:
            out.append((cur, b))
    return out


def q(xs, p):
    xs = sorted(xs)
    if not xs:
        return None
    return xs[min(len(xs) - 1, int(round(p * (len(xs) - 1))))]


# ---------- Q1: the game ----------

def read_jsonl(path):
    try:
        f = open(path, encoding="utf-8", errors="replace")
    except OSError:
        return
    with f:
        for line in f:
            try:
                yield json.loads(line)
            except ValueError:
                continue


def proof_intervals(live_dir, lo, hi):
    """[(start, end, item)] for every live proof/site log: start from the name, end from mtime."""
    out = []
    for p in glob.glob(os.path.join(live_dir, "*.log")):
        m = LIVE_RE.match(os.path.basename(p))
        if not m:
            continue
        a, b = ts(m.group("ts")), os.path.getmtime(p)
        if b > lo and a < hi and b > a:
            out.append((max(a, lo), min(b, hi), m.group("item")))
    return out


def round_records(path):
    """Every live round record (a dict with 'at', its START stamp) in round.out, a stream of pretty-printed JSON.
    relentless_live_round.run_round stamps `at` when the round starts and, since LIVEROUND_SHRINK_PROOFS_ARE_THE_SHORT_PART,
    `ended` when it writes the record; until then this file read `at` as the END and so charged every round with the
    idle gap to the round before it (2026-11-03: "11.5 h of rounds" whose runs spanned 2.2 h)."""
    try:
        txt = open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return []
    dec, i, out = json.JSONDecoder(), 0, []
    while i < len(txt):
        while i < len(txt) and txt[i] in " \r\n\t":
            i += 1
        if i >= len(txt):
            break
        try:
            o, i = dec.raw_decode(txt, i)
        except ValueError:
            nl = txt.find("\n", i)
            i = len(txt) if nl < 0 else nl + 1
            continue
        if isinstance(o, dict) and "at" in o:
            out.append(o)
    return sorted(out, key=lambda o: ts(o["at"]))


def round_spans(recs, live_dir):
    """[(start, end, record)] per round: start = its `at`; end = its `ended`, or for a record written before `ended`
    existed, the last live log (proof or site) that started inside the round, before the next round started (a round
    runs its clauses one after another, each with its own log); a round that ran no proof ends where it started."""
    logs = []
    for p in glob.glob(os.path.join(live_dir, "*.log")):
        m = LIVE_RE.match(os.path.basename(p))
        if m:
            logs.append((ts(m.group("ts")), os.path.getmtime(p)))
    logs.sort()
    starts = [ts(o["at"]) for o in recs]
    out = []
    for k, o in enumerate(recs):
        a = starts[k]
        if o.get("ended"):
            b = ts(o["ended"])
        else:
            nxt = starts[k + 1] if k + 1 < len(starts) else float("inf")
            b = max([a] + [e for s, e in logs[bisect.bisect_left(logs, (a - 1,)):] if s < nxt])
        out.append((a, max(a, b), o))
    return out


def round_outcomes(recs, lo, hi):
    """{outcome: n} over every criterion run in rounds that started in [lo,hi), plus rounds with/without a run."""
    out, with_runs = {}, 0
    n = 0
    for o in recs:
        if not (lo <= ts(o["at"]) < hi):
            continue
        n += 1
        runs = o.get("runs") or []
        with_runs += bool(runs)
        for r in runs:
            k = str(r.get("outcome"))
            out[k] = out.get(k, 0) + 1
    return {"rounds": n, "rounds_with_runs": with_runs, "criterion_runs": dict(sorted(out.items()))}


def round_intervals(spans, lo, hi, legacy=None):
    """[(start, end)] per round from round_spans, clipped to [lo,hi). legacy: True only the records without `ended`
    (their end read from logs), False only the stamped ones, None all."""
    return clip([(a, b) for a, b, o in spans if legacy is None or legacy == (not o.get("ended"))], lo, hi)


def samples(journal, lo, hi):
    """[(t, dt, acts)] for every tick/game_next record in [lo,hi); dt to the next sample, capped."""
    recs = sorted(((ts(r["at"]), r.get("acts") or []) for r in journal
                   if r.get("do") in ("tick", "game_next") and "at" in r), key=lambda x: x[0])
    times = [t for t, _ in recs]
    out = []
    for t, acts in recs:
        if not (lo <= t < hi):
            continue
        j = bisect.bisect_right(times, t)        # the next STRICTLY later sample: two records at one stamp both last
        nxt = times[j] if j < len(times) else hi
        d = min(nxt, hi) - t
        out.append((t, d if d <= TICK_GAP_CAP else 0.0, acts))
    return out


def stage_intervals(journal, lo, hi):
    """[(start, end)] from each item's game_stage act to its next game_staged act (a game restart/load)."""
    open_at, out = {}, []
    evs = []
    for r in journal:
        for a in r.get("acts") or []:
            if a.get("do") in ("game_stage", "game_staged") and "at" in r:
                evs.append((ts(r["at"]), a["do"], a.get("item")))
    for t, d, item in sorted(evs, key=lambda e: e[0]):
        if d == "game_stage":
            open_at.setdefault(item, t)
        elif item in open_at:
            out.append((open_at.pop(item), t))
    return clip(out, lo, hi)


CHECK_ENDS = ("proof_weak", "blind_fail", "done", "game_entered", "game_implemented", "checker_lost", "returned")


def check_intervals(journal):
    """{item: [(start, end)]} from each check_started act to the item's next verdict act."""
    evs = []
    for r in journal:
        if "at" not in r:
            continue
        for a in r.get("acts") or []:
            if a.get("item") and (a.get("do") == "check_started" or a.get("do") in CHECK_ENDS):
                evs.append((ts(r["at"]), a["do"], a["item"]))
    open_at, out = {}, {}
    for t, d, item in sorted(evs, key=lambda e: e[0]):
        if d == "check_started":
            open_at.setdefault(item, t)
        elif item in open_at:
            out.setdefault(item, []).append((open_at.pop(item), t))
    return out


def wait_class(why):
    why = why or ""
    if HOLD_RE.search(why):
        return "held_by_item"
    if "driver lock" in why or "NOT TAKEABLE" in why:
        return "bridge_held_by_seat"
    if why.startswith("harness") or "cannot be read" in why:
        return "harness"
    return "other"


def game_measure(root, lo, hi):
    store = os.path.join(root, "store")
    journal = list(read_jsonl(os.path.join(store, "journal.jsonl")))
    proofs = proof_intervals(os.path.join(root, "live"), lo, hi)
    prove_u = merge([(a, b) for a, b, _ in proofs])
    stage_u = merge(stage_intervals(journal, lo, hi))
    recs = round_records(os.path.join(root, "live", "round.out"))
    spans = round_spans(recs, os.path.join(root, "live"))
    rounds = round_intervals(spans, lo, hi)
    round_u = merge(rounds)
    busy_u = merge(prove_u + stage_u + round_u)
    window = hi - lo
    sm = samples(journal, lo, hi)
    covered = sum(d for _, d, _ in sm)

    # item-seconds waiting for the game, split by what the game was doing over the same seconds
    wait = {"total": 0.0, "while_proving": 0.0, "while_staging": 0.0, "while_round_not_proving": 0.0,
            "while_idle": 0.0}
    by_class = {}
    demand_u, slots_full_u, check_backlog_u = [], [], []
    per_item_wait = {}
    for t, d, acts in sm:
        if d <= 0:
            continue
        waiting = [a for a in acts if a.get("do") == "game_waits"]
        if waiting:
            demand_u.append((t, t + d))
        pr = overlap(t, t + d, prove_u)
        st = overlap(t, t + d, subtract(stage_u, prove_u))
        rd = overlap(t, t + d, subtract(round_u, prove_u + stage_u))
        for a in waiting:
            c = wait_class(a.get("why"))
            by_class[c] = by_class.get(c, 0.0) + d
            wait["total"] += d
            wait["while_proving"] += pr
            wait["while_staging"] += st
            wait["while_round_not_proving"] += rd
            wait["while_idle"] += d - pr - st - rd
            it = a.get("item")
            w = per_item_wait.setdefault(it, {"total": 0.0, "while_proving": 0.0})
            w["total"] += d
            w["while_proving"] += pr
        whys = {a.get("why") for a in acts if a.get("do") == "wait"}
        if "max_workers" in whys:
            slots_full_u.append((t, t + d))
        if "check_backlog" in whys:
            check_backlog_u.append((t, t + d))
    demand_u = merge(demand_u)

    checks = check_intervals(journal)

    # per-item lead time for items done in the window
    items = []
    for sp in glob.glob(os.path.join(store, "items", "*", "state.json")):
        try:
            s = json.load(open(sp, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if s.get("status") != "done" or not s.get("done_at") or not s.get("enrolled_at"):
            continue
        done, enr = float(s["done_at"]), float(s["enrolled_at"])
        if not (lo <= done < hi):
            continue
        att = list(read_jsonl(os.path.join(os.path.dirname(sp), "attempts.jsonl")))
        worker, cur, first = 0.0, None, None
        for r in sorted(att, key=lambda r: r.get("at", "")):
            if "start" in r and "end" not in r:
                cur = ts(r["at"])
                first = cur if first is None else first
            elif "end" in r and cur is not None:
                worker += max(0.0, ts(r["at"]) - cur)
                cur = None
        item = s["item"]
        own = total([(a, b) for a, b, i in proofs if i == item and a >= enr])
        gw = per_item_wait.get(item, {"total": 0.0, "while_proving": 0.0})
        live = bool(s.get("game")) or own > 0 or gw["total"] > 0
        lead = done - enr
        queue = max(0.0, (first if first is not None else done) - enr)
        chk = total(clip(checks.get(item, []), enr, done))
        items.append({"item": item, "live": live, "lead_s": lead, "queue_s": queue, "worker_s": worker,
                      "check_s": chk, "own_prove_s": own,
                      "game_wait_s": gw["total"], "game_wait_while_proving_s": gw["while_proving"],
                      "other_s": max(0.0, lead - queue - worker - chk - own - gw["total"]),
                      "proj_2x_save_lo_s": own / 2,
                      "proj_2x_save_hi_s": own / 2 + gw["while_proving"]})

    def agg(rows):
        if not rows:
            return {"n": 0}
        lead = sum(r["lead_s"] for r in rows)
        out = {"n": len(rows), "lead_h_sum": lead / 3600, "lead_h_median": statistics.median(r["lead_s"] for r in rows) / 3600}
        for k in ("queue_s", "worker_s", "check_s", "own_prove_s", "game_wait_s", "other_s"):
            out[k.replace("_s", "_share")] = sum(r[k] for r in rows) / lead if lead else None
        out["proj_2x_save_share_lo"] = sum(r["proj_2x_save_lo_s"] for r in rows) / lead if lead else None
        out["proj_2x_save_share_hi"] = sum(r["proj_2x_save_hi_s"] for r in rows) / lead if lead else None
        return out

    staffing = {"samples": 0, "why_s": {}, "running_ge_target_s": 0.0, "ready_median": None}
    st_rows = [r for r in read_jsonl(os.path.join(store, "staffing.jsonl")) if "t" in r and lo <= r["t"] < hi]
    st_rows.sort(key=lambda r: r["t"])
    readies = []
    for i, r in enumerate(st_rows):
        d = (st_rows[i + 1]["t"] if i + 1 < len(st_rows) else hi) - r["t"]
        d = d if d <= TICK_GAP_CAP else 0.0
        w = str(r.get("why"))
        staffing["why_s"][w] = staffing["why_s"].get(w, 0.0) + d
        if (r.get("running") or 0) >= (r.get("target") or 0):
            staffing["running_ge_target_s"] += d
        if r.get("ready") is not None:
            readies.append(r["ready"])
    staffing["samples"] = len(st_rows)
    staffing["ready_median"] = statistics.median(readies) if readies else None

    return {
        "window": [iso(lo), iso(hi)], "window_h": window / 3600,
        "sources": {"journal": os.path.join(store, "journal.jsonl"), "live": os.path.join(root, "live"),
                    "items": os.path.join(store, "items"), "staffing": os.path.join(store, "staffing.jsonl")},
        "supervisor_sampled_h": covered / 3600,
        "game": {"proving_h": total(prove_u) / 3600, "staging_h": total(subtract(stage_u, prove_u)) / 3600,
                 "rounds": sum(1 for a, _, _ in spans if lo <= a < hi), "round_h": total(round_u) / 3600,
                 "rounds_end_from_logs": sum(1 for a, _, o in spans if lo <= a < hi and not o.get("ended")),
                 "round_minus_proof_h": total(subtract(round_u, prove_u)) / 3600,
                 "busy_h": total(busy_u) / 3600, "busy_share": total(busy_u) / window if window else None,
                 "proof_logs": len(proofs),
                 "outcomes": round_outcomes(recs, lo, hi),
                 "demand_h": total(demand_u) / 3600,
                 "demand_and_idle_h": total(subtract(demand_u, busy_u)) / 3600},
        "game_wait_item_h": {k: v / 3600 for k, v in wait.items()},
        "game_wait_by_reason_item_h": {k: v / 3600 for k, v in sorted(by_class.items())},
        "worker_slots_full_h": total(slots_full_u) / 3600,
        "check_backlog_h": total(check_backlog_u) / 3600,
        "staffing": {**staffing, "why_s": {k: round(v) for k, v in staffing["why_s"].items()}},
        "done_items": {"all": agg(items), "live": agg([r for r in items if r["live"]]),
                       "offline": agg([r for r in items if not r["live"]])},
        "proj_note": "proj_2x_save_lo = half of each item's own proof time; _hi adds every second it waited "
                     "behind another item's running proof (generous: a second lane removes that queue entirely). "
                     "Waits behind staging or a held-but-idle game phase are not counted: 2x proof speed does not "
                     "touch them.",
        "items": sorted(items, key=lambda r: -r["lead_s"]),
    }


# ---------- Q2: publish outcomes by writer model ----------

BENIGN = ("nothing to publish", "a message is required", "outside this repo", "not inside a git repository")


def classify_publish(text):
    """One ./publish tool_result text -> outcome class."""
    if "PUBLISHED" in text:
        return "published"
    low = text.lower()
    if any(b in low for b in BENIGN):
        return "benign"
    if "REFUSED" not in text:
        return "no_verdict"
    if "uncommitted edits" in low or "reset --keep" in low or "dirty" in low or "unstaged" in low:
        return "dirty_tree"
    if "conflict" in low:
        return "conflict"
    if "source-stamp" in low or "srchash" in low or "rebuild of" in low:
        return "dll_stamp"
    if ("origin kept moving" in low or "head moved" in low or "publish lock" in low or "push failed" in low
            or "non-fast-forward" in low or "already holds a submission" in low):
        return "race"
    return "other_refused"


PUBLISH_RE = re.compile(r"(^|[;&|\s(])\./publish\b")


def writer_model(dirname):
    if dirname.startswith("-home-mandrake-rm-relentless-clones-"):
        return "per_writer_clone"
    if dirname.startswith("-home-mandrake-rm-bench") or dirname.startswith("-home-mandrake-rm-foundry"):
        return "shared_seat_clone"
    return None


def scan_transcript(path):
    """-> [(start_epoch, dur_s, cls)] for every ./publish Bash call in one transcript, in order."""
    pend, rows = {}, []
    for line in open(path, encoding="utf-8", errors="replace"):
        if "publish" not in line and "PUBLISHED" not in line and "REFUSED" not in line:
            continue
        try:
            r = json.loads(line)
        except ValueError:
            continue
        t = r.get("timestamp")
        c = (r.get("message") or {}).get("content")
        if not t or not isinstance(c, list):
            continue
        for b in c:
            if not isinstance(b, dict):
                continue
            if b.get("type") == "tool_use" and b.get("name") == "Bash":
                if PUBLISH_RE.search((b.get("input") or {}).get("command", "")):
                    pend[b.get("id")] = ts(t)
            elif b.get("type") == "tool_result" and b.get("tool_use_id") in pend:
                s = pend.pop(b["tool_use_id"])
                cont = b.get("content")
                txt = cont if isinstance(cont, str) else json.dumps(cont)
                rows.append((s, max(0.0, ts(t) - s), classify_publish(txt)))
    return rows


def recovery_times(rows):
    """For each collision refusal, seconds to the next published call in the same transcript (None if never)."""
    out = []
    for i, (s, _, c) in enumerate(rows):
        if c in ("dirty_tree", "dll_stamp", "conflict", "race", "other_refused"):
            nxt = next((s2 for s2, _, c2 in rows[i + 1:] if c2 == "published"), None)
            out.append((c, None if nxt is None else nxt - s))
    return out


def publish_measure(lo, hi, projects=PROJECTS):
    days = {}
    files = 0
    for d in sorted(os.listdir(projects)):
        model = writer_model(d)
        if not model:
            continue
        for p in glob.glob(os.path.join(projects, d, "**", "*.jsonl"), recursive=True):
            if os.path.getmtime(p) < lo:
                continue
            rows = [r for r in scan_transcript(p) if lo <= r[0] < hi]
            if not rows:
                continue
            files += 1
            for s, dur, c in rows:
                k = (model, iso(s)[:10])
                e = days.setdefault(k, {"calls": 0, "call_s": 0.0, "writers": set(), "cls": {}, "recover_s": [],
                                        "unrecovered": 0})
                e["calls"] += 1
                e["call_s"] += dur
                e["writers"].add(p)
                e["cls"][c] = e["cls"].get(c, 0) + 1
            for (c, rec), (s, _, _) in zip(recovery_times(rows), [r for r in rows if r[2] in
                                                                  ("dirty_tree", "dll_stamp", "conflict", "race",
                                                                   "other_refused")]):
                e = days[(model, iso(s)[:10])]
                if rec is None:
                    e["unrecovered"] += 1
                else:
                    e["recover_s"].append(rec)
    out = {}
    for (model, day), e in sorted(days.items()):
        coll = sum(e["cls"].get(c, 0) for c in ("dirty_tree", "dll_stamp", "conflict", "race", "other_refused"))
        out.setdefault(model, {})[day] = {
            "calls": e["calls"], "writers": len(e["writers"]), "call_min": e["call_s"] / 60,
            "classes": dict(sorted(e["cls"].items())), "collisions": coll,
            "collisions_per_100_calls": 100.0 * coll / e["calls"] if e["calls"] else None,
            "recover_min_median": (statistics.median(e["recover_s"]) / 60) if e["recover_s"] else None,
            "recover_min_sum": sum(e["recover_s"]) / 60, "unrecovered": e["unrecovered"]}
    return {"window": [iso(lo), iso(hi)], "transcripts_with_publish": files, "source": projects, "by_model_day": out}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("what", choices=("game", "publish", "all"))
    ap.add_argument("--since", required=True, help="ISO UTC, e.g. 2026-11-03T00:00:00Z")
    ap.add_argument("--until", required=True)
    ap.add_argument("--root", default=os.environ.get("RELENTLESS_ROOT") or DEFAULT_ROOT)
    ap.add_argument("--projects", default=PROJECTS)
    ap.add_argument("--out", help="write the full JSON here (stdout gets the summary without per-item rows)")
    a = ap.parse_args(argv)
    lo, hi = ts(a.since), ts(a.until)
    res = {}
    if a.what in ("game", "all"):
        res["game"] = game_measure(a.root, lo, hi)
    if a.what in ("publish", "all"):
        res["publish"] = publish_measure(lo, hi, a.projects)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, sort_keys=True)
    short = json.loads(json.dumps(res))
    if "game" in short:
        short["game"].pop("items", None)
    print(json.dumps(short, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
