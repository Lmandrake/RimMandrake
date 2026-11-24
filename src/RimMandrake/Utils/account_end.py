#!/usr/bin/env python3
"""The end of an account (RIMMANDRAKE_BUILD_ACCOUNT_END_WARN_SAVE_PAUSE_SWITCH_SIZED_BY_BURN; page
design/specs/2026-11-24-account-end/boundary.md): the numbers (burn rate, warning line, pause), the text of the two
orders, their delivery into the live runs, and the records. switching_plan.py decides and acts; this module holds no
decision of its own and never touches the meter or the switcher. The numbers are switching_plan.json `account_end`.

    account_end.py burn [ACCOUNT]    the burn rate of an account (default: the live one), and what it would size
"""
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
RIMFLOW = HERE.parent / "rimflow"
if str(RIMFLOW) not in sys.path:
    sys.path.insert(0, str(RIMFLOW))
SERIES = Path("/mnt/d/ClaudeWork/rimmandrake/account_usage/series.jsonl")
SERIES_TAIL = 400_000   # bytes: about 800 lines, over two days of readings; the window needs one hour
ITEM = "RIMMANDRAKE_BUILD_ACCOUNT_END_WARN_SAVE_PAUSE_SWITCH_SIZED_BY_BURN"   # the ledger events' item
FAMILIES = ("detached", "role")     # the runs of the control store that carry the stop hook and spend the account
RESET_JITTER_S = 900    # a week's reset time moves by a minute between readings; another week is days away


def epoch(s):
    """-> the time of an ISO string, None when there is none; ValueError when it is no time."""
    return datetime.fromisoformat(str(s)).timestamp() if s else None


def iso(t):
    return datetime.fromtimestamp(t, timezone.utc).astimezone().isoformat(timespec="seconds")


# ------------------------------------------------------------------ the numbers (pure)
def burn_of(rows, account, now, cfg):
    """-> {"rate": % of the week per minute, or None, "stale": bool, "why", "age_s", "span_min"}. The slope of the
    account's MEASURED readings of this week inside the last burn_window_min before its newest one. rate None and stale
    True when there are fewer than two, or the newest is older than stale_min: could not read is never a slow burn."""
    rd = []
    for r in rows or []:
        if not isinstance(r, dict) or r.get("account") != account or r.get("source") != "MEASURED":
            continue
        try:
            t, u, rs = epoch(r.get("measured_at")), r.get("week_pct_used"), epoch(r.get("week_resets_at"))
        except ValueError:      # no readable time: no reading
            continue
        if t is not None and t <= now + 60 and isinstance(u, (int, float)) and not isinstance(u, bool):
            rd.append((t, float(u), rs))
    none = {"rate": None, "stale": True, "age_s": None, "span_min": None}
    if not rd:
        return {**none, "why": "no measured reading of %s" % account}
    rd.sort()
    t1, u1, rs = rd[-1]
    age = max(0.0, now - t1)
    if age > cfg["stale_min"] * 60:
        return {**none, "age_s": age, "why": "the newest reading of %s is %d min old" % (account, age // 60)}
    win, prev = [], u1
    for t, u, r in reversed(rd):      # back to the window's start, or to where the week changed (what is used fell)
        if t < t1 - cfg["burn_window_min"] * 60 or u > prev or (
                rs is not None and r is not None and abs(r - rs) > RESET_JITTER_S):
            break
        win.append((t, u))
        prev = u
    span = t1 - win[-1][0]
    if span < cfg["burn_min_span_min"] * 60:
        return {**none, "age_s": age, "why": "only %d min of readings of %s in this week" % (span // 60, account)}
    return {"rate": (u1 - win[-1][1]) / (span / 60), "stale": False, "age_s": age, "span_min": span / 60, "why": ""}


def read_burn(account, now, cfg, path=None):
    """burn_of over the tail of series.jsonl; unreadable reads stale, with the cause."""
    try:
        with open(path or SERIES, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - SERIES_TAIL))
            lines = f.read().decode("utf-8", "replace").splitlines()
    except OSError as e:
        return {"rate": None, "stale": True, "age_s": None, "span_min": None, "why": "series unreadable: %s" % e}
    rows = []
    for ln in lines:
        try:
            rows.append(json.loads(ln))
        except ValueError:
            continue
    return burn_of(rows, account, now, cfg)


def stale_burn(why):
    return {"rate": None, "stale": True, "age_s": None, "span_min": None, "why": why}


def has_emergency(line, cfg):
    """An account whose line keeps it well above zero has no emergency step."""
    return line is not None and line <= cfg["emergency_max_line"]


def fast_rate(base, cfg):
    """The burn over which a save does not fit between `base` percent and the emergency line."""
    return (base - cfg["emergency_pct"]) / cfg["save_need_min"]


def warning_line(line, burn, cfg):
    """The percent left at which the save warning fires on an account with this line: max(line, warn_pct), one step
    (warn_fast_pct - warn_pct) more when the burn is fast, stale or unknown."""
    base = max(line, cfg["warn_pct"])
    if burn is None or burn.get("stale") or burn.get("rate") is None or burn["rate"] > fast_rate(base, cfg):
        return base + (cfg["warn_fast_pct"] - cfg["warn_pct"])
    return base


def target_line(line, cfg):
    """No switch lands on an account at or under this: it would be warned at once."""
    return max(line, cfg["warn_fast_pct"])


def safe_rate(burn, cfg):
    """The rate the estimates use: the measured one; with no measured one, the rate that the 3% line is sized for."""
    if burn and burn.get("rate") is not None and not burn.get("stale"):
        return burn["rate"], False
    return (cfg["warn_fast_pct"] - cfg["emergency_pct"]) / cfg["save_need_min"], True


def minutes_left(pct, burn, cfg):
    """Estimated minutes until the meter reads the emergency percent; None when nothing burns."""
    rate, _ = safe_rate(burn, cfg)
    if rate <= 0:
        return None
    return max(0.0, (pct - cfg["emergency_pct"]) / rate - ((burn or {}).get("age_s") or 0) / 60)


def pause_s(burn, cfg):
    """The pause between the emergency order and the switch: a fifth of the time from 0.5% to zero at the burn rate,
    less the age of the reading, in [pause_min_s, pause_max_s]. Stale or unknown: the shortest (the reasoning: the page's
    the-pause-keeps-the-chance-of-zero-under-ten-percent)."""
    if not burn or burn.get("stale") or burn.get("rate") is None:
        return cfg["pause_min_s"]
    if burn["rate"] <= 0:
        return cfg["pause_max_s"]
    s = cfg["pause_share"] * cfg["pause_from_pct"] / burn["rate"] * 60 - (burn.get("age_s") or 0)
    return int(min(cfg["pause_max_s"], max(cfg["pause_min_s"], s)))


# ------------------------------------------------------------------ the two orders (pure text)
def numbers(pct, burn):
    b = burn or {}
    if b.get("rate") is None or b.get("stale"):
        return "%s%% of its week is left and the burn rate is STALE (%s), so these are safe values, not measurements" % (
            num(pct), b.get("why") or "could not read it")
    return "%s%% of its week is left and the machine burns %.3f%% a minute" % (num(pct), b["rate"])


def num(x):
    return "?" if x is None else ("%g" % x)


CARRY = ("Start your last note with LEFT OPEN: in place of STOPPED, and say exactly what is done, half-done and next: "
         "your work is then carried on by itself after the switch. No trial of yours is spent")


def warn_text(account, pct, burn, line, cfg, last):
    then = ("then the machine stops until an account resets" if last else "then the machine switches accounts")
    if has_emergency(line, cfg):
        m = minutes_left(pct, burn, cfg)
        when = ("you have about %s to complete your save, until the emergency step at %g%%" % (
            "no limit at this rate" if m is None else "%d minutes" % int(m), cfg["emergency_pct"]))
        if (burn or {}).get("stale", True):
            when = "assume %d minutes at most to complete your save, until the emergency step at %g%%" % (
                int(m or 0), cfg["emergency_pct"])
        end = "%s; %s and every Claude process is stopped. " % (when, then)
    else:
        end = ("there is no emergency step on this account: when the last run has ended, %s. " % then.replace("then ", ""))
    return ("ACCOUNT END, the save warning: wrap it up cleanly and safely save your work. Account %s: %s; %s"
            "Let that decide what you still finish: publish what is done first, start nothing that does not fit. %s"
            % (account, numbers(pct, burn), end, CARRY))


def emergency_text(account, pct, burn, secs, last):
    return ("ACCOUNT END, emergency: record your state immediately and prepare for termination. Account %s: %s; in "
            "about %d seconds %s and every Claude process is stopped. Write one note now, then publish only if it is one "
            "command away. %s" % (account, numbers(pct, burn), secs,
                                  "the machine stops until an account resets" if last else
                                  "the machine switches accounts", CARRY))


# ------------------------------------------------------------------ delivery (impure: the control store)
class Orders:
    """The orders' way into the live runs: the control store's stop orders, which each run's own PostToolUse hook reads
    (`pipe stop --at-easy-spot | --write-now` use the same rows). A test hands a fake."""

    def __init__(self, db=None):
        self.db = db

    def store_runs(self):
        """-> the started detached and role units of the store. Raises control.Unreadable: could not look is not "none"."""
        import control as C
        rows = C._q("SELECT unit, family FROM runs WHERE state='started'", (), self.db)
        return [r["unit"] for r in rows if r["family"] in FAMILIES]

    def send(self, units, mode, text, deadline=None):
        """One stop order per unit. -> (act id, None) or (None, why): an order that could not be written never stops the
        machine's own step."""
        import control as C
        try:
            return C.order_runs(units, mode, text, deadline=deadline, p=self.db)["id"], None
        except Exception as e:  # noqa: BLE001
            return None, "%s: %s" % (type(e).__name__, e)

    def withdraw(self, acts, why):
        import control as C
        try:
            return C.withdraw_orders(acts, why, p=self.db), None
        except Exception as e:  # noqa: BLE001
            return None, "%s: %s" % (type(e).__name__, e)

    def saved(self, unit, since):
        """What one ordered run had saved, read before the switch -> one phrase."""
        import control as C
        import detached_helper as DH
        try:
            r = C.run_state(unit, self.db)
        except Exception as e:  # noqa: BLE001
            return "could not look (%s)" % e
        if r and r.get("state") in ("ended", "killed"):
            return "ended by itself before the switch" if r["state"] == "ended" else "killed before the switch"
        rec = DH.read_record(unit)
        if not rec:
            return "still live; no run record, so its notes could not be looked for"
        if rec.get("status") == "finished":
            return "ended by itself before the switch"
        shard = Path(rec.get("clone") or "/nonexistent") / DH.EVENTS_REL / ("%s.jsonl" % rec.get("seat"))
        try:
            with open(shard, "rb") as f:
                f.seek(0, 2)
                f.seek(max(0, f.tell() - 300_000))
                tail = f.read().decode("utf-8", "replace").splitlines()
        except OSError as e:
            return "still live; its ledger could not be read (%s)" % e.__class__.__name__
        last = None
        for ln in tail:
            try:
                e = json.loads(ln)
            except ValueError:
                continue
            t = DH._epoch(e.get("ts")) if isinstance(e, dict) else None
            if t is not None and t >= since and e.get("id") == rec.get("item") and e.get("event") == "note":
                last = t
        return ("still live; saved a note at %s" % time.strftime("%I:%M:%S %p %Z", time.localtime(last))) if last else \
            "still live; no note seen since its order"


# ------------------------------------------------------------------ records (impure)
def conductor_line(text, now):
    import detached_helper as DH
    DH.conductor_line(text, now, head="ACCOUNT END")


def ledger_events(texts):
    """Each text as one note event on ITEM, by the RUNNER seat from the dispatch clone, published (the road of
    deadman_check.live_filer). -> the texts not written."""
    import fcntl
    import importlib.util
    q = Path(os.environ.get("TESTQ_QUEUE", "/mnt/d/ClaudeWork/rimmandrake/testq"))
    spec = importlib.util.spec_from_file_location("account_end_ingest", str(HERE / "testq" / "ingest.py"))
    ing = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ing)
    left = list(texts)
    with open(q / "ingest.lock", "w") as lk:
        try:
            fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            return left     # held: the next pass writes them
        n = 0
        for t in texts:
            rc, out = ing.rimflow("note", ITEM, "--text", t, "--why", "account end (switching_plan.py, no AI)")
            if rc:
                print("account_end: ledger note refused: %s" % out[-300:], file=sys.stderr)
                continue
            left.remove(t)
            n += 1
        if n:
            print("account_end: " + str(ing.publish(n, message="ledger: account end")))
    return left


def main(argv=None):
    import switching_plan as SP
    av = list(sys.argv[1:] if argv is None else argv)
    if av[:1] != ["burn"]:
        print(__doc__)
        return 2
    plan, now = SP.load_plan(), time.time()
    cfg, meter = plan["account_end"], SP.meter_now()
    acct = av[1] if len(av) > 1 else SP.switcher_status().get("live")
    b = read_burn(acct, now, cfg)
    line = SP.lines(meter, SP.at(plan, now, meter), now)[0].get(acct)
    out = {"account": acct, "line": line, "burn": b, "has_emergency": has_emergency(line, cfg), "pause_s": pause_s(b, cfg)}
    if line is not None:
        out["warning_line"] = warning_line(line, b, cfg)
        out["minutes_from_warning_to_emergency"] = minutes_left(out["warning_line"], b, cfg)
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
