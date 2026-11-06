#!/usr/bin/env python3
"""The Dispatcher's helper budget (HELPER_BUDGET_MIGRATE_INTO_DISPATCHER).

v3 has no BENCH seat (design/RimMandrake/rimflow_v3_2026-10-26.md §2-3): the Dispatcher, a program, enforces budgets
mechanically. Every tick it computes the per-seat helper budget with slot_allocator (the computing library: the
measured pace, his word, the payback, the brakes; its rules in src/RimMandrake/Utils/slot_rules.json, split.rule "v3")
and publishes it as `<dispatcher state>/helper_budget.json` under the v3 seat names:

  RELENTLESS the machine's whole helper budget (the pace fit), less any payback owed;
  CONDUCTOR  helpers only while the owner is in its window (session-only), unless his word (slot_override.json) says
             otherwise; every Conductor helper-hour is owed and paid back from RELENTLESS after he leaves.

Owner, 2026-10-29: the interactive Conductor window (AGENT_SEAT BENCH, no RM_ROLE_UNIT) is unlimited only within 20 min
of his last typed message, then two helpers (slot_rules.json conductor_window); the numbers here govern scheduled and
Dispatcher-launched runs and RELENTLESS only (relentless_rules.json staffing.seat reads it;
the key was FOUNDRY until that seat retired, FOUNDRY_LITERALS_EXCISE_FROM_CODE).

The spawn hook (.claude/hooks/block_agent_over_slots.py) reads this file first. It computes for itself only when the
file is missing, older than MAX_AGE_S, or older than his last word (slot_override.json), so a new word acts at once.
compute() is pure reading (about 0.2 s); the allocator's stateful record (allocation.json: overage, sitting) stays
with its own 15-min writer, so two writers never advance that state.

Role runs (rm-role-* units) are counted as the seat they run as (AGENT_SEAT); their token caps are advisory.

Token pacing never lowers the published seats (owner 2026-11-02; slot_rules.json advisory): the paced seats ride
along as `advice`. attention() raised them to the Conductor log and Operations when they would place fewer; it is off
(schedule helper_budget.pacing_attention false) since the owner, 2026-11-04: "all token limits rescinded as well as work
type. Token is no longer constrained." (scoped the same day to the Dispatcher's token pacing; Relentless
per-item spend attention, system-before-content and Steve's 50% stop stay).

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
    rec = {"t": now, "at": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(now)), "by": "dispatcher",
           "seats": seats, "mode": dec.get("mode"), "presence": dec.get("presence"), "why": dec.get("why", ""),
           "override": dec.get("override")}
    adv = dec.get("advice")
    if isinstance(adv, dict):
        # the paced seats token pacing would have placed: advisory since owner 2026-11-02, reported, never applied
        rec["advice"] = dict(adv, paced_seats={budget_seat(sa.seat_label(k)): int(v)
                                               for k, v in (adv.get("paced_seats") or {}).items()},
                             short={budget_seat(sa.seat_label(k)): int(v) for k, v in (adv.get("short") or {}).items()})
    return rec


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


ATTENTION_KIND = "budget:token_pacing"


def _stand(st, key, on, now):
    """What this tick read for one budget alarm key, for incident.standing_of (RELAPSE_HELPERS_FIX_DIED_TWICE): its
    incident stays open while the alarm's cause stands and closes on sustain_min once it is gone. on None: no reader
    (off); on "unknown": this tick could not read it, so it is stale, never quiet."""
    if on is None:
        (st.get("standing") or {}).pop(key, None)
    elif on == "unknown":
        st.setdefault("standing", {})[key] = {"t": None, "keys": [], "unknown_since": now}
    else:
        st.setdefault("standing", {})[key] = {"t": now, "keys": [key] if on else []}


def attention(sch, st, rec, now, journal=None, tell=None):
    """Token pacing is ADVISORY (owner, 2026-11-02: "Please make token limits advisory at this time everywhere. Nothing
    gets killed or stopped for that, but it might call attention from another agent (Conductor, Operations) to
    investigate and THAT agent may determine it needs to be killed for evidence-based reasons."). When the published
    budget's advice says pacing would place fewer helpers than were placed, say so: journalled (the journal callback
    also signals Operations' incident ledger) and one line to the Conductor log via `tell`, once per alarm_every_s
    while it lasts. -> the alarm record when it fired, else None. Off when the schedule's helper_budget.pacing_attention
    is false (owner 2026-11-04: "all token limits rescinded as well as work type. Token is no longer constrained.")."""
    alarms = st.setdefault("alarms", {})
    if (sch.get("helper_budget") or {}).get("pacing_attention", True) is False:
        alarms.pop(ATTENTION_KIND, None)
        _stand(st, ATTENTION_KIND, None, now)
        return None
    adv = (rec or {}).get("advice") or {}
    short = {k: v for k, v in (adv.get("short") or {}).items() if isinstance(v, int) and v > 0}
    _stand(st, ATTENTION_KIND, bool(short), now)
    if not short:
        alarms.pop(ATTENTION_KIND, None)
        return None
    if now - alarms.get(ATTENTION_KIND, -1e18) < sch.get("alarm_every_s", 6 * 3600):
        return None
    alarms[ATTENTION_KIND] = now
    paced = adv.get("paced_seats") or {}
    placed = rec.get("seats") or {}
    out = {"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)), "do": "alarm", "kind": ATTENTION_KIND,
           "advisory": True, "conductor_log": True,
           "why": "token pacing over its advisory line (%s): it would place %s, %d helper(s) fewer than the %s placed; "
                  "nothing was cut (owner 2026-11-02, token limits are advisory). Look: helper_budget.json advice, "
                  "slot_allocator why: %s" % (
                      adv.get("token_mode"),
                      ", ".join("%s %s" % (k, paced.get(k, 0)) for k in sorted(placed)), sum(short.values()),
                      ", ".join("%s %s" % (k, placed[k]) for k in sorted(placed)), str(adv.get("why") or "")[:300]),
           "raise_first": "Token pacing is past its line; nothing stopped. Judge on evidence whether anything should."}
    for f in (journal, tell):
        if f:
            try:
                f(out)
            except Exception:  # noqa: BLE001  an advisory line must never stop a tick
                pass
    return out


def tick_step(sch, st, root, now, sa=None, journal=None, tell=None):
    """One Dispatcher tick's budget step. Returns None, or the alarm record (journalled once per alarm_every_s): a
    publish failure, or the advisory token-pacing attention (see attention()), which `tell` also writes to the
    Conductor log. Opt-in: only a schedule with helper_budget.enabled true publishes (the live
    dispatcher_schedule.json does), so a fixture schedule in a selftest never computes over the real transcripts."""
    if (sch.get("helper_budget") or {}).get("enabled") is not True:
        for k in ("budget:failed", ATTENTION_KIND):
            _stand(st, k, None, now)
        return None
    alarms = st.setdefault("alarms", {})
    key = "budget:failed"
    try:
        pub = publish(root, now, sa)
    except Exception as e:  # noqa: BLE001  a budget failure must never stop a tick: the hook falls back on its own
        _stand(st, key, True, now)
        _stand(st, ATTENTION_KIND, "unknown", now)    # no published advice this tick: the pacing reading is not current
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
    _stand(st, key, False, now)
    return attention(sch, st, pub, now, journal, tell)


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
