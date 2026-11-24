#!/usr/bin/env python3
"""The account plan: one file, one pure decision, one-line commands (./acct). No model call, no poll in a status.

Page: design/specs/2026-11-24-account-plan-one-file/boundary.md (the promises; selftest_account_plan.py checks each by
name). Design: design.md beside it. Item RIMMANDRAKE_DESIGN_ACCOUNT_PLAN_ONE_FILE_COMMANDED_IN_ONE_LINE.

The rule (owner, 2026-11-24): the live account STAYS live until its own step is finished. The order of the steps says
only which account is next. A switch that rescues allowance from a reset must be worth a switch, and it never stops a
run and never refuses a start. Each decision says its reason in one line.

    ./acct status | next | plan | readings | forecast | measures | burn-mode | can-use A
    ./acct order A B C · line A N · step add|set|rm|move · switch A · pin · unpin · hold --for 2h · release
    ./acct set numbers.K=V · undo [REV] · whatif -- <a write> · import-legacy · tick [--shadow]
    ./acct driver [old|new] · pass        which engine the timer's pass runs; the pass itself

The plan file: $RM_ACCOUNT_PLAN_DIR/plan.json (default ~/.local/state/rimmandrake/account_plan), outside every clone:
a write binds at the next read. Levels are read only through account_usage.py; the switch, the save orders and the
pause stay in switching_plan._check and account_end.py, which `tick` drives with this file's decision.
Exit: 0 done or a value · 1 no · 2 could not look · 3 refused, nothing written · 4 failed · 5 none.
Test seams: RM_ACCOUNT_PLAN_DIR, RM_ACCOUNT_PLAN_FRAME (a JSON frame in place of every live reading).
"""
import argparse
import copy
import fcntl
import getpass
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import account_end as AE  # noqa: E402  the account-end numbers have one definition

OK, NO, COULD_NOT_LOOK, REFUSED, FAILED, NONE = 0, 1, 2, 3, 4, 5
TZ = ZoneInfo("America/Los_Angeles")
WEEK = 7 * 86400
SEED = HERE / "account_plan.seed.json"
STEP_KEYS = {"name", "use", "leave", "warn", "until", "when", "from", "ends", "ends_at_reset_of", "why", "by"}
DAYS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
GOOD_BURN = {"rate": 0.0, "stale": False}     # the week ahead uses the ordinary warning line, never the fast one


class Refused(Exception):
    """A fault in what was asked. The text names the fault and its repair; nothing was written."""


def clock() -> float:
    """Now. RM_ACCOUNT_PLAN_NOW names a fixed time for a selftest."""
    return float(os.environ.get("RM_ACCOUNT_PLAN_NOW") or time.time())


def plan_dir() -> Path:
    return Path(os.environ.get("RM_ACCOUNT_PLAN_DIR") or Path.home() / ".local/state/rimmandrake/account_plan")


# ------------------------------------------------------------------ times
def stamp(s):
    """Epoch of an ISO time. A time with no offset is Pacific. None when there is none or it does not parse."""
    if s in (None, ""):
        return None
    try:
        d = datetime.fromisoformat(str(s))
    except ValueError:
        return None
    return (d if d.tzinfo else d.replace(tzinfo=TZ)).timestamp()


def stamp_or(s, default):
    """stamp(s), or `default` where the text holds no time: the caller says what an unreadable time means there."""
    t = stamp(s)
    return default if t is None else t


def iso(t) -> str:
    return datetime.fromtimestamp(t, TZ).isoformat(timespec="seconds")


def pacific(t) -> str:
    return datetime.fromtimestamp(t, TZ).strftime("%a %b %d %-I:%M %p %Z")


def span(text):
    """'90m', '2h', '3d' -> seconds; Refused when it is none of these."""
    m = re.fullmatch(r"(\d+(?:\.\d+)?)([mhd])", str(text).strip())
    if not m:
        raise Refused(f"`{text}` is no duration; repair: a number and m, h or d, as in 2h")
    return float(m.group(1)) * {"m": 60, "h": 3600, "d": 86400}[m.group(2)]


def g(x) -> str:
    return "%g" % round(x, 1)


# ------------------------------------------------------------------ conditions: a small fixed grammar, three values
TERMS = ("left", "hours_to_reset", "hours_since_reset", "age_min", "burn", "runs", "clock", "weekday")
WORD_RX = re.compile(r"\s*(\(|\)|<=|>=|==|!=|<|>|\d\d?:\d\d|\d+(?:\.\d+)?|[A-Za-z_][\w.\-]*(?::[\w.\-]+)?)")
_PARSED = {}


def parse(text):
    """-> the condition as nested tuples. Refused, with the place, when the text is not in the grammar."""
    if text in _PARSED:
        return _PARSED[text]
    toks, i = [], 0
    s = str(text)
    while i < len(s):
        if s[i:].strip() == "":
            break
        m = WORD_RX.match(s, i)
        if not m:
            raise Refused(f"condition `{text}`: cannot read `{s[i:].strip()[:20]}`; repair: terms {', '.join(TERMS)} "
                          "with < <= == != >= > and a number, joined by and, or, not")
        toks.append(m.group(1))
        i = m.end()
    pos = [0]

    def peek():
        return toks[pos[0]] if pos[0] < len(toks) else None

    def take():
        pos[0] += 1
        return toks[pos[0] - 1]

    def p_or():
        a = p_and()
        while peek() == "or":
            take()
            a = ("or", a, p_and())
        return a

    def p_and():
        a = p_not()
        while peek() == "and":
            take()
            a = ("and", a, p_not())
        return a

    def p_not():
        if peek() == "not":
            take()
            return ("not", p_not())
        if peek() == "(":
            take()
            a = p_or()
            if peek() != ")":
                raise Refused(f"condition `{text}`: a bracket is not closed")
            take()
            return a
        return p_cmp()

    def p_cmp():
        t = peek()
        name, _, acct = (t or "").partition(":")
        if name not in TERMS:
            raise Refused(f"condition `{text}`: `{t}` is no term; repair: one of {', '.join(TERMS)}")
        take()
        op = peek()
        if op not in ("<", "<=", "==", "!=", ">=", ">"):
            raise Refused(f"condition `{text}`: after `{t}` comes one of < <= == != >= >")
        take()
        v = peek()
        if v is None:
            raise Refused(f"condition `{text}`: `{t} {op}` has no value")
        take()
        if name == "clock":
            m = re.fullmatch(r"(\d\d?):(\d\d)", v)
            if not m or int(m.group(1)) > 23 or int(m.group(2)) > 59:
                raise Refused(f"condition `{text}`: clock takes a local time as HH:MM, not `{v}`")
            val = int(m.group(1)) * 60 + int(m.group(2))
        elif name == "weekday":
            if v.lower() not in DAYS:
                raise Refused(f"condition `{text}`: weekday takes one of {', '.join(DAYS)}, not `{v}`")
            val = DAYS.index(v.lower())
        else:
            try:
                val = float(v)
            except ValueError:
                raise Refused(f"condition `{text}`: `{v}` is no number") from None
        return ("cmp", name, acct or None, op, val)

    tree = p_or()
    if peek() is not None:
        raise Refused(f"condition `{text}`: `{peek()}` is left over; repair: join clauses with and, or")
    _PARSED[text] = tree
    return tree


def terms_accounts(tree):
    if tree[0] == "cmp":
        return {tree[2]} - {None}
    return set().union(*(terms_accounts(x) for x in tree[1:]))


def truth(tree, env, me):
    """True, False or None (unknown). Unknown stays unknown under `not`; it never reads as permission."""
    k = tree[0]
    if k == "not":
        v = truth(tree[1], env, me)
        return None if v is None else not v
    if k in ("and", "or"):
        a, b = truth(tree[1], env, me), truth(tree[2], env, me)
        if k == "and":
            return False if (a is False or b is False) else (None if (a is None or b is None) else True)
        return True if (a is True or b is True) else (None if (a is None or b is None) else False)
    _k, name, acct, op, val = tree
    x = env.term(name, acct or me)
    if x is None:
        return None
    return {"<": x < val, "<=": x <= val, "==": x == val, "!=": x != val, ">=": x >= val, ">": x > val}[op]


class Env:
    """What a condition can read, at one moment: real readings, or the state of a week ahead."""

    def __init__(self, now, left, reset, age=None, burn=None, runs=None, entry=None):
        self.now, self._left, self._reset, self._age = now, left, reset, age or (lambda a: None)
        self.burn, self.runs, self._entry = burn, runs, entry or (lambda a: None)

    def left(self, a):
        return self._left(a)

    def reset(self, a):
        return self._reset(a)

    def to_reset_h(self, a):
        rs = self._reset(a)
        return None if rs is None else (rs - self.now) / 3600

    def entry_left(self, a):
        return self._entry(a)

    def first_reset_after(self, a, t0):
        rs = self._reset(a)
        if rs is None:
            return None
        while rs - WEEK > t0:
            rs -= WEEK
        while rs <= t0:
            rs += WEEK
        return rs

    def term(self, name, a):
        if name == "left":
            return self.left(a)
        if name == "hours_to_reset":
            return self.to_reset_h(a)
        if name == "hours_since_reset":
            h = self.to_reset_h(a)
            return None if h is None else 168 - h
        if name == "age_min":
            return self._age(a)
        if name == "burn":
            return self.burn
        if name == "runs":
            return self.runs
        d = datetime.fromtimestamp(self.now, TZ)
        return d.hour * 60 + d.minute if name == "clock" else d.weekday()


# ------------------------------------------------------------------ the plan file: read, validate, write
NUMBER_KEYS = {
    "floor_pct": float, "last_account_floor_pct": float, "blind_pct": float, "entry_margin_pct": float,
    "switch_cost_pts": float, "idle_weight": float, "evening_share_pct": float, "request_default_h": float,
    "forecast.burn_window_h": float, "forecast.step_min": float, "fresh.near_pct": float, "fresh.max_age_min": float,
    "reset_day.hours": float, "burn_mode.window_h": float, "burn_mode.min_at_risk_pts": float,
    "burn_mode.max_load_per_core": float,
    **{"account_end." + k: float for k in (
        "warn_pct", "warn_fast_pct", "emergency_pct", "emergency_max_line", "save_need_min", "burn_window_min",
        "burn_min_span_min", "stale_min", "poll_min", "pause_share", "pause_from_pct", "pause_max_s", "pause_min_s",
        "clear_pct")}}


def dig(d, path):
    for k in path.split("."):
        if not isinstance(d, dict) or k not in d:
            return None
        d = d[k]
    return d


def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def problems(plan) -> list:
    """Every fault of the plan, each with its repair. [] is a valid plan."""
    out = []
    if not isinstance(plan, dict) or plan.get("schema") != 1:
        return ["the plan is not a schema 1 object; repair: ./acct undo, or ./acct import-legacy"]
    accts = plan.get("accounts")
    if not isinstance(accts, dict) or not accts:
        return ["`accounts` is missing; repair: ./acct undo"]
    for a, c in accts.items():
        if not isinstance(c, dict) or c.get("kind") not in ("claude", "meter"):
            out.append(f"account {a}: `kind` must be claude or meter")
    if plan.get("driver", "old") not in ("old", "new"):
        out.append("`driver` must be old or new; repair: ./acct driver old")
    N = plan.get("numbers")
    if not isinstance(N, dict):
        return out + ["`numbers` is missing; repair: ./acct undo"]
    for k in NUMBER_KEYS:
        v = dig(N, k)
        if not is_num(v) or v < 0:
            out.append(f"numbers.{k} must be a number of 0 or more, not {v!r}; repair: ./acct set numbers.{k}=<number>")
    rd = N.get("reset_day") or {}
    if not isinstance(rd.get("accounts"), list) or any(a not in accts for a in rd.get("accounts", [])):
        out.append("numbers.reset_day.accounts must list accounts of the plan")
    ln = rd.get("line") or {}
    for kind in ("claude", "meter"):
        if not (ln.get(kind) == "floor" or (is_num(ln.get(kind)) and 0 <= ln[kind] <= 100)):
            out.append(f"numbers.reset_day.line.{kind} must be a percent or `floor`")
    v = dig(N, "rescue.drain_h")
    if not isinstance(N.get("rescue"), dict) or "drain_h" not in N["rescue"] or (
            v is not None and not (is_num(v) and v >= 0)):
        out.append("numbers.rescue.drain_h must be null (a rescue never refuses a start) or hours; repair: ./acct set "
                   "numbers.rescue.drain_h=2")
    floor = N.get("floor_pct") if is_num(N.get("floor_pct")) else 0
    steps = plan.get("steps")
    if not isinstance(steps, list) or not steps:
        return out + ["the plan has no step; repair: ./acct step add <name> --use <account> --leave <percent>"]
    seen = set()
    for i, s in enumerate(steps):
        tag = f"step {s.get('name') if isinstance(s, dict) else '#%d' % i}"
        if not isinstance(s, dict) or not re.fullmatch(r"[A-Za-z0-9_.\-]+", str(s.get("name") or "")):
            out.append(f"{tag}: needs a name of letters, digits, _ . -")
            continue
        if s["name"] in seen:
            out.append(f"{tag}: the name is used twice; repair: ./acct step rm {s['name']}")
        seen.add(s["name"])
        extra = sorted(set(s) - STEP_KEYS)
        if extra:
            out.append(f"{tag}: unknown field(s) {extra}; repair: ./acct step set {s['name']} {extra[0]}=")
        a = s.get("use")
        if a not in accts:
            out.append(f"{tag}: `use` names no account of the plan ({sorted(accts)})")
            continue
        lv, lo = s.get("leave"), (floor if accts[a].get("kind") == "claude" else 0)
        rel = isinstance(lv, str) and re.fullmatch(r"entry-\d+(\.\d+)?", lv)
        if not rel and not (is_num(lv) and lo <= lv <= 100):
            out.append(f"{tag}: `leave` must be a percent from {g(lo)} to 100 (a Claude account is never taken under "
                       f"the floor) or entry-N, not {lv!r}; repair: ./acct step set {s['name']} leave=<percent>")
        if s.get("warn") is not None and not (is_num(s["warn"]) and 0 <= s["warn"] <= 100):
            out.append(f"{tag}: `warn` is the leeway in points, 0 to 100")
        for k in ("until", "when"):
            if s.get(k) is not None:
                try:
                    bad = terms_accounts(parse(s[k])) - set(accts)
                    if bad:
                        out.append(f"{tag}: `{k}` names no account of the plan: {sorted(bad)}")
                except Refused as e:
                    out.append(f"{tag}: {e}")
        f, u = stamp(s.get("from")), stamp(s.get("ends"))
        for k in ("from", "ends"):
            if s.get(k) is not None and stamp(s[k]) is None:
                out.append(f"{tag}: `{k}` is no ISO time ({s[k]!r})")
        if f is not None and u is not None and u <= f:
            out.append(f"{tag}: `ends` must fall after `from`")
        if s.get("ends_at_reset_of") is not None:
            if s["ends_at_reset_of"] not in accts:
                out.append(f"{tag}: `ends_at_reset_of` names no account of the plan")
            if f is None:
                out.append(f"{tag}: `ends_at_reset_of` needs a `from` (the reset meant is the first one after it)")
    if not any(accts.get(s.get("use"), {}).get("kind") == "claude" for s in steps if isinstance(s, dict)):
        out.append("no step uses a Claude account; repair: ./acct step add <name> --use <account> --leave <percent>")
    for kind, need in (("holds", ("id", "at", "ends")), ("pins", ("account", "at", "ends")),
                       ("requests", ("to", "at", "ends"))):
        if not isinstance(plan.get(kind), list):
            out.append(f"`{kind}` must be a list; repair: ./acct undo")
            continue
        for i, h in enumerate(plan[kind]):
            if not isinstance(h, dict) or any(k not in h for k in need) or stamp(h.get("at")) is None \
                    or stamp(h.get("ends")) is None:
                out.append(f"{kind}[{i}]: needs {', '.join(need)}, with `at` and `ends` as ISO times; a brake or a "
                           "request with no end is refused; repair: --for 2h or --until <time>")
            elif kind != "holds" and accts.get(h.get("account") or h.get("to"), {}).get("kind") != "claude":
                out.append(f"{kind}[{i}]: names no Claude account of the plan")
    return out


def read_json(path, default=None):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return default


def load_plan():
    """-> (plan, None), or (None, why): NONE when there is no plan file yet, the faults when it is not valid."""
    p = plan_dir() / "plan.json"
    try:
        text = p.read_text()
    except FileNotFoundError:
        return None, f"NONE: no plan file at {p}; repair: ./acct import-legacy"
    except OSError as e:
        return None, f"COULD NOT LOOK: {p}: {e}"
    try:
        plan = json.loads(text)
    except ValueError as e:
        return None, f"the plan file is not JSON ({e}); repair: ./acct undo"
    bad = problems(plan)
    if bad:
        return None, "the plan file is refused: " + "; ".join(bad[:3]) + "; repair: ./acct undo"
    return plan, None


def write_atomic(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp%d" % os.getpid())
    with open(tmp, "w") as f:
        f.write(json.dumps(obj, indent=1, sort_keys=False) + "\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def history() -> list:
    out = []
    try:
        for ln in (plan_dir() / "history.jsonl").read_text().splitlines():
            try:
                out.append(json.loads(ln))
            except ValueError:
                continue
    except OSError:
        pass
    return out


def commit(change, meta: dict, base=None):
    """One write: lock, read, change a copy, validate, replace, history line. -> (rev, plan). Refused: nothing written."""
    d = plan_dir()
    d.mkdir(parents=True, exist_ok=True)
    with open(d / "plan.lock", "a") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)      # a write takes milliseconds: the second writer waits its turn
        if base is None:
            old, why = load_plan()
            if old is None and not meta.get("create"):
                raise Refused(why)
        else:
            old = base
        new = change(copy.deepcopy(old) if old is not None else None)
        bad = problems(new)
        if bad:
            raise Refused("; ".join(bad))
        new["rev"] = max([int((old or {}).get("rev") or 0)] + [int(h.get("rev") or 0) for h in history()]) + 1
        write_atomic(d / "plan.json", new)
        rec = {"rev": new["rev"], "at": iso(time.time()), "by": os.environ.get("RM_SEAT") or getpass.getuser(),
               **{k: v for k, v in meta.items() if k != "create" and v}, "before": old, "after": new}
        if not any(meta.get(k) for k in ("why", "owner_said", "by_card", "per_ruling")):
            rec["why"] = "no reason given"
        if meta.get("owner_said") or meta.get("by_card"):
            rec["ledger"] = "owed"
        with open(d / "history.jsonl", "a") as f:
            f.write(json.dumps(rec) + "\n")
    return new["rev"], new


# ------------------------------------------------------------------ readings (through account_usage only)
def reading(row, now) -> dict:
    """One account_usage.read_now() row as the plan reads it. `left` is None unless MEASURED, fresh and of this week."""
    if not row:
        return {"left": None, "ok": False, "state": "UNMEASURED", "reset": None, "reset_passed": False,
                "age_min": None, "last_left": None, "why": "no reading"}
    rs = stamp(row.get("week_resets_at"))
    passed = rs is not None and rs <= now
    nxt = rs
    while nxt is not None and nxt <= now:
        nxt += WEEK
    left = None if passed else row.get("week_pct_left")
    if left is None and not passed and is_num(row.get("week_pct_used")):
        left = round(100 - row["week_pct_used"], 1)
    ok = row.get("source") == "MEASURED" and not row.get("stale") and left is not None
    state = "RESET PASSED" if passed else "MEASURED" if ok else ("STALE" if row.get("stale") else
                                                                 str(row.get("source") or "UNMEASURED"))
    return {"left": left if ok else None, "ok": ok, "state": state, "reset": nxt, "reset_passed": passed,
            "age_min": row.get("age_min"), "last_left": left, "why": row.get("why") or ""}


def fleet_burn(rows, now, window_h, accounts=None):
    """Points of a week per hour that the machine burned over the last window_h: the rises of what is used between
    two MEASURED readings of one account in one week, summed over the accounts. None when under an hour is covered."""
    per, t0 = {}, now - window_h * 3600
    for r in rows or []:
        if not isinstance(r, dict) or r.get("source") != "MEASURED" or (accounts and r.get("account") not in accounts):
            continue
        t, u = stamp(r.get("measured_at")), r.get("week_pct_used")
        if t is None or not is_num(u) or not t0 <= t <= now + 60:
            continue
        per.setdefault(r["account"], []).append((t, float(u), stamp(r.get("week_resets_at"))))
    total, first = 0.0, None
    for rd in per.values():
        rd.sort()
        first = rd[0][0] if first is None else min(first, rd[0][0])
        for (ta, ua, ra), (tb, ub, rb) in zip(rd, rd[1:]):
            same = ra is None or rb is None or abs(ra - rb) <= AE.RESET_JITTER_S
            if same and ub > ua:
                total += ub - ua
    if first is None or now - first < 3600:
        return None
    return total / ((now - first) / 3600)


def series_rows(tail_bytes=1_200_000, path=None):
    """The tail of the reader's series (about six days), or None when it cannot be read."""
    try:
        with open(path or os.environ.get("RM_ACCOUNT_PLAN_SERIES") or AE.SERIES, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - tail_bytes))
            lines = f.read().decode("utf-8", "replace").splitlines()
    except OSError:
        return None
    out = []
    for ln in lines:
        try:
            out.append(json.loads(ln))
        except ValueError:
            continue
    return out


def meter_reading(points, now):
    """Codex's weekly meter (account_usage.read_codex_points) as a reading."""
    used, hrs = (points or {}).get("codex.week_used_pct") or {}, (points or {}).get("codex.hours_to_reset") or {}
    v = used.get("v")
    if not is_num(v) or v < 0:
        return {"left": None, "ok": False, "state": "UNMEASURED", "reset": None, "reset_passed": False, "age_min": None,
                "last_left": None, "why": used.get("why") or "no weekly reading", "burn_h": None}
    h = hrs.get("v")
    at = stamp((used.get("x") or {}).get("reading_at"))
    ok = used.get("m") == "MEASURED"
    rate = ((points.get("codex.runway") or {}).get("x") or {}).get("rate_pct_h")
    return {"left": round(100 - v, 1) if ok else None, "ok": ok, "state": "MEASURED" if ok else "ESTIMATE",
            "reset": now + h * 3600 if is_num(h) else None, "reset_passed": False,
            "age_min": None if at is None else round((now - at) / 60, 1), "last_left": round(100 - v, 1),
            "why": used.get("why") or "", "burn_h": rate if is_num(rate) else None}


def gather(now=None, slow=False) -> dict:
    """Every input of a decision, read once. RM_ACCOUNT_PLAN_FRAME names a JSON frame in its place (tests).
    slow: also read Codex and JPL GenAI (seconds) and keep them in frame.json; otherwise they come from that file."""
    seam = os.environ.get("RM_ACCOUNT_PLAN_FRAME")
    if seam:
        f = json.loads(Path(seam).read_text())
        f.setdefault("now", now or time.time())
        return f
    import account_live as AL
    import account_usage as AU
    import switching_plan as SP
    now = now or time.time()
    ans = AL.read(exe_path=SP.CA)
    live = AL.status_of(ans).get("live")
    rows = AU.read_now(now).get("accounts")
    if rows is None:        # the reader has no latest.json: every level then reads UNMEASURED, by name, never 0
        rows = {}
    try:
        runs = SP.live_detached_runs()
    except Exception:  # noqa: BLE001  unreadable runs count as live
        runs = None
    markers, sws = SP.read_markers(), SP.switches()
    plan, _why = load_plan()
    cfg = dig(plan or {}, "numbers.account_end") or SP.load_plan()["account_end"]
    series = series_rows()
    cache = read_json(plan_dir() / "frame.json", {})
    if not isinstance(cache, dict):
        cache = {}
    if slow:
        try:
            codex = meter_reading(AU.read_codex_points(), now)
        except Exception as e:  # noqa: BLE001  the reader failing is could not look, named
            codex = {**reading(None, now), "why": f"reader failed: {type(e).__name__}: {e}", "burn_h": None}
        codex["read_at"] = now
        genai = list(AU.read_genai_status())
        cache = {"codex": codex, "genai": genai, "at": now}
        write_atomic(plan_dir() / "frame.json", cache)
    codex = cache.get("codex") or {**reading(None, now), "why": "no timed pass has read it yet", "burn_h": None}
    entry = {}
    if plan and any(isinstance(s.get("leave"), str) for s in plan["steps"]):
        for s in plan["steps"]:
            if isinstance(s.get("leave"), str):
                entry[s["use"]] = entry_level(series, sws, s["use"])
    try:
        load = os.getloadavg()[0]
    except OSError:
        load = None
    return {"now": now, "live": live, "live_why": AL.why_of(ans) if not live else "", "runs": runs,
            "rows": rows, "burn_live": SP.burn_now(live, rows, now, cfg, SP.default_burn) if live else None,
            "burn_h": fleet_burn(series, now, dig(plan or {}, "numbers.forecast.burn_window_h") or 24,
                                 accounts=set(rows)),
            "switches": sws, "hand": bool(SP.manual_switch((sws or [None])[-1], markers, live)) if sws else False,
            "draining": draining(SP),
            "markers": markers, "state": SP.load_state(), "hold_file": (SP.OUT / "HOLD").exists(),
            "codex": codex, "genai": cache.get("genai"), "slow_at": cache.get("at"), "entry": entry,
            "load": load, "ncpu": os.cpu_count() or 1}


def entry_level(series, switches, account):
    """The level of `account` when it last went live: its MEASURED reading nearest that switch (inside 30 min)."""
    ts = next((stamp(s.get("ts")) for s in reversed(switches or []) if s.get("to") == account), None)
    if ts is None:
        return None
    best = None
    for r in series or []:
        t = stamp(r.get("measured_at"))
        if r.get("account") == account and r.get("source") == "MEASURED" and t is not None \
                and is_num(r.get("week_pct_used")) and abs(t - ts) <= 1800:
            if best is None or abs(t - ts) < best[0]:
                best = (abs(t - ts), 100 - r["week_pct_used"])
    return None if best is None else best[1]


def readings_of(f) -> dict:
    return {a: reading(r, f["now"]) for a, r in (f.get("rows") or {}).items()}


# ------------------------------------------------------------------ the rule of an account (pure)
def claude_accounts(plan):
    return [a for a, c in plan["accounts"].items() if c["kind"] == "claude"]


def step_alive(step, env) -> bool:
    """Inside its life and its `when` true. An end that cannot be known, or a `when` that is unknown: not alive."""
    t, fr, end = env.now, stamp(step.get("from")), stamp(step.get("ends"))
    if fr is not None and t < fr:
        return False
    ra = step.get("ends_at_reset_of")
    if ra:
        rs = env.first_reset_after(ra, fr) if fr is not None else None
        if rs is None and end is None:
            return False
        if rs is not None:
            end = rs if end is None else min(end, rs)
    if end is not None and t >= end:
        return False
    return not step.get("when") or truth(parse(step["when"]), env, step["use"]) is True


def rule_of(plan, a, env):
    """The first alive step that uses `a`, with its leave line in force: {step, line, warn, until, reset_day}; None."""
    N = plan["numbers"]
    kind = plan["accounts"][a]["kind"]
    for s in plan["steps"]:
        if s["use"] != a or not step_alive(s, env):
            continue
        lv = s["leave"]
        if isinstance(lv, str):
            e = env.entry_left(a)
            if e is None:
                continue        # the level at switch-in is unknown: this step gives no permission
            lv = max(N["floor_pct"], e - float(lv.split("-", 1)[1]))
        line = lv + (N["evening_share_pct"] if kind == "claude" else 0)
        rd, h = N["reset_day"], env.to_reset_h(a)
        day = a in rd["accounts"] and h is not None and 0 < h <= rd["hours"]
        if day:
            dl = rd["line"][kind]
            line = min(line, N["floor_pct"] if dl == "floor" else dl)
        return {"step": s["name"], "line": line, "warn": s.get("warn"), "until": s.get("until"), "reset_day": day}
    return None


def standing_line(plan, a):
    """The leave line of the last step that uses `a` (its standing step), whatever its `when`; None with no step."""
    for s in reversed(plan["steps"]):
        if s["use"] == a and is_num(s["leave"]):
            return s["leave"]
    return None


def order_now(plan, rules):
    out = []
    for s in plan["steps"]:
        a = s["use"]
        if plan["accounts"][a]["kind"] == "claude" and rules.get(a) and rules[a]["step"] == s["name"] and a not in out:
            out.append(a)
    return out


def entry_line(plan, line):
    """A switch never lands on an account at or under this: it would be inside its own warning zone."""
    N = plan["numbers"]
    return AE.warning_line(line, None, N["account_end"]) + N["entry_margin_pct"]


# ------------------------------------------------------------------ the week ahead (pure; the pick and the forecast)
def week_ahead(plan, f, first=None, rate=None, hours=None):
    """One run of the week ahead under the plan: stay on the live account until its step is finished, then the best
    next account; each account refills at its reset. first: an account to switch to now (None: stay). -> {first,
    events, erased: {account: points}, erased_total, switches, idle_pts, cost, rate, hours}, or None when it cannot
    be run (no burn rate, the live account unknown, no reset time)."""
    rate = f.get("burn_h") if rate is None else rate
    live = f.get("live")
    if rate is None or not live:
        return None
    N, now = plan["numbers"], f["now"]
    rd = readings_of(f)
    accts = claude_accounts(plan)
    left, reset = {}, {}
    for a in accts:
        r = rd.get(a) or reading(None, now)
        left[a] = 100.0 if r["reset_passed"] else r["last_left"]
        reset[a] = r["reset"]
    known = [reset[a] for a in accts if reset[a] is not None]
    if not known or (live in accts and left.get(live) is None):
        return None
    dt = N["forecast"]["step_min"] * 60
    # to just past the last next reset: the allowance that each account has now is counted at its own reset, once
    horizon = now + hours * 3600 if hours else min(max(known), now + WEEK) + dt
    st = {"t": now, "live": live, "left": left, "reset": reset, "entry": dict(f.get("entry") or {}),
          "erased": {}, "switches": 0, "idle": 0.0, "events": []}
    if first is not None and first != live:
        _switch(st, first, "now")
    res = _run(plan, st, rate, horizon, dt)
    res.update(first=first or live, rate=rate, hours=round((horizon - now) / 3600, 1))
    return res


def _switch(st, to, why):
    st["events"].append({"kind": "switch", "at": st["t"], "from": st["live"], "to": to, "why": why,
                         "left": {a: (None if v is None else round(v, 1)) for a, v in st["left"].items()}})
    st["entry"][to] = st["left"].get(to)
    st["live"], st["switches"] = to, st["switches"] + 1


def _cost(plan, st):
    N = plan["numbers"]
    return sum(st["erased"].values()) + N["switch_cost_pts"] * st["switches"] + N["idle_weight"] * st["idle"]


def _run(plan, st, rate, horizon, dt):
    N, cfg = plan["numbers"], plan["numbers"]["account_end"]
    accts = claude_accounts(plan)
    while st["t"] < horizon:
        t = st["t"]
        env = Env(t, lambda a: st["left"].get(a), lambda a: st["reset"].get(a), burn=rate,
                  entry=lambda a: st["entry"].get(a))
        for a in accts:                      # a reset erases what is above the account's line, then refills it
            if st["reset"][a] is not None and st["reset"][a] <= t:
                before = Env(st["reset"][a] - 1, env.left, lambda b, a=a: st["reset"].get(b), burn=rate,
                             entry=env.entry_left)
                rl = rule_of(plan, a, before)
                line = rl["line"] if rl else standing_line(plan, a)
                lost = 0.0 if (line is None or st["left"][a] is None) else max(0.0, st["left"][a] - line)
                st["erased"][a] = st["erased"].get(a, 0.0) + lost
                st["events"].append({"kind": "reset", "at": st["reset"][a], "account": a, "erased": round(lost, 1),
                                     "line": line})
                st["left"][a], st["reset"][a] = 100.0, st["reset"][a] + WEEK
        rules = {a: rule_of(plan, a, env) for a in accts}
        live = st["live"]
        rl = rules.get(live)
        can = [a for a in order_now(plan, rules) if a != live and st["left"][a] is not None
               and st["left"][a] > entry_line(plan, rules[a]["line"])]
        if rl is None:
            done, under = True, True
        else:
            line = rl["line"] if can else max(rl["line"], N["last_account_floor_pct"])
            end = max(AE.warning_line(line, GOOD_BURN, cfg), line + (rl["warn"] or 0))
            under = st["left"][live] <= end
            done = under or (rl["until"] is not None and truth(parse(rl["until"]), env, live) is True)
        if done and can:
            if len(can) == 1:
                _switch(st, can[0], "its step is finished")
            else:                                   # more than one account can take over: the best week ahead wins
                best = None
                for a in can:
                    alt = copy.deepcopy(st)
                    _switch(alt, a, "its step is finished")
                    out = _run(plan, alt, rate, horizon, dt)
                    if best is None or out["cost"] < best["cost"] - 1e-9:
                        best = out
                return best
        elif done and under:
            st["idle"] += rate * dt / 3600      # nowhere to go: this burn finds no account
            st["t"] += dt
            continue
        st["left"][st["live"]] = max(0.0, st["left"][st["live"]] - rate * dt / 3600)
        st["t"] += dt
    return {"events": st["events"], "erased": {a: round(v, 1) for a, v in st["erased"].items()},
            "erased_total": round(sum(st["erased"].values()), 1), "switches": st["switches"],
            "idle_pts": round(st["idle"], 1), "cost": round(_cost(plan, st), 3)}


def choices(plan, f, can, stay=True):
    """The week ahead of each choice now: {None: stay, account: switch to it}. {} when it cannot be run."""
    out = {}
    if stay:
        out[None] = week_ahead(plan, f)
    for a in can:
        out[a] = week_ahead(plan, f, first=a)
    return {k: v for k, v in out.items() if v is not None}


def best_of(ch, order):
    """The lowest cost; a tie goes to fewer switches, then to stay, then to the step order."""
    def key(k):
        return (round(ch[k]["cost"], 6), ch[k]["switches"], 0 if k is None else 1, order.index(k) if k in order else 99)
    return min(ch, key=key) if ch else None


def runs_say(runs) -> str:
    return "the live runs are UNMEASURED, so they count as live" if runs is None else "%d live run%s" % (
        len(runs), "" if len(runs) == 1 else "s")


def say(res):
    return "%s points erased, %d switch%s" % (g(res["erased_total"]), res["switches"], "" if res["switches"] == 1 else "es")


# ------------------------------------------------------------------ the decision (pure)
def active(items, now):
    """The holds, pins or requests that stand now. One whose start or end holds no time does not stand."""
    return [h for h in items if stamp_or(h.get("at"), float("inf")) <= now < stamp_or(h.get("ends"), 0)]


def open_requests(plan, f):
    """Requests still to do: inside their life, and the switcher's log shows no switch to that account since. While
    that log cannot be read (None), no request is acted on: nobody can say that it was not done already."""
    out, log = [], f.get("switches")
    for q in active(plan["requests"], f["now"]):
        at = stamp(q["at"])
        done = log is None or q["to"] == f.get("live") or any(
            s.get("to") == q["to"] and stamp_or(s.get("ts"), 0) >= at for s in log)
        if not done:
            out.append(q)
    return out


def decide(plan, f, polled=True) -> dict:
    """-> the decision, in the words of the old actuator (do: passive|skip|poll|normal|soft|switch|hold|stop|stopped|
    start; to, account, line, pct_left, warn_line, under, key, why) plus next, pending, week (the counts)."""
    import switching_plan as SP
    now, N = f["now"], plan["numbers"]
    cfg, fr = N["account_end"], N["fresh"]
    hold = active(plan["holds"], now)
    if hold:
        return {"do": "passive", "why": "hold %s until %s: %s" % (hold[0]["id"], pacific(stamp(hold[0]["ends"])),
                                                                  hold[0].get("why") or "no reason given")}
    live = f.get("live")
    if not live:
        return {"do": "skip", "why": "COULD NOT LOOK: the live account is unknown (%s)" % (f.get("live_why") or "the "
                                                                                           "switcher gave no status")}
    rd = readings_of(f)
    env = Env(now, lambda a: (rd.get(a) or {}).get("left"), lambda a: (rd.get(a) or {}).get("reset"),
              age=lambda a: (rd.get(a) or {}).get("age_min"), burn=f.get("burn_h"),
              runs=None if f.get("runs") is None else len(f["runs"]), entry=lambda a: (f.get("entry") or {}).get(a))
    accts = claude_accounts(plan)
    if live not in accts:       # somebody put the machine there by hand: the plan has no line for it and leaves it alone
        return {"do": "normal", "account": live, "to": None, "line": None, "warn_line": None,
                "pct_left": (rd.get(live) or {}).get("last_left"),
                "why": "%s is live and is no account of the plan: it is left alone, with no line and no warning; repair: "
                       "./acct step add %s --use %s --leave <percent> (after adding it to the plan's accounts), or "
                       "./acct switch <account>" % (live, live, live)}
    rules = {a: rule_of(plan, a, env) for a in accts}
    order = order_now(plan, rules)
    state, markers, runs = f.get("state") or {}, f.get("markers") or {}, f.get("runs")
    stopped_here = (state.get("stopped") or {}).get("account") == live

    def take(a):
        """(can take over, fresh enough to act on, why not)."""
        r, rl = rd.get(a) or reading(None, now), rules.get(a)
        if rl is None:
            return False, False, "no step uses it now"
        if not r["ok"]:
            return False, False, "its level reads %s" % r["state"]
        el = entry_line(plan, rl["line"])
        if r["left"] <= el:
            return False, False, "%s%% is not above its entry line %s%%" % (g(r["left"]), g(el))
        age = r["age_min"]
        return True, age is not None and age <= fr["max_age_min"], ""
    can = [a for a in order if a != live and take(a)[0]]
    lr = rd.get(live) or reading(None, now)
    rl = rules.get(live)
    blind = (not lr["ok"] and lr["last_left"] is not None and not lr["reset_passed"]
             and lr["last_left"] <= N["blind_pct"])
    pl = 0.0 if blind else lr["left"]
    burn = f.get("burn_live")
    if rl is None:
        line, warn = standing_line(plan, live) if live in accts else None, None
        if line is None:
            line = N["floor_pct"]
    else:
        line = rl["line"] if can else max(rl["line"], N["last_account_floor_pct"])
        warn = max(AE.warning_line(line, burn, cfg), line + (rl["warn"] or 0))
        ep = state.get("account_end") or {}
        if ep.get("account") == live and ep.get("warn_line") is not None and not (
                ep.get("line") is not None and line < ep["line"]):
            warn = max(warn, ep["warn_line"])       # a warning that fired is not taken back by a slower burn
    base = {"account": live, "line": line, "pct_left": pl if pl is not None else lr["last_left"], "to": None,
            "warn_line": warn, "step": rl["step"] if rl else None}
    rate = f.get("burn_h")

    def out(d, **more):
        d = {**base, **d, **more}
        return SP.drained(d, {"account_end": cfg}, runs)

    # ---- fresh readings before any act
    need, near_old = [], False
    if not lr["ok"] and not blind:
        need.append("%s (live) reads %s" % (live, lr["state"]))
    elif lr["ok"] and warn is not None and pl - warn <= fr["near_pct"]:
        old = cfg["poll_min"] if pl <= warn + 1 else fr["max_age_min"]
        if lr["age_min"] is None or lr["age_min"] > old:
            near_old = pl > warn
            need.append("%s at %s%% is within %s of its %s%% warning line on a %s-min-old reading" % (
                live, g(pl), g(fr["near_pct"]), g(warn), lr["age_min"]))
    for a in accts:
        if a != live and (rd.get(a) or {}).get("reset_passed"):
            need.append("%s's reset has passed and its reading is from before it" % a)

    under = rl is None or (pl is not None and warn is not None and pl <= warn)
    until = bool(rl) and rl["until"] is not None and truth(parse(rl["until"]), env, live) is True
    if not under and not until and not lr["ok"] and not blind:
        if need and not polled:
            return {**base, "do": "poll", "poll": True, "why": "; ".join(need)}
        if lr["last_left"] is None or warn is None or lr["last_left"] <= warn + fr["near_pct"]:
            return {**base, "do": "soft", "why": "%s reads %s and its last level (%s) cannot prove that it is above its "
                                                 "warning line: no new start until it is read" % (
                                                     live, lr["state"], lr["last_left"])}
        return {**base, "do": "normal", "why": "%s reads %s; its last level was %s%%, above its %s%% warning line: "
                                               "it stays" % (live, lr["state"], g(lr["last_left"]), g(warn))}

    def switch_to(a, is_under, why, week=None):
        """The switch to `a`, behind the guards of an act in flight (a pending or failed switcher call)."""
        if not take(a)[1]:
            if not polled:
                return {**base, "do": "poll", "poll": True, "to": a,
                        "why": "%s (the switch target) was read %s min ago" % (a, rd[a]["age_min"])}
            if is_under and stopped_here:
                return {**base, "do": "stopped", "why": "stopped on %s; %s cannot be confirmed after a poll" % (live, a)}
            if is_under:
                return out({"do": "stop", "key": SP.stop_key(live, f["rows"].get(live) or {}, now),
                            "why": "%s is finished and %s cannot be confirmed after a poll" % (live, a)})
            return {**base, "do": "normal", "to": None, "why": "the switch to %s waits: its reading is %s min old "
                                                               "after a poll; %s stays" % (a, rd[a]["age_min"], live)}
        key = SP.switch_key(live, a, f["rows"].get(a))
        m = markers.get(key) or {}
        age = now - stamp_or(m.get("at"), 0)       # a marker with no time is old: it guards nothing
        if m.get("phase") == "failed" and is_under and not stopped_here:
            return out({"do": "stop", "key": SP.stop_key(live, f["rows"].get(live) or {}, now),
                        "why": "the switch %s failed and %s is finished: stop; the switch is tried again from the "
                               "stopped fleet" % (key, live)})
        if m.get("phase") == "pending" and age < SP.STALE_PENDING_S:
            if is_under and stopped_here:
                return {**base, "do": "stopped", "why": "stopped on %s; the switch %s is in flight" % (live, key)}
            if is_under:
                return out({"do": "stop", "key": SP.stop_key(live, f["rows"].get(live) or {}, now),
                            "why": "the switch %s is in flight yet %s is still live at its line: stop" % (key, live)})
            return {**base, "do": "hold", "to": a, "key": key, "why": "the switch %s is in flight" % key}
        return out({"do": "switch", "to": a, "key": key, "under": is_under, "why": why}, week=week)

    # ---- the live account is finished: which account is next
    if under or until:
        ch = choices(plan, f, can, stay=False) if len(can) > 1 else {}
        nxt = best_of(ch, order) if ch else (can[0] if can else None)
        for q in open_requests(plan, f):
            if q["to"] in can:
                nxt = q["to"]
        if nxt is not None:
            how = ("no step uses %s now" % live) if rl is None else (
                "%s at %s%% is at its %s%% warning line (line %s%%)" % (live, g(pl), g(warn), g(line)) if under else
                "the step %s ends: %s" % (rl["step"], rl["until"]))
            why = "%s. Next: %s (%s%% left)" % (how, nxt, g(rd[nxt]["left"]))
            if ch:
                alt = [a for a in ch if a != nxt]
                why += ". Week ahead: %s" % say(ch[nxt]) + "".join(
                    "; with %s next: %s" % (a, say(ch[a])) for a in alt[:1])
            elif len(can) > 1:
                why += ", the first in the step order (no burn rate is measured)"
            if not under and (runs is None or runs):
                return {**base, "do": "normal", "pending": {"to": nxt, "why": "its step ended"},
                        "why": why + ". The switch goes at the first pass with no live run (%s); ./acct switch %s "
                               "--now goes at once" % (runs_say(runs), nxt)}
            return switch_to(nxt, bool(under), why, week=ch.get(nxt))
        if not under:
            return {**base, "do": "normal", "why": "the step %s ended (%s) and no account can take over: %s stays" % (
                rl["step"], rl["until"], live)}
        blockers = "; ".join("%s: %s" % (a, take(a)[2]) for a in accts if a != live) or "no other account in the plan"
        if stopped_here:
            return {**base, "do": "stopped", "why": "stopped on %s; waiting for a reset (%s)" % (live, blockers)}
        unread = [a for a in accts if a != live and rules.get(a) and not (rd.get(a) or {}).get("ok")]
        if unread and not polled:
            return {**base, "do": "poll", "poll": True, "why": "read %s before any stop" % ", ".join(unread)}
        if rl is not None and pl is not None and pl > line:
            return {**base, "do": "soft", "drain": True, "account_end": True,
                    "why": "%s at %s%% is at its %s%% warning line and no account can take over (%s): no new start; "
                           "the fleet stops at its %s%% line" % (live, g(pl), g(warn), blockers, g(line))}
        return out({"do": "stop", "key": SP.stop_key(live, f["rows"].get(live) or {}, now),
                    "why": "no account can take over (%s); %s at %s%% is finished%s" % (
                        blockers, live, "?" if pl is None else g(pl), " (blind meter)" if blind else "")})

    # ---- the live account is not finished: it stays
    if need and not polled:
        return {**base, "do": "poll", "poll": True, "why": "; ".join(need)}
    if near_old and lr["age_min"] is not None and lr["age_min"] > fr["max_age_min"]:
        return {**base, "do": "soft", "why": "%s at %s%% on a %s-min-old reading, within %s points of its %s%% warning "
                                             "line: the level cannot be confirmed after a poll, so no new start until "
                                             "it is read" % (live, g(pl), g(lr["age_min"]), g(fr["near_pct"]), g(warn))}
    if stopped_here:
        if pl <= warn + N["entry_margin_pct"]:
            return {**base, "do": "stopped", "why": "stopped on %s: no start inside its warning zone" % live}
        return {**base, "do": "start", "why": "%s has headroom again after the stop" % live}
    eta = None if not rate else (pl - warn) / rate
    head = "%s live at %s%% (line %s%%, warning at %s%%): it stays" % (live, g(pl), g(line), g(warn))
    head += "" if eta is None else ", about %s h to its warning at %s points an hour" % (g(eta), g(rate))
    for q in open_requests(plan, f):
        ok, _fresh, why_not = take(q["to"])
        if not ok:
            return {**base, "do": "normal", "pending": {"to": q["to"], "why": "requested"},
                    "why": "%s. The requested switch to %s cannot go: %s" % (head, q["to"], why_not)}
        if q.get("now") or (runs is not None and not runs):
            return switch_to(q["to"], False, "requested at %s: switch to %s (%s)" % (
                pacific(stamp(q["at"])), q["to"], q.get("why") or "no reason given"))
        return {**base, "do": "normal", "pending": {"to": q["to"], "why": "requested"},
                "why": "%s. The requested switch to %s goes at the first pass with no live run (%s)" % (
                    head, q["to"], runs_say(runs))}
    pin = [p for p in active(plan["pins"], now) if p["account"] == live]
    ch = choices(plan, f, can)      # {} with no burn rate: week_ahead is the one place that says so
    stay = ch.get(None)
    nxt_ev = next((e for e in (stay or {}).get("events", []) if e["kind"] == "switch"), None)
    nxt = nxt_ev["to"] if nxt_ev else (can[0] if can and not stay else None)
    tail = ". Next: %s" % (nxt or "none (no account can take over: it waits for a reset)")
    if nxt_ev:
        tail += " at about %s" % pacific(nxt_ev["at"])
    if stay is None:
        return {**base, "do": "normal", "next": nxt, "why": head + tail + ". No burn rate is measured: no week ahead, "
                                                                          "and the next account is by step order"}
    best = best_of(ch, order)
    week = ". Week ahead: %s" % say(stay) if stay else ""
    others = {k: v for k, v in ch.items() if k is not None}
    alt = best_of(others, order) if others else None
    if alt is not None and stay:
        gain = stay["cost"] - others[alt]["cost"]
        week += ". Best other choice (switch to %s now): %s, %s (a switch counts %s points)" % (
            alt, say(others[alt]), "not worth leaving %s early" % live if gain < N["switch_cost_pts"] else "better by %s points" % g(gain),
            g(N["switch_cost_pts"]))
    d = {**base, "do": "normal", "next": nxt, "week": stay, "why": head + tail + week}
    if best is None or stay is None:
        return d
    gain = stay["cost"] - ch[best]["cost"]
    if gain < N["switch_cost_pts"]:     # leaving a live account before its line must itself be worth a switch
        return d
    if pin or f.get("hand"):
        return {**d, "why": d["why"] + ". No rescue switch: " + (
            "pinned until %s" % pacific(stamp(pin[0]["ends"])) if pin else
            "the last switch was made by hand, so %s is kept until it is finished (./acct switch %s goes)" % (live, best))}
    drain_h = dig(N, "rescue.drain_h")
    idle = runs is not None and not runs
    delayed = 0.0 if drain_h is None else rate * drain_h   # the work that a drain of that length delays, in points
    rescue = "rescue: leaving %s for %s now betters the week ahead by %s points (switch now: %s; stay: %s)" % (
        live, best, g(gain), say(ch[best]), say(stay))
    if idle:
        return switch_to(best, False, rescue + "; no run is live", week=ch[best])
    # a drain that the actuator has started goes on while the rescue is still worth a switch: no stop and start
    if drain_h is not None and gain >= N["switch_cost_pts"] + (0.0 if f.get("draining") else delayed):
        return switch_to(best, False, rescue + "; %s: no new start while they finish, at most %s h, then the switch "
                         "(the wait delays about %s points of work)" % (runs_say(runs), g(drain_h), g(delayed)),
                         week=ch[best])
    return {**d, "pending": {"to": best, "why": "rescue", "gain_pts": round(gain, 1)},
            "why": d["why"] + ". The switch to %s goes at the first pass with no live run (%s); no start is refused "
                              "for %s points; ./acct switch %s --now goes at once" % (best, runs_say(runs), g(gain), best)}


# ------------------------------------------------------------------ Burn Mode (pure)
def burn_mode(plan, f) -> dict:
    """The state that other programs read. Per account: on, off or unmeasured, the target burn and the points at risk."""
    N, now = plan["numbers"], f["now"]
    bm = N["burn_mode"]
    rd = readings_of(f)
    rd["codex"] = f.get("codex") or reading(None, now)
    env = Env(now, lambda a: (rd.get(a) or {}).get("left"), lambda a: (rd.get(a) or {}).get("reset"),
              entry=lambda a: (f.get("entry") or {}).get(a))
    out = {}
    names = [a for a, c in plan["accounts"].items() if c["kind"] == "meter" or a == f.get("live")]
    for a in names:
        r, rl = rd.get(a), None
        if r is None:
            continue
        rl = rule_of(plan, a, env)
        burn = f.get("burn_h") if plan["accounts"][a]["kind"] == "claude" else r.get("burn_h")
        h = None if r.get("reset") is None else (r["reset"] - now) / 3600
        if rl is None:
            out[a] = {"state": "off", "why": "no step uses %s now" % a}
        elif not r["ok"] or h is None:
            out[a] = {"state": "unmeasured", "why": "the level or the reset of %s is not measured (%s)" % (a, r["state"])}
        elif h > bm["window_h"]:
            out[a] = {"state": "off", "why": "%s resets in %s h, outside the %s h window" % (a, g(h), g(bm["window_h"]))}
        else:
            usable = max(0.0, r["left"] - rl["line"])
            need = usable / h if h > 0 else None
            row = {"usable_pts": round(usable, 1), "line": rl["line"], "hours_to_reset": round(h, 2),
                   "ends": iso(r["reset"]), "target_burn_pct_h": None if need is None else round(need, 2),
                   "measured_burn_pct_h": None if burn is None else round(burn, 2)}
            if burn is None:
                out[a] = {**row, "state": "unmeasured", "why": "%s has %s usable points and %s h to its reset, but no "
                                                                 "burn rate is measured" % (a, g(usable), g(h))}
            else:
                risk = usable - burn * h
                on = risk >= bm["min_at_risk_pts"]
                out[a] = {**row, "state": "on" if on else "off", "at_risk_pts": round(max(0.0, risk), 1),
                          "why": "%s: %s usable points above its %s%% line, %s h to its reset; at %s points an hour %s "
                                 "would be erased%s" % (a, g(usable), g(rl["line"]), g(h), g(burn), g(max(0.0, risk)),
                                                        "; the burn that uses them all is %s points an hour" % g(need)
                                                        if on else "")}
    load, n = f.get("load"), f.get("ncpu") or 1
    cap = bm["max_load_per_core"] * n
    raise_ok = load is not None and load <= cap
    return {"at": iso(now), "accounts": out, "raise_ok": raise_ok,
            "load": load, "load_why": "UNMEASURED load: no raise" if load is None else (
                "machine load %s is %s the %s that %s cores carry" % (g(load), "under" if raise_ok else "over", g(cap), n)),
            "on": sorted(a for a, v in out.items() if v["state"] == "on")}


def can_use(plan, f, a):
    """May our work send `a` a job now? -> (OK | NO | COULD_NOT_LOOK, one line)."""
    now = f["now"]
    rd = readings_of(f)
    rd["codex"] = f.get("codex") or reading(None, now)
    if a not in plan["accounts"]:
        return COULD_NOT_LOOK, "COULD NOT LOOK: %s is no account of the plan" % a
    r = rd.get(a) or reading(None, now)
    env = Env(now, lambda x: (rd.get(x) or {}).get("left"), lambda x: (rd.get(x) or {}).get("reset"))
    rl = rule_of(plan, a, env)
    if rl is None:
        return NO, "NO: no step uses %s now" % a
    if not r["ok"]:
        return COULD_NOT_LOOK, "COULD NOT LOOK: %s reads %s (%s)" % (a, r["state"], r.get("why") or "no cause given")
    if r["left"] > rl["line"]:
        return OK, "yes: %s has %s%% left, over its %s%% line%s" % (
            a, g(r["left"]), g(rl["line"]), " (reset day: the line is lifted)" if rl["reset_day"] else "")
    return NO, "NO: %s has %s%% left, at or under its %s%% line" % (a, g(r["left"]), g(rl["line"]))


# ------------------------------------------------------------------ the measures (pure)
def week_of(t) -> str:
    d = datetime.fromtimestamp(t, TZ)
    return (d - timedelta(days=d.weekday())).strftime("%Y-%m-%d")


def measures(rows, switches, line_at, since=None):
    """-> {week (its Monday): {"erased": {account: points | "UNMEASURED: why"}, "left_at_reset": {...}, "switches": n}}.
    A reset is seen where an account's reset time moves on by days. The level at a reset is its last MEASURED reading
    before it; none inside 6 h before the reset is UNMEASURED, never 0. line_at(account, time) is the leave line then."""
    out, per = {}, {}
    for r in rows or []:
        if isinstance(r, dict) and r.get("source") == "MEASURED" and is_num(r.get("week_pct_used")):
            t, rs = stamp(r.get("measured_at")), stamp(r.get("week_resets_at"))
            if t is not None and rs is not None:
                per.setdefault(r["account"], []).append((t, float(r["week_pct_used"]), rs))
    for a, rd in per.items():
        rd.sort()
        for (ta, ua, ra), (tb, _ub, rb) in zip(rd, rd[1:]):
            if rb - ra <= 86400 or tb < ra:     # the same week, or a reset time that only moved a little
                continue
            if since is not None and ra < since:
                continue
            w = out.setdefault(week_of(ra), {"erased": {}, "left_at_reset": {}, "switches": 0, "resets": {}})
            w["resets"][a] = iso(ra)
            if ra - ta > 6 * 3600:
                w["erased"][a] = w["left_at_reset"][a] = "UNMEASURED: the last reading is %s h before the reset" % g(
                    (ra - ta) / 3600)
                continue
            left, line = 100 - ua, line_at(a, ra)
            w["left_at_reset"][a] = round(left, 1)
            w["erased"][a] = "UNMEASURED: no line known" if line is None else round(max(0.0, left - line), 1)
    for s in switches or []:
        t = stamp(s.get("ts"))
        if t is not None and (since is None or t >= since):
            out.setdefault(week_of(t), {"erased": {}, "left_at_reset": {}, "switches": 0, "resets": {}})["switches"] += 1
    return dict(sorted(out.items()))


def runs_at_switches(log) -> dict:
    """{week: {"switches": n, "runs": the live runs at those passes, "unread": passes whose runs could not be read}}
    from this tool's own log: the passes where it decided a switch (not a shadow pass). Work wasted by switching."""
    out = {}
    for r in log:
        t = stamp(r.get("at"))
        if t is None or r.get("do") != "switch" or r.get("shadow"):
            continue
        w = out.setdefault(week_of(t), {"switches": 0, "runs": 0, "unread": 0})
        w["switches"] += 1
        if is_num(r.get("runs")):
            w["runs"] += r["runs"]
        else:
            w["unread"] += 1
    return out


def own_log() -> list:
    out = []
    try:
        for ln in (plan_dir() / "log.jsonl").read_text().splitlines():
            try:
                out.append(json.loads(ln))
            except ValueError:
                continue
    except FileNotFoundError:
        pass
    return out


# ------------------------------------------------------------------ the old plan file, read once
def convert_legacy(legacy: dict, seed: dict, now=None) -> dict:
    """switching_plan.json as a plan of this schema: each standing account a step, each dated exception a temporary
    step in front. now: exceptions that ended before it are left out."""
    N = copy.deepcopy(seed["numbers"])
    N["account_end"] = {k: v for k, v in legacy["account_end"].items() if not k.startswith("_")}
    N["fresh"] = {k: v for k, v in legacy["fresh"].items() if not k.startswith("_")}
    N["floor_pct"] = legacy["floors"]["switch_away_pct_left"]
    N["last_account_floor_pct"] = legacy["floors"]["wait_pct_left"]
    N["blind_pct"] = legacy["floors"].get("blind_zero_pct", N["blind_pct"])
    N["entry_margin_pct"] = legacy.get("soft_margin_pct", N["entry_margin_pct"])
    order = list(legacy["order"])
    accounts = {a: {"kind": "claude"} for a in order}
    accounts.update({a: {"kind": "meter"} for a in seed.get("meter_steps", {})})

    def standing(a):
        c = legacy["accounts"].get(a) or {}
        s = {"name": a, "use": a, "leave": c.get("leave_pct_left", N["floor_pct"])}
        if c.get("window_h_after_reset") is not None:
            s["when"] = "hours_since_reset <= %g" % c["window_h_after_reset"]
        return s
    steps = []
    for e in legacy.get("exceptions") or []:
        if not isinstance(e, dict) or stamp(e.get("until")) is None or (now is not None and stamp(e["until"]) <= now):
            continue
        for a in e.get("order") or order:
            c = (e.get("accounts") or {}).get(a) or {}
            s = standing(a)
            s.update(name="%s.%s" % (e["id"], a), **{"from": e["from"], "ends": e["until"]})
            if "leave_pct_left" in c:
                s["leave"] = c["leave_pct_left"]
            if "window_h_after_reset" in c:
                s.pop("when", None)
                if c["window_h_after_reset"] is not None:
                    s["when"] = "hours_since_reset <= %g" % c["window_h_after_reset"]
            if e.get("ends_at_reset_of"):
                s["ends_at_reset_of"] = e["ends_at_reset_of"]
            s["why"] = "from switching_plan.json exception %s" % e["id"]
            steps.append(s)
    for a in order:
        steps.append({**standing(a), "why": "from switching_plan.json (standing)"})
    for a, lv in (seed.get("meter_steps") or {}).items():
        if lv is not None:
            steps.append({"name": a, "use": a, "leave": lv, "why": seed.get("meter_why", "")})
    return {"schema": 1, "rev": 0, "accounts": accounts, "steps": steps, "holds": [], "pins": [], "requests": [],
            "numbers": N, "ledger_item": seed.get("ledger_item")}


# ------------------------------------------------------------------ printing
def account_lines(plan, f) -> list:
    """One line for each account of the plan, as what is LEFT; never what is used; an absent one says so."""
    now = f["now"]
    rd = readings_of(f)
    rd["codex"] = f.get("codex") or reading(None, now)
    env = Env(now, lambda a: (rd.get(a) or {}).get("left"), lambda a: (rd.get(a) or {}).get("reset"),
              entry=lambda a: (f.get("entry") or {}).get(a))
    out = []
    for a, c in plan["accounts"].items():
        if a == "jpl-genai":
            gs = f.get("genai")
            if not gs:
                out.append("  %-10s UNMEASURED: no timed pass has read it yet" % a)
            elif gs[0] == "absent":
                out.append("  %-10s not on this machine" % a)
            elif gs[0] != "ok":
                out.append("  %-10s UNMEASURED: %s" % (a, gs[1]))
            else:
                out.append("  %-10s %s" % (a, " ".join(str(gs[1]).split())[:120]))
            continue
        r = rd.get(a) or reading(None, now)
        rl = rule_of(plan, a, env)
        rule = "no step uses it now" if rl is None else "step %s, line %s%%%s" % (
            rl["step"], g(rl["line"]), " (reset day)" if rl["reset_day"] else "")
        reset = "reset unknown" if r["reset"] is None else "resets %s (in %s h)" % (
            pacific(r["reset"]), g((r["reset"] - now) / 3600))
        age = "age unknown" if r["age_min"] is None else "%s min old" % g(r["age_min"])
        if r["ok"]:
            lvl = "%s%% left" % g(r["left"])
            mark = "measured, " + age
        elif r["reset_passed"]:
            lvl, mark = "UNMEASURED: its reset has passed and no reading since", age
        elif r["last_left"] is not None:
            lvl, mark = "UNMEASURED now (%s): at most %s%% left" % (r["state"], g(r["last_left"])), age
        else:
            lvl, mark = "UNMEASURED: %s" % (r.get("why") or r["state"]), age
        out.append("  %-10s %s, %s [%s]  %s%s" % (a, lvl, reset, mark, rule, "  LIVE" if a == f.get("live") else ""))
    return out


def next_line(plan, f, d=None) -> str:
    d = d or decide(plan, f)
    return "%s: %s" % (d["do"].upper(), d["why"])


def status_text(plan, f):
    """-> (text, exit). Exit 2 when the live account or its level could not be looked at."""
    d = decide(plan, f)
    live = f.get("live")
    lr = readings_of(f).get(live) if live else None
    rc = OK if (live and lr and (lr["ok"] or d["do"] in ("stop", "stopped", "switch"))) or d["do"] == "passive" \
        else COULD_NOT_LOOK
    runs = f.get("runs")
    out = ["NOW   " + next_line(plan, f, d),
           "      plan rev %s; live runs: %s; last switch %s" % (
               plan.get("rev"), "UNMEASURED (systemd could not be read)" if runs is None else len(runs),
               "by hand" if f.get("hand") else "the plan's or none")]
    bm = burn_mode(plan, f)
    for a, v in bm["accounts"].items():
        out.append("BURN MODE %s: %s. %s" % (a, v["state"].upper(), v["why"]))
    out.append("      a raise of load is %s: %s" % ("allowed" if bm["raise_ok"] else "NOT allowed", bm["load_why"]))
    out.append("ACCOUNTS (what is LEFT)")
    out += account_lines(plan, f)
    if f.get("slow_at"):
        out.append("      codex and jpl-genai were read by the timed pass %s min ago" % g((f["now"] - f["slow_at"]) / 60))
    for kind in ("holds", "pins", "requests"):
        for h in active(plan[kind], f["now"]):
            out.append("%s %s until %s: %s" % (kind[:-1].upper(), h.get("id") or h.get("account") or h.get("to"),
                                               pacific(stamp(h["ends"])), h.get("why") or "no reason given"))
    if f.get("hold_file"):
        out.append("HOLD  a HOLD file made by hand stands in the old engine's folder: no pass acts until it is removed")
    return "\n".join(out), rc


def plan_text(plan, f=None) -> str:
    now = (f or {}).get("now") or time.time()
    out = ["PLAN rev %s (%s)" % (plan.get("rev"), plan_dir() / "plan.json"), "STEPS, in order (the first live step of "
           "an account is its rule; the order says only which account is next):"]
    for i, s in enumerate(plan["steps"], 1):
        bits = ["use %s until %s%% left" % (s["use"], s["leave"]) if is_num(s["leave"]) else
                "use %s until %s points under its level at switch-in" % (s["use"], s["leave"].split("-")[1])]
        if s.get("until"):
            bits.append("or until " + s["until"])
        if s.get("warn") is not None:
            bits.append("warn %s points before" % g(s["warn"]))
        if s.get("when"):
            bits.append("only when " + s["when"])
        if s.get("from"):
            bits.append("from " + pacific(stamp(s["from"])))
        if s.get("ends"):
            bits.append("ends " + pacific(stamp(s["ends"])) + (" (ENDED)" if stamp(s["ends"]) <= now else ""))
        if s.get("ends_at_reset_of"):
            bits.append("ends at the reset of " + s["ends_at_reset_of"])
        out.append("  %d. %-28s %s" % (i, s["name"], "; ".join(bits)))
    for kind in ("holds", "pins", "requests"):
        live = active(plan[kind], now)
        out.append("%s: %s" % (kind.upper(), "none" if not live else "; ".join(
            "%s until %s (%s)" % (h.get("id") or h.get("account") or h.get("to"), pacific(stamp(h["ends"])),
                                  h.get("why") or "no reason given") for h in live)))
    out.append("NUMBERS: " + json.dumps(plan["numbers"], sort_keys=True))
    return "\n".join(out)


def forecast_text(plan, f, rate=None) -> tuple:
    res = week_ahead(plan, f, rate=rate)
    if res is None:
        return "COULD NOT LOOK: the week ahead needs a burn rate (pass --rate), the live account and a reset time", \
            COULD_NOT_LOOK
    out = ["THE WEEK AHEAD at %s points an hour, %s h, from %s live: %s" % (g(res["rate"]), g(res["hours"]), f["live"],
                                                                             say(res))]
    for e in res["events"]:
        if e["kind"] == "switch":
            out.append("  %s  switch %s -> %s (%s)" % (pacific(e["at"]), e["from"], e["to"], e["why"]))
        else:
            out.append("  %s  reset of %s: %s points above its %s line erased" % (
                pacific(e["at"]), e["account"], g(e["erased"]), "?" if e["line"] is None else g(e["line"]) + "%"))
    if res["idle_pts"]:
        out.append("  %s points of burn find no account (every account at its line)" % g(res["idle_pts"]))
    return "\n".join(out), OK


# ------------------------------------------------------------------ the writes (each a pure change of a copy)
def find_step(plan, name):
    for i, s in enumerate(plan["steps"]):
        if s["name"] == name:
            return i
    raise Refused("no step is named %s; repair: ./acct plan lists the names (%s)" % (
        name, ", ".join(s["name"] for s in plan["steps"])))


def first_of(plan, account):
    return next((i for i, s in enumerate(plan["steps"]) if s["use"] == account), len(plan["steps"]))


def value(text):
    if text == "":
        return None
    try:
        return json.loads(text)
    except ValueError:
        return text


def life(a, now) -> dict:
    """The life flags of a command as step fields."""
    out = {}
    if getattr(a, "for_", None):
        out.update({"from": iso(now), "ends": iso(now + span(a.for_))})
    if getattr(a, "until", None) and a.cmd != "step":
        if stamp(a.until) is None:
            raise Refused("`--until %s` is no ISO time; repair: --until 2026-11-25T14:00 (Pacific) or --for 2h" % a.until)
        out.update({"from": iso(now), "ends": iso(stamp(a.until))})
    if getattr(a, "until_reset", None):
        out.update({"from": out.get("from", iso(now)), "ends_at_reset_of": a.until_reset})
    return out


def change_of(a, now):
    """The command line as (a function that changes a copy of the plan, the words of what it did)."""
    c = a.cmd
    if c == "order":
        def fn(p):
            unknown = [x for x in a.accounts if p["accounts"].get(x, {}).get("kind") != "claude"]
            if unknown:
                raise Refused("%s: no Claude account of the plan; repair: one of %s" % (
                    ", ".join(unknown), ", ".join(claude_accounts(p))))
            lf = life(a, now)
            lines = dict(x.split("=", 1) for x in a.line or [])
            if lf:
                tag = "T%d" % (int(p.get("rev") or 0) + 1)
                new = []
                for acc in a.accounts:
                    base = next((s for s in reversed(p["steps"]) if s["use"] == acc), None) or {"leave": p["numbers"]["floor_pct"]}
                    s = {"name": "%s.%s" % (acc, tag), "use": acc, "leave": base["leave"], **lf}
                    if lf.get("ends_at_reset_of") is True:
                        s["ends_at_reset_of"] = acc
                    if base.get("when") and acc not in lines:
                        s["when"] = base["when"]
                    if acc in lines:
                        s["leave"] = value(lines[acc])
                    new.append(s)
                p["steps"] = new + p["steps"]
            else:
                if lines:
                    raise Refused("--line goes with a temporary order; repair: add --until-reset <account> or --for 2h, "
                                  "or use ./acct line")
                rank = {x: i for i, x in enumerate(a.accounts)}
                p["steps"] = sorted(p["steps"], key=lambda s: (
                    2 if p["accounts"][s["use"]]["kind"] != "claude" else 0 if s["use"] in rank else 1,
                    rank.get(s["use"], 0)))
            return p
        return fn, "order " + " ".join(a.accounts)
    if c == "line":
        def fn(p):
            if a.account not in p["accounts"]:
                raise Refused("%s is no account of the plan; repair: one of %s" % (a.account, ", ".join(p["accounts"])))
            lf, lv = life(a, now), value(a.percent)
            if lf.get("ends_at_reset_of") is True:
                lf["ends_at_reset_of"] = a.account
            if lf:
                s = {"name": "%s.T%d" % (a.account, int(p.get("rev") or 0) + 1), "use": a.account, "leave": lv, **lf}
                if a.when:
                    s["when"] = a.when
                p["steps"].insert(first_of(p, a.account), s)
            else:
                idx = [i for i, s in enumerate(p["steps"]) if s["use"] == a.account
                       and not (s.get("from") or s.get("ends") or s.get("ends_at_reset_of"))]
                if idx:
                    p["steps"][idx[-1]]["leave"] = lv
                else:
                    p["steps"].append({"name": a.account, "use": a.account, "leave": lv})
            return p
        return fn, "line %s %s" % (a.account, a.percent)
    if c == "step":
        def fn(p):
            if a.act == "add":
                s = {"name": a.name, "use": a.use, "leave": value(a.leave) if a.leave is not None else None}
                for k in ("warn", "until", "when", "from_", "ends"):
                    v = getattr(a, k)
                    if v is not None:
                        s[k.rstrip("_")] = float(v) if k == "warn" else v
                lf = life(a, now)
                if lf.get("ends_at_reset_of") is True:
                    lf["ends_at_reset_of"] = a.use
                s.update({k: v for k, v in lf.items() if k not in s})
                if a.use not in p["accounts"]:
                    raise Refused("--use %s names no account of the plan (%s)" % (a.use, ", ".join(p["accounts"])))
                p["steps"].insert(place(p, a, first_of(p, a.use)), s)
            elif a.act == "rm":
                del p["steps"][find_step(p, a.name)]
            elif a.act == "move":
                s = p["steps"].pop(find_step(p, a.name))
                p["steps"].insert(place(p, a, len(p["steps"])), s)
            else:
                s = p["steps"][find_step(p, a.name)]
                for kv in a.fields:
                    k, eq, v = kv.partition("=")
                    if not eq or k not in STEP_KEYS - {"name"}:
                        raise Refused("`%s` is no field=value of a step; repair: one of %s" % (
                            kv, ", ".join(sorted(STEP_KEYS - {"name"}))))
                    if v == "":
                        s.pop(k, None)
                    else:
                        s[k] = value(v) if k in ("leave", "warn") else v
            return p
        return fn, "step %s %s" % (a.act, a.name)
    if c == "set":
        def fn(p):
            for kv in a.fields:
                path, eq, v = kv.partition("=")
                parts = path.split(".")
                if not eq or parts[0] not in ("numbers", "steps") or len(parts) < 2:
                    raise Refused("`%s` is not numbers.<key>=<value> or steps.<name>.<field>=<value>" % kv)
                if parts[0] == "steps":
                    if len(parts) != 3:
                        raise Refused("`%s`: a step field is steps.<name>.<field>=<value>" % kv)
                    p["steps"][find_step(p, parts[1])][parts[2]] = value(v)
                    continue
                d = p["numbers"]
                for k in parts[1:-1]:
                    if not isinstance(d.get(k), dict):
                        raise Refused("numbers has no `%s`; repair: ./acct plan prints the numbers" % ".".join(parts[1:]))
                    d = d[k]
                if parts[-1] not in d:
                    raise Refused("numbers has no `%s`; repair: ./acct plan prints the numbers" % ".".join(parts[1:]))
                d[parts[-1]] = value(v)
            return p
        return fn, "set " + " ".join(a.fields)
    if c in ("hold", "pin", "switch"):
        def fn(p):
            lf = life(a, now)
            if c == "hold":
                if "ends" not in lf:
                    raise Refused("a hold needs its end; repair: ./acct hold --for 2h --why \"...\"")
                p.setdefault("holds", []).append({"id": "H%d" % (int(p.get("rev") or 0) + 1), "at": iso(now),
                                                  "ends": lf["ends"], "why": words(a)})
            elif c == "pin":
                p.setdefault("pins", []).append({"account": a.account, "at": iso(now),
                                                 "ends": lf.get("ends") or iso(now + WEEK), "why": words(a)})
            else:
                p.setdefault("requests", []).append({
                    "to": a.account, "at": iso(now), "now": bool(a.now), "why": words(a),
                    "ends": lf.get("ends") or iso(now + (1 if a.now else p["numbers"]["request_default_h"]) * 3600)})
            return p
        return fn, {"hold": "hold", "pin": "pin %s" % getattr(a, "account", ""),
                    "switch": "switch to %s%s" % (getattr(a, "account", ""), " now" if getattr(a, "now", False) else
                                                  " when no run is live")}[c]
    if c == "driver":
        def fn(p):
            p["driver"] = a.which
            return p
        return fn, "driver %s (the timer's pass runs %s)" % (a.which, "this plan" if a.which == "new" else
                                                             "the old engine, with this plan's pick logged beside it")
    if c in ("release", "unpin"):
        kind = "holds" if c == "release" else "pins"

        def fn(p):
            if not active(p[kind], now):
                raise LookupError("NONE: no %s stands" % kind[:-1])
            p[kind] = [h for h in p[kind] if h not in active(p[kind], now)]
            return p
        return fn, c
    raise Refused("`%s` is no write" % c)


def place(p, a, default):
    if getattr(a, "first", False):
        return 0
    if getattr(a, "last", False):
        return len(p["steps"])
    if getattr(a, "before", None):
        return find_step(p, a.before)
    if getattr(a, "after", None):
        return find_step(p, a.after) + 1
    return default


def words(a) -> str:
    return a.owner_said or a.by_card or a.why or a.per_ruling or "no reason given"


def meta_of(a, argv) -> dict:
    return {"cmd": "./acct " + " ".join(argv), "why": a.why, "owner_said": a.owner_said, "by_card": a.by_card,
            "per_ruling": a.per_ruling}


# ------------------------------------------------------------------ the timed pass
def legacy_view(plan, f) -> dict:
    """The numbers of the plan file in the shape that switching_plan._check reads (it reads no rule from this)."""
    rd = readings_of(f)
    env = Env(f["now"], lambda a: (rd.get(a) or {}).get("left"), lambda a: (rd.get(a) or {}).get("reset"),
              entry=lambda a: (f.get("entry") or {}).get(a))
    accts = claude_accounts(plan)
    rules = {a: rule_of(plan, a, env) for a in accts}
    N = plan["numbers"]
    order = order_now(plan, rules)
    return {"order": order if order else accts,
            "accounts": {a: ({"leave_pct_left": rules[a]["line"]} if rules.get(a) else {}) for a in accts},
            "floors": {"switch_away_pct_left": N["floor_pct"], "wait_pct_left": N["last_account_floor_pct"],
                       "blind_zero_pct": N["blind_pct"]},
            "account_end": N["account_end"], "fresh": N["fresh"], "soft_margin_pct": 0,
            # the old actuator's drain before a switch above the line: a rescue's, never a `switch --now`'s
            "pull_drain_max_s": 0 if any(q.get("now") for q in active(plan["requests"], f["now"]))
            else (0 if dig(N, "rescue.drain_h") is None else N["rescue"]["drain_h"]) * 3600,
            "switch_lead_min": 0, "window_margin_min": 0, "exceptions": [], "level_model": None}


def log(rec: dict) -> None:
    d = plan_dir()
    d.mkdir(parents=True, exist_ok=True)
    with open(d / "log.jsonl", "a") as fh:
        fh.write(json.dumps({"at": iso(time.time()), **rec}, sort_keys=True) + "\n")


def publish_state(plan, f, d, shadow) -> None:
    out = plan_dir()
    write_atomic(out / "burn_mode.json", burn_mode(plan, f))
    write_atomic(out / "decision.json", {"at": iso(f["now"]), "shadow": shadow, "rev": plan.get("rev"),
                                         **{k: v for k, v in d.items() if k != "week"}})


def old_pick(SP, f):
    """What the old engine decides on the same frame (it acts on nothing here)."""
    rows = SP.levelled(f["rows"], None)
    mk = f.get("markers") or {}
    return SP.decide(rows, f["live"], f["now"], SP.load_plan(), f.get("state") or {}, mk, polled=True,
                     manual=SP.manual_switch((f.get("switches") or [None])[-1], mk, f["live"]) if f.get("switches") else None,
                     live_runs=f.get("runs"), burn=f.get("burn_live"))


def same_pick(old, new) -> bool:
    """Both keep the live account, or both leave it for the same account, and both refuse or allow new starts."""
    def k(d):
        return (d.get("to") if d["do"] in ("switch", "hold") or d.get("drain_of") == "switch" else None,
                d["do"] in ("soft", "stop", "stopped"))
    return k(old) == k(new)


def tick(shadow=False, dry=False, seams=None) -> int:
    """The timed pass. seams (tests): the keyword arguments of switching_plan.check (meter_fn, poll_fn, runs_fn,
    burn_fn, orders, now, passes); with them no live source is read."""
    import switching_plan as SP
    seams = dict(seams or {})
    plan, why = load_plan()
    if plan is None:
        log({"do": "passive", "why": why, "shadow": shadow})
        print("PASSIVE: " + why)
        return NONE if why.startswith("NONE") else COULD_NOT_LOOK
    if shadow:
        f = seams["frame"] if "frame" in seams else gather(slow=True)
        new = decide(plan, f)
        rec = {"shadow": True, "live": f.get("live"), "new": {k: new.get(k) for k in ("do", "to", "why", "pct_left", "line")},
               "levels": {a: r["last_left"] for a, r in readings_of(f).items()}, "runs": None if f["runs"] is None else len(f["runs"])}
        rc = OK
        if f.get("live") and not f.get("hold_file") and new["do"] != "passive":
            old = old_pick(SP, f)
            rec["old"] = {k: old.get(k) for k in ("do", "to", "why", "pct_left", "line")}
            rec["agree"] = same_pick(old, new)
            rc = OK if rec["agree"] else NO
        log(rec)
        publish_state(plan, f, new, True)
        print(json.dumps(rec, sort_keys=True))
        return rc
    if active(plan["holds"], clock()):
        h = active(plan["holds"], clock())[0]
        log({"do": "passive", "why": "hold %s: %s" % (h["id"], h.get("why"))})
        print("PASSIVE: hold %s until %s" % (h["id"], pacific(stamp(h["ends"]))))
        return OK
    last = {}

    def new_decide(meter, live, now, _plan, state, markers, polled=False, manual=None, live_runs=(), burn=None):
        """switching_plan.decide's place: the plan file is read again at each call, so a write binds inside a pass."""
        p, w = load_plan()
        if p is None:
            return {"do": "passive", "why": w}
        f = frame_for_pass(SP, meter, live, now, state, markers, manual, live_runs, burn, p)
        d = decide(p, f, polled=polled)
        last.update(plan=p, frame=f, decision=d)
        return d

    def new_load_plan(path=None):
        p, _w = load_plan()
        rows = seams["meter_fn"]() if callable(seams.get("meter_fn")) else None
        return legacy_view(p or plan, {"now": seams.get("now") or time.time(), "rows": rows} if rows is not None
                           else gather_light(SP))
    saved = SP.decide, SP.load_plan
    SP.decide, SP.load_plan = new_decide, new_load_plan
    try:
        rc = SP.check(dry=dry, **({"passes": 5} if not seams else {k: v for k, v in seams.items() if k != "frame"}))
    finally:
        SP.decide, SP.load_plan = saved
    if last:
        f, d = last["frame"], last["decision"]
        if not seams:
            slow = gather(slow=True)
            f.update(codex=slow["codex"], genai=slow["genai"], slow_at=slow["slow_at"], load=slow["load"],
                     ncpu=slow["ncpu"])
        log({"do": d["do"], "to": d.get("to"), "live": f.get("live"), "why": d.get("why"), "pct_left": d.get("pct_left"),
             "line": d.get("line"), "runs": None if f["runs"] is None else len(f["runs"]), "rev": last["plan"].get("rev")})
        if not dry:
            publish_state(last["plan"], f, d, False)
            flush_ledger(last["plan"])
    return rc


def timer_pass(seams=None) -> int:
    """What the timer runs. The plan file names the driver: `new` runs tick(); `old` (and a plan file that is missing or
    refused) runs the old engine as it is, and then logs this tool's pick beside it (shadow). The shadow never breaks
    the pass."""
    import switching_plan as SP
    plan, why = load_plan()
    if plan is not None and plan.get("driver", "old") == "new":
        return tick(seams=seams)
    if plan is None:
        print("account_plan: %s; the old engine runs" % why)
    rc = SP.check(**({"passes": 5} if not seams else {k: v for k, v in seams.items() if k != "frame"}))
    if plan is not None:
        try:
            tick(shadow=True, seams=seams)
        except Exception as e:  # noqa: BLE001  a shadow that broke is said, and the old pass stands
            print("account_plan: the shadow pass broke: %s: %s" % (type(e).__name__, e), file=sys.stderr)
    return rc


def gather_light(SP) -> dict:
    import account_usage as AU
    now = time.time()
    return {"now": now, "rows": AU.read_now(now).get("accounts") or {}}


def frame_for_pass(SP, meter, live, now, state, markers, manual, live_runs, burn, plan) -> dict:
    series, sws = series_rows(), SP.switches()
    entry = {s["use"]: entry_level(series, sws, s["use"]) for s in plan["steps"] if isinstance(s.get("leave"), str)}
    return {"now": now, "live": live, "runs": None if live_runs is None else list(live_runs), "rows": meter,
            "burn_live": burn, "burn_h": fleet_burn(series, now, plan["numbers"]["forecast"]["burn_window_h"],
                                                    accounts=set(meter)),
            "switches": sws, "hand": bool(manual), "markers": markers, "state": state, "entry": entry,
            "draining": draining(SP)}


def draining(SP) -> bool:
    """The old actuator's notice says that a drain before a switch above the line is in flight (not an account end)."""
    nt = SP.read_json(SP.OUT / "notice.json", {})
    return isinstance(nt, dict) and nt.get("state") == "soft" and bool(nt.get("drain")) and not nt.get("account_end")


def not_alive(old, new, f) -> str:
    """The steps that a write added and that give no rule now, each with its cause; '' when each is alive."""
    rd = readings_of(f)
    env = Env(f["now"], lambda a: (rd.get(a) or {}).get("left"), lambda a: (rd.get(a) or {}).get("reset"),
              age=lambda a: (rd.get(a) or {}).get("age_min"), burn=f.get("burn_h"),
              entry=lambda a: (f.get("entry") or {}).get(a))
    had, out = {s["name"] for s in old["steps"]}, []
    for s in new["steps"]:
        if s["name"] in had or step_alive(s, env):
            continue
        ra = s.get("ends_at_reset_of")
        if ra and env.reset(ra) is None and stamp(s.get("ends")) is None:
            why = "the reset of %s is not measured, so its end is unknown" % ra
        elif s.get("when") and truth(parse(s["when"]), env, s["use"]) is not True:
            why = "`%s` is %s now" % (s["when"], "unknown" if truth(parse(s["when"]), env, s["use"]) is None else "false")
        else:
            why = "now is outside its life"
        out.append("%s: %s" % (s["name"], why))
    return "; ".join(out)


def flush_ledger(plan) -> None:
    """Each owner-authority change that the ledger has not had goes there as one note. Never raises; a failure leaves
    the plan as it is and the note owed."""
    item, d = plan.get("ledger_item"), plan_dir()
    mark = read_json(d / "ledger_sent.json", {})
    sent = mark.get("rev", 0) if isinstance(mark, dict) else 0
    owed = [h for h in history() if h.get("ledger") == "owed" and h.get("rev", 0) > sent]
    if not owed or not item:
        return
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("account_plan_ingest", str(HERE / "testq" / "ingest.py"))
        ing = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ing)
        for h in owed:
            text = "ACCOUNT PLAN rev %s: %s. %s" % (h["rev"], h.get("cmd"), h.get("owner_said") or h.get("by_card") or "")
            rc, out = ing.rimflow("note", item, "--text", text, "--why", "account plan change (account_plan.py, no AI)")
            if rc:
                print("account_plan: ledger note refused: %s" % str(out)[-300:], file=sys.stderr)
                return
            write_atomic(d / "ledger_sent.json", {"rev": h["rev"]})
        print("account_plan: " + str(ing.publish(len(owed), message="ledger: account plan")))
    except Exception as e:  # noqa: BLE001  tried again at the next pass
        print("account_plan: ledger notes not written: %s: %s" % (type(e).__name__, e), file=sys.stderr)


# ------------------------------------------------------------------ the command line
class Parser(argparse.ArgumentParser):
    def error(self, message):       # argparse would exit 2, which here means could not look
        raise Refused("%s; repair: ./acct --help" % message)


def parser():
    ap = Parser(prog="acct", description="The account plan: one file, one-line commands.")
    sub = ap.add_subparsers(dest="cmd", required=True, parser_class=Parser)
    who = argparse.ArgumentParser(add_help=False)
    for flag in ("--why", "--owner-said", "--by-card", "--per-ruling"):
        who.add_argument(flag, default=None)
    ends = argparse.ArgumentParser(add_help=False)
    ends.add_argument("--for", dest="for_", default=None, help="a life: 90m, 2h, 3d")
    ends.add_argument("--until", default=None, help="a life: an ISO time (Pacific when it has no offset)")
    for name in ("status", "next", "plan", "readings", "burn-mode", "import-legacy"):
        p = sub.add_parser(name, parents=[who] if name == "import-legacy" else [])
        if name == "import-legacy":
            p.add_argument("--from", dest="src", default=str(HERE / "switching_plan.json"))
            p.add_argument("--replace", action="store_true")
    p = sub.add_parser("forecast")
    p.add_argument("--rate", type=float, default=None, help="points an hour (default: the last 24 h)")
    p = sub.add_parser("measures")
    p.add_argument("--weeks", type=int, default=4)
    p = sub.add_parser("can-use")
    p.add_argument("account")
    p = sub.add_parser("tick")
    p.add_argument("--shadow", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p = sub.add_parser("whatif")
    p.add_argument("rest", nargs=argparse.REMAINDER)
    p = sub.add_parser("undo", parents=[who])
    p.add_argument("rev", nargs="?", type=int)
    p = sub.add_parser("order", parents=[who, ends])
    p.add_argument("accounts", nargs="+")
    p.add_argument("--until-reset", nargs="?", const=True, default=None)
    p.add_argument("--line", action="append", help="account=percent, with a temporary order")
    p = sub.add_parser("line", parents=[who, ends])
    p.add_argument("account")
    p.add_argument("percent")
    p.add_argument("--until-reset", nargs="?", const=True, default=None)
    p.add_argument("--when", default=None)
    p = sub.add_parser("step", parents=[who])
    p.add_argument("act", choices=("add", "set", "rm", "move"))
    p.add_argument("name")
    p.add_argument("fields", nargs="*")
    for flag in ("--use", "--leave", "--warn", "--until", "--when", "--ends", "--before", "--after"):
        p.add_argument(flag, default=None)
    p.add_argument("--from", dest="from_", default=None)
    p.add_argument("--for", dest="for_", default=None)
    p.add_argument("--until-reset", "--ends-at-reset", dest="until_reset", nargs="?", const=True, default=None)
    p.add_argument("--first", action="store_true")
    p.add_argument("--last", action="store_true")
    p = sub.add_parser("set", parents=[who])
    p.add_argument("fields", nargs="+")
    p = sub.add_parser("switch", parents=[who, ends])
    p.add_argument("account")
    p.add_argument("--now", action="store_true")
    p = sub.add_parser("pin", parents=[who, ends])
    p.add_argument("account", nargs="?")
    sub.add_parser("unpin", parents=[who])
    sub.add_parser("hold", parents=[who, ends])
    sub.add_parser("release", parents=[who])
    sub.add_parser("pass")
    p = sub.add_parser("driver", parents=[who])
    p.add_argument("which", nargs="?", choices=("old", "new"))
    return ap


WRITES = ("order", "line", "step", "set", "switch", "pin", "unpin", "hold", "release", "driver")


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        return run(argv)
    except Refused as e:
        print("REFUSED: %s" % e)
        return REFUSED
    except LookupError as e:
        print(str(e).strip("'\""))
        return NONE
    except OSError as e:
        print("FAILED: %s: %s" % (type(e).__name__, e))
        return FAILED


def run(argv) -> int:
    a = parser().parse_args(argv)
    now = clock()
    if a.cmd == "tick":
        return tick(shadow=a.shadow, dry=a.dry_run)
    if a.cmd == "pass":
        return timer_pass()
    if a.cmd == "import-legacy":
        legacy, seed = json.loads(Path(a.src).read_text()), json.loads(SEED.read_text())
        old, _w = load_plan()
        if old is not None and not a.replace:
            raise Refused("a plan file stands (rev %s); repair: --replace to write over it (./acct undo brings it back)"
                          % old.get("rev"))
        new = convert_legacy(legacy, seed, now)
        rev, _p = commit(lambda _old: new, {**meta_of(a, argv), "create": True}, base=old)
        print("DONE rev %s: the plan file is written from %s (%d steps)\n%s\nundo: ./acct undo %s" % (
            rev, a.src, len(new["steps"]), plan_dir() / "plan.json", rev))
        return OK
    if a.cmd == "undo":
        hist = history()
        if not hist:
            raise LookupError("NONE: the history has no change to undo")
        rev = a.rev if a.rev is not None else hist[-1]["rev"]
        h = next((x for x in hist if x["rev"] == rev), None)
        if h is None or h.get("before") is None:
            raise LookupError("NONE: no change with rev %s that has a plan before it" % rev)
        later = [x["rev"] for x in hist if x["rev"] > rev]
        # create: the undo also repairs a plan file that a hand edit broke
        new_rev, _p = commit(lambda _old: copy.deepcopy(h["before"]), {**meta_of(a, argv), "undoes": rev, "create": True})
        print("DONE rev %s: the plan is as it was before rev %s%s\nundo: ./acct undo %s" % (
            new_rev, rev, " (this also takes back rev %s)" % ", ".join(map(str, later)) if later else "", new_rev))
        return OK
    plan, why = load_plan()
    if plan is None:
        print(why if why.startswith(("NONE", "COULD NOT LOOK")) else "REFUSED: " + why)
        return NONE if why.startswith("NONE") else COULD_NOT_LOOK if why.startswith("COULD") else REFUSED
    if a.cmd == "driver" and a.which is None:
        print("%s: the timer's pass (./acct pass) runs %s" % (plan.get("driver", "old"), "this plan" if plan.get(
            "driver") == "new" else "the old engine, with this plan's pick logged beside it"))
        return OK
    if a.cmd in WRITES:
        if a.cmd == "pin" and not a.account:
            a.account = gather(now).get("live")
            if not a.account:
                print("COULD NOT LOOK: the live account is unknown; repair: ./acct pin <account>")
                return COULD_NOT_LOOK
        fn, what = change_of(a, now)
        rev, new = commit(fn, meta_of(a, argv))
        f = gather(now)
        dead = not_alive(plan, new, f)
        print("DONE rev %s: %s%s\n%s\nundo: ./acct undo %s" % (
            rev, what, " (NOT ALIVE NOW: %s)" % dead if dead else "", next_line(new, f), rev))
        return OK
    if a.cmd == "whatif":
        rest = [x for x in a.rest if x != "--"]
        b = parser().parse_args(rest)
        if b.cmd not in WRITES:
            raise Refused("whatif takes a write (%s), not `%s`" % (", ".join(WRITES), b.cmd))
        fn, what = change_of(b, now)
        new = fn(copy.deepcopy(plan))
        bad = problems(new)
        if bad:
            raise Refused("; ".join(bad))
        f = gather(now)
        wa, wb = week_ahead(plan, f), week_ahead(new, f)
        print("WHAT IF %s (nothing is written)\nnow:   %s\n       week ahead: %s\nthen:  %s\n       week ahead: %s" % (
            what, next_line(plan, f), say(wa) if wa else "COULD NOT LOOK", next_line(new, f),
            say(wb) if wb else "COULD NOT LOOK"))
        return OK
    f = gather(now)
    if a.cmd == "status":
        text, rc = status_text(plan, f)
        print(text)
        return rc
    if a.cmd == "next":
        d = decide(plan, f)
        print(next_line(plan, f, d))
        return COULD_NOT_LOOK if d["do"] == "skip" else OK
    if a.cmd == "plan":
        print(plan_text(plan, f))
        return OK
    if a.cmd == "readings":
        print("ACCOUNTS (what is LEFT)\n" + "\n".join(account_lines(plan, f)))
        return OK
    if a.cmd == "forecast":
        text, rc = forecast_text(plan, f, a.rate)
        print(text)
        return rc
    if a.cmd == "burn-mode":
        print(json.dumps(burn_mode(plan, f), indent=1))
        return OK
    if a.cmd == "can-use":
        rc, text = can_use(plan, f, a.account)
        print(text)
        return rc
    if a.cmd == "measures":
        return measures_cmd(plan, f, a.weeks)
    return REFUSED


def measures_cmd(plan, f, weeks) -> int:
    import switching_plan as SP
    rows = f.get("series") if "series" in f else series_rows(tail_bytes=10**9)
    sws = f.get("switches") if "switches" in f else SP.switches()
    if rows is None:
        print("COULD NOT LOOK: the reader's series cannot be read (%s)" % AE.SERIES)
        return COULD_NOT_LOOK
    m = measures(rows, sws, lambda a, t: standing_line(plan, a), since=f["now"] - weeks * WEEK)
    if not m:
        print("NONE: no reset and no switch in the last %d weeks of the series" % weeks)
        return NONE
    print("ALLOWANCE ERASED AT RESETS and SWITCHES, per week (Monday), against the lines of the plan as it is now")
    mine = runs_at_switches(own_log())
    for w, v in m.items():
        er = "; ".join("%s %s" % (a, x if isinstance(x, str) else "%s points (%s%% left at its reset)" % (
            g(x), g(v["left_at_reset"][a]))) for a, x in sorted(v["erased"].items())) or "no reset seen"
        k = mine.get(w)
        print("  week of %s: %d switches; %s; erased: %s" % (w, v["switches"], (
            "%d live runs at the plan's %d switches%s" % (k["runs"], k["switches"], ", %d of them with the runs unread"
                                                          % k["unread"] if k["unread"] else "")) if k else
            "the plan made no switch (its log has none)", er))
    wa = week_ahead(plan, f)
    print("FORECAST for the plan now: " + (say(wa) if wa else "COULD NOT LOOK: no burn rate, live account or reset time"))
    return OK


if __name__ == "__main__":
    sys.exit(main())
