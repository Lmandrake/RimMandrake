#!/usr/bin/env python3
"""rimflow/priority_list.py: the one short plan list (DI3, MI1 in design/RimMandrake/operating_requirements_2026-11-01.md).

infrastructure/state/priority_list.json, written by Producer or Conductor through this tool and committed by them:

    {"set_at": "<iso>", "set_by": "Producer", "entries": [
        {"id": "<item>", "reading": {"mod": "Abyss"}},
        {"row": "<V1 row>", "reading": {"file": "infrastructure/state/x.json", "key": "a.b"}}]}

Only the Dispatcher's ring (`rimflow next`) and relentless's pool order by it. A listed item goes ahead of everything
else on those two paths, raised items included; an item `rimflow raise` puts up that is not listed keeps its place
behind the list and ahead of the rest. A list that is missing, torn or too long gives no order, so both paths keep
today's; ops_watch's `plan` family reads that as distressed. Age and advance limits are the ranges block of
Utils/ops_watch_rules.json (plan.list_age_h, plan.days_since_advance), never here.

    python3 src/RimMandrake/rimflow/priority_list.py show
    python3 src/RimMandrake/rimflow/priority_list.py set --file <entries.json> --by Producer|Conductor
    python3 src/RimMandrake/rimflow/priority_list.py add <ID> --mod <Mod> --by Producer|Conductor
"""
import argparse
import datetime
import json
import math
import os
import sys

RELPATH = os.path.join("infrastructure", "state", "priority_list.json")
MAX_ENTRIES = 29        # "under 30 entries"
WRITERS = ("Producer", "Conductor")
FUTURE_SLACK_S = 300


def path(root):
    return os.environ.get("RM_PRIORITY_LIST") or os.path.join(str(root), RELPATH)


def epoch(s):
    try:
        return datetime.datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def reading_problem(spec):
    """-> what is wrong with one entry's finish-line reading, or None. A file reading stays inside the repo."""
    if not isinstance(spec, dict):
        return "names no finish-line reading"
    if isinstance(spec.get("mod"), str) and spec["mod"].strip() and len(spec) == 1:
        return None
    f, k = spec.get("file"), spec.get("key")
    if len(spec) != 2 or not isinstance(f, str) or not f or not isinstance(k, str) or not k:
        return "reading is {mod} or {file, key}"
    if os.path.isabs(f) or ".." in f.replace("\\", "/").split("/"):
        return "reading file %s is outside the repo" % f
    return None


def entry_key(e):
    return "row:%s" % e["row"] if "row" in e else e["id"]


def problem(doc):
    """-> ("over_limit"|"invalid", why) for a list no one may obey, else None."""
    if not isinstance(doc, dict) or not isinstance(doc.get("entries"), list):
        return "invalid", "not an object with entries"
    es = doc["entries"]
    if len(es) > MAX_ENTRIES:
        return "over_limit", "%d entries, the list holds %d" % (len(es), MAX_ENTRIES)
    if doc.get("set_by") not in WRITERS:
        return "invalid", "set_by is %r, not one of %s" % (doc.get("set_by"), "/".join(WRITERS))
    if epoch(doc.get("set_at")) is None:
        return "invalid", "set_at is not a time"
    seen = set()
    for i, e in enumerate(es):
        names = [k for k in ("id", "row") if isinstance(e, dict) and k in e]
        if len(names) != 1 or set(e) != {names[0], "reading"} or not isinstance(e[names[0]], str) or not e[names[0]]:
            return "invalid", "entry %d is not one id or one row, as text, with a reading" % i
        k = entry_key(e)
        if k in seen:
            return "invalid", "%s is listed twice" % k
        seen.add(k)
        bad = reading_problem(e.get("reading"))
        if bad:
            return "invalid", "%s: %s" % (k, bad)
    return None


def load(root):
    """-> {"state": ok|missing|torn|over_limit|invalid, "why", "doc", "entries"}. `entries` is [] unless ok."""
    p = path(root)
    try:
        with open(p, encoding="utf-8") as f:
            doc = json.load(f)
    except FileNotFoundError:
        return {"state": "missing", "why": "%s does not exist" % p, "doc": None, "entries": []}
    except (OSError, ValueError) as e:
        return {"state": "torn", "why": "%s: %s" % (p, str(e)[:160]), "doc": None, "entries": []}
    bad = problem(doc)
    if bad:
        return {"state": bad[0], "why": bad[1], "doc": doc, "entries": []}
    return {"state": "ok", "why": "", "doc": doc, "entries": doc["entries"]}


def order_map(entries):
    """-> {("id"|"row", name): position}, what `position` reads. Hashable keys, so a ctx can carry it."""
    return {("row", str(e["row"])) if "row" in e else ("id", e["id"]): n for n, e in enumerate(entries)}


def position(item, orders):
    """Sort key: an item's place on the list, its own id before its row; past every entry when it is not listed."""
    if orders:
        for k in (("id", item.id), ("row", str(getattr(item, "row", None)))):
            if k in orders:
                return orders[k]
    return MAX_ENTRIES + 1


def open_items(entry, world, open_states):
    """-> the open items an entry stands for. An id or row with none left is a closed entry."""
    if "id" in entry:
        it = world.items.get(entry["id"])
        return [it] if it is not None and it.state in open_states else []
    return [i for i in world.items.values() if str(i.row) == str(entry["row"]) and i.state in open_states]


def closed_entries(entries, world, open_states):
    return [entry_key(e) for e in entries if not open_items(e, world, open_states)]


def read_key(doc, dotted):
    for part in dotted.split("."):
        if not isinstance(doc, dict) or part not in doc:
            return None
        doc = doc[part]
    return doc


def read_reading(spec, root, status_rank):
    """-> (number, None) or (None, why): one entry's finish-line reading, now. `status_rank` turns a mod's modcheck
    status into a number. Never a guess: an unknown status or non-number is a reading not seen."""
    mod = spec.get("mod")
    rel = os.path.join("infrastructure", "state", "modcheck_status.json") if mod else spec["file"]
    try:
        with open(os.path.join(str(root), rel), encoding="utf-8") as f:
            doc = json.load(f)
    except (OSError, ValueError) as e:
        return None, "%s: %s" % (rel, str(e)[:120])
    if mod:
        v = read_key({"m": doc.get(mod) if isinstance(doc, dict) else None}, "m.status")
        return (status_rank[v], None) if isinstance(v, str) and v in status_rank else (None, "%s status %r has no rank" % (mod, v))
    v = read_key(doc, spec["key"])
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
        return None, "%s %s is %r, not a number" % (rel, spec["key"], v)
    return v, None


def advance(entries, root, status_rank, kept, now):
    """One pass of MI1. `kept`: {entry key: {"spec", "best", "rose_t"}} from the last pass.
    -> (new kept, {key: days since its reading last rose}, {key: why unread}). A fall then a return to the old best is
    no rise. A changed reading is a new finish line and starts its own count. A torn record is reported, never reset:
    that would start the clock of an entry already flat."""
    out, days, unread = {}, {}, {}
    for e in entries:
        k = entry_key(e)
        old = kept.get(k) if isinstance(kept.get(k), dict) and kept[k].get("spec") == e["reading"] else None
        v, why = read_reading(e["reading"], root, status_rank)
        if why:
            unread[k] = why
            if old:
                out[k] = old
            continue
        if old is not None and not all(isinstance(old.get(f), (int, float)) and not isinstance(old.get(f), bool)
                                       and math.isfinite(old[f]) for f in ("best", "rose_t")):
            unread[k] = "its advance record is torn: mend or remove it in plan_advance.json"
            out[k] = old
            continue
        if old is None or v > old["best"]:
            out[k] = {"spec": e["reading"], "best": v, "rose_t": now}
        else:
            out[k] = old
        days[k] = round(max(now - out[k]["rose_t"], 0) / 86400.0, 2)
    return out, days, unread


def write(root, entries, by, now=None):
    """The one writer: refuses what `problem` refuses, stamps set_at, replaces atomically. -> the doc."""
    now = now or datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    doc = {"set_at": now, "set_by": by, "entries": entries}
    bad = problem(doc)
    if bad:
        raise ValueError("REFUSED, %s: %s" % bad)
    p = path(root)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")
    os.replace(tmp, p)
    return doc


def main(argv=None):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from rimflow import model
    ap = argparse.ArgumentParser(description="the one short plan list (DI3, MI1)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("show")
    s = sub.add_parser("set")
    s.add_argument("--file", required=True, help="JSON: the entries, in order")
    s.add_argument("--by", required=True, choices=WRITERS)
    a = sub.add_parser("add")
    a.add_argument("id")
    a.add_argument("--mod", required=True, help="the mod whose modcheck status is this entry's finish line")
    a.add_argument("--by", required=True, choices=WRITERS)
    args = ap.parse_args(argv)
    root = model.ROOT
    cur = load(root)
    if args.cmd == "show":
        print(json.dumps(cur, indent=1) if cur["state"] == "ok" else "%s: %s" % (cur["state"], cur["why"]))
        return 0 if cur["state"] == "ok" else 1
    if args.cmd == "set":
        with open(args.file, encoding="utf-8") as f:
            entries = json.load(f)
    elif cur["state"] not in ("ok", "missing"):
        print("REFUSED: the list on disk is %s (%s); `set` a whole one" % (cur["state"], cur["why"]), file=sys.stderr)
        return 1
    else:
        entries = cur["entries"] + [{"id": args.id, "reading": {"mod": args.mod}}]
    if not isinstance(entries, list):
        print("REFUSED: the entries are not a list", file=sys.stderr)
        return 1
    world = model.replay(model.read())
    try:
        dead = closed_entries([e for e in entries if isinstance(e, dict) and (e.get("id") or e.get("row"))], world, model.OPEN_STATES)
        if dead:
            raise ValueError("REFUSED, closed or unknown: %s" % ", ".join(dead))
        doc = write(root, entries, args.by)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 1
    print("%s: %d entries, set_at %s; commit it by path" % (path(root), len(doc["entries"]), doc["set_at"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
