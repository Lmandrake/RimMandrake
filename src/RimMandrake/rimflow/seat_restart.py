#!/usr/bin/env python3
"""seat_restart.py — a fresh Claude window per ticket: the seat asks, the Dispatcher restarts it (FOUNDRY_CONTEXT_BUILD_FRESH_PER_TICKET).

Why: a long-lived seat window (FOUNDRY) carries every ticket's context into the next — stale beliefs, "already ruled"
errors, compaction drift. The fix is ONE restart mechanism, shared with the Conductor's goodbye restart
(design/RimMandrake/conductor_briefing_2026-10-28.md Part B): the window is killed and relaunched as a NEW interactive
window with Remote Control on — never `claude -p`, never `--resume`, never /login.

Flow (state per seat in the Dispatcher's state.json, key "seat_restart"):
  request    the seat, at the end of its ticket's unit of work with no helper alive, runs
             `seat_restart.py request --seat FOUNDRY --ticket <ID> --reason closed --note "<3-5 lines>"`: the note goes
             to its seat log (read by the fresh window). While the window's context is under backstop_ctx_tokens it
             prints CONTEXT OK and writes NO request: the seat runs `rimflow next` and keeps going
             (FOUNDRY_IDLE_DIAGNOSE_CAP_STARVES_TRIAGE). Over it (or UNMEASURED, or --fresh) the request goes to
             <dispatcher state>/restart/<SEAT>.request.json.
             Refused while any helper of the window is alive. Backstop: the Dispatcher also starts one for a window that
             is idle, has no live helper, and whose context (last usage in its transcript) is past a threshold.
  pending    grace (grace_s; FOUNDRY 30 s); cancelled by new HUMAN input in the window's transcript after the request
             (never by the Dispatcher's ring, a task notification or a seat's cross-session message: _is_human_input;
             a Conductor's goodbye restart is the exception, cancelled by ANY input: cursor_verdict),
             or by the window's session changing. No ring while pending (ring_hold, bounded). HELD (never killed) while: a helper is alive (a stale one also alarms), the bridge or
             driver lock is held by the seat or unreadable, the seat's last game event is transitional, PAUSE, or a
             doorbell ring is in flight. Not quiet (idle + last record an ended assistant turn, 30 s old) for 3 ticks
             -> failed: busy.
  claimed    -> restart_kill: ~/.claude/sessions/<pid>.json must name the session and the seat's window name; then
             <state>/restart/<SEAT>.killed.json is written (the relaunch argv) and the pid gets SIGTERM, SIGKILL after
             10 s. Never fleet_stop, never pkill -f. Dry run: journalled, nothing killed.
  killed     the tile relaunches itself: the WT profile runs seat_loop.sh, which on Claude's exit calls `intile`, which
             claims the kill once and execs the relaunch argv (the profile's own LAUNCH line + a first prompt). No
             claim in 30 s -> fallback: machine.json's launch_fleet.ps1 narrowed to `-Seats <SEAT>` (a new tab; the old
             one is left at a shell). No window in 90 s more -> failed + alarm.
  relaunched a new session with the seat's name; verified once the doorbell is ARMED for that new session (the first
             prompt makes it end a turn), else failed + alarm after arm_s.
Every step is journalled (dispatcher journal.jsonl); failures alarm and note the ticket. Off unless the schedule key
`seat_restart.enabled` is true (design/RimMandrake/rimflow_v3_golive_wave1.md, "Seat restart: enable steps").
"""
import argparse
import datetime
import glob
import json
import os
import re
import signal
import subprocess
import sys
import time
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UTILS = os.path.join(REPO, "src", "RimMandrake", "Utils")
for _p in (HERE, os.path.dirname(HERE), UTILS):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import session_match as SM  # noqa: E402
import doorbell  # noqa: E402
from rmpaths import rm_str  # noqa: E402

DEFAULTS = {"grace_s": 120, "quiet_s": 30, "busy_ticks": 3, "verify_s": 90, "arm_s": 900, "intile_wait_s": 30,
            "intile_window_s": 90, "backstop_ctx_tokens": 110_000, "backstop_idle_s": 1800,
            "helper_stale_s": 1800, "game_hold_s": 3600, "cooldown_s": 1800,
            "hold_alarm_s": 3600, "request_max_age_s": 3600, "claimed_max_s": 300,
            "fence_s": 1020, "ring_hold_s": 600,
            "kind": "doorbell", "backstop_human_idle_s": 0, "goodbye_quiet_s": 600}
ACTIVE = ("pending", "claimed", "killed", "relaunched")
OWNS = ("claimed", "killed", "relaunched")      # pending leaves ring/recover running (review2: no recovery deadlock)
TRANSITIONAL = ("DEPLOYING", "LOADING", "GOING_DOWN")
DOES = ("restart_request", "restart_kill", "restart_fallback")
BOUNDED = "{clone}/src/RimMandrake/Utils/claude_bounded.sh"
MACHINE = os.path.expanduser("~/.claude-accounts/machine.json")
PROMPT = ("[RimFlow seat restart] You are a FRESH {seat} window: the last one was restarted after its ticket ended "
          "({why}). Run `python3 src/RimMandrake/rimflow/seat_restart.py wake --seat {seat}{gen}`, read what it prints, "
          "then end your turn: the Dispatcher hands you your next ticket through the doorbell.")
# kind "conductor" (CONDUCTOR_GOODBYE_DESIGN_FRESH_EACH_TIME): the BENCH window is the owner's Conductor. It has no
# doorbell (doorbell.py is FOUNDRY's Stop hook only) and no ticket to wait for: it wakes as the Conductor, answers any
# message he sent the old window after its close-out, and waits for him.
CONDUCTOR_PROMPT = ("[RimFlow seat restart] You are a FRESH Conductor window (session CONDUCTOR, seat key {seat}): the "
                    "last one closed out ({why}) and the Dispatcher restarted it; nobody typed this. Do the Start of "
                    "turn in infrastructure/agents/CONDUCTOR.md, and run `python3 src/RimMandrake/rimflow/seat_restart.py "
                    "wake --seat {seat}{gen}`: answer FIRST any owner message it lists as sent to the old window after the "
                    "close-out. Then report in a few lines what is open and what needs him, and wait for him.")
PROMPTS = {"doorbell": PROMPT, "conductor": CONDUCTOR_PROMPT}


# ---------------------------------------------------------------------------------------------------------------------
# config and paths

def config(sch):
    """-> {seat: cfg with defaults} for the seats seat_restart covers; {} while the key is off."""
    sr = sch.get("seat_restart") or {}
    if sr.get("enabled") is not True:
        return {}
    out = {}
    for seat, c in sorted((sr.get("seats") or {}).items()):
        if not isinstance(c, dict) or c.get("enabled") is False:
            continue
        base = dict((sch.get("seats") or {}).get(seat) or {})
        cfg = dict(DEFAULTS)
        cfg.update({k: v for k, v in sr.items() if k in DEFAULTS})
        cfg.update({k: base[k] for k in ("session_name", "session_aliases", "clone", "model") if k in base})
        cfg.update(c)
        cfg.setdefault("session_name", "AGENT " + seat)
        # a tile may never claim a relaunch decide() has already given up on (review3 #3)
        cfg["intile_window_s"] = min(cfg["intile_window_s"], cfg["intile_wait_s"] + cfg["verify_s"])
        out[seat] = cfg
    return out


def restart_dir(root=None):
    return os.path.join(root or doorbell.state_dir(), "restart")


def request_path(seat, root=None):
    return os.path.join(restart_dir(root), "%s.request.json" % seat)


def killed_path(seat, root=None):
    return os.path.join(restart_dir(root), "%s.killed.json" % seat)


def intile_path(seat, killed_at, root=None):
    return os.path.join(restart_dir(root), "%s.intile.%d.json" % (seat, int(killed_at)))


def seat_log_path(seat, cfg=None):
    if cfg and cfg.get("seat_log"):
        return cfg["seat_log"]
    return os.path.join(os.environ.get("RM_SEAT_LOG_DIR") or rm_str("seat_log"), "%s.md" % seat)


def _write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = "%s.%d.tmp" % (path, os.getpid())
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)
    os.replace(tmp, path)


def _read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else None
    except (OSError, ValueError):
        return None


def _iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def _ts(s):
    """ISO (with or without milliseconds, Z or offset) -> epoch, or None."""
    if not isinstance(s, str) or not s:
        return None
    try:
        d = datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=datetime.timezone.utc)
    return d.timestamp()


# ---------------------------------------------------------------------------------------------------------------------
# readers: transcript, helpers, session file, bridge, game

def claude_home():
    return os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")


def session_file(pid):
    """~/.claude/sessions/<pid>.json (pid, sessionId, cwd, name, status...) or None."""
    try:
        return _read_json(os.path.join(claude_home(), "sessions", "%d.json" % int(pid)))
    except (TypeError, ValueError):
        return None


def transcript_path(cwd, session_id):
    return os.path.join(claude_home(), "projects", re.sub(r"[^A-Za-z0-9]", "-", cwd), "%s.jsonl" % session_id)


def transcript_for(sess, cfg):
    sf = session_file(sess.get("pid")) or {}
    cwd = sess.get("cwd") or sf.get("cwd") or cfg.get("clone")
    sid = sess.get("sessionId") or sf.get("sessionId")
    return transcript_path(cwd, sid) if cwd and sid else None


class Malformed(ValueError):
    """A transcript line that is not one whole JSON record, or a record still being written at EOF (no newline). Every
    reader fails CLOSED on it (blind review 2 2026-10-29 P0-2: skipping it read an interrupted write as "nothing new").
    MEASURED 2026-10-29: 0 malformed lines in 2597 transcripts on SteveDesktop, 1 file without a final newline."""


class Torn(Malformed):
    """The last record at EOF has no newline yet: a write in progress (a hold, not proof of anything)."""


def _parse_line(raw):
    """-> the dict on one complete transcript line, None for a blank line; Malformed for anything else."""
    if not raw.strip():
        return None
    try:
        r = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        raise Malformed("undecodable transcript line (%d bytes)" % len(raw))
    if not isinstance(r, dict):
        raise Malformed("transcript line is not a record")
    return r


def _tail_records(path, nbytes):
    """-> the records in the last nbytes of path. Raises Malformed on a bad line or a torn last record (callers turn it
    into UNMEASURED; OSError likewise)."""
    with open(path, "rb") as f:
        f.seek(0, os.SEEK_END)
        size = f.tell()
        f.seek(max(0, size - nbytes))
        data = f.read()
    lines = data.split(b"\n")
    if lines and lines[-1].strip():
        raise Torn("torn last record (no newline at EOF)")
    if size > nbytes:
        lines = lines[1:]           # the first line of a tail is a fragment
    out = []
    for raw in lines:
        r = _parse_line(raw)
        if r is not None:
            out.append(r)
    return out


def _is_input(rec):
    """A user record that is real input (a typed or delivered prompt), not a tool result or a meta line."""
    if rec.get("isMeta") or rec.get("isCompactSummary"):
        return False
    content = (rec.get("message") or {}).get("content")
    if isinstance(content, str):
        return bool(content.strip())
    if isinstance(content, list):
        kinds = {b.get("type") for b in content if isinstance(b, dict)}
        return "tool_result" not in kinds and bool(kinds & {"text", "image"})
    return False


# Input no person typed. MEASURED 2026-10-29 over every transcript on SteveDesktop: a Dispatcher ring arrives as a
# Stop-hook task-notification (origin.kind task-notification, promptSource system) — the one that cancelled the dry
# restart at 04:27:29Z; a helper's or background task's end the same; a peer message as origin.kind "peer" with the
# sender's session name; `claude -p` prompts as promptSource sdk; scheduled prompts as turnOrigin scheduled.
MACHINE_ORIGINS = ("task-notification",)
MACHINE_SOURCES = ("system", "sdk")
MACHINE_TURNS = ("task_notification", "scheduled", "system", "sdk")
HUMAN_ORIGINS = ("human",)
HUMAN_TURNS = ("human",)
HUMAN_SOURCES = ("typed", "queued")
MACHINE_MARKERS = ("[RimFlow ", "<task-notification>", "[Cross-session idle notice]")
RING_MARK = "a program, not a person"
_FROM_NAME = re.compile(r'<cross-session-message\b[^>]*\bfrom-name="([^"]*)"')


def _text(rec):
    c = (rec.get("message") or {}).get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return "\n".join(b.get("text") or "" for b in c if isinstance(b, dict) and b.get("type") == "text")
    return ""


def peer_names(sch=None):
    """-> every session name of every scheduled seat (CONDUCTOR, AGENT BENCH, AGENT FOUNDRY, ...): a cross-session
    message from one of them is a seat talking, not the owner. A peer of any other name (OWNER: broadcast.py stamps it
    for the owner's `./game` messages) still counts as his input."""
    if sch is None:
        sch = _schedule()
    out = []
    for seat in sorted((sch.get("seats") or {})):
        for n in SM.seat_names(seat, sch):
            if n not in out:
                out.append(n)
    return out


def _is_human_input(rec, peers):
    """Real input (_is_input) that a person typed or delivered — never the Dispatcher's ring, a task notification, a
    [RimFlow] prompt, a `claude -p`/scheduled prompt, or a cross-session message from a seat named in peers."""
    if not _is_input(rec):
        return False
    o = rec.get("origin") if isinstance(rec.get("origin"), dict) else {}
    text = _text(rec).lstrip()
    if o.get("kind") == "peer" or rec.get("turnOrigin") == "peer":
        m = _FROM_NAME.search(text)
        name = o.get("name") or (m.group(1) if m else None)
        return not (name and SM.name_matches(name, list(peers or [])))
    if o.get("kind") in MACHINE_ORIGINS or rec.get("promptSource") in MACHINE_SOURCES \
            or rec.get("turnOrigin") in MACHINE_TURNS:
        return False
    # Structure over text (SEAT_RESTART_FIX_HUMAN_INPUT_MARKERS, Codex review 2026-10-29 P1 2): a record Claude Code
    # stamped as typed/queued by a person is human whatever it quotes (the owner may paste a ring or ask about "a
    # program, not a person"). MEASURED 2026-10-29 over every bench/foundry transcript: 1590 origin.kind human records,
    # none carrying a machine marker; every ring arrived as a task-notification or an sdk prompt.
    if o.get("kind") in HUMAN_ORIGINS or rec.get("turnOrigin") in HUMAN_TURNS \
            or rec.get("promptSource") in HUMAN_SOURCES:
        return True
    if text.startswith(MACHINE_MARKERS) or RING_MARK in text[:200]:   # fallback: a record with no origin fields
        return False
    return True


def _queued_as_user(rec):
    """A message he typed WHILE a turn ran is delivered into that turn and lands in the transcript ONLY as
    {type: attachment, attachment: {type: queued_command, commandMode: prompt, origin: {kind: human}, prompt}}, no user
    record. MEASURED 2026-10-29 over every ~/.claude/projects transcript: 444 such prompts, 440 never echoed as a user
    record (task notifications use commandMode task-notification). -> a user-shaped record for _is_human_input, or None.
    Without this a "wait" typed during the goodbye close-out was invisible to every cancel check."""
    a = rec.get("attachment") if rec.get("type") == "attachment" else None
    if not isinstance(a, dict) or a.get("type") != "queued_command" or a.get("commandMode") != "prompt":
        return None
    pr = a.get("prompt")
    content = pr if isinstance(pr, (str, list)) else ""
    out = {"type": "user", "timestamp": rec.get("timestamp") or a.get("timestamp"), "uuid": rec.get("uuid"),
           "isSidechain": rec.get("isSidechain"), "message": {"role": "user", "content": content},
           "queued_command": True}
    if isinstance(a.get("origin"), dict):
        out["origin"] = a["origin"]
    return out


def _assistant_kind(rec):
    sr = (rec.get("message") or {}).get("stop_reason")
    return "assistant_end" if sr == "end_turn" else "assistant_tool" if sr == "tool_use" else "assistant_other"


def tx_summary(path, tail_bytes=4 << 20, peers=None):
    """-> {last_kind, last_at, last_user_at, ctx_tokens} from the main transcript's tail, or None (unreadable).
    last_kind: assistant_end (turn ended) | assistant_tool | assistant_other | user. ctx_tokens: the last assistant
    record's input + cache read + cache creation tokens (what the next call re-sends). last_user_at: the last HUMAN
    input only (_is_human_input; peers default to every scheduled seat's names) — that is what cancels a restart."""
    if peers is None:
        peers = peer_names()
    try:
        recs = _tail_records(path, tail_bytes)
    except (OSError, Malformed):          # fail closed: an unreadable or torn tail is no reading at all
        return None
    s = {"last_kind": None, "last_at": None, "last_user_at": None, "ctx_tokens": None}
    for r in recs:
        q = _queued_as_user(r)
        if q is not None:                # typed mid-turn: counts as his input, does not change the turn's state
            if not q.get("isSidechain") and _is_human_input(q, peers):
                s["last_user_at"] = _ts(q.get("timestamp"))
            continue
        t = r.get("type")
        if t not in ("user", "assistant") or r.get("isSidechain"):
            continue
        at = _ts(r.get("timestamp"))
        if t == "assistant":
            s["last_kind"] = _assistant_kind(r)
            u = (r.get("message") or {}).get("usage") or {}
            if u:
                s["ctx_tokens"] = sum(int(u.get(k) or 0) for k in (
                    "input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
        else:
            s["last_kind"] = "user"
            if _is_human_input(r, peers):
                s["last_user_at"] = at
        s["last_at"] = at
    return s if s["last_kind"] else None


def _lines_from(path, offset):
    """Yield (record dict, end byte offset) for EVERY record from offset to EOF, any type: a full streaming read with
    no tail cap (review 1 P0-2). Raises Malformed on a bad line or a torn last record (review 2 P0-2), OSError as is."""
    with open(path, "rb") as f:
        f.seek(offset)
        pos = offset
        for raw in f:
            pos += len(raw)
            if not raw.endswith(b"\n"):
                raise Torn("torn last record at byte %d (no newline at EOF)" % (pos - len(raw)))
            r = _parse_line(raw)
            if r is not None:
                yield r, pos


def scan_records(path, offset=0):
    """Yield (record, end byte offset) for every main-chain user/assistant record (a queued_command prompt as a user
    record, _queued_as_user) from offset to EOF. Fails closed: raises Malformed (see _lines_from)."""
    for r, pos in _lines_from(path, offset):
        r = _queued_as_user(r) or r
        if r.get("type") in ("user", "assistant") and not r.get("isSidechain"):
            yield r, pos


def _is_any_input(raw, rec):
    """Input of ANY origin (his, a ring, a task notification, a peer): a user input record, a queued_command attachment
    of any mode, or a queue-operation enqueue. MEASURED 2026-10-29 over the bench transcripts: Claude Code writes the
    queue-operation enqueue (4569 of them) when a prompt is SUBMITTED, before its user record, so it is the earliest
    trace of a submit."""
    if raw.get("isSidechain"):
        return False
    if raw.get("type") == "queue-operation":
        return raw.get("operation") == "enqueue"
    if raw.get("type") == "attachment":
        return (raw.get("attachment") or {}).get("type") == "queued_command"
    return rec.get("type") == "user" and _is_input(rec)


def cursor_scan(path, offset, peers=None):
    """-> what the transcript holds from byte `offset` to EOF, read in full:
    {human: [his input records], inputs: [records of ANY input], last_at: newest record timestamp or None, size,
     malformed: None or why (a complete line that is not a record), torn: None or why (the last record has no newline
     yet)} — both fail CLOSED (cursor_verdict: malformed cancels, torn holds)
    or None (UNMEASURED: no path or cursor, unreadable, or the file is now shorter than the cursor).
    No timestamp filter (blind review 2 P0-3): every record after the cursor counts, whatever its clock says."""
    if not path or offset is None:
        return None
    if peers is None:
        peers = peer_names()
    out = {"human": [], "inputs": [], "last_at": None, "size": None, "malformed": None, "torn": None}
    try:
        out["size"] = os.path.getsize(path)
        if out["size"] < offset:
            return None
        for raw, _ in _lines_from(path, offset):
            at = _ts(raw.get("timestamp")) if raw.get("timestamp") else None
            if at is not None and (out["last_at"] is None or at > out["last_at"]):
                out["last_at"] = at
            r = _queued_as_user(raw) or raw
            if _is_any_input(raw, r):
                out["inputs"].append(r)
            if r.get("type") == "user" and not r.get("isSidechain") and _is_human_input(r, peers):
                out["human"].append(r)
    except Torn as e:
        out["torn"] = str(e)
    except Malformed as e:
        out["malformed"] = str(e)
    except OSError:
        return None
    return out


def human_since_offset(path, offset, peers=None):
    """-> every HUMAN input record from byte offset to EOF (no timestamp filter, review 2 P0-3), [] when there is none,
    or None (UNMEASURED: no path, unreadable, shorter than the cursor, or a malformed/torn record)."""
    sc = cursor_scan(path, offset, peers)
    if sc is None or sc["malformed"] or sc["torn"]:
        return None
    return sc["human"]


def last_human(path, peers=None):
    """-> (ts, record, end byte offset, file size) of the LAST human input in the whole transcript, (None, None, None,
    size) when he never typed, or None (unreadable or malformed: fail closed)."""
    if peers is None:
        peers = peer_names()
    best = (None, None, None)
    try:
        size = os.path.getsize(path)
        for r, end in scan_records(path, 0):
            if r.get("type") == "user" and _is_human_input(r, peers):
                best = (_ts(r.get("timestamp")), r, end)
    except (OSError, Malformed):
        return None
    return best + (size,)


def _non_text(rec):
    """-> ['image', ...]: the content blocks of an input record that are not text (an image he pasted)."""
    c = (rec.get("message") or {}).get("content")
    if not isinstance(c, list):
        return []
    return [b.get("type") or "?" for b in c if isinstance(b, dict) and b.get("type") not in ("text", None)]


def helpers_of(path, now=None, stale_s=None):
    """-> [{id, alive, last_at}] for ALL the window's subagent transcripts (<session>/subagents/agent-*.jsonl), or None
    (UNMEASURED: no main transcript, or a helper file that cannot be read) — never aged out by mtime: a helper silent
    for days still counts until its transcript ends (GPT review 2026-10-28 HIGH 3). MEASURED 2026-10-28 on the BENCH session: a finished helper's last user/assistant record is an
    assistant turn with stop_reason end_turn; a running one ends in tool_use, a tool result or an attachment. Anything
    else (empty, unreadable) counts as ALIVE: a helper is never read as dead without proof."""
    if not path or not os.path.isfile(path):
        return None
    out = []
    base = path[:-len(".jsonl")]
    sub = os.path.join(base, "subagents")
    try:                                 # one explicit listing, used as is: glob() swallows errors (review2/3 #3),
        names = os.listdir(sub)          # and no stat guard first: a failed stat would read as "no helpers" (review4)
    except FileNotFoundError:            # no session dir or no subagents dir: the window never had a helper
        names = []
    except OSError:
        return None
    for f in sorted(os.path.join(sub, n) for n in names if n.startswith("agent-") and n.endswith(".jsonl")):
        try:
            mt = os.path.getmtime(f)
            recs = [r for r in _tail_records(f, 256 << 10) if r.get("type") in ("user", "assistant")]
        except (OSError, Malformed):     # a helper mid-write or with a bad line: inventory UNMEASURED (review2 P0-2)
            return None
        alive = not (recs and recs[-1].get("type") == "assistant" and _assistant_kind(recs[-1]) == "assistant_end")
        retired = None                   # proof of death (lesson 20261030T163434Z): an API/auth error is the last record
        if alive and recs and (recs[-1].get("isApiErrorMessage") or recs[-1].get("error")):
            retired = "API error tail (%s)" % (recs[-1].get("error") or "isApiErrorMessage")
        elif alive and now is not None and now - mt > (stale_s if stale_s is not None else DEFAULTS["helper_stale_s"]):
            retired = "transcript silent %d s" % (now - mt)   # or silent past the bound (above the 600 s subagent watchdog)
        if retired:
            alive = False
        out.append({"id": os.path.basename(f)[:-len(".jsonl")], "alive": alive, "last_at": mt,
                    **({"retired": retired} if retired else {})})
    return out


def bridge_reading(seat):
    """-> {state: MEASURED|UNMEASURED, holders: [seat...], why}. The cross-clone bridge mirror and the driver lock."""
    holders = []
    try:
        from rimflow import model
        b = model.read_shared_bridge()
        if b and b.get("holder"):
            holders.append(str(b["holder"]).upper())
    except Exception as e:  # noqa: BLE001 - an unreadable bridge holds the restart
        return {"state": "UNMEASURED", "holders": [], "why": "shared bridge: %s: %s" % (type(e).__name__, e)}
    try:
        import driver_lock
        p = driver_lock.lock_path()
        if p:
            s = driver_lock.status(p)
            if s.get("state") == "HELD":
                holders.append(str(s.get("seat") or "?").upper())
            elif s.get("state") not in ("FREE", "STALE"):
                return {"state": "UNMEASURED", "holders": holders, "why": "driver lock: %s" % s.get("state")}
    except Exception as e:  # noqa: BLE001
        return {"state": "UNMEASURED", "holders": holders, "why": "driver lock: %s: %s" % (type(e).__name__, e)}
    return {"state": "MEASURED", "holders": holders}


def game_reading(seat, clone, events_since, now, hold_s):
    """The seat's last `game` event in its own shard within hold_s -> {state, at} or None."""
    last = None
    for ev in events_since(clone, seat, _iso(now - hold_s)):
        if ev.get("event") == "game":
            last = ev
    return {"state": last.get("state"), "at": _ts(last.get("ts"))} if last else None


WORK_EVENTS = ("claim", "start", "reclaim")
WORK_LEASE = ("take", "renew")


def work_since(clone, seat, req_ts):
    """-> the work-taking events (claim / start / reclaim / lease take|renew) SEAT wrote to its own shard in CLONE from
    the request's second on, [] if the seat has no shard yet, or None (UNMEASURED: the shard cannot be read). The
    ledger stamps whole seconds, so an event in the request's own second counts: a false void never kills anything."""
    p = os.path.join(clone or "", "infrastructure", "state", "ledger", "events", "%s.jsonl" % seat)
    since = int(req_ts)
    out = []
    try:
        with open(p, "rb") as f:
            data = f.read()
    except FileNotFoundError:
        return []
    except OSError:
        return None
    for raw in data.splitlines():
        try:
            ev = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, ValueError):
            continue
        if not isinstance(ev, dict) or ev.get("seat") != seat:
            continue
        if ev.get("event") not in WORK_EVENTS and not (ev.get("event") == "lease" and ev.get("action") in WORK_LEASE):
            continue
        at = _ts(ev.get("ts"))
        if at is not None and at >= since:
            out.append(ev)
    return out


def new_work(events, ticket):
    """-> the first event in events that is NEW work after a restart request for ticket, or None. Taking, claiming or
    starting any ticket is new work; renewing a lease is new work only on a ticket other than the request's own."""
    for ev in events or []:
        if ev.get("event") == "lease":
            if ev.get("action") not in WORK_LEASE or (ev.get("action") == "renew" and ticket and ev.get("id") == ticket):
                continue
        elif ev.get("event") not in WORK_EVENTS:
            continue
        return ev
    return None


def _work_why(ev):
    return "the seat took new work after the request: %s%s %s at %s" % (
        ev.get("event"), " " + ev["action"] if ev.get("action") else "", ev.get("id"), ev.get("ts"))


def killed_reading(seat, root=None):
    """The killed record plus old_alive: is the process it names (pid + start time) still running?"""
    rec = _read_json(killed_path(seat, root))
    if rec and rec.get("old_pid"):
        rec["old_alive"] = (proc_alive(rec["old_pid"], rec["old_start"]) if rec.get("old_start") is not None
                            else doorbell._alive(int(rec["old_pid"])))
    return rec


def read_intile(seat, killed_at, root=None):
    return _read_json(intile_path(seat, killed_at, root))


def default_obs(sch, events_since, now_fn=time.time):
    cfgs = config(sch)
    return {
        "request": lambda seat: _read_json(request_path(seat)),
        "tx": lambda seat, s: tx_summary(transcript_for(s, cfgs[seat]) or ""),
        "helpers": lambda seat, s: helpers_of(transcript_for(s, cfgs[seat]), now_fn(), cfgs[seat].get("helper_stale_s")),
        "killed": killed_reading,
        "start": proc_start,
        "bridge": bridge_reading,
        "game": lambda seat: game_reading(seat, cfgs[seat].get("clone"), events_since, now_fn(),
                                          cfgs[seat]["game_hold_s"]),
        "armed": lambda seat: doorbell._read_json(doorbell.armed_path(seat)),
        "intile": lambda seat, killed_at: read_intile(seat, killed_at),
        "work": lambda seat, req_ts: work_since(cfgs[seat].get("clone"), seat, req_ts),
        # the transcript the request named (review 2 P1-4), else the one the live session resolves to
        "cursor": lambda seat, s, rs: cursor_scan(rs.get("tx_path") or transcript_for(s, cfgs[seat]), rs.get("tx_offset")),
        "last_human": lambda seat, s: last_human(transcript_for(s, cfgs[seat]) or ""),
    }


# ---------------------------------------------------------------------------------------------------------------------
# argv

def relaunch_argv(seat, cfg, why="ticket ended", gen=None):
    """The WT seat profile's own LAUNCH line (install_wt_seat_profiles.LAUNCH) as an argv, plus a first prompt so the
    fresh window ends one turn and its Stop hook arms the doorbell. gen: the restart's generation token, passed to the
    wake so it reads only the killed record of THIS restart (blind review 2 P1-5)."""
    label = cfg["session_name"]
    return [BOUNDED.format(clone=cfg["clone"]), "--dangerously-skip-permissions", "--name", label,
            "--model", cfg.get("model") or "sonnet", "--remote-control", label,
            PROMPTS[cfg.get("kind") or "doorbell"].format(seat=seat, why=why, gen=" --gen %s" % gen if gen else "")]


def fallback_argv(seat, machine=None):
    """machine.json's fleet relaunch (account_failover's launcher) narrowed to `-Seats <SEAT>`, or None."""
    if machine is None:
        machine = _read_json(MACHINE) or {}
    r = machine.get("relaunch")
    if isinstance(r, str):
        import shlex
        r = shlex.split(r)
    if not isinstance(r, list) or not r:
        return None
    out, hit = [], False
    for i, tok in enumerate(r):
        tok = str(tok)
        if i and str(r[i - 1]) == "-Seats":            # a tokenised `-Seats`, `A,B,C` (GPT review MEDIUM 9)
            out.append(seat)
            continue
        hit = hit or tok == "-Seats" or bool(re.search(r"-Seats\s+[A-Za-z0-9_,]+", tok))
        out.append(re.sub(r"-Seats\s+[A-Za-z0-9_,]+", "-Seats " + seat, tok))
    return out if hit and out[-1] != "-Seats" else None


# ---------------------------------------------------------------------------------------------------------------------
# decide (pure except the lazy reads in obs["seat_restart"])

def in_flight(st, seat, sch=None, now=None):
    """The restart owns the seat (no ring, no recover) while its state is active. With the key off (rollback) a pending
    restart is released at once; a claimed or killed one stays fenced for fence_s after its claim/kill, so a recovery
    cannot race the in-tile relaunch of the window it just lost (GPT review HIGH 7)."""
    rs = (st.get("seat_restart") or {}).get(seat) or {}
    if sch is not None and seat not in config(sch):
        at = rs.get("killed_at") or rs.get("claimed_at")
        if rs.get("state") not in OWNS or not at:
            return False
        return (now if now is not None else time.time()) - at < DEFAULTS["fence_s"]
    return rs.get("state") in OWNS


def ring_hold(st, seat, sch, now):
    """-> why the Dispatcher should not ring SEAT now, or None. A ring into a window whose restart is pending would
    start a new ticket in the context the restart is about to drop (then busy -> failed): rings wait while the
    restart is pending, for at most grace_s + ring_hold_s, so a held restart never starves the seat. Recovery is not
    gated here (C8: a pending restart never freezes a recovery)."""
    cfg = config(sch).get(seat)
    rs = (st.get("seat_restart") or {}).get(seat) or {}
    if not cfg or rs.get("state") != "pending" or rs.get("ts") is None:
        return None
    age = now - rs["ts"]
    if age >= cfg["grace_s"] + cfg["ring_hold_s"]:
        return None
    return "seat restart pending (%d s old): no ring until it ends" % age


def _find(sessions, name):
    hits = [s for s in sessions or [] if isinstance(s, dict) and SM.name_matches(s.get("name"), name)]
    return hits


def decide(sch, st, obs, now, apply, act):
    cfgs = config(sch)
    if not cfgs:
        return
    agents = obs.get("agents") or {}
    if agents.get("state") != "MEASURED":
        return
    R = st.setdefault("seat_restart", {})
    for seat, cfg in cfgs.items():
        try:
            _one(seat, cfg, R, st, obs, agents.get("sessions"), now, apply, act)
        except Exception as e:  # noqa: BLE001 - one seat's fault never stops the tick
            act(do="alarm", kind="restart:decide:" + seat, seat=seat, note=True,
                why="seat restart NOT decided for %s: %s: %s" % (seat, type(e).__name__, str(e)[:200]))


def _fail(rs, seat, cls, why, now, act):
    rs.update(state="failed", why=why, ended_at=now, cooldown_until=now + rs.get("cooldown_s", DEFAULTS["cooldown_s"]))
    act(do="alarm", kind="restart:%s:%s" % (seat, cls), seat=seat, ticket=rs.get("ticket"), note=True,
        why="seat restart of %s FAILED (%s): %s" % (seat, cls, why))


def _one(seat, cfg, R, st, obs, sessions, now, apply, act):
    ro = obs["seat_restart"]
    rs = R.get(seat) or {}
    if rs.get("alarm_pending"):          # a failure execute() met (it cannot alarm itself)
        why = rs.pop("alarm_pending")
        act(do="alarm", kind="restart:%s:execute" % seat, seat=seat, ticket=rs.get("ticket"), note=True, why=why)
    named = _find(sessions, SM.names_of(cfg))
    cur = named[0] if len(named) == 1 else None
    state = rs.get("state")

    if state not in ACTIVE:
        req = ro["request"](seat)
        if req and req.get("ts") is not None and req.get("ts") != rs.get("req_ts"):
            ts = float(req["ts"])
            new = {"source": "request", "ts": ts, "req_ts": req["ts"], "session_id": req.get("session_id"),
                   "pid": req.get("pid"), "start": req.get("start"), "ticket": req.get("ticket"), "reason": req.get("reason"), "busy": 0,
                   "cooldown_s": cfg["cooldown_s"],
                   # the cancel window opens at the input that asked for the restart (his goodbye), not at the
                   # request's own time minutes later (blind review 2026-10-29 P0-1); tx_offset is the byte cursor
                   # just past that input, so every later record is read in full, never through a tail (P0-2)
                   "cancel_after": float(req["input_ts"]) if req.get("input_ts") is not None else ts,
                   "tx_offset": req.get("tx_offset"), "tx_path": req.get("tx_path")}
            act(do="restart_request", seat=seat, ticket=req.get("ticket"), session_id=req.get("session_id"),
                req_ts=req["ts"], why="requested by %s: %s" % (seat, req.get("reason")))
            R[seat] = new
            if req.get("seat") not in (None, seat):
                return _cancel(new, seat, "request is for seat %s" % req.get("seat"), now, act)
            if now - ts > cfg["request_max_age_s"]:
                return _cancel(new, seat, "request is %d s old (stale)" % (now - ts), now, act)
            if cur is None or cur.get("sessionId") != req.get("session_id"):
                return _cancel(new, seat, "request names session %s, the seat runs %s" % (
                    req.get("session_id"), (cur or {}).get("sessionId") or "none/ambiguous"), now, act)
            new["state"] = "pending"
            rs = new
        elif cfg.get("backstop") and cur and rs.get("cooldown_until", 0) <= now and cur.get("status") == "idle":
            tx = ro["tx"](seat, cur)
            if not tx or tx.get("ctx_tokens") is None or tx["ctx_tokens"] < cfg["backstop_ctx_tokens"]:
                return
            if tx.get("last_kind") != "assistant_end" or now - (tx.get("last_at") or now) < cfg["backstop_idle_s"]:
                return
            # a window the owner talks to (the Conductor) is backstopped only after he has typed nothing for
            # backstop_human_idle_s; no readable human message -> no backstop (fail closed, never kill a conversation)
            hi = cfg.get("backstop_human_idle_s") or 0
            if hi and (tx.get("last_user_at") is None or now - tx["last_user_at"] < hi):
                return
            hs = ro["helpers"](seat, cur)
            if hs is None or any(h.get("alive") for h in hs):
                return
            born = reg_start(cur)                # the window's own registration names its birth (review4 #1)
            if born is None or ro["start"](cur.get("pid")) != born:
                return
            # bind the cursor just past his LAST input (blind review 2 P0-3), never offset 0 plus a time filter
            lh = ro["last_human"](seat, cur) if callable(ro.get("last_human")) else None
            if lh is None:
                return                           # unreadable or malformed transcript: no backstop (fail closed)
            rs = R[seat] = {"source": "backstop", "ts": now, "session_id": cur.get("sessionId"), "pid": cur.get("pid"),
                            "start": born,
                            "ticket": None, "reason": "backstop: context %d tokens >= %d, idle %d s" % (
                                tx["ctx_tokens"], cfg["backstop_ctx_tokens"], now - tx["last_at"]),
                            "busy": 0, "cooldown_s": cfg["cooldown_s"], "state": "pending",
                            # the whole transcript is scanned for a human input after the last one this read saw
                            "cancel_after": tx.get("last_user_at") or now, "tx_offset": lh[2] or 0,
                            "tx_path": transcript_for(cur, cfg)}
            act(do="restart_request", seat=seat, session_id=rs["session_id"], why=rs["reason"])
        else:
            return

    state = rs["state"]
    if state == "pending":
        return _pending(seat, cfg, rs, st, obs, ro, cur, now, act)
    if state == "claimed":
        rec = ro["killed"](seat) if ro.get("killed") else None    # a crash between the kill and the state save
        if (rec and not rec.get("aborted") and rec.get("old_alive") is False and rec.get("session_id") == rs.get("session_id")
                and (rec.get("killed_at") or 0) >= rs.get("ts", 0)):
            rs.update(state="killed", killed_at=rec["killed_at"], kill="reconciled from the killed record",
                      window_s=rec.get("window_s"))
            act(do="restart_hold", seat=seat, why="claimed restart found killed at %s (state reconciled)" % _iso(
                rec["killed_at"]))
            return
        if now - rs.get("claimed_at", now) > cfg["claimed_max_s"]:
            _fail(rs, seat, "claimed", "claimed at %s but the kill never executed" % _iso(rs["claimed_at"]), now, act)
        return
    if state == "killed":
        new = [s for s in named if s.get("sessionId") != rs.get("session_id")]
        if new:
            mk = ro["intile"](seat, rs["killed_at"])
            rs.update(state="relaunched", new_session=new[0].get("sessionId"), new_pid=new[0].get("pid"),
                      relaunched_at=now, how=(mk.get("by") or "in-tile") if mk else ("fallback" if rs.get("fallback_at") else "?"))
            act(do="restart_relaunched", seat=seat, ticket=rs.get("ticket"), session_id=rs["new_session"],
                why="new %s window (%s) %d s after the kill" % (seat, rs["how"], now - rs["killed_at"]))
            return
        since = now - rs["killed_at"]
        # the give-up deadline never falls inside the tile window written at the kill, even if the config shrank (review6)
        deadline = max(cfg["intile_wait_s"] + cfg["verify_s"], rs.get("window_s") or 0)
        if not rs.get("fallback_at") and since >= cfg["intile_wait_s"] and not ro["intile"](seat, rs["killed_at"]):
            argv = fallback_argv(seat, cfg.get("machine"))
            if not argv:                 # fail only at the deadline: until then a tile may still claim (review5 #1)
                if since >= deadline:
                    return _fail(rs, seat, "relaunch", "no in-tile relaunch and no fleet launcher to fall back on",
                                 now, act)
                return
            rs["fallback_at"] = now
            act(do="restart_fallback", seat=seat, argv=argv, killed_at=rs["killed_at"],
                why="no in-tile relaunch %d s after the kill: opening a new %s tile" % (since, seat))
            return
        if since >= deadline:
            _fail(rs, seat, "relaunch", "no new %r window %d s after the kill" % (cfg["session_name"], since), now,
                  act)
        return
    if state == "relaunched" and cfg.get("kind") == "conductor":
        # no doorbell: the fresh window proves itself by ending its first turn (its wake read) after the kill
        mine = [s for s in named if s.get("sessionId") == rs.get("new_session")]
        tx = ro["tx"](seat, mine[0]) if mine else None
        if tx and tx.get("last_kind") == "assistant_end" and (tx.get("last_at") or 0) >= rs.get("killed_at", 0):
            rs.update(state="verified", ended_at=now, cooldown_until=now + cfg["cooldown_s"])
            act(do="restart_verified", seat=seat, ticket=rs.get("ticket"), note=True,
                evidence="fresh %s window %s (pid %s) ended its first turn at %s" % (
                    seat, rs["new_session"], rs.get("new_pid"), _iso(tx["last_at"])))
        elif now - rs["relaunched_at"] >= cfg["arm_s"]:
            _fail(rs, seat, "firstturn", "the new window %s never ended its first turn in %d s" % (
                rs.get("new_session"), cfg["arm_s"]), now, act)
        return
    if state == "relaunched":
        armed = ro["armed"](seat) or {}
        if armed.get("session_id") and armed.get("session_id") == rs.get("new_session"):
            rs.update(state="verified", ended_at=now, cooldown_until=now + cfg["cooldown_s"])
            act(do="restart_verified", seat=seat, ticket=rs.get("ticket"), note=True,
                evidence="fresh %s window %s (pid %s), doorbell armed at %s" % (
                    seat, rs["new_session"], rs.get("new_pid"), armed.get("armed_at")))
        elif now - rs["relaunched_at"] >= cfg["arm_s"]:
            _fail(rs, seat, "rearm", "the new window %s never armed its doorbell in %d s" % (
                rs.get("new_session"), cfg["arm_s"]), now, act)


def cursor_verdict(cfg, rs, sc, now, track=True):
    """Judge one full read of the window's transcript from rs's byte cursor (cursor_scan's dict, or None).
    -> ("cancel", why) | ("hold", why) | ("ok", None).

    The Conductor rule (blind review 2 2026-10-29 P0-1, simplified on the coordinator's direction): after his goodbye
    the window is restarted only once its transcript has been QUIET for goodbye_quiet_s (600 s) with every record
    parsed cleanly, and ANY input at all since the goodbye cancels — his, a ring, a task notification, a peer; a
    malformed record cancels; a torn last record holds. Quiet is judged on two clocks: the newest record timestamp
    after the cursor, and the Dispatcher's own clock since it last saw the file grow (rs seen_size / quiet_since, so a
    transcript clock that runs backwards cannot shorten it, review 2 P0-3). That turns the final-fence race into a
    ten-minute margin. The owner's machine idle clock is never read (owner 2026-10-30: "I really, really need you to
    strip "when I come back to the machine" as an event for anything changing."; and 2026-10-29: "If I'm typing at
    the same time it's an acceptable risk.").
    A doorbell seat keeps the old rule: only his input cancels; no cursor -> its tail check alone."""
    conductor = cfg.get("kind") == "conductor"
    off = rs.get("tx_offset")
    if off is None:
        return ("hold", "no transcript cursor on a Conductor restart (cannot prove nothing came after the goodbye)") \
            if conductor else ("ok", None)
    if sc is None:
        return "hold", "transcript cursor scan UNMEASURED (unreadable, missing, or shorter than the cursor)"
    if sc.get("human"):
        r = sc["human"][-1]
        return "cancel", "new input in the window at %s, after the cursor (cursor scan): %s" % (
            _iso(_ts(r.get("timestamp"))), _text(r)[:80])
    if conductor and sc.get("inputs"):
        r = sc["inputs"][-1]
        return "cancel", "input after the goodbye (any input cancels a Conductor restart): %s %s" % (
            r.get("type"), (_text(r) or str(r.get("content") or ""))[:80])
    if sc.get("malformed"):
        return "cancel", "malformed transcript record after the cursor (%s): fail closed" % sc["malformed"]
    if sc.get("torn"):
        return "hold", "transcript record being written (%s)" % sc["torn"]
    if not conductor:
        return "ok", None
    q = cfg.get("goodbye_quiet_s") or 0
    since = rs.get("quiet_since")
    if track and (since is None or sc.get("size") != rs.get("seen_size")):
        since = rs["quiet_since"] = now if since is not None else rs.get("cancel_after", rs.get("ts", now))
        rs["seen_size"] = sc.get("size")
    elif not track and sc.get("size") != rs.get("seen_size"):
        return "hold", "the transcript grew since the last tick (%s -> %s bytes)" % (rs.get("seen_size"), sc.get("size"))
    anchor = max(rs.get("cancel_after", rs.get("ts", now)), sc.get("last_at") or 0, since if since is not None else now)
    if now - anchor < q:
        return "hold", "quiet window: %d s left of goodbye_quiet_s %d (last activity %s)" % (
            q - (now - anchor), q, _iso(anchor))
    return "ok", None


def _cancel(rs, seat, why, now, act):
    rs.update(state="cancelled", why=why, ended_at=now)
    act(do="restart_cancel", seat=seat, ticket=rs.get("ticket"), why=why)


def _pending(seat, cfg, rs, st, obs, ro, cur, now, act):
    if cur is None or cur.get("sessionId") != rs.get("session_id"):
        return _cancel(rs, seat, "the window's session changed or is gone (%s)" % ((cur or {}).get("sessionId")), now,
                       act)
    tx = ro["tx"](seat, cur)
    after = rs.get("cancel_after", rs["ts"])
    if tx and tx.get("last_user_at") and tx["last_user_at"] > after:
        return _cancel(rs, seat, "new input in the window at %s, after the request" % _iso(tx["last_user_at"]), now,
                       act)
    sc = None
    if rs.get("tx_offset") is not None:
        try:
            sc = ro["cursor"](seat, cur, rs) if callable(ro.get("cursor")) else None
        except Exception:  # noqa: BLE001 - an unreadable transcript holds (cursor_verdict: sc None)
            sc = None
    verdict, cursor_why = cursor_verdict(cfg, rs, sc, now)
    if verdict == "cancel":
        return _cancel(rs, seat, cursor_why, now, act)
    cursor_hold = cursor_why if verdict == "hold" else None
    # SEAT_RESTART_FIX_KILL_AFTER_NEW_WORK (Codex review 2026-10-29 P1 1): machine input no longer cancels (0cf054ade8),
    # so a seat that took a ticket after its request and then idled on external input would be killed mid-ticket.
    # Its own ledger says so: any claim/start/lease take after the request voids it. Unreadable -> held below.
    work = ro["work"](seat, rs["ts"]) if ro.get("work") else None
    nw = new_work(work, rs.get("ticket"))
    if nw:
        return _cancel(rs, seat, _work_why(nw), now, act)
    if now - rs["ts"] < cfg["grace_s"]:
        act(do="restart_hold", seat=seat, why="grace: %d s left" % (cfg["grace_s"] - (now - rs["ts"])))
        return
    holds = [cursor_hold] if cursor_hold else []
    hs = ro["helpers"](seat, cur)
    live = [h for h in hs or [] if h.get("alive")]
    if hs is None:
        holds.append("helper inventory UNMEASURED (transcript or a subagent file unreadable)")
    if live:
        holds.append("helper(s) alive: %s" % ", ".join(h["id"] for h in live))
        stale = [h for h in live if now - (h.get("last_at") or now) > cfg["helper_stale_s"]]
        if stale:
            act(do="alarm", kind="restart:%s:helper_stale" % seat, seat=seat, note=True,
                why="helper(s) of %s look alive but silent > %d s: %s (held, never read as dead)" % (
                    seat, cfg["helper_stale_s"], ", ".join(h["id"] for h in stale)))
    if work is None:
        holds.append("the seat's ledger shard is UNMEASURED (cannot tell whether it took new work)")
    br = ro["bridge"](seat) or {}
    if br.get("state") != "MEASURED":
        holds.append("bridge unreadable (%s)" % br.get("why"))
    elif seat in (br.get("holders") or []):
        holds.append("bridge/driver lock held by %s" % seat)
    g = ro["game"](seat)
    if g and g.get("state") in TRANSITIONAL and now - (g.get("at") or now) < cfg["game_hold_s"]:
        holds.append("game action by %s: %s" % (seat, g["state"]))
    if obs.get("paused"):
        holds.append("PAUSE: %s" % obs["paused"])
    ss = (st.get("seats") or {}).get(seat) or {}
    if ss.get("ring"):
        holds.append("doorbell ring in flight")
    if ss.get("recover"):
        holds.append("Dispatcher recovery in flight")
    if holds:
        rs.setdefault("held_since", now)
        if now - rs["held_since"] >= cfg["hold_alarm_s"]:
            act(do="alarm", kind="restart:%s:held" % seat, seat=seat, ticket=rs.get("ticket"), note=True,
                why="seat restart of %s held %d s: %s" % (seat, now - rs["held_since"], "; ".join(holds)))
        act(do="restart_hold", seat=seat, why="; ".join(holds))
        return
    rs.pop("held_since", None)
    quiet = (cur.get("status") == "idle" and tx and tx.get("last_kind") == "assistant_end"
             and now - (tx.get("last_at") or now) >= cfg["quiet_s"])
    if not quiet:
        rs["busy"] = rs.get("busy", 0) + 1
        why = "window not quiet (status %s, last record %s) %d/%d" % (
            cur.get("status"), (tx or {}).get("last_kind", "unreadable"), rs["busy"], cfg["busy_ticks"])
        if rs["busy"] >= cfg["busy_ticks"]:
            return _fail(rs, seat, "busy", why, now, act)
        act(do="restart_hold", seat=seat, why=why)
        return
    if rs.get("pid") is not None and cur.get("pid") != rs["pid"]:
        return _cancel(rs, seat, "the window's pid %s is not the requester's %s" % (cur.get("pid"), rs["pid"]), now,
                       act)
    rs.update(state="claimed", claimed_at=now, pid=cur.get("pid"), gen=rs.get("gen") or uuid.uuid4().hex[:12])
    act(do="restart_kill", seat=seat, pid=cur.get("pid"), session_id=rs["session_id"],
        session_name=cfg["session_name"], session_names=SM.names_of(cfg), ticket=rs.get("ticket"), gen=rs["gen"],
        argv=relaunch_argv(seat, cfg, rs.get("reason") or "ticket ended", rs["gen"]),
        why="%s: grace over, nothing held, window quiet" % rs.get("source"))


# ---------------------------------------------------------------------------------------------------------------------
# execute

def _proc_stat(pid):
    """-> (state letter, start time in clock ticks) from /proc/<pid>/stat, or None."""
    try:
        with open("/proc/%d/stat" % int(pid)) as f:
            rest = f.read().rsplit(")", 1)[1].split()
        return rest[0], int(rest[19])
    except (OSError, ValueError, IndexError, TypeError):
        return None


def proc_start(pid):
    s = _proc_stat(pid)
    return s[1] if s and s[0] != "Z" else None


def reg_start(sf):
    """-> the /proc start time Claude Code wrote into sessions/<pid>.json (procStart, same clock ticks as proc_start),
    or None. It is the session's own birth record, so a pid reused by another process never matches it."""
    try:
        return int((sf or {}).get("procStart"))
    except (TypeError, ValueError):
        return None


def proc_alive(pid, start):
    """The SAME process (pid + start time) is still running (a zombie counts as gone)."""
    return start is not None and proc_start(pid) == start


def kill_pid(pid, wait_s=10, start=None):
    """SIGTERM, then SIGKILL after wait_s, each only while pid still has the start time seen at the check (no PID
    reuse kill), then death confirmed. -> how it ended: SIGTERM | SIGKILL | already gone | refused: .. | survived: .."""
    if start is None:
        start = proc_start(pid)
        if start is None:
            return "already gone"
    try:                                 # pin the process first: a pidfd cannot be re-pointed by PID reuse (review2 #4)
        pfd = os.pidfd_open(pid)
    except ProcessLookupError:
        return "already gone"
    try:
        if proc_start(pid) != start:     # checked AFTER the pin, so the pinned process is the one with this start time
            return ("refused: pid %s now has start %s, not %s (reused)" % (pid, proc_start(pid), start)
                    if proc_start(pid) is not None else "already gone")
        return _signal_pinned(pfd, pid, start, wait_s)
    finally:
        os.close(pfd)


def _signal_pinned(pfd, pid, start, wait_s):
    try:
        signal.pidfd_send_signal(pfd, signal.SIGTERM)
    except ProcessLookupError:
        return "already gone"
    for sig, label in ((None, "SIGTERM"), (signal.SIGKILL, "SIGKILL")):
        if sig is not None:
            if not proc_alive(pid, start):
                return "SIGTERM (late)"
            try:
                signal.pidfd_send_signal(pfd, sig)
            except ProcessLookupError:
                return "SIGTERM (late)"
        end = time.time() + (wait_s if sig is None else 5)
        while time.time() < end:
            if not proc_alive(pid, start):
                return label
            time.sleep(0.2)
    return "survived: pid %s still alive after SIGKILL" % pid


def write_killed(seat, rec, root=None):
    _write_json(killed_path(seat, root), rec)


def consume_request(seat, root=None, ts=None):
    """Move the request to done/ — only if it is still the one decided on (ts) when read here (MEDIUM 10). The check
    and the move are not atomic: a request written between them is taken unread (accepted, golive §10 known limits;
    nothing is killed for it)."""
    p = request_path(seat, root)
    if ts is not None and ((_read_json(p) or {}).get("ts") != ts):
        return
    if os.path.exists(p):
        d = os.path.join(restart_dir(root), "done")
        os.makedirs(d, exist_ok=True)
        os.replace(p, os.path.join(d, "%s-%d.request.json" % (seat, int(time.time()))))


def run_fallback(argv):
    env = {k: v for k, v in os.environ.items() if k not in ("AGENT_SEAT", "RIMFLOW_SEAT", "CLAUDE_CODE_SESSION_ID")}
    r = subprocess.run(argv, env=env, cwd=os.path.expanduser("~"), capture_output=True, text=True, timeout=180)
    return "rc=%d %s" % (r.returncode, (r.stderr or r.stdout).strip()[-200:])


def execute(a, sch, st, apply, now, fx=None):
    """Carry out one restart_* action. -> result text. Dry run: nothing is killed, launched or consumed."""
    fx = fx or {}
    seat = a["seat"]
    rs = (st.get("seat_restart") or {}).get(seat) or {}
    if a["do"] == "restart_request":
        if not apply:
            return "would take the request"
        fx.get("consume", consume_request)(seat, ts=a.get("req_ts"))
        return "request taken"
    if a["do"] == "restart_fallback":
        if not apply:
            return "would run %s" % " ".join(a["argv"])
        root = fx.get("root")
        rec = _read_json(killed_path(seat, root)) or {}
        if rec.get("old_pid") and fx.get("alive", lambda p: old_alive(rec))(int(rec["old_pid"])):
            return "skipped: the killed window's pid %s is still alive" % rec["old_pid"]
        try:                             # the same O_EXCL election as the tile (GPT review HIGH 5): one launch per kill
            fd = os.open(intile_path(seat, a.get("killed_at") or rec.get("killed_at"), root),
                         os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        except FileExistsError:
            return "skipped: the relaunch is already claimed (in-tile)"
        with os.fdopen(fd, "w") as f:
            json.dump({"seat": seat, "at": now, "killed_at": a.get("killed_at"), "by": "fallback"}, f)
        try:
            return fx.get("fallback", run_fallback)(a["argv"])
        except Exception as e:  # noqa: BLE001
            return "fallback failed: %s: %s" % (type(e).__name__, str(e)[:160])
    if a["do"] != "restart_kill":
        return None
    if seat not in config(sch):          # a seat switched off is never killed, whatever action reaches here (review 3)
        rs.update(state="cancelled", why="seat_restart is off for %s: kill refused" % seat, ended_at=now)
        rs.pop("claimed_at", None)
        return "refused: seat_restart is off for %s (nothing killed)" % seat
    if rs.get("state") != "claimed":
        return "skipped: restart state is %s" % rs.get("state")
    if not apply:
        rs.update(state="dry", ended_at=now, why="dry run")
        return "would SIGTERM pid %s (%s) and relaunch in-tile: %s" % (a["pid"], a["session_id"], a["argv"][:-1])
    sf = fx.get("session_file", session_file)(a["pid"]) or {}
    if sf.get("sessionId") != a["session_id"] or not SM.name_matches(sf.get("name"), a.get("session_names") or a["session_name"]):
        why = "sessions/%s.json names %s/%r, not %s/%r: nothing killed" % (
            a["pid"], sf.get("sessionId"), sf.get("name"), a["session_id"], a["session_name"])
        rs.update(state="failed", why=why, ended_at=now, alarm_pending="seat restart of %s refused: %s" % (seat, why),
                  cooldown_until=now + rs.get("cooldown_s", DEFAULTS["cooldown_s"]))
        return "refused: " + why
    # the re-check right before the kill (conductor B3.3; GPT review HIGH 1): status must SAY idle, and the transcript,
    # helpers and bridge are read again — anything off puts it back to pending, where decide() re-judges next tick
    holds = [] if sf.get("status") == "idle" else ["the window's status is %s" % sf.get("status")]
    holds = holds or fx.get("recheck", recheck_at_kill)(seat, sch, rs, sf)
    if holds:
        rs.update(state="pending", busy=rs.get("busy", 0) + 1)
        rs.pop("claimed_at", None)
        return "held at the kill: %s" % "; ".join(holds)
    start = fx.get("start", proc_start)(a["pid"])
    if start is not None and start != rs.get("start"):   # birth identity bound at the request (review3 #1)
        why = "pid %s has start %s, not the %s seen when the restart was asked for (reused, or unbound)" % (
            a["pid"], start, rs.get("start"))
        rs.update(state="failed", why=why, ended_at=now, alarm_pending="seat restart of %s refused: %s" % (seat, why),
                  cooldown_until=now + rs.get("cooldown_s", DEFAULTS["cooldown_s"]))
        return "refused: " + why
    if start is None:
        rs.update(state="failed", why="pid %s gone before the kill" % a["pid"], ended_at=now,
                  alarm_pending="seat restart of %s: pid %s vanished before the kill (no relaunch)" % (seat, a["pid"]),
                  cooldown_until=now + rs.get("cooldown_s", DEFAULTS["cooldown_s"]))
        return "refused: pid %s gone before the kill" % a["pid"]
    wall = time.time()      # the tile's window starts at the real kill, not the tick's start (GPT review P1)
    kt = max(now, wall) if abs(wall - now) < 600 else now
    rec = {"seat": seat, "old_pid": a["pid"], "old_start": start, "session_id": a["session_id"], "killed_at": kt,
           "argv": a["argv"], "ticket": a.get("ticket"), "req_ts": rs.get("ts"),
           "input_ts": rs.get("cancel_after"), "tx_offset": rs.get("tx_offset"),   # the wake reads on from here (P1-5)
           # the transcript the request named (review 2 P1-4) and this restart's generation, which only the relaunch
           # prompt carries: the wake reads this record only for that token, and only once (review 2 P1-5)
           "tx_path": rs.get("tx_path"), "gen": a.get("gen") or rs.get("gen"),
           "window_s": config(sch).get(seat, DEFAULTS)["intile_window_s"]}   # the tile obeys decide()'s deadline (review4 #2)
    fx.get("write_killed", write_killed)(seat, rec)
    # the final fence (blind review 2026-10-29 P0-3; review 2 P0-1): the killed record is on disk, so anything the old
    # window accepts from here on is still recovered by the new window's wake (it reads from the record's cursor). In
    # this order, each read AFTER the one before: the transcript from the cursor (it must not have grown since the
    # tick that claimed), and last the window's status. A Conductor got here only
    # after goodbye_quiet_s of transcript silence (cursor_verdict), so the gap left between the status read and the
    # signal (milliseconds) needs him to submit within it after ten silent minutes: a margin, not a proof (no Claude
    # Code API admits input atomically against a kill).
    late = fx.get("final", final_fence)(seat, sch, rs, sf)
    if not late:
        sf2 = fx.get("session_file", session_file)(a["pid"]) or {}
        if sf2.get("status") != "idle":
            late = ["the window's status is %s at the fence" % sf2.get("status")]
    if late:
        fx.get("write_killed", write_killed)(seat, dict(rec, aborted="final fence: " + "; ".join(late)))
        rs.update(state="pending", busy=rs.get("busy", 0) + 1)
        rs.pop("claimed_at", None)
        return "held at the final fence: %s" % "; ".join(late)
    how = fx.get("kill", kill_pid)(a["pid"], start=start)
    if how.startswith(("refused", "survived")):     # never relaunch beside a window that may still be there
        fx.get("write_killed", write_killed)(seat, dict(rec, aborted=how))
        rs.update(state="failed", why=how, ended_at=now, alarm_pending="seat restart of %s: %s" % (seat, how),
                  cooldown_until=now + rs.get("cooldown_s", DEFAULTS["cooldown_s"]))
        return "refused: " + how
    rs.update(state="killed", killed_at=kt, kill=how, window_s=rec["window_s"])
    return "killed pid %s (%s)" % (a["pid"], how)


def final_fence(seat, sch, rs, sf, path=None, now=None):
    """-> holds from a full read of the window's transcript from rs's cursor (cursor_verdict without moving the quiet
    clock: any growth since the claiming tick holds). [] = go. A seat without a cursor and not a Conductor passes (its tail check
    stands)."""
    cfg = config(sch).get(seat) or dict(DEFAULTS)
    if path is None:
        path = rs.get("tx_path") or transcript_for(sf, cfg)
    sc = cursor_scan(path, rs.get("tx_offset")) if rs.get("tx_offset") is not None else None
    verdict, why = cursor_verdict(cfg, rs, sc, time.time() if now is None else now, track=False)
    if verdict != "ok":
        return ["%s at the fence: %s" % (verdict, why)]
    return []


def paused_now():
    """state/PAUSE (the Dispatcher's stop-everything file): its reason, or None."""
    p = os.path.join(doorbell.state_dir(), "PAUSE")
    if not os.path.exists(p):
        return None
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            return f.read().strip() or "paused"
    except OSError as e:
        return "PAUSE unreadable: %s" % e


def recheck_at_kill(seat, sch, rs, sf, paused=paused_now, work=None):
    """-> the holds found by reading transcript, helpers, bridge and PAUSE again at the kill
    (empty = go). Between this and the signal there is no barrier: that gap is one /proc start read, the killed-record
    write, the pidfd open and its start re-check (milliseconds)."""
    cfg = config(sch).get(seat) or dict(DEFAULTS)
    path = transcript_for(sf, cfg)
    tx = tx_summary(path or "")
    holds = []
    if not tx:
        holds.append("transcript unreadable")
    elif (tx.get("last_user_at") or 0) > rs.get("cancel_after", rs.get("ts", 0)):
        holds.append("new input at %s" % _iso(tx["last_user_at"]))
    elif tx.get("last_kind") != "assistant_end":
        holds.append("turn not ended (%s)" % tx.get("last_kind"))
    elif tx.get("last_at") is None:
        holds.append("last record time unknown")
    elif time.time() - tx["last_at"] < cfg["quiet_s"]:
        holds.append("not quiet: last record %.0f s ago < quiet_s %d" % (time.time() - tx["last_at"], cfg["quiet_s"]))
    holds += final_fence(seat, sch, rs, sf, path=rs.get("tx_path") or path)
    hs = helpers_of(path, time.time())
    if hs is None:
        holds.append("helper inventory UNMEASURED")
    elif any(h.get("alive") for h in hs):
        holds.append("helper(s) alive: %s" % ", ".join(h["id"] for h in hs if h.get("alive")))
    br = bridge_reading(seat)
    if br.get("state") != "MEASURED" or seat in (br.get("holders") or []):
        holds.append("bridge %s" % (br.get("why") or "held by %s" % seat))
    pz = paused()
    if pz:
        holds.append("PAUSE: %s" % pz)
    evs = (work or (lambda s_, ts: work_since(cfg.get("clone"), s_, ts)))(seat, rs.get("ts", 0))
    if evs is None:
        holds.append("ledger shard UNMEASURED")
    else:
        nw = new_work(evs, rs.get("ticket"))
        if nw:
            holds.append(_work_why(nw))
    return holds


# ---------------------------------------------------------------------------------------------------------------------
# the tile side (seat_loop.sh) and the seat side (request, wake)

def old_alive(rec):
    """Is the killed record's old window still there? pid AND birth time when recorded (review5: a reused pid is not
    the old window); pid alone for a record without old_start."""
    pid = int(rec["old_pid"])
    return proc_alive(pid, rec["old_start"]) if rec.get("old_start") is not None else doorbell._alive(pid)


def intile_claim(seat, now, alive=None, root=None, window_s=DEFAULTS["intile_window_s"]):
    """-> the relaunch argv if this seat's window was just killed by a restart and no tile has claimed it; else None.
    The claim is an O_EXCL marker per kill, so exactly one relaunch happens."""
    rec = _read_json(killed_path(seat, root))
    if not rec or rec.get("aborted") or not isinstance(rec.get("argv"), list) or not rec.get("killed_at"):
        return None
    if rec.get("window_s") is not None:
        window_s = min(window_s, rec["window_s"])
    if now - rec["killed_at"] >= window_s or now < rec["killed_at"] - 5:
        return None
    if rec.get("old_pid") and (alive(int(rec["old_pid"])) if alive else old_alive(rec)):
        return None
    p = intile_path(seat, rec["killed_at"], root)
    try:
        fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError:
        return None
    with os.fdopen(fd, "w") as f:
        json.dump({"seat": seat, "at": now, "killed_at": rec["killed_at"], "by_pid": os.getpid()}, f)
    return rec["argv"]


def check_request(seat, sf, helpers):
    """Seat-side gate: the calling window must be the seat's window, and no helper of it may be alive."""
    if not sf or not sf.get("sessionId"):
        return False, "no ~/.claude/sessions/<pid>.json for the calling window"
    names = SM.seat_names(seat)
    if not SM.name_matches(sf.get("name"), names):
        return False, "this window is %r, not %s" % (sf.get("name"), " / ".join("'%s'" % n for n in names))
    if helpers is None:
        return False, "helper inventory UNMEASURED (transcript or a subagent file unreadable)"
    live = [h["id"] for h in helpers if h.get("alive")]
    if live:
        return False, "helper(s) still alive: %s: wait for them (or stop them) before the close-out" % ", ".join(live)
    ret = ["%s (%s)" % (h["id"], h["retired"]) for h in helpers if h.get("retired")]
    return True, ("ok; retired dead helper(s): %s" % ", ".join(ret)) if ret else "ok"


def unpublished_shard(seat, clone):
    """-> None, or why the seat's ledger shard in `clone` is not on origin (uncommitted lines or commits not on origin/main),
    or "UNMEASURED: ..." when git cannot say.
    A close-out that ends with the shard only in the clone hides every event of the window from every other seat:
    17 FOUNDRY events sat so for 3 h on 2026-10-28 (V3_CUTOVER_MIGRATE_BENCH_LANE_TO_FOUNDRY). UNMEASURED -> None."""
    rel = "infrastructure/state/ledger/events/%s.jsonl" % seat
    try:
        dirty = subprocess.run(["git", "status", "--porcelain", "--", rel], cwd=clone, capture_output=True,
                               text=True, timeout=60)
        # ./publish pushes to origin main, so that is the publication ref (not whatever @{u} happens to be)
        ahead = subprocess.run(["git", "log", "--oneline", "origin/main..HEAD", "--", rel], cwd=clone,
                               capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError) as e:
        return "UNMEASURED: git failed (%s)" % e
    if dirty.returncode != 0 or ahead.returncode != 0:
        return "UNMEASURED: %s" % ((dirty.stderr or ahead.stderr).strip().splitlines() or ["git error"])[0]
    if dirty.stdout.strip():
        return "%s has uncommitted lines" % rel
    if ahead.stdout.strip():
        return "%s has %d commit(s) not pushed" % (rel, len(ahead.stdout.strip().splitlines()))
    return None


def append_seat_log(seat, ticket, note, now=None, cfg=None):
    lines = [x.rstrip() for x in (note or "").strip().splitlines() if x.strip()]
    if not lines:
        return None
    p = seat_log_path(seat, cfg)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write("\n## %s %s\n%s\n" % (_iso(now or time.time()), ticket or "-", "\n".join(lines[:8])))
    return p


def _schedule():
    try:
        with open(os.path.join(HERE, "dispatcher_schedule.json"), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def cmd_request(args):
    seat = (args.seat or doorbell.seat_name() or "").upper()
    if not seat:
        print("seat_restart: no seat (--seat or AGENT_SEAT)")
        return 2
    unpub = unpublished_shard(seat, REPO)
    if unpub and unpub.startswith("UNMEASURED"):    # fail closed (blind review 2026-10-29 P1-4)
        print("seat_restart: REFUSED: could not tell whether your ledger shard is published (%s). Run `git status "
              "infrastructure/state/ledger/events/%s.jsonl` and `./publish`, then request again." % (unpub, seat))
        return 3
    elif unpub:
        print("seat_restart: REFUSED: %s. Close-out step 1: commit it by explicit path, then ./publish, then request "
              "again (ledger-only tickets too)." % unpub)
        return 3
    cfgs = config(_schedule())
    logged = append_seat_log(seat, args.ticket, args.note, cfg=cfgs.get(seat))
    if logged:
        print("seat log: appended to %s" % logged)
    if seat not in cfgs:
        print("seat_restart is not enabled for %s (dispatcher_schedule.json seat_restart): no restart requested. "
              "Carry on in this window." % seat)
        return 0
    pid = args.pid or doorbell.claude_ancestor()
    sf = session_file(pid) if pid else None
    path = transcript_path(sf["cwd"], sf["sessionId"]) if sf and sf.get("cwd") and sf.get("sessionId") else None
    ok, why = check_request(seat, sf, helpers_of(path, time.time()))
    if not ok:
        print("seat_restart: REFUSED: %s" % why)
        return 3
    born = reg_start(sf)
    if born is None or proc_start(pid) != born:
        print("seat_restart: REFUSED: pid %s is not the process its session file registered (procStart %s, live %s)"
              % (pid, sf.get("procStart"), proc_start(pid)))
        return 3
    cfg = cfgs[seat]
    # FOUNDRY_IDLE_DIAGNOSE_CAP_STARVES_TRIAGE (owner 2026-10-28: "we should let Foundry do more than one if it's
    # context is ok"): under the backstop threshold the window keeps going on its next ticket itself — no request, no
    # ring spent. Over it, UNMEASURED, or --fresh: the fresh window.
    tx = tx_summary(path) if path else None
    ctx = (tx or {}).get("ctx_tokens")
    limit = cfg["backstop_ctx_tokens"]
    if not args.fresh and ctx is not None and ctx < limit:
        print("CONTEXT OK for %s: %d tokens < %d (backstop_ctx_tokens). No restart requested. Do NOT end the turn: "
              "run `python3 src/RimMandrake/rimflow/cli.py next --seat %s` and work the item it gives you, "
              "with the same close-out after it. Waiting on a lane job, a test result or a helper is NOT idle: take the "
              "next item and read those results between items. Only an empty queue ends the turn; if `next` gives you "
              "nothing workable, say why in a `rimflow note` before you end it." % (seat, ctx, limit, seat))
        return 0
    # bind the request to the input that asked for it (blind review 2026-10-29 P0-1): the cancel window opens at his
    # goodbye, and a byte cursor just past it lets the Dispatcher read every later record in full (P0-2)
    lh = last_human(path) if path else None
    if lh is None and cfg.get("kind") == "conductor":
        print("seat_restart: REFUSED: the window's transcript %s is unreadable (cannot bind the request to his last "
              "message)." % path)
        return 3
    in_ts, in_rec, in_end, size = lh or (None, None, None, None)   # a doorbell seat keeps its tail check alone
    if cfg.get("kind") == "conductor":
        import goodbye_phrase as GP
        if in_rec is None or not GP.is_goodbye(_text(in_rec), GP.phrases(cfg)):
            print("seat_restart: REFUSED: his last message (%s) is not the goodbye: %r. He wrote after the goodbye: "
                  "answer him; this window stays open." % (_iso(in_ts), _text(in_rec or {})[:160]))
            return 3
        cursor = in_end
    else:
        cursor = size                 # a doorbell seat: everything after the request time, from here on
    req = {"seat": seat, "pid": pid, "start": born, "session_id": sf["sessionId"], "ticket": args.ticket,
           "reason": args.reason, "ts": time.time(), "ctx_tokens": ctx,
           "input_ts": in_ts if cfg.get("kind") == "conductor" else None, "tx_offset": cursor,
           "tx_path": path}             # the transcript actually read, carried to the kill and the wake (review 2 P1-4)
    _write_json(request_path(seat), req)
    wait = ("once this window has been quiet for %d s (goodbye_quiet_s) and nothing holds it. End your turn now; ANY "
            "new input cancels it" % cfg["goodbye_quiet_s"]) if cfg.get("kind") == "conductor" else (
            "after a %d s grace once this turn has ended and nothing holds it. End your turn now; a new prompt from "
            "the owner cancels it" % cfg["grace_s"])
    print("RESTART REQUESTED for %s (%s; context %s tokens, backstop %d%s). The Dispatcher acts %s."
          % (seat, sf["sessionId"], "UNMEASURED" if ctx is None else ctx, limit, ", --fresh" if args.fresh else "",
             wait))
    return 0


def _wake_conductor(seat, cfg, rec, gen=None, root=None):
    """The Conductor's wake read after a goodbye restart: EVERY message he sent the old window after his goodbye, read
    in full from the killed record's byte cursor in the transcript the record names (review 1 P1-5; review 2 P1-4).
    Bound to ONE restart (review 2 P1-5): the record is read only when its generation token is the `--gen` the
    relaunch prompt passed, it was not aborted, and no earlier wake consumed it; after a full read it is marked woken,
    so a later window never replays it."""
    if not rec:
        print("\n== no restart record: this window was not made by a goodbye restart (a fleet launch or boot).")
        return
    if rec.get("aborted"):
        print("\n== no restart record: the last restart (%s) was ABORTED before any kill (%s); the old window was "
              "never killed, so there is nothing to recover." % (rec.get("gen") or "?", str(rec["aborted"])[:160]))
        return
    if not gen or rec.get("gen") != gen:
        print("\n== no restart record for this window: the killed record is restart %s, this window was given %s. It is "
              "NOT replayed (it may be an older restart's, already answered). If the fleet launcher opened this window "
              "right after a goodbye restart, the owner's messages are in %s after byte %s." % (
                  rec.get("gen") or "(none)", gen or "no --gen", rec.get("tx_path") or "?", rec.get("tx_offset")))
        return
    if rec.get("woken_at"):
        print("\n== restart %s was already recovered by a wake at %s: not replayed." % (gen, _iso(rec["woken_at"])))
        return
    path = rec.get("tx_path")
    off = rec.get("tx_offset")
    since = rec.get("input_ts") or rec.get("req_ts") or rec.get("killed_at") or 0
    print("\n== his messages to the old window %s after his goodbye at %s (read in full from byte %s of %s):" % (
        rec.get("session_id"), _iso(since), off, path))
    msgs = human_since_offset(path, off) if path and off is not None else None
    if msgs is None:
        print("UNMEASURED: the old transcript %s is unreadable, shorter than the cursor, has a malformed record, or "
              "the killed record names no transcript/cursor. Say so to him in one line; ask whether he sent anything "
              "after his goodbye." % path)
        return                           # not consumed: a later read may still recover them
    if not msgs:
        print("(none)")
    else:
        for r in msgs:
            extra = _non_text(r)
            print("- %s [record %s]%s:\n%s" % (
                _iso(_ts(r.get("timestamp"))), r.get("uuid") or "?",
                " (+ %s: open the record in the transcript to see it)" % ", ".join(extra) if extra else "",
                _text(r).strip() or "(no text)"))
        print("Answer these FIRST, before anything else.")
    write_killed(seat, dict(rec, woken_at=time.time()), root)


def cmd_wake(args):
    seat = (args.seat or doorbell.seat_name() or "").upper()
    cfg = config(_schedule()).get(seat) or {}
    p = seat_log_path(seat, cfg)
    print("== seat log tail: %s" % p)
    try:
        with open(p, encoding="utf-8") as f:
            print("".join(f.readlines()[-args.lines:]).rstrip() or "(empty)")
    except OSError:
        print("(no seat log yet)")
    rec = _read_json(killed_path(seat)) or {}
    if rec:
        print("\n== the restart that made this window: killed %s at %s after ticket %s" % (
            rec.get("session_id"), _iso(rec.get("killed_at") or 0), rec.get("ticket") or "-"))
    if cfg.get("kind") == "conductor":
        _wake_conductor(seat, cfg, rec, gen=args.gen)
        return 0
    print("\n== handoff pointers (handoff.py --wake)")
    try:
        r = subprocess.run([sys.executable, os.path.join(UTILS, "handoff.py"), "--wake"], cwd=REPO,
                           capture_output=True, text=True, timeout=120)
        out = (r.stdout or r.stderr or "").strip().splitlines()
        print("\n".join(out[:args.lines]) or "(nothing)")
    except Exception as e:  # noqa: BLE001
        print("handoff.py --wake failed: %s" % e)
    print("\n== your ticket: the Dispatcher hands it through the doorbell once this turn ends. Do NOT pick work "
          "yourself on this first turn; end it now.")
    return 0


def cmd_intile(args):
    seat = (args.seat or doorbell.seat_name() or "").upper()
    deadline = time.time() + 15
    while True:
        argv = intile_claim(seat, time.time())
        rec = _read_json(killed_path(seat)) or {}
        if argv or time.time() >= deadline or not rec.get("old_pid") or not doorbell._alive(int(rec["old_pid"])):
            break
        time.sleep(1)       # the killed window is still dying: give it a moment
    if not argv:
        return 3
    print("[seat_restart] relaunching %s in this tile" % seat, flush=True)
    os.execv(argv[0], argv)
    return 0


def cmd_status(args):
    st = _read_json(os.path.join(doorbell.state_dir(), "state.json")) or {}
    print(json.dumps({"config": config(_schedule()), "state": st.get("seat_restart") or {}}, indent=1, default=str))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("request", help="the seat asks for a fresh window (close-out step)")
    r.add_argument("--seat")
    r.add_argument("--ticket", required=True)
    r.add_argument("--reason", default="ticket ended")
    r.add_argument("--note", default="", help="3-5 lines for the seat log the fresh window reads")
    r.add_argument("--fresh", action="store_true",
                   help="ask for the fresh window even while context is under backstop_ctx_tokens")
    r.add_argument("--pid", type=int, help=argparse.SUPPRESS)
    w = sub.add_parser("wake", help="the fresh window's first read")
    w.add_argument("--seat")
    w.add_argument("--lines", type=int, default=40)
    w.add_argument("--gen", help="the restart generation the relaunch prompt carries (binds the wake to that restart)")
    i = sub.add_parser("intile", help="seat_loop.sh: relaunch here if a restart just killed this seat (exit 3: no)")
    i.add_argument("--seat")
    sub.add_parser("status")
    args = ap.parse_args(argv)
    return {"request": cmd_request, "wake": cmd_wake, "intile": cmd_intile, "status": cmd_status}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
