#!/usr/bin/env python3
"""Daily agent improvement pass, step 0: gather one day's evidence per agent and per skill (no AI).

Design: design/RimMandrake/daily_agent_improvement_2026-11-02.md (item AGENT_IMPROVE_BUILD_JUDGED_DAILY_DIFFS).

    python3 src/RimMandrake/Utils/agent_improve.py gather [--day YYYY-MM-DD] [--out DIR] [--dry-run]

Reads day D's evidence (lessons filed, Relentless reject reasons, learned lines and alarms, Operations alarms, owner
words), routes each piece to a target (a role, `relentless`, or a skill), and writes a packet for the Curator:
<out>/<D>/packet.json and packet.md. A target is SIGNALLED only on recurrence: at least RECUR pieces in the WINDOW_DAYS
ending on D (owner ruling LESSONS_RETIRE_INBOX_AS_QUEUE: promote on recurrence, never count the backlog). At most
MAX_TARGETS signalled targets go in the packet, most pieces first. The Curator, the Judge and the apply step are owed.
"""
import argparse
import calendar
import glob
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import lessons  # noqa: E402  (parse_name, home_of)

STORE = "/home/mandrake/rm/relentless/store"          # relentless.DEFAULT_ROOT + /store
OPS_ALARMS = "/mnt/d/ClaudeWork/rimmandrake/ops_watch/alarms.json"
OUT = "/mnt/d/ClaudeWork/rimmandrake/agent_improve"
WINDOW_DAYS = 7
RECUR = 2
MAX_TARGETS = 6
AGENTS = {"relentless", "operations", "designer"}    # the agents rank before skills and docs under the cap
MAX_PIECES = 25                                       # per target in the packet; the kinds line counts them all
OK_ENDS = {"finish", "done"}                          # an attempt end that is not a reject
LEARNED = re.compile(r"^- (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z) gen \d+: (.*)$")


def day_bounds(day):
    t0 = calendar.timegm(time.strptime(day, "%Y-%m-%d"))
    return t0, t0 + 86400


def epoch(ts):
    try:
        return calendar.timegm(time.strptime(str(ts)[:19], "%Y-%m-%dT%H:%M:%S"))
    except (TypeError, ValueError):
        return None


def first_line(text, n=200):
    for ln in str(text or "").splitlines():
        ln = ln.strip().lstrip("#").strip()
        if ln:
            return ln[:n]
    return ""


def norm_target(home):
    """A lesson's `home:` to a target name: a skill name, or a doc path's basename; NONE is unrouted."""
    words = (home or "").replace("`", " ").split()
    if words and re.fullmatch(r"skills?:?", words[0], re.I):   # "skill foo", "skill: foo"
        words = words[1:]
    h = re.sub(r"^skills?:", "", words[0], flags=re.I) if words else ""
    if not h or h.upper() == "NONE":
        return None
    if "/" in h:
        parts = [p for p in h.split("/") if p]
        if "skills" in parts and parts.index("skills") + 1 < len(parts):
            return parts[parts.index("skills") + 1]
        return parts[-1]
    return h


def piece(target, kind, ts, path, text):
    return {"target": target, "kind": kind, "ts": ts, "path": path, "text": first_line(text)}


def lesson_pieces(lessons_dir, lo, hi):
    out = []
    for p in sorted(glob.glob(os.path.join(lessons_dir, "*.md"))):
        t, _seat = lessons.parse_name(p)
        if t is None or not lo <= t < hi:
            continue
        try:
            body = open(p, encoding="utf-8").read()
        except OSError:
            continue
        out.append(piece(norm_target(lessons.home_of(p)), "lesson", t, p, body))
    return out


def relentless_pieces(store, lo, hi):
    out = []
    for p in glob.glob(os.path.join(store, "items", "*", "attempts.jsonl")):
        item = os.path.basename(os.path.dirname(p))
        for ln in open(p, encoding="utf-8", errors="replace"):
            try:
                r = json.loads(ln)
            except ValueError:
                continue
            t = epoch(r.get("at"))
            if t is None or not lo <= t < hi or not r.get("end") or r.get("end") in OK_ENDS:
                continue
            out.append(piece("relentless", "reject:%s" % r.get("end"), t, p,
                             "%s: %s" % (item, r.get("detail") or r.get("why") or r.get("end"))))
    for p in glob.glob(os.path.join(store, "items", "*", "learned.md")):
        item = os.path.basename(os.path.dirname(p))
        for ln in open(p, encoding="utf-8", errors="replace"):
            m = LEARNED.match(ln.rstrip("\n"))
            t = epoch(m.group(1)) if m else None
            if t is not None and lo <= t < hi:
                out.append(piece("relentless", "learned", t, p, "%s: %s" % (item, m.group(2))))
    j = os.path.join(store, "journal.jsonl")
    if os.path.exists(j):
        for ln in open(j, encoding="utf-8", errors="replace"):
            if '"alarm"' not in ln:
                continue
            try:
                r = json.loads(ln)
            except ValueError:
                continue
            t = epoch(r.get("at"))
            if r.get("do") == "alarm" and t is not None and lo <= t < hi:
                out.append(piece("relentless", "alarm:%s" % r.get("kind"), t, j, r.get("why") or r.get("kind")))
    return out


def ops_pieces(alarms_path, lo, hi):
    try:
        d = json.load(open(alarms_path, encoding="utf-8"))
    except (OSError, ValueError):
        return []
    rows = d.values() if isinstance(d, dict) else d
    out = []
    for r in rows:
        if not isinstance(r, dict):
            continue
        t = epoch(r.get("since") or r.get("filed"))
        if t is not None and lo <= t < hi:
            out.append(piece("operations", "alarm", t, alarms_path, "%s: %s" % (r.get("name"), r.get("title"))))
    return out


def owner_pieces(owner_shard, lo, hi):
    out = []
    if not os.path.exists(owner_shard):
        return out
    for ln in open(owner_shard, encoding="utf-8", errors="replace"):
        if '"ownerSaid"' not in ln:
            continue
        try:
            r = json.loads(ln)
        except ValueError:
            continue
        t = epoch(r.get("ts"))
        if t is not None and lo <= t < hi and r.get("ownerSaid"):
            out.append(piece(None, "owner_said", t, owner_shard, "%s: %s" % (r.get("id") or "-", r["ownerSaid"])))
    return out


def collect(lo, hi, src):
    return (lesson_pieces(src["lessons"], lo, hi) + relentless_pieces(src["store"], lo, hi)
            + ops_pieces(src["ops_alarms"], lo, hi) + owner_pieces(src["owner"], lo, hi))


def target_entry(t, window_count, ps):
    """Every kind counted; the pieces kept are the newest MAX_PIECES, spread over kinds (one of each kind first)."""
    kinds = {}
    for p in ps:
        kinds[p["kind"]] = kinds.get(p["kind"], 0) + 1
    newest = sorted(ps, key=lambda p: -p["ts"])
    keep, seen = [], set()
    for p in newest:
        if p["kind"] not in seen and len(keep) < MAX_PIECES:
            keep.append(p)
            seen.add(p["kind"])
    for p in newest:
        if len(keep) >= MAX_PIECES:
            break
        if p not in keep:
            keep.append(p)
    return {"target": t, "window_count": window_count, "today": len(ps), "kinds": kinds,
            "pieces": sorted(keep, key=lambda p: p["ts"])}


def gather(day, src):
    lo, hi = day_bounds(day)
    today = collect(lo, hi, src)
    window = collect(hi - WINDOW_DAYS * 86400, hi, src)
    counts = {}
    for p in window:
        if p["target"]:
            counts[p["target"]] = counts.get(p["target"], 0) + 1
    by_target = {}
    for p in today:
        if p["target"]:
            by_target.setdefault(p["target"], []).append(p)
    signalled = sorted((t for t in by_target if counts.get(t, 0) >= RECUR),
                       key=lambda t: (t not in AGENTS, -counts[t], -len(by_target[t]), t))
    kept = signalled[:MAX_TARGETS]
    return {
        "day": day, "window_days": WINDOW_DAYS, "recur": RECUR, "max_targets": MAX_TARGETS,
        "pieces_today": len(today),
        "targets": [target_entry(t, counts[t], by_target[t]) for t in kept],
        "dropped_over_cap": signalled[MAX_TARGETS:],
        "unsignalled": sorted(t for t in by_target if t not in signalled),
        "unrouted": [p for p in today if not p["target"]],
    }


def render(pk):
    L = ["# Agent improvement packet %s" % pk["day"], "",
         "%d pieces today; %d signalled targets (>= %d pieces in %d days), cap %d."
         % (pk["pieces_today"], len(pk["targets"]), pk["recur"], pk["window_days"], pk["max_targets"]), ""]
    for t in pk["targets"]:
        L.append("## %s (%d in window, %d today)" % (t["target"], t["window_count"], t["today"]))
        L.append("kinds: " + ", ".join("%s %d" % kv for kv in sorted(t["kinds"].items(), key=lambda kv: -kv[1])))
        if t["today"] > len(t["pieces"]):
            L.append("(showing %d of %d)" % (len(t["pieces"]), t["today"]))
        for p in t["pieces"]:
            L.append("- [%s] %s  (%s)" % (p["kind"], p["text"], p["path"]))
        L.append("")
    if pk["unrouted"]:
        L.append("## unrouted (the Curator routes these or leaves them)")
        L += ["- [%s] %s" % (p["kind"], p["text"]) for p in pk["unrouted"][-MAX_PIECES:]]
        if len(pk["unrouted"]) > MAX_PIECES:
            L.append("(showing the newest %d of %d)" % (MAX_PIECES, len(pk["unrouted"])))
        L.append("")
    L.append("Not signalled today: %s" % (", ".join(pk["unsignalled"]) or "none"))
    if pk["dropped_over_cap"]:
        L.append("Over the cap, left for tomorrow: %s" % ", ".join(pk["dropped_over_cap"]))
    return "\n".join(L) + "\n"


def default_src():
    return {"lessons": os.path.join(REPO, "infrastructure", "state", "lessons"), "store": STORE,
            "ops_alarms": OPS_ALARMS, "owner": os.path.join(REPO, "infrastructure", "state", "ledger", "events",
                                                            "OWNER.jsonl")}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gather")
    g.add_argument("--day", help="UTC day, default yesterday")
    g.add_argument("--out", default=OUT)
    g.add_argument("--dry-run", action="store_true", help="print the packet, write nothing")
    a = ap.parse_args(argv)
    day = a.day or time.strftime("%Y-%m-%d", time.gmtime(time.time() - 86400))
    pk = gather(day, default_src())
    md = render(pk)
    if a.dry_run:
        sys.stdout.write(md)
        return 0
    d = os.path.join(a.out, day)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "packet.json"), "w", encoding="utf-8") as f:
        json.dump(pk, f, indent=1)
    with open(os.path.join(d, "packet.md"), "w", encoding="utf-8") as f:
        f.write(md)
    print("WROTE %s (%d pieces, %d targets)" % (d, pk["pieces_today"], len(pk["targets"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
