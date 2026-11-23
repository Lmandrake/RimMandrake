#!/usr/bin/env python3
"""rimflow/priority_list.py: the Conductor's one short list of what comes first (DI3 in design/RimMandrake/operating_requirements_2026-11-01.md).

infrastructure/state/priority_list.json, written by the Conductor through this tool and committed:

    {"set_at": "<iso>", "set_by": "Conductor", "entries": [
        {"id": "<item>", "reading": {"mod": "Abyss"}},
        {"row": "<V1 row>", "reading": {"file": "infrastructure/state/x.json", "key": "a.b"}}]}

`rimflow next` orders by it. A listed item goes ahead of everything else, raised items included; an item `rimflow
raise` puts up that is not listed keeps its place behind the list and ahead of the rest. A list that is missing, torn
or too long gives no order. A listed item that has closed drops by itself: no reader orders by it and `add` removes it.

    python3 src/RimMandrake/rimflow/priority_list.py show
    python3 src/RimMandrake/rimflow/priority_list.py set --file <entries.json> --by Conductor
    python3 src/RimMandrake/rimflow/priority_list.py add <ID> --mod <Mod> --by Conductor
"""
import argparse
import datetime
import json
import os
import sys

RELPATH = os.path.join("infrastructure", "state", "priority_list.json")
MAX_ENTRIES = 29        # "under 30 entries"
WRITERS = ("Conductor",)
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
        return {"state": "torn", "why": "%s: %s" % (p, str(e)), "doc": None, "entries": []}
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
    ap = argparse.ArgumentParser(description="the one short list of what comes first (DI3)")
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
    if os.environ.get("RIMFLOW_LEDGER"):        # the redirect cli.py's _bind_paths makes, so a selftest reads its own
        model.EVENTS = os.environ["RIMFLOW_LEDGER"]
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
    if args.cmd == "add":
        # RIMMANDRAKE_PRUNE_PRIORITY_LIST_CLOSED_ENTRY_STALLS_PLAN: a finished entry already on the list drops by itself;
        # it once refused the whole add until somebody wrote a full `set`
        gone = closed_entries(cur["entries"], world, model.OPEN_STATES)
        if gone:
            entries = [e for e in entries if entry_key(e) not in gone]
            print("dropped closed: %s" % ", ".join(gone))
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
