#!/usr/bin/env python3
"""The owner's rulings, DATED, read from disk — never from a compaction summary.

A compaction summary keeps his words verbatim but almost never their date (10 of 316 quotes,
design/RimMandrake/compaction_retention_test_2026-10-26.md), so a resumed seat stamps an old
ruling with today's date. The ledger already holds the date: every `--owner-said` / `--by-card`
event lands in infrastructure/state/ledger/events/OWNER.jsonl with its `ts`. This prints them.

    python3 src/RimMandrake/rimflow/owner_rulings.py                  # last 40, oldest first
    python3 src/RimMandrake/rimflow/owner_rulings.py --grep kelp      # regex over words + item
    python3 src/RimMandrake/rimflow/owner_rulings.py --item SOME_ID --since 2026-10-20 --last 0

Line shape:  2026-10-24 19:08Z  said  ITEM_ID  "his words"   (`card` = a decision by card)
The date is when the words were RECORDED on the ledger; an agent relaying older words records
them late, so the date is never later than the truth but may be later than the saying.
Identical words on several events print once, at their FIRST date.
"""
import argparse
import glob
import json
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
EVENTS = os.path.join(REPO, "infrastructure", "state", "ledger", "events")
KINDS = (("ownerSaid", "said"), ("byCard", "card"))


def norm(text):
    return re.sub(r"\s+", " ", text).strip()


def rulings(events_dir=EVENTS):
    """Every dated owner ruling across all shards, first date per distinct words, oldest first."""
    seen = {}
    for path in sorted(glob.glob(os.path.join(events_dir, "*.jsonl"))):
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                ts = e.get("ts") or ""
                if not re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", ts):
                    continue  # an undated ruling is exactly what this tool exists to refuse
                for field, kind in KINDS:
                    words = e.get(field)
                    if not isinstance(words, str) or not norm(words):
                        continue
                    key = (kind, norm(words))
                    row = {"ts": ts, "kind": kind, "id": e.get("id") or e.get("event") or "-",
                           "words": norm(words)}
                    if key not in seen or ts < seen[key]["ts"]:
                        seen[key] = row
    return sorted(seen.values(), key=lambda r: (r["ts"], r["id"]))


def fmt(r):
    return f'{r["ts"][:10]} {r["ts"][11:16]}Z  {r["kind"]}  {r["id"]}  "{r["words"]}"'


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--grep", help="regex (case-insensitive) over the words and the item id")
    ap.add_argument("--item", help="only this item id")
    ap.add_argument("--since", help="YYYY-MM-DD: only rulings recorded on or after")
    ap.add_argument("--kind", choices=("said", "card"))
    ap.add_argument("--last", type=int, default=40, help="newest N (0 = all); default 40")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--events", default=EVENTS, help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    if not os.path.isdir(a.events):
        print(f"owner_rulings: no ledger shards at {a.events}", file=sys.stderr)
        return 2
    rows = rulings(a.events)
    if a.item:
        rows = [r for r in rows if r["id"] == a.item]
    if a.kind:
        rows = [r for r in rows if r["kind"] == a.kind]
    if a.since:
        rows = [r for r in rows if r["ts"][:10] >= a.since]
    if a.grep:
        rx = re.compile(a.grep, re.I)
        rows = [r for r in rows if rx.search(r["words"]) or rx.search(r["id"])]
    if a.last:
        rows = rows[-a.last:]
    for r in rows:
        print(json.dumps(r) if a.json else fmt(r))
    if not rows:
        print("owner_rulings: 0 rulings match (measured over the ledger shards)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
