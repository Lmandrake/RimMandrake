#!/usr/bin/env python3
"""When did the owner last DELIBERATELY interact with the system? -> the clock on his OWNER bridge hold.

🔴 OWNER, by question card 2026-10-30 ("Should agents ever be allowed to take your hold?"), typed: "45 minutes after
my last interaction, or I deliberately release it". So an OWNER hold is takeable only once 45 min have passed since
the latest of his interactions; otherwise every take refuses, `--force` included, naming his last interaction time.

What counts as an interaction (the Conductor's reading of "interaction", BRIDGE_DECIDE_STALE_OWNER_HOLD):
  ledger   an event HIS OWN HANDS wrote (is_his_act below): seat OWNER carrying no relay marker (his own commands,
           `./game` run by him, which broadcast.py stamps OWNER), and an event whose `override` says "the OWNER ..."
           (his `./bridge bench|foundry|free`, which is emitted under the target seat). Seat OWNER alone is his
           AUTHORITY, not his activity: an agent under --owner-said/--by-card/--per-ruling, or an agent's `./game
           --why`, wears that seat and never resets his clock (OWNER_CLOCK_FIX_RELAYED_ORDERS_WEAR_HAT). Gathered by
           cli.py from the replay.
  hold     the OWNER hold's own events (its `since`; the shared cross-clone lock's `touched`). Gathered by cli.py.
  bridge   a bare `./bridge` (`bridge who --seat OWNER`, which writes no event): the stamp file written here.
  chat     his prompts to ANY seat window: the last HUMAN input (seat_restart._is_human_input — the same signal
           block_agent_over_slots.py uses for its 20-min conductor_window rule, via seat_restart.tx_summary) in every
           main transcript of every scheduled seat's clone, under the Claude config dir; and a question card he
           answered there, which is his act at the moment he clicked (a --by-card event only relays it, later).

⛔ NEVER keyboard, mouse or any machine input clock. OWNER 2026-10-30, verbatim: "I really, really need you to strip
"when I come back to the machine" as an event for anything changing." (selftest_no_owner_presence.py guards it.)
Only a transcript a seat window wrote, and only the input records in it that a person typed, are read.

UNMEASURED REFUSES: a transcript touched inside the window that cannot be read, an unreadable stamp, an unreadable
seat schedule or a missing Claude projects dir is not "he was quiet" — the take is refused and the reason printed.

Test ledgers: under a redirected RIMFLOW_LEDGER the chat scan is off (no seat windows belong to a throwaway ledger)
unless RIMFLOW_OWNER_CHAT_DIRS names the transcript dirs to read (os.pathsep-separated; set-but-empty = none). The
stamp sits beside the shared bridge lock when there is one (both clones see it), else beside the ledger's lock;
RIMFLOW_OWNER_ACT_STAMP overrides it.
"""
import calendar
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if os.path.dirname(HERE) not in sys.path:               # `from rimflow import ...`: the SAME module objects cli.py
    sys.path.insert(0, os.path.dirname(HERE))           # uses, so its rebinding of model.EVENTS is seen here

WINDOW_S = 45 * 60          # his "45 minutes"; cli.py asserts this equals model.BRIDGE_STALE_SECONDS


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t)) if t is not None else "?"


# ---------------------------------------------------------------------------------------------------------------------
# ledger: whose hands wrote an event

# An event carrying any of these was written by an agent. byCard/ownerSaid/perRuling relay him; `why` is, by the flag's
# definition, the agent's own reason; ranBy names the seat whose hands ran it; role_unit is a headless role's run. The
# fields are on the history already (ranBy only on `game`), so no migration is owed.
RELAY_FIELDS = ("ownerSaid", "byCard", "perRuling", "why", "ranBy", "role_unit")


def is_his_act(ev):
    """Pure. Did the owner's own hands write this event? The one definition of "his activity" in the ledger: use it,
    not `seat == "OWNER"`, for his clock and for any count of what he did. Seat OWNER says whose AUTHORITY an event
    carries, which is his under every relay too."""
    if any(ev.get(f) for f in RELAY_FIELDS):
        return False
    return ev.get("seat") == "OWNER" or str(ev.get("override") or "").startswith("the OWNER ")


def agent_hands(role_seat=None):
    """-> the seat whose shell is running this ("BENCH", "AGENT" for a Claude shell naming none), or "" for a plain
    terminal: his. Stamped as `ranBy` on what they write under his seat, and it keeps a bare `./bridge` run by an agent
    off his clock. RIMFLOW_SEAT is not read: `./game` forces it to OWNER (and passes the real seat in RIMFLOW_RAN_BY).
    role_seat: the session role file's seat. A `!` command he types inside a Claude window reads as that window's: his chat record there is what counts."""
    for val in (os.environ.get("RIMFLOW_RAN_BY"), os.environ.get("AGENT_SEAT"), role_seat):
        val = (val or "").strip().upper()
        if val and val != "OWNER":
            return val
    return "AGENT" if os.environ.get("CLAUDECODE") else ""


# ---------------------------------------------------------------------------------------------------------------------
# bare ./bridge: the stamp

def stamp_path():
    env = os.environ.get("RIMFLOW_OWNER_ACT_STAMP")
    if env:
        return env
    from rimflow import lease, model
    shared = model.shared_bridge_path()
    base = os.path.dirname(shared) if shared else os.path.dirname(lease.lock_path())
    return os.path.join(base, "OWNER_LAST_ACT.json")


def write_stamp(what, now=None):
    """Record one deliberate owner act that writes no ledger event (bare `./bridge`). Atomic replace."""
    p = stamp_path()
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    tmp = "%s.%d.tmp" % (p, os.getpid())
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"at": iso(time.time() if now is None else now), "what": what}, f)
    os.replace(tmp, p)


def read_stamp():
    """-> (epoch or None, problem or None). Absent = he never did it (measured); unreadable = UNMEASURED."""
    p = stamp_path()
    try:
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        return calendar.timegm(time.strptime(d["at"], "%Y-%m-%dT%H:%M:%SZ")), None
    except FileNotFoundError:
        return None, None
    except (OSError, ValueError, KeyError, TypeError) as e:
        return None, "the ./bridge stamp %s is unreadable (%s)" % (p, type(e).__name__)


# ---------------------------------------------------------------------------------------------------------------------
# chat: his prompts to any seat window

def chat_dirs():
    """-> (list of transcript dirs, problem or None)."""
    env = os.environ.get("RIMFLOW_OWNER_CHAT_DIRS")
    if env is not None:
        return [d for d in env.split(os.pathsep) if d], None
    if os.environ.get("RIMFLOW_LEDGER"):
        return [], None
    from rimflow import seat_restart as SR
    try:
        sch = SR._schedule()
        clones = sorted({c.get("clone") for c in (sch.get("seats") or {}).values()
                         if isinstance(c, dict) and c.get("clone")})
    except Exception as e:  # noqa: BLE001 - any failure to read the seat schedule is UNMEASURED
        return [], "the seat schedule is unreadable (%s: %s)" % (type(e).__name__, e)
    if not clones:
        return [], "the seat schedule names no seat clone"
    root = os.path.join(SR.claude_home(), "projects")
    if not os.path.isdir(root):
        return [], "no Claude projects dir at %s" % root
    try:                                    # listdir, not glob: glob turns an unreadable dir into "nothing there"
        names = os.listdir(root)
    except OSError as e:
        return [], "the Claude projects dir %s is unreadable (%s)" % (root, type(e).__name__)
    out = []
    for c in clones:
        stem = re.sub(r"[^A-Za-z0-9]", "-", c)
        # the clone itself, and a window started in a subdirectory of it (<stem>-src-...)
        out += sorted(os.path.join(root, n) for n in names
                      if (n == stem or n.startswith(stem + "-")) and os.path.isdir(os.path.join(root, n)))
    return out, None


def last_card_answer(path, tail_bytes=None):
    """-> epoch of the last question card answered in this transcript's tail (None: all of it), or None. The caller has already had the
    tail judged readable by tx_summary; a line that will not parse here is the mid-write last line, never an answer."""
    with open(path, "rb") as f:
        f.seek(0, os.SEEK_END)
        f.seek(max(0, f.tell() - tail_bytes) if tail_bytes else 0)
        data = f.read()
    best = None
    for raw in data.split(b"\n"):
        if b'"toolUseResult"' not in raw or b'"answers"' not in raw:
            continue
        try:
            rec = json.loads(raw)
        except ValueError:
            continue
        res = rec.get("toolUseResult")
        if isinstance(res, dict) and res.get("answers"):
            try:
                t = calendar.timegm(time.strptime(rec["timestamp"][:19], "%Y-%m-%dT%H:%M:%S"))
            except (KeyError, TypeError, ValueError):
                continue
            if best is None or t > best:
                best = t
    return best


def last_chat(now=None, window_s=WINDOW_S):
    """-> (epoch of his latest prompt found in a transcript touched inside the window, or None; problem or None).

    Only main transcripts (<dir>/*.jsonl; a helper's are under <session>/subagents/) whose mtime is inside the
    window are read: one older than the window cannot hold a prompt inside it, so the take decision needs no more."""
    from rimflow import seat_restart as SR
    now = time.time() if now is None else now
    dirs, problem = chat_dirs()
    if problem:
        return None, problem
    best, problems = None, []
    peers = None
    for d in dirs:
        try:                                # listdir, not glob: an unreadable dir is UNMEASURED, not "no prompts"
            paths = [os.path.join(d, n) for n in os.listdir(d) if n.endswith(".jsonl")]
        except OSError as e:
            problems.append("%s: %s" % (d, type(e).__name__))
            continue
        for path in paths:
            try:
                st = os.stat(path)
            except OSError as e:
                problems.append("%s: %s" % (path, type(e).__name__))
                continue
            if st.st_mtime < now - window_s:
                continue
            if peers is None:
                try:
                    peers = SR.peer_names()
                except Exception as e:  # noqa: BLE001
                    return None, "seat peer names unreadable (%s)" % type(e).__name__
            tail = 4 << 20
            try:
                s = SR.tx_summary(path, tail_bytes=tail, peers=peers)
            except Exception as e:  # noqa: BLE001 - a reader crash is UNMEASURED, never a traceback or "quiet"
                problems.append("%s: reader failed (%s)" % (path, type(e).__name__))
                continue
            if s is None:
                problems.append("%s unreadable or mid-write" % path)
                continue
            t = s.get("last_user_at")
            scan = tail                                # a prompt in the tail is newer than any answer before the tail
            if t is None and st.st_size > tail:        # his last prompt may sit before the tail: read it all
                scan = None
                try:
                    lh = SR.last_human(path, peers=peers)
                except Exception:  # noqa: BLE001
                    lh = None
                if lh is None:
                    problems.append("%s unreadable" % path)
                    continue
                t = lh[0]
            try:
                card = last_card_answer(path, scan)
            except OSError as e:
                problems.append("%s: %s" % (path, type(e).__name__))
                continue
            t = max(x for x in (t, card, 0) if x is not None) or None
            if t is not None and (best is None or t > best):
                best = t
    if problems:
        return best, "transcript(s) not measurable: %s" % "; ".join(problems[:3])
    return best, None


# ---------------------------------------------------------------------------------------------------------------------
# the verdict

def verdict(times, problems, now=None, window_s=WINDOW_S):
    """Pure. times: {source label: epoch or None}; problems: [str]. -> (takeable, text).

    takeable only when nothing is UNMEASURED and every known interaction is at least window_s old."""
    now = time.time() if now is None else now
    known = [(t, k) for k, t in times.items() if t is not None]
    last = max(known) if known else None
    lasttxt = ("%s (%s, %d min ago)" % (iso(last[0]), last[1], max(0, int(now - last[0])) // 60)
               if last else "none recorded")
    if problems:
        return False, ("his last interaction is UNMEASURED (%s); last measured: %s"
                       % ("; ".join(problems), lasttxt))
    if last and now - last[0] < window_s:
        return False, ("his last interaction was %s; his hold is takeable %d min after it, at %s"
                       % (lasttxt, window_s // 60, iso(last[0] + window_s)))
    return True, "the owner has not interacted for %d+ min (last: %s)" % (window_s // 60, lasttxt)
