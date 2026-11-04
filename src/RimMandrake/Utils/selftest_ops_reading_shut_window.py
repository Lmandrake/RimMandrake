#!/usr/bin/env python3
"""OPS_READING_FIX_SHUT_WINDOW_IS_FULL: the Dispatcher's ops reading (role_launch.ops_reading over ops_watch's
accounts.* points) must be MEASURED, so no role:<name>:ops alarm, when the account_usage record shows a MEASURED week
and no open 5-hour window, and when the weekly reset passed after the last poll. The live instance (2026-11-04
20:20:23Z, 21 min after the system account's reset at 11:59 PST) read accounts.system.runway UNMEASURED, its why
echoing the record's unrelated 'no session window' note. Real account_usage.record/derive_record, real
ops_watch.c_accounts and real role_launch.ops_reading; only the readers they call for live state are faked."""
import os
import sys
import tempfile
import time
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "rimflow"))
TMP = Path(tempfile.mkdtemp(prefix="selftest_ops_reading_shut_window_"))
os.environ["RM_OPS_WATCH_DIR"] = str(TMP / "ops")
os.environ["RM_DATA_ROOT"] = str(TMP / "data")
import account_usage as AU  # noqa: E402
import ops_watch as OW  # noqa: E402
import role_launch as RL  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  %s" % (detail,)))
    if not cond:
        FAILS.append(name)


def ts(s):
    return OW.epoch(s)


RESET = "2026-11-04T11:59-08:00"                       # the system account's weekly reset that day
READ = ts("2026-11-04T11:56:10-08:00")                 # the last poll before it (series.jsonl: 100% used)
NOW = ts("2026-11-04T12:20:23-08:00")                  # the launch that raised role:Operations:ops


def rec(name, read_at, used, resets, src="MEASURED", session=None):
    return AU.record(name, read_at, src, "plan usage endpoint", "m",
                     {"week_pct_used": used, "week_resets_at": resets, "session_pct_used": session}, AU.iso(read_at))


def accounts(rows, lent=None):
    """c_accounts over these records, read as read_now would at NOW; a fake slope and registry."""
    saved = {m: sys.modules.get(m) for m in ("account_usage", "slot_allocator")}
    sys.modules["account_usage"] = types.SimpleNamespace(
        read_now=lambda now: {"accounts": {n: AU.derive_record(r, now) for n, r in rows.items()}},
        live_email=lambda: "s@x", registry=lambda: {"system": "s@x"})
    sys.modules["slot_allocator"] = types.SimpleNamespace(
        slope=lambda *a: (None, 0, 0.0), load_rules=lambda: {"lent_accounts": lent or {}},
        lent_allowance=lambda r, rules, now: (30.0, "open loan"))
    try:
        return OW.c_accounts(NOW, OW.load_rules(), {})
    finally:
        for m, v in saved.items():
            if v is None:
                sys.modules.pop(m, None)
            else:
                sys.modules[m] = v


def reading(pts, account="system"):
    return RL.ops_reading({"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(NOW)), "points": pts}, account, NOW)


# --- the live instance: the week reset after the last poll -----------------------------------------------------------
gap = rec("system", READ, 100.0, RESET)
check("fixture: the record carries the 'no session window' note and a MEASURED week",
      gap["source"] == "MEASURED" and "no session window" in gap["why"], gap)
check("fixture: read_now blanks the passed week (the gap the alarm fell into)",
      AU.derive_record(gap, NOW)["week_pct_left"] is None)
pts = accounts({"system": gap})
r = reading(pts)
check("reset gap: the ops reading is MEASURED (no role:<name>:ops alarm at role_launch's degraded branch)",
      r["state"] == "MEASURED", r)
check("reset gap: runway is the full cap, an ESTIMATE naming the reset",
      pts["accounts.system.runway"]["m"] == "ESTIMATE" and pts["accounts.system.runway"]["v"] == 10.0
      and "reset" in pts["accounts.system.runway"]["why"], pts["accounts.system.runway"])
check("reset gap: 100% of the week left, an upper bound", pts["accounts.system.week_left_pct"]["v"] == 100.0
      and pts["accounts.system.week_left_pct"]["m"] == "ESTIMATE", pts["accounts.system.week_left_pct"])
h = pts["accounts.system.hours_to_reset"]["v"]
check("reset gap: the next reset is one week after the passed one", h is not None and abs(h - (168 - 21.4 / 60)) < 0.1, h)
check("reset gap: the band is GREEN, not the cautious RED a degraded launch gets",
      RL.band({"throttle_bands": {"GREEN": {"runway_ge": 1.5}, "RED": {"runway_ge": 0.0}}}, r)[0] == "GREEN", r)

# --- the item's own words: week MEASURED, five_hour null --------------------------------------------------------------
shut = rec("system", NOW - 600, 3.0, "2026-11-11T11:59-08:00")
pts = accounts({"system": shut})
r = reading(pts)
check("no open 5-hour window, MEASURED week: the ops reading is MEASURED", r["state"] == "MEASURED", r)
check("no open 5-hour window: week left is MEASURED 97", r.get("week_left") == 97.0 and r.get("week_left_m") == "MEASURED", r)

# --- what must still read UNMEASURED ------------------------------------------------------------------------------------
pts = accounts({"system": rec("system", NOW - 600, None, None, src="UNMEASURED")})
check("an UNMEASURED week still reads UNMEASURED", reading(pts)["state"] == "UNMEASURED", pts)
old = rec("system", NOW - 9 * 86400, 40.0, AU.iso(NOW - 8 * 86400))
pts = accounts({"system": old})
check("a record whose reset passed over a week ago is not called a fresh week",
      pts["accounts.system.runway"]["m"] == "UNMEASURED", pts["accounts.system.runway"])
check("...and its why names the missing week figure, not the session window note",
      "no week figure" in pts["accounts.system.runway"]["why"], pts["accounts.system.runway"])

# --- a lent account in the gap is judged by its loan, as outside it -----------------------------------------------------
pts = accounts({"system": gap, "lentone": rec("lentone", READ, 50.0, RESET)},
               lent={"lentone": {"max_used_by_us_pct": 48, "prefer_start_of_week_h": 48, "floor_pct_left": 10}})
lr = pts.get("accounts.lentone.loan_runway") or {}
check("reset gap, lent account: a loan runway is read and the week runway defers to it",
      lr.get("m") == "ESTIMATE" and lr.get("v") is not None
      and pts["accounts.lentone.runway"].get("judged_by") == "accounts.lentone.loan_runway", (lr, pts["accounts.lentone.runway"]))

print("RESULT: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
sys.exit(1 if FAILS else 0)
