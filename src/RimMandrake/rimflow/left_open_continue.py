#!/usr/bin/env python3
"""left_open_continue: a detached run that ends success with work left is continued by itself
(RIMMANDRAKE_CONTINUE_LEFT_OPEN_RUNS_WITHOUT_A_HAND_RELAUNCH).

2026-11-18: a four-ticket lane closed one ticket and exited, a five-step code split did step one and exited with a
LEFT OPEN note, and the Conductor relaunched each by hand; a third run, stopped by its spend cap mid-job, was resumed
by hand. Owner: "Why are you having to relaunch it?" His 2026-11-15 rule: a wait is automated or paused with an alarm,
never hand-walked.

  plan    finish calls it with the run's clone still standing: what the run left, from its own ledger
  run     `left_open_continue.py run --unit U`, its own unit (<U>-continue, --no-block) started by finish: it waits
          for the run's clone to be given back (detached_helper.launch does), checks the gates again and launches ONE
          continuation of the same work, same model, seat, budget and env, with a header quoting what was left

A run is continued when it ended success (exit 0) and either its item is still open with a `LEFT OPEN:` note written
since the run began, or its brief is a lane (it says "lane" and bullets ticket ids) with tickets still open: the
continuation then works the first open ticket. A run the spend watchdog stopped is continued only when its launch
carried `--continue-on-cap N` (default 0), at most N times along its chain: a cap stays meaningful. A run whose own
item is open works that item, the open lane tickets listed; a closed one hands off to the first open lane ticket whose
dated wait is not running. A run that ended success with its item open and nothing said (no LEFT OPEN: note, none in
its result text, no open lane ticket) is continued ONCE, kind `owed`, to close the item on its published sha or say
what is left; an owed continuation that ends the same way is the alarm (RIMMANDRAKE_CLOSE_DETACHED_ITEM_AT_RUN_END:
13 such runs were closed by hand in five days, 6 of them with work left, so a close from the exit alone is wrong).
Boundary: design/specs/2026-11-19-run-end-continue/boundary.md. Never continued:
a killed, voided or failed run, a closed item (a lane with every ticket closed), an owner-held mod, a paused pipeline,
a `pipe off` switch on its scope; a gate that cannot be read is a named no. At most MAX_PER_DAY continuations per item
(its chain's first item) in 24 h; the next one is the alarm ALARM_ID in the Conductor log and no launch. The header
carries no spend, cap or remainder (owner 2026-11-16: no launched agent is told its spend).

The continuation RESUMES the ended session (`--resume`) when its transcript is found and its last context is under
RESUME_WHOLE_MAX_TOKENS, whatever the time since it ended; the prompt is then the header alone. A larger (or unreadable)
context starts FRESH when the run left a progress record (PROGRESS: or LEFT OPEN: notes on its item since its chain
began): the brief is the header, that record and the previous brief, and the record names why (continue_fresh_why).
With no progress record it resumes anyway, so nothing is lost (continue_resume_why). The Conductor's manual
`detached_helper.py launch --resume` follows the same rule (conductor_resume). Boundary:
design/specs/2026-11-21-live-sitting-context-burn/boundary.md (RIMMANDRAKE_STOP_RESUME_REWRITING_CONTEXT_A_MILLION_AT_ONCE).
A blind role never resumes: a judge, reader, examiner, challenger or coverage
judge starts fresh every time (RIMMANDRAKE_LAUNCH_SIX_CONTEXT_KEEPING_CHANGES_FROM_THE_SCAN; owner 2026-11-20: "The
needless churn of shutdown->reload context->figure out what to do when you literally started that way before
shutdown. That needs to STOP." and "blind judges and others don't inherit the builder's context").
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import detached_helper as DH  # noqa: E402

MAX_PER_DAY = 3
DAY_S = 86400
ALARM_ID = "DETACHED_CONTINUE_LIMIT_REACHED"
HEAD = "LEFT OPEN CONTINUE"
LANE_RX = re.compile(r"\blane\b", re.I)
BULLET_ID_RX = re.compile(r"^\s*[-*]\s+`([A-Z][A-Z0-9_]{7,})`", re.M)
# A resume carries the session's whole context into every request, and on a cache miss (past the 1 h cache life, or a
# model change) its first request writes all of it again: 2026-11-21, resumes of 252k-362k contexts cost 0.72M-1.20M
# weighted_v2 in that one request, 29-48% of a 2.5M cap; a fresh sitting starts at 74k-105k. Past this, a run that left a
# progress record starts fresh from it (design/specs/2026-11-21-live-sitting-context-burn/boundary.md LIMITS).
RESUME_WHOLE_MAX_TOKENS = 150000
PROGRESS_HEADS = ("PROGRESS:", "LEFT OPEN:")
CONDUCTOR_PROJECTS = None      # the transcripts' projects dir for conductor_resume (None: detached_helper's default)
BLIND_STAGES = ("blind_challenge",)
BLIND_VERBS = ("JUDGE", "CHALLENGE", "PILOT", "EXAMINE")     # maturation_dispatch.JUDGE_VERBS, and the exam's
ROLE_RX = re.compile(r"\byou are (?:a|an|the)\s+(?:[\w-]+\s+){0,2}?(judge|reviewer|reader|examiner|challenger)\b", re.I)
TITLE_RX = re.compile(r"\b(blind|fresh read(?:er)?|second reader|naive judge|independent (?:read|review|judge))\b", re.I)
TERMINAL = ("done", "dropped", "superseded")     # model.TERMINAL, without importing the ledger here
READ_STATES = r"""
import json, os, sys
sys.path.insert(0, os.path.join("src", "RimMandrake", "rimflow"))
import model
items = model.replay(model.read()).items
print(json.dumps({i: {"state": getattr(items.get(i), "state", None), "wait_until": getattr(items.get(i), "wait_until", None)}
                  for i in sys.argv[1:]}))
"""


def local(t):
    return time.strftime("%Y-%m-%d %I:%M %p %Z", time.localtime(t))


def brief_of(rec):
    """-> the brief the chain began with (a continuation's own brief is header + this), or ""."""
    for p in (rec.get("continue_brief_src"), rec.get("brief_src")):
        try:
            with open(p or "/nonexistent", encoding="utf-8", errors="replace") as f:
                return f.read()
        except OSError:
            continue
    return ""


def lane_tickets_of(rec):
    """-> the ticket ids a lane brief bullets, in order; [] for a brief that is not a lane."""
    b = brief_of(rec)
    if not LANE_RX.search(b):
        return []
    return list(dict.fromkeys(BULLET_ID_RX.findall(b)))


def read_states(clone, ids):
    """-> {id: {"state", "wait_until"}} as the run's clone folds its ledger; raises when it cannot be read."""
    if not ids:
        return {}
    r = subprocess.run([sys.executable, "-c", READ_STATES] + list(ids), cwd=clone, capture_output=True, text=True,
                       timeout=300, stdin=subprocess.DEVNULL)  # budget: class=rimflow
    if r.returncode:
        raise RuntimeError("ledger read in %s exited %d: %s" % (clone, r.returncode, (r.stderr or "")))
    return json.loads(r.stdout)


def capped(rec):
    """True when the spend watchdog (or claude's own budget stop) ended the run."""
    import role_launch as RL
    return DH.cap_stopped(RL.read_result({"out": rec.get("out") or "", "err": rec.get("err") or ""}))


def _state(v):
    """A lane read: {"state", "wait_until"}, or a bare state (a plan written before the waits were read)."""
    return v.get("state") if isinstance(v, dict) else v


def _wait(v):
    return v.get("wait_until") if isinstance(v, dict) else None


def result_left_open(rec):
    """-> the run's own `LEFT OPEN:` paragraph from its result text (DH.result_left_open), its spend sentences taken
    out, or "" when the result says none. A run that wrote it only there said what is left."""
    import spend_talk
    return spend_talk.strip(DH.result_left_open(rec)).strip()


def last_left_open(notes, item, since):
    """-> the newest note on `item` since `since` that starts LEFT OPEN:, or None."""
    best = None
    for e in notes or []:
        t = DH._epoch(e.get("ts")) if isinstance(e, dict) else None
        if (t is not None and t >= since and e.get("id") == item and e.get("event") == "note"
                and str(e.get("text") or "").strip().upper().startswith(DH.LEFT_OPEN)):
            if best is None or t >= best[0]:
                best = (t, e)
    return best[1] if best else None


# ---------------------------------------------------------------- gates (each injectable; a read failure is a no)
def _paused(mod):
    import pipeline_pause
    return pipeline_pause.blocks(mod)


def _held(mod):
    import mod_owner_hold
    h = mod_owner_hold.held(mod) if mod else None
    return mod_owner_hold.status(h) if h else None


def _voided(unit):
    import control as C
    import run_void
    return bool(C.voided([unit])) or unit in run_void.active()


def _blocked(spec):
    import control as C
    return C.blocked(spec)


GATES = {"paused": _paused, "held": _held, "voided": _voided, "blocked": _blocked}


def gate_no(rec, item, gates):
    """-> why no continuation may start now, or None."""
    g = dict(GATES, **(gates or {}))
    mod = (rec.get("env") or {}).get("RM_CONTROL_MOD")
    spec = {"family": "detached", "item": item, "mod": mod, "stage": (rec.get("env") or {}).get("RM_CONTROL_STAGE")}
    for name, arg in (("voided", rec.get("unit")), ("held", mod), ("paused", mod), ("blocked", spec)):
        try:
            v = g[name](arg)
        except Exception as e:  # noqa: BLE001  a gate that cannot be read never lets a launch through
            return "the %s gate could not be read (%s: %s)" % (name, type(e).__name__, e)
        if v:
            return "the run is voided" if name == "voided" else str(v)
    return None


def today(rec, now, root=None):
    """-> the continuations of this chain's item (or this item) launched in the last DAY_S, oldest first. A refused or
    failed launch ran nothing and spends no slot, and nor does a continuation that died of a system cause
    (failure_class: no trial is spent by a system failure)."""
    import stop_resume as SR
    import failure_class as FC

    def died(r):
        fc = FC.of_run(r) if r.get("status") == "finished" else None
        return bool(fc and fc.classed and not fc.counts)
    key = rec.get("continue_root_item") or rec.get("item")
    return sorted((r for r in SR.recent_records(root, now)
                   if r.get("continued_from") and (r.get("at") or 0) >= now - DAY_S
                   and r.get("status") not in ("refused", "launch_failed") and not died(r)
                   and key in (r.get("continue_root_item"), r.get("item"))), key=lambda r: r.get("at") or 0)


def relaunched(rec, targets, now, root=None):
    """-> the unit of a run of one of `targets` (the item, its lane's open tickets) launched after this run began (a
    hand relaunch, another continuation), or None."""
    import stop_resume as SR
    later = sorted((r for r in SR.recent_records(root, now) if r.get("unit") != rec.get("unit")
                    and r.get("item") in set(targets) and (r.get("at") or 0) > (rec.get("at") or 0)
                    and r.get("status") not in ("launch_failed", "refused")), key=lambda r: r.get("at") or 0)
    return later[0]["unit"] if later else None


def waiting(got, now):
    """-> why the item's own dated `rimflow wait` forbids a continuation now, or None (no wait, or its date passed).
    A wait is the item saying nothing can move before its date; an unreadable date is a no, named."""
    until = (got or {}).get("wait_until")
    if not until:
        return None
    t = DH._epoch(until)
    if t is None:
        return "its wait date %r could not be read, so it is treated as still running" % (until,)
    return "it waits until %s (rimflow wait), so a continuation now has nothing to do" % local(t) if t > now else None


def plan(rec, got, lane_states, now=None, gates=None, root=None):
    """-> {act: continue|alarm|none, why, ...}. rec: the finished run (its result set); got: read_item's {state, notes}
    for its item from the run's clone; lane_states: {ticket: state} for its lane's tickets."""
    now = now or time.time()
    item = rec.get("item")
    res = str(rec.get("result") or "")
    base = {"unit": rec.get("unit"), "item": item}
    if rec.get("continued_by"):
        return dict(base, act="none", why="already continued as %s" % rec["continued_by"])
    if rec.get("next_act_owner"):     # list_dispatch counts its own runs (design/specs/2026-11-23-list-dispatch)
        return dict(base, act="none", why="its next act belongs to %s, which launched it" % rec["next_act_owner"])
    if res.startswith("killed"):
        return dict(base, act="none", why="killed runs are never continued (%s)" % res)
    cap = capped(rec)
    opt = int(rec.get("continue_on_cap") or 0)
    used = int(rec.get("cap_continues_used") or 0)
    if cap and used >= opt:
        return dict(base, act="none", why="stopped by the spend watchdog; its launch's --continue-on-cap %d is %s"
                    % (opt, "used" if opt else "not set"))
    if not cap and not res.startswith("success ("):
        return dict(base, act="none", why="the run did not end success (%s)" % (res or "no result"))
    if not isinstance(got, dict):
        return dict(base, act="none", why="its item's state could not be read from the run's clone")
    state = got.get("state")
    lane = lane_tickets_of(rec)
    ls = lane_states or {}
    open_lane = [t for t in lane if _state(ls.get(t)) and _state(ls.get(t)) not in TERMINAL]
    noted = last_left_open(got.get("notes"), item, rec.get("at") or 0)
    said = "" if noted else result_left_open(rec)
    if said:
        noted = {"ts": "its result text", "text": said}
    item_open = bool(state) and state not in TERMINAL
    kind = None
    if item_open and (noted or open_lane or cap):
        target = item
    elif open_lane:
        free = [t for t in open_lane if not waiting({"wait_until": _wait(ls.get(t))}, now)]
        if not free:
            return dict(base, act="none", why="every open lane ticket waits: " + "; ".join(
                "%s: %s" % (t, waiting({"wait_until": _wait(ls.get(t))}, now)) for t in open_lane))
        target = free[0]
    elif not item_open:
        return dict(base, act="none", why="%s is %s" % (item, state or "absent from the ledger"))
    elif rec.get("continue_kind") == "owed":
        return dict(base, act="alarm", why="%s is still %s after a continuation asked only to close it or say what is "
                                           "left, and it did neither" % (item, state))
    else:
        target, kind = item, "owed"
    waits = waiting(got, now) if target == item else None
    if waits:
        return dict(base, act="none", why=waits)
    no = gate_no(rec, target, gates)
    if no:
        return dict(base, act="none", why=no)
    done = today(rec, now, root)
    if len(done) >= MAX_PER_DAY:
        return dict(base, act="alarm", why="%d continuations of %s in 24 h already (%s)" % (
            len(done), rec.get("continue_root_item") or item, ", ".join(r["unit"] for r in done[-MAX_PER_DAY:])))
    progress = progress_record(got.get("notes"), [x for x in (item, rec.get("continue_root_item")) if x],
                               chain_start(rec, root))
    if said:
        progress.append({"ts": "its result text", "text": said})
    return dict(base, act="continue", target=target, open_lane=open_lane, capped=cap, kind=kind, progress=progress,
                note={"ts": noted.get("ts"), "text": noted.get("text")} if noted else None,
                n=int(rec.get("continue_n") or 0) + 1,
                why=("stopped from outside; --continue-on-cap %d" % opt) if cap else
                    "ended success with its item open and nothing said (OWED)" if kind == "owed" else
                    ("LEFT OPEN note" + (" in its result" if said else "") if noted and target == item
                     else "%d lane ticket(s) open" % len(open_lane)))


def blind_role(rec, target=None):
    """-> the blind role this run holds (a judge, reader, examiner, challenger, coverage judge: its point is NOT to
    carry another's context), or None. Read from its stage, its item names and the opening of its brief; a builder whose
    brief only names a judge as its subject is not one. A false yes costs only a fresh start, as before resume existed."""
    st = (rec.get("env") or {}).get("RM_CONTROL_STAGE")
    if st in BLIND_STAGES:
        return "stage %s" % st
    for it in (rec.get("item"), target):     # BLIND and a judge's verb: its slot-2 verb, or any word of an old name
        s = str(it or "").upper()
        verbs = [s[12:].split("_", 1)[0]] if s.startswith("RIMMANDRAKE_") else s.split("_")
        if "BLIND" in s and any(v in BLIND_VERBS for v in verbs):
            return "item %s" % it
    b = brief_of(rec)
    m = ROLE_RX.search(b[:800])  # cut-ok: search the brief header for a role
    if m:
        return "its brief says %r" % m.group(0)
    first = next((ln for ln in b.splitlines() if ln.strip()), "")
    m = TITLE_RX.search(first) if first.lstrip().startswith("#") else None
    return "its brief's title says %r" % m.group(0) if m else None


def chain_start(rec, root=None):
    """-> the start time of the chain's first run (its continue_root's record), else this run's own start."""
    first = DH.read_record(rec["continue_root"], root) if rec.get("continue_root") else None
    for r in (first, rec):
        if isinstance((r or {}).get("at"), (int, float)):
            return r["at"]
    return 0


def progress_record(notes, items, since):
    """-> the run's progress record: every note on one of `items` whose text starts PROGRESS: or LEFT OPEN: (any case),
    written at or after `since`, as [{"ts", "text"}] oldest first, each text whole."""
    out = []
    for e in notes or []:
        t = DH._epoch(e.get("ts")) if isinstance(e, dict) else None
        if (t is not None and t >= since and e.get("event") == "note" and e.get("id") in set(items)
                and str(e.get("text") or "").strip().upper().startswith(PROGRESS_HEADS)):
            out.append((t, {"ts": e.get("ts"), "text": str(e.get("text"))}))
    return [n for _, n in sorted(out, key=lambda x: x[0])]


def progress_block(progress):
    """The progress record as brief text, or "" when there is none."""
    if not progress:
        return ""
    lines = ["---- the run's progress record (its PROGRESS: and LEFT OPEN: notes, oldest first, verbatim) ----"]
    for n in progress:
        lines.append("[%s]" % (n.get("ts") or "?"))
        lines += ["> " + ln for ln in str(n.get("text") or "").splitlines() or [""]]
    return "\n".join(lines) + "\n"


def whole_or_fresh(ctx, progress):
    """The one rule. -> (resume?, why). ctx: the session's last context in tokens, or None when unreadable."""
    if ctx is not None and ctx < RESUME_WHOLE_MAX_TOKENS:
        return True, "its context of %d tokens is under %d: it resumes" % (ctx, RESUME_WHOLE_MAX_TOKENS)
    size = ("its context of %d tokens is at or over %d" % (ctx, RESUME_WHOLE_MAX_TOKENS) if ctx is not None else
            "its context is UNMEASURED (no main-thread usage), counted as at or over %d" % RESUME_WHOLE_MAX_TOKENS)
    if progress:
        return False, "%s, and it left a progress record (%d note(s)): a fresh session starts from it" % (
            size, len(progress))
    return True, "%s, but it left no progress record (no PROGRESS: or LEFT OPEN: note since its chain began): it " \
                 "resumes, so nothing is lost" % size


def resume_choice(rec, p, now, projects=None):
    """-> (session id, None, why it resumes) to resume the ended run's session, or (None, why it starts fresh, None)."""
    role = blind_role(rec, p.get("target"))
    if role:
        return None, "a blind role (%s) always starts fresh, never in a session that holds earlier context" % role, None
    import stop_resume as SR
    sid = rec.get("session") or rec.get("session_id")
    if not (sid and DH.find_transcript(sid, projects)):
        sid = SR.session_of(rec, projects)
    t = DH.find_transcript(sid, projects) if sid else None
    if not t:
        return None, "no transcript of its session was found", None
    resume, why = whole_or_fresh(DH.context_tokens(t), p.get("progress") or [])
    return (sid, None, why) if resume else (None, why, None)


def conductor_resume(session, item, brief, projects=None, reader=None, env=None):
    """The Conductor's `launch --resume SESSION`, under the one rule. -> {"session": the session to resume or None,
    "brief": the brief to launch, "extra": record fields, "line": one line to print first, or ""}.
    A converted resume also returns the launch env with any fresh-start role carried over."""
    projects = projects or CONDUCTOR_PROJECTS
    t = DH.find_transcript(session, projects)
    if not t:          # the launch itself refuses a session with no transcript, as before
        return {"session": session, "brief": brief, "extra": {}, "line": ""}
    mine = sorted((r for r in DH.all_records() if session in (r.get("session"), r.get("resume_session"))
                   and isinstance(r.get("at"), (int, float))), key=lambda r: r["at"])
    if not mine:
        return {"session": session, "brief": brief, "line": "", "extra": {"continue_resume_why": "no run record holds "
                "session %s, so its progress record cannot be read: it resumes" % session}}
    got = (reader or (lambda i: DH.read_item(DH.REPO, i)))(item)
    if not isinstance(got, dict):       # could not look: never read as "no progress record", said as its own cause
        return {"session": session, "brief": brief, "line": "", "extra": {"continue_resume_why": "the notes of %s "
                "could not be read (progress record UNMEASURED): it resumes" % item}}
    items = [item] + [x for x in (mine[0].get("continue_root_item"), mine[0].get("item")) if x and x != item]
    progress = progress_record(got.get("notes"), items, chain_start(mine[0]))
    resume, why = whole_or_fresh(DH.context_tokens(t), progress)
    if resume:
        return {"session": session, "brief": brief, "extra": {"continue_resume_why": why}, "line": ""}
    orig = brief_of(mine[0])          # the session's first run holds the original brief; a resume's is its short prompt
    rest = progress_block(progress)
    if orig.strip():
        rest += "\n---- the previous run's brief ----\n" + orig.rstrip() + "\n"
    new = {"item": item, "env": env}
    role = DH.mark_fresh(new, brief + "\n\n" + rest, session)
    packet_hint = "" if role else (" and the ITEM PACKET below (no packet, or a part left out: `python3 "
                                   "src/RimMandrake/rimflow/cli.py show %s`)" % item)
    text = (brief.rstrip() + "\n\nThis is a FRESH session, not a resume of session %s (%s). Your clone stands on "
            "origin/main. First read `git log --oneline -15`%s; do not redo work that is already published. Then carry on "
            "from the progress record below.\n\n" % (session, why, packet_hint)) + rest
    return {"session": None, "brief": text, "env": new["env"], "line": "FRESH instead of --resume %s: %s" % (session, why),
            "extra": {"continue_how": "fresh", "continue_fresh_why": why, "resume_converted_from": session}}


def header(rec, p, now):
    """The continuation's brief header. Never a word on spend, its cap, what is left of one or why a run was stopped:
    a stopped run is "interrupted", nothing more (RIMMANDRAKE_HIDE_CAP_STOP_FROM_RESUMED_RUN_READER_TRIMMED)."""
    lines = ["CONTINUED BY ITSELF (left_open_continue.py, %s): continuation %d of at most %d a day for %s." % (
        local(now), p["n"], MAX_PER_DAY, rec.get("continue_root_item") or rec["item"])]
    if p.get("capped"):
        lines.append("Your previous run %s on %s was interrupted before it finished." % (rec["unit"], rec["item"]))
    elif p.get("kind") == "owed":
        lines.append("Your previous run %s on %s ended success but left the item open and said nothing: no close, no "
                     "LEFT OPEN: note. Your one job is to settle that. If its work is done and published, close the item "
                     "on that sha (`python3 src/RimMandrake/rimflow/cli.py close %s --sha <sha> --seat %s --why \"...\"`). "
                     "If work is left, do it and close, or write a note whose text starts LEFT OPEN: and says exactly "
                     "what is left. Ending with neither raises an alarm to the Conductor."
                     % (rec["unit"], rec["item"], rec["item"], rec.get("seat") or "BENCH"))
    else:
        lines.append("Your previous run %s on %s ended success with work left, so it is carried on without a hand "
                     "relaunch." % (rec["unit"], rec["item"]))
    if p.get("note"):
        lines.append("Its LEFT OPEN note (%s), verbatim:" % (p["note"].get("ts") or "?"))
        lines += ["> " + ln for ln in str(p["note"].get("text") or "").splitlines() or [""]]
    if p.get("open_lane"):
        lines.append("Still open: %s (lane tickets in the brief below; you work %s first)."
                     % (", ".join("`%s`" % t for t in p["open_lane"]), p["target"]))
    if p.get("resumed"):
        lines.append("This is the same session, resumed: everything above is your own earlier work. Your clone is a new "
                     "one on origin/main (the footer names it): what you had not published is not in it%s. Read `git "
                     "log --oneline -5` and carry on from where you stopped; do not re-read what you already know." % (
                         "; it was saved in %s (HEAD, diff.patch, untracked.tar, deleted)" % rec["bundle"]
                         if rec.get("bundle") else ""))
        return "\n".join(lines) + "\n"
    import item_packet
    role = item_packet.role_of(brief_of(rec), rec.get("env"))
    packet_hint = "" if role else (" and the ITEM PACKET below (no packet, or a part left out: `%s`)"
                                   % (item_packet.SHOW % p["target"]))
    lines.append("This is a fresh session with no memory of the previous one. Your clone stands on origin/main. First "
                 "read `git log --oneline -15`%s; do not redo work that is already published. Then carry on from where "
                 "it stopped%s." % (packet_hint, ", as the progress record below says" if p.get("progress") else ""))
    return "\n".join(lines) + "\n" + ("\n" + progress_block(p.get("progress")) if p.get("progress") else "")


def alarm(rec, p, now, log_path=None, root=None):
    """The Conductor-log alarm, once per run. A log write that failed marks nothing, so the next pass raises it again.
    -> plan with act alarmed | alarm_failed | none."""
    rec = DH.read_record(rec["unit"], root) or rec
    if rec.get("continue_alarm"):
        return dict(p, act="none", why="alarm already raised")
    try:
        DH.conductor_line("ALARM %s: %s on %s ended with work left and is NOT continued: %s. Look at the item "
                          "(rimflow show %s) and relaunch by hand or close it." % (
                              ALARM_ID, rec["unit"], rec["item"], p["why"], rec["item"]), now, log_path, head=HEAD)
    except Exception as e:  # noqa: BLE001
        rec["continue_alarm_failed"] = {"at": now, "why": "%s: %s" % (type(e).__name__, e)}
        DH.write_record(rec, root)
        journal({"at": DH.iso(now), **{k: v for k, v in p.items() if k != "note"}, "act": "alarm_failed",
                 "log_failed": str(e)}, root)
        return dict(p, act="alarm_failed", log_failed="%s: %s" % (type(e).__name__, e))
    rec["continue_alarm"] = {"at": now, "why": p["why"]}
    rec.pop("continue_alarm_failed", None)
    DH.write_record(rec, root)
    journal({"at": DH.iso(now), **{k: v for k, v in p.items() if k != "note"}, "act": "alarm"}, root)
    return dict(p, act="alarmed")


def journal(row, root=None):
    try:
        with open(os.path.join(DH.runs_dir(root), "left_open_continue.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(row, sort_keys=True, default=str) + "\n")
    except OSError:
        pass


def read_target(target):
    """The step's own read of its target, from the clone the step runs in. -> read_item's dict, or None."""
    return DH.read_item(DH.REPO, target)


def recheck(rec, now, gates=None, root=None, reader=None):
    """The continuation step's own look, minutes after finish planned it: the plan still stands? -> why not, or None.
    The target is read again last (a close or a new dated wait since finish stops the launch)."""
    p = rec.get("continue_plan") or {}
    if p.get("act") != "continue":
        return "no continuation planned"
    if rec.get("continued_by"):
        return "already continued as %s" % rec["continued_by"]
    claim = rec.get("continue_claim")
    if claim and now - claim < 900:
        return "another continuation step claimed it at %s" % local(claim)
    later = relaunched(rec, [p["target"]] + list(p.get("open_lane") or []), now, root)
    if later:
        return "already relaunched as %s" % later
    no = gate_no(rec, p["target"], gates)
    if no:
        return no
    if len(today(rec, now, root)) >= MAX_PER_DAY:
        return "limit"
    try:
        got = (reader or read_target)(p["target"])
    except Exception as e:  # noqa: BLE001
        got, err = None, "%s: %s" % (type(e).__name__, e)
    else:
        err = "no ledger answer"
    if not isinstance(got, dict):
        return "the target %s could not be read again before launch (%s)" % (p["target"], err)
    st = got.get("state")
    if not st or st in TERMINAL:
        return "the target %s is now %s" % (p["target"], st or "absent from the ledger")
    return waiting(got, now)


def run(unit, now=None, launch_fn=None, gates=None, root=None, log_path=None, reader=None, projects=None):
    """The continuation unit's step: launch the planned continuation once. -> {act, why, ...}."""
    now = now or time.time()
    rec = DH.read_record(unit, root)
    if not rec:
        return {"unit": unit, "act": "none", "why": "no record"}
    p = dict(rec.get("continue_plan") or {})
    why = recheck(rec, now, gates, root, reader)
    if why == "limit":
        return alarm(rec, dict(p, why="%d continuations in 24 h already" % MAX_PER_DAY), now, log_path, root)
    if why:
        if p.get("act") == "continue":
            rec["continue_skipped"] = {"at": now, "why": why}
            DH.write_record(rec, root)
            journal({"at": DH.iso(now), "unit": unit, "item": rec.get("item"), "act": "skipped", "why": why}, root)
        return {"unit": unit, "act": "none", "why": why}
    waits_for = account_end_wait(now)
    if waits_for:       # its run was told to save and end because the account ends: kick_waiting starts it after
        rec["continue_waits"] = {"at": now, "why": waits_for}
        DH.write_record(rec, root)
        journal({"at": DH.iso(now), "unit": unit, "item": rec.get("item"), "act": "waits", "why": waits_for}, root)
        return {"unit": unit, "act": "none", "why": "waits for the account switch: " + waits_for[:200]}  # cut-ok: terminal display
    rec["continue_claim"] = now
    DH.write_record(rec, root)
    root_brief = rec.get("continue_brief_src") or rec.get("brief_src")
    sid, fresh_why, resume_why = resume_choice(rec, p, now, projects)
    import stop_resume as SR

    def written(resumed):
        text = header(rec, dict(p, resumed=resumed), now)
        orig = brief_of(rec)
        if orig.strip() and not resumed:
            text += "\n---- the previous run's brief ----\n" + orig.rstrip() + "\n"
        return SR.with_card_text(p["target"], text, DH.REPO)
    extra = {"continued_from": unit, "continue_root": rec.get("continue_root") or unit,
             "continue_root_item": rec.get("continue_root_item") or rec["item"], "continue_n": p["n"],
             "continue_brief_src": root_brief, "continue_on_cap": int(rec.get("continue_on_cap") or 0),
             "cap_continues_used": int(rec.get("cap_continues_used") or 0) + (1 if p.get("capped") else 0)}
    if p.get("kind"):
        extra["continue_kind"] = p["kind"]
    launch_fn = launch_fn or DH.launch

    def go(session, why):
        x = dict(extra, continue_how="resume" if session else "fresh")
        if why:
            x["continue_fresh_why"] = why
        elif resume_why:
            x["continue_resume_why"] = resume_why
        kw = {"resume_session": session, "projects": projects} if session else {}
        try:
            return launch_fn(rec.get("seat"), p["target"], written(bool(session)), rec.get("model"),
                             rec.get("max_s") or "none", rec.get("budget_usd") or 0.0, now=now,
                             env=rec.get("env") or None, clone=SR.given_clone(rec), extra=x,
                             skip_launch_checks=("continuation of %s: the same work, whose launch checks already ran"
                                                 % unit) if p["target"] == rec.get("item") else None, **kw)
        except Exception as e:  # noqa: BLE001
            return 1, "%s: %s" % (type(e).__name__, e)
    code, out = go(sid, fresh_why)
    if sid and code and "has no transcript" in str(out):     # it vanished between the look and the launch
        sid, fresh_why = None, "the resume of session %s was refused: %s" % (sid, " ".join(str(out).split()))
        code, out = go(None, fresh_why)
    rec = DH.read_record(unit, root) or rec
    rec.pop("continue_claim", None)
    m = re.match(r"DETACHED (\S+)", out or "")
    if code == 0 and m:
        rec.update(continued_by=m.group(1), continued_at=now)
        DH.write_record(rec, root)
        line = "%s on %s ended with work left (%s); continued as %s on %s, same model %s, %s (%d of at most %d today)" % (
            unit, rec["item"], p.get("why"), m.group(1), p["target"], rec.get("model"),
            "its session resumed" if sid else "fresh: " + str(fresh_why), p["n"], MAX_PER_DAY)
        try:
            DH.conductor_line(line, now, log_path, head=HEAD)
        except Exception as e:  # noqa: BLE001
            print("conductor log not written: %s" % e, file=sys.stderr)
        journal({"at": DH.iso(now), "unit": unit, "item": rec["item"], "act": "continued", "new": m.group(1),
                 "target": p["target"]}, root)
        return {"unit": unit, "act": "continued", "new": m.group(1), "why": p.get("why")}
    rec["continue_refused"] = {"at": now, "why": str(out)}
    DH.write_record(rec, root)
    try:
        DH.conductor_line("%s on %s ended with work left but its continuation was REFUSED: %s" % (
            unit, rec["item"], " ".join(str(out).split())), now, log_path, head=HEAD)
    except Exception:  # noqa: BLE001
        pass
    journal({"at": DH.iso(now), "unit": unit, "item": rec["item"], "act": "refused", "why": str(out)}, root)
    return {"unit": unit, "act": "refused", "why": str(out)[:300]}  # cut-ok: terminal display


def account_end_wait(now, plan_dir=None):
    """-> why no continuation may start while the account ends (drain_refusal's text), or None. plan_dir: a test's
    folder; then only its notice is read."""
    return DH.drain_refusal(now, {"continued_from": "-"},
                            path=os.path.join(plan_dir, "notice.json") if plan_dir else None)


def kick_waiting(now=None, root=None, runner=subprocess.run, plan_dir=None):
    """Start the continuations that waited for the account switch, once the plan has headroom (the account plan's
    timed pass calls this after each pass, through the actuator's check). -> one line."""
    import stop_resume as SR
    now = now or time.time()
    waiting_recs = [r for r in SR.recent_records(root, now) if r.get("continue_waits") and not r.get("continued_by")]
    if not waiting_recs:
        return "left_open: none waits"
    ok, why = SR.headroom(plan_dir, now)
    if not ok or account_end_wait(now, plan_dir):
        return "left_open: %d wait (%s)" % (len(waiting_recs), why)
    said = []
    for r in waiting_recs:
        r = DH.read_record(r["unit"], root) or r
        kept = r.pop("continue_waits")
        DH.write_record(r, root)
        line = kick(r, r.get("continue_plan") or {}, runner)
        if "kicked" not in line or "NOT kicked" in line:    # tried again at the next pass
            r["continue_waits"] = kept
            DH.write_record(r, root)
        said.append(line)
    return "; ".join(said)


def kick_argv(rec):
    """The continuation step as its own unit (--no-block): finish runs inside the run's TimeoutStopSec and the return
    step after it gives the clone back, so the launch (which waits for that return) cannot run inside finish."""
    me = os.path.basename(os.path.abspath(__file__))
    env = ["--setenv", "RM_DISPATCHER_STATE=" + rec["state"], "--setenv", "RIMFLOW_SEAT=" + rec["seat"],
           "--setenv", "AGENT_SEAT=" + rec["seat"]]
    for k in ("RM_DETACHED_POOL", "RM_CONDUCTOR_LOG", "RELENTLESS_ROOT", "PATH", "WSL_INTEROP"):
        if os.environ.get(k):
            env += ["--setenv", "%s=%s" % (k, os.environ[k])]
    return ["--user", "--quiet", "--collect", "--no-block",     # control.launch_unit names the unit
            "-p", "RuntimeMaxSec=10800", "-p", "WorkingDirectory=/", *env,
            "--", *DH.stop_resolver(candidates(rec, me), ["run", "--unit", rec["unit"]])]


def candidates(rec, me):
    """Where the step's script may run from: the seat clones first, the run's own clone last (its return deletes it
    while the step waits, and the step imports more modules after that wait)."""
    own = rec.get("clone") and os.path.join(os.path.abspath(rec["clone"]), "")
    c = DH.stop_candidates(rec, me, run_clone_last=True)
    return [x for x in c if not (own and os.path.abspath(x).startswith(own))] + \
        [x for x in c if own and os.path.abspath(x).startswith(own)]


def kick(rec, p, runner=subprocess.run):
    """finish's step: start the continuation unit. -> one line."""
    import control as C     # the one admission point: `pipe off family:left_open_continue` stops every kick
    try:
        r = C.launch_unit(kick_argv(rec), {"family": "left_open_continue", "unit": rec["unit"] + "-continue",
                                           "item": p.get("target"), "reuse_name": True},
                          # budget: danger=a hung launch holds the run's end; longest=1.3s (admission to start of 1057 runs,
                          # budget: control.db)
                          runner=runner, capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
    except Exception as e:  # noqa: BLE001
        return "continue NOT kicked: %s: %s" % (type(e).__name__, e)
    if getattr(r, "refused", False):
        return "continue refused by control: %s" % r.why
    return "continue kicked %s-continue (%s)" % (rec["unit"], p.get("why")) if r.returncode == 0 else \
        "continue NOT kicked: %s" % ((r.stderr or r.stdout or "").strip())


def at_finish(rec, got, clone, now, runner=subprocess.run, continuer=None, states_reader=None):
    """finish's whole step: plan, then alarm or kick. -> (plan, step line)."""
    try:
        lane = lane_tickets_of(rec)
        states = (states_reader or read_states)(clone, lane) if lane else {}
    except Exception as e:  # noqa: BLE001
        return {"act": "none", "why": "lane tickets unreadable: %s" % e}, "continue: lane tickets UNMEASURED (%s)" % e
    try:
        p = plan(rec, got, states, now=now)
    except Exception as e:  # noqa: BLE001
        return {"act": "none", "why": "plan failed: %s" % e}, "continue: plan FAILED (%s: %s)" % (type(e).__name__, e)
    fresh = DH.read_record(rec["unit"]) or rec
    fresh["continue_plan"] = p          # written before the kick: the continuation step reads it
    DH.write_record(fresh)
    if p["act"] == "alarm":
        alarm(fresh, p, now)
        return p, "continue: ALARM %s (%s)" % (ALARM_ID, p["why"])
    if p["act"] != "continue":
        return p, "continue: none (%s)" % p["why"]
    return p, (continuer or (lambda r, q: kick(r, q, runner)))(fresh, p)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="the continuation unit's step (finish starts it)")
    r.add_argument("--unit", required=True)
    s = sub.add_parser("plan", help="read-only: what finish would plan for a finished run, from its record alone")
    s.add_argument("--unit", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "run":
        x = run(a.unit)
    else:
        rec = DH.read_record(a.unit) or {}
        x = rec.get("continue_plan") or {"act": "none", "why": "no plan on the record (finish wrote none)"}
    print("%s %s: %s" % (x.get("act"), a.unit, x.get("why")))
    return 0 if x.get("act") in ("continued", "none", "continue", "alarmed", "alarm") else 1


if __name__ == "__main__":
    sys.exit(main())
