#!/usr/bin/env python3
"""The Dispatcher's helper budget (HELPER_BUDGET_MIGRATE_INTO_DISPATCHER).

v3 has no BENCH seat (design/RimMandrake/rimflow_v3_2026-10-26.md §2-3): the Dispatcher, a program, enforces budgets
mechanically. Every tick it computes the per-seat helper budget with slot_allocator (the computing library: the
measured pace, his word, the payback, the brakes; its rules in src/RimMandrake/Utils/slot_rules.json, split.rule "v3")
and publishes it as `<dispatcher state>/helper_budget.json` under the v3 seat names:

  FOUNDRY    the machine's whole helper budget (the pace fit), less any payback owed;
  CONDUCTOR  helpers only while the owner is in its window (session-only), unless his word (slot_override.json) says
             otherwise; every Conductor helper-hour is owed and paid back from FOUNDRY after he leaves.

The spawn hook (.claude/hooks/block_agent_over_slots.py) reads this file first. It computes for itself only when the
file is missing, older than MAX_AGE_S, or older than his last word (slot_override.json), so a new word acts at once.
compute() is pure reading (about 0.2 s); the allocator's stateful record (allocation.json: overage, sitting) stays
with its own 15-min writer, so two writers never advance that state.

Role runs (rm-role-* units) are counted as the seat they run as (AGENT_SEAT) and keep their token caps.

    python3 src/RimMandrake/rimflow/helper_budget.py show      # what the Dispatcher last published
    python3 src/RimMandrake/rimflow/helper_budget.py now       # compute now, print, publish nothing
"""
import json
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.abspath(os.path.join(HERE, "..", "Utils"))
FILE = "helper_budget.json"
MAX_AGE_S = 600          # the Dispatcher ticks every 120 s: five missed ticks and the hook stops trusting the file
FUTURE_SLACK_S = 5       # same machine, same clock: only jitter; a budget from the future would hide a newer word
ALIASES = {"BENCH": "CONDUCTOR"}   # the window v2 called BENCH is the Conductor's (AGENT_SEAT=BENCH still)


def _sa():
    if UTILS not in sys.path:
        sys.path.insert(0, UTILS)
    import slot_allocator
    return slot_allocator


def state_root():
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    import doorbell
    return doorbell.state_dir()


def budget_seat(seat):
    s = str(seat or "").strip().upper()
    return ALIASES.get(s, s)


def compute(now, sa=None):
    sa = sa or _sa()
    rules = sa.load_rules()
    dec = sa.compute(now, rules)
    seats = {}
    for k, v in (dec.get("seats") or {}).items():
        seats[budget_seat(sa.seat_label(k))] = int(v)
    return {"t": now, "at": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(now)), "by": "dispatcher",
            "seats": seats, "mode": dec.get("mode"), "presence": dec.get("presence"), "why": dec.get("why", ""),
            "override": dec.get("override")}


def _write_atomic(path, text):
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=FILE + ".", suffix=".tmp", dir=d)
    try:
        with os.fdopen(fd, "w") as f:
            f.write(text)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def publish(root, now, sa=None):
    rec = compute(now, sa)
    _write_atomic(os.path.join(root, FILE), json.dumps(rec, indent=1, sort_keys=True, default=str))
    return rec


def _count(v):
    return isinstance(v, int) and not isinstance(v, bool) and v >= 0


def read(root=None, now=None, max_age_s=MAX_AGE_S, sa=None):
    """The published budget if it can be trusted now, else None (the caller computes or falls back). Never raises."""
    try:
        now = time.time() if now is None else now
        root = root or state_root()
        with open(os.path.join(root, FILE)) as f:
            rec = json.load(f)
        t = float(rec.get("t"))
        if not (now - max_age_s <= t <= now + FUTURE_SLACK_S):
            return None
        seats = rec.get("seats")
        if not isinstance(seats, dict) or not seats or not all(_count(v) for v in seats.values()):
            return None
        sa = sa or _sa()
        try:
            ov_m = os.path.getmtime(os.path.join(str(sa.streams_dir()), "slot_override.json"))
        except OSError:
            ov_m = 0
        if ov_m > t:
            return None        # his word is newer than the budget: it must act now, not at the next tick
        return rec
    except Exception:  # noqa: BLE001
        return None


def tick_step(sch, st, root, now, sa=None, journal=None):
    """One Dispatcher tick's budget step. Returns None, or the alarm record (journalled once per alarm_every_s).
    Opt-in: only a schedule with helper_budget.enabled true publishes (the live dispatcher_schedule.json does), so a
    fixture schedule in a selftest never computes over the real transcripts."""
    if (sch.get("helper_budget") or {}).get("enabled") is not True:
        return None
    alarms = st.setdefault("alarms", {})
    key = "budget:failed"
    try:
        publish(root, now, sa)
    except Exception as e:  # noqa: BLE001  a budget failure must never stop a tick: the hook falls back on its own
        rec = {"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)), "do": "alarm", "kind": key,
               "why": "helper budget not published (%s: %s); the spawn hook computes for itself"
                      % (type(e).__name__, str(e)[:200])}
        if now - alarms.get(key, -1e18) >= sch.get("alarm_every_s", 6 * 3600):
            alarms[key] = now
            if journal:
                try:
                    journal(rec)
                except Exception:  # noqa: BLE001  the disk that failed the budget may fail the journal too
                    pass
        return rec
    alarms.pop(key, None)
    return None


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    cmd = argv[0] if argv else "show"
    if cmd == "now":
        print(json.dumps(compute(time.time()), indent=1, sort_keys=True, default=str))
        return 0
    if cmd == "show":
        p = os.path.join(state_root(), FILE)
        try:
            rec = json.load(open(p))
        except (OSError, ValueError) as e:
            print("no budget published at %s (%s)" % (p, e))
            return 1
        trusted = read() is not None
        print("%s seats %s mode %s (%s)\n%s" % (rec.get("at"), rec.get("seats"), rec.get("mode"),
                                               "fresh: the hook uses it" if trusted else "NOT trusted by the hook now",
                                               rec.get("why")))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
