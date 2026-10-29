#!/usr/bin/env python3
"""Conductor goodbye — UserPromptSubmit (CONDUCTOR_GOODBYE_DESIGN_FRESH_EACH_TIME).

WHY THIS EXISTS. The Conductor window (seat key BENCH, session CONDUCTOR) is meant to be fresh each time he comes
back (design/RimMandrake/conductor_briefing_2026-10-28.md B2/B3). When his WHOLE message is a goodbye, this hook puts
the light close-out into that window's context on that turn: his rulings onto the ledger, open promises filed for
OWNER, 3-5 lines to the Conductor log, then `seat_restart.py request --seat BENCH --fresh`. The Dispatcher then
relaunches a fresh CONDUCTOR window after the grace (seat_restart.py, kind "conductor").

Only a whole-message goodbye fires: src/RimMandrake/rimflow/goodbye_phrase.py (case-folded, apostrophes dropped,
every run of non-word characters read as one space; letters of any script stay) compared WHOLE against
seat_restart.seats.BENCH.goodbye_phrases. "goodbye to the old pipe system" and "goodbye 取消" never fire. Only the
Conductor window fires: AGENT_SEAT BENCH and a session name the BENCH seat answers to (CONDUCTOR if the schedule is
unreadable). A window whose session file cannot be read gets one diagnostic line, never the close-out.

Prints nothing on an ordinary prompt and on any unreadable input (exit 0 always: a hook must never block his message).
It only prints: the restart itself is requested by the window and acted on by the Dispatcher, which holds it while
helpers are alive, he is typing, or the window is mid-reply.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RIMFLOW = ROOT / "src" / "RimMandrake" / "rimflow"
SCHEDULE = Path(os.environ.get("CONDUCTOR_GOODBYE_SCHEDULE") or RIMFLOW / "dispatcher_schedule.json")  # seam: tests
SEAT = "BENCH"
FIXED_NAME = "CONDUCTOR"         # the Conductor window's name when the schedule cannot be read (P2-8)
UNREADABLE_SEAM = "__UNREADABLE__"
sys.path.insert(0, str(RIMFLOW))
try:
    import goodbye_phrase as GP  # the one shared rule (seat_restart.py request applies it too)
except Exception:  # noqa: BLE001 - unloadable rule: the hook stays silent (main), never blocks his message
    GP = None


def norm(text):
    return GP.norm(text)


def _bench_restart(sch):
    return (((sch or {}).get("seat_restart") or {}).get("seats") or {}).get(SEAT)


def phrases(sch):
    return GP.phrases(_bench_restart(sch), default=())


def is_goodbye(prompt, phr):
    return GP.is_goodbye(prompt, phr)


def _names(sch):
    if not sch:
        return [FIXED_NAME]
    base = ((sch or {}).get("seats") or {}).get(SEAT) or {}
    out = []
    for n in [base.get("session_name")] + list(base.get("session_aliases") or []):
        if isinstance(n, str) and n and n not in out:
            out.append(n)
    return out


def is_conductor(env, sf, sch):
    """-> (ok, why). The Conductor window: AGENT_SEAT BENCH and a session name BENCH answers to (exact, or name +
    the title separator). An unreadable session file is NOT the Conductor (blind review 2026-10-29 P1-7: the close-out
    files and publishes the BENCH shard, so an unidentified window must not run it)."""
    seat = (env.get("AGENT_SEAT") or "").strip().upper()
    if seat != SEAT:
        return False, "AGENT_SEAT is %r, not %s" % (seat or None, SEAT)
    names = _names(sch)
    if not names:
        return False, "no session names for seat %s in dispatcher_schedule.json" % SEAT
    if sf is None:
        return False, "session name UNMEASURED (session file unreadable)"
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
        return None if seam == UNREADABLE_SEAM else {"name": seam}
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
    if GP is None or (os.environ.get("AGENT_SEAT") or "").strip().upper() != SEAT:
        return 0
    sch = _load_schedule()
    phr = phrases(sch) or GP.phrases({})
    if not is_goodbye(prompt, phr):
        return 0
    sf = _session_file()
    ok, why = is_conductor(os.environ, sf, sch)
    if not ok:
        if sf is None:
            print("GOODBYE seen (conductor_goodbye.py) but this window's identity is UNMEASURED (its session file "
                  "cannot be read): do NOT close out or restart. Tell him in one line that this window could not "
                  "confirm it is the Conductor, so it stays open.")
        return 0
    print(message(sch, ok_why=why))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # noqa: BLE001 - never block his message
        sys.exit(0)
