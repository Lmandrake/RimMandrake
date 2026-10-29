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
             (never by the Dispatcher's ring, a task notification or a seat's cross-session message: _is_human_input),
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
            "helper_stale_s": 3600, "game_hold_s": 3600, "cooldown_s": 1800,
            "hold_alarm_s": 3600, "request_max_age_s": 3600, "claimed_max_s": 300,
            "owner_idle_s": 120, "backstop_owner_idle_s": 1200, "fence_s": 1020, "ring_hold_s": 600,
            "kind": "doorbell", "backstop_human_idle_s": 0}
ACTIVE = ("pending", "claimed", "killed", "relaunched")
OWNS = ("claimed", "killed", "relaunched")      # pending leaves ring/recover running (review2: no recovery deadlock)
TRANSITIONAL = ("DEPLOYING", "LOADING", "GOING_DOWN")
DOES = ("restart_request", "restart_kill", "restart_fallback")
BOUNDED = "{clone}/src/RimMandrake/Utils/claude_bounded.sh"
MACHINE = os.path.expanduser("~/.claude-accounts/machine.json")
PROMPT = ("[RimFlow seat restart] You are a FRESH {seat} window: the last one was restarted after its ticket ended "
          "({why}). Run `python3 src/RimMandrake/rimflow/seat_restart.py wake --seat {seat}`, read what it prints, "
          "then end your turn: the Dispatcher hands you your next ticket through the doorbell.")
# kind "conductor" (CONDUCTOR_GOODBYE_DESIGN_FRESH_EACH_TIME): the BENCH window is the owner's Conductor. It has no
# doorbell (doorbell.py is FOUNDRY's Stop hook only) and no ticket to wait for: it wakes as the Conductor, answers any
# message he sent the old window after its close-out, and waits for him.
CONDUCTOR_PROMPT = ("[RimFlow seat restart] You are a FRESH Conductor window (session CONDUCTOR, seat key {seat}): the "
                    "last one closed out ({why}) and the Dispatcher restarted it; nobody typed this. Do the Start of "
                    "turn in infrastructure/agents/CONDUCTOR.md, and run `python3 src/RimMandrake/rimflow/seat_restart.py "
                    "wake --seat {seat}`: answer FIRST any owner message it lists as sent to the old window after the "
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


def _tail_records(path, nbytes):
    with open(path, "rb") as f:
        f.seek(0, os.SEEK_END)
        size = f.tell()
        f.seek(max(0, size - nbytes))
        data = f.read()
    lines = data.split(b"\n")
    if size > nbytes:
        lines = lines[1:]           # the first line of a tail is a fragment
    out = []
    for raw in lines:
        try:
            r = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, ValueError):
            continue
        if isinstance(r, dict):
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
    except OSError:
        return None
    s = {"last_kind": None, "last_at": None, "last_user_at": None, "ctx_tokens": None}
    for r in recs:
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


def helpers_of(path, now=None):
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
        except OSError:
            return None
        alive = not (recs and recs[-1].get("type") == "assistant" and _assistant_kind(recs[-1]) == "assistant_end")
        out.append({"id": os.path.basename(f)[:-len(".jsonl")], "alive": alive, "last_at": mt})
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
        "helpers": lambda seat, s: helpers_of(transcript_for(s, cfgs[seat]), now_fn()),
        "killed": killed_reading,
        "start": proc_start,
        "bridge": bridge_reading,
        "game": lambda seat: game_reading(seat, cfgs[seat].get("clone"), events_since, now_fn(),
                                          cfgs[seat]["game_hold_s"]),
        "armed": lambda seat: doorbell._read_json(doorbell.armed_path(seat)),
        "intile": lambda seat, killed_at: read_intile(seat, killed_at),
        "work": lambda seat, req_ts: work_since(cfgs[seat].get("clone"), seat, req_ts),
    }


# ---------------------------------------------------------------------------------------------------------------------
# argv

def relaunch_argv(seat, cfg, why="ticket ended"):
    """The WT seat profile's own LAUNCH line (install_wt_seat_profiles.LAUNCH) as an argv, plus a first prompt so the
    fresh window ends one turn and its Stop hook arms the doorbell."""
    label = cfg["session_name"]
    return [BOUNDED.format(clone=cfg["clone"]), "--dangerously-skip-permissions", "--name", label,
            "--model", cfg.get("model") or "sonnet", "--remote-control", label,
            PROMPTS[cfg.get("kind") or "doorbell"].format(seat=seat, why=why)]


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
                   "cooldown_s": cfg["cooldown_s"]}
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
            rs = R[seat] = {"source": "backstop", "ts": now, "session_id": cur.get("sessionId"), "pid": cur.get("pid"),
                            "start": born,
                            "ticket": None, "reason": "backstop: context %d tokens >= %d, idle %d s" % (
                                tx["ctx_tokens"], cfg["backstop_ctx_tokens"], now - tx["last_at"]),
                            "busy": 0, "cooldown_s": cfg["cooldown_s"], "state": "pending"}
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


def owner_ok(obs, need):
    """idle_probe's verdict on obs["owner"]() (the machine's last-input clock: MEASURED idle >= need, else hold).
    Typing into the window shows here before it reaches the transcript; a Remote Control draft on the phone does not."""
    import idle_probe
    try:
        reading = obs["owner"]() if callable(obs.get("owner")) else None
    except Exception as e:  # noqa: BLE001 - an unreadable owner clock holds
        reading = {"state": "UNMEASURED", "why": "%s: %s" % (type(e).__name__, e)}
    return idle_probe.idle_verdict(reading, need)


def _cancel(rs, seat, why, now, act):
    rs.update(state="cancelled", why=why, ended_at=now)
    act(do="restart_cancel", seat=seat, ticket=rs.get("ticket"), why=why)


def _pending(seat, cfg, rs, st, obs, ro, cur, now, act):
    if cur is None or cur.get("sessionId") != rs.get("session_id"):
        return _cancel(rs, seat, "the window's session changed or is gone (%s)" % ((cur or {}).get("sessionId")), now,
                       act)
    tx = ro["tx"](seat, cur)
    if tx and tx.get("last_user_at") and tx["last_user_at"] > rs["ts"]:
        return _cancel(rs, seat, "new input in the window at %s, after the request" % _iso(tx["last_user_at"]), now,
                       act)
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
    holds = []
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
    ok, owner_why = owner_ok(obs, cfg["backstop_owner_idle_s" if rs.get("source") == "backstop" else "owner_idle_s"])
    if not ok:                           # the owner may be typing into the window: never counts toward the held alarm
        act(do="restart_hold", seat=seat, why=owner_why)
        return
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
    rs.update(state="claimed", claimed_at=now, pid=cur.get("pid"))
    act(do="restart_kill", seat=seat, pid=cur.get("pid"), session_id=rs["session_id"],
        session_name=cfg["session_name"], session_names=SM.names_of(cfg), ticket=rs.get("ticket"),
        argv=relaunch_argv(seat, cfg, rs.get("reason") or "ticket ended"),
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
           "window_s": config(sch).get(seat, DEFAULTS)["intile_window_s"]}   # the tile obeys decide()'s deadline (review4 #2)
    fx.get("write_killed", write_killed)(seat, rec)
    how = fx.get("kill", kill_pid)(a["pid"], start=start)
    if how.startswith(("refused", "survived")):     # never relaunch beside a window that may still be there
        fx.get("write_killed", write_killed)(seat, dict(rec, aborted=how))
        rs.update(state="failed", why=how, ended_at=now, alarm_pending="seat restart of %s: %s" % (seat, how),
                  cooldown_until=now + rs.get("cooldown_s", DEFAULTS["cooldown_s"]))
        return "refused: " + how
    rs.update(state="killed", killed_at=kt, kill=how, window_s=rec["window_s"])
    return "killed pid %s (%s)" % (a["pid"], how)


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


def recheck_at_kill(seat, sch, rs, sf, owner=None, paused=paused_now, work=None):
    """-> the holds found by reading transcript, helpers, bridge, the owner's idle clock and PAUSE again at the kill
    (empty = go). Between this and the signal there is no barrier: that gap is one /proc start read, the killed-record
    write, the pidfd open and its start re-check (milliseconds)."""
    import idle_probe
    cfg = config(sch).get(seat) or dict(DEFAULTS)
    path = transcript_for(sf, cfg)
    tx = tx_summary(path or "")
    holds = []
    if not tx:
        holds.append("transcript unreadable")
    elif (tx.get("last_user_at") or 0) > rs.get("ts", 0):
        holds.append("new input at %s" % _iso(tx["last_user_at"]))
    elif tx.get("last_kind") != "assistant_end":
        holds.append("turn not ended (%s)" % tx.get("last_kind"))
    hs = helpers_of(path, time.time())
    if hs is None:
        holds.append("helper inventory UNMEASURED")
    elif any(h.get("alive") for h in hs):
        holds.append("helper(s) alive: %s" % ", ".join(h["id"] for h in hs if h.get("alive")))
    br = bridge_reading(seat)
    if br.get("state") != "MEASURED" or seat in (br.get("holders") or []):
        holds.append("bridge %s" % (br.get("why") or "held by %s" % seat))
    ok, why = owner_ok({"owner": owner or idle_probe.measure},
                       cfg["backstop_owner_idle_s" if rs.get("source") == "backstop" else "owner_idle_s"])
    if not ok:
        holds.append(why)
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
    return True, "ok"


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
    if unpub and unpub.startswith("UNMEASURED"):
        print("seat_restart: WARNING: could not tell whether your ledger shard is published (%s); check it "
              "yourself (close-out step 1)." % unpub)
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
              "run `python3 src/RimMandrake/rimflow/cli.py next --seat %s --ringed` and work the item it gives you, "
              "with the same close-out after it. Waiting on a lane job, a test result or a helper is NOT idle: take the "
              "next item and read those results between items. Only an empty queue ends the turn; if `next` gives you "
              "nothing workable, say why in a `rimflow note` before you end it." % (seat, ctx, limit, seat))
        return 0
    req = {"seat": seat, "pid": pid, "start": born, "session_id": sf["sessionId"], "ticket": args.ticket,
           "reason": args.reason, "ts": time.time(), "ctx_tokens": ctx}
    _write_json(request_path(seat), req)
    print("RESTART REQUESTED for %s (%s; context %s tokens, backstop %d%s). The Dispatcher acts after a %d s grace once "
          "this turn has ended and nothing holds it. End your turn now; a new prompt from the owner cancels it."
          % (seat, sf["sessionId"], "UNMEASURED" if ctx is None else ctx, limit, ", --fresh" if args.fresh else "",
             cfg["grace_s"]))
    return 0


def human_inputs_since(path, since, peers=None, tail_bytes=8 << 20):
    """-> [(ts, text)] of every HUMAN input (_is_human_input) in the transcript's tail newer than `since`, or None
    (unreadable). B1 of the Conductor design: a message he sent the old window after its close-out is answered first."""
    if peers is None:
        peers = peer_names()
    try:
        recs = _tail_records(path, tail_bytes)
    except (OSError, TypeError):
        return None
    out = []
    for r in recs:
        if r.get("type") != "user" or r.get("isSidechain") or not _is_human_input(r, peers):
            continue
        at = _ts(r.get("timestamp"))
        if at is not None and at > since:
            out.append((at, _text(r).strip()))
    return out


def _wake_conductor(seat, cfg, rec):
    """The Conductor's wake read after a goodbye restart: the old window's messages from him after the close-out."""
    if not rec:
        print("\n== no restart record: this window was not made by a goodbye restart (a fleet launch or boot).")
        return
    path = transcript_path(cfg.get("clone") or REPO, rec.get("session_id") or "")
    since = rec.get("req_ts") or rec.get("killed_at") or 0
    msgs = human_inputs_since(path, since)
    print("\n== his messages to the old window %s after the close-out (%s):" % (rec.get("session_id"), _iso(since)))
    if msgs is None:
        print("UNMEASURED: the old transcript %s is unreadable. Say so to him in one line; ask whether he sent "
              "anything after his goodbye." % path)
    elif not msgs:
        print("(none)")
    else:
        for at, text in msgs:
            print("- %s: %s" % (_iso(at), text[:2000]))
        print("Answer these FIRST, before anything else.")


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
        _wake_conductor(seat, cfg, rec)
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
    i = sub.add_parser("intile", help="seat_loop.sh: relaunch here if a restart just killed this seat (exit 3: no)")
    i.add_argument("--seat")
    sub.add_parser("status")
    args = ap.parse_args(argv)
    return {"request": cmd_request, "wake": cmd_wake, "intile": cmd_intile, "status": cmd_status}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
