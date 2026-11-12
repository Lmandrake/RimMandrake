#!/usr/bin/env python3
"""refusal_contract.py - the refusal contract for judges and gates (spec
design/specs/2026-11-12-refusal-contract-for-judges-and-gates.md; item RIMMANDRAKE_BIND_REFUSALS_TO_FIXES_NO_CEREMONY_LOOPS).

A refusal that names no way to pass, or that repeats on the same evidence, is a loop that spends and fixes nothing: the
ExplosiveKnockback coverage judge said not_covered nine times in three hours (~90M tokens against a 4M cap), with 15 of its
50 gap ids first named after round 1. This module holds the contract's one alarm:

  REFUSAL_NOTHING_COULD_EVER_PASS   one fixed id, routed to the Conductor (alarm_routes.json). One row per subject (an
                                    item, a concept, a judge family) in alarms.json; a repeat trip updates that row and
                                    tells nobody again; a release closes it, and the next trip after a release tells again.
                                    Never a new queue item per trip.

    python3 src/RimMandrake/rimflow/refusal_contract.py alarms          the open alarm rows, one line each

The rows live in RM_REFUSAL_DIR, default /mnt/d/ClaudeWork/rimmandrake/refusal_contract (a program reads them: scratch,
not the repo). The told row goes through incident.signal when dispatcher_schedule.json has the incident ledger on.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

ALARM_ID = "REFUSAL_NOTHING_COULD_EVER_PASS"
REAL_DIR = "/mnt/d/ClaudeWork/rimmandrake/refusal_contract"
SCHEDULE = os.path.join(HERE, "dispatcher_schedule.json")


def state_dir():
    return os.environ.get("RM_REFUSAL_DIR") or REAL_DIR


def alarms_path():
    return os.path.join(state_dir(), "alarms.json")


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def _read(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return {}
    if not isinstance(data, dict):
        raise ValueError("%s is not a JSON object" % path)
    return data


def _write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = "%s.tmp.%d" % (path, os.getpid())
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, sort_keys=True, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, path)


def _told(why, now):
    """-> None when told (or the incident ledger is off), else why the told row could not be written."""
    try:
        import incident
        with open(SCHEDULE, encoding="utf-8") as f:
            sch = json.load(f)
        incident.signal(sch, ALARM_ID, why, now)
        return None
    except Exception as e:  # noqa: BLE001 - the row on disk stands; the failure to tell is written into it
        return "%s: %s" % (type(e).__name__, str(e)[:200])


def alarm(subject, why, now=None, family=None, detail=None):
    """Raise or update the one alarm for `subject`. -> the row. The first trip of an open row tells the Conductor;
    a repeat only updates trips, last_at and why."""
    now = time.time() if now is None else now
    path = alarms_path()
    rows = _read(path)
    row = rows.get(subject)
    fresh = not (isinstance(row, dict) and row.get("open"))
    if fresh:
        row = {"id": ALARM_ID, "subject": subject, "first_at": iso(now), "trips": 0, "open": True}
    row.update(last_at=iso(now), why=str(why), trips=int(row.get("trips") or 0) + 1)
    if family:
        row["family"] = family
    if detail is not None:
        row["detail"] = detail
    if fresh:
        err = _told("%s: %s" % (subject, why), now)
        row["told_at"] = iso(now)
        if err:
            row["told_error"] = err
        else:
            row.pop("told_error", None)
    rows[subject] = row
    _write(path, rows)
    return row


def clear(subject, why, now=None):
    """A release: the row closes (kept, with its history), so the next trip tells again. -> the row or None."""
    now = time.time() if now is None else now
    path = alarms_path()
    rows = _read(path)
    row = rows.get(subject)
    if not isinstance(row, dict):
        return None
    row.update(open=False)
    row.setdefault("releases", []).append({"at": iso(now), "why": str(why)})
    rows[subject] = row
    _write(path, rows)
    return row


def open_alarms():
    return [r for r in _read(alarms_path()).values() if isinstance(r, dict) and r.get("open")]


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] != ["alarms"]:
        print(__doc__)
        return 2
    rows = open_alarms()
    for r in rows:
        print("%s %s trips=%d since %s: %s" % (r["id"], r["subject"], r.get("trips", 0), r.get("first_at"), r.get("why")))
    print("%d open" % len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
