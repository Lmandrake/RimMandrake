#!/usr/bin/env python3
"""whittle_now.py: the Claude Whittle workers' ops page, written once a minute with no model call.

The owner, 2026-11-11: "Look for our recent, highly polished running.md documents we had for relentless and
artisan. Please make another now for Whittle in the same spirit so I can track their progress."

Writes D:\\ClaudeWork\\rimmandrake\\conductor\\WHITTLE_NOW.md and WHITTLE_NOW_PHONE.md beside the Artisan and
Relentless pages. Run by rm-whittle-now.timer (src/RimMandrake/Utils/systemd/).

    python3 whittle_now.py            build and write both pages
    python3 whittle_now.py --print    build the page to stdout, write nothing
    python3 whittle_now.py --phone    build the phone copy to stdout, write nothing
    python3 whittle_now.py --check    print the page's age; exit 1 when older than 3 minutes

What it reads, per worker folder under D:\\ClaudeWork\\rimmandrake\\whittle_claude\\<worker>\\ (the loop's file
contract, 2026-11-11): worker.json {worker, unit, machine, lane fwlive|offline, game, item, item_started_at, round,
state, note}; loop.log lines "YYYY-MM-DD HH:MM round N start, open=K item=<ID>" and "YYYY-MM-DD HH:MM round N end:
<ID> closed|parked|dropped|failed sha=<sha> tokens=<n>"; progress.md; OWNER_QUESTIONS.md; and the roster
whittle_claude\\workers.json. Any of them may be missing, partial or a little off format: the page says what it could
not read (UNMEASURED, with the reason) and never stops for it.

Truth about an item comes from the rimflow ledger of the clone this runs from (the dispatch clone, which the belt
keeps level with origin): a worker saying "closed" is a claim; closed in the ledger is the only "accepted".

Read-only by rule: it writes nothing but its two pages and its own state file, never calls the game's bridge, calls
no model. Stdlib only; every subprocess has a timeout. Machine and account readers are artisan_now.py's, imported.
"""

import datetime as dt
import json
import os
import re
import sys
import threading
import time
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import artisan_now as A  # noqa: E402  (the shared readers and the picture's drawing kit)
from artisan_now import Unmeasured, ago, cell, clock, mtime, now_s, read_tail, read_text, run, short, toks, write_atomic  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RIMFLOW = os.path.join(REPO, "src", "RimMandrake", "rimflow")
ROOT = os.environ.get("WHITTLE_ROOT", "/mnt/d/ClaudeWork/rimmandrake/whittle_claude")
NATIVE_ROOT = r"D:\ClaudeWork\rimmandrake\whittle_claude"
OUT_DIR = os.environ.get("WHITTLE_NOW_OUT", "/mnt/d/ClaudeWork/rimmandrake/conductor")
NATIVE_OUT = r"D:\ClaudeWork\rimmandrake\conductor"
NOTICE = os.environ.get("WHITTLE_NOTICE", "/mnt/d/ClaudeWork/rimmandrake/switching_plan/notice.json")
LANE_FILE = os.path.join(REPO, "infrastructure", "state", "flowworks_lane.json")
STEVE_HOST = os.environ.get("WHITTLE_STEVE_SSH", "stevedesktop-wsl")

STALE_PAGE_S = 180
STUCK_ROUNDS = 2            # more rounds than this on one item is stuck (the brief: "stuck >2 rounds")
STUCK_RUNS = 3              # more non-pass ledger runs in a row than this is stuck (">3 non-pass runs")
QUIET_S = 45 * 60           # unit up and no file of the worker written for this long: it may be hung
CLAIM_GRACE_S = 15 * 60     # a "closed" the ledger has not caught up with after this long is a mismatch
WINDOW_S = 12 * 3600        # the picture shows at most this much of the clock
ROUNDS_SHOWN = 12
IGNORED_DIRS = {"tools", "logs", "archive", "old"}
OUTCOMES = ("closed", "parked", "dropped", "failed", "blocked", "timeout", "skipped", "error")


# ---- small readers -----------------------------------------------------------------------------------

def parse_when(v):
    """Epoch seconds from an epoch number, an ISO stamp or 'YYYY-MM-DD HH:MM[:SS]' on the local clock; else None."""
    if v is None or v == "":
        return None
    if isinstance(v, (int, float)):
        return float(v) / 1000 if v > 1e11 else float(v)
    s = str(v).strip()
    if re.fullmatch(r"\d{9,13}(\.\d+)?", s):
        return parse_when(float(s))
    try:
        d = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        m = re.match(r"(\d{4}-\d\d-\d\d)[ T](\d\d:\d\d(?::\d\d)?)", s)
        if not m:
            return None
        try:
            d = dt.datetime.fromisoformat("%s %s" % (m[1], m[2]))
        except ValueError:
            return None
    if d.tzinfo is None:
        d = d.astimezone()      # a naive stamp is the local clock, as the loop writes it
    return d.timestamp()


def read_json(path):
    """(value, None) or (None, reason)."""
    try:
        with open(path, encoding="utf-8-sig") as f:
            return json.load(f), None
    except FileNotFoundError:
        return None, "missing"
    except (OSError, ValueError) as e:
        return None, "unreadable (%s)" % short(e, 80)


def today_start():
    d = dt.datetime.fromtimestamp(now_s()).astimezone()
    return d.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()


def plain_state(s):
    return re.sub(r"[_-]+", " ", str(s or "")).strip().lower()


def int_of(text):
    """'12,345' / '1.2M' / '340k' -> int, else None."""
    if text is None:
        return None
    m = re.fullmatch(r"([\d.,]+)\s*([kKmM]?)", str(text).strip())
    if not m:
        return None
    try:
        n = float(m[1].replace(",", ""))
    except ValueError:
        return None
    return int(n * {"": 1, "k": 1e3, "m": 1e6}[m[2].lower()])


# ---- the loop log ------------------------------------------------------------------------------------

STAMP = r"(\d{4}-\d\d-\d\d[ T]\d\d:\d\d(?::\d\d)?(?:\.\d+)?(?:Z|[+-]\d\d:?\d\d)?)"
ROUND_LINE = re.compile(r"^\s*\[?" + STAMP + r"\]?\s+round\s+#?(\d+)\s+(start|started|begin|end|ended|done)\b[\s,:;-]*(.*)$", re.I)
STAMPED = re.compile(r"^\s*\[?" + STAMP + r"\]?\s+(.*)$")
ITEM_ID = re.compile(r"\b([A-Z][A-Z0-9]*(?:_[A-Z0-9]+){1,})\b")
KV = re.compile(r"\b(open|item|sha|tokens|outcome|result)\s*[=:]\s*([^\s,;]+)", re.I)


def parse_loop_log(text):
    """-> (rounds by number, other stamped lines [(t, text)], lines it could not read)."""
    rounds, other, odd = {}, [], 0
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        m = ROUND_LINE.match(line)
        if not m:
            s = STAMPED.match(line)
            if s:
                other.append((parse_when(s[1]), s[2]))
            else:
                odd += 1
            continue
        t, n, kind, rest = parse_when(m[1]), int(m[2]), m[3].lower(), m[4]
        kv = {k.lower(): v for k, v in KV.findall(rest)}
        r = rounds.setdefault(n, {"n": n, "start": None, "end": None, "item": None, "outcome": None,
                                  "sha": None, "tokens": None, "open": None})
        if kind in ("start", "started", "begin"):
            r["start"] = t
            r["open"] = int_of(kv.get("open"))
            item = kv.get("item")
            if item and item.lower() not in ("none", "-", "null"):
                r["item"] = item.strip("`*")
        else:
            r["end"] = t
            words = re.findall(r"[A-Za-z]+", rest.lower())
            r["outcome"] = (kv.get("outcome") or kv.get("result") or next((w for w in words if w in OUTCOMES), None) or
                            (words[0] if words else "ended"))
            r["outcome"] = r["outcome"].lower()
            ids = ITEM_ID.findall(re.sub(r"\b(sha|tokens|open)\s*[=:]\s*\S+", "", rest, flags=re.I))
            if ids:
                r["end_item"] = ids[0]
                r["item"] = r["item"] or ids[0]
            sha = kv.get("sha")
            r["sha"] = sha if sha and re.fullmatch(r"[0-9a-fA-F]{6,40}", sha) else None
            r["tokens"] = int_of(kv.get("tokens"))
    return rounds, other, odd


# ---- workers -----------------------------------------------------------------------------------------

def read_roster(root, sources):
    """-> {name: info} from workers.json, tolerant of a list, a {"workers": [...]} wrapper or a name map."""
    path = os.path.join(root, "workers.json")
    data, why = read_json(path)
    if why:
        sources.add("roster workers.json", None, "%s: %s" % (why, path))
        return {}, why
    sources.file("roster workers.json", path)
    if isinstance(data, dict) and isinstance(data.get("workers"), (list, dict)):
        data = data["workers"]
    out = {}
    if isinstance(data, list):
        for w in data:
            if isinstance(w, dict) and (w.get("worker") or w.get("name")):
                out[str(w.get("worker") or w.get("name"))] = w
            elif isinstance(w, str):
                out[w] = {}
    elif isinstance(data, dict):
        for k, v in data.items():
            if not str(k).startswith("_"):
                out[str(k)] = v if isinstance(v, dict) else {}
    else:
        return {}, "not a list or an object"
    return out, None


def discover(root, sources):
    """Every worker the roster names or a folder holds. -> ([rec], roster_why)."""
    roster, roster_why = read_roster(root, sources)
    names = list(roster)
    try:
        for e in sorted(os.scandir(root), key=lambda e: e.name):
            if not e.is_dir() or e.name.startswith(".") or e.name.lower() in IGNORED_DIRS or e.name in names:
                continue
            if any(os.path.exists(os.path.join(e.path, f)) for f in ("worker.json", "loop.log", "progress.md")):
                names.append(e.name)
    except OSError as e:
        sources.add("whittle folder", None, "unreadable: %s" % e)
    return [read_worker(root, n, roster.get(n) or {}) for n in names], roster_why


def read_worker(root, name, roster_info):
    folder = os.path.join(root, name)
    rec = {"name": name, "dir": folder, "why": [], "files": {}}
    info = dict(roster_info)
    wj, why = read_json(os.path.join(folder, "worker.json"))
    if why:
        rec["why"].append("worker.json %s" % why)
    elif not isinstance(wj, dict):
        rec["why"].append("worker.json is not an object")
    else:
        info.update({k: v for k, v in wj.items() if v not in (None, "")})
    rec["info"] = info
    for f in ("worker.json", "loop.log", "progress.md", "OWNER_QUESTIONS.md"):
        rec["files"][f] = mtime(os.path.join(folder, f))
    rec["rounds"], rec["other"], rec["odd"] = {}, [], 0
    try:
        rec["rounds"], rec["other"], rec["odd"] = parse_loop_log(read_tail(os.path.join(folder, "loop.log"), 600_000))
    except FileNotFoundError:
        rec["why"].append("no loop.log yet")
    except OSError as e:
        rec["why"].append("loop.log unreadable (%s)" % short(e, 60))
    for f, key in (("progress.md", "progress"), ("OWNER_QUESTIONS.md", "questions")):
        try:
            rec[key] = read_text(os.path.join(folder, f), 120_000)
        except FileNotFoundError:
            rec[key] = None
        except OSError as e:
            rec[key] = None
            rec["why"].append("%s unreadable (%s)" % (f, short(e, 60)))
    return rec


def worker_units(recs):
    """[(unit, host)] to ask about. A unit runs on Archmagi unless the worker file says otherwise or Archmagi lacks it."""
    out = []
    for r in recs:
        u = r["info"].get("unit")
        if u:
            u = str(u) if "." in str(u) else "%s.service" % u
            r["unit"] = u
            out.append(u)
    return out


SHOW_PROPS = "Id,LoadState,ActiveState,SubState,ActiveEnterTimestamp,Result"


def parse_show(text):
    """systemctl show output for several units -> {Id: props}."""
    out = {}
    for block in re.split(r"\n\s*\n", text.strip()):
        props = dict(l.split("=", 1) for l in block.splitlines() if "=" in l)
        if props.get("Id"):
            out[props["Id"]] = props
    return out


def units_local(units):
    if not units:
        return {}
    rc, out, err = run(["systemctl", "--user", "show", "-p", SHOW_PROPS] + units, timeout=6)
    if rc and not out:
        raise Unmeasured("systemctl: %s" % short(err or "exit %d" % rc, 80))
    return parse_show(out)


def units_remote(units):
    if not units:
        return {}
    cmd = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=4", "-o", "LogLevel=ERROR", STEVE_HOST,
           "systemctl", "--user", "show", "-p", SHOW_PROPS] + units
    rc, out, err = run(cmd, timeout=9)
    if rc and not out:
        raise Unmeasured("ssh %s: %s" % (STEVE_HOST, short(err or "exit %d" % rc, 80)))
    return parse_show(out)


def read_units(recs, sources):
    """Unit state per worker, in r["unit_state"]: {word, host, since, detail}. Unreachable is not stopped."""
    units = worker_units(recs)
    try:
        local = units_local(units)
        sources.add("systemd on Archmagi", 0, None)
    except Unmeasured as e:
        local, local_why = {}, str(e)
        sources.add("systemd on Archmagi", None, local_why)
    remote_want = [r["unit"] for r in recs if r.get("unit") and (
        str(r["info"].get("unit_host", "")).lower().startswith("steve") or
        (local.get(r["unit"], {}).get("LoadState") == "not-found" and str(r["info"].get("machine", "")).lower().startswith("steve")))]
    remote, remote_why = {}, None
    if remote_want:
        try:
            remote = units_remote(remote_want)
            sources.add("systemd on SteveDesktop (ssh)", 0, None)
        except Unmeasured as e:
            remote_why = str(e)
            sources.add("systemd on SteveDesktop (ssh)", None, remote_why)
    for r in recs:
        u = r.get("unit")
        if not u:
            r["unit_state"] = {"word": "no unit named", "host": None}
            continue
        if u in remote_want:
            host = "SteveDesktop"
            if remote_why:
                r["unit_state"] = {"word": "unreachable", "host": host, "detail": remote_why}
                continue
            p = remote.get(u)
        else:
            host = "Archmagi"
            p = local.get(u)
            if p is None and not local:
                r["unit_state"] = {"word": "UNMEASURED", "host": host, "detail": "systemd did not answer"}
                continue
        if not p or p.get("LoadState") == "not-found":
            r["unit_state"] = {"word": "not installed", "host": host}
            continue
        word = p.get("ActiveState", "unknown")
        r["unit_state"] = {"word": word, "sub": p.get("SubState"), "host": host,
                           "since": parse_systemd_time(p.get("ActiveEnterTimestamp")), "result": p.get("Result")}


def parse_systemd_time(s):
    m = re.match(r"\w+ (\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)", s or "")
    return parse_when(m[1]) if m else None


# ---- the ledger --------------------------------------------------------------------------------------

def load_ledger(sources):
    """-> (events, world) from the rimflow ledger of this clone."""
    if RIMFLOW not in sys.path:
        sys.path.insert(0, RIMFLOW)
    try:
        import cli as rimflow_cli   # noqa: E402
        evs, w = rimflow_cli.load()
    except BaseException as e:  # rimflow's die() is a SystemExit; the page must not stop for it
        why = "rimflow could not read the ledger: %s" % short(e, 100)
        sources.add("rimflow ledger", None, why)
        raise Unmeasured(why)
    sources.add("rimflow ledger (%d items)" % len(w.items), 0, None)
    return evs, w


def event_time(evs, index):
    try:
        return parse_when(evs[index].get("ts"))
    except (IndexError, TypeError, AttributeError):
        return None


def nonpass_tail(item):
    n = 0
    for r in reversed(getattr(item, "runs", None) or []):
        if str(getattr(r, "result", "")).lower() == "pass":
            break
        n += 1
    return n


def truth(ledger, iid):
    """What the ledger says about one item: {known, state, title, word, closed, sha, at, nonpass}."""
    if not iid:
        return {"known": False, "word": "no item"}
    if ledger is None:
        return {"known": False, "word": "UNMEASURED (ledger unread)"}
    evs, w = ledger
    it = w.items.get(iid)
    if it is None:
        return {"known": False, "word": "not in the ledger"}
    state = it.state
    out = {"known": True, "state": state, "title": it.title, "closed": state == "done", "sha": it.closed_sha,
           "nonpass": nonpass_tail(it), "runs": len(it.runs or [])}
    if state == "done":
        out["at"] = event_time(evs, it.done_index)
        out["word"] = "closed in the ledger%s%s" % (" %s" % clock(out["at"]) if out["at"] else "",
                                                    ", commit %s" % it.closed_sha if it.closed_sha else "")
    elif state in ("dropped", "superseded"):
        out["word"] = "%s in the ledger" % state + (" by %s" % getattr(it, "superseded_by", None) if getattr(it, "superseded_by", None) else "")
    else:
        lease = getattr(it, "lease", None)
        holder = lease.get("seat") if isinstance(lease, dict) else getattr(lease, "seat", None) if lease else None
        out["word"] = "open in the ledger, %s%s%s" % (state, ", held by %s" % holder if holder else "",
                                                       ", blocked" if it.blocked else "")
    return out


def lane_count(ledger, sources):
    """FlowWorks items still open in the ledger, by the lane file's id patterns."""
    if ledger is None:
        raise Unmeasured("ledger unread")
    data, why = read_json(LANE_FILE)
    if why:
        sources.add("FlowWorks lane file", None, why)
        raise Unmeasured("lane file %s" % why)
    sources.file("FlowWorks lane file", LANE_FILE)
    pats = []
    for p in data.get("id_patterns") or []:
        try:
            pats.append(re.compile(p))
        except re.error:
            pass
    if not pats:
        raise Unmeasured("the lane file has no id pattern")
    evs, w = ledger
    fw = [it for it in w.items.values() if any(p.search(it.id) for p in pats)]
    opened = [it for it in fw if it.open]
    by_state = {}
    for it in opened:
        by_state[it.state] = by_state.get(it.state, 0) + 1
    t0 = today_start()
    closed_today = [it for it in fw if it.state == "done" and (event_time(evs, it.done_index) or 0) >= t0]
    owner = sum(1 for it in opened if it.needs == "owner")
    return {"open": len(opened), "by_state": by_state, "closed_today": len(closed_today), "needs_owner": owner,
            "total": len(fw)}


# ---- machines, accounts, bridge ---------------------------------------------------------------------

def read_notice(sources):
    data, why = read_json(NOTICE)
    if why:
        sources.add("account switcher notice.json", None, why)
        return None
    sources.file("account switcher notice.json", NOTICE)
    return data if isinstance(data, dict) else None


def bridge_lines(ledger):
    if ledger is None:
        return {}
    out = {}
    for host, b in (getattr(ledger[1], "bridge_hosts", None) or {}).items():
        if not isinstance(b, dict):
            continue
        since = parse_when(b.get("since"))
        if b.get("holder"):
            out[host] = "held by %s%s, since %s" % (b["holder"], " for %s" % short(b["purpose"], 80) if b.get("purpose") else "",
                                                    clock(since))
        else:
            out[host] = "free since %s" % clock(since)
    return out


# ---- reading one worker ------------------------------------------------------------------------------

def assess(r, ledger):
    """Derive what the page says about a worker, in r itself."""
    info = r["info"]
    rounds = sorted(r["rounds"].values(), key=lambda x: (x["start"] or x["end"] or 0, x["n"]))
    r["rounds_sorted"] = rounds
    for x in rounds:
        x["truth"] = truth(ledger, x["item"]) if x["item"] else {"known": False, "word": "no item"}
    t0 = today_start()
    ended = [x for x in rounds if x["end"]]
    r["closed_today"] = [x for x in ended if x["outcome"] == "closed" and x["end"] >= t0]
    r["accepted_today"] = [x for x in r["closed_today"] if x["truth"].get("closed")]
    r["tokens_today"] = sum(x["tokens"] or 0 for x in ended if x["end"] >= t0)
    r["tokens_all"] = sum(x["tokens"] or 0 for x in ended)
    r["tokens_seen"] = any(x["tokens"] is not None for x in ended)
    r["counts"] = {}
    for x in ended:
        r["counts"][x["outcome"]] = r["counts"].get(x["outcome"], 0) + 1
    live = rounds[-1] if rounds and not rounds[-1]["end"] else None
    r["live_round"] = live
    item = info.get("item") or (live and live["item"])
    if item in ("", "none", "None", "-"):
        item = None
    r["item"] = item
    r["item_truth"] = truth(ledger, item) if item else {"known": False, "word": "no item"}
    started = parse_when(info.get("item_started_at")) or (live and live["start"])
    r["item_since"] = started
    # rounds spent on the current item: the run of the newest rounds that name it
    on = 0
    for x in reversed(rounds):
        if x["item"] == item:
            on += 1
        else:
            break
    r["rounds_on_item"] = on if item else 0
    r["round_no"] = info.get("round") if info.get("round") not in (None, "") else (rounds[-1]["n"] if rounds else None)
    last_write = max([t for t in r["files"].values() if t] or [0]) or None
    r["last_write"] = last_write
    us = r.get("unit_state") or {}
    st = plain_state(info.get("state"))
    if us.get("word") == "active":
        r["state_word"] = "working" if not st or st in ("working", "running", "round", "busy", "active") else st
    elif us.get("word") in ("activating", "reloading"):
        r["state_word"] = "starting"
    elif us.get("word") in ("failed",):
        r["state_word"] = "UNIT FAILED"
    elif us.get("word") == "inactive":
        r["state_word"] = "stopped" if st not in ("done", "finished", "drained", "out of work") else st
    elif us.get("word") == "unreachable":
        r["state_word"] = "%s (machine unreachable)" % (st or "UNMEASURED")
    else:
        r["state_word"] = st or "UNMEASURED"
    r["questions_list"] = A.parse_questions(r["questions"]) if r.get("questions") and not re.fullmatch(
        r"\s*(#[^\n]*\n)?\s*(none|no questions?( yet)?|nothing( yet)?|-)?\.?\s*", r["questions"], re.I) else []
    return r


def needs_for(r):
    """Plain sentences for 'Needs you' about one worker, each a (rank, text)."""
    out = []
    n = r["name"]
    title = item_title(r["item"], r["item_truth"])
    if r["questions_list"]:
        q = r["questions_list"]
        out.append((1, '**%s asks you %d question%s**, written %s ago, first: "%s". In full under its section.' % (
            n, len(q), "" if len(q) == 1 else "s", ago(now_s() - (r["files"]["OWNER_QUESTIONS.md"] or now_s())), q[0]["title"])))
    if r["item"] and r["rounds_on_item"] > STUCK_ROUNDS and not r["item_truth"].get("closed"):
        out.append((2, "**%s is stuck on %s**: %d rounds on it%s." % (
            n, title, r["rounds_on_item"], ", %s on it" % ago(now_s() - r["item_since"]) if r["item_since"] else "")))
    np = r["item_truth"].get("nonpass") or 0
    if r["item"] and np > STUCK_RUNS and not r["item_truth"].get("closed"):
        out.append((2, "**%s's item %s has failed %d ledger runs in a row** (none passed since). The Test Pilot rule routes it to a live sitting." % (
            n, title, np)))
    us = r.get("unit_state") or {}
    st = plain_state(r["info"].get("state"))
    if us.get("word") == "failed":
        out.append((2, "**%s's unit `%s` has failed** on %s%s." % (n, r["unit"], us.get("host"), " (%s)" % us["result"] if us.get("result") not in (None, "success") else "")))
    elif us.get("word") == "inactive" and st in ("working", "running", "round", "busy", "active"):
        out.append((2, "**%s's file says it is working, but its unit `%s` is stopped** on %s. Its last write was %s ago." % (
            n, r["unit"], us.get("host"), ago(now_s() - r["last_write"]) if r["last_write"] else "never")))
    if us.get("word") == "active" and r["last_write"] and now_s() - r["last_write"] > QUIET_S:
        out.append((3, "**%s has written nothing for %s** while its unit runs. It may be hung." % (n, ago(now_s() - r["last_write"]))))
    for x in r["rounds_sorted"]:
        if x["outcome"] == "closed" and x["end"] and now_s() - x["end"] > CLAIM_GRACE_S and x["truth"].get("known") is not None \
                and not x["truth"].get("closed") and x["truth"].get("word") != "UNMEASURED (ledger unread)":
            out.append((3, "**%s said it closed %s in round %d, %s ago, but the ledger says: %s.** Not accepted until the ledger closes it." % (
                n, item_title(x["item"], x["truth"]), x["n"], ago(now_s() - x["end"]), x["truth"]["word"])))
    tail = []
    for x in reversed([x for x in r["rounds_sorted"] if x["end"]]):
        if x["outcome"] in ("failed", "error", "timeout"):
            tail.append(x)
        else:
            break
    if len(tail) >= 2:
        out.append((3, "**%s's last %d rounds failed** (rounds %s)." % (n, len(tail), ", ".join(str(x["n"]) for x in reversed(tail)))))
    if r["why"] and any("worker.json" in w for w in r["why"]):
        out.append((4, "%s: %s, so its state is taken from its unit and its item from its loop.log." % (n, "; ".join(w for w in r["why"] if "worker.json" in w))))
    return out


def item_title(iid, t):
    if not iid:
        return "no item"
    title = t.get("title") if t else None
    return "`%s` (%s)" % (iid, short(title, 90)) if title else "`%s`" % iid


# ---- the picture -------------------------------------------------------------------------------------

OUT_COLOUR = {"closed": "#2aa98a", "parked": "#b28a00", "dropped": "#6b7380", "failed": "#ff5a4d",
              "running": "#4f97d6", "other": "#b277d6", "noend": "url(#arcHatch)"}
OUT_WORD = {"closed": "closed", "parked": "parked", "dropped": "dropped", "failed": "failed", "running": "running now",
            "other": "other end", "noend": "no end line, unit not running"}


def picture(recs):
    P = A.Pic()
    W = A.PIC_W
    left, right = 150, W - 150
    now = now_s()
    starts = [x["start"] for r in recs for x in r["rounds_sorted"] if x["start"]]
    t_from = max(now - WINDOW_S, (min(starts) - 900) if starts else now - 3600)
    t_from = min(t_from, now - 3600)
    span = now - t_from

    def X(t):
        return left + (max(t, t_from) - t_from) / span * (right - left)

    x0 = 12
    for k in ("closed", "parked", "dropped", "failed", "running", "other", "noend"):
        P.rect(x0, 12, 11, 11, OUT_COLOUR[k], rx=2)
        P.text(x0 + 15, 22, OUT_WORD[k])
        x0 += 15 + A.text_w(OUT_WORD[k], 11) + 16
    P.text(W - 12, 22, "as of %s" % clock(now), weight="600", anchor="end")
    P.text(12, 39, "Each block is one round of a worker, its width the round's real time, coloured by how it ended. Round number inside.", colour=A.DIM)
    row_h, top = 46, 62
    h = top + max(1, len(recs)) * row_h + 10
    step = next(s for s in (900, 1800, 3600, 7200, 10800, 21600) if span / s <= 8)
    t = (int(t_from) // step + 1) * step
    while t < now - step * 0.3:
        x = X(t)
        P.line(x, top, x, h - 8, A.EDGE)
        P.text(x, top - 4, dt.datetime.fromtimestamp(t).strftime("%H:%M"), size=10.5, colour=A.DIM, anchor="middle")
        t += step
    P.line(X(now), top, X(now), h - 8, A.TEXT)
    P.text(X(now), top - 4, "now", size=10.5, weight="700", anchor="middle")
    if not recs:
        P.text(W / 2, top + 28, "No Whittle workers yet: no roster and no worker folder.", size=13, colour=A.DIM, anchor="middle")
    for i, r in enumerate(recs):
        y = top + i * row_h
        alert = any(rank <= 2 for rank, _ in needs_for(r))
        P.text(12, y + 18, short(r["name"], 18), size=14, weight="700", colour=A.ALERT if alert else A.TEXT)
        P.text(12, y + 34, short(r["state_word"].replace("machine unreachable", "unreachable"), 24), size=10.5, colour=A.ALERT if alert else A.DIM)
        P.line(left, y + row_h - 4, right, y + row_h - 4, "#262b34")
        for x in r["rounds_sorted"]:
            a = x["start"] or x["end"]
            b = x["end"] or (now if x is r["live_round"] else None)
            if a is None or b is None or b < t_from:
                continue
            up = (r.get("unit_state") or {}).get("word") in ("active", "activating", "unreachable", "UNMEASURED", None)
            kind = ("running" if up else "noend") if not x["end"] else (x["outcome"] if x["outcome"] in OUT_COLOUR else "other")
            xa, xb = X(a), X(b)
            tip = "round %d: %s, %s%s" % (x["n"], x["item"] or "no item", OUT_WORD.get(kind, kind) if kind != "other" else x["outcome"],
                                          ", ledger: %s" % x["truth"]["word"] if x["item"] else "")
            P.rect(xa, y + 8, max(2.5, xb - xa - 1), 24, OUT_COLOUR[kind], rx=2, title=tip)
            if xb - xa > 20:
                P.text((xa + xb) / 2, y + 24, x["n"], size=10.5, colour=A.TEXT if kind == "noend" else A.INK, weight="600", anchor="middle")
        side = "%d closed today" % len(r["closed_today"])
        if r["closed_today"] and len(r["accepted_today"]) != len(r["closed_today"]):
            side += ", %d in ledger" % len(r["accepted_today"])
        P.text(right + 12, y + 18, side, size=11, weight="600")
        sub = "%s tokens today" % toks(r["tokens_today"]) if r["tokens_seen"] else "tokens not logged"
        P.text(right + 12, y + 33, sub, size=10.5, colour=A.DIM)
    label = "Whittle workers on one clock: " + ("; ".join("%s %s" % (r["name"], r["state_word"]) for r in recs) or "none yet")
    return P.out(h, label)


# ---- the page ----------------------------------------------------------------------------------------

def unit_text(r):
    us = r.get("unit_state") or {}
    if not r.get("unit"):
        return "none named"
    w = us.get("word")
    host = us.get("host") or "?"
    if w == "active":
        return "`%s` on %s: running%s" % (r["unit"], host, " since %s" % clock(us["since"]) if us.get("since") else "")
    if w == "unreachable":
        return "`%s` on %s: **unreachable** (%s), not known to be stopped" % (r["unit"], host, short(us.get("detail"), 70))
    if w == "UNMEASURED":
        return "`%s` on %s: UNMEASURED (%s)" % (r["unit"], host, us.get("detail"))
    return "`%s` on %s: **%s**" % (r["unit"], host, w)


def lane_word(info):
    lane = str(info.get("lane") or "").lower()
    if lane == "fwlive":
        return "live FlowWorks, drives the game"
    if lane == "offline":
        return "offline, no game"
    return lane or "UNMEASURED"


def glance(recs):
    rows = ["| Worker | State | Machine | Kind | Now on | On it for | Round | Closed today | Tokens today |",
            "|---|---|---|---|---|---|---|---|---|"]
    for r in recs:
        info = r["info"]
        closed = "%d" % len(r["closed_today"])
        if len(r["accepted_today"]) != len(r["closed_today"]):
            closed += " said, %d in ledger" % len(r["accepted_today"])
        on = item_title(r["item"], r["item_truth"]) if r["item"] else "no item"
        rows.append("| **%s** | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            cell(r["name"]), cell(r["state_word"].upper() if r["state_word"] not in ("working",) else "working"),
            cell(info.get("machine") or "UNMEASURED"), cell(lane_word(info)), cell(on),
            cell(A.hm(now_s() - r["item_since"]) if r["item"] and r["item_since"] else "-"),
            cell(r["round_no"] if r["round_no"] is not None else "-"), cell(closed),
            cell("~" + toks(r["tokens_today"]) if r["tokens_seen"] else "not logged")))
    return rows


def round_rows(r):
    rows = ["| Round | Started | Took | Item | Ended | Ledger now | Commit | Tokens |", "|---|---|---|---|---|---|---|---|"]
    for x in r["rounds_sorted"][-ROUNDS_SHOWN:][::-1]:
        took = A.hm((x["end"] or now_s()) - x["start"]) if x["start"] else "-"
        up = (r.get("unit_state") or {}).get("word") in ("active", "activating", "unreachable", "UNMEASURED", None)
        ended = x["outcome"] or ("**running**" if x is r["live_round"] and up else "no end line" + (", unit not running" if x is r["live_round"] else ""))
        rows.append("| %d | %s | %s | %s | %s | %s | %s | %s |" % (
            x["n"], cell(clock(x["start"]) if x["start"] else "-"), cell(took), cell(item_title(x["item"], x["truth"])),
            cell(ended), cell(x["truth"]["word"] if x["item"] else "-"), cell("`%s`" % x["sha"] if x["sha"] else "-"),
            cell(toks(x["tokens"]) if x["tokens"] is not None else "-")))
    return rows


def demote(text, by=3):
    """Headings inside a quoted file sit under the worker's section."""
    return re.sub(r"(?m)^(#{1,6})\s", lambda m: "#" * min(6, len(m[1]) + by) + " ", text)


def worker_section(r):
    info = r["info"]
    L = ["## %s: %s" % (r["name"], r["state_word"].upper()), ""]
    L.append("- **Machine and game:** %s, %s%s." % (info.get("machine") or "machine UNMEASURED", lane_word(info),
                                                   ", game %s" % info["game"] if info.get("game") else ""))
    L.append("- **Unit:** %s." % unit_text(r))
    if r["item"]:
        t = r["item_truth"]
        L.append("- **Now on:** %s." % item_title(r["item"], t))
        L.append("  - Ledger: %s%s." % (t["word"], "; %d runs on record, the last %d not a pass" % (t["runs"], t["nonpass"]) if t.get("runs") else ""))
        bits = []
        if r["item_since"]:
            bits.append("on it %s, since %s" % (A.hm(now_s() - r["item_since"]), clock(r["item_since"])))
        if r["rounds_on_item"]:
            bits.append("round %d of it" % r["rounds_on_item"] if r["rounds_on_item"] > 1 else "its first round on it")
        if bits:
            L.append("  - " + "; ".join(bits) + ".")
    else:
        L.append("- **Now on:** no item%s." % (" (worker.json unread)" if any("worker.json" in w for w in r["why"]) else ""))
    if r["round_no"] is not None:
        L.append("- **Round:** %s%s." % (r["round_no"], ", running since %s" % clock(r["live_round"]["start"]) if r["live_round"] and r["live_round"]["start"] else ""))
    if info.get("note"):
        L.append("- **Its note:** %s" % short(info["note"], 400))
    c = r["counts"]
    if c:
        L.append("- **Rounds ended:** %s." % ", ".join("%d %s" % (v, k) for k, v in sorted(c.items(), key=lambda kv: -kv[1])))
    L.append("- **Closed today:** %d said by the worker, %d closed in the ledger." % (len(r["closed_today"]), len(r["accepted_today"])))
    L.append("- **Tokens:** %s." % ("~%s today, ~%s on record" % (toks(r["tokens_today"]), toks(r["tokens_all"])) if r["tokens_seen"] else "not logged in loop.log"))
    ages = ", ".join("%s %s" % (f, "%s ago" % ago(now_s() - t) if t else "missing") for f, t in r["files"].items())
    L.append("- **Files:** %s. Folder `%s\\%s`." % (ages, NATIVE_ROOT, r["name"]))
    if r["why"]:
        L.append("- **Could not read:** %s." % "; ".join(r["why"]))
    if r["odd"]:
        L.append("- loop.log has %d line%s with no time stamp, not read." % (r["odd"], "" if r["odd"] == 1 else "s"))
    L.append("")
    if r["questions_list"]:
        L += ["### Questions for you", "", "From OWNER_QUESTIONS.md, written %s ago, in full:" % ago(now_s() - r["files"]["OWNER_QUESTIONS.md"]), ""]
        L += [demote(r["questions"].strip()), ""]
    if r["rounds_sorted"]:
        L += ["### Recent rounds", ""] + round_rows(r) + [""]
        if len(r["rounds_sorted"]) > ROUNDS_SHOWN:
            L += ["%d earlier rounds not shown." % (len(r["rounds_sorted"]) - ROUNDS_SHOWN), ""]
    other = [(t, s) for t, s in r["other"] if s][-8:]
    if other:
        L += ["### Other lines in its log", ""] + ["- %s: %s" % (clock(t) if t else "-", short(s, 200)) for t, s in other[::-1]] + [""]
    if r.get("progress"):
        lines = r["progress"].rstrip().splitlines()
        tail = lines[-30:]
        L += ["### Its progress file", "", "progress.md, written %s ago%s:" % (
            ago(now_s() - r["files"]["progress.md"]), ", last 30 of %d lines" % len(lines) if len(lines) > 30 else ""), ""]
        L += ["> " + l if l.strip() else ">" for l in demote("\n".join(tail)).splitlines()] + [""]
    return L


def headline(recs, lane, needs, ledger_ok):
    if not recs:
        s = "No Whittle workers yet: no roster and no worker folder under %s." % NATIVE_ROOT
    else:
        states = {}
        for r in recs:
            k = r["state_word"].split(" (")[0]
            states[k] = states.get(k, 0) + 1
        s = "%d worker%s: %s." % (len(recs), "" if len(recs) == 1 else "s",
                                   ", ".join("%d %s" % (v, k) for k, v in sorted(states.items(), key=lambda kv: -kv[1])))
        said = sum(len(r["closed_today"]) for r in recs)
        acc = sum(len(r["accepted_today"]) for r in recs)
        if not ledger_ok:
            s += " Closed today: %d said, ledger UNMEASURED." % said
        elif said == acc:
            s += " Closed today: %d, all in the ledger." % acc if said else " Closed today: none yet."
        else:
            s += " Closed today: %d said, %d in the ledger." % (said, acc)
        if any(r["tokens_seen"] for r in recs):
            s += " Tokens today: ~%s." % toks(sum(r["tokens_today"] for r in recs))
    s += " FlowWorks lane: %s open." % (lane["open"] if isinstance(lane, dict) else "UNMEASURED")
    s += " Needs you: %d." % len(needs)
    return "**%s**" % s


def build(stubs=None):
    """-> (page, phone, state). `stubs` replaces readers in the selftest: units, ledger, machines, accounts."""
    stubs = stubs or {}
    sources = A.Sources()
    state = {}
    try:
        with open(os.path.join(OUT_DIR, "whittle_now_state.json"), encoding="utf-8") as f:
            state = json.load(f) or {}
    except (OSError, ValueError):
        state = {}
    machines = {}

    def machine_work():
        try:
            machines.update((stubs.get("machines") or A.read_machines)(state, sources))
        except Exception as e:  # a reader bug must not take the page down
            machines["_why"] = short(e, 100)

    th = threading.Thread(target=machine_work, daemon=True)
    th.start()
    recs, roster_why = discover(ROOT, sources)
    (stubs.get("units") or read_units)(recs, sources)
    try:
        ledger = (stubs.get("ledger") or load_ledger)(sources)
    except Unmeasured as e:
        ledger, ledger_why = None, str(e)
    else:
        ledger_why = None
    for r in recs:
        assess(r, ledger)
    try:
        lane = lane_count(ledger, sources)
    except Unmeasured as e:
        lane = str(e)
    try:
        accounts = (stubs.get("accounts") or A.read_accounts)(sources)
    except (Unmeasured, OSError, ValueError) as e:
        accounts = str(e)
    notice = (stubs.get("notice") or read_notice)(sources)
    bridges = bridge_lines(ledger)
    th.join(max(0.1, A.MACHINE_DEADLINE_S + 1))

    needs = []
    for r in recs:
        needs += needs_for(r)
    if ledger_why:
        needs.append((2, "**The ledger could not be read**, so nothing on this page is known to be accepted: %s." % ledger_why))
    needs = [t for _, t in sorted(needs, key=lambda x: x[0])]

    head = headline(recs, lane, needs, ledger is not None)
    P = ["# Whittle now", "", picture(recs), "", head, "",
         "Generated %s by `whittle_now.py`, no model called. Written every minute: over 3 minutes old means the timer is dead." % (
             dt.datetime.fromtimestamp(now_s()).astimezone().strftime("%b %-d, %H:%M:%S %Z")), ""]
    P += ["## Needs you", ""]
    P += ["%d. %s" % (i + 1, t) for i, t in enumerate(needs)] if needs else ["Nothing needs you now."]
    P += [""]
    P += ["## Workers at a glance", ""]
    if recs:
        P += glance(recs)
        P += ["", "\"Closed\" is the worker's word; \"in ledger\" means rimflow closed it, which is the only acceptance."]
    else:
        P += ["No workers yet. The page looks for `%s\\workers.json` and for worker folders holding worker.json or loop.log%s." % (
            NATIVE_ROOT, " (roster: %s)" % roster_why if roster_why else "")]
    P += [""]

    P += ["## FlowWorks lane", ""]
    if isinstance(lane, dict):
        order = ("proposed", "ready", "doing", "built", "validated")
        parts = ", ".join("%d %s" % (lane["by_state"][k], k) for k in sorted(lane["by_state"], key=lambda k: order.index(k) if k in order else 9))
        P += ["- **Open in the ledger: %d** FlowWorks and GSS items%s." % (lane["open"], " (%s)" % parts if parts else ""),
              "- Of them, %d %s you live (marked needs owner)." % (lane["needs_owner"], "needs" if lane["needs_owner"] == 1 else "need"),
              "- Closed in the ledger today, by any seat: %d." % lane["closed_today"]]
    else:
        P += ["- UNMEASURED: %s." % lane]
    P += [""]

    P += ["## Closed today", ""]
    closed = sorted(((x["end"], r["name"], x) for r in recs for x in r["closed_today"]), key=lambda z: z[0], reverse=True)
    if closed:
        P += ["| Time | Worker | Item | Ledger now | Commit |", "|---|---|---|---|---|"]
        for t, name, x in closed:
            P.append("| %s | %s | %s | %s | %s |" % (cell(clock(t)), cell(name), cell(item_title(x["item"], x["truth"])),
                                                    cell(x["truth"]["word"]), cell("`%s`" % x["sha"] if x["sha"] else "-")))
    else:
        P += ["No worker has logged a closed round today."]
    P += [""]

    P += ["## Games and machines", ""]
    on_machine = {}
    for r in recs:
        if str(r["info"].get("lane", "")).lower() == "fwlive" and r["info"].get("machine"):
            on_machine.setdefault(str(r["info"]["machine"]).lower(), []).append(r["name"])
    for name in ("Archmagi", "SteveDesktop"):
        P += ["### %s" % name, ""]
        who = on_machine.get(name.lower())
        P.append("- Live Whittle worker on this game: %s." % (", ".join(who) if who else "none"))
        m = machines.get(name)
        if m:
            P += ["- %s" % l for l in A.machine_lines(name, m)]
        else:
            P.append("- Machine read: UNMEASURED (%s)." % machines.get("_why", "no answer in time"))
        b = bridges.get(name.lower())
        P.append("- Bridge, by the ledger: %s." % (b or "UNMEASURED"))
        for host in sorted(h for h in bridges if h.startswith(name.lower() + ".")):
            P.append("- Its second bridge (%s), by the ledger: %s." % (host, bridges[host]))
        P.append("")

    P += ["## Accounts", ""]
    if isinstance(accounts, list):
        sysrow = next((a for a in accounts if a["name"].lower().startswith("system")), None)
        if sysrow:
            P.append("- **Claude System account: %s of its week used**, resets in %s (read %s ago)." % (
                "%d%%" % round(sysrow["used"]) if sysrow["used"] is not None else "UNMEASURED",
                ago(sysrow["resets"] - now_s()) if sysrow["resets"] else "UNMEASURED", ago(now_s() - sysrow["t"]) if sysrow["t"] else "UNMEASURED"))
        others = [a for a in accounts if a is not sysrow]
        if others:
            P.append("- Others: %s." % ", ".join("%s %s used" % (a["name"], "%d%%" % round(a["used"]) if a["used"] is not None else "UNMEASURED") for a in others))
    else:
        P.append("- Account readings UNMEASURED: %s." % accounts)
    if notice:
        P.append("- Account switcher: on **%s**, %s left (it switches below %s%%)%s." % (
            notice.get("account", "UNMEASURED"), "%d%%" % round(notice["pct_left"]) if isinstance(notice.get("pct_left"), (int, float)) else "UNMEASURED",
            notice.get("line", "?"), "; says: %s" % short(notice["message"], 160) if notice.get("message") else ""))
    P.append("")

    for r in recs:
        P += worker_section(r)

    P += ["## Sources", "", "| Source | Age | Problem |", "|---|---|---|"]
    for n, age, why in sources.rows:
        P.append("| %s | %s | %s |" % (cell(n), cell(ago(age) if age is not None else "-"), cell(why or "")))
    P += ["", "Written to `%s\\WHITTLE_NOW.md` by rm-whittle-now.timer from the dispatch clone." % NATIVE_OUT, ""]
    page = "\n".join(P)
    phone = phone_page(head, recs, needs, lane, machines)
    return page, phone, state


def phone_page(head, recs, needs, lane, machines):
    L = ["Whittle %s" % dt.datetime.fromtimestamp(now_s()).astimezone().strftime("%H:%M %Z"), head.strip("*"), ""]
    if needs:
        L.append("NEEDS YOU %d" % len(needs))
        L += ["- " + short(re.sub(r"\*\*|`", "", n), 150) for n in needs[:8]]
        L.append("")
    L.append("WORKERS")
    if not recs:
        L.append("none yet")
    for r in recs:
        item = r["item"] or "no item"
        L.append("%s: %s, %s, %s" % (r["name"], r["state_word"], r["info"].get("machine") or "?", item))
        L.append("  closed today %d (ledger %d)%s" % (len(r["closed_today"]), len(r["accepted_today"]),
                                                       ", on item %s" % A.hm(now_s() - r["item_since"]) if r["item"] and r["item_since"] else ""))
    L += ["", "LANE", "FlowWorks open: %s" % (lane["open"] if isinstance(lane, dict) else "UNMEASURED"), "", "GAMES"]
    for name in ("Archmagi", "SteveDesktop"):
        m = machines.get(name)
        d = m and m.get("data")
        if not m or (not m.get("fresh") and not d):
            L.append("%s: UNMEASURED" % name)
        else:
            g = d.get("game")
            L.append("%s: %s%s" % (name, "game up" if g else "game down" if g is False else "game UNMEASURED", "" if m.get("fresh") else " (old reading)"))
    return "\n".join(L) + "\n"


def check():
    path = os.path.join(OUT_DIR, "WHITTLE_NOW.md")
    m = mtime(path)
    if m is None:
        print("WHITTLE_NOW.md: UNMEASURED (missing)")
        return 1
    age = now_s() - m
    print("WHITTLE_NOW.md is %s old%s" % (ago(age), "" if age <= STALE_PAGE_S else " - STALE (limit 3 min)"))
    return 0 if age <= STALE_PAGE_S else 1


def main():
    if "--check" in sys.argv:
        return check()
    page, phone, state = build()
    if "--print" in sys.argv:
        print(page)
        return 0
    if "--phone" in sys.argv:
        print(phone)
        return 0
    os.makedirs(OUT_DIR, exist_ok=True)
    write_atomic(os.path.join(OUT_DIR, "whittle_now_state.json"), json.dumps(state))
    write_atomic(os.path.join(OUT_DIR, "WHITTLE_NOW.md"), page)
    write_atomic(os.path.join(OUT_DIR, "WHITTLE_NOW_PHONE.md"), phone)
    return 0


if __name__ == "__main__":
    sys.exit(main())
