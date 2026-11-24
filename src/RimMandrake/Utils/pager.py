#!/usr/bin/env python3
r"""pager.py — the one program that may ring the owner's phone, through Pushover, for CRITICAL needs only.

Owner, 2026-11-19 ~7:00 PM PST: "I already have Pushover. On trial for now. We should design emergency alert system for
that now, only for CRITICAL needs like hardware failure, inability to switch accounts, or shocking inability to achieve
a stated goal. Conductor or Operations only." Item RIMMANDRAKE_DESIGN_PUSHOVER_ALERTS_CRITICAL_ONLY_TWO_SENDERS.
Design and page: design/specs/2026-11-19-pushover-critical-alerts/{design,boundary}.md. Selftest: selftest_pager.py.

    pager.py send --class C --cause K --reading "..." --why "..." [--item ID] [--goal "<goal title>"] [--dry-run]
    pager.py test --why "..." [--dry-run]       the Conductor's drill: one emergency page of class TEST
    pager.py check-credentials                  Pushover's users/validate call: proves the two values, rings nothing
    pager.py ack [<receipt>]                    did he acknowledge the last page (or this receipt)? reads, rings nothing
    pager.py status                             open faults, failing sends, the last outcome
    pager.py classes                            the closed list (pager_classes.json)

Outcomes, one verdict line `PAGER <OUTCOME> ...` printed last, after the outcome is known, and an exit code each:
    0 SENT            Pushover accepted an emergency-priority page (receipt in the line)
    1 REFUSED         the caller, class, cause, reading, goal or why is not allowed; nothing was sent
    2 REPEAT          the same class and cause paged inside its window: recorded, not rung again
    3 COULD_NOT_SEND  allowed, but the page did not leave (no credentials, network, Pushover said no); cause named
    4 DRY_RUN         --dry-run: says what it would do; no network, no state change
    5 ERROR           the tool itself broke (an exception): no outcome is claimed
Only the Conductor window and an Operations role run may send (caller()). Credentials are read at call time from the
environment (PUSHOVER_USER_KEY, PUSHOVER_APP_TOKEN) or else one file, <RM data root>/secrets/pushover.env
(D:\ClaudeWork\rimmandrake\secrets\pushover.env); a missing value is named, never printed, never defaulted.
"""
import argparse
import datetime as _dt
import fcntl
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

CLASSES_FILE = os.path.join(HERE, "pager_classes.json")
GOALS_FILE = os.path.join(TOP, "infrastructure", "state", "CONDUCTOR_GOALS.md")
API = "https://api.pushover.net/1"

SENT, REFUSED, REPEAT, COULD_NOT_SEND, DRY_RUN = "SENT", "REFUSED", "REPEAT", "COULD_NOT_SEND", "DRY_RUN"
EXIT = {SENT: 0, REFUSED: 1, REPEAT: 2, COULD_NOT_SEND: 3, DRY_RUN: 4}

# Pushover emergency priority (pushover.net/api, read 2026-11-19: retry >= 30 s, expire <= 10800 s, at most 50 retries).
PRIORITY = 2
# A real page rings with "Pushover Echo (long)", his pick of 2026-11-19 (Machinist knowledge/pushover.md). A TEST page
# sends no sound and keeps the app's brief default (owner, 2026-11-23: the default is "very brief" for a real alert and
# "a good test sound").
REAL_SOUND = "echo"
# RETRY_S: how often an unacknowledged page rings again. Danger: a page that rings once is missed while he is away from
# the phone (the Todoist alarms rang never, 2026-11-08); ringing every 30 s for an hour (Pushover's floor) is noise he
# learns to mute. 120 s gives 30 rings in EXPIRE_S.
RETRY_S = 120
# EXPIRE_S: when an unacknowledged page stops ringing. Danger: rings that go on after an hour reach him asleep or away
# for a fault the next page (the dedupe window ending) will raise again; Pushover refuses more than 10800.
EXPIRE_S = 3600
# HTTP_TIMEOUT_S: urllib waits forever without a timeout (its default is None), and the state lock is held across the
# send, so one hung connection would block every later page. A Pushover answer that takes longer is COULD_NOT_SEND.
HTTP_TIMEOUT_S = 20
# The text that reaches Pushover's servers is a fixed template filled with these fields only (design §3.5 of
# phone_alerts_design_20261108.md: never paths, tokens, JPL content, chat text). No slash, backslash, @, quote or
# newline, so no path, address or URL fits. READING_MAX: Pushover's message limit is 1024; a reading is a key and a
# value, and anything longer is not a reading.
CAUSE_RE = re.compile(r"^[a-z0-9][a-z0-9_.:-]{0,79}$")
READING_RE = re.compile(r"^[A-Za-z0-9 _.,:;=<>%+()#-]{1,200}$")
ITEM_RE = re.compile(r"^[A-Z0-9_]{3,64}$")
WHY_MIN_WORDS = 4
KEY_RE = re.compile(r"^[A-Za-z0-9]{30}$")       # Pushover user keys and app tokens are 30 letters and digits

ENV_USER, ENV_TOKEN = "PUSHOVER_USER_KEY", "PUSHOVER_APP_TOKEN"


def now_utc():
    return _dt.datetime.now(_dt.timezone.utc)


def iso(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(s):
    try:
        return _dt.datetime.strptime(str(s), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=_dt.timezone.utc)
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------- where things live

def data_root():
    """<RM data root> (rmpaths: RM_DATA_ROOT, else Lodestar's agent storage root + /rimmandrake); raises by name."""
    import rmpaths
    return str(rmpaths.rm_data_root())


def pager_dir():
    return os.environ.get("RM_PAGER_DIR") or os.path.join(data_root(), "pager")


def credentials_path():
    return os.environ.get("RM_PAGER_CREDENTIALS") or os.path.join(data_root(), "secrets", "pushover.env")


def conductor_log_path():
    return os.environ.get("RM_PAGER_CONDUCTOR_LOG") or os.path.join(data_root(), "conductor", "log.md")


def native(p):
    m = re.match(r"^/mnt/([a-zA-Z])(/.*)?$", p)
    return (m.group(1).upper() + ":" + (m.group(2) or "/").replace("/", "\\")) if m else p


# ---------------------------------------------------------------- the closed list

def load_classes(path=None):
    """-> {name: spec}. Raises ValueError naming the fault when the file or an entry is malformed: a class list that
    cannot be read pages nothing."""
    with open(path or CLASSES_FILE, encoding="utf-8") as f:
        d = json.load(f)
    cl = d.get("classes") if isinstance(d, dict) else None
    if not isinstance(cl, dict) or not cl:
        raise ValueError("pager_classes.json has no `classes` object")
    for name, c in cl.items():
        if not re.match(r"^[A-Z][A-Z0-9_]{2,40}$", name):
            raise ValueError("class name %r is not UPPER_SNAKE" % name)
        if not isinstance(c, dict):
            raise ValueError("class %s is not an object" % name)
        for k in ("label", "senders", "window_h", "template", "means", "added"):
            if k not in c:
                raise ValueError("class %s lacks `%s`" % (name, k))
        if not set(c["senders"]) <= {"conductor", "operations"} or not c["senders"]:
            raise ValueError("class %s: senders must be conductor and/or operations, got %r" % (name, c["senders"]))
        if not isinstance(c["window_h"], (int, float)) or c["window_h"] < 0:
            raise ValueError("class %s: window_h must be a number >= 0" % name)
        a = c["added"]
        if not isinstance(a, dict) or a.get("by") != "CONDUCTOR" or not a.get("on") or not a.get("per"):
            raise ValueError("class %s: `added` must name by CONDUCTOR, on and per (adding a class is the Conductor's "
                             "logged act)" % name)
    return cl


def goal_titles(path=None):
    """-> the bold titles of the numbered goals in the newest (top) block of CONDUCTOR_GOALS.md. Raises OSError when
    the file cannot be read; [] when the top block has no numbered goal."""
    with open(path or GOALS_FILE, encoding="utf-8") as f:
        text = f.read()
    blocks = re.split(r"(?m)^## ", text)
    top = blocks[1] if len(blocks) > 1 else ""
    return [m.group(1).strip() for m in re.finditer(r"(?m)^\d+\.\s+\*\*(.+?)\*\*", top)]


# ---------------------------------------------------------------- who is calling

def _cgroup(path="/proc/self/cgroup"):
    with open(path, encoding="utf-8") as f:
        return f.read()


def caller(env=None, cgroup=None):
    """-> ("conductor" | "operations" | None, why). Two proofs each, an environment and the process's own cgroup (a
    launched run cannot leave its systemd unit by changing its environment):
      conductor   seat BENCH (AGENT_SEAT, else RIMFLOW_SEAT), no RM_ROLE_UNIT, and a cgroup in a window's own scope
                  `claude-seat-BENCH-<pid>.scope` with no rm-* unit on its path (claude_bounded names it so).
      operations  RM_ROLE_UNIT=rm-role-operations-<epoch>, seat BENCH, and that unit's name on the cgroup path
                  (its service, or its claude scope `claude-seat-BENCH-rm-role-operations-<epoch>.scope`).
    An unreadable cgroup proves nothing: None."""
    env = os.environ if env is None else env
    try:
        cg = _cgroup() if cgroup is None else cgroup
    except OSError as e:
        return None, "the caller could not be proved: /proc/self/cgroup unreadable (%s)" % e
    seat = (env.get("AGENT_SEAT") or env.get("RIMFLOW_SEAT") or "").strip().upper()
    unit = (env.get("RM_ROLE_UNIT") or "").strip()
    segs = [s for line in cg.splitlines() for s in line.split(":", 2)[-1].split("/") if s]
    if unit:
        if re.match(r"^rm-role-operations-\d+$", unit):
            if seat != "BENCH":
                return None, "an Operations run on seat %s, not BENCH" % (seat or "unset")
            if any(s in (unit + ".service", "claude-seat-BENCH-%s.scope" % unit) for s in segs):
                return "operations", "the Operations role run %s" % unit
            return None, "RM_ROLE_UNIT says %s but this process is not in that unit (cgroup %s)" % (
                unit, "/".join(segs[-2:]) or "empty")
        return None, "a launched run (RM_ROLE_UNIT=%s) is neither the Conductor window nor an Operations run" % unit
    if seat != "BENCH":
        return None, "seat %s is not the Conductor's (BENCH)" % (seat or "unset")
    if any(re.match(r"^(claude-seat-[A-Za-z]+-)?rm-[a-z]", s) for s in segs):
        return None, "this process runs inside a launched unit (%s) with RM_ROLE_UNIT unset" % next(
            s for s in segs if re.match(r"^(claude-seat-[A-Za-z]+-)?rm-[a-z]", s))
    if any(re.match(r"^claude-seat-BENCH-\d+\.scope$", s) for s in segs):
        return "conductor", "the Conductor window"
    return None, "not in a Conductor window's scope (claude-seat-BENCH-<pid>.scope); cgroup %s" % (
        "/".join(segs[-2:]) or "empty")


# ---------------------------------------------------------------- credentials (never printed)

def read_credentials(env=None, path=None):
    """-> ({"user", "token"}, None) or (None, cause). The environment wins over the file; each value is checked for
    Pushover's shape (30 letters and digits). The cause names the variable and the file, never a value."""
    env = os.environ if env is None else env
    path = path or credentials_path()
    vals = {ENV_USER: (env.get(ENV_USER) or "").strip(), ENV_TOKEN: (env.get(ENV_TOKEN) or "").strip()}
    if not (vals[ENV_USER] and vals[ENV_TOKEN]):
        try:
            with open(path, encoding="utf-8-sig") as f:
                for line in f:
                    m = re.match(r"^\s*(?:export\s+)?([A-Z_]+)\s*=\s*['\"]?([^'\"\s#]*)", line)
                    if m and m.group(1) in vals and not vals[m.group(1)]:
                        vals[m.group(1)] = m.group(2).strip()
        except FileNotFoundError:
            missing = [k for k, v in vals.items() if not v]
            return None, "credentials: %s not set and %s does not exist" % (" and ".join(missing), native(path))
        except OSError as e:
            return None, "credentials: %s could not be read (%s)" % (native(path), type(e).__name__)
    for k, v in vals.items():
        if not v:
            return None, "credentials: %s is not in the environment or %s" % (k, native(path))
        if not KEY_RE.match(v):
            return None, "credentials: %s is not 30 letters and digits (Pushover's shape); check %s" % (k, native(path))
    return {"user": vals[ENV_USER], "token": vals[ENV_TOKEN]}, None


# ---------------------------------------------------------------- the transport

def http_post(url, fields, timeout=HTTP_TIMEOUT_S):
    """-> (http status or None, body text, error or None). Never raises."""
    data = urllib.parse.urlencode(fields).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace"), None
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", "replace")
        except Exception:  # noqa: BLE001
            body = ""
        return e.code, body, "HTTP %d" % e.code
    except Exception as e:  # noqa: BLE001  network down, DNS, TLS, timeout: all are "could not send"
        return None, "", "%s: %s" % (type(e).__name__, e)


def http_get(url, timeout=HTTP_TIMEOUT_S):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace"), None
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", "replace")
        except Exception:  # noqa: BLE001
            body = ""
        return e.code, body, "HTTP %d" % e.code
    except Exception as e:  # noqa: BLE001
        return None, "", "%s: %s" % (type(e).__name__, e)


def pushover_verdict(status, body, err):
    """-> (ok, receipt or None, cause). ok only for HTTP 200 with JSON status 1 and a receipt (emergency priority
    always returns one); anything else is a cause."""
    try:
        j = json.loads(body) if body else {}
    except ValueError:
        j = {}
    if status == 200 and j.get("status") == 1 and j.get("receipt"):
        return True, str(j["receipt"]), "accepted"
    if status is None:
        return False, None, "Pushover unreachable: %s" % err
    errs = j.get("errors") if isinstance(j, dict) else None
    detail = "; ".join(str(x) for x in errs) if isinstance(errs, list) and errs else (err or "no receipt")
    if status == 200:
        return False, None, "Pushover answered 200 without status 1 and a receipt: %s" % detail
    return False, None, "Pushover refused the request (HTTP %s): %s" % (status, detail)


# ---------------------------------------------------------------- the record

def _append(path, line):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(line)


def log_event(rec):
    """One line per attempt in <pager dir>/log.jsonl, whatever the outcome. Returns the error text or None."""
    try:
        _append(os.path.join(pager_dir(), "log.jsonl"), json.dumps(rec, sort_keys=True) + "\n")
        return None
    except OSError as e:
        return "log.jsonl not written: %s" % e


def conductor_line(text, t):
    try:
        _append(conductor_log_path(), "\n%s — PAGER: %s\n" % (iso(t), text))
        return None
    except OSError as e:
        return "conductor log not written: %s" % e


def read_state():
    """-> the state dict. Raises ValueError on a torn or wrong-shaped file (never read as empty: an empty state would
    ring every open fault again)."""
    p = os.path.join(pager_dir(), "state.json")
    try:
        with open(p, encoding="utf-8") as f:
            s = json.load(f)
    except FileNotFoundError:
        return {"open": {}, "failing": {}}
    if not isinstance(s, dict) or not isinstance(s.get("open"), dict) or not isinstance(s.get("failing"), dict):
        raise ValueError("%s is not a pager state (open, failing)" % p)
    return s


def write_state(s):
    p = os.path.join(pager_dir(), "state.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp.%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(s, f, indent=1, sort_keys=True)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, p)


class _Lock:
    """One page at a time: two callers for the same fault in the same second must not both ring. The holder is bounded
    by HTTP_TIMEOUT_S, so the wait is too."""

    def __enter__(self):
        # a pager dir that cannot be written (D: failing is itself a hardware fault) does not stop a critical page:
        # it goes unlocked, and `error` says so
        self.f, self.error = None, None
        try:
            os.makedirs(pager_dir(), exist_ok=True)
            self.f = open(os.path.join(pager_dir(), "state.lock"), "a")
            fcntl.flock(self.f, fcntl.LOCK_EX)
        except OSError as e:
            self.error = "unlocked: %s" % e
        return self

    def __exit__(self, *a):
        if self.f is not None:
            fcntl.flock(self.f, fcntl.LOCK_UN)
            self.f.close()


# ---------------------------------------------------------------- the one door

def _words(s):
    return [w for w in str(s or "").split() if re.search(r"\w", w)]


def validate(cls_name, cause, reading, why, item=None, goal=None, who=None, classes=None, goals_path=None):
    """-> (class spec, None) or (None, refusal cause). Order: class, sender, fields, goal."""
    try:
        classes = classes if classes is not None else load_classes()
    except (OSError, ValueError) as e:
        return None, "the class list could not be read (%s): nothing may page" % e
    c = classes.get(str(cls_name or ""))
    if c is None:
        return None, "class %r is not on the closed list (%s); anything not on it cannot page him" % (
            cls_name, ", ".join(sorted(classes)))
    if who not in c["senders"]:
        return None, "class %s may be sent only by %s, not by %s" % (cls_name, " or ".join(c["senders"]), who)
    if not CAUSE_RE.match(str(cause or "")):
        return None, "--cause must be a reading's key, lower case [a-z0-9_.:-], at most 80 (got %r)" % (cause,)
    if not READING_RE.match(str(reading or "")):
        return None, ("--reading must be 1 to 200 of letters, digits, spaces and _.,:;=<>%+()#- (no path, address, "
                      "URL, quote or newline: the text goes to Pushover's servers)")
    if item is not None and not ITEM_RE.match(item):
        return None, "--item must be an item id (A-Z 0-9 _), got %r" % (item,)
    if len(_words(why)) < WHY_MIN_WORDS:
        return None, "--why must state the reading and why it is critical (at least %d words)" % WHY_MIN_WORDS
    if c.get("needs_goal"):
        try:
            titles = goal_titles(goals_path)
        except OSError as e:
            return None, "the goals file could not be read (%s): a goal page needs it" % e
        if goal not in titles:
            return None, "--goal must be the title of a goal in the top block of CONDUCTOR_GOALS.md (%s)" % (
                "; ".join(titles) or "the top block lists none")
        if not READING_RE.match(goal):
            return None, "the goal title holds characters a page may not carry"
    elif goal is not None:
        return None, "--goal belongs to GOAL_SHOCK only"
    return c, None


def message_for(cls_name, c, reading, item=None, goal=None):
    title = "RimMandrake CRITICAL: %s" % c["label"]
    body = c["template"].format(reading=reading, goal=goal or "")
    if item:
        body += " Item %s." % item
    return title, body


def send(cls_name, cause, reading, why, item=None, goal=None, dry_run=False, env=None, cgroup=None,
         post=None, classes=None, goals_path=None, t=None):
    """The one door. -> (outcome, detail dict). Never raises for a page that could not leave; every outcome is logged."""
    t = t or now_utc()
    post = post or http_post
    who, who_why = caller(env, cgroup)
    rec = {"at": iso(t), "class": cls_name, "cause": cause, "item": item, "caller": who or "refused", "why": why,
           "dry_run": bool(dry_run)}
    if who is None:
        rec.update(outcome=REFUSED, detail="refused: " + who_why)
        log_event(rec)
        return REFUSED, rec
    c, bad = validate(cls_name, cause, reading, why, item, goal, who, classes, goals_path)
    if bad:
        rec.update(outcome=REFUSED, detail="refused: " + bad)
        log_event(rec)
        return REFUSED, rec
    key = "%s:%s" % (cls_name, cause)
    rec["key"] = key
    title, body = message_for(cls_name, c, reading, item, goal)
    with _Lock() as lk:
        if lk.error:
            rec["lock_error"] = lk.error
        try:
            state = read_state()
        except (OSError, ValueError) as e:
            # a state that cannot be read cannot dedupe; a critical page still goes (one extra ring beats a lost one).
            # The torn file is kept aside, never overwritten unread.
            state, rec["state_error"] = {"open": {}, "failing": {}}, str(e)
            p = os.path.join(pager_dir(), "state.json")
            if not dry_run and os.path.exists(p):
                aside = "%s.torn-%s" % (p, t.strftime("%Y%m%dT%H%M%SZ"))
                try:
                    os.replace(p, aside)
                    rec["state_aside"] = aside
                except OSError as e2:
                    rec["state_error"] += "; not moved aside: %s" % e2
        o = state["open"].get(key)
        last = parse_iso(o.get("last_paged")) if isinstance(o, dict) else None
        win = float(c["window_h"]) * 3600.0
        if last is not None and win > 0 and (t - last).total_seconds() < win:
            if dry_run:
                rec.update(outcome=DRY_RUN, detail="dry run: would be a REPEAT of %s paged %s (window %sh): no ring"
                           % (key, o["last_paged"], c["window_h"]))
                log_event(rec)
                return DRY_RUN, rec
            o.update(last_seen=iso(t), repeats=int(o.get("repeats") or 0) + 1, last_reading=reading)
            try:
                write_state(state)
            except OSError as e:
                rec["state_error"] = str(e)
            rec.update(outcome=REPEAT, detail="repeat %d of %s inside %sh of the page at %s: recorded, not rung" % (
                o["repeats"], key, c["window_h"], o["last_paged"]))
            log_event(rec)
            return REPEAT, rec
        creds, cred_bad = read_credentials(env)
        if dry_run:
            rec.update(outcome=DRY_RUN, title=title, message=body,
                       detail="dry run: would page '%s' / '%s' at priority %d (retry %d s, expire %d s); %s" % (
                           title, body, PRIORITY, RETRY_S, EXPIRE_S,
                           cred_bad or "credentials present (not checked with Pushover)"))
            log_event(rec)
            return DRY_RUN, rec
        if cred_bad:
            ok, receipt, why_not = False, None, cred_bad
        else:
            fields = {"token": creds["token"], "user": creds["user"], "title": title, "message": body,
                      "priority": PRIORITY, "retry": RETRY_S, "expire": EXPIRE_S}
            if cls_name != "TEST":
                fields["sound"] = REAL_SOUND
            ok, receipt, why_not = pushover_verdict(*post(API + "/messages.json", fields))
        f = state["failing"].get(key)
        if ok:
            state["open"][key] = {"class": cls_name, "cause": cause, "first_paged": iso(t), "last_paged": iso(t),
                                  "last_seen": iso(t), "repeats": 0, "last_reading": reading, "receipt": receipt}
            state["failing"].pop(key, None)
            state["last_sent"] = {"at": iso(t), "key": key, "receipt": receipt}
            try:
                write_state(state)
            except OSError as e:   # the page left; the record did not (boundary: the next call rings again)
                rec["state_error"] = str(e)
            note = conductor_line("SENT %s (%s): %s receipt %s%s" % (key, who, body, receipt, (
                "; after %d failed attempt(s) since %s" % (f["attempts"], f["since"])) if isinstance(f, dict) else ""),
                t)
            rec.update(outcome=SENT, receipt=receipt, detail="sent: Pushover receipt %s" % receipt)
            if note:
                rec["conductor_log_error"] = note
            log_event(rec)
            return SENT, rec
        first = not isinstance(f, dict)
        state["failing"][key] = {"since": iso(t) if first else f["since"], "last": iso(t), "cause": why_not,
                                 "attempts": 1 if first else int(f.get("attempts") or 0) + 1}
        try:
            write_state(state)
        except OSError as e:
            rec["state_error"] = str(e)
        if first:   # one line when a failing streak starts; every attempt is in log.jsonl
            note = conductor_line("COULD NOT SEND %s (%s): %s. The page did not reach his phone." % (key, who, why_not),
                                  t)
            if note:
                rec["conductor_log_error"] = note
        rec.update(outcome=COULD_NOT_SEND, detail="could not send: " + why_not)
        log_event(rec)
        return COULD_NOT_SEND, rec


def verdict_line(outcome, rec):
    return "PAGER %s class=%s cause=%s %s" % (outcome, rec.get("class"), rec.get("cause"), rec.get("detail", ""))


# ---------------------------------------------------------------- reads that ring nothing

def check_credentials(env=None, post=None):
    """-> (exit, line): 0 valid, 1 Pushover says the user or token is invalid, 3 could not look."""
    creds, bad = read_credentials(env)
    if bad:
        return 3, "CREDENTIALS COULD NOT LOOK: " + bad
    status, body, err = (post or http_post)(API + "/users/validate.json", {"token": creds["token"],
                                                                            "user": creds["user"]})
    try:
        j = json.loads(body) if body else {}
    except ValueError:
        j = {}
    if status == 200 and j.get("status") == 1:
        return 0, "CREDENTIALS VALID: Pushover knows the user key and app token; devices: %s" % (
            ", ".join(j.get("devices") or []) or "none listed")
    if status is None:
        return 3, "CREDENTIALS COULD NOT LOOK: Pushover unreachable: %s" % err
    if status == 400 or j.get("status") == 0:
        return 1, "CREDENTIALS INVALID: %s" % "; ".join(str(x) for x in (j.get("errors") or [err]))[:200]  # cut-ok: terminal display
    return 3, "CREDENTIALS COULD NOT LOOK: Pushover answered HTTP %s" % status


def ack(receipt=None, env=None, get=None):
    """-> (exit, line): 0 acknowledged, 2 not yet (still ringing or expired), 3 could not look."""
    if not receipt:
        try:
            receipt = (read_state().get("last_sent") or {}).get("receipt")
        except (OSError, ValueError) as e:
            return 3, "ACK COULD NOT LOOK: state unreadable: %s" % e
        if not receipt:
            return 3, "ACK COULD NOT LOOK: no page has been sent (state has no last_sent)"
    if not re.match(r"^[A-Za-z0-9]{1,64}$", receipt):
        return 3, "ACK COULD NOT LOOK: %r is not a receipt" % receipt
    creds, bad = read_credentials(env)
    if bad:
        return 3, "ACK COULD NOT LOOK: " + bad
    status, body, err = (get or http_get)("%s/receipts/%s.json?token=%s" % (API, receipt, creds["token"]))
    try:
        j = json.loads(body) if body else {}
    except ValueError:
        j = {}
    if status != 200 or j.get("status") != 1:
        return 3, "ACK COULD NOT LOOK: %s" % (err or "Pushover answered status %r" % j.get("status"))
    if j.get("acknowledged") == 1:
        at = _dt.datetime.fromtimestamp(int(j.get("acknowledged_at") or 0), _dt.timezone.utc)
        return 0, "ACKNOWLEDGED receipt %s at %s" % (receipt, iso(at))
    return 2, "NOT ACKNOWLEDGED receipt %s (expired %s)" % (receipt, "yes" if j.get("expired") == 1 else "no")


def status_lines():
    try:
        s = read_state()
    except (OSError, ValueError) as e:
        return 3, ["PAGER STATE UNREADABLE: %s" % e]
    out = ["open faults (paged, inside or past their window): %d" % len(s["open"])]
    for k, o in sorted(s["open"].items()):
        out.append("  %s paged %s, repeats %s, last %s" % (k, o.get("last_paged"), o.get("repeats"), o.get("last_reading")))
    out.append("failing sends: %d" % len(s["failing"]))
    for k, f in sorted(s["failing"].items()):
        out.append("  %s since %s, %s attempt(s): %s" % (k, f.get("since"), f.get("attempts"), f.get("cause")))
    out.append("last sent: %s" % (json.dumps(s.get("last_sent")) if s.get("last_sent") else "none"))
    return 0, out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("send")
    s.add_argument("--class", dest="cls", required=True)
    s.add_argument("--cause", required=True)
    s.add_argument("--reading", required=True)
    s.add_argument("--why", required=True)
    s.add_argument("--item")
    s.add_argument("--goal")
    s.add_argument("--dry-run", action="store_true")
    te = sub.add_parser("test")
    te.add_argument("--why", required=True)
    te.add_argument("--dry-run", action="store_true")
    sub.add_parser("check-credentials")
    a_ = sub.add_parser("ack")
    a_.add_argument("receipt", nargs="?")
    sub.add_parser("status")
    sub.add_parser("classes")
    a = ap.parse_args(argv)
    try:
        return _run(a)
    except Exception as e:  # noqa: BLE001  the tool broke: no outcome is known, so none is claimed
        print("PAGER ERROR %s: %s (no outcome: whether a page left is unknown; see log.jsonl)" % (type(e).__name__, e))
        return 5


def _run(a):
    if a.cmd in ("send", "test"):
        if a.cmd == "test":
            t = now_utc()
            # a test never dedupes (window_h 0), so each drill gets its own cause
            outcome, rec = send("TEST", "drill:%s" % t.strftime("%Y%m%dt%H%M%S"),
                                "drill from the Conductor window at %s" % iso(t).replace("T", " "), a.why,
                                dry_run=a.dry_run, t=t)
        else:
            outcome, rec = send(a.cls, a.cause, a.reading, a.why, item=a.item, goal=a.goal, dry_run=a.dry_run)
        print(verdict_line(outcome, rec))
        return EXIT[outcome]
    if a.cmd == "check-credentials":
        rc, line = check_credentials()
        print(line)
        return rc
    if a.cmd == "ack":
        rc, line = ack(a.receipt)
        print(line)
        return rc
    if a.cmd == "status":
        rc, lines = status_lines()
        print("\n".join(lines))
        return rc
    try:
        cl = load_classes()
    except (OSError, ValueError) as e:
        print("CLASSES UNREADABLE: %s" % e)
        return 3
    for n, c in cl.items():
        print("%-24s senders=%-21s window=%sh  %s" % (n, "+".join(c["senders"]), c["window_h"], c["means"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
