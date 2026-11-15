#!/usr/bin/env python3
"""record_check.py — the rerun command of a test table's `kind: record` decider: is the ledger event still there, unchanged?

    python3 src/RimMandrake/rimflow/record_check.py --seat OWNER --tsn <tsn> --id <item> [--said-contains "<his words>"]
        [--sha256 <hex of the event's line>] [--events-dir infrastructure/state/ledger/events]

A record (his approval of a sheet, a card answer) has no behaviour to rerun, so a blind judge's rerun of it used to read
`not_rerunnable` and the exit could never be met (Pyrelands cycle 1, RECORD_ART_SHEET). This makes the record a check:
exactly one line of <SEAT>.jsonl carries that `tsn`, with that seat and item id, holds his words when asked, and its bytes
hash to the pinned sha256 (an edited or re-written event fails). Exit 0 and one `RECORD PASS` line, else exit 1 and one
`RECORD FAIL <why>` line. Read-only."""
import argparse, hashlib, json, os, sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))


def check(events_dir, seat, tsn, item, said=None, sha=None):
    """-> (ok, line). Never raises on a bad ledger: the reason is the line."""
    path = os.path.join(events_dir, "%s.jsonl" % seat)
    try:
        with open(path, "rb") as f:
            raw = f.read().split(b"\n")
    except OSError as e:
        return False, "RECORD FAIL %s unreadable: %s" % (path, e)
    hits = []
    for n, b in enumerate(raw, 1):
        if str(tsn).encode() not in b:
            continue
        try:
            ev = json.loads(b)
        except ValueError:
            continue
        if str(ev.get("tsn")) == str(tsn):
            hits.append((n, b, ev))
    where = "%s.jsonl" % seat
    if len(hits) != 1:
        return False, "RECORD FAIL %d events in %s carry tsn %s (exactly 1 wanted)" % (len(hits), where, tsn)
    n, b, ev = hits[0]
    h = hashlib.sha256(b.rstrip(b"\r")).hexdigest()
    if ev.get("seat") != seat:
        return False, "RECORD FAIL %s:%d seat is %r, not %s" % (where, n, ev.get("seat"), seat)
    if ev.get("id") != item:
        return False, "RECORD FAIL %s:%d id is %r, not %s" % (where, n, ev.get("id"), item)
    if said and said not in (ev.get("ownerSaid") or ""):
        return False, "RECORD FAIL %s:%d ownerSaid does not hold %r" % (where, n, said)
    if sha and h != sha.lower():
        return False, "RECORD FAIL %s:%d sha256 %s, pinned %s (the event changed)" % (where, n, h, sha.lower())
    return True, "RECORD PASS %s:%d tsn=%s id=%s sha256=%s" % (where, n, tsn, item, h)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--seat", required=True)
    ap.add_argument("--tsn", required=True)
    ap.add_argument("--id", required=True)
    ap.add_argument("--said-contains")
    ap.add_argument("--sha256")
    ap.add_argument("--events-dir", default=os.path.join(REPO, "infrastructure", "state", "ledger", "events"))
    a = ap.parse_args(argv)
    good, line = check(a.events_dir, a.seat, a.tsn, a.id, a.said_contains, a.sha256)
    print(line)
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
