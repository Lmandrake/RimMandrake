#!/usr/bin/env python3
"""The account plan: one file, one pure decision, one-line commands (./acct). No model call, no poll in a status.

Page: design/specs/2026-11-24-account-plan-one-file/boundary.md (the promises; selftest_account_plan.py checks each by
name). Design: design.md beside it. Item RIMMANDRAKE_DESIGN_ACCOUNT_PLAN_ONE_FILE_COMMANDED_IN_ONE_LINE.

The rule (owner, 2026-11-24): the live account STAYS live until its own step is finished. The order of the steps says
only which account is next. A switch that rescues allowance from a reset must be worth a switch, and it never stops a
run and never refuses a start. Each decision says its reason in one line.

    ./acct status | next | plan | readings | forecast | measures | burn-mode | can-use A
    ./acct order A B C · line A N · step add|set|rm|move · switch A · pin · unpin · hold --for 2h · release
    ./acct set numbers.K=V · undo [REV] · whatif -- <a write> · init · tick [--dry-run] · pass

The plan file: $RM_ACCOUNT_PLAN_DIR/plan.json (default ~/.local/state/rimmandrake/account_plan), outside every clone:
a write binds at the next read. Levels are read only through account_usage.py; the switch, the save orders and the
pause are account_actuator.py's and account_end.py's, which `tick` drives with this file's decision. The pass always
has rules: the plan file; when that is missing or refused, the last revision that history.jsonl accepted; with no
history, the first plan of account_plan.seed.json. Each such pass says which in its log.
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
STEP_KEYS = {"name", "use", "leave", "schedule", "warn", "until", "when", "from", "ends", "ends_at_reset_of", "why", "by"}
DAYS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")


class Refused(Exception):
    """A fault in what was asked. The text names the fault and its repair; nothing was written."""


def clock() -> float:
    """Now. RM_ACCOUNT_PLAN_NOW names a fixed time for a selftest."""
    return float(os.environ.get("RM_ACCOUNT_PLAN_NOW") or time.time())


def plan_dir() -> Path:
    """The folder of the plan file. A test child (RM_UNDER_SELFTEST) that names no folder of its own gets one that
    does not exist: it reads no plan and can write none, so no test ever reaches the live plan."""
    d = os.environ.get("RM_ACCOUNT_PLAN_DIR")
    if not d and os.environ.get("RM_UNDER_SELFTEST"):
        return Path("/nonexistent/rm_account_plan_of_a_test")
    return Path(d or Path.home() / ".local/state/rimmandrake/account_plan")


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


def problems(plan, writing=False) -> list:
    """Every fault of the plan, each with its repair. [] is a valid plan. writing: a write is checked, so a line
    schedule must read; at a read a schedule that cannot be read is no fault of the plan (the pass is could not look on
    that step, and uses its highest percent: line_of_step)."""
    out = []
    if not isinstance(plan, dict) or plan.get("schema") != 1:
        return ["the plan is not a schema 1 object; repair: ./acct undo, or ./acct init"]
    accts = plan.get("accounts")
    if not isinstance(accts, dict) or not accts:
        return ["`accounts` is missing; repair: ./acct undo"]
    for a, c in accts.items():
        if not isinstance(c, dict) or c.get("kind") not in ("claude", "meter"):
            out.append(f"account {a}: `kind` must be claude or meter")
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
        if s.get("schedule") is not None:
            if not isinstance(s["schedule"], str) or not is_num(lv):
                out.append(f"{tag}: a step with a line schedule holds its text in `schedule` and its highest percent in "
                           f"`leave`; repair: ./acct line {a} --schedule \"...\"")
            elif writing:
                try:
                    pts = parse_schedule(s["schedule"], lo)
                    if lv != max(x["pct"] for x in pts):
                        out.append(f"{tag}: `leave` must be the highest percent of its line schedule; repair: ./acct "
                                   f"line {a} --schedule \"{s['schedule']}\"")
                except Refused as e:
                    out.append(f"{tag}: {e}")
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
    ms = plan.get("machines", {})
    if not isinstance(ms, dict):
        out.append("`machines` must be an object; repair: ./acct undo")
    else:
        for m, c in ms.items():
            if not re.fullmatch(r"[A-Za-z0-9_.\-]+", str(m)) or not isinstance(c, dict) or not re.fullmatch(
                    r"[A-Za-z0-9_.@\-]+", str(c.get("ssh") or "")):
                out.append("machine %s: needs `ssh`, the ssh name of that machine; repair: ./acct machine add %s --ssh "
                           "<name>" % (m, m))
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
        return None, f"NONE: no plan file at {p}; repair: ./acct init"
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


def first_plan() -> dict:
    """The first plan file (account_plan.seed.json `plan`): what `./acct init` writes, and the rules of a pass that has
    no plan file and no history."""
    return copy.deepcopy(json.loads(SEED.read_text())["plan"])


def plan_in_force():
    """-> (plan, None) from the plan file; when it is missing or refused, (the last revision that history.jsonl
    accepted, or else the first plan, the cause and which one): the pass and the readers always have rules, and say
    which. (None, why) only when the file could not be read (COULD NOT LOOK) or nothing at all is valid."""
    plan, why = load_plan()
    if plan is not None or why.startswith("COULD NOT LOOK"):
        return plan, why if plan is None else None
    for h in reversed(history()):
        cand = h.get("after")
        if isinstance(cand, dict) and not problems(cand):
            return cand, "%s; the pass runs on rev %s, the last revision that history.jsonl accepted" % (why, cand.get("rev"))
    try:
        cand = first_plan()
    except (OSError, ValueError, KeyError) as e:
        return None, "%s; and the first plan in %s cannot be read: %s" % (why, SEED, e)
    bad = problems(cand)
    if bad:
        return None, "%s; and the first plan in %s is refused: %s" % (why, SEED, "; ".join(bad[:3]))
    return cand, "%s; the pass runs on the first plan of %s (no history)" % (why, SEED.name)


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
        if isinstance(new, dict):
            new.pop("driver", None)     # the key of the retired engine switch (until 2026-11-27): it means nothing now
        bad = problems(new, writing=True)
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
    import account_actuator as ACT
    now = now or time.time()
    ans = AL.read(exe_path=ACT.CA)
    live = AL.status_of(ans).get("live")
    rows = AU.read_now(now).get("accounts")
    if rows is None:        # the reader has no latest.json: every level then reads UNMEASURED, by name, never 0
        rows = {}
    try:
        runs = ACT.live_detached_runs()
    except Exception:  # noqa: BLE001  unreadable runs count as live
        runs = None
    markers, sws = ACT.read_markers(), ACT.switches()
    plan, _why = load_plan()
    cfg = dig(plan or {}, "numbers.account_end") or first_plan()["numbers"]["account_end"]
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
    if plan and any(entry_points(s) is not None for s in plan["steps"]):
        for s in plan["steps"]:
            if entry_points(s) is not None:
                entry[s["use"]] = entry_level(series, sws, s["use"])
    try:
        load = os.getloadavg()[0]
    except OSError:
        load = None
    return {"now": now, "live": live, "live_why": AL.why_of(ans) if not live else "", "runs": runs,
            "rows": rows, "burn_live": ACT.burn_now(live, rows, now, cfg, ACT.default_burn) if live else None,
            "burn_h": fleet_burn(series, now, dig(plan or {}, "numbers.forecast.burn_window_h") or 24,
                                 accounts=set(rows)),
            "switches": sws, "hand": bool(ACT.manual_switch((sws or [None])[-1], markers, live)) if sws else False,
            "draining": draining(ACT),
            "notice": read_json(notice_dir() / "notice.json"), "published": read_json(plan_dir() / "decision.json"),
            "markers": markers, "state": ACT.load_state(), "hold_file": (ACT.OUT / "HOLD").exists(),
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


def frame_env(f):
    """The Env of a frame's readings, Codex's included."""
    rd = readings_of(f)
    rd["codex"] = f.get("codex") or reading(None, f["now"])
    return Env(f["now"], lambda a: (rd.get(a) or {}).get("left"), lambda a: (rd.get(a) or {}).get("reset"),
               entry=lambda a: (f.get("entry") or {}).get(a))


# ------------------------------------------------------------------ the line schedule (pure; page
# design/specs/2026-11-27-account-line-schedule/boundary.md)
# Not a limit (it ends no work): a tolerance. Danger of a small one: a reset that moves by minutes, or by the hour of a
# daylight-saving change, puts the point at the reset at the start of the week and the schedule reads backwards.
# Danger of a large one: a point meant hours after the reset is read as at the reset. Evidence: the meter moves a reset
# by up to a minute (account_end.RESET_JITTER_S 15 min); a reset fixed in UTC moves one hour on the Pacific clock.
SNAP_S = 2 * 3600
# Ends no work: the command refuses a longer list with the repair. Danger: a schedule that nobody reads in one line.
MAX_POINTS = 14
DAY_OF = {**{d: i for i, d in enumerate(DAYS)},
          **{d: i for i, d in enumerate(("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"))},
          "tues": 1, "weds": 2, "thur": 3, "thurs": 3}
POINT_RX = re.compile(r"([A-Za-z]+)\.?\s+(\d{1,2})(?::(\d\d))?\s*([AaPp][Mm])?\s*=\s*(-?\d+(?:\.\d+)?)\s*%?\s*([A-Za-z]+)?")
SCHED_HELP = 'a weekday, a Pacific time, = a percent, and hold or ramp, in the order of the week from the reset: ' \
             '--schedule "Sat 23:59=40 hold; Tue 13:30=0 ramp"'
_SCHED = {}


def parse_schedule(text, floor=0.0) -> list:
    """The points of a line schedule, in the order typed: [{day, min, pct, how, text}]. Refused with the reason and
    the repair. floor: the lowest percent a point may have (a Claude account's floor)."""
    if not isinstance(text, str):
        raise Refused("a line schedule is a text, not %r; repair: %s" % (text, SCHED_HELP))
    parts = [x.strip() for x in text.split(";") if x.strip()]
    if not parts:
        raise Refused("the line schedule has no point; repair: %s" % SCHED_HELP)
    if len(parts) > MAX_POINTS:
        raise Refused("the line schedule has %d points, more than %d; repair: fewer points" % (len(parts), MAX_POINTS))
    pts = []
    for i, x in enumerate(parts):
        m = POINT_RX.fullmatch(x)
        if not m:
            raise Refused("`%s` cannot be read as a point; repair: %s" % (x, SCHED_HELP))
        day = DAY_OF.get(m.group(1).lower())
        if day is None:
            raise Refused("`%s`: %s is no weekday; repair: mon, tue, wed, thu, fri, sat or sun" % (x, m.group(1)))
        hh = int(m.group(2))
        mm = int(m.group(3)) if m.group(3) is not None else 0           # `Sat 9` is 9:00
        half = m.group(4).lower() if m.group(4) is not None else ""      # no am/pm: a 24-hour clock
        if half and not 1 <= hh <= 12:
            hh = 99
        elif half:
            hh = hh % 12 + (12 if half == "pm" else 0)
        if not (0 <= hh <= 23 and 0 <= mm <= 59):
            raise Refused("`%s`: %s is no time; repair: 0:00 to 23:59, or 1:30pm" % (x, x.split("=")[0].split(None, 1)[1].strip()))
        pct = float(m.group(5))
        if not 0 <= pct <= 100:
            raise Refused("`%s`: a percent is 0 to 100, not %s; repair: a percent from 0 to 100" % (x, g(pct)))
        if pct < floor:
            raise Refused("`%s`: %s%% is under the floor %s%% (a Claude account is never taken under it); repair: a percent "
                          "of %s or more" % (x, g(pct), g(floor), g(floor)))
        how = m.group(6).lower() if m.group(6) is not None else "hold"     # no word: hold
        if how not in ("hold", "ramp"):
            raise Refused("`%s`: `%s` is neither hold nor ramp; repair: %s" % (x, m.group(6), SCHED_HELP))
        if i == 0 and how == "ramp":
            raise Refused("`%s`: a ramp runs from the point before it, and the first point has no point before it; "
                          "repair: make the first point hold (the line from the reset), or put a point before it" % x)
        pts.append({"day": day, "min": hh * 60 + mm, "pct": pct, "how": how, "text": x})
    span = 0
    for a, b in zip(pts, pts[1:]):
        gap = ((b["day"] * 1440 + b["min"]) - (a["day"] * 1440 + a["min"])) % (7 * 1440)
        if gap == 0:
            raise Refused("`%s` and `%s` are at the same moment; repair: keep one of them" % (a["text"], b["text"]))
        span += gap
    if span >= 7 * 1440:
        raise Refused("the points run past a week (%s days from the first to the last, each after the one before); "
                      "repair: type the points in the order of the week from the reset" % g(span / 1440))
    return pts


def schedule_points(text):
    """parse_schedule with a cache, at a read: -> (points, None) or (None, why)."""
    if text not in _SCHED:
        try:
            _SCHED[text] = (parse_schedule(text), None)
        except Refused as e:
            _SCHED[text] = (None, str(e))
    return _SCHED[text]


def next_moment(p, after):
    """The first moment after `after` with the weekday and the Pacific clock of point p."""
    d0 = datetime.fromtimestamp(after, TZ).date()
    for k in range(9):
        d = d0 + timedelta(days=k)
        if d.weekday() != p["day"]:
            continue
        t = datetime(d.year, d.month, d.day, p["min"] // 60, p["min"] % 60, tzinfo=TZ).timestamp()
        if t > after:
            return t
    raise ValueError("no moment for %r after %s" % (p, after))     # cannot happen: a weekday comes in 7 days


def place_schedule(pts, reset):
    """Each point's moment in the account's week (reset - 7 days, reset]: [{at, raw, outside, snapped}]. The first point
    at its first moment after the reset began the week (SNAP_S of leeway), each next one after the point before; a
    point up to SNAP_S past the reset is at the reset; one further past is outside the week."""
    key = (tuple((p["day"], p["min"], p["pct"], p["how"]) for p in pts), reset)
    got = _SCHED.get(key)
    if got is not None:
        return got
    start, out, prev = reset - WEEK, [], None
    for i, p in enumerate(pts):
        raw = next_moment(p, start - SNAP_S if i == 0 else prev)
        at, snapped = raw, 0.0
        if i == 0 and raw < start:
            at, snapped = start, start - raw
        if raw > reset and raw - reset <= SNAP_S:
            at, snapped = reset, raw - reset
        out.append({"at": at, "raw": raw, "outside": raw - reset > SNAP_S, "snapped": snapped})
        prev = raw
    if len(_SCHED) > 4096:      # a cache, not a limit: a long sweep sees many resets
        _SCHED.clear()
    _SCHED[key] = out
    return out


def schedule_at(pts, reset, t) -> dict:
    """The line of the schedule at t, in the week that ends at `reset` (or the week of t, when t is outside it).
    -> {pct, next, next_at, points: [...], notes: [...], reset}."""
    while t > reset:
        reset += WEEK
    while t <= reset - WEEK:
        reset -= WEEK
    pl = place_schedule(pts, reset)
    times = [x["at"] if not x["outside"] else x["raw"] for x in pl]
    j = next((i for i, x in enumerate(times) if x >= t), None)
    if j is None:
        pct = pts[-1]["pct"]
    elif j == 0 or pts[j]["how"] != "ramp" or times[j] <= times[j - 1]:
        pct = pts[j]["pct"]
    else:
        a, b = times[j - 1], times[j]
        pct = pts[j - 1]["pct"] + (pts[j]["pct"] - pts[j - 1]["pct"]) * (t - a) / (b - a)
    pct = round(pct, 2)
    if j is None or times[j] > reset:
        end = reset
        nxt = "held until the reset %s, then %s%% again" % (pacific(reset), g(pts[0]["pct"])) if j is None or \
            pts[j]["how"] != "ramp" else "a ramp towards %s%% at %s, cut by the reset %s (there %s%%)" % (
                g(pts[j]["pct"]), pacific(times[j]), pacific(reset), g(round(pts[j - 1]["pct"] + (
                    pts[j]["pct"] - pts[j - 1]["pct"]) * (reset - times[j - 1]) / (times[j] - times[j - 1]), 1)))
    elif pts[j]["how"] == "ramp" and j > 0:
        end = times[j]
        nxt = "on a ramp to %s%% at %s" % (g(pts[j]["pct"]), pacific(times[j]))
    else:
        end = times[j]
        k = j + 1
        if k < len(pts) and times[k] <= reset + SNAP_S:
            then = ("then a ramp to %s%% at %s" % (g(pts[k]["pct"]), pacific(min(times[k], reset))) if pts[k]["how"] == "ramp"
                    else "then %s%% until %s" % (g(pts[k]["pct"]), pacific(min(times[k], reset))))
        else:
            then = "then %s%% until the reset %s" % (g(pts[j]["pct"]), pacific(reset)) if k >= len(pts) else \
                "then %s (outside the week)" % pts[k]["text"]
        nxt = "held until %s, %s" % (pacific(times[j]), then)
    notes = []
    for p, x in zip(pts, pl):
        if x["outside"]:
            notes.append("%s is outside the week: the reset %s comes %s h before it; the line follows the typed weekdays"
                         % (p["text"], pacific(reset), g((x["raw"] - reset) / 3600)))
        elif x["snapped"] >= 60:
            notes.append("%s is taken as the reset (%s min from it)" % (p["text"], g(x["snapped"] / 60)))
    return {"pct": pct, "next": nxt, "next_at": end, "reset": reset, "notes": notes,
            "points": [{"text": p["text"], "at": x["at"], "outside": x["outside"],
                        "h_before_reset": round((reset - (x["raw"] if x["outside"] else x["at"])) / 3600, 1)}
                       for p, x in zip(pts, pl)]}


def entry_points(s):
    """N of a step whose leave is entry-N (N points under the level at switch-in), else None."""
    lv = s.get("leave")
    return float(lv.split("-", 1)[1]) if isinstance(lv, str) else None


def line_of_step(plan, s, a, env, numeric_only=False):
    """THE one function that gives the leave line of step s of account a at env.now: every reader of a line goes
    through it (rule_of, standing_line). -> {line, note, schedule}, or None when the line cannot be known (entry-N
    with no level at switch-in; numeric_only: an entry-N step). A schedule that cannot be read, or an account whose
    reset is not measured: the step's leave (the schedule's highest percent), and a note that starts COULD NOT LOOK."""
    lv = s["leave"]
    if s.get("schedule") is not None:
        pts, why = schedule_points(s["schedule"])
        rs = None if env is None else env.reset(a)
        hi = lv if is_num(lv) else 100.0
        if pts is None or rs is None:
            return {"line": hi, "schedule": None, "note": "COULD NOT LOOK: the line schedule of %s %s: its highest "
                    "percent, %s%%, holds" % (a, "cannot be read (%s)" % why if pts is None else
                                              "cannot be placed: the reset is not measured", g(hi))}
        info = schedule_at(pts, rs, env.now)
        return {"line": info["pct"], "schedule": info, "note": "; ".join(info["notes"]) or None}
    if isinstance(lv, str):
        e = None if (numeric_only or env is None) else env.entry_left(a)
        if e is None:
            return None         # the level at switch-in is unknown: this step gives no permission
        return {"line": max(plan["numbers"]["floor_pct"], e - entry_points(s)), "schedule": None, "note": None}
    return {"line": lv, "schedule": None, "note": None}


def put_schedule(p, s, text):
    """A write: step s of plan p takes the schedule text (parsed and refused here), and its leave the highest percent."""
    floor = p["numbers"]["floor_pct"] if p["accounts"][s["use"]]["kind"] == "claude" else 0.0
    pts = parse_schedule(text, floor)
    s["schedule"] = text
    s["leave"] = max(x["pct"] for x in pts)
    return pts


def pacific_point(t) -> str:
    """A moment as a point of a schedule: `Sat 23:59` (Pacific)."""
    return datetime.fromtimestamp(t, TZ).strftime("%a %H:%M")


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
    """The first alive step that uses `a`, with its leave line in force (line_of_step): {step, line, warn, until,
    reset_day, note, schedule}; None. A step with a line schedule keeps the schedule's line on the reset day: the
    schedule says the line at every moment up to the reset."""
    N = plan["numbers"]
    kind = plan["accounts"][a]["kind"]
    for s in plan["steps"]:
        if s["use"] != a or not step_alive(s, env):
            continue
        ln = line_of_step(plan, s, a, env)
        if ln is None:
            continue        # the level at switch-in is unknown: this step gives no permission
        line = ln["line"] + (N["evening_share_pct"] if kind == "claude" else 0)
        rd, h = N["reset_day"], env.to_reset_h(a)
        day = s.get("schedule") is None and a in rd["accounts"] and h is not None and 0 < h <= rd["hours"]
        if day:
            dl = rd["line"][kind]
            line = min(line, N["floor_pct"] if dl == "floor" else dl)
        out = {"step": s["name"], "line": line, "warn": s.get("warn"), "until": s.get("until"), "reset_day": day}
        if s.get("schedule") is not None:
            out.update(note=ln["note"], schedule=ln["schedule"])
        return out
    return None


def standing_line(plan, a, env=None):
    """The leave line of the last step that uses `a` (its standing step), whatever its `when`, at env.now (a line
    schedule needs env; with none it gives its highest percent); None with no step."""
    for s in reversed(plan["steps"]):
        if s["use"] == a:
            ln = line_of_step(plan, s, a, env, numeric_only=True)
            if ln is not None:
                return ln["line"]
    return None


def order_now(plan, rules):
    out = []
    for s in plan["steps"]:
        a = s["use"]
        if plan["accounts"][a]["kind"] == "claude" and rules.get(a) and rules[a]["step"] == s["name"] and a not in out:
            out.append(a)
    return out


def entry_line(plan, rl):
    """A switch never lands on an account (its rule is rl) at or under this: it would be inside its own warning zone."""
    N = plan["numbers"]
    return max(AE.warning_line(rl["line"], None, N["account_end"]), rl["line"] + (rl["warn"] or 0)) + N["entry_margin_pct"]


def ended(rl, env, a):
    """The `until` of the rule of `a` is true: its step is finished."""
    return bool(rl) and rl["until"] is not None and truth(parse(rl["until"]), env, a) is True


def targets(can, rules, env, under):
    """The accounts of `can` that a switch may land on: one whose step has ended (`until`) only where the live account
    is at its own line and no other can take over. Else two ended steps would hand the machine to and fro."""
    return [a for a in can if not ended(rules[a], env, a)] or (can if under else [])


# ------------------------------------------------------------------ the week ahead (pure; the pick and the forecast)
def week_ahead(plan, f, first=None, rate=None, hours=None, step_min=None):
    """One run of the week ahead under the plan: stay on the live account until its step is finished, then the best
    next account; each account refills at its reset. first: an account to switch to now (None: stay). -> {first,
    events, erased: {account: points}, erased_total, switches, idle_pts, cost, rate, hours}, or None when it cannot
    be run (no burn rate, the live account unknown, no reset time). step_min: the step of the run (default
    numbers.forecast.step_min)."""
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
    dt = (step_min or N["forecast"]["step_min"]) * 60
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
    N = plan["numbers"]
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
                line = rl["line"] if rl else standing_line(plan, a, before)
                lost = 0.0 if (line is None or st["left"][a] is None) else max(0.0, st["left"][a] - line)
                st["erased"][a] = st["erased"].get(a, 0.0) + lost
                st["events"].append({"kind": "reset", "at": st["reset"][a], "account": a, "erased": round(lost, 1),
                                     "line": line})
                st["left"][a], st["reset"][a] = 100.0, st["reset"][a] + WEEK
        rules = {a: rule_of(plan, a, env) for a in accts}
        live = st["live"]
        rl = rules.get(live)
        can = [a for a in order_now(plan, rules) if a != live and st["left"][a] is not None
               and st["left"][a] > entry_line(plan, rules[a])]
        if rl is None:
            done, under = True, True
        else:
            line = rl["line"] if can else max(rl["line"], N["last_account_floor_pct"])
            under = st["left"][live] <= line        # used down to its line; the warning zone is burned too
            done = under or ended(rl, env, live)
        can = targets(can, rules, env, under)
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
            st.setdefault("idle_from", t)       # the first moment of it: the fleet stops (ops_watch fleet_stop_h)
            st["t"] += dt
            continue
        st["left"][st["live"]] = max(0.0, st["left"][st["live"]] - rate * dt / 3600)
        st["t"] += dt
    return {"events": st["events"], "erased": {a: round(v, 1) for a, v in st["erased"].items()},
            "erased_total": round(sum(st["erased"].values()), 1), "switches": st["switches"],
            "idle_pts": round(st["idle"], 1), "idle_from": st.get("idle_from"), "cost": round(_cost(plan, st), 3)}


def pool_pace(plan, f) -> dict:
    """The pace of the whole pool (the allocator's pool pacing; card 2026-10-28: "Pace the whole pool BECAUSE it
    spreads out the human review time"), on the rules in force now (legacy_view: the alive steps' order and lines).
    Each account in that order holds its budget down to its line (the last to reset: at least the last account's
    floor), due at its next reset, and each refill (100 - its line) at the reset after, up to one week past the last
    reset. An account's present budget is left out when the
    accounts before it in the order that outlive it hold more than the pace without it burns before its reset. The
    rate is the max over the deadlines of the cumulative spend / hours. -> {pct, rate_pct_h, deadline_h, total_pct,
    parts}; rate None when no account has a reset time."""
    now, N = f["now"], plan["numbers"]
    v = legacy_view(plan, f)
    order, rd = v["order"], readings_of(f)
    line = {a: v["accounts"][a].get("leave_pct_left", N["floor_pct"]) for a in order}
    exp, elig, present, refills = {}, {}, {}, []
    for a in order:
        r = rd.get(a) or reading(None, now)
        exp[a] = r["reset"]
        elig[a] = r["ok"] and r["left"] > line[a]
    horizon = max((e for e in exp.values() if e is not None), default=None)
    last = max((a for a in order if exp[a] is not None), key=lambda a: exp[a], default=None)
    if last is not None:    # the last account to expire has no other to hand over to: the pass waits at this floor
        line[last] = max(line[last], N["last_account_floor_pct"])
    horizon = None if horizon is None else horizon + WEEK
    for a in order:
        r, e = rd.get(a) or reading(None, now), exp[a]
        if e is None:
            continue
        p = r["last_left"]              # an ESTIMATE or a stale figure is its upper bound
        if p is not None and not r["ok"] and p <= N["blind_pct"]:
            p = 0.0                     # a blind near-empty account counts as empty
        if p is None and r["reset_passed"]:
            p = 100.0
        present[a] = (max(0.0, (p or 0.0) - line[a]), e)
        k = 0
        while k == 0 or e + (k + 1) * WEEK <= horizon:   # each refill up to one week past the last reset
            refills.append((a, max(0.0, 100.0 - line[a]), e + (k + 1) * WEEK))
            k += 1

    def pace(parts):
        parts = sorted(parts, key=lambda t: t[2])
        cum, rate, bind, dl = 0.0, 0.0, 0.0, None
        for _a, sp, d in parts:
            cum += sp
            h = (d - now) / 3600
            if h > 0 and (dl is None or cum / h > rate):
                rate, bind, dl = cum / h, cum, h
        return parts, cum, rate, bind, dl

    def blockers(a):
        return [b for b in present if b != a and elig.get(b) and order.index(b) < order.index(a)
                and present[b][1] > present[a][1]]

    def placed(keep):
        """A kept budget's account that comes before another kept one and outlives it is burned first: its budget is
        due by the other's reset."""
        due = {a: present[a][1] for a in keep}
        for a in keep:
            for b in blockers(a):
                if b in keep:
                    due[b] = min(due[b], present[a][1])
        return [(a, present[a][0], min(present[a][1], due[a])) for a in keep if present[a][0] > 0] + refills

    keep = set(present)
    for _ in range(4):      # the pace depends on what is kept: settle it in a few rounds
        new = {a for a, (_sp, e) in present.items()
               if not blockers(a) or sum(present[b][0] for b in blockers(a)) < pace(placed(keep - {a}))[2] * (e - now) / 3600}
        if new == keep:
            break
        keep = new
    parts = placed(keep)
    if not parts:
        return {"pct": None, "rate_pct_h": None, "deadline_h": None, "total_pct": None, "parts": [],
                "why": "no account has a reset time"}
    parts, cum, rate, bind, dl = pace(parts)
    return {"pct": round(bind, 2), "rate_pct_h": round(rate, 4), "deadline_h": round(dl, 2) if dl else None,
            "total_pct": round(cum, 2),
            "parts": [{"account": a, "spend_pct": round(sp, 2), "by_h": round((d - now) / 3600, 2)} for a, sp, d in parts]}


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


def commanded(plan, f) -> bool:
    """The last switch is the one that a `switch` request asked for: the first one to that account after the request."""
    log = f.get("switches") or []
    if not log or log[-1].get("to") != f.get("live"):
        return False
    return any(q["to"] == f["live"] and stamp(q["at"]) <= stamp_or(log[-1].get("ts"), 0) < stamp(q["ends"]) and not any(
        s.get("to") == q["to"] and stamp_or(s.get("ts"), 0) >= stamp(q["at"]) for s in log[:-1]) for q in plan["requests"])


def decide(plan, f, polled=True) -> dict:
    """-> the decision, in the words of the actuator (do: passive|skip|poll|normal|soft|switch|hold|stop|stopped|
    start; to, account, line, pct_left, warn_line, under, key, why) plus next, pending, week (the counts)."""
    import account_actuator as ACT
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
        el = entry_line(plan, rl)
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
        line, warn = standing_line(plan, live, env) if live in accts else None, None
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
    if warn is not None and pl is not None and line < pl <= warn:
        # the warning zone: the runs are warned and keep working, new work starts; the account ends at its line
        base.update(warning=True, last_account=not can)
    rate = f.get("burn_h")

    def out(d, **more):
        d = {**base, **d, **more}
        dd = ACT.drained(d, {"account_end": cfg}, runs)
        # an_account_end_drain_ends_at_its_bound: on an account with no emergency step (a high line), a run that did not
        # end in rescue.drain_h hours after its save order no longer holds the fleet: the act goes, and it stops it
        ep, bound, nt = state.get("account_end") or {}, dig(N, "rescue.drain_h"), f.get("notice") or {}
        since = stamp(ep.get("save_at")) if ep.get("account") == live else None
        if since is None and nt.get("state") == "soft" and nt.get("drain") and nt.get("account") == live:
            since = stamp(nt.get("since"))      # a drain with no save order (past its window): the notice's start
        if dd.get("drain") and dd.get("drain_of") and bound is not None and since is not None \
                and now - since >= bound * 3600 and not AE.has_emergency(dd.get("line"), cfg):
            return {**d, "why": "%s; the drain began at %s and %s after rescue.drain_h (%s h): the %s goes now and "
                                "stops them" % (d.get("why"), pacific(since), runs_say(runs), g(bound), d["do"])}
        return dd

    # ---- fresh readings before any act
    need, near_old, near_end = [], False, False
    if not lr["ok"] and not blind:
        need.append("%s (live) reads %s" % (live, lr["state"]))
    elif lr["ok"] and warn is not None and pl - warn <= fr["near_pct"]:
        old = cfg["poll_min"] if pl <= warn + 1 else fr["max_age_min"]
        if lr["age_min"] is None or lr["age_min"] > old:
            near_old, near_end = pl > warn, pl <= warn
            need.append("%s at %s%% is within %s of its %s%% warning line on a %s-min-old reading" % (
                live, g(pl), g(fr["near_pct"]), g(warn), lr["age_min"]))
    for a in accts:
        if a != live and (rd.get(a) or {}).get("reset_passed"):
            need.append("%s's reset has passed and its reading is from before it" % a)

    under = rl is None or (pl is not None and pl <= line)       # finished at its line; the warning line only warns
    # a_stopped_fleet_switches_when_an_account_refills: a fleet stopped on an account that it would not start again (its
    # warning zone) is finished there once another account can take over; else it waits for that account's own reset
    stopped_end = (stopped_here and not under and bool(can) and pl is not None and warn is not None
                   and pl <= warn + N["entry_margin_pct"])
    under = under or stopped_end
    until = ended(rl, env, live)
    can = targets(can, rules, env, under)
    base["can_now"] = list(can)         # the accounts that a switch may land on now (status prints the end with it)
    if not under and not until and not lr["ok"] and not blind:
        if need and not polled:
            return {**base, "do": "poll", "poll": True, "why": "; ".join(need)}
        if lr["last_left"] is None or warn is None or lr["last_left"] <= warn + fr["near_pct"]:
            # a last level inside the warning zone warns the runs as a read one does (account end, a stale reading
            # uses the safe values: the burn is stale too, so the order says so)
            zone = warn is not None and lr["last_left"] is not None and line < lr["last_left"] <= warn
            return {**base, "do": "soft", "unread": True,   # no switch is pending: the level is only unread
                    **({"warning": True, "last_account": not can} if zone else {}),
                    "why": "%s reads %s and its last level (%s) cannot prove that it is above its "
                           "warning line: no new start until it is read" % (live, lr["state"], lr["last_left"])}
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
            if is_under and not (rl is None and pl is not None and pl > line):
                return out({"do": "stop", "key": ACT.stop_key(live, f["rows"].get(live) or {}, now),
                            "why": "%s is finished and %s cannot be confirmed after a poll" % (live, a)})
            return {**base, "do": "normal", "to": None, "why": "the switch to %s waits: its reading is %s min old "
                                                               "after a poll; %s stays" % (a, rd[a]["age_min"], live)}
        key = ACT.switch_key(live, a, f["rows"].get(a))
        m = markers.get(key) or {}
        age = now - stamp_or(m.get("at"), 0)       # a marker with no time is old: it guards nothing
        # a_failed_switch_off_an_account_above_its_line_stops_nothing: left only because no step uses it, above its
        # line, the account is not spent: a failed switch is tried again and the fleet goes on
        above = rl is None and pl is not None and pl > line
        if m.get("phase") == "failed" and is_under and not stopped_here and not above:
            return out({"do": "stop", "key": ACT.stop_key(live, f["rows"].get(live) or {}, now),
                        "why": "the switch %s failed and %s is finished: stop; the switch is tried again from the "
                               "stopped fleet" % (key, live)})
        if m.get("phase") == "pending" and age < ACT.STALE_PENDING_S:
            if is_under and stopped_here:
                return {**base, "do": "stopped", "why": "stopped on %s; the switch %s is in flight" % (live, key)}
            if is_under:
                return out({"do": "stop", "key": ACT.stop_key(live, f["rows"].get(live) or {}, now),
                            "why": "the switch %s is in flight yet %s is still live at its line: stop" % (key, live)})
            return {**base, "do": "hold", "to": a, "key": key, "why": "the switch %s is in flight" % key}
        return out({"do": "switch", "to": a, "key": key, "under": is_under, "why": why}, week=week,
                   **({"above_line": True} if above else {}))

    # ---- the live account is finished: which account is next
    if under or until:
        if near_end and not polled:     # the end of an account is read at poll_min: the waits below act on this level
            return {**base, "do": "poll", "poll": True, "why": "; ".join(need)}
        if under and polled:            # an account confirmed by a fresh reading beats a stop on one that is not
            can = [a for a in can if take(a)[1]] or can
        ch = choices(plan, f, can, stay=False) if len(can) > 1 else {}
        nxt = best_of(ch, order) if ch else (can[0] if can else None)
        for q in open_requests(plan, f):
            if q["to"] in can:
                nxt = q["to"]
        if nxt is not None:
            how = ("no step uses %s now" % live) if rl is None else (
                "the fleet is stopped on %s at %s%%, inside its warning zone, and another account can take over" % (
                    live, g(pl)) if stopped_end else
                "%s at %s%% is at its %s%% line" % (live, g(pl), g(line)) if under else
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
        return out({"do": "stop", "key": ACT.stop_key(live, f["rows"].get(live) or {}, now),
                    "why": "no account can take over (%s); %s at %s%% is finished%s" % (
                        blockers, live, "?" if pl is None else g(pl), " (blind meter)" if blind else "")})

    # ---- the live account is not finished: it stays
    if need and not polled:
        return {**base, "do": "poll", "poll": True, "why": "; ".join(need)}
    if near_old and lr["age_min"] is not None and lr["age_min"] > fr["max_age_min"]:
        return {**base, "do": "soft", "unread": True,       # no switch is pending: the level is only unconfirmed
                "why": "%s at %s%% on a %s-min-old reading, within %s points of its %s%% warning "
                       "line: the level cannot be confirmed after a poll, so no new start until "
                       "it is read" % (live, g(pl), g(lr["age_min"]), g(fr["near_pct"]), g(warn))}
    if stopped_here:
        if pl <= warn + N["entry_margin_pct"]:
            return {**base, "do": "stopped", "why": "stopped on %s: no start inside its warning zone" % live}
        return {**base, "do": "start", "why": "%s has headroom again after the stop" % live}
    eta = None if not rate else (pl - warn) / rate
    head = "%s live at %s%% (line %s%%, warning at %s%%): it stays" % (live, g(pl), g(line), g(warn))
    if base.get("warning"):
        head += ", inside its warning zone: the runs are warned, keep working and new work starts until its line"
        eta = None if not rate else (pl - line) / rate
        head += "" if eta is None else ", about %s h to its line at %s points an hour" % (g(eta), g(rate))
    else:
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
    if pin or f.get("hand") or commanded(plan, f):
        return {**d, "why": d["why"] + ". No rescue switch: " + (
            "pinned until %s" % pacific(stamp(pin[0]["ends"])) if pin else
            "the last switch was made %s, so %s is kept until it is finished (./acct switch %s goes)" % (
                "by hand" if f.get("hand") else "by command", live, best))}
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
            if rl.get("schedule"):      # a line schedule: what the reset erases is above the line at the reset
                end = rule_of(plan, a, Env(r["reset"] - 1, env.left, lambda x: r["reset"] if x == a else env.reset(x),
                                           entry=env.entry_left))
                rl = end or rl
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


def can_use(plan, f, a, carried=False):
    """May our work send `a` a job now? -> (OK | NO | COULD_NOT_LOOK, one line). A meter account (Codex): its level is
    over its line. A Claude account: a new run may start on it on this machine (new_run_gate)."""
    now = f["now"]
    rd = readings_of(f)
    rd["codex"] = f.get("codex") or reading(None, now)
    if a not in plan["accounts"]:
        return COULD_NOT_LOOK, "COULD NOT LOOK: %s is no account of the plan" % a
    if plan["accounts"][a]["kind"] == "claude":
        return new_run_gate(plan, f, a, carried)
    r = rd.get(a) or reading(None, now)
    env = Env(now, lambda x: (rd.get(x) or {}).get("left"), lambda x: (rd.get(x) or {}).get("reset"))
    rl = rule_of(plan, a, env)
    if rl is None:
        return NO, "NO: no step uses %s now" % a
    if not r["ok"]:
        return COULD_NOT_LOOK, "COULD NOT LOOK: %s reads %s (%s)" % (a, r["state"], r.get("why") or "no cause given")
    tail = " (line schedule: %s)" % rl["note"] if rl.get("note") else " (line schedule)" if "note" in rl else ""
    if r["left"] > rl["line"]:
        return OK, "yes: %s has %s%% left, over its %s%% line%s" % (
            a, g(r["left"]), g(rl["line"]), " (reset day: the line is lifted)" if rl["reset_day"] else tail)
    return NO, "NO: %s has %s%% left, at or under its %s%% line%s" % (a, g(r["left"]), g(rl["line"]), tail)


def meter_answer(a, now=None, slow=False):
    """`./acct can-use <a meter account>` for a program (Codex's door, the allocator's advice line). -> (OK | NO |
    COULD_NOT_LOOK, one line). slow: read the meter now (about 2 s); else the last timed pass's reading, which is could
    not look once it is older than NOTICE_FRESH_S. No plan file is could not look: a caller then sends its job."""
    now = clock() if now is None else now
    plan, why = load_plan()
    if plan is None:
        return COULD_NOT_LOOK, "COULD NOT LOOK: " + why
    if os.environ.get("RM_ACCOUNT_PLAN_FRAME"):
        return can_use(plan, gather(now), a)
    if slow:
        try:
            import account_usage as AU
            codex = meter_reading(AU.read_codex_points(), now)
        except Exception as e:  # noqa: BLE001  the reader failing is could not look, by name
            return COULD_NOT_LOOK, "COULD NOT LOOK: the reader of %s failed (%s: %s)" % (a, type(e).__name__, e)
    else:
        cache = read_json(plan_dir() / "frame.json", {})
        cache = cache if isinstance(cache, dict) else {}
        codex, at = cache.get("codex"), cache.get("at")
        if not isinstance(codex, dict) or not is_num(at) or now - at > NOTICE_FRESH_S:
            return COULD_NOT_LOOK, "COULD NOT LOOK: no timed pass has read %s in the last %d min" % (a, NOTICE_FRESH_S // 60)
    return can_use(plan, {"now": now, "rows": {}, "codex": codex}, a)


# ------------------------------------------------------------------ the gate: may a new run start now (one answer)
# budget: danger=a notice that outlived the pass that wrote it (its timer stopped) holds every launch of the deciding
# budget: machine; evidence=a stopped engine's HOLD file held launches on 2026-11-05, and the pass writes each 5 min, so
# budget: 20 min is four missed passes; ends no work: on the deciding machine an older notice refuses nothing and the
# budget: plan decides at once. On a following machine an older notice is could not look, and no NEW run starts there
# budget: (the owner's order of 2026-11-24 for two machines on one account); its live runs go on.
NOTICE_FRESH_S = 20 * 60
REFUSES = ("soft", "stop", "stopped", "switch", "hold")       # the decisions under which no new run starts


def notice_dir() -> Path:
    """The folder of the actuator's notice, which each machine's launch gate and hooks read."""
    import account_actuator as ACT
    return Path(os.environ.get("RM_SWITCH_PLAN_DIR") or ACT.LIVE_OUT)


def fresh_record(n, now) -> bool:
    """n is a record written under NOTICE_FRESH_S ago (its `at`)."""
    at = stamp(n.get("at")) if isinstance(n, dict) else None
    return at is not None and now - at <= NOTICE_FRESH_S


def notice_refusal(n, now, carried=False):
    """Why the actuator's notice n refuses a new run now, or None. A stop refuses each start. A drain refuses a new
    run; a carried run (the continuation of a live run, or a resume of its session) is that run finishing, and goes
    until the account is at its line (`account_end`). The warning zone refuses nothing. A notice that cannot be read,
    or is older than NOTICE_FRESH_S, refuses nothing here: the caller says what that means on its machine."""
    if not fresh_record(n, now):
        return None
    acc, since = n.get("account") or "?", n.get("since") or "?"
    if n.get("could_not_look"):
        return str(n.get("message") or "COULD NOT LOOK: the account of this machine could not be read; no new start")
    if n.get("state") == "stop":
        return ("the account %s is out (notice since %s): the fleet is stopped and nothing starts until an account "
                "resets (./acct status shows it)" % (acc, since))
    if n.get("state") == "soft" and n.get("drain") and not (carried and not n.get("account_end")):
        if n.get("switch_pending") is False:        # a level that is not read: no switch is pending
            return ("the level of the account %s is not read (notice since %s): no new run starts until it is read; "
                    "live runs go on. Why: %s" % (acc, since, " ".join(str(n.get("why") or "").split())))
        return ("the account %s is draining (notice since %s): live runs finish on it and no new run starts until the "
                "switch (./acct status shows it). Why: %s" % (acc, since, " ".join(str(n.get("why") or "").split())))
    return None


def new_run_gate(plan, f, a, carried=False):
    """May a new run start on the Claude account `a` on this machine now? -> (OK | NO | COULD_NOT_LOOK, one line).
    NO when `a` is not the live account here; when the actuator's fresh notice refuses (a stop, a drain); when the
    decision refuses new runs. The decision is the one that the last pass published; with no pass inside
    NOTICE_FRESH_S (its timer stopped), or with another account live since, the plan decides now on the last readings."""
    now, live = f["now"], f.get("live")
    if not live:
        return COULD_NOT_LOOK, "COULD NOT LOOK: the live account of this machine is unknown (%s)" % (
            f.get("live_why") or "the switcher gave no status")
    if a != live:
        return NO, "NO: %s is not the live account of this machine (%s is); ./acct switch %s asks for it" % (a, live, a)
    why = notice_refusal(f.get("notice"), now, carried)
    if why:
        return NO, "NO: " + why
    pd = f.get("published")
    if fresh_record(pd, now) and not pd.get("shadow") and pd.get("account") == a and pd.get("rev") == plan.get("rev"):
        d, how = pd, "the pass of %s" % pacific(stamp(pd["at"]))
    else:
        d, how = decide(plan, f), "decided now (no pass has published this plan for %s in the last %d min)" % (
            a, NOTICE_FRESH_S // 60)
    if d["do"] == "skip":
        return COULD_NOT_LOOK, d["why"]
    # at the line: the save order, or a switch due under the line with no run live (ACT.drained leaves it a switch)
    at_line = d.get("account_end") or d.get("under") or (
        is_num(d.get("pct_left")) and is_num(d.get("line")) and d["pct_left"] <= d["line"])
    if d["do"] in REFUSES and not (carried and not at_line and d["do"] != "stop" and d["do"] != "stopped"):
        return NO, "NO: no new run starts on %s (%s): %s" % (a, how, d["why"])
    return OK, "yes (%s): %s" % (how, d["why"])


def launch_gate(now=None, carried=False):
    """The one answer that a launcher asks before it starts a run on this machine (`./acct can-use`). -> (exit, one
    line, role). role: `decider` (this machine holds the plan file), `follower` (its notice comes from the deciding
    machine: follows.json beside the notice), `none`. The actuator's fresh notice refuses on every machine. A following
    machine whose notice is missing or older than NOTICE_FRESH_S cannot look: COULD_NOT_LOOK, and its launcher starts
    nothing. A test reads no live plan (plan_dir): it names its own folder, or only the notice counts."""
    now = clock() if now is None else now
    nd = notice_dir()
    n = read_json(nd / "notice.json")
    # a test world that names its notice folder names its plan folder too, or has no plan
    own = (plan_dir() / "plan.json").exists() and not (
        os.environ.get("RM_SWITCH_PLAN_DIR") and not os.environ.get("RM_ACCOUNT_PLAN_DIR"))
    if own:
        plan, why = plan_in_force()     # the rules of the pass, a fallback included
        if plan is None:        # no rules could be read: the actuator's notice is the answer
            r = notice_refusal(n, now, carried)
            return (NO, "NO: " + r, "decider") if r else (
                OK, "yes: by the actuator's notice alone (%s)" % why, "decider")
        f = gather(now)
        if not f.get("live"):
            return COULD_NOT_LOOK, "COULD NOT LOOK: the live account of this machine is unknown (%s)" % (
                f.get("live_why") or "the switcher gave no status"), "decider"
        rc, text = can_use(plan, f, f["live"], carried)
        return rc, text, "decider"
    fol = read_json(nd / "follows.json")
    if isinstance(fol, dict):
        of = fol.get("of") or "the deciding machine"
        if not fresh_record(n, now):
            at = stamp(n.get("at")) if isinstance(n, dict) else None
            return COULD_NOT_LOOK, ("COULD NOT LOOK: this machine takes its account plan from %s, and %s; no new run "
                                    "starts here until a notice arrives (on %s: ./acct status)" % (
                                        of, "it has no notice" if at is None else "its last notice is %d min old" % (
                                            (now - at) / 60), of)), "follower"
        r = notice_refusal(n, now, carried)
        return (NO, "NO: " + r, "follower") if r else (
            OK, "yes: the notice of %s from %s refuses nothing" % (pacific(stamp(n["at"])), of), "follower")
    r = notice_refusal(n, now, carried)
    return (NO, "NO: " + r, "none") if r else (
        NONE, "NONE: this machine holds no account plan and follows none; nothing is refused", "none")


# ------------------------------------------------------------------ the machines on the plan's accounts
def machine_notice(plan, f, account, now, name, prev=None, why_unread=None) -> dict:
    """The notice for the machine `name`, which is on `account`: the plan's decision for that account from the same
    readings (pure). A decision under which no new run starts is a drain there (at the line: `account_end`, save and
    publish); the warning zone carries the warning text; an account that could not be read refuses new runs and says
    could not look. Its switch at the line is machine_switch's, after the notice."""
    import account_actuator as ACT
    prev = prev if isinstance(prev, dict) else {}
    tag = {"machine": name, "follows": os.uname().nodename}
    if not account:
        msg = "COULD NOT LOOK: the live account of %s could not be read (%s); no new run starts there" % (
            name, why_unread or "no cause given")
        return {"state": "soft", "since": prev.get("since") if prev.get("could_not_look") and prev.get("since")
                else iso(now), "at": iso(now), "account": None, "line": None, "pct_left": None, "message": msg,
                "why": msg, "drain": True, "account_end": False, "warning": None, "could_not_look": True, **tag}
    fm = machine_facts(f, account)
    d = decide(plan, fm)
    if d["do"] in REFUSES:      # a last level that is not read now is no level at the line (no save order on it)
        under = is_num(d.get("pct_left")) and is_num(d.get("line")) and d["pct_left"] <= d["line"] and not d.get("unread")
        dm = {**d, "do": "soft", "drain": True, "account_end": under}
    else:
        dm = {**d, "do": "normal", "account": account}
        if d.get("warning"):
            dm["warning_text"] = AE.warn_text(account, d.get("pct_left"), fm["burn_live"], d.get("line"),
                                              plan["numbers"]["account_end"], bool(d.get("last_account")))
    n = ACT.notice_of(dm, now, prev)
    # its runs are not read here (machine_facts): the deciding pass counts them over ssh (machine_switch), and a reader
    # there must not take this for a systemd read that failed on its own machine
    blind, said = ACT.runs_why(None), "the runs there are counted by the pass of %s, not read in this decision" % tag["follows"]
    return {**{k: v.replace(blind, said) if isinstance(v, str) else v for k, v in n.items()}, **tag}


def machine_facts(f, account) -> dict:
    """The readings of this pass, seen from a machine that is on `account` (its runs are not this machine's)."""
    return {**f, "live": account, "runs": None, "state": {}, "markers": {}, "hand": True, "draining": False,
            "burn_live": f.get("burn_live") if account == f.get("live") else None}


SWITCH_RETRY_S = 30 * 60    # budget: danger=a switch asked on every pass while it fails; ends no work: asked again
def stop_grace_s():
    """From the write-now stop of a run on another machine to its machine's switch: twice the stop's own kill deadline
    (control.ACCOUNT_STOP_DEADLINE_S, the account end's write-now deadline, whose danger and evidence are written there):
    the deadline, then as long again for the kill and the run's end to land. A run that is still listed then is closed
    by the switch."""
    sys.path.insert(0, str(HERE.parent / "rimflow"))
    import control as C
    return 2 * C.ACCOUNT_STOP_DEADLINE_S


def machine_bound_s(plan, d):
    """-> (seconds from the save order to the write-now stop, why) for a machine whose account `d` is at its end. The
    same bound as this machine's own drain at an account with no emergency step (an_account_end_drain_ends_at_its_bound):
    `rescue.drain_h`, and never under ten times `save_need_min`, the measured time that a run needs to save (17 of 19
    orders heard 2026-11-24 ended p90 9.5, max 13.8 min after the order). Danger of none: a following machine that
    refuses every launch for as long as one run waits (2026-11-26: over 3 h, five tickets, 3 to 6 refused launches
    each). With `rescue.drain_h` null the floor alone holds: no hand stops a run on another machine. At an emergency
    step (an account with a low line, at `emergency_pct` or under) the bound is 0, as the emergency order is here."""
    N, cfg = plan["numbers"], plan["numbers"]["account_end"]
    pct, line = d.get("pct_left"), d.get("line")
    if AE.has_emergency(line, cfg) and is_num(pct) and pct <= cfg["emergency_pct"]:
        return 0, "at the emergency step (%s%%)" % g(cfg["emergency_pct"])
    floor = 10 * cfg["save_need_min"] * 60
    h = dig(N, "rescue.drain_h")
    return max(floor, h * 3600 if is_num(h) else 0), ("rescue.drain_h %s h, at least ten saves of %s min" % (
        g(h) if is_num(h) else "null", g(cfg["save_need_min"])))


def machine_switch(plan, f, now, name, m, account, n, prev, runs_of, switch, order=None, stop=None):
    """RIMMANDRAKE_AUTOMATE_STEVEDESKTOP_ACCOUNT_SWITCH_PLAN_SAYS_NEVER: a machine whose notice says its account is at
    its end is switched to the plan's next account when it lists no live helper run (the switch closes every Claude
    window there). Its account is at its end at its line (the notice's `account_end`), or above it when no step uses
    the account now: the decision then leaves it when its runs end, and the notice says so.
    RIMMANDRAKE_SWITCH_STEVEDESKTOP_PAST_A_RUN_THAT_ONLY_WAITS: with runs live there, each gets the save order once (the
    order at the line, as on this machine); a run still live machine_bound_s after it is stopped (`pipe stop U
    --write-now` there: no trial spent, carried on by left_open_continue), and the switch goes once the runs end or
    stop_grace_s() after the stop. -> the record of what was done ({to, at, ok, line, end}), or None when its account is
    not at its end. Pure but for the seams."""
    d = decide(plan, machine_facts(f, account)) if account else {}
    finished = d.get("under") and (d.get("do") == "switch" or d.get("drain_of") == "switch")
    if not (n.get("account_end") or finished):
        return None
    can = d.get("can_now")
    nxt = next((a for a in (d.get("to"), (d.get("pending") or {}).get("to"), d.get("next"))
                if a and a != account and (can is None or a in can)), None) or next(
        (a for a in (can or []) if a != account), None)
    if not nxt:
        return {"to": None, "at": iso(now), "ok": False, "line": "no account can take over; it waits for a reset"}
    last = prev.get("switch") if isinstance(prev.get("switch"), dict) else {}
    if last.get("to") == nxt and stamp(last.get("at")) is not None and now - stamp(last["at"]) < SWITCH_RETRY_S:
        return dict(last, line="switch to %s asked at %s; not asked again yet" % (nxt, last["at"]))
    runs, why = runs_of(m["ssh"])
    if runs is None:
        return {"to": nxt, "at": None, "ok": False, "line": "COULD NOT LOOK at its live runs (%s); not switched" % why,
                "end": prev.get("end")}
    units = None if isinstance(runs, int) else list(runs)
    live = runs if isinstance(runs, int) else len(units)
    end = prev.get("end") if isinstance(prev.get("end"), dict) and prev["end"].get("account") == account else {}
    end = dict(end, account=account)
    stopped = stamp(end.get("stopped_at"))
    cfg = plan["numbers"]["account_end"]
    bound, bwhy = machine_bound_s(plan, d)
    grace = stop_grace_s() if bound else cfg["pause_max_s"]   # at the emergency step: the pause, as on this machine
    if live and not (stopped is not None and now - stopped >= grace):
        end.setdefault("since", iso(now))
        said = []
        if order is not None and not end.get("ordered_at") and bound > 0:
            text = "%s If a run is still live %s after this order, it is stopped (write-now) and %s switches " \
                   "accounts." % (AE.save_text(account, d.get("pct_left"), None, d.get("line"), cfg, False),
                                  dur(bound), name)
            ok, words = order(m["ssh"], units, text)
            end.update(ordered_at=iso(now), order=words) if ok else None
            said.append(("the save order went to them (%s)" % words) if ok else
                        "the save order did not reach them (%s); tried again next pass" % words)
        since = stamp(end.get("ordered_at")) or stamp(end["since"])
        if stop is not None and stopped is None and now - since >= bound:
            why_stop = ("account end on %s: %s is at its end (%s%% left, line %s%%) and its switch to %s waited %s for "
                        "its runs (%s); write where you are and end" % (
                            name, account, g(d.get("pct_left")), g(d.get("line")), nxt, dur(now - since), bwhy))
            ok, words = stop(m["ssh"], units, why_stop)
            if ok:
                end.update(stopped_at=iso(now), stop=words, stop_units=units)
            said.append(("stopped (write-now) after %s: %s" % (dur(now - since), words)) if ok else
                        "the write-now stop did not reach it (%s); tried again next pass" % words)
        elif stopped is not None:
            said.append("stopped (write-now) at %s; the switch goes when they end, at the latest %s after the stop" % (
                end["stopped_at"], dur(grace)))
        else:
            said.append("stopped (write-now) at %s if still live" % pacific(since + bound))
        return {"to": nxt, "at": None, "ok": False, "end": end,
                "line": "%d live run(s) there; the switch to %s waits; %s" % (live, nxt, "; ".join(said))}
    ok, words = switch(m["ssh"], name, nxt)
    return {"to": nxt, "at": iso(now), "ok": bool(ok), "end": end if not ok else None,
            "line": ("switched to %s%s" % (nxt, (" (%d run(s) still listed %s after their stop: the switch closes them)"
                                                 % (live, dur(now - stopped))) if live else ""))
            if ok else "the switch to %s failed: %s" % (nxt, words)}


def dur(s):
    """Seconds as a short duration: 2 h, 10 min."""
    return ("%s h" % g(round(s / 3600, 1))) if s >= 3600 else "%d min" % round(s / 60)


def push_machines(plan, f, now, account_of=None, send=None, runs_of=None, switch=None, order=None, stop=None,
                  kick=None, carry=True) -> dict:
    """Each machine of the plan gets the plan's decision for the account that it is on, from the readings of this pass.
    -> {machine: {ok, account, state, line}}. Never raises: a machine that could not be reached is said, and its own
    gate refuses new runs once its notice is older than NOTICE_FRESH_S. With `carry` (the pass that drives, as this
    machine's own kick runs only after a live pass), a machine whose notice refuses nothing gets left_open_continue's
    kick: the continuations that waited there for its switch start."""
    import account_plan_machines as MS      # the ssh transport: this file starts no process
    out = {}
    if send is not None:        # test seams for the notice: an act with no seam of its own does nothing
        none = lambda *a: (False, "no seam given")  # noqa: E731
        runs_of = runs_of or (lambda alias: (None, "no runs reader given"))
        order, stop, kick = order or none, stop or none, kick or none
    runs_of, switch = runs_of or MS.machine_runs, switch or MS.switch_machine
    order, kick = order or MS.order_machine, kick or MS.kick_machine
    stop = stop or (lambda alias, units, why: MS.stop_machine_runs(
        alias, units, why, per_ruling="RIMMANDRAKE_SWITCH_STEVEDESKTOP_PAST_A_RUN_THAT_ONLY_WAITS"))
    for name, m in (plan.get("machines") or {}).items():
        try:
            account, why = (account_of or MS.machine_account)(m["ssh"])
            keep = plan_dir() / ("machine.%s.json" % name)
            prev = read_json(keep, {})
            prev = prev if isinstance(prev, dict) else {}
            n = machine_notice(plan, f, account, now, name, prev, why)
            ok, err = (send or MS.send_notice)(m["ssh"], n)
            sw = machine_switch(plan, f, now, name, m, account, n, prev, runs_of, switch, order, stop) if ok else None
            if ok:
                rec = dict(n)
                if sw and sw.get("at"):
                    rec["switch"] = {k: v for k, v in sw.items() if k != "end"}
                elif prev.get("switch"):
                    rec["switch"] = prev["switch"]
                if sw and sw.get("end"):
                    rec["end"] = sw["end"]
                if sw:
                    rec["step"] = sw["line"]
                write_atomic(keep, rec)
            out[name] = {"ok": bool(ok), "account": account, "state": n["state"], "drain": n["drain"],
                         "line": ("sent: " + (n["message"] or "nothing is refused")) if ok else
                         "COULD NOT LOOK: the notice did not reach %s (%s)" % (name, err)}
            if sw:
                out[name]["switch"] = sw["line"]
            if carry and ok and n["state"] == "none":
                kok, said = kick(m["ssh"])
                out[name]["kick"] = said if kok else "COULD NOT LOOK: left_open_continue there: %s" % said
        except Exception as e:  # noqa: BLE001  the pass goes on; the machine's own gate handles a missing notice
            out[name] = {"ok": False, "account": None, "state": None, "drain": None,
                         "line": "COULD NOT LOOK: %s: %s" % (type(e).__name__, e)}
    return out


def machine_lines(plan, now) -> list:
    """One line for each machine of the plan: the account it is on and the last notice that reached it."""
    out = []
    for name in plan.get("machines") or {}:
        n = read_json(plan_dir() / ("machine.%s.json" % name))
        if not isinstance(n, dict) or stamp(n.get("at")) is None:
            out.append("MACHINE %s: UNMEASURED: no notice has reached it yet" % name)
            continue
        age = (now - stamp(n["at"])) / 60
        out.append("MACHINE %s: on %s; %s (the last notice reached it %s min ago%s)%s" % (
            name, n.get("account") or "an account that could not be read",
            n.get("message") or "nothing is refused", g(age),
            "" if age * 60 <= NOTICE_FRESH_S else ": it now refuses new runs, could not look",
            "; the pass there: %s" % n["step"] if n.get("step") else "; its last switch: %s at %s" % (
                n["switch"].get("line"), n["switch"].get("at")) if isinstance(n.get("switch"), dict) else ""))
    return out


def rules_now(rows=None, now=None):
    """The rules in force now, flat (order, lines, floors: the shape of legacy_view), for a program that reads only
    those (the Dispatcher's priority). -> (rules, where they came from), or (None, why) when there are none
    (plan_in_force). A step's `when` has no place in this shape: an account is in the order while its step is alive
    now."""
    plan, why = plan_in_force()
    if plan is None:
        return None, why
    now = time.time() if now is None else now
    if rows is None:
        import account_usage as AU
        rows = AU.read_now(now).get("accounts") or {}
    return (legacy_view(plan, {"now": now, "rows": rows, "switches": None}),
            "the account plan, rev %s" % plan.get("rev") + ("" if why is None else " (%s)" % why))


def temporary_line(plan, a, now, hours_to_reset=None):
    """(step name, its end as ISO or None, leave line) when the rule of `a` now is a step with a life (a temporary
    line: `./acct line A N --until-reset`) and no `when`, else None. hours_to_reset: the caller's reading of a's reset."""
    reset = None if hours_to_reset is None else now + hours_to_reset * 3600
    env = Env(now, lambda x: None, lambda x: reset if x == a else None)
    rl = rule_of(plan, a, env)
    if rl is None:
        return None
    s = plan["steps"][find_step(plan, rl["step"])]
    if s.get("when") or not (s.get("ends") or s.get("ends_at_reset_of")) or entry_points(s) is not None:
        return None
    ends = [stamp(s.get("ends"))] + ([env.first_reset_after(s["ends_at_reset_of"], stamp(s.get("from")))]
                                     if s.get("ends_at_reset_of") and stamp(s.get("from")) is not None else [])
    ends = [e for e in ends if e is not None]
    return s["name"], iso(min(ends)) if ends else None, rl["line"]


# ------------------------------------------------------------------ the measures (pure)
def week_of(t) -> str:
    d = datetime.fromtimestamp(t, TZ)
    return (d - timedelta(days=d.weekday())).strftime("%Y-%m-%d")


def measures(rows, switches, line_at, since=None, line_now=None):
    """-> {week (its Monday): {"erased": {account: points | "UNMEASURED: why"}, "left_at_reset": {...}, "switches": n}}.
    A reset is seen where an account's reset time moves on by days. The level at a reset is its last MEASURED reading
    before it; none inside 6 h before the reset is UNMEASURED, never 0. line_at(account, time) is the leave line then.
    line_now(account, time, reset): the leave line of that moment; with it, each week also has the reserve kept:
    `under_line_min` (the minutes that a reading was under that line, each reading counting until the next one of the
    same week, at most 6 h) and `lowest_gap` (the lowest level less line)."""
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
    if line_now is not None:
        for a, rd in per.items():
            for (ta, ua, ra), (tb, _ub, rb) in zip(rd, rd[1:] + [(None, None, None)]):
                if since is not None and ta < since:
                    continue
                line = line_now(a, ta, ra)
                if line is None:
                    continue
                w = out.setdefault(week_of(ta), {"erased": {}, "left_at_reset": {}, "switches": 0, "resets": {}})
                gap = round(100 - ua - line, 1)
                lg = w.setdefault("lowest_gap", {})
                lg[a] = gap if a not in lg else min(lg[a], gap)
                um = w.setdefault("under_line_min", {})
                um.setdefault(a, 0)
                if gap < 0 and tb is not None and abs(rb - ra) <= 86400:
                    um[a] += round(min(tb - ta, 6 * 3600) / 60)
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


def dark_hours(log) -> dict:
    """{week: {dark_h, passes, unread}} from this tool's own log: the hours whose pass refused a new run (its `do` is
    one of REFUSES), each pass counting until the next one (at most 15 min; the last one 5 min, the timer's period).
    The log does not say whether work waited, so this is the dark hours' upper bound. unread: refusing passes whose
    runs could not be read."""
    out, rows = {}, sorted(((stamp(r.get("at")), r) for r in log if stamp(r.get("at")) is not None
                            and not r.get("shadow")), key=lambda x: x[0])
    for i, (t, r) in enumerate(rows):
        w = out.setdefault(week_of(t), {"dark_s": 0.0, "passes": 0, "unread": 0})
        w["passes"] += 1
        if r.get("do") in REFUSES:
            nxt = rows[i + 1][0] if i + 1 < len(rows) else t + 300
            w["dark_s"] += min(nxt - t, 900)
            w["unread"] += r.get("runs") is None
    return {k: {"dark_h": round(v.pop("dark_s") / 3600, 2), **v} for k, v in out.items()}


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
                out.append("  %-10s %s" % (a, " ".join(str(gs[1]).split())))
            continue
        r = rd.get(a) or reading(None, now)
        rl = rule_of(plan, a, env)
        rule = "no step uses it now" if rl is None else "step %s, line %s%%%s" % (
            rl["step"], g(rl["line"]), " (reset day)" if rl["reset_day"] else " (line schedule%s)" % (
                ": COULD NOT LOOK" if str(rl.get("note") or "").startswith("COULD NOT LOOK") else "")
            if "note" in rl else "")
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


def schedule_lines(plan, f, accounts=None) -> list:
    """For each account whose step in force (else its standing step) has a line schedule: the line now, its next change
    with its Pacific time, and each point with its place as hours before the reset (what the pass computes)."""
    now = f["now"]
    rd = readings_of(f)
    rd["codex"] = f.get("codex") or reading(None, now)
    env = Env(now, lambda a: (rd.get(a) or {}).get("left"), lambda a: (rd.get(a) or {}).get("reset"),
              entry=lambda a: (f.get("entry") or {}).get(a))
    out = []
    for a in plan["accounts"]:
        if accounts is not None and a not in accounts:
            continue
        rl = rule_of(plan, a, env)
        s = next((x for x in plan["steps"] if rl and x["name"] == rl["step"]), None) or next(
            (x for x in reversed(plan["steps"]) if x["use"] == a and x.get("schedule") is not None), None)
        if s is None or s.get("schedule") is None:
            continue
        ln = line_of_step(plan, s, a, env)
        info = ln["schedule"]
        alive = "" if rl and rl["step"] == s["name"] else " (the step is not in force now)"
        if info is None:
            out.append("SCHEDULE %s (step %s%s): %s" % (a, s["name"], alive, ln["note"]))
            out.append("      as typed: %s" % s["schedule"])
            continue
        out.append("SCHEDULE %s (step %s%s): %s%% now, %s" % (a, s["name"], alive, g(info["pct"]), info["next"]))
        out.append("      the points, in the week from the reset %s to %s: %s" % (
            pacific(info["reset"] - WEEK), pacific(info["reset"]), "; ".join(
                "%s at %s (%s h before the reset%s)" % (p["text"], pacific(p["at"]), g(p["h_before_reset"]),
                                                        ", OUTSIDE THE WEEK" if p["outside"] else "")
                for p in info["points"])))
        for nt in info["notes"]:
            out.append("      note: " + nt)
    return out


def next_line(plan, f, d=None) -> str:
    d = d or decide(plan, f)
    return "%s: %s" % (d["do"].upper(), d["why"])


def end_lines(plan, f, d) -> list:
    """What the timed pass does by itself at the end of the live account, with the numbers in force, the machines on
    the same account, and the hand commands with the names filled in. [] when the live account has no line."""
    live, line, warn = d.get("account"), d.get("line"), d.get("warn_line")
    if not live or line is None or live not in claude_accounts(plan):
        return []
    cfg, rd = plan["numbers"]["account_end"], readings_of(f)
    can = d.get("can_now")              # None: the decision ended before it knew (a hold, an unread live account)
    nxt = next((a for a in (d.get("to"), (d.get("pending") or {}).get("to"), d.get("next"))
                if a and (can is None or a in can)), None) or (can[0] if can else None)
    act = "switch" if nxt else "stop"
    out = ["END OF %s (what the timed pass does by itself)" % live]
    if warn is not None and warn > line:
        out.append("      from %s%% to %s%%: each live run gets one warning (save a note, publish, keep working); new runs "
                   "start, warned" % (g(warn), g(line)))
    out.append("      at %s%%: no new run starts; each live run is told to save and end; the %s goes when the last one "
               "ends" % (g(line), act))
    if AE.has_emergency(line, cfg):
        out.append("      at %s%%: each Claude process is paused, the level is read again, then the %s goes with runs "
                   "live" % (g(cfg["emergency_pct"]), act))
    if nxt:
        left = (rd.get(nxt) or {}).get("left")
        out.append("      next account: %s (%s)" % (nxt, "UNMEASURED now" if left is None else "%s%% left" % g(left)))
    else:
        first = min(((r["reset"], a) for a, r in rd.items() if a != live and a in claude_accounts(plan)
                     and r["reset"] is not None), default=None)
        out.append("      no account can take over now: the fleet stops at %s%% and starts again at a reset%s" % (
            g(line), "" if first is None else " (the reset of %s, %s, is the first)" % (first[1], pacific(first[0]))))
    for name, m in (plan.get("machines") or {}).items():
        n = read_json(plan_dir() / ("machine.%s.json" % name))
        if isinstance(n, dict) and n.get("account") == live:
            out.append("      %s is on %s too: it gets no new run at the same line; the pass switches it when it lists no "
                       "live run (by hand: ssh -t %s claude-account-switch %s <account>)" % (name, live, m["ssh"], name))
    out.append("      by hand: ./acct switch %s --now · ./acct hold --for 2h · ./acct line %s <percent> --until-reset · "
               "./acct --help" % (nxt or "<account>", live))
    return out


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
    out += end_lines(plan, f, d)
    out.append("ACCOUNTS (what is LEFT)")
    out += account_lines(plan, f)
    out += schedule_lines(plan, f)
    if f.get("slow_at"):
        out.append("      codex and jpl-genai were read by the timed pass %s min ago" % g((f["now"] - f["slow_at"]) / 60))
    for kind in ("holds", "pins", "requests"):
        for h in active(plan[kind], f["now"]):
            out.append("%s %s until %s: %s" % (kind[:-1].upper(), h.get("id") or h.get("account") or h.get("to"),
                                               pacific(stamp(h["ends"])), h.get("why") or "no reason given"))
    out += machine_lines(plan, f["now"])
    if f.get("hold_file"):
        out.append("HOLD  a HOLD file made by hand stands in the actuator's folder: no pass acts until it is removed")
    return "\n".join(out), rc


def plan_text(plan, f=None) -> str:
    now = (f or {}).get("now") or time.time()
    out = ["PLAN rev %s (%s)" % (plan.get("rev"), plan_dir() / "plan.json"), "STEPS, in order (the first live step of "
           "an account is its rule; the order says only which account is next):"]
    for i, s in enumerate(plan["steps"], 1):
        bits = ["use %s by its line schedule \"%s\" (highest %s%%)" % (s["use"], s["schedule"], g(s["leave"]))
                if s.get("schedule") is not None else
                "use %s until %s%% left" % (s["use"], s["leave"]) if is_num(s["leave"]) else
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
    out.append("MACHINES that get this plan's decision for the account they are on: %s" % (", ".join(
        "%s (ssh %s)" % (m, c["ssh"]) for m, c in (plan.get("machines") or {}).items()) or "none but this one"))
    if f is not None:
        out += schedule_lines(plan, f)
    out.append("NUMBERS: " + json.dumps(plan["numbers"], sort_keys=True))
    return "\n".join(out)


def forecast_text(plan, f, rate=None) -> tuple:
    res = week_ahead(plan, f, rate=rate)
    if res is None:
        return "\n".join(["COULD NOT LOOK: the week ahead needs a burn rate (pass --rate), the live account and a reset "
                          "time"] + schedule_lines(plan, f)), COULD_NOT_LOOK
    out = ["THE WEEK AHEAD at %s points an hour, %s h, from %s live: %s" % (g(res["rate"]), g(res["hours"]), f["live"],
                                                                             say(res))]
    for e in res["events"]:
        if e["kind"] == "switch":
            out.append("  %s  switch %s -> %s (%s)" % (pacific(e["at"]), e["from"], e["to"], e["why"]))
        else:
            out.append("  %s  reset of %s: %s points above its %s line erased" % (
                pacific(e["at"]), e["account"], g(e["erased"]), "?" if e["line"] is None else g(e["line"]) + "%"))
    if res["idle_pts"]:
        out.append("  %s points of burn find no account (every account at its line), the first at %s" % (
            g(res["idle_pts"]), pacific(res["idle_from"])))
    out += schedule_lines(plan, f)
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
                meter = [x for x in unknown if p["accounts"].get(x, {}).get("kind") == "meter"]
                raise Refused("%s: no Claude account of the plan; repair: one of %s%s" % (
                    ", ".join(unknown), ", ".join(claude_accounts(p)),
                    "; a meter account's step has its place by ./acct step move" if meter else ""))
            lf = life(a, now)
            lines = dict(x.split("=", 1) for x in a.line or [])
            if lf:
                tag = "T%d" % (int(p.get("rev") or 0) + 1)
                new = []
                for acc in a.accounts:
                    base = next((s for s in reversed(p["steps"]) if s["use"] == acc), None) or {"leave": p["numbers"]["floor_pct"]}
                    s = {"name": "%s.%s" % (acc, tag), "use": acc, "leave": base["leave"], **lf}
                    if base.get("schedule") is not None:
                        s["schedule"] = base["schedule"]
                    if lf.get("ends_at_reset_of") is True:
                        s["ends_at_reset_of"] = acc
                    if base.get("when") and acc not in lines:
                        s["when"] = base["when"]
                    if acc in lines:
                        s["leave"] = value(lines[acc])
                        s.pop("schedule", None)
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
        sched = getattr(a, "schedule", None)
        if (a.percent is None) == (sched is None):
            raise Refused("a line is one percent or one --schedule; repair: ./acct line %s 25, or ./acct line %s "
                          "--schedule \"Sat 23:59=40 hold; Tue 13:30=0 ramp\"" % (a.account, a.account))

        def fn(p):
            if a.account not in p["accounts"]:
                raise Refused("%s is no account of the plan; repair: one of %s" % (a.account, ", ".join(p["accounts"])))
            lf, lv = life(a, now), None if sched is not None else value(a.percent)
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
                    s = p["steps"][idx[-1]]
                else:
                    s = {"name": a.account, "use": a.account}
                    p["steps"].append(s)
                s["leave"] = lv
            if sched is not None:
                put_schedule(p, s, sched)
            else:
                s.pop("schedule", None)     # a flat number again
            return p
        return fn, "line %s %s" % (a.account, a.percent if sched is None else "--schedule \"%s\"" % sched)
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
                    elif k == "schedule":
                        put_schedule(p, s, v)
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
                    st = p["steps"][find_step(p, parts[1])]
                    if parts[2] == "schedule" and v != "":
                        put_schedule(p, st, v)
                    else:
                        st[parts[2]] = value(v)
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
    if c == "machine":
        def fn(p):
            ms = p.setdefault("machines", {})
            if a.act == "add":
                if not a.ssh:
                    raise Refused("a machine needs its ssh name; repair: ./acct machine add %s --ssh <name>" % a.name)
                ms[a.name] = {"ssh": a.ssh}
            elif a.name not in ms:
                raise LookupError("NONE: no machine is named %s (%s)" % (a.name, ", ".join(ms) or "the plan lists none"))
            else:
                del ms[a.name]
            return p
        return fn, "machine %s %s" % (a.act, a.name)
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
    """The numbers of the plan file in the shape that account_actuator._check reads (it reads no rule from this)."""
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
            # the actuator's drain before a switch above the line: a rescue's, never a `switch --now`'s
            "pull_drain_max_s": 0 if any(q.get("now") for q in open_requests(plan, f))
            else (0 if dig(N, "rescue.drain_h") is None else N["rescue"]["drain_h"]) * 3600,
            "switch_lead_min": 0, "window_margin_min": 0, "exceptions": [], "level_model": None}


def log(rec: dict) -> None:
    d = plan_dir()
    d.mkdir(parents=True, exist_ok=True)
    with open(d / "log.jsonl", "a") as fh:
        fh.write(json.dumps({"at": iso(time.time()), **rec}, sort_keys=True) + "\n")


def publish_state(plan, f, d) -> None:
    out = plan_dir()
    write_atomic(out / "burn_mode.json", burn_mode(plan, f))
    write_atomic(out / "decision.json", {"at": iso(f["now"]), "rev": plan.get("rev"),
                                         **{k: v for k, v in d.items() if k != "week"}})


def tick(dry=False, seams=None) -> int:
    """The timed pass: account_actuator.check, driven with this file's decision and numbers. seams (tests): the keyword
    arguments of account_actuator.check (meter_fn, poll_fn, runs_fn, burn_fn, orders, now, passes), and `machines`
    (push_machines' seams); with them no live source is read. The rules are plan_in_force's: a pass on a fallback says
    so in its log."""
    import account_actuator as ACT
    seams = dict(seams or {})
    plan, why = plan_in_force()
    if plan is None:
        log({"do": "passive", "why": why})
        print("PASSIVE: " + why)
        return COULD_NOT_LOOK
    if why:
        log({"do": "fallback", "why": why, "rev": plan.get("rev")})
        print("FALLBACK: " + why)
    if active(plan["holds"], clock()):
        h = active(plan["holds"], clock())[0]
        rec = {"do": "passive", "why": "hold %s: %s" % (h["id"], h.get("why"))}
        if plan.get("machines"):    # a hold acts on nothing and refuses nothing: the other machines are told so
            rec["machines"] = push_machines(plan, {"now": clock(), "rows": {}}, pass_now(seams), carry=False,
                                            **(seams.get("machines") or {}))
        log(rec)
        print("PASSIVE: hold %s until %s" % (h["id"], pacific(stamp(h["ends"]))))
        return OK
    last = {}

    def decide_now(meter, live, now, _plan, state, markers, polled=False, manual=None, live_runs=(), burn=None):
        """The actuator's decision: the rules are read again at each call, so a write binds inside a pass."""
        p, w = plan_in_force()
        if p is None:
            return {"do": "passive", "why": w}
        f = frame_for_pass(ACT, meter, live, now, state, markers, manual, live_runs, burn, p)
        # the pass rewrites its own notice before it polls and before it calls the switcher: a drain that this pass
        # found in flight stays in flight for each later decision of the pass
        f["draining"] = last["draining"] = f["draining"] or bool(last.get("draining"))
        d = decide(p, f, polled=polled)
        last.update(plan=p, frame=f, decision=d)
        return d

    def numbers_now():
        p, _w = plan_in_force()
        rows = seams["meter_fn"]() if callable(seams.get("meter_fn")) else None
        return legacy_view(p or plan, {"now": seams.get("now") or time.time(), "rows": rows, "switches": ACT.switches()}
                           if rows is not None else gather_light(ACT))
    rc = ACT.check(decide_now, numbers_now, dry=dry,
                   **({"passes": 5} if not seams else {k: v for k, v in seams.items() if k != "machines"}))
    if "decision" in last:
        f, d = last["frame"], last["decision"]
        if not seams:
            slow = gather(slow=True)
            f.update(codex=slow["codex"], genai=slow["genai"], slow_at=slow["slow_at"], load=slow["load"],
                     ncpu=slow["ncpu"])
        rec = {"do": d["do"], "to": d.get("to"), "live": f.get("live"), "why": d.get("why"), "pct_left": d.get("pct_left"),
               "line": d.get("line"), "runs": None if f["runs"] is None else len(f["runs"]), "rev": last["plan"].get("rev")}
        if not dry and last["plan"].get("machines"):
            rec["machines"] = push_machines(last["plan"], f, pass_now(seams), **(seams.get("machines") or {}))
        log(rec)
        if not dry:
            publish_state(last["plan"], f, d)
            flush_ledger(last["plan"])
    return rc


def timer_pass(seams=None) -> int:
    """What the timer runs (`./acct pass`): one pass of tick, repeating while an account ends."""
    return tick(seams=seams)


def pass_now(seams) -> float:
    """The time of an act of the pass: a test's clock, else now (a pass can last minutes)."""
    import account_actuator as ACT
    return ACT.clock() if seams else time.time()


def gather_light(ACT) -> dict:
    import account_usage as AU
    now = time.time()
    sws = ACT.switches()
    return {"now": now, "rows": AU.read_now(now).get("accounts") or {}, "switches": sws,
            "live": (sws or [{}])[-1].get("to")}


def frame_for_pass(ACT, meter, live, now, state, markers, manual, live_runs, burn, plan) -> dict:
    series, sws = series_rows(), ACT.switches()
    entry = {s["use"]: entry_level(series, sws, s["use"]) for s in plan["steps"] if entry_points(s) is not None}
    return {"now": now, "live": live, "runs": None if live_runs is None else list(live_runs), "rows": meter,
            "notice": ACT.read_json(ACT.OUT / "notice.json", {}), "burn_live": burn, "burn_h": fleet_burn(series, now, plan["numbers"]["forecast"]["burn_window_h"],
                                                    accounts=set(meter)),
            "switches": sws, "hand": bool(manual), "markers": markers, "state": state, "entry": entry,
            "draining": draining(ACT)}


def draining(ACT) -> bool:
    """The actuator's notice says that a drain before a switch above the line is in flight (not an account end)."""
    nt = ACT.read_json(ACT.OUT / "notice.json", {})
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
                print("account_plan: ledger note refused: %s" % str(out), file=sys.stderr)
                return
            write_atomic(d / "ledger_sent.json", {"rev": h["rev"]})
        print("account_plan: " + str(ing.publish(len(owed), message="ledger: account plan")))
    except Exception as e:  # noqa: BLE001  tried again at the next pass
        print("account_plan: ledger notes not written: %s: %s" % (type(e).__name__, e), file=sys.stderr)


# ------------------------------------------------------------------ the command line
class Parser(argparse.ArgumentParser):
    def error(self, message):       # argparse would exit 2, which here means could not look
        raise Refused("%s; repair: ./acct --help" % message)


PAGE = """\
THE OPERATOR'S PAGE: an account end, with no other file open

LOOK
  ./acct status              now and next, the end of the live account, each account as LEFT, each machine, holds
  ./acct next                one line: what the next pass does, and why
  ./acct forecast            the week ahead: each switch and reset, the points that a reset erases
  ./acct readings            each account: what is left, its reset in Pacific time, the age of the reading
  ./acct plan                the steps in order, the lines, the machines, the numbers
  ./acct can-use [A]         may a new run start here now (A: may a job go to that account); exit 0 yes, 1 no, 2 could not look
  ./acct burn-mode           the state that the helper allocator and Codex's door read
  ./acct measures            past weeks: points erased at each reset, switches, runs live at each switch

WHAT THE TIMED PASS DOES BY ITSELF (each 5 minutes; near a line it reads the level more often)
  above the warning line     nothing: the live account stays, whatever the order of the steps
  warning line to the line   each live run gets one warning (save a note, publish, keep working); new runs start, warned
  at the line                no new run; each live run is told to save and end; the switch goes when the last one ends
  at the emergency percent   each Claude process is paused, the level is read again, then the switch goes with runs live
  no account can take over   the fleet stops at the line, and starts again at the first reset
  after a switch             each window is reopened as a new session; a run that ended for the switch is started again, once
  `./acct status` prints these steps with the numbers and the names in force.

CHANGE (each write prints its undo; --why "..." or --owner-said "..." records the reason; none is demanded)
  ./acct hold --for 2h       stop each automatic act (./acct release ends it; a hold ends by itself)
  ./acct switch A --now      go to account A at the next pass (with no --now: at the first pass with no live run)
  ./acct line A N --until-reset    another leave line for A until its reset (burn deeper, or leave earlier)
  ./acct line A --schedule "Sat 23:59=40 hold; Tue 13:30=0 ramp"   a leave line that changes through A's week:
                             each point is the line up to its moment (hold), or a straight line to it from the point
                             before (ramp); ./acct line A N sets one flat number again
  ./acct pin --for 6h        keep the live account: no rescue switch leaves it (./acct unpin ends it)
  ./acct order A B C         which account is next when the live one is finished
  ./acct step add|set|rm|move NAME ...    a step of the plan (use, leave, warn, until, when, a life)
  ./acct set numbers.K=V     one number of the plan (./acct plan prints them)
  ./acct machine add NAME --ssh SSHNAME   another machine that gets this plan's decision (./acct machine rm NAME)
  ./acct whatif -- <a write> the same write on a copy: now, next and the week ahead, before and after; writes nothing
  ./acct undo [REV]          the plan as it was before that change

ANOTHER MACHINE on the same account (./acct status has a line for each)
  Each pass writes it the plan's decision for the account that it is on. At the line it starts no new run and its
  live runs are told to save. With no notice for 20 minutes it starts no new run and says COULD NOT LOOK.
  At the line, once it lists no live helper run, the pass switches it to the next account (claude-account use).
  By hand: ssh -t SSHNAME claude-account-switch NAME ACCOUNT

WHEN IT LOOKS WRONG
  COULD NOT LOOK in status   the meter or the switcher is unread: python3 src/RimMandrake/Utils/account_usage.py poll
  a switch failed            status says so; `claude-account status` shows the logins; the pass tries again from a stopped fleet
  the plan file is refused   ./acct undo   (meanwhile the pass runs on the last revision that history accepted, and says so)
  a launch is refused        ./acct can-use says why; a refusal with ACCOUNT GATE ends by itself after the switch

EXIT  0 done, or yes · 1 no · 2 could not look · 3 refused, nothing written · 4 failed · 5 none
"""


def parser():
    ap = Parser(prog="acct", description="The account plan: one file, one-line commands.", epilog=PAGE,
                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True, parser_class=Parser)
    who = argparse.ArgumentParser(add_help=False)
    for flag in ("--why", "--owner-said", "--by-card", "--per-ruling"):
        who.add_argument(flag, default=None)
    ends = argparse.ArgumentParser(add_help=False)
    ends.add_argument("--for", dest="for_", default=None, help="a life: 90m, 2h, 3d")
    ends.add_argument("--until", default=None, help="a life: an ISO time (Pacific when it has no offset)")
    for name in ("status", "next", "plan", "readings", "burn-mode", "init"):
        p = sub.add_parser(name, parents=[who] if name == "init" else [])
        if name == "init":
            p.add_argument("--replace", action="store_true")
    p = sub.add_parser("forecast")
    p.add_argument("--rate", type=float, default=None, help="points an hour (default: the last 24 h)")
    p = sub.add_parser("measures")
    p.add_argument("--weeks", type=int, default=4)
    p = sub.add_parser("can-use", help="may a job go to this account now; with no account: may a new run start here")
    p.add_argument("account", nargs="?")
    p.add_argument("--carried", action="store_true", help="the run is a continuation of a live run")
    p = sub.add_parser("machine", parents=[who], help="a machine that gets this plan's decision for its account")
    p.add_argument("act", choices=("add", "rm"))
    p.add_argument("name")
    p.add_argument("--ssh", default=None)
    p = sub.add_parser("tick")
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
    p.add_argument("percent", nargs="?")
    p.add_argument("--schedule", default=None, help='a line schedule: "Sat 23:59=40 hold; Tue 13:30=0 ramp"')
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
    return ap


WRITES = ("order", "line", "step", "set", "switch", "pin", "unpin", "hold", "release", "machine")


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
        return tick(dry=a.dry_run)
    if a.cmd == "pass":
        return timer_pass()
    if a.cmd == "init":
        old, _w = load_plan()
        if old is not None and not a.replace:
            raise Refused("a plan file stands (rev %s); repair: --replace to write over it (./acct undo brings it back)"
                          % old.get("rev"))
        new = first_plan()
        rev, _p = commit(lambda _old: new, {**meta_of(a, argv), "create": True}, base=old)
        print("DONE rev %s: the plan file is the first plan of %s (%d steps)\n%s\nundo: ./acct undo %s" % (
            rev, SEED.name, len(new["steps"]), plan_dir() / "plan.json", rev))
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
    if a.cmd == "can-use" and (a.account is None or plan is None):
        rc, text, _role = launch_gate(now, a.carried)
        print(text)
        return rc
    if plan is None:
        print(why if why.startswith(("NONE", "COULD NOT LOOK")) else "REFUSED: " + why)
        return NONE if why.startswith("NONE") else COULD_NOT_LOOK if why.startswith("COULD") else REFUSED
    if a.cmd in WRITES:
        if a.cmd == "pin" and not a.account:
            a.account = gather(now).get("live")
            if not a.account:
                print("COULD NOT LOOK: the live account is unknown; repair: ./acct pin <account>")
                return COULD_NOT_LOOK
        fn, what = change_of(a, now)
        sched = a.cmd == "line" and getattr(a, "schedule", None) is not None
        if sched:       # with the reset measured, a point that is outside the account's week is refused now
            f = gather(now)
            rs = frame_env(f).reset(a.account)
            if rs is not None:
                fl = plan["numbers"]["floor_pct"] if dig(plan, "accounts.%s.kind" % a.account) == "claude" else 0.0
                out = [p["text"] for p, x in zip(parse_schedule(a.schedule, fl), place_schedule(
                    parse_schedule(a.schedule, fl), schedule_at(parse_schedule(a.schedule, fl), rs, now)["reset"]))
                    if x["outside"]]
                if out:
                    raise Refused("%s falls outside the week of %s (from the reset %s to %s); repair: type the points in "
                                  "the order of the week from that reset" % (", ".join(out), a.account, pacific(rs - WEEK),
                                                                            pacific(rs)))
        rev, new = commit(fn, meta_of(a, argv))
        f = gather(now)
        dead = not_alive(plan, new, f)
        if a.cmd == "machine" and a.act == "rm" and not os.environ.get("RM_ACCOUNT_PLAN_FRAME"):
            import account_plan_machines as MS
            ok, err = MS.forget_machine(plan["machines"][a.name]["ssh"])
            what += "" if ok else (" (its follower mark could not be removed: %s; repair: ssh %s rm %s/follows.json)" % (
                err, plan["machines"][a.name]["ssh"], MS.REMOTE_DIR))
        shown = schedule_lines(new, f, [a.account] if a.cmd == "line" else None) if (
            sched or a.cmd in ("step", "set")) else []
        print("DONE rev %s: %s%s\n%s\n%sundo: ./acct undo %s" % (
            rev, what, " (NOT ALIVE NOW: %s)" % dead if dead else "", next_line(new, f),
            "".join(x + "\n" for x in shown), rev))
        return OK
    if a.cmd == "whatif":
        rest = [x for x in a.rest if x != "--"]
        b = parser().parse_args(rest)
        if b.cmd not in WRITES:
            raise Refused("whatif takes a write (%s), not `%s`" % (", ".join(WRITES), b.cmd))
        fn, what = change_of(b, now)
        new = fn(copy.deepcopy(plan))
        bad = problems(new, writing=True)
        if bad:
            raise Refused("; ".join(bad))
        f = gather(now)
        wa, wb = week_ahead(plan, f), week_ahead(new, f)
        print("WHAT IF %s (nothing is written)\nnow:   %s\n       week ahead: %s\nthen:  %s\n       week ahead: %s" % (
            what, next_line(plan, f), say(wa) if wa else "COULD NOT LOOK", next_line(new, f),
            say(wb) if wb else "COULD NOT LOOK"))
        env = frame_env(f)
        for x in plan["accounts"]:
            ra, rb = rule_of(plan, x, env), rule_of(new, x, env)
            la, lb = (None if ra is None else ra["line"]), (None if rb is None else rb["line"])
            if la != lb:
                print("       %s line %s -> %s" % (x, "none" if la is None else g(la) + "%", "none" if lb is None else g(lb) + "%"))
        for ln in schedule_lines(new, f):
            print("       " + ln)
        return OK
    f = gather(now, slow=a.cmd == "can-use" and dig(plan, "accounts.%s.kind" % a.account) == "meter")
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
        rc, text = can_use(plan, f, a.account, a.carried)
        print(text)
        return rc
    if a.cmd == "measures":
        return measures_cmd(plan, f, a.weeks)
    return REFUSED


def line_in_force(plan, a, t, reset):
    """The leave line of the step of `a` in force at t (its reset at `reset`), or None when no step uses `a` then."""
    rl = rule_of(plan, a, Env(t, lambda x: None, lambda x: reset if x == a else None))
    return None if rl is None else rl["line"]


def measures_cmd(plan, f, weeks) -> int:
    import account_actuator as ACT
    rows = f.get("series") if "series" in f else series_rows(tail_bytes=10**9)
    sws = f.get("switches") if "switches" in f else ACT.switches()
    if rows is None:
        print("COULD NOT LOOK: the reader's series cannot be read (%s)" % AE.SERIES)
        return COULD_NOT_LOOK
    m = measures(rows, sws, lambda a, t: standing_line(plan, a, Env(t - 1, lambda x: None, lambda x: t)),
                 since=f["now"] - weeks * WEEK,
                 line_now=lambda a, t, rs: line_in_force(plan, a, t, rs))
    if not m:
        print("NONE: no reset and no switch in the last %d weeks of the series" % weeks)
        return NONE
    print("ALLOWANCE ERASED AT RESETS and SWITCHES, per week (Monday), against the lines of the plan as it is now")
    lg = own_log()
    mine, dark = runs_at_switches(lg), dark_hours(lg)
    for w, v in m.items():
        er = "; ".join("%s %s" % (a, x if isinstance(x, str) else "%s points (%s%% left at its reset)" % (
            g(x), g(v["left_at_reset"][a]))) for a, x in sorted(v["erased"].items())) or "no reset seen"
        k = mine.get(w)
        res = "; ".join("%s %s min under its line, lowest gap %s" % (a, v["under_line_min"].get(a, 0), g(x))
                        for a, x in sorted((v.get("lowest_gap") or {}).items()))
        print("  week of %s: reserve kept: %s" % (w, res or "no reading"))
        dk = dark.get(w)
        print("  week of %s: dark: %s" % (w, "%s h in which the pass refused a new run (%d passes; %d of them with the runs "
                                             "unread)" % (g(dk["dark_h"]), dk["passes"], dk["unread"]) if dk else
                                             "UNMEASURED: the plan's log has no pass that week"))
        print("  week of %s: %d switches; %s; erased: %s" % (w, v["switches"], (
            "%d live runs at the plan's %d switches%s" % (k["runs"], k["switches"], ", %d of them with the runs unread"
                                                          % k["unread"] if k["unread"] else "")) if k else
            "the plan made no switch (its log has none)", er))
    wa = week_ahead(plan, f)
    print("FORECAST for the plan now: " + (say(wa) if wa else "COULD NOT LOOK: no burn rate, live account or reset time"))
    return OK


if __name__ == "__main__":
    sys.exit(main())
