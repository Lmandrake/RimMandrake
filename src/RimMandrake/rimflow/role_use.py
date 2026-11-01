#!/usr/bin/env python3
"""role_use: RO1 of operating_requirements_2026-11-01.md, does anybody use what a role makes? Report-only.

Per role and per week, read from the ledger: its outputs (items, raises, notes, verdicts) with a later action on the same
item, over its outputs, plus its runs and silent_days. It is coarse on purpose and it is never a target: ops_watch shows
it, the Conductor names a fix after two weeks under range, and nothing gates on it (`ops_watch.py lint` refuses a roles.*
range that could alarm, and a target on one). Do not import this from anything that decides.

Roles work under a seat's name, so a role is recognised by the words it leaves: rules["roles"] in ops_watch_rules.json.
  outputs   a file, raise or note event whose why/text/reason matches the role's `marked`, and not `not_output`
  acted     an event of `action_events` on that item, later in the ledger, not carrying the role's own mark. Notes,
            raises, leases and reassigns do not count: they move no work.
  coarse    the design's own first reading: a file event whose why matches `coarse`. It also catches any item whose why
            merely opens with the word ("audit of 24 rows"), so it is reported, and acted_share does not use it.
  runs      distinct rm-role-<role>-<n> units named in the window, plus one for each day of output naming no unit (a
            run that wrote prose only). silent_days: window days with no run and no output.
  A role with no output has no share: UNMEASURED by the caller, never 0.

    python3 src/RimMandrake/rimflow/role_use.py read [--since ISO --until ISO] [--root CLONE] [--json]
"""
import argparse
import calendar
import json
import re
import sys
import time
from pathlib import Path

DAY = 86400.0
HERE = Path(__file__).resolve().parent
RULES = HERE.parent / "Utils" / "ops_watch_rules.json"
TEXTS = ("why", "text", "reason")


def epoch(s):
    try:
        return float(calendar.timegm(time.strptime(str(s)[:19], "%Y-%m-%dT%H:%M:%S")))
    except (ValueError, TypeError):
        return None


def said(ev):
    return " ".join(str(ev[k]) for k in TEXTS if ev.get(k))


def compile_role(role):
    return {k: re.compile(role[k]) for k in ("marked", "coarse", "not_output")}


def is_mine(ev, rx):
    return any(rx["marked"].search(str(ev.get(k) or "")) for k in TEXTS) and not rx["not_output"].search(said(ev))


def read_role(name, role, events, since, until, actions, outputs_of=("file", "raise", "note")):
    """-> one role's reading over events in canonical order. Only events up to `until` exist for it, so a reading of a
    past date stays the same however the ledger grows."""
    rx, unit = compile_role(role), re.compile(r"rm-role-%s-(\d+)" % re.escape(name.lower()))
    timed = [(i, e, epoch(e.get("ts"))) for i, e in enumerate(events)]
    timed = [x for x in timed if x[2] is not None and x[2] <= until]
    acted_at = {}
    for i, e, _ in timed:
        if e.get("event") in actions and e.get("id"):
            acted_at.setdefault(e["id"], []).append((i, e))

    def acted(i, ev):
        return any(j > i and not rx["marked"].search(said(a)) for j, a in acted_at.get(ev.get("id"), ()))

    out = {"role": name, "outputs": 0, "acted": 0, "items": 0, "untouched": [], "items_coarse": 0, "untouched_coarse": []}
    runs, days, run_days = set(), set(), set()
    for i, e, t in timed:
        if t < since:
            continue
        for u in unit.findall(said(e)):
            runs.add(u)
            run_days.add(int((t - since) // DAY))
        if e.get("event") == "file" and rx["coarse"].search(str(e.get("why") or "")):
            out["items_coarse"] += 1
            if not acted(i, e):
                out["untouched_coarse"].append(e["id"])
        if e.get("event") in outputs_of and is_mine(e, rx):
            hit = acted(i, e)
            out["outputs"] += 1
            out["acted"] += int(hit)
            days.add(int((t - since) // DAY))
            if e.get("event") == "file":
                out["items"] += 1
                if not hit:
                    out["untouched"].append(e["id"])
    span = max(1, int(round((until - since) / DAY)))
    out.update(runs=len(runs) + len(days - run_days), days=span,
               silent_days=span - len([d for d in days | run_days if 0 <= d < span]),
               acted_share=round(out["acted"] / out["outputs"], 3) if out["outputs"] else None)
    return out


def read(events, cfg, since, until):
    """-> {role: reading}, every role of cfg["roles"]."""
    actions = set(cfg["action_events"])
    return {n: read_role(n, r, events, since, until, actions) for n, r in cfg["roles"].items()}


def weeks_under(share_this, share_last, under):
    """Consecutive weeks under range, newest first, 0 to 2. A week with no share is no week under."""
    return 0 if share_this is None or not under(share_this) else 1 + int(share_last is not None and under(share_last))


def load_ledger(root):
    sys.path.insert(0, str(HERE))
    import model as M   # rimflow's own reader: the frozen history and every seat shard
    events = []
    for f in M.ledger_files(str(Path(root) / "infrastructure/state/ledger/events.jsonl")):
        p = Path(f)
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                try:
                    events.append(json.loads(line))
                except ValueError:
                    continue            # a torn line, as pulse_core reads it
    return M.canonical_order(events)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("read")
    r.add_argument("--since", help="ISO UTC; default 7 days before --until")
    r.add_argument("--until", help="ISO UTC; default now")
    r.add_argument("--root", default=str(HERE.parents[2]), help="the clone whose ledger to read")
    r.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    until = epoch(a.until) if a.until else time.time()
    since = epoch(a.since) if a.since else until - 7 * DAY
    if until is None or since is None:
        ap.error("--since and --until are ISO UTC, 2026-11-01T14:24:59Z")
    cfg = json.loads(RULES.read_text(encoding="utf-8"))["roles"]
    got = read(load_ledger(a.root), cfg, since, until)
    if a.json:
        print(json.dumps(got, indent=1))
        return 0
    for n, g in got.items():
        print("%-10s acted_share %s (%d of %d outputs)  runs %d  silent_days %d of %d  items %d untouched %d  "
              "coarse items %d untouched %d" % (n, g["acted_share"], g["acted"], g["outputs"], g["runs"], g["silent_days"],
                                                g["days"], g["items"], len(g["untouched"]), g["items_coarse"],
                                                len(g["untouched_coarse"])))
        print("  untouched: %s" % (", ".join(g["untouched"]) or "none"))
        print("  untouched coarse: %s" % (", ".join(g["untouched_coarse"]) or "none"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
