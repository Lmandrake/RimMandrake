#!/usr/bin/env python3
"""Conductor goodbye — UserPromptSubmit (CONDUCTOR_GOODBYE_DESIGN_FRESH_EACH_TIME).

WHY THIS EXISTS. The Conductor window (seat key BENCH, session CONDUCTOR) is meant to be fresh each time he comes
back (design/RimMandrake/conductor_briefing_2026-10-28.md B2/B3). When his WHOLE message is a goodbye, this hook puts
the light close-out into that window's context on that turn: his rulings onto the ledger, open promises filed for
OWNER, 3-5 lines to the Conductor log, then `seat_restart.py request --seat BENCH --fresh`. The Dispatcher then
relaunches a fresh CONDUCTOR window after the grace (seat_restart.py, kind "conductor").

Only a whole-message goodbye fires: lower-cased, apostrophes dropped, every other non-alphanumeric run read as one
space, then compared WHOLE against seat_restart.seats.BENCH.goodbye_phrases. "goodbye to the old pipe system" never
fires. Only the Conductor window fires: AGENT_SEAT BENCH and a session name the BENCH seat answers to.

Prints nothing on an ordinary prompt and on any unreadable input (exit 0 always: a hook must never block his message).
It only prints: the restart itself is requested by the window and acted on by the Dispatcher, which holds it while
helpers are alive, he is typing, or the window is mid-reply.
"""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RIMFLOW = ROOT / "src" / "RimMandrake" / "rimflow"
SCHEDULE = RIMFLOW / "dispatcher_schedule.json"
SEAT = "BENCH"


def norm(text):
    t = (text or "").lower()
    t = re.sub(r"['\u2019\u2018`]", "", t)
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return t.strip()


def _bench_restart(sch):
    return (((sch or {}).get("seat_restart") or {}).get("seats") or {}).get(SEAT)


def phrases(sch):
    c = _bench_restart(sch)
    out = []
    for p in (c or {}).get("goodbye_phrases") or []:
        n = norm(p) if isinstance(p, str) else ""
        if n and n not in out:
            out.append(n)
    return out


def is_goodbye(prompt, phr):
    n = norm(prompt)
    return bool(n) and n in set(phr or ())


def _names(sch):
    base = ((sch or {}).get("seats") or {}).get(SEAT) or {}
    out = []
    for n in [base.get("session_name")] + list(base.get("session_aliases") or []):
        if isinstance(n, str) and n and n not in out:
            out.append(n)
    return out


def is_conductor(env, sf, sch):
    """-> (ok, why). The Conductor window: AGENT_SEAT BENCH and a session name BENCH answers to (exact, or name +
    the title separator). An unreadable session file still fires, said so: `seat_restart.py request` re-checks."""
    seat = (env.get("AGENT_SEAT") or "").strip().upper()
    if seat != SEAT:
        return False, "AGENT_SEAT is %r, not %s" % (seat or None, SEAT)
    names = _names(sch)
    if not names:
        return False, "no session names for seat %s in dispatcher_schedule.json" % SEAT
    if sf is None:
        return True, "session name UNMEASURED (session file unreadable); the restart request re-checks it"
    name = sf.get("name")
    sys.path.insert(0, str(RIMFLOW))
    try:
        import session_match as SM
        ok = SM.name_matches(name, names)
    except Exception:  # noqa: BLE001 - fall back to the same rule inline
        ok = isinstance(name, str) and any(name == n or name.startswith(n + " \u25b6 ") for n in names)
    return (True, "session %r" % name) if ok else (False, "session %r is not one of %s" % (name, names))


CLOSE_OUT = """GOODBYE (conductor_goodbye.py): his whole message was a goodbye. Do the light close-out NOW, in this order, \
briefly (B2, design/RimMandrake/conductor_briefing_2026-10-28.md; window: {why}):
1. Every ruling he gave in this window that is not on the ledger yet: `python3 src/RimMandrake/rimflow/cli.py note \
<ITEM> --text "..." --owner-said "<his exact words>"` (or file/close with --owner-said). His words only; your own reasons \
take --why.
2. Every promise you made him that is still open: file it for him, `python3 src/RimMandrake/rimflow/cli.py file \
<SUBJECT>_<INTENT>_PROMISED_AT_GOODBYE --for OWNER --why "<what was promised, where>"` (name it with `rimflow \
namecheck` first).
3. Commit the BENCH ledger shard (infrastructure/state/ledger/events/BENCH.jsonl) by explicit path, then `./publish`.
4. {restart}
5. Reply to him in ONE line: "Closed out: N rulings on the ledger, M promises filed. {tail}" Then end the turn. \
Do not start new work."""

RESTART = """3-5 lines for the next window go in via the request itself (they land in {log}): \
`python3 src/RimMandrake/rimflow/seat_restart.py request --seat BENCH --ticket GOODBYE --reason goodbye --fresh \
--note "<3-5 lines: what is open, what needs him, what you promised>"`. If it prints REFUSED (helpers still alive, \
unpublished shard, wrong window), fix what it names and run it again once; if it still refuses, tell him in your one \
line that this window stays open and why."""

NO_RESTART = """{reason}: NO restart. Write the 3-5 lines yourself: append them under a `## <UTC time> GOODBYE` \
heading to {log}. This window stays open."""


def message(sch, ok_why=""):
    c = _bench_restart(sch)
    log = (c or {}).get("seat_log") or ((sch or {}).get("no_handoff") or {}).get("conductor_log") \
        or "/mnt/d/ClaudeWork/rimmandrake/conductor/log.md"
    sr = (sch or {}).get("seat_restart") or {}
    if not sch:
        reason = "dispatcher_schedule.json UNREADABLE"
    elif sr.get("enabled") is not True:
        reason = "seat_restart is off in dispatcher_schedule.json"
    elif not isinstance(c, dict) or c.get("enabled") is False:
        reason = "seat_restart is off for BENCH in dispatcher_schedule.json"
    else:
        reason = None
    if reason:
        step4 = NO_RESTART.format(reason=reason, log=log)
        tail = "This window stays open (%s)." % reason
    else:
        step4 = RESTART.format(log=log)
        tail = "Fresh Conductor in 2-6 min; write any time, and nothing you send is lost."
    return CLOSE_OUT.format(why=ok_why or "-", restart=step4, tail=tail)


def _load_schedule():
    try:
        with open(SCHEDULE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _session_file():
    seam = os.environ.get("CONDUCTOR_GOODBYE_SESSION_NAME")
    if seam:
        return {"name": seam}
    sys.path.insert(0, str(RIMFLOW))
    try:
        import doorbell
        import seat_restart as SR
        pid = doorbell.claude_ancestor()
        return SR.session_file(pid) if pid else None
    except Exception:  # noqa: BLE001
        return None


def main():
    try:
        data = json.loads(sys.stdin.read() or "")
    except ValueError:
        return 0
    prompt = data.get("prompt") if isinstance(data, dict) else None
    if not isinstance(prompt, str):
        return 0
    if (os.environ.get("AGENT_SEAT") or "").strip().upper() != SEAT:
        return 0
    sch = _load_schedule()
    phr = phrases(sch) or [norm(p) for p in ("goodbye", "bye", "gn", "good night", "done for now", "thats all")]
    if not is_goodbye(prompt, phr):
        return 0
    ok, why = is_conductor(os.environ, _session_file(), sch)
    if not ok:
        return 0
    print(message(sch, ok_why=why))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # noqa: BLE001 - never block his message
        sys.exit(0)
