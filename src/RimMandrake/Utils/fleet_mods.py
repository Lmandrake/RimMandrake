#!/usr/bin/env python3
"""fleet_mods.py — the slow half of RUNNING_NOW (running_now.py): receipts, mods worked on lately, the factory line.

FLEETWATCH_PAGE_SHRINK_LESS_BASH_MORE_MODS (owner, by card 2026-11-02): "there should be a lower section that has a
list of all Mods worked on in the past week or so and where they stand. What was done? Each task that contributed to
that mod (one line)." Everything here is computed in Python so the page stays dumb; running_now.py renders it.
(The Fleet Watch board that first carried it was retired by the owner, 2026-11-04: FLEETWATCH_CODE_RETIRE_NOBODY_WAS_WATCHING.)

  receipts(...)  one row per item finished today (local day): ✓/✗, the blind check's verdict, one plain sentence of
                 what changed (its main commit's subject), real commit count (ledger-only commits excluded), tokens.
  mods(...)      one doc per mod touched in the last 7 days, grouped by the paths the commits changed under src/
                 (src/<Tier>/<Mod>/...; tooling folders and paths outside src/ -> "Infrastructure & tooling"):
                 closed/open/parked counts, proof state (modcheck record and the last blind check), what is next and
                 what waits on the owner or the game, one line per contributing task.
  factory(...)   the header line: factory ok or not, N/target workers, tokens today.
  detached_done(hours)  finished detached dispatcher helpers (dispatcher/detached/*.json), the receipts' second source.

Inputs (read-only): `git log origin/main --since=7.days --name-only` (one call), the rimflow ledger (model.read),
the Relentless store (~/rm/relentless/store), infrastructure/state/modcheck_status.json, src/*/*/About/About.xml.

    python3 src/RimMandrake/Utils/fleet_mods.py [--days 7]      # prints {"factory":…, "receipts":[…], "mods":[…]}
"""
import argparse
import calendar
import glob
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import owner_queue  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
DETACHED = "/mnt/d/ClaudeWork/rimmandrake/dispatcher/detached"
SH_TIMEOUT = 120


def sh(*a, cwd=REPO):
    try:
        return subprocess.run(a, cwd=cwd, capture_output=True, text=True, timeout=SH_TIMEOUT).stdout.strip()
    except subprocess.TimeoutExpired:
        return ""


def short(s, n=160):
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[: n - 1] + "…"


UPPER_ID = re.compile(r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b")
PATHLIKE = re.compile(r"(?:[\w.~-]*/)+([\w.-]+)")


def de_id(text):
    """UPPER_SNAKE ids -> 'Upper snake' words; paths -> their basename."""
    text = PATHLIKE.sub(lambda m: m.group(1), text)
    return UPPER_ID.sub(lambda m: re.sub(r"_\d+$", "", m.group(0)).replace("_", " ").capitalize(), text)


GENERIC_HEADS = {"experiment", "question", "investigate", "investigation", "research", "follow-up", "followup",
                 "proposal", "decision", "cleanup", "regression", "feature", "finding", "harness"}


def title_short(title, n=28, min_words=1):
    """A rimflow title -> at most n readable chars: the head before the first ':', ' — ', '(' or ';' when that head is
    a phrase of its own (at least `min_words` words; 'Full list' says nothing, so the page asks for 3), ids made words,
    cut at a word with '…'."""
    t = " ".join(str(title or "").split())
    t = re.sub(r"^(?:\[[A-Za-z -]{2,12}\]\s*)+", "", t)
    t = re.sub(r"^(?:Ops alarm|alarm|FINDING|finding|BUG|bug|MOD|SITE|HARNESS)(?:\s*:\s*|\s+)", "", t)
    if re.fullmatch(r"[a-z][a-z0-9]*(?:_[a-z0-9]+)+", t):  # a bare snake_case name: make it words
        t = t.replace("_", " ").capitalize()
    parts = re.split(r"\s*(?::\s|\s[—–-]{1,2}\s|\(|;)\s*", t, maxsplit=1)
    if len(parts) == 2 and parts[0].lower() in GENERIC_HEADS:  # "Experiment: can we ..." -> "Can we ..."
        t = parts[1][:1].upper() + parts[1][1:]
        parts = re.split(r"\s*(?::\s|\s[—–-]{1,2}\s|\(|;)\s*", t, maxsplit=1)
    head = parts[0]
    if len(head) >= 8 and (" " in head or len(parts) == 1) and (len(parts) == 1 or len(head.split()) >= min_words):  # a lone path/token head says nothing: keep the rest
        t = head
    t = de_id(t).strip(" .,:;-")
    if len(t) <= n:
        return t
    cut = t[: n - 1]
    if t[n - 1] != " " and " " in cut[n // 2:]:
        cut = cut[: cut.rindex(" ")]
    return cut.rstrip(" ,.:;-") + "…"


LEDGER_ONLY = re.compile(r"^(?:infrastructure/state/ledger/|conversations/|infrastructure/state/code_review/)")


def real_count(log_text):
    """`git log --format=@@%h --name-only` text -> commits that changed something besides the ledger and its echoes."""
    n, files = 0, None
    for line in log_text.splitlines() + ["@@end"]:
        if line.startswith("@@"):
            if files is not None and any(not LEDGER_ONLY.match(f) for f in files):
                n += 1
            files = []
        elif line.strip() and files is not None:
            files.append(line.strip())
    return n


def detached_tokens(out_path):
    """A finished detached helper's `claude -p --output-format json` result -> total tokens, or None (UNMEASURED)."""
    try:
        with open(out_path) as f:
            u = (json.load(f) or {}).get("usage") or {}
    except (OSError, ValueError, TypeError, AttributeError):
        return None
    n = sum(int(u.get(k) or 0) for k in ("input_tokens", "output_tokens", "cache_creation_input_tokens",
                                          "cache_read_input_tokens"))
    return n or None


def detached_done(hours, now=None, root=DETACHED, unit_state=None, item_state=None, commits=None):
    """Detached dispatcher helpers started within `hours` whose unit is no longer running -> receipt rows
    {item, status Done|Ended|Stopped, started, finished_at, commit_count, tokens}. The three readers are injectable
    so the selftest runs offline."""
    now = time.time() if now is None else now
    unit_state = unit_state or (lambda u: sh("systemctl", "--user", "is-active", u) or "unknown")
    item_state = item_state or _item_state
    commits = commits or (lambda item, since: real_count(sh("git", "log", "origin/main", "--since=@%d" % int(since),
                                                            "--format=@@%h", "--name-only", "-F", "--grep=" + item)))
    out = []
    for p in sorted(glob.glob(os.path.join(root, "*.json"))):
        if p.endswith(".out.json"):
            continue
        try:
            with open(p) as f:
                r = json.load(f)
        except (OSError, ValueError):
            continue
        if not isinstance(r, dict) or not r.get("item") or now - r.get("at", 0) > hours * 3600:
            continue
        if unit_state(r.get("unit", "")) in ("active", "activating"):
            continue  # still building: not a receipt yet
        cs = commits(r["item"], r["at"])
        st = item_state(r["item"])
        status = "Done" if st in ("closed", "done", "implemented", "validated") else ("Ended" if cs else "Stopped")
        try:
            fin = int(os.path.getmtime(r["out"]))
        except (OSError, KeyError, TypeError):
            fin = int(r["at"])
        out.append({"item": r["item"], "status": status, "started": int(r["at"]), "finished_at": fin,
                    "commit_count": cs, "tokens": detached_tokens(r.get("out"))})
    return out


def _item_state(item):
    out = sh("python3", "src/RimMandrake/rimflow/cli.py", "show", item)
    first = out.splitlines()[0] if out else ""
    m = re.match(r"\S+\s+(\S+)", first)
    return m.group(1) if m else "unknown"
STORE = os.path.expanduser("~/rm/relentless/store")
MODCHECK = os.path.join(REPO, "infrastructure", "state", "modcheck_status.json")
DAYS = 7
INFRA = "_infra"
INFRA_NAME = "Infrastructure & tooling"
# folders under src/<Tier>/ that are tooling, not a mod the player loads
TOOLING = {"Utils", "rimflow", "_Shared", "arena", "bridgetools", "contracts", "mapsynth", "art_bench", "ideoligion"}
MARKS = re.compile(r"^(?:review marks?|clean marks?|mark\b|marks\b|lesson\b|ledger\b|rebase\b)", re.I)
CLOSED_STATES = ("done",)


# ---------------------------------------------------------------- pure helpers (selftest_fleet_mods.py) ----------
def parse_log(text):
    """`git log --format=@@%H%x09%ct%x09%s --name-only` -> [{sha, at, subject, files}] newest first."""
    out, cur = [], None
    for line in text.splitlines():
        if line.startswith("@@"):
            parts = line[2:].split("\t", 2)
            if len(parts) < 3:
                cur = None
                continue
            cur = {"sha": parts[0], "at": int(parts[1] or 0), "subject": parts[2], "files": []}
            out.append(cur)
        elif line.strip() and cur is not None:
            cur["files"].append(line.strip())
    return out


def real_files(files):
    return [f for f in files if not LEDGER_ONLY.match(f)]


def mod_of_path(path, mods):
    """'src/RimMandrake/Stillsand/Defs/x.xml' -> 'Stillsand' when Stillsand is a mod folder; design/<Tier>/<Mod>/... too.
    Anything else -> None (infrastructure)."""
    p = path.split("/")
    if len(p) >= 4 and p[0] in ("src", "design") and p[2] in mods:
        return p[2]
    return None


def item_ids(subject, known):
    """Item ids named in a commit subject that the ledger knows."""
    return [t for t in dict.fromkeys(re.findall(r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b", subject)) if t in known]


def mod_by_name(item, mods_upper):
    """An item id whose leading segments spell a mod folder (LEANINGSCRUB_STALL_1 -> LeaningScrub; longest wins)."""
    segs = item.split("_")
    best = None
    for k in range(1, len(segs)):
        name = "".join(segs[:k])
        if name in mods_upper:
            best = mods_upper[name]
    return best


def plain_subject(subject):
    """'ITEM_X: exact-step speed proof + engine-law test' -> 'Exact-step speed proof + engine-law test.'"""
    s = re.sub(r"^(?:[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+[,:]?\s*)+", "", subject).strip()
    s = re.sub(r"\b[0-9a-f]{7,40}\b", "", s)
    s = s.lstrip("+-*· ").strip()
    s = de_id(" ".join(s.split())).strip(" ;,")
    if not s:
        return ""
    s = s[0].upper() + s[1:]
    s = short(s, 120)
    return s if s.endswith(("…", ".", "!", "?", ")")) else s + "."


def outcome(commits_of_item):
    """The item's main commit (most real files, not a review/lesson mark) as one plain sentence; "" if none."""
    best = None
    for c in commits_of_item:
        n = len(real_files(c["files"]))
        if not n or MARKS.match(re.sub(r"^[A-Z0-9_]+[:,]\s*", "", c["subject"])):
            continue
        if best is None or n > best[0]:
            best = (n, c)
    return plain_subject(best[1]["subject"]) if best else ""


def day_label(at, now=None):
    """'1 Nov'; '' for no date or for today (the owner reads today as the default)."""
    if not at or (now is not None and at >= local_midnight(now)):
        return ""
    return time.strftime("%-d %b", time.localtime(at))


def local_midnight(now):
    t = time.localtime(now)
    return int(time.mktime((t.tm_year, t.tm_mon, t.tm_mday, 0, 0, 0, 0, 0, -1)))


# ---------------------------------------------------------------- inputs --------------------------------------------
def mod_folders():
    """{folder: display name} for every src/<Tier>/<Mod>/ that is not tooling; a display name two folders share gets
    its tier added."""
    out, tier = {}, {}
    for d in sorted(glob.glob(os.path.join(REPO, "src", "*", "*", ""))):
        name = os.path.basename(d.rstrip("/"))
        if name in TOOLING or name.startswith(".") or not os.path.isdir(d):
            continue
        disp = name
        try:
            with open(os.path.join(d, "About", "About.xml"), encoding="utf-8", errors="replace") as f:
                m = re.search(r"<name>([^<]+)</name>", f.read())
            if m:
                disp = re.sub(r"^(?:RimMandrake|RimUtinni|RimStarWars|Jawa)\s*:\s*", "", m.group(1).strip())
        except OSError:
            if not glob.glob(os.path.join(d, "*")):
                continue
        out[name] = disp[:1].upper() + disp[1:]
        tier[name] = os.path.basename(os.path.dirname(d.rstrip("/")))
    seen = {}
    for k, v in out.items():
        seen.setdefault(v, []).append(k)
    for v, ks in seen.items():
        if len(ks) > 1:
            for k in ks:
                out[k] = "%s (%s)" % (v, tier[k])
    return out


def git_log(days):
    return sh("git", "log", "origin/main", "--since=%d.days" % days, "--format=@@%H%x09%ct%x09%s", "--name-only")


def ledger():
    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))
    import model  # noqa: E402
    evs = model.read()
    return evs, model.replay(evs)


def relentless_states(strict=False):
    """Every item's state. strict: an item whose state cannot be read raises (a short list would drop its hold and its
    receipt, and read as true); otherwise it is skipped."""
    out = {}
    root = os.path.join(STORE, "items")
    for name in os.listdir(root) if strict else (os.path.basename(os.path.dirname(p)) for p in glob.glob(os.path.join(root, "*", "state.json"))):
        p = os.path.join(root, name, "state.json")
        try:
            with open(p) as f:
                s = json.load(f)
        except FileNotFoundError:
            if strict and os.path.isdir(os.path.join(root, name)):
                raise
            continue
        except (OSError, ValueError):
            if strict:
                raise
            continue
        out[s.get("item") or name] = s
    return out


def load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def close_at(item, evs):
    """Epoch of the item's last close event, or None."""
    for i in reversed(item.history or []):
        e = evs[i] if 0 <= i < len(evs) else {}
        if e.get("event") == "close":
            return _epoch(e.get("ts"))
    return None


def _epoch(ts):
    try:
        return int(calendar.timegm(time.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")))
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------- derivations ---------------------------------------
def verdict_of(rs):
    c = (rs or {}).get("check")
    return c.get("verdict") if isinstance(c, dict) else None


def ledger_verdict(it):
    """The last blind-check run the ledger records for an item: 'PASS' / 'FAIL' / None."""
    runs = [x for x in (getattr(it, "runs", None) or []) if "blind-check" in str(getattr(x, "config", ""))]
    return {"pass": "PASS", "fail": "FAIL"}.get(str(getattr(runs[-1], "result", "")).lower()) if runs else None


def check_of(item, it, rel):
    """An item's blind-check verdict from the Relentless store, else the ledger; None = never checked."""
    return verdict_of(rel.get(item)) or (ledger_verdict(it) if it is not None else None)


# ✓ only for a finish a blind check PASSED; a finish nobody checked gets ● (owner review 2026-11-02, point 10)
FINISH_MARK = {"PASS": ("✓", "pass"), "FAIL": ("✗", "fail")}
UNCHECKED = ("●", "done")


def finish_mark(verdict, ok=True):
    if not ok:
        return ("✗", "fail")
    return FINISH_MARK.get(verdict, UNCHECKED)


def receipts(now, commits_by_item, rel, world, evs, detached_done=()):
    """Rows (status Done/Ended) for items finished since local midnight: Relentless done_at today, plus finished
    detached helper rows passed in. Each carries a `receipt` the page renders without thinking."""
    since = local_midnight(now)
    out = {}
    for item, s in rel.items():
        if s.get("status") != "done" or (s.get("done_at") or 0) < since:
            continue
        v = verdict_of(s)
        out[item] = {"item": item, "status": "Done", "glyph": finish_mark(v)[0],
                     "finished_at": int(s["done_at"]), "started": int(s.get("enrolled_at") or s["done_at"]),
                     "relentless": True,
                     "receipt": {"ok": v != "FAIL", "check": v,
                                 "outcome": outcome(commits_by_item.get(item, [])),
                                 "commits": sum(1 for c in commits_by_item.get(item, []) if real_files(c["files"])),
                                 "tokens": s.get("spent") or None}}
    for r in detached_done:
        if (r.get("finished_at") or 0) < since or (r["item"] in out and out[r["item"]]["started"] >= r.get("started", 0)):
            continue  # the newest run (by start, the newest start wins) speaks
        it = world.items.get(r["item"])
        v = ledger_verdict(it)
        ok = r["status"] == "Done" and v != "FAIL"
        out[r["item"]] = dict(r, glyph=finish_mark(v, ok)[0], receipt={
            "ok": ok, "check": v, "outcome": outcome(commits_by_item.get(r["item"], [])),
            "commits": r.get("commit_count") or 0, "tokens": r.get("tokens")})
    return sorted(out.values(), key=lambda r: -r["finished_at"])


def attribute(log, known, mods):
    """-> (by_item {item: [commit]}, item_mods {item: set(mod or INFRA)}, mod_last {mod: epoch}, item_last)"""
    by_item, item_mods, mod_last, item_last = {}, {}, {}, {}
    for c in log:
        files = real_files(c["files"])
        if not files:
            continue
        touched = {mod_of_path(f, mods) or INFRA for f in files}
        for m in touched:
            mod_last[m] = max(mod_last.get(m, 0), c["at"])
        for i in item_ids(c["subject"], known):
            by_item.setdefault(i, []).append(c)
            item_mods.setdefault(i, set()).update(touched)
            item_last[i] = max(item_last.get(i, 0), c["at"])
    for i, ms in item_mods.items():  # an item that touched a mod is that mod's, not also infra's
        if len(ms) > 1:
            ms.discard(INFRA)
    return by_item, item_mods, mod_last, item_last


PARKED_REL = ("held", "blocked", "retired")
NEXT_REL = ("running", "candidate", "game", "queued")
CROSS = "_cross"
CROSS_NAME = "Cross-mod work"
CROSS_MIN = 3  # an item whose commits touched this many mods is shown once, in the cross-mod block, counted for none
TASKS_KEPT = 30  # the page shows 5 and "and N more" (a tap shows the rest of these)
TITLE_MAX = 160  # a sanity bound, not a visual cut: the page ellipsizes by the width it has


def task_mark(it, rs, verdict=None):
    """-> (glyph, kind). Finished: ✓ PASS / ✗ FAIL / ● unchecked; open: ⏸ parked / ○ open."""
    if it is not None and it.state in CLOSED_STATES:
        return finish_mark(verdict)
    if parked(it, rs):
        return ("⏸", "park")
    return ("○", "open")


def parked(it, rs):
    return bool(it is not None and (getattr(it, "held", False) or getattr(it, "blocked", False))) or \
        (rs or {}).get("status") in PARKED_REL


def waits_on(it, rs, evs=None):
    """'you' / 'the game' / '' for an open item."""
    if it is None:
        return ""
    if owner_queue.is_his(it, rs, evs):  # the same test as the board's Needs you (FLEETWATCH_NEEDS_FIX_NOTHING_WHILE_MODS_WAIT)
        return "you"
    if (rs or {}).get("status") == "game" or getattr(it, "blocked_kind", None) == "live":
        return "the game"
    return ""


HOLD_PLANS = {   # a Relentless tooling hold -> (who it waits on, what is planned); owner card 2026-11-03: every stuck line
    # "says what is planned to unstick it and who it waits on"
    "proof_weak": ("the Conductor", "its proof kept reading weak; the Conductor rewrites the proof so a blind checker "
                                    "can rerun it, or drops the item"),
    "strikes": ("the Conductor", "workers failed it several times running; the Conductor re-scopes or drops it"),
    "game": ("the game", "it runs in the next live game round (the game takes one test at a time)"),
}


def first_sentence(text, cap=160):
    """The first sentence of a free-text block reason, cut at a word, never mid-word."""
    t = " ".join(str(text).split())
    m = re.match(r"(.+?[.;!?])(\s|$)", t)
    t = (m.group(1) if m else t).rstrip(".;: ")
    return t if len(t) <= cap else t[:cap].rsplit(" ", 1)[0] + " …"


SNAG_PREFIX = re.compile(r"^\s*(?:relentless\s+)?snag\s+[a-z_]+\s*:\s*", re.I)
ITEM_ID = re.compile(r"\b[A-Z][A-Z0-9]+(?:_[A-Z0-9]+){2,}\b")
SLUG = re.compile(r"\b[a-z]+(?:_[a-z]+)+\b(?![.(/])")


def plain_reason(text, known=None):
    """A free-text block reason without machine words: no 'snag <class>:' prefix, an item id becomes its title (or
    'another item'), a snake_case slug becomes words. A file name (foo_bar.py) or a call (foo_bar()) is left alone."""
    t = SNAG_PREFIX.sub("", text or "")
    t = ITEM_ID.sub(lambda m: "'%s'" % display_title(known[m.group(0)].title or m.group(0)) if known and
                    m.group(0) in known else "another item", t)
    return SLUG.sub(lambda m: m.group(0).replace("_", " "), t)


def block_who(reason):
    """Who a free-text block reason waits on. Never 'you': only owner_queue.is_his says that (Needs you must match)."""
    r = reason.lower()
    if re.search(r"\b(live|quicktest|in[- ]game|game[- ]up|cold load)\b", r):
        return "the game"
    if re.search(r"\b(owner|card|ruling|deferred|parked)\b", r):
        return "a past ruling of yours (parked on purpose, no question open)"
    if re.search(r"\b(art|render|sprite|texture)s?\b", r):
        return "art"
    return "the Conductor"


def stuck_of(it, rs, evs=None, known=None, asks=None):
    """-> {"waits": who, "plan": what happens next} for an open item that is not moving, or None when it is moving.
    'you' comes only from owner_queue.is_his, the same test as Needs you, so the page's count and its tags agree."""
    if it is None or not it.open:
        return None
    rs = rs or {}
    status = rs.get("status")
    if owner_queue.is_his(it, rs, evs):
        return {"waits": "you", "plan": "the Conductor brings you a question card (it is in Needs you)"}
    if owner_queue.routed(it) and not owner_queue.answered(it, evs) and owner_queue.tooling_hold(rs) is None \
            and owner_queue.awaiting_designer(it):
        return {"waits": "the Designer", "plan": "its first-touch pass comes first; it joins Needs you when there is a "
                                                 "result or a turn to certify"}
    h = owner_queue.tooling_hold(rs)
    if h is not None:
        who, plan = HOLD_PLANS.get(h.get("kind"), ("the Conductor", "the Conductor reads why Relentless stopped and "
                                                                    "decides the next step"))
        return {"waits": who, "plan": plan}
    if getattr(it, "blocked", False):
        kind, on = getattr(it, "blocked_kind", None), getattr(it, "blocked_on", None)
        if on and known and on in known:
            return {"waits": "another item", "plan": "starts again by itself once '%s' is done"
                    % display_title(known[on].title or on)}
        if kind == "live":
            return {"waits": "the game", "plan": "it runs in the next live game round (the game takes one test at a time)"}
        if kind == "judge":
            return {"waits": "a judge agent", "plan": "a fresh agent that did not make it rules on it, then work resumes"}
        if kind == "time":
            until = getattr(it, "blocked_until", None)
            return {"waits": "time", "plan": "resumes by itself" + (" after %s" % str(until)[:10] if until else
                                                                     " when its wait is over")}
        if owner_queue.answered(it, evs):
            return {"waits": "the Conductor", "plan": "you answered it; the Conductor carries out your answer and lifts "
                                                      "the block"}
        reason = plain_reason(first_sentence(getattr(it, "blocked_reason", None) or ""), known)
        return {"waits": block_who(reason) if kind != "external" else "something outside the project",
                "plan": ("resumes when this clears: " + reason) if reason else
                "resumes when its blocker clears; none is named, so the Conductor names one"}
    if getattr(it, "held", False):
        return {"waits": "a fix", "plan": "a blind check failed it; the next worker fixes what failed and it is checked again"}
    if status == "game":
        return {"waits": "the game", "plan": "it runs in the next live game round (the game takes one test at a time)"}
    if status == "retired":
        return {"waits": "the Conductor", "plan": "Relentless stopped trying; the Conductor rewrites or drops it"}
    if status == "blocked":
        return {"waits": "another item", "plan": "starts again by itself once the item it waits on is done"}
    if status == "held":        # his kind of hold not yet on the ledger: never 'you' until is_his says so
        return {"waits": "Relentless", "plan": "it is being handed to you; it joins Needs you once the hand-over is "
                                               "on record"}
    return None


def proof_line(mod, mc, blind, now, days):
    """'Blind check PASS 2 Nov · modcheck not run in 7 days' — both instruments, each with its date."""
    parts = []
    if blind:
        parts.append(("blind check %s %s" % (blind[1], day_label(blind[0], now))).strip())
    e = mc.get(mod)
    if e and now - (e.get("ts") or 0) <= days * 86400:
        parts.append(("modcheck %s %s" % (e.get("status"), day_label(e["ts"], now))).strip())
    else:
        parts.append("modcheck not run in %d days" % days)
    s = " · ".join(parts)
    return s[:1].upper() + s[1:]


def display_title(title):
    """The page's title: no fixed cut (CSS ellipsizes by width; TITLE_MAX is a sanity bound); a head shorter than three
    words ('Full list', 'Hose tick') keeps the rest of the title."""
    return title_short(title, TITLE_MAX, min_words=3)


def n_words(n, one, many=None):
    return "%d %s" % (n, one if n == 1 else (many or one + "s"))


def split_cross(item_mods):
    """-> set of items whose commits touched CROSS_MIN+ mods (infra not counted)."""
    return {i for i, ms in item_mods.items() if len(ms - {INFRA}) >= CROSS_MIN}


def mods(now, log, world, evs, rel, mc, folders, days=DAYS):
    """One doc per mod touched in the window, plus the infra block and the cross-mod block. No position field: the
    page sorts by `waits_you`, `closed`, `last_at` (a stored position would rewrite every doc when one moves)."""
    known = world.items
    by_item, item_mods, mod_last, item_last = attribute(log, known, folders)
    upper = {k.upper(): k for k in folders}
    window = now - days * 86400
    cross = split_cross(item_mods)
    groups = {}
    for i, ms in item_mods.items():
        for m in ([CROSS] if i in cross else ms):
            groups.setdefault(m, set()).add(i)
    if groups.get(CROSS):
        mod_last[CROSS] = max(item_last.get(i, 0) for i in groups[CROSS])
    # open items named for a mod count toward its backlog even with no commit yet (they are its queue)
    named_open = {}
    for iid, it in known.items():
        if not it.open or iid in cross:
            continue
        m = mod_by_name(iid, upper)
        if m and m in mod_last:
            named_open.setdefault(m, set()).add(iid)
    closed_at = {i: close_at(known[i], evs) for i in item_mods if known[i].state in CLOSED_STATES}
    verdicts = {i: check_of(i, known[i], rel) for i in item_mods}
    asks = owner_queue.load_questions()  # the same plain question the board's Needs you shows
    docs = []
    for m, last in mod_last.items():
        if last < window:
            continue
        items = groups.get(m, set())
        if not items and m == CROSS:
            continue
        closed_week = [i for i in items if (closed_at.get(i) or 0) >= window]
        open_all = {i for i in items | named_open.get(m, set()) if known[i].open}
        parked_n = [i for i in open_all if parked(known[i], rel.get(i))]
        open_n = len(open_all) - len(parked_n)
        blind = None
        for i in items:
            s = rel.get(i) or {}
            c = s.get("check") if isinstance(s.get("check"), dict) else None
            if c and c.get("verdict") and (c.get("verdict_at") or c.get("at") or 0) >= window:
                at = int(c.get("verdict_at") or c.get("at"))
                if blind is None or at > blind[0]:
                    blind = (at, c["verdict"])
            elif not c:         # a check only the ledger records dates from the item's close
                v = ledger_verdict(known[i])
                at = closed_at.get(i)
                if v and at and at >= window and (blind is None or at > blind[0]):
                    blind = (at, v)
        nxt, waits, waits_you, waits_game = "", [], 0, 0
        cand = sorted(open_all, key=lambda i: (NEXT_REL.index(rel[i]["status"]) if rel.get(i, {}).get("status") in NEXT_REL
                                               else 9, {"doing": 0, "built": 1, "validated": 1, "ready": 2}.get(known[i].state, 3),
                                               -(item_last.get(i) or 0), i))
        for i in cand:  # next = the first open item nobody is waiting on
            if not parked(known[i], rel.get(i)) and not waits_on(known[i], rel.get(i), evs):
                nxt = display_title(known[i].title or i)
                break
        for i in cand:
            w = waits_on(known[i], rel.get(i), evs)
            if w == "you":
                waits_you += 1
                waits.append("waits on you: %s" % (asks.get(i) or display_title(known[i].title or i)))
            elif w:
                waits_game += 1
        waits = waits[:3] + (["%s more %s on you" % (waits_you - 3, "waits" if waits_you == 4 else "wait")]
                             if waits_you > 3 else [])
        if waits_game:
            waits.append("%s on the game" % n_words(waits_game, "item waits", "items wait"))
        stuck = []      # every open item of the mod that is not moving: who it waits on, and what is planned
        for i in cand:
            st = stuck_of(known[i], rel.get(i), evs, known, asks)
            if st:
                stuck.append(dict(st, id=i, title=asks.get(i) if st["waits"] == "you" and asks.get(i)
                                  else display_title(known[i].title or i)))
        tasks = []
        # this week's list: finished first (newest close first), then the open ones by their last commit
        for i in sorted(items, key=lambda i: (-(closed_at.get(i) or 0), -(item_last.get(i) or 0), i)):
            it = known[i]
            g, kind = task_mark(it, rel.get(i), verdicts.get(i))
            t = {"id": i, "mark": g, "kind": kind, "title": display_title(it.title or i),
                 "date": day_label(closed_at.get(i) or item_last.get(i), now)}
            if kind == "done" and verdicts.get(i):
                t["note"] = "check " + verdicts[i]
            if m == CROSS:
                names = sorted(folders.get(x, x) for x in item_mods[i] if x != INFRA)
                t["note"] = "%d mods: %s" % (len(names), ", ".join(names[:4]) + (" and %d more" % (len(names) - 4)
                                                                                 if len(names) > 4 else ""))
            tasks.append(t)
        name = INFRA_NAME if m == INFRA else CROSS_NAME if m == CROSS else folders.get(m, m)
        unchecked = sum(1 for i in closed_week if verdicts.get(i) not in ("PASS", "FAIL"))
        bits = []
        if closed_week:
            bits.append("%d done" % len(closed_week) + (", %d unchecked" % unchecked if unchecked else ""))
        if waits_you:
            bits.append("waits on you" if waits_you == 1 else "%d wait on you" % waits_you)
        if not bits:
            bits.append(day_label(last, now) or "today")  # the page heads these "Touched in the last 7 days"
        meta = " · ".join(bits)
        docs.append({"id": m, "name": name, "infra": m == INFRA, "cross": m == CROSS, "last_at": int(last),
                     "closed": len(closed_week), "open": open_n, "parked": len(parked_n), "waits_you": waits_you,
                     "unchecked": unchecked, "meta": meta,
                     "backlog": "Backlog: %d open · %d parked" % (open_n, len(parked_n)),
                     "counts": "%s · %d open · %d parked" % (meta, open_n, len(parked_n)),  # the pre-repair page reads this
                     "proof": "" if m in (INFRA, CROSS) else proof_line(m, mc, blind, now, days),
                     "next": nxt, "waits": waits, "stuck": stuck, "week": len(tasks),
                     "tasks": tasks[:TASKS_KEPT], "more": max(0, len(tasks) - TASKS_KEPT)})
    docs.sort(key=lambda d: (d["infra"] or d["cross"], -d["waits_you"], -d["closed"], -d["last_at"]))
    return docs


def factory(now, store=STORE):
    """Header facts: factory ok or the plain reason it is not, running/target workers, Relentless tokens today (UTC)."""
    st = load_json(os.path.join(store, "staffing.json"), {})
    br = load_json(os.path.join(store, "breaker.json"), {})
    integ = load_json(os.path.join(store, "integrity.json"), {})
    why = ""
    if not st:
        why = "no staffing reading"
    elif now - (st.get("t") or 0) > 15 * 60:
        why = "silent %dm" % int((now - (st.get("t") or 0)) / 60)
    elif (br.get("until") or 0) > now:
        why = "paused after repeated failures"
    elif integ.get("blocked"):
        why = "blocked by a damage check"
    elif st.get("alarmed"):
        why = "alarm raised"
    return {"ok": not why, "why": why, "running": st.get("running"), "target": st.get("target"),
            "tokens_today": st.get("spent_today"), "at": int(now)}


def gather(now, days=DAYS, detached_done=()):
    log = parse_log(git_log(days))
    evs, world = ledger()
    rel = relentless_states(strict=True)
    with open(MODCHECK) as f:      # unread, every mod would claim "modcheck not run": let the reading fail instead
        mc = json.load(f)
    folders = mod_folders()
    by_item, item_mods = attribute(log, world.items, folders)[:2]
    cross = split_cross(item_mods)
    for r in detached_done:
        it = world.items.get(r["item"])
        if it is not None:
            r.setdefault("title", it.title)
    rec = receipts(now, by_item, rel, world, evs, detached_done)
    for r in rec:
        it = world.items.get(r["item"])
        r.setdefault("title", (it.title if it else "") or r["item"])
        r["where"], r["infra"] = where(r["item"], item_mods, cross, folders)
    return {"factory": factory(now), "receipts": rec, "mods": mods(now, log, world, evs, rel, mc, folders, days),
            "needs": owner_queue.needs_you(world.items, rel, evs=evs, turns=owner_queue.designer_turns())}


def where(item, item_mods, cross, folders):
    """-> (plain words for the mod(s) a finished item served, infra?). Infra/tooling receipts live in the infra block."""
    ms = item_mods.get(item) or set()
    if item in cross:
        return "%d mods" % len(ms - {INFRA}), False
    names = sorted(folders.get(m, m) for m in ms if m != INFRA)
    return ", ".join(names), not names and INFRA in ms  # no commit at all is not infra: it stays in the list


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=DAYS)
    a = ap.parse_args()
    print(json.dumps(gather(int(time.time()), a.days), indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
